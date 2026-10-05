#!/usr/bin/env python3
"""
Lecture de l'état git (worktrees, commits en attente de push) pour les
projets Bridge_Agent, en commandes git directes — sans dépendre du code de
bridge_agent (watcher.py, app/git_etat.py), hors périmètre pour un CCL
travaillant sur relecture_bridge.

La liste des projets est récupérée depuis BRIDGE_AGENT_DOC.md (même source
et même tableau qu'installer.sh), pas codée en dur ici.
"""

import datetime
import hashlib
import json
import os
import re
import socket
import subprocess
import urllib.request

DOC_URL = "https://raw.githubusercontent.com/AlainDelree/Bridge_Agent/master/BRIDGE_AGENT_DOC.md"
DEBUT_TABLEAU = "<!-- DEBUT:TABLEAU_PROJETS_ACTIFS"
FIN_TABLEAU = "<!-- FIN:TABLEAU_PROJETS_ACTIFS"

# Colonne "Couleur" optionnelle en dernière position du tableau (issue #73) :
# repérée par sa forme (hexadécimal), pas par un nom de colonne précis, pour
# rester tolérante à l'absence de la colonne (tableau à 4 champs, dernier
# champ "Topic ntfy" par ex.) sans jamais lever d'erreur.
MOTIF_COULEUR_HEX = re.compile(r"^#(?:[0-9A-Fa-f]{3}){1,2}$")

TIMEOUT_RESEAU = 20
TIMEOUT_GIT = 10
# Opérations git potentiellement longues (push vers le remote, merge sur un
# historique volumineux) — un dépôt avec beaucoup de commits accumulés ou une
# connexion lente peut largement dépasser TIMEOUT_GIT sans que la commande
# ait réellement échoué (issue #39).
TIMEOUT_GIT_LONG = 120
MAX_COMMITS_AFFICHES = 30

# Config par projet, à éditer à la main (voir charger_branches_cibles) —
# dans relecture_bridge, pas dans configs/ de bridge_agent (hors périmètre).
CHEMIN_BRANCHES_CIBLES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "branches_cibles.conf")

# Config du PC fixe Windows (issue #94, voir ccw_host.conf) : un seul hôte
# pour tous les projets CCW distants, pas besoin de sur-ingénierie pour un
# seul hôte configurable (contrairement à branches_cibles.conf, une entrée
# par projet).
CHEMIN_CONFIG_CCW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ccw_host.conf")
CLE_SSH_CCW_DEFAUT = os.path.expanduser("~/.ssh/ccl_ccw")
# ConnectTimeout court côté ssh (en plus du timeout applicatif existant,
# TIMEOUT_GIT/TIMEOUT_GIT_LONG) : un PC fixe éteint ne doit jamais faire
# attendre un appel indéfiniment ni bloquer le serveur Flask de
# développement, mono-thread (issue #94).
TIMEOUT_SSH_CONNECT = 6

# Un projet est « distant » si son `repertoire` (tel que retourné par
# fetch_projets) a la forme d'un chemin Windows (`C:\...`) — heuristique
# gratuite validée par le diagnostic de l'issue #91 : le PC fixe CCW est
# aujourd'hui le seul cas où ce format apparaît (le ThinkPad, lui, n'utilise
# que des chemins POSIX).
MOTIF_CHEMIN_WINDOWS = re.compile(r"^[A-Za-z]:\\")


class ErreurRecuperationProjets(Exception):
    """La liste des projets n'a pas pu être récupérée depuis BRIDGE_AGENT_DOC.md."""


def normaliser_couleur_hex(valeur):
    """Normalise `valeur` en couleur hexadécimale à 6 chiffres (`#rrggbb`),
    ou None si `valeur` n'a pas la forme d'une couleur hexadécimale valide
    (colonne absente, vide, ou tout autre contenu — issue #73). Accepte la
    forme courte à 3 chiffres (`#abc` -> `#aabbcc`)."""
    if not valeur or not MOTIF_COULEUR_HEX.match(valeur):
        return None
    chiffres = valeur[1:]
    if len(chiffres) == 3:
        chiffres = "".join(c * 2 for c in chiffres)
    return "#" + chiffres.lower()


def couleur_texte_lisible(couleur_hex):
    """Noir ou blanc, selon lequel reste lisible sur `couleur_hex` (issue
    #73) — formule de luminance perçue classique (YIQ), un fond saturé
    (ex. jaune) appelant du texte noir, un fond sombre appelant du texte
    blanc. `couleur_hex` doit déjà être normalisée (voir
    `normaliser_couleur_hex`)."""
    chiffres = couleur_hex.lstrip("#")
    r, g, b = (int(chiffres[i:i + 2], 16) for i in (0, 2, 4))
    luminance_percue = (r * 299 + g * 587 + b * 114) / 1000
    return "#000000" if luminance_percue > 125 else "#ffffff"


def _telecharger_doc_projets(forcer_ipv4):
    """Télécharge DOC_URL, en forçant éventuellement la résolution IPv4."""
    if not forcer_ipv4:
        with urllib.request.urlopen(DOC_URL, timeout=TIMEOUT_RESEAU) as reponse:
            return reponse.read().decode("utf-8")

    getaddrinfo_original = socket.getaddrinfo

    def _getaddrinfo_ipv4_uniquement(hote, port, famille=0, type_socket=0, proto=0, flags=0):
        return getaddrinfo_original(hote, port, socket.AF_INET, type_socket, proto, flags)

    socket.getaddrinfo = _getaddrinfo_ipv4_uniquement
    try:
        with urllib.request.urlopen(DOC_URL, timeout=TIMEOUT_RESEAU) as reponse:
            return reponse.read().decode("utf-8")
    finally:
        socket.getaddrinfo = getaddrinfo_original


def fetch_projets():
    """Récupère et parse le tableau des projets actifs depuis BRIDGE_AGENT_DOC.md."""
    # Résolution forcée en IPv4 pour cet appel précis : sur la connexion
    # d'Alain, la résolution IPv6 (tentée en premier par urllib) échoue
    # lentement et retente plusieurs adresses en série avant de retomber sur
    # IPv4 — jusqu'à 4x TIMEOUT_RESEAU (80s) au lieu de 0,4s (issue #57).
    try:
        contenu = _telecharger_doc_projets(forcer_ipv4=True)
    except Exception:
        # Filet de secours (issue #58) : le forçage IPv4 n'a plus de repli si
        # LUI-MÊME échoue (coupure réseau ponctuelle, IPv4 momentanément
        # indisponible...) — avant l'issue #57, un tel échec aurait pu
        # retomber sur IPv6 (lentement, mais sans échec total). On retente
        # donc une seconde fois en laissant urllib choisir normalement,
        # au prix d'une lenteur exceptionnelle plutôt qu'un échec complet.
        try:
            contenu = _telecharger_doc_projets(forcer_ipv4=False)
        except Exception as exc:
            raise ErreurRecuperationProjets(
                f"Impossible de récupérer BRIDGE_AGENT_DOC.md ({exc})"
            ) from exc

    debut = contenu.find(DEBUT_TABLEAU)
    fin = contenu.find(FIN_TABLEAU)
    if debut == -1 or fin == -1:
        raise ErreurRecuperationProjets(
            "Tableau des projets actifs introuvable dans BRIDGE_AGENT_DOC.md "
            "(balises DEBUT/FIN:TABLEAU_PROJETS_ACTIFS absentes)."
        )

    projets = []
    for ligne in contenu[debut:fin].splitlines():
        ligne = ligne.strip()
        if not ligne.startswith("|"):
            continue
        if re.fullmatch(r"\|[\-\s|:]+\|", ligne):
            continue
        champs = [c.strip() for c in ligne.strip("|").split("|")]
        if len(champs) < 3:
            continue
        nom, depot, repertoire = champs[0].strip("`"), champs[1], champs[2]
        if nom in ("", "Nom") or repertoire in ("", "Répertoire de travail CCL"):
            continue
        # Colonne "Couleur" (issue #73) : dernier champ de la ligne, quand il
        # y en a un au-delà de nom/dépôt/répertoire — généré entre backticks
        # (``#rrggbb``) par `regenerer_tableaux_projets.py` côté bridge_agent
        # (issue #608), même convention que la colonne "Nom" ci-dessus.
        # Lecture tolérante par la forme du contenu (voir
        # `normaliser_couleur_hex`), pas par position de colonne fixe ni par
        # en-tête — un tableau à 4 colonnes existant (ex. "Topic ntfy" en
        # dernière position) ne matche simplement pas le motif hexadécimal et
        # retombe sans erreur sur couleur=None.
        couleur = normaliser_couleur_hex(champs[-1].strip("`")) if len(champs) > 3 else None
        projets.append({
            "nom": nom,
            "depot": depot,
            "repertoire": os.path.expanduser(repertoire),
            "couleur": couleur,
            "couleur_texte": couleur_texte_lisible(couleur) if couleur else None,
        })

    if not projets:
        raise ErreurRecuperationProjets(
            "Aucun projet trouvé dans le tableau de BRIDGE_AGENT_DOC.md."
        )
    return projets


def est_projet_distant(repertoire):
    """True si `repertoire` a la forme d'un chemin Windows (`C:\\...`,
    voir MOTIF_CHEMIN_WINDOWS) — le PC fixe CCW (issue #94), par
    opposition à un projet local sur le ThinkPad (chemin POSIX)."""
    return bool(MOTIF_CHEMIN_WINDOWS.match(repertoire or ""))


def charger_config_ccw():
    """Lit `ccw_host.conf` (issue #94, même convention que
    `charger_branches_cibles` : `cle = valeur`, une entrée par ligne, `#`
    pour les commentaires). Retourne {"host": "user@hote", "cle": chemin}
    si `ccw_host` est configuré, sinon None (fichier absent, vide, ou
    entrée `ccw_host` manquante/commentée) — état par défaut avant
    qu'Alain ne renseigne le PC fixe. `ccw_key` est optionnelle, repli sur
    CLE_SSH_CCW_DEFAUT (~/.ssh/ccl_ccw, déjà en place côté ThinkPad)."""
    try:
        with open(CHEMIN_CONFIG_CCW, encoding="utf-8") as fichier:
            contenu = fichier.read()
    except FileNotFoundError:
        return None

    config = {"host": None, "cle": CLE_SSH_CCW_DEFAUT}
    for ligne in contenu.splitlines():
        ligne = ligne.split("#", 1)[0].strip()
        if not ligne or "=" not in ligne:
            continue
        cle, _, valeur = ligne.partition("=")
        cle, valeur = cle.strip(), valeur.strip()
        if cle == "ccw_host" and valeur:
            config["host"] = valeur
        elif cle == "ccw_key" and valeur:
            config["cle"] = os.path.expanduser(valeur)

    return config if config["host"] else None


def _quoter_argument_distant(argument):
    """Échappe un argument pour la commande transmise au shell distant
    (issue #94) — un chemin Windows du PC fixe (ex. `C:\\CCW\\Nom Projet`)
    peut contenir des espaces, et le shell réellement utilisé côté PC fixe
    (PowerShell, cmd.exe ou Git Bash) n'a pas pu être confirmé par le
    diagnostic (issue #91). Entourer de guillemets doubles dès qu'un espace
    est présent reste correct dans les trois cas : cmd.exe ne traite pas
    l'antislash comme caractère d'échappement à l'intérieur de guillemets
    (un chemin Windows s'y comporte donc normalement), et un shell POSIX
    (Git Bash) préserve de même un antislash isolé entre guillemets
    doubles."""
    if not argument:
        return '""'
    if any(c in argument for c in (" ", "\t")):
        return f'"{argument}"'
    return argument


def _commande_ssh_ccw(config, commande_distante):
    """Commande `ssh` complète (liste d'arguments, prête pour
    `subprocess.run`) vers le PC fixe CCW configuré (issue #94) —
    `ConnectTimeout` court (TIMEOUT_SSH_CONNECT) pour qu'un PC fixe éteint
    échoue vite plutôt que de bloquer, `BatchMode=yes` pour ne jamais
    tomber sur une invite de mot de passe interactive (clé déjà en place),
    `StrictHostKeyChecking=accept-new` pour accepter silencieusement un
    hôte encore inconnu (première connexion) sans échouer ni demander de
    confirmation interactive, comme une machine physique unique et déjà
    identifiée par sa clé le permet ici."""
    return [
        "ssh", "-i", config["cle"],
        "-o", f"ConnectTimeout={TIMEOUT_SSH_CONNECT}",
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        config["host"],
        commande_distante,
    ]


def _lancer_git_distant(repertoire, args, timeout, entree):
    """Exécute une commande git sur le PC fixe CCW via SSH (issue #94),
    appelée par `_lancer_git` quand `est_projet_distant(repertoire)` est
    vrai — conserve la même interface de retour (code de retour, stdout,
    stderr, via un `subprocess.CompletedProcess`) que l'exécution locale,
    pour ne rien casser côté appelants de ce module.

    Chaque commande git est envoyée seule (jamais enchaînée par `&&` sur le
    shell distant, dont l'implémentation exacte — PowerShell, cmd.exe ou
    Git Bash — n'a pas pu être confirmée par le diagnostic) : les
    appelants de haut niveau qui enchaînent plusieurs étapes (ex.
    `fusionner_worktree` : checkout, merge, checkout retour) le font déjà
    via des appels `_lancer_git` séparés, jamais via un seul `&&` shell —
    ce module reste donc robuste au shell distant réel sans rien changer à
    ces appelants.

    Si `ccw_host` n'est pas configuré (voir `charger_config_ccw`), retourne
    directement un échec (code 1) sans tenter de connexion — évite une
    erreur SSH confuse (hôte manquant) là où le message peut être clair
    immédiatement."""
    config = charger_config_ccw()
    if not config:
        return subprocess.CompletedProcess(
            args=[], returncode=1, stdout="",
            stderr="ccw_host non configuré (relecture_web/ccw_host.conf) — impossible de joindre le PC fixe.",
        )

    commande_git = " ".join(_quoter_argument_distant(a) for a in ("git", "-C", repertoire, *args))
    commande_ssh = _commande_ssh_ccw(config, commande_git)
    return subprocess.run(commande_ssh, input=entree, capture_output=True, text=True, timeout=timeout)


