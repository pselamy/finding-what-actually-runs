"""Regression controls for the required native receipt check."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from check_native import verify


class NativeReceiptTests(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.job = Path(scratch.name)
        self.agent = {"name": "oracle"}
        self.task = "draft-test"
        self.trial = self.job / "draft-test__attempt"
        self.trial.mkdir()
        task_path = f"tasks/{self.task}"
        locked = {"task": {"type": "local", "name": self.task, "path": task_path}}
        self.trial_config = {
            "agent": self.agent,
            "job_id": "control-job",
            "trial_name": self.trial.name,
            "task": {"path": task_path, "git_url": None},
        }
        self.result = {
            "config": self.trial_config,
            "task_name": f"drafts/{self.task}",
            "task_id": {"path": task_path},
            "trial_name": self.trial.name,
            "finished_at": "2026-11-20T18:00:00Z",
            "exception_info": None,
            "reward_valid": True,
            "verifier_environment_mode": "separate",
            "verifier_result": {"rewards": {
                "reward": 1,
                "submission_present": 1,
                "target_case_pass_rate": 1.0,
                "preserved_case_pass_rate": 1.0,
            }},
        }
        self.save(self.job / "lock.json", {"harbor": {"version": "0.26.0"}, "trials": [locked]})
        self.save(self.job / "config.json", {"agents": [self.agent], "n_attempts": 1, "retry": {"max_retries": 0}})
        self.save(self.job / "result.json", {
            "id": "control-job",
            "finished_at": "2026-11-20T18:00:00Z",
            "n_total_trials": 1,
            "stats": {"n_completed_trials": 1, "n_errored_trials": 0},
        })
        self.save(self.trial / "lock.json", locked)
        self.save(self.trial / "config.json", self.trial_config)
        self.save(self.trial / "result.json", self.result)

    def save(self, path, value):
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_matching_complete_receipt(self):
        verify(self.job, {self.task}, "oracle")

    def test_foreign_receipt_cannot_attest_to_current_job(self):
        self.trial_config["job_id"] = "earlier-job"
        self.save(self.trial / "config.json", self.trial_config)
        self.save(self.trial / "result.json", self.result)
        with self.assertRaisesRegex(ValueError, "does not belong"):
            verify(self.job, {self.task}, "oracle")

    def test_reward_with_incomplete_target_cases_is_rejected(self):
        self.result["verifier_result"]["rewards"]["target_case_pass_rate"] = 0.5
        self.save(self.trial / "result.json", self.result)
        with self.assertRaisesRegex(ValueError, "target_case_pass_rate"):
            verify(self.job, {self.task}, "oracle")

    def test_unfinished_trial_cannot_attest_to_current_job(self):
        self.result["finished_at"] = None
        self.save(self.trial / "result.json", self.result)
        with self.assertRaisesRegex(ValueError, "lacks a valid"):
            verify(self.job, {self.task}, "oracle")


if __name__ == "__main__":
    unittest.main()
