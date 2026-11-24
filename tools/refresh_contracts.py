"""Watch, and refresh, the ETNIC contracts embedded in pyetnic.

Three sources are compared with the repository, for every service of
``Config.SERVICES``:

1. **The live service.** Its WSDL is fetched from the ETNIC gateway. Where it
   imports its schemas by absolute URL (SEPS, Formation Organisation), the
   gateway serves them too and the whole contract is compared. Where it imports
   them by relative path (Formations Liste, Documents 1, 2 and 3), the gateway
   refuses them ("Policy Falsified"): the WSDL alone is compared live, and the
   schemas come from the catalogue archive.
2. **The SOA catalogue** (extra.etnic.be, "Tableau services web"): the version
   and the endpoints it announces, its contract archive, and the user manuals
   with their revision. Every manual file the catalogue publishes for a service
   must be named by the spec of that service, so that a new revision is noticed.
   A catalogue service of a watched product that pyetnic does not embed is
   reported too.
3. **The next major version** of each service (``/v8`` while ``/v7`` is
   embedded): the gateway answers 404 for a version that does not exist.

Documents are compared in canonical form (C14N 2.0, comments and surrounding
whitespace dropped, ``schemaLocation`` reduced to its file name, endpoint
address ignored): formatting differences between the gateway, the catalogue and
the repository are not drift.

Without ``--check``, the embedded contracts are rewritten from the live service
(and from the catalogue archive for the schemas the gateway does not serve).
A service folder that does not exist yet is first created from the catalogue
archive, which gives the file names, then refreshed from the live service. The
versions, endpoints and manuals are only reported: they call for a change of
code or of spec, not for a file refresh.

Usage:
    python tools/refresh_contracts.py --check               # report, exit 1 on drift
    python tools/refresh_contracts.py --check --report drift.md
    python tools/refresh_contracts.py                       # refresh the contracts
    python tools/refresh_contracts.py --env tq --check      # TQ (lags production)
    python tools/refresh_contracts.py --service ORGANISATION

Exit codes: 0 nothing differs, 1 drift, 2 a source could not be read.
"""

from __future__ import annotations

import argparse
import html
import io
import posixpath
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "pyetnic" / "resources"
SPECS = ROOT / "specs"

HOSTS = {"prod": "ws.etnic.be", "tq": "ws-tq.etnic.be"}
CONFIG_ENV = {"prod": "prod", "tq": "dev"}
CATALOGUE_ROOT = "https://extra.etnic.be"
CATALOGUE = CATALOGUE_ROOT + "/catalogue-de-services/solutions-applicatives/tableau-services-web"
WATCHED_PRODUCTS = ("EPROM", "SEPS")
USER_AGENT = "pyetnic-contract-watch (+https://github.com/Lapin-Blanc/pyetnic)"
TIMEOUT = 60


@dataclass(frozen=True)
class Watched:
    """A service of ``Config.SERVICES`` and where the catalogue and the specs describe it."""

    key: str
    product: str
    catalogue_name: str
    specs: tuple[str, ...]


# The country and municipality code lists the catalogue files with the SEPS
# student services are described by the referentials spec.
REFERENTIELS = "15_referentiels_seps.md"

WATCHED = [
    Watched("LISTE_FORMATIONS", "EPROM", "Formations Liste", ("01_formations_liste_v2.md",)),
    Watched("ORGANISATION", "EPROM", "Formation Organisation", ("02_formation_organisation_v7.md",)),
    Watched("DOCUMENT1", "EPROM", "Formation Population", ("03_formation_population_v1.md",)),
    Watched("DOCUMENT2", "EPROM", "Formation Périodes", ("04_formation_periodes_v1.md",)),
    Watched("DOCUMENT3", "EPROM", "Document 3", ("05_document3_v1.md",)),
    Watched("SEPS_RECHERCHE_ETUDIANTS", "SEPS", "Recherche Étudiants", ("09_seps_recherche_etudiants_v1.md", REFERENTIELS)),
    Watched("SEPS_ENREGISTRER_ETUDIANT", "SEPS", "Enregistrer Étudiant", ("10_seps_enregistrer_etudiant_v1.md", REFERENTIELS)),
    Watched("SEPS_ENREGISTRER_INSCRIPTION", "SEPS", "Enregistrer Inscription", ("11_seps_enregistrer_inscription_v1.md",)),
    Watched("SEPS_RECHERCHE_INSCRIPTIONS", "SEPS", "Recherche Inscriptions", ("12_seps_recherche_inscriptions_v1.md",)),
    Watched("SEPS_NOTIFICATIONS", "SEPS", "Notifications", ("13_seps_notifications_v1.md",)),
]


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------