def tester_connectivite_ccw():
    """True si le PC fixe CCW configuré (voir `charger_config_ccw`) répond
    actuellement via SSH, False sinon (hôte non configuré, PC éteint,
    mauvais hôte/port, timeout) — précondition testée par
    `collect_etat_projets` avant toute tentative de commande git sur un
    projet distant (issue #94), sur le modèle du test `os.path.isdir` déjà
    en place pour les projets locaux. `ConnectTimeout` court
    (TIMEOUT_SSH_CONNECT) : un PC fixe éteint ne doit jamais faire attendre
    indéfiniment, le serveur Flask de développement étant mono-thread."""
    config = charger_config_ccw()
    if not config:
        return False
    commande = _commande_ssh_ccw(config, "exit 0")
    try:
        resultat = subprocess.run(
            commande, capture_output=True, text=True, timeout=TIMEOUT_SSH_CONNECT + 3,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return resultat.returncode == 0


def commande_affichee(repertoire, commande_git):
    """Commande à afficher à Alain avant confirmation (issue #94) : pour un
    projet distant (voir `est_projet_distant`), préfixe `commande_git`
    (ex. `git -C C:\\CCW\\Projet push origin main`) par la commande ssh
    réellement exécutée, pour qu'il sache que l'action passera par le
    réseau plutôt que de lui montrer seulement la commande git nue. Pour un
    projet local, retourne `commande_git` inchangée (comportement
    d'affichage identique à avant cette issue)."""
    if not est_projet_distant(repertoire):
        return commande_git
    config = charger_config_ccw()
    prefixe_ssh = f"ssh -i {config['cle']} {config['host']}" if config else "ssh <ccw_host non configuré>"
    return f"{prefixe_ssh} {commande_git}"


def _lancer_git(repertoire, *args, timeout=TIMEOUT_GIT, entree=None):
    """Point d'entrée unique pour toute commande git de ce module (issue
    #93/#94 : router `repertoire` vers une exécution locale ou distante,
    voir `est_projet_distant`/`_lancer_git_distant`, en un seul endroit).
    `timeout` permet aux appelants aux durées atypiques (`TIMEOUT_GIT_LONG`
    pour push/merge/commit, `TIMEOUT_RESEAU` pour `ls-remote`) de le
    surcharger sans dupliquer l'appel ; `entree` transmet un texte sur
    l'entrée standard, pour les commandes qui lisent un pipe (ex. `git
    patch-id` recevant la sortie de `git show`/`git log -p`)."""
    if est_projet_distant(repertoire):
        return _lancer_git_distant(repertoire, args, timeout, entree)
    return subprocess.run(
        ["git", "-C", repertoire, *args],
        input=entree, capture_output=True, text=True, timeout=timeout,
    )


def get_worktrees(repertoire):
    """Liste les worktrees actifs d'un dépôt via `git worktree list --porcelain`."""
    resultat = _lancer_git(repertoire, "worktree", "list", "--porcelain")
    if resultat.returncode != 0:
        return []

    worktrees = []
    courant = None
    for ligne in resultat.stdout.splitlines():
        if ligne.startswith("worktree "):
            if courant is not None:
                worktrees.append(courant)
            courant = {"path": ligne[len("worktree "):], "branch": None, "detache": False}
        elif courant is None:
            continue
        elif ligne.startswith("branch "):
            courant["branch"] = ligne[len("branch "):].replace("refs/heads/", "", 1)
        elif ligne == "detached":
            courant["detache"] = True
    if courant is not None:
        worktrees.append(courant)
    return worktrees


def _lignes_deja_pris_watcher(nom_projet, repertoire_bridge_agent):
    """Lignes contenant « déjà pris » de `logs/watcher-<nom_projet>.log`, le
    journal que bridge_agent écrit (issue #589) quand une tâche `mode_write`
    ne peut pas obtenir son propre worktree (chemin ou branche déjà pris) et
    retombe sur REP_TRAVAIL — utilisées pour repérer un worktree orphelin
    laissé par cette tentative précédente (issue #67).

    Lecture seule d'un fichier hors périmètre relecture_bridge, comme
    `get_worktrees` le fait déjà via `git -C <repertoire>` pour l'état git
    des autres projets. `repertoire_bridge_agent` est le répertoire de
    travail du projet "bridge_agent" lui-même (là où vit `logs/`, partagé
    entre tous les projets) ; absent ou fichier introuvable/illisible ->
    liste vide, best-effort, ne doit jamais faire échouer l'affichage des
    worktrees."""
    if not repertoire_bridge_agent:
        return []
    chemin_log = os.path.join(repertoire_bridge_agent, "logs", f"watcher-{nom_projet}.log")
    try:
        with open(chemin_log, encoding="utf-8", errors="replace") as fichier:
            return [ligne for ligne in fichier if "déjà pris" in ligne]
    except OSError:
        return []


def worktree_orphelin_signale(chemin_worktree, lignes_deja_pris):
    """True si `chemin_worktree` apparaît dans une des `lignes_deja_pris`
    (voir `_lignes_deja_pris_watcher`) — ce worktree correspond à une
    tentative pour laquelle bridge_agent a signalé un repli sur REP_TRAVAIL,
    donc potentiellement resté planté sur le disque avec du travail non
    committé (issue #67)."""
    return any(chemin_worktree in ligne for ligne in lignes_deja_pris)


def _pid_vivant(pid):
    """True si un processus `pid` existe actuellement sur la machine (signal
    0, qui ne tue rien — juste un test d'existence standard côté Unix, voir
    `os.kill`). Un verrou Bridge_Agent (voir `lire_verrous_actifs`) dont le
    pid ne correspond plus à aucun processus vivant est un fichier orphelin
    (tâche terminée sans nettoyage, ex. kill -9) : il ne doit plus compter
    comme actif."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        # PermissionError (pid existant mais appartenant à un autre
        # utilisateur) ou toute autre erreur d'accès : impossible d'affirmer
        # que le processus est mort, on le considère par prudence toujours
        # vivant plutôt que de risquer un faux négatif sur le badge.
        return True
    return True


def lire_verrous_actifs(repertoire_bridge_agent):
    """Chemins `rep=` des verrous actifs de Bridge_Agent — un fichier par
    tâche `mode_write` en cours dans `logs/verrous/*.lock`, avec des paires
    `pid=<pid>`, `rep=<chemin_worktree>` et `mode=<mode>` (ajouté par #609
    côté bridge_agent) séparées par des espaces — sur une seule ligne en
    pratique côté Bridge_Agent, mais réparties sur plusieurs lignes
    également acceptées (issue #89) — utilisés pour signaler dans la page
    projet (issue #88) qu'une tâche CCL travaille peut-être encore dans un
    worktree donné avant de proposer sa suppression (voir
    `worktree_ccl_actif`).

    Un verrou n'est retenu que si son `pid` correspond à un processus
    toujours vivant (voir `_pid_vivant`) — un fichier `.lock` laissé derrière
    par une tâche terminée sans nettoyage (ex. kill -9) ne doit pas signaler
    indéfiniment un worktree comme occupé.

    Dégrade proprement à liste vide si Bridge_Agent n'est pas installé au
    même endroit (`repertoire_bridge_agent` absent) ou si son dossier de
    verrous est inaccessible/inexistant — jamais d'exception qui romprait
    l'affichage de la page projet, même principe que
    `_lignes_deja_pris_watcher`."""
    if not repertoire_bridge_agent:
        return []
    dossier_verrous = os.path.join(repertoire_bridge_agent, "logs", "verrous")
    try:
        noms_fichiers = [n for n in os.listdir(dossier_verrous) if n.endswith(".lock")]
    except OSError:
        return []

    reps_actifs = []
    for nom in noms_fichiers:
        try:
            with open(os.path.join(dossier_verrous, nom), encoding="utf-8", errors="replace") as fichier:
                contenu = fichier.read()
        except OSError:
            continue

        champs = {}
        for ligne in contenu.splitlines():
            for jeton in ligne.split():
                cle, separateur, valeur = jeton.partition("=")
                if separateur:
                    champs[cle.strip()] = valeur.strip()

        rep = champs.get("rep")
        pid_texte = champs.get("pid")
        if not rep or not pid_texte:
            continue
        try:
            pid = int(pid_texte)
        except ValueError:
            continue
        if _pid_vivant(pid):
            reps_actifs.append(rep)
    return reps_actifs


def worktree_ccl_actif(chemin_worktree, reps_actifs):
    """True si `chemin_worktree` correspond au `rep=` d'un verrou Bridge_Agent
    actif (voir `lire_verrous_actifs`) — badge « ⚠ CCL travaille ici » de la
    page projet (issue #88). Comparaison par chemin réel (`os.path.realpath`)
    des deux côtés, pour ne pas manquer une correspondance à cause d'un lien
    symbolique ou d'un `..` résiduel dans l'un des deux chemins."""
    if not chemin_worktree:
        return False
    chemin_reel = os.path.realpath(chemin_worktree)
    return any(os.path.realpath(rep) == chemin_reel for rep in reps_actifs)


def get_branche_courante(repertoire):
    """Branche extraite (HEAD) dans `repertoire` — le répertoire du projet
    est toujours le worktree principal du dépôt (le premier de `git worktree
    list`), donc c'est là la branche principale à utiliser comme cible de
    merge. Retourne None si indéterminable (dépôt détaché, erreur git)."""
    resultat = _lancer_git(repertoire, "rev-parse", "--abbrev-ref", "HEAD")
    if resultat.returncode != 0:
        return None
    branche = resultat.stdout.strip()
    return branche if branche and branche != "HEAD" else None


def est_branche_mergee(repertoire, branche_principale, branche):
    """True si `branche` est un ancêtre de `branche_principale` dans le dépôt
    de `repertoire` — c'est-à-dire intégralement fusionnée, condition requise
    avant de proposer la suppression d'un worktree.


    `branche_principale` peut être une liste (projet à plusieurs cibles
    configurées, issue #41/#50) : `branche` est alors considérée fusionnée
    dès qu'elle est ancêtre d'au moins une des candidates — un
    `git merge-base --is-ancestor` par candidate, répété au pire une poignée
    de fois (nombre de cibles configurées), sans commune mesure avec le coût
    d'un `git cherry`/calcul de distance sur tout l'historique qui avait
    déjà provoqué un timeout (issue #42)."""
    if not branche_principale or not branche:
        return False
    candidates = branche_principale if isinstance(branche_principale, list) else [branche_principale]
    return any(
        _lancer_git(repertoire, "merge-base", "--is-ancestor", branche, candidate).returncode == 0
        for candidate in candidates
    )


def get_nombre_commits_non_fusionnes(repertoire, branche_reference, branche):
    """Nombre de commits propres à `branche` absents de `branche_reference`
    (`git log branche_reference..branche --oneline`) — résumé affiché avant
    confirmation du bouton « Rejeter » (issue #95), pour qu'Alain voie
    l'ampleur du travail jamais fusionné qu'il s'apprête à perdre
    définitivement. Retourne None si la commande échoue plutôt que 0, pour
    distinguer « aucun commit en avance » de « indéterminable »."""
    resultat = _lancer_git(repertoire, "log", "--oneline", f"{branche_reference}..{branche}")
    if resultat.returncode != 0:
        return None
    return len([ligne for ligne in resultat.stdout.splitlines() if ligne.strip()])


def get_hashes_commits_non_fusionnes(repertoire, branche_reference, branche):
    """Hashes complets des commits propres à `branche` absents de
    `branche_reference` (`git log branche_reference..branche --format=%H`) —
    pendant de `get_nombre_commits_non_fusionnes` qui retourne les hashes
    plutôt qu'un compte, pour que le bouton « Rejeter » sache précisément
    quels commits deviendront orphelins après `branch -D` et doivent donc
    être ciblés par la purge réelle optionnelle (`purger_reflog_et_gc`,
    issue #96). Retourne None si la commande échoue, même convention que
    `get_nombre_commits_non_fusionnes`."""
    resultat = _lancer_git(repertoire, "log", "--format=%H", f"{branche_reference}..{branche}")
    if resultat.returncode != 0:
        return None
    return [ligne.strip() for ligne in resultat.stdout.splitlines() if ligne.strip()]


def commit_existe(repertoire, hash_commit):
    """True si `hash_commit` désigne toujours un commit valide dans le dépôt
    (`git cat-file -e <hash>^{commit}`) — utilisé après `purger_reflog_et_gc`
    (issue #96) pour vérifier, avant de nettoyer son résumé `Non_Lu/`, qu'un
    commit visé par le rejet a réellement disparu plutôt que de le supposer."""
    resultat = _lancer_git(repertoire, "cat-file", "-e", f"{hash_commit}^{{commit}}")
    return resultat.returncode == 0


def purger_reflog_et_gc(repertoire):
    """Purge réelle et DÉFINITIVE de tout objet non atteignable du dépôt
    (`git reflog expire --expire=now --all` puis `git gc --prune=now`) —
    complément à la suppression de branche du bouton « Rejeter » (issue #96) :
    `git branch -D` seul ne fait que détacher la branche, le commit reste
    récupérable (reflog, 90 jours par défaut) et continue d'apparaître comme
    commit orphelin « ambigu » dans le diagnostic automatique.

    Ces deux commandes sont globales au dépôt entier : aucune option git ne
    permet de n'expirer/purger que le reflog d'une branche déjà supprimée
    (son fichier de reflog, orphelin lui aussi, n'est plus listé par
    `--all`, qui n'énumère que les refs existantes). Tout AUTRE commit
    orphelin présent dans le dépôt est donc également concerné, SAUF s'il
    reste atteignable depuis une vraie branche — notamment une branche de
    sécurisation `recuperation-<hash>` créée par `securiser_commit_orphelin`
    : un pointeur de branche protège son commit indépendamment du reflog, de
    cette purge y compris. C'est pourquoi « Sécuriser » reste le geste à
    recommander à l'appelant (voir `rejeter_worktrees_route`) pour mettre un
    commit orphelin hors d'atteinte de cette purge — aucune purge ciblée
    plus fine n'est possible avec les commandes git disponibles.

    N'est appelée qu'après confirmation explicite d'Alain (jamais en
    arrière-plan silencieux) : à l'appelant de lister les autres commits
    orphelins non sécurisés menacés avant de déclencher cet appel. Timeout
    long (`TIMEOUT_GIT_LONG`) : `git gc` peut prendre du temps sur un
    historique volumineux. Retourne {ok, erreur, commande} ; le `gc` n'est
    pas tenté si le `reflog expire` a déjà échoué."""
    commande_reflog = ["git", "-C", repertoire, "reflog", "expire", "--expire=now", "--all"]
    resultat_reflog = _lancer_git(
        repertoire, "reflog", "expire", "--expire=now", "--all", timeout=TIMEOUT_GIT_LONG
    )
    if resultat_reflog.returncode != 0:
        return {
            "ok": False,
            "erreur": (resultat_reflog.stderr or resultat_reflog.stdout).strip(),
            "commande": commande_affichee(repertoire, " ".join(commande_reflog)),
        }

    commande_gc = ["git", "-C", repertoire, "gc", "--prune=now"]
    resultat_gc = _lancer_git(repertoire, "gc", "--prune=now", timeout=TIMEOUT_GIT_LONG)
    commande_complete = " ".join(commande_reflog) + " && " + " ".join(commande_gc)
    return {
        "ok": resultat_gc.returncode == 0,
        "erreur": (resultat_gc.stderr or resultat_gc.stdout).strip() if resultat_gc.returncode != 0 else None,
        "commande": commande_affichee(repertoire, commande_complete),
    }


def charger_branches_cibles():
    """Lit `branches_cibles.conf` (une ligne `nom_projet = branche` par
    entrée, `#` pour les commentaires) — configure, projet par projet, la ou
    les branches à utiliser comme référence pour savoir si un commit
    orphelin ou en attente est déjà intégré, quand ce n'est pas la branche
    principale du dépôt (ex. un projet qui travaille sur `dev` avant de
    merger vers `main` : comparer contre `main` donnerait un écart de
    commits trompeur).
    `nom_projet` est le champ "nom" de BRIDGE_AGENT_DOC.md (ex.
    "ff_galerie"), pas le nom de dossier. Fichier absent ou entrée manquante
    pour un projet : aucune surcharge, comportement inchangé.

    `branche` accepte plusieurs branches séparées par une virgule (ex.
    `master, feature/moteur-strategique`) pour les projets à lignes de
    développement parallèles et indépendantes (issue #41) — dans ce cas,
    l'entrée stockée est une liste plutôt qu'une chaîne unique (voir
    `get_branche_cible_comparaison`)."""
    branches_cibles = {}
    try:
        with open(CHEMIN_BRANCHES_CIBLES, encoding="utf-8") as fichier:
            contenu = fichier.read()
    except FileNotFoundError:
        return branches_cibles

    for ligne in contenu.splitlines():
        ligne = ligne.split("#", 1)[0].strip()
        if not ligne or "=" not in ligne:
            continue
        nom_projet, valeur = ligne.split("=", 1)
        nom_projet = nom_projet.strip()
        cibles = [c.strip() for c in valeur.split(",") if c.strip()]
        if nom_projet and cibles:
            branches_cibles[nom_projet] = cibles[0] if len(cibles) == 1 else cibles
    return branches_cibles


def get_branche_cible_comparaison(nom_projet, branche_principale, branches_cibles=None):
    """Branche(s) cible(s) de comparaison d'un projet : la valeur configurée
    dans `branches_cibles.conf` si elle existe, sinon `branche_principale`
    (repli par défaut, comportement inchangé pour les projets sans
    configuration explicite). Retourne une chaîne unique pour un projet à
    une seule cible (comportement inchangé depuis l'issue #20), ou une liste
    de chaînes pour un projet à plusieurs cibles configurées (issue #41) —
    à charge de l'appelant de gérer les deux formes ; le choix de la cible à
    utiliser pour un commit donné dans ce second cas n'est pas traité ici
    (voir issue de suivi). `branches_cibles` peut être fourni déjà chargé
    pour éviter de relire le fichier à chaque projet dans une boucle."""
    if branches_cibles is None:
        branches_cibles = charger_branches_cibles()
    return branches_cibles.get(nom_projet, branche_principale)


def get_branches_locales(repertoire, branche_cible=None):
    """Liste toutes les branches locales d'un dépôt (`git for-each-ref
    refs/heads/`), contrairement à `get_worktrees` qui ne voit que celles
    ayant un worktree actif. Pour chaque branche : son dernier commit, le
    chemin de son worktree s'il en existe un, et si elle est fusionnée
    (via `est_branche_mergee`) dans `branche_cible` — la branche cible de
    comparaison configurée (issue #20) si fournie, sinon la branche
    principale git par défaut (repli, comportement inchangé pour les
    projets sans configuration explicite — issue #26). `branche_cible` peut
    être une liste (projet à plusieurs cibles configurées, issue #41) :
    `est_branche_mergee` gère elle-même ce cas (issue #50)."""
    resultat = _lancer_git(
        repertoire, "for-each-ref", "refs/heads/",
        "--format=%(refname:short)%09%(objectname:short)%09"
        "%(committerdate:iso-strict)%09%(subject)",
    )
    if resultat.returncode != 0:
        return []

    branche_principale = get_branche_courante(repertoire)
    branche_reference = branche_cible or branche_principale
    chemin_worktree_par_branche = {
        worktree["branch"]: worktree["path"]
        for worktree in get_worktrees(repertoire)
        if worktree["branch"]
    }

    branches = []
    for ligne in resultat.stdout.splitlines():
        if not ligne.strip():
            continue
        champs = ligne.split("\t", 3)
        if len(champs) < 4:
            continue
        nom, hash_commit, date, sujet = champs
        chemin_worktree = chemin_worktree_par_branche.get(nom)
        branches.append({
            "nom": nom,
            "dernier_commit": {"hash": hash_commit, "date": date, "sujet": sujet},
            "chemin_worktree": chemin_worktree,
            "a_un_worktree": chemin_worktree is not None,
            "mergee": est_branche_mergee(repertoire, branche_reference, nom),
        })
    return branches


def get_sujet_commit(repertoire, hash_commit):
    """Sujet (première ligne du message) d'un commit donné — utilisé pour
    afficher hash + message sur les cartes de commit repliées, sans dépendre
    du nom de fichier `.diff` (qui est un slug, pas le message d'origine)."""
    resultat = _lancer_git(repertoire, "show", "-s", "--format=%s", hash_commit)
    if resultat.returncode != 0:
        return None
    return resultat.stdout.strip() or None


def get_date_commit(repertoire, hash_commit):
    """Date (+ heure) de création d'un commit donné, au format lisible
    jj/mm/aaaa hh:mm — même pattern que `get_sujet_commit`. La date réelle du
    commit vient toujours de git, jamais de la date du fichier `.diff` dans
    `Non_Lu/` (trompeuse : un déplacement manuel entre dossiers change la
    date du fichier sans changer celle du commit, voir issue #48)."""
    resultat = _lancer_git(
        repertoire, "show", "-s", "--date=format:%d/%m/%Y %H:%M", "--format=%cd", hash_commit
    )
    if resultat.returncode != 0:
        return None
    return resultat.stdout.strip() or None


def get_branches_contenant(repertoire, hash_commit):
    """Branches locales contenant `hash_commit` (`git branch --contains`) —
    un commit déjà fusionné peut apparaître dans plusieurs branches ; une
    liste vide signifie qu'aucune branche locale actuelle ne le contient
    (ex. branche supprimée depuis)."""
    resultat = _lancer_git(
        repertoire, "branch", "--list", "--contains", hash_commit,
        "--format=%(refname:short)",
    )
    if resultat.returncode != 0:
        return []
    return [l.strip() for l in resultat.stdout.splitlines() if l.strip()]


def get_commit_est_vide(repertoire, hash_commit):
    """True si `hash_commit` ne modifie aucun fichier — un commit de backup
    (`--allow-empty`, voir post-commit) : toujours exclu du diagnostic
    `git cherry` (issue #21, case D), même s'il apparaît comme ancêtre dans
    la chaîne d'un autre commit orphelin."""
    resultat = _lancer_git(repertoire, "show", "--format=", "--numstat", hash_commit)
    if resultat.returncode != 0:
        return False
    return not resultat.stdout.strip()


def get_chaine_cherry(repertoire, branche_cible, hash_commit):
    """Chaîne de commits entre la base commune avec `branche_cible` et
    `hash_commit`, classés par `git cherry <branche_cible> <hash_commit>` —
    qui compare le **contenu** (patch-id) des commits, pas leur hash ni leur
    message (voir issue #21) : chaque maillon est {hash, statut}, statut
    'nouveau' (préfixe `+`, contenu absent de `branche_cible`) ou 'doublon'
    (préfixe `-`, contenu déjà présent sous un autre hash). Les commits vides
    (backup) sont retirés de la chaîne (case D). Retourne None si
    `git cherry` échoue ou renvoie une ligne inattendue (case F, ambigu —
    aucun verdict automatique)."""
    resultat = _lancer_git(repertoire, "cherry", branche_cible, hash_commit)
    if resultat.returncode != 0:
        return None

    chaine = []
    for ligne in resultat.stdout.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        prefixe, _, sha = ligne.partition(" ")
        sha = sha.strip()
        if prefixe == "+":
            statut = "nouveau"
        elif prefixe == "-":
            statut = "doublon"
        else:
            return None
        if get_commit_est_vide(repertoire, sha):
            continue
        chaine.append({"hash": sha, "statut": statut})
    return chaine


def get_diagnostic_doublons_branche(repertoire, branche_cible, branche):
    """True si fusionner `branche` dans `branche_cible` n'apporterait aucun
    contenu nouveau. False si `branche_cible` n'est pas configurée.

    Cas particulier `recuperation-<hash>` (issue #23) : une telle branche ne
    contient par construction qu'un seul commit d'intérêt, celui dont elle
    porte le nom. Utiliser l'agrégat `git cherry` sur toute la branche est
    fragile si elle a été créée sur un point ancien de l'arbre : la chaîne
    remonte alors aussi de vieux commits d'historique sans rapport avec le
    commit orphelin visé, et un seul d'entre eux suffit à faire échouer
    l'agrégat même si le commit visé est bien un doublon (issue #27). On
    réutilise donc directement le diagnostic de ce commit précis (même
    logique que `diagnostiquer_commits_orphelins`, cas B/D = rien à
    apporter), plutôt que de relancer `git cherry` sur toute la chaîne.

    Pour toute autre branche (worktree `mode_write` ordinaire, plusieurs
    commits propres légitimes), comportement inchangé (issue #25) : agrégat
    sur la chaîne complète renvoyée par `git cherry` (commits vides de
    backup déjà exclus par `get_chaine_cherry`) — False si `branche` n'a
    aucun commit propre (déjà fusionnée, rien à signaler ici), ou si `git
    cherry` échoue (ambigu, laissé au jugement manuel comme le cas F).

    `branche_cible` peut être une liste (projet à plusieurs cibles
    configurées, issue #41) : contrairement à `est_branche_mergee`
    (`git merge-base --is-ancestor`, peu coûteux), ce diagnostic repose sur
    `git cherry` sur toute la chaîne de la branche — répété pour chaque
    branche locale de la page projet (pas juste les commits orphelins,
    beaucoup moins nombreux), ce coût cumulé est le même qui a déjà fait
    échouer par timeout une tentative similaire (`scrabble`, issue #42/#46).
    Même parti pris que le cas 'M' de `diagnostiquer_commits_orphelins` :
    on ne devine rien, aucun `git cherry` supplémentaire n'est lancé, la
    vérification reste manuelle (issue #50)."""
    if isinstance(branche_cible, list):
        return False

    if not branche_cible:
        return False

    hash_recuperation = hash_depuis_branche_recuperation(branche)
    if hash_recuperation:
        diagnostic = _diagnostiquer_commit(repertoire, branche_cible, hash_recuperation)
        return diagnostic["cas"] in ("B", "D")

    chaine = get_chaine_cherry(repertoire, branche_cible, branche)
    if not chaine:
        return False
    return all(maillon["statut"] == "doublon" for maillon in chaine)


def get_rapport_cherry_brut(repertoire, branche_cible, hash_commit):
    """Sortie brute de `git cherry <branche_cible> <hash_commit>` (issue #22,
    bouton « Générer rapport »), indépendante du parsing de
    `get_chaine_cherry` : donne à l'humain exactement ce que verrait
    quelqu'un lançant la commande à la main, y compris le message d'erreur
    en cas d'échec — c'est précisément ce qu'un diagnostic classé en cas F
    (ambigu, voir `diagnostiquer_commits_orphelins`) ne peut pas interpréter
    automatiquement."""
    if not branche_cible:
        return {"commande": None, "sortie": None, "erreur": "Branche cible de comparaison non configurée pour ce projet."}
    commande = ["git", "-C", repertoire, "cherry", branche_cible, hash_commit]
    resultat = _lancer_git(repertoire, "cherry", branche_cible, hash_commit)
    return {
        "commande": commande_affichee(repertoire, " ".join(commande)),
        "sortie": resultat.stdout.strip() if resultat.returncode == 0 else None,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
    }


def get_patch_id_commit(repertoire, hash_commit):
    """Empreinte de patch (`git patch-id --stable`) du contenu introduit par
    `hash_commit` — compare le contenu réel du diff, indépendamment du hash
    ou du message de commit (même principe que `git cherry`, voir
    `get_chaine_cherry`), utilisée pour retrouver précisément quel commit de
    la branche cible correspond à un commit orphelin diagnostiqué doublon
    (cas B, bouton « Comparer », issue #30). Retourne None si le commit est
    introuvable ou si le calcul échoue."""
    diff = _lancer_git(repertoire, "show", "--no-color", hash_commit)
    if diff.returncode != 0:
        return None
    patch_id = _lancer_git(repertoire, "patch-id", "--stable", entree=diff.stdout)
    if patch_id.returncode != 0:
        return None
    lignes = patch_id.stdout.strip().splitlines()
    return lignes[0].split()[0] if lignes else None


def trouver_commit_correspondant(repertoire, branche_cible, hash_commit):
    """Retrouve, dans `branche_cible`, le commit dont le contenu (empreinte
    de patch, `git patch-id`) correspond exactement à `hash_commit` (bouton
    « Comparer », issue #30) — répond à la question que le diagnostic cas B
    (voir `_diagnostiquer_commit`) laisse ouverte : `git cherry` indique
    qu'un contenu équivalent existe déjà dans `branche_cible` sans jamais
    dire sous quel hash précis. Ne cherche que parmi les commits propres à
    `branche_cible` depuis sa base commune avec `hash_commit` (même
    périmètre de comparaison que celui utilisé par `git cherry` lui-même),
    pas tout l'historique du dépôt.

    `branche_cible` peut être une liste (projet à plusieurs cibles
    configurées, issue #41/#46) : contrairement au diagnostic automatique
    (case 'M', voir `diagnostiquer_commits_orphelins`) qui évite tout calcul
    supplémentaire sur l'ensemble des commits orphelins, une recherche
    déclenchée à la demande par le bouton « Comparer » ne porte que sur un
    seul commit — essayer chaque branche candidate à tour de rôle reste donc
    négligeable, et permet au bouton de rester utilisable tel quel dans ce
    cas plutôt que d'échouer.

    Retourne le hash exact trouvé, ou None si aucune empreinte ne
    correspond — contenu légèrement retouché entre-temps malgré le verdict
    « doublon » de `git cherry`, aucune branche candidate ne contenant ce
    contenu, ou branche cible non configurée. À l'appelant de distinguer ce
    cas plutôt que d'afficher un mauvais candidat (voir
    `comparer_commit_doublon`)."""
    if not branche_cible:
        return None

    if isinstance(branche_cible, list):
        for candidate in branche_cible:
            trouve = trouver_commit_correspondant(repertoire, candidate, hash_commit)
            if trouve:
                return trouve
        return None

    base = _lancer_git(repertoire, "merge-base", branche_cible, hash_commit)
    if base.returncode != 0 or not base.stdout.strip():
        return None
    base_commune = base.stdout.strip()

    patch_id_cible = get_patch_id_commit(repertoire, hash_commit)
    if not patch_id_cible:
        return None

    log = _lancer_git(repertoire, "log", "--no-color", "-p", f"{base_commune}..{branche_cible}")
    if log.returncode != 0 or not log.stdout.strip():
        return None

    patch_ids = _lancer_git(repertoire, "patch-id", "--stable", entree=log.stdout)
    if patch_ids.returncode != 0:
        return None

    for ligne in patch_ids.stdout.splitlines():
        empreinte, _, sha = ligne.strip().partition(" ")
        if empreinte == patch_id_cible and sha.strip():
            return sha.strip()
    return None


def get_diff_entre_commits(repertoire, hash_a, hash_b):
    """Diff complet entre deux commits (`git diff`), pour affichage brut
    (bouton « Comparer », issue #30) — pour un vrai doublon détecté par
    `trouver_commit_correspondant`, attendu vide ou quasi vide. Retourne
    None si la commande git échoue."""
    resultat = _lancer_git(repertoire, "diff", "--no-color", hash_a, hash_b)
    if resultat.returncode != 0:
        return None
    return resultat.stdout


def comparer_commit_doublon(repertoire, branche_cible, hash_commit):
    """Assemble la comparaison affichée par le bouton « Comparer » (issue
    #30) pour un commit orphelin diagnostiqué doublon (cas B) : retrouve le
    commit correspondant exact de `branche_cible` (via
    `trouver_commit_correspondant`) et le diff entre les deux (via
    `get_diff_entre_commits`). Distingue explicitement l'absence de
    correspondance exacte d'un échec technique, pour ne jamais afficher un
    mauvais candidat ni échouer silencieusement — décision de principe du
    chantier : le diagnostic automatique aide à prioriser, il ne doit
    jamais empêcher une vérification humaine directe.

    Retourne {trouve, hash_correspondant, sujet_correspondant, diff,
    message_absence, vide}."""
    if get_commit_est_vide(repertoire, hash_commit):
        return {
            "trouve": False,
            "hash_correspondant": None,
            "sujet_correspondant": None,
            "diff": None,
            "message_absence": "Commit vide — rien à comparer, aucune action requise.",
            "vide": True,
        }

    hash_correspondant = trouver_commit_correspondant(repertoire, branche_cible, hash_commit)
    if not hash_correspondant:
        cibles_affichees = (
            " ou ".join(branche_cible) if isinstance(branche_cible, list) else branche_cible
        )
        message_absence = (
            "Branche cible de comparaison non configurée pour ce projet."
            if not branche_cible else
            "Aucun commit correspondant précis n'a pu être identifié automatiquement dans "
            f"« {cibles_affichees} » (empreinte de patch différente de tous les commits comparés "
            "— le contenu a peut-être été légèrement retouché entre-temps, malgré le verdict "
            "« doublon » de git cherry)."
        )
        return {
            "trouve": False,
            "hash_correspondant": None,
            "sujet_correspondant": None,
            "diff": None,
            "message_absence": message_absence,
        }

    return {
        "trouve": True,
        "hash_correspondant": hash_correspondant,
        "sujet_correspondant": get_sujet_commit(repertoire, hash_correspondant),
        "diff": get_diff_entre_commits(repertoire, hash_commit, hash_correspondant),
        "message_absence": None,
    }


def get_branches_distantes_contenant(repertoire, hash_commit):
    """Branches distantes (remote-tracking) contenant `hash_commit` (`git
    branch -r --contains`) — pendant côté distant de `get_branches_contenant`,
    pour le rapport de diagnostic manuel (issue #22) : l'absence de branche
    locale ne dit rien de ce qui existe déjà côté distant."""
    resultat = _lancer_git(
        repertoire, "branch", "-r", "--list", "--contains", hash_commit,
        "--format=%(refname:short)",
    )
    if resultat.returncode != 0:
        return []
    return [l.strip() for l in resultat.stdout.splitlines() if l.strip()]


def diagnostiquer_commits_orphelins(repertoire, branche_cible, hashes_orphelins):
    """Classe chaque commit orphelin `hashes_orphelins` (aucune branche
    locale ne le contient, voir `regrouper_resumes_par_branche`) selon la
    table de l'issue #21, à l'aide de `git cherry` contre `branche_cible` :
      - 'M' si plusieurs branches cibles sont configurées pour le projet
        (`branche_cible` est une liste, issue #41) : choisir automatiquement
        la plus pertinente impliquerait de croiser chaque commit orphelin
        avec chaque branche candidate (`git cherry`/`merge-base`), un coût
        qui a déjà fait échouer par timeout une tentative en ce sens sur un
        historique volumineux (`scrabble`, issue #46) — on ne devine rien,
        aucune commande git supplémentaire n'est lancée, la vérification
        reste manuelle via le bouton « Comparer » (issue #30/#32) ;
      - 'E' si `branche_cible` n'est pas configurée (rien à comparer, on ne
        devine rien) ;
      - 'D' si le commit lui-même ne modifie aucun fichier (backup) ;
      - 'F' si `git cherry` échoue ou renvoie une sortie inattendue pour ce
        commit (ambigu, laissé à un traitement à part) ;
      - 'A' si le contenu du commit est absent de `branche_cible` (vrai
        travail non intégré, à merger) ;
      - 'B' si le contenu est déjà présent dans `branche_cible` sous un
        autre hash (doublon confirmé, nettoyable comme un commit pushé).

    Un commit orphelin qui apparaît comme ancêtre dans la chaîne d'un autre
    commit orphelin (case C, chaîne de commits liés) est fusionné dans
    l'entrée de ce dernier plutôt que signalé séparément — `git cherry`
    renvoie déjà toute la chaîne depuis la base commune, donc un tel
    ancêtre apparaît dans `chaine` de l'entrée du commit le plus récent, et
    son hash est listé dans `orphelins_absorbes` de cette entrée.

    Retourne une liste de diagnostics {hash, cas, chaine, orphelins_absorbes},
    un par commit orphelin non absorbé dans la chaîne d'un autre."""
    if isinstance(branche_cible, list):
        return [
            {"hash": h, "cas": "M", "chaine": [], "orphelins_absorbes": []}
            for h in hashes_orphelins
        ]

    if not branche_cible:
        return [
            {"hash": h, "cas": "E", "chaine": [], "orphelins_absorbes": []}
            for h in hashes_orphelins
        ]

    ensemble_orphelins = set(hashes_orphelins)
    diagnostics = {}
    absorbes_global = set()

    for h in hashes_orphelins:
        diagnostic = _diagnostiquer_commit(repertoire, branche_cible, h)
        if diagnostic["cas"] in ("D", "F"):
            diagnostics[h] = {"hash": h, "cas": diagnostic["cas"], "chaine": [], "orphelins_absorbes": []}
            continue

        chaine = diagnostic["chaine"]
        maillon_tip = diagnostic["maillon_tip"]
        orphelins_absorbes = [
            autre for autre in ensemble_orphelins
            if autre != h and any(m["hash"].startswith(autre) for m in chaine if m is not maillon_tip)
        ]
        absorbes_global.update(orphelins_absorbes)

        diagnostics[h] = {
            "hash": h,
            "cas": diagnostic["cas"],
            "chaine": chaine,
            "orphelins_absorbes": orphelins_absorbes,
        }

    return [diag for h, diag in diagnostics.items() if h not in absorbes_global]


def _diagnostiquer_commit(repertoire, branche_cible, hash_commit):
    """Diagnostic d'un unique commit contre `branche_cible` (cas D/F/A/B de
    la table de l'issue #21, cas E exclu — à la charge de l'appelant quand
    `branche_cible` n'est pas configurée), sans la logique d'absorption de
    chaîne propre à `diagnostiquer_commits_orphelins` — brique commune,
    réutilisée telle quelle par cette dernière et par
    `get_diagnostic_doublons_branche` pour les branches `recuperation-<hash>`
    (issue #27), où seul le diagnostic du commit visé importe, pas celui de
    toute la chaîne de divergence remontée par `git cherry`."""
    if get_commit_est_vide(repertoire, hash_commit):
        return {"cas": "D", "chaine": [], "maillon_tip": None}

    chaine = get_chaine_cherry(repertoire, branche_cible, hash_commit)
    maillon_tip = (
        next((m for m in chaine if m["hash"].startswith(hash_commit)), None) if chaine else None
    )
    if chaine is None or maillon_tip is None:
        return {"cas": "F", "chaine": [], "maillon_tip": None}

    return {
        "cas": "A" if maillon_tip["statut"] == "nouveau" else "B",
        "chaine": chaine,
        "maillon_tip": maillon_tip,
    }


def extraire_numero_issue(sujet):
    """Numéro d'issue référencé dans un message de commit (motif `#123`), ou
    None si absent — indice indépendant de la comparaison de contenu
    `git cherry`, utilisé pour repérer un cas A potentiellement reformulé
    (issue #28)."""
    if not sujet:
        return None
    correspondance = re.search(r"#(\d+)", sujet)
    return correspondance.group(1) if correspondance else None


def get_issue_deja_referencee(repertoire, branche_cible, numero_issue):
    """True si au moins un commit de `branche_cible` référence `numero_issue`
    dans son message (motif `#<numero_issue>`, bordé pour ne pas confondre
    `#12` et `#123`) — indice qu'un commit orphelin classé cas A (nouveau,
    voir `_diagnostiquer_commit`) pourrait en réalité être un doublon
    reformulé du même sujet (variables renommées, logique réorganisée) que
    `git cherry` ne peut pas détecter par comparaison de contenu (issue #28).
    Ne remplace pas la vérification humaine : le numéro peut coïncider avec
    un sujet réellement différent."""
    if not branche_cible or not numero_issue:
        return False
    resultat = _lancer_git(
        repertoire, "log", branche_cible, "--oneline", "--extended-regexp",
        f"--grep=#{numero_issue}([^0-9]|$)",
    )
    if resultat.returncode != 0:
        return False
    return bool(resultat.stdout.strip())


def nom_branche_recuperation(hash_commit):
    """Nom de la branche de sécurisation d'un commit orphelin — même
    convention que le geste manuel déjà pratiqué (issue #23) :
    `git branch recuperation-<hash> <hash>`."""
    return f"recuperation-{hash_commit}"


def hash_depuis_branche_recuperation(nom_branche):
    """Inverse de `nom_branche_recuperation` : le hash orphelin visé si
    `nom_branche` suit la convention `recuperation-<hash>`, sinon None —
    utilisé par `get_diagnostic_doublons_branche` (issue #27) pour repérer
    les branches de récupération, qui ne contiennent par construction qu'un
    seul commit d'intérêt."""
    prefixe = "recuperation-"
    if not nom_branche.startswith(prefixe):
        return None
    return nom_branche[len(prefixe):] or None


def commit_est_securise(repertoire, hash_commit):
    """True si une branche de sécurisation (voir `nom_branche_recuperation`)
    existe déjà pour ce commit — évite de recréer inutilement la branche et
    permet d'afficher l'état déjà sécurisé plutôt qu'un bouton d'action."""
    resultat = _lancer_git(
        repertoire, "rev-parse", "--verify", "--quiet",
        f"refs/heads/{nom_branche_recuperation(hash_commit)}",
    )
    return resultat.returncode == 0


def securiser_commit_orphelin(repertoire, hash_commit):
    """Sécurise un commit orphelin (aucune branche locale ne le contient,
    donc retenu uniquement par le reflog — 90 jours par défaut, purgeable
    ensuite par un `git gc`) en créant une branche `recuperation-<hash>`
    pointant dessus (issue #23) — geste défensif pur, qui ne fusionne ni ne
    modifie rien, identique au geste manuel déjà pratiqué sur ff_galerie.

    N'a besoin d'aucun diagnostic préalable (cas A-F, voir
    `diagnostiquer_commits_orphelins`) : s'applique à n'importe quel commit
    orphelin, tranché ou non. Idempotent : si la branche existe déjà,
    retourne ok=True avec `deja_securise=True` sans relancer git branch.
    Retourne {ok, deja_securise, erreur, commande, nom_branche} pour
    affichage transparent."""
    nom_branche = nom_branche_recuperation(hash_commit)
    if commit_est_securise(repertoire, hash_commit):
        return {
            "ok": True, "deja_securise": True, "erreur": None,
            "commande": None, "nom_branche": nom_branche,
        }

    commande = ["git", "-C", repertoire, "branch", nom_branche, hash_commit]
    resultat = _lancer_git(repertoire, "branch", nom_branche, hash_commit)
    return {
        "ok": resultat.returncode == 0,
        "deja_securise": False,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
        "nom_branche": nom_branche,
    }


def get_commit_est_pushe(repertoire, hash_commit):
    """True si `hash_commit` est déjà un ancêtre d'au moins une branche
    distante (`git branch -r --contains`) — donc en sécurité sur le dépôt
    distant, indépendamment de la branche locale d'origine (qui peut avoir
    été supprimée depuis)."""
    resultat = _lancer_git(repertoire, "branch", "-r", "--contains", hash_commit)
    if resultat.returncode != 0:
        return False
    return bool(resultat.stdout.strip())


def get_remote_defaut(repertoire):
    """Nom du remote à utiliser pour un push (`origin` si présent, sinon le
    premier remote configuré, sinon `origin` par défaut pour affichage)."""
    resultat = _lancer_git(repertoire, "remote")
    if resultat.returncode != 0:
        return "origin"
    noms = [l.strip() for l in resultat.stdout.splitlines() if l.strip()]
    if "origin" in noms:
        return "origin"
    return noms[0] if noms else "origin"


MOTIF_CHANGELOG_WORKTREE = re.compile(r"^CHANGELOG-\d+\.md$")

# Journal persistant des tentatives de fusion automatique du CHANGELOG —
# le message flash (app.py) n'est visible qu'une fois, juste après l'action ;
# ce fichier permet de vérifier après coup si une fusion a réussi ou échoué
# pour un merge donné, même si Alain n'a pas regardé le flash au bon moment
# (issue #62). Propre à relecture_web, pas commité (voir .gitignore).
CHEMIN_JOURNAL_FUSION_CHANGELOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "changelog_fusion.log"
)

# Script de fusion CHANGELOG-<N>.md -> CHANGELOG.md : toujours celui de CE
# dépôt (relecture_bridge), résolu à partir de l'emplacement de ce fichier
# (relecture_web/git_info.py est à un niveau sous la racine du dépôt, comme
# scripts/) — jamais une copie potentiellement absente dans le dépôt cible
# (issue #87 : le merge sur chesscoach échouait avec « script introuvable »
# faute d'une telle copie, alors que seuls quelques projets en possèdent
# une). `--repo` cible ensuite le dépôt sur lequel la fusion doit avoir lieu.
CHEMIN_SCRIPT_FUSION_CHANGELOG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts", "fusionner_changelog.py",
)


def _journaliser_fusion_changelog(nom_projet, commande, ok, erreur):
    """Ajoute une ligne au journal persistant des tentatives de fusion du
    CHANGELOG (voir CHEMIN_JOURNAL_FUSION_CHANGELOG). N'échoue jamais de
    façon visible pour l'utilisateur : une erreur d'écriture du journal ne
    doit pas faire échouer la fusion elle-même."""
    horodatage = datetime.datetime.now().isoformat(timespec="seconds")
    statut = "SUCCES" if ok else "ECHEC"
    ligne = f"{horodatage} | projet={nom_projet} | commande={commande} | resultat={statut}"
    if erreur:
        ligne += f" | erreur={erreur}"
    try:
        with open(CHEMIN_JOURNAL_FUSION_CHANGELOG, "a", encoding="utf-8") as fichier:
            fichier.write(ligne + "\n")
    except OSError:
        pass


def fusionner_changelog_worktree(repertoire, nom_projet=None):
    """Si la fusion qui vient d'avoir lieu dans `repertoire` a introduit un
    ou plusieurs `CHANGELOG-<N>.md` à la racine du dépôt (chaque worktree
    mode_write écrit le sien plutôt que dans `CHANGELOG.md` directement,
    pour éviter les conflits entre worktrees actifs en parallèle — issue
    #577 côté Bridge_Agent), lance `scripts/fusionner_changelog.py` — celui
    de CE dépôt (relecture_bridge, voir CHEMIN_SCRIPT_FUSION_CHANGELOG),
    jamais une copie du dépôt cible qui peut ne pas en avoir (issue #87) —
    pour les intégrer dans `CHANGELOG.md`, geste qu'Alain devait jusqu'ici
    penser à faire lui-même à chaque merge (issue #51). Retourne None si aucun
    `CHANGELOG-<N>.md` trouvé (rien à fusionner, pas de message nécessaire),
    sinon {ok, erreur, commande} pour affichage transparent — jamais
    d'échec silencieux même si le script est absent. Chaque tentative
    réellement lancée (script trouvé ou non) est aussi journalisée dans
    CHEMIN_JOURNAL_FUSION_CHANGELOG, indépendamment du message flash
    (issue #62)."""
    try:
        fichiers_changelog = sorted(
            nom for nom in os.listdir(repertoire) if MOTIF_CHANGELOG_WORKTREE.match(nom)
        )
    except OSError:
        fichiers_changelog = []
    if not fichiers_changelog:
        return None

    nom_projet = nom_projet or os.path.basename(os.path.normpath(repertoire))
    script = CHEMIN_SCRIPT_FUSION_CHANGELOG
    commande = ["python3", script, "--repo", repertoire]
    commande_str = " ".join(commande)
    if not os.path.isfile(script):
        erreur = f"script introuvable : {script}"
        _journaliser_fusion_changelog(nom_projet, commande_str, False, erreur)
        return {
            "ok": False,
            "erreur": erreur,
            "commande": commande_str,
        }

    # `commande` lance un script Python, pas une commande git : reste hors
    # de la centralisation _lancer_git de l'issue #93 (routage local/SSH à
    # venir), donc une deuxième surface d'exécution distincte de git dans ce
    # module, à garder à l'esprit pour une éventuelle issue de suivi.
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    if resultat.returncode != 0:
        return {
            "ok": False,
            "erreur": (resultat.stderr or resultat.stdout).strip(),
            "commande": " ".join(commande),
        }

    # Le script fusionner_changelog.py modifie CHANGELOG.md et supprime les
    # CHANGELOG-<N>.md sur disque mais ne commite rien lui-même — sans ce
    # commit immédiat, ce résultat reste une modification non indexée du
    # dépôt. `fusionner_worktree` (l'appelant) bascule ensuite potentiellement
    # sur une autre branche (`doit_basculer`) : un `git checkout` avec un
    # `CHANGELOG.md` modifié en local est refusé par git dès que la branche
    # de destination diffère sur ce fichier, ce qui bloque le retour de
    # branche silencieusement (voir `fusionner_worktree`) — et si le dépôt
    # reste malgré tout praticable et que ces changements non commités sont
    # ensuite écrasés (checkout, reset, etc. fait par ailleurs), la fusion se
    # trouve annulée sans qu'aucun message ne l'ait jamais signalé comme un
    # échec (cause du bug #63 : CHANGELOG-585.md/586.md restés non fusionnés
    # malgré un script qui, lui, réussissait). Committer ici rend la fusion
    # durable dès son exécution, indépendamment de ce que fait l'appelant
    # ensuite.
    #
    # Portée strictement limitée à CHANGELOG.md et aux CHANGELOG-<N>.md
    # consommés (`git add -- <chemins>` puis `git commit -- <mêmes chemins>`,
    # jamais `git commit -a`/`git add -A`) : `repertoire` est le worktree
    # PRINCIPAL du projet, potentiellement le même dossier où un autre CCL
    # travaille encore en repli sur REP_TRAVAIL (worktree dédié « déjà pris »)
    # — `-a` aurait alors indexé et commité tout son travail inachevé sous ce
    # message générique (issue #74, cause du commit 0c477c0 pendant l'issue
    # #73). `git commit -- <pathspec>` ne committe que ces chemins précis même
    # si l'index contient par ailleurs d'autres modifications déjà stagées
    # par un tiers, indépendamment de ce qui vient d'être `git add`é ici.
    chemins_changelog = ["CHANGELOG.md"] + fichiers_changelog
    ajout = _lancer_git(repertoire, "add", "--", *chemins_changelog)
    if ajout.returncode != 0:
        return {
            "ok": False,
            "erreur": "fusion effectuée mais git add impossible : "
                      + (ajout.stderr or ajout.stdout).strip(),
            "commande": " ".join(commande),
        }

    commit = _lancer_git(
        repertoire, "commit", "-m",
        "chore: fusionne CHANGELOG-<N>.md dans CHANGELOG.md (auto)",
        "--", *chemins_changelog,
    )
    if commit.returncode != 0:
        return {
            "ok": False,
            "erreur": "fusion effectuée mais commit impossible : "
                      + (commit.stderr or commit.stdout).strip(),
            "commande": " ".join(commande),
        }

    return {"ok": True, "erreur": None, "commande": " ".join(commande)}


def get_modifications_non_committees(repertoire):
    """Fichiers suivis modifiés ou fichiers non suivis non ignorés dans
    `repertoire` (`git status --porcelain=v1`, qui exclut déjà les fichiers
    ignorés par construction) — précondition du garde-fou avant Merger
    (issue #74) : un dépôt dans cet état au moment de lancer un merge peut
    signifier qu'une tâche CCL y travaille encore, repliée sur ce même
    dossier faute de worktree dédié disponible (comme lors de l'issue #73,
    où l'intégration automatique du CHANGELOG avait alors committé ce
    travail en cours par-dessus). Contrairement à `get_fichiers_en_conflit`
    (qui ne repère que les chemins non fusionnés d'un merge déjà en cours),
    signale ici tout écart par rapport à un arbre de travail propre, fusion
    en cours ou non.

    Retourne une liste de chemins (vide = arbre propre), ou une liste vide
    aussi si la commande échoue — comportement permissif par défaut, comme
    les autres fonctions de lecture d'état de ce module, pour ne jamais
    bloquer un merge légitime à cause d'une erreur d'exécution git elle-même
    plutôt que d'un vrai état non committé."""
    resultat = _lancer_git(repertoire, "status", "--porcelain=v1")
    if resultat.returncode != 0:
        return []
    return [ligne[3:].strip() for ligne in resultat.stdout.splitlines() if ligne.strip()]


def fusionner_worktree(repertoire, branche_cible, branche_source, nom_projet=None):
    """Fusionne `branche_source` dans `branche_cible` (comme un `git merge`
    manuel), sans jamais pousser. Si `branche_cible` n'est pas la branche
    actuellement extraite dans `repertoire` (projet avec une branche cible
    de comparaison différente de la branche principale git — voir
    `get_branche_cible_comparaison`, issue #20), bascule dessus le temps de
    la fusion puis revient sur la branche d'origine, seule façon de
    fusionner dans une branche qui n'a pas de worktree dédié déjà extrait
    dessus. Un conflit laisse volontairement le dépôt sur `branche_cible`
    en état de fusion non résolue (pas de retour en arrière), pour ne pas
    perdre l'information. Après une fusion réussie, tente aussi d'intégrer
    un éventuel `CHANGELOG-<N>.md` introduit par la branche source (voir
    `fusionner_changelog_worktree`, issue #51) — toujours avant la bascule
    de retour, pendant que `branche_cible` est encore extraite dans
    `repertoire`. Retourne {ok, erreur, commande, changelog,
    erreur_retour_branche} pour affichage transparent (`changelog` vaut None
    si aucun CHANGELOG-<N>.md n'était à fusionner ; `erreur_retour_branche`
    n'est renseigné que si la bascule de retour vers la branche d'origine a
    échoué après une fusion par ailleurs réussie)."""
    branche_courante = get_branche_courante(repertoire)
    doit_basculer = branche_courante is not None and branche_courante != branche_cible

    if doit_basculer:
        bascule = _lancer_git(repertoire, "checkout", branche_cible)
        if bascule.returncode != 0:
            return {
                "ok": False,
                "erreur": (bascule.stderr or bascule.stdout).strip(),
                "commande": commande_affichee(repertoire, f"git -C {repertoire} checkout {branche_cible}"),
                "changelog": None,
            }

    commande = ["git", "-C", repertoire, "merge", branche_source]
    resultat = _lancer_git(repertoire, "merge", branche_source, timeout=TIMEOUT_GIT_LONG)

    resultat_changelog = None
    if resultat.returncode == 0:
        resultat_changelog = fusionner_changelog_worktree(repertoire, nom_projet)

    erreur_retour_branche = None
    if doit_basculer and resultat.returncode == 0:
        retour = _lancer_git(repertoire, "checkout", branche_courante)
        if retour.returncode != 0:
            # Ne doit plus arriver depuis que fusionner_changelog_worktree
            # commite son résultat (le dépôt est donc propre au moment de ce
            # checkout), mais gardé signalé plutôt que silencieux en cas
            # d'autre cause (conflit sans lien avec le changelog, etc.) —
            # avant ce correctif, ce retour n'était jamais vérifié, ce qui a
            # laissé passer le bug #63 sans aucun message d'erreur.
            erreur_retour_branche = (
                f"la fusion a réussi mais le retour sur « {branche_courante} » "
                f"a échoué : {(retour.stderr or retour.stdout).strip()} — "
                f"le dépôt est resté sur « {branche_cible} »"
            )

    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
        "changelog": resultat_changelog,
        "erreur_retour_branche": erreur_retour_branche,
    }


def verifier_merge_apres_timeout(repertoire, branche_cible, branche_source):
    """Après un `TimeoutExpired` sur `fusionner_worktree` (issue #66) —
    détermine l'état réel de la fusion en relisant le dépôt plutôt que de
    renvoyer Alain vers une vérification manuelle en ligne de commande.
    Trois issues distinctes : fusion aboutie (`branche_source` est devenue
    un ancêtre de `branche_cible`), fusion arrêtée sur des conflits
    (`MERGE_HEAD` toujours présent — pas un échec à proprement parler, la
    page de résolution de conflits prend normalement le relais), ou fusion
    non aboutie (ni l'un ni l'autre, le merge n'a probablement même pas pu
    démarrer). Retourne {etat, erreur} où `etat` vaut "reussie",
    "conflits_en_attente", "non_aboutie" ou "indetermine" (uniquement si la
    vérification elle-même échoue, auquel cas `erreur` est renseignée)."""
    if get_merge_en_cours(repertoire):
        return {"etat": "conflits_en_attente", "erreur": None}

    resultat = _lancer_git(repertoire, "merge-base", "--is-ancestor", branche_source, branche_cible)
    if resultat.returncode == 0:
        return {"etat": "reussie", "erreur": None}
    if resultat.returncode == 1:
        return {"etat": "non_aboutie", "erreur": None}
    return {"etat": "indetermine", "erreur": (resultat.stderr or resultat.stdout).strip()}


def verifier_finalisation_merge_apres_timeout(repertoire):
    """Après un `TimeoutExpired` sur `finaliser_commit_merge` (issue #66) —
    dans ce flux, le seul moyen connu de faire disparaître `MERGE_HEAD` est
    le commit visé par `finaliser_commit_merge` lui-même (personne d'autre
    n'a lancé de `merge --abort` en parallèle) : sa disparition signale donc
    de façon fiable que le commit a bien été créé avant que le timeout
    Python ne tue le process (probablement resté bloqué dans un hook
    post-commit). Retourne {ok} : True si le merge est bien finalisé
    (`MERGE_HEAD` disparu), False s'il est toujours en attente."""
    return {"ok": not get_merge_en_cours(repertoire)}


def supprimer_worktree(repertoire, chemin_worktree):
    """Supprime un worktree via `git worktree remove`, jamais forcé (donc git
    refuse de lui-même si le worktree a des modifications non commitées).
    Retourne {ok, erreur, commande} pour affichage transparent."""
    commande = ["git", "-C", repertoire, "worktree", "remove", chemin_worktree]
    resultat = _lancer_git(repertoire, "worktree", "remove", chemin_worktree)
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
    }


def supprimer_branche(repertoire, nom_branche):
    """Supprime définitivement une branche locale (`git branch -D
    <nom_branche>`) — utilisé pour une branche confirmée fusionnée dont le
    worktree a déjà été retiré (manuellement ou autrement), cas où
    `supprimer_worktree` ne peut plus rien puisqu'il n'y a plus de dossier de
    worktree à retirer (issue #43). Contrairement à
    `supprimer_branche_recuperation`, aucune contrainte de nommage n'est
    imposée ici : la sécurité vient de la vérification `mergee` faite par
    l'appelant avant l'appel, exactement comme pour `supprimer_worktree`.
    Retourne {ok, erreur, commande} pour affichage transparent."""
    commande = ["git", "-C", repertoire, "branch", "-D", nom_branche]
    resultat = _lancer_git(repertoire, "branch", "-D", nom_branche)
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
    }


def supprimer_branche_recuperation(repertoire, nom_branche):
    """Supprime définitivement une branche de récupération (`git branch -D
    <nom_branche>`) — contrairement à `supprimer_worktree`, ces branches
    (créées par `securiser_commit_orphelin`, issue #23) n'ont jamais de
    worktree associé, donc `git worktree remove` échoue sans effet dessus
    (issue #29).

    Protection structurelle : refuse toute branche dont le nom ne suit pas
    exactement la convention `recuperation-<hash>` (via
    `hash_depuis_branche_recuperation`), sans même tenter la commande git —
    indépendant du diagnostic de doublons affiché côté template, pour que
    `dev`, `main` ou une branche de travail ordinaire ne puissent jamais
    passer par cette fonction, même en cas d'erreur de diagnostic amont.
    Retourne {ok, erreur, commande} pour affichage transparent."""
    if hash_depuis_branche_recuperation(nom_branche) is None:
        return {
            "ok": False,
            "erreur": f"« {nom_branche} » ne suit pas la convention recuperation-<hash>, suppression refusée.",
            "commande": None,
        }

    commande = ["git", "-C", repertoire, "branch", "-D", nom_branche]
    resultat = _lancer_git(repertoire, "branch", "-D", nom_branche)
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
    }


