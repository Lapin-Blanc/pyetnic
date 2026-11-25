"""A response value that breaks its simple type raises EtnicResponseError (#52).

zeep (4.3) logs a value it cannot convert and hands ``None`` on, as if the
element were absent. The responses below go through zeep's real parser, from a
canned transport: a Doc 3 with a decimal in ``nbPeriodesPrevuesDoc2``
(``xs:int``), as the manual's example writes it. Identifiers are fictitious.
"""

from __future__ import annotations

import logging

import pytest
import requests
from zeep import Client
from zeep.transports import Transport

from pyetnic.config import Config
from pyetnic.exceptions import EtnicError, EtnicResponseError
from pyetnic.soap_client import SoapClientManager, _conversion_failures, get_wsdl_path

_RESPONSE = """<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Body>
<m:LireDocument3Reponse xmlns:m="http://services-web.etnic.be/eprom/formation/document3/messages/v1"
  xmlns:r="http://etnic.be/types/technical/ResponseStatus/v3"
  xmlns:d="http://enseignement.cfwb.be/types/formation/document3/v1"
  xmlns:o="http://enseignement.cfwb.be/types/organisation/v1">
 <r:success>true</r:success>
 <m:response><d:document3>
  <d:id><o:anneeScolaire>2025-2026</o:anneeScolaire><o:etabId>1234</o:etabId>
   <o:numAdmFormation>328</o:numAdmFormation><o:numOrganisation>1</o:numOrganisation></d:id>
  <d:activiteListe><d:activite>
   <d:coNumBranche>10</d:coNumBranche><d:coCategorie>A</d:coCategorie>
   <d:teNomBranche>Branche</d:teNomBranche><d:noAnneeEtude>1</d:noAnneeEtude>
   <d:nbPeriodesDoc8>24</d:nbPeriodesDoc8>
   <d:nbPeriodesPrevuesDoc2>{prevues}</d:nbPeriodesPrevuesDoc2>
   <d:nbPeriodesReellesDoc2>24</d:nbPeriodesReellesDoc2>
  </d:activite></d:activiteListe>
 </d:document3></m:response>
</m:LireDocument3Reponse></soap-env:Body></soap-env:Envelope>"""

_ID = {"anneeScolaire": "2025-2026", "etabId": 1234, "numAdmFormation": 328, "numOrganisation": 1}


class _CannedTransport(Transport):
    """Answers every call with the same bytes, without any network."""

    def __init__(self, content: bytes):
        super().__init__()
        self.content = content

    def post_xml(self, address, envelope, headers):
        response = requests.Response()
        response.status_code = 200
        response.headers["Content-Type"] = "text/xml; charset=utf-8"
        response._content = self.content
        return response


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


def _offline_doc3(monkeypatch, prevues: str) -> None:
    """Every DOCUMENT3 manager answers with the canned response."""
    config = Config.SERVICES["DOCUMENT3"]
    content = _RESPONSE.format(prevues=prevues).encode()
    client = Client(get_wsdl_path("pyetnic.resources", config.wsdl_path), transport=_CannedTransport(content))
    service = client.create_service(config.binding_name, "http://localhost.invalid/doc3")
    monkeypatch.setattr(SoapClientManager, "_initialize_client", lambda self: service)


def _activite(response: dict) -> dict:
    return response["body"]["response"]["document3"]["activiteListe"]["activite"][0]


def test_a_conforming_response_parses(monkeypatch):
    _offline_doc3(monkeypatch, "24")
    response = SoapClientManager("DOCUMENT3").call_service("LireDocument3", id=_ID)
    assert _activite(response)["nbPeriodesPrevuesDoc2"] == 24


def test_a_decimal_in_an_int_raises(monkeypatch):
    _offline_doc3(monkeypatch, "24.0")
    with pytest.raises(EtnicResponseError, match="nbPeriodesPrevuesDoc2='24.0'") as raised:
        SoapClientManager("DOCUMENT3").call_service("LireDocument3", id=_ID)
    error = raised.value
    assert isinstance(error, EtnicError)
    assert error.values == [("nbPeriodesPrevuesDoc2", "24.0")]
    assert error.request_id
    # The rest of the answer stays reachable; the broken value is the None zeep made of it.
    activite = _activite(error.response)
    assert activite["nbPeriodesPrevuesDoc2"] is None
    assert activite["nbPeriodesDoc8"] == 24


def test_the_public_reader_raises_even_in_permissive_mode(monkeypatch):
    """A broken answer is not a refusal: the deprecated permissive mode does not turn it into None."""
    from pyetnic.eprom import OrganisationId, lire_document_3, permissive_errors

    _offline_doc3(monkeypatch, "24.0")
    org_id = OrganisationId(anneeScolaire="2025-2026", etabId=1234, numAdmFormation=328, numOrganisation=1)
    with pytest.raises(EtnicResponseError):
        lire_document_3(org_id)
    with pytest.deprecated_call(), permissive_errors(), pytest.raises(EtnicResponseError):
        lire_document_3(org_id)


def test_an_attribute_is_named_with_an_at_sign():
    from zeep.xsd import Attribute
    from zeep.xsd.types.builtins import Integer

    failures: list = []
    token = _conversion_failures.set(failures)
    try:
        assert Attribute("code", Integer()).parse("x") is None
    finally:
        _conversion_failures.reset(token)
    assert failures == [("@code", "x")]


def test_nothing_is_collected_outside_a_call():
    from zeep.xsd import Attribute
    from zeep.xsd.types.builtins import Integer

    assert Attribute("code", Integer()).parse("x") is None
    assert _conversion_failures.get() is None


def test_a_silenced_zeep_logger_is_reported_once(monkeypatch, caplog):
    monkeypatch.setattr(logging.getLogger("zeep.xsd.types.simple"), "disabled", True)
    _offline_doc3(monkeypatch, "24")
    with caplog.at_level(logging.WARNING, logger="pyetnic.soap_client"):
        SoapClientManager("DOCUMENT3").call_service("LireDocument3", id=_ID)
        SoapClientManager("DOCUMENT3").call_service("LireDocument3", id=_ID)
    assert sum("conversion errors are silenced" in r.message for r in caplog.records) == 1
