"""Unit tests for SoapClientManager internals (Q5, Q6)."""

import logging
from unittest.mock import patch, MagicMock

import pytest

from pyetnic.config import Config
from pyetnic.soap_client import SoapClientManager


@pytest.fixture(autouse=True)
def clean():
    Config._reset()
    SoapClientManager.reset_cache()
    Config.ENV = "dev"
    Config.USERNAME = "test"
    Config.PASSWORD = "test"
    yield
    Config._reset()
    SoapClientManager.reset_cache()


class TestSslWarningSuppression:
    """Q5: SSL warning flag should be resettable."""

    def test_ssl_warning_flag_resets_with_cache(self):
        """reset_cache() must also reset the SSL warning flag."""
        SoapClientManager._ssl_warnings_suppressed = True
        SoapClientManager.reset_cache()
        assert SoapClientManager._ssl_warnings_suppressed is False

    def test_no_module_level_ssl_global(self):
        """The old module-level _ssl_warnings_suppressed must not exist."""
        import pyetnic.soap_client as mod
        # The flag should be on the class, not the module.
        assert not hasattr(mod, '_ssl_warnings_suppressed') or \
            mod._ssl_warnings_suppressed is SoapClientManager._ssl_warnings_suppressed

    def test_flag_lives_on_the_class(self):
        """The SSL warning flag is a class attribute on SoapClientManager."""
        assert hasattr(SoapClientManager, '_ssl_warnings_suppressed')
        assert SoapClientManager._ssl_warnings_suppressed is False


class TestRequestIdLogging:
    """Q6: request_id should be logged on success."""

    def test_request_id_logged_on_success(self, caplog):
        """A successful SOAP call should log the request_id at DEBUG level."""
        mgr = SoapClientManager("ORGANISATION")

        fake_service = MagicMock()
        fake_method = MagicMock()
        fake_method.return_value = MagicMock()  # any return value
        fake_service.LireOrganisation = fake_method

        with patch.object(mgr, '_initialize_client', return_value=fake_service):
            with patch('pyetnic.soap_client.serialize_object', return_value={'body': {}}):
                with caplog.at_level(logging.DEBUG, logger="pyetnic.soap_client"):
                    mgr.call_service("LireOrganisation", id={})

        # A success log carrying the request_id must have been emitted.
        assert any(
            "request_id" in record.message and "succeeded" in record.message
            for record in caplog.records
        ), f"Expected a success log with request_id. Got: {[r.message for r in caplog.records]}"


def test_request_breaking_the_contract_raises_an_etnic_validation_error(monkeypatch):
    """zeep refuses a request that breaks the contract before sending it: pyetnic types it.

    ``except EtnicError`` must catch everything pyetnic raises; a Doc 3 write with an
    empty ``activite`` list breaks the contract's ``[1..*]``.
    """
    from zeep import Client

    from pyetnic.config import Config
    from pyetnic.exceptions import EtnicError, EtnicValidationError
    from pyetnic.soap_client import SoapClientManager, get_wsdl_path

    config = Config.SERVICES["DOCUMENT3"]
    offline = Client(get_wsdl_path("pyetnic.resources", config.wsdl_path)).create_service(
        config.binding_name, "http://localhost.invalid/never-called")
    manager = SoapClientManager("DOCUMENT3")
    monkeypatch.setattr(manager, "_initialize_client", lambda: offline)

    with pytest.raises(EtnicValidationError, match="does not match the contract") as raised:
        manager.call_service(
            "ModifierDocument3",
            id={"anneeScolaire": "2025-2026", "etabId": 1234, "numAdmFormation": 1, "numOrganisation": 1},
            activiteListe={"activite": []},
        )
    assert isinstance(raised.value, EtnicError)
    assert raised.value.request_id


def test_enum_members_go_on_the_wire_as_their_value(monkeypatch):
    """zeep writes ``str(member)``, ``"ModeEnregistrement.NISS"``: call_service sends the code (#50)."""
    import re

    from lxml import etree
    from zeep import Client

    from pyetnic.nomenclatures import ModeEnregistrement, Sexe
    from pyetnic.soap_client import get_wsdl_path

    config = Config.SERVICES["SEPS_ENREGISTRER_ETUDIANT"]
    client = Client(get_wsdl_path("pyetnic.resources", config.wsdl_path))
    sent: dict = {}

    class _Offline:
        def enregistrerEtudiant(self, _soapheaders=None, **kwargs):
            sent.update(kwargs)
            sent["xml"] = etree.tostring(
                client.create_message(client.service, "enregistrerEtudiant", **kwargs)
            ).decode()
            return {}

    manager = SoapClientManager("SEPS_ENREGISTRER_ETUDIANT")
    monkeypatch.setattr(manager, "_initialize_client", lambda: _Offline())
    manager.call_service(
        "enregistrerEtudiant",
        modeEnregistrement=ModeEnregistrement.NISS,
        etudiantDetails={"nom": "DUPONT", "sexe": Sexe.FEMININ, "autrePrenom": [Sexe.AUTRE]},
    )

    assert type(sent["modeEnregistrement"]) is str
    assert type(sent["etudiantDetails"]["sexe"]) is str
    assert sent["etudiantDetails"]["autrePrenom"] == ["X"]
    assert re.search(r"modeEnregistrement[^>]*>NISS<", sent["xml"])
    assert re.search(r"sexe[^>]*>F<", sent["xml"])
    assert "ModeEnregistrement." not in sent["xml"] and "Sexe." not in sent["xml"]
