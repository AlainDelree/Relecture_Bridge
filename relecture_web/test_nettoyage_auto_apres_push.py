#!/usr/bin/env python3
"""Tests de l'issue #128 : nettoyage automatique des résumés déjà pushés
après un push confirmé abouti depuis relecture_web (jusqu'ici réservé au
bouton « Nettoyer ce projet », issue #68, qu'il fallait recliquer).

Couvre les deux chemins de push existants (issue #122) :
- Push synchrone (projet SANS crochet pre-push, `pousser_branches_route`) :
  nettoyage juste après la confirmation du résultat (push direct ou
  vérification après dépassement de délai), compte de résumés supprimés
  ajouté au message flash existant.
- Push en arrière-plan (projet équipé d'un crochet pre-push,
  `push_arriere_plan._executer_push_arriere_plan`) : nettoyage à la fin du
  thread, seulement si l'état final est « pousse », sans message et sans
  effet sur l'entrée d'état écrite.

Dans les deux cas, réutilise `resumes_info.nettoyer_resumes_pousses` (donc
`lister_fichiers_resumes_pushes`/`get_commit_est_pushe`, même garde-fou que
le bouton manuel) — jamais une seconde implémentation. Aucun nettoyage pour
un push refusé, interrompu ou indéterminé ; jamais pour un projet distant
(pas de dossier `Non_Lu` local) ; une erreur de nettoyage reste sans effet
sur le résultat du push affiché.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_nettoyage_auto_apres_push -v` depuis
la racine du dépôt, ou directement
`python3 relecture_web/test_nettoyage_auto_apres_push.py`.

Aucun accès réseau réel, et aucune lecture/écriture des vrais fichiers
locaux de relecture_web : dépôts/remotes/état/dossier `Non_Lu` jetables
créés dans un dossier temporaire par test (même pattern que
`test_push_arriere_plan.py`) — `resumes_info.DOSSIER_RELECTURE` et
`push_arriere_plan.CHEMIN_ETAT_PUSH` sont redirigés pour toute la durée de
chaque test."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module  # noqa: E402  (après l'ajustement de sys.path ci-dessus)
import git_info  # noqa: E402
import push_arriere_plan  # noqa: E402
import resumes_info  # noqa: E402


def _init_depot_avec_remote(chemin_local, chemin_remote):
    os.makedirs(chemin_remote, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "--bare", chemin_remote], check=True)
    os.makedirs(chemin_local, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "-b", "main", chemin_local], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=chemin_local, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin_local, check=True)
    with open(os.path.join(chemin_local, "fichier.txt"), "w", encoding="utf-8") as f:
        f.write("contenu\n")
    subprocess.run(["git", "add", "fichier.txt"], cwd=chemin_local, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "initial"], cwd=chemin_local, check=True)
    subprocess.run(["git", "remote", "add", "origin", chemin_remote], cwd=chemin_local, check=True)
    subprocess.run(["git", "push", "--quiet", "origin", "main"], cwd=chemin_local, check=True)


def _creer_branche(chemin_local, nom):
    subprocess.run(["git", "checkout", "-b", nom], cwd=chemin_local, check=True, capture_output=True)
    with open(os.path.join(chemin_local, f"{nom}.txt"), "w", encoding="utf-8") as f:
        f.write(f"contenu {nom}\n")
    subprocess.run(["git", "add", f"{nom}.txt"], cwd=chemin_local, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", f"commit {nom}"], cwd=chemin_local, check=True)
    subprocess.run(["git", "checkout", "main"], cwd=chemin_local, check=True, capture_output=True)


def _installer_hook_pre_push(chemin_local, script_texte, executable=True):
    chemin_hook = git_info.chemin_hook_pre_push(chemin_local)
    os.makedirs(os.path.dirname(chemin_hook), exist_ok=True)
    with open(chemin_hook, "w", encoding="utf-8") as f:
        f.write(script_texte)
    if executable:
        os.chmod(chemin_hook, 0o755)
    return chemin_hook


def _hash_local(chemin_local, branche):
    resultat = subprocess.run(
        ["git", "rev-parse", f"refs/heads/{branche}"],
        cwd=chemin_local, capture_output=True, text=True, check=True,
    )
    return resultat.stdout.strip()


class BaseNettoyageAutoTestCase(unittest.TestCase):
    """Harnais Flask commun : un projet local avec remote bare jetable,
    état du push ET dossier `Non_Lu` redirigés vers des emplacements
    temporaires (jamais les vrais fichiers de relecture_web)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_nettoyage_auto_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self._dossier_relecture_original = resumes_info.DOSSIER_RELECTURE
        resumes_info.DOSSIER_RELECTURE = self.scratch
        self.addCleanup(self._restaurer_dossier_relecture)

        self._chemin_etat_original = push_arriere_plan.CHEMIN_ETAT_PUSH
        push_arriere_plan.CHEMIN_ETAT_PUSH = os.path.join(self.scratch, "push_etat.json")
        self.addCleanup(self._restaurer_chemin_etat)

        self._timeout_original = push_arriere_plan.TIMEOUT_PUSH_ARRIERE_PLAN
        self.addCleanup(self._restaurer_timeout)

        self.repertoire = os.path.join(self.scratch, "projet_local")
        self.remote = os.path.join(self.scratch, "projet_local_remote.git")
        _init_depot_avec_remote(self.repertoire, self.remote)

        self.projets = [
            {
                "nom": "projet_local", "depot": "projet_local", "repertoire": self.repertoire,
                "couleur": None, "couleur_texte": None,
            },
        ]
        self._fetch_original = git_info.fetch_projets
        git_info.fetch_projets = lambda: self.projets
        self.addCleanup(self._restaurer_fetch)

        app_module.app.config["TESTING"] = True
        app_module.app.config["MDP_EXIGE"] = False
        self.client = app_module.app.test_client()

    def _restaurer_dossier_relecture(self):
        resumes_info.DOSSIER_RELECTURE = self._dossier_relecture_original

    def _restaurer_chemin_etat(self):
        push_arriere_plan.CHEMIN_ETAT_PUSH = self._chemin_etat_original

    def _restaurer_timeout(self):
        push_arriere_plan.TIMEOUT_PUSH_ARRIERE_PLAN = self._timeout_original

    def _restaurer_fetch(self):
        git_info.fetch_projets = self._fetch_original

    def _creer_resume(self, hash_commit, suffixe="diff"):
        """Crée un fichier `Non_Lu/<hash>_test.<suffixe>` factice pour
        « projet_local » — un seul fichier suffit : `lister_fichiers_resumes_pushes`
        ne filtre jamais par extension, seulement par hash."""
        dossier = os.path.join(self.scratch, "projet_local", "Non_Lu")
        os.makedirs(dossier, exist_ok=True)
        chemin = os.path.join(dossier, f"{hash_commit}_test.{suffixe}")
        with open(chemin, "w", encoding="utf-8") as f:
            f.write("contenu de test\n")
        return chemin

    def _espionner_nettoyage_arriere_plan(self):
        """Remplace `resumes_info.nettoyer_resumes_pousses` par un espion qui
        continue d'appeler l'implémentation réelle — compte les appels sans
        changer le comportement. `push_arriere_plan._executer_push_arriere_plan`
        y accède via `resumes_info.nettoyer_resumes_pousses(...)` (attribut de
        module), donc ce patch est bien vu."""
        appels = []
        original = resumes_info.nettoyer_resumes_pousses

        def espion(*args, **kwargs):
            appels.append((args, kwargs))
            return original(*args, **kwargs)

        resumes_info.nettoyer_resumes_pousses = espion
        self.addCleanup(lambda: setattr(resumes_info, "nettoyer_resumes_pousses", original))
        return appels

    def _espionner_nettoyage_synchrone(self):
        """Même principe que ci-dessus, mais pour le chemin synchrone :
        `app.py` a importé `nettoyer_resumes_pousses` par valeur dans son
        propre espace de noms (`from resumes_info import ...`), donc c'est
        `app_module.nettoyer_resumes_pousses` qu'il faut patcher ici."""
        appels = []
        original = app_module.nettoyer_resumes_pousses

        def espion(*args, **kwargs):
            appels.append((args, kwargs))
            return original(*args, **kwargs)

        app_module.nettoyer_resumes_pousses = espion
        self.addCleanup(lambda: setattr(app_module, "nettoyer_resumes_pousses", original))
        return appels

    def _attendre_fin_push(self, nom_projet="projet_local", timeout=10.0):
        fin = time.time() + timeout
        while time.time() < fin:
            entree = push_arriere_plan.lire_entree(nom_projet)
            if entree and entree.get("etat") != "en_cours":
                return entree
            time.sleep(0.03)
        raise AssertionError("le push en arrière-plan ne s'est pas terminé à temps")


