#!/usr/bin/env python3
"""Tests du chargement à la demande des projets distants (PC fixe CCW,
issue #109, suite de #108) :

- `_charger_projets()` (page d'accueil, barre latérale, page d'un AUTRE
  projet, « Nettoyer tous les projets ») ne doit JAMAIS déclencher de test
  de connectivité SSH ni de commande git distante, quel que soit le nombre
  de projets distants dans le tableau ;
- seule la page d'un projet distant (ou une action qui le concerne) peut
  déclencher ce test de connectivité, via `_charger_projet_complet` /
  `git_info.charger_etat_projet` — jamais plus d'une fois par requête ;
- l'accueil et la barre latérale affichent les projets locaux puis les
  projets distants, séparés par un libellé visuel qui n'apparaît que s'il
  existe au moins un projet distant.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_chargement_a_la_demande_distant -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_chargement_a_la_demande_distant.py`.

Aucun accès réseau réel : `git_info.fetch_projets` (téléchargement de
BRIDGE_AGENT_DOC.md) est remplacée par un tableau fabriqué en mémoire,
`git_info.charger_config_ccw` (lecture de `ccw_host.conf`, jamais le vrai
fichier du disque, voir issue #110) par une config factice ou `None`, et
`git_info.tester_connectivite_ccw` (seul point d'entrée qui lance
réellement `ssh` vers le PC fixe) est remplacée par un faux compteur
d'appels qui ne lance jamais de processus — les projets locaux, eux, sont
de vrais petits dépôts git créés dans un dossier temporaire, pour exercer
le vrai code `_lancer_git` local sans rien simuler à ce niveau."""

import os
import subprocess
import sys
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module  # noqa: E402  (après l'ajustement de sys.path ci-dessus)
import git_info  # noqa: E402


def _init_depot_git_local(chemin):
    """Dépôt git local minimal (un commit) dans `chemin`, pour que
    `get_branche_courante`/`get_worktrees` renvoient de vraies valeurs sans
    rien simuler côté local — seul le PC fixe CCW (SSH) est simulé dans ces
    tests, pas git lui-même."""
    os.makedirs(chemin, exist_ok=True)
    subprocess.run(["git", "init", "--quiet"], cwd=chemin, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=chemin, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin, check=True)
    with open(os.path.join(chemin, "fichier.txt"), "w", encoding="utf-8") as f:
        f.write("contenu\n")
    subprocess.run(["git", "add", "fichier.txt"], cwd=chemin, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "initial"], cwd=chemin, check=True)


class BaseChargementADemandeTestCase(unittest.TestCase):
    """Tableau factice : deux projets locaux (dépôts git réels dans un
    dossier temporaire) et, sauf précision contraire, un projet distant
    (chemin Windows, jamais présent sur ce disque)."""

    AVEC_PROJET_DISTANT = True
    # `ccw_host.conf` "configuré" par défaut (host/clé factices, voir
    # `_faux_charger_config_ccw` ci-dessous) — une sous-classe représentant
    # l'état réel "non configuré" (issue #110, fichier absent ou vide, voir
    # ProjetDistantNonConfigureTestCase) doit positionner CCW_CONFIGURE à
    # False, auquel cas `tester_connectivite_ccw` n'est alors JAMAIS appelée
    # (même comportement que le vrai code : aucune connexion SSH tentée tant
    # que l'hôte n'est pas renseigné).
    CCW_CONFIGURE = True
    # PC fixe « éteint ou injoignable » par défaut (hôte configuré mais ne
    # répondant pas) — une sous-classe peut forcer True pour simuler un PC
    # fixe joignable (voir ProjetDistantJoignableTestCase), auquel cas elle
    # doit aussi fournir un faux `_lancer_git_distant` (jamais de vrai ssh
    # lancé dans ces tests). Sans effet si CCW_CONFIGURE est False.
    CONNECTIVITE_CCW = False

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_distant_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self.repertoire_local_a = os.path.join(self.scratch, "projet_local_a")
        self.repertoire_local_b = os.path.join(self.scratch, "projet_local_b")
        _init_depot_git_local(self.repertoire_local_a)
        _init_depot_git_local(self.repertoire_local_b)

        self.nom_distant = "rummikub_ccw"
        self.chemin_windows = "C:\\CCW\\rummikub"

        projets = [
            {
                "nom": "projet_local_a", "depot": "projet_local_a",
                "repertoire": self.repertoire_local_a, "couleur": None, "couleur_texte": None,
            },
            {
                "nom": "projet_local_b", "depot": "projet_local_b",
                "repertoire": self.repertoire_local_b, "couleur": None, "couleur_texte": None,
            },
        ]
        if self.AVEC_PROJET_DISTANT:
            projets.append({
                "nom": self.nom_distant, "depot": "rummikub",
                "repertoire": self.chemin_windows, "couleur": None, "couleur_texte": None,
            })

        self.compteur_ssh = {"n": 0}

        def _faux_fetch_projets():
            return projets

        def _faux_charger_config_ccw():
            # Jamais le vrai `ccw_host.conf` du disque (issue #110) : config
            # factice si CCW_CONFIGURE, None sinon (hôte non configuré).
            if not self.CCW_CONFIGURE:
                return None
            return {"host": "utilisateur@192.0.2.1", "cle": "/chemin/factice/cle"}

        def _faux_tester_connectivite_ccw():
            # Jamais de vrai `ssh` lancé dans ces tests — seul le COMPTAGE
            # des appels nous intéresse.
            self.compteur_ssh["n"] += 1
            return self.CONNECTIVITE_CCW

        self._original_fetch_projets = git_info.fetch_projets
        self._original_charger_config_ccw = git_info.charger_config_ccw
        self._original_tester_connectivite = git_info.tester_connectivite_ccw
        git_info.fetch_projets = _faux_fetch_projets
        git_info.charger_config_ccw = _faux_charger_config_ccw
        git_info.tester_connectivite_ccw = _faux_tester_connectivite_ccw
        self.addCleanup(self._restaurer_git_info)

        app_module.app.config["TESTING"] = True
        app_module.app.config["MDP_EXIGE"] = False
        self.client = app_module.app.test_client()

    def _restaurer_git_info(self):
        git_info.fetch_projets = self._original_fetch_projets
        git_info.charger_config_ccw = self._original_charger_config_ccw
        git_info.tester_connectivite_ccw = self._original_tester_connectivite


