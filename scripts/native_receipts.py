"""Read saved Harbor 0.26.0 receipts against the job's locked assignments."""

from hashlib import sha256
import json


def read_json(path):
    return json.loads(path.read_bytes())


def native_task_matches(task_id, configured, locked):
    if locked["type"] == "package":
        package = f"{task_id['org']}/{task_id['name']}"
        return package == locked["name"] == configured["name"] and task_id.get("ref") == configured["ref"]
    same_path = task_id["path"] == locked.get("path") == configured["path"]
    if locked["type"] == "git":
        return (
            same_path and task_id["git_url"] == locked["git_url"] == configured["git_url"]
            and task_id.get("git_commit_id") == configured["git_commit_id"]
        )
    return same_path and locked["type"] == "local" and configured["git_url"] is None


def job_plan(job, task_names, expected_lock_digest):
    lock_bytes = (job / "lock.json").read_bytes()
    digest = sha256(lock_bytes).hexdigest()
    if expected_lock_digest is not None and digest != expected_lock_digest:
        raise ValueError("job lock SHA-256 differs from the expected launch-time digest")
    lock = json.loads(lock_bytes)
    if lock["harbor"]["version"] != "0.26.0":
        raise ValueError("native job import expects a Harbor 0.26.0 lock")
    plan = {row["task"]["name"].rsplit("/", 1)[-1]: row for row in lock["trials"]}
    if set(plan) != task_names or len(plan) != len(lock["trials"]):
        raise ValueError("job lock and assignment manifest disagree on the scheduled tasks")
    return plan, digest


def trial_metrics(path, job_id, expected_agent, plan):
    trial = read_json(path)
    config = read_json(path.parent / "config.json")
    if trial["config"] != config or config["job_id"] != job_id:
        raise ValueError(f"trial receipt does not belong to this job in {path}")
    if trial["trial_name"] != path.parent.name or config["trial_name"] != path.parent.name:
        raise ValueError(f"trial name does not match the directory in {path}")
    if config["agent"] != expected_agent:
        raise ValueError(f"trial agent configuration differs from the job in {path}")
    task = trial["task_name"].rsplit("/", 1)[-1]
    lock = read_json(path.parent / "lock.json")
    if task not in plan or lock != plan[task]:
        raise ValueError(f"trial lock does not match the planned task in {path}")
    if not native_task_matches(trial["task_id"], config["task"], lock["task"]):
        raise ValueError(f"trial task identity does not match its lock in {path}")
    if not trial["finished_at"] or trial["exception_info"] is not None or trial["reward_valid"] is not True:
        return task, None
    if trial["verifier_environment_mode"] != "separate":
        raise ValueError(f"expected a separate verifier in {path}")
    metrics = trial["verifier_result"]["rewards"]
    reward = metrics["reward"]
    if type(reward) not in (int, float) or reward not in (0, 1):
        raise ValueError(f"expected a binary verifier reward in {path}")
    return task, metrics


def read_harbor_metrics(job, agent, task_names, expected_lock_digest=None):
    config = read_json(job / "config.json")
    if len(config["agents"]) != 1 or config["n_attempts"] != 1 or config["retry"]["max_retries"] != 0:
        raise ValueError("native job import requires one agent configuration, one attempt and no retries")
    expected_agent = config["agents"][0]
    if agent != (expected_agent.get("name") or expected_agent.get("import_path")):
        raise ValueError(f"agent {agent!r} does not match the job configuration")

    plan, digest = job_plan(job, task_names, expected_lock_digest)
    job_result = read_json(job / "result.json")
    if len(plan) != job_result["n_total_trials"]:
        raise ValueError("job result and lock disagree on the number of scheduled tasks")
    receipts = {}
    for path in sorted(job.glob("*/result.json")):
        task, metrics = trial_metrics(path, job_result["id"], expected_agent, plan)
        if task in receipts:
            raise ValueError(f"duplicate native trial receipt for {task}")
        receipts[task] = metrics
    return {task: receipts.get(task) for task in plan}, {
        "job_id": job_result["id"],
        "job_lock_sha256": digest,
        "trial_receipts_present": len(receipts),
    }
