#!/usr/bin/env python3
"""Tests du bouton « Annuler » ajouté aux pages de confirmation de
suppression (issue #113, suite de #112) :

- `confirmation_fichiers_ignores_worktree.html` : un seul bouton visible
  (« Confirmer la suppression malgré tout ») donnait psychologiquement
  l'impression de n'avoir que ce choix. Un élément « Annuler » doit
  apparaître AVANT ce bouton, avec le focus par défaut. **Depuis l'issue
  #116** (suite de celle-ci), ce n'est plus un lien `<a>` de retour direct
  sans soumission : la case « à garder » par fichier et le journal des
  décisions imposent d'enregistrer une décision avant de revenir à la page
  du projet, donc Annuler est devenu un bouton de soumission du même
  formulaire que Confirmer (menu obligatoire « origine de la décision »,
  voir `test_decisions_fichiers_ignores_worktree.py` pour le détail de ce
  nouveau comportement) — seules les invariants encore valables ici (ordre
  des boutons, focus par défaut) sont revérifiés.
- `echec_suppression_worktree.html` (suppression forcée après un premier
  échec, issue #103) avait le même défaut pour chaque worktree concerné :
  même correction, même ordre, focus par défaut sur le premier Annuler de
  la page seulement (un seul élément avec `autofocus` par page, comme
  l'exige le HTML). **Non concernée par l'issue #116** — comportement et
  tests inchangés ci-dessous.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_bouton_annuler_confirmation_suppression -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_bouton_annuler_confirmation_suppression.py`.

Aucun accès réseau réel : dépôts/worktrees locaux jetables créés dans un
dossier temporaire (même pattern que
`test_fichiers_ignores_suppression_worktree.py`)."""

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