class AucunContactPcFixeTestCase(BaseChargementADemandeTestCase):
    """Zéro appel SSH pour toute page/action qui ne concerne pas
    spécifiquement le projet distant — même quand un projet distant existe
    dans le tableau (issue #109, partie A1/A2/A4/A5)."""

    def test_accueil_zero_appel_ssh(self):
        reponse = self.client.get("/")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(self.compteur_ssh["n"], 0)

    def test_barre_laterale_zero_appel_ssh(self):
        # La barre latérale est injectée sur TOUTE page (context_processor) ;
        # une page de projet local suffit à l'exercer en même temps que la
        # page elle-même.
        reponse = self.client.get(f"/projet/projet_local_a")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(self.compteur_ssh["n"], 0)

    def test_page_projet_local_zero_appel_ssh(self):
        reponse = self.client.get("/projet/projet_local_b")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(self.compteur_ssh["n"], 0)

    def test_action_sur_projet_local_zero_appel_ssh(self):
        reponse = self.client.post("/projet/projet_local_a/nettoyer")
        self.assertIn(reponse.status_code, (200, 302))
        self.assertEqual(self.compteur_ssh["n"], 0)

    def test_nettoyer_tous_les_projets_zero_appel_ssh(self):
        reponse = self.client.post("/nettoyer-tous-les-projets")
        self.assertIn(reponse.status_code, (200, 302))
        self.assertEqual(self.compteur_ssh["n"], 0)


class ChargementProjetDistantTestCase(BaseChargementADemandeTestCase):
    """La page du projet distant lui-même déclenche bien le chargement
    complet (au moins un test de connectivité SSH), et jamais plus d'une
    fois par requête (issue #109, partie A2)."""

    def test_page_projet_distant_au_moins_un_appel_ssh(self):
        reponse = self.client.get(f"/projet/{self.nom_distant}")
        self.assertEqual(reponse.status_code, 200)
        self.assertGreaterEqual(self.compteur_ssh["n"], 1)

    def test_page_projet_distant_un_seul_appel_ssh_par_requete(self):
        reponse = self.client.get(f"/projet/{self.nom_distant}")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(self.compteur_ssh["n"], 1)

    def test_page_projet_distant_statut_injoignable_affiche(self):
        reponse = self.client.get(f"/projet/{self.nom_distant}")
        self.assertIn("injoignable", reponse.get_data(as_text=True))


