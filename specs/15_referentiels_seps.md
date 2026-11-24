# Référentiels SEPS - Codes pays, nationalités et communes (INS)

> Documentation et extraction exploitable des référentiels qui alimentent les champs « code » de la signalétique SEPS.
> Sources : `Codes_Pays.xls` (260 pays) et `INS_communesNais200723.xlsx` (communes/districts INS), fichiers de référence du catalogue SOA ; manuel « Enregistrer Étudiants » **2.3** (rev 10.0, 10/06/2026), §3.1.2, §3.1.8.2, §3.1.8.4 et §3.3.1.2 ; contrat de production `etudiantDetails_v1.xsd` (relevé du 2026-11-24).
> Première analyse : 2026-06-09 (session 7). Mise à jour : 2026-11-24 (#24) : références au manuel 2.3, assouplissement d'`AdresseType`, état réel de pyetnic.

---

## Pourquoi ce référentiel

Dans les XSD SEPS, les champs `codePays`, `codeNationalite` et `localite.code` sont déclarés en **`xs:string` libre** (aucune énumération, aucun pattern). Leur **sens** (codes **INS/ONSS**) n'est donné que par le manuel et par ces deux fichiers de référence du catalogue SOA.

Champs concernés (specs 09 et 10) :

| Champ XSD | Card. (contrat de production) | Référentiel | Format réel (manuel 2.3) |
|---|---|---|---|
| `naissance.codePays` | obligatoire | **pays** (`CO_ONSS_ID`) | INS pays, **5 chiffres** (`[0-9]{5}`, ex. `00150`) |
| `adresse.codePays` | **0..1** (obligatoire au catalogue 2.1 et au manuel) | **pays** (`CO_ONSS_ID`) | idem |
| `codeNationalite` | 0..1 | **pays** (`CO_NATIO_ID`) | INS nationalité, **5 chiffres** (ex. `00150`) |
| `naissance.localite.code` | 0..1 | **communes** (`code INS`) | INS commune, **5 chiffres** (`[0-9]{5}`, ex. `25072`) ; obligatoire si **belge** |
| `adresse.localite.code` | 0..1 | **communes** | idem |

> Règles du manuel 2.3 :
> - §3.1.2 : la **localité** porte un `code` INS **obligatoire si la commune ou le district est belge** ; sinon seul `description` (libellé de la ville) est renseigné. Pour un enregistrement sans NISS (§3.3.1.2.1) : code de la localité de naissance si le pays est la Belgique, sinon sa description ; description de la localité d'adresse si le pays n'est pas la Belgique.
> - §3.1.8.2 : pour une naissance à l'étranger, le RN ne renvoie que le **nom** de la ville, sans code.
> - Le **`codePays`** est un code INS **pays** (pas un code de commune).
> - Erreur associée : `30076` « Code de la localité est invalide ou est absent et la localité est en Belgique ou si la localité n'est pas en Belgique et la description de la localité est vide » (spec 10).
>
> **`codeNationalite` : `00150`, pas `BE`.** L'exemple DETAILS du manuel 2.3 (§3.3.1.2.2.2) envoie encore `BE` ; toutes les réponses portent le code INS. Envoyer le code INS à 5 chiffres.

---

## Référentiel PAYS / NATIONALITÉS

**Source** : `Codes_Pays.xls`, feuille `pays`, **260 entrées**. Colonnes d'origine : `CO_ONSS_ID`, `CO_ISO`, `CO_ISO_3`, `TE_NOM_PAYS` (majuscules), `TE_NOM_PAYS_MIN`, `TE_NOM_PAYS_LONG`, `CO_NATIO_ID`, `DT_DATE_DEBUT`, `DT_DATE_FIN`.

### Règle de codage
- **`codePays`** (naissance, adresse) = **`CO_ONSS_ID`** complété à 5 chiffres. Ex. Belgique `150` -> **`00150`**, France `111` -> `00111`, Congo (RDC) `306` -> `00306`.
- **`codeNationalite`** = **`CO_NATIO_ID`** complété à 5 chiffres.
- `CO_ONSS_ID` est compris entre 101 et 999. **Codes spéciaux** : `900` Apatride, `901` Pas encore définitivement établi, `999` Indéterminé.
- **`CO_NATIO_ID` diffère de `CO_ONSS_ID` pour 43 entrées** : certains territoires renvoient à la nationalité du pays « parent ». Ex. Gibraltar (180) -> nationalité 112 (Royaume-Uni) ; Macao/Hong Kong (231/234) -> 218 (Chine) ; Mayotte/Réunion (350/387) -> 111 (France). **Ne pas déduire la nationalité du code pays** : utiliser la colonne `code_nationalite`.
- **Namibie** : ISO2 = `NA` (préservé à l'extraction ; piège classique « NA -> valeur manquante »).

### Extraction produite
- **`referentiels/codes_pays.csv`** : colonnes `code_pays` (5 ch.), `co_onss_id`, `iso2`, `iso3`, `nom_pays`, `nom_pays_long`, `code_nationalite` (5 ch.), `co_natio_id`, `date_debut`, `date_fin`.
- **`referentiels/codes_pays.json`** : même contenu (tableau d'objets).

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

**Source** : `INS_communesNais200723.xlsx`, feuille `Feuil1`, **3 277 lignes**, **2 789 codes INS uniques**. Colonnes : `code INS`, `Date de début`, `Date de fin`, `Nom officiel (RN)`, `Nom unique (ETNIC)`.

### Caractéristiques
- **`code INS`** : toujours **5 chiffres** (plage 11001-93090). C'est ce qui alimente `localite.code`.
- **Historique** : plusieurs lignes par code (avant et après les **fusions de communes**, ex. 1977, 2014). Une ligne sans `Date de fin` = **entrée active** (**601 lignes actives**).
- **`Nom officiel (RN)`** : libellé en majuscules tel que renvoyé par le Registre national.
- **`Nom unique (ETNIC)`** : libellé désambiguïsé (ex. plusieurs « Berchem » -> `Berchem (ANTWERPEN)`, `Berchem (OOST-VLAANDEREN)`…).

### Extraction produite
- **`referentiels/codes_communes_ins.csv`** : historique complet (3 277 lignes) : `code_ins`, `date_debut`, `date_fin`, `nom_officiel_rn`, `nom_unique_etnic`, `actif` (`O`/`N`).
- **`referentiels/codes_communes_ins.json`** : même contenu (tableau d'objets).
- **`referentiels/codes_communes_ins_actives.csv`** : les **601** communes/districts **actifs** : `code_ins`, `nom_officiel_rn`, `nom_unique_etnic`, `date_debut`.

Extrait :

| code_ins | nom_officiel_rn | nom_unique_etnic | actif |
|---|---|---|---|
| 25072 | NIVELLES | Nivelles | O |
| 62063 | LIÈGE | Liège | O |
| 11003 | BERCHEM | Berchem (ANTWERPEN) | N (fin 31/12/1982) |

---

## État dans pyetnic

pyetnic **n'embarque pas** ces référentiels et ne valide ni ne résout ces codes (état au 2026-11-24) : les champs restent des chaînes, transmises telles quelles. Les extraits de `specs/referentiels/` servent de référence aux applications clientes.

Ce qu'une application cliente doit savoir pour s'en servir :
1. **Date de l'extrait** : le fichier des communes date du **20/07/2023** d'après son nom. Le resynchroniser depuis le catalogue SOA en cas de doute.
2. **À l'écriture** (`enregistrerEtudiant`, `modifierEtudiant`) : `codePays` / `codeNationalite` parmi les codes à 5 chiffres connus (compléter un entier à 5 chiffres) ; `localite.code` requis et valide si `codePays == "00150"` (Belgique), sinon `localite.description`.
3. **À la lecture** : `code_pays -> nom_pays`, `code_ins -> nom_unique_etnic` pour l'affichage.
4. **Communes historiques** : pour une date de naissance ancienne, le code peut désigner une commune **fusionnée** depuis : garder l'historique complet pour résoudre, proposer les communes **actives** à la saisie.

---

## Fichiers livrés

| Fichier | Lignes | Description |
|---|---|---|
| `referentiels/codes_pays.csv` / `.json` | 260 | Pays et nationalités (codes INS 5 ch.) |
| `referentiels/codes_communes_ins.csv` / `.json` | 3 277 | Communes/districts INS (historique complet) |
| `referentiels/codes_communes_ins_actives.csv` | 601 | Communes/districts actifs |

> Source de vérité : catalogue de services SOA ETNIC (« documentation sur les pays / communes / districts et codes INS », citée par le manuel 2.3 §3.1.2 et §3.1.8.2). Les extraits ci-dessus en sont une copie exploitable, à resynchroniser périodiquement.
