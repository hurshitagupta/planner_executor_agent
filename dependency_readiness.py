from dataclasses import dataclass, asdict
from pathlib import Path
from time import perf_counter
import json

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_STEPS = 10

@dataclass
class Step:
    id: str
    action: str
    dependencies: list[str]
    status: str = "pending"

def validate_steps(steps: list[Step]) -> None:
    if not steps:
        raise ValueError("Plan cannot be empty.")

    if len(steps) > MAX_STEPS:
        raise ValueError("Step limit exceeded.")

    ids = {step.id for step in steps}

    for step in steps:
        if not step.id.strip():
            raise ValueError("Step id cannot be empty.")

        if not step.action.strip():
            raise ValueError("Step action cannot be empty.")

        for dependency in step.dependencies:
            if dependency not in ids:
                raise ValueError(f"Unknown dependency: {dependency}")

def is_ready(step: Step, steps: list[Step]) -> bool:
    """ A step is ready only if it is pending and all dependency steps have succeeded."""

    if step.status != "pending":
        return False

    for dependency_id in step.dependencies:
        dependency_step = next(item for item in steps if item.id == dependency_id)

        if dependency_step.status != "success":
            return False

    return True


def next_ready(steps: list[Step]) -> Step | None:
    validate_steps(steps)

    for step in steps:
        if is_ready(step, steps):
            return step

    return None

def execute_ready_step(steps: list[Step]) -> dict:
    step = next_ready(steps)

    if step is None:
        return {"status": "blocked", "message": "No step is ready for execution."}

    step.status = "running"
    step.status = "success"

    return {
        "status": "executed",
        "step_id": step.id,
        "action": step.action,
    }

def run() -> dict:
    start = perf_counter()

    steps = [
        Step(id="1", action="Collect customer details", dependencies=[], status="success"),
        Step(id="2", action="Verify customer details", dependencies=["1"]),
        Step(id="3", action="Prepare response", dependencies=["2"]),
    ]

    ready_before = next_ready(steps)
    first_execution = execute_ready_step(steps)
    ready_after = next_ready(steps)

    blocked_steps = [step.id for step in steps
        if step.status == "pending" and not is_ready(step, steps)]

    duration_ms = round((perf_counter() - start) * 1000, 3)

    return {
        "steps": [asdict(step) for step in steps],
        "ready_before_execution": (ready_before.id if ready_before else None),
        "first_execution": first_execution,
        "ready_after_execution": (ready_after.id if ready_after else None),
        "blocked_steps": blocked_steps,
        "total_steps": len(steps),
        "duration_ms": duration_ms,
    }


def save_output(result: dict) -> None:
    output_file = OUTPUT_DIR / "dependency_readiness.txt"

    output_file.write_text(json.dumps(result, indent=2), encoding="utf-8")

def main():
    result = run()
    save_output(result)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()