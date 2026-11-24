"""The contract watch (``tools/refresh_contracts.py``), without network.

The canonical form must ignore what the gateway, the catalogue and the
repository write differently without changing the contract, and catch the rest;
the catalogue parser must read the pages as the catalogue serves them.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[2] / "tools" / "refresh_contracts.py"
spec = importlib.util.spec_from_file_location("refresh_contracts", TOOL)
rc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = rc  # dataclasses resolve their annotations through sys.modules
spec.loader.exec_module(rc)

WSDL = b"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Version 1.1 -->
<wsdl:definitions xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/"
    xmlns:m="urn:messages" name="S" targetNamespace="urn:service">
  <wsdl:types>
    <xs:schema>
      <xs:import namespace="urn:messages" schemaLocation="xsd/Messages_v1.xsd"/>
    </xs:schema>
  </wsdl:types>
  <wsdl:message name="LireRequete"><wsdl:part element="m:Lire" name="parameter"/></wsdl:message>
  <wsdl:message name="LireReponse"><wsdl:part element="m:LireReponse" name="parameter"/></wsdl:message>
  <wsdl:service name="S">
    <wsdl:port binding="b" name="P"><soap:address location="https://ws.etnic.be/x/v1"/></wsdl:port>
  </wsdl:service>
</wsdl:definitions>
"""

# Same contract as the live gateway writes it: other prefix order, explicit end
# tags, messages in another order, relative import path, documentation, address.
WSDL_LIVE = b"""<!-- Project: be.etnic.esb.resources:eprom:4.5.3 --><wsdl:definitions name="S"
 targetNamespace="urn:service" xmlns:m="urn:messages"
 xmlns:soap="http://schemas.xmlsoap.org/wsdl/soap/" xmlns:wsdl="http://schemas.xmlsoap.org/wsdl/"
 xmlns:xs="http://www.w3.org/2001/XMLSchema">
\t<wsdl:documentation>Generated</wsdl:documentation>
\t<wsdl:types><xs:schema>
\t\t<xs:import namespace="urn:messages" schemaLocation="../xsd/eprom/Messages_v1.xsd"></xs:import>
\t</xs:schema></wsdl:types>
\t<wsdl:message name="LireReponse"><wsdl:part name="parameter" element="m:LireReponse"/></wsdl:message>
\t<wsdl:message name="LireRequete"><wsdl:part name="parameter" element="m:Lire"/></wsdl:message>
\t<wsdl:service name="S"><wsdl:port name="P" binding="b">
\t\t<soap:address location="https://services-web.etnic.be:11443/x/v1"/>
\t</wsdl:port></wsdl:service>
</wsdl:definitions>"""

XSD = b"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:t">
  <xs:complexType name="T">
    <xs:annotation><xs:documentation>DEPRECATED</xs:documentation></xs:annotation>
    <xs:sequence>
      <xs:element name="a" type="xs:string"/>
      <xs:element name="b" type="xs:int" minOccurs="0"/>
    </xs:sequence>
  </xs:complexType>
</xs:schema>"""


class TestCanonical:
    def test_formatting_order_paths_and_address_are_not_drift(self):
        assert rc.canonical(WSDL) == rc.canonical(WSDL_LIVE)

    def test_annotations_are_not_drift(self):
        bare = XSD.replace(b"<xs:annotation><xs:documentation>DEPRECATED</xs:documentation></xs:annotation>", b"")
        assert rc.canonical(XSD) == rc.canonical(bare)

    def test_an_added_element_is_drift(self):
        grown = XSD.replace(b'minOccurs="0"/>', b'minOccurs="0"/><xs:element name="c" type="xs:boolean" minOccurs="0"/>')
        assert rc.canonical(XSD) != rc.canonical(grown)
        assert rc.describe_change(XSD, grown) == "added element:c"

    def test_the_order_of_a_sequence_is_drift(self):
        swapped = XSD.replace(b'<xs:element name="a" type="xs:string"/>', b"").replace(
            b'minOccurs="0"/>', b'minOccurs="0"/><xs:element name="a" type="xs:string"/>')
        assert rc.canonical(XSD) != rc.canonical(swapped)

    def test_a_changed_occurrence_is_drift(self):
        required = XSD.replace(b' minOccurs="0"', b"")
        assert rc.canonical(XSD) != rc.canonical(required)


class TestImports:
    def test_absolute_imports_mean_served_schemas(self):
        served = b'<x schemaLocation="https://ws.etnic.be/service/abc?serviceoid=1&amp;servdocoid=2"/>'
        assert rc.imports(served) == ["https://ws.etnic.be/service/abc?serviceoid=1&servdocoid=2"]
        assert rc.is_absolute(rc.imports(served)[0])
        assert not rc.is_absolute("../xsd/eprom/Messages_v1.xsd")

    def test_relative_live_imports_point_at_the_xsd_folder(self):
        localised = rc.localise_relative(WSDL_LIVE)
        assert b'schemaLocation="xsd/Messages_v1.xsd"' in localised
        assert localised.endswith(b"\n")

    @pytest.mark.parametrize("path, expected", [
        ("eprom/formation/organisation/v7", "eprom/formation/organisation/v8"),
        ("seps/notifications/v1", "seps/notifications/v2"),
        ("eprom/formation/document1D/v1", "eprom/formation/document1D/v2"),
        ("ecole/sans/version", None),
    ])
    def test_next_version(self, path, expected):
        assert rc.next_version(path) == expected


TABLE = """
<tr>
 <td><a href="/tableau-services-web?tx_etnicservices_webservicefrt%5Baction%5D=show&amp;tx_etnicservices_webservicefrt%5Bcontroller%5D=Service&amp;tx_etnicservices_webservicefrt%5Bserviceid%5D=b089&amp;cHash=1">EPROM</a></td>
 <td><a href="/tableau-services-web?tx_etnicservices_webservicefrt%5Baction%5D=show&amp;tx_etnicservices_webservicefrt%5Bcontroller%5D=Service&amp;tx_etnicservices_webservicefrt%5Bserviceid%5D=b089&amp;cHash=1">Formation Organisation</a></td>
 <td><a href="/tableau-services-web?tx_etnicservices_webservicefrt%5Baction%5D=show&amp;tx_etnicservices_webservicefrt%5Bcontroller%5D=Service&amp;tx_etnicservices_webservicefrt%5Bserviceid%5D=b089&amp;cHash=1">8.0</a></td>
