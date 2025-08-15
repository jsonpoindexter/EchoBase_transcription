#!/usr/bin/env bash
set -euo pipefail

# Ensure dirs exist
mkdir -p /models /models/hf-cache /models/.hf-home /app/temp

# Make them writable by the celery user and a shared group
groupadd -g 10001 appshare 2>/dev/null || true
id -u celery &>/dev/null || useradd -m -u 10001 -g appshare celery || true
usermod -aG appshare celery || true

chown -R celery:appshare /models /app/temp || true
chmod -R g+rwX /models /app/temp || true
# setgid bit so new files inherit the group
chmod g+s /models /app/temp || true

# Drop privileges and exec CMD
exec gosu celery "$@"
