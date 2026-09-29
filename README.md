# Implement Planner-Executor

## Overview

This project implements the core behavior of a Planner-Executor architecture.

The assessment is divided into five tasks:

1. Planner/Executor Split
2. Step State Machine
3. Dependency Readiness
4. Recovery
5. Progress Report

Each task includes:

- Source code
- Automated tests
- Saved execution output
- Saved test output
- Validation and limits
- Success and failure behavior
- Basic measurements and traceability

---

## Project Structure

```text
planner_executor/
│
├── planner_executor_split.py
├── step_state_machine.py
├── dependency_readiness.py
├── recovery.py
├── progress_report.py
│
├── tests/
│   ├── test_planner_executor_split.py
│   ├── test_step_state_machine.py
│   ├── test_dependency_readiness.py
│   ├── test_recovery.py
│   └── test_progress_report.py
│
├── outputs/
│   ├── planner_executor_split.txt
│   ├── test_planner_executor_split.txt
│   ├── step_state_machine.txt
│   ├── test_step_state_machine.txt
│   ├── dependency_readiness.txt
│   ├── test_dependency_readiness.txt
│   ├── recovery.txt
│   ├── test_recovery.txt
│   ├── progress_report.txt
│   └── test_progress_report.txt
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Task 1 — Planner/Executor Split

## Objective

Separate planning from execution.

The planner is responsible for creating steps from a goal, while the executor is responsible only for executing the steps already created.

This prevents planning and execution responsibilities from being mixed together.

## Implementation

The `planner()` function:

- Validates the goal
- Creates a structured list of steps
- Applies a maximum step limit

The `executor()` function:

- Receives the plan
- Executes existing steps
- Does not create new planning steps
- Stops when a step fails

The implementation also records:

- Total number of steps
- Successful steps
- Failed steps
- Execution duration

## Run

```bash
python planner_executor_split.py
```

## Run Tests

```bash
pytest tests/test_planner_executor_split.py -v
```

## Evidence

Execution output:

```text
outputs/planner_executor_split.txt
```

Test output:

```text
outputs/test_planner_executor_split.txt
```

---

# Task 2 — Step State Machine

## Objective

Control how a step moves between execution states.

The implementation uses the states already represented by the starter implementation:

```text
pending → running → success
                  → failed
```

A step cannot directly move between invalid states.

For example:

```text
pending → success
```

is rejected because the step must first enter the `running` state.

## Implementation

The main states are:

- `pending`
- `running`
- `success`
- `failed`

The `update_status()` function validates every state transition.

Completed or failed steps cannot restart.

The implementation also records the complete state transition trace for each executed step.

## Run

```bash
python step_state_machine.py
```

## Run Tests

```bash
pytest tests/test_step_state_machine.py -v
```

## Evidence

Execution output:

```text
outputs/step_state_machine.txt
```

Test output:

```text
outputs/test_step_state_machine.txt
```

---

# Task 3 — Dependency Readiness

## Objective

Ensure that a step becomes ready only after all its required dependencies have completed successfully.

A dependent step cannot execute simply because it appears next in the plan.

## Implementation

Each `Step` contains a list of dependency IDs.

The `is_ready()` function checks:

- The step must still be `pending`
- Every dependency must exist
- Every dependency must have status `success`

The `next_ready()` function returns the next step that satisfies these conditions.

If no step is ready, execution returns a blocked result.

## Run

```bash
python dependency_readiness.py
```

## Run Tests

```bash
pytest tests/test_dependency_readiness.py -v
```

## Evidence

Execution output:

```text
outputs/dependency_readiness.txt
```

Test output:

```text
outputs/test_dependency_readiness.txt
```

---

# Task 4 — Recovery

## Objective

Recover safely from execution failures while respecting retry and replanning boundaries.

The implementation distinguishes between transient and permanent failures.

## Retry Behavior

Only transient failures are retried. Permanent failures are not retried.


Retries are capped using `MAX_RETRIES`.

## Replanning Behavior

Replanning happens only when new evidence invalidates the remaining plan.

If the evidence does not invalidate the plan, the current plan is preserved.

During replanning:

- Successfully completed steps are preserved
- Remaining invalid steps are replaced
- The original goal is kept unchanged
- Replanning is limited using `MAX_REPLANS`

This follows the assessment boundary:

> The planner should be called again only when evidence invalidates the remaining plan.

## Run

```bash
python recovery.py
```

## Run Tests

```bash
pytest tests/test_recovery.py -v
```

## Evidence

Execution output:

```text
outputs/recovery.txt
```

Test output:

```text
outputs/test_recovery.txt
```

---

# Task 5 — Progress Report

## Objective

Provide observable progress information for a planner-executor run.

The progress report summarizes the current state of all plan steps.

## Implementation

The report includes:

- Total steps
- Successful steps
- Failed steps
- Pending steps
- Running steps
- Progress percentage
- Overall execution status
- Individual step information

The overall status can be:

- `complete`
- `in_progress`
- `blocked`

A failure results in a `blocked` execution status.

## Run

```bash
python progress_report.py
```

## Run Tests

```bash
pytest tests/test_progress_report.py -v
```

## Evidence

Execution output:

```text
outputs/progress_report.txt
```

Test output:

```text
outputs/test_progress_report.txt
```
---

# Guardrails

The assessment requires guardrails across the tasks.

1. Step Limits : Hard limits are used where applicable to prevent uncontrolled execution.

2. Validation : Inputs and execution state are validated before processing.

3. Retry : Retries are demonstrated in the Recovery task. Only failures classified as transient are retried. Permanent failures stop immediately. Retry attempts are capped.

4. Timeout : The implementation uses only small, deterministic local Python operations and does not call external APIs, tools, networks, or long-running processes. Therefore, there is no external operation requiring a per-call timeout in the current implementation.

5. Secret Hygiene: The project does not require credentials, API keys, or external services.No secrets are stored in the source code. If external services are added later, credentials should be loaded using environment variables rather than hardcoded values.

---

# Measurements and Traceability

Each task provides observable evidence through saved output files.

Measurements include values such as:
- Step counts
- Successful steps
- Failed steps
- Retry attempts
- Replan count
- Progress percentage
- Execution duration

Execution traces allow the examiner to follow:
- Step status changes
- Dependency decisions
- Retry attempts
- Recovery decisions
- Replanning behavior
- Progress state

---

# Run All Tests

To run the complete automated test suite:

```bash
pytest tests/ -v
```

---

# Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

The implementation itself uses the Python standard library.

`pytest` is required for automated testing.

---

# Summary

This project demonstrates a basic Planner-Executor architecture with:

- Separate planning and execution responsibilities
- Controlled step state transitions
- Dependency-based execution readiness
- Retry and replanning recovery boundaries
- Observable progress reporting
- Validation and bounded execution
- Automated success and failure tests
- Saved outputs and measurements
