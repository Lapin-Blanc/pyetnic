"""``import pyetnic`` does no I/O (H7, settled for 1.0).

The audit (H7) found that importing pyetnic instantiated every service, the SEPS
clients and their X509 certificate included. The service singletons still exist,
but a service only stores its name until the first call: the import reads no
``.env``, no certificate and no WSDL, and builds no zeep client. This pins it, in a
fresh interpreter since the test session has already imported pyetnic.
"""

from __future__ import annotations

import subprocess
import sys

_PROBE = """
import builtins, io
opened = []
_open = io.open
def spy(file, *args, **kwargs):
    opened.append(str(file))
    return _open(file, *args, **kwargs)
builtins.open = io.open = spy

import pyetnic, pyetnic.eprom, pyetnic.seps, pyetnic.services
from pyetnic.config import _ConfigMeta
from pyetnic.soap_client import SoapClientManager

assert not _ConfigMeta._dotenv_loaded, "the import read the .env"
assert not SoapClientManager._client_cache, "the import built a zeep client"
touched = [f for f in opened if f.lower().endswith((".env", ".pfx", ".p12", ".wsdl", ".xsd"))]
assert not touched, touched
print("clean")
"""


def test_import_reads_nothing_and_builds_no_client(tmp_path):
    done = subprocess.run(
        [sys.executable, "-c", _PROBE], cwd=tmp_path, capture_output=True, text=True, timeout=120,
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == "clean"
