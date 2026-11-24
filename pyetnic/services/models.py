from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date

# Alias for the fields named `date`: inside their class body the name is bound to the
# field's default before the annotation is evaluated.
_Date = date

# ---------------------------------------------------------------------------
# Types communs
# ---------------------------------------------------------------------------

@dataclass
class StatutDocument:
    statut: str
    dateStatut: date

@dataclass
class OrganisationId:
    anneeScolaire: str
    etabId: int
    numAdmFormation: int
    numOrganisation: int
    implId: Optional[int] = None

@dataclass
class OrganisationApercu:
    """Vue légère d'une organisation, disponible depuis lister_formations() (OrganisationApercuCT)."""
    id: OrganisationId
    dateDebutOrganisation: date
    dateFinOrganisation: date
    statutDocumentOrganisation: Optional[StatutDocument] = None
    statutDocumentPopulationPeriodes: Optional[StatutDocument] = None
    statutDocumentDroitsInscription: Optional[StatutDocument] = None
    statutDocumentAttributions: Optional[StatutDocument] = None

@dataclass
class Organisation(OrganisationApercu):
    """Vue complète d'une organisation, disponible depuis lire_organisation() (FormationOrganisationCT)."""
    nombreSemaineFormation: Optional[int] = None
    organisationPeriodesSupplOuEPT: Optional[bool] = None
    valorisationAcquis: Optional[bool] = None
    enPrison: Optional[bool] = None
    eLearning: Optional[bool] = None
    reorientation7TP: Optional[bool] = None
    activiteFormation: Optional[bool] = None
    conseillerPrevention: Optional[bool] = None
    partiellementDistance: Optional[bool] = None
    enseignementHybride: Optional[bool] = None
    numOrganisation2AnneesScolaires: Optional[int] = None
    typeInterventionExterieure: Optional[str] = None
    interventionExterieure50p: Optional[bool] = None
    # Organisation v8: unit given only for the BES "assistant en soins infirmiers"
    # (from school year 2026-2027). Last, so that positional construction keeps working.
    BESAeSI: Optional[bool] = None

@dataclass
class Formation:
    numAdmFormation: int
    libelleFormation: str
    codeFormation: str
    organisations: List[OrganisationApercu] = field(default_factory=list)

@dataclass
class FormationsListeResult:
    success: bool
    formations: List[Formation]
    messages: List[str] = field(default_factory=list)

    def __bool__(self):
        return self.success

    def __iter__(self):
        return iter(self.formations)

    def __len__(self):
        return len(self.formations)

# ---------------------------------------------------------------------------
# Modèles Document 1
# ---------------------------------------------------------------------------

@dataclass
class Doc1PopulationLine:
    """Ligne de population par année d'étude (PopDocument1AnneeEtudeLineCT)."""
    coAnnEtude: int
    nbEleveA: int
    nbEleveEhr: int
    nbEleveFse: int
    nbElevePi: int
    nbEleveB: int
    nbEleveTot2a5: int
    nbEleveDem: int
    nbEleveMin: int
    nbEleveExm: int
    nbElevePl: int
    nbEleveTot6et8: int
    nbEleveTotFse: int
    nbEleveTotPi: int
    nbEleveTotHom: int
    nbEleveTotFem: int
    swAppPopD1: bool
    swAppD1: bool
    tsMaj: Optional[str] = None
    teUserMaj: Optional[str] = None

@dataclass
class Doc1PopulationList:
    """Liste de populations par année d'étude (PopDocument1AnneeEtudeLstCT)."""
    population: List[Doc1PopulationLine] = field(default_factory=list)

@dataclass
class Doc1PopulationLineSave:
    """Ligne de population à sauvegarder (PopDocument1AnneeEtudeLineSaveCT)."""
    coAnnEtude: int
    nbEleveA: Optional[int] = None
    nbEleveEhr: Optional[int] = None
    nbEleveB: Optional[int] = None
    nbEleveDem: Optional[int] = None
    nbEleveMin: Optional[int] = None
    nbEleveExm: Optional[int] = None
    nbElevePl: Optional[int] = None
    nbEleveTotHom: Optional[int] = None
    nbEleveTotFem: Optional[int] = None