class PushSynchroneNettoyageTestCase(BaseNettoyageAutoTestCase):
    """Projet SANS crochet pre-push : chemin synchrone de `pousser_branches_route`."""

    def test_nettoyage_declenche_apres_push_synchrone_abouti(self):
        appels = self._espionner_nettoyage_synchrone()
        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        reponse = self.client.post(
            "/projet/projet_local/pousser", data={"branches": ["feature-a"]}, follow_redirects=True,
        )
        texte = reponse.get_data(as_text=True)

        self.assertIn("poussée", texte)
        self.assertIn("1 résumé(s) déjà pushé(s) nettoyé(s) automatiquement", texte)
        self.assertFalse(os.path.exists(chemin_resume))
        self.assertEqual(len(appels), 1)

    def test_resume_non_encore_pousse_conserve(self):
        """Un résumé dont le commit n'est PAS sur la branche poussée doit
        survivre au nettoyage automatique — même garde-fou que le bouton
        manuel (`get_commit_est_pushe`)."""
        _creer_branche(self.repertoire, "feature-a")
        _creer_branche(self.repertoire, "feature-b")
        hash_a = _hash_local(self.repertoire, "feature-a")[:7]
        hash_b = _hash_local(self.repertoire, "feature-b")[:7]
        chemin_a = self._creer_resume(hash_a)
        chemin_b = self._creer_resume(hash_b)

        self.client.post(
            "/projet/projet_local/pousser", data={"branches": ["feature-a"]}, follow_redirects=True,
        )

        self.assertFalse(os.path.exists(chemin_a), "le résumé du commit poussé aurait dû être supprimé")
        self.assertTrue(os.path.exists(chemin_b), "le résumé du commit non poussé doit être conservé")

    def test_nettoyage_non_declenche_apres_push_refuse(self):
        appels = self._espionner_nettoyage_synchrone()
        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        # Remote cassé : le push échoue (resultat["ok"] est False), donc le
        # nettoyage automatique ne doit jamais être tenté.
        subprocess.run(
            ["git", "remote", "set-url", "origin", os.path.join(self.scratch, "remote_inexistant")],
            cwd=self.repertoire, check=True,
        )

        reponse = self.client.post(
            "/projet/projet_local/pousser", data={"branches": ["feature-a"]}, follow_redirects=True,
        )
        texte = reponse.get_data(as_text=True)

        self.assertIn("Échec du push", texte)
        self.assertNotIn("nettoyé(s) automatiquement", texte)
        self.assertTrue(os.path.exists(chemin_resume))
        self.assertEqual(appels, [])

    def test_erreur_de_nettoyage_sans_effet_sur_le_resultat_du_push(self):
        original = app_module.nettoyer_resumes_pousses

        def nettoyage_casse(*args, **kwargs):
            raise RuntimeError("panne factice du nettoyage")

        app_module.nettoyer_resumes_pousses = nettoyage_casse
        self.addCleanup(lambda: setattr(app_module, "nettoyer_resumes_pousses", original))

        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        reponse = self.client.post(
            "/projet/projet_local/pousser", data={"branches": ["feature-a"]}, follow_redirects=True,
        )
        texte = reponse.get_data(as_text=True)

        self.assertEqual(reponse.status_code, 200)
        self.assertIn("poussée", texte)
        # La panne du nettoyage ne doit jamais remonter dans le message, ni
        # faire échouer l'affichage du résultat du push lui-même.
        self.assertNotIn("panne factice", texte)
        # Le fichier reste en place puisque le nettoyage a échoué avant de
        # pouvoir le supprimer — mais ceci n'est pas le point testé : seul
        # l'absence d'erreur affichée compte ici.
        self.assertTrue(os.path.exists(chemin_resume))


