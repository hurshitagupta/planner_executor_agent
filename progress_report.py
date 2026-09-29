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
    status: str = "pending"


def validate_steps(steps: list[Step]) -> None:
    if not steps:
        raise ValueError("Steps cannot be empty.")

    if len(steps) > MAX_STEPS:
        raise ValueError("Step limit exceeded.")

    valid_statuses = {"pending", "running", "success", "failed"}

    for step in steps:
        if not step.id.strip():
            raise ValueError("Step id cannot be empty.")

        if not step.action.strip():
            raise ValueError("Step action cannot be empty.")

        if step.status not in valid_statuses:
            raise ValueError(f"Invalid step status: {step.status}")

def generate_progress_report(steps: list[Step]) -> dict:
    validate_steps(steps)
    total_steps = len(steps)

    successful_steps = sum(1 for step in steps if step.status == "success")

    failed_steps = sum(1 for step in steps if step.status == "failed")

    pending_steps = sum(1 for step in steps if step.status == "pending")

    running_steps = sum(1 for step in steps if step.status == "running")

    progress_percentage = round((successful_steps / total_steps) * 100, 2)

    if successful_steps == total_steps:
        execution_status = "complete"

    elif failed_steps > 0:
        execution_status = "blocked"

    else:
        execution_status = "in_progress"

    return {
        "total_steps": total_steps,
        "successful_steps": successful_steps,
        "failed_steps": failed_steps,
        "pending_steps": pending_steps,
        "running_steps": running_steps,
        "progress_percentage": progress_percentage,
        "execution_status": execution_status,
        "steps": [asdict(step) for step in steps]}


def run() -> dict:
    start = perf_counter()

    steps = [Step(id="1", action="Collect customer details", status="success"),
            Step(id="2", action="Verify customer details", status="success"),
            Step(id="3", action="Prepare response", status="pending")]

    report = generate_progress_report(steps)

    duration_ms = round((perf_counter() - start) * 1000, 3)
    report["duration_ms"] = duration_ms
    return report

def save_output(report: dict) -> None:
    output_file = OUTPUT_DIR / "progress_report.txt"

    output_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

def main():
    report = run()
    save_output(report)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()