@dataclass
class Doc1PopulationListSave:
    """Liste de populations à sauvegarder (PopDocument1AnneeEtudeLstSaveCT)."""
    population: List[Doc1PopulationLineSave] = field(default_factory=list)

    @classmethod
    def from_document(cls, document: "FormationDocument1") -> "Doc1PopulationListSave":
        """The population of a Doc 1 just read, as :func:`approuver_document_1` must send it back."""
        lines = document.populationListe.population if document.populationListe else []
        return cls([
            Doc1PopulationLineSave(
                coAnnEtude=p.coAnnEtude, nbEleveA=p.nbEleveA, nbEleveEhr=p.nbEleveEhr,
                nbEleveB=p.nbEleveB, nbEleveDem=p.nbEleveDem, nbEleveMin=p.nbEleveMin,
                nbEleveExm=p.nbEleveExm, nbElevePl=p.nbElevePl,
                nbEleveTotHom=p.nbEleveTotHom, nbEleveTotFem=p.nbEleveTotFem,
            )
            for p in lines
        ])

@dataclass
class FormationDocument1:
    """Représente un document 1 (populations de formation)."""
    id: OrganisationId
    populationListe: Optional[Doc1PopulationList] = None

# ---------------------------------------------------------------------------
# Modèles Document 1D (droits d'inscription)
# ---------------------------------------------------------------------------

@dataclass
class Doc1DDroitInscriptionLine:
    """Ligne par année d'études du document 1D (Doc1DDroitInscriptionLineCT).

    ``nbEleves5ieme`` is the population counted at 5/10 of the unit,
    ``mtDroitsInscription`` the enrolment fee. ``swAppPopD1D`` is the school's
    approval of the population, ``swAppD1D`` the administration's.
    ``mtDroitsInscriptionOccupationnel`` is no longer used (manual §3.1.3.4).
    """
    coAnnEtude: str
    nbEleves5ieme: int
    mtDroitsInscription: float
    mtDroitsInscriptionOccupationnel: float
    swAppPopD1D: bool
    swAppD1D: bool
    tsMaj: Optional[str] = None
    teUserMaj: Optional[str] = None

@dataclass
class Doc1DDroitInscriptionList:
    """Lignes du document 1D (Doc1DDroitInscriptionLstCT)."""
    droitInscription: List[Doc1DDroitInscriptionLine] = field(default_factory=list)

@dataclass
class Doc1DDroitInscriptionLineSave:
    """Ligne à modifier (Doc1DDroitInscriptionSaveLineCT).

    ``nbEleves5ieme`` is writable until the population is approved,
    ``mtDroitsInscription`` only after (error 20112 before, 1546 in the manual).
    """
    coAnnEtude: str
    nbEleves5ieme: Optional[int] = None
    mtDroitsInscription: Optional[float] = None

@dataclass
class Doc1DDroitInscriptionListSave:
    """Lignes à modifier (Doc1DDroitInscriptionSaveLstCT)."""
    droitInscription: List[Doc1DDroitInscriptionLineSave] = field(default_factory=list)

@dataclass
class Doc1DDroitInscriptionLineAppr:
    """Ligne à approuver (Doc1DDroitInscriptionApprLineCT): the population as read."""
    coAnnEtude: str
    nbEleves5ieme: int

@dataclass
class Doc1DDroitInscriptionListAppr:
    """Lignes à approuver (Doc1DDroitInscriptionApprLstCT)."""
    droitInscription: List[Doc1DDroitInscriptionLineAppr] = field(default_factory=list)

    @classmethod
    def from_document(cls, document: "FormationDocument1D") -> "Doc1DDroitInscriptionListAppr":
        """The lines of a document just read, as the approval must send them back."""
        lines = document.droitInscriptionListe.droitInscription if document.droitInscriptionListe else []
        return cls([Doc1DDroitInscriptionLineAppr(line.coAnnEtude, line.nbEleves5ieme) for line in lines])

