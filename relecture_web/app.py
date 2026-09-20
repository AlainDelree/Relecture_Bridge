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
import subprocess

from flask import Flask, flash, g, redirect, render_template, request, url_for

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
    get_chaine_cherry,
    get_date_commit,
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
    supprimer_branche,
    supprimer_branche_recuperation,
    supprimer_worktree,
)
from resumes_info import (
    collect_resumes_projet,
    lister_fichiers_resumes_hash,
    lister_fichiers_resumes_pushes,
    regrouper_resumes_par_branche,
)

PORT = 5057

app = Flask(__name__)
# Usage strictement local (pas d'exposition réseau) : une clé fixe par
# processus suffit, seule utilité ici est la signature des messages flash.
app.secret_key = os.urandom(24)


def _charger_projets():
    """Mémoïse le résultat dans `g` (durée d'une seule requête HTTP) : la
    barre latérale (issue #44) a besoin de la même liste de projets que la
    route en cours, et `collect_etat_projets()` déclenche un appel réseau
    vers BRIDGE_AGENT_DOC.md (voir `fetch_projets`) — sans ce cache, ce
    serait un deuxième appel réseau par page, le coût déjà corrigé une fois
    en page d'accueil (issue #17/#19) se répétant alors sur toutes les
    pages."""
    if not hasattr(g, "_projets_charges"):
        try:
            g._projets_charges = (collect_etat_projets(), None)
        except ErreurRecuperationProjets as exc:
            g._projets_charges = ([], str(exc))
    return g._projets_charges


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
    commit). Enrichit chaque diagnostic avec le sujet et la date réelle du
    commit (`get_date_commit`, jamais la date du fichier dans `Non_Lu/`, voir
    issue #48), pour affichage, sans redemander à l'appelant de le faire."""
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
        diagnostic["date"] = resume["date"] if resume else get_date_commit(repertoire, diagnostic["hash"])
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


@app.context_processor
def injecter_barre_laterale():
    """Barre latérale (issue #44) injectée dans tous les templates : liste
    des noms de projets, plus le nom du projet actuellement affiché (déduit
    de `nom_projet` dans l'URL courante, absent sur les pages qui n'en ont
    pas comme l'accueil) pour le mettre en évidence. Réutilise
    `_charger_projets()`, déjà mémoïsé par requête (voir plus haut) : aucun
    appel réseau supplémentaire par page."""
    projets, _erreur = _charger_projets()
    return {
        "projets_sidebar": [projet["nom"] for projet in projets],
        "nom_projet_actif": (request.view_args or {}).get("nom_projet"),
    }


@app.route("/projet/<nom_projet>/rapport/<hash_commit>")
def rapport_commit_route(nom_projet, hash_commit):
    """Rapport texte prêt à copier pour un commit que le diagnostic
    automatique ne peut pas trancher (typiquement cas F, issue #22) :
    rassemble hash/message/résumé déjà généré, sortie brute de `git cherry`,
    branches locales/distantes le contenant, et le contexte déjà disponible
    (branche cible configurée, autres commits orphelins en attente) — pour
    coller le tout dans une conversation Claude Chat dédiée au projet.
    Route en lecture seule (GET), aucune action git déclenchée.
    `nom_branche` (query string, optionnel, issue #35) : nom de la branche
    d'origine si l'appel vient de `branche_route`, pour que le bouton
    « Précédent » y revienne plutôt qu'à la page projet — absent pour un
    commit orphelin, qui n'a pas de branche d'origine."""
    nom_branche = request.args.get("nom_branche") or None
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
    return render_template(
        "rapport.html", projet=projet, hash_commit=hash_commit, rapport=rapport,
        nom_branche=nom_branche,
    )


@app.route("/projet/<nom_projet>/comparer/<hash_commit>")
def comparer_commit_route(nom_projet, hash_commit):
    """Bouton « Comparer » (issue #30) pour un commit orphelin diagnostiqué
    doublon (cas B) : retrouve le commit exact de la branche cible dont le
    contenu correspond (empreinte de patch `git patch-id`, voir
    `comparer_commit_doublon`), et affiche le diff entre les deux — pour une
    vérification humaine directe, sans deviner de candidat ni lancer de
    commande manuelle. Route en lecture seule (GET), aucune action git
    déclenchée.
    `nom_branche` (query string, optionnel, issue #35) : voir
    `rapport_commit_route` — même logique de retour vers `branche_route`."""
    nom_branche = request.args.get("nom_branche") or None
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    repertoire = projet["repertoire"]
    branche_cible = projet["branche_cible_comparaison"]
    branche_cible_affichage = (
        " ou ".join(branche_cible) if isinstance(branche_cible, list) else branche_cible
    )
    sujet = get_sujet_commit(repertoire, hash_commit)
    comparaison = comparer_commit_doublon(repertoire, branche_cible, hash_commit)

    return render_template(
        "comparer.html", projet=projet, hash_commit=hash_commit, sujet=sujet,
        branche_cible=branche_cible, branche_cible_affichage=branche_cible_affichage,
        comparaison=comparaison, nom_branche=nom_branche,
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


@app.route("/projet/<nom_projet>/orphelins/securiser-tous", methods=["POST"])
def securiser_tous_orphelins_route(nom_projet):
    """Sécurise en un seul geste tous les commits orphelins affichés pour ce
    projet (issue #34), en appliquant `securiser_commit_orphelin` (issue #23)
    à chacun — même action défensive pure que le bouton individuel, mais sans
    répéter la confirmation commit par commit : contrairement à un merge, il
    n'y a jamais de cas où il faudrait choisir de ne pas sécuriser. Rapporte
    le résultat par commit (succès / déjà sécurisé / échec), comme le fait
    déjà `nettoyer_tous_les_projets_route` (issue #17) pour son propre
    rapport multi-éléments."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_orphelins = regrouper_resumes_par_branche(resumes, projet["repertoire"]).get(None, [])
    hashes_orphelins = [r["hash"] for r in resumes_orphelins]
    if not hashes_orphelins:
        flash("ℹ️ Aucun commit orphelin à sécuriser.", "succes")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    nb_crees, nb_deja_securises, echecs = 0, 0, []
    for hash_commit in hashes_orphelins:
        resultat = securiser_commit_orphelin(projet["repertoire"], hash_commit)
        if resultat["deja_securise"]:
            nb_deja_securises += 1
        elif resultat["ok"]:
            nb_crees += 1
        else:
            echecs.append(f"{hash_commit} ({resultat['erreur']})")

    if echecs:
        flash(
            f"⚠️ {nb_crees} sécurisé(s), {nb_deja_securises} déjà sécurisé(s) — "
            f"échec sur {len(echecs)} commit(s) : " + ", ".join(echecs),
            "erreur",
        )
    else:
        flash(
            f"✅ {nb_crees} commit(s) orphelin(s) sécurisé(s) ({nb_deja_securises} déjà sécurisé(s)).",
            "succes",
        )
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
    cible_merge_configuree = projet["branche_cible_comparaison"]
    branches = get_branches_locales(projet["repertoire"], cible_merge_configuree)

    # Issue #52 : un projet à plusieurs cibles configurées (ex. `scrabble`,
    # `master` ou `feature/moteur-strategique`) n'a pas de cible évidente à
    # calculer automatiquement — merger vers l'une ou l'autre n'a pas le même
    # sens selon le contenu de la branche. On expose donc la liste des
    # cibles candidates au template (`cibles_merge`, toujours une liste,
    # même à une seule entrée pour garder un seul chemin de rendu), à charge
    # d'Alain de choisir explicitement via le sélecteur du panneau d'actions
    # avant de merger — comportement inchangé pour un projet à une seule
    # cible (`cibles_merge` réduite à cette unique entrée).
    cibles_merge = (
        cible_merge_configuree if isinstance(cible_merge_configuree, list) else [cible_merge_configuree]
    )
    projet["cibles_merge"] = cibles_merge

    def _commande_merge(cible, nom_branche):
        if cible == projet["branche_principale"]:
            return f"git -C {projet['repertoire']} merge {nom_branche}"
        return (
            f"git -C {projet['repertoire']} checkout {cible} && "
            f"git merge {nom_branche} && git checkout {projet['branche_principale']}"
        )

    for branche in branches:
        branche["nb_resumes"] = len(resumes_par_branche.get(branche["nom"], []))
        branche["est_principale"] = branche["nom"] == projet["branche_principale"]
        branche["commande_push"] = f"git -C {projet['repertoire']} push {remote} {branche['nom']}"

        branche["peut_merger"] = branche["nom"] not in cibles_merge

        if len(cibles_merge) == 1:
            branche_cible_merge = cibles_merge[0]
            branche["ne_contient_que_doublons"] = branche["peut_merger"] and get_diagnostic_doublons_branche(
                projet["repertoire"], branche_cible_merge, branche["nom"]
            )
            if branche["ne_contient_que_doublons"]:
                branche["peut_merger"] = False
            branche["commande_merge"] = (
                _commande_merge(branche_cible_merge, branche["nom"]) if branche["peut_merger"] else None
            )
            branche["commandes_merge"] = None
        else:
            # Plusieurs cibles configurées : aucun diagnostic de doublons
            # automatique (même parti pris que le cas M du diagnostic des
            # commits orphelins, issue #46/#50 — pas de `git cherry` contre
            # une cible qui n'a pas encore été choisie), aucune commande par
            # défaut. Une commande est précalculée par cible candidate ;
            # `merger_branches_route` n'utilisera que celle correspondant à
            # la cible choisie explicitement dans le formulaire.
            branche["ne_contient_que_doublons"] = False
            branche["commande_merge"] = None
            branche["commandes_merge"] = (
                {cible: _commande_merge(cible, branche["nom"]) for cible in cibles_merge}
                if branche["peut_merger"] else None
            )

        # Une branche fusionnée reste supprimable même sans worktree associé
        # (retiré manuellement entre-temps) : `git worktree remove` n'a alors
        # plus rien à retirer, donc bascule sur `git branch -D` directement
        # (issue #43) — même bouton, seule la commande sous-jacente diffère.
        branche["peut_supprimer"] = branche["mergee"] and not branche["est_principale"]
        branche["commande_suppression"] = (
            f"git -C {projet['repertoire']} worktree remove {branche['chemin_worktree']}"
            if branche["peut_supprimer"] and branche["a_un_worktree"]
            else f"git -C {projet['repertoire']} branch -D {branche['nom']}"
            if branche["peut_supprimer"]
            else None
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
        try:
            resultat = pousser_branche(projet["repertoire"], nom)
        except subprocess.TimeoutExpired:
            flash(
                f"⚠️ Le push de « {nom} » a dépassé le délai, mais a pu se terminer "
                "entre-temps — vérifiez manuellement si besoin.",
                "erreur",
            )
            continue
        except Exception as exc:
            flash(f"❌ Erreur inattendue lors du push de « {nom} » : {exc}", "erreur")
            continue
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
    individuellement (issue #12).

    Projet à plusieurs cibles configurées (issue #52) : aucune cible n'est
    devinée. Le formulaire doit alors fournir `cible_merge` (sélecteur du
    panneau d'actions, voir `projet.html`), validé contre la liste des
    cibles candidates — sans ce choix explicite, l'action est refusée plutôt
    que de deviner une cible, un merge étant une action qui modifie
    réellement le dépôt."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    cible_configuree = projet["branche_cible_comparaison"]
    if isinstance(cible_configuree, list):
        cible_choisie = request.form.get("cible_merge")
        if not cible_choisie or cible_choisie not in cible_configuree:
            flash(
                f"❌ Plusieurs cibles sont configurées pour « {nom_projet} » "
                f"({', '.join(cible_configuree)}) — choisissez explicitement la "
                "cible de fusion avant de merger.",
                "erreur",
            )
            return redirect(url_for("projet_route", nom_projet=nom_projet))
        branche_cible = cible_choisie
    else:
        branche_cible = cible_configuree

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
        try:
            resultat = fusionner_worktree(projet["repertoire"], branche_cible, nom)
        except subprocess.TimeoutExpired:
            flash(
                f"⚠️ La fusion de « {nom} » a dépassé le délai, mais a pu se terminer "
                "entre-temps — vérifiez manuellement si besoin.",
                "erreur",
            )
            continue
        except Exception as exc:
            flash(f"❌ Erreur inattendue lors de la fusion de « {nom} » : {exc}", "erreur")
            continue
        if resultat["ok"]:
            flash(f"✅ « {nom} » fusionnée dans « {branche_cible} » — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec de la fusion de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/supprimer", methods=["POST"])
def supprimer_worktrees_route(nom_projet):
    """Supprime chaque branche sélectionnée (case à cocher, niveau 2),
    seulement si son merge est confirmé — même garde-fou qu'avant (issue
    précédente), rattaché à la sélection plutôt qu'à l'affichage par
    worktree. Si la branche a encore un worktree, le retire (`git worktree
    remove`) ; sinon (worktree déjà retiré manuellement, ne laissant que la
    branche), supprime directement la branche (`git branch -D`) — même
    bouton, même garde-fou `mergee`, seule la commande diffère (issue #43)."""
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
        if not branche["mergee"]:
            flash(
                f"❌ Suppression de « {nom} » refusée : branche pas confirmée "
                f"fusionnée dans « {branche_cible} ».",
                "erreur",
            )
            continue
        if branche["a_un_worktree"]:
            resultat = supprimer_worktree(projet["repertoire"], branche["chemin_worktree"])
            libelle = f"Worktree de « {nom} » supprimé"
        else:
            resultat = supprimer_branche(projet["repertoire"], nom)
            libelle = f"Branche « {nom} » supprimée"
        if resultat["ok"]:
            flash(f"✅ {libelle} — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec de la suppression de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/supprimer-branche-recuperation", methods=["POST"])
def supprimer_branches_recuperation_route(nom_projet):
    """Supprime définitivement (`git branch -D`) chaque branche de
    récupération sélectionnée (case à cocher, niveau 2), ainsi que les
    fichiers Non_Lu/ associés à **toute la chaîne de commits qu'elle
    protège** — pas seulement le hash nommé dans la branche (issue #40).

    Une branche `recuperation-<hash>` créée sur un commit qui a lui-même des
    ancêtres non fusionnés protège toute cette chaîne (comportement normal
    de git : un pointeur de branche protège tout ce qui est en dessous), le
    même regroupement que le cas C du diagnostic (voir
    `diagnostiquer_commits_orphelins`). On réutilise donc `get_chaine_cherry`
    (même brique) pour lister ces ancêtres avant de supprimer la branche, et
    on nettoie le fichier Non_Lu/ de chacun — sans quoi un ancêtre protégé
    uniquement par cette branche redeviendrait orphelin et non protégé après
    coup (issue #40, plus grave que #31 : là où #31 ne laissait derrière que
    des doublons, ici l'ancêtre peut être du vrai travail non intégré, cas A).

    Ces branches (issue #23) n'ont pas de worktree, donc distinct de
    `supprimer_worktrees_route`. Revérifiée ici indépendamment de la case
    cochée côté template : seule la convention de nom `recuperation-<hash>`
    (issue #26) autorise la suppression, jamais le badge de diagnostic
    (issue #29).

    Les deux suppressions (branche + résumés) sont faites dans le même geste
    car aucun cas n'a de sens à supprimer l'une sans l'autre : sans elles,
    le(s) commit(s) redevien(nen)t orphelin(s) non sécurisé(s) juste après
    (issue #31)."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    branches = _branches_par_nom(projet)
    branche_cible = projet["branche_cible_comparaison"]
    for nom in noms_branches:
        if nom not in branches:
            flash(f"❌ Branche « {nom} » introuvable.", "erreur")
            continue
        hash_commit = hash_depuis_branche_recuperation(nom)
        if hash_commit is None:
            flash(f"❌ « {nom} » ne suit pas la convention recuperation-<hash>, suppression refusée.", "erreur")
            continue

        hashes_a_nettoyer = {hash_commit}
        if branche_cible:
            chaine = get_chaine_cherry(projet["repertoire"], branche_cible, hash_commit)
            if chaine:
                hashes_a_nettoyer.update(maillon["hash"] for maillon in chaine)

        resultat = supprimer_branche_recuperation(projet["repertoire"], nom)
        if not resultat["ok"]:
            flash(f"❌ Échec de la suppression de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
            continue

        fichiers = set()
        for h in hashes_a_nettoyer:
            fichiers.update(lister_fichiers_resumes_hash(projet["dossier_relecture"], h))
        nb_supprimes, nb_echecs = _supprimer_fichiers(fichiers)
        detail_chaine = f" (chaîne de {len(hashes_a_nettoyer)} commits)" if len(hashes_a_nettoyer) > 1 else ""
        if nb_echecs:
            flash(
                f"⚠️ Branche « {nom} » supprimée ({resultat['commande']}), mais {nb_echecs} "
                f"fichier(s) Non_Lu/ associé(s) à « {hash_commit} »{detail_chaine} n'ont pas pu être supprimés.",
                "erreur",
            )
        elif nb_supprimes:
            flash(
                f"✅ Branche « {nom} » supprimée — {resultat['commande']} "
                f"({nb_supprimes} fichier(s) Non_Lu/ associé(s) supprimé(s){detail_chaine})",
                "succes",
            )
        else:
            flash(f"✅ Branche « {nom} » supprimée — {resultat['commande']}", "succes")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/comparer-selection", methods=["POST"])
def comparer_selection_route(nom_projet):
    """Vérification groupée (issue #47) pour une sélection de branches de
    récupération (case à cocher, niveau 2, même sélection que
    `supprimer_branches_recuperation_route`) : relance `comparer_commit_doublon`
    (issue #30, aucune nouvelle logique de comparaison) pour chacune, et
    affiche un résultat par ligne — diff vide (doublon confirmé), diff non
    vide (à vérifier manuellement, lien vers le détail), ou commit vide
    (rien à comparer, issue #45). Route en lecture seule malgré la méthode
    POST, nécessaire pour transmettre la sélection (liste de noms de
    branches) — ne déclenche aucune commande git de modification.

    Une branche qui ne suit pas la convention `recuperation-<hash>` est
    ignorée avec un message flash, même garde-fou que pour la suppression
    groupée (issue #29)."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    repertoire = projet["repertoire"]
    branche_cible = projet["branche_cible_comparaison"]
    branche_cible_affichage = (
        " ou ".join(branche_cible) if isinstance(branche_cible, list) else branche_cible
    )

    resultats = []
    ignorees = []
    for nom in noms_branches:
        hash_commit = hash_depuis_branche_recuperation(nom)
        if hash_commit is None:
            ignorees.append(nom)
            continue
        comparaison = comparer_commit_doublon(repertoire, branche_cible, hash_commit)
        if comparaison.get("vide"):
            statut = "vide"
        elif comparaison["trouve"] and not comparaison["diff"]:
            statut = "doublon_confirme"
        else:
            statut = "a_verifier"
        resultats.append({
            "nom_branche": nom,
            "hash": hash_commit,
            "sujet": get_sujet_commit(repertoire, hash_commit),
            "comparaison": comparaison,
            "statut": statut,
        })

    if ignorees:
        flash(
            "⚠️ Ignorée(s) car ne suit/suivent pas la convention recuperation-<hash> : "
            + ", ".join(ignorees),
            "erreur",
        )
    if not resultats:
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    return render_template(
        "comparer_selection.html", projet=projet, resultats=resultats,
        branche_cible_affichage=branche_cible_affichage,
    )


if __name__ == "__main__":
    import threading
    import webbrowser
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)
