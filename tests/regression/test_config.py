"""Regression tests for Config attribute types (Q4).

These tests pin the contract that numeric env-backed attributes
(``ETAB_ID``, ``IMPL_ID``) are cast to ``int`` before being returned,
while string attributes (``ENV``, ``ANNEE_SCOLAIRE``, ...) are not.
Explicit overrides (``Config.X = value``) are returned as-is.
"""

from __future__ import annotations

import pytest

from pyetnic.config import Config


@pytest.fixture(autouse=True)
def clean_config(monkeypatch):
    monkeypatch.delenv("DEFAULT_ETABID", raising=False)
    monkeypatch.delenv("DEFAULT_IMPLID", raising=False)
    Config._reset()
    yield
    Config._reset()


def test_etab_id_returns_int_from_env(monkeypatch):
    """Config.ETAB_ID must return an int when set via env var."""
    monkeypatch.setenv("DEFAULT_ETABID", "3052")
    Config._reset()
    result = Config.ETAB_ID
    assert result == 3052
    assert isinstance(result, int)


def test_impl_id_returns_int_from_env(monkeypatch):
    """Config.IMPL_ID must return an int when set via env var."""
    monkeypatch.setenv("DEFAULT_IMPLID", "6050")
    Config._reset()
    result = Config.IMPL_ID
    assert result == 6050
    assert isinstance(result, int)


def test_etab_id_returns_none_when_unset():
    """Config.ETAB_ID must return None when the env var is absent."""
    result = Config.ETAB_ID
    assert result is None


def test_etab_id_returns_none_for_empty_string(monkeypatch):
    """An empty env value must return None, not raise ValueError."""
    monkeypatch.setenv("DEFAULT_ETABID", "")
    Config._reset()
    result = Config.ETAB_ID
    assert result is None


def test_etab_id_returns_none_for_non_numeric(monkeypatch):
    """A non-numeric env value must return None, not crash at import time."""
    monkeypatch.setenv("DEFAULT_ETABID", "not-a-number")
    Config._reset()
    result = Config.ETAB_ID
    assert result is None


def test_etab_id_override_preserves_type():
    """Explicit overrides are returned as-is (no auto-casting)."""
    Config.ETAB_ID = 9999
    assert Config.ETAB_ID == 9999
    assert isinstance(Config.ETAB_ID, int)

    Config.ETAB_ID = "9999"
    assert Config.ETAB_ID == "9999"
    assert isinstance(Config.ETAB_ID, str)


def test_env_returns_str():
    """Config.ENV must still return a string (no caster)."""
    result = Config.ENV
    assert isinstance(result, str)


def test_annee_scolaire_returns_str():
    """Config.ANNEE_SCOLAIRE must still return a string (no caster)."""
    result = Config.ANNEE_SCOLAIRE
    assert isinstance(result, str)
