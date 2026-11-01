#!/usr/bin/env python3
"""Tests de l'issue #118 : garde-fou avant toute fusion (« Merger » et
« Merger et supprimer ») si une issue Bridge_Agent travaille déjà dans le
dossier où le merge va réellement s'exécuter.

Réutilise le code d'analyse des verrous de l'issue #88/#89
(`git_info.lire_verrous_actifs`), étendu aux champs `projet=`/`mode=` :
- `git_info.lire_verrous_actifs` / `git_info.verrous_sur_dossier` sont
  couvertes directement (format multi-paires toléré, pid mort ignoré,
  comparaison par chemin réel) ;
- les routes `/projet/<nom>/merger` et `/projet/<nom>/merger-et-supprimer`
  sont couvertes via le client de test Flask, même pattern que
  `test_bouton_annuler_confirmation_suppression.py` /
  `test_refus_modifications_non_committees_noms_fichiers.py`.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_verrou_avant_fusion -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_verrou_avant_fusion.py`.

Aucun accès réseau réel : dépôts/worktrees locaux jetables créés dans un
dossier temporaire (même pattern que les autres fichiers de test de ce
dossier)."""

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


def _pid_mort():
    """PID garanti mort : lance un processus trivial, attend sa fin (donc
    déjà « reap » par `wait()`), puis renvoie son PID — aucun risque de
    collision avec un processus réellement vivant sur la machine de test."""
    processus = subprocess.Popen(["true"])
    processus.wait()
    return processus.pid


