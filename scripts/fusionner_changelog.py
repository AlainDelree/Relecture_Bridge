#!/usr/bin/env python3
"""scripts/fusionner_changelog.py — fusionne les CHANGELOG-<N>.md dans CHANGELOG.md.

Contexte : issue #336 — futur système de worktrees. Quand CCL travaille dans
un répertoire isolé, il écrit son entrée dans un fichier `CHANGELOG-<N>.md`
(N = numéro de l'issue) plutôt que dans `CHANGELOG.md` directement, pour
éviter les conflits systématiques sur ce fichier unique quand plusieurs
issues mode_write tournent en parallèle dans des worktrees distincts. Ce
script fusionne ces fichiers dans `CHANGELOG.md` avant le push d'Alain.

Fonctionnement : chaque `CHANGELOG-<N>.md` trouvé à la racine du dépôt est
inséré en tête de `CHANGELOG.md`, juste après l'en-tête fixe du fichier
(jusqu'à la ligne vide qui suit « Convention d'ajout : ... »), triés par N
décroissant — cohérent avec la convention « plus récente en tête » de
`CHANGELOG.md` (issue #252). Le contenu de chaque fichier est repris sans
modification, à une exception près (issue #104) : si le fichier commence
(lignes vides tolérées avant) par la ligne de titre d'échange « # CHANGELOG-N
— à fusionner dans CHANGELOG.md » (tiret cadratin ou simple, N quelconque),
cette ligne et la ou les lignes vides qui la suivent directement sont
retirées avant insertion — elle ne décrit que le fichier temporaire, pas
l'entrée de changelog elle-même. Absente, rien n'est retiré. Les fichiers
`CHANGELOG-<N>.md` traités sont ensuite supprimés. Aucun fichier trouvé :
message et sortie propre (code 0), `CHANGELOG.md` inchangé — propriété qui
rend une seconde exécution sans nouveaux fichiers idempotente, puisque les
fichiers sources du premier passage ont déjà été supprimés.

Ce script n'est pas appelé par watcher.py (qui ne connaît rien au système de
worktrees) mais par `fusionner_changelog_worktree` dans relecture_web/git_info.py
(issue #51), automatiquement juste après chaque fusion de branche réussie
depuis l'interface relecture_web — un lancement manuel reste possible (voir
Usage ci-dessous) pour rattraper un cas resté non fusionné.

Depuis l'issue #87, c'est toujours CETTE copie (celle de relecture_bridge)
qui est utilisée, quel que soit le projet cible (passé via `--repo`) : la
plupart des projets n'ont pas leur propre copie du script, seul relecture_web
en a besoin pour intégrer le CHANGELOG. Le script doit donc rester robuste
face à un `CHANGELOG.md` cible qui ne suit pas forcément la convention
« Convention d'ajout : ... » de relecture_bridge (issue #252) :
- en-tête attendu présent -> insertion juste après, comme avant ;
- en-tête absent mais un titre de niveau 1 (`# ...`) présent -> insertion
  juste après ce titre (et la ligne vide qui le suit, le cas échéant) ;
- ni l'un ni l'autre (fichier vide, ou sans titre) -> insertion en tête du
  fichier ;
- `CHANGELOG.md` absent -> créé avec pour seul contenu les entrées fusionnées.
Dans tous les cas, le contenu existant est conservé intégralement : jamais de
perte de contenu, seulement un point d'insertion différent.

Fins de ligne (issue #114, même défaut que celui corrigé par #107 côté
résolution de conflit dans relecture_web/git_info.py) : ce script peut être
exécuté sur un PC fixe Windows (projet distant CCW, via le bouton
« Fusionner le changelog »), où `os.linesep` vaut `\r\n`. Lire/écrire avec
les fonctions par défaut de `pathlib`/`open` (mode texte universel) aurait
traduit silencieusement toute fin de ligne vers `\r\n` à l'ÉCRITURE,
indépendamment de la convention d'origine de `CHANGELOG.md` : un fichier
entièrement en LF se serait retrouvé entièrement en CRLF après un simple
ajout d'entrée, faisant apparaître tout le fichier comme modifié dans le
commit. Tous les fichiers sont donc lus et réécrits avec `newline=""`
(aucune traduction, voir `_normaliser_fin_de_ligne`/`_fin_de_ligne_
dominante`) : le contenu déjà présent dans `CHANGELOG.md` n'est jamais
touché, seul le texte inséré est ramené à la fin de ligne dominante du
fichier cible.

Usage :
    python3 scripts/fusionner_changelog.py                # dépôt courant (.)
    python3 scripts/fusionner_changelog.py --repo /chemin/vers/le/depot
"""
import argparse
import re
import sys
from pathlib import Path

