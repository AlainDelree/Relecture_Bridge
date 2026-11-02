#!/usr/bin/env python3
"""Tests du grisage du bouton de validation de la fenêtre de confirmation
pendant que l'envoi réel tourne (issue #120, suite de #49/#71/#73/#116) :

- `ouvrirConfirmation` (`base.html`, commune à toutes les actions qui
  l'utilisent) grise désormais son propre bouton de validation avec un
  libellé « ... en cours... » dès le clic de validation (pas à
  l'ouverture), bloque son bouton Annuler, et bloque en plus — si fourni —
  `options.boutonDeclencheur`, le bouton « Confirmer » de la page derrière
  qui a ouvert la fenêtre, pour qu'aucun second envoi ne parte pendant que
  le premier tourne. Un `pageshow` global réinitialise ces trois boutons
  si une restauration par le bouton « précédent » du navigateur (bfcache)
  les avait figés désactivés.
- Les trois pages de confirmation forte dédiées (page derrière = un seul
  bouton de formulaire, jamais la fenêtre commune elle-même) relient
  chacune leur bouton réel à `options.boutonDeclencheur` :
  `confirmation_fichiers_ignores_worktree.html`,
  `echec_suppression_worktree.html`, `confirmation_verrou_fusion.html`.

Pas de framework de test externe dans ce dépôt (voir #107), et aucun
moteur JS disponible pour exécuter `ouvrirConfirmation` elle-même : ces
tests vérifient donc, comme les autres fichiers de ce dossier le font déjà
pour la structure HTML, que le code JS attendu est bien présent dans la
page rendue (recherche de sous-chaînes exactes) — pas un remplacement à un
test d'exécution réelle, mais ce qui est simplement couvrable ici.

Lançable par
`python3 -m unittest relecture_web.test_bouton_grise_confirmation_en_cours -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_bouton_grise_confirmation_en_cours.py`."""

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


