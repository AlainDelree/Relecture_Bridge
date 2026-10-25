#!/usr/bin/env python3
"""Tests de la prise en charge des chemins Windows (lignes <nom>_ccw du
tableau §2 de BRIDGE_AGENT_DOC.md, issue #108, suite de #94) :

- `git_info.chemins_windows_egaux` / `nom_dossier_chemin_windows` /
  `worktree_est_principal` — reconnaissance du worktree principal d'un
  projet distant malgré barres obliques inverses vs normales, casse, barre
  finale, et comportement inchangé pour un projet local ;
- `git_info.fusionner_changelog_worktree` — refus explicite pour un projet
  distant plutôt qu'un faux-négatif silencieux (lecture/écriture de fichier
  hors des commandes git routées) ;
- `installer.sh` — message explicite pour une ligne à chemin Windows,
  distinct du message « pas un dépôt git », sans jamais installer de hook
  dans un vrai dépôt (tableau factice en scratch, `curl` simulé).

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_chemins_windows_ccw -v` depuis la
racine du dépôt, ou directement
`python3 relecture_web/test_chemins_windows_ccw.py`.

Aucun accès réseau réel : la comparaison de chemins est testée via les
fonctions isolées de `git_info.py` (pas de faux `ssh` nécessaire, le module
n'en avait pas encore au moment de cette issue), et `installer.sh` est
exécuté avec un `curl` factice (scratch) qui ne contacte jamais GitHub."""

import os
import stat
import subprocess
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import git_info  # noqa: E402  (après l'ajustement de sys.path ci-dessus)


RACINE_DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CheminsWindowsEgauxTestCase(unittest.TestCase):
    """`chemins_windows_egaux` : comparaison de chemins Windows (issue #108)."""

    def test_barres_obliques_inverses_contre_normales(self):
        self.assertTrue(git_info.chemins_windows_egaux(
            "C:\\CCW\\rummikub", "C:/CCW/rummikub",
        ))

    def test_casse_differente(self):
        self.assertTrue(git_info.chemins_windows_egaux(
            "C:\\CCW\\rummikub", "c:\\ccw\\RUMMIKUB",
        ))

    def test_barre_finale(self):
        self.assertTrue(git_info.chemins_windows_egaux(
            "C:\\CCW\\rummikub", "C:/CCW/rummikub/",
        ))

    def test_combinaison_des_trois(self):
        self.assertTrue(git_info.chemins_windows_egaux(
            "C:\\CCW\\rummikub", "c:/ccw/RUMMIKUB/",
        ))

    def test_chemin_reellement_different(self):
        # Un autre worktree du même clone (ex. worktree dédié CCL) : doit
        # rester distingué du dossier principal, pas confondu avec lui.
        self.assertFalse(git_info.chemins_windows_egaux(
            "C:\\CCW\\rummikub", "C:\\CCW\\rummikub-worktrees\\feature-x",
        ))

    def test_chemin_different_meme_prefixe(self):
        # Piège courant d'une comparaison trop permissive (sous-chaîne) :
        # un chemin plus long partageant le même préfixe ne doit jamais
        # être jugé égal à l'exact chemin principal.
        self.assertFalse(git_info.chemins_windows_egaux(
            "C:\\CCW\\rummikub", "C:\\CCW\\rummikub2",
        ))


class NomDossierCheminWindowsTestCase(unittest.TestCase):
    """`nom_dossier_chemin_windows` : pendant distant de `os.path.basename`."""

    def test_barres_obliques_inverses(self):
        self.assertEqual(git_info.nom_dossier_chemin_windows("C:\\CCW\\rummikub"), "rummikub")

    def test_barres_obliques_normales(self):
        self.assertEqual(git_info.nom_dossier_chemin_windows("C:/CCW/rummikub"), "rummikub")

    def test_barre_finale(self):
        self.assertEqual(git_info.nom_dossier_chemin_windows("C:\\CCW\\rummikub\\"), "rummikub")


