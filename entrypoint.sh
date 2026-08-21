#!/usr/bin/env sh
# Deploy-time startup: migrate, then serve.
#
# Migrations run here rather than inside the application so that a failure is
# loud and stops the boot, instead of serving traffic against a schema that
# does not match the code (spec 004, HU-02).

set -eu

echo "[entrypoint] applying database migrations..."
if ! alembic upgrade head; then
    echo "[entrypoint] MIGRATION FAILED - refusing to start." >&2
    exit 1
fi

PORT="${PORT:-9600}"
echo "[entrypoint] starting uvicorn on 0.0.0.0:${PORT} (env=${ENVIRONMENT:-development})"

exec uvicorn core.main:app \
    --host 0.0.0.0 \
    --port "${PORT}" \
    --proxy-headers \
    --forwarded-allow-ips '*'
