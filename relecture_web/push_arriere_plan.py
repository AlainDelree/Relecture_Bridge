#!/usr/bin/env python3
"""
Push en arrière-plan pour les projets équipés d'un crochet `pre-push`
(issue #122).

Contexte : un crochet `pre-push` qui lance une suite de tests (~80-90s)
avant chaque push rend le push synchrone actuel (`pousser_branche`,
`TIMEOUT_GIT_LONG` = 120s, voir `git_info.py`) peu praticable — un push
proche ou au-delà de 120s bloquerait la page, et le message « n'a PAS
abouti » pourrait même être faux (même piège que l'issue #66, mais plus
probable avec un crochet qui allonge franchement chaque push).

Ce module ne concerne QUE les projets « équipés » d'un crochet `pre-push`
exécutable (voir `git_info.projet_equipe_hook_pre_push`) — un projet non
équipé continue d'utiliser `git_info.pousser_branche` de façon synchrone,
inchangé, directement depuis `app.py`.

Le process git est lancé dans son propre groupe de processus
(`start_new_session=True`) : au dépassement du délai propre à ce module
(`TIMEOUT_PUSH_ARRIERE_PLAN`, distinct de `TIMEOUT_GIT_LONG`), tuer
seulement le process git laisserait tourner les tests lancés par le
crochet (ses enfants, dans le même groupe), qui pourraient alors
chevaucher le push suivant — `os.killpg` arrête tout le groupe d'un coup.

État persistant (une entrée par projet, voir `CHEMIN_ETAT_PUSH`) : sert
aussi de verrou — un projet est considéré verrouillé par un push tant que
son entrée a `etat == "en_cours"` (voir `projet_verrouille_par_push`). Ce
verrou survit à la durée de vie du thread (relu depuis le fichier à chaque
requête), mais pas à un redémarrage du process relecture_web : une entrée
restée « en_cours » après un redémarrage ne peut provenir que d'un thread
disparu avec l'ancien process — voir `reconcilier_au_demarrage`, appelée
une seule fois au lancement de `app.py`.
"""

import json
import os
import signal
import subprocess
import tempfile
import threading
from datetime import datetime

import git_info

# Délai propre au push en arrière-plan (issue #122) — distinct de
# `git_info.TIMEOUT_GIT_LONG` (120s, push synchrone des projets non
# équipés) : un crochet pre-push qui lance une suite de tests peut
# légitimement prendre plusieurs minutes, sans bloquer l'interface puisque
# ce délai ne s'applique plus qu'à un thread serveur, jamais à la requête
# HTTP elle-même.
TIMEOUT_PUSH_ARRIERE_PLAN = 600

# Taille bornée de la sortie conservée dans l'état persistant (issue #122,
# point 4) — fin du crochet et de git seulement, jamais la totalité : un
# crochet de tests verbeux ne doit jamais faire grossir indéfiniment le
# fichier d'état.
MAX_LIGNES_SORTIE_PUSH = 60
MAX_CARACTERES_SORTIE_PUSH = 20000

# Fichier local, ignoré par git comme les autres journaux de ce dossier
# (`changelog_fusion.log`, `decisions_fichiers_ignores.log`,
# `bruit_projets.log` — voir le `.gitignore` racine) : une entrée par
# projet, jamais commise.
CHEMIN_ETAT_PUSH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "push_arriere_plan_etat.json")

# Un seul verrou process-wide pour toute lecture-modification-écriture du
# fichier d'état : protège la vérification « déjà en cours ? » suivie de
# l'écriture de l'entrée « en_cours » contre une course entre deux requêtes
# simultanées sur le même projet (issue #122, point 3) — la durée réelle du
# push, elle, n'est jamais tenue sous ce verrou (seulement ces écritures
# brèves), donc ne bloque jamais une requête sur un AUTRE projet.
_VERROU_ECRITURE = threading.Lock()


def _maintenant_iso():
    return datetime.now().isoformat(timespec="seconds")


def _lire_etat_brut(chemin_etat):
    """Dégradation systématique vers un état vide (issue #122, point 4) :
    fichier absent, illisible, JSON corrompu, ou contenu qui n'est pas un
    objet -> `{}`, jamais d'exception, jamais d'erreur affichée."""
    try:
        with open(chemin_etat, encoding="utf-8") as fichier:
            etat = json.load(fichier)
    except (OSError, json.JSONDecodeError):
        return {}
    return etat if isinstance(etat, dict) else {}