</tr>
<a href="/catalogue-de-services">Catalogue</a>
"""

PAGE = """
<a href="/tableau-services-web?tx_etnicservices_webservicefrt%5Baction%5D=download&amp;tx_etnicservices_webservicefrt%5Bcontroller%5D=Attachment&amp;tx_etnicservices_webservicefrt%5Bserviceid%5D=b089&amp;cHash=2">T&eacute;l&eacute;charger le contrat</a>
<div class="form-group row">
	<label for="endpoint" class="col-sm-2 col-form-label">Endpoint URL TQ</label>
	<div class="col-sm-10">
	https://ws-tq.etnic.be/eprom/formation/organisation/v8
	</div>
</div>
<div class="form-group row">
	<label for="endpoint" class="col-sm-2 col-form-label">Endpoint URL PROD</label>
	<div class="col-sm-10">
	https://ws.etnic.be/eprom/formation/organisation/v8
	</div>
</div>
<table class="table table-striped"><thead><tr><th>Nom</th><th>Version</th></tr></thead><tbody>
	<tr class="row1">
		<td>EPROM Formation Organisation 8.0 - Manuel d&#039;utilisation</td>
		<td>6.0</td>
		<td>21-05-2026</td>
		<td><center>PDF</center></td>
		<td class="dlcenter"><a href="/fileadmin/Soa/SEPS\\ETNIC_Manuel_rev6.0.pdf" target="_blank">T&eacute;l&eacute;charger</a></td>
	</tr>
</tbody></table>
"""


class TestCatalogue:
    def test_table_rows_become_entries(self):
        [entry] = rc.parse_table(TABLE)
        assert (entry.product, entry.name, entry.version) == ("EPROM", "Formation Organisation", "8.0")
        assert entry.page.startswith("https://extra.etnic.be/tableau-services-web?")

    def test_service_page_gives_endpoints_contract_and_manuals(self):
        entry = rc.parse_service_page(rc.CatalogueEntry("EPROM", "Formation Organisation", "8.0", "p"), PAGE)
        assert entry.endpoint_prod == "https://ws.etnic.be/eprom/formation/organisation/v8"
        assert entry.endpoint_tq == "https://ws-tq.etnic.be/eprom/formation/organisation/v8"
        assert "action%5D=download" in entry.contract
        [manual] = entry.manuals
        assert (manual.name, manual.revision, manual.date) == (
            "EPROM Formation Organisation 8.0 - Manuel d'utilisation", "6.0", "21-05-2026")
        assert manual.file == "ETNIC_Manuel_rev6.0.pdf"

    def test_pages_in_windows_1252_are_read(self):
        assert rc.decode("Périodes".encode("cp1252")) == "Périodes"
        assert rc.decode("Périodes".encode()) == "Périodes"

    def test_names_match_without_case_or_accents(self):
        assert rc.fold("Recherche Étudiants") == rc.fold("recherche etudiants")


def test_every_watched_service_is_configured():
    services = rc.load_services("prod")
    assert {w.key for w in rc.WATCHED} <= set(services)
    for watched in rc.WATCHED:
        for name in watched.specs:
            assert (rc.SPECS / name).exists(), name
        assert services[watched.key].wsdl.exists()
