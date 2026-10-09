
from __future__ import annotations

import re
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, asdict
from typing import Any

from app.config import settings


_LITERAL_RE = re.compile(r"'(?:''|[^'])*'|\b\d+(?:\.\d+)?\b")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_sql(sql: str) -> str:
    """Normalize SQL to group queries with different literal values."""
    return _WHITESPACE_RE.sub(
        " ", _LITERAL_RE.sub("?", sql)
    ).strip().lower()


def _safe_preview(parameters: Any, max_chars: int = 180) -> str:
    try:
        value = repr(parameters)
    except Exception:
        value = "<unavailable>"

    return value[:max_chars] + ("…" if len(value) > max_chars else "")


@dataclass
class QueryEvent:
    id: str
    timestamp: float
    sql: str
    fingerprint: str
    duration_ms: float
    parameters: str
    is_select: bool
    slow: bool


class QueryStore:
    def __init__(self):
        self._lock = threading.RLock()

        self._events: deque[QueryEvent] = deque(
            maxlen=max(50, settings.query_history_limit)
        )

        # Warnings are stored separately from the rolling query history.
        self._alerts: dict[tuple[str, str], dict] = {}

        self._total_queries = 0
        self._total_slow = 0

    def before_execute(
        self, conn, cursor, statement, parameters, context, executemany
    ):
        context._inspector_started_at = time.perf_counter()

    def after_execute(
        self, conn, cursor, statement, parameters, context, executemany
    ):
        started = getattr(context, "_inspector_started_at", None)
        if started is None:
            return

        duration_ms = (time.perf_counter() - started) * 1000
        sql = str(statement)
        fingerprint = normalize_sql(sql)[:1000]

        event = QueryEvent(
            id=uuid.uuid4().hex[:12],
            timestamp=time.time(),
            sql=sql[:4000],
            fingerprint=fingerprint,
            duration_ms=round(duration_ms, 3),
            parameters=_safe_preview(parameters),
            is_select=fingerprint.startswith("select "),
            slow=duration_ms >= settings.slow_query_ms,
        )

        with self._lock:
            self._events.append(event)
            self._total_queries += 1
            self._total_slow += int(event.slow)

            # Save slow-query warnings instead of recalculating them
            # from a temporary time window.
            if event.slow:
                key = ("slow_query", event.fingerprint)
                self._alerts[key] = {
                    "type": "slow_query",
                    "severity": "warning",
                    "query_id": event.id,
                    "message": (
                        f"Query took {event.duration_ms:.1f} ms "
                        f"(threshold {settings.slow_query_ms:.1f} ms)"
                    ),
                    "fingerprint": event.fingerprint,
                }

            # Detect N+1 only within the configured time window.
            # Once detected, its warning remains in _alerts.
            if event.is_select:
                cutoff = time.time() - settings.n1_window_seconds

                matching = [
                    item
                    for item in self._events
                    if item.is_select
                    and item.fingerprint == event.fingerprint
                    and item.timestamp >= cutoff
                ]

                if len(matching) >= settings.n1_threshold:
                    key = ("possible_n_plus_one", event.fingerprint)

                    self._alerts[key] = {
                        "type": "possible_n_plus_one",
                        "severity": "high",
                        "count": len(matching),
                        "message": (
                            f"Repeated SELECT fingerprint observed "
                            f"{len(matching)} times within "
                            f"{settings.n1_window_seconds:.0f}s"
                        ),
                        "fingerprint": event.fingerprint,
                        "query_ids": [item.id for item in matching[-10:]],
                    }

    def events(self, limit: int = 100) -> list[dict]:
        with self._lock:
            selected = list(self._events)[
                -max(1, min(limit, 500)):
            ]
            return [asdict(event) for event in reversed(selected)]

    def summary(self) -> dict:
        with self._lock:
            events = list(self._events)
            total = self._total_queries
            slow = self._total_slow

        recent = events[-100:]

        return {
            "total_queries": total,
            "slow_queries": slow,
            "queries_in_window": len(recent),
            "select_queries_in_window": sum(
                event.is_select for event in recent
            ),
            "average_duration_ms": (
                round(
                    sum(event.duration_ms for event in recent)
                    / len(recent),
                    3,
                )
                if recent
                else 0
            ),
            "slow_query_threshold_ms": settings.slow_query_ms,
            "n1_threshold": settings.n1_threshold,
        }

    def alerts(self) -> list[dict]:
        with self._lock:
            # Return a copy so callers cannot mutate stored warnings.
            return [dict(alert) for alert in self._alerts.values()]

    def clear(self):
        with self._lock:
            self._events.clear()
            self._alerts.clear()
            self._total_queries = 0
            self._total_slow = 0


query_store = QueryStore()