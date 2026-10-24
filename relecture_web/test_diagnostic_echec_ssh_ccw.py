#!/usr/bin/env python3
"""Tests du diagnostic fin des échecs de connexion SSH vers le PC fixe CCW
(issue #111, suite de #110) :

- `_classer_echec_ssh_ccw`/`_message_echec_ssh_ccw` : les cinq catégories
  (clé d'hôte modifiée, clé refusée, connexion refusée, PC éteint ou
  adresse introuvable, cause non reconnue), avec le libellé repris à
  l'identique dans le message et l'adresse réelle (jamais écrite en dur)
  pour la commande `ssh-keygen -R` ;
- `tester_connectivite_ccw()` de bout en bout avec un FAUX `ssh` (script
  shell posé devant le vrai sur le PATH, jamais de réseau ni de vrai ssh) :
  mêmes catégories, plus le cas de succès, plus le cas où le propre délai
  du test est dépassé ;
- `charger_etat_projet` : le statut "injoignable" porte désormais
  `ccw_categorie`/`ccw_message`, un projet local ou un PC fixe joignable
  n'est pas affecté.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_diagnostic_echec_ssh_ccw -v` depuis
la racine du dépôt, ou directement
`python3 relecture_web/test_diagnostic_echec_ssh_ccw.py`."""

import os
import shutil
import stat
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import git_info  # noqa: E402  (après l'ajustement de sys.path ci-dessus)


class ClasserEchecSshCcwTestCase(unittest.TestCase):
    """`_classer_echec_ssh_ccw`/`_message_echec_ssh_ccw` directement, sans
    passer par un vrai (ou faux) processus `ssh` — les textes d'erreur
    ci-dessous sont ceux réellement produits par OpenSSH (en anglais,
    toujours, voir le contexte de l'issue)."""

    def setUp(self):
        self.config_a = {"host": "alain@192.0.2.5", "cle": "/chemin/factice/cle"}
        self.config_b = {"host": "alain@203.0.113.9", "cle": "/chemin/factice/cle"}

    def test_cle_hote_modifiee(self):
        texte = (
            "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            "@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @\n"
            "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            "Host key verification failed.\n"
        )
        categorie = git_info._classer_echec_ssh_ccw(texte)
        self.assertEqual(categorie, git_info.CCW_CLE_HOTE_MODIFIEE)
        message = git_info._message_echec_ssh_ccw(categorie, self.config_a, texte)
        self.assertIn(git_info.CCW_LIBELLES[categorie], message)
        self.assertIn("ssh-keygen -R 192.0.2.5", message)

    def test_cle_hote_modifiee_adresse_jamais_en_dur(self):
        # Deux configurations différentes -> deux commandes différentes :
        # preuve que l'adresse vient de `config`, pas d'une valeur fixe.
        texte = "Host key verification failed.\n"
        categorie = git_info._classer_echec_ssh_ccw(texte)
        message_a = git_info._message_echec_ssh_ccw(categorie, self.config_a, texte)
        message_b = git_info._message_echec_ssh_ccw(categorie, self.config_b, texte)
        self.assertIn("ssh-keygen -R 192.0.2.5", message_a)
        self.assertIn("ssh-keygen -R 203.0.113.9", message_b)
        self.assertNotIn("203.0.113.9", message_a)
        self.assertNotIn("192.0.2.5", message_b)

    def test_cle_refusee(self):
        texte = "alain@192.0.2.5: Permission denied (publickey).\n"
        categorie = git_info._classer_echec_ssh_ccw(texte)
        self.assertEqual(categorie, git_info.CCW_CLE_REFUSEE)
        message = git_info._message_echec_ssh_ccw(categorie, self.config_a, texte)
        self.assertIn(git_info.CCW_LIBELLES[categorie], message)
        self.assertIn("Bridge_Agent", message)

    def test_connexion_refusee(self):
        texte = "ssh: connect to host 192.0.2.5 port 22: Connection refused\n"
        categorie = git_info._classer_echec_ssh_ccw(texte)
        self.assertEqual(categorie, git_info.CCW_CONNEXION_REFUSEE)
        message = git_info._message_echec_ssh_ccw(categorie, self.config_a, texte)
        self.assertIn(git_info.CCW_LIBELLES[categorie], message)

    def test_hote_inaccessible_delai_depasse(self):
        texte = "ssh: connect to host 192.0.2.5 port 22: Connection timed out\n"
        categorie = git_info._classer_echec_ssh_ccw(texte)
        self.assertEqual(categorie, git_info.CCW_HOTE_INACCESSIBLE)
        message = git_info._message_echec_ssh_ccw(categorie, self.config_a, texte)
        self.assertIn(git_info.CCW_LIBELLES[categorie], message)

    def test_hote_inaccessible_pas_de_route(self):
        texte = "ssh: connect to host 192.0.2.5 port 22: No route to host\n"
        self.assertEqual(git_info._classer_echec_ssh_ccw(texte), git_info.CCW_HOTE_INACCESSIBLE)

    def test_hote_inaccessible_reseau_inaccessible(self):
        texte = "ssh: connect to host 192.0.2.5 port 22: Network is unreachable\n"
        self.assertEqual(git_info._classer_echec_ssh_ccw(texte), git_info.CCW_HOTE_INACCESSIBLE)

    def test_hote_inaccessible_nom_non_resolu(self):
        texte = "ssh: Could not resolve hostname pc-fixe-inexistant: Name or service not known\n"
        self.assertEqual(git_info._classer_echec_ssh_ccw(texte), git_info.CCW_HOTE_INACCESSIBLE)

    def test_cause_inconnue_texte_imprevu(self):
        texte = "ssh: un message jamais vu dans aucune catégorie connue\nligne suivante\n"
        categorie = git_info._classer_echec_ssh_ccw(texte)
        self.assertEqual(categorie, git_info.CCW_CAUSE_INCONNUE)
        message = git_info._message_echec_ssh_ccw(categorie, self.config_a, texte)
        self.assertIn(git_info.CCW_LIBELLES[categorie], message)
        # Première ligne seulement, pas la suite.
        self.assertIn("ssh: un message jamais vu dans aucune catégorie connue", message)
        self.assertNotIn("ligne suivante", message)


