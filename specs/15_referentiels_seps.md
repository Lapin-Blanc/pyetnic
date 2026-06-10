# Référentiels SEPS — Codes pays, nationalités & communes (INS)

> Documentation + extraction exploitable des référentiels alimentant les champs « code » de la signalétique SEPS.
> Sources : `Codes_Pays.xls` (260 pays) + `INS_communesNais200723.xlsx` (communes/districts INS) + manuel SEPS §3.1.2/§3.1.8.2.
> Date d'analyse : 2026-06-09 (session 7)

---

## Pourquoi ce référentiel

Dans les XSD SEPS, les champs `codePays`, `codeNationalite` et `localite.code` sont déclarés en **`xs:string` libre** (aucune énumération). Leur **sémantique** (codes **INS/ONSS**) n'est donnée que par le manuel et par ces deux fichiers de référence du catalogue SOA. Pour pyetnic, il faut donc un référentiel **embarqué** permettant de **valider** et **résoudre** ces codes.

Champs concernés (specs 09-12) :

| Champ XSD | Type déclaré | Référentiel | Format réel |
|---|---|---|---|
| `naissance.codePays` | string | **pays** (`CO_ONSS_ID`) | INS pays, **5 chiffres** zero-paddés (ex. `00150`) |
| `adresse.codePays` | string | **pays** (`CO_ONSS_ID`) | idem |
| `codeNationalite` | string | **pays** (`CO_NATIO_ID`) | INS nationalité, **5 chiffres** (ex. `00150`) |
| `naissance.localite.code` | string | **communes** (`code INS`) | INS commune, **5 chiffres** (ex. `25072`) ; obligatoire si **belge** |
| `adresse.localite.code` | string | **communes** | idem |

> Règle manuel : la **localité** porte un `code` INS **uniquement si la commune/district est belge** ; sinon seul `description` (libellé ville) est renseigné. Le **`codePays`** est un code INS **pays** (≠ code commune).

---

## Référentiel PAYS / NATIONALITÉS

**Source** : `Codes_Pays.xls`, feuille `pays` — **260 entrées**. Colonnes d'origine : `CO_ONSS_ID`, `CO_ISO`, `CO_ISO_3`, `TE_NOM_PAYS` (maj.), `TE_NOM_PAYS_MIN`, `TE_NOM_PAYS_LONG`, `CO_NATIO_ID`, `DT_DATE_DEBUT`, `DT_DATE_FIN`.