def _ecrire_etat_brut(etat, chemin_etat):
    """Écriture atomique (fichier temporaire puis `os.replace`) pour qu'un
    lecteur concurrent (page projet, à chaque affichage) ne voie jamais un
    JSON à moitié écrit. Retourne False sans lever d'exception si
    l'écriture échoue (dossier en lecture seule, disque plein...) — une
    écriture impossible ne doit jamais empêcher ni masquer un push (issue
    #122, garde-fou), seulement déclencher un avertissement côté appelant."""
    dossier = os.path.dirname(chemin_etat) or "."
    try:
        descripteur, chemin_tmp = tempfile.mkstemp(dir=dossier, prefix=".push_arriere_plan_etat_")
    except OSError:
        return False
    try:
        with os.fdopen(descripteur, "w", encoding="utf-8") as fichier:
            json.dump(etat, fichier, ensure_ascii=False, indent=2)
        os.replace(chemin_tmp, chemin_etat)
        return True
    except OSError:
        try:
            os.remove(chemin_tmp)
        except OSError:
            pass
        return False


def _tronquer_sortie(texte):
    """Fin de la sortie seulement, taille bornée (issue #122, point 4) :
    d'abord un plafond de caractères (pour qu'une seule ligne géante ne
    contourne pas le plafond de lignes), puis un plafond de lignes."""
    if not texte:
        return ""
    if len(texte) > MAX_CARACTERES_SORTIE_PUSH:
        texte = texte[-MAX_CARACTERES_SORTIE_PUSH:]
    lignes = texte.splitlines()
    if len(lignes) > MAX_LIGNES_SORTIE_PUSH:
        lignes = lignes[-MAX_LIGNES_SORTIE_PUSH:]
    return "\n".join(lignes)


def lire_entree(nom_projet, chemin_etat=None):
    """Entrée actuelle de `nom_projet`, ou None si aucune (jamais eu de
    push en arrière-plan, ou fichier d'état absent/corrompu)."""
    return _lire_etat_brut(chemin_etat or CHEMIN_ETAT_PUSH).get(nom_projet)


def ecrire_entree(nom_projet, chemin_etat=None, **champs):
    """Met à jour (fusion, pas remplacement) l'entrée de `nom_projet` avec
    `champs`, sous le verrou d'écriture. Retourne le succès de l'écriture
    (voir `_ecrire_etat_brut`)."""
    chemin = chemin_etat or CHEMIN_ETAT_PUSH
    with _VERROU_ECRITURE:
        etat = _lire_etat_brut(chemin)
        entree = dict(etat.get(nom_projet) or {})
        entree.update(champs)
        etat[nom_projet] = entree
        return _ecrire_etat_brut(etat, chemin)


def marquer_vu(nom_projet, chemin_etat=None):
    """Acquitte le résultat affiché (bouton « Vu », issue #122, point 5) —
    ne change jamais `etat` ni aucun autre champ, seulement `vu`."""
    return ecrire_entree(nom_projet, chemin_etat=chemin_etat, vu=True)


# Champs exposés par `etats_a_signaler` (issue #123) à la route de sondage
# HTTP et à la barre latérale — jamais `repertoire` ni `pid`, propres à
# cette machine et sans intérêt pour l'affichage.
_CHAMPS_ETAT_PUBLIC = ("etat", "vu", "debut", "fin", "branches", "sortie", "resultats")


def etats_a_signaler(chemin_etat=None):
    """Sous-ensemble de l'état persistant à afficher globalement (issue
    #123, point 1) : seuls les projets dont un push est en cours, ou dont
    le dernier résultat n'a pas encore été acquitté (`vu` faux) — un projet
    jamais poussé en arrière-plan, ou dont le dernier résultat est déjà
    acquitté, n'y figure pas du tout (c'est précisément ce qui permet à la
    barre latérale de redevenir normale une fois un refus vu). Réutilisé à
    la fois par la route `/push/etat` (sondage JS) et par la barre latérale
    côté serveur (premier rendu de page, avant que le JS n'ait sondé quoi
    que ce soit)."""
    etat = _lire_etat_brut(chemin_etat or CHEMIN_ETAT_PUSH)
    resultat = {}
    for nom_projet, entree in etat.items():
        if not isinstance(entree, dict):
            continue
        if entree.get("etat") != "en_cours" and entree.get("vu"):
            continue
        resultat[nom_projet] = {champ: entree.get(champ) for champ in _CHAMPS_ETAT_PUBLIC}
    return resultat