class TesterConnectiviteCcwFauxSshTestCase(unittest.TestCase):
    """`tester_connectivite_ccw()` de bout en bout, avec un FAUX `ssh`
    (script shell dans un dossier placé en tête du PATH) — jamais de vrai
    réseau ni de vrai `ssh`. Le faux script lit deux variables
    d'environnement (`FAUX_SSH_CODE`, `FAUX_SSH_STDERR`) pour décider de
    son comportement, pilotées depuis chaque test."""

    def setUp(self):
        self.dossier = tempfile.mkdtemp(prefix="relecture_bridge_test_faux_ssh_")
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)

        chemin_script = os.path.join(self.dossier, "ssh")
        with open(chemin_script, "w", encoding="utf-8") as f:
            f.write(
                "#!/bin/sh\n"
                'if [ -n "$FAUX_SSH_STDERR" ]; then\n'
                '  printf "%s" "$FAUX_SSH_STDERR" >&2\n'
                "fi\n"
                'exit "${FAUX_SSH_CODE:-0}"\n'
            )
        os.chmod(chemin_script, os.stat(chemin_script).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        self._path_original = os.environ.get("PATH", "")
        os.environ["PATH"] = self.dossier + os.pathsep + self._path_original
        self.addCleanup(self._restaurer_environnement)

        self._config_original = git_info.charger_config_ccw
        git_info.charger_config_ccw = lambda: {"host": "alain@192.0.2.5", "cle": "/chemin/factice/cle"}
        self.addCleanup(self._restaurer_config)

    def _restaurer_environnement(self):
        os.environ["PATH"] = self._path_original
        for cle in ("FAUX_SSH_CODE", "FAUX_SSH_STDERR"):
            os.environ.pop(cle, None)

    def _restaurer_config(self):
        git_info.charger_config_ccw = self._config_original

    def _simuler(self, code, stderr=""):
        os.environ["FAUX_SSH_CODE"] = str(code)
        if stderr:
            os.environ["FAUX_SSH_STDERR"] = stderr
        else:
            os.environ.pop("FAUX_SSH_STDERR", None)

    def test_succes(self):
        self._simuler(0)
        ok, categorie, message = git_info.tester_connectivite_ccw()
        self.assertTrue(ok)
        self.assertIsNone(categorie)
        self.assertIsNone(message)

    def test_cle_hote_modifiee(self):
        self._simuler(255, "Host key verification failed.\n")
        ok, categorie, message = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_CLE_HOTE_MODIFIEE)
        self.assertIn("ssh-keygen -R 192.0.2.5", message)

    def test_cle_refusee(self):
        self._simuler(255, "alain@192.0.2.5: Permission denied (publickey).\n")
        ok, categorie, message = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_CLE_REFUSEE)
        self.assertIn(git_info.CCW_LIBELLES[categorie], message)

    def test_connexion_refusee(self):
        self._simuler(255, "ssh: connect to host 192.0.2.5 port 22: Connection refused\n")
        ok, categorie, message = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_CONNEXION_REFUSEE)

    def test_delai_depasse(self):
        self._simuler(255, "ssh: connect to host 192.0.2.5 port 22: Connection timed out\n")
        ok, categorie, message = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_HOTE_INACCESSIBLE)

    def test_pas_de_route(self):
        self._simuler(255, "ssh: connect to host 192.0.2.5 port 22: No route to host\n")
        ok, categorie, _ = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_HOTE_INACCESSIBLE)

    def test_reseau_inaccessible(self):
        self._simuler(255, "ssh: connect to host 192.0.2.5 port 22: Network is unreachable\n")
        ok, categorie, _ = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_HOTE_INACCESSIBLE)

    def test_nom_non_resolu(self):
        self._simuler(255, "ssh: Could not resolve hostname pc-fixe: Name or service not known\n")
        ok, categorie, _ = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_HOTE_INACCESSIBLE)

    def test_cause_imprevue(self):
        self._simuler(255, "quelque chose de jamais vu\n")
        ok, categorie, message = git_info.tester_connectivite_ccw()
        self.assertFalse(ok)
        self.assertEqual(categorie, git_info.CCW_CAUSE_INCONNUE)
        self.assertIn("quelque chose de jamais vu", message)

    def test_adresse_jamais_en_dur_deuxieme_hote(self):
        # Même scénario (clé d'hôte modifiée) mais avec un AUTRE hôte
        # configuré -> la commande affichée doit suivre, preuve que
        # l'adresse n'est pas écrite en dur dans le code.
        git_info.charger_config_ccw = lambda: {"host": "alain@203.0.113.9", "cle": "/chemin/factice/cle"}
        self._simuler(255, "Host key verification failed.\n")
        _, _, message = git_info.tester_connectivite_ccw()
        self.assertIn("ssh-keygen -R 203.0.113.9", message)
        self.assertNotIn("192.0.2.5", message)