@dataclass
class FormationDocument1D:
    """Document 1D: population at 5/10 and enrolment fees (FormationDocument1DCT)."""
    id: OrganisationId
    droitInscriptionListe: Optional[Doc1DDroitInscriptionList] = None

# ---------------------------------------------------------------------------
# Modèles Document 2
# ---------------------------------------------------------------------------

@dataclass
class Doc2ActiviteEnseignementLine:
    """Ligne d'activité d'enseignement pour le document 2.

    Ordre et types alignés sur le XSD ``Doc2ActiviteEnseignementLineCT`` (cf.
    ``specs/04_formation_periodes_v1.md``) : les 14 champs sont obligatoires en
    réponse, ``coEtuReg`` (année d'études Rgp, string) vient en dernier après
    les trois numéros de regroupement ``coAdmReg``/``coOrgReg``/``coBraReg`` (int).
    """
    coNumBranche: int
    coCategorie: str
    teNomBranche: str
    coAnnEtude: str
    nbEleveC1: int
    nbPeriodeBranche: float
    nbPeriodePrevueAn1: float
    nbPeriodePrevueAn2: float
    nbPeriodeReelleAn1: float
    nbPeriodeReelleAn2: float
    coAdmReg: int
    coOrgReg: int
    coBraReg: int
    coEtuReg: str

@dataclass
class Doc2ActiviteEnseignementList:
    """Liste d'activités d'enseignement pour le document 2."""
    activiteEnseignement: List[Doc2ActiviteEnseignementLine] = field(default_factory=list)

@dataclass
class Doc2ActiviteEnseignementDetail:
    """Détail des activités d'enseignement pour le document 2."""
    activiteEnseignementListe: Optional[Doc2ActiviteEnseignementList] = None
    nbTotPeriodePrevueAn1: float = 0.0
    nbTotPeriodePrevueAn2: float = 0.0
    nbTotPeriodeReelleAn1: float = 0.0
    nbTotPeriodeReelleAn2: float = 0.0

@dataclass
class Doc2PeriodeExtLine:
    """Période pour intervention extérieure."""
    coCodePar: str
    teLibPeriode: str
    nbPerAn1: float
    nbPerAn2: float

@dataclass
class Doc2PeriodeExtList:
    """Liste de périodes pour intervention extérieure."""
    periode: List[Doc2PeriodeExtLine] = field(default_factory=list)

@dataclass
class Doc2InterventionExtLine:
    """Ligne d'intervention extérieure pour le document 2."""
    coNumIex: int
    coCatCol: str
    teTypeInterventionExt: str
    coObjFse: str
    teSousTypeInterventionExt: str
    coRefPro: str
    coCriCee: str
    periodeListe: Optional[Doc2PeriodeExtList] = None

@dataclass
class Doc2InterventionExtList:
    """Liste d'interventions extérieures pour le document 2."""
    interventionExterieure: List[Doc2InterventionExtLine] = field(default_factory=list)

@dataclass
class Doc2ActiviteEnseignementLineSave:
    """Activité d'enseignement à sauvegarder (Doc2ActiviteEnseignementLineSaveCT)."""
    coNumBranche: int
    nbEleveC1: Optional[int] = None
    nbPeriodePrevueAn1: Optional[float] = None
    nbPeriodePrevueAn2: Optional[float] = None
    nbPeriodeReelleAn1: Optional[float] = None
    nbPeriodeReelleAn2: Optional[float] = None
    coAdmReg: Optional[int] = None
    coOrgReg: Optional[int] = None
    coBraReg: Optional[int] = None
    coEtuReg: Optional[str] = None

@dataclass
class Doc2ActiviteEnseignementListSave:
    """Liste d'activités d'enseignement à sauvegarder."""
    activiteEnseignement: List[Doc2ActiviteEnseignementLineSave] = field(default_factory=list)

