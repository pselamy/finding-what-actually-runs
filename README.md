# Finding What Actually Runs

A Harbor calibration for coding agents repairing software in misleading repositories.

A draft service erases fields during a partial save. Its visible checks pass and nearby code looks relevant. The calibration varies which handler serves the request, which downstream step drops the value, and whether the repository contains plausible inactive code. A separate verifier reinstalls the submitted service and checks the HTTP behavior.

**Release scope.** This is one disclosed synthetic issue with 32 matched variants. The reference repairs and verifier cases are public. Use it to qualify a Harbor runner, test a harness integration, and develop a study protocol.

## Quickstart

Use a shell with Git, Python 3.12 or 3.13, [uv](https://docs.astral.sh/uv/getting-started/installation/), and a running Docker daemon with Compose and Buildx. Run these commands in a fresh clone.

```sh
git clone https://github.com/pselamy/finding-what-actually-runs.git
cd finding-what-actually-runs
python3 scripts/materialize.py
uv sync --locked
uv run --locked harbor run -p .harbor/fixed-map/tasks -a oracle -e docker -n 4 -r 0 --jobs-dir .harbor/jobs --job-name oracle
python3 scripts/check_native.py .harbor/fixed-map/assignments.json .harbor/jobs/oracle oracle
```

The last command prints `Verified 32 oracle control receipts with full preservation.` Run the unchanged-submission control with the same dataset.

```sh
uv run --locked harbor run -p .harbor/fixed-map/tasks -a nop -e docker -n 4 -r 0 --jobs-dir .harbor/jobs --job-name nop
python3 scripts/check_native.py .harbor/fixed-map/assignments.json .harbor/jobs/nop nop
```

Every reference submission should earn reward 1. Every unchanged submission should earn reward 0. Both should preserve all required existing behavior. The checker requires complete, valid separate-verifier receipts in both jobs.

## Use with an evaluation harness

Point Harbor at `.harbor/fixed-map/tasks`. Each generated directory is an ordinary Harbor task. Keep the checkout, assignment manifest, solutions, and verifier files in the evaluator workspace. Give the agent only its assigned instruction and task environment. The shipped agent and verifier tasks run without outbound network access. Use the network policy supported by your runner for a model that needs provider access, and record any resulting configuration changes. The scripted controls require no provider credentials.

Import a complete native job with one agent, one attempt per task, and automatic retries disabled.

```sh
python3 scripts/score_study.py .harbor/fixed-map/assignments.json .harbor/jobs/oracle oracle \
  --harbor-job --with-edit-hint --profiles-per-issue 4
```

Harbor is pinned to 0.26.0 in [pyproject.toml](pyproject.toml), with transitive dependencies in [uv.lock](uv.lock). The workload, assignment design, grading scope and interpretation are in [the methodology](docs/methodology.md).

## Develop

Edit the [calibration source](calibrations/fixed-map/), then generate a fresh dataset and run the local qualification.

```sh
python3 scripts/materialize.py --output .harbor/check
python3 scripts/check_calibration.py .harbor/check > .harbor/local-controls.json
```

This checks prompt and fixture matching, reproduces eight installed starting runs, and exercises 56 known submissions. CI also runs both full native control jobs on GitHub-hosted runners.

## Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for fixture evidence, review, and merge requirements.

## License

[MIT](LICENSE).
