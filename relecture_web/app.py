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
    comparer_commit_doublon,
    commit_est_securise,
    diagnostiquer_commits_orphelins,
    extraire_numero_issue,
    fusionner_worktree,
    get_branches_contenant,
    get_branches_distantes_contenant,
    get_branches_locales,
    get_diagnostic_doublons_branche,
    get_issue_deja_referencee,
    get_rapport_cherry_brut,
    get_remote_defaut,
    get_sujet_commit,
    hash_depuis_branche_recuperation,
    nom_branche_recuperation,
    pousser_branche,
    revert_commit,
    securiser_commit_orphelin,
    supprimer_branche_recuperation,
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


def _branches_par_nom(projet):
    return {
        branche["nom"]: branche
        for branche in get_branches_locales(projet["repertoire"], projet["branche_cible_comparaison"])
    }


def _diagnostiquer_orphelins(projet, resumes_orphelins):
    """Diagnostic automatique (issue #21) des commits orphelins d'un
    projet : ceux du groupe `None` de `regrouper_resumes_par_branche`
    (résumés en attente dont aucune branche locale actuelle ne contient le
    commit). Enrichit chaque diagnostic avec le sujet du commit, pour
    affichage, sans redemander à l'appelant de le faire."""
    if not resumes_orphelins:
        return []

    repertoire = projet["repertoire"]
    branche_cible = projet["branche_cible_comparaison"]
    resumes_par_hash = {resume["hash"]: resume for resume in resumes_orphelins}
    diagnostics = diagnostiquer_commits_orphelins(
        repertoire, branche_cible, list(resumes_par_hash.keys())
    )
    for diagnostic in diagnostics:
        resume = resumes_par_hash.get(diagnostic["hash"])
        diagnostic["sujet"] = resume["sujet"] if resume else get_sujet_commit(repertoire, diagnostic["hash"])
        for maillon in diagnostic["chaine"]:
            maillon["sujet"] = get_sujet_commit(repertoire, maillon["hash"])

        # Doute sur un cas A (issue #28) : `git cherry` compare le contenu
        # des diffs, pas les messages — un doublon réimplémenté différemment
        # (variables renommées, logique réorganisée) est alors classé
        # « nouveau, sûr » à tort. Le numéro d'issue référencé dans le
        # message est un indice indépendant : s'il apparaît déjà dans
        # branche_cible, on ne présente plus ce cas A comme un verdict
        # tranché. Ne concerne pas les autres cas (B/D/E/F), déjà nuancés ou
        # déjà signalés comme doublon.
        diagnostic["numero_issue"] = None
        diagnostic["doublon_possible"] = False
        if diagnostic["cas"] == "A":
            numero_issue = extraire_numero_issue(diagnostic["sujet"])
            if numero_issue and get_issue_deja_referencee(repertoire, branche_cible, numero_issue):
                diagnostic["numero_issue"] = numero_issue
                diagnostic["doublon_possible"] = True

        # Sécurisation (issue #23) : indépendante du diagnostic A-F ci-dessus,
        # affichée pour tout commit orphelin, tranché ou non.
        diagnostic["nom_branche_recuperation"] = nom_branche_recuperation(diagnostic["hash"])
        diagnostic["deja_securise"] = commit_est_securise(repertoire, diagnostic["hash"])
        diagnostic["commande_securisation"] = (
            f"git -C {repertoire} branch {diagnostic['nom_branche_recuperation']} {diagnostic['hash']}"
        )
    return diagnostics


def _construire_rapport_commit(
    projet, hash_commit, sujet, resume_texte, branche_cible,
    cherry, branches_locales, branches_distantes, autres_orphelins,
):
    """Assemble le texte du rapport de diagnostic manuel (issue #22) —
    tout ce qui est déjà disponible côté relecture_bridge pour un commit que
    le diagnostic automatique n'a pas pu trancher, prêt à coller dans une
    conversation Claude Chat dédiée au projet concerné."""
    lignes = [
        "=== Rapport de diagnostic — commit non tranché automatiquement ===",
        f"Projet : {projet['nom']} ({projet['depot']})",
        f"Répertoire : {projet['repertoire']}",
        f"Branche cible de comparaison configurée : {branche_cible or 'non configurée'}",
        "",
        f"Commit : {hash_commit}",
        f"Message : {sujet or '(sujet introuvable)'}",
        "",
        "--- Résumé déjà généré ---",
        resume_texte.strip() if resume_texte and resume_texte.strip() else "Aucun résumé disponible pour ce commit.",
        "",
        f"--- git cherry {branche_cible or '<branche cible>'} {hash_commit} ---",
        f"Échec : {cherry['erreur']}" if cherry["erreur"]
        else (cherry["sortie"] or "(sortie vide — aucun commit entre la base commune et ce hash)"),
        "",
        "--- Branches locales contenant ce commit ---",
        ", ".join(branches_locales) if branches_locales else "aucune",
        "",
        "--- Branches distantes contenant ce commit ---",
        ", ".join(branches_distantes) if branches_distantes else "aucune",
        "",
        "--- Autres commits orphelins actuellement en attente (ce projet) ---",
    ]
    if autres_orphelins:
        lignes.extend(f"{h} — {s or '(sujet introuvable)'}" for h, s in autres_orphelins)
    else:
        lignes.append("aucun autre")
    return "\n".join(lignes)