def revert_commit(repertoire, hash_commit):
    """Annule `hash_commit` via `git revert --no-edit` : crée un nouveau
    commit d'annulation, indépendant des autres commits de la branche
    (contrairement au push, pas de contrainte d'ordre). Retourne
    {ok, erreur, commande} pour affichage transparent."""
    commande = ["git", "-C", repertoire, "revert", "--no-edit", hash_commit]
    resultat = _lancer_git(repertoire, "revert", "--no-edit", hash_commit)
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
    }


def pousser_branche(repertoire, branche):
    """Pousse `branche` jusqu'à son dernier commit vers le remote par défaut
    (`git push <remote> <branche>`) — un push cible toujours une branche
    entière jusqu'à un point donné, jamais une sélection de commits épars.
    Retourne {ok, erreur, commande} pour affichage transparent."""
    remote = get_remote_defaut(repertoire)
    commande = ["git", "-C", repertoire, "push", remote, branche]
    resultat = _lancer_git(repertoire, "push", remote, branche, timeout=TIMEOUT_GIT_LONG)
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
    }


def verifier_push_apres_timeout(repertoire, branche):
    """Après un `TimeoutExpired` sur `pousser_branche` (issue #66) — le
    process git a pu être tué localement par le timeout Python juste après
    que le remote a accepté le push mais avant que la confirmation réseau
    ne revienne, laissant croire à un échec alors que le push a abouti.
    Compare le commit local de `branche` au commit que le remote expose
    réellement via `git ls-remote` (pas le suivi local `refs/remotes/...`,
    qui ne serait mis à jour que par un `fetch` et pourrait donc rester
    périmé). Retourne {ok, hash_local, hash_distant, erreur} : `ok` vaut
    True si les deux hash coïncident (push confirmé abouti), False s'ils
    diffèrent ou si la branche est absente côté remote (push non abouti),
    None si l'état n'a pas pu être déterminé (erreur réseau/git lors de la
    vérification elle-même — dans ce cas seulement, `erreur` est renseignée)."""
    local = _lancer_git(repertoire, "rev-parse", f"refs/heads/{branche}")
    if local.returncode != 0:
        return {"ok": None, "hash_local": None, "hash_distant": None, "erreur": "branche locale introuvable"}
    hash_local = local.stdout.strip()

    remote = get_remote_defaut(repertoire)
    try:
        resultat = _lancer_git(
            repertoire, "ls-remote", remote, f"refs/heads/{branche}", timeout=TIMEOUT_RESEAU
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": None, "hash_local": hash_local, "hash_distant": None,
            "erreur": "la vérification réseau elle-même a dépassé son délai",
        }
    if resultat.returncode != 0:
        return {
            "ok": None, "hash_local": hash_local, "hash_distant": None,
            "erreur": (resultat.stderr or resultat.stdout).strip(),
        }

    ligne = resultat.stdout.strip()
    if not ligne:
        return {"ok": False, "hash_local": hash_local, "hash_distant": None, "erreur": None}
    hash_distant = ligne.split()[0]
    return {"ok": hash_distant == hash_local, "hash_local": hash_local, "hash_distant": hash_distant, "erreur": None}