class BaseProjetLocalTestCase(unittest.TestCase):
    """Harnais Flask commun : un seul projet local avec une branche fusionnée
    dans un dépôt git jetable — même pattern que
    `test_bouton_annuler_confirmation_suppression.py`."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_grisage_")
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

    def _rendre_sale(self, worktree, nom_branche):
        with open(os.path.join(worktree, f"{nom_branche}.txt"), "a", encoding="utf-8") as f:
            f.write("modification non committée\n")


class ScriptCommunGrisageTestCase(BaseProjetLocalTestCase):
    """`ouvrirConfirmation` (base.html) est incluse sur toutes les pages
    via `{% extends "base.html" %}` : n'importe quelle page suffit pour
    vérifier sa présence — ici la page projet, déjà disponible sans
    déclencher aucune confirmation."""

    def _texte_page_projet(self):
        reponse = self.client.get("/projet/projet_local")
        self.assertEqual(reponse.status_code, 200)
        return reponse.get_data(as_text=True)

    def test_bouton_validation_grise_et_relibelle_au_clic_de_confirmation(self):
        texte = self._texte_page_projet()
        self.assertIn('boutonConfirmer.disabled = true;', texte)
        self.assertIn('boutonConfirmer.textContent = options.libelleBouton + " en cours…";', texte)

    def test_annuler_et_bouton_declencheur_bloques_en_meme_temps(self):
        texte = self._texte_page_projet()
        self.assertIn('boutonAnnuler.disabled = true;', texte)
        self.assertIn('if (options.boutonDeclencheur) {', texte)
        self.assertIn('options.boutonDeclencheur.disabled = true;', texte)

    def test_etat_normal_reinitialise_a_chaque_ouverture(self):
        # Ligne distincte de celle posée dans surConfirmer ci-dessus (false,
        # pas true) : une fenêtre rouverte après une précédente confirmation
        # (Annuler puis une autre action) ne doit jamais réafficher Annuler
        # désactivé.
        texte = self._texte_page_projet()
        self.assertIn('boutonAnnuler.disabled = false;', texte)

    def test_pageshow_global_reinitialise_la_fenetre_et_le_bouton_declencheur(self):
        texte = self._texte_page_projet()
        self.assertIn('window.addEventListener("pageshow"', texte)
        self.assertIn('boutonConfirmerModal.disabled = false;', texte)
        self.assertIn('boutonAnnulerModal.disabled = false;', texte)
        self.assertIn('boutonDeclencheurEnCours.disabled = false;', texte)

    def test_indicateur_ns_existant_de_push_merger_non_retire(self):
        # Garde-fou de non-régression : l'indicateur "... en cours... Ns"
        # de Push/Merger (issue #49) doit rester intact, jamais remplacé
        # par ce grisage.
        texte = self._texte_page_projet()
        self.assertIn('overlayTexte.textContent = libelle + " en cours... " + secondes + "s";', texte)


class PageFichiersIgnoresBoutonDeclencheurTestCase(BaseProjetLocalTestCase):
    """`confirmation_fichiers_ignores_worktree.html` — un seul bouton
    « Confirmer » sur la page derrière la fenêtre commune."""

    def test_boutonDeclencheur_relie_au_bouton_confirmer_de_la_page(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        reponse = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-build"]})
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        self.assertIn('boutonDeclencheur: boutonConfirmerSubmit', texte)


class PageEchecSuppressionBoutonDeclencheurTestCase(BaseProjetLocalTestCase):
    """`echec_suppression_worktree.html` — un formulaire (et un seul
    bouton) par worktree en échec."""

    def test_boutonDeclencheur_relie_au_bouton_du_formulaire_concerne(self):
        worktree = self._creer_branche_worktree("feature-sale")
        self._fusionner_branche("feature-sale")
        self._rendre_sale(worktree, "feature-sale")

        texte = self.client.post(
            "/projet/projet_local/supprimer", data={"branches": ["feature-sale"]}
        ).get_data(as_text=True)
        self.assertIn(
            'var boutonSubmit = evenement.submitter || formulaire.querySelector(".bouton-forcer-suppression");',
            texte,
        )
        self.assertIn('boutonDeclencheur: boutonSubmit', texte)


class PageVerrouFusionBoutonDeclencheurTestCase(unittest.TestCase):
    """`confirmation_verrou_fusion.html` — un seul formulaire, un seul
    bouton « Fusionner quand même » sur la page derrière la fenêtre."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_grisage_verrou_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self.repertoire = os.path.join(self.scratch, "projet_local")
        _init_depot_git_local(self.repertoire)
        self.dossier_bridge_agent = os.path.join(self.scratch, "bridge_agent")
        _init_depot_git_local(self.dossier_bridge_agent)
        self.dossier_verrous = os.path.join(self.dossier_bridge_agent, "logs", "verrous")

        projets = [
            {
                "nom": "projet_local", "depot": "projet_local",
                "repertoire": self.repertoire, "couleur": None, "couleur_texte": None,
            },
            {
                "nom": "bridge_agent", "depot": "bridge_agent",
                "repertoire": self.dossier_bridge_agent, "couleur": None, "couleur_texte": None,
            },
        ]

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
        with open(os.path.join(chemin_worktree, f"{nom_branche}.txt"), "w", encoding="utf-8") as f:
            f.write(f"contenu de {nom_branche}\n")
        subprocess.run(["git", "add", f"{nom_branche}.txt"], cwd=chemin_worktree, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", f"commit {nom_branche}"], cwd=chemin_worktree, check=True)
        return chemin_worktree

    def _ecrire_verrou(self, nom_fichier, pid, rep, projet, mode):
        os.makedirs(self.dossier_verrous, exist_ok=True)
        with open(os.path.join(self.dossier_verrous, nom_fichier), "w", encoding="utf-8") as f:
            f.write(f"pid={pid} rep={rep} projet={projet} mode={mode}\n")

    def test_boutonDeclencheur_relie_au_bouton_fusionner_quand_meme(self):
        self._creer_branche_worktree("feature-a")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "lecture",
        )

        reponse = self.client.post(
            "/projet/projet_local/merger", data={"branches": ["feature-a"]}, follow_redirects=False
        )
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        self.assertIn(
            'var boutonSubmit = evenement.submitter || formulaire.querySelector(".bouton-forcer-fusion-malgre-verrou");',
            texte,
        )
        self.assertIn('boutonDeclencheur: boutonSubmit', texte)


if __name__ == "__main__":
    unittest.main()
