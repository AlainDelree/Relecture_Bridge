#!/usr/bin/env python3
"""Tests de la décision par fichier et du journal des décisions sur
confirmation_fichiers_ignores_worktree.html (issue #116, suite de #113) :

- une case « à garder » par fichier/dossier listé, décochée par défaut,
  jamais présélectionnée — et un moyen de tout cocher/décocher d'un seul
  geste par worktree (la suppression reste toujours par worktree entier) ;
- « Confirmer la suppression malgré tout » refusé CÔTÉ SERVEUR (pas
  seulement désactivé dans la page) si au moins une case est cochée, ou si
  le menu obligatoire « origine de la décision » (Vu avec Claude Chat /
  Décision personnelle, sans valeur présélectionnée) n'a pas été rempli ;
  sinon, chaque fichier listé est journalisé « supprimer » puis la
  suppression a lieu comme avant ;
- « Annuler » n'est plus un simple lien : il impose le même menu
  obligatoire, journalise « garder »/« supprimer (pas encore fait) » par
  fichier selon les cases cochées, et ne supprime jamais rien — contraire
  à « Précédent », au fil d'Ariane ou à tout lien vers un autre projet, qui
  n'envoient toujours aucune requête et n'enregistrent donc rien ;
- le journal (`git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES`) est un
  fichier texte en ajout, hors de tout worktree, ignoré par git, dont une
  écriture impossible n'empêche jamais l'action en cours (avertissement
  affiché à la place) ;
- un projet distant (PC fixe CCW) se comporte à l'identique, sans jamais
  déclencher de calcul de taille par SSH (issue #109, inchangé).

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_decisions_fichiers_ignores_worktree -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_decisions_fichiers_ignores_worktree.py`.

Aucun accès réseau réel, aucune vraie commande ssh, et jamais le vrai
journal d'Alain : `git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES` est
redirigée vers un fichier d'un dossier temporaire dans `setUp`/`tearDown`
de chaque cas, comme les autres constantes de chemin de ce module dans les
tests précédents (même pattern que `test_fichiers_ignores_suppression_worktree.py`)."""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from subprocess import CompletedProcess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module  # noqa: E402  (après l'ajustement de sys.path ci-dessus)
import git_info  # noqa: E402

RACINE_DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def _extraire_fichiers_json(texte):
    match = re.search(r'id="champ-fichiers-json" value=\'(.*?)\'', texte, re.S)
    assert match, "champ fichiers_json introuvable sur la page"
    return match.group(1)


def _extraire_cases_garder(texte):
    """[(index, worktree), ...] dans l'ordre d'apparition, et vérifie
    qu'aucune n'est présélectionnée (jamais `checked` sur la balise)."""
    cases = re.findall(
        r'<input type="checkbox" class="case-a-garder" name="garder" value="(\d+)" data-worktree="([^"]+)">',
        texte,
    )
    toutes_les_cases_brutes = re.findall(r'<input type="checkbox" class="case-a-garder"[^>]*>', texte)
    for case in toutes_les_cases_brutes:
        assert "checked" not in case, f"case présélectionnée trouvée : {case}"
    return cases


