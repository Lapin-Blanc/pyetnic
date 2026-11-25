---
name: consolider
description: "Fin de fil pyetnic : capitaliser ce que la conversation a établi (comportement d'un service ETNIC, décision, reste à faire) en le rangeant à sa place (spec, issue GitHub, mémoire, CHANGELOG, CLAUDE.md), puis contrôler et commiter. À lancer avant de fermer un fil qui a appris quelque chose, ou pour préparer le fil suivant."
---

# Consolider un fil pyetnic

Ce qu'un fil établit et n'écrit pas disparaît avec lui. pyetnic a une place pour chaque
sorte de savoir : ce skill range, il n'accumule pas. Un corpus court et juste vaut mieux
qu'un long.

## 1. Relever

Reparcourir le fil et lister, en une phrase chacun, les faits **indérivables** : comportement
d'un service constaté, décision de l'utilisateur, piège rencontré, erreur corrigée, reste à
faire. Écarter ce qui se relit dans le code ou est déjà écrit. Marquer chaque fait
**vérifié** (avec son environnement et sa date) ou **supposé**, et ne jamais écrire un
supposé sans le dire.

## 2. Ranger : une question en cascade

1. **Son oubli peut-il casser quelque chose d'irréversible ?** (écriture en production,
   publication PyPI, donnée personnelle dans le dépôt public) -> `CLAUDE.md`, en impératif
   court.
2. **Est-ce un comportement d'un service ETNIC ?** -> la spec du service (`specs/NN_*.md`),
   sourcé : « (testé sur TQ, AAAA-MM-JJ) », « (observé en production, AAAA-MM-JJ) »,
   « observé une fois (date) », « (manuel rév x, §y) ». Un code d'erreur : aussi
   `specs/00_REGISTRE.md` et son routage dans `pyetnic/exceptions.py`. Ce qui change l'usage
   d'une fonction : aussi sa docstring.
3. **Est-ce un reste à faire ou une question ouverte ?** -> une issue GitHub : le backlog vit
   là, pas dans la mémoire.
4. **Est-ce une décision, le contexte d'un chantier, l'état des consommateurs, une
   préférence de méthode ?** -> une mémoire : une chose par fichier, une `description` écrite
   avec les mots des questions futures (c'est elle qui décide du rappel), des liens
   `[[nom]]`, la ligne d'index dans `MEMORY.md`. Une mémoire contredite se corrige ou se
   supprime, elle ne se double pas.
5. **Est-ce vérifiable par une commande ?** -> garder la commande, pas le résultat
   (`python tools/refresh_contracts.py --check`, un test).
6. **Est-ce un changement livré ?** -> `CHANGELOG.md`, section `[Unreleased]`.

## 3. Ce qui ne va pas dans le dépôt

Le dépôt est public. Aucun NISS, matricule, nom de personne, numéro ou nom d'établissement
(exemples en `etab 1234` / `impl 5678`), ni adresse mail. Ce qui est propre à l'utilisateur
(ses accords pour un essai en production, ses applications, ses démarches) va en mémoire.
Le réglementaire (circulaires, dotation, encadrement) n'a pas sa place ici : il vit dans
l'application qui consomme pyetnic.

Les scripts d'essai du scratchpad disparaissent avec la session : leurs constats vont dans
la spec, avec assez de détail pour rejouer l'essai. Un script qui resservira devient un outil
de `tools/`, avec ses tests.

## 4. Contrôler et clore

Sur les fichiers touchés :

    git diff | grep '^+' | grep -nE '\b[0-9]{11}\b|\b[0-9]{2}\.[0-9]{2}\.[0-9]{2}-[0-9]{3}\.[0-9]{2}\b'
    git diff | grep '^+' | grep -n $'\xe2\x80\x94'
    .venv/Scripts/python.exe -m pytest tests/regression tests/unit -q

et `python tools/refresh_contracts.py --check` si un contrat, un manuel ou une spec a bougé.
Tout résultat des deux premières commandes s'examine (un NISS ou un matricule à retirer, un
tiret cadratin à remplacer par un tiret court ; la seconde cherche ses octets UTF-8, la
locale de Git Bash refusant `grep -P '\x{2014}'`).

Puis commiter selon `CLAUDE.md` (Conventional Commits, branche et PR pour ce qui est
structurel), et commiter la mémoire, qui est un dépôt git local :

    git -C ~/.claude/projects/<slug du projet>/memory add <fichiers>
    git -C ~/.claude/projects/<slug du projet>/memory commit -m "docs: ..."

Rendre compte en quelques lignes : ce qui a été écrit et où, les issues ouvertes, et **ce qui
reste supposé** et demanderait une vérification.
