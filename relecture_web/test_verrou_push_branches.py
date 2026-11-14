#!/usr/bin/env python3
"""Tests de l'issue #134 : verrou de push par branche (cadenas, verrouillé
par défaut) sur la page « branches d'un projet ».

Couvre :
- `git_info.lire_autorisations_push`/`autoriser_push_branche`/
  `verrouiller_push_branche` : fichier absent -> toutes les branches
  verrouillées (y compris la branche principale), ajout/retrait, pas de
  doublon, ligne mal formée ignorée seule (sans faire échouer les lignes
  voisines), fichier illisible dégradé vers « tout verrouillé », écriture
  impossible toujours signalée par un retour False sans jamais faire
  croire à un changement d'état réel ;
- `git_info.nettoyer_autorisations_push_disparues` : ne retire que les
  branches disparues DU PROJET CONCERNÉ, jamais celles d'un autre projet
  ni celles encore présentes ;
- refus serveur de `app.pousser_branches_route` : une seule branche
  verrouillée dans la sélection -> rien n'est poussé (tout ou rien, même
  les branches déverrouillées de la même sélection), pour un projet SANS
  crochet pre-push comme pour un projet ÉQUIPÉ (le garde-fou est placé
  avant la séparation entre push synchrone et push en arrière-plan) ;
- `app.basculer_verrou_push_route` : bascule verrouillée <-> autorisée
  sans toucher aux autres branches ni aux autres projets, branche
  introuvable signalée sans planter ;
- nettoyage automatique de l'autorisation à la disparition d'une branche :
  suppression confirmée fusionnée (`supprimer_worktrees_route`) et
  affichage de la page projet pour une branche disparue par un autre
  moyen (terminal, autre session).

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_verrou_push_branches -v` depuis la
racine du dépôt, ou directement
`python3 relecture_web/test_verrou_push_branches.py`.

Aucun accès réseau réel, et jamais le vrai fichier d'Alain :
`git_info.CHEMIN_AUTORISATIONS_PUSH` est redirigée vers un fichier d'un
dossier temporaire dans `setUp`/`tearDown` de chaque cas, même pattern que
les autres constantes de chemin de ce dépôt (voir
`test_bruit_fichiers_ignores_projets.py`)."""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module  # noqa: E402  (après l'ajustement de sys.path ci-dessus)
import git_info  # noqa: E402
import push_arriere_plan  # noqa: E402