class BaseDecisionsTestCase(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_decisions_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self.repertoire = os.path.join(self.scratch, "projet_local")
        _init_depot_git_local(self.repertoire)

        self.chemin_journal = os.path.join(self.scratch, "decisions_fichiers_ignores.log")
        self._journal_original = git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES
        git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES = self.chemin_journal
        self.addCleanup(self._restaurer_journal)

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

    def _restaurer_journal(self):
        git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES = self._journal_original

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

    def _worktree_existe(self, chemin_worktree):
        return os.path.isdir(chemin_worktree)

    def _branche_existe(self, nom_branche):
        resultat = subprocess.run(
            ["git", "branch", "--list", nom_branche], cwd=self.repertoire,
            capture_output=True, text=True, check=True,
        )
        return bool(resultat.stdout.strip())

    def _lire_journal(self):
        if not os.path.exists(self.chemin_journal):
            return []
        with open(self.chemin_journal, encoding="utf-8") as f:
            return [l for l in f.read().splitlines() if l.strip()]

    def _obtenir_confirmation(self, branches, route="/projet/projet_local/supprimer"):
        reponse = self.client.post(route, data={"branches": branches})
        self.assertEqual(reponse.status_code, 200)
        return reponse.get_data(as_text=True)


class PageCasesEtMenuTestCase(BaseDecisionsTestCase):
    def test_une_case_par_fichier_jamais_presaisie(self):
        # Deux ENTRÉES ignorées distinctes (git réduit un dossier ignoré
        # entier à son seul nom, voir lister_fichiers_ignores_worktree) :
        # un même dossier avec deux fichiers dedans ne compterait que
        # pour une seule entrée/case.
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/", "cache/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        _creer_fichier(worktree, "cache/tmp.bin")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        cases = _extraire_cases_garder(texte)
        self.assertEqual(len(cases), 2)

    def test_origine_decision_sans_valeur_presaisie(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        self.assertIn('name="origine_decision" id="champ-origine-decision" value="">', texte)

    def test_bouton_tout_cocher_et_tout_decocher_presents_par_worktree(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        self.assertIn("bouton-tout-cocher-garder", texte)
        self.assertIn("bouton-tout-decocher-garder", texte)
        # La suppression reste par worktree entier : ces boutons ciblent un
        # seul worktree (attribut data-cible-worktree), jamais une sélection
        # inter-worktrees.
        self.assertIn('data-cible-worktree="wt-1"', texte)

    def test_fichiers_json_correspond_aux_cases_rendues(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        fichiers = json.loads(_extraire_fichiers_json(texte))
        self.assertEqual(len(fichiers), 1)
        self.assertEqual(fichiers[0]["branche"], "feature-build")
        self.assertTrue(fichiers[0]["chemin"].startswith("installeur"))


class LiensSansEffetTestCase(BaseDecisionsTestCase):
    """Précédent, le fil d'Ariane, un lien vers un autre projet, le bouton
    retour du navigateur : toujours de simples liens <a> (jamais soumis),
    donc aucune requête d'enregistrement n'est même possible — vérifié ici
    en constatant qu'une navigation GET supplémentaire (équivalente à l'un
    de ces liens, ou au retour navigateur) ne touche jamais le journal ni
    le worktree."""

    def test_navigation_get_apres_la_page_necrit_rien(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        self._obtenir_confirmation(["feature-build"])
        for chemin in ("/projet/projet_local", "/"):
            reponse = self.client.get(chemin)
            self.assertIn(reponse.status_code, (200, 302))
        self.assertEqual(self._lire_journal(), [])
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-build"))


class AnnulerAvecMenuTestCase(BaseDecisionsTestCase):
    def test_annuler_avec_menu_journalise_et_ne_supprime_rien(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/", "cache/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        _creer_fichier(worktree, "cache/tmp.bin")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)
        cases = _extraire_cases_garder(texte)
        self.assertEqual(len(cases), 2)
        # Coche la première case « à garder » (installeur), laisse l'autre
        # (cache) décochée.
        index_garde = cases[0][0]

        reponse = self.client.post("/projet/projet_local/fichiers-ignores/annuler", data={
            "fichiers_json": fichiers_json,
            "garder": [index_garde],
            "origine_decision": "claude_chat",
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-build"))

        lignes = self._lire_journal()
        self.assertEqual(len(lignes), 2)
        self.assertTrue(any("decision=garder" in l and "bouton=annuler" in l for l in lignes))
        self.assertTrue(any("decision=supprimer (pas encore fait)" in l and "bouton=annuler" in l for l in lignes))
        self.assertTrue(all("origine=claude_chat" in l for l in lignes))
        self.assertTrue(all("projet=projet_local" in l and "branche=feature-build" in l for l in lignes))

    def test_annuler_sans_menu_refuse_cote_serveur(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)

        reponse = self.client.post("/projet/projet_local/fichiers-ignores/annuler", data={
            "fichiers_json": fichiers_json,
            # Pas de origine_decision du tout — menu non rempli.
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(self._lire_journal(), [])
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-build"))


class ConfirmerCoteServeurTestCase(BaseDecisionsTestCase):
    def _donnees_confirmation(self, branches, fichiers_json, **extra):
        donnees = {
            "branches": branches,
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
        }
        donnees.update(extra)
        return donnees

    def test_confirmer_avec_case_cochee_refuse_sans_suppression(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)
        cases = _extraire_cases_garder(texte)

        reponse = self.client.post("/projet/projet_local/supprimer", data=self._donnees_confirmation(
            ["feature-build"], fichiers_json,
            garder=[cases[0][0]], origine_decision="personnelle",
        ))
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(self._lire_journal(), [])
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-build"))

    def test_confirmer_sans_case_cochee_mais_sans_menu_refuse(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)

        reponse = self.client.post("/projet/projet_local/supprimer", data=self._donnees_confirmation(
            ["feature-build"], fichiers_json,
        ))
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(self._lire_journal(), [])
        self.assertTrue(self._worktree_existe(worktree))
        self.assertTrue(self._branche_existe("feature-build"))

    def test_confirmer_sans_case_cochee_avec_menu_supprime_et_journalise(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)

        reponse = self.client.post("/projet/projet_local/supprimer", data=self._donnees_confirmation(
            ["feature-build"], fichiers_json, origine_decision="personnelle",
        ))
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree))
        self.assertFalse(self._branche_existe("feature-build"))

        lignes = self._lire_journal()
        self.assertEqual(len(lignes), 1)
        self.assertIn("decision=supprimer", lignes[0])
        self.assertNotIn("decision=supprimer (pas encore fait)", lignes[0])
        self.assertIn("bouton=confirmer", lignes[0])
        self.assertIn("origine=personnelle", lignes[0])
        self.assertIn("fichier=installeur", lignes[0])

    def test_plusieurs_worktrees_confirmation_supprime_et_journalise_chacun(self):
        worktree_a = self._creer_branche_worktree("feature-a")
        _ajouter_et_committer_gitignore(worktree_a, ["installeur/output/"])
        _creer_fichier(worktree_a, "installeur/output/app.exe")
        self._fusionner_branche("feature-a")
        worktree_b = self._creer_branche_worktree("feature-b")
        _ajouter_et_committer_gitignore(worktree_b, ["cache/"])
        _creer_fichier(worktree_b, "cache/tmp.bin")
        self._fusionner_branche("feature-b")

        texte = self._obtenir_confirmation(["feature-a", "feature-b"])
        fichiers_json = _extraire_fichiers_json(texte)
        fichiers = json.loads(fichiers_json)
        self.assertEqual({f["branche"] for f in fichiers}, {"feature-a", "feature-b"})

        reponse = self.client.post("/projet/projet_local/supprimer", data=self._donnees_confirmation(
            ["feature-a", "feature-b"], fichiers_json, origine_decision="claude_chat",
        ))
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree_a))
        self.assertFalse(self._worktree_existe(worktree_b))

        lignes = self._lire_journal()
        self.assertEqual(len(lignes), 2)
        self.assertTrue(any("branche=feature-a" in l for l in lignes))
        self.assertTrue(any("branche=feature-b" in l for l in lignes))
        self.assertTrue(all("decision=supprimer" in l and "bouton=confirmer" in l for l in lignes))


class JournalNonInscriptibleTestCase(BaseDecisionsTestCase):
    def setUp(self):
        super().setUp()
        self.dossier_lecture_seule = os.path.join(self.scratch, "journal_lecture_seule")
        os.makedirs(self.dossier_lecture_seule, exist_ok=True)
        git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES = os.path.join(
            self.dossier_lecture_seule, "decisions_fichiers_ignores.log"
        )
        os.chmod(self.dossier_lecture_seule, stat.S_IRUSR | stat.S_IXUSR)
        self.addCleanup(lambda: os.chmod(self.dossier_lecture_seule, stat.S_IRWXU))

    def test_ecriture_impossible_naffecte_pas_la_suppression_mais_avertit(self):
        worktree = self._creer_branche_worktree("feature-build")
        _ajouter_et_committer_gitignore(worktree, ["installeur/output/"])
        _creer_fichier(worktree, "installeur/output/app.exe")
        self._fusionner_branche("feature-build")

        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)

        reponse = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build"],
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
            "origine_decision": "personnelle",
        }, follow_redirects=True)
        self.assertEqual(reponse.status_code, 200)
        # L'action (suppression) n'est jamais bloquée par l'échec d'écriture
        # du journal — seulement signalée.
        self.assertFalse(self._worktree_existe(worktree))
        self.assertFalse(self._branche_existe("feature-build"))
        self.assertIn("journal", reponse.get_data(as_text=True))
        self.assertFalse(os.path.exists(git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES))


class GitignoreJournalDecisionsTestCase(unittest.TestCase):
    """Chemin du journal (`relecture_web/decisions_fichiers_ignores.log`,
    comme `relecture_web/changelog_fusion.log`) ignoré par git — vérifié
    avec `git check-ignore` dans un dépôt git jetable, jamais le vrai dépôt
    de travail de ce test."""

    def setUp(self):
        self.depot = tempfile.mkdtemp(prefix="relecture_bridge_test_gitignore_journal_")
        self.addCleanup(shutil.rmtree, self.depot, ignore_errors=True)
        subprocess.run(["git", "init", "--quiet"], cwd=self.depot, check=True)
        shutil.copy(os.path.join(RACINE_DEPOT, ".gitignore"), os.path.join(self.depot, ".gitignore"))

    def test_chemin_du_journal_ignore(self):
        resultat = subprocess.run(
            ["git", "check-ignore", "-q", "relecture_web/decisions_fichiers_ignores.log"],
            cwd=self.depot,
        )
        self.assertEqual(resultat.returncode, 0)


class ProjetDistantFauxSshTestCase(BaseDecisionsTestCase):
    """Même comportement pour un projet distant (PC fixe CCW) : chaque
    commande git est routée via un faux `_lancer_git_distant` (jamais de
    vrai ssh), et `lister_fichiers_ignores_worktree` ne calcule jamais de
    taille par SSH (issue #109, inchangé) — `taille_affichee` reste "taille
    non calculée", reportée telle quelle dans le journal."""

    def setUp(self):
        # Pas de dépôt git local pour ce cas : tout est routé par le faux
        # ssh ci-dessous, aucune commande git réelle n'est lancée pour ce
        # projet précis.
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_decisions_distant_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self.chemin_journal = os.path.join(self.scratch, "decisions_fichiers_ignores.log")
        self._journal_original = git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES
        git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES = self.chemin_journal
        self.addCleanup(self._restaurer_journal)

        self.repertoire = "C:\\CCW\\projet_distant"
        self.worktree_feature = "C:\\CCW\\projet_distant_worktree_feature-distant"

        projets = [{
            "nom": "projet_distant", "depot": "projet_distant",
            "repertoire": self.repertoire, "couleur": None, "couleur_texte": None,
        }]

        def _faux_fetch_projets():
            return projets

        def _faux_charger_config_ccw():
            return {"host": "utilisateur@192.0.2.1", "cle": "/chemin/factice/cle"}

        def _faux_tester_connectivite_ccw():
            return True, None, None

        def _faux_lancer_git_distant(repertoire, args, timeout, entree):
            a = list(args)
            if a[0] == "for-each-ref":
                sortie = (
                    "main\tabc1234\t2024-01-01T00:00:00+00:00\tinitial\n"
                    "feature-distant\tdef5678\t2024-01-02T00:00:00+00:00\tcommit feature\n"
                )
                return CompletedProcess(args=[], returncode=0, stdout=sortie, stderr="")
            if a[0] == "rev-parse" and "HEAD" in a:
                return CompletedProcess(args=[], returncode=0, stdout="main\n", stderr="")
            if a[0] == "rev-parse":
                return CompletedProcess(args=[], returncode=1, stdout="", stderr="pas d'amont")
            if a[0] == "worktree" and a[1] == "list":
                sortie = (
                    f"worktree {self.repertoire}\nbranch refs/heads/main\n\n"
                    f"worktree {self.worktree_feature}\nbranch refs/heads/feature-distant\n\n"
                )
                return CompletedProcess(args=[], returncode=0, stdout=sortie, stderr="")
            if a[0] == "worktree" and a[1] == "remove":
                return CompletedProcess(args=[], returncode=0, stdout="", stderr="")
            if a[0] == "merge-base":
                return CompletedProcess(args=[], returncode=0, stdout="", stderr="")
            if a[0] == "branch" and a[1] == "-D":
                return CompletedProcess(args=[], returncode=0, stdout="", stderr="")
            if a[0] == "status" and repertoire == self.worktree_feature:
                return CompletedProcess(args=[], returncode=0, stdout="!! secret_key.conf\n", stderr="")
            return CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        self._original_fetch_projets = git_info.fetch_projets
        self._original_charger_config_ccw = git_info.charger_config_ccw
        self._original_tester_connectivite = git_info.tester_connectivite_ccw
        self._original_lancer_git_distant = git_info._lancer_git_distant
        git_info.fetch_projets = _faux_fetch_projets
        git_info.charger_config_ccw = _faux_charger_config_ccw
        git_info.tester_connectivite_ccw = _faux_tester_connectivite_ccw
        git_info._lancer_git_distant = _faux_lancer_git_distant
        self.addCleanup(self._restaurer_git_info)

        app_module.app.config["TESTING"] = True
        app_module.app.config["MDP_EXIGE"] = False
        self.client = app_module.app.test_client()

    def _restaurer_git_info(self):
        git_info.fetch_projets = self._original_fetch_projets
        git_info.charger_config_ccw = self._original_charger_config_ccw
        git_info.tester_connectivite_ccw = self._original_tester_connectivite
        git_info._lancer_git_distant = self._original_lancer_git_distant

    def test_confirmation_affiche_taille_non_calculee(self):
        texte = self._obtenir_confirmation(["feature-distant"], route="/projet/projet_distant/supprimer")
        self.assertIn("secret_key.conf", texte)
        self.assertIn("taille non calculée", texte)

    def test_confirmer_sur_projet_distant_supprime_et_journalise_taille_non_calculee(self):
        texte = self._obtenir_confirmation(["feature-distant"], route="/projet/projet_distant/supprimer")
        fichiers_json = _extraire_fichiers_json(texte)

        reponse = self.client.post("/projet/projet_distant/supprimer", data={
            "branches": ["feature-distant"],
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
            "origine_decision": "personnelle",
        })
        self.assertEqual(reponse.status_code, 302)

        lignes = self._lire_journal()
        self.assertEqual(len(lignes), 1)
        self.assertIn("projet=projet_distant", lignes[0])
        self.assertIn("branche=feature-distant", lignes[0])
        self.assertIn("taille=taille non calculée", lignes[0])
        self.assertIn("decision=supprimer", lignes[0])

    def _lire_journal(self):
        if not os.path.exists(self.chemin_journal):
            return []
        with open(self.chemin_journal, encoding="utf-8") as f:
            return [l for l in f.read().splitlines() if l.strip()]

    def _obtenir_confirmation(self, branches, route):
        reponse = self.client.post(route, data={"branches": branches})
        self.assertEqual(reponse.status_code, 200)
        return reponse.get_data(as_text=True)


if __name__ == "__main__":
    unittest.main()
