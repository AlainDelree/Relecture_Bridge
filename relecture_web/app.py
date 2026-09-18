#!/usr/bin/env python3
"""
Programme web indépendant de relecture_bridge : affiche, pour chaque projet
Bridge_Agent, ses worktrees actifs et ses commits locaux en attente de push.

Distinct de new_issue.py (dépôt bridge_agent, port et code séparés) — ce
programme est la maison des futures actions de relecture (merge/suppression
de worktree, résumés) ; la lecture git est réimplémentée dans git_info.py,
sans importer le code de bridge_agent (hors périmètre relecture_bridge).

Usage local uniquement, pas de protection par mot de passe (même choix que
new_issue.py).

    python3 relecture_web/app.py
"""

from flask import Flask, render_template

from git_info import ErreurRecuperationProjets, collect_etat_projets
from resumes_info import collect_resumes_projet

PORT = 5057

app = Flask(__name__)


@app.route("/")
def index():
    try:
        projets = collect_etat_projets()
        erreur = None
    except ErreurRecuperationProjets as exc:
        projets = []
        erreur = str(exc)

    for projet in projets:
        projet["resumes"] = collect_resumes_projet(projet["dossier_relecture"])

    return render_template("index.html", projets=projets, erreur=erreur)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
