import pytest

from dependency_readiness import Step, is_ready, next_ready, execute_ready_step

def test_step_without_dependencies_is_ready():
    steps = [Step(id="1", action="Collect data", dependencies=[])]
    assert is_ready(steps[0], steps) is True

def test_step_is_ready_when_dependency_succeeds():
    steps = [Step(id="1", action="Collect data", dependencies=[], status="success"),
            Step(id="2", action="Process data", dependencies=["1"])]

    assert is_ready(steps[1], steps) is True


def test_step_is_blocked_when_dependency_is_pending():
    steps = [Step(id="1", action="Collect data", dependencies=[], status="pending"),
            Step(id="2", action="Process data", dependencies=["1"])]

    assert is_ready(steps[1], steps) is False


def test_step_is_blocked_when_dependency_failed():
    steps = [Step(id="1", action="Collect data", dependencies=[], status="failed"),
            Step(id="2", action="Process data", dependencies=["1"])]

    assert is_ready(steps[1], steps) is False


def test_next_ready_returns_correct_step():
    steps = [Step(id="1", action="Collect data", dependencies=[], status="success"),
            Step(id="2", action="Process data", dependencies=["1"])]

    step = next_ready(steps)

    assert step is not None
    assert step.id == "2"


def test_unknown_dependency_is_rejected():
    steps = [Step(id="1", action="Process data", dependencies=["99"])]

    with pytest.raises(ValueError, match="Unknown dependency"):
        next_ready(steps)


def test_no_ready_step_returns_blocked():
    steps = [Step(id="1", action="Collect data", dependencies=[], status="failed"),
            Step(id="2", action="Process data", dependencies=["1"])]

    result = execute_ready_step(steps)

    assert result["status"] == "blocked"