def get_commits_en_attente(chemin_worktree):
    """Commits locaux non poussés vers la branche amont configurée."""
    amont = _lancer_git(
        chemin_worktree, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
    )
    if amont.returncode != 0:
        return {"amont": None, "commits": [], "erreur": "aucune branche amont configurée"}

    nom_amont = amont.stdout.strip()
    log = _lancer_git(
        chemin_worktree, "log", "--oneline",
        f"{nom_amont}..HEAD", "-n", str(MAX_COMMITS_AFFICHES),
    )
    if log.returncode != 0:
        return {"amont": nom_amont, "commits": [], "erreur": "lecture des commits impossible"}

    commits = [l for l in log.stdout.splitlines() if l.strip()]
    return {"amont": nom_amont, "commits": commits, "erreur": None}


# Codes à deux lettres que `git status --porcelain=v1` utilise pour un
# chemin « non fusionné » (issue #55) — `UU` (modifié des deux côtés) est
# de loin le plus fréquent en pratique sur ce dépôt (worktrees fusionnés en
# parallèle), mais les combinaisons ajout/suppression en conflit existent
# aussi et sont tout autant des conflits de fusion non résolue.
CODES_CONFLIT_FUSION = {"DD", "AU", "UD", "UA", "DU", "AA", "UU"}