@dataclass
class Doc2PeriodeExtLineSave:
    """Période d'intervention extérieure à sauvegarder (Doc2PeriodeExtLineSaveCT)."""
    coCodePar: str
    nbPerAn1: Optional[float] = None
    nbPerAn2: Optional[float] = None

@dataclass
class Doc2PeriodeExtListSave:
    """Liste de périodes d'intervention extérieure à sauvegarder."""
    periode: List[Doc2PeriodeExtLineSave] = field(default_factory=list)

@dataclass
class Doc2InterventionExtLineSave:
    """Intervention extérieure à sauvegarder (Doc2InterventionExtLineSaveCT)."""
    coCatCol: str
    coNumIex: Optional[int] = None
    coObjFse: Optional[str] = None
    coRefPro: Optional[str] = None
    coCriCee: Optional[str] = None
    periodeListe: Optional[Doc2PeriodeExtListSave] = None

@dataclass
class Doc2InterventionExtListSave:
    """Liste d'interventions extérieures à sauvegarder."""
    interventionExterieure: List[Doc2InterventionExtLineSave] = field(default_factory=list)

@dataclass
class FormationDocument2:
    """Représente un document 2 (périodes de formation)."""
    id: OrganisationId
    activiteEnseignementDetail: Optional[Doc2ActiviteEnseignementDetail] = None
    interventionExterieureListe: Optional[Doc2InterventionExtList] = None
    swAppD2: bool = False
    tsMaj: Optional[str] = None
    teUserMaj: Optional[str] = None

# ---------------------------------------------------------------------------
# Modèles Document 3
# ---------------------------------------------------------------------------

@dataclass
class Doc3EnseignantDetail:
    """Attribution d'enseignant pour le document 3 (Doc3EnseignantDetailCT)."""
    coNumAttribution: Optional[int] = None
    noMatEns: Optional[str] = None
    teNomEns: Optional[str] = None
    tePrenomEns: Optional[str] = None
    teAbrEns: Optional[str] = None
    teEnseignant: Optional[str] = None
    coDispo: Optional[str] = None
    teStatut: Optional[str] = None
    nbPeriodesAttribuees: Optional[float] = None
    tsMaj: Optional[str] = None
    teUserMaj: Optional[str] = None

@dataclass
class Doc3EnseignantList:
    """Liste des attributions d'enseignants pour le document 3 (Doc3EnseignantLstCT)."""
    enseignant: List[Doc3EnseignantDetail] = field(default_factory=list)

@dataclass
class Doc3ActiviteDetail:
    """Détail d'une activité d'enseignement pour le document 3 (Doc3ActiviteDetailCT)."""
    coNumBranche: Optional[int] = None
    coCategorie: Optional[str] = None
    teNomBranche: Optional[str] = None
    noAnneeEtude: Optional[str] = None
    # xs:int in FormationDocument3_v1.xsd (audit D7): zeep returns integers.
    nbPeriodesDoc8: Optional[int] = None
    nbPeriodesPrevuesDoc2: Optional[int] = None
    nbPeriodesReellesDoc2: Optional[int] = None
    enseignantListe: Optional[Doc3EnseignantList] = None

@dataclass
class Doc3ActiviteListe:
    """Liste des activités d'enseignement pour le document 3 (Doc3ActiviteListeCT)."""
    activite: List[Doc3ActiviteDetail] = field(default_factory=list)

@dataclass
class Doc3EnseignantDetailSave:
    """Attribution d'enseignant à sauvegarder (Doc3EnseignantDetailSaveCT)."""
    coNumAttribution: Optional[int] = None
    noMatEns: Optional[str] = None
    coDispo: Optional[str] = None
    teStatut: Optional[str] = None
    nbPeriodesAttribuees: Optional[float] = None

@dataclass
class Doc3EnseignantListSave:
    """Liste des attributions d'enseignants à sauvegarder (Doc3EnseignantLstSaveCT)."""
    enseignant: List[Doc3EnseignantDetailSave] = field(default_factory=list)

