#!/usr/bin/env python3
"""
Annote un fichier .diff (sortie de `git show`) avec des explications
pédagogiques insérées au-dessus des lignes structurelles (commit, Author,
Date, diff --git, index, ---/+++,  @@ ... @@).

Usage :
    python3 annoter_diff.py fichier.diff > fichier_annote.txt

Les explications complètes n'apparaissent qu'une fois par type de ligne
dans tout le fichier (pour éviter la répétition sur un commit qui touche
plusieurs fichiers) ; les occurrences suivantes reçoivent un repère court.
"""

import re
import sys

EXPLICATIONS = {
    "commit": (
        "# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver "
        "précisément (ex. `git show <hash>`).",
        "# (commit suivant, même signification)",
    ),
    "author": (
        "# ── Qui a fait ce commit.",
        "# (auteur du commit suivant)",
    ),
    "date": (
        "# ── Quand ce commit a été fait.",
        "# (date du commit suivant)",
    ),
    "message": (
        "# ── Message de commit : résumé de l'intention du changement, "
        "écrit par celui qui a committé.",
        "# (message du commit suivant)",
    ),
    "diff_git": (
        "# ── Début du diff pour CE fichier précis. a/ = version avant, "
        "b/ = version après (identiques si le fichier n'a pas été renommé).",
        "# (diff du fichier suivant)",
    ),
    "new_file": (
        "# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.",
        None,
    ),
    "deleted_file": (
        "# ── Ce fichier est supprimé par ce commit.",
        None,
    ),
    "index": (
        "# ── Identifiants internes git (hash du contenu avant/après). "
        "Sans intérêt au quotidien, ignorable.",
        "# (index — ignorable)",
    ),
    "moins_moins_moins": (
        "# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).",
        "# (avant — fichier suivant)",
    ),
    "plus_plus_plus": (
        "# ── Version APRÈS ce commit.",
        "# (après — fichier suivant)",
    ),
    "hunk": (
        None,  # généré dynamiquement, voir plus bas
        None,
    ),
}

REGEX_COMMIT = re.compile(r"^commit [0-9a-f]{7,40}")
REGEX_AUTHOR = re.compile(r"^Author:\s")
REGEX_DATE = re.compile(r"^Date:\s")
REGEX_DIFF_GIT = re.compile(r"^diff --git a/(.+) b/(.+)$")
REGEX_NEW_FILE = re.compile(r"^new file mode")
REGEX_DELETED_FILE = re.compile(r"^deleted file mode")
REGEX_INDEX = re.compile(r"^index [0-9a-f]")
REGEX_MOINS = re.compile(r"^--- ")
REGEX_PLUS = re.compile(r"^\+\+\+ ")
REGEX_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def expliquer_hunk(correspondance):
    debut_avant, nb_avant, debut_apres, nb_apres = correspondance.groups()
    nb_avant = nb_avant or "1"
    nb_apres = nb_apres or "1"
    return (
        f"# ── Zone modifiée : ligne {debut_avant} ({nb_avant} ligne(s)) dans "
        f"l'ancienne version → ligne {debut_apres} ({nb_apres} ligne(s)) dans "
        f"la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = "
        f"contexte inchangé."
    )


def annoter(lignes):
    deja_vu = set()
    sortie = []
    attend_message = False

    for ligne in lignes:
        ligne_sans_saut = ligne.rstrip("\n")

        if REGEX_COMMIT.match(ligne_sans_saut):
            cle = "commit"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)

        elif REGEX_AUTHOR.match(ligne_sans_saut):
            cle = "author"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)

        elif REGEX_DATE.match(ligne_sans_saut):
            cle = "date"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)
            attend_message = True

        elif attend_message and ligne_sans_saut.strip() and ligne_sans_saut.startswith("    "):
            cle = "message"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)
            attend_message = False

        elif REGEX_DIFF_GIT.match(ligne_sans_saut):
            cle = "diff_git"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)

        elif REGEX_NEW_FILE.match(ligne_sans_saut):
            sortie.append(EXPLICATIONS["new_file"][0])

        elif REGEX_DELETED_FILE.match(ligne_sans_saut):
            sortie.append(EXPLICATIONS["deleted_file"][0])

        elif REGEX_INDEX.match(ligne_sans_saut):
            cle = "index"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)

        elif REGEX_MOINS.match(ligne_sans_saut):
            cle = "moins_moins_moins"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)

        elif REGEX_PLUS.match(ligne_sans_saut):
            cle = "plus_plus_plus"
            sortie.append(EXPLICATIONS[cle][1] if cle in deja_vu else EXPLICATIONS[cle][0])
            deja_vu.add(cle)

        correspondance_hunk = REGEX_HUNK.match(ligne_sans_saut)
        if correspondance_hunk:
            sortie.append(expliquer_hunk(correspondance_hunk))

        sortie.append(ligne_sans_saut)

    return "\n".join(sortie) + "\n"


def main():
    if len(sys.argv) != 2:
        print("Usage : annoter_diff.py fichier.diff", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8", errors="replace") as f:
        lignes = f.readlines()

    print(annoter(lignes), end="")


if __name__ == "__main__":
    main()