def projet_verrouille_par_push(nom_projet, chemin_etat=None):
    """True si un push en arrière-plan est actuellement en cours pour
    `nom_projet` — sert de verrou (issue #122, point 3) : un second push
    sur ce même projet, ou toute autre action git qui le modifie, doit
    être refusé tant que ceci est vrai. Une entrée `en_cours` ne peut
    provenir que d'un thread réellement actif DANS CE PROCESS (voir le
    docstring de ce module) — sauf juste après un redémarrage, corrigé une
    fois pour toutes par `reconcilier_au_demarrage`."""
    entree = lire_entree(nom_projet, chemin_etat)
    return bool(entree) and entree.get("etat") == "en_cours"


def _etat_global(tue_par_timeout, code_retour, resultats):
    """État global du projet à l'issue d'une tentative de push (issue
    #122) à partir du résultat réel par branche (`resultats`, même forme
    que `git_info.verifier_push_apres_timeout` : {"ok": True/False/None,
    ...}, jamais la seule supposition du code de sortie ou du timeout) :

    - `tue_par_timeout` (le groupe de processus a été tué par ce module,
      délai dépassé) -> toujours "interrompu" : le process n'est jamais
      allé jusqu'au bout de ses propres termes, sa sortie est
      nécessairement incomplète, même si le résultat réel révèle que le
      push a malgré tout abouti juste avant le coup de `killpg` (même
      piège que l'issue #66) — le détail par branche reste consultable.
    - sinon, code de sortie 0 ET toutes les branches confirmées poussées
      -> "pousse".
    - sinon, au moins une branche confirmée NON poussée -> "refuse" (le
      crochet ou git a rejeté le push — cas normal à afficher avec la fin
      de sortie des tests, jusqu'à acquittement).
    - sinon (aucune branche confirmée ni dans un sens ni dans l'autre,
      échec de la vérification réseau elle-même) -> "indetermine"."""
    if tue_par_timeout:
        return "interrompu"
    valeurs = [r.get("ok") for r in resultats.values()]
    if not valeurs:
        return "indetermine"
    if code_retour == 0 and all(v is True for v in valeurs):
        return "pousse"
    if any(v is False for v in valeurs):
        return "refuse"
    return "indetermine"


