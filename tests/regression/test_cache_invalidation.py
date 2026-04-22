"""Regression tests for D1 — SOAP client cache invalidation on Config changes.

These tests exercise the real WSDL parsing path (no network required — the
WSDL files are bundled under ``pyetnic.resources``) to prove that a change to
``Config.ENV`` or ``Config.USERNAME`` produces a different cached client.
"""

import pytest

from pyetnic.config import Config
from pyetnic.soap_client import SoapClientManager


@pytest.fixture
def reset_soap_cache():
    """Each test starts and ends with an empty SOAP client cache."""
    SoapClientManager.reset_cache()
    yield
    SoapClientManager.reset_cache()


def test_cache_returns_same_client_when_config_unchanged(reset_soap_cache):
    """Calling _initialize_client twice with the same Config returns the same object."""
    Config.ENV = "dev"
    Config.USERNAME = "user_a"
    Config.PASSWORD = "pass_a"

    mgr = SoapClientManager("ORGANISATION")
    client1 = mgr._initialize_client()
    client2 = mgr._initialize_client()

    assert client1 is client2


def test_cache_invalidates_on_env_change(reset_soap_cache):
    """Changing Config.ENV produces a new client object."""
    Config.ENV = "dev"
    Config.USERNAME = "user_a"
    Config.PASSWORD = "pass_a"

    mgr = SoapClientManager("ORGANISATION")
    client_dev = mgr._initialize_client()

    Config.ENV = "prod"
    client_prod = mgr._initialize_client()

    assert client_dev is not client_prod


def test_cache_invalidates_on_username_change(reset_soap_cache):
    """Changing Config.USERNAME produces a new client object."""
    Config.ENV = "dev"
    Config.USERNAME = "user_a"
    Config.PASSWORD = "pass_a"

    mgr = SoapClientManager("ORGANISATION")
    client_a = mgr._initialize_client()

    Config.USERNAME = "user_b"
    client_b = mgr._initialize_client()

    assert client_a is not client_b


def test_cache_invalidation_uses_correct_endpoint(reset_soap_cache):
    """After env change, the new client targets the new environment's endpoint."""
    Config.ENV = "dev"
    Config.USERNAME = "user"
    Config.PASSWORD = "pass"

    mgr = SoapClientManager("ORGANISATION")
    client_dev = mgr._initialize_client()
    dev_address = client_dev._binding_options["address"]
    assert "-tq" in dev_address

    Config.ENV = "prod"
    client_prod = mgr._initialize_client()
    prod_address = client_prod._binding_options["address"]
    assert "-tq" not in prod_address


def test_reset_cache_clears_entries(reset_soap_cache):
    """reset_cache() removes every cached client across all keys."""
    Config.ENV = "dev"
    Config.USERNAME = "user_a"
    Config.PASSWORD = "pass_a"

    mgr = SoapClientManager("ORGANISATION")
    mgr._initialize_client()
    assert SoapClientManager._client_cache

    SoapClientManager.reset_cache()
    assert SoapClientManager._client_cache == {}