class WorktreeEstPrincipalTestCase(unittest.TestCase):
    """`worktree_est_principal` : reconnaissance du worktree principal, projet
    distant (chemin Windows normalisé) vs projet local (comportement
    inchangé, `os.path.realpath`)."""

    def test_distant_barres_inverses_contre_normales(self):
        self.assertTrue(git_info.worktree_est_principal(
            "C:\\CCW\\rummikub", "C:/CCW/rummikub", True,
        ))

    def test_distant_casse_differente(self):
        self.assertTrue(git_info.worktree_est_principal(
            "C:\\CCW\\rummikub", "c:\\ccw\\RUMMIKUB", True,
        ))

    def test_distant_barre_finale(self):
        self.assertTrue(git_info.worktree_est_principal(
            "C:\\CCW\\rummikub", "C:\\CCW\\rummikub\\", True,
        ))

    def test_distant_autre_worktree_du_meme_clone(self):
        self.assertFalse(git_info.worktree_est_principal(
            "C:\\CCW\\rummikub", "C:\\CCW\\rummikub-worktrees\\feature-x", True,
        ))

    def test_local_inchange_meme_chemin(self):
        with tempfile.TemporaryDirectory(prefix="relecture_bridge_test_ccw_") as repertoire:
            self.assertTrue(git_info.worktree_est_principal(repertoire, repertoire, False))

    def test_local_inchange_barre_finale(self):
        # os.path.realpath normalisait déjà une barre finale avant cette
        # issue — comportement local inchangé, pas une régression.
        with tempfile.TemporaryDirectory(prefix="relecture_bridge_test_ccw_") as repertoire:
            self.assertTrue(git_info.worktree_est_principal(repertoire, repertoire + "/", False))

    def test_local_inchange_casse_distincte(self):
        # Contrairement au chemin Windows, un chemin POSIX reste sensible à
        # la casse (sur un filesystem Linux standard) : pas de normalisation
        # de casse ici, comportement local inchangé.
        with tempfile.TemporaryDirectory(prefix="relecture_bridge_test_ccw_") as repertoire:
            variante_majuscules = repertoire.upper()
            if variante_majuscules == repertoire:
                self.skipTest("chemin temporaire sans lettre minuscule, test non significatif")
            self.assertFalse(git_info.worktree_est_principal(repertoire, variante_majuscules, False))

    def test_local_inchange_chemin_different(self):
        with tempfile.TemporaryDirectory(prefix="relecture_bridge_test_ccw_") as a, \
             tempfile.TemporaryDirectory(prefix="relecture_bridge_test_ccw_") as b:
            self.assertFalse(git_info.worktree_est_principal(a, b, False))


class FusionChangelogProjetDistantTestCase(unittest.TestCase):
    """`fusionner_changelog_worktree` ne doit jamais tenter d'accès
    filesystem local sur un chemin Windows (issue #108) — `os.listdir`
    échouerait silencieusement sur un tel chemin depuis ce process Linux.

    Depuis l'issue #114, la détection passe par `detecter_changelogs_a_
    fusionner` (git, routé en SSH) plutôt que par le filesystem : sans
    `ccw_host` configuré (cas de ce test, pas de `ccw_host.conf` dans cet
    environnement), la détection échoue proprement (liste vide, voir
    `detecter_changelogs_a_fusionner`) et la fonction retombe sur son
    comportement « rien à signaler » (None), plutôt que sur un message
    d'erreur — le cas « détection positive côté distant » est couvert par
    `test_fusion_changelog_distant.py` (ssh/scp factices, dépôt jetable).

    `git_info.CHEMIN_CONFIG_CCW` redirigée vers un chemin inexistant (jamais
    le vrai `ccw_host.conf` du dépôt — même principe que
    test_ccw_host_conf.py) : sans cette redirection, un `ccw_host.conf` réel
    déjà configuré sur cette machine ferait tenter une vraie connexion SSH
    depuis ce test, ce qu'aucun test de ce dépôt ne doit jamais faire."""

    def setUp(self):
        self._config_original = git_info.CHEMIN_CONFIG_CCW
        git_info.CHEMIN_CONFIG_CCW = "/chemin/inexistant/ccw_host.conf"

    def tearDown(self):
        git_info.CHEMIN_CONFIG_CCW = self._config_original

    def test_aucun_acces_disque_local_sans_ccw_host_configure(self):
        resultat = git_info.fusionner_changelog_worktree("C:\\CCW\\rummikub", "rummikub_ccw")
        self.assertIsNone(resultat)

    def test_local_inchange_aucun_changelog(self):
        with tempfile.TemporaryDirectory(prefix="relecture_bridge_test_ccw_") as repertoire:
            # Dépôt local sans aucun CHANGELOG-<N>.md à la racine : toujours
            # None (rien à fusionner), comportement inchangé.
            self.assertIsNone(git_info.fusionner_changelog_worktree(repertoire, "projet_local"))