class GitInfoVerrousTestCase(unittest.TestCase):
    """Tests directs de `git_info.lire_verrous_actifs` et
    `git_info.verrous_sur_dossier`, sans passer par Flask."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_verrous_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self.dossier_bridge_agent = os.path.join(self.scratch, "bridge_agent")
        self.dossier_verrous = os.path.join(self.dossier_bridge_agent, "logs", "verrous")
        os.makedirs(self.dossier_verrous)

    def _ecrire_verrou(self, nom, contenu):
        with open(os.path.join(self.dossier_verrous, nom), "w", encoding="utf-8") as f:
            f.write(contenu)

    def test_pid_vivant_garde_projet_et_mode(self):
        self._ecrire_verrou(
            "a.lock",
            f"pid={os.getpid()} rep={self.scratch} projet=diagnostique_programme mode=lecture\n",
        )
        verrous = git_info.lire_verrous_actifs(self.dossier_bridge_agent)
        self.assertEqual(len(verrous), 1)
        self.assertEqual(verrous[0]["rep"], self.scratch)
        self.assertEqual(verrous[0]["projet"], "diagnostique_programme")
        self.assertEqual(verrous[0]["mode"], "lecture")

    def test_pid_mort_ignore(self):
        self._ecrire_verrou(
            "a.lock",
            f"pid={_pid_mort()} rep={self.scratch} projet=diagnostique_programme mode=ecriture\n",
        )
        self.assertEqual(git_info.lire_verrous_actifs(self.dossier_bridge_agent), [])

    def test_tolerance_format_multi_paires_sur_plusieurs_lignes(self):
        # Même tolérance que pour le badge #88/#89 : les paires peuvent être
        # réparties sur plusieurs lignes plutôt que toutes sur une seule.
        self._ecrire_verrou(
            "a.lock",
            f"pid={os.getpid()}\nrep={self.scratch}\nprojet=diagnostique_programme\nmode=lecture\n",
        )
        verrous = git_info.lire_verrous_actifs(self.dossier_bridge_agent)
        self.assertEqual(len(verrous), 1)
        self.assertEqual(verrous[0]["rep"], self.scratch)

    def test_dossier_verrous_absent_degrade_a_liste_vide(self):
        self.assertEqual(git_info.lire_verrous_actifs(os.path.join(self.scratch, "inexistant")), [])
        self.assertEqual(git_info.lire_verrous_actifs(None), [])

    def test_verrous_sur_dossier_filtre_par_chemin_reel(self):
        autre_dossier = os.path.join(self.scratch, "autre")
        os.makedirs(autre_dossier)
        self._ecrire_verrou("a.lock", f"pid={os.getpid()} rep={self.scratch} projet=p mode=lecture\n")
        self._ecrire_verrou("b.lock", f"pid={os.getpid()} rep={autre_dossier} projet=q mode=ecriture\n")
        verrous = git_info.lire_verrous_actifs(self.dossier_bridge_agent)

        concernes = git_info.verrous_sur_dossier(self.scratch, verrous)
        self.assertEqual(len(concernes), 1)
        self.assertEqual(concernes[0]["projet"], "p")

    def test_verrous_sur_dossier_vide_sans_chemin(self):
        self.assertEqual(git_info.verrous_sur_dossier(None, []), [])
        self.assertEqual(git_info.verrous_sur_dossier("", [{"rep": "/x"}]), [])


class BaseVerrouFusionTestCase(unittest.TestCase):
    """Harnais Flask commun : un projet local avec une branche à fusionner,
    et un projet « bridge_agent » (répertoire git minimal, jamais utilisé
    pour autre chose que localiser `logs/verrous/`) dont le dossier de
    verrous est peuplé par chaque test."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_verrou_fusion_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self.repertoire = os.path.join(self.scratch, "projet_local")
        _init_depot_git_local(self.repertoire)

        self.dossier_bridge_agent = os.path.join(self.scratch, "bridge_agent")
        _init_depot_git_local(self.dossier_bridge_agent)
        self.dossier_verrous = os.path.join(self.dossier_bridge_agent, "logs", "verrous")

        self.projets = [
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
            return self.projets

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

    def _branche_fusionnee(self, nom_branche):
        branche_principale = git_info.get_branche_courante(self.repertoire)
        resultat = subprocess.run(
            ["git", "merge-base", "--is-ancestor", nom_branche, branche_principale],
            cwd=self.repertoire,
        )
        return resultat.returncode == 0

    def _poster_merger(self, route, branches, donnees_supplementaires=None, follow_redirects=True):
        donnees = {"branches": branches}
        if donnees_supplementaires:
            donnees.update(donnees_supplementaires)
        return self.client.post(f"/projet/projet_local/{route}", data=donnees, follow_redirects=follow_redirects)


class VerrouSurDossierCibleBloqueTestCase(BaseVerrouFusionTestCase):
    """Scénario principal : verrou vivant sur le dossier principal du
    projet, qui est aussi le dossier cible du merge (branche cible sans
    worktree dédié — comportement normal pour `master`)."""

    def test_merger_bloque_et_nomme_projet_et_mode(self):
        self._creer_branche_worktree("feature-a")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "lecture",
        )

        reponse = self._poster_merger("merger", ["feature-a"], follow_redirects=False)
        self.assertEqual(reponse.status_code, 200)
        texte = reponse.get_data(as_text=True)
        self.assertIn("diagnostique_programme", texte)
        self.assertIn("lecture", texte)
        self.assertIn("Fusionner quand même", texte)

    def test_merger_bloque_ne_fusionne_rien(self):
        self._creer_branche_worktree("feature-a")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "ecriture",
        )

        self._poster_merger("merger", ["feature-a"], follow_redirects=False)
        self.assertFalse(self._branche_fusionnee("feature-a"))

    def test_merger_et_supprimer_bloque_aussi(self):
        chemin_worktree = self._creer_branche_worktree("feature-b")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "ecriture",
        )

        reponse = self._poster_merger("merger-et-supprimer", ["feature-b"], follow_redirects=False)
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("Fusionner quand même", reponse.get_data(as_text=True))
        self.assertFalse(self._branche_fusionnee("feature-b"))
        self.assertTrue(os.path.isdir(chemin_worktree))

    def test_mode_ecriture_affiche_un_badge_attention(self):
        self._creer_branche_worktree("feature-a")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "écriture",
        )
        texte = self._poster_merger("merger", ["feature-a"], follow_redirects=False).get_data(as_text=True)
        self.assertIn("badge--attention", texte)


