#!/usr/bin/env python3
"""Lifecycle gate checks for CERES governance orchestrator.

This is a lightweight guardrail to enforce:
- no execution before a visible Task Plan exists (`todo.md` with unchecked tasks)
- optional Gap Ledger presence
- optional Prompt Debug Report presence

Use this as a pre-execution gate; fail fast if prerequisites are missing. Optionally logs
gate outcomes via the umbrella `scripts/log_event.py`.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path


def has_unchecked_tasks(todo_path: Path) -> bool:
    if not todo_path.exists():
        return False
    for line in todo_path.read_text().splitlines():
        if line.strip().startswith("- [ ]"):
            return True
    return False


def check_ceres_todo(todo_path: Path) -> bool:
    if not todo_path.exists():
        return False
    lines = todo_path.read_text().splitlines()
    if not lines:
        return False
    return "CERES" in lines[0]


def log_event(log_helper: Path, status: str, message: str, context: dict) -> None:
    if not log_helper:
        return
    if not log_helper.exists():
        sys.stderr.write(f"Log helper not found at {log_helper}
")
        return
    cmd = [
        sys.executable,
        str(log_helper),
        "--type",
        "gate",
        "--status",
        status,
        "--message",
        message,
        "--context",
        json.dumps(context),
    ]
    subprocess.run(cmd, check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="CERES lifecycle gate")
    parser.add_argument("--todo", type=Path, default=Path("todo.md"), help="Path to todo.md")
    parser.add_argument("--gap-ledger", type=Path, help="Optional path to gap ledger file")
    parser.add_argument("--prompt-report", type=Path, help="Optional path to prompt debug report")
    parser.add_argument("--require-ceres-todo", action="store_true", help="Fail if todo.md does not look like CERES template")
    parser.add_argument("--task-id", help="Optional task identifier for logging context")
    parser.add_argument(
        "--log-helper",
        type=Path,
        help="Optional path to umbrella scripts/log_event.py to log gate outcome",
    )
    args = parser.parse_args()

    failures = []
    context = {
        "todo": str(args.todo),
        "gap_ledger": str(args.gap_ledger) if args.gap_ledger else None,
        "prompt_report": str(args.prompt_report) if args.prompt_report else None,
        "task_id": args.task_id,
    }

    if not has_unchecked_tasks(args.todo):
        failures.append(f"Missing or empty task plan: {args.todo}")

    if args.gap_ledger and not args.gap_ledger.exists():
        failures.append(f"Gap ledger missing: {args.gap_ledger}")

    if args.prompt_report and not args.prompt_report.exists():
        failures.append(f"Prompt debug report missing: {args.prompt_report}")

    if args.require_ceres_todo and not check_ceres_todo(args.todo):
        failures.append(f"todo.md does not appear to be the CERES template: {args.todo}")

    if failures:
        sys.stderr.write("Lifecycle gate failed:
" + "
".join(f"- {f}" for f in failures) + "
")
        log_event(args.log_helper, "fail", "lifecycle gate failed", {**context, "failures": failures})
        sys.exit(1)

    sys.stdout.write("Lifecycle gate passed
")
    log_event(args.log_helper, "pass", "lifecycle gate passed", context)


if __name__ == "__main__":
    main()
