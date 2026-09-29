from dataclasses import dataclass, asdict
from pathlib import Path
from time import perf_counter
import json

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

MAX_TRANSITIONS = 3

@dataclass
class Step:
    id: str
    action: str
    status: str = "pending"


def validate_step(step: Step) -> None:
    if not step.id.strip():
        raise ValueError("Step id cannot be empty.")

    if not step.action.strip():
        raise ValueError("Step action cannot be empty.")

    if step.status not in {"pending", "running", "success", "failed"}:
        raise ValueError("Invalid step status.")


def update_status(step: Step, new_status: str) -> None:
    """
    Allow only the expected state transitions:
    pending -> running
    running -> success / failed
    """

    allowed_transitions = {
        "pending": {"running"},
        "running": {"success", "failed"},
        "success": set(),
        "failed": set(),
    }

    if new_status not in allowed_transitions[step.status]:
        raise ValueError(f"Invalid transition: {step.status} -> {new_status}")

    step.status = new_status

def execute_step(step: Step, should_fail: bool = False) -> list[dict]:
    validate_step(step)

    trace = [{"step_id": step.id, "status": step.status}]

    transition_count = 0

    update_status(step, "running")
    transition_count += 1

    trace.append({"step_id": step.id, "status": step.status})

    if transition_count >= MAX_TRANSITIONS:
        raise RuntimeError("Transition limit reached.")

    if should_fail:
        update_status(step, "failed")
    else:
        update_status(step, "success")

    transition_count += 1

    trace.append({"step_id": step.id, "status": step.status})

    return trace

def run() -> dict:
    start = perf_counter()

    success_step = Step(id="1", action="Collect customer details")

    failed_step = Step(id="2", action="Process customer request")

    success_trace = execute_step(success_step)

    failure_trace = execute_step(failed_step, should_fail=True)

    duration_ms = round((perf_counter() - start) * 1000, 3)

    return {
        "success_step": asdict(success_step),
        "failed_step": asdict(failed_step),
        "success_trace": success_trace,
        "failure_trace": failure_trace,
        "total_steps": 2,
        "successful_steps": 1,
        "failed_steps": 1,
        "duration_ms": duration_ms,
    }


def save_output(result: dict) -> None:
    output_file = OUTPUT_DIR / "step_state_machine.txt"

    output_file.write_text(json.dumps(result, indent=2), encoding="utf-8")

def main():
    result = run()
    save_output(result)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()