# Calibration methodology

The unit of independent evidence is the issue. The 32 task directories here derive from one issue and must be scored as one issue. A useful next study would repeat the design on independent, unseen issues, with a frozen harness and a separate realism check.

## Assignment

The generator crosses two installed handlers, two downstream causes, two forests, and four information conditions. The profile supplied in `example.json` determines the handler and cause. The symptom and visible check are the same across starting profiles. Both forests have the same number of files, total bytes, and extension mix. Only the competing forest presents inactive code written to resemble the affected service.

| Condition | Information supplied with the issue |
| --- | --- |
| Map-free | True response fact |
| Source map | Common source map and the same response fact |
| Observed handler | Common source map and the handler observed in the installed request |
| Edit hint | Common source map and the reference repair file |

The response fact controls for an extra observation in the prompt. Its relevance differs from a handler name. A stricter comparison could give the source-map arm a true shared code entry observed in the same request. That would estimate the value of identifying the active handler beyond the common entry point. That comparison requires its own task snapshot and run label.

Each handler can encounter either downstream cause. A handler observation leaves two reference edit sites possible. The grader accepts an eligible shared repair that meets the HTTP contract without editing the reference file.

## Acceptance

Harbor transfers the existing service source into a separate verifier. The verifier checks the submission, reinstalls it using its own installer, and starts the installed loopback service with fresh state for each scenario. The cases cover sparse updates, explicitly clearing both fields, same-session reads, unchanged neighboring records, rejected payloads, full updates, missing records and health. Each task grades the assigned workspace and layout. Edits to the existing installed source files are the submission contract.

The case rates and `submission_present` are diagnostic. The binary reward requires all target and preservation cases to pass. Recipe and scorer names are labels within this calibration. A missing or invalid verifier result stays unknown until adjudicated in the trial ledger.

## Comparisons

The unassisted decoy penalty is the map-free acceptance rate on unrelated code minus the rate on competing code. For the evidence comparison, hold the source map fixed. Compute the gain from the observed handler on competing code and on unrelated code. Subtract the latter from the former to estimate how much more the disclosure helps under misdirection. Report both gains. A positive interaction can coexist with a flat or worse result on competing code.

Rerun gains on independent issues before interpreting them as model or harness capabilities. Hold the harness fixed to compare models. Hold the model fixed to compare a harness change. Keep unknown outcomes, wall time, spend, and human effort visible. Export repeated or independently route-audited trials as normalized rows with the full assignment manifest.

Before a model run, record the checkout commit, assignment-manifest hash, task locks, verifier dependencies, Harbor version, effective model, adapter, resource caps, and network policy. Container base image references use digests. The builds still install distro packages at build time, so record the built image identity or retain the images for an exact environment replay. Keep calibration results separate from any sealed evaluation.

## Prior work

- RepoMirage already evaluates hidden runtime targets, inactive look-alikes and structural hints. Here the installed profile and supplied evidence vary independently with the same verifier. [RepoMirage](https://arxiv.org/html/2605.26177v1)
- Programmable Distributions already evaluates keyword-matched dead code and other repository rewrites across models and scaffolds. The matched forests here support a comparison of route evidence under plausible inactive code. [Programmable Distributions](https://arxiv.org/html/2608.18389v2)
- From Finding to Fixing already measures the value of fault-localization and gold edit hints. The handler-only arm here identifies an executed edge while leaving the downstream cause open. [From Finding to Fixing](https://arxiv.org/html/2610.25826v1)
