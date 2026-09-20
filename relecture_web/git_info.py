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
TIMEOUT_PUSH = 30
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
    avant de proposer la suppression d'un worktree."""
    if not branche_principale or not branche:
        return False
    resultat = _lancer_git(
        repertoire, "merge-base", "--is-ancestor", branche, branche_principale
    )
    return resultat.returncode == 0


def charger_branches_cibles():
    """Lit `branches_cibles.conf` (une ligne `nom_projet = branche` par
    entrée, `#` pour les commentaires) — configure, projet par projet, la
    branche à utiliser comme référence pour savoir si un commit orphelin ou
    en attente est déjà intégré, quand ce n'est pas la branche principale du
    dépôt (ex. un projet qui travaille sur `dev` avant de merger vers
    `main` : comparer contre `main` donnerait un écart de commits trompeur).
    `nom_projet` est le champ "nom" de BRIDGE_AGENT_DOC.md (ex.
    "ff_galerie"), pas le nom de dossier. Fichier absent ou entrée manquante
    pour un projet : aucune surcharge, comportement inchangé."""
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
        nom_projet, branche = ligne.split("=", 1)
        nom_projet, branche = nom_projet.strip(), branche.strip()
        if nom_projet and branche:
            branches_cibles[nom_projet] = branche
    return branches_cibles


def get_branche_cible_comparaison(nom_projet, branche_principale, branches_cibles=None):
    """Branche cible de comparaison d'un projet : la valeur configurée dans
    `branches_cibles.conf` si elle existe, sinon `branche_principale` (repli
    par défaut, comportement inchangé pour les projets sans configuration
    explicite). `branches_cibles` peut être fourni déjà chargé pour éviter
    de relire le fichier à chaque projet dans une boucle."""
    if branches_cibles is None:
        branches_cibles = charger_branches_cibles()
    return branches_cibles.get(nom_projet, branche_principale)


def get_branches_locales(repertoire):
    """Liste toutes les branches locales d'un dépôt (`git for-each-ref
    refs/heads/`), contrairement à `get_worktrees` qui ne voit que celles
    ayant un worktree actif. Pour chaque branche : son dernier commit, le
    chemin de son worktree s'il en existe un, et si elle est fusionnée dans
    la branche principale (via `est_branche_mergee`)."""
    resultat = _lancer_git(
        repertoire, "for-each-ref", "refs/heads/",
        "--format=%(refname:short)%09%(objectname:short)%09"
        "%(committerdate:iso-strict)%09%(subject)",
    )
    if resultat.returncode != 0:
        return []

    branche_principale = get_branche_courante(repertoire)
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
            "mergee": est_branche_mergee(repertoire, branche_principale, nom),
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
    if not branche_cible:
        return [
            {"hash": h, "cas": "E", "chaine": [], "orphelins_absorbes": []}
            for h in hashes_orphelins
        ]

    ensemble_orphelins = set(hashes_orphelins)
    diagnostics = {}
    absorbes_global = set()

    for h in hashes_orphelins:
        if get_commit_est_vide(repertoire, h):
            diagnostics[h] = {"hash": h, "cas": "D", "chaine": [], "orphelins_absorbes": []}
            continue

        chaine = get_chaine_cherry(repertoire, branche_cible, h)
        maillon_tip = (
            next((m for m in chaine if m["hash"].startswith(h)), None) if chaine else None
        )
        if chaine is None or maillon_tip is None:
            diagnostics[h] = {"hash": h, "cas": "F", "chaine": [], "orphelins_absorbes": []}
            continue

        orphelins_absorbes = [
            autre for autre in ensemble_orphelins
            if autre != h and any(m["hash"].startswith(autre) for m in chaine if m is not maillon_tip)
        ]
        absorbes_global.update(orphelins_absorbes)

        diagnostics[h] = {
            "hash": h,
            "cas": "A" if maillon_tip["statut"] == "nouveau" else "B",
            "chaine": chaine,
            "orphelins_absorbes": orphelins_absorbes,
        }

    return [diag for h, diag in diagnostics.items() if h not in absorbes_global]


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


def fusionner_worktree(repertoire, branche):
    """Fusionne `branche` dans la branche courante de `repertoire` (comme un
    `git merge` manuel lancé depuis le worktree principal), sans jamais
    pousser. Retourne {ok, erreur, commande} pour affichage transparent."""
    commande = ["git", "-C", repertoire, "merge", branche]
    resultat = subprocess.run(
        commande, capture_output=True, text=True, timeout=TIMEOUT_GIT,
    )
    return {
        "ok": resultat.returncode == 0,
        "erreur": (resultat.stderr or resultat.stdout).strip() if resultat.returncode != 0 else None,
        "commande": " ".join(commande),
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
        commande, capture_output=True, text=True, timeout=TIMEOUT_PUSH,
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
                    repertoire, branche_principale, worktree["branch"]
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
