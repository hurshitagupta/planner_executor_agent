from dataclasses import dataclass, asdict
from pathlib import Path
from time import perf_counter
import json

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_STEPS = 5

@dataclass
class Step:
    id: str
    action: str
    status: str = "pending"


def validate_goal(goal: str) -> None:
    """Validate the incoming goal before planning."""

    if not isinstance(goal, str):
        raise ValueError("Goal must be a string.")

    if not goal.strip():
        raise ValueError("Goal cannot be empty.")

    if len(goal) > 200:
        raise ValueError("Goal is too long.")


def planner(goal: str) -> list[Step]:
    """ Planner is responsible only for creating the plan. It does not execute any step. """

    validate_goal(goal)

    steps = [
        Step(id="1", action=f"Collect information for: {goal}"),
        Step(id="2", action="Process collected information"),
        Step(id="3", action="Prepare final response"),
    ]

    if len(steps) > MAX_STEPS:
        raise ValueError("Plan exceeds step limit.")

    return steps


def execute_step(step: Step) -> Step:
    """ Execute one existing step. Executor does not create new plan steps. """

    if not step.action.strip():
        step.status = "failed"
        return step

    step.status = "running"
    step.status = "success"

    return step


def executor(steps: list[Step]) -> list[Step]:
    """ Execute the plan created by the planner. """

    if not steps:
        raise ValueError("Executor received an empty plan.")

    if len(steps) > MAX_STEPS:
        raise ValueError("Execution rejected: step limit exceeded.")

    for step in steps:
        execute_step(step)

        if step.status == "failed":
            break

    return steps


def run(goal: str) -> dict:
    start = perf_counter()

    plan = planner(goal)
    result = executor(plan)

    duration_ms = round((perf_counter() - start) * 1000, 3)

    trace = {
        "goal": goal,
        "steps": [asdict(step) for step in result],
        "step_count": len(result),
        "successful_steps": sum(1 for step in result if step.status == "success"),
        "failed_steps": sum(1 for step in result if step.status == "failed"),
        "duration_ms": duration_ms,
    }

    return trace


def save_trace(trace: dict) -> None:
    output_file = OUTPUT_DIR / "planner_executor_split.txt"

    output_file.write_text(json.dumps(trace, indent=2), encoding="utf-8")


def main():
    goal = "Prepare customer order summary"
    trace = run(goal)
    save_trace(trace)

    print(json.dumps(trace, indent=2))


if __name__ == "__main__":
    main()