@dataclass
class Doc3ActiviteDetailSave:
    """Détail d'une activité à sauvegarder (Doc3ActiviteDetailSaveCT).

    Les trois champs sont requis par le XSD (pas de minOccurs="0").
    """
    coNumBranche: int
    noAnneeEtude: str
    enseignantListe: Doc3EnseignantListSave

@dataclass
class Doc3ActiviteListeSave:
    """Liste des activités à sauvegarder (Doc3ActiviteListeSaveCT)."""
    activite: List[Doc3ActiviteDetailSave] = field(default_factory=list)

@dataclass
class FormationDocument3:
    """Représente un document 3 (attributions d'enseignants)."""
    id: OrganisationId
    activiteListe: Optional[Doc3ActiviteListe] = None

# ---------------------------------------------------------------------------
# Modèles SEPS — RechercheEtudiants v1
# ---------------------------------------------------------------------------

@dataclass
class SepsLocalite:
    """Localité (LocaliteType)."""
    code: Optional[str] = None
    description: Optional[str] = None

@dataclass
class SepsAdresse:
    """Adresse postale (AdresseType)."""
    rue: Optional[str] = None
    codePostal: Optional[str] = None
    codePays: Optional[str] = None
    numero: Optional[str] = None
    boite: Optional[str] = None
    extension: Optional[str] = None
    localite: Optional[SepsLocalite] = None
    localiteExtension: Optional[str] = None

@dataclass
class SepsNaissance:
    """Données de naissance (NaissanceType)."""
    date: Optional[str] = None
    codePays: Optional[str] = None
    localite: Optional[SepsLocalite] = None

@dataclass
class SepsDeces:
    """Données de décès (DecesType)."""
    date: Optional[_Date] = None

@dataclass
class EtudiantDetails:
    """Détails d'un étudiant depuis le registre national ou CFWB (EtudiantDetailsType)."""
    niss: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    autrePrenom: Optional[List[str]] = None
    sexe: Optional[str] = None
    naissance: Optional[SepsNaissance] = None
    deces: Optional[SepsDeces] = None
    adresse: Optional[SepsAdresse] = None
    codeNationalite: Optional[str] = None

@dataclass
class Etudiant:
    """Étudiant SEPS avec ses données RN et/ou CFWB (EtudiantType)."""
    cfNum: Optional[str] = None
    rnDetails: Optional[EtudiantDetails] = None
    cfwbDetails: Optional[EtudiantDetails] = None
    bisCreated: Optional[str] = None                      # "O" | "N" : NISS bis créé (enregistrerEtudiant)

# Types Save pour EnregistrerEtudiant / ModifierEtudiant

@dataclass
class SepsNaissanceSave:
    """Données de naissance à envoyer (NaissanceType — date et codePays requis)."""
    date: str                          # format YYYY ou YYYY-MM-DD
    codePays: str
    localite: Optional[SepsLocalite] = None

@dataclass
class SepsAdresseSave:
    """Adresse postale à envoyer (AdresseType — rue, codePostal, codePays requis)."""
    rue: str
    codePostal: str
    codePays: str
    numero: Optional[str] = None
    boite: Optional[str] = None
    extension: Optional[str] = None
    localite: Optional[SepsLocalite] = None
    localiteExtension: Optional[str] = None

@dataclass
class EtudiantDetailsSave:
    """Détails d'un étudiant à envoyer (EtudiantDetailsType — tous les champs optionnels)."""
    niss: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    autrePrenom: Optional[List[str]] = None
    sexe: Optional[str] = None
    naissance: Optional[SepsNaissanceSave] = None
    deces: Optional[SepsDeces] = None
    adresse: Optional[SepsAdresseSave] = None
    codeNationalite: Optional[str] = None

# ---------------------------------------------------------------------------
# Modèles Inscription (lecture)
# ---------------------------------------------------------------------------

