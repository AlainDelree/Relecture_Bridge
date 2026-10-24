#!/usr/bin/env python3
"""Tests de `ccw_host.conf` non suivi par git + modèle `ccw_host.conf.example`
suivi, lui (issue #110, suite de #94/#109) :

- `git_info.charger_config_ccw()` : fichier absent (installation neuve, ou
  après la suppression du fichier réel désormais hors git) -> `None`, sans
  exception ni plantage ("hôte non configuré") ;
- fichier présent avec `ccw_host` renseigné -> config chargée normalement ;
- le modèle `ccw_host.conf.example` ne contient que des commentaires (la
  ligne `ccw_host` y est commentée) : lu comme fichier de config, il doit
  donner le même résultat que "non configuré", jamais une configuration
  valide ;
- le `.gitignore` de `relecture_web/` ignore bien le fichier réel
  `ccw_host.conf` et pas le modèle `ccw_host.conf.example`, vérifié via
  `git check-ignore` dans un dépôt jetable (scratch), jamais dans le vrai
  dépôt de travail.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_ccw_host_conf -v` depuis la racine
du dépôt, ou directement `python3 relecture_web/test_ccw_host_conf.py`.

Aucun accès réseau réel, et aucune écriture dans le vrai dépôt de travail :
`git_info.CHEMIN_CONFIG_CCW` est redirigée vers un dossier temporaire pour
les tests de `charger_config_ccw`, et le test du `.gitignore` crée son
propre dépôt git jetable dans un dossier temporaire plutôt que d'inspecter
celui où tourne ce test."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import git_info  # noqa: E402  (après l'ajustement de sys.path ci-dessus)

RACINE_DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_EXEMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ccw_host.conf.example")


class ChargerConfigCcwTestCase(unittest.TestCase):
    """`git_info.charger_config_ccw()`, `CHEMIN_CONFIG_CCW` redirigée vers un
    dossier temporaire — jamais le vrai `ccw_host.conf` du dépôt de
    travail."""

    def setUp(self):
        self.dossier = tempfile.mkdtemp(prefix="relecture_bridge_test_ccw_conf_")
        self.addCleanup(shutil.rmtree, self.dossier, ignore_errors=True)
        self.chemin_config = os.path.join(self.dossier, "ccw_host.conf")

        self._chemin_original = git_info.CHEMIN_CONFIG_CCW
        git_info.CHEMIN_CONFIG_CCW = self.chemin_config
        self.addCleanup(self._restaurer_chemin)

    def _restaurer_chemin(self):
        git_info.CHEMIN_CONFIG_CCW = self._chemin_original

    def _ecrire_config(self, contenu):
        with open(self.chemin_config, "w", encoding="utf-8") as f:
            f.write(contenu)

    def test_fichier_absent_hote_non_configure(self):
        self.assertFalse(os.path.exists(self.chemin_config))
        self.assertIsNone(git_info.charger_config_ccw())

    def test_fichier_absent_pas_de_plantage_tester_connectivite(self):
        # `tester_connectivite_ccw` ne doit jamais tenter de connexion SSH
        # (donc jamais lever/bloquer) quand l'hôte n'est pas configuré.
        self.assertFalse(git_info.tester_connectivite_ccw())

    def test_fichier_present_ccw_host_renseigne(self):
        self._ecrire_config("ccw_host = utilisateur@192.0.2.1\n")
        config = git_info.charger_config_ccw()
        self.assertIsNotNone(config)
        self.assertEqual(config["host"], "utilisateur@192.0.2.1")
        self.assertEqual(config["cle"], git_info.CLE_SSH_CCW_DEFAUT)

    def test_fichier_present_ccw_host_et_ccw_key_renseignes(self):
        self._ecrire_config(
            "ccw_host = utilisateur@192.0.2.1\n"
            "ccw_key = ~/.ssh/une_cle\n"
        )
        config = git_info.charger_config_ccw()
        self.assertEqual(config["host"], "utilisateur@192.0.2.1")
        self.assertEqual(config["cle"], os.path.expanduser("~/.ssh/une_cle"))

    def test_fichier_present_mais_vide_hote_non_configure(self):
        self._ecrire_config("")
        self.assertIsNone(git_info.charger_config_ccw())

    def test_modele_contenu_jamais_une_config_valide(self):
        # Le modèle réel (ccw_host.conf.example, suivi par git) ne doit
        # contenir QUE des lignes de commentaire — y compris la ligne
        # ccw_host elle-même — donc être lu exactement comme "non
        # configuré" s'il était par erreur chargé comme fichier de config.
        with open(CHEMIN_EXEMPLE, encoding="utf-8") as f:
            contenu_modele = f.read()
        self._ecrire_config(contenu_modele)
        self.assertIsNone(git_info.charger_config_ccw())


class GitignoreCcwHostTestCase(unittest.TestCase):
    """`.gitignore` de `relecture_web/` : ignore le fichier réel
    `ccw_host.conf`, pas le modèle `ccw_host.conf.example` — vérifié avec
    `git check-ignore` dans un dépôt git jetable (scratch), jamais dans le
    vrai dépôt de travail de ce test."""

    def setUp(self):
        self.depot = tempfile.mkdtemp(prefix="relecture_bridge_test_ccw_gitignore_")
        self.addCleanup(shutil.rmtree, self.depot, ignore_errors=True)
        subprocess.run(["git", "init", "--quiet"], cwd=self.depot, check=True)
        shutil.copy(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".gitignore"),
            os.path.join(self.depot, ".gitignore"),
        )

    def _est_ignore(self, nom_fichier):
        resultat = subprocess.run(
            ["git", "check-ignore", nom_fichier],
            cwd=self.depot, capture_output=True, text=True,
        )
        return resultat.returncode == 0

    def test_fichier_reel_ignore(self):
        self.assertTrue(self._est_ignore("ccw_host.conf"))

    def test_modele_non_ignore(self):
        self.assertFalse(self._est_ignore("ccw_host.conf.example"))


if __name__ == "__main__":
    unittest.main()
