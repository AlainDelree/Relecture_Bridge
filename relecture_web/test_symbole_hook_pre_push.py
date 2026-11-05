#!/usr/bin/env python3
"""Tests de l'issue #129 : symbole « crochet pre-push actif » (ou
avertissement « présent mais non exécutable ») affiché devant le nom du
projet sur la page « branches d'un projet » (`projet.html`).

Couvre :
- `git_info.projet_a_hook_pre_push_non_executable` : nouvelle fonction pour
  le cas avertissement, même résolution de chemin que
  `projet_equipe_hook_pre_push` (`chemin_hook_pre_push`) — crochet absent,
  présent et exécutable, présent et non exécutable, projet distant (PC fixe
  CCW, jamais vrai).
- Rendu de `app.projet_route` : le symbole actif (🪝) réutilise EXACTEMENT
  `projet_equipe_hook_pre_push` (pas une seconde logique de détection,
  issue #129), le symbole d'avertissement (⚠️) apparaît pour un crochet non
  exécutable, aucun des deux pour un projet sans crochet, et une détection
  qui lève une exception laisse la page se charger normalement sans aucun
  symbole (garde-fou de l'issue).

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), même harnais que
`test_push_arriere_plan.py` (projet injecté via `git_info.fetch_projets`).
Aucun accès réseau réel, aucune lecture/écriture des vrais fichiers locaux
de relecture_web : dépôt jetable créé dans un dossier temporaire par test."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module  # noqa: E402  (après l'ajustement de sys.path ci-dessus)
import git_info  # noqa: E402


def _init_depot(chemin):
    os.makedirs(chemin, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "-b", "main", chemin], check=True)
    subprocess.run(["git", "config", "user.email", "t@e.com"], cwd=chemin, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin, check=True)
    subprocess.run(["git", "commit", "--quiet", "--allow-empty", "-m", "init"], cwd=chemin, check=True)


def _installer_hook_pre_push(chemin_local, executable=True):
    chemin_hook = git_info.chemin_hook_pre_push(chemin_local)
    os.makedirs(os.path.dirname(chemin_hook), exist_ok=True)
    with open(chemin_hook, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\nexit 0\n")
    if executable:
        os.chmod(chemin_hook, 0o755)
    return chemin_hook


class DetectionHookNonExecutableTestCase(unittest.TestCase):
    """`git_info.projet_a_hook_pre_push_non_executable`, même résolution de
    chemin que `projet_equipe_hook_pre_push` (déjà testée dans
    `test_push_arriere_plan.py`)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_hook_non_exec_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self.repertoire = os.path.join(self.scratch, "depot")
        _init_depot(self.repertoire)

    def test_hook_absent(self):
        self.assertFalse(git_info.projet_a_hook_pre_push_non_executable(self.repertoire))

    def test_hook_present_et_executable(self):
        _installer_hook_pre_push(self.repertoire, executable=True)
        self.assertFalse(git_info.projet_a_hook_pre_push_non_executable(self.repertoire))
        self.assertTrue(git_info.projet_equipe_hook_pre_push(self.repertoire))

    def test_hook_present_mais_non_executable(self):
        _installer_hook_pre_push(self.repertoire, executable=False)
        self.assertTrue(git_info.projet_a_hook_pre_push_non_executable(self.repertoire))
        self.assertFalse(git_info.projet_equipe_hook_pre_push(self.repertoire))

    def test_projet_distant_jamais_signale(self):
        chemin_windows = r"C:\CCW\projet_fictif"
        self.assertFalse(git_info.projet_a_hook_pre_push_non_executable(chemin_windows))


class SymbolePagePorjetTestCase(unittest.TestCase):
    """Rendu de la page « branches d'un projet » (`app.projet_route` +
    `projet.html`)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_symbole_hook_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self.repertoire = os.path.join(self.scratch, "projet_local")
        _init_depot(self.repertoire)

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

    def _restaurer_fetch(self):
        git_info.fetch_projets = self._fetch_original

    def _page(self):
        return self.client.get("/projet/projet_local").get_data(as_text=True)

    def test_hook_executable_affiche_symbole_actif(self):
        _installer_hook_pre_push(self.repertoire, executable=True)
        page = self._page()
        self.assertIn("symbole-hook-pre-push", page)
        self.assertIn("🪝", page)
        self.assertIn("Crochet pre-push actif : les tests se lancent avant chaque push", page)
        self.assertNotIn("Crochet pre-push présent mais non exécutable", page)

    def test_hook_non_executable_affiche_avertissement(self):
        _installer_hook_pre_push(self.repertoire, executable=False)
        page = self._page()
        self.assertIn("symbole-hook-pre-push--avertissement", page)
        self.assertIn(
            "Crochet pre-push présent mais non exécutable : ignoré par git, aucun test ne se lance", page,
        )
        self.assertNotIn("Crochet pre-push actif", page)

    def test_aucun_hook_aucun_symbole(self):
        page = self._page()
        self.assertNotIn("symbole-hook-pre-push", page)

    def test_erreur_detection_page_chargee_sans_symbole(self):
        """Une détection qui lève une exception ne doit jamais faire planter
        la page (garde-fou de l'issue #129) — seulement absence du symbole,
        page chargée normalement par ailleurs."""
        _installer_hook_pre_push(self.repertoire, executable=True)
        original = app_module.projet_equipe_hook_pre_push

        def _detection_cassee(repertoire):
            raise RuntimeError("détection cassée (test)")

        app_module.projet_equipe_hook_pre_push = _detection_cassee
        self.addCleanup(lambda: setattr(app_module, "projet_equipe_hook_pre_push", original))

        reponse = self.client.get("/projet/projet_local")
        self.assertEqual(reponse.status_code, 200)
        page = reponse.get_data(as_text=True)
        self.assertNotIn("symbole-hook-pre-push", page)
        self.assertIn("projet_local", page)


if __name__ == "__main__":
    unittest.main()
