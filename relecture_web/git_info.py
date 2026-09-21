#!/usr/bin/env python3
"""
Lecture de l'état git (worktrees, commits en attente de push) pour les
projets Bridge_Agent, en commandes git directes — sans dépendre du code de
bridge_agent (watcher.py, app/git_etat.py), hors périmètre pour un CCL
travaillant sur relecture_bridge.

La liste des projets est récupérée depuis BRIDGE_AGENT_DOC.md (même source
et même tableau qu'installer.sh), pas codée en dur ici.
"""

import os
import re
import subprocess
import urllib.request

DOC_URL = "https://raw.githubusercontent.com/AlainDelree/Bridge_Agent/master/BRIDGE_AGENT_DOC.md"
DEBUT_TABLEAU = "<!-- DEBUT:TABLEAU_PROJETS_ACTIFS"
FIN_TABLEAU = "<!-- FIN:TABLEAU_PROJETS_ACTIFS"

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


class ErreurRecuperationProjets(Exception):
    """La liste des projets n'a pas pu être récupérée depuis BRIDGE_AGENT_DOC.md."""


def fetch_projets():
    """Récupère et parse le tableau des projets actifs depuis BRIDGE_AGENT_DOC.md."""
    try:
        with urllib.request.urlopen(DOC_URL, timeout=TIMEOUT_RESEAU) as reponse:
            contenu = reponse.read().decode("utf-8")
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
        projets.append({
            "nom": nom,
            "depot": depot,
            "repertoire": os.path.expanduser(repertoire),
        })

    if not projets:
        raise ErreurRecuperationProjets(
            "Aucun projet trouvé dans le tableau de BRIDGE_AGENT_DOC.md."
        )
    return projets


