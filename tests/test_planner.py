from pathlib import Path

import pytest

from codexbench.planner import BudgetError, build_plan, require_budget
from codexbench.specs import ExecutionBudgetSpec, load_experiment


ROOT = Path(__file__).resolve().parents[1]


def test_when_main_plan_is_12_by_6_by_2() -> None:
    manifest = ROOT / "experiments" / "week4-when-main.yaml"
    experiment = load_experiment(manifest)
    plan = build_plan(experiment, manifest)
    assert len(plan) == 144
    assert len({row["run_id"] for row in plan}) == 144
    assert {row["repetition"] for row in plan} == {1, 2}
    assert require_budget(experiment, plan)["within_budget"] is True


def test_pilot_reuses_none_and_combined_for_eight_unique_runs() -> None:
    manifest = ROOT / "experiments" / "week4-pilot.yaml"
    experiment = load_experiment(manifest)
    plan = build_plan(experiment, manifest)
    assert len(plan) == 8
    assert {row["condition_id"] for row in plan} >= {
        "full_off",
        "full_on",
        "what_repo",
        "what_test",
    }


def test_budget_rejects_matrix_before_execution() -> None:
    manifest = ROOT / "experiments" / "week4-pilot.yaml"
    experiment = load_experiment(manifest).model_copy(
        update={"execution_budget": ExecutionBudgetSpec(max_runs=1)}
    )
    with pytest.raises(BudgetError):
        require_budget(experiment, build_plan(experiment, manifest))
