"""Exception hierarchy for pyetnic.

This module defines the typed exceptions raised by EPROM services when
strict error mode is enabled (see phase 1.3 / opt-in raise-on-error).

The hierarchy is designed so that:

- ``except EtnicError`` catches everything pyetnic can raise.
- ``except EtnicBusinessError`` catches only server-side refusals
  (``success=False``), letting transport errors propagate.
- The legacy ``SoapError`` is an alias for ``EtnicTransportError``, so
  existing ``except SoapError`` code keeps working.

SEPS exceptions (``SepsEtnicError`` and subclasses) live in
``pyetnic.services.seps`` and are intentionally separate. They will be
unified with this hierarchy in a future major version.
"""

from typing import Optional


class EtnicError(Exception):
    """Base class for all pyetnic exceptions.

    Catch this if you want to handle any error from pyetnic.
    """


class EtnicTransportError(EtnicError):
    """Network-level or SOAP-protocol-level error.

    Raised when the SOAP request itself fails: connection refused, timeout,
    invalid SOAP envelope, malformed WSDL, etc. This is NOT raised when the
    server processes the request and returns ``success=False`` — see
    :class:`EtnicBusinessError` for that case.

    Attributes:
        message: Human-readable error description.
        soap_fault: The original zeep/requests exception, if any.
        request_id: The pyetnic-generated request ID for this call (useful
            when reporting bugs to ETNIC support).
    """

    def __init__(
        self,
        message: str,
        soap_fault: Optional[Exception] = None,
        request_id: Optional[str] = None,
    ):
        self.message = message
        self.soap_fault = soap_fault
        self.request_id = request_id
        super().__init__(message)


class EtnicBusinessError(EtnicError):
    """Server-side refusal of a valid request.

    Raised when ETNIC processes the request but returns ``success=False``.
    Examples: workflow violations (Doc1 not approved yet), invalid input
    values, business rule violations, document not accessible.

    Attributes:
        code: ETNIC error code (e.g. ``"20102"``, ``"00009"``). May be
            ``None`` if the response had no structured error.
        description: ETNIC's human-readable error description.
        request_id: The pyetnic-generated request ID for this call.
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        description: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.code = code
        self.description = description
        self.request_id = request_id
        super().__init__(message)


class EtnicDocumentNotAccessibleError(EtnicBusinessError):
    """A document is not yet accessible in the workflow.

    Raised when accessing Doc 1 / Doc 2 / Doc 3 before the prerequisite
    documents have been approved. Most notably, ETNIC error code 20102
    ("Doc 1 and Doc 2 must be approved before Doc 3 is accessible").

    This is a NORMAL workflow state, not a hard error — calling code may
    legitimately catch this exception to mean "not ready yet".
    """


class EtnicNotFoundError(EtnicBusinessError):
    """The requested resource does not exist.

    Raised when ETNIC reports that no record matches the query. ETNIC
    error code 00009 typically maps to this.
    """


class EtnicValidationError(EtnicBusinessError):
    """The request was rejected as malformed or invalid.

    Raised when ETNIC refuses the request for input-validation reasons:
    missing required fields, invalid format, value out of range, etc.
    """
