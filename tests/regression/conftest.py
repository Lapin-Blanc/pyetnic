"""Shared fixtures for regression tests. Mock-based, no network."""

from unittest.mock import MagicMock, patch

import pytest

from pyetnic.config import Config


@pytest.fixture
def mock_soap_call():
    """Patch SoapClientManager.call_service for the duration of a test.

    Yields a MagicMock. Tests configure its return_value (or side_effect)
    to the dict they want the SOAP layer to produce, then call the public
    pyetnic function and assert on the returned dataclass.

    The patch targets the class method, so all service singletons created
    at import time pick it up automatically.
    """
    with patch(
        "pyetnic.soap_client.SoapClientManager.call_service",
        new_callable=MagicMock,
    ) as mock:
        yield mock


@pytest.fixture(autouse=True)
def block_dotenv():
    """Keep the whole regression suite hermetic w.r.t. the developer's .env.

    ``Config._reset()`` clears the "dotenv loaded" flag, so the next attribute
    access re-runs ``load_dotenv()`` and re-populates ``os.environ`` from the
    on-disk ``.env`` — silently undoing any ``monkeypatch.delenv(...)`` a test
    performed. That makes tests like ``test_etab_id_returns_none_when_unset``
    pass in CI (no .env) but fail on a developer machine that has one. Patch
    the loader to a no-op so behavior is identical everywhere. Integration
    tests live under tests/integration/ — out of this conftest's scope — so
    they keep reading the real .env.
    """
    with patch("pyetnic.config._load_dotenv_compat", lambda: None):
        yield


@pytest.fixture(autouse=True)
def isolate_config():
    """Each regression test starts with a clean Config state.

    Resets programmatic overrides and dotenv state, then sets a minimal
    valid configuration so services can instantiate without touching .env.
    """
    Config._reset()
    Config.ENV = "dev"
    Config.ANNEE_SCOLAIRE = "2024-2025"
    Config.ETAB_ID = "3052"
    Config.IMPL_ID = "6050"
    yield
    Config._reset()
