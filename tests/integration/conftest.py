"""Integration tests run on TQ, the ETNIC test environment, whatever ``.env`` says.

Several of them write: they create, modify and delete organisations, and rewrite
documents before restoring them. ``.env`` usually points at production, where a
test must never write, so every integration test is pinned to TQ here, and the
endpoints are checked before the test runs.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from pyetnic.config import Config

TQ_HOST = "ws-tq.etnic.be"


@pytest.fixture(autouse=True)
def _tq_only() -> Iterator[None]:
    """Per test, not per session: another module may reset the configuration in between."""
    Config.ENV = "dev"
    for key, service in Config.SERVICES.items():
        assert TQ_HOST in service.endpoint, f"{key} would not reach TQ: {service.endpoint}"
    yield
