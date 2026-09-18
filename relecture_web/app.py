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

import os

from flask import Flask, flash, redirect, render_template, request, url_for

from git_info import (
    ErreurRecuperationProjets,
    collect_etat_projets,
    fusionner_worktree,
    supprimer_worktree,
)
from resumes_info import collect_resumes_projet

PORT = 5057

app = Flask(__name__)
# Usage strictement local (pas d'exposition réseau) : une clé fixe par
# processus suffit, seule utilité ici est la signature des messages flash.
app.secret_key = os.urandom(24)


def _charger_projets():
    try:
        return collect_etat_projets(), None
    except ErreurRecuperationProjets as exc:
        return [], str(exc)


def _trouver_worktree(nom_projet, chemin_worktree):
    """Revérifie l'existence du projet/worktree à partir de l'état git actuel
    (pas des seules données du formulaire) avant toute action destructrice."""
    projets, _erreur = _charger_projets()
    for projet in projets:
        if projet["nom"] != nom_projet:
            continue
        for worktree in projet["worktrees"]:
            if os.path.realpath(worktree["path"]) == os.path.realpath(chemin_worktree):
                return projet, worktree
    return None, None


@app.route("/")
def index():
    projets, erreur = _charger_projets()

    for projet in projets:
        projet["resumes"] = collect_resumes_projet(projet["dossier_relecture"])

    return render_template("index.html", projets=projets, erreur=erreur)


@app.route("/projet/<nom_projet>/merger", methods=["POST"])
def merger_worktree_route(nom_projet):
    chemin_worktree = request.form.get("chemin_worktree", "")
    projet, worktree = _trouver_worktree(nom_projet, chemin_worktree)

    if not projet or not worktree or worktree["est_worktree_principal"] or not worktree["branch"]:
        flash("❌ Worktree introuvable ou action invalide.", "erreur")
        return redirect(url_for("index"))

    resultat = fusionner_worktree(projet["repertoire"], worktree["branch"])
    if resultat["ok"]:
        flash(
            f"✅ « {worktree['branch']} » fusionnée dans « {projet['branche_principale']} » "
            f"— {resultat['commande']}",
            "succes",
        )
    else:
        flash(f"❌ Échec de la fusion ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("index"))


@app.route("/projet/<nom_projet>/supprimer", methods=["POST"])
def supprimer_worktree_route(nom_projet):
    chemin_worktree = request.form.get("chemin_worktree", "")
    projet, worktree = _trouver_worktree(nom_projet, chemin_worktree)

    if not projet or not worktree or worktree["est_worktree_principal"]:
        flash("❌ Worktree introuvable ou action invalide.", "erreur")
        return redirect(url_for("index"))
    if not worktree["merge_ok"]:
        flash(
            "❌ Suppression refusée : cette branche n'est pas confirmée "
            "fusionnée dans la branche principale.",
            "erreur",
        )
        return redirect(url_for("index"))

    resultat = supprimer_worktree(projet["repertoire"], worktree["path"])
    if resultat["ok"]:
        flash(f"✅ Worktree supprimé — {resultat['commande']}", "succes")
    else:
        flash(f"❌ Échec de la suppression ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