def get_fichiers_en_conflit(repertoire):
    """Fichiers en conflit de fusion non résolue dans `repertoire` (issue
    #55) — lecture seule pure, aucune commande git de modification. Détecte
    via `git status --porcelain=v1` : chaque ligne commence par un code à
    deux lettres (XY) suivi d'un espace puis du chemin ; un des codes de
    `CODES_CONFLIT_FUSION` signale un chemin non fusionné. Retourne une
    liste vide si le dépôt n'est pas en état de fusion non résolue, ou si
    la commande échoue."""
    resultat = _lancer_git(repertoire, "status", "--porcelain=v1")
    if resultat.returncode != 0:
        return []

    fichiers = []
    for ligne in resultat.stdout.splitlines():
        if len(ligne) < 4:
            continue
        code, chemin = ligne[:2], ligne[3:]
        if code not in CODES_CONFLIT_FUSION:
            continue
        if chemin.startswith('"') and chemin.endswith('"'):
            # git status entoure de guillemets (et échappe) les chemins
            # contenant des caractères spéciaux — retire juste les
            # guillemets, cas rare sur ces projets.
            chemin = chemin[1:-1]
        fichiers.append({"chemin": chemin, "code": code})
    return fichiers


_MARQUEUR_DEBUT = "<<<<<<<"
_MARQUEUR_SEPARATEUR = "======="
_MARQUEUR_BASE = "|||||||"
_MARQUEUR_FIN = ">>>>>>>"


