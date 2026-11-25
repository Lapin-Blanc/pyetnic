"""Public names kept until 1.0, served with a ``DeprecationWarning`` (PEP 562).

``SoapError`` and ``TYPES_INTERVENTION_EXTERIEURE`` were documented as deprecated
since 0.1.0 but never warned, while the deprecation process
(``docs/BACKWARDS_COMPAT.md``) asks for a warning before a removal. The public
modules that export them resolve them through :func:`deprecated_name` in their
module ``__getattr__``, so the warning names the caller's line.

Internal code keeps using ``pyetnic.soap_client.SoapError``, which does not warn:
the services still raise it, so that ``except SoapError`` keeps working until 1.0.
"""

from __future__ import annotations

import warnings
from typing import Any

DEPRECATED_NAMES = ("SoapError", "TYPES_INTERVENTION_EXTERIEURE")

_MESSAGES = {
    "SoapError": (
        "SoapError is deprecated and goes in pyetnic 1.0: catch EtnicTransportError, "
        "the class it derives from"
    ),
    "TYPES_INTERVENTION_EXTERIEURE": (
        "TYPES_INTERVENTION_EXTERIEURE is deprecated and goes in pyetnic 1.0: use the "
        "TypeInterventionExterieure enum ([m.value for m in TypeInterventionExterieure])"
    ),
}


def deprecated_name(name: str) -> Any:
    """The value of the deprecated public ``name``, after a ``DeprecationWarning``.

    Called from a module ``__getattr__``: ``stacklevel`` points past it, at the
    line that imported or read the name.
    """
    warnings.warn(_MESSAGES[name], DeprecationWarning, stacklevel=3)
    if name == "SoapError":
        from .soap_client import SoapError

        return SoapError
    from .nomenclatures import _TYPES_INTERVENTION_EXTERIEURE

    return _TYPES_INTERVENTION_EXTERIEURE