def _lancer_git(repertoire, *args):
    return subprocess.run(
        ["git", "-C", repertoire, *args],
        capture_output=True, text=True, timeout=TIMEOUT_GIT,
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
    resultat = subprocess.run(commande, capture_output=True, text=True, timeout=TIMEOUT_GIT)
    return {
        "commande": " ".join(commande),
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
    diff = subprocess.run(
        ["git", "-C", repertoire, "show", "--no-color", hash_commit],
        capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    if diff.returncode != 0:
        return None
    patch_id = subprocess.run(
        ["git", "-C", repertoire, "patch-id", "--stable"],
        input=diff.stdout, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
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

    log = subprocess.run(
        ["git", "-C", repertoire, "log", "--no-color", "-p", f"{base_commune}..{branche_cible}"],
        capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    if log.returncode != 0 or not log.stdout.strip():
        return None

    patch_ids = subprocess.run(
        ["git", "-C", repertoire, "patch-id", "--stable"],
        input=log.stdout, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
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
    resultat = subprocess.run(
        ["git", "-C", repertoire, "diff", "--no-color", hash_a, hash_b],
        capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
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
    resultat = subprocess.run(commande, capture_output=True, text=True, timeout=TIMEOUT_GIT)
    return {
        "ok": resultat.returncode == 0,
        "deja_securise": False,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
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


def fusionner_changelog_worktree(repertoire):
    """Si la fusion qui vient d'avoir lieu dans `repertoire` a introduit un
    ou plusieurs `CHANGELOG-<N>.md` à la racine du dépôt (chaque worktree
    mode_write écrit le sien plutôt que dans `CHANGELOG.md` directement,
    pour éviter les conflits entre worktrees actifs en parallèle — issue
    #577 côté Bridge_Agent), lance `scripts/fusionner_changelog.py` (déjà
    présent dans chaque projet équipé du système de worktrees) pour les
    intégrer dans `CHANGELOG.md`, geste qu'Alain devait jusqu'ici penser à
    faire lui-même à chaque merge (issue #51). Retourne None si aucun
    `CHANGELOG-<N>.md` trouvé (rien à fusionner, pas de message nécessaire),
    sinon {ok, erreur, commande} pour affichage transparent — jamais
    d'échec silencieux même si le script est absent."""
    try:
        presence = any(
            MOTIF_CHANGELOG_WORKTREE.match(nom) for nom in os.listdir(repertoire)
        )
    except OSError:
        presence = False
    if not presence:
        return None

    script = os.path.join(repertoire, "scripts", "fusionner_changelog.py")
    commande = ["python3", script, "--repo", repertoire]
    if not os.path.isfile(script):
        return {
            "ok": False,
            "erreur": f"script introuvable : {script}",
            "commande": " ".join(commande),
        }

    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
    }


def fusionner_worktree(repertoire, branche_cible, branche_source):
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
    `repertoire`. Retourne {ok, erreur, commande, changelog} pour affichage
    transparent (`changelog` vaut None si aucun CHANGELOG-<N>.md n'était à
    fusionner)."""
    branche_courante = get_branche_courante(repertoire)
    doit_basculer = branche_courante is not None and branche_courante != branche_cible

    if doit_basculer:
        bascule = _lancer_git(repertoire, "checkout", branche_cible)
        if bascule.returncode != 0:
            return {
                "ok": False,
                "erreur": (bascule.stderr or bascule.stdout).strip(),
                "commande": f"git -C {repertoire} checkout {branche_cible}",
                "changelog": None,
            }

    commande = ["git", "-C", repertoire, "merge", branche_source]
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT_LONG,
    )

    resultat_changelog = None
    if resultat.returncode == 0:
        resultat_changelog = fusionner_changelog_worktree(repertoire)

    if doit_basculer and resultat.returncode == 0:
        _lancer_git(repertoire, "checkout", branche_courante)

    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
        "changelog": resultat_changelog,
    }


def supprimer_worktree(repertoire, chemin_worktree):
    """Supprime un worktree via `git worktree remove`, jamais forcé (donc git
    refuse de lui-même si le worktree a des modifications non commitées).
    Retourne {ok, erreur, commande} pour affichage transparent."""
    commande = ["git", "-C", repertoire, "worktree", "remove", chemin_worktree]
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
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
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
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
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
    }


def revert_commit(repertoire, hash_commit):
    """Annule `hash_commit` via `git revert --no-edit` : crée un nouveau
    commit d'annulation, indépendant des autres commits de la branche
    (contrairement au push, pas de contrainte d'ordre). Retourne
    {ok, erreur, commande} pour affichage transparent."""
    commande = ["git", "-C", repertoire, "revert", "--no-edit", hash_commit]
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
    }


def pousser_branche(repertoire, branche):
    """Pousse `branche` jusqu'à son dernier commit vers le remote par défaut
    (`git push <remote> <branche>`) — un push cible toujours une branche
    entière jusqu'à un point donné, jamais une sélection de commits épars.
    Retourne {ok, erreur, commande} pour affichage transparent."""
    remote = get_remote_defaut(repertoire)
    commande = ["git", "-C", repertoire, "push", remote, branche]
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT_LONG,
    )
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
    }


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


def _extraire_blocs_conflit(contenu):
    """Découpe le contenu d'un fichier en conflit en segments alternant
    texte de contexte et blocs de conflit (issue #55) — le texte hors
    conflit doit s'afficher normalement autour, pour donner le contexte
    (demande explicite de l'issue). Un éventuel bloc de base commune
    (marqueur `|||||||`, présent seulement si `merge.conflictStyle=diff3`
    est configuré) est ignoré : seules les deux versions en conflit sont
    affichées, pas la base à trois voies.

    Retourne une liste de segments : {type: 'contexte', texte} ou
    {type: 'conflit', entete_ours, texte_ours, entete_theirs, texte_theirs}.
    Un marqueur ouvert sans fermeture (fichier tronqué/corrompu) rattache le
    fragment orphelin au contexte plutôt que d'échouer."""
    lignes = contenu.splitlines(keepends=True)
    segments = []
    contexte = []
    i, n = 0, len(lignes)

    while i < n:
        ligne = lignes[i]
        if not ligne.startswith(_MARQUEUR_DEBUT):
            contexte.append(ligne)
            i += 1
            continue

        depart = i
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
            contexte.extend(lignes[depart:])
            break
        i += 1  # ligne =======
        theirs = []
        while i < n and not lignes[i].startswith(_MARQUEUR_FIN):
            theirs.append(lignes[i])
            i += 1
        if i >= n:
            contexte.extend(lignes[depart:])
            break
        entete_theirs = lignes[i].rstrip("\n")
        i += 1

        if contexte:
            segments.append({"type": "contexte", "texte": "".join(contexte)})
            contexte = []
        segments.append({
            "type": "conflit",
            "entete_ours": entete_ours,
            "texte_ours": "".join(ours),
            "entete_theirs": entete_theirs,
            "texte_theirs": "".join(theirs),
        })

    if contexte:
        segments.append({"type": "contexte", "texte": "".join(contexte)})
    return segments


def lire_conflits_fichier(repertoire, chemin_relatif):
    """Lit un fichier en conflit et le découpe en segments contexte/conflit
    (issue #55) — lecture seule stricte, aucune écriture. `chemin_relatif`
    doit être un chemin déjà validé par l'appelant (présent dans le retour
    actuel de `get_fichiers_en_conflit`) : cette fonction ne revérifie pas
    elle-même que le fichier est en conflit, seulement qu'il est lisible.
    Retourne {segments, nb_blocs, erreur} — `erreur` non None si le fichier
    est illisible (supprimé entre-temps, permissions, etc.)."""
    chemin_absolu = os.path.join(repertoire, chemin_relatif)
    try:
        with open(chemin_absolu, encoding="utf-8", errors="replace") as fichier:
            contenu = fichier.read()
    except OSError as exc:
        return {"segments": [], "nb_blocs": 0, "erreur": str(exc)}

    segments = _extraire_blocs_conflit(contenu)
    nb_blocs = sum(1 for segment in segments if segment["type"] == "conflit")
    return {"segments": segments, "nb_blocs": nb_blocs, "erreur": None}


def collect_etat_projets():
    """Assemble, pour chaque projet de BRIDGE_AGENT_DOC.md, ses worktrees et
    leurs commits en attente de push."""
    projets = fetch_projets()
    branches_cibles = charger_branches_cibles()
    resultat = []
    for projet in projets:
        entree = dict(projet, worktrees=[])
        repertoire = projet["repertoire"]

        # Nom du dossier de relecture (Relecture_Bridge/<dossier>/Non_Lu) : le
        # même calcul que le hook post-commit (basename du répertoire de
        # travail), PAS le champ "nom" du tableau, qui peut différer (ex.
        # "alchess" pour le dossier "NicLink" — voir post-commit).
        entree["dossier_relecture"] = os.path.basename(os.path.normpath(repertoire))

        if not os.path.isdir(repertoire):
            entree["statut"] = "introuvable"
            resultat.append(entree)
            continue
        if not os.path.exists(os.path.join(repertoire, ".git")):
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
        for worktree in get_worktrees(repertoire):
            worktree.update(get_commits_en_attente(worktree["path"]))
            worktree["branche_principale"] = branche_principale
            worktree["est_worktree_principal"] = (
                os.path.realpath(worktree["path"]) == chemin_principal
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


if __name__ == "__main__":
    import json
    print(json.dumps(collect_etat_projets(), ensure_ascii=False, indent=2))
