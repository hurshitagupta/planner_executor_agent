import pytest

from planner_executor_split import Step, planner, executor, run


def test_planner_executor_success():
    plan = planner("Prepare order summary")

    assert len(plan) == 3
    assert all(step.status == "pending" for step in plan)

    result = executor(plan)

    assert all(step.status == "success" for step in result)


def test_executor_failure():
    steps = [
        Step(id="1", action="Collect information"),
        Step(id="2", action=""),
    ]

    result = executor(steps)

    assert result[0].status == "success"
    assert result[1].status == "failed"

def test_empty_goal_rejected():
    with pytest.raises(ValueError, match="Goal cannot be empty"):
        planner("")

def test_step_limit():
    steps = [Step(str(i), f"Action {i}") for i in range(10)]

    with pytest.raises(ValueError, match="step limit exceeded"):
        executor(steps)

def test_trace_contains_measurements():
    trace = run("Prepare order summary")

    assert trace["step_count"] == 3
    assert trace["successful_steps"] == 3
    assert trace["failed_steps"] == 0
    assert "duration_ms" in trace