class PidMortIgnoreTestCase(BaseVerrouFusionTestCase):
    def test_merger_procede_si_le_pid_du_verrou_est_mort(self):
        self._creer_branche_worktree("feature-a")
        self._ecrire_verrou(
            "x.lock", _pid_mort(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "ecriture",
        )

        texte = self._poster_merger("merger", ["feature-a"]).get_data(as_text=True)
        self.assertIn("fusionnée dans", texte)
        self.assertTrue(self._branche_fusionnee("feature-a"))


class VerrouSurAutreWorktreeTestCase(BaseVerrouFusionTestCase):
    """Un verrou actif sur le worktree d'UNE AUTRE issue du même projet ne
    doit déclencher aucun avertissement : fusionner la branche sélectionnée
    (vers `master`, sans worktree dédié) n'a aucun rapport avec le dossier
    de cette autre issue."""

    def test_aucun_avertissement_pour_le_worktree_dune_autre_issue(self):
        self._creer_branche_worktree("feature-a")
        chemin_autre_worktree = self._creer_branche_worktree("feature-autre-issue")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(chemin_autre_worktree),
            "diagnostique_programme", "ecriture",
        )

        texte = self._poster_merger("merger", ["feature-a"]).get_data(as_text=True)
        self.assertIn("fusionnée dans", texte)
        self.assertNotIn("Fusionner quand même", texte)
        self.assertTrue(self._branche_fusionnee("feature-a"))


class DossierVerrousAbsentTestCase(BaseVerrouFusionTestCase):
    def test_aucun_avertissement_si_bridge_agent_absent_du_tableau(self):
        self._creer_branche_worktree("feature-a")
        self.projets = [p for p in self.projets if p["nom"] != "bridge_agent"]

        texte = self._poster_merger("merger", ["feature-a"]).get_data(as_text=True)
        self.assertIn("fusionnée dans", texte)
        self.assertTrue(self._branche_fusionnee("feature-a"))

    def test_aucun_avertissement_si_dossier_logs_verrous_inexistant(self):
        # dossier_verrous jamais créé par ce test (contrairement aux autres,
        # qui l'instancient via _ecrire_verrou) — dégradation silencieuse.
        self._creer_branche_worktree("feature-a")
        self.assertFalse(os.path.isdir(self.dossier_verrous))

        texte = self._poster_merger("merger", ["feature-a"]).get_data(as_text=True)
        self.assertIn("fusionnée dans", texte)
        self.assertTrue(self._branche_fusionnee("feature-a"))


class ContournementTestCase(BaseVerrouFusionTestCase):
    def test_contournement_confirme_laisse_fusionner_malgre_le_verrou(self):
        self._creer_branche_worktree("feature-a")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "ecriture",
        )

        texte = self._poster_merger(
            "merger", ["feature-a"], donnees_supplementaires={"forcer_malgre_verrou": "on"},
        ).get_data(as_text=True)
        self.assertIn("fusionnée dans", texte)
        self.assertTrue(self._branche_fusionnee("feature-a"))

    def test_contournement_non_confirme_reste_bloque(self):
        self._creer_branche_worktree("feature-a")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "ecriture",
        )

        # Champ absent du formulaire (valeur par défaut d'un navigateur sans
        # ce champ cocher) : toujours bloqué, jamais un contournement implicite.
        reponse = self._poster_merger("merger", ["feature-a"], follow_redirects=False)
        self.assertEqual(reponse.status_code, 200)
        self.assertIn("Fusionner quand même", reponse.get_data(as_text=True))
        self.assertFalse(self._branche_fusionnee("feature-a"))

    def test_contournement_ne_survit_pas_a_une_requete_suivante(self):
        # Même leçon que la case « Purger » (issue #102) : le contournement
        # n'est accepté que pour la requête qui le porte explicitement — une
        # seconde action sur une AUTRE branche, sans le champ cette fois,
        # doit retrouver le même avertissement si le verrou est toujours actif.
        self._creer_branche_worktree("feature-a")
        self._creer_branche_worktree("feature-b")
        self._ecrire_verrou(
            "x.lock", os.getpid(), os.path.realpath(self.repertoire),
            "diagnostique_programme", "ecriture",
        )

        self._poster_merger("merger", ["feature-a"], donnees_supplementaires={"forcer_malgre_verrou": "on"})
        self.assertTrue(self._branche_fusionnee("feature-a"))

        reponse = self._poster_merger("merger", ["feature-b"], follow_redirects=False)
        self.assertIn("Fusionner quand même", reponse.get_data(as_text=True))
        self.assertFalse(self._branche_fusionnee("feature-b"))


if __name__ == "__main__":
    unittest.main()
