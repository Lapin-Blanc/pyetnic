"""Regression tests verifying that unexpected exceptions propagate.

Before phase 1.5, ``FormationsListeService`` had ``except Exception``
clauses that swallowed parser bugs (KeyError, TypeError, ...) and
turned them into ``FormationsListeResult(success=False, ...)``. That
masked real bugs. Now these exceptions propagate with full traceback.
"""

import pytest

from pyetnic.eprom import lister_formations, lister_formations_organisables


def test_lister_formations_propagates_keyerror_from_parser(mock_soap_call):
    """A malformed response (missing 'success') must raise KeyError, not be
    wrapped in FormationsListeResult(success=False).
    """
    mock_soap_call.return_value = {"body": {}}
    with pytest.raises(KeyError):
        lister_formations(annee_scolaire="2024-2025")


def test_lister_formations_organisables_propagates_keyerror(mock_soap_call):
    mock_soap_call.return_value = {"body": {}}
    with pytest.raises(KeyError):
        lister_formations_organisables(annee_scolaire="2024-2025")