### Règle de codage
- **`codePays`** (naissance, adresse) = **`CO_ONSS_ID`** zero-paddé à 5 chiffres. Ex. Belgique `150` → **`00150`**, France `111` → `00111`, Congo (RDC) `306` → `00306`.
- **`codeNationalite`** = **`CO_NATIO_ID`** zero-paddé à 5 chiffres.
- `CO_ONSS_ID` ∈ [101 ; 999]. **Codes spéciaux** : `900` Apatride, `901` Pas encore définitivement établi, `999` Indéterminé.
- ⚠️ **`CO_NATIO_ID` ≠ `CO_ONSS_ID` pour 43 entrées** : certains territoires renvoient à la nationalité du pays « parent ». Ex. Gibraltar (180) → natio 112 (Royaume-Uni) ; Macao/Hong Kong (231/234) → 218 (Chine) ; Mayotte/Réunion (350/387) → 111 (France). **⇒ ne pas déduire la nationalité du code pays : utiliser la colonne `code_nationalite`.**
- ⚠️ **Namibie** : ISO2 = `NA` (préservé à l'extraction ; piège classique « NA → valeur manquante »).

### Extraction produite
- **`referentiels/codes_pays.csv`** — colonnes : `code_pays` (5 ch.), `co_onss_id`, `iso2`, `iso3`, `nom_pays`, `nom_pays_long`, `code_nationalite` (5 ch.), `co_natio_id`, `date_debut`, `date_fin`.
- **`referentiels/codes_pays.json`** — même contenu (tableau d'objets).

Extrait :

| code_pays | iso2 | nom_pays | code_nationalite |
|---|---|---|---|
| 00111 | FR | France | 00111 |
| 00150 | BE | Belgique | 00150 |
| 00306 | CD | Congo (Rép.Dém.) | 00306 |
| 00900 | *(vide)* | Apatride | 00900 |
| 00999 | *(vide)* | Indéterminé | 00999 |

---

## Référentiel COMMUNES / DISTRICTS (INS)

**Source** : `INS_communesNais200723.xlsx`, feuille `Feuil1` — **3 277 lignes**, **2 789 codes INS uniques**. Colonnes : `code INS`, `Date de début`, `Date de fin`, `Nom officiel (RN)`, `Nom unique (ETNIC)`.

### Caractéristiques
- **`code INS`** : toujours **5 chiffres** (plage 11001-93090). C'est ce qui alimente `localite.code`.
- **Historique** : plusieurs lignes par code (avant/après les **fusions de communes**, ex. 2014, 1977). Une ligne sans `Date de fin` = **entrée active** (**601 lignes actives**).
- **`Nom officiel (RN)`** : libellé en MAJUSCULES tel que renvoyé par le Registre National.
- **`Nom unique (ETNIC)`** : libellé désambiguïsé (ex. plusieurs « Berchem » → `Berchem (ANTWERPEN)`, `Berchem (OOST-VLAANDEREN)`…).

### Extraction produite
- **`referentiels/codes_communes_ins.csv`** — historique complet (3 277 lignes) : `code_ins`, `date_debut`, `date_fin`, `nom_officiel_rn`, `nom_unique_etnic`, `actif` (`O`/`N`).
- **`referentiels/codes_communes_ins.json`** — même contenu (tableau d'objets).
- **`referentiels/codes_communes_ins_actives.csv`** — **601** communes/districts **actifs** (sous-ensemble pratique pour validation/saisie courante) : `code_ins`, `nom_officiel_rn`, `nom_unique_etnic`, `date_debut`.

Extrait :

| code_ins | nom_officiel_rn | nom_unique_etnic | actif |
|---|---|---|---|
| 25072 | NIVELLES | Nivelles | O |
| 62063 | LIÈGE | Liège | O |
| 11003 | BERCHEM | Berchem (ANTWERPEN) | N (fin 31/12/1982) |

---

## Usage côté pyetnic (recommandations)

1. **Embarquer** les CSV/JSON dans le package (données de référence versionnées). Noter la date de l'extrait communes (**20/07/2023** d'après le nom de fichier) ; prévoir une procédure de mise à jour depuis le catalogue SOA.
2. **Validation à l'écriture** (`enregistrerEtudiant`, `enregistrerInscription`) :
   - `codePays` / `codeNationalite` ∈ ensemble des codes 5 chiffres connus ; padder un entier sur 5 (`f"{n:05d}"`).
   - `localite.code` requis (et valide) **si** `codePays == "00150"` (Belgique) ; sinon fournir `localite.description`.
3. **Résolution à la lecture** : `code_pays → nom_pays`, `code_ins → nom_unique_etnic` pour affichage.
4. **Communes historiques** : pour une date de naissance ancienne, le code peut référencer une commune **fusionnée** ; conserver l'historique complet pour la résolution, mais proposer les **actives** à la saisie.

### Esquisse d'API (helpers — option retenue : extraction simple, helpers à implémenter dans pyetnic)
```python
def pad_code(n: int | str) -> str: return f"{int(n):05d}"

def valider_code_pays(code: str) -> bool: ...        # ∈ codes_pays.code_pays
def resoudre_pays(code: str) -> str | None: ...      # -> nom_pays
def code_nationalite_du_pays(code_pays: str) -> str: # via co_natio_id (≠ co_onss_id parfois)
def valider_localite(code_ins: str, *, belge: bool) -> bool: ...
def resoudre_commune(code_ins: str) -> str | None: ...  # -> nom_unique_etnic
```

---

## Fichiers livrés

| Fichier | Lignes | Description |
|---|---|---|
| `referentiels/codes_pays.csv` / `.json` | 260 | Pays + nationalités (codes INS 5 ch.) |
| `referentiels/codes_communes_ins.csv` / `.json` | 3 277 | Communes/districts INS (historique complet) |
| `referentiels/codes_communes_ins_actives.csv` | 601 | Communes/districts actifs |

> Source de vérité : catalogue de services SOA ETNIC (« documentation sur les pays / communes / districts et codes INS »). Les extraits ci-dessus en sont une copie exploitable, à re-synchroniser périodiquement.