@unittest.skipUnless(shutil.which("bash"), "bash introuvable")
class InstallerShCheminsWindowsTestCase(unittest.TestCase):
    """`installer.sh` : message explicite pour une ligne à chemin Windows,
    distinct de « pas un dépôt git », sans jamais toucher un vrai dépôt —
    exécuté dans un dossier scratch avec un `curl` factice (aucun réseau),
    sur un tableau de projets entièrement fabriqué pour ce test."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_installer_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        installer_source = os.path.join(RACINE_DEPOT, "installer.sh")
        self.installer_copie = os.path.join(self.scratch, "installer.sh")
        shutil.copyfile(installer_source, self.installer_copie)
        os.chmod(self.installer_copie, 0o755)

        # post-commit factice — installer.sh exige seulement sa présence à
        # côté de lui, son contenu réel (hook Bridge_Agent) est hors sujet
        # pour ce test.
        with open(os.path.join(self.scratch, "post-commit"), "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\nexit 0\n")

        self.projet_git = os.path.join(self.scratch, "projet_git_reel")
        os.makedirs(self.projet_git)
        subprocess.run(["git", "init", "--quiet"], cwd=self.projet_git, check=True)

        self.projet_sans_git = os.path.join(self.scratch, "projet_sans_git")
        os.makedirs(self.projet_sans_git)

        self.chemin_windows = "C:\\CCW\\rummikub"

        doc_contenu = (
            "<!-- DEBUT:TABLEAU_PROJETS_ACTIFS -->\n"
            "| Nom | Dépôt | Répertoire de travail CCL |\n"
            "|---|---|---|\n"
            f"| rummikub_ccw | rummikub | {self.chemin_windows} |\n"
            f"| projet_git | projet_git | {self.projet_git} |\n"
            f"| projet_sans_git | projet_sans_git | {self.projet_sans_git} |\n"
            "<!-- FIN:TABLEAU_PROJETS_ACTIFS -->\n"
        )

        bin_factice = os.path.join(self.scratch, "bin_factice")
        os.makedirs(bin_factice)
        chemin_curl_factice = os.path.join(bin_factice, "curl")
        with open(chemin_curl_factice, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\ncat <<'DOC_FACTICE_EOF'\n" + doc_contenu + "DOC_FACTICE_EOF\n")
        st = os.stat(chemin_curl_factice)
        os.chmod(chemin_curl_factice, st.st_mode | stat.S_IEXEC)

        self.env = dict(os.environ)
        self.env["PATH"] = bin_factice + os.pathsep + self.env.get("PATH", "")

    def _lancer_installer(self):
        return subprocess.run(
            ["bash", self.installer_copie],
            cwd=self.scratch, env=self.env,
            capture_output=True, text=True, timeout=30,
        )

    def test_message_explicite_pour_chemin_windows(self):
        resultat = self._lancer_installer()
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        self.assertIn(f"Clone Windows distant (PC fixe CCW) — pas de hook installé par ce script : {self.chemin_windows}", resultat.stdout)
        # Jamais confondu avec un vrai dossier non-git.
        self.assertNotIn(f"pas un dépôt git) : {self.chemin_windows}", resultat.stdout)

    def test_message_inchange_pour_vrai_dossier_non_git(self):
        resultat = self._lancer_installer()
        self.assertIn(f"⚠ Ignoré (pas un dépôt git) : {self.projet_sans_git}", resultat.stdout)

    def test_hook_installe_sur_vrai_depot_local(self):
        resultat = self._lancer_installer()
        self.assertIn(f"✓ Hook installé sur {self.projet_git}", resultat.stdout)
        chemin_hook = os.path.join(self.projet_git, ".git", "hooks", "post-commit")
        self.assertTrue(os.path.isfile(chemin_hook))

    def test_aucun_hook_cree_pour_chemin_windows(self):
        # Rien ne doit avoir été créé sur disque pour la ligne Windows —
        # ce chemin n'existe pas localement, et ne doit jamais être traité
        # comme un dossier à créer ou inspecter.
        self._lancer_installer()
        self.assertFalse(os.path.exists(self.chemin_windows))


if __name__ == "__main__":
    unittest.main()
