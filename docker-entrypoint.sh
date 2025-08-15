#!/bin/bash
chown -R celery:celery /models || true
exec "$@"