@dataclass
class SepsDroitInscription:
    """Droit d'inscription (DroitInscriptionType)."""
    indicateurDroitInscription: str                        # "O" | "N"
    exempte: Optional["SepsExempteDroitInscription"] = None
    montant: Optional[str] = None                         # texte libre, si indicateur à "O"

@dataclass
class SepsExempteDroitInscription:
    """Exemption de droit d'inscription (ExempteDroitInscriptionType)."""
    indicateurExempteDroitInscription: str                 # "O" | "N"
    motifExemption: str                                    # C01-C07

@dataclass
class SepsDroitInscriptionSpecifique:
    """Droit d'inscription spécifique (DroitInscriptionSpecifiqueType)."""
    indicateurDroitInscriptionSpecifique: str              # "O" | "N"
    exempte: Optional["SepsExempteDroitInscriptionSpec"] = None
    montant: Optional[str] = None                         # texte libre, si indicateur à "O"

@dataclass
class SepsExempteDroitInscriptionSpec:
    """Exemption de droit d'inscription spécifique."""
    indicateurExempteDroitInscriptionSpec: str             # "O" | "N"
    motifExemptionSpec: str                                # C01-C13, C50

@dataclass
class SepsAdmission:
    """Données d'admission (AdmissionType)."""
    codeAdmission: str                                     # "REUSSITE"|"TITREBEL"|"TITREETR"|"AUTRE"|"AUCUN"
    typeEnseignement: Optional[str] = None
    titreDelivre: Optional[str] = None
    equivalence: Optional[str] = None                     # C01-C04
    valorisationAcquis: Optional[str] = None              # C01-C04, C10-C40, C50

@dataclass
class SepsSanction:
    """Sanction de formation (SanctionType).

    ``codeSectionFlag``, ``codeSection`` (11 caractères) et ``point`` ne sont
    pris en compte que pour une épreuve intégrée ; ``pourcentageAttribue``
    seulement si ``codeSanction`` vaut ``RE``.
    """
    codeSanction: Optional[str] = None                    # "RE"|"AB"|"EH" (facultatif dans le contrat en direct)
    valorisationAcquisSanction: Optional[str] = None      # C00-C05
    motifAbandon: Optional[str] = None                    # TPS|PRO|FAM|SAN|ATT|MEM|FMJ|NUM|AUT|INC
    statutFinFormation: Optional[str] = None              # C01-C06
    pourcentageAttribue: Optional[str] = None
    codeSectionFlag: Optional[bool] = None
    codeSection: Optional[str] = None
    point: Optional[str] = None
    ajournement1Session: Optional[str] = None             # "O" | "N"

@dataclass
class SepsSpecificite:
    """Spécificités d'inscription (SpecificiteDataType — lecture)."""
    regulier1: Optional[str] = None                       # "O" | "N"
    regulier5: Optional[str] = None                       # "O" | "N"
    droitInscription: Optional[SepsDroitInscription] = None
    droitInscriptionSpecifique: Optional[SepsDroitInscriptionSpecifique] = None
    dureeInoccupation: Optional[str] = None               # C00|C06|C12|C24
    situationMenage: Optional[str] = None                 # ISOL|SSEM|A1EM|X
    enfantACharge: Optional[str] = None                   # "O" | "N"
    difficulteHandicap: Optional[str] = None              # "O" | "N" | "X"
    difficulteAutre: Optional[str] = None                 # "O" | "N" | "X"
    admission: Optional[SepsAdmission] = None
    sanction: Optional[SepsSanction] = None
    regulier3: Optional[str] = None                       # "O" | "N", régulier au 3/10

@dataclass
class SepsUE:
    """Unité d'enseignement (UEType — lecture)."""
    noAdministratif: int
    noOrganisation: int
    label: Optional[str] = None
    code: Optional[str] = None
    codeNiveau: Optional[str] = None                      # "SI"|"SS"|"SC"|"SL"
    nombreSemaine: Optional[int] = None
    dateDebut: Optional[str] = None
    dateFin: Optional[str] = None
    fse: Optional[str] = None                             # "O" | "N"
    noOrganisationPrecedent: Optional[str] = None
    activiteDeFormation: Optional[str] = None             # "O" | "N"

