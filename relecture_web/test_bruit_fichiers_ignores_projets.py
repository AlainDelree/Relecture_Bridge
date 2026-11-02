#!/usr/bin/env python3
"""Tests du classement en bruit par projet sur
confirmation_fichiers_ignores_worktree.html (issue #119, suite de
#112/#116) — remplace le menu obligatoire « origine de la décision » et la
journalisation à l'annulation retirés par cette même issue (voir
test_decisions_fichiers_ignores_worktree.py pour ce qui reste inchangé) :

- une case « Classer comme bruit pour ce projet » par fichier/dossier
  listé dans la fenêtre de confirmation forte, décochée par défaut, jamais
  présélectionnée ;
- un chemin classé pour un projet masque ce chemin pour CE projet
  seulement (`git_info.lire_bruit_projets`, `_entree_ignoree_est_bruit`) —
  jamais par nom seul pour tous les projets ;
- un classement n'est accepté CÔTÉ SERVEUR que dans une requête qui porte
  la confirmation de suppression elle-même (`ignorer_avertissement_
  fichiers_ignores=on`, sans case « à garder » cochée) — jamais seul, et
  jamais si une case « à garder » bloque déjà la confirmation ;
- le fichier de stockage (`git_info.CHEMIN_LISTE_BRUIT_PROJETS`) est un
  fichier texte lisible à la main, une entrée par ligne, créé au premier
  ajout, dégradé vers la prudence (jamais de filtrage supplémentaire) si
  absent/illisible/mal formé ;
- un panneau sur la page projet liste les entrées et permet de les retirer
  sans confirmation (même esprit que le panneau .gitignore, issue #98) ;
- un projet distant (PC fixe CCW) utilise le même mécanisme, sans accès
  SSH ajouté ;
- les deux entrées initiales pour relecture_bridge lui-même
  (`relecture_web/secret_key.conf`, `relecture_web/changelog_fusion.log`)
  masquent bien les deux fichiers correspondants, pour ce projet
  seulement — sans dépendre du vrai fichier de ce dépôt, absent d'un
  nouveau worktree puisque non versionné (issue #121, constaté pendant
  #120).

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_bruit_fichiers_ignores_projets -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_bruit_fichiers_ignores_projets.py`.

Aucun accès réseau réel, aucune vraie commande ssh, et jamais le vrai
fichier de bruit d'Alain : `git_info.CHEMIN_LISTE_BRUIT_PROJETS` est
redirigée vers un fichier d'un dossier temporaire dans `setUp`/`tearDown`
de chaque cas, même pattern que les autres constantes de chemin de ce
module dans les tests précédents."""

import json
import os
import re
import shutil
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


class CheminTemporaireMixin:
    """Redirige CHEMIN_LISTE_BRUIT_PROJETS et CHEMIN_JOURNAL_DECISIONS_
    FICHIERS_IGNORES vers un dossier temporaire, restauré en fin de test —
    jamais le vrai fichier d'Alain."""

    def _preparer_chemins_temporaires(self, dossier):
        self.chemin_bruit = os.path.join(dossier, "bruit_projets.log")
        self._bruit_original = git_info.CHEMIN_LISTE_BRUIT_PROJETS
        git_info.CHEMIN_LISTE_BRUIT_PROJETS = self.chemin_bruit
        self.addCleanup(self._restaurer_bruit)

        self.chemin_journal = os.path.join(dossier, "decisions_fichiers_ignores.log")
        self._journal_original = git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES
        git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES = self.chemin_journal
        self.addCleanup(self._restaurer_journal)

    def _restaurer_bruit(self):
        git_info.CHEMIN_LISTE_BRUIT_PROJETS = self._bruit_original

    def _restaurer_journal(self):
        git_info.CHEMIN_JOURNAL_DECISIONS_FICHIERS_IGNORES = self._journal_original

    def _lire_journal(self):
        if not os.path.exists(self.chemin_journal):
            return []
        with open(self.chemin_journal, encoding="utf-8") as f:
            return [l for l in f.read().splitlines() if l.strip()]


