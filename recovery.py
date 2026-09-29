from dataclasses import dataclass, asdict
from pathlib import Path
from time import perf_counter
import json

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_RETRIES = 2
MAX_REPLANS = 1

@dataclass
class Step:
    id: str
    action: str
    status: str = "pending"

def validate_goal(goal: str) -> None:
    if not isinstance(goal, str):
        raise ValueError("Goal must be a string.")

    if not goal.strip():
        raise ValueError("Goal cannot be empty.")

def execute_step(step: Step, failure_type: str | None = None, attempt: int = 1) -> str:
    """Simulates execution behavior.
    transient: first attempt fails, later attempt succeeds
    permanent: always fails"""

    if not step.action.strip():
        raise ValueError("Step action cannot be empty.")

    step.status = "running"

    if failure_type == "transient" and attempt == 1:
        step.status = "pending"
        return "transient_failure"

    if failure_type == "permanent":
        step.status = "failed"
        return "permanent_failure"

    step.status = "success"
    return "success"

def execute_with_retry(step: Step, failure_type: str | None = None) -> dict:
    """ Retry only transient failures. """

    attempts = []

    for attempt in range(1, MAX_RETRIES + 2):
        result = execute_step(step, failure_type=failure_type, attempt=attempt)

        attempts.append({"attempt": attempt, "result": result})

        if result == "success":
            return {"status": "success", "attempts": attempts}

        if result == "permanent_failure":
            return {"status": "failed", "attempts": attempts}

    step.status = "failed"

    return {"status": "failed", "attempts": attempts}

def replan(goal: str, steps: list[Step], evidence_invalidates_plan: bool, replan_count: int) -> tuple[list[Step], int]:
    """ Replan only when evidence invalidates the remaining plan. Completed steps are preserved. """

    if not evidence_invalidates_plan:
        return steps, replan_count

    if replan_count >= MAX_REPLANS:
        raise RuntimeError("Replan limit reached.")

    completed_steps = [step for step in steps if step.status == "success"]

    revised_steps = completed_steps + [
        Step(id="3R", action="Use revised information"),
        Step(id="4R", action="Prepare revised response")]

    return revised_steps, replan_count + 1


def run() -> dict:
    start = perf_counter()

    goal = "Resolve customer request"
    validate_goal(goal)

    steps = [Step(id="1", action="Collect customer information", status="success"),
            Step(id="2", action="Verify information"),
            Step(id="3", action="Prepare response")]

    retry_result = execute_with_retry(steps[1], failure_type="transient")

    revised_steps, replan_count = replan(goal=goal, steps=steps, evidence_invalidates_plan=True, replan_count=0)

    duration_ms = round((perf_counter() - start) * 1000, 3)

    result = {
        "goal": goal,
        "retry_result": retry_result,
        "replan_count": replan_count,
        "revised_steps": [asdict(step) for step in revised_steps],
        "completed_steps_preserved": [step.id for step in revised_steps if step.status == "success"],
        "duration_ms": duration_ms,
    }

    return result

def save_output(result: dict) -> None:
    output_file = OUTPUT_DIR / "recovery.txt"
    output_file.write_text(json.dumps(result, indent=2), encoding="utf-8")

def main():
    result = run()
    save_output(result)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()