class SourceError(Exception):
    """A source (gateway, catalogue) could not be read."""


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise SourceError(f"HTTP {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SourceError(f"{exc} for {url}") from exc


def status(url: str) -> int:
    """HTTP status of a GET, without raising on 4xx/5xx."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise SourceError(f"{exc} for {url}") from exc


# ---------------------------------------------------------------------------
# XML documents
# ---------------------------------------------------------------------------

SCHEMA_LOCATION = re.compile(rb'schemaLocation="([^"]+)"')


def target_namespace(data: bytes) -> str:
    namespace = ET.fromstring(data).get("targetNamespace")
    if not namespace:
        raise SourceError("document without targetNamespace")
    return namespace


def imports(data: bytes) -> list[str]:
    return [html.unescape(m.decode()) for m in SCHEMA_LOCATION.findall(data)]


def is_absolute(location: str) -> bool:
    return urllib.parse.urlparse(location).scheme in ("http", "https")


XSD = "{http://www.w3.org/2001/XMLSchema}"
WSDL = "{http://schemas.xmlsoap.org/wsdl/}"
NOT_CONTRACT = {XSD + "annotation", WSDL + "documentation"}
# Children whose order carries no meaning: top-level declarations of a WSDL or a
# schema, and the operations of a port type or a binding.
UNORDERED = {WSDL + "definitions", XSD + "schema", WSDL + "types", WSDL + "portType", WSDL + "binding"}


def file_name(location: str) -> str:
    """Last segment of a path or URL; the catalogue sometimes writes Windows separators."""
    return posixpath.basename(html.unescape(location).replace("\\", "/"))


def canonical(data: bytes) -> str:
    """Canonical form of a WSDL or XSD, blind to what does not change the contract.

    Formatting, comments, annotations, the order of top-level declarations and of
    operations, the path of each import (reduced to its file name) and the
    endpoint address are ignored.
    """
    root = ET.fromstring(data)

    def serialised(element: ET.Element) -> str:
        return ET.canonicalize(ET.tostring(element, encoding="unicode"), strip_text=True)

    def clean(element: ET.Element) -> None:
        if element.text is not None and not element.text.strip():
            element.text = None
        for child in list(element):
            if child.tag in NOT_CONTRACT:
                element.remove(child)
                continue
            if child.tail is not None and not child.tail.strip():
                child.tail = None
            clean(child)
        if element.get("schemaLocation"):
            element.set("schemaLocation", file_name(element.get("schemaLocation")))
        if element.tag.endswith("}address") and "location" in element.attrib:
            del element.attrib["location"]
        if element.tag in UNORDERED:
            element[:] = sorted(element, key=serialised)

    clean(root)
    return serialised(root)


def element_names(data: bytes) -> set[str]:
    return {
        f"{el.tag.split('}')[-1]}:{el.get('name') or el.get('value')}"
        for el in ET.fromstring(data).iter()
        if el.get("name") or el.get("value")
    }


def describe_change(old: bytes, new: bytes) -> str:
    added = sorted(element_names(new) - element_names(old))
    removed = sorted(element_names(old) - element_names(new))
    parts = []
    if added:
        parts.append("added " + ", ".join(added))
    if removed:
        parts.append("removed " + ", ".join(removed))
    return "; ".join(parts) or "same names, other content"


def normalise(data: bytes) -> bytes:
    data = data.replace(b"\r\n", b"\n")
    return data if data.endswith(b"\n") else data + b"\n"


@dataclass
class LiveDocument:
    url: str
    namespace: str
    data: bytes


def crawl(wsdl_url: str) -> dict[str, LiveDocument]:
    """The live WSDL and every schema it imports by absolute URL, keyed by URL."""
    documents: dict[str, LiveDocument] = {}
    queue = [wsdl_url]
    while queue:
        url = queue.pop(0)
        if url in documents:
            continue
        data = fetch(url)
        documents[url] = LiveDocument(url, target_namespace(data), data)
        queue.extend(loc for loc in imports(data) if is_absolute(loc))
    return documents


def local_files(folder: Path) -> dict[str, Path]:
    """Contract files of one service folder, keyed by target namespace."""
    files = list(folder.glob("*.wsdl")) + list((folder / "xsd").glob("*.xsd"))
    return {target_namespace(path.read_bytes()): path for path in files}


def localise(document: LiveDocument, by_url: dict[str, LiveDocument],
             by_namespace: dict[str, Path], folder: Path, own_path: Path) -> bytes:
    """Point every absolute schemaLocation of a live document at the local file.

    The WSDL sits at the folder root and imports ``xsd/<file>``; a schema sits in
    ``xsd/`` and imports its siblings by bare file name.
    """
    in_xsd = own_path.parent.name == "xsd"

    def replace(match: re.Match[bytes]) -> bytes:
        target = by_url[html.unescape(match.group(1).decode())]
        relative = by_namespace[target.namespace].relative_to(folder)
        if in_xsd:
            relative = relative.relative_to("xsd")
        return b'schemaLocation="' + relative.as_posix().encode() + b'"'

    return normalise(SCHEMA_LOCATION.sub(replace, document.data))


def localise_relative(data: bytes) -> bytes:
    """Point the relative imports of a live WSDL (``../xsd/eprom/X.xsd``) at ``xsd/X.xsd``."""

    def replace(match: re.Match[bytes]) -> bytes:
        return b'schemaLocation="xsd/' + file_name(match.group(1).decode()).encode() + b'"'

    return normalise(SCHEMA_LOCATION.sub(replace, data))


# ---------------------------------------------------------------------------
# SOA catalogue
# ---------------------------------------------------------------------------

ANCHOR = re.compile(r'<a\b[^>]*?href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
FIELD = re.compile(r"<label\b[^>]*>(.*?)</label>\s*<div\b[^>]*>(.*?)</div>", re.DOTALL)
ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.DOTALL)
CELL = re.compile(r"<td\b[^>]*>(.*?)</td>", re.DOTALL)
PLUGIN = "tx_etnicservices_webservicefrt"


@dataclass
class Manual:
    name: str
    revision: str
    date: str
    url: str

    @property
    def file(self) -> str:
        return file_name(urllib.parse.unquote(urllib.parse.urlparse(self.url).path))


@dataclass
class CatalogueEntry:
    product: str
    name: str
    version: str
    page: str
    contract: str | None = None
    endpoint_tq: str | None = None
    endpoint_prod: str | None = None
    manuals: list[Manual] = field(default_factory=list)


def decode(data: bytes) -> str:
    """The catalogue declares UTF-8 but serves some pages in Windows-1252."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252")