class LireEtModifierBruitProjetsTestCase(CheminTemporaireMixin, unittest.TestCase):
    """Tests unitaires directs de `lire_bruit_projets`/`ajouter_bruit_
    projet`/`retirer_bruit_projet`, sans passer par Flask ni par git."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_bruit_unitaire_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self._preparer_chemins_temporaires(self.scratch)

    def test_fichier_absent_degrade_vers_dict_vide(self):
        self.assertFalse(os.path.exists(self.chemin_bruit))
        self.assertEqual(git_info.lire_bruit_projets(), {})

    def test_ajout_cree_le_fichier_et_relecture_le_confirme(self):
        self.assertTrue(git_info.ajouter_bruit_projet("mon_projet", "relecture_web/secret_key.conf"))
        self.assertTrue(os.path.exists(self.chemin_bruit))
        self.assertEqual(
            git_info.lire_bruit_projets(), {"mon_projet": {"relecture_web/secret_key.conf"}}
        )

    def test_ajout_ne_duplique_jamais_la_meme_entree(self):
        git_info.ajouter_bruit_projet("mon_projet", "cache/")
        git_info.ajouter_bruit_projet("mon_projet", "cache/")
        with open(self.chemin_bruit, encoding="utf-8") as f:
            lignes = [l for l in f.read().splitlines() if l.strip()]
        self.assertEqual(len(lignes), 1)

    def test_lignes_mal_formees_ignorees_une_par_une(self):
        with open(self.chemin_bruit, "w", encoding="utf-8") as f:
            f.write(
                "ceci n'est pas une ligne valide\n"
                "projet=mon_projet | chemin=cache/\n"
                "projet=sans_chemin_du_tout\n"
                "projet= | chemin=vide_cote_projet\n"
            )
        self.assertEqual(git_info.lire_bruit_projets(), {"mon_projet": {"cache/"}})

    def test_fichier_illisible_degrade_vers_dict_vide_jamais_une_exception(self):
        os.makedirs(self.chemin_bruit)  # un dossier à la place d'un fichier -> OSError à l'ouverture
        self.assertEqual(git_info.lire_bruit_projets(), {})

    def test_retirer_une_entree_absente_reste_sans_effet_et_ok(self):
        self.assertTrue(git_info.retirer_bruit_projet("mon_projet", "cache/"))
        self.assertEqual(git_info.lire_bruit_projets(), {})

    def test_ajout_puis_retrait_fait_disparaitre_lentree(self):
        git_info.ajouter_bruit_projet("mon_projet", "cache/")
        git_info.ajouter_bruit_projet("mon_projet", "installeur/output/")
        self.assertTrue(git_info.retirer_bruit_projet("mon_projet", "cache/"))
        self.assertEqual(
            git_info.lire_bruit_projets(), {"mon_projet": {"installeur/output/"}}
        )

    def test_retrait_ne_touche_pas_le_meme_chemin_dans_un_autre_projet(self):
        git_info.ajouter_bruit_projet("projet_a", "cache/")
        git_info.ajouter_bruit_projet("projet_b", "cache/")
        git_info.retirer_bruit_projet("projet_a", "cache/")
        self.assertEqual(git_info.lire_bruit_projets(), {"projet_b": {"cache/"}})


class MasquagePourProjetUniquementTestCase(CheminTemporaireMixin, unittest.TestCase):
    """`lister_fichiers_ignores_worktree(chemin, nom_projet)` ne masque un
    chemin que pour LE projet où il a été classé — jamais par nom seul
    pour tous les projets (un fichier de clé/journal du même nom ailleurs
    doit rester signalé)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_bruit_masquage_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self._preparer_chemins_temporaires(self.scratch)

        self.repertoire = os.path.join(self.scratch, "depot")
        _init_depot_git_local(self.repertoire)
        _ajouter_et_committer_gitignore(self.repertoire, ["secret_key.conf"])
        _creer_fichier(self.repertoire, "secret_key.conf")

    def test_chemin_classe_pour_ce_projet_est_masque(self):
        git_info.ajouter_bruit_projet("projet_a", "secret_key.conf")
        fichiers = git_info.lister_fichiers_ignores_worktree(self.repertoire, "projet_a")
        self.assertEqual(fichiers, [])

    def test_meme_chemin_toujours_signale_pour_un_autre_projet(self):
        git_info.ajouter_bruit_projet("projet_a", "secret_key.conf")
        fichiers = git_info.lister_fichiers_ignores_worktree(self.repertoire, "projet_b")
        self.assertEqual([f["chemin"] for f in fichiers], ["secret_key.conf"])

    def test_sans_nom_de_projet_rien_nest_masque_par_le_bruit_projet(self):
        git_info.ajouter_bruit_projet("projet_a", "secret_key.conf")
        fichiers = git_info.lister_fichiers_ignores_worktree(self.repertoire)
        self.assertEqual([f["chemin"] for f in fichiers], ["secret_key.conf"])