@dataclass
class SepsLieuCours:
    """Lieu de cours (LieuCoursType)."""
    codePostal: Optional[str] = None
    ville: Optional[str] = None

@dataclass
class Inscription:
    """Inscription d'un étudiant à une UE (InscriptionType)."""
    cfNum: str
    anneeScolaire: Optional[int] = None
    idEtab: Optional[int] = None
    idImplantation: Optional[int] = None
    dateInscription: Optional[str] = None
    lieuCours: Optional[SepsLieuCours] = None
    statut: Optional[str] = None                          # "DE" | "AN"
    ue: Optional[SepsUE] = None
    specificite: Optional[SepsSpecificite] = None
    audit: Optional["SepsAudit"] = None


@dataclass
class SepsAudit:
    """Traçabilité d'une inscription tenue par le serveur SEPS (AuditType).

    Les dates viennent telles que le serveur les écrit (chaîne ISO, heure
    locale). Absent du contrat du catalogue, présent dans le contrat en direct.
    """
    dateCreation: Optional[str] = None
    utilisateurCreation: Optional[str] = None
    dateModification: Optional[str] = None
    utilisateurModification: Optional[str] = None

# ---------------------------------------------------------------------------
# Modèles Inscription (envoi)
# ---------------------------------------------------------------------------

@dataclass
class SepsUESave:
    """Unité d'enseignement à envoyer (UEInputType)."""
    noAdministratif: int
    noOrganisation: int

@dataclass
class SepsSpecificiteSave:
    """Spécificités d'inscription à envoyer (SpecificiteDataType).

    L'élément d'entrée ``inscription/specificite`` est typé ``SpecificiteDataType``,
    qui porte ``regulier1`` / ``regulier5`` (IndicateurType, "O"/"N"). Le contrat
    du catalogue déclarait aussi un ``SpecificiteDataInputType`` sans eux, jamais
    référencé ; le contrat en direct ne l'a plus.

    ``regulier3`` (régulier au 3/10) n'est accepté que par ``enregistrerInscription``
    en production : le service de recherche et l'environnement TQ ne le
    connaissent pas encore (observé le 2026-11-24).
    """
    regulier1: Optional[str] = None                       # "O" | "N"
    regulier5: Optional[str] = None                       # "O" | "N"
    droitInscription: Optional[SepsDroitInscription] = None
    droitInscriptionSpecifique: Optional[SepsDroitInscriptionSpecifique] = None
    dureeInoccupation: Optional[str] = None               # C00|C06|C12|C24
    situationMenage: Optional[str] = None                 # ISOL|SSEM|A1EM|X
    enfantACharge: Optional[str] = None                   # "O" | "N"
    difficulteHandicap: Optional[str] = None              # "O" | "N" | "X"
    difficulteAutre: Optional[str] = None                 # "O" | "N" | "X"
    admission: Optional[SepsAdmission] = None
    sanction: Optional[SepsSanction] = None
    regulier3: Optional[str] = None                       # "O" | "N", enregistrerInscription seulement

@dataclass
class InscriptionInputSave:
    """Données d'inscription à envoyer (InscriptionInputType)."""
    dateInscription: str                                   # requis
    statut: str                                            # requis: "DE" | "AN"
    anneeScolaire: Optional[int] = None
    ue: Optional[SepsUESave] = None
    specificite: Optional[SepsSpecificiteSave] = None
    # Champs FSE exigés si l'UE est FSE et l'inscription régulière au 1/10
    # (défaut serveur : True). False les rend facultatifs.
    fse: Optional[bool] = None

@dataclass
class InscriptionInputDataSave:
    """Données complètes d'inscription à envoyer (InscriptionInputDataType)."""
    cfNum: str                                             # requis
    idEtab: int                                            # requis
    idImplantation: int                                    # requis
    codePostalLieuCours: str                               # requis
    inscription: InscriptionInputSave                      # requis