def text(fragment: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def fold(value: str) -> str:
    """Case- and accent-insensitive key, for names the catalogue may re-encode."""
    stripped = unicodedata.normalize("NFKD", value)
    return "".join(c for c in stripped if not unicodedata.combining(c)).casefold().strip()


def plugin_query(href: str) -> dict[str, str]:
    query = urllib.parse.parse_qs(urllib.parse.urlparse(html.unescape(href)).query)
    prefix = PLUGIN + "["
    return {k[len(prefix):-1]: v[0] for k, v in query.items() if k.startswith(prefix)}


def parse_table(page: str) -> list[CatalogueEntry]:
    """Services of the catalogue table: each row links every cell to the service page."""
    cells: dict[str, list[str]] = {}
    hrefs: dict[str, str] = {}
    for href, inner in ANCHOR.findall(page):
        query = plugin_query(href)
        if query.get("action") != "show" or "serviceid" not in query:
            continue
        service_id = query["serviceid"]
        cells.setdefault(service_id, []).append(text(inner))
        hrefs[service_id] = html.unescape(href)
    return [
        CatalogueEntry(product=values[0], name=values[1], version=values[2],
                       page=urllib.parse.urljoin(CATALOGUE_ROOT, hrefs[service_id]))
        for service_id, values in cells.items()
        if len(values) >= 3
    ]


def parse_service_page(entry: CatalogueEntry, page: str) -> CatalogueEntry:
    fields = {text(label): text(value) for label, value in FIELD.findall(page)}
    entry.endpoint_tq = fields.get("Endpoint URL TQ") or None
    entry.endpoint_prod = fields.get("Endpoint URL PROD") or None
    for href, _ in ANCHOR.findall(page):
        if plugin_query(href).get("action") == "download":
            entry.contract = urllib.parse.urljoin(CATALOGUE_ROOT, html.unescape(href))
            break
    for row in ROW.findall(page):
        cells = CELL.findall(row)
        if len(cells) < 5:
            continue
        link = ANCHOR.search(cells[-1])
        if link:
            entry.manuals.append(Manual(
                name=text(cells[0]), revision=text(cells[1]), date=text(cells[2]),
                url=urllib.parse.urljoin(CATALOGUE_ROOT, html.unescape(link.group(1))),
            ))
    return entry


def read_catalogue() -> list[CatalogueEntry]:
    entries = [e for e in parse_table(decode(fetch(CATALOGUE))) if e.product in WATCHED_PRODUCTS]
    if not entries:
        raise SourceError(f"no {'/'.join(WATCHED_PRODUCTS)} service in {CATALOGUE}")
    return [parse_service_page(e, decode(fetch(e.page))) for e in entries]


def read_archive(url: str) -> dict[str, bytes]:
    """Files of a catalogue contract archive, by path (``X.wsdl``, ``xsd/Y.xsd``)."""
    with zipfile.ZipFile(io.BytesIO(fetch(url))) as archive:
        return {
            info.filename.replace("\\", "/"): archive.read(info)
            for info in archive.infolist()
            if not info.is_dir() and info.filename.lower().endswith((".wsdl", ".xsd"))
        }


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------


@dataclass
class Service:
    """A service as pyetnic configures it, in one environment."""

    key: str
    endpoint: str
    wsdl_path: str

    @property
    def path(self) -> str:
        return urllib.parse.urlparse(self.endpoint).path.strip("/")

    @property
    def folder(self) -> Path:
        return RESOURCES / self.wsdl_path.split("/")[0]

    @property
    def wsdl(self) -> Path:
        return RESOURCES / self.wsdl_path

    @property
    def folder_version(self) -> str | None:
        match = re.search(r"_(\d+(?:\.\d+)*)$", self.folder.name)
        return match.group(1) if match else None


@dataclass
class Report:
    drift: list[tuple[str, str]] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)
    written: list[str] = field(default_factory=list)

    def add(self, service: str, message: str) -> None:
        self.drift.append((service, message))
        print(f"  DRIFT  {service}: {message}")

    def error(self, service: str, message: str) -> None:
        self.errors.append((service, message))
        print(f"  ERROR  {service}: {message}")

    def wrote(self, path: Path) -> None:
        self.written.append(path.relative_to(ROOT).as_posix())
        print(f"  wrote  {path.relative_to(ROOT).as_posix()}")

    def markdown(self, env: str) -> str:
        lines = [f"Contract watch ({env}, `tools/refresh_contracts.py --check`).", ""]
        if self.drift:
            lines += ["### Drift", ""]
            lines += [f"- **{service}**: {message}" for service, message in self.drift]
            lines.append("")
        if self.errors:
            lines += ["### Sources that could not be read", ""]
            lines += [f"- **{service}**: {message}" for service, message in self.errors]
            lines.append("")
        if not self.drift and not self.errors:
            lines.append("Nothing differs.")
        return "\n".join(lines) + "\n"