@app.route("/projet/<nom_projet>/rapport/<hash_commit>")
def rapport_commit_route(nom_projet, hash_commit):
    """Rapport texte prêt à copier pour un commit que le diagnostic
    automatique ne peut pas trancher (typiquement cas F, issue #22) :
    rassemble hash/message/résumé déjà généré, sortie brute de `git cherry`,
    branches locales/distantes le contenant, et le contexte déjà disponible
    (branche cible configurée, autres commits orphelins en attente) — pour
    coller le tout dans une conversation Claude Chat dédiée au projet.
    Route en lecture seule (GET), aucune action git déclenchée."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    repertoire = projet["repertoire"]
    branche_cible = projet["branche_cible_comparaison"]
    sujet = get_sujet_commit(repertoire, hash_commit)

    resumes = collect_resumes_projet(projet["dossier_relecture"], repertoire)
    resume_entree = next((r for r in resumes if r["hash"] == hash_commit), None)
    resume_texte = None
    if resume_entree:
        resume_texte = resume_entree.get("contenu_resume_brut") or resume_entree.get("contenu_annote")

    cherry = get_rapport_cherry_brut(repertoire, branche_cible, hash_commit)
    branches_locales = get_branches_contenant(repertoire, hash_commit)
    branches_distantes = get_branches_distantes_contenant(repertoire, hash_commit)

    resumes_orphelins = regrouper_resumes_par_branche(resumes, repertoire).get(None, [])
    autres_orphelins = [
        (r["hash"], r.get("sujet")) for r in resumes_orphelins if r["hash"] != hash_commit
    ]

    rapport = _construire_rapport_commit(
        projet, hash_commit, sujet, resume_texte, branche_cible,
        cherry, branches_locales, branches_distantes, autres_orphelins,
    )
    return render_template("rapport.html", projet=projet, hash_commit=hash_commit, rapport=rapport)


@app.route("/projet/<nom_projet>/comparer/<hash_commit>")
def comparer_commit_route(nom_projet, hash_commit):
    """Bouton « Comparer » (issue #30) pour un commit orphelin diagnostiqué
    doublon (cas B) : retrouve le commit exact de la branche cible dont le
    contenu correspond (empreinte de patch `git patch-id`, voir
    `comparer_commit_doublon`), et affiche le diff entre les deux — pour une
    vérification humaine directe, sans deviner de candidat ni lancer de
    commande manuelle. Route en lecture seule (GET), aucune action git
    déclenchée."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    repertoire = projet["repertoire"]
    branche_cible = projet["branche_cible_comparaison"]
    sujet = get_sujet_commit(repertoire, hash_commit)
    comparaison = comparer_commit_doublon(repertoire, branche_cible, hash_commit)

    return render_template(
        "comparer.html", projet=projet, hash_commit=hash_commit, sujet=sujet,
        branche_cible=branche_cible, comparaison=comparaison,
    )


@app.route("/projet/<nom_projet>/orphelin/<hash_commit>/securiser", methods=["POST"])
def securiser_orphelin_route(nom_projet, hash_commit):
    """Sécurise un commit orphelin (issue #23) en créant une branche
    `recuperation-<hash>` pointant dessus — action déclenchée en un clic
    confirmé côté template, applicable à tout commit orphelin sans attendre
    le diagnostic A-F (voir `securiser_commit_orphelin`)."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    resultat = securiser_commit_orphelin(projet["repertoire"], hash_commit)
    if resultat["deja_securise"]:
        flash(f"ℹ️ « {hash_commit} » déjà sécurisé — branche « {resultat['nom_branche']} » existante.", "succes")
    elif resultat["ok"]:
        flash(
            f"✅ « {hash_commit} » sécurisé — branche « {resultat['nom_branche']} » créée "
            f"({resultat['commande']}).",
            "succes",
        )
    else:
        flash(f"❌ Échec de la sécurisation de « {hash_commit} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


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
        projet["diagnostics_orphelins"] = []
        return render_template("projet.html", projet=projet, erreur=erreur)

    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_par_branche = regrouper_resumes_par_branche(resumes, projet["repertoire"])
    projet["diagnostics_orphelins"] = _diagnostiquer_orphelins(projet, resumes_par_branche.get(None, []))

    remote = get_remote_defaut(projet["repertoire"])
    branches = get_branches_locales(projet["repertoire"], projet["branche_cible_comparaison"])
    branche_cible_merge = projet["branche_cible_comparaison"]
    for branche in branches:
        branche["nb_resumes"] = len(resumes_par_branche.get(branche["nom"], []))
        branche["est_principale"] = branche["nom"] == projet["branche_principale"]
        branche["commande_push"] = f"git -C {projet['repertoire']} push {remote} {branche['nom']}"

        branche["peut_merger"] = branche["nom"] != branche_cible_merge
        branche["ne_contient_que_doublons"] = branche["peut_merger"] and get_diagnostic_doublons_branche(
            projet["repertoire"], branche_cible_merge, branche["nom"]
        )
        if branche["ne_contient_que_doublons"]:
            branche["peut_merger"] = False

        if not branche["peut_merger"]:
            branche["commande_merge"] = None
        elif branche_cible_merge == projet["branche_principale"]:
            branche["commande_merge"] = f"git -C {projet['repertoire']} merge {branche['nom']}"
        else:
            branche["commande_merge"] = (
                f"git -C {projet['repertoire']} checkout {branche_cible_merge} && "
                f"git merge {branche['nom']} && git checkout {projet['branche_principale']}"
            )

        branche["peut_supprimer"] = (
            branche["a_un_worktree"] and branche["mergee"] and not branche["est_principale"]
        )
        branche["commande_suppression"] = (
            f"git -C {projet['repertoire']} worktree remove {branche['chemin_worktree']}"
            if branche["peut_supprimer"] else None
        )

        # Suppression de branche de récupération (issue #29) : seule la
        # convention de nom `recuperation-<hash>` conditionne la
        # disponibilité de l'action, indépendamment du badge de diagnostic
        # ci-dessus — ces branches n'ont jamais de worktree, donc
        # `peut_supprimer` (qui exige `a_un_worktree`) ne les couvre jamais.
        branche["peut_supprimer_branche_recuperation"] = (
            hash_depuis_branche_recuperation(branche["nom"]) is not None
        )
        branche["commande_suppression_branche_recuperation"] = (
            f"git -C {projet['repertoire']} branch -D {branche['nom']}"
            if branche["peut_supprimer_branche_recuperation"] else None
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

    branches = _branches_par_nom(projet)
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
    branche cible de comparaison configurée pour le projet (repli sur la
    branche principale git si aucune configuration explicite — voir
    `get_branche_cible_comparaison`, issue #20 ; issue #24) — action
    rattachée à la sélection de branches plutôt qu'à un worktree affiché
    individuellement (issue #12)."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    branche_cible = projet["branche_cible_comparaison"]
    branches = _branches_par_nom(projet)
    for nom in noms_branches:
        if nom not in branches:
            flash(f"❌ Branche « {nom} » introuvable.", "erreur")
            continue
        if nom == branche_cible:
            flash(f"❌ « {nom} » est la branche cible de fusion, fusion ignorée.", "erreur")
            continue
        if get_diagnostic_doublons_branche(projet["repertoire"], branche_cible, nom):
            flash(
                f"❌ « {nom} » ne contient que des doublons déjà intégrés dans « {branche_cible} », fusion ignorée.",
                "erreur",
            )
            continue
        resultat = fusionner_worktree(projet["repertoire"], branche_cible, nom)
        if resultat["ok"]:
            flash(f"✅ « {nom} » fusionnée dans « {branche_cible} » — {resultat['commande']}", "succes")
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
    branche_cible = projet["branche_cible_comparaison"]
    branches = _branches_par_nom(projet)
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
                f"fusionnée dans « {branche_cible} ».",
                "erreur",
            )
            continue
        resultat = supprimer_worktree(projet["repertoire"], branche["chemin_worktree"])
        if resultat["ok"]:
            flash(f"✅ Worktree de « {nom} » supprimé — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec de la suppression de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/supprimer-branche-recuperation", methods=["POST"])
def supprimer_branches_recuperation_route(nom_projet):
    """Supprime définitivement (`git branch -D`) chaque branche de
    récupération sélectionnée (case à cocher, niveau 2) — ces branches
    (issue #23) n'ont pas de worktree, donc distinct de
    `supprimer_worktrees_route`. Revérifiée ici indépendamment de la case
    cochée côté template : seule la convention de nom
    `recuperation-<hash>` (issue #26) autorise la suppression, jamais le
    badge de diagnostic (issue #29)."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    branches = _branches_par_nom(projet)
    for nom in noms_branches:
        if nom not in branches:
            flash(f"❌ Branche « {nom} » introuvable.", "erreur")
            continue
        if hash_depuis_branche_recuperation(nom) is None:
            flash(f"❌ « {nom} » ne suit pas la convention recuperation-<hash>, suppression refusée.", "erreur")
            continue
        resultat = supprimer_branche_recuperation(projet["repertoire"], nom)
        if resultat["ok"]:
            flash(f"✅ Branche « {nom} » supprimée — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec de la suppression de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


if __name__ == "__main__":
    import threading
    import webbrowser
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)