def _ajouter_et_committer_gitignore(chemin_worktree, motifs):
    with open(os.path.join(chemin_worktree, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("\n".join(motifs) + "\n")
    subprocess.run(["git", "add", ".gitignore"], cwd=chemin_worktree, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "ajoute .gitignore"], cwd=chemin_worktree, check=True)


def _creer_fichier(chemin_worktree, chemin_relatif, contenu="x"):
    chemin_absolu = os.path.join(chemin_worktree, chemin_relatif)
    os.makedirs(os.path.dirname(chemin_absolu), exist_ok=True)
    with open(chemin_absolu, "w", encoding="utf-8") as f:
        f.write(contenu)


class BaseAnnulerTestCase(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_annuler_")
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


class PageFichiersIgnoresTestCase(BaseAnnulerTestCase):
    """confirmation_fichiers_ignores_worktree.html — page atteinte via
    /projet/<nom>/supprimer quand un fichier ignoré de valeur serait
    perdu (issue #112)."""

    def _obtenir_page(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        reponse = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-build"]})
        self.assertEqual(reponse.status_code, 200)
        return reponse.get_data(as_text=True)

    def test_annuler_present_avant_le_bouton_de_confirmation(self):
        texte = self._obtenir_page()
        position_annuler = texte.find(">Annuler<")
        position_confirmer = texte.find("Confirmer la suppression malgré tout")
        self.assertNotEqual(position_annuler, -1, "aucun élément « Annuler » trouvé")
        self.assertNotEqual(position_confirmer, -1, "bouton de confirmation introuvable")
        self.assertLess(position_annuler, position_confirmer)

    def test_annuler_est_un_bouton_de_soumission_depuis_lissue_116(self):
        # Depuis l'issue #116, Annuler n'est plus un simple lien <a> : il
        # soumet le même formulaire que Confirmer (menu obligatoire
        # d'origine de la décision), vers une route dédiée qui n'efface
        # jamais rien — voir test_decisions_fichiers_ignores_worktree.py.
        texte = self._obtenir_page()
        self.assertNotIn(
            '<a href="/projet/projet_local" class="bouton bouton--annuler lien-bouton"',
            texte,
        )
        self.assertIn(
            'id="bouton-annuler-fichiers-ignores" class="bouton bouton--annuler"\n'
            '            formaction="/projet/projet_local/fichiers-ignores/annuler" autofocus>Annuler</button>',
            texte,
        )

    def test_un_seul_autofocus_sur_la_page_et_cest_annuler(self):
        texte = self._obtenir_page()
        self.assertEqual(texte.count("autofocus"), 1)
        # Le seul "autofocus" de la page doit être sur l'élément Annuler,
        # pas sur le bouton de confirmation.
        debut = texte.index("autofocus")
        self.assertIn("Annuler", texte[debut:debut + 60])

    def test_formulaire_de_confirmation_inchange(self):
        texte = self._obtenir_page()
        self.assertIn('class="form-confirmer-fichiers-ignores"', texte)
        self.assertIn('name="ignorer_avertissement_fichiers_ignores" value="on"', texte)
        self.assertIn('name="branches"', texte)
        self.assertIn('class="bouton bouton--danger">Confirmer la suppression malgré tout</button>', texte)

    def test_annuler_ne_declenche_aucune_suppression(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-build"]})
        # N'exerce pas le bouton Annuler lui-même (voir
        # test_decisions_fichiers_ignores_worktree.py, issue #116, pour son
        # comportement complet depuis qu'il soumet le formulaire) : une
        # simple navigation GET vers la page projet, sans aucune requête
        # supplémentaire, ne doit rien avoir changé — invariant inchangé.
        reponse_projet = self.client.get("/projet/projet_local")
        self.assertEqual(reponse_projet.status_code, 200)
        self.assertTrue(os.path.isdir(worktree))


class PageEchecSuppressionForceeTestCase(BaseAnnulerTestCase):
    """echec_suppression_worktree.html — page atteinte via
    /projet/<nom>/supprimer quand `git worktree remove` (sans --force)
    échoue à cause de fichiers suivis modifiés/non commités (issue #103)."""

    def _obtenir_page(self, noms_branches):
        return self.client.post(
            "/projet/projet_local/supprimer", data={"branches": noms_branches}
        ).get_data(as_text=True)

    def _rendre_sale(self, worktree, nom_branche):
        with open(os.path.join(worktree, f"{nom_branche}.txt"), "a", encoding="utf-8") as f:
            f.write("modification non committée\n")

    def test_annuler_present_avant_le_bouton_de_forcage(self):
        worktree = self._creer_branche_worktree("feature-sale")
        self._fusionner_branche("feature-sale")
        self._rendre_sale(worktree, "feature-sale")

        texte = self._obtenir_page(["feature-sale"])
        self.assertIn("Forcer la suppression", texte)
        position_annuler = texte.find(">Annuler<")
        position_forcer = texte.find("Forcer la suppression")
        self.assertNotEqual(position_annuler, -1, "aucun élément « Annuler » trouvé")
        self.assertLess(position_annuler, position_forcer)

    def test_annuler_est_un_lien_vers_la_page_projet(self):
        worktree = self._creer_branche_worktree("feature-sale")
        self._fusionner_branche("feature-sale")
        self._rendre_sale(worktree, "feature-sale")

        texte = self._obtenir_page(["feature-sale"])
        self.assertIn('<a href="/projet/projet_local" class="bouton bouton--annuler lien-bouton"', texte)

    def test_un_seul_autofocus_meme_avec_plusieurs_worktrees_en_echec(self):
        worktree_1 = self._creer_branche_worktree("feature-sale-1")
        self._fusionner_branche("feature-sale-1")
        self._rendre_sale(worktree_1, "feature-sale-1")
        worktree_2 = self._creer_branche_worktree("feature-sale-2")
        self._fusionner_branche("feature-sale-2")
        self._rendre_sale(worktree_2, "feature-sale-2")

        texte = self._obtenir_page(["feature-sale-1", "feature-sale-2"])
        self.assertEqual(texte.count("Forcer la suppression"), 2)
        self.assertEqual(texte.count("autofocus"), 1)
        # Un lien Annuler par worktree en échec — exclut l'Annuler générique
        # de la fenêtre modale (base.html), lui aussi présent sur la page
        # mais jamais visible tant qu'aucune action n'est cliquée.
        self.assertEqual(texte.count('bouton--annuler lien-bouton">Annuler</a>') +
                          texte.count('bouton--annuler lien-bouton" autofocus>Annuler</a>'), 2)

    def test_formulaire_de_forcage_inchange(self):
        worktree = self._creer_branche_worktree("feature-sale")
        self._fusionner_branche("feature-sale")
        self._rendre_sale(worktree, "feature-sale")

        texte = self._obtenir_page(["feature-sale"])
        self.assertIn('class="form-forcer-suppression"', texte)
        self.assertIn('name="branche" value="feature-sale"', texte)
        self.assertIn(
            'class="bouton bouton--danger bouton-forcer-suppression">Forcer la suppression</button>', texte
        )


if __name__ == "__main__":
    unittest.main()
