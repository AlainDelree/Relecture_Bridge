#!/usr/bin/env python3
"""
Programme web indépendant de relecture_bridge : affiche, pour chaque projet
Bridge_Agent, ses worktrees actifs et ses commits locaux en attente de push.

Distinct de new_issue.py (dépôt bridge_agent, port et code séparés) — ce
programme est la maison des futures actions de relecture (merge/suppression
de worktree, résumés) ; la lecture git est réimplémentée dans git_info.py,
sans importer le code de bridge_agent (hors périmètre relecture_bridge).

Authentification (issue #92, voir auth.py) : mot de passe optionnel selon le
mode de lancement — voir RELECTURE_WEB_DOC.md.

    python3 relecture_web/app.py             # 127.0.0.1, sans mot de passe
    python3 relecture_web/app.py --lan       # 0.0.0.0, HTTP, sans mot de passe
    python3 relecture_web/app.py --externe   # 0.0.0.0, HTTPS, mot de passe obligatoire
    python3 relecture_web/app.py --set-password
"""

import os
import subprocess
from datetime import timedelta
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for

import auth
from git_info import (
    ErreurRecuperationProjets,
    ajouter_motif_gitignore,
    classifier_ligne_gitignore,
    collect_etat_projets,
    commande_affichee,
    comparer_commit_doublon,
    commit_est_securise,
    commit_existe,
    committer_gitignore,
    diagnostiquer_commits_orphelins,
    ecrire_lignes_gitignore,
    est_projet_distant,
    extraire_numero_issue,
    finaliser_commit_merge,
    fusionner_worktree,
    get_branches_contenant,
    get_branches_distantes_contenant,
    get_branches_locales,
    get_chaine_cherry,
    get_date_commit,
    get_diagnostic_doublons_branche,
    get_fichiers_en_conflit,
    get_fichiers_non_suivis,
    get_fichiers_resolus_merge,
    get_fichiers_suivis_correspondant,
    get_hashes_commits_non_fusionnes,
    get_issue_deja_referencee,
    get_merge_en_cours,
    get_modifications_non_committees,
    get_nombre_commits_non_fusionnes,
    get_rapport_cherry_brut,
    get_remote_defaut,
    get_sujet_commit,
    gitignore_a_des_modifications_non_committees,
    hash_depuis_branche_recuperation,
    lire_conflits_fichier,
    lire_lignes_gitignore,
    lire_verrous_actifs,
    nom_branche_recuperation,
    pousser_branche,
    purger_reflog_et_gc,
    resoudre_bloc_conflit,
    resoudre_tous_blocs_conflit,
    retirer_du_suivi,
    retraiter_fichier_conflit,
    revert_commit,
    securiser_commit_orphelin,
    supprimer_branche,
    supprimer_branche_recuperation,
    supprimer_worktree,
    verifier_finalisation_merge_apres_timeout,
    verifier_merge_apres_timeout,
    verifier_push_apres_timeout,
    worktree_ccl_actif,
)
from resumes_info import (
    collect_resumes_projet,
    lister_fichiers_resumes_hash,
    lister_fichiers_resumes_pushes,
    regrouper_resumes_par_branche,
)

PORT = 5057

app = Flask(__name__)
# Clé persistée (issue #92, auth.py) — jamais régénérée à chaque lancement,
# sinon une session survivante serait invalidée à chaque redémarrage.
app.secret_key = auth.charger_ou_creer_cle_secrete()
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
# MDP_EXIGE n'est vrai qu'en mode --externe (voir bloc __main__ en bas de ce
# fichier) — False par défaut pour que les imports (tests, etc.) ne se
# retrouvent jamais avec une authentification exigée sans configuration
# explicite.
app.config["MDP_EXIGE"] = False


def login_requis(f):
    """Décorateur de connexion (issue #92, même principe que côté
    bridge_agent) appliqué à toutes les routes. Ne bloque rien tant que
    `MDP_EXIGE` est faux (modes par défaut et --lan, comportement local
    préservé) — seul le mode --externe l'active."""
    @wraps(f)
    def enveloppe(*args, **kwargs):
        if not app.config.get("MDP_EXIGE"):
            return f(*args, **kwargs)
        if not session.get("authentifie"):
            return redirect(url_for("connexion_route", suivant=request.path))
        return f(*args, **kwargs)
    return enveloppe


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
    if projet and projet["statut"] == "injoignable":
        return None, "🔌 PC fixe éteint ou injoignable — projet indisponible pour le moment."
    if not projet or projet["statut"] != "ok":
        return None, f"❌ Projet « {nom_projet} » introuvable ou inaccessible."
    return projet, None


def _branches_par_nom(projet):
    return {
        branche["nom"]: branche
        for branche in get_branches_locales(projet["repertoire"], projet["branche_cible_comparaison"])
    }


def _verrous_actifs_projets(projets):
    """Verrous Bridge_Agent actifs (issue #88, voir `lire_verrous_actifs`) —
    localise le répertoire du projet "bridge_agent" dans `projets` (même
    tableau BRIDGE_AGENT_DOC.md que `collect_etat_projets`, réutilisé ici
    plutôt que retélécharger la doc), puis lit ses `logs/verrous/*.lock`.
    Dégrade proprement à liste vide si ce projet est absent du tableau."""
    repertoire_bridge_agent = next(
        (p["repertoire"] for p in projets if p["nom"] == "bridge_agent"), None
    )
    return lire_verrous_actifs(repertoire_bridge_agent)


def _refus_modification_gitignore(projet):
    """Raisons de refus communes aux trois actions du panneau .gitignore
    (issue #98) — projet distant (lecture/écriture de fichier hors
    périmètre git, #94), fusion en cours (MERGE_HEAD), badge « CCL travaille
    ici » actif sur le worktree principal du projet, ou .gitignore déjà
    modifié avant toute action de ce panneau (modification d'origine
    extérieure à ne jamais embarquer silencieusement dans le commit
    automatique). Retourne un message de refus (str), ou None si l'action
    peut continuer."""
    repertoire = projet["repertoire"]
    if est_projet_distant(repertoire):
        return "❌ Projet distant (PC fixe) — édition du .gitignore indisponible pour ce projet."
    if get_merge_en_cours(repertoire):
        return "❌ Fusion en cours sur ce projet — édition du .gitignore refusée tant qu'elle n'est pas finalisée."
    projets, _erreur = _charger_projets()
    verrous_actifs = _verrous_actifs_projets(projets)
    if worktree_ccl_actif(repertoire, verrous_actifs):
        return "❌ Un verrou Bridge_Agent actif signale CCL en train de travailler ici — édition du .gitignore refusée."
    if gitignore_a_des_modifications_non_committees(repertoire):
        return (
            "❌ Le .gitignore contient déjà des modifications non committées d'origine extérieure "
            "— vérifiez-les manuellement avant toute action depuis ce panneau."
        )
    return None