class BaseConfirmationTestCase(CheminTemporaireMixin, unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_bruit_confirmation_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self._preparer_chemins_temporaires(self.scratch)

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

    def _worktree_existe(self, chemin_worktree):
        return os.path.isdir(chemin_worktree)

    def _obtenir_confirmation(self, branches, route="/projet/projet_local/supprimer"):
        reponse = self.client.post(route, data={"branches": branches})
        self.assertEqual(reponse.status_code, 200)
        return reponse.get_data(as_text=True)

    def _preparer_worktree_avec_fichier_ignore(self, nom_branche="feature-build", motif="installeur/output/", fichier="installeur/output/app.exe"):
        worktree = self._creer_branche_worktree(nom_branche)
        # Le motif peut déjà être présent (hérité de main si un worktree
        # précédent l'a déjà committé puis fusionné) : un second ajout
        # identique n'aurait rien à committer.
        chemin_gitignore = os.path.join(worktree, ".gitignore")
        deja_present = False
        if os.path.exists(chemin_gitignore):
            with open(chemin_gitignore, encoding="utf-8") as f:
                deja_present = motif in f.read().splitlines()
        if not deja_present:
            _ajouter_et_committer_gitignore(worktree, [motif])
        _creer_fichier(worktree, fichier)
        self._fusionner_branche(nom_branche)
        return worktree


class ClassementDepuisConfirmationTestCase(BaseConfirmationTestCase):
    def test_case_cochee_classe_journalise_et_supprime(self):
        worktree = self._preparer_worktree_avec_fichier_ignore()
        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)
        chemin = json.loads(fichiers_json)[0]["chemin"]

        reponse = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build"],
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
            "bruit_chemins": json.dumps([chemin]),
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree))

        self.assertEqual(git_info.lire_bruit_projets(), {"projet_local": {chemin}})

        lignes = self._lire_journal()
        self.assertEqual(len(lignes), 2)
        self.assertTrue(any("decision=supprimer" in l for l in lignes))
        self.assertTrue(any("decision=bruit" in l for l in lignes))

    def test_case_decochee_ne_classe_rien(self):
        worktree = self._preparer_worktree_avec_fichier_ignore()
        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)

        reponse = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build"],
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
            # Pas de bruit_chemins du tout, comme une fenêtre validée sans
            # avoir coché aucune case.
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertFalse(self._worktree_existe(worktree))
        self.assertEqual(git_info.lire_bruit_projets(), {})

        lignes = self._lire_journal()
        self.assertEqual(len(lignes), 1)
        self.assertNotIn("decision=bruit", lignes[0])

    def test_classement_refuse_hors_requete_de_confirmation(self):
        """`bruit_chemins` posté SANS `ignorer_avertissement_fichiers_
        ignores=on` ne doit jamais classer quoi que ce soit — la route
        affiche alors simplement de nouveau la page d'avertissement,
        sans même regarder ce champ."""
        worktree = self._preparer_worktree_avec_fichier_ignore()
        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)
        chemin = json.loads(fichiers_json)[0]["chemin"]

        reponse = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build"],
            "fichiers_json": fichiers_json,
            "bruit_chemins": json.dumps([chemin]),
        })
        self.assertEqual(reponse.status_code, 200)  # ré-affiche la page d'avertissement
        self.assertEqual(git_info.lire_bruit_projets(), {})
        self.assertTrue(self._worktree_existe(worktree))

    def test_classement_refuse_si_case_a_garder_cochee(self):
        """Un classement demandé dans la MÊME requête qu'une case « à
        garder » cochée est refusé en bloc, comme la suppression
        elle-même — jamais l'un sans l'autre."""
        worktree = self._preparer_worktree_avec_fichier_ignore()
        texte = self._obtenir_confirmation(["feature-build"])
        fichiers_json = _extraire_fichiers_json(texte)
        chemin = json.loads(fichiers_json)[0]["chemin"]

        reponse = self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-build"],
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
            "garder": ["0"],
            "bruit_chemins": json.dumps([chemin]),
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(git_info.lire_bruit_projets(), {})
        self.assertTrue(self._worktree_existe(worktree))
        self.assertEqual(self._lire_journal(), [])

    def test_chemin_classe_masque_la_suppression_suivante(self):
        """Une fois classé, le même chemin ne déclenche plus la page
        d'avertissement pour un NOUVEAU worktree de ce projet."""
        self._preparer_worktree_avec_fichier_ignore("feature-un")
        texte = self._obtenir_confirmation(["feature-un"])
        fichiers_json = _extraire_fichiers_json(texte)
        chemin = json.loads(fichiers_json)[0]["chemin"]
        self.client.post("/projet/projet_local/supprimer", data={
            "branches": ["feature-un"],
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
            "bruit_chemins": json.dumps([chemin]),
        })

        self._preparer_worktree_avec_fichier_ignore("feature-deux")
        reponse = self.client.post("/projet/projet_local/supprimer", data={"branches": ["feature-deux"]})
        # Plus aucun fichier à signaler pour ce nouveau worktree -> pas de
        # page d'avertissement, la suppression a lieu directement (302).
        self.assertEqual(reponse.status_code, 302)