class ChargerEtatProjetDiagnosticTestCase(unittest.TestCase):
    """`charger_etat_projet` propage `ccw_categorie`/`ccw_message` pour un
    projet distant injoignable, et laisse un projet local ou un PC fixe
    joignable inchangés (issue #111)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_charger_etat_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self._config_original = git_info.charger_config_ccw
        self._tester_original = git_info.tester_connectivite_ccw
        self.addCleanup(self._restaurer)

    def _restaurer(self):
        git_info.charger_config_ccw = self._config_original
        git_info.tester_connectivite_ccw = self._tester_original

    def test_projet_distant_injoignable_porte_categorie_et_message(self):
        git_info.charger_config_ccw = lambda: {"host": "alain@192.0.2.5", "cle": "/chemin/factice/cle"}
        git_info.tester_connectivite_ccw = lambda: (
            False, git_info.CCW_CONNEXION_REFUSEE, "message factice de test",
        )
        projet = {
            "nom": "rummikub_ccw", "depot": "rummikub",
            "repertoire": "C:\\CCW\\rummikub", "couleur": None, "couleur_texte": None,
        }
        entree = git_info.charger_etat_projet(projet)
        self.assertEqual(entree["statut"], "injoignable")
        self.assertEqual(entree["ccw_categorie"], git_info.CCW_CONNEXION_REFUSEE)
        self.assertEqual(entree["ccw_message"], "message factice de test")

    def test_projet_distant_joignable_sans_champs_ccw(self):
        import subprocess

        git_info.charger_config_ccw = lambda: {"host": "alain@192.0.2.5", "cle": "/chemin/factice/cle"}
        git_info.tester_connectivite_ccw = lambda: (True, None, None)
        original_lancer_git_distant = git_info._lancer_git_distant
        git_info._lancer_git_distant = lambda repertoire, args, timeout, entree: subprocess.CompletedProcess(
            args=[], returncode=0, stdout="main\n", stderr="",
        )
        try:
            projet = {
                "nom": "rummikub_ccw", "depot": "rummikub",
                "repertoire": "C:\\CCW\\rummikub", "couleur": None, "couleur_texte": None,
            }
            entree = git_info.charger_etat_projet(projet)
        finally:
            git_info._lancer_git_distant = original_lancer_git_distant
        self.assertNotEqual(entree["statut"], "injoignable")
        self.assertNotIn("ccw_categorie", entree)
        self.assertNotIn("ccw_message", entree)

    def test_projet_local_non_affecte(self):
        chemin = os.path.join(self.scratch, "projet_local")
        os.makedirs(chemin)
        import subprocess
        subprocess.run(["git", "init", "--quiet"], cwd=chemin, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=chemin, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin, check=True)
        with open(os.path.join(chemin, "f.txt"), "w", encoding="utf-8") as f:
            f.write("x\n")
        subprocess.run(["git", "add", "f.txt"], cwd=chemin, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "initial"], cwd=chemin, check=True)

        projet = {
            "nom": "projet_local", "depot": "projet_local",
            "repertoire": chemin, "couleur": None, "couleur_texte": None,
        }
        entree = git_info.charger_etat_projet(projet)
        self.assertEqual(entree["statut"], "ok")
        self.assertNotIn("ccw_categorie", entree)
        self.assertNotIn("ccw_message", entree)


if __name__ == "__main__":
    unittest.main()
