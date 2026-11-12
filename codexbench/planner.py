from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from codexbench.specs import ExperimentSpec, build_run_spec


class BudgetError(ValueError):
    pass


def build_plan(experiment: ExperimentSpec, manifest: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for repetition in range(1, experiment.repetitions + 1):
        for task in experiment.tasks:
            for condition in experiment.conditions:
                spec = build_run_spec(
                    experiment, manifest, task.id, condition.id, repetition
                )
                rows.append(
                    {
                        "task_id": task.id,
                        "condition_id": condition.id,
                        "condition_label": condition.label,
                        "condition_metadata": condition.metadata,
                        "repetition": repetition,
                        "run_id": spec.run_id,
                        "max_effective_tokens": experiment.runtime.token_budget,
                        "max_wall_seconds": (
                            experiment.runtime.agent_timeout_seconds
                            + experiment.runtime.evaluator_timeout_seconds
                            + 300
                        ),
                    }
                )
    random.Random(experiment.seed).shuffle(rows)
    for order, row in enumerate(rows, start=1):
        row["order"] = order
    return rows


def budget_summary(experiment: ExperimentSpec, plan: list[dict[str, Any]]) -> dict[str, Any]:
    requested = {
        "runs": len(plan),
        "effective_tokens": sum(row["max_effective_tokens"] for row in plan),
        "wall_seconds": sum(row["max_wall_seconds"] for row in plan),
    }
    allowed = {
        "runs": experiment.execution_budget.max_runs,
        "effective_tokens": experiment.execution_budget.max_effective_tokens,
        "wall_seconds": experiment.execution_budget.max_wall_seconds,
    }
    violations = {
        key: {"requested": requested[key], "allowed": allowed[key]}
        for key in requested
        if requested[key] > allowed[key]
    }
    return {
        "requested": requested,
        "allowed": allowed,
        "within_budget": not violations,
        "violations": violations,
    }


def require_budget(experiment: ExperimentSpec, plan: list[dict[str, Any]]) -> dict[str, Any]:
    summary = budget_summary(experiment, plan)
    if not summary["within_budget"]:
        raise BudgetError(f"matrix exceeds execution budget: {summary['violations']}")
    return summary


def write_plan(
    experiment: ExperimentSpec,
    manifest: Path,
    output_dir: Path,
) -> dict[str, Any]:
    plan = build_plan(experiment, manifest)
    budget = require_budget(experiment, plan)
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl = output_dir / f"{experiment.experiment_id}.jsonl"
    jsonl.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in plan),
        encoding="utf-8",
    )
    summary = {
        "experiment_id": experiment.experiment_id,
        "manifest": str(manifest.resolve()),
        "seed": experiment.seed,
        "tasks": len(experiment.tasks),
        "conditions": len(experiment.conditions),
        "repetitions": experiment.repetitions,
        "runs": len(plan),
        "budget": budget,
        "plan_jsonl": str(jsonl),
    }
    (output_dir / f"{experiment.experiment_id}.summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return summary

