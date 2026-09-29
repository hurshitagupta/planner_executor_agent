import pytest

from step_state_machine import Step, execute_step, update_status, run

def test_success_state_flow():
    step = Step(id="1", action="Collect customer details")

    trace = execute_step(step)

    assert step.status == "success"

    assert [item["status"] for item in trace] == ["pending", "running","success"]


def test_failure_state_flow():
    step = Step(id="2", action="Process customer request")

    trace = execute_step(step, should_fail=True)

    assert step.status == "failed"

    assert [item["status"] for item in trace] == ["pending", "running", "failed"]


def test_pending_cannot_go_directly_to_success():
    step = Step(id="1", action="Collect data")

    with pytest.raises(ValueError, match="Invalid transition"):
        update_status(step, "success")

def test_success_step_cannot_run_again():
    step = Step(id="1", action="Collect data", status="success")

    with pytest.raises(ValueError, match="Invalid transition"):
        update_status(step, "running")

def test_empty_action_rejected():
    step = Step(id="1", action="")

    with pytest.raises(ValueError, match="Step action cannot be empty"):
        execute_step(step)

def test_run_reports_measurements():
    result = run()

    assert result["total_steps"] == 2
    assert result["successful_steps"] == 1
    assert result["failed_steps"] == 1
    assert "duration_ms" in result