def _executer_push_arriere_plan(repertoire, nom_projet, branches, chemin_etat):
    """Tourne dans un thread démon lancé par `demarrer_push_arriere_plan` —
    jamais appelée directement. Un seul `git push` pour toutes les
    `branches` (issue #122, point 2 : le crochet ne tourne qu'une fois),
    le résultat réel étant de toute façon établi branche par branche après
    coup via `git_info.verifier_push_apres_timeout`, indépendamment du
    code de sortie global de la commande."""
    remote = git_info.get_remote_defaut(repertoire)
    commande = ["git", "-C", repertoire, "push", remote, *branches]
    try:
        processus = subprocess.Popen(
            commande, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, start_new_session=True,
        )
    except OSError as exc:
        ecrire_entree(
            nom_projet, chemin_etat=chemin_etat, etat="indetermine", fin=_maintenant_iso(),
            sortie=_tronquer_sortie(f"Impossible de lancer « {' '.join(commande)} » : {exc}"),
            pid=None, resultats={},
        )
        return

    # Mémorise le pid tout de suite (son groupe de processus, issue #122 —
    # `start_new_session=True` fait de ce pid le pgid du groupe) : seule
    # trace qui permette à `reconcilier_au_demarrage`, après un redémarrage
    # de relecture_web, de savoir si le process est toujours vivant.
    ecrire_entree(nom_projet, chemin_etat=chemin_etat, pid=processus.pid)

    tue_par_timeout = False
    try:
        sortie, _ = processus.communicate(timeout=TIMEOUT_PUSH_ARRIERE_PLAN)
    except subprocess.TimeoutExpired:
        tue_par_timeout = True
        try:
            os.killpg(processus.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            pass
        try:
            sortie, _ = processus.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            processus.kill()
            try:
                sortie, _ = processus.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                sortie = ""

    code_retour = processus.returncode
    resultats = {
        branche: git_info.verifier_push_apres_timeout(repertoire, branche) for branche in branches
    }
    etat_global = _etat_global(tue_par_timeout, code_retour, resultats)
    ecrire_entree(
        nom_projet, chemin_etat=chemin_etat, etat=etat_global, fin=_maintenant_iso(),
        sortie=_tronquer_sortie(sortie or ""), pid=None, resultats=resultats,
        vu=(etat_global == "pousse"),
    )


def demarrer_push_arriere_plan(repertoire, nom_projet, branches, chemin_etat=None):
    """Démarre, si possible, le push en arrière-plan de `branches` pour
    `nom_projet` (déjà confirmé équipé d'un crochet pre-push par
    l'appelant, voir `git_info.projet_equipe_hook_pre_push`). Retourne
    `(demarre, avertissement)` :

    - `(False, message_refus)` si un push est déjà en cours sur ce projet
      (issue #122, point 3) — rien n'est démarré, aucune écriture.
    - `(True, None)` si le push démarre normalement.
    - `(True, message_avertissement)` si le push démarre malgré une
      écriture d'état impossible (garde-fou du point 4 : une écriture
      impossible ne doit jamais empêcher ni masquer le push lui-même)."""
    chemin = chemin_etat or CHEMIN_ETAT_PUSH
    with _VERROU_ECRITURE:
        etat = _lire_etat_brut(chemin)
        if (etat.get(nom_projet) or {}).get("etat") == "en_cours":
            return False, "❌ Un push est déjà en cours sur ce projet — attendez qu'il se termine avant d'en relancer un."
        etat[nom_projet] = {
            "etat": "en_cours", "branches": list(branches), "repertoire": repertoire,
            "debut": _maintenant_iso(), "fin": None, "sortie": "", "vu": False,
            "pid": None, "resultats": {},
        }
        ecrit = _ecrire_etat_brut(etat, chemin)

    thread = threading.Thread(
        target=_executer_push_arriere_plan,
        args=(repertoire, nom_projet, list(branches), chemin),
        daemon=True,
    )
    thread.start()

    if not ecrit:
        return True, "⚠️ Le fichier d'état du push n'a pas pu être écrit — le push démarre malgré tout, son résultat ne sera pas affiché ici."
    return True, None


def reconcilier_au_demarrage(chemin_etat=None):
    """À appeler une seule fois, juste avant de démarrer le serveur (issue
    #122, point 4) : toute entrée restée « en_cours » ne peut provenir que
    d'un thread du process relecture_web PRÉCÉDENT (voir le docstring de ce
    module) — sauf si le process git lui-même, détaché dans son propre
    groupe, tourne encore en orphelin (pid toujours vivant) : dans ce seul
    cas, l'entrée est laissée telle quelle (toujours verrouillée), faute de
    pouvoir savoir quand il se terminera. Sinon, marquée « interrompu » puis
    revérifiée par branche (`git_info.verifier_push_apres_timeout`, résultat
    réel noté dans `resultats`). Fichier d'état absent/corrompu -> rien à
    faire, jamais d'erreur."""
    chemin = chemin_etat or CHEMIN_ETAT_PUSH
    with _VERROU_ECRITURE:
        etat = _lire_etat_brut(chemin)
        modifie = False
        for nom_projet, entree in etat.items():
            if not isinstance(entree, dict) or entree.get("etat") != "en_cours":
                continue
            pid = entree.get("pid")
            if pid is not None and git_info._pid_vivant(pid):
                continue

            repertoire = entree.get("repertoire")
            branches = entree.get("branches") or []
            resultats = {}
            if repertoire:
                resultats = {
                    branche: git_info.verifier_push_apres_timeout(repertoire, branche)
                    for branche in branches
                }
            note = "⚠️ relecture_web a redémarré pendant ce push — état réel revérifié ci-dessus."
            ancienne_sortie = entree.get("sortie") or ""
            entree["etat"] = "interrompu"
            entree["fin"] = _maintenant_iso()
            entree["pid"] = None
            entree["vu"] = False
            entree["resultats"] = resultats
            entree["sortie"] = _tronquer_sortie(f"{ancienne_sortie}\n{note}" if ancienne_sortie else note)
            modifie = True
        if modifie:
            _ecrire_etat_brut(etat, chemin)
