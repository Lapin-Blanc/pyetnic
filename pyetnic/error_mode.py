"""Error mode of the EPROM services: raise (the default) or return ``None``.

Since 0.3.0 the EPROM services raise typed exceptions (``EtnicBusinessError``
and its subclasses) when the server refuses a call, as the SEPS services
always did. The flag lives in :attr:`pyetnic.config.Config.RAISE_ON_ERROR`,
backed by a :class:`contextvars.ContextVar`, so it is per thread and per
asyncio task.

- :func:`strict_errors` forces the raising mode inside a block. It is the
  default now; the context manager keeps working, and restores raising inside
  a :func:`permissive_errors` block.
- :func:`permissive_errors` (or ``Config.RAISE_ON_ERROR = False``) restores the
  pre-0.3.0 behaviour inside a block: ``None`` (or
  ``FormationsListeResult(success=False, ...)``) instead of an exception. It is
  meant for code still testing for ``None`` during its migration, is
  deprecated, and will be removed in 1.0.
"""

from __future__ import annotations

import warnings
from contextlib import contextmanager
from typing import Iterator

from .config import _raise_on_error

PERMISSIVE_DEPRECATION = (
    "pyetnic's permissive error mode (None instead of an exception) is deprecated "
    "since 0.3.0 and will be removed in 1.0: catch EtnicBusinessError instead."
)


@contextmanager
def strict_errors() -> Iterator[None]:
    """Raise typed exceptions inside the enclosed block (the default since 0.3.0).

    On exit, the previous mode is restored, including when an exception
    propagates out of the block. Safe in multi-threaded and asyncio code:
    each thread / task sees its own value.

    Example::

        from pyetnic import strict_errors
        from pyetnic.eprom import lire_organisation

        with strict_errors():
            org = lire_organisation(org_id)  # raises on failure
    """
    token = _raise_on_error.set(True)
    try:
        yield
    finally:
        _raise_on_error.reset(token)


@contextmanager
def permissive_errors() -> Iterator[None]:
    """Return ``None`` on a server refusal inside the enclosed block (deprecated).

    The pre-0.3.0 behaviour, for code that still tests for ``None``: readers
    and writers return ``None``, ``lister_formations*`` a
    ``FormationsListeResult(success=False, ...)``, ``supprimer_organisation``
    ``False``. Emits a :class:`DeprecationWarning`; removed in 1.0.
    """
    warnings.warn(PERMISSIVE_DEPRECATION, DeprecationWarning, stacklevel=3)
    token = _raise_on_error.set(False)
    try:
        yield
    finally:
        _raise_on_error.reset(token)