def _trouver_blocs_conflit(lignes):
    """Repère chaque bloc de conflit dans une liste de lignes déjà découpée
    (`str.splitlines(keepends=True)`) — factorise le parcours entre
    l'affichage (`_extraire_blocs_conflit`, issue #55) et la résolution
    (`resoudre_bloc_conflit`, issue #56), pour que les deux emploient
    exactement la même numérotation de blocs (0-based, ordre d'apparition
    dans le fichier) et qu'une résolution ne puisse jamais toucher le
    mauvais bloc. Un éventuel bloc de base commune (marqueur `|||||||`,
    présent seulement si `merge.conflictStyle=diff3` est configuré) est
    ignoré : seules les deux versions en conflit sont retenues, pas la base
    à trois voies. Un marqueur ouvert sans fermeture (fichier
    tronqué/corrompu) n'est pas compté comme un bloc.

    Retourne une liste de dicts {debut, fin, entete_ours, texte_ours,
    entete_theirs, texte_theirs} — `debut`/`fin` sont des index dans
    `lignes` ([debut:fin[ couvre tout le bloc, marqueurs compris), pour
    permettre à l'appelant de le remplacer par simple slicing."""
    blocs = []
    i, n = 0, len(lignes)

    while i < n:
        ligne = lignes[i]
        if not ligne.startswith(_MARQUEUR_DEBUT):
            i += 1
            continue

        debut = i
        entete_ours = ligne.rstrip("\n")
        i += 1
        ours = []
        while i < n and not lignes[i].startswith(_MARQUEUR_SEPARATEUR) and not lignes[i].startswith(_MARQUEUR_BASE):
            ours.append(lignes[i])
            i += 1
        if i < n and lignes[i].startswith(_MARQUEUR_BASE):
            i += 1
            while i < n and not lignes[i].startswith(_MARQUEUR_SEPARATEUR):
                i += 1
        if i >= n:
            break
        i += 1  # ligne =======
        theirs = []
        while i < n and not lignes[i].startswith(_MARQUEUR_FIN):
            theirs.append(lignes[i])
            i += 1
        if i >= n:
            break
        entete_theirs = lignes[i].rstrip("\n")
        i += 1

        blocs.append({
            "debut": debut, "fin": i,
            "entete_ours": entete_ours, "texte_ours": "".join(ours),
            "entete_theirs": entete_theirs, "texte_theirs": "".join(theirs),
        })

    return blocs


def _texte_affiche_bloc(bloc):
    """Reconstitue le texte tel qu'affiché dans le panneau gauche pour un
    bloc de conflit (issue #90, bouton « Copier ce bloc ») : l'en-tête
    HEAD, son contenu, l'en-tête de la branche entrante puis son contenu,
    dans l'ordre où `conflit.html` les empile visuellement (chaque saut de
    ligne entre eux n'est ajouté que si le texte qui précède n'en a pas déjà
    un en fin, pour ne jamais dupliquer une ligne vide)."""
    partie_ours = bloc["entete_ours"] + "\n" + bloc["texte_ours"]
    if not partie_ours.endswith("\n"):
        partie_ours += "\n"
    return partie_ours + bloc["entete_theirs"] + "\n" + bloc["texte_theirs"]