MOTIF_FICHIER = re.compile(r"^CHANGELOG-(\d+)\.md$")
MOTIF_ENTETE_ECHANGE = re.compile(
    r"^#\s*CHANGELOG-\d+\s*[—-]\s*.*\bà fusionner\b", re.IGNORECASE
)


def _trouver_fichiers(repo: Path) -> list:
    """Retourne les (N, chemin) des CHANGELOG-<N>.md trouvés à la racine du
    dépôt, triés par N décroissant (plus récent en tête)."""
    fichiers = []
    for chemin in repo.iterdir():
        if not chemin.is_file():
            continue
        m = MOTIF_FICHIER.match(chemin.name)
        if m:
            fichiers.append((int(m.group(1)), chemin))
    fichiers.sort(key=lambda t: t[0], reverse=True)
    return fichiers


def _point_insertion(lignes: list) -> int:
    """Index (dans `lignes`) de la ligne juste après la ligne vide qui suit
    « Convention d'ajout : ... » — point d'insertion en tête du contenu,
    juste après l'en-tête fixe de CHANGELOG.md (convention #252). None si
    l'en-tête attendu est introuvable (CHANGELOG.md d'un autre projet, qui ne
    suit pas forcément cette convention — voir `_point_insertion_repli`)."""
    for i, ligne in enumerate(lignes):
        if ligne.startswith("Convention d'ajout"):
            for j in range(i + 1, len(lignes)):
                if lignes[j].strip() == "":
                    return j + 1
            return len(lignes)
    return None


def _point_insertion_repli(lignes: list) -> int:
    """Point d'insertion utilisé quand l'en-tête « Convention d'ajout : ... »
    est absent (issue #87 — CHANGELOG.md d'un projet sans cette convention) :
    juste après le premier titre de niveau 1 (`# ...`) rencontré, et la ligne
    vide qui le suit le cas échéant ; sinon (aucun titre, ou fichier vide/
    absent) en tête du fichier (index 0). Ne perd jamais de contenu : ne fait
    que choisir où insérer les nouvelles entrées."""
    for i, ligne in enumerate(lignes):
        if ligne.lstrip().startswith("# "):
            j = i + 1
            while j < len(lignes) and lignes[j].strip() == "":
                j += 1
            return j
    return 0


def _retirer_entete_echange(texte: str) -> str:
    """Retire, si présente, la ligne de titre d'échange « # CHANGELOG-N —
    à fusionner dans CHANGELOG.md » en tout début de fichier (lignes vides
    tolérées avant elle), ainsi que la ou les lignes vides qui la suivent
    directement — pour ne pas laisser de trou dans le résultat. Cette ligne
    ne décrit que le fichier d'échange temporaire, pas l'entrée de
    changelog elle-même (issue #104). Si elle est absente, le texte est
    retourné inchangé : jamais de perte d'une vraie entrée."""
    lignes = texte.splitlines(keepends=True)
    i = 0
    while i < len(lignes) and lignes[i].strip() == "":
        i += 1
    if i >= len(lignes) or not MOTIF_ENTETE_ECHANGE.match(lignes[i].strip()):
        return texte
    i += 1
    while i < len(lignes) and lignes[i].strip() == "":
        i += 1
    return "".join(lignes[i:])


def _fin_de_ligne_dominante(contenu: str) -> str:
    """Fin de ligne dominante de `contenu` (issue #114, même principe que
    `_fin_de_ligne_dominante_fichier` dans relecture_web/git_info.py, issue
    #107 — dupliqué ici plutôt qu'importé : ce script est copié seul sur le
    PC fixe CCW, sans le reste de relecture_web) : la plus fréquente entre
    `\\r\\n` (CRLF) et `\\n` isolé (LF), par simple comptage — `\\n` par
    défaut en cas d'égalité ou d'absence totale de fin de ligne."""
    nb_crlf = contenu.count("\r\n")
    nb_lf_isole = contenu.count("\n") - nb_crlf
    return "\r\n" if nb_crlf > nb_lf_isole else "\n"