def bootstrap(service: Service, archive: dict[str, bytes], report: Report) -> None:
    """Create a missing service folder from the catalogue archive."""
    for name, data in archive.items():
        target = service.folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(normalise(data))
        report.wrote(target)


def compare_served(service: Service, url: str, report: Report, write: bool) -> None:
    """Whole contract served by the gateway: compare (and refresh) every document."""
    live = crawl(url)
    by_namespace = local_files(service.folder)
    live_namespaces = {doc.namespace for doc in live.values()}
    if live_namespaces != set(by_namespace):
        report.add(service.key, f"namespaces differ: live only {sorted(live_namespaces - set(by_namespace))}, "
                                f"local only {sorted(set(by_namespace) - live_namespaces)}")
        return
    for document in live.values():
        path = by_namespace[document.namespace]
        new = localise(document, live, by_namespace, service.folder, path)
        old = path.read_bytes()
        if canonical(new) == canonical(old):
            continue
        name = path.relative_to(service.folder).as_posix()
        if write:
            path.write_bytes(new)
            report.wrote(path)
        else:
            report.add(service.key, f"live `{name}` differs ({describe_change(old, new)})")


def compare_wsdl_only(service: Service, live_wsdl: bytes, archive: dict[str, bytes] | None,
                      report: Report, write: bool) -> None:
    """Schemas not served: compare the WSDL live, the schemas with the catalogue archive."""
    old = service.wsdl.read_bytes()
    if canonical(live_wsdl) != canonical(old):
        if write:
            service.wsdl.write_bytes(localise_relative(live_wsdl))
            report.wrote(service.wsdl)
        else:
            report.add(service.key, f"live WSDL differs ({describe_change(old, live_wsdl)})")
    if archive is None:
        return
    archive_wsdls = [data for name, data in archive.items() if name.endswith(".wsdl")]
    if archive_wsdls and canonical(archive_wsdls[0]) != canonical(live_wsdl):
        report.add(service.key, "the catalogue archive's WSDL differs from the live one: "
                                "its schemas may lag behind the service")
        if write:
            return
    local = {p.name: p for p in (service.folder / "xsd").glob("*.xsd")}
    remote = {file_name(n): d for n, d in archive.items() if n.endswith(".xsd")}
    for name in sorted(set(remote) - set(local)):
        if write:
            target = service.folder / "xsd" / name
            target.write_bytes(normalise(remote[name]))
            report.wrote(target)
        else:
            report.add(service.key, f"schema `{name}` is in the catalogue archive, not in the repository")
    for name in sorted(set(local) - set(remote)):
        report.add(service.key, f"schema `{name}` is in the repository, not in the catalogue archive")
    for name in sorted(set(local) & set(remote)):
        old_xsd = local[name].read_bytes()
        if canonical(old_xsd) == canonical(remote[name]):
            continue
        if write:
            local[name].write_bytes(normalise(remote[name]))
            report.wrote(local[name])
        else:
            report.add(service.key, f"catalogue schema `{name}` differs ({describe_change(old_xsd, remote[name])})")


