from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date

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

@dataclass
class FormationDocument1:
    """Représente un document 1 (populations de formation)."""
    id: OrganisationId
    populationListe: Optional[Doc1PopulationList] = None

# ---------------------------------------------------------------------------
# Modèles Document 2
# ---------------------------------------------------------------------------

@dataclass
class Doc2ActiviteEnseignementLine:
    """Ligne d'activité d'enseignement pour le document 2."""
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
    coEtuReg: str
    coAdmReg: int = 0
    coOrgReg: int = 0
    coBraReg: int = 0

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
    nbPeriodesDoc8: Optional[float] = None
    nbPeriodesPrevuesDoc2: Optional[float] = None
    nbPeriodesReellesDoc2: Optional[float] = None
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
    date: Optional[date] = None

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