def _construire_panneau_gitignore(projet):
    """Données du panneau repliable « .gitignore » de la page projet (issue
    #98) — accède directement au filesystem local, donc n'a de sens que
    pour un projet local, ou si aucun autre garde-fou n'empêche déjà toute
    modification (voir `_refus_modification_gitignore` : projet distant,
    fusion en cours, badge « CCL travaille ici », .gitignore déjà modifié
    d'origine extérieure) — dans ces cas, le panneau affiche juste le motif
    du refus plutôt que de lire quoi que ce soit, même en lecture (évite un
    accès filesystem qui n'a pas de sens pour un projet distant, #94).

    Pour chaque ligne « motif » affichée, vérifie en plus si des fichiers
    déjà suivis y correspondent (voir `get_fichiers_suivis_correspondant`)
    — même piège git signalé après un ajout, ici affiché en permanence
    pour rester visible même après un rafraîchissement de la page."""
    projet["gitignore_refus"] = _refus_modification_gitignore(projet)
    if projet["gitignore_refus"]:
        projet["gitignore_lignes"] = None
        projet["gitignore_non_suivis"] = []
        return

    repertoire = projet["repertoire"]
    lignes_brutes = lire_lignes_gitignore(repertoire)
    if lignes_brutes is None:
        projet["gitignore_lignes"] = None
    else:
        lignes = []
        for index, ligne_brute in enumerate(lignes_brutes):
            type_ligne = classifier_ligne_gitignore(ligne_brute)
            texte = ligne_brute.rstrip("\r\n")
            fichiers_suivis = (
                get_fichiers_suivis_correspondant(repertoire, texte) if type_ligne == "motif" else []
            )
            lignes.append({
                "index": index,
                "type": type_ligne,
                "texte": texte,
                "commande_retrait": (
                    commande_affichee(repertoire, f"git -C {repertoire} commit -m \"chore: .gitignore — retire {texte}\" -- .gitignore")
                    if type_ligne == "motif" else None
                ),
                "fichiers_suivis": [
                    {
                        "chemin": chemin,
                        "commande": commande_affichee(repertoire, f"git -C {repertoire} rm --cached -- {chemin}"),
                    }
                    for chemin in fichiers_suivis
                ],
            })
        projet["gitignore_lignes"] = lignes
    projet["gitignore_non_suivis"] = get_fichiers_non_suivis(repertoire)


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
        diagnostic["commande_securisation"] = commande_affichee(
            repertoire,
            f"git -C {repertoire} branch {diagnostic['nom_branche_recuperation']} {diagnostic['hash']}",
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


@app.route("/connexion", methods=["GET", "POST"])
def connexion_route():
    """Page de connexion (issue #92) — n'existe fonctionnellement qu'en mode
    --externe (`MDP_EXIGE`) : dans les autres modes, redirige directement
    vers `suivant` sans rien demander, pour ne jamais bloquer l'usage local
    ou LAN existant."""
    suivant = request.values.get("suivant") or url_for("index")
    if not app.config.get("MDP_EXIGE"):
        return redirect(suivant)

    if request.method == "POST":
        if auth.verifier_mot_de_passe(request.form.get("mot_de_passe", "")):
            session.clear()
            session["authentifie"] = True
            session.permanent = True
            return redirect(suivant)
        flash("❌ Mot de passe incorrect.", "erreur")

    return render_template("connexion.html", suivant=suivant)


@app.route("/deconnexion", methods=["POST"])
def deconnexion_route():
    session.clear()
    return redirect(url_for("connexion_route"))


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
        "projets_sidebar": [
            {"nom": projet["nom"], "couleur": projet.get("couleur"), "couleur_texte": projet.get("couleur_texte")}
            for projet in projets
        ],
        "nom_projet_actif": (request.view_args or {}).get("nom_projet"),
    }


@app.route("/projet/<nom_projet>/rapport/<hash_commit>")
@login_requis
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
@login_requis
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


