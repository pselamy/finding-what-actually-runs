# Preserve draft fields during partial saves

Editing a draft through the installed service sometimes clears the field the user did not edit. Fix the installed HTTP service.

Repair the workspace and layout supplied in `example.json`. Submit changes to the existing installed service source files so the evaluator can rebuild the service with its own installer.

`PATCH /api/drafts/{id}` accepts any subset of `title` and `body`. Apply the submitted strings verbatim, including an explicit empty string. Keep each omitted field unchanged. An empty object leaves both fields unchanged. Return the complete updated record with its original identifier and folder. `GET /api/drafts/{id}` must return the new record on subsequent requests in the same server session.

Keep the existing behavior of full saves, reads, missing drafts, and rejection of unsupported fields or non-string values. Keep the health endpoint working.

Install into a fresh directory with `./scripts/install /tmp/drafts-local`. Run the installed command with `/tmp/drafts-local/bin/draft-service --snapshot example.json`. It prints its loopback URL on startup. Run the existing checks with `./scripts/ci`.
