"""Check the crossed Harbor calibration inputs and the installed HTTP controls."""

import argparse
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
import tomllib

import http_probe


WORKSPACES = {"personal": "desk", "shared": "team"}
LAYOUTS = ("imported", "current")
FORESTS = ("unrelated", "competing")
ARMS = ("control", "structural", "disclosed", "edit_hint")


def load_module(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fingerprint(task):
    return {p.relative_to(task).as_posix(): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode))
            for p in task.rglob("*") if p.is_file() and p.name not in ("instruction.md", "task.toml")}


def differences(a, b):
    return {p for p in a.keys() | b.keys() if a.get(p) != b.get(p)}


def compare_inputs(root, rows):
    cells = {(r["workspace"], r["layout"], r["forest"], r["arm"]) for r in rows}
    assert cells == set(product(WORKSPACES, LAYOUTS, FORESTS, ARMS)) and len(rows) == 32
    assert len({r["task"] for r in rows}) == 32
    assert len({r["base_issue"] for r in rows}) == 1
    assert {p.name for p in (root / "tasks").iterdir()} == {r["task"] for r in rows}
    source_maps, common_issues, sites = set(), set(), set()
    configs = []
    profiles = {}
    observations = {}
    for row in rows:
        workspace, layout, forest, arm = (row[key] for key in ("workspace", "layout", "forest", "arm"))
        handler = WORKSPACES[workspace]
        site = f"{handler}_{'normalize' if layout == 'imported' else 'persist'}.py"
        assert row["route"] == f"{workspace}-{layout}" and row["handler"] == handler
        assert row["reference_edit_file"] == site
        sites.add(site)
        task = root / "tasks" / row["task"]
        prompt, observation = (task / "instruction.md").read_text().strip().rsplit("\n\nStarting-state information: ", 1)
        if arm != "control":
            prompt, source_map = prompt.split("\n\nSource map ", 1)
            source_maps.add(source_map)
        common_issues.add(prompt)
        if arm == "disclosed":
            assert observation == f"The installed PATCH request reached `{handler}.save`."
            assert observation == observations.setdefault(handler, observation)
        elif arm == "edit_hint":
            assert observation == f"The reference repair changes `service/{site}`."
        else:
            assert observation == "The installed PATCH returned a JSON draft record."
        fixture = {"workspace": workspace, "layout": layout}
        assert json.loads((task / "tests/profile.json").read_text()) == fixture
        sample = json.loads((task / "environment/project/example.json").read_text())
        assert {k: sample[k] for k in fixture} == fixture
        assert f"/service/{site} " in (task / "solution/solve.sh").read_text()
        config = tomllib.loads((task / "task.toml").read_text())
        assert config["task"].pop("name") == f"draft-fixed-map/{row['task']}"
        configs.append(config)
        files = fingerprint(task)
        assert profiles.setdefault((workspace, layout, forest), files) == files
    assert len(source_maps) == len(common_issues) == 1 and len(sites) == 4
    assert all(x == configs[0] for x in configs)
    for forest in FORESTS:
        reference = profiles["personal", "imported", forest]
        for workspace, layout in product(WORKSPACES, LAYOUTS):
            candidate = profiles[workspace, layout, forest]
            changed = differences(candidate, reference)
            if (workspace, layout) == ("personal", "imported"):
                assert not changed
            else:
                assert changed == {"environment/project/example.json", "tests/profile.json", "solution/solve.sh"}
    for workspace, layout in product(WORKSPACES, LAYOUTS):
        left, right = (profiles[workspace, layout, f] for f in FORESTS)
        changed = differences(left, right)
        assert changed and all(p.startswith(("environment/project/tools/drafts/", "environment/project/tools/labels/")) for p in changed)
        assert len(left) == len(right)
        assert sum(len(b) for b, _ in left.values()) == sum(len(b) for b, _ in right.values())
        assert Counter(Path(p).suffix for p in left) == Counter(Path(p).suffix for p in right)
    return {"tasks": len(rows), "source_map_count": len(source_maps), "reference_edit_files": sorted(sites)}


