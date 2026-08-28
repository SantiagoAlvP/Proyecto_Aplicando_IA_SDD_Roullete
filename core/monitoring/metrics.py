"""Minimal in-process telemetry for API endpoints.

This is intentionally lightweight: an in-memory counter, no external
dependencies, no background threads. It answers the operational question
"how is this endpoint being used right now?" (hits, denials, not-found rate)
without pulling in a full metrics stack (Prometheus, StatsD, etc.).

If/when the project adopts a real metrics backend, `record_project_access`
is the single seam to redirect - callers don't need to change.
"""

from __future__ import annotations

import threading
from collections import defaultdict

_lock = threading.Lock()
_counters: dict[str, int] = defaultdict(int)

# Outcomes tracked for GET /api/v1/projects/{project_id}.
PROJECT_ACCESS_OUTCOMES = ("granted", "not_found", "unauthorized", "forbidden")


def record_project_access(outcome: str) -> None:
    """Increment the counter for a project-access outcome.

    `outcome` should be one of PROJECT_ACCESS_OUTCOMES, but unknown values
    are still recorded (under their own key) rather than raising - metrics
    code must never break the request path it's observing.
    """
    key = f"projects.get_by_id.{outcome}"
    with _lock:
        _counters[key] += 1


def get_metrics_snapshot() -> dict[str, int]:
    """Return a copy of all recorded counters."""
    with _lock:
        return dict(_counters)


def reset_metrics() -> None:
    """Clear all counters. Intended for tests only."""
    with _lock:
        _counters.clear()