@app.route("/projet/<nom_projet>/conflit/<path:chemin_relatif>")
@login_requis
def conflit_fichier_route(nom_projet, chemin_relatif):
    """Détail d'un fichier en conflit de fusion non résolue (issue #55) :
    localise chaque bloc entre `<<<<<<<`/`=======`/`>>>>>>>` et l'affiche en
    lecture seule, les deux versions distinguées visuellement (contrairement
    à un `<textarea>`, qui ne supporte pas le texte en couleur), avec le
    texte hors conflit autour pour donner le contexte. Route en lecture
    seule (GET), aucune commande git de modification — la résolution
    elle-même se fait via `traiter_bloc_conflit_route` (issue #56), un
    `<textarea>` éditable par bloc affiché juste à côté de cette lecture
    seule.

    `chemin_relatif` n'est accepté que s'il figure dans la liste actuelle
    des fichiers en conflit du projet, recalculée ici (pas depuis le cache
    mémoïsé par requête) : jamais construit à l'aveugle à partir du seul
    paramètre d'URL, pour ne jamais lire un fichier hors de ce périmètre
    précis."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    fichiers_conflit = get_fichiers_en_conflit(projet["repertoire"])
    fichier = next((f for f in fichiers_conflit if f["chemin"] == chemin_relatif), None)
    if not fichier:
        flash(
            f"❌ « {chemin_relatif} » n'est pas (ou plus) un fichier en conflit pour « {nom_projet} ».",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    lecture = lire_conflits_fichier(projet["repertoire"], chemin_relatif)
    return render_template(
        "conflit.html", projet=projet, chemin_relatif=chemin_relatif,
        code=fichier["code"], lecture=lecture,
    )


@app.route("/projet/<nom_projet>/conflit/<path:chemin_relatif>/traiter", methods=["POST"])
@login_requis
def traiter_bloc_conflit_route(nom_projet, chemin_relatif):
    """Applique le texte final composé par Alain pour un bloc de conflit
    précis (issue #56) : remplace ce bloc (marqueurs compris) par le
    contenu du `<textarea>` soumis, dans le fichier réel (voir
    `resoudre_bloc_conflit`). Si le fichier ne contient plus aucun bloc de
    conflit après coup, `git add` a déjà été lancé dessus par
    `resoudre_bloc_conflit` — le commit et le push restent des gestes
    manuels d'Alain. Revalide que `chemin_relatif` est toujours un fichier
    en conflit du projet avant d'écrire, comme la route de lecture voisine.

    Redirige vers la même page de conflit s'il reste des blocs (elle les
    recalcule à l'affichage, donc le bloc suivant apparaît naturellement en
    premier), ou vers la page du projet avec un message clair si le fichier
    vient d'être entièrement résolu."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    fichiers_conflit = get_fichiers_en_conflit(projet["repertoire"])
    fichier = next((f for f in fichiers_conflit if f["chemin"] == chemin_relatif), None)
    if not fichier:
        flash(
            f"❌ « {chemin_relatif} » n'est pas (ou plus) un fichier en conflit pour « {nom_projet} ».",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    try:
        index_bloc = int(request.form.get("index_bloc", ""))
    except ValueError:
        flash("❌ Numéro de bloc invalide.", "erreur")
        return redirect(url_for("conflit_fichier_route", nom_projet=nom_projet, chemin_relatif=chemin_relatif))

    texte_final = request.form.get("texte_final", "")

    resultat = resoudre_bloc_conflit(projet["repertoire"], chemin_relatif, index_bloc, texte_final)
    if not resultat["ok"]:
        flash(
            f"❌ Échec du traitement du bloc n°{index_bloc} de « {chemin_relatif} » : {resultat['erreur']}",
            "erreur",
        )
        return redirect(url_for("conflit_fichier_route", nom_projet=nom_projet, chemin_relatif=chemin_relatif))

    if resultat["fichier_resolu"]:
        git_add = resultat["git_add"]
        if git_add and git_add["ok"]:
            flash(
                f"✅ « {chemin_relatif} » entièrement résolu (dernier bloc traité) — "
                "`git add` effectué, prêt pour le commit (manuel).",
                "succes",
            )
        elif git_add:
            flash(
                f"⚠️ « {chemin_relatif} » entièrement résolu (plus aucun bloc de conflit), "
                f"mais `git add` a échoué : {git_add['erreur']}",
                "erreur",
            )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    flash(
        f"✅ Bloc n°{index_bloc} de « {chemin_relatif} » traité — "
        f"{resultat['nb_blocs_restants']} bloc(s) restant(s).",
        "succes",
    )
    return redirect(url_for("conflit_fichier_route", nom_projet=nom_projet, chemin_relatif=chemin_relatif))


@app.route("/projet/<nom_projet>/conflit/<path:chemin_relatif>/traiter-tous", methods=["POST"])
@login_requis
def traiter_tous_blocs_conflit_route(nom_projet, chemin_relatif):
    """Variante « tout ou rien » de `traiter_bloc_conflit_route` (issue #69,
    bouton « Traiter tous les blocs ») : applique en une seule opération
    chaque bloc de conflit de `chemin_relatif` au texte soumis pour lui,
    plutôt que de recliquer « Traiter ce bloc » un par un (qui recharge la
    page à chaque fois). Revalide `chemin_relatif` comme fichier en conflit
    du projet, comme la route de lecture et la route bloc par bloc voisines.

    `nb_blocs` et `empreinte` (formulaire, construits côté navigateur à
    partir de ce qui a été affiché sur la page Conflit) sont transmis tels
    quels à `resoudre_tous_blocs_conflit`, qui refuse tout le traitement si
    le fichier a changé depuis l'affichage — jamais d'écriture partielle."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    fichiers_conflit = get_fichiers_en_conflit(projet["repertoire"])
    fichier = next((f for f in fichiers_conflit if f["chemin"] == chemin_relatif), None)
    if not fichier:
        flash(
            f"❌ « {chemin_relatif} » n'est pas (ou plus) un fichier en conflit pour « {nom_projet} ».",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    try:
        nb_blocs = int(request.form.get("nb_blocs", ""))
    except ValueError:
        flash("❌ Nombre de blocs invalide.", "erreur")
        return redirect(url_for("conflit_fichier_route", nom_projet=nom_projet, chemin_relatif=chemin_relatif))

    empreinte_attendue = request.form.get("empreinte", "")
    textes_finaux = [request.form.get(f"texte_final_{i}", "") for i in range(nb_blocs)]

    resultat = resoudre_tous_blocs_conflit(projet["repertoire"], chemin_relatif, textes_finaux, empreinte_attendue)
    if not resultat["ok"]:
        flash(
            f"❌ Échec du traitement groupé de « {chemin_relatif} » : {resultat['erreur']}",
            "erreur",
        )
        return redirect(url_for("conflit_fichier_route", nom_projet=nom_projet, chemin_relatif=chemin_relatif))

    git_add = resultat["git_add"]
    if git_add and git_add["ok"]:
        flash(
            f"✅ « {chemin_relatif} » entièrement résolu — {nb_blocs} bloc(s) traité(s) en une seule "
            "opération, `git add` effectué, prêt pour le commit (manuel).",
            "succes",
        )
    else:
        flash(
            f"⚠️ « {chemin_relatif} » entièrement résolu ({nb_blocs} bloc(s)), mais `git add` a échoué : "
            f"{git_add['erreur']}",
            "erreur",
        )
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/finaliser-merge", methods=["POST"])
@login_requis
def finaliser_merge_route(nom_projet):
    """Finalise le commit de merge une fois tous les conflits résolus (issue
    #61) — jusqu'ici une étape manuelle en terminal (`git commit` sans `-m`,
    pour accepter le message déjà préparé par git) malgré le fait que chaque
    fichier résolu via `traiter_bloc_conflit_route` fasse déjà le `git add`
    automatiquement, ce qui cassait le flux : commencer la résolution dans
    `relecture_web`, puis devoir basculer en terminal pour la conclure.

    Revalide à partir de l'état git actuel (pas de la seule page déjà
    affichée, qui a pu être ouverte avant la résolution du dernier fichier)
    qu'un merge est bien en cours et qu'aucun fichier ne reste en conflit,
    avant d'appeler `finaliser_commit_merge` — jamais de commit partiel,
    même sur un formulaire soumis depuis une page obsolète."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    if not get_merge_en_cours(projet["repertoire"]):
        flash(f"❌ « {nom_projet} » n'est pas en état de fusion non finalisée — rien à commiter.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    fichiers_conflit = get_fichiers_en_conflit(projet["repertoire"])
    if fichiers_conflit:
        flash(
            f"❌ {len(fichiers_conflit)} fichier(s) encore en conflit pour « {nom_projet} » — "
            "résolvez-les tous avant de finaliser le merge.",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    try:
        resultat = finaliser_commit_merge(projet["repertoire"])
    except subprocess.TimeoutExpired:
        verification = verifier_finalisation_merge_apres_timeout(projet["repertoire"])
        if verification["ok"]:
            flash(
                f"✅ La finalisation du merge de « {nom_projet} » a dépassé le délai affiché, mais la "
                "vérification automatique confirme qu'elle a bien abouti (plus de fusion en attente).",
                "succes",
            )
        else:
            flash(
                f"❌ La finalisation du merge de « {nom_projet} » a dépassé le délai et la vérification "
                "automatique confirme qu'elle n'a PAS abouti (fusion toujours en attente) — à relancer.",
                "erreur",
            )
        return redirect(url_for("projet_route", nom_projet=nom_projet))
    except Exception as exc:
        flash(f"❌ Erreur inattendue lors de la finalisation du merge de « {nom_projet} » : {exc}", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    if resultat["ok"]:
        flash(f"✅ Merge finalisé pour « {nom_projet} » — {resultat['commande']}", "succes")
    else:
        flash(
            f"❌ Échec de la finalisation du merge de « {nom_projet} » ({resultat['commande']}) : "
            f"{resultat['erreur']}",
            "erreur",
        )
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/conflit/<path:chemin_relatif>/retraiter", methods=["POST"])
@login_requis
def retraiter_fichier_conflit_route(nom_projet, chemin_relatif):
    """Remet un fichier déjà résolu pendant le merge en cours dans son état
    de conflit d'origine (issue #72) — corrige la limite documentée à tort
    par l'issue #71 : un `git add` de résolution n'est pas définitif tant
    que le merge n'est pas finalisé (voir `get_fichiers_resolus_merge` et
    `retraiter_fichier_conflit`).

    Revérifie à partir de l'état git actuel, jamais du seul paramètre
    d'URL : qu'un merge est bien en cours (même principe que
    `finaliser_merge_route`), et que `chemin_relatif` figure bien dans la
    liste actuelle des fichiers résolus renvoyée par git (même principe que
    `conflit_fichier_route` pour les fichiers en conflit)."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    if not get_merge_en_cours(projet["repertoire"]):
        flash(f"❌ « {nom_projet} » n'est pas en état de fusion non finalisée — rien à retraiter.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    fichiers_resolus = get_fichiers_resolus_merge(projet["repertoire"])
    if chemin_relatif not in fichiers_resolus:
        flash(
            f"❌ « {chemin_relatif} » n'est pas (ou plus) un fichier résolu de ce merge pour « {nom_projet} ».",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    resultat = retraiter_fichier_conflit(projet["repertoire"], chemin_relatif)
    if resultat["ok"]:
        flash(
            f"🔁 « {chemin_relatif} » remis en conflit ({nom_projet}) — les marqueurs recréés portent les "
            "libellés génériques « ours »/« theirs » (au lieu de HEAD et du nom de la branche entrante).",
            "succes",
        )
        # Amène directement sur la page Conflit du fichier remis en conflit
        # (issue #73), plutôt que sur la page projet qui obligeait à recliquer
        # dessus.
        return redirect(url_for("conflit_fichier_route", nom_projet=nom_projet, chemin_relatif=chemin_relatif))

    flash(
        f"❌ Échec du retraitement de « {chemin_relatif} » ({resultat['commande']}) : {resultat['erreur']}",
        "erreur",
    )
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/orphelin/<hash_commit>/securiser", methods=["POST"])
@login_requis
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
@login_requis
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
@login_requis
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
@login_requis
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
        projet["fichiers_conflit"] = []
        projet["fichiers_resolus_merge"] = []
        projet["merge_en_cours"] = False
        projet["peut_finaliser_merge"] = False
        projet["commande_finaliser_merge"] = None
        return render_template("projet.html", projet=projet, erreur=erreur)

    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_par_branche = regrouper_resumes_par_branche(resumes, projet["repertoire"])
    projet["diagnostics_orphelins"] = _diagnostiquer_orphelins(projet, resumes_par_branche.get(None, []))
    projet["fichiers_conflit"] = get_fichiers_en_conflit(projet["repertoire"])
    _construire_panneau_gitignore(projet)

    # Option « Purger réellement » du bouton Rejeter (issue #96) : commits
    # orphelins déjà connus du diagnostic ci-dessus, mais pas encore
    # sécurisés (donc réellement menacés par `purger_reflog_et_gc`, globale
    # au dépôt) — affichés dans l'avertissement de confirmation pour
    # qu'Alain sache ce qu'il perdrait EN PLUS du commit qu'il rejette.
    # `commande_purge_rejet` est la même pour tout le projet (pas par
    # branche, contrairement à `commande_rejet`), affichée telle quelle dans
    # la confirmation quand la case est cochée.
    projet["orphelins_non_securises_menaces"] = [
        d for d in projet["diagnostics_orphelins"] if not d["deja_securise"]
    ]
    projet["commande_purge_rejet"] = commande_affichee(
        projet["repertoire"],
        f"git -C {projet['repertoire']} reflog expire --expire=now --all && "
        f"git -C {projet['repertoire']} gc --prune=now",
    )

    # Bouton « Finaliser le merge » (issue #61) : proposé seulement quand un
    # merge est réellement en cours (MERGE_HEAD présent) ET qu'il ne reste
    # plus aucun fichier en conflit — jamais de tentative de commit partiel.
    projet["merge_en_cours"] = get_merge_en_cours(projet["repertoire"])
    projet["peut_finaliser_merge"] = projet["merge_en_cours"] and not projet["fichiers_conflit"]
    projet["commande_finaliser_merge"] = (
        commande_affichee(projet["repertoire"], f"git -C {projet['repertoire']} commit --no-edit")
        if projet["peut_finaliser_merge"] else None
    )

    # Bouton « Retraiter le fichier en conflit » (issue #72) : proposé pour
    # chaque fichier déjà résolu (git add fait) du merge en cours, que
    # d'autres fichiers restent en conflit ou non — corrige la limite
    # documentée à tort par l'issue #71 (voir get_fichiers_resolus_merge).
    projet["fichiers_resolus_merge"] = (
        get_fichiers_resolus_merge(projet["repertoire"]) if projet["merge_en_cours"] else []
    )

    remote = get_remote_defaut(projet["repertoire"])
    cible_merge_configuree = projet["branche_cible_comparaison"]
    branches = get_branches_locales(projet["repertoire"], cible_merge_configuree)

    # Badge « ⚠ CCL travaille ici » (issue #88) : un verrou Bridge_Agent actif
    # dont le `rep=` correspond au worktree d'une branche signale qu'une
    # tâche mode_write y travaille peut-être encore (reprise après
    # redémarrage, cf. l'incident #73/#609 côté Bridge_Agent) — simple signal
    # visuel avant toute action, voir `worktree_ccl_actif` plus bas.
    verrous_actifs = _verrous_actifs_projets(projets)

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
        branche["commande_push"] = commande_affichee(
            projet["repertoire"], f"git -C {projet['repertoire']} push {remote} {branche['nom']}"
        )
        branche["verrou_ccl_actif"] = worktree_ccl_actif(branche["chemin_worktree"], verrous_actifs)

        branche["peut_merger"] = branche["nom"] not in cibles_merge

        # Commandes brutes (sans préfixe ssh) gardées à part pour composer
        # l'aperçu combiné « Merger et supprimer » ci-dessous — un seul
        # préfixe ssh en tête de l'aperçu final pour un projet distant
        # (issue #94, voir `commande_affichee`), jamais un par segment
        # enchaîné par `&&` : la commande git est envoyée seule à chaque
        # étape (voir `_lancer_git_distant`), le `&&` n'existe que dans cet
        # aperçu, pas dans ce qui est réellement exécuté sur le PC fixe.
        if len(cibles_merge) == 1:
            branche_cible_merge = cibles_merge[0]
            branche["ne_contient_que_doublons"] = branche["peut_merger"] and get_diagnostic_doublons_branche(
                projet["repertoire"], branche_cible_merge, branche["nom"]
            )
            if branche["ne_contient_que_doublons"]:
                branche["peut_merger"] = False
            commande_merge_brute = (
                _commande_merge(branche_cible_merge, branche["nom"]) if branche["peut_merger"] else None
            )
            branche["commande_merge"] = (
                commande_affichee(projet["repertoire"], commande_merge_brute) if commande_merge_brute else None
            )
            branche["commandes_merge"] = None
            commandes_merge_brutes = None
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
            commandes_merge_brutes = (
                {cible: _commande_merge(cible, branche["nom"]) for cible in cibles_merge}
                if branche["peut_merger"] else None
            )
            branche["commandes_merge"] = (
                {
                    cible: commande_affichee(projet["repertoire"], commande)
                    for cible, commande in commandes_merge_brutes.items()
                }
                if commandes_merge_brutes else None
            )

        # Bouton combiné « Merger et supprimer » (issue #88) : mêmes
        # conditions d'éligibilité que le Merger seul (`peut_merger`),
        # PLUS le refus si le badge « CCL travaille ici » est actif pour
        # cette branche — contrairement au Merger seul, qui reste autorisé
        # avec ce badge (l'utilisateur peut savoir ce qu'il fait
        # délibérément, voir `merger_et_supprimer_route`). La commande de
        # suppression prévisualisée ici est calculée SANS passer par
        # `peut_supprimer` (qui exige `mergee`, forcément faux avant le
        # merge que ce bouton s'apprête justement à faire) : une fois la
        # fusion faite, la branche sera par construction fusionnée dans la
        # cible choisie, donc supprimable selon la même logique que
        # `commande_suppression` ci-dessous.
        branche["peut_merger_et_supprimer"] = branche["peut_merger"] and not branche["verrou_ccl_actif"]
        commande_suppression_apres_merge_brute = (
            f"git -C {projet['repertoire']} worktree remove {branche['chemin_worktree']}"
            f" && git -C {projet['repertoire']} branch -D {branche['nom']}"
            if branche["a_un_worktree"]
            else f"git -C {projet['repertoire']} branch -D {branche['nom']}"
        )
        if len(cibles_merge) == 1:
            branche["commande_merger_et_supprimer"] = (
                commande_affichee(
                    projet["repertoire"],
                    f"{commande_merge_brute} && {commande_suppression_apres_merge_brute}",
                )
                if branche["peut_merger_et_supprimer"] and commande_merge_brute else None
            )
            branche["commandes_merger_et_supprimer"] = None
        else:
            branche["commande_merger_et_supprimer"] = None
            branche["commandes_merger_et_supprimer"] = (
                {
                    cible: commande_affichee(
                        projet["repertoire"], f"{commande} && {commande_suppression_apres_merge_brute}"
                    )
                    for cible, commande in commandes_merge_brutes.items()
                }
                if branche["peut_merger_et_supprimer"] and commandes_merge_brutes else None
            )

        # Une branche fusionnée reste supprimable même sans worktree associé
        # (retiré manuellement entre-temps) : `git worktree remove` n'a alors
        # plus rien à retirer, donc bascule sur `git branch -D` directement
        # (issue #43) — même bouton. Si le worktree existe encore, les deux
        # commandes s'enchaînent dans le même clic (issue #54), d'où
        # l'aperçu combiné affiché avant confirmation.
        branche["peut_supprimer"] = branche["mergee"] and not branche["est_principale"]
        commande_suppression_brute = (
            f"git -C {projet['repertoire']} worktree remove {branche['chemin_worktree']}"
            f" && git -C {projet['repertoire']} branch -D {branche['nom']}"
            if branche["peut_supprimer"] and branche["a_un_worktree"]
            else f"git -C {projet['repertoire']} branch -D {branche['nom']}"
            if branche["peut_supprimer"]
            else None
        )
        branche["commande_suppression"] = (
            commande_affichee(projet["repertoire"], commande_suppression_brute)
            if commande_suppression_brute else None
        )

        # Bouton « Rejeter » (issue #95) : garde-fou strictement inverse de
        # « Supprimer la/les branche(s) fusionnée(s) » ci-dessus — cible
        # explicitement une branche PAS confirmée fusionnée (sinon
        # « Supprimer » est le bon bouton), jamais la branche principale.
        # Même mécanique de suppression (worktree remove puis branch -D, ou
        # branch -D seule), mais sans jamais tenter de merge au préalable :
        # un rejet signale que le travail ne doit jamais être intégré (ex.
        # doublon d'une autre issue déjà traitée, fusion qui créerait des
        # conflits inutiles). Le nombre de commits non fusionnés (contre la
        # branche principale du dépôt, toujours une chaîne unique même pour
        # un projet à plusieurs cibles configurées) est calculé ici pour
        # être affiché dans l'avertissement de la confirmation forte, avant
        # qu'Alain ne valide une perte réelle et définitive.
        branche["peut_rejeter"] = not branche["mergee"] and not branche["est_principale"]
        branche["nb_commits_non_fusionnes"] = (
            get_nombre_commits_non_fusionnes(projet["repertoire"], projet["branche_principale"], branche["nom"])
            if branche["peut_rejeter"] else None
        )
        commande_rejet_brute = (
            f"git -C {projet['repertoire']} worktree remove {branche['chemin_worktree']}"
            f" && git -C {projet['repertoire']} branch -D {branche['nom']}"
            if branche["peut_rejeter"] and branche["a_un_worktree"]
            else f"git -C {projet['repertoire']} branch -D {branche['nom']}"
            if branche["peut_rejeter"]
            else None
        )
        branche["commande_rejet"] = (
            commande_affichee(projet["repertoire"], commande_rejet_brute)
            if commande_rejet_brute else None
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
            commande_affichee(projet["repertoire"], f"git -C {projet['repertoire']} branch -D {branche['nom']}")
            if branche["peut_supprimer_branche_recuperation"] else None
        )
    projet["branches"] = branches
    projet["worktree_par_branche"] = {
        worktree["branch"]: worktree for worktree in projet["worktrees"] if worktree["branch"]
    }

    return render_template("projet.html", projet=projet, erreur=erreur)


@app.route("/projet/<nom_projet>/branche/<path:nom_branche>")
@login_requis
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
        resume["commande_revert"] = commande_affichee(
            projet["repertoire"], f"git -C {projet['repertoire']} revert --no-edit {resume['hash']}"
        )

    return render_template(
        "branche.html", projet=projet, nom_branche=nom_branche, resumes=resumes_branche,
    )


@app.route("/projet/<nom_projet>/branche/<path:nom_branche>/revert", methods=["POST"])
@login_requis
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
@login_requis
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


@app.route("/projet/<nom_projet>/nettoyer", methods=["POST"])
@login_requis
def nettoyer_projet_route(nom_projet):
    """Nettoie les résumés déjà pushés du seul projet affiché (issue #68) —
    même critère de sécurité que `nettoyer_tous_les_projets_route` (issue
    #17, `lister_fichiers_resumes_pushes`/`get_commit_est_pushe`), mais sans
    repasser par la liste des projets pour ne nettoyer que celui qu'on vient
    de traiter depuis la page « branches d'un projet »."""
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    try:
        fichiers = lister_fichiers_resumes_pushes(projet["dossier_relecture"], projet["repertoire"])
        nb_supprimes, nb_echecs = _supprimer_fichiers(fichiers)
    except Exception as exc:
        flash(f"❌ Échec du nettoyage de « {nom_projet} » ({exc}).", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    if nb_echecs:
        flash(f"⚠️ {nb_supprimes} résumé(s) supprimé(s), {nb_echecs} échec(s) sur « {nom_projet} ».", "erreur")
    else:
        flash(f"✅ {nb_supprimes} résumé(s) déjà pushé(s) supprimé(s) sur « {nom_projet} ».", "succes")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/gitignore/ajouter", methods=["POST"])
@login_requis
def ajouter_motif_gitignore_route(nom_projet):
    """Ajoute un motif au .gitignore de la racine du projet (panneau
    repliable, issue #98) — champ texte libre, ou raccourci « Ignorer »
    d'un fichier/dossier non suivi (même valeur envoyée directement comme
    `motif`). Valide : une seule ligne, non vide, pas de doublon exact.
    Complète automatiquement par un `/` final si l'entrée correspond à un
    dossier existant du projet (signalé dans le message de retour plutôt
    que de le forcer silencieusement sans explication)."""
    motif_brut = request.form.get("motif", "")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    refus = _refus_modification_gitignore(projet)
    if refus:
        flash(refus, "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    if "\n" in motif_brut or "\r" in motif_brut:
        flash("❌ Une seule ligne à la fois pour le .gitignore.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    motif = motif_brut.strip()
    if not motif:
        flash("❌ Motif vide.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    repertoire = projet["repertoire"]

    # Motif désignant un dossier existant du projet : complète par un "/"
    # final s'il manque — sans lui, le motif masquerait aussi un futur
    # fichier de même nom à la racine du dossier parent, probablement pas
    # l'intention en visant ce dossier précis.
    motif_final = motif
    dossier_detecte = False
    if not motif.endswith("/") and os.path.isdir(os.path.join(repertoire, motif.lstrip("/"))):
        motif_final = motif + "/"
        dossier_detecte = True

    lignes_existantes = lire_lignes_gitignore(repertoire) or []
    motifs_existants = {
        ligne.rstrip("\r\n") for ligne in lignes_existantes
        if classifier_ligne_gitignore(ligne) == "motif"
    }
    if motif_final in motifs_existants:
        flash(f"❌ « {motif_final} » est déjà présent dans le .gitignore.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    ajouter_motif_gitignore(repertoire, motif_final)
    resultat = committer_gitignore(repertoire, f"chore: .gitignore — ajoute {motif_final}")
    if not resultat["ok"]:
        flash(
            f"❌ .gitignore modifié sur disque mais commit impossible ({resultat['commande']}) : "
            f"{resultat['erreur']}",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    message = f"✅ « {motif_final} » ajouté au .gitignore"
    if dossier_detecte:
        message += " (dossier détecté, « / » ajouté automatiquement)"
    message += f" — {resultat['commande']}"

    fichiers_suivis = get_fichiers_suivis_correspondant(repertoire, motif_final)
    if fichiers_suivis:
        message += (
            f" — ⚠️ piège gitignore : {len(fichiers_suivis)} fichier(s) déjà suivi(s) continuent "
            "d'être suivis malgré ce motif (" + ", ".join(fichiers_suivis) + ") — "
            "utilisez « Ne plus suivre » ci-dessous si c'est voulu."
        )
    flash(message, "succes")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/gitignore/retirer", methods=["POST"])
@login_requis
def retirer_motif_gitignore_route(nom_projet):
    """Retire une ligne « motif » du .gitignore (bouton ✕, issue #98) —
    jamais une ligne commentaire/vide (le template ne propose le bouton que
    sur les motifs). `index` + `texte` (envoyés tous les deux, voir
    projet.html) doivent correspondre exactement à la ligne actuellement en
    place : un décalage (fichier modifié entre l'affichage et l'envoi du
    formulaire) fait échouer l'action plutôt que de retirer la mauvaise
    ligne."""
    index_brut = request.form.get("index", "")
    texte_attendu = request.form.get("texte", "")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))

    refus = _refus_modification_gitignore(projet)
    if refus:
        flash(refus, "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    try:
        index = int(index_brut)
    except ValueError:
        flash("❌ Index de ligne invalide.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    repertoire = projet["repertoire"]
    lignes = lire_lignes_gitignore(repertoire)
    if (
        lignes is None or not (0 <= index < len(lignes))
        or classifier_ligne_gitignore(lignes[index]) != "motif"
        or lignes[index].rstrip("\r\n") != texte_attendu
    ):
        flash("❌ Le .gitignore a changé depuis l'affichage de la page — rafraîchissez et réessayez.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    del lignes[index]
    ecrire_lignes_gitignore(repertoire, lignes)
    resultat = committer_gitignore(repertoire, f"chore: .gitignore — retire {texte_attendu}")
    if not resultat["ok"]:
        flash(
            f"❌ .gitignore modifié sur disque mais commit impossible ({resultat['commande']}) : "
            f"{resultat['erreur']}",
            "erreur",
        )
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    flash(
        f"✅ « {texte_attendu} » retiré du .gitignore — les fichiers concernés peuvent réapparaître "
        f"comme non suivis (risque de les committer par erreur) — {resultat['commande']}",
        "succes",
    )
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/gitignore/ne-plus-suivre", methods=["POST"])
@login_requis
def ne_plus_suivre_route(nom_projet):
    """`git rm --cached` sur un fichier déjà suivi qui correspond à un motif
    du .gitignore (piège connu, issue #98) — jamais lancé automatiquement,
    seulement sur ce bouton explicite après confirmation forte côté
    template (modifie l'index et crée un commit)."""
    chemin = request.form.get("chemin", "")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not chemin:
        flash("❌ Chemin manquant.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    refus = _refus_modification_gitignore(projet)
    if refus:
        flash(refus, "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    resultat = retirer_du_suivi(projet["repertoire"], chemin)
    if resultat["ok"]:
        flash(
            f"✅ « {chemin} » ne sera plus suivi par git (fichier conservé sur disque) — {resultat['commande']}",
            "succes",
        )
    else:
        flash(f"❌ Échec de « git rm --cached » sur « {chemin} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/pousser", methods=["POST"])
@login_requis
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
            verification = verifier_push_apres_timeout(projet["repertoire"], nom)
            if verification["ok"] is True:
                flash(
                    f"✅ Le push de « {nom} » a dépassé le délai affiché, mais la vérification "
                    "automatique confirme qu'il a bien abouti (commit distant identique au local).",
                    "succes",
                )
            elif verification["ok"] is False:
                flash(
                    f"❌ Le push de « {nom} » a dépassé le délai et la vérification automatique "
                    "confirme qu'il n'a PAS abouti (commit distant différent ou absent) — à relancer.",
                    "erreur",
                )
            else:
                flash(
                    f"⚠️ Le push de « {nom} » a dépassé le délai, et la vérification automatique n'a "
                    f"pas pu déterminer l'état réel ({verification['erreur'] or 'raison inconnue'}) — "
                    "vérifiez manuellement si besoin.",
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
@login_requis
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

    # Garde-fou avant tout merge (issue #74) : un dossier de branche cible
    # avec des modifications non committées peut signifier qu'une tâche CCL y
    # travaille encore, repliée sur ce même dossier faute de worktree dédié
    # disponible (voir issue #73, où l'intégration automatique du CHANGELOG
    # avait committé ce travail en cours par-dessus) — refus explicite plutôt
    # que de fusionner par-dessus un travail potentiellement en cours.
    modifications = get_modifications_non_committees(projet["repertoire"])
    if modifications:
        flash(
            f"❌ Modifications non committées dans « {projet['repertoire']} » — une tâche CCL y "
            f"travaille peut-être ; merge refusé ({len(modifications)} fichier(s) concerné(s)).",
            "erreur",
        )
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
            resultat = fusionner_worktree(projet["repertoire"], branche_cible, nom, projet["nom"])
        except subprocess.TimeoutExpired:
            verification = verifier_merge_apres_timeout(projet["repertoire"], branche_cible, nom)
            if verification["etat"] == "reussie":
                flash(
                    f"✅ La fusion de « {nom} » a dépassé le délai affiché, mais la vérification "
                    f"automatique confirme qu'elle a bien abouti dans « {branche_cible} ».",
                    "succes",
                )
            elif verification["etat"] == "conflits_en_attente":
                flash(
                    f"⚠️ La fusion de « {nom} » a dépassé le délai — le dépôt est en état de fusion "
                    "avec des conflits à résoudre (voir la page de résolution de conflits).",
                    "erreur",
                )
            elif verification["etat"] == "non_aboutie":
                flash(
                    f"❌ La fusion de « {nom} » a dépassé le délai et la vérification automatique "
                    "confirme qu'elle n'a PAS abouti — à relancer.",
                    "erreur",
                )
            else:
                flash(
                    f"⚠️ La fusion de « {nom} » a dépassé le délai, et la vérification automatique n'a "
                    f"pas pu déterminer l'état réel ({verification['erreur'] or 'raison inconnue'}) — "
                    "vérifiez manuellement si besoin.",
                    "erreur",
                )
            continue
        except Exception as exc:
            flash(f"❌ Erreur inattendue lors de la fusion de « {nom} » : {exc}", "erreur")
            continue
        if resultat["ok"]:
            flash(f"✅ « {nom} » fusionnée dans « {branche_cible} » — {resultat['commande']}", "succes")
            changelog = resultat.get("changelog")
            if changelog is not None:
                if changelog["ok"]:
                    flash(f"✅ CHANGELOG-<N>.md fusionné dans CHANGELOG.md — {changelog['commande']}", "succes")
                else:
                    flash(
                        f"⚠️ « {nom} » fusionnée, mais l'intégration du CHANGELOG a échoué "
                        f"({changelog['commande']}) : {changelog['erreur']} — à fusionner manuellement.",
                        "erreur",
                    )
            erreur_retour_branche = resultat.get("erreur_retour_branche")
            if erreur_retour_branche:
                flash(f"⚠️ {erreur_retour_branche}", "erreur")
        else:
            flash(f"❌ Échec de la fusion de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/merger-et-supprimer", methods=["POST"])
@login_requis
def merger_et_supprimer_route(nom_projet):
    """Bouton combiné « Merger et supprimer » (issue #88) : enchaîne dans le
    même clic la fusion d'une branche (même logique que
    `merger_branches_route`) puis sa suppression (même logique que
    `supprimer_worktrees_route`), pour les branches sélectionnées où les deux
    conditions d'aujourd'hui du Merger seul sont réunies (branche pas la
    cible, pas de contenu doublons uniquement) — mêmes garde-fous que
    `merger_branches_route` par ailleurs (modifications non committées,
    choix explicite de la cible pour un projet à plusieurs cibles
    configurées).

    Refuse en plus d'agir, avec un message flash explicite, si le badge
    « ⚠ CCL travaille ici » (issue #88, voir `worktree_ccl_actif`) est actif
    pour une branche — contrairement au Merger seul, qui reste autorisé même
    avec ce badge affiché (l'utilisateur peut savoir ce qu'il fait
    délibérément).

    Si le merge échoue (conflit, erreur, timeout non confirmé abouti), aucune
    suppression n'est tentée pour cette branche — comportement identique à
    `merger_branches_route`. Si le merge réussit mais que la suppression
    échoue ensuite (modifications non committées détectées entre-temps par
    git, cas rare mais réel), les deux résultats sont rapportés séparément
    dans le message flash : le merge a eu lieu, la suppression non, avec la
    raison."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    # Même garde-fou qu'avant tout merge (issue #74) : voir
    # merger_branches_route pour le détail du raisonnement.
    modifications = get_modifications_non_committees(projet["repertoire"])
    if modifications:
        flash(
            f"❌ Modifications non committées dans « {projet['repertoire']} » — une tâche CCL y "
            f"travaille peut-être ; fusion+suppression refusée ({len(modifications)} fichier(s) concerné(s)).",
            "erreur",
        )
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
    projets, _erreur = _charger_projets()
    verrous_actifs = _verrous_actifs_projets(projets)

    for nom in noms_branches:
        branche = branches.get(nom)
        if not branche:
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
        if worktree_ccl_actif(branche["chemin_worktree"], verrous_actifs):
            flash(
                f"❌ « {nom} » : un verrou Bridge_Agent actif signale une tâche CCL toujours en cours "
                "dans ce worktree — fusion+suppression refusée (le Merger seul reste possible si vous "
                "savez ce que vous faites).",
                "erreur",
            )
            continue

        merge_confirme = False
        try:
            resultat = fusionner_worktree(projet["repertoire"], branche_cible, nom, projet["nom"])
        except subprocess.TimeoutExpired:
            verification = verifier_merge_apres_timeout(projet["repertoire"], branche_cible, nom)
            if verification["etat"] == "reussie":
                merge_confirme = True
                flash(
                    f"✅ La fusion de « {nom} » a dépassé le délai affiché, mais la vérification "
                    f"automatique confirme qu'elle a bien abouti dans « {branche_cible} ».",
                    "succes",
                )
            elif verification["etat"] == "conflits_en_attente":
                flash(
                    f"⚠️ La fusion de « {nom} » a dépassé le délai — le dépôt est en état de fusion "
                    "avec des conflits à résoudre (voir la page de résolution de conflits) ; "
                    "suppression non tentée.",
                    "erreur",
                )
            elif verification["etat"] == "non_aboutie":
                flash(
                    f"❌ La fusion de « {nom} » a dépassé le délai et la vérification automatique "
                    "confirme qu'elle n'a PAS abouti — à relancer ; suppression non tentée.",
                    "erreur",
                )
            else:
                flash(
                    f"⚠️ La fusion de « {nom} » a dépassé le délai, et la vérification automatique n'a "
                    f"pas pu déterminer l'état réel ({verification['erreur'] or 'raison inconnue'}) — "
                    "suppression non tentée.",
                    "erreur",
                )
        except Exception as exc:
            flash(
                f"❌ Erreur inattendue lors de la fusion de « {nom} » : {exc} — suppression non tentée.",
                "erreur",
            )
        else:
            if resultat["ok"]:
                merge_confirme = True
                flash(f"✅ « {nom} » fusionnée dans « {branche_cible} » — {resultat['commande']}", "succes")
                changelog = resultat.get("changelog")
                if changelog is not None:
                    if changelog["ok"]:
                        flash(f"✅ CHANGELOG-<N>.md fusionné dans CHANGELOG.md — {changelog['commande']}", "succes")
                    else:
                        flash(
                            f"⚠️ « {nom} » fusionnée, mais l'intégration du CHANGELOG a échoué "
                            f"({changelog['commande']}) : {changelog['erreur']} — à fusionner manuellement.",
                            "erreur",
                        )
                erreur_retour_branche = resultat.get("erreur_retour_branche")
                if erreur_retour_branche:
                    flash(f"⚠️ {erreur_retour_branche}", "erreur")
            else:
                flash(
                    f"❌ Échec de la fusion de « {nom} » ({resultat['commande']}) : {resultat['erreur']} — "
                    "suppression non tentée.",
                    "erreur",
                )

        if not merge_confirme:
            continue

        # Merge confirmé abouti (chemin direct ou après vérification de
        # timeout) : on enchaîne la suppression, même logique que
        # `supprimer_worktrees_route` — sauf que `mergee` n'est pas
        # revérifié ici : la fusion qui vient d'avoir lieu dans
        # `branche_cible` suffit par construction (comportement volontaire de
        # ce bouton combiné, contrairement à Supprimer seul qui repart d'un
        # état affiché potentiellement obsolète).
        if branche["a_un_worktree"]:
            resultat_worktree = supprimer_worktree(projet["repertoire"], branche["chemin_worktree"])
            if not resultat_worktree["ok"]:
                flash(
                    f"⚠️ « {nom} » fusionnée, mais la suppression du worktree a échoué "
                    f"({resultat_worktree['commande']}) : {resultat_worktree['erreur']}.",
                    "erreur",
                )
                continue
            resultat_branche = supprimer_branche(projet["repertoire"], nom)
            if resultat_branche["ok"]:
                flash(
                    f"✅ Worktree et branche « {nom} » supprimés — {resultat_worktree['commande']} "
                    f"+ {resultat_branche['commande']}",
                    "succes",
                )
            else:
                flash(
                    f"⚠️ « {nom} » fusionnée et worktree supprimé ({resultat_worktree['commande']}), mais la "
                    f"branche n'a pas pu être supprimée ({resultat_branche['commande']}) : "
                    f"{resultat_branche['erreur']}",
                    "erreur",
                )
        else:
            resultat_branche = supprimer_branche(projet["repertoire"], nom)
            if resultat_branche["ok"]:
                flash(f"✅ Branche « {nom} » supprimée — {resultat_branche['commande']}", "succes")
            else:
                flash(
                    f"⚠️ « {nom} » fusionnée, mais la suppression de la branche a échoué "
                    f"({resultat_branche['commande']}) : {resultat_branche['erreur']}.",
                    "erreur",
                )
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/supprimer", methods=["POST"])
@login_requis
def supprimer_worktrees_route(nom_projet):
    """Supprime chaque branche sélectionnée (case à cocher, niveau 2),
    seulement si son merge est confirmé — même garde-fou qu'avant (issue
    précédente), rattaché à la sélection plutôt qu'à l'affichage par
    worktree. Si la branche a encore un worktree, retire le worktree
    (`git worktree remove`) PUIS la branche (`git branch -D`) dans le même
    geste — sans quoi il fallait recliquer une seconde fois pour que la
    branche, désormais sans worktree détecté, tombe enfin sous le second cas
    (issue #54). Si le worktree n'existe déjà plus (retiré manuellement),
    supprime directement la branche — même bouton, même garde-fou `mergee`,
    seule la commande diffère (issue #43)."""
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
            resultat_worktree = supprimer_worktree(projet["repertoire"], branche["chemin_worktree"])
            if not resultat_worktree["ok"]:
                flash(
                    f"❌ Échec de la suppression de « {nom} » ({resultat_worktree['commande']}) : "
                    f"{resultat_worktree['erreur']}",
                    "erreur",
                )
                continue
            resultat_branche = supprimer_branche(projet["repertoire"], nom)
            if resultat_branche["ok"]:
                flash(
                    f"✅ Worktree et branche « {nom} » supprimés — {resultat_worktree['commande']} "
                    f"+ {resultat_branche['commande']}",
                    "succes",
                )
            else:
                flash(
                    f"⚠️ Worktree de « {nom} » supprimé ({resultat_worktree['commande']}), mais la "
                    f"branche n'a pas pu être supprimée ({resultat_branche['commande']}) : "
                    f"{resultat_branche['erreur']}",
                    "erreur",
                )
            continue
        resultat = supprimer_branche(projet["repertoire"], nom)
        if resultat["ok"]:
            flash(f"✅ Branche « {nom} » supprimée — {resultat['commande']}", "succes")
        else:
            flash(f"❌ Échec de la suppression de « {nom} » ({resultat['commande']}) : {resultat['erreur']}", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


@app.route("/projet/<nom_projet>/rejeter", methods=["POST"])
@login_requis
def rejeter_worktrees_route(nom_projet):
    """Rejette chaque branche sélectionnée confirmée NON fusionnée (issue
    #95) — garde-fou strictement inverse de `supprimer_worktrees_route` :
    cette action cible explicitement une branche qui ne doit jamais être
    intégrée (ex. doublon d'une autre issue déjà traitée, fusion qui
    créerait des conflits inutiles sur du travail redondant), là où
    « Supprimer » exige au contraire une branche confirmée fusionnée. Même
    mécanique de suppression (worktree remove puis branch -D, ou branch -D
    seule si le worktree a déjà été retiré), sans jamais tenter de merge au
    préalable.

    Pas de fermeture d'issue GitHub ici (retirée en #97) : en usage normal,
    l'issue correspondante est déjà fermée par le watcher CCL dès la fin de
    son traitement (label `done`), bien avant qu'un rejet n'intervienne.

    Si la case « Purger réellement » est cochée (champ `purger_commit_rejet`,
    issue #96) : `branch -D` seul ne fait que détacher la branche, le commit
    reste récupérable via le reflog (90 jours par défaut) et continue
    d'apparaître comme orphelin « ambigu » dans le diagnostic automatique
    (constat fait en testant le geste manuel équivalent sur chesscoach,
    worktree-issue-88). Les hashes propres à chaque branche effectivement
    rejetée (`get_hashes_commits_non_fusionnes`, capturés AVANT le
    `branch -D` : la plage `principale..branche` ne se résout plus une fois
    la branche supprimée) sont donc accumulés puis purgés pour de bon en une
    seule fois après la boucle, via `_purger_commits_rejetes` ci-dessous —
    jamais par branche, pour n'exécuter qu'un seul `git gc --prune=now`
    (coûteux) par clic plutôt qu'un par branche sélectionnée."""
    noms_branches = request.form.getlist("branches")
    projet, message_erreur = _projet_pret(nom_projet)
    if not projet:
        flash(message_erreur, "erreur")
        return redirect(url_for("index"))
    if not noms_branches:
        flash("❌ Aucune branche sélectionnée.", "erreur")
        return redirect(url_for("projet_route", nom_projet=nom_projet))

    purger = request.form.get("purger_commit_rejet") == "on"

    branche_principale = projet["branche_principale"]
    branches = _branches_par_nom(projet)
    hashes_a_purger = set()
    for nom in noms_branches:
        branche = branches.get(nom)
        if not branche:
            flash(f"❌ Branche « {nom} » introuvable.", "erreur")
            continue
        if nom == branche_principale:
            flash(f"❌ « {nom} » est la branche principale, rejet ignoré.", "erreur")
            continue
        if branche["mergee"]:
            flash(
                f"❌ Rejet de « {nom} » refusé : branche confirmée fusionnée — utilisez « Supprimer la/les "
                "branche(s) fusionnée(s) » à la place.",
                "erreur",
            )
            continue

        hashes_branche = (
            get_hashes_commits_non_fusionnes(projet["repertoire"], branche_principale, nom) if purger else None
        )

        rejet_reussi = False
        if branche["a_un_worktree"]:
            resultat_worktree = supprimer_worktree(projet["repertoire"], branche["chemin_worktree"])
            if not resultat_worktree["ok"]:
                flash(
                    f"❌ Échec du rejet de « {nom} » ({resultat_worktree['commande']}) : "
                    f"{resultat_worktree['erreur']}",
                    "erreur",
                )
                continue
            resultat_branche = supprimer_branche(projet["repertoire"], nom)
            if resultat_branche["ok"]:
                rejet_reussi = True
                flash(
                    f"✅ Worktree et branche « {nom} » rejetés (jamais fusionnés) — "
                    f"{resultat_worktree['commande']} + {resultat_branche['commande']}",
                    "succes",
                )
            else:
                flash(
                    f"⚠️ Worktree de « {nom} » retiré ({resultat_worktree['commande']}), mais la branche "
                    f"n'a pas pu être supprimée ({resultat_branche['commande']}) : {resultat_branche['erreur']}",
                    "erreur",
                )
        else:
            resultat_branche = supprimer_branche(projet["repertoire"], nom)
            if resultat_branche["ok"]:
                rejet_reussi = True
                flash(f"✅ Branche « {nom} » rejetée (jamais fusionnée) — {resultat_branche['commande']}", "succes")
            else:
                flash(
                    f"❌ Échec du rejet de « {nom} » ({resultat_branche['commande']}) : "
                    f"{resultat_branche['erreur']}",
                    "erreur",
                )

        if not rejet_reussi:
            continue

        if purger and hashes_branche:
            hashes_a_purger.update(hashes_branche)

    if purger:
        if hashes_a_purger:
            _purger_commits_rejetes(projet, hashes_a_purger)
        else:
            flash("ℹ️ Purge demandée, mais aucun rejet n'a réussi — aucun commit à purger.", "erreur")
    return redirect(url_for("projet_route", nom_projet=nom_projet))


def _hashes_orphelins_non_securises(projet, hashes_a_exclure):
    """Hashes des commits actuellement orphelins (diagnostic habituel, voir
    `_diagnostiquer_orphelins`) et pas encore sécurisés, hors
    `hashes_a_exclure` (hashes complets) — ce sont les commits qu'une purge
    globale au dépôt (`purger_reflog_et_gc`, issue #96) détruirait EN PLUS de
    ceux visés par le rejet en cours. Un commit déjà sécurisé reste
    atteignable depuis sa branche `recuperation-<hash>`, donc jamais
    concerné par cette purge — inutile de le signaler ici.

    `hashes_a_exclure` contient des hashes complets (`git log --format=%H`),
    les résumés `Non_Lu/` n'en connaissent que le hash court (nom de
    fichier) : comparaison par préfixe, comme `lister_fichiers_resumes_hash`."""
    resumes = collect_resumes_projet(projet["dossier_relecture"], projet["repertoire"])
    resumes_orphelins = regrouper_resumes_par_branche(resumes, projet["repertoire"]).get(None, [])
    return [
        r["hash"] for r in resumes_orphelins
        if not any(h.startswith(r["hash"]) for h in hashes_a_exclure)
        and not commit_est_securise(projet["repertoire"], r["hash"])
    ]


def _purger_commits_rejetes(projet, hashes_cibles):
    """Purge réellement (issue #96) les commits de `hashes_cibles` — ceux
    dont la branche vient d'être rejetée par `rejeter_worktrees_route` —
    via `purger_reflog_et_gc`, globale au dépôt : calcule d'abord les autres
    commits orphelins non sécurisés qui seraient perdus par la même purge
    (Alain en a déjà été averti avant l'envoi du formulaire, voir
    l'avertissement de confirmation dans projet.html), pour les citer dans
    le message de résultat plutôt que de les laisser disparaître en silence.

    Nettoie ensuite, pour tout hash confirmé disparu (`commit_existe`), les
    fichiers `Non_Lu/` associés — aussi bien les commits visés que ces
    orphelins collatéraux, puisque leur résumé laisserait sinon exactement
    le même résidu « ambigu » déjà constaté par le diagnostic (second
    symptôme de l'issue #96)."""
    repertoire = projet["repertoire"]
    autres_orphelins = _hashes_orphelins_non_securises(projet, hashes_cibles)

    resultat = purger_reflog_et_gc(repertoire)
    if not resultat["ok"]:
        flash(f"❌ Échec de la purge ({resultat['commande']}) : {resultat['erreur']}", "erreur")
        return

    hashes_a_verifier = set(hashes_cibles) | set(autres_orphelins)
    hashes_purges = {h for h in hashes_a_verifier if not commit_existe(repertoire, h)}
    hashes_cibles_non_purgees = [h for h in hashes_cibles if h not in hashes_purges]

    fichiers = set()
    for h in hashes_purges:
        fichiers.update(lister_fichiers_resumes_hash(projet["dossier_relecture"], h))
    nb_supprimes, nb_echecs = _supprimer_fichiers(fichiers)

    nb_cibles_purgees = len(hashes_cibles) - len(hashes_cibles_non_purgees)
    nb_collateraux_purges = len(hashes_purges) - nb_cibles_purgees
    message = (
        f"🔥 Purge réelle effectuée ({resultat['commande']}) — {nb_cibles_purgees}/{len(hashes_cibles)} "
        "commit(s) rejeté(s) réellement supprimé(s) du dépôt"
    )
    if nb_collateraux_purges:
        message += (
            f", {nb_collateraux_purges} autre(s) commit(s) orphelin(s) non sécurisé(s) perdu(s) en même temps"
        )
    if nb_supprimes:
        message += f" — {nb_supprimes} fichier(s) Non_Lu/ associé(s) nettoyé(s)"
    flash(message + ".", "erreur" if hashes_cibles_non_purgees or nb_echecs else "succes")

    if hashes_cibles_non_purgees:
        flash(
            "⚠️ Toujours présent(s) dans le dépôt après la purge (probablement protégé(s) par une autre "
            "référence) : " + ", ".join(h[:10] for h in hashes_cibles_non_purgees) +
            " — fichier(s) Non_Lu/ correspondant(s) non nettoyé(s).",
            "erreur",
        )
    if nb_echecs:
        flash(f"⚠️ {nb_echecs} fichier(s) Non_Lu/ n'ont pas pu être supprimés après la purge.", "erreur")


@app.route("/projet/<nom_projet>/supprimer-branche-recuperation", methods=["POST"])
@login_requis
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
@login_requis
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
    import argparse
    import threading
    import webbrowser

    analyseur = argparse.ArgumentParser(description="Lance relecture_web.")
    groupe_mode = analyseur.add_mutually_exclusive_group()
    groupe_mode.add_argument(
        "--lan", action="store_true",
        help="Écoute sur 0.0.0.0 en HTTP, sans mot de passe (réseau local de confiance uniquement).",
    )
    groupe_mode.add_argument(
        "--externe", action="store_true",
        help="Écoute sur 0.0.0.0 en HTTPS, mot de passe obligatoire (exposition au-delà du LAN).",
    )
    analyseur.add_argument(
        "--set-password", action="store_true", dest="set_password",
        help="Définit (ou change) le mot de passe de relecture_web, puis quitte.",
    )
    arguments = analyseur.parse_args()

    if arguments.set_password:
        raise SystemExit(0 if auth.definir_mot_de_passe_interactif() else 1)

    contexte_ssl = None
    if arguments.externe:
        if not auth.mot_de_passe_configure():
            print(
                "❌ Mode --externe refusé : aucun mot de passe configuré pour relecture_web.\n"
                "   Lancez d'abord : python3 relecture_web/app.py --set-password"
            )
            raise SystemExit(1)
        hote = "0.0.0.0"
        app.config["MDP_EXIGE"] = True
        contexte_ssl = auth.assurer_certificat_ssl()
    elif arguments.lan:
        hote = "0.0.0.0"
        app.config["MDP_EXIGE"] = False
    else:
        hote = "127.0.0.1"
        app.config["MDP_EXIGE"] = False

    schema = "https" if contexte_ssl else "http"
    threading.Timer(1.0, lambda: webbrowser.open(f"{schema}://127.0.0.1:{PORT}/")).start()
    app.run(host=hote, port=PORT, debug=False, ssl_context=contexte_ssl)