def _normaliser_fin_de_ligne(texte: str, fin_de_ligne: str) -> str:
    """Ramène toutes les fins de ligne de `texte` à `fin_de_ligne`, quelle
    que soit leur forme d'origine (`\\r\\n`, `\\n`, ou un mélange des deux)
    — appliqué UNIQUEMENT au texte de chaque CHANGELOG-<N>.md inséré,
    jamais au contenu déjà présent dans CHANGELOG.md, pour que celui-ci
    reste strictement inchangé (issue #114)."""
    return texte.replace("\r\n", "\n").replace("\n", fin_de_ligne)


def fusionner(repo: Path) -> dict:
    """Exécute la fusion. Retourne un rapport structuré (utilisé aussi bien
    pour l'affichage console que pour des tests)."""
    fichiers = _trouver_fichiers(repo)
    if not fichiers:
        return {"erreur": None, "traites": [], "message": "Aucun CHANGELOG-<N>.md trouvé — rien à fusionner."}

    fichier_changelog = repo / "CHANGELOG.md"
    en_tete_absent = False
    if fichier_changelog.exists():
        # `newline=""` (issue #114) : aucune traduction de fin de ligne à la
        # lecture — sans ça, le mode texte universel par défaut aplatirait
        # silencieusement tout `\r\n`/`\r` en `\n`, et la fin de ligne
        # dominante calculée ci-dessous porterait alors toujours sur un
        # contenu déjà perdu.
        with open(fichier_changelog, encoding="utf-8", newline="") as f:
            contenu = f.read()
        fin_de_ligne = _fin_de_ligne_dominante(contenu)
        lignes = contenu.splitlines(keepends=True)
        idx = _point_insertion(lignes)
        if idx is None:
            en_tete_absent = True
            idx = _point_insertion_repli(lignes)
    else:
        lignes = []
        idx = 0
        fin_de_ligne = "\n"

    blocs = []
    for n, chemin in fichiers:
        with open(chemin, encoding="utf-8", newline="") as f:
            texte_brut = f.read()
        texte = _retirer_entete_echange(texte_brut).strip("\r\n")
        texte = _normaliser_fin_de_ligne(texte, fin_de_ligne)
        blocs.append(texte + fin_de_ligne * 2)

    nouveau_contenu = "".join(lignes[:idx]) + "".join(blocs) + "".join(lignes[idx:])
    # `newline=""` à l'écriture aussi : sans ça, Python retraduirait chaque
    # `\n` vers `os.linesep` de la machine qui EXÉCUTE ce script — `\r\n` sur
    # le PC fixe Windows, ce qui aurait converti en bloc tout CHANGELOG.md
    # resté en LF jusqu'ici (le défaut que #107 avait déjà corrigé côté
    # résolution de conflit, voir l'en-tête de ce fichier).
    with open(fichier_changelog, "w", encoding="utf-8", newline="") as f:
        f.write(nouveau_contenu)

    for n, chemin in fichiers:
        chemin.unlink()

    return {
        "erreur": None,
        "traites": [(n, chemin.name) for n, chemin in fichiers],
        "en_tete_absent": en_tete_absent,
    }


def _afficher_rapport(rapport: dict) -> int:
    if rapport.get("erreur"):
        print(f"ERREUR : {rapport['erreur']}", file=sys.stderr)
        return 1

    if not rapport["traites"]:
        print(rapport["message"])
        return 0

    numeros = ", ".join(f"#{n}" for n, _ in rapport["traites"])
    print(f"{len(rapport['traites'])} fichier(s) fusionné(s) dans CHANGELOG.md (issues {numeros}) :")
    for n, nom in rapport["traites"]:
        print(f"  - {nom} -> supprimé après fusion")
    if rapport.get("en_tete_absent"):
        print("NOTE : en-tête « Convention d'ajout : ... » absent de CHANGELOG.md "
              "(projet sans cette convention) — insertion en repli, après le "
              "premier titre trouvé ou en tête de fichier.")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Fusionne les CHANGELOG-<N>.md (worktrees) dans CHANGELOG.md, "
                     "les plus récents (N décroissant) en tête, puis les supprime."
    )
    parser.add_argument("--repo", type=Path, default=Path("."),
                         help="racine du dépôt à scanner (défaut : .)")
    args = parser.parse_args()

    rapport = fusionner(args.repo.resolve())
    sys.exit(_afficher_rapport(rapport))


if __name__ == "__main__":
    main()