class ProjetDistantJoignableTestCase(BaseChargementADemandeTestCase):
    """Même PC fixe « joignable » (statut "ok", pas seulement "injoignable")
    — simulé par un faux `_lancer_git_distant` qui ne lance jamais de vrai
    `ssh` (issue #109, partie A4 : bouton « Nettoyer ce projet » refusé
    pour un projet distant même quand il est parfaitement accessible)."""

    CONNECTIVITE_CCW = True

    def setUp(self):
        super().setUp()
        self.compteur_git_distant = {"n": 0}

        def _faux_lancer_git_distant(repertoire, args, timeout, entree):
            self.compteur_git_distant["n"] += 1
            return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        self._original_lancer_git_distant = git_info._lancer_git_distant
        git_info._lancer_git_distant = _faux_lancer_git_distant
        self.addCleanup(self._restaurer_lancer_git_distant)

    def _restaurer_lancer_git_distant(self):
        git_info._lancer_git_distant = self._original_lancer_git_distant

    def test_page_projet_distant_statut_ok(self):
        reponse = self.client.get(f"/projet/{self.nom_distant}")
        self.assertEqual(reponse.status_code, 200)
        self.assertNotIn("injoignable", reponse.get_data(as_text=True))

    def test_bouton_nettoyer_ce_projet_absent_pour_projet_distant(self):
        texte = self.client.get(f"/projet/{self.nom_distant}").get_data(as_text=True)
        self.assertNotIn("form-nettoyer-ce-projet", texte)

    def test_nettoyer_ce_projet_refuse_pour_projet_distant(self):
        reponse = self.client.post(f"/projet/{self.nom_distant}/nettoyer", follow_redirects=True)
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("projet distant", reponse.get_data(as_text=True))


class ProjetDistantNonConfigureTestCase(BaseChargementADemandeTestCase):
    """`ccw_host.conf` absent ou vide (issue #110 — installation neuve, ou
    après la suppression du fichier réel désormais hors git) : statut dédié
    "ccw_non_configure", zéro appel SSH (jamais tenté, contrairement à
    "injoignable"), message explicite invitant à copier
    `ccw_host.conf.example` plutôt que le message générique "éteint ou
    injoignable"."""

    CCW_CONFIGURE = False

    def test_page_projet_distant_zero_appel_ssh(self):
        reponse = self.client.get(f"/projet/{self.nom_distant}")
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(self.compteur_ssh["n"], 0)

    def test_page_projet_distant_message_explicite_affiche(self):
        texte = self.client.get(f"/projet/{self.nom_distant}").get_data(as_text=True)
        self.assertIn("ccw_host.conf.example", texte)
        self.assertNotIn("injoignable", texte)

    def test_action_sur_projet_distant_non_configure_message_explicite(self):
        reponse = self.client.post(f"/projet/{self.nom_distant}/nettoyer", follow_redirects=True)
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("ccw_host.conf.example", reponse.get_data(as_text=True))


class AffichageAccueilSansProjetDistantTestCase(BaseChargementADemandeTestCase):
    """Comportement inchangé (pas de séparateur) quand aucun projet distant
    n'existe dans le tableau (issue #109, partie B1)."""

    AVEC_PROJET_DISTANT = False

    def test_accueil_sans_separateur(self):
        reponse = self.client.get("/")
        self.assertNotIn("PC fixe (Windows)", reponse.get_data(as_text=True))

    def test_accueil_zero_appel_ssh_sans_projet_distant(self):
        self.client.get("/")
        self.assertEqual(self.compteur_ssh["n"], 0)


class AffichageAccueilAvecProjetDistantTestCase(BaseChargementADemandeTestCase):
    """Ordre « projets locaux puis projets distants » et séparateur visuel
    (issue #109, partie B1), à l'accueil comme dans la barre latérale."""

    def test_accueil_separateur_present(self):
        reponse = self.client.get("/")
        self.assertIn("PC fixe (Windows)", reponse.get_data(as_text=True))

    def test_accueil_ordre_locaux_puis_distants(self):
        texte = self.client.get("/").get_data(as_text=True)
        position_a = texte.index("projet_local_a")
        position_b = texte.index("projet_local_b")
        position_distant = texte.index(self.nom_distant)
        position_separateur = texte.index("PC fixe (Windows)")
        self.assertLess(max(position_a, position_b), position_separateur)
        self.assertLess(position_separateur, position_distant)

    def test_accueil_pas_de_decompte_resumes_pour_projet_distant(self):
        texte = self.client.get("/").get_data(as_text=True)
        # Dans la LISTE DE PROJETS de l'accueil (pas la barre latérale, qui
        # mentionne aussi le nom du projet distant mais sans décompte).
        liste_projets = texte[texte.index('<ul class="liste-projets">'):]
        bloc_distant = liste_projets[liste_projets.index(self.nom_distant):]
        self.assertNotIn("(0)", bloc_distant.split("</li>")[0])
        self.assertIn("chargé à l'ouverture", bloc_distant.split("</li>")[0])

    def test_barre_laterale_separateur_present(self):
        texte = self.client.get("/projet/projet_local_a").get_data(as_text=True)
        self.assertIn("PC fixe (Windows)", texte)

    def test_page_projet_distant_indication_pc_fixe(self):
        texte = self.client.get(f"/projet/{self.nom_distant}").get_data(as_text=True)
        self.assertIn("PC fixe", texte)
        self.assertIn("SSH", texte)
        self.assertIn(self.chemin_windows, texte)


if __name__ == "__main__":
    unittest.main()
