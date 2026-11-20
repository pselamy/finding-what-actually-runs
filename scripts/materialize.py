#!/usr/bin/env python3
"""Generate the disclosed fixed-map Harbor tasks from tracked source."""

import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from shutil import copytree
from tempfile import TemporaryDirectory


FIXTURE = Path(__file__).resolve().parents[1] / "calibrations" / "fixed-map"
WORKSPACES = {"personal": "desk", "shared": "team"}
LAYOUTS = {"imported": "normalize", "current": "persist"}
FORESTS = ("unrelated", "competing")
ARMS = ("control", "structural", "disclosed", "edit_hint")
NEUTRAL = "The installed PATCH returned a JSON draft record."


def write_json(path, data, **options):
    path.write_text(json.dumps(data, **options) + "\n", encoding="utf-8")


def write_task(tasks, workspace, layout, forest, arm):
    profile = f"{workspace}-{layout}"
    seed = f"draft-fixed-map-v1:{profile}:{forest}:{arm}"
    task_id = "draft-" + sha256(seed.encode()).hexdigest()[:12]
    handler = WORKSPACES[workspace]
    kind = LAYOUTS[layout]
    site = f"{handler}_{kind}.py"
    task = tasks / task_id

    copytree(FIXTURE / "template", task)
    copytree(FIXTURE / "forests" / forest, task, dirs_exist_ok=True)
    settings = {"workspace": workspace, "layout": layout}
    example = task / "environment" / "project" / "example.json"
    write_json(example, json.loads(example.read_bytes()) | settings, indent=2)
    write_json(task / "tests" / "profile.json", settings, sort_keys=True)

    prompt = [(FIXTURE / "issue.md").read_text(encoding="utf-8").rstrip()]
    if arm != "control":
        prompt.append((FIXTURE / "source-map.md").read_text(encoding="utf-8").rstrip())
    observation = {
        "control": NEUTRAL,
        "structural": NEUTRAL,
        "disclosed": f"The installed PATCH request reached `{handler}.save`.",
        "edit_hint": f"The reference repair changes `service/{site}`.",
    }[arm]
    prompt.append(f"Starting-state information: {observation}")
    (task / "instruction.md").write_text("\n\n".join(prompt) + "\n", encoding="utf-8")
    config = (FIXTURE / "task.toml.in").read_text(encoding="utf-8")
    (task / "task.toml").write_text(config.replace("@TASK_ID@", task_id), encoding="utf-8")

    fix = (FIXTURE / "repairs" / f"{kind}.py").read_text(encoding="utf-8")
    solution = task / "solution" / "solve.sh"
    solution.parent.mkdir()
    solution.write_text(
        f"#!/bin/sh\nset -eu\ncat > /app/drafts/service/{site} <<'PYCODE'\n{fix}PYCODE\n",
        encoding="utf-8",
    )
    solution.chmod(0o755)
    return {
        "task": task_id,
        "base_issue": "draft_partial_save",
        "route": profile,
        "forest": forest,
        "arm": arm,
        "handler": handler,
        "layout": layout,
        "workspace": workspace,
        "reference_edit_file": site,
    }


def materialize(output):
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".generate-", dir=output.parent) as scratch:
        staged = Path(scratch) / "dataset"
        tasks = staged / "tasks"
        tasks.mkdir(parents=True)
        rows = [
            write_task(tasks, workspace, layout, forest, arm)
            for workspace, layout, forest, arm in product(WORKSPACES, LAYOUTS, FORESTS, ARMS)
        ]
        write_json(staged / "assignments.json", rows, indent=2)
        staged.rename(output)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(".harbor/fixed-map"))
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error(f"{args.output} already exists. Choose a fresh output directory.")
    print(f"Materialized {materialize(args.output)} tasks in {args.output}")


if __name__ == "__main__":
    main()
