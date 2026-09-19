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
    get_branches_locales,
    supprimer_worktree,
)
from resumes_info import collect_resumes_projet, regrouper_resumes_par_branche

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


def _trouver_projet(nom_projet):
    projets, erreur = _charger_projets()
    for projet in projets:
        if projet["nom"] == nom_projet:
            return projet, erreur
    return None, erreur


@app.route("/")
def index():
    """Niveau 1 : liste des projets, avec le nombre de résumés en attente
    pour chacun — pas de détail de branches/commits ici."""
    projets, erreur = _charger_projets()

    for projet in projets:
        if projet["statut"] == "ok":
            projet["resumes"] = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
        else:
            projet["resumes"] = []

    return render_template("index.html", projets=projets, erreur=erreur)


@app.route("/projet/<nom_projet>")
def projet_route(nom_projet):
    """Niveau 2 : branches d'un projet (issue #10), chacune avec son compteur
    de résumés en attente. Les worktrees actifs y apparaissent naturellement
    (une branche = un worktree potentiel) ; les actions merge/suppression
    existantes restent ici, en attendant leur refonte dans une issue séparée."""
    projet, erreur = _trouver_projet(nom_projet)
    if not projet:
        flash(f"❌ Projet « {nom_projet} » introuvable.", "erreur")
        return redirect(url_for("index"))

    if projet["statut"] != "ok":
        projet["branches"] = []
        return render_template("projet.html", projet=projet, erreur=erreur)

    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_par_branche = regrouper_resumes_par_branche(resumes, projet["repertoire"])

    branches = get_branches_locales(projet["repertoire"])
    for branche in branches:
        branche["nb_resumes"] = len(resumes_par_branche.get(branche["nom"], []))
    projet["branches"] = branches
    projet["worktree_par_branche"] = {
        worktree["branch"]: worktree for worktree in projet["worktrees"] if worktree["branch"]
    }

    return render_template("projet.html", projet=projet, erreur=erreur)


@app.route("/projet/<nom_projet>/branche/<path:nom_branche>")
def branche_route(nom_projet, nom_branche):
    """Niveau 3 : commits d'une branche, en cartes repliées par défaut (hash +
    message seulement) — le résumé structuré et le diff complet restent
    consultables en dépliant chaque carte."""
    projet, _erreur = _trouver_projet(nom_projet)
    if not projet or projet["statut"] != "ok":
        flash(f"❌ Projet « {nom_projet} » introuvable ou inaccessible.", "erreur")
        return redirect(url_for("index"))

    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_par_branche = regrouper_resumes_par_branche(resumes, projet["repertoire"])
    resumes_branche = resumes_par_branche.get(nom_branche, [])

    return render_template(
        "branche.html", projet=projet, nom_branche=nom_branche, resumes=resumes_branche,
    )


@app.route("/projet/<nom_projet>/merger", methods=["POST"])
def merger_worktree_route(nom_projet):
    chemin_worktree = request.form.get("chemin_worktree", "")
    projet, worktree = _trouver_worktree(nom_projet, chemin_worktree)

    if not projet or not worktree or worktree["est_worktree_principal"] or not worktree["branch"]:
        flash("❌ Worktree introuvable ou action invalide.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    resultat = fusionner_worktree(projet["repertoire"], worktree["branch"])
    if resultat["ok"]:
        flash(
            f"✅ « {worktree['branch']} » fusionnée dans « {projet['branche_principale']} » "
            f"— {resultat['commande']}",
            "succes",
        )
    else:
        flash(f"❌ Échec de la fusion ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/supprimer", methods=["POST"])
def supprimer_worktree_route(nom_projet):
    chemin_worktree = request.form.get("chemin_worktree", "")
    projet, worktree = _trouver_worktree(nom_projet, chemin_worktree)

    if not projet or not worktree or worktree["est_worktree_principal"]:
        flash("❌ Worktree introuvable ou action invalide.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))
    if not worktree["merge_ok"]:
        flash(
            "❌ Suppression refusée : cette branche n'est pas confirmée "
            "fusionnée dans la branche principale.",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    resultat = supprimer_worktree(projet["repertoire"], worktree["path"])
    if resultat["ok"]:
        flash(f"✅ Worktree supprimé — {resultat['commande']}", "succes")
    else:
        flash(f"❌ Échec de la suppression ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=PORT, debug=False)