def check_starting_profiles(dataset, rows):
    findings = []
    for row in rows:
        if row["arm"] != "disclosed":
            continue
        task = dataset / "tasks" / row["task"]
        project = task / "environment/project"
        with TemporaryDirectory(prefix="draft-fixed-map-") as directory:
            root = Path(directory).resolve()
            prefix = root / "installed"
            subprocess.run([project / "scripts/install", prefix], cwd=project, check=True, capture_output=True)
            deployed = prefix / "lib/draft-service"
            receipt = root / "calls"
            (root / "sitecustomize.py").write_text(f'''import sys
from pathlib import Path

def record(frame, event, arg):
    source = Path(frame.f_code.co_filename)
    if event == "call" and source.parent == Path({str(deployed)!r}):
        function = frame.f_code.co_name
        if function in ("save", "expand", "keep", "overlay", "replace"):
            with open({str(receipt)!r}, "a") as output:
                print(f"{{source.stem}}.{{function}}", file=output)

sys.setprofile(record)
''')
            launcher = prefix / "bin/draft-service"
            snapshot = project / "example.json"
            initial = http_probe.request_save(launcher, snapshot, http_probe.ENVIRONMENT)
            verified = http_probe.request_save(launcher, snapshot, http_probe.ENVIRONMENT | {"PYTHONPATH": str(root)})
            handler = row["handler"]
            normalizer, persistence = ("expand", "overlay") if row["layout"] == "imported" else ("keep", "replace")
            route = receipt.read_text().splitlines()
            assert route == [f"{handler}.save", f"{handler}_normalize.{normalizer}", f"{handler}_persist.{persistence}"]
            assert initial == verified and initial["status"] == 200 and initial["record"]["title"] == ""
            status = subprocess.run([project / "scripts/ci"], cwd=project, check=True, capture_output=True)
            assert not status.stdout and not status.stderr
        findings.append({"profile": row["route"], "forest": row["forest"], "http": initial, "trace": route, "ci_exit": 0})
    assert len(findings) == 8 and len({json.dumps(r["http"], sort_keys=True) for r in findings}) == 1
    return findings


def check_submissions(dataset, rows):
    controls = []
    references = {}
    for r in rows:
        if r["forest"] == "competing" and r["arm"] == "disclosed":
            path = dataset / "tasks" / r["task"] / "solution/solve.sh"
            heredoc = path.read_text().split("<<'PYCODE'\n", 1)[1].removesuffix("PYCODE\n")
            references[r["reference_edit_file"]] = heredoc
    assert len(references) == 4
    for r in rows:
        if r["arm"] != "disclosed":
            continue
        task = dataset / "tasks" / r["task"]
        grader = load_module("fixture_grader", task / "tests/grade.py")
        cases = {"unchanged": {}, **{name: {name: body} for name, body in references.items()}}
        cases["shared_handler"] = {f"{r['handler']}.py": '''def save(current, fields, layout):
    return {name: fields.get(name, current[name]) for name in ("title", "body")}
'''}
        cases["drops_explicit_empty_title"] = {f"{r['handler']}.py": '''def save(current, fields, layout):
    return {"title": fields.get("title") or current["title"], "body": fields.get("body", current["body"])}
'''}
        for label, changes in cases.items():
            with TemporaryDirectory(prefix="draft-grader-") as directory:
                root = Path(directory)
                source = root / "source"
                shutil.copytree(task / "environment/project/service", source)
                for name, content in changes.items():
                    (source / name).write_text(content)
                scratch = root / "verifier"
                scratch.mkdir()
                grade = grader.score(source, task / "tests/install", scratch, use_privilege_boundary=False)
            expected = int(label in (r["reference_edit_file"], "shared_handler"))
            target_rate = 5 / 6 if label == "drops_explicit_empty_title" else expected
            assert grade["reward"] == expected and grade["target_case_pass_rate"] == target_rate, (r, label, grade)
            assert grade["preserved_case_pass_rate"] == 1, (r, label, grade)
            controls.append({"profile": r["route"], "forest": r["forest"], "submission": label, **grade})
    assert len(controls) == 56
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, nargs="?", default=Path(".harbor/fixed-map"))
    dataset = parser.parse_args().dataset.resolve()
    sys.dont_write_bytecode = True
    rows = json.loads((dataset / "assignments.json").read_bytes())
    compared = compare_inputs(dataset, rows)
    print(json.dumps({"inputs": compared, "starting_profiles": check_starting_profiles(dataset, rows),
                      "local_controls": check_submissions(dataset, rows)}, indent=2))


if __name__ == "__main__":
    main()
