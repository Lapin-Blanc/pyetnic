"""Opt-in strict error mode for EPROM service calls.

Exposes the :func:`strict_errors` context manager. Inside a ``with
strict_errors():`` block, EPROM services raise typed exceptions
(``EtnicBusinessError`` and friends) instead of silently returning ``None``
or a ``FormationsListeResult(success=False, ...)``.

The flag itself lives in :attr:`pyetnic.config.Config.RAISE_ON_ERROR` and
is backed by a :class:`contextvars.ContextVar`, so it is automatically
per-thread and per-asyncio-task.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from .config import Config


@contextmanager
def strict_errors() -> Iterator[None]:
    """Enable strict error mode inside the enclosed block.

    While the block is active, EPROM service calls raise typed exceptions
    (``EtnicBusinessError``, ``EtnicDocumentNotAccessibleError``,
    ``EtnicNotFoundError``, ``EtnicValidationError``) instead of returning
    ``None`` (or ``FormationsListeResult(success=False, ...)``) on a
    server-side refusal.

    On exit, the previous value of ``Config.RAISE_ON_ERROR`` is restored,
    including when an exception propagates out of the block.

    Because ``Config.RAISE_ON_ERROR`` is backed by a ``ContextVar``, this
    is safe to use in multi-threaded and asyncio code: each thread / task
    sees its own value.

    Example::

        from pyetnic import strict_errors
        from pyetnic.eprom import lire_organisation

        with strict_errors():
            org = lire_organisation(org_id)  # raises on failure
    """
    previous = Config.RAISE_ON_ERROR
    Config.RAISE_ON_ERROR = True
    try:
        yield
    finally:
        Config.RAISE_ON_ERROR = previous
