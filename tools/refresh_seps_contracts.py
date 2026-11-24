"""Refresh the embedded SEPS contracts from the live ETNIC services.

The SOA catalogue (extra.etnic.be, "Tableau des services web") offers contracts
labelled 2.1 that lag behind the services: the live WSDL of each production
endpoint, and the schemas it imports through the ETNIC gateway, are the current
contract. This script fetches them, rewrites every ``schemaLocation`` to the local
file of the same target namespace, and writes them over ``pyetnic/resources``.

Folder and file names are kept: each live document replaces the local document
that has the same ``targetNamespace``. A namespace present on one side only stops
the script rather than being guessed.

Usage:
    python tools/refresh_seps_contracts.py            # write, from production
    python tools/refresh_seps_contracts.py --check    # report only, exit 1 on drift
    python tools/refresh_seps_contracts.py --env tq   # TQ instead (lags production)
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

HOSTS = {"prod": "ws.etnic.be", "tq": "ws-tq.etnic.be"}

# Local resource folder -> service path on the ETNIC gateway.
SERVICES = {
    "SEPS_Enregistrer_Etudiant_2.1": "enregistrerEtudiant",
    "SEPS_Enregistrer_Inscription_2.1": "enregistrerInscription",
    "SEPS_Recherche_Etudiants_2.1": "rechercheEtudiants",
    "SEPS_Recherche_Inscriptions_2.1": "rechercheInscriptions",
}

SCHEMA_LOCATION = re.compile(rb'schemaLocation="([^"]+)"')
RESOURCES = Path(__file__).resolve().parent.parent / "pyetnic" / "resources"


@dataclass
class LiveDocument:
    url: str
    namespace: str
    data: bytes


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def target_namespace(data: bytes) -> str:
    namespace = ET.fromstring(data).get("targetNamespace")
    if not namespace:
        raise SystemExit("document without targetNamespace")
    return namespace


def crawl(wsdl_url: str) -> dict[str, LiveDocument]:
    """The live WSDL and every schema it imports, keyed by URL."""
    documents: dict[str, LiveDocument] = {}
    queue = [wsdl_url]
    while queue:
        url = queue.pop(0)
        if url in documents:
            continue
        data = fetch(url)
        documents[url] = LiveDocument(url, target_namespace(data), data)
        queue.extend(html.unescape(m.decode()) for m in SCHEMA_LOCATION.findall(data))
    return documents


def local_files(folder: Path) -> dict[str, Path]:
    """Local contract files of one service folder, keyed by target namespace."""
    files = list(folder.glob("*.wsdl")) + list((folder / "xsd").glob("*.xsd"))
    return {target_namespace(path.read_bytes()): path for path in files}


def localise(document: LiveDocument, by_url: dict[str, LiveDocument],
             by_namespace: dict[str, Path], folder: Path, own_path: Path) -> bytes:
    """Point every schemaLocation of a live document at the local file.

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

    data = SCHEMA_LOCATION.sub(replace, document.data)
    data = data.replace(b"\r\n", b"\n")
    return data if data.endswith(b"\n") else data + b"\n"


def element_names(data: bytes) -> set[str]:
    return {
        f"{el.tag.split('}')[-1]}:{el.get('name') or el.get('value')}"
        for el in ET.fromstring(data).iter()
        if el.get("name") or el.get("value")
    }


def refresh(env: str, check: bool) -> bool:
    """Refresh (or compare) every SEPS folder; True when something differs."""
    drift = False
    for folder_name, service in SERVICES.items():
        folder = RESOURCES / folder_name
        url = f"https://{HOSTS[env]}/seps/{service}/v1?wsdl"
        live = crawl(url)
        by_namespace = local_files(folder)
        live_namespaces = {doc.namespace for doc in live.values()}
        if live_namespaces != set(by_namespace):
            raise SystemExit(
                f"{folder_name}: namespaces differ, live only "
                f"{sorted(live_namespaces - set(by_namespace))}, "
                f"local only {sorted(set(by_namespace) - live_namespaces)}"
            )
        print(f"{folder_name} <- {url}")
        for document in live.values():
            path = by_namespace[document.namespace]
            new = localise(document, live, by_namespace, folder, path)
            old = path.read_bytes()
            if new == old:
                print(f"  unchanged  {path.relative_to(folder).as_posix()}")
                continue
            drift = True
            added = sorted(element_names(new) - element_names(old))
            removed = sorted(element_names(old) - element_names(new))
            print(f"  {'differs' if check else 'updated'}    {path.relative_to(folder).as_posix()}"
                  f"  +{added or ''} -{removed or ''}")
            if not check:
                path.write_bytes(new)
    return drift


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--env", choices=sorted(HOSTS), default="prod")
    parser.add_argument("--check", action="store_true", help="report only, exit 1 on drift")
    args = parser.parse_args()
    drift = refresh(args.env, args.check)
    sys.exit(1 if (args.check and drift) else 0)


if __name__ == "__main__":
    main()