def watch_live(service: Service, url: str, host: str, archive: dict[str, bytes] | None,
               report: Report, write: bool) -> None:
    """Compare (or refresh) one service with its live contract, then probe its next version."""
    if not service.folder.exists():
        if not write:
            report.add(service.key, f"`{service.folder.relative_to(ROOT).as_posix()}` does not exist")
            return
        if archive is None:
            report.error(service.key, "no catalogue archive to create the service folder from")
            return
        bootstrap(service, archive, report)
    live_wsdl = fetch(url)
    if all(is_absolute(location) for location in imports(live_wsdl)):
        compare_served(service, url, report, write)
    else:
        compare_wsdl_only(service, live_wsdl, archive, report, write)
    following = next_version(service.path)
    if following and status(f"https://{host}/{following}?wsdl") == 200:
        report.add(service.key, f"a next version is live: https://{host}/{following}")


def next_version(path: str) -> str | None:
    match = re.search(r"/v(\d+)$", "/" + path)
    return re.sub(r"v\d+$", f"v{int(match.group(1)) + 1}", path) if match else None


def check_catalogue(watched: Watched, prod: Service, tq: Service,
                    entry: CatalogueEntry | None, report: Report) -> None:
    if entry is None:
        report.add(watched.key, f"no catalogue entry named {watched.product} / {watched.catalogue_name}")
        return
    if prod.folder_version and entry.version != prod.folder_version:
        report.add(watched.key, f"the catalogue announces version {entry.version}, "
                                f"the repository embeds `{prod.folder.name}`")
    for label, announced, configured in (("PROD", entry.endpoint_prod, prod.endpoint),
                                         ("TQ", entry.endpoint_tq, tq.endpoint)):
        if announced and announced.rstrip("/") != configured.rstrip("/"):
            report.add(watched.key, f"the catalogue announces the {label} endpoint {announced}, "
                                    f"pyetnic calls {configured}")
    specs = ""
    for name in watched.specs:
        if (SPECS / name).exists():
            specs += (SPECS / name).read_text(encoding="utf-8")
        else:
            report.add(watched.key, f"`specs/{name}` does not exist")
    named_by = ", ".join(f"`specs/{name}`" for name in watched.specs)
    for manual in entry.manuals:
        if manual.file not in specs:
            report.add(watched.key, f"manual \"{manual.name}\" rev. {manual.revision} ({manual.date}) "
                                    f"is not named by {named_by}: {manual.url}")


