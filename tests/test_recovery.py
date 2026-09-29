import pytest

from recovery import Step, execute_with_retry, replan


def test_transient_failure_is_retried():
    step = Step(id="1", action="Verify information")
    result = execute_with_retry(step, failure_type="transient")

    assert result["status"] == "success"
    assert len(result["attempts"]) == 2
    assert step.status == "success"


def test_permanent_failure_is_not_retried():
    step = Step(id="1", action="Verify information")
    result = execute_with_retry(step, failure_type="permanent")

    assert result["status"] == "failed"
    assert len(result["attempts"]) == 1
    assert step.status == "failed"


def test_no_replan_when_evidence_does_not_invalidate_plan():
    steps = [Step(id="1", action="Collect information", status="success"),
            Step(id="2", action="Prepare response")]

    revised_steps, replan_count = replan(goal="Resolve request", steps=steps, evidence_invalidates_plan=False, replan_count=0)

    assert revised_steps == steps
    assert replan_count == 0


def test_replan_when_evidence_invalidates_remaining_plan():
    steps = [Step(id="1", action="Collect information", status="success"),
            Step(id="2", action="Verify information", status="failed"),
            Step(id="3", action="Prepare response")]

    revised_steps, replan_count = replan(goal="Resolve request", steps=steps, evidence_invalidates_plan=True, replan_count=0)

    assert replan_count == 1

    assert revised_steps[0].id == "1"
    assert revised_steps[0].status == "success"

    assert any(step.id == "3R" for step in revised_steps)


def test_replan_limit_is_enforced():
    steps = [Step(id="1", action="Collect information", status="success")]

    with pytest.raises(RuntimeError, match="Replan limit reached"):
        replan(goal="Resolve request", steps=steps, evidence_invalidates_plan=True, replan_count=1)


def test_empty_action_is_rejected():
    step = Step(id="1", action="")

    with pytest.raises(ValueError, match="Step action cannot be empty"):
        execute_with_retry(step)