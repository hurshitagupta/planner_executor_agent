import pytest

from progress_report import Step, generate_progress_report

def test_progress_report_in_progress():
    steps = [Step(id="1", action="Collect data", status="success"),
            Step(id="2", action="Process data", status="pending")]

    report = generate_progress_report(steps)

    assert report["total_steps"] == 2
    assert report["successful_steps"] == 1
    assert report["pending_steps"] == 1
    assert report["progress_percentage"] == 50.0
    assert report["execution_status"] == "in_progress"


def test_progress_report_complete():
    steps = [Step(id="1", action="Collect data", status="success"),
            Step(id="2", action="Prepare response", status="success")]

    report = generate_progress_report(steps)

    assert report["successful_steps"] == 2
    assert report["progress_percentage"] == 100.0
    assert report["execution_status"] == "complete"


def test_progress_report_blocked_on_failure():
    steps = [Step(id="1", action="Collect data", status="success"),
            Step(id="2", action="Verify data", status="failed"),
            Step(id="3", action="Prepare response", status="pending")]

    report = generate_progress_report(steps)

    assert report["failed_steps"] == 1
    assert report["execution_status"] == "blocked"


def test_running_step_is_reported():
    steps = [Step(id="1", action="Collect data", status="success"),
            Step(id="2", action="Process data", status="running")]

    report = generate_progress_report(steps)

    assert report["running_steps"] == 1
    assert report["execution_status"] == "in_progress"


def test_empty_steps_are_rejected():
    with pytest.raises(ValueError, match="Steps cannot be empty"):
        generate_progress_report([])

def test_invalid_status_is_rejected():
    steps = [Step(id="1", action="Collect data", status="unknown")]

    with pytest.raises(ValueError, match="Invalid step status"):
        generate_progress_report(steps)

def test_step_limit_is_enforced():
    steps = [Step(id=str(i), action=f"Action {i}") for i in range(11)]

    with pytest.raises(ValueError, match="Step limit exceeded"):
        generate_progress_report(steps)