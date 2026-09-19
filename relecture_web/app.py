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
    get_remote_defaut,
    pousser_branche,
    revert_commit,
    supprimer_worktree,
)
from resumes_info import collect_resumes_projet, lister_fichiers_resumes_pushes, regrouper_resumes_par_branche

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


def _trouver_projet(nom_projet):
    projets, erreur = _charger_projets()
    for projet in projets:
        if projet["nom"] == nom_projet:
            return projet, erreur
    return None, erreur


def _projet_pret(nom_projet):
    """Revérifie l'existence et l'accessibilité du projet à partir de l'état
    git actuel (pas des seules données du formulaire) avant toute action.
    Retourne (projet, None) si prêt, sinon (None, message_erreur)."""
    projet, _erreur = _trouver_projet(nom_projet)
    if not projet or projet["statut"] != "ok":
        return None, f"❌ Projet « {nom_projet} » introuvable ou inaccessible."
    return projet, None


def _branches_par_nom(repertoire):
    return {branche["nom"]: branche for branche in get_branches_locales(repertoire)}


@app.route("/")
def index():
    """Niveau 1 : liste des projets, avec le nombre de résumés en attente
    pour chacun — pas de détail de branches/commits ici. Le nombre de
    résumés déjà pushés n'est plus précalculé ici (issue #19, ralentissait le
    chargement sur les projets à nombreux fichiers en attente) : il n'est
    annoncé qu'après coup, dans le message flash du bouton « Nettoyer tous
    les projets »."""
    projets, erreur = _charger_projets()

    for projet in projets:
        if projet["statut"] == "ok":
            projet["resumes"] = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
            projet["nb_worktrees_secondaires"] = sum(
                1 for worktree in projet["worktrees"] if not worktree["est_worktree_principal"]
            )
        else:
            projet["resumes"] = []

    return render_template("index.html", projets=projets, erreur=erreur)


@app.route("/projet/<nom_projet>")
def projet_route(nom_projet):
    """Niveau 2 : branches d'un projet (issue #10), chacune avec son compteur
    de résumés en attente et une case à cocher pour la sélection multiple
    (issue #12) — le panneau d'actions (push/merger/supprimer) qui apparaît
    pour la sélection agit sur ces branches, plus jamais par worktree affiché
    individuellement."""
    projets, erreur = _charger_projets()
    projet = next((p for p in projets if p["nom"] == nom_projet), None)
    if not projet:
        flash(f"❌ Projet « {nom_projet} » introuvable.", "erreur")
        return redirect(url_for("index"))

    if projet["statut"] != "ok":
        projet["branches"] = []
        return render_template("projet.html", projet=projet, erreur=erreur)

    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_par_branche = regrouper_resumes_par_branche(resumes, projet["repertoire"])

    remote = get_remote_defaut(projet["repertoire"])
    branches = get_branches_locales(projet["repertoire"])
    for branche in branches:
        branche["nb_resumes"] = len(resumes_par_branche.get(branche["nom"], []))
        branche["est_principale"] = branche["nom"] == projet["branche_principale"]
        branche["commande_push"] = f"git -C {projet['repertoire']} push {remote} {branche['nom']}"

        branche["peut_merger"] = not branche["est_principale"]
        branche["commande_merge"] = (
            f"git -C {projet['repertoire']} merge {branche['nom']}" if branche["peut_merger"] else None
        )

        branche["peut_supprimer"] = (
            branche["a_un_worktree"] and branche["mergee"] and not branche["est_principale"]
        )
        branche["commande_suppression"] = (
            f"git -C {projet['repertoire']} worktree remove {branche['chemin_worktree']}"
            if branche["peut_supprimer"] else None
        )
    projet["branches"] = branches
    projet["worktree_par_branche"] = {
        worktree["branch"]: worktree for worktree in projet["worktrees"] if worktree["branch"]
    }

    return render_template("projet.html", projet=projet, erreur=erreur)


@app.route("/projet/<nom_projet>/branche/<path:nom_branche>")
def branche_route(nom_projet, nom_branche):
    """Niveau 3 : commits d'une branche, en cartes repliées par défaut (hash +
    message seulement) — le résumé structuré et le diff complet restent
    consultables en dépliant chaque carte. Chaque carte dépliée porte
    l'action revert (issue #12), indépendante des autres commits."""
    projet, _erreur = _trouver_projet(nom_projet)
    if not projet or projet["statut"] != "ok":
        flash(f"❌ Projet « {nom_projet} » introuvable ou inaccessible.", "erreur")
        return redirect(url_for("index"))

    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_par_branche = regrouper_resumes_par_branche(resumes, projet["repertoire"])
    resumes_branche = resumes_par_branche.get(nom_branche, [])
    for resume in resumes_branche:
        resume["commande_revert"] = f"git -C {projet['repertoire']} revert --no-edit {resume['hash']}"

    return render_template(
        "branche.html", projet=projet, nom_branche=nom_branche, resumes=resumes_branche,
    )


