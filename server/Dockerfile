# Reference: https://docs.docker.com/reference/dockerfile/
FROM ubuntu:24.04 AS builder

RUN apt-get update && apt-get install -y openssl
COPY scripts/new-jwt-key.sh /scripts/new-jwt-key.sh
RUN /scripts/new-jwt-key.sh

FROM python:3.12-alpine AS runner

COPY requirements.txt /app/requirements.txt

WORKDIR /app
RUN pip install --no-cache-dir --no-compile -r requirements.txt && pip cache purge

COPY scripts /app/scripts
COPY server /app/server
COPY README.md /app/README.md
COPY --from=builder secrets /app/secrets
