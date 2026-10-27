#!/usr/bin/env python3
"""Tests de l'issue #117 :

- les refus « Modifications non committées » de Merger et de Merger et
  supprimer (garde-fou de l'issue #74) nomment désormais les fichiers
  concernés avec leur statut (modifié, non suivi, supprimé...) au lieu de
  seulement en donner le nombre — plafonné à une dizaine d'entrées suivies
  de « … et N autres » (`git_info.decrire_modifications_non_committees`) ;
- le panneau repliable « 📄 .gitignore » (issue #98) est désormais affiché
  en bas de la page projet, après la liste des branches, dans une section
  « Outils du projet » — jamais confondu avec la liste des fichiers d'un
  refus affichée en haut de page, juste sous les messages flash. Son
  identifiant (`#details-gitignore`) et ses routes (ajouter/retirer un
  motif, ne plus suivre) restent inchangés.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_refus_modifications_non_committees_noms_fichiers -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_refus_modifications_non_committees_noms_fichiers.py`.

Aucun accès réseau réel : dépôt git local jetable créé dans un dossier
temporaire (même pattern que `test_fichiers_ignores_suppression_worktree.py`).
Le garde-fou « modifications non committées » est vérifié avant même que
les branches envoyées existent réellement (voir `merger_branches_route` /
`merger_et_supprimer_route`) : inutile de créer de vraies branches pour ces
tests, un nom de branche arbitraire suffit à passer le premier garde-fou
(« Aucune branche sélectionnée »)."""

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
    os.makedirs(chemin, exist_ok=True)
    subprocess.run(["git", "init", "--quiet"], cwd=chemin, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=chemin, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin, check=True)
    with open(os.path.join(chemin, "fichier.txt"), "w", encoding="utf-8") as f:
        f.write("contenu\n")
    subprocess.run(["git", "add", "fichier.txt"], cwd=chemin, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "initial"], cwd=chemin, check=True)


