import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.inspector import query_store


@pytest.fixture
def query_count_guard():
    """Detect repeated SELECT statements inside a test."""

    @contextmanager
    def guard(max_repeats=3):
        known_ids = {
            event["id"] for event in query_store.events(500)
        }

        yield

        new_events = [
            event
            for event in query_store.events(500)
            if event["id"] not in known_ids
        ]

        counts = Counter(
            event["fingerprint"]
            for event in new_events
            if event["is_select"]
        )

        violations = {
            fingerprint: count
            for fingerprint, count in counts.items()
            if count > max_repeats
        }

        if violations:
            details = "\n".join(
                f"{count} executions: {sql}"
                for sql, count in violations.items()
            )
            raise AssertionError(
                f"Repeated SQL statements exceeded "
                f"max_repeats={max_repeats}:\n{details}"
            )

    return guard

