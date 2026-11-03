#!/usr/bin/env python3
"""Tests de l'issue #123 : affichage global du résultat d'un push en
arrière-plan (issue #122, déjà testée dans `test_push_arriere_plan.py`,
jamais modifiée ici) sur toutes les pages — route de sondage, barre
latérale (pastille animée / panneau « Attention Refus » / panneau « À
vérifier »), acquittement AJAX global, et absence d'affichage quand aucun
push n'est suivi.

Ne couvre pas le JS de `base.html` (fenêtre de résultat globale, préfixe du
titre de l'onglet, sondage périodique) : aucun framework de test navigateur
dans ce dépôt (voir #107) — seuls le rendu serveur (route + template) et
l'état exposé par `push_arriere_plan.etats_a_signaler` sont vérifiés ici.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), même harnais que
`test_push_arriere_plan.py` — état du push redirigé vers un fichier
temporaire, jamais le vrai `push_arriere_plan_etat.json`, aucune lecture ni
écriture des vrais fichiers locaux de relecture_web."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module  # noqa: E402  (après l'ajustement de sys.path ci-dessus)
import git_info  # noqa: E402
import push_arriere_plan  # noqa: E402


def _init_depot(chemin_local):
    os.makedirs(chemin_local, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "-b", "main", chemin_local], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=chemin_local, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin_local, check=True)
    subprocess.run(["git", "commit", "--quiet", "--allow-empty", "-m", "initial"], cwd=chemin_local, check=True)


class BaseAffichageGlobalTestCase(unittest.TestCase):
    """Harnais Flask commun : deux projets locaux jetables (sans crochet
    pre-push, leur comportement de push réel n'est pas sous test ici — seul
    l'affichage dérivé de l'état persistant l'est), état du push redirigé
    vers un fichier temporaire."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_affichage_push_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self._chemin_etat_original = push_arriere_plan.CHEMIN_ETAT_PUSH
        push_arriere_plan.CHEMIN_ETAT_PUSH = os.path.join(self.scratch, "push_etat.json")
        self.addCleanup(self._restaurer_chemin_etat)

        self.repertoire_a = os.path.join(self.scratch, "projet_a")
        self.repertoire_b = os.path.join(self.scratch, "projet_b")
        _init_depot(self.repertoire_a)
        _init_depot(self.repertoire_b)

        self.projets = [
            {"nom": "projet_a", "depot": "projet_a", "repertoire": self.repertoire_a, "couleur": None, "couleur_texte": None},
            {"nom": "projet_b", "depot": "projet_b", "repertoire": self.repertoire_b, "couleur": None, "couleur_texte": None},
        ]
        self._fetch_original = git_info.fetch_projets
        git_info.fetch_projets = lambda: self.projets
        self.addCleanup(self._restaurer_fetch)

        app_module.app.config["TESTING"] = True
        app_module.app.config["MDP_EXIGE"] = False
        self.client = app_module.app.test_client()

    def _restaurer_chemin_etat(self):
        push_arriere_plan.CHEMIN_ETAT_PUSH = self._chemin_etat_original

    def _restaurer_fetch(self):
        git_info.fetch_projets = self._fetch_original

    def _barre_laterale(self, chemin="/"):
        """Isole le `<nav class="barre-laterale">` de la page : le script
        inline de `base.html` mentionne les mêmes noms de classe en toutes
        lettres (JS qui les manipule), donc un `assertIn`/`assertNotIn` sur
        la page entière serait toujours vrai, qu'un panneau soit rendu ou
        non — seul le balisage réellement rendu par le template doit être
        inspecté ici."""
        page = self.client.get(chemin).get_data(as_text=True)
        debut = page.index('<nav class="barre-laterale">')
        fin = page.index("</nav>", debut)
        return page[debut:fin]

    def _ecrire_entree(self, nom_projet, **champs):
        base = {
            "etat": "en_cours", "branches": ["main"], "repertoire": self.repertoire_a,
            "debut": "2026-11-03T10:00:00", "fin": None, "sortie": "", "vu": False,
            "pid": None, "resultats": {},
        }
        base.update(champs)
        push_arriere_plan.ecrire_entree(nom_projet, **base)


class RouteEtatPushTestCase(BaseAffichageGlobalTestCase):
    """`GET /push/etat` (issue #123, point 1) : ne renvoie que les projets
    dont le push est en cours ou dont le résultat n'a pas été acquitté."""

    def test_rien_quand_aucun_push_suivi(self):
        reponse = self.client.get("/push/etat")
        self.assertEqual(reponse.get_json(), {"projets": {}})

    def test_projet_en_cours_present(self):
        self._ecrire_entree("projet_a", etat="en_cours", vu=False)
        donnees = self.client.get("/push/etat").get_json()
        self.assertIn("projet_a", donnees["projets"])
        self.assertEqual(donnees["projets"]["projet_a"]["etat"], "en_cours")

    def test_refus_non_acquitte_present(self):
        self._ecrire_entree("projet_a", etat="refuse", fin="2026-11-03T10:05:00", sortie="ÉCHEC", vu=False)
        donnees = self.client.get("/push/etat").get_json()
        self.assertIn("projet_a", donnees["projets"])
        self.assertEqual(donnees["projets"]["projet_a"]["etat"], "refuse")
        self.assertEqual(donnees["projets"]["projet_a"]["sortie"], "ÉCHEC")

    def test_refus_acquitte_absent(self):
        self._ecrire_entree("projet_a", etat="refuse", fin="2026-11-03T10:05:00", sortie="ÉCHEC", vu=True)
        donnees = self.client.get("/push/etat").get_json()
        self.assertNotIn("projet_a", donnees["projets"])

    def test_push_abouti_deja_acquitte_absent(self):
        self._ecrire_entree("projet_a", etat="pousse", fin="2026-11-03T10:05:00", vu=True)
        donnees = self.client.get("/push/etat").get_json()
        self.assertNotIn("projet_a", donnees["projets"])

    def test_pid_et_repertoire_jamais_exposes(self):
        self._ecrire_entree("projet_a", etat="en_cours", pid=12345)
        donnees = self.client.get("/push/etat").get_json()
        entree = donnees["projets"]["projet_a"]
        self.assertNotIn("pid", entree)
        self.assertNotIn("repertoire", entree)

    def test_deux_projets_independants(self):
        self._ecrire_entree("projet_a", etat="en_cours")
        self._ecrire_entree("projet_b", etat="refuse", fin="2026-11-03T10:05:00", vu=False)
        donnees = self.client.get("/push/etat").get_json()
        self.assertEqual(set(donnees["projets"].keys()), {"projet_a", "projet_b"})


class BarreLateraleTestCase(BaseAffichageGlobalTestCase):
    """Contenu rendu de la barre latérale (`base.html`) pour chaque état —
    premier rendu serveur, avant tout sondage JS."""

    def test_aucun_affichage_sans_push_suivi(self):
        barre = self._barre_laterale()
        self.assertNotIn("indicateur-push-en-cours", barre)
        self.assertNotIn("panneau-sidebar-push", barre)

    def test_pastille_animee_pendant_le_push(self):
        self._ecrire_entree("projet_a", etat="en_cours")
        barre = self._barre_laterale()
        self.assertIn('class="indicateur-push-en-cours"', barre)
        self.assertNotIn("panneau-sidebar-push", barre)

    def test_panneau_attention_refus_tant_que_non_acquitte(self):
        self._ecrire_entree("projet_a", etat="refuse", fin="2026-11-03T10:05:00", vu=False)
        barre = self._barre_laterale()
        self.assertIn("panneau-sidebar-push--refus", barre)
        self.assertIn("ATTENTION", barre)
        self.assertIn("REFUS", barre)
        self.assertNotIn("indicateur-push-en-cours", barre)

    def test_panneau_a_verifier_pour_interrompu(self):
        self._ecrire_entree("projet_a", etat="interrompu", fin="2026-11-03T10:05:00", vu=False)
        barre = self._barre_laterale()
        self.assertIn("panneau-sidebar-push--verifier", barre)
        self.assertIn("À VÉRIFIER", barre)

    def test_panneau_a_verifier_pour_indetermine(self):
        self._ecrire_entree("projet_a", etat="indetermine", fin="2026-11-03T10:05:00", vu=False)
        barre = self._barre_laterale()
        self.assertIn("panneau-sidebar-push--verifier", barre)

    def test_entree_redevient_normale_une_fois_acquittee(self):
        self._ecrire_entree("projet_a", etat="refuse", fin="2026-11-03T10:05:00", vu=True)
        barre = self._barre_laterale()
        self.assertNotIn("panneau-sidebar-push", barre)
        self.assertNotIn("indicateur-push-en-cours", barre)

    def test_push_abouti_non_signale(self):
        # `vu` est mis à True automatiquement dès qu'un push aboutit (issue
        # #122, moteur inchangé) — jamais de panneau pour un succès.
        self._ecrire_entree("projet_a", etat="pousse", fin="2026-11-03T10:05:00", vu=True)
        barre = self._barre_laterale()
        self.assertNotIn("panneau-sidebar-push", barre)
        self.assertNotIn("indicateur-push-en-cours", barre)

    def test_affichage_present_sur_une_autre_page_que_le_projet_concerne(self):
        self._ecrire_entree("projet_a", etat="refuse", fin="2026-11-03T10:05:00", vu=False)
        barre = self._barre_laterale("/projet/projet_b")
        self.assertIn("panneau-sidebar-push--refus", barre)


class AcquittementGlobalTestCase(BaseAffichageGlobalTestCase):
    """`POST /push/<nom_projet>/vu` (issue #123) : acquittement AJAX
    utilisable depuis n'importe quelle page, efface le panneau partout."""

    def test_acquittement_efface_le_panneau(self):
        self._ecrire_entree("projet_a", etat="refuse", fin="2026-11-03T10:05:00", vu=False)
        self.assertIn("panneau-sidebar-push--refus", self._barre_laterale())

        reponse = self.client.post("/push/projet_a/vu")
        self.assertEqual(reponse.get_json(), {"ok": True})

        self.assertNotIn("panneau-sidebar-push", self._barre_laterale())
        self.assertNotIn("projet_a", self.client.get("/push/etat").get_json()["projets"])

    def test_acquittement_ne_change_pas_letat(self):
        self._ecrire_entree("projet_a", etat="refuse", fin="2026-11-03T10:05:00", vu=False)
        self.client.post("/push/projet_a/vu")
        entree = push_arriere_plan.lire_entree("projet_a")
        self.assertEqual(entree["etat"], "refuse")
        self.assertTrue(entree["vu"])

    def test_acquittement_projet_sans_entree_ne_leve_pas_derreur(self):
        reponse = self.client.post("/push/projet_inconnu/vu")
        self.assertEqual(reponse.status_code, 200)


if __name__ == "__main__":
    unittest.main()