@app.route("/projet/<nom_projet>/branche/<path:nom_branche>/revert", methods=["POST"])
def revert_commit_route(nom_projet, nom_branche):
    hash_commit = request.form.get("hash_commit", "")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not hash_commit:
        flash("❌ Hash de commit manquant.", "erreur")
        return redirect(url_for("branche_route", nom_projet=nom_projet, nom_branche=nom_branche))

    resultat = revert_commit(projet["repertoire"], hash_commit)
    if resultat["ok"]:
        flash(f"✅ Commit « {hash_commit} » annulé (revert) — {resultat['commande']}", "succes")
    else:
        flash(f"❌ Échec du revert de « {hash_commit} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("branche_route", nom_projet=nom_projet, nom_branche=nom_branche))


def _supprimer_fichiers(chemins):
    """Supprime chaque fichier de `chemins`, retourne (nb_supprimes, nb_echecs)."""
    nb_supprimes, nb_echecs = 0, 0
    for chemin in chemins:
        try:
            os.remove(chemin)
            nb_supprimes += 1
        except OSError:
            nb_echecs += 1
    return nb_supprimes, nb_echecs


@app.route("/nettoyer-tous-les-projets", methods=["POST"])
def nettoyer_tous_les_projets_route():
    """Applique à chaque projet accessible (statut « ok ») le nettoyage des
    résumés déjà pushés (issue #17, remplace le bouton par-projet de l'issue
    #16) — réutilise `lister_fichiers_resumes_pushes`/`get_commit_est_pushe`
    projet par projet ; l'échec d'un projet (dossier introuvable, pas de
    remote, etc.) est rapporté à part sans bloquer les autres."""
    projets, erreur = _charger_projets()
    if erreur:
        flash(erreur, "erreur")
        return redirect(url_for("index"))

    nb_supprimes_total, nb_echecs_total = 0, 0
    projets_en_echec = []
    for projet in projets:
        if projet["statut"] != "ok":
            continue
        try:
            fichiers = lister_fichiers_resumes_pushes(projet["dossier_relecture"], projet["repertoire"])
            nb_supprimes, nb_echecs = _supprimer_fichiers(fichiers)
            nb_supprimes_total += nb_supprimes
            nb_echecs_total += nb_echecs
        except Exception as exc:
            projets_en_echec.append(f"{projet['nom']} ({exc})")

    if projets_en_echec:
        flash(
            f"⚠️ {nb_supprimes_total} résumé(s) supprimé(s) au total — "
            f"échec sur {len(projets_en_echec)} projet(s) : " + ", ".join(projets_en_echec),
            "erreur",
        )
    elif nb_echecs_total:
        flash(f"⚠️ {nb_supprimes_total} fichier(s) supprimé(s), {nb_echecs_total} échec(s).", "erreur")
    else:
        flash(f"✅ {nb_supprimes_total} résumé(s) déjà pushé(s) supprimé(s) sur tous les projets.", "succes")
    return redirect(url_for("index"))


@app.route("/projet/<nom_projet>/pousser", methods=["POST"])
def pousser_branches_route(nom_projet):
    """Pousse chaque branche sélectionnée (case à cocher, niveau 2) jusqu'à
    son dernier commit — un push cible toujours une branche entière, jamais
    une sélection de commits épars (contrairement au revert)."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    branches = _branches_par_nom(projet["repertoire"])
    for nom in noms_branches:
        if nom not in branches:
            flash(f"❌ Branche « {nom} » introuvable.", "erreur")
            continue
        resultat = pousser_branche(projet["repertoire"], nom)
        if resultat["ok"]:
            flash(f"✅ « {nom} » poussée — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec du push de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/merger", methods=["POST"])
def merger_branches_route(nom_projet):
    """Fusionne chaque branche sélectionnée (case à cocher, niveau 2) dans la
    branche principale — action rattachée à la sélection de branches plutôt
    qu'à un worktree affiché individuellement (issue #12)."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    branche_principale = projet["branche_principale"]
    branches = _branches_par_nom(projet["repertoire"])
    for nom in noms_branches:
        if nom not in branches:
            flash(f"❌ Branche « {nom} » introuvable.", "erreur")
            continue
        if nom == branche_principale:
            flash(f"❌ « {nom} » est la branche principale, fusion ignorée.", "erreur")
            continue
        resultat = fusionner_worktree(projet["repertoire"], nom)
        if resultat["ok"]:
            flash(f"✅ « {nom} » fusionnée dans « {branche_principale} » — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec de la fusion de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/supprimer", methods=["POST"])
def supprimer_worktrees_route(nom_projet):
    """Supprime le worktree de chaque branche sélectionnée (case à cocher,
    niveau 2), seulement si son merge est confirmé — même garde-fou qu'avant
    (issue précédente), rattaché à la sélection plutôt qu'à l'affichage par
    worktree."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    branche_principale = projet["branche_principale"]
    branches = _branches_par_nom(projet["repertoire"])
    for nom in noms_branches:
        branche = branches.get(nom)
        if not branche:
            flash(f"❌ Branche « {nom} » introuvable.", "erreur")
            continue
        if nom == branche_principale:
            flash(f"❌ « {nom} » est la branche principale, suppression ignorée.", "erreur")
            continue
        if not branche["a_un_worktree"]:
            flash(f"❌ « {nom} » : pas de worktree actif, suppression impossible.", "erreur")
            continue
        if not branche["mergee"]:
            flash(
                f"❌ Suppression de « {nom} » refusée : branche pas confirmée "
                f"fusionnée dans « {branche_principale} ».",
                "erreur",
            )
            continue
        resultat = supprimer_worktree(projet["repertoire"], branche["chemin_worktree"])
        if resultat["ok"]:
            flash(f"✅ Worktree de « {nom} » supprimé — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec de la suppression de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


if __name__ == "__main__":
    import threading
    import webbrowser
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)
