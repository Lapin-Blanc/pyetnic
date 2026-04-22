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

from typing import Any, Optional, Tuple, Type


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


# ---------------------------------------------------------------------------
# Helpers used by EPROM services to signal errors in strict mode
# ---------------------------------------------------------------------------


def map_etnic_error_code_to_class(code: Optional[str]) -> Type[EtnicBusinessError]:
    """Map a known ETNIC error code to its specialized exception class.

    Returns :class:`EtnicBusinessError` for unknown codes.
    """
    if code is None:
        return EtnicBusinessError
    if code == "20102":
        return EtnicDocumentNotAccessibleError
    if code == "00009":
        return EtnicNotFoundError
    return EtnicBusinessError


def extract_error_info(result: Any) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract (code, description, request_id) from a SOAP response dict.

    Tolerant to missing/partial shapes — any field that cannot be found
    is returned as ``None``.
    """
    code: Optional[str] = None
    description: Optional[str] = None
    request_id: Optional[str] = None

    if not isinstance(result, dict):
        return code, description, request_id

    header = result.get("header")
    if isinstance(header, dict):
        rid = header.get("requestId")
        if rid is not None:
            request_id = str(rid)

    body = result.get("body")
    if not isinstance(body, dict):
        return code, description, request_id

    messages = body.get("messages") or {}
    if not isinstance(messages, dict):
        return code, description, request_id

    errors = messages.get("error")
    if not errors:
        return code, description, request_id

    err = errors[0] if isinstance(errors, list) else errors
    if isinstance(err, dict):
        if err.get("code") is not None:
            code = str(err.get("code"))
        description = err.get("description")

    return code, description, request_id


def signal_business_error(
    result: Any = None,
    *,
    message: Optional[str] = None,
    code: Optional[str] = None,
    description: Optional[str] = None,
    request_id: Optional[str] = None,
    error_class: Optional[Type[EtnicBusinessError]] = None,
) -> None:
    """Raise a typed business error if strict mode is on, else return ``None``.

    Service methods call this when they detect a server-side failure
    (``success=False``, empty ``response``, etc.).

    - In default mode (``Config.RAISE_ON_ERROR == False``), this function
      returns ``None`` silently, preserving the legacy "return None on
      error" contract.
    - In strict mode, it raises a subclass of :class:`EtnicBusinessError`
      chosen by :func:`map_etnic_error_code_to_class` (unless
      ``error_class`` is given explicitly).

    Args:
        result: The raw SOAP response dict. If provided, error fields
            (code, description, request_id) missing from the kwargs are
            extracted from it via :func:`extract_error_info`.
        message: Human-readable error message. Auto-generated from the
            code and description if omitted.
        code: ETNIC error code if already known.
        description: ETNIC error description if already known.
        request_id: Request ID for traceability.
        error_class: Specific exception class to raise. Defaults to the
            class returned by :func:`map_etnic_error_code_to_class`.

    Returns:
        ``None`` — but only in default mode. In strict mode, this raises.
    """
    # Local import to avoid a circular import at module load time.
    from .config import Config

    if not Config.RAISE_ON_ERROR:
        return None

    if result is not None and (code is None or description is None or request_id is None):
        ex_code, ex_desc, ex_rid = extract_error_info(result)
        code = code if code is not None else ex_code
        description = description if description is not None else ex_desc
        request_id = request_id if request_id is not None else ex_rid

    cls = error_class or map_etnic_error_code_to_class(code)
    if message is None:
        message = f"ETNIC business error (code={code}, description={description})"

    raise cls(message, code=code, description=description, request_id=request_id)
