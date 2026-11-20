#!/usr/bin/env python3
"""Require complete, valid Harbor control receipts and expected preservation."""

import argparse
from pathlib import Path

from native_receipts import read_harbor_metrics, read_json


def verify(job, tasks, agent):
    expected = int(agent == "oracle")
    result = read_json(job / "result.json")
    stats = result["stats"]
    if not result["finished_at"] or stats["n_completed_trials"] != len(tasks) or stats["n_errored_trials"] != 0:
        raise ValueError("native control job did not complete every trial without errors")
    receipts, _ = read_harbor_metrics(job, agent, tasks)
    expected_metrics = {
        "submission_present": 1,
        "reward": expected,
        "target_case_pass_rate": expected,
        "preserved_case_pass_rate": 1,
    }
    for task, rewards in receipts.items():
        if rewards is None:
            raise ValueError(f"{task} lacks a valid separate verifier result for {agent}")
        for name, value in expected_metrics.items():
            observed = rewards.get(name)
            if type(observed) not in (int, float) or observed != value:
                raise ValueError(f"{task} produced {name}={observed!r}, expected {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("assignments", type=Path)
    parser.add_argument("job", type=Path)
    parser.add_argument("agent", choices=("oracle", "nop"))
    parser.add_argument("--task", action="append", help="Expect only the named task. May be repeated.")
    args = parser.parse_args()
    try:
        manifest = read_json(args.assignments)
        tasks = {row["task"] for row in manifest}
        if not tasks or len(tasks) != len(manifest):
            raise ValueError("assignment manifest has no tasks or contains duplicates")
        if args.task:
            if not set(args.task) <= tasks:
                raise ValueError("requested task is absent from the manifest")
            tasks = set(args.task)
        verify(args.job, tasks, args.agent)
    except (KeyError, OSError, TypeError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")
    print(f"Verified {len(tasks)} {args.agent} control receipts with full preservation.")


if __name__ == "__main__":
    main()