class PanneauBruitTestCase(BaseConfirmationTestCase):
    def test_panneau_vide_par_defaut(self):
        reponse = self.client.get("/projet/projet_local")
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        self.assertIn("Bruit ignoré pour ce projet", texte)
        self.assertIn("Aucune entrée classée comme bruit pour ce projet", texte)

    def test_panneau_liste_puis_retrait_fait_disparaitre_lentree(self):
        git_info.ajouter_bruit_projet("projet_local", "cache/")

        reponse = self.client.get("/projet/projet_local")
        texte = reponse.get_data(as_text=True)
        self.assertIn("cache/", texte)

        reponse = self.client.post(
            "/projet/projet_local/bruit-fichiers-ignores/retirer", data={"chemin": "cache/"},
        )
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(git_info.lire_bruit_projets(), {})

        texte_apres = self.client.get("/projet/projet_local").get_data(as_text=True)
        self.assertIn("Aucune entrée classée comme bruit pour ce projet", texte_apres)

    def test_retrait_sans_confirmation_prealable(self):
        """Pas de fenêtre de confirmation pour « Retirer » (contrairement
        au panneau .gitignore) : un simple POST suffit, aucun paramètre
        supplémentaire de confirmation n'est exigé côté serveur."""
        git_info.ajouter_bruit_projet("projet_local", "cache/")
        reponse = self.client.post(
            "/projet/projet_local/bruit-fichiers-ignores/retirer", data={"chemin": "cache/"},
            follow_redirects=True,
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(git_info.lire_bruit_projets(), {})


class ProjetDistantBruitTestCase(CheminTemporaireMixin, unittest.TestCase):
    """Même mécanisme de classement pour un projet distant (PC fixe CCW,
    issue #108/#109) : même clé de projet, aucun accès SSH ajouté — le
    classement en bruit ne touche jamais le filesystem distant, seulement
    le fichier local CHEMIN_LISTE_BRUIT_PROJETS."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_bruit_distant_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self._preparer_chemins_temporaires(self.scratch)

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

    def test_classement_sur_projet_distant_masque_puis_disparait_du_panneau(self):
        reponse = self.client.post("/projet/projet_distant/supprimer", data={"branches": ["feature-distant"]})
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        fichiers_json = _extraire_fichiers_json(texte)

        reponse = self.client.post("/projet/projet_distant/supprimer", data={
            "branches": ["feature-distant"],
            "ignorer_avertissement_fichiers_ignores": "on",
            "fichiers_json": fichiers_json,
            "bruit_chemins": json.dumps(["secret_key.conf"]),
        })
        self.assertEqual(reponse.status_code, 302)
        self.assertEqual(git_info.lire_bruit_projets(), {"projet_distant": {"secret_key.conf"}})

        # Panneau de la page projet : l'entrée apparaît, puis disparaît
        # après retrait — identique à un projet local.
        texte_projet = self.client.get("/projet/projet_distant").get_data(as_text=True)
        self.assertIn("secret_key.conf", texte_projet)

        self.client.post(
            "/projet/projet_distant/bruit-fichiers-ignores/retirer", data={"chemin": "secret_key.conf"},
        )
        self.assertEqual(git_info.lire_bruit_projets(), {})


class EntreesInitialesRelectureBridgeTestCase(CheminTemporaireMixin, unittest.TestCase):
    """Les deux entrées initiales demandées par l'issue #119 pour
    relecture_bridge lui-même (`relecture_web/secret_key.conf`,
    `relecture_web/changelog_fusion.log`) reviennent à chaque suppression
    d'un worktree de relecture_bridge et n'ont aucune valeur dans un
    worktree — mais ce test ne lit JAMAIS le vrai fichier de bruit d'Alain
    (`relecture_web/bruit_projets.log`, local, ignoré par git) : un nouveau
    worktree de ce dépôt ne le contient pas, ce qui faisait échouer ce
    test dans chaque worktree, sans lien avec le travail en cours (issue
    #121, constaté pendant #120). Le fichier est fabriqué ici dans un
    dossier temporaire, avec les deux mêmes entrées, via le même mécanisme
    de redirection (`CheminTemporaireMixin`) que les autres tests de ce
    module."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_bruit_entrees_initiales_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self._preparer_chemins_temporaires(self.scratch)

        git_info.ajouter_bruit_projet("relecture_bridge", "relecture_web/secret_key.conf")
        git_info.ajouter_bruit_projet("relecture_bridge", "relecture_web/changelog_fusion.log")

        self.repertoire = os.path.join(self.scratch, "depot")
        _init_depot_git_local(self.repertoire)
        # Un fichier suivi dans relecture_web/ (ex. app.py dans le vrai
        # dépôt) empêche git de réduire le dossier entier à son seul nom
        # dans `git status --ignored` : sans lui, les deux fichiers ignorés
        # ci-dessous seraient rapportés comme "relecture_web/" plutôt que
        # chacun par son propre chemin.
        _creer_fichier(self.repertoire, "relecture_web/app.py", contenu="suivi\n")
        subprocess.run(["git", "add", "relecture_web/app.py"], cwd=self.repertoire, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "ajoute relecture_web/"], cwd=self.repertoire, check=True)
        _ajouter_et_committer_gitignore(
            self.repertoire,
            ["relecture_web/secret_key.conf", "relecture_web/changelog_fusion.log"],
        )
        _creer_fichier(self.repertoire, "relecture_web/secret_key.conf")
        _creer_fichier(self.repertoire, "relecture_web/changelog_fusion.log")

    def test_deux_entrees_initiales_masquees_pour_relecture_bridge(self):
        fichiers = git_info.lister_fichiers_ignores_worktree(self.repertoire, "relecture_bridge")
        self.assertEqual(fichiers, [])

    def test_deux_entrees_initiales_toujours_signalees_pour_un_autre_projet(self):
        fichiers = git_info.lister_fichiers_ignores_worktree(self.repertoire, "autre_projet")
        self.assertEqual(
            sorted(f["chemin"] for f in fichiers),
            ["relecture_web/changelog_fusion.log", "relecture_web/secret_key.conf"],
        )

    def test_fichier_ignore_par_git(self):
        depot = tempfile.mkdtemp(prefix="relecture_bridge_test_gitignore_bruit_")
        try:
            subprocess.run(["git", "init", "--quiet"], cwd=depot, check=True)
            shutil.copy(os.path.join(RACINE_DEPOT, ".gitignore"), os.path.join(depot, ".gitignore"))
            resultat = subprocess.run(
                ["git", "check-ignore", "-q", "relecture_web/bruit_projets.log"], cwd=depot,
            )
            self.assertEqual(resultat.returncode, 0)
        finally:
            shutil.rmtree(depot, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
