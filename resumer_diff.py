#!/usr/bin/env python3
"""
Résume un fichier .diff (sortie de `git show`) en un résumé de relecture
fonctionnelle, en appelant le CLI Claude Code déjà installé sur la machine
(`claude -p`, sans outils) plutôt qu'en ouvrant un nouveau canal d'appel
(clé API, requête HTTP directe, etc.).

Usage :
    python3 resumer_diff.py fichier.diff > fichier_resume.md

Le résumé produit suit toujours trois sections : nature du changement,
intention probable, et points d'attention (secrets/tokens, sécurité,
dépendance d'ordre avec d'autres commits/worktrees).
"""

import subprocess
import sys

TIMEOUT_SECONDES = 120

# Diffs énormes (ex. lockfile régénéré, fichier vendoré) : on tronque pour
# garder un coût et un temps de réponse raisonnables sur un hook qui tourne
# après chaque commit, sans jamais faire échouer l'export pour autant.
TAILLE_MAX_DIFF = 150_000

PROMPT = """Tu es un assistant de relecture de code pour un développeur qui vérifie ses commits avant de les pousser sur GitHub. Voici un diff git complet (sortie de `git show`), fourni sur l'entrée standard.

Rédige en français un résumé de relecture fonctionnelle, au format markdown, avec EXACTEMENT ces trois sections :

## Nature du changement
2 à 4 lignes maximum : ce qui a été modifié concrètement (fichiers, fonctions, comportement), sans paraphraser ligne à ligne le diff.

## Intention probable
1 à 2 lignes : pourquoi ce changement a probablement été fait, déduit du message de commit et du contenu du diff.

## Points d'attention
Liste à puces des points qui méritent une vigilance particulière avant de pousser : gestion de secrets/tokens/identifiants, code touchant à la sécurité (authentification, permissions, validation d'entrée), changement dont l'ordre d'application avec d'autres commits ou worktrees pourrait compter. Si rien de tel n'est détecté, écris une seule ligne : "Rien de particulier à signaler."

Ne produis aucun texte en dehors de ces trois sections. Ne pose pas de question. N'utilise aucun outil."""


def lire_diff(chemin):
    with open(chemin, "r", encoding="utf-8", errors="replace") as f:
        contenu = f.read()

    if len(contenu) > TAILLE_MAX_DIFF:
        contenu = (
            contenu[:TAILLE_MAX_DIFF]
            + "\n\n[... diff tronqué, trop volumineux pour le résumé automatique — voir le .diff complet ...]"
        )

    return contenu


def resumer(contenu_diff):
    resultat = subprocess.run(
        [
            "claude",
            "-p",
            "--no-session-persistence",
            "--tools", "",
            "--output-format", "text",
            PROMPT,
        ],
        input=contenu_diff,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDES,
    )

    if resultat.returncode != 0:
        raise RuntimeError(
            f"claude -p a échoué (code {resultat.returncode}) : {resultat.stderr.strip()}"
        )

    resume = resultat.stdout.strip()
    if not resume:
        raise RuntimeError("claude -p n'a renvoyé aucun texte")

    return resume + "\n"


def main():
    if len(sys.argv) != 2:
        print("Usage : resumer_diff.py fichier.diff", file=sys.stderr)
        sys.exit(1)

    contenu_diff = lire_diff(sys.argv[1])
    print(resumer(contenu_diff), end="")


if __name__ == "__main__":
    main()