def _extraire_blocs_conflit(contenu):
    """Découpe le contenu d'un fichier en conflit en segments alternant
    texte de contexte et blocs de conflit (issue #55), via
    `_trouver_blocs_conflit` — le texte hors conflit doit s'afficher
    normalement autour, pour donner le contexte (demande explicite de
    l'issue). Un marqueur ouvert sans fermeture (fichier tronqué/corrompu)
    rattache le fragment orphelin au contexte plutôt que d'échouer.

    Retourne une liste de segments : {type: 'contexte', texte} ou
    {type: 'conflit', index, entete_ours, texte_ours, entete_theirs,
    texte_theirs, texte_affiche} — `index` (0-based) est la numérotation
    stable du bloc, à renvoyer telle quelle lors d'une résolution (issue
    #56) ; `texte_affiche` (issue #90) est le texte complet du panneau
    gauche pour ce bloc, marqueurs de conflit compris, prêt à copier."""
    lignes = contenu.splitlines(keepends=True)
    blocs = _trouver_blocs_conflit(lignes)

    segments = []
    position = 0
    for index_bloc, bloc in enumerate(blocs):
        contexte = "".join(lignes[position:bloc["debut"]])
        if contexte:
            segments.append({"type": "contexte", "texte": contexte})
        segments.append({
            "type": "conflit",
            "index": index_bloc,
            "entete_ours": bloc["entete_ours"],
            "texte_ours": bloc["texte_ours"],
            "entete_theirs": bloc["entete_theirs"],
            "texte_theirs": bloc["texte_theirs"],
            "texte_affiche": _texte_affiche_bloc(bloc),
        })
        position = bloc["fin"]

    reste = "".join(lignes[position:])
    if reste:
        segments.append({"type": "contexte", "texte": reste})
    return segments


def get_merge_en_cours(repertoire):
    """True si le dépôt de `repertoire` est actuellement en état de fusion
    non finalisée (`MERGE_HEAD` présent, issue #61) — précondition du bouton
    « Finaliser le merge », distincte de `get_fichiers_en_conflit` : celle-ci
    détecte des chemins non fusionnés dans `git status`, mais rien n'indique
    par elle seule qu'un merge est en cours (un revert ou un cherry-pick en
    conflit produit les mêmes codes `UU`/`AA`/etc. sans jamais créer
    `MERGE_HEAD`)."""
    resultat = _lancer_git(repertoire, "rev-parse", "--verify", "--quiet", "MERGE_HEAD")
    return resultat.returncode == 0


def finaliser_commit_merge(repertoire):
    """Finalise un merge dont tous les fichiers en conflit ont déjà été
    résolus (issue #61) : lance `git commit --no-edit`, l'équivalent
    non-interactif de `git commit` sans `-m` — accepte tel quel le message
    déjà préparé par git dans `.git/MERGE_MSG` (résumé des branches
    fusionnées), sans ouvrir d'éditeur, impossible à piloter depuis cette
    interface web.

    Ne revérifie pas elle-même les préconditions (voir `get_merge_en_cours`
    et `get_fichiers_en_conflit`) : à charge de l'appelant de ne l'invoquer
    que lorsque le bouton est réellement proposé, jamais à l'aveugle sur un
    merge partiellement résolu.

    Retourne {ok, erreur, commande} pour affichage transparent."""
    commande = ["git", "-C", repertoire, "commit", "--no-edit"]
    resultat = _lancer_git(repertoire, "commit", "--no-edit", timeout=TIMEOUT_GIT_LONG)
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
    }


def get_fichiers_resolus_merge(repertoire):
    """Fichiers déjà résolus (`git add` fait) pendant le merge en cours,
    mais pour lesquels git conserve encore de quoi annuler cette résolution
    (issue #72) — précondition du bouton « Retraiter le fichier en
    conflit ». Contrairement à ce que documentait initialement l'issue #71,
    un `git add` de résolution n'est pas un point de non-retour individuel :
    git garde ces informations dans son mécanisme « resolve-undo » jusqu'à
    la finalisation du merge (`git commit`), à ce moment précis seulement il
    n'y a plus moyen de revenir en arrière fichier par fichier.

    `git ls-files --resolve-undo -z` liste une ligne par version encore
    connue d'un chemin (base/ours/theirs selon le type de conflit, jusqu'à
    trois lignes pour un même chemin) — `-z` (séparateur NUL) évite toute
    ambiguïté sur un chemin contenant espaces ou caractères spéciaux, comme
    ailleurs dans ce module. Un chemin actuellement en conflit (pas encore
    résolu) n'y figure jamais : ces entrées disparaissent dès qu'il redevient
    non fusionné, donc aucun recoupement possible avec
    `get_fichiers_en_conflit`.

    Retourne une liste de chemins uniques, dans l'ordre de première
    apparition, ou une liste vide si la commande échoue (dépôt introuvable,
    etc.)."""
    resultat = _lancer_git(repertoire, "ls-files", "--resolve-undo", "-z")
    if resultat.returncode != 0:
        return []

    chemins, deja_vus = [], set()
    for entree in resultat.stdout.split("\0"):
        if not entree:
            continue
        _, _, chemin = entree.partition("\t")
        if chemin and chemin not in deja_vus:
            deja_vus.add(chemin)
            chemins.append(chemin)
    return chemins


def retraiter_fichier_conflit(repertoire, chemin_relatif):
    """Remet `chemin_relatif` dans son état de conflit d'origine (issue #72)
    via `git checkout --conflict=merge -- <chemin>` : reconstruit les
    marqueurs `<<<<<<<`/`=======`/`>>>>>>>` à partir des versions encore
    connues par git (voir `get_fichiers_resolus_merge`), effaçant la
    résolution déjà appliquée sur ce fichier. Différence par rapport aux
    marqueurs d'origine (vérifié sur git 2.43) : les libellés redeviennent
    génériques (`ours`/`theirs`) au lieu de `HEAD` et du nom de la branche
    entrante, que git ne conserve pas dans ce mécanisme — à charge de
    l'appelant de le signaler clairement (message flash).

    Échoue proprement, sans rien modifier, sur un conflit ajout/suppression
    (codes `AU`/`UD`/`DU`/`UA` de `get_fichiers_en_conflit`) : l'un des deux
    côtés n'a alors aucune version du fichier, donc rien à placer dans le
    bloc correspondant — git refuse la reconstruction plutôt que d'inventer
    un contenu.

    Ne revérifie pas elle-même qu'un merge est en cours ni que
    `chemin_relatif` figure dans `get_fichiers_resolus_merge` : à charge de
    l'appelant, comme les autres fonctions de résolution de ce module.

    Retourne {ok, erreur, commande}."""
    commande = ["git", "-C", repertoire, "checkout", "--conflict=merge", "--", chemin_relatif]
    resultat = _lancer_git(repertoire, "checkout", "--conflict=merge", "--", chemin_relatif)
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": commande_affichee(repertoire, " ".join(commande)),
    }


def lire_conflits_fichier(repertoire, chemin_relatif):
    """Lit un fichier en conflit et le découpe en segments contexte/conflit
    (issue #55) — lecture seule stricte, aucune écriture. `chemin_relatif`
    doit être un chemin déjà validé par l'appelant (présent dans le retour
    actuel de `get_fichiers_en_conflit`) : cette fonction ne revérifie pas
    elle-même que le fichier est en conflit, seulement qu'il est lisible.
    Retourne {segments, nb_blocs, empreinte, erreur} — `erreur` non None si
    le fichier est illisible (supprimé entre-temps, permissions, etc.).
    `empreinte` (sha256 du contenu brut, None si erreur) permet à
    `resoudre_tous_blocs_conflit` (issue #69, bouton « Traiter tous les
    blocs ») de vérifier que le fichier n'a pas changé depuis cet affichage
    avant d'appliquer tous les blocs d'un coup."""
    chemin_absolu = os.path.join(repertoire, chemin_relatif)
    try:
        with open(chemin_absolu, encoding="utf-8", errors="replace") as fichier:
            contenu = fichier.read()
    except OSError as exc:
        return {"segments": [], "nb_blocs": 0, "empreinte": None, "erreur": str(exc)}

    segments = _extraire_blocs_conflit(contenu)
    nb_blocs = sum(1 for segment in segments if segment["type"] == "conflit")
    empreinte = hashlib.sha256(contenu.encode("utf-8")).hexdigest()
    return {"segments": segments, "nb_blocs": nb_blocs, "empreinte": empreinte, "erreur": None}