class PushArrierePlanNettoyageTestCase(BaseNettoyageAutoTestCase):
    """Projet équipé d'un crochet pre-push : chemin en arrière-plan de
    `push_arriere_plan._executer_push_arriere_plan`."""

    def test_nettoyage_declenche_apres_push_arriere_plan_abouti(self):
        appels = self._espionner_nettoyage_arriere_plan()
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 0\n")
        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        demarre, avertissement = push_arriere_plan.demarrer_push_arriere_plan(
            self.repertoire, "projet_local", ["feature-a"],
        )
        self.assertTrue(demarre)
        self.assertIsNone(avertissement)

        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "pousse")
        self.assertFalse(os.path.exists(chemin_resume))
        self.assertEqual(len(appels), 1)
        # Aucun effet sur les champs de l'état persistant — pas de nouveau
        # champ "nettoyage" ni de message ajouté à la sortie.
        self.assertNotIn("nettoyage", entree)

    def test_nettoyage_non_declenche_apres_push_refuse(self):
        appels = self._espionner_nettoyage_arriere_plan()
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 1\n")
        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        demarre, avertissement = push_arriere_plan.demarrer_push_arriere_plan(
            self.repertoire, "projet_local", ["feature-a"],
        )
        self.assertTrue(demarre)

        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "refuse")
        self.assertEqual(appels, [])
        self.assertTrue(os.path.exists(chemin_resume))

    def test_nettoyage_non_declenche_apres_push_interrompu(self):
        appels = self._espionner_nettoyage_arriere_plan()
        push_arriere_plan.TIMEOUT_PUSH_ARRIERE_PLAN = 0.4
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nsleep 30\n")
        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        demarre, avertissement = push_arriere_plan.demarrer_push_arriere_plan(
            self.repertoire, "projet_local", ["feature-a"],
        )
        self.assertTrue(demarre)

        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "interrompu")
        self.assertEqual(appels, [])
        self.assertTrue(os.path.exists(chemin_resume))

    def test_nettoyage_non_declenche_apres_push_indetermine(self):
        appels = self._espionner_nettoyage_arriere_plan()
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 0\n")
        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        # Remote cassé pour le push ET sa revérification : ni confirmé
        # poussé, ni confirmé non-poussé -> état "indetermine".
        subprocess.run(
            ["git", "remote", "set-url", "origin", os.path.join(self.scratch, "remote_inexistant")],
            cwd=self.repertoire, check=True,
        )

        demarre, avertissement = push_arriere_plan.demarrer_push_arriere_plan(
            self.repertoire, "projet_local", ["feature-a"],
        )
        self.assertTrue(demarre)

        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "indetermine")
        self.assertEqual(appels, [])
        self.assertTrue(os.path.exists(chemin_resume))

    def test_erreur_de_nettoyage_sans_effet_sur_letat_du_push(self):
        original = resumes_info.nettoyer_resumes_pousses

        def nettoyage_casse(*args, **kwargs):
            raise RuntimeError("panne factice du nettoyage")

        resumes_info.nettoyer_resumes_pousses = nettoyage_casse
        self.addCleanup(lambda: setattr(resumes_info, "nettoyer_resumes_pousses", original))

        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 0\n")
        _creer_branche(self.repertoire, "feature-a")
        hash_commit = _hash_local(self.repertoire, "feature-a")[:7]
        chemin_resume = self._creer_resume(hash_commit)

        demarre, avertissement = push_arriere_plan.demarrer_push_arriere_plan(
            self.repertoire, "projet_local", ["feature-a"],
        )
        self.assertTrue(demarre)

        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "pousse")
        # Le résumé reste en place puisque le nettoyage a échoué, mais le
        # point testé est que le push lui-même est quand même rapporté comme
        # abouti malgré la panne du nettoyage.
        self.assertTrue(os.path.exists(chemin_resume))


class ProjetDistantNonDeclencheTestCase(unittest.TestCase):
    """Un projet distant (PC fixe CCW) n'a jamais de dossier `Non_Lu` local
    (pas de hook post-commit sur le clone Windows, voir `nettoyer_projet_route`)
    — le nettoyage automatique doit être refusé avant même de tenter une
    lecture/écriture locale, exactement comme le bouton manuel."""

    def test_suffixe_nettoyage_vide_pour_projet_distant(self):
        appels = []
        original = app_module.nettoyer_resumes_pousses

        def espion(*args, **kwargs):
            appels.append((args, kwargs))
            return original(*args, **kwargs)

        app_module.nettoyer_resumes_pousses = espion
        try:
            resultat = app_module._suffixe_nettoyage_auto_apres_push(
                {"distant": True, "dossier_relecture": "peu_importe", "repertoire": "/chemin/inexistant"}
            )
        finally:
            app_module.nettoyer_resumes_pousses = original

        self.assertEqual(resultat, "")
        self.assertEqual(appels, [])


if __name__ == "__main__":
    unittest.main()
