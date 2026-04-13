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