def _init_depot_avec_remote(chemin_local, chemin_remote):
    os.makedirs(chemin_remote, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "--bare", chemin_remote], check=True)
    os.makedirs(chemin_local, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "-b", "main", chemin_local], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=chemin_local, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=chemin_local, check=True)
    with open(os.path.join(chemin_local, "fichier.txt"), "w", encoding="utf-8") as f:
        f.write("contenu\n")
    subprocess.run(["git", "add", "fichier.txt"], cwd=chemin_local, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", "initial"], cwd=chemin_local, check=True)
    subprocess.run(["git", "remote", "add", "origin", chemin_remote], cwd=chemin_local, check=True)
    subprocess.run(["git", "push", "--quiet", "origin", "main"], cwd=chemin_local, check=True)


def _creer_branche(chemin_local, nom):
    subprocess.run(["git", "checkout", "-b", nom], cwd=chemin_local, check=True, capture_output=True)
    with open(os.path.join(chemin_local, f"{nom}.txt"), "w", encoding="utf-8") as f:
        f.write(f"contenu {nom}\n")
    subprocess.run(["git", "add", f"{nom}.txt"], cwd=chemin_local, check=True)
    subprocess.run(["git", "commit", "--quiet", "-m", f"commit {nom}"], cwd=chemin_local, check=True)
    subprocess.run(["git", "checkout", "main"], cwd=chemin_local, check=True, capture_output=True)


def _hash_distant(chemin_remote, branche):
    resultat = subprocess.run(
        ["git", "ls-remote", chemin_remote, f"refs/heads/{branche}"],
        capture_output=True, text=True, check=True,
    )
    ligne = resultat.stdout.strip()
    return ligne.split()[0] if ligne else None


def _installer_hook_pre_push(chemin_local):
    chemin_hook = git_info.chemin_hook_pre_push(chemin_local)
    os.makedirs(os.path.dirname(chemin_hook), exist_ok=True)
    with open(chemin_hook, "w", encoding="utf-8") as f:
        f.write("#!/bin/sh\nexit 0\n")
    os.chmod(chemin_hook, 0o755)


class CheminTemporaireMixin:
    """Redirige CHEMIN_AUTORISATIONS_PUSH vers un fichier temporaire,
    restauré en fin de test — jamais le vrai fichier d'Alain."""

    def _preparer_chemin_autorisations(self, dossier):
        self.chemin_autorisations = os.path.join(dossier, "autorisations_push.log")
        self._autorisations_original = git_info.CHEMIN_AUTORISATIONS_PUSH
        git_info.CHEMIN_AUTORISATIONS_PUSH = self.chemin_autorisations
        self.addCleanup(self._restaurer_autorisations)

    def _restaurer_autorisations(self):
        git_info.CHEMIN_AUTORISATIONS_PUSH = self._autorisations_original


class LireEtModifierAutorisationsPushTestCase(CheminTemporaireMixin, unittest.TestCase):
    """Tests unitaires directs de `lire_autorisations_push`/`autoriser_
    push_branche`/`verrouiller_push_branche`/`nettoyer_autorisations_push_
    disparues`, sans passer par Flask ni par un vrai dépôt git."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_verrou_push_unitaire_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self._preparer_chemin_autorisations(self.scratch)

    def test_fichier_absent_degrade_vers_tout_verrouille(self):
        self.assertFalse(os.path.exists(self.chemin_autorisations))
        self.assertEqual(git_info.lire_autorisations_push(), {})
        self.assertFalse(git_info.branche_push_autorisee("mon_projet", "main"))

    def test_autorisation_cree_le_fichier_et_relecture_le_confirme(self):
        self.assertTrue(git_info.autoriser_push_branche("mon_projet", "feature-a"))
        self.assertTrue(os.path.exists(self.chemin_autorisations))
        self.assertEqual(git_info.lire_autorisations_push(), {"mon_projet": {"feature-a"}})
        self.assertTrue(git_info.branche_push_autorisee("mon_projet", "feature-a"))

    def test_autorisation_ne_duplique_jamais_la_meme_entree(self):
        git_info.autoriser_push_branche("mon_projet", "feature-a")
        git_info.autoriser_push_branche("mon_projet", "feature-a")
        with open(self.chemin_autorisations, encoding="utf-8") as f:
            lignes = [l for l in f.read().splitlines() if l.strip()]
        self.assertEqual(len(lignes), 1)

    def test_lignes_mal_formees_ignorees_une_par_une(self):
        with open(self.chemin_autorisations, "w", encoding="utf-8") as f:
            f.write(
                "ceci n'est pas une ligne valide\n"
                "projet=mon_projet | branche=feature-a\n"
                "projet=sans_branche_du_tout\n"
                "projet= | branche=vide_cote_projet\n"
            )
        self.assertEqual(git_info.lire_autorisations_push(), {"mon_projet": {"feature-a"}})

    def test_fichier_illisible_degrade_vers_tout_verrouille_jamais_une_exception(self):
        os.makedirs(self.chemin_autorisations)  # un dossier à la place d'un fichier -> OSError à l'ouverture
        self.assertEqual(git_info.lire_autorisations_push(), {})
        self.assertFalse(git_info.branche_push_autorisee("mon_projet", "feature-a"))

    def test_branche_principale_verrouillee_par_defaut_comme_les_autres(self):
        git_info.autoriser_push_branche("mon_projet", "feature-a")
        self.assertFalse(git_info.branche_push_autorisee("mon_projet", "main"))

    def test_verrouiller_une_entree_absente_reste_sans_effet_et_ok(self):
        self.assertTrue(git_info.verrouiller_push_branche("mon_projet", "feature-a"))
        self.assertEqual(git_info.lire_autorisations_push(), {})

    def test_autorisation_puis_verrou_fait_disparaitre_lentree(self):
        git_info.autoriser_push_branche("mon_projet", "feature-a")
        git_info.autoriser_push_branche("mon_projet", "feature-b")
        self.assertTrue(git_info.verrouiller_push_branche("mon_projet", "feature-a"))
        self.assertEqual(git_info.lire_autorisations_push(), {"mon_projet": {"feature-b"}})

    def test_verrou_ne_touche_pas_la_meme_branche_dans_un_autre_projet(self):
        git_info.autoriser_push_branche("projet_a", "feature-a")
        git_info.autoriser_push_branche("projet_b", "feature-a")
        git_info.verrouiller_push_branche("projet_a", "feature-a")
        self.assertEqual(git_info.lire_autorisations_push(), {"projet_b": {"feature-a"}})

    def test_nettoyage_retire_seulement_les_branches_disparues_du_bon_projet(self):
        git_info.autoriser_push_branche("projet_a", "feature-encore-la")
        git_info.autoriser_push_branche("projet_a", "feature-disparue")
        git_info.autoriser_push_branche("projet_b", "feature-disparue")
        self.assertTrue(
            git_info.nettoyer_autorisations_push_disparues("projet_a", {"feature-encore-la"})
        )
        self.assertEqual(
            git_info.lire_autorisations_push(),
            {"projet_a": {"feature-encore-la"}, "projet_b": {"feature-disparue"}},
        )

    def test_nettoyage_sans_rien_a_retirer_reste_ok(self):
        git_info.autoriser_push_branche("projet_a", "feature-a")
        self.assertTrue(git_info.nettoyer_autorisations_push_disparues("projet_a", {"feature-a"}))
        self.assertEqual(git_info.lire_autorisations_push(), {"projet_a": {"feature-a"}})


class EcritureImpossibleTestCase(unittest.TestCase):
    """Une écriture impossible (dossier en lecture seule, disque plein) ne
    doit JAMAIS faire croire à un changement d'état — False renvoyé, état
    affiché inchangé (issue #134, point 4)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_verrou_push_ecriture_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self.dossier_lecture_seule = os.path.join(self.scratch, "dossier_lecture_seule")
        os.makedirs(self.dossier_lecture_seule, exist_ok=True)
        self.chemin_autorisations = os.path.join(self.dossier_lecture_seule, "autorisations_push.log")
        self._autorisations_original = git_info.CHEMIN_AUTORISATIONS_PUSH
        git_info.CHEMIN_AUTORISATIONS_PUSH = self.chemin_autorisations
        self.addCleanup(self._restaurer_autorisations)

    def _restaurer_autorisations(self):
        os.chmod(self.dossier_lecture_seule, stat.S_IRWXU)
        if os.path.exists(self.chemin_autorisations):
            os.chmod(self.chemin_autorisations, stat.S_IRUSR | stat.S_IWUSR)
        git_info.CHEMIN_AUTORISATIONS_PUSH = self._autorisations_original

    def test_deverrouillage_impossible_reste_verrouille(self):
        # Création impossible (champ nouveau, le fichier n'existe pas encore) :
        # retrait du droit d'écriture sur le DOSSIER lui-même (la création
        # d'une nouvelle entrée de répertoire exige ce droit, contrairement à
        # la réécriture d'un fichier déjà existant, voir le test suivant).
        os.chmod(self.dossier_lecture_seule, stat.S_IRUSR | stat.S_IXUSR)
        self.assertFalse(git_info.autoriser_push_branche("mon_projet", "feature-a"))
        os.chmod(self.dossier_lecture_seule, stat.S_IRWXU)
        self.assertFalse(git_info.branche_push_autorisee("mon_projet", "feature-a"))

    def test_reverrouillage_impossible_reste_autorise(self):
        git_info.autoriser_push_branche("mon_projet", "feature-a")  # dossier encore inscriptible ici
        # Réécriture impossible (le fichier existe déjà) : retrait du droit
        # d'écriture sur le FICHIER lui-même — le dossier reste, lui,
        # inscriptible (réécrire le contenu d'un fichier existant n'exige
        # aucun droit particulier sur le dossier qui le contient).
        os.chmod(self.chemin_autorisations, stat.S_IRUSR)
        self.assertFalse(git_info.verrouiller_push_branche("mon_projet", "feature-a"))
        os.chmod(self.chemin_autorisations, stat.S_IRUSR | stat.S_IWUSR)
        self.assertTrue(git_info.branche_push_autorisee("mon_projet", "feature-a"))


class BasePushVerrouTestCase(unittest.TestCase):
    """Harnais Flask commun : un projet local avec remote bare jetable,
    autorisations de push ET état du push en arrière-plan redirigés vers
    des fichiers temporaires (jamais les vrais fichiers de relecture_web)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_verrou_push_flask_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self._autorisations_original = git_info.CHEMIN_AUTORISATIONS_PUSH
        git_info.CHEMIN_AUTORISATIONS_PUSH = os.path.join(self.scratch, "autorisations_push.log")
        self.addCleanup(self._restaurer_autorisations)

        self._chemin_etat_original = push_arriere_plan.CHEMIN_ETAT_PUSH
        push_arriere_plan.CHEMIN_ETAT_PUSH = os.path.join(self.scratch, "push_etat.json")
        self.addCleanup(self._restaurer_chemin_etat)

        self.repertoire = os.path.join(self.scratch, "projet_local")
        self.remote = os.path.join(self.scratch, "projet_local_remote.git")
        _init_depot_avec_remote(self.repertoire, self.remote)

        self.projets = [
            {
                "nom": "projet_local", "depot": "projet_local", "repertoire": self.repertoire,
                "couleur": None, "couleur_texte": None,
            },
        ]
        self._fetch_original = git_info.fetch_projets
        git_info.fetch_projets = lambda: self.projets
        self.addCleanup(self._restaurer_fetch)

        app_module.app.config["TESTING"] = True
        app_module.app.config["MDP_EXIGE"] = False
        self.client = app_module.app.test_client()

    def _restaurer_autorisations(self):
        git_info.CHEMIN_AUTORISATIONS_PUSH = self._autorisations_original

    def _restaurer_chemin_etat(self):
        push_arriere_plan.CHEMIN_ETAT_PUSH = self._chemin_etat_original

    def _restaurer_fetch(self):
        git_info.fetch_projets = self._fetch_original

    def _poster_push(self, branches, nom_projet="projet_local", follow_redirects=True):
        return self.client.post(
            f"/projet/{nom_projet}/pousser", data={"branches": branches}, follow_redirects=follow_redirects,
        )


class RefusServeurBrancheVerrouilleeTestCase(BasePushVerrouTestCase):
    """`app.pousser_branches_route` refuse une sélection contenant une
    branche verrouillée, indépendamment de l'affichage côté template
    (issue #134, point 3)."""

    def test_push_refuse_quand_branche_verrouillee_par_defaut(self):
        _creer_branche(self.repertoire, "feature-a")
        reponse = self._poster_push(["feature-a"])
        self.assertIn("verrouillée", reponse.get_data(as_text=True))
        self.assertIsNone(_hash_distant(self.remote, "feature-a"))

    def test_push_autorise_apres_deverrouillage(self):
        _creer_branche(self.repertoire, "feature-a")
        git_info.autoriser_push_branche("projet_local", "feature-a")
        reponse = self._poster_push(["feature-a"])
        self.assertIn("poussée", reponse.get_data(as_text=True))
        self.assertIsNotNone(_hash_distant(self.remote, "feature-a"))

    def test_refus_tout_ou_rien_une_seule_branche_verrouillee_parmi_plusieurs(self):
        _creer_branche(self.repertoire, "feature-a")
        _creer_branche(self.repertoire, "feature-b")
        git_info.autoriser_push_branche("projet_local", "feature-a")
        # feature-b reste verrouillée.
        reponse = self._poster_push(["feature-a", "feature-b"])
        texte = reponse.get_data(as_text=True)
        self.assertIn("feature-b", texte)
        self.assertIn("verrouillée", texte)
        # Tout ou rien : feature-a, pourtant déverrouillée, n'est pas poussée non plus.
        self.assertIsNone(_hash_distant(self.remote, "feature-a"))
        self.assertIsNone(_hash_distant(self.remote, "feature-b"))

    def test_refus_vaut_aussi_pour_un_projet_equipe_dun_crochet_pre_push(self):
        _installer_hook_pre_push(self.repertoire)
        _creer_branche(self.repertoire, "feature-a")
        self.assertTrue(git_info.projet_equipe_hook_pre_push(self.repertoire))

        reponse = self._poster_push(["feature-a"])
        self.assertIn("verrouillée", reponse.get_data(as_text=True))
        self.assertIsNone(_hash_distant(self.remote, "feature-a"))
        # Jamais entré dans le chemin push en arrière-plan : aucune entrée d'état écrite.
        self.assertIsNone(push_arriere_plan.lire_entree("projet_local"))


class BasculerVerrouPushRouteTestCase(BasePushVerrouTestCase):
    """`app.basculer_verrou_push_route` (cadenas de la page projet)."""

    def test_bascule_verrouillee_vers_autorisee_puis_retour(self):
        _creer_branche(self.repertoire, "feature-a")
        self.assertFalse(git_info.branche_push_autorisee("projet_local", "feature-a"))

        reponse = self.client.post(
            "/projet/projet_local/branche/feature-a/verrou-push", follow_redirects=True,
        )
        self.assertIn("déverrouillée", reponse.get_data(as_text=True))
        self.assertTrue(git_info.branche_push_autorisee("projet_local", "feature-a"))

        reponse = self.client.post(
            "/projet/projet_local/branche/feature-a/verrou-push", follow_redirects=True,
        )
        self.assertIn("verrouillée", reponse.get_data(as_text=True))
        self.assertFalse(git_info.branche_push_autorisee("projet_local", "feature-a"))

    def test_branche_introuvable_signalee_sans_planter(self):
        reponse = self.client.post(
            "/projet/projet_local/branche/branche-inexistante/verrou-push", follow_redirects=True,
        )
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("introuvable", reponse.get_data(as_text=True))

    def test_bascule_ne_touche_pas_les_autres_branches(self):
        _creer_branche(self.repertoire, "feature-a")
        _creer_branche(self.repertoire, "feature-b")
        git_info.autoriser_push_branche("projet_local", "feature-b")

        self.client.post("/projet/projet_local/branche/feature-a/verrou-push")

        self.assertTrue(git_info.branche_push_autorisee("projet_local", "feature-a"))
        self.assertTrue(git_info.branche_push_autorisee("projet_local", "feature-b"))


class NettoyageSuppressionBrancheTestCase(BasePushVerrouTestCase):
    """Nettoyage automatique de l'autorisation à la disparition d'une
    branche (issue #134, point 5)."""

    def test_autorisation_retiree_quand_branche_fusionnee_supprimee(self):
        worktree = os.path.join(self.scratch, "worktree_feature-a")
        subprocess.run(
            ["git", "worktree", "add", "-b", "feature-a", worktree], cwd=self.repertoire, check=True,
        )
        with open(os.path.join(worktree, "feature-a.txt"), "w", encoding="utf-8") as f:
            f.write("contenu\n")
        subprocess.run(["git", "add", "feature-a.txt"], cwd=worktree, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", "commit feature-a"], cwd=worktree, check=True)
        subprocess.run(["git", "merge", "--quiet", "feature-a"], cwd=self.repertoire, check=True)

        git_info.autoriser_push_branche("projet_local", "feature-a")
        self.assertTrue(git_info.branche_push_autorisee("projet_local", "feature-a"))

        reponse = self.client.post(
            "/projet/projet_local/supprimer", data={"branches": ["feature-a"]}, follow_redirects=True,
        )
        self.assertIn("supprimé", reponse.get_data(as_text=True))
        self.assertFalse(git_info.branche_push_autorisee("projet_local", "feature-a"))
        self.assertEqual(git_info.lire_autorisations_push(), {})

    def test_affichage_page_projet_nettoie_une_branche_disparue_hors_relecture_web(self):
        _creer_branche(self.repertoire, "feature-ephemere")
        git_info.autoriser_push_branche("projet_local", "feature-ephemere")
        # Disparue « en terminal », hors de toute action de relecture_web
        # (limite documentée de l'issue #134 : aucun crochet git concerné).
        subprocess.run(["git", "branch", "-D", "feature-ephemere"], cwd=self.repertoire, check=True)

        self.client.get("/projet/projet_local")

        self.assertFalse(git_info.branche_push_autorisee("projet_local", "feature-ephemere"))
        self.assertEqual(git_info.lire_autorisations_push(), {})


if __name__ == "__main__":
    unittest.main()