def resoudre_bloc_conflit(repertoire, chemin_relatif, index_bloc, texte_final):
    """Remplace le bloc de conflit numéro `index_bloc` (0-based, même
    numérotation que `lire_conflits_fichier`, via `_trouver_blocs_conflit`)
    par `texte_final` dans le fichier réel (issue #56) — marqueurs
    `<<<<<<<`/`=======`/`>>>>>>>` compris, le reste du fichier intact. Si le
    fichier ne contient plus aucun bloc de conflit après ce remplacement,
    lance `git add <chemin_relatif>` pour marquer sa résolution (jamais de
    commit ni de push, qui restent des gestes manuels d'Alain).

    Lecture stricte en UTF-8 (contrairement à `lire_conflits_fichier`, qui
    tolère les octets invalides avec `errors="replace"` puisqu'elle
    n'écrit jamais) : ici une écriture suit la lecture, remplacer les
    octets invalides par des caractères de substitution les perdrait
    définitivement — mieux vaut échouer proprement sur un fichier non
    UTF-8 que corrompre son contenu.

    `index_bloc` doit provenir du même état de fichier que ce qui a été
    affiché (voir la route appelante) : si le fichier a changé entre-temps
    au point que ce numéro ne corresponde plus à un bloc existant (bloc
    déjà traité, fichier modifié en dehors de relecture_web...), retourne
    une erreur plutôt que d'écrire à l'aveugle sur le mauvais bloc.

    Retourne {ok, erreur, nb_blocs_restants, fichier_resolu, git_add} —
    `git_add` est None si `git add` n'a pas été nécessaire (blocs
    restants), sinon {ok, erreur} de la commande elle-même."""
    chemin_absolu = os.path.join(repertoire, chemin_relatif)
    try:
        with open(chemin_absolu, encoding="utf-8") as fichier:
            contenu = fichier.read()
    except (OSError, UnicodeDecodeError) as exc:
        return {
            "ok": False, "erreur": str(exc), "nb_blocs_restants": 0,
            "fichier_resolu": False, "git_add": None,
        }

    lignes = contenu.splitlines(keepends=True)
    blocs = _trouver_blocs_conflit(lignes)
    if not (0 <= index_bloc < len(blocs)):
        return {
            "ok": False,
            "erreur": (
                f"bloc n°{index_bloc} introuvable — le fichier a changé depuis "
                "l'affichage (bloc déjà traité, ou modifié en dehors de "
                "relecture_web). Recharge la page pour repartir des blocs actuels."
            ),
            "nb_blocs_restants": len(blocs), "fichier_resolu": False, "git_add": None,
        }

    bloc = blocs[index_bloc]
    if texte_final and not texte_final.endswith("\n"):
        texte_final += "\n"
    nouvelles_lignes = lignes[:bloc["debut"]] + ([texte_final] if texte_final else []) + lignes[bloc["fin"]:]

    try:
        with open(chemin_absolu, "w", encoding="utf-8") as fichier:
            fichier.write("".join(nouvelles_lignes))
    except OSError as exc:
        return {
            "ok": False, "erreur": str(exc), "nb_blocs_restants": len(blocs),
            "fichier_resolu": False, "git_add": None,
        }

    nb_blocs_restants = len(blocs) - 1
    fichier_resolu = nb_blocs_restants == 0
    git_add = None
    if fichier_resolu:
        resultat = _lancer_git(repertoire, "add", "--", chemin_relatif)
        git_add = {
            "ok": resultat.returncode == 0,
            "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        }

    return {
        "ok": True, "erreur": None, "nb_blocs_restants": nb_blocs_restants,
        "fichier_resolu": fichier_resolu, "git_add": git_add,
    }


def resoudre_tous_blocs_conflit(repertoire, chemin_relatif, textes_finaux, empreinte_attendue):
    """Version « tout ou rien » de `resoudre_bloc_conflit` (bouton « Traiter
    tous les blocs », issue #69) : remplace en une seule opération chaque
    bloc de conflit de `chemin_relatif` par le texte de `textes_finaux`
    (même ordre et même numérotation 0-based que `_trouver_blocs_conflit`,
    donc que l'affichage — `textes_finaux[i]` doit correspondre au bloc
    d'index `i`).

    Même garde-fou que `resoudre_bloc_conflit`, mais vérifié sur l'ensemble
    du fichier avant d'écrire quoi que ce soit : si le nombre de blocs
    actuellement présents ne correspond pas à `len(textes_finaux)`, ou si
    `empreinte_attendue` (sha256 du contenu tel que lu par
    `lire_conflits_fichier` au moment de l'affichage) ne correspond plus au
    contenu actuel du fichier, refuse tout le traitement — aucun bloc n'est
    écrit, même partiellement.

    Applique les remplacements du dernier bloc vers le premier : remplacer
    un bloc décale les index de lignes de tous les blocs qui le suivent
    dans le fichier (jamais ceux qui le précèdent), donc traiter dans
    l'ordre inverse garantit que chaque remplacement utilise encore des
    index valides pour les blocs restant à traiter.

    Comme `resoudre_bloc_conflit`, `git add <chemin_relatif>` est lancé une
    fois tous les blocs remplacés (systématique ici, puisque chaque bloc
    détecté a nécessairement un texte correspondant en entrée) — le commit
    et le push restent des gestes manuels d'Alain.

    Retourne {ok, erreur, git_add}."""
    chemin_absolu = os.path.join(repertoire, chemin_relatif)
    try:
        with open(chemin_absolu, encoding="utf-8") as fichier:
            contenu = fichier.read()
    except (OSError, UnicodeDecodeError) as exc:
        return {"ok": False, "erreur": str(exc), "git_add": None}

    empreinte_actuelle = hashlib.sha256(contenu.encode("utf-8")).hexdigest()
    lignes = contenu.splitlines(keepends=True)
    blocs = _trouver_blocs_conflit(lignes)

    if len(blocs) != len(textes_finaux) or empreinte_actuelle != empreinte_attendue:
        return {
            "ok": False,
            "erreur": (
                "le fichier a changé depuis l'affichage (nombre ou contenu des blocs "
                "différent de ce qui a été affiché) — recharge la page pour repartir "
                "des blocs actuels."
            ),
            "git_add": None,
        }

    for index_bloc in range(len(blocs) - 1, -1, -1):
        bloc = blocs[index_bloc]
        texte_final = textes_finaux[index_bloc]
        if texte_final and not texte_final.endswith("\n"):
            texte_final += "\n"
        lignes = lignes[:bloc["debut"]] + ([texte_final] if texte_final else []) + lignes[bloc["fin"]:]

    try:
        with open(chemin_absolu, "w", encoding="utf-8") as fichier:
            fichier.write("".join(lignes))
    except OSError as exc:
        return {"ok": False, "erreur": str(exc), "git_add": None}

    resultat = _lancer_git(repertoire, "add", "--", chemin_relatif)
    git_add = {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
    }
    return {"ok": True, "erreur": None, "git_add": git_add}


def collect_etat_projets():
    """Assemble, pour chaque projet de BRIDGE_AGENT_DOC.md, ses worktrees et
    leurs commits en attente de push."""
    projets = fetch_projets()
    branches_cibles = charger_branches_cibles()
    repertoire_bridge_agent = next(
        (p["repertoire"] for p in projets if p["nom"] == "bridge_agent"), None
    )
    resultat = []
    for projet in projets:
        entree = dict(projet, worktrees=[])
        repertoire = projet["repertoire"]

        # Nom du dossier de relecture (Relecture_Bridge/<dossier>/Non_Lu) : le
        # même calcul que le hook post-commit (basename du répertoire de
        # travail), PAS le champ "nom" du tableau, qui peut différer (ex.
        # "alchess" pour le dossier "NicLink" — voir post-commit).
        entree["dossier_relecture"] = os.path.basename(os.path.normpath(repertoire))

        if est_projet_distant(repertoire):
            # Projet distant (PC fixe CCW, issue #94) : le test `os.path.isdir`
            # ci-dessous ne peut pas s'appliquer (chemin Windows, pas de
            # filesystem partagé) — pendant distant du même garde-fou, un
            # test de connectivité SSH borné (ConnectTimeout court, voir
            # tester_connectivite_ccw) avant toute tentative de commande git,
            # pour qu'un PC fixe éteint ne bloque jamais le serveur Flask de
            # développement (mono-thread) ni ne fasse attendre la page
            # indéfiniment.
            if not tester_connectivite_ccw():
                entree["statut"] = "injoignable"
                resultat.append(entree)
                continue
        elif not os.path.isdir(repertoire):
            entree["statut"] = "introuvable"
            resultat.append(entree)
            continue
        elif not os.path.exists(os.path.join(repertoire, ".git")):
            entree["statut"] = "pas_un_depot_git"
            resultat.append(entree)
            continue

        entree["statut"] = "ok"
        branche_principale = get_branche_courante(repertoire)
        entree["branche_principale"] = branche_principale
        entree["branche_cible_comparaison"] = get_branche_cible_comparaison(
            projet["nom"], branche_principale, branches_cibles
        )
        chemin_principal = os.path.realpath(repertoire)
        lignes_deja_pris = _lignes_deja_pris_watcher(projet["nom"], repertoire_bridge_agent)
        for worktree in get_worktrees(repertoire):
            worktree.update(get_commits_en_attente(worktree["path"]))
            worktree["branche_principale"] = branche_principale
            worktree["est_worktree_principal"] = (
                os.path.realpath(worktree["path"]) == chemin_principal
            )
            worktree["orphelin_signale"] = (
                not worktree["est_worktree_principal"]
                and worktree_orphelin_signale(worktree["path"], lignes_deja_pris)
            )

            peut_agir = (
                branche_principale
                and worktree["branch"]
                and not worktree["est_worktree_principal"]
            )
            if peut_agir:
                worktree["merge_ok"] = est_branche_mergee(
                    repertoire, entree["branche_cible_comparaison"], worktree["branch"]
                )
                worktree["commande_merge"] = f"git -C {repertoire} merge {worktree['branch']}"
                worktree["commande_suppression"] = (
                    f"git -C {repertoire} worktree remove {worktree['path']}"
                )
            else:
                worktree["merge_ok"] = False
                worktree["commande_merge"] = None
                worktree["commande_suppression"] = None

            entree["worktrees"].append(worktree)
        resultat.append(entree)

    return resultat


# --- Panneau « .gitignore » de la page projet (issue #98) ---------------
#
# Agit uniquement sur le .gitignore à la racine du worktree PRINCIPAL d'un
# projet LOCAL (jamais sur ceux des worktrees de CCL, jamais sur un projet
# distant CCW — #94, dont le filesystem n'est pas accessible directement
# depuis ce process : `open()` ne peut viser qu'un chemin local). L'appelant
# (app.py) est responsable d'écarter un projet distant avant d'appeler quoi
# que ce soit ci-dessous.

def chemin_gitignore(repertoire):
    return os.path.join(repertoire, ".gitignore")


def lire_lignes_gitignore(repertoire):
    """Lignes brutes du .gitignore de `repertoire`, chacune avec sa
    terminaison d'origine intacte (`\\n`, `\\r\\n`, ou aucune pour une
    dernière ligne sans retour final) — nécessaire pour réécrire le fichier
    sans en changer le format (ordre, commentaires, fins de ligne). None si
    le fichier n'existe pas."""
    try:
        with open(chemin_gitignore(repertoire), "r", encoding="utf-8", newline="") as fichier:
            contenu = fichier.read()
    except OSError:
        return None
    return contenu.splitlines(keepends=True) if contenu else []


def ecrire_lignes_gitignore(repertoire, lignes):
    """Réécrit le .gitignore de `repertoire` avec exactement `lignes` (voir
    `lire_lignes_gitignore`) — simple concaténation, aucune transformation."""
    with open(chemin_gitignore(repertoire), "w", encoding="utf-8", newline="") as fichier:
        fichier.write("".join(lignes))


def classifier_ligne_gitignore(ligne):
    """« motif » (un chemin à ignorer), « commentaire » (ligne commençant
    par # une fois les espaces de tête retirés) ou « vide » — ces deux
    derniers ne sont jamais proposés à la suppression individuelle (voir
    projet.html)."""
    texte = ligne.rstrip("\r\n").strip()
    if not texte:
        return "vide"
    if texte.startswith("#"):
        return "commentaire"
    return "motif"


def _terminaison_dominante(lignes):
    for ligne in reversed(lignes):
        if ligne.endswith("\r\n"):
            return "\r\n"
        if ligne.endswith("\n"):
            return "\n"
    return "\n"


def ajouter_motif_gitignore(repertoire, motif):
    """Ajoute `motif` en fin de .gitignore de `repertoire` (le crée s'il
    n'existe pas encore), en gardant intactes les lignes déjà présentes. La
    terminaison de la nouvelle ligne reprend celle déjà utilisée dans le
    fichier (dernière ligne terminée), `\\n` par défaut pour un fichier
    vide/nouveau. Ne valide rien (doublon, ligne unique, etc.) — à charge de
    l'appelant (voir app.py)."""
    lignes = lire_lignes_gitignore(repertoire) or []
    terminaison = _terminaison_dominante(lignes)
    if lignes and not lignes[-1].endswith(("\n", "\r\n")):
        lignes[-1] = lignes[-1] + terminaison
    lignes.append(motif + terminaison)
    ecrire_lignes_gitignore(repertoire, lignes)


def committer_gitignore(repertoire, message):
    """Commit du .gitignore seul (`git add -- .gitignore` puis `git commit
    -- .gitignore`), jamais `-a`/`-A` — même principe de portée que le
    commit CHANGELOG de `fusionner_changelog_worktree` (issue #74) :
    `repertoire` peut être le même dossier où un CCL travaille encore en
    repli sur REP_TRAVAIL, un commit plus large embarquerait son travail
    inachevé. Retourne {ok, erreur, commande}."""
    ajout = _lancer_git(repertoire, "add", "--", ".gitignore")
    commande_add = commande_affichee(repertoire, f"git -C {repertoire} add -- .gitignore")
    if ajout.returncode != 0:
        return {"ok": False, "erreur": (ajout.stderr or ajout.stdout).strip(), "commande": commande_add}

    commit = _lancer_git(repertoire, "commit", "-m", message, "--", ".gitignore")
    commande_commit = commande_affichee(
        repertoire, f"git -C {repertoire} commit -m {json.dumps(message)} -- .gitignore"
    )
    if commit.returncode != 0:
        return {"ok": False, "erreur": (commit.stderr or commit.stdout).strip(), "commande": commande_commit}
    return {"ok": True, "erreur": None, "commande": commande_commit}


def gitignore_a_des_modifications_non_committees(repertoire):
    """True si le .gitignore de `repertoire` porte déjà une modification non
    committée (`git status --porcelain=v1 -- .gitignore`) — garde-fou avant
    toute action du panneau (issue #98) : une modification déjà présente
    avant que ce panneau ne touche quoi que ce soit vient forcément d'une
    autre source (édition manuelle en terminal, autre outil) et ne doit
    jamais être embarquée dans le commit automatique sans qu'Alain le
    sache."""
    resultat = _lancer_git(repertoire, "status", "--porcelain=v1", "--", ".gitignore")
    if resultat.returncode != 0:
        return False
    return bool(resultat.stdout.strip())


def get_fichiers_suivis_correspondant(repertoire, motif):
    """Fichiers déjà suivis par git qui correspondent à `motif` (piège connu
    de gitignore, issue #98 : ajouter un motif n'arrête jamais de suivre un
    fichier déjà suivi). `git ls-files -i -c --exclude=<motif>` simule
    l'effet de ce seul motif avec le même moteur de correspondance que git
    lui-même (gère `/` final, `**`, négation, etc.), sans réimplémentation
    approximative ici. Retourne une liste de chemins (vide si aucun, ou en
    cas d'erreur git)."""
    resultat = _lancer_git(repertoire, "ls-files", "-i", "-c", f"--exclude={motif}")
    if resultat.returncode != 0:
        return []
    return [ligne for ligne in resultat.stdout.splitlines() if ligne.strip()]


def retirer_du_suivi(repertoire, chemin):
    """`git rm --cached -- <chemin>` (bouton « Ne plus suivre », issue #98) :
    retire uniquement l'entrée de l'index, le fichier reste intact sur
    disque. Committe immédiatement, portée strictement limitée à `chemin`
    (même principe que `committer_gitignore` ci-dessus) — jamais lancé
    automatiquement, seulement sur action explicite confirmée côté
    template.

    Ne commit PAS avec `git commit -- <chemin>` (contrairement à
    `committer_gitignore`) : une fois `chemin` redevenu non suivi par le
    `rm --cached` ci-dessous, git le voit aussi comme un fichier ordinaire
    du répertoire de travail (resté sur disque) et répond « rien à
    valider » au lieu de committer la suppression pourtant déjà indexée
    (vérifié sur git 2.43) — `--include`/`-i` contourne ce symptôme mais
    committe en même temps tout AUTRE changement déjà indexé par un tiers,
    ce que #74 interdit justement. Un commit sans pathspec est donc utilisé
    à la place, mais seulement si l'index est déjà vide AVANT le `rm
    --cached` (vérifié ici, pas après coup) : dans ce cas, le seul
    changement indexé au moment du commit est forcément celui qu'on vient
    de faire — refus (sans toucher à rien) si l'index contenait déjà
    d'autres changements."""
    commande_rm = commande_affichee(repertoire, f"git -C {repertoire} rm --cached -- {chemin}")

    diff_avant = _lancer_git(repertoire, "diff", "--cached", "--name-only")
    chemins_deja_indexes = [ligne.strip() for ligne in diff_avant.stdout.splitlines() if ligne.strip()]
    if chemins_deja_indexes:
        return {
            "ok": False,
            "erreur": (
                "d'autres modifications sont déjà indexées dans ce dépôt "
                f"({', '.join(chemins_deja_indexes)}) — action refusée pour ne pas les embarquer."
            ),
            "commande": commande_rm,
        }

    rm = _lancer_git(repertoire, "rm", "--cached", "--", chemin)
    if rm.returncode != 0:
        return {"ok": False, "erreur": (rm.stderr or rm.stdout).strip(), "commande": commande_rm}

    commit = _lancer_git(repertoire, "commit", "-m", f"chore: ne plus suivre {chemin}")
    if commit.returncode != 0:
        return {
            "ok": False,
            "erreur": "git rm --cached fait, mais commit impossible : " + (commit.stderr or commit.stdout).strip(),
            "commande": commande_rm,
        }
    return {"ok": True, "erreur": None, "commande": commande_rm}


def get_fichiers_non_suivis(repertoire):
    """Fichiers et dossiers non suivis et non ignorés de `repertoire` (même
    source que `get_modifications_non_committees` : `git status
    --porcelain=v1`, qui exclut déjà les chemins ignorés) — raccourci
    pratique du panneau .gitignore (issue #98), limité au code `??` (un
    fichier suivi modifié n'a pas sa place dans cette liste, contrairement
    à `get_modifications_non_committees`)."""
    resultat = _lancer_git(repertoire, "status", "--porcelain=v1")
    if resultat.returncode != 0:
        return []
    chemins = []
    for ligne in resultat.stdout.splitlines():
        if len(ligne) < 4 or not ligne.startswith("??"):
            continue
        chemin = ligne[3:]
        if chemin.startswith('"') and chemin.endswith('"'):
            chemin = chemin[1:-1]
        chemins.append(chemin)
    return chemins


if __name__ == "__main__":
    print(json.dumps(collect_etat_projets(), ensure_ascii=False, indent=2))