class BaseRefusTestCase(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_refus_noms_")
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

    def _poster_merger(self, route="merger"):
        return self.client.post(
            f"/projet/projet_local/{route}", data={"branches": ["peu-importe"]}, follow_redirects=True,
        )


class RefusNommeLesFichiersTestCase(BaseRefusTestCase):
    """Garde-fou « Modifications non committées » (issue #74), message
    enrichi par l'issue #117 — un seul fichier modifié, un seul fichier non
    suivi, un fichier supprimé, et les deux routes concernées (Merger,
    Merger et supprimer)."""

    def test_merger_refus_nomme_le_fichier_modifie(self):
        with open(os.path.join(self.repertoire, "fichier.txt"), "a", encoding="utf-8") as f:
            f.write("modification non committée\n")

        texte = self._poster_merger("merger").get_data(as_text=True)
        self.assertIn("fichier.txt (modifié)", texte)
        self.assertIn("dossier principal du projet", texte)
        self.assertIn("non suivis par git", texte)
        self.assertIn("merge refusé", texte)

    def test_merger_refus_nomme_le_fichier_non_suivi(self):
        with open(os.path.join(self.repertoire, "nouveau.txt"), "w", encoding="utf-8") as f:
            f.write("contenu\n")

        texte = self._poster_merger("merger").get_data(as_text=True)
        self.assertIn("nouveau.txt (non suivi)", texte)

    def test_merger_refus_nomme_le_fichier_supprime(self):
        os.remove(os.path.join(self.repertoire, "fichier.txt"))

        texte = self._poster_merger("merger").get_data(as_text=True)
        self.assertIn("fichier.txt (supprimé)", texte)

    def test_merger_et_supprimer_refus_nomme_les_fichiers(self):
        with open(os.path.join(self.repertoire, "fichier.txt"), "a", encoding="utf-8") as f:
            f.write("modification non committée\n")
        with open(os.path.join(self.repertoire, "nouveau.txt"), "w", encoding="utf-8") as f:
            f.write("contenu\n")

        texte = self._poster_merger("merger-et-supprimer").get_data(as_text=True)
        self.assertIn("fichier.txt (modifié)", texte)
        self.assertIn("nouveau.txt (non suivi)", texte)
        self.assertIn("fusion+suppression refusée", texte)

    def test_plusieurs_fichiers_separes_par_des_virgules(self):
        with open(os.path.join(self.repertoire, "a.txt"), "w", encoding="utf-8") as f:
            f.write("a\n")
        with open(os.path.join(self.repertoire, "b.txt"), "w", encoding="utf-8") as f:
            f.write("b\n")

        texte = self._poster_merger("merger").get_data(as_text=True)
        self.assertIn("a.txt (non suivi), b.txt (non suivi)", texte)


class PlafondDesFichiersListesTestCase(BaseRefusTestCase):
    """Plafonnée à une dizaine d'entrées suivies de « … et N autres »
    (issue #117) — jamais une liste illimitée."""

    def test_treize_fichiers_dix_listes_puis_trois_autres(self):
        for i in range(13):
            with open(os.path.join(self.repertoire, f"fichier_{i:02d}.txt"), "w", encoding="utf-8") as f:
                f.write("contenu\n")

        texte = self._poster_merger("merger").get_data(as_text=True)
        for i in range(10):
            self.assertIn(f"fichier_{i:02d}.txt (non suivi)", texte)
        for i in range(10, 13):
            self.assertNotIn(f"fichier_{i:02d}.txt (non suivi)", texte)
        self.assertIn("… et 3 autre(s)", texte)


class FonctionDecrireModificationsTestCase(unittest.TestCase):
    """Tests directs de `git_info.decrire_modifications_non_committees`,
    sans passer par l'application web — mêmes garanties (plafond, « … et N
    autres », chaîne vide si rien à signaler)."""

    def test_vide_si_rien_a_signaler(self):
        self.assertEqual(git_info.decrire_modifications_non_committees([]), "")

    def test_un_seul_fichier(self):
        self.assertEqual(
            git_info.decrire_modifications_non_committees([("a.txt", "modifié")]),
            "a.txt (modifié)",
        )

    def test_plafond_exact_sans_suffixe(self):
        details = [(f"f{i}.txt", "modifié") for i in range(10)]
        segment = git_info.decrire_modifications_non_committees(details)
        self.assertNotIn("autre", segment)
        self.assertEqual(segment.count(".txt"), 10)

    def test_au_dela_du_plafond_ajoute_le_suffixe(self):
        details = [(f"f{i}.txt", "modifié") for i in range(12)]
        segment = git_info.decrire_modifications_non_committees(details)
        self.assertEqual(segment.count(".txt"), 10)
        self.assertIn("… et 2 autre(s)", segment)


class PanneauGitignoreApresBranchesTestCase(BaseRefusTestCase):
    """Le panneau .gitignore (issue #98) apparaît désormais après la liste
    des branches et son panneau d'actions, dans une section « Outils du
    projet » (issue #117) — jamais avant, à l'endroit où un refus affiche
    sa propre liste de fichiers."""

    def test_panneau_gitignore_situe_apres_panneau_actions_branches(self):
        texte = self.client.get("/projet/projet_local").get_data(as_text=True)
        index_panneau_actions = texte.find('id="panneau-actions-branches"')
        index_panneau_gitignore = texte.find('id="details-gitignore"')
        self.assertNotEqual(index_panneau_actions, -1)
        self.assertNotEqual(index_panneau_gitignore, -1)
        self.assertLess(index_panneau_actions, index_panneau_gitignore)

    def test_panneau_gitignore_dans_section_outils_du_projet(self):
        texte = self.client.get("/projet/projet_local").get_data(as_text=True)
        index_section = texte.find('class="outils-projet"')
        index_panneau_gitignore = texte.find('id="details-gitignore"')
        self.assertNotEqual(index_section, -1)
        self.assertLess(index_section, index_panneau_gitignore)

    def test_panneau_toujours_replie_par_defaut(self):
        texte = self.client.get("/projet/projet_local").get_data(as_text=True)
        self.assertIn('<details class="panneau-gitignore" id="details-gitignore">', texte)

    def test_ajouter_motif_gitignore_fonctionne_toujours(self):
        reponse = self.client.post(
            "/projet/projet_local/gitignore/ajouter", data={"motif": "build/"}, follow_redirects=True,
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("build/", reponse.get_data(as_text=True))

    def test_retirer_motif_gitignore_fonctionne_toujours(self):
        self.client.post("/projet/projet_local/gitignore/ajouter", data={"motif": "build/"})
        lignes = git_info.lire_lignes_gitignore(self.repertoire)
        index = next(i for i, l in enumerate(lignes) if l.strip() == "build/")

        reponse = self.client.post(
            "/projet/projet_local/gitignore/retirer",
            data={"index": str(index), "texte": "build/"},
            follow_redirects=True,
        )
        self.assertEqual(reponse.status_code, 200)
        lignes_apres = git_info.lire_lignes_gitignore(self.repertoire)
        self.assertNotIn("build/", [l.strip() for l in lignes_apres])


if __name__ == "__main__":
    unittest.main()
