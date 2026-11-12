from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from codexbench.reporting import generate_report
from codexbench.planner import BudgetError, build_plan, require_budget, write_plan
from codexbench.runner import HarnessError, Runner, resolve_paths, validate_environment
from codexbench.specs import build_run_spec, load_experiment
from codexbench.store import ResultStore
from codexbench.week4_analysis import generate_week4_analysis


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="codexbench")
    commands = root.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="Validate manifest, tools, tasks, and Docker")
    validate.add_argument("manifest", type=Path)
    validate.add_argument("--pull-images", action="store_true")

    plan = commands.add_parser("plan", help="Create a seeded matrix plan and enforce budgets")
    plan.add_argument("manifest", type=Path)
    plan.add_argument("--output", type=Path, default=Path("plans"))

    run = commands.add_parser("run", help="Run one task/condition/repetition")
    run.add_argument("manifest", type=Path)
    run.add_argument("--task", required=True)
    run.add_argument("--condition", required=True)
    run.add_argument("--repetition", type=int, default=1)
    run.add_argument("--resume", action="store_true")

    run_all = commands.add_parser("run-all", help="Run the complete deterministic pilot matrix")
    run_all.add_argument("manifest", type=Path)
    run_all.add_argument("--resume", action="store_true")
    run_all.add_argument(
        "--confirm-large-matrix",
        action="store_true",
        help="Required when a matrix contains more than 20 model calls",
    )

    report = commands.add_parser("report", help="Aggregate SQLite results")
    report.add_argument("manifest", type=Path)
    report.add_argument("--output", type=Path, default=Path("reports"))

    analyze = commands.add_parser("analyze-week4", help="Build WHEN/WHAT pilot analysis")
    analyze.add_argument("manifest", type=Path)
    analyze.add_argument("--output", type=Path, default=Path("reports"))
    return root


def _load(path: Path):
    path = path.resolve()
    experiment = load_experiment(path)
    return path, experiment, resolve_paths(experiment, path)


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        manifest, experiment, paths = _load(args.manifest)
        if args.command == "validate":
            report = validate_environment(experiment, paths, pull_images=args.pull_images)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["status"] == "ready" else 2

        if args.command == "plan":
            output = args.output
            if not output.is_absolute():
                output = paths.project_root / output
            summary = write_plan(experiment, manifest, output)
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return 0

        store = ResultStore(paths.database)
        try:
            if args.command == "run":
                spec = build_run_spec(
                    experiment,
                    manifest,
                    args.task,
                    args.condition,
                    args.repetition,
                )
                result = Runner(spec, paths, store, resume=args.resume).run()
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return 0 if result["status"] == "completed" else 1

            if args.command == "run-all":
                plan = build_plan(experiment, manifest)
                require_budget(experiment, plan)
                if len(plan) > 20 and not args.confirm_large_matrix:
                    raise HarnessError(
                        f"matrix has {len(plan)} model calls; inspect `codexbench plan` output "
                        "and pass --confirm-large-matrix to execute"
                    )
                failures = 0
                used_tokens = 0
                used_seconds = 0.0
                for row in plan:
                    spec = build_run_spec(
                        experiment,
                        manifest,
                        row["task_id"],
                        row["condition_id"],
                        row["repetition"],
                    )
                    result = Runner(spec, paths, store, resume=args.resume).run()
                    used_tokens += (result.get("token_usage") or {}).get("budget_tokens", 0)
                    used_seconds += result.get("duration_seconds") or 0
                    if used_tokens > experiment.execution_budget.max_effective_tokens:
                        raise HarnessError("observed effective-token budget exceeded")
                    if used_seconds > experiment.execution_budget.max_wall_seconds:
                        raise HarnessError("observed wall-time budget exceeded")
                    print(
                        json.dumps(
                            {
                                "run_id": result["run_id"],
                                "status": result["status"],
                                "outcome_kind": result["outcome_kind"],
                                "resolved": result["resolved"],
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
                    failures += result["status"] != "completed"
                return 1 if failures else 0

            if args.command == "report":
                output = args.output
                if not output.is_absolute():
                    output = paths.project_root / output
                report = generate_report(experiment, store, output)
                print(json.dumps(report, indent=2, ensure_ascii=False))
                return 0
            if args.command == "analyze-week4":
                output = args.output
                if not output.is_absolute():
                    output = paths.project_root / output
                report = generate_week4_analysis(experiment, store, output)
                print(json.dumps(report, indent=2, ensure_ascii=False))
                return 0
        finally:
            store.close()
    except (ValidationError, HarnessError, BudgetError, KeyError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2

