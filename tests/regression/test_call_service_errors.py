"""Regression tests for SoapClientManager.call_service error handling."""

from unittest.mock import MagicMock, patch

import pytest
from zeep.exceptions import Fault

from pyetnic.soap_client import SoapClientManager, SoapError


def test_attribute_error_is_not_swallowed_as_soap_error():
    """AttributeError must propagate, not be wrapped in SoapError.

    Before phase 1.4, call_service caught AttributeError and wrapped it
    in SoapError. This masked real bugs like typos in method names. Now,
    AttributeError propagates as-is so the developer sees the actual error.
    """
    mgr = SoapClientManager("ORGANISATION")

    fake_service = MagicMock()
    fake_method = MagicMock(side_effect=AttributeError("simulated attribute error"))
    fake_service.SomeMethod = fake_method

    with patch.object(mgr, "_initialize_client", return_value=fake_service):
        with pytest.raises(AttributeError, match="simulated attribute error"):
            mgr.call_service("SomeMethod")


def test_fault_is_still_wrapped_as_soap_error():
    """zeep Fault is still caught and wrapped (regression baseline)."""
    mgr = SoapClientManager("ORGANISATION")

    fake_service = MagicMock()
    fake_method = MagicMock(side_effect=Fault("simulated SOAP fault"))
    fake_service.SomeMethod = fake_method

    with patch.object(mgr, "_initialize_client", return_value=fake_service):
        with pytest.raises(SoapError):
            mgr.call_service("SomeMethod")
