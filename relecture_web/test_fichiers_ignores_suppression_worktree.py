#!/usr/bin/env python3
"""Tests de la détection des fichiers ignorés par git avant suppression de
worktree (issue #112) :

- `git status` (sans --ignored) — et donc `git worktree remove` même sans
  --force, et le diagnostic d'échec existant (issue #103) — ne voit JAMAIS
  les fichiers ignorés par `.gitignore` : ils disparaissent silencieusement
  avec le worktree. `git_info.lister_fichiers_ignores_worktree` corrige ce
  point mort, et les routes de suppression (`supprimer_worktrees_route`,
  `merger_et_supprimer_route`, `rejeter_worktrees_route`) doivent intercepter
  AVANT toute suppression (et avant toute fusion) dès qu'au moins un
  worktree sélectionné en contient un qui n'est pas du bruit sans valeur.
- le bruit sans valeur (caches Python/outils, .pyc, fichiers système) ne
  doit jamais apparaître dans cet avertissement, mais un dossier de build
  (ou tout autre dossier ignoré de valeur) ne doit jamais être caché par
  cette exclusion, même mélangé à du bruit.
- un projet distant (PC fixe CCW) ne doit jamais subir de calcul de taille
  coûteux par SSH, et la détection elle-même doit passer par les mêmes
  commandes git routées que le reste de l'outil (issue #109/#94) — jamais
  d'accès au PC fixe hors d'une action sur CE projet précis.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_fichiers_ignores_suppression_worktree -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_fichiers_ignores_suppression_worktree.py`.

Aucun accès réseau réel, aucune vraie commande ssh : les dépôts/worktrees
locaux sont de vrais dépôts git jetables créés dans un dossier temporaire
(même pattern que `test_chargement_a_la_demande_distant.py`), et le seul
cas « projet distant » teste directement le routage via un faux
`git_info._lancer_git_distant` qui ne lance jamais de vrai `ssh`."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module  # noqa: E402  (après l'ajustement de sys.path ci-dessus)
import git_info  # noqa: E402


def _init_depot_git_local(chemin):
    """Dépôt git local minimal (un commit) dans `chemin` — même helper que
    `test_chargement_a_la_demande_distant.py`."""
    os.makedirs(chemin, exist_ok=True)
    subprocess.run(["git", "init", "--quiet"], cwd=chemin, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=chemin, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin, check=True)
    with open(os.path.join(chemin, "fichier.txt"), "w", encoding="utf-8") as f:
        f.write("contenu\n")
    subprocess.run(["git", "add", "fichier.txt"], cwd=chemin, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "initial"], cwd=chemin, check=True)


def _ajouter_et_committer_gitignore(chemin_worktree, motifs):
    """Committe un `.gitignore` dans `chemin_worktree` — committé (pas
    seulement présent sur le disque) pour que ce fichier lui-même n'apparaisse
    jamais comme une modification non committée dans les scénarios de test
    qui se veulent par ailleurs "propres" (git respecte un .gitignore non
    suivi tout aussi bien, mais le laisser non suivi fausserait les
    scénarios "rien à signaler d'autre que les fichiers ignorés")."""
    with open(os.path.join(chemin_worktree, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("\n".join(motifs) + "\n")
    subprocess.run(["git", "add", ".gitignore"], cwd=chemin_worktree, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "ajoute .gitignore"], cwd=chemin_worktree, check=True)


def _creer_fichier(chemin_worktree, chemin_relatif, contenu="x"):
    chemin_absolu = os.path.join(chemin_worktree, chemin_relatif)
    os.makedirs(os.path.dirname(chemin_absolu), exist_ok=True)
    with open(chemin_absolu, "w", encoding="utf-8") as f:
        f.write(contenu)


# ---------------------------------------------------------------------------
# Niveau 1 : git_info.lister_fichiers_ignores_worktree directement, sur de
# vrais dépôts/worktrees jetables.
# ---------------------------------------------------------------------------

class DetectionFichiersIgnoresTestCase(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_ignores_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self.depot = os.path.join(self.scratch, "depot")
        _init_depot_git_local(self.depot)

    def test_rien_ignore_retourne_liste_vide(self):
        self.assertEqual(git_info.lister_fichiers_ignores_worktree(self.depot), [])

    def test_bruit_seul_exclu(self):
        _ajouter_et_committer_gitignore(self.depot, ["__pycache__/", "*.pyc", ".DS_Store", "Thumbs.db"])
        _creer_fichier(self.depot, "__pycache__/module.pyc")
        _creer_fichier(self.depot, "racine.pyc")
        _creer_fichier(self.depot, ".DS_Store")
        self.assertEqual(git_info.lister_fichiers_ignores_worktree(self.depot), [])

    def test_dossier_build_detecte_avec_taille(self):
        _ajouter_et_committer_gitignore(self.depot, ["installeur/output/"])
        _creer_fichier(self.depot, "installeur/output/app.exe", contenu="x" * 100)
        _creer_fichier(self.depot, "installeur/output/app.zip", contenu="y" * 50)

        resultat = git_info.lister_fichiers_ignores_worktree(self.depot)
        self.assertEqual(len(resultat), 1)
        self.assertTrue(resultat[0]["chemin"].startswith("installeur"))
        self.assertEqual(resultat[0]["taille"], 150)
        self.assertNotEqual(resultat[0]["taille_affichee"], "taille non calculée")

    def test_melange_bruit_et_build_ne_cache_pas_le_build(self):
        _ajouter_et_committer_gitignore(self.depot, ["installeur/output/", "__pycache__/", "*.pyc"])
        _creer_fichier(self.depot, "installeur/output/app.exe")
        _creer_fichier(self.depot, "__pycache__/module.pyc")
        _creer_fichier(self.depot, "racine.pyc")

        resultat = git_info.lister_fichiers_ignores_worktree(self.depot)
        chemins = [entree["chemin"] for entree in resultat]
        self.assertEqual(len(chemins), 1)
        self.assertTrue(chemins[0].startswith("installeur"))
        self.assertFalse(any("pycache" in c or c.endswith(".pyc") for c in chemins))

    def test_fichier_pyc_imbrique_dans_dossier_suivi_exclu(self):
        # Le dossier src/ lui-même est suivi (main.py tracké) : git ne peut
        # pas réduire l'entrée à "src/", seul "src/main.pyc" apparaît —
        # doit rester exclu malgré cette profondeur.
        _ajouter_et_committer_gitignore(self.depot, ["*.pyc"])
        _creer_fichier(self.depot, "src/main.py", contenu="code")
        subprocess.run(["git", "add", "src/main.py"], cwd=self.depot, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "ajoute src/main.py"], cwd=self.depot, check=True)
        _creer_fichier(self.depot, "src/main.pyc")
        self.assertEqual(git_info.lister_fichiers_ignores_worktree(self.depot), [])

    def test_chemin_introuvable_retourne_liste_vide(self):
        chemin_absent = os.path.join(self.scratch, "nexiste_pas")
        self.assertEqual(git_info.lister_fichiers_ignores_worktree(chemin_absent), [])


# ---------------------------------------------------------------------------
# Niveau 2 : routage local/distant (issue #109/#94) — la détection doit
# passer par exactement les mêmes commandes routées que le reste de
# l'outil, sans jamais calculer de taille par SSH.
# ---------------------------------------------------------------------------

class RoutageDistantDetectionTestCase(unittest.TestCase):
    def setUp(self):
        self.compteur_ssh = {"n": 0}

        def _faux_lancer_git_distant(repertoire, args, timeout, entree):
            self.compteur_ssh["n"] += 1
            if tuple(args[:2]) == ("status", "--porcelain=v1"):
                sortie = "!! installeur/output/\n!! __pycache__/\n"
                return subprocess.CompletedProcess(args=[], returncode=0, stdout=sortie, stderr="")
            return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        self._original_lancer_git_distant = git_info._lancer_git_distant
        git_info._lancer_git_distant = _faux_lancer_git_distant
        self.addCleanup(self._restaurer)

    def _restaurer(self):
        git_info._lancer_git_distant = self._original_lancer_git_distant

    def test_chemin_windows_route_via_ssh(self):
        resultat = git_info.lister_fichiers_ignores_worktree("C:\\CCW\\rummikub\\worktree-feature")
        self.assertEqual(self.compteur_ssh["n"], 1)
        self.assertEqual(len(resultat), 1)
        self.assertTrue(resultat[0]["chemin"].startswith("installeur"))

    def test_chemin_windows_jamais_de_calcul_de_taille_ssh(self):
        resultat = git_info.lister_fichiers_ignores_worktree("C:\\CCW\\rummikub\\worktree-feature")
        self.assertIsNone(resultat[0]["taille"])
        self.assertEqual(resultat[0]["taille_affichee"], "taille non calculée")
        # Un seul appel ssh (le `status --ignored`) : aucune tentative de
        # calcul de taille supplémentaire par SSH pour l'entrée détectée.
        self.assertEqual(self.compteur_ssh["n"], 1)

    def test_chemin_local_aucun_appel_ssh(self):
        scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_ignores_local_")
        try:
            _init_depot_git_local(scratch)
            git_info.lister_fichiers_ignores_worktree(scratch)
            self.assertEqual(self.compteur_ssh["n"], 0)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


# ---------------------------------------------------------------------------
# Niveau 3 : routes Flask de suppression — intégration complète sur de vrais
# dépôts/worktrees jetables.
# ---------------------------------------------------------------------------

class BaseSuppressionAvecFichiersIgnoresTestCase(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_suppr_ignores_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self.repertoire = os.path.join(self.scratch, "projet_local")
        _init_depot_git_local(self.repertoire)

        projets = [{
            "nom": "projet_local", "depot": "projet_local",
            "repertoire": self.repertoire, "couleur": None, "couleur_texte": None,
        }]

        def _faux_fetch_projets():
            return projets

        self._original_fetch_projets = git_info.fetch_projets
        git_info.fetch_projets = _faux_fetch_projets
        self.addCleanup(self._restaurer_fetch_projets)

        app_module.app.config["TESTING"] = True
        app_module.app.config["MDP_EXIGE"] = False
        self.client = app_module.app.test_client()

    def _restaurer_fetch_projets(self):
        git_info.fetch_projets = self._original_fetch_projets

    def _creer_branche_worktree(self, nom_branche):
        """Crée `nom_branche` + son worktree avec un commit propre (toujours
        à partir du worktree principal, déjà sur la branche principale),
        jamais fusionnée elle-même — voir `_fusionner_branche`, à appeler
        explicitement APRÈS tout ajout de fichier ignoré sur cette branche
        (sans quoi un commit ajouté après une fusion anticipée la ferait
        ressortir comme non fusionnée, puisque son dernier commit ne serait
        alors plus un ancêtre de la branche principale)."""
        chemin_worktree = os.path.join(self.scratch, f"worktree_{nom_branche}")
        subprocess.run(
            ["git", "worktree", "add", "-b", nom_branche, chemin_worktree],
            cwd=self.repertoire, check=True,
        )
        _creer_fichier(chemin_worktree, f"{nom_branche}.txt", contenu=f"contenu de {nom_branche}\n")
        subprocess.run(["git", "add", f"{nom_branche}.txt"], cwd=chemin_worktree, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", f"commit {nom_branche}"], cwd=chemin_worktree, check=True)
        return chemin_worktree

    def _fusionner_branche(self, nom_branche):
        subprocess.run(["git", "merge", "--quiet", nom_branche], cwd=self.repertoire, check=True)

    def _worktree_existe(self, chemin_worktree):
        return os.path.isdir(chemin_worktree)

    def _branche_existe(self, nom_branche):
        resultat = subprocess.run(
            ["git", "branch", "--list", nom_branche], cwd=self.repertoire,
            capture_output=True, text=True, check=True,
        )
        return bool(resultat.stdout.strip())


class SupprimerAvecFichiersIgnoresTestCase(BaseSuppressionAvecFichiersIgnoresTestCase):
    def test_bruit_seul_pas_de_confirmation_suppression_directe(self):
        worktree = self._creer_branche_worktree("feature-bruit")
        _ajouter_et_committer_gitignore(worktree, ["__pycache__/", "*.pyc"])
        _creer_fichier(worktree, "__pycache__/module.pyc")
        self._fusionner_branche("feature-bruit")

        reponse = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-bruit"]})
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree))
        self.assertFalse(self._branche_existe("feature-bruit"))

    def test_rien_ignore_pas_de_confirmation_suppression_directe(self):
        worktree = self._creer_branche_worktree("feature-propre")
        self._fusionner_branche("feature-propre")

        reponse = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-propre"]})
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree))
        self.assertFalse(self._branche_existe("feature-propre"))

    def test_dossier_build_ignore_affiche_confirmation_et_ne_supprime_rien(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        reponse = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-build"]})
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        self.assertIn("ignoré", texte)
        self.assertIn("installeur", texte)
        self.assertIn("feature-build", texte)
        # Rien n'a été supprimé tant que la confirmation n'a pas eu lieu.
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-build"))

    def test_melange_bruit_et_build_confirmation_affiche_build_pas_le_bruit(self):
        worktree = self._creer_branche_worktree("feature-mix")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/", "__pycache__/", "*.pyc"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        _creer_fichier(worktree, "__pycache__/module.pyc")
        self._fusionner_branche("feature-mix")

        reponse = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-mix"]})
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        self.assertIn("installeur", texte)
        self.assertNotIn("__pycache__", texte)
        self.assertTrue(self._worktree_existe(worktree))

    def test_confirmation_puis_bypass_supprime_reellement(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        premiere = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-build"]})
        self.assertEqual(premiere.status_code, 200)
        self.assertTrue(self._worktree_existe(worktree))

        confirmee = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build"],
            "ignorer_avertissement_fichiers_ignores": "on",
            # Menu obligatoire introduit par l'issue #116 (suite de celle-ci) :
            # sans ce champ, la re-soumission est maintenant refusée côté
            # serveur avant toute suppression (voir test dédié).
            "origine_decision": "personnelle",
        })
        self.assertEqual(confirmee.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree))
        self.assertFalse(self._branche_existe("feature-build"))

    def test_annuler_ne_supprime_rien(self):
        # « Annuler » ne fait qu'un lien retour vers la page projet, sans
        # aucune re-soumission du formulaire — rien de plus à exercer côté
        # serveur que l'absence de suppression après la première requête
        # (déjà vérifiée ci-dessus), confirmée ici par une simple requête
        # GET supplémentaire qui ne doit rien avoir changé.
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-build"]})
        reponse_projet = self.client.get("/projet/projet_local")
        self.assertEqual(reponse_projet.status_code, 200)
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-build"))

    def test_plusieurs_worktrees_un_seul_concerne_rien_ne_part_avant_confirmation(self):
        worktree_build = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree_build, ["installeur/output/"])
        _creer_fichier(worktree_build, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")
        worktree_propre = self._creer_branche_worktree("feature-propre")
        self._fusionner_branche("feature-propre")

        reponse = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build", "feature-propre"],
        })
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        self.assertIn("feature-build", texte)
        # Seul le worktree concerné est listé avec ses fichiers ignorés —
        # feature-propre n'a rien à signaler (il peut réapparaître comme
        # simple champ caché du formulaire de ré-envoi, mais pas comme
        # worktree listé avec des fichiers ignorés).
        self.assertNotIn('<span class="nom-branche">feature-propre</span>', texte)
        # Rien n'a été supprimé pour AUCUN des deux, même celui sans fichier
        # ignoré — le lot entier est mis en pause.
        self.assertTrue(self._worktree_existe(worktree_build))
        self.assertTrue(self._branche_existe("feature-build"))
        self.assertTrue(self._worktree_existe(worktree_propre))
        self.assertTrue(self._branche_existe("feature-propre"))

    def test_plusieurs_worktrees_confirmation_supprime_les_deux(self):
        worktree_build = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree_build, ["installeur/output/"])
        _creer_fichier(worktree_build, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")
        worktree_propre = self._creer_branche_worktree("feature-propre")
        self._fusionner_branche("feature-propre")

        self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build", "feature-propre"],
        })
        reponse = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build", "feature-propre"],
            "ignorer_avertissement_fichiers_ignores": "on",
            # Menu obligatoire introduit par l'issue #116 (suite de celle-ci) :
            # sans ce champ, la re-soumission est maintenant refusée côté
            # serveur avant toute suppression (voir test dédié).
            "origine_decision": "personnelle",
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree_build))
        self.assertFalse(self._branche_existe("feature-build"))
        self.assertFalse(self._worktree_existe(worktree_propre))
        self.assertFalse(self._branche_existe("feature-propre"))


class RejeterAvecFichiersIgnoresTestCase(BaseSuppressionAvecFichiersIgnoresTestCase):
    def test_dossier_build_ignore_affiche_confirmation_et_ne_rejette_rien(self):
        worktree = self._creer_branche_worktree("feature-rejet")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")

        reponse = self.client.post("/projet/projet_local/rejeter", data={"branches": ["feature-rejet"]})
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("installeur", reponse.get_data(as_text=True))
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-rejet"))

    def test_confirmation_puis_bypass_rejette_reellement(self):
        worktree = self._creer_branche_worktree("feature-rejet")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")

        self.client.post("/projet/projet_local/rejeter", data={"branches": ["feature-rejet"]})
        reponse = self.client.post("/projet/projet_local/rejeter", data={
            "branches": ["feature-rejet"],
            "ignorer_avertissement_fichiers_ignores": "on",
            # Menu obligatoire introduit par l'issue #116 (suite de celle-ci) :
            # sans ce champ, la re-soumission est maintenant refusée côté
            # serveur avant toute suppression (voir test dédié).
            "origine_decision": "personnelle",
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree))
        self.assertFalse(self._branche_existe("feature-rejet"))


class MergerEtSupprimerAvecFichiersIgnoresTestCase(BaseSuppressionAvecFichiersIgnoresTestCase):
    def test_dossier_build_ignore_affiche_confirmation_sans_fusionner(self):
        worktree = self._creer_branche_worktree("feature-merge")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")

        reponse = self.client.post(
            "/projet/projet_local/merger-et-supprimer", data={"branches": ["feature-merge"]}
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("installeur", reponse.get_data(as_text=True))
        # Ni la fusion ni la suppression n'ont eu lieu : le fichier propre à
        # la branche n'est pas encore dans la branche principale, et le
        # worktree/la branche existent toujours.
        self.assertFalse(os.path.exists(os.path.join(self.repertoire, "feature-merge.txt")))
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-merge"))

    def test_confirmation_puis_bypass_fusionne_et_supprime(self):
        worktree = self._creer_branche_worktree("feature-merge")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")

        self.client.post("/projet/projet_local/merger-et-supprimer", data={"branches": ["feature-merge"]})
        reponse = self.client.post("/projet/projet_local/merger-et-supprimer", data={
            "branches": ["feature-merge"],
            "ignorer_avertissement_fichiers_ignores": "on",
            # Menu obligatoire introduit par l'issue #116 (suite de celle-ci) :
            # sans ce champ, la re-soumission est maintenant refusée côté
            # serveur avant toute suppression (voir test dédié).
            "origine_decision": "personnelle",
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertTrue(os.path.exists(os.path.join(self.repertoire, "feature-merge.txt")))
        self.assertFalse(self._worktree_existe(worktree))
        self.assertFalse(self._branche_existe("feature-merge"))


if __name__ == "__main__":
    unittest.main()