def load_services(env: str) -> dict[str, Service]:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from pyetnic.config import Config, _ConfigMeta  # the tool runs from a checkout

    # Leave the caller's configuration as it was, override included or not.
    overrides = _ConfigMeta._overrides
    had_override, previous = "ENV" in overrides, overrides.get("ENV")
    Config.ENV = env
    try:
        return {key: Service(key, cfg.endpoint, cfg.wsdl_path) for key, cfg in Config.SERVICES.items()}
    finally:
        if had_override:
            overrides["ENV"] = previous
        else:
            overrides.pop("ENV", None)


def run(env: str, write: bool, only: set[str] | None) -> Report:
    report = Report()
    prod_services = load_services(CONFIG_ENV["prod"])
    tq_services = load_services(CONFIG_ENV["tq"])
    services = load_services(CONFIG_ENV[env])
    host = HOSTS[env]

    print(f"Catalogue <- {CATALOGUE}")
    try:
        catalogue = read_catalogue()
    except SourceError as exc:
        report.error("catalogue", str(exc))
        catalogue = []
    by_name = {(e.product, fold(e.name)): e for e in catalogue}

    for watched in WATCHED:
        if only and watched.key not in only:
            continue
        service = services.get(watched.key)
        if service is None:
            report.error(watched.key, "not in Config.SERVICES")
            continue
        url = f"https://{host}/{service.path}?wsdl"
        print(f"{watched.key} <- {url}")
        entry = by_name.get((watched.product, fold(watched.catalogue_name)))
        archive = None
        if entry and entry.contract:
            try:
                archive = read_archive(entry.contract)
            except (SourceError, zipfile.BadZipFile) as exc:
                report.error(watched.key, f"catalogue archive: {exc}")
        try:
            watch_live(service, url, host, archive, report, write)
        except (SourceError, ET.ParseError) as exc:
            report.error(watched.key, str(exc))
        if catalogue:
            check_catalogue(watched, prod_services[watched.key], tq_services[watched.key], entry, report)

    if catalogue and not only:
        known = {(w.product, fold(w.catalogue_name)) for w in WATCHED}
        for entry in catalogue:
            if (entry.product, fold(entry.name)) not in known:
                report.add(f"{entry.product} / {entry.name}",
                           f"version {entry.version} is in the catalogue, not in pyetnic: {entry.page}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--env", choices=sorted(HOSTS), default="prod")
    parser.add_argument("--check", action="store_true", help="report only, exit 1 on drift")
    parser.add_argument("--report", type=Path, help="write the report as Markdown to this file")
    parser.add_argument("--service", action="append", help="limit to these Config.SERVICES keys")
    args = parser.parse_args()
    report = run(args.env, write=not args.check, only=set(args.service) if args.service else None)
    if args.report:
        args.report.write_text(report.markdown(args.env), encoding="utf-8")
    print(f"{len(report.drift)} drift, {len(report.errors)} error(s), {len(report.written)} file(s) written")
    if report.errors:
        sys.exit(2)
    sys.exit(1 if (args.check and report.drift) else 0)


if __name__ == "__main__":
    main()
