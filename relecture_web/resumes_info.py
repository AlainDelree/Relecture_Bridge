#!/usr/bin/env python3
"""
Lecture des fichiers en attente de relecture (Non_Lu/) pour chaque projet.

Le hook post-commit exporte, pour chaque commit, un `.diff` brut et soit un
`_resume.md` (résumé fonctionnel en trois sections, généré par
resumer_diff.py), soit un `_annote.md` pour les fichiers plus anciens non
encore relus (ancien format pédagogique, avant le changement d'objectif du
projet). Ce module regroupe ces fichiers par commit et prépare les résumés
pour un affichage scannable, sans dépendre du code de bridge_agent.
"""

import html
import os
import re

# relecture_web/ est un sous-dossier direct de la racine Relecture_Bridge, là
# où le hook post-commit crée <projet>/Non_Lu/ (DOSSIER_RELECTURE="$HOME/Relecture_Bridge").
DOSSIER_RELECTURE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Titres exacts produits par le prompt de resumer_diff.py.
TITRES_SECTIONS = {
    "nature du changement": "nature",
    "intention probable": "intention",
    "points d'attention": "attention",
}


def _extraire_hash(nom_fichier):
    """Le hash court est le premier segment du nom de fichier, avant le
    premier '_' (ex. 'd46a7ba' dans 'd46a7ba_bloc-formes...diff')."""
    return nom_fichier.split("_", 1)[0]


def _parser_sections_resume(texte):
    """Découpe un _resume.md en ses trois sections attendues (nature du
    changement / intention probable / points d'attention)."""
    lignes_par_section = {"nature": [], "intention": [], "attention": []}
    cle_courante = None
    for ligne in texte.splitlines():
        if ligne.startswith("## "):
            cle_courante = TITRES_SECTIONS.get(ligne[3:].strip().lower())
            continue
        if cle_courante:
            lignes_par_section[cle_courante].append(ligne)
    return {cle: "\n".join(lignes).strip() for cle, lignes in lignes_par_section.items()}


def _rendu_leger(texte):
    """Transforme le texte d'une section (puces '- ...', gras '**...**') en
    HTML minimal, sans dépendance à une bibliothèque markdown externe.
    Échappe d'abord tout le texte pour rester sûr même si le contenu du
    résumé (généré par un LLM à partir d'un diff) contient des caractères
    HTML."""
    echappe = html.escape(texte)
    echappe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", echappe)

    morceaux = []
    dans_liste = False
    for ligne in echappe.splitlines():
        if ligne.startswith("- "):
            if not dans_liste:
                morceaux.append("<ul>")
                dans_liste = True
            morceaux.append(f"<li>{ligne[2:]}</li>")
        else:
            if dans_liste:
                morceaux.append("</ul>")
                dans_liste = False
            if ligne.strip():
                morceaux.append(f"<p>{ligne}</p>")
    if dans_liste:
        morceaux.append("</ul>")
    return "\n".join(morceaux)


def collect_resumes_projet(dossier_relecture_projet):
    """Liste, pour un projet, les fichiers en attente dans Non_Lu/ : chaque
    entrée regroupe le .diff et son résumé (_resume.md ou _annote.md) par
    hash de commit, du plus récent au plus ancien."""
    dossier_non_lu = os.path.join(DOSSIER_RELECTURE, dossier_relecture_projet, "Non_Lu")
    if not os.path.isdir(dossier_non_lu):
        return []

    par_hash = {}
    for nom_fichier in os.listdir(dossier_non_lu):
        chemin = os.path.join(dossier_non_lu, nom_fichier)
        if not os.path.isfile(chemin):
            continue

        entree = par_hash.setdefault(_extraire_hash(nom_fichier), {
            "diff": None, "resume": None, "annote": None, "mtime": 0,
        })
        entree["mtime"] = max(entree["mtime"], os.path.getmtime(chemin))
        if nom_fichier.endswith(".diff"):
            entree["diff"] = nom_fichier
        elif nom_fichier.endswith("_resume.md"):
            entree["resume"] = nom_fichier
        elif nom_fichier.endswith("_annote.md"):
            entree["annote"] = nom_fichier

    resultats = []
    for hash_commit, entree in par_hash.items():
        entree["hash"] = hash_commit

        if entree["resume"]:
            chemin = os.path.join(dossier_non_lu, entree["resume"])
            with open(chemin, encoding="utf-8", errors="replace") as f:
                contenu_resume = f.read()
            sections = _parser_sections_resume(contenu_resume)
            if any(sections.values()):
                entree["sections"] = {cle: _rendu_leger(texte) for cle, texte in sections.items()}
            else:
                # Résumé présent mais qui ne suit pas le format en trois
                # sections attendu (ex. généré avant un changement de
                # prompt) : on l'affiche tel quel plutôt que de perdre
                # l'information.
                entree["resume_brut"] = contenu_resume

        if entree["annote"]:
            chemin = os.path.join(dossier_non_lu, entree["annote"])
            with open(chemin, encoding="utf-8", errors="replace") as f:
                entree["contenu_annote"] = f.read()

        if entree["diff"]:
            chemin = os.path.join(dossier_non_lu, entree["diff"])
            with open(chemin, encoding="utf-8", errors="replace") as f:
                entree["contenu_diff"] = f.read()

        resultats.append(entree)

    resultats.sort(key=lambda e: e["mtime"], reverse=True)
    return resultats
