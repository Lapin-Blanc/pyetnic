"""SEPS Notifications service (issue #23).

Answers follow the manual "Notifications 2.3" and what production answered on
2026-11-24 (codes 04, 05, 06 and 08, the last without description).
Identifiers are fictitious.
"""

from __future__ import annotations

import datetime as dt

import pytest

import pyetnic.seps
from pyetnic.nomenclatures import CodeNotification
from pyetnic.services.models import SepsNotification
from pyetnic.services.notifications import NotificationsService
from pyetnic.services.seps_errors import SepsValidationError


def answer(*, notifications=None, error=(), warning=(), success=True):
    body = {
        "success": success,
        "messages": {"error": list(error), "warning": list(warning), "info": [{"code": "200"}, {"code": "2.4.6"}]},
    }
    if notifications is not None:
        body["response"] = {"notification": notifications}
    return {"body": body}


@pytest.fixture
def service(monkeypatch):
    svc = NotificationsService()
    calls = []

    def fake(method, **kwargs):
        calls.append((method, kwargs))
        return svc.next_answer

    monkeypatch.setattr(svc.client_manager, "call_service", fake)
    svc.calls = calls
    return svc


def test_notifications_are_parsed(service):
    service.next_answer = answer(notifications=[
        {"id": 25, "cfNum": "1234567-89", "date": dt.date(2026, 10, 2), "code": "05", "description": "MODIF ETUDIANT:CHANGEMENT ADRESSE"},
        {"id": 33, "cfNum": "1234567-89", "date": dt.date(2026, 11, 19), "code": "08"},
    ])
    notes = service.lire_notifications(1234, "2026-10-01")
    assert notes == [
        SepsNotification(25, "1234567-89", "2026-10-02", "05", "MODIF ETUDIANT:CHANGEMENT ADRESSE"),
        SepsNotification(33, "1234567-89", "2026-11-19", "08", None),
    ]
    assert notes[1].code == CodeNotification.STATUT


def test_single_notification_and_request_shape(service):
    service.next_answer = answer(notifications={"id": 1, "cfNum": "1234567-89", "date": "2026-10-02", "code": "04"})
    notes = service.lire_notifications(1234, dt.date(2026, 10, 1))
    assert len(notes) == 1
    assert service.calls == [("lireNotifications", {"etabId": "1234", "dateDebut": "2026-10-01"})]


def test_none_found_is_empty(service):
    service.next_answer = answer(
        success=False,
        warning=[{"code": "30105", "description": "No notification found for etabId : 1234 and dateFrom : 2026-10-01"}],
    )
    assert service.lire_notifications(1234, "2026-10-01") == []


def test_invalid_date_raises(service):
    service.next_answer = answer(success=False, error=[{"code": "30050", "description": "Validation dateFrom"}])
    with pytest.raises(SepsValidationError):
        service.lire_notifications(1234, "2026-13-01")


def test_public_namespace():
    assert pyetnic.seps.lire_notifications.__name__ == "lire_notifications"
    assert {c.value for c in CodeNotification} == {"02", "04", "05", "06", "07", "08"}
