from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from codexbench.specs import ExperimentSpec
from codexbench.store import ResultStore, utc_now


def _result(row: dict[str, Any]) -> dict[str, Any]:
    return json.loads(row["result_json"]) if row.get("result_json") else {}


def generate_week4_analysis(
    experiment: ExperimentSpec,
    store: ResultStore,
    output_dir: Path,
) -> dict[str, Any]:
    rows = store.experiment_runs(experiment.experiment_id)
    conditions = {condition.id: condition for condition in experiment.conditions}
    run_rows: list[dict[str, Any]] = []
    for row in rows:
        result = _result(row)
        condition = conditions[row["condition_id"]]
        run_rows.append(
            {
                "condition_id": row["condition_id"],
                "metadata": condition.metadata,
                "status": row["status"],
                "outcome_kind": row["outcome_kind"],
                "resolved": None if row["resolved"] is None else bool(row["resolved"]),
                "duration_seconds": row["duration_seconds"],
                "effective_tokens": row["budget_tokens"],
                "behavior": result.get("behavior") or {},
                "error": result.get("error"),
                "run_id": row["run_id"],
            }
        )

    by_id = {row["condition_id"]: row for row in run_rows}
    when = {
        level: {
            "off": by_id[f"{level}_off"],
            "on": by_id[f"{level}_on"],
        }
        for level in ("full", "partial", "sparse")
    }
    what = {
        "none": by_id["full_off"],
        "repo": by_id["what_repo"],
        "test": by_id["what_test"],
        "combined": by_id["full_on"],
    }
    evaluated = [row for row in run_rows if row["resolved"] is not None]
    resolved = [row for row in evaluated if row["resolved"]]
    failures = [row for row in run_rows if row["status"] == "failed"]
    analysis = {
        "generated_at": utc_now(),
        "experiment_id": experiment.experiment_id,
        "planned_runs": len(experiment.tasks) * len(experiment.conditions) * experiment.repetitions,
        "stored_runs": len(run_rows),
        "evaluated_runs": len(evaluated),
        "resolved_runs": len(resolved),
        "resolved_rate_among_evaluated": round(len(resolved) / len(evaluated), 4) if evaluated else None,
        "budget_exceeded_runs": sum(row["outcome_kind"] == "budget_exceeded" for row in run_rows),
        "when": when,
        "what": what,
        "failures": failures,
        "runs": run_rows,
        "interpretation": (
            "One task and one repetition are an engineering pilot, not evidence of a causal "
            "AGENTS.md effect. Budget-exceeded runs are missing evaluator outcomes, not unresolved patches."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "week4-analysis.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    lines = [
        "# Week 4 WHEN·WHAT 파일럿 분석",
        "",
        f"- 실행 저장: `{len(run_rows)}/{analysis['planned_runs']}`",
        f"- 비공개 평가 완료: `{len(evaluated)}`",
        f"- 평가 완료 run 중 resolved: `{len(resolved)}/{len(evaluated)}`",
        f"- Token budget 초과: `{analysis['budget_exceeded_runs']}`",
        "- 표본: 1 task × 1 repetition — 연구 결론이 아닌 시스템 파일럿",
        "",
        "## WHEN",
        "",
        "| 문서 수준 | OFF 결과 | OFF tokens | ON 결과 | ON tokens |",
        "|---|---|---:|---|---:|",
    ]
    for level, pair in when.items():
        lines.append(
            f"| {level} | {pair['off']['outcome_kind']} | {pair['off']['effective_tokens']} | "
            f"{pair['on']['outcome_kind']} | {pair['on']['effective_tokens']} |"
        )
    lines.extend(
        [
            "",
            "## WHAT",
            "",
            "| 지침 정보 | 결과 | Resolved | 시간(초) | Effective tokens | 명령/테스트 명령 |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for name, row in what.items():
        behavior = row["behavior"]
        lines.append(
            f"| {name} | {row['outcome_kind']} | {row['resolved']} | "
            f"{row['duration_seconds']:.3f} | {row['effective_tokens']} | "
            f"{behavior.get('command_count', 0)}/{behavior.get('test_command_count', 0)} |"
        )
    lines.extend(
        [
            "",
            "## 실패 사례",
            "",
        ]
    )
    for row in failures:
        lines.extend(
            [
                f"### {row['condition_id']}",
                "",
                f"- 분류: `{row['outcome_kind']}`",
                f"- Effective tokens: `{row['effective_tokens']}` / `{experiment.runtime.token_budget}`",
                f"- 원인: `{row['error']}`",
                "- 해석: Codex process는 정상 종료했지만 budget gate가 evaluator 실행 전에 fail-closed 처리함.",
                "",
            ]
        )
    lines.extend(
        [
            "## 해석 제한",
            "",
            "모든 evaluator 완료 run이 resolved됐지만, task 1개·반복 1회이므로 지침 효과를 주장할 수 없다. "
            "특히 budget 초과 두 조건은 정확성 결과가 결측이며 unresolved로 세면 안 된다. "
            "본 결과는 144회 본실험을 실행하기 전 조건 생성·로그 연결·예산 중단·실패 보존을 검증한 것이다.",
            "",
        ]
    )
    (output_dir / "week4-analysis.ko.md").write_text("\n".join(lines), encoding="utf-8")
    return analysis

