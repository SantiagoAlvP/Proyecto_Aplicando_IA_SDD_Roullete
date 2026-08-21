# syntax=docker/dockerfile:1

# ── Stage 1: build the SPA ───────────────────────────────────────────────────
# Node exists only here, so it never ships to production: smaller image, less
# attack surface (plan 004, Complexity Tracking).
FROM node:22-slim AS frontend

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN pip install --no-cache-dir uv

# Dependencies first: this layer is cached across code-only changes, which is
# what keeps a live-demo redeploy under a couple of minutes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY core/ ./core/
COPY alembic/ ./alembic/
COPY data/ ./data/
COPY alembic.ini project_jackpot.py entrypoint.sh ./
COPY --from=frontend /frontend/dist ./frontend/dist

RUN chmod +x entrypoint.sh

# Never run as root: a container escape should not start with uid 0.
RUN useradd --create-home --uid 1001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 9600

ENTRYPOINT ["./entrypoint.sh"]
