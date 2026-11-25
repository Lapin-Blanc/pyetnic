"""Exception hierarchy for pyetnic.

This module defines the typed exceptions the EPROM services raise when the
server refuses a call: the default since 0.3.0 (see :mod:`pyetnic.error_mode`).

The hierarchy is designed so that:

- ``except EtnicError`` catches everything pyetnic can raise.
- ``except EtnicBusinessError`` catches only server-side refusals
  (``success=False``), letting transport errors propagate.
- ``EtnicResponseError`` is an answer that breaks its own contract (a value
  zeep cannot convert to its declared type).
- The legacy ``SoapError`` is an alias for ``EtnicTransportError``, so
  existing ``except SoapError`` code keeps working.

SEPS exceptions (``SepsEtnicError`` and subclasses) live in
``pyetnic.services.seps_errors`` and join this hierarchy: ``SepsEtnicError``
derives from ``EtnicBusinessError``, and the SEPS validation and not-found
errors also derive from ``EtnicValidationError`` and ``EtnicNotFoundError``.
SEPS services always raise on a refusal: ``Config.RAISE_ON_ERROR`` does not
apply to them.
"""

from typing import Any, List, Optional, Tuple, Type


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


class EtnicResponseError(EtnicError):
    """A value of the response does not match its type in the contract.

    zeep cannot convert it (a decimal in an ``xs:int``, a date that is not
    one...): it logs the failure and would hand ``None`` to the model, as if
    the element were absent, and a read-merge-write would then erase the
    stored value. pyetnic raises instead (#52). The server did answer: this is
    neither a transport error nor a refusal.

    Detection reads zeep's own error log: a zeep logger disabled or set above
    ``ERROR`` turns it off (pyetnic then logs a warning).

    Attributes:
        message: Human-readable error description.
        values: ``(element, raw text)`` of each value that failed, in the
            order zeep met them; an attribute is named ``@name``.
        response: The whole response as a dict, each failed value at ``None``.
        request_id: The pyetnic-generated request ID for this call.
    """

    def __init__(
        self,
        message: str,
        values: Optional[List[Tuple[Optional[str], Optional[str]]]] = None,
        response: Optional[dict] = None,
        request_id: Optional[str] = None,
    ):
        self.message = message
        self.values = values or []
        self.response = response
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

    Raised when accessing a document before the prerequisite documents have
    been approved: 20101 for Documents 1 and 1D before "Doc A" (the
    organisation itself) is approved, 20103 for Document 2 before the Doc 1
    population is validated, 20102 for Document 3 before Doc A and Doc 2 are
    approved. Also 20112 (1546 in the manual), a Document 1D fee written
    before its population is approved, and 30003 / 30006 (document status,
    PO step not active).

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
    Covers the bulk of the ETNIC catalogue (most ``20xxx``/``30xxx`` codes,
    the population-consistency ``4004``-``4012`` range, etc.).
    """


class EtnicAlreadyApprovedError(EtnicBusinessError):
    """The document is already approved, so the operation is refused.

    1530: approved by the administration, nothing is writable any more.
    1545 (Documents 1 and 1D): approved by the school, the population is
    frozen and a second approval is refused. Document 2 uses 1545 for
    something else (see ``_SERVICE_CODE_TO_CLASS``).
    """


class EtnicConcurrencyError(EtnicBusinessError):
    """The record was modified by another user since it was read.

    Optimistic-concurrency violation (code 00011), and the approval of
    Documents 1 and 1D sent with values that differ from the stored ones
    (code 20104): re-read and retry.
    """


# ---------------------------------------------------------------------------
# Helpers used by EPROM services to signal errors in strict mode
# ---------------------------------------------------------------------------


# Discrete ETNIC error codes → exception class. String keys preserve the
# leading zeros ETNIC uses (e.g. "00009", "00011"). Source: specs/00_REGISTRE.md
# §4 "Codes d'erreur communs". Codes 00025 (security) and 00999 (internal SQL)
# are intentionally left on the base class: they are not client-fixable.
_CODE_TO_CLASS: dict[str, Type[EtnicBusinessError]] = {
    "00009": EtnicNotFoundError,
    # Workflow / document not accessible: Doc A not approved (Documents 1 and
    # 1D), Doc 1 population not validated (Document 2), Doc A and Doc 2 not
    # approved (Document 3)
    "20101": EtnicDocumentNotAccessibleError,
    "20103": EtnicDocumentNotAccessibleError,
    "20102": EtnicDocumentNotAccessibleError,
    "30003": EtnicDocumentNotAccessibleError,
    "30006": EtnicDocumentNotAccessibleError,
    # Not yet approved: Doc 1D fees written before the population is approved
    # (20112 on the wire, tested on TQ 2026-11-24; 1546 in the manual)
    "20112": EtnicDocumentNotAccessibleError,
    "1546": EtnicDocumentNotAccessibleError,
    # Already approved (by the school for 1545, by the administration for 1530).
    # 1545 means something else for Document 2: see _SERVICE_CODE_TO_CLASS.
    "1530": EtnicAlreadyApprovedError,
    "1545": EtnicAlreadyApprovedError,
    # Optimistic-concurrency violation; 20104: the values sent to an approval
    # (Documents 1 and 1D) differ from the stored ones, reload and retry
    "00011": EtnicConcurrencyError,
    "20104": EtnicConcurrencyError,
    # Input validation — Organisation (30xxx)
    "30001": EtnicValidationError,
    "30002": EtnicValidationError,
    "30004": EtnicValidationError,
    "30005": EtnicValidationError,
    "30007": EtnicValidationError,
    "30008": EtnicValidationError,
    "30009": EtnicValidationError,
    "30010": EtnicValidationError,  # BESAeSI before 2026-2027 (Organisation v8)
    # Input validation — Organisation (20xxx)
    "20005": EtnicValidationError,
    "20006": EtnicValidationError,
    "20007": EtnicValidationError,
    "20010": EtnicValidationError,
    "20011": EtnicValidationError,
    "20012": EtnicValidationError,
    "20013": EtnicValidationError,
    "20016": EtnicValidationError,
    "20019": EtnicValidationError,
    "20023": EtnicValidationError,
    "20024": EtnicValidationError,
    "20025": EtnicValidationError,
    "20026": EtnicValidationError,
    "20027": EtnicValidationError,
    "20028": EtnicValidationError,
    "20029": EtnicValidationError,
    "20030": EtnicValidationError,
    "20031": EtnicValidationError,
    "20034": EtnicValidationError,
    "20037": EtnicValidationError,
    "20038": EtnicValidationError,
    "20042": EtnicValidationError,  # BESAeSI switch (Organisation v8)
    # Document 2: an intervention type without the sub-type it imposes (J -> OA,
    # G -> AI; Périodes manual rev 1.4)
    "20041": EtnicValidationError,
    # Input validation - Document 3: periods above the ceilings (1538, 1574-1576),
    # unknown staff number, availability code or status (20108-20110)
    "1538": EtnicValidationError,
    "1574": EtnicValidationError,
    "1575": EtnicValidationError,
    "1576": EtnicValidationError,
    "20108": EtnicValidationError,
    "20109": EtnicValidationError,
    "20110": EtnicValidationError,
    # Input validation — Documents 1 & 2
    "1113": EtnicValidationError,
    "1114": EtnicValidationError,
    "2106": EtnicValidationError,
    "2118": EtnicValidationError,
}

# (low, high, class) — inclusive ranges, matched on int(code) when the code is
# not in _CODE_TO_CLASS. The same code number can mean different things per
# service, but every code in these ranges maps to the same class, so no service
# disambiguation is needed. Source: specs/00_REGISTRE.md §4.
_CODE_RANGES: list[Tuple[int, int, Type[EtnicBusinessError]]] = [
    (4004, 4012, EtnicValidationError),   # population consistency (Doc 1)
    (1527, 1528, EtnicValidationError),   # invalid grouping (Doc 2)
    (1598, 1604, EtnicValidationError),   # external-intervention type/subtype (Doc 2)
    (20015, 20036, EtnicValidationError),  # external-intervention errors (Doc 2)
    (30016, 30017, EtnicValidationError),  # business constraints (Doc 2)
]


# Codes whose meaning, and so class, depends on the service, keyed by the
# ``Config.SERVICES`` name. They win over _CODE_TO_CLASS for that service only.
# Source: the error tables of specs 03 to 06.
_SERVICE_CODE_TO_CLASS: dict[str, dict[str, Type[EtnicBusinessError]]] = {
    # Document 2: "Vous ne pouvez pas créer une 5ième intervention extérieure".
    "DOCUMENT2": {"1545": EtnicValidationError},
}


def map_etnic_error_code_to_class(
    code: Optional[str], service: Optional[str] = None
) -> Type[EtnicBusinessError]:
    """Map a known ETNIC error code to its specialized exception class.

    Some codes mean different things in different services (``1545`` is
    "already approved" for Documents 1 and 1D, "fifth external intervention"
    for Document 2): pass the ``Config.SERVICES`` name of the service that
    answered as ``service`` to get the class that matches its meaning.

    Returns :class:`EtnicBusinessError` for unknown or not-client-fixable codes.
    """
    if code is None:
        return EtnicBusinessError
    if service is not None and code in _SERVICE_CODE_TO_CLASS.get(service, {}):
        return _SERVICE_CODE_TO_CLASS[service][code]
    if code in _CODE_TO_CLASS:
        return _CODE_TO_CLASS[code]
    try:
        n = int(code)
    except (TypeError, ValueError):
        return EtnicBusinessError
    for low, high, cls in _CODE_RANGES:
        if low <= n <= high:
            return cls
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

    # Common_v2 services (Organisation v8) also carry requestId as an XML
    # attribute of the response root, which lands as a top-level key of
    # ``body`` after zeep serialization. Organisation v8 echoes it in the SOAP
    # header too, with the same value (TQ, 2026-11-24): the header wins and the
    # attribute is the fallback.
    if request_id is None:
        rid = body.get("requestId")
        if rid is not None:
            request_id = str(rid)

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
    service: Optional[str] = None,
) -> None:
    """Raise a typed business error, or return ``None`` in permissive mode.

    Service methods call this when they detect a server-side failure
    (``success=False``, empty ``response``, etc.).

    - By default (``Config.RAISE_ON_ERROR`` true since 0.3.0), it raises a
      subclass of :class:`EtnicBusinessError` chosen by
      :func:`map_etnic_error_code_to_class` (unless ``error_class`` is given
      explicitly).
    - In the deprecated permissive mode (:func:`permissive_errors`), it
      returns ``None``, the pre-0.3.0 contract.

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
        service: ``Config.SERVICES`` name of the service that answered, for
            the codes whose meaning depends on the service.

    Returns:
        ``None``, in permissive mode only; otherwise this raises.
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

    cls = error_class or map_etnic_error_code_to_class(code, service)
    if message is None:
        if code is not None:
            # Surface the real ETNIC code + description instead of a generic
            # placeholder, so str(exc) is actionable for callers.
            message = f"ETNIC error {code}: {description}"
        else:
            message = "ETNIC business error (empty response or success=False)"

    raise cls(message, code=code, description=description, request_id=request_id)
