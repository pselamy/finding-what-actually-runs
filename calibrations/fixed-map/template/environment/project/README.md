# Workspace draft service

The local HTTP service supports reading and saving drafts in a workspace. Install a fresh build with `./scripts/install /tmp/drafts-local`, then launch `/tmp/drafts-local/bin/draft-service --snapshot example.json`. A loopback URL appears on standard output. Use the API routes under `/api/drafts` and the health check at `/health`. Run `./scripts/ci` before merging.
