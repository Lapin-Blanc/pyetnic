"""Document 1D against TQ, read only.

Its writes cannot be undone (the school's approval freezes the population), so
they are not automated: the life cycle was tested by hand on 2026-11-24 (spec 06).
"""

from __future__ import annotations

import pytest

from pyetnic.config import Config
from pyetnic.eprom import (
    EtnicDocumentNotAccessibleError,
    FormationDocument1D,
    lire_document_1d,
    lister_formations,
    strict_errors,
)


def test_lire_document1d_reel():
    if not Config.ETAB_ID:
        pytest.skip("Config DEFAULT_ETABID non définie dans .env")

    with strict_errors():
        formations = lister_formations(annee_scolaire=Config.ANNEE_SCOLAIRE, etab_id=Config.ETAB_ID)
        organisations = [o for f in formations.formations for o in f.organisations]
        if not organisations:
            pytest.skip("Aucune organisation pour cette année")
        for apercu in organisations:
            try:
                doc = lire_document_1d(apercu.id)
            except EtnicDocumentNotAccessibleError:
                continue  # 20101: the Doc A of this organisation is not approved yet
            break
        else:
            pytest.skip("Aucun document 1D accessible (Doc A non approuvé partout)")

    assert isinstance(doc, FormationDocument1D)
    assert doc.id == apercu.id
    for line in doc.droitInscriptionListe.droitInscription:
        assert isinstance(line.coAnnEtude, str)
        assert isinstance(line.nbEleves5ieme, int)
        assert isinstance(line.swAppPopD1D, bool) and isinstance(line.swAppD1D, bool)