# ---------------------------------------------------------------------------
# Résultats des écritures SEPS
# ---------------------------------------------------------------------------

# Codes of a successful write: 201 creation, 200 modification (or, for a student
# registered by NISS, merge with an existing establishment record).
_SEPS_SUCCESS_CODES = ("201", "200")


@dataclass
class SepsMessage:
    """Un message du bloc retour SEPS (error, warning ou info).

    Le message de version du service (``2.4.6``, « version ») n'est jamais repris.
    """
    niveau: str                                            # "error" | "warning" | "info"
    code: Optional[str] = None
    description: Optional[str] = None


@dataclass
class SepsEcritureResult:
    """Ce que le serveur répond à une écriture SEPS acceptée.

    Un refus lève une ``SepsEtnicError`` : un résultat est toujours un succès.

    Attributes:
        code: Le code principal : ``201`` (création), ``200`` (modification ou,
            pour un étudiant enregistré par NISS, fusion avec une fiche
            existante), sinon le premier code non bloquant reçu, ou ``None``.
        messages: Tous les messages reçus, version du service exclue.
    """
    code: Optional[str]
    messages: List[SepsMessage] = field(default_factory=list)

    @property
    def avertissements(self) -> List[SepsMessage]:
        """Les messages autres que le code de succès (201 / 200)."""
        return [m for m in self.messages if m.code not in _SEPS_SUCCESS_CODES]

    def a_le_code(self, code: str) -> bool:
        """Vrai si le serveur a renvoyé ce code, quel que soit son niveau."""
        return any(m.code == code for m in self.messages)


@dataclass
class EnregistrerEtudiantResult(SepsEcritureResult):
    """Résultat de ``enregistrer_etudiant``.

    Attributes:
        etudiant: L'étudiant tel que le serveur le renvoie.
        bis_cree: ``True`` si le serveur a créé un NISS bis (``bisCreated`` à
            ``O``), ``False`` s'il dit que non, ``None`` s'il ne dit rien.
    """
    etudiant: Optional[Etudiant] = None
    bis_cree: Optional[bool] = None

    @property
    def cree(self) -> bool:
        """Nouvel étudiant, nouveau numéro CF (code 201)."""
        return self.code == "201"

    @property
    def fusionne(self) -> bool:
        """Rattaché à une fiche établissement existante, qui garde son CF (code 200).

        Le manuel « Enregistrer Etudiants 2.3 » décrit cette fusion en mode NISS
        quand un seul doublon (nom, prénom, sexe, date de naissance) existe.
        """
        return self.code == "200"


@dataclass
class ModifierEtudiantResult(SepsEcritureResult):
    """Résultat de ``modifier_etudiant``."""
    etudiant: Optional[Etudiant] = None


@dataclass
class InscriptionResult(SepsEcritureResult):
    """Résultat de ``enregistrer_inscription`` et ``modifier_inscription``."""
    inscription: Optional[Inscription] = None

    @property
    def plus_de_4_ue(self) -> bool:
        """Créée, mais l'étudiant est inscrit dans plus de 4 UE (code 30051)."""
        return self.a_le_code("30051")


# ---------------------------------------------------------------------------
# Notifications SEPS
# ---------------------------------------------------------------------------

@dataclass
class SepsNotification:
    """Changement de signalétique d'un étudiant (NotificationType).

    ``code`` : 02 sexe, 04 nom / prénom, 05 adresse, 06 nationalité, 07 NISS,
    08 statut (voir :class:`~pyetnic.nomenclatures.CodeNotification`). Le code 08
    arrive sans ``description`` : le contrat n'en prévoit pas pour lui (observé en
    production le 2026-11-24).
    """
    id: Optional[int] = None
    cfNum: Optional[str] = None
    date: Optional[str] = None                            # AAAA-MM-JJ
    code: Optional[str] = None
    description: Optional[str] = None
