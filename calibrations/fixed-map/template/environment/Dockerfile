FROM node:22-bookworm-slim@sha256:e9f565d32859f0cbfb52125eafe8be39390f24dac302dc3cdf566e8ba3ab21ee
RUN apt-get update && apt-get install -y --no-install-recommends python3 util-linux \
    && rm -rf /var/lib/apt/lists/*
COPY project/ /app/drafts/
RUN /app/drafts/scripts/install
WORKDIR /app/drafts
