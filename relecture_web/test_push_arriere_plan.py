#!/usr/bin/env python3
"""Tests de l'issue #122 : push en arrière-plan pour les projets équipés
d'un crochet `pre-push` (moteur `push_arriere_plan.py`, détection du
crochet dans `git_info.py`, verrou par projet et affichage sur la page
projet dans `app.py`/`projet.html`).

Couvre :
- `git_info.chemin_hook_pre_push`/`projet_equipe_hook_pre_push` : crochet
  présent, absent, non exécutable, `core.hooksPath` personnalisé, worktree
  (hérite du crochet du dépôt principal), projet distant (jamais équipé,
  aucun accès réseau).
- Projet NON équipé : comportement synchrone strictement inchangé, aucune
  entrée d'état écrite.
- Projet équipé : un seul `git push` pour plusieurs branches (le crochet
  ne tourne qu'une fois — vérifié en comptant ses invocations réelles),
  verrou par projet (second push refusé, une autre action git refusée,
  un AUTRE projet reste libre), dépassement du délai (process group tué,
  revérification par branche), redémarrage avec une entrée « en_cours »
  devenue « interrompu », fichier d'état absent/corrompu, et acquittement
  (« Vu ») d'un refus.

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_push_arriere_plan -v` depuis la
racine du dépôt, ou directement `python3 relecture_web/test_push_arriere_plan.py`.

Aucun accès réseau réel, et aucune lecture/écriture des vrais fichiers
locaux de relecture_web : dépôts/remotes/état jetables créés dans un
dossier temporaire par test (même pattern que les autres fichiers de ce
dossier) — `push_arriere_plan.CHEMIN_ETAT_PUSH` est redirigé vers un
fichier temporaire pour toute la durée de chaque test."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
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


def _installer_hook_pre_push(chemin_local, script_texte, executable=True):
    chemin_hook = git_info.chemin_hook_pre_push(chemin_local)
    os.makedirs(os.path.dirname(chemin_hook), exist_ok=True)
    with open(chemin_hook, "w", encoding="utf-8") as f:
        f.write(script_texte)
    if executable:
        os.chmod(chemin_hook, 0o755)
    return chemin_hook


def _hash_distant(chemin_remote, branche):
    resultat = subprocess.run(
        ["git", "ls-remote", chemin_remote, f"refs/heads/{branche}"],
        capture_output=True, text=True, check=True,
    )
    ligne = resultat.stdout.strip()
    return ligne.split()[0] if ligne else None


def _hash_local(chemin_local, branche):
    resultat = subprocess.run(
        ["git", "rev-parse", f"refs/heads/{branche}"],
        cwd=chemin_local, capture_output=True, text=True, check=True,
    )
    return resultat.stdout.strip()


def _pid_mort():
    """PID garanti mort (même pattern que test_verrou_avant_fusion.py) :
    lance un processus trivial, attend sa fin (déjà « reap » par wait()),
    renvoie son pid — aucun risque de collision avec un processus vivant."""
    processus = subprocess.Popen(["true"])
    processus.wait()
    return processus.pid


def _processus_toujours_actif(pid):
    """True si `pid` est un processus Linux encore réellement actif — pas
    seulement présent dans la table des processus : un zombie (déjà tué,
    pas encore « reap » par son parent) ne compte PAS comme actif ici,
    contrairement à un simple `os.kill(pid, 0)` qui réussirait encore pour
    lui. Utilisé pour vérifier qu'un groupe de processus tué par
    `os.killpg` (issue #122) a bien cessé de tourner, même si son reap
    final par un processus tiers (init...) peut prendre un instant."""
    try:
        with open(f"/proc/{pid}/stat", encoding="utf-8") as f:
            contenu = f.read()
    except OSError:
        return False
    etat = contenu.rsplit(")", 1)[-1].split()[0]
    return etat != "Z"


class EtatGlobalTestCase(unittest.TestCase):
    """Tests directs de `push_arriere_plan._etat_global`, sans aucun
    process ni fichier — la logique de décision pure."""

    def test_tue_par_timeout_toujours_interrompu(self):
        resultats = {"a": {"ok": True}}
        self.assertEqual(push_arriere_plan._etat_global(True, 0, resultats), "interrompu")

    def test_toutes_branches_poussees_code_zero(self):
        resultats = {"a": {"ok": True}, "b": {"ok": True}}
        self.assertEqual(push_arriere_plan._etat_global(False, 0, resultats), "pousse")

    def test_une_branche_non_aboutie_donne_refuse(self):
        resultats = {"a": {"ok": True}, "b": {"ok": False}}
        self.assertEqual(push_arriere_plan._etat_global(False, 1, resultats), "refuse")

    def test_aucune_branche_determinee_donne_indetermine(self):
        resultats = {"a": {"ok": None}}
        self.assertEqual(push_arriere_plan._etat_global(False, 0, resultats), "indetermine")

    def test_resultats_vide_donne_indetermine(self):
        self.assertEqual(push_arriere_plan._etat_global(False, 0, {}), "indetermine")


class DetectionHookPrePushTestCase(unittest.TestCase):
    """`git_info.chemin_hook_pre_push`/`projet_equipe_hook_pre_push`."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_hook_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)
        self.repertoire = os.path.join(self.scratch, "depot")
        os.makedirs(self.repertoire)
        subprocess.run(["git", "init", "--quiet", "-b", "main", self.repertoire], check=True)
        subprocess.run(["git", "config", "user.email", "t@e.com"], cwd=self.repertoire, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.repertoire, check=True)
        subprocess.run(["git", "commit", "--quiet", "--allow-empty", "-m", "init"], cwd=self.repertoire, check=True)

    def test_hook_absent(self):
        self.assertFalse(git_info.projet_equipe_hook_pre_push(self.repertoire))
        chemin = git_info.chemin_hook_pre_push(self.repertoire)
        self.assertTrue(chemin.endswith(os.path.join(".git", "hooks", "pre-push")))

    def test_hook_present_et_executable(self):
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 0\n")
        self.assertTrue(git_info.projet_equipe_hook_pre_push(self.repertoire))

    def test_hook_present_mais_non_executable(self):
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 0\n", executable=False)
        self.assertFalse(git_info.projet_equipe_hook_pre_push(self.repertoire))

    def test_core_hooks_path_personnalise(self):
        dossier_hooks = os.path.join(self.scratch, "hooks_perso")
        subprocess.run(
            ["git", "config", "core.hooksPath", dossier_hooks], cwd=self.repertoire, check=True,
        )
        os.makedirs(dossier_hooks)
        chemin_hook = os.path.join(dossier_hooks, "pre-push")
        with open(chemin_hook, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\nexit 0\n")
        os.chmod(chemin_hook, 0o755)

        self.assertEqual(
            os.path.realpath(git_info.chemin_hook_pre_push(self.repertoire)),
            os.path.realpath(chemin_hook),
        )
        self.assertTrue(git_info.projet_equipe_hook_pre_push(self.repertoire))

    def test_worktree_herite_du_crochet_du_depot_principal(self):
        chemin_worktree = os.path.join(self.scratch, "worktree_wt1")
        subprocess.run(
            ["git", "worktree", "add", "-b", "wt1", chemin_worktree],
            cwd=self.repertoire, check=True, capture_output=True,
        )
        self.assertFalse(git_info.projet_equipe_hook_pre_push(chemin_worktree))

        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 0\n")
        self.assertTrue(git_info.projet_equipe_hook_pre_push(chemin_worktree))

    def test_projet_distant_jamais_equipe(self):
        chemin_windows = r"C:\CCW\projet_fictif"
        self.assertTrue(git_info.est_projet_distant(chemin_windows))
        self.assertIsNone(git_info.chemin_hook_pre_push(chemin_windows))
        self.assertFalse(git_info.projet_equipe_hook_pre_push(chemin_windows))


class BasePushTestCase(unittest.TestCase):
    """Harnais Flask commun : un projet local avec remote bare jetable,
    état du push redirigé vers un fichier temporaire (jamais le vrai
    `push_arriere_plan_etat.json` de relecture_web)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_push_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self._chemin_etat_original = push_arriere_plan.CHEMIN_ETAT_PUSH
        push_arriere_plan.CHEMIN_ETAT_PUSH = os.path.join(self.scratch, "push_etat.json")
        self.addCleanup(self._restaurer_chemin_etat)

        self._timeout_original = push_arriere_plan.TIMEOUT_PUSH_ARRIERE_PLAN
        self.addCleanup(self._restaurer_timeout)

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

    def _restaurer_chemin_etat(self):
        push_arriere_plan.CHEMIN_ETAT_PUSH = self._chemin_etat_original

    def _restaurer_timeout(self):
        push_arriere_plan.TIMEOUT_PUSH_ARRIERE_PLAN = self._timeout_original

    def _restaurer_fetch(self):
        git_info.fetch_projets = self._fetch_original

    def _poster_push(self, branches, nom_projet="projet_local", follow_redirects=True):
        return self.client.post(
            f"/projet/{nom_projet}/pousser", data={"branches": branches}, follow_redirects=follow_redirects,
        )

    def _attendre_fin_push(self, nom_projet="projet_local", timeout=5.0):
        fin = time.time() + timeout
        while time.time() < fin:
            entree = push_arriere_plan.lire_entree(nom_projet)
            if entree and entree.get("etat") != "en_cours":
                return entree
            time.sleep(0.03)
        raise AssertionError("le push en arrière-plan ne s'est pas terminé à temps")


class ProjetNonEquipeInchangeTestCase(BasePushTestCase):
    """Un projet SANS crochet pre-push garde le comportement synchrone
    d'avant l'issue #122 : aucune entrée d'état écrite, push normal."""

    def test_push_synchrone_sans_entree_detat(self):
        _creer_branche(self.repertoire, "feature-a")
        reponse = self._poster_push(["feature-a"])
        self.assertIn("poussée", reponse.get_data(as_text=True))
        self.assertEqual(_hash_distant(self.remote, "feature-a"), _hash_local(self.repertoire, "feature-a"))
        self.assertIsNone(push_arriere_plan.lire_entree("projet_local"))


class PushArrierePlanEquipeTestCase(BasePushTestCase):
    """Projet équipé d'un crochet pre-push trivial (toujours accepté) —
    un seul `git push` pour plusieurs branches."""

    def setUp(self):
        super().setUp()
        self.compteur_invocations = os.path.join(self.scratch, "compteur_hook.txt")
        _installer_hook_pre_push(
            self.repertoire,
            f"#!/bin/sh\necho invocation >> {self.compteur_invocations}\nexit 0\n",
        )

    def test_un_seul_push_pour_plusieurs_branches(self):
        _creer_branche(self.repertoire, "feature-a")
        _creer_branche(self.repertoire, "feature-b")

        reponse = self._poster_push(["feature-a", "feature-b"])
        self.assertIn("arrière-plan", reponse.get_data(as_text=True))

        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "pousse")
        self.assertEqual(set(entree["branches"]), {"feature-a", "feature-b"})
        self.assertEqual(_hash_distant(self.remote, "feature-a"), _hash_local(self.repertoire, "feature-a"))
        self.assertEqual(_hash_distant(self.remote, "feature-b"), _hash_local(self.repertoire, "feature-b"))

        with open(self.compteur_invocations, encoding="utf-8") as f:
            lignes = [l for l in f.read().splitlines() if l.strip()]
        self.assertEqual(len(lignes), 1, "le crochet pre-push n'a dû tourner qu'une seule fois")


class VerrouParProjetTestCase(BasePushTestCase):
    """Issue #122, point 3 : un seul push à la fois par projet, projet
    verrouillé pendant ce temps pour les autres actions git."""

    def setUp(self):
        super().setUp()
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nsleep 1\nexit 0\n")
        _creer_branche(self.repertoire, "feature-a")
        _creer_branche(self.repertoire, "feature-b")

    def test_second_push_refuse_pendant_le_premier(self):
        self._poster_push(["feature-a"], follow_redirects=False)
        # L'entrée « en_cours » est écrite de façon synchrone, avant même le
        # retour de la requête — pas besoin d'attendre pour tenter le second.
        self.assertTrue(push_arriere_plan.projet_verrouille_par_push("projet_local"))

        reponse = self._poster_push(["feature-b"])
        self.assertIn("Push en cours", reponse.get_data(as_text=True))

        self._attendre_fin_push()
        self.assertEqual(_hash_distant(self.remote, "feature-a"), _hash_local(self.repertoire, "feature-a"))
        self.assertIsNone(_hash_distant(self.remote, "feature-b"))

    def test_autre_action_git_refusee_pendant_le_push(self):
        self._poster_push(["feature-a"], follow_redirects=False)
        self.assertTrue(push_arriere_plan.projet_verrouille_par_push("projet_local"))

        reponse = self.client.post(
            "/projet/projet_local/merger", data={"branches": ["feature-b"]}, follow_redirects=True,
        )
        self.assertIn("Push en cours", reponse.get_data(as_text=True))

        self._attendre_fin_push()
        merge_base = subprocess.run(
            ["git", "merge-base", "--is-ancestor", "feature-b", "main"],
            cwd=self.repertoire,
        )
        self.assertNotEqual(merge_base.returncode, 0, "feature-b n'aurait jamais dû être fusionnée")

    def test_autre_projet_reste_libre_pendant_le_push(self):
        repertoire_autre = os.path.join(self.scratch, "projet_autre")
        remote_autre = os.path.join(self.scratch, "projet_autre_remote.git")
        _init_depot_avec_remote(repertoire_autre, remote_autre)
        _creer_branche(repertoire_autre, "feature-c")
        self.projets.append({
            "nom": "projet_autre", "depot": "projet_autre", "repertoire": repertoire_autre,
            "couleur": None, "couleur_texte": None,
        })

        self._poster_push(["feature-a"], follow_redirects=False)
        self.assertTrue(push_arriere_plan.projet_verrouille_par_push("projet_local"))

        reponse = self.client.post(
            "/projet/projet_autre/merger", data={"branches": ["feature-c"]}, follow_redirects=True,
        )
        self.assertIn("fusionnée dans", reponse.get_data(as_text=True))

        self._attendre_fin_push()


class DepassementDelaiTestCase(BasePushTestCase):
    """Issue #122, point 2 : dépassement du délai propre au push en
    arrière-plan -> tout le groupe de processus est tué (pas seulement
    git), puis l'état réel est revérifié branche par branche."""

    def test_timeout_tue_le_groupe_et_revérifie(self):
        push_arriere_plan.TIMEOUT_PUSH_ARRIERE_PLAN = 0.4
        chemin_pid_enfant = os.path.join(self.scratch, "pid_enfant.txt")
        _installer_hook_pre_push(
            self.repertoire,
            "#!/bin/sh\n"
            "sleep 30 &\n"
            f"echo $! > {chemin_pid_enfant}\n"
            "wait\n",
        )
        _creer_branche(self.repertoire, "feature-a")

        debut = time.time()
        demarre, avertissement = push_arriere_plan.demarrer_push_arriere_plan(
            self.repertoire, "projet_local", ["feature-a"],
        )
        self.assertTrue(demarre)
        self.assertIsNone(avertissement)

        entree = self._attendre_fin_push(timeout=10.0)
        duree = time.time() - debut
        self.assertLess(duree, 10.0, "le push aurait dû être interrompu bien avant les 30s du sommeil du crochet")
        self.assertEqual(entree["etat"], "interrompu")
        self.assertFalse(entree["resultats"]["feature-a"]["ok"])

        fin = time.time() + 3.0
        pid_enfant = None
        while time.time() < fin and pid_enfant is None:
            if os.path.exists(chemin_pid_enfant):
                with open(chemin_pid_enfant, encoding="utf-8") as f:
                    contenu = f.read().strip()
                if contenu:
                    pid_enfant = int(contenu)
            time.sleep(0.05)
        self.assertIsNotNone(pid_enfant, "le crochet n'a jamais écrit le pid de son enfant")
        self.assertFalse(
            _processus_toujours_actif(pid_enfant),
            "l'enfant du crochet (même groupe de processus) devrait avoir été tué avec git",
        )


class RedemarrageTestCase(BasePushTestCase):
    """Issue #122, point 4 : au démarrage de relecture_web, une entrée
    « en_cours » dont plus rien ne tourne est marquée « interrompu » puis
    revérifiée par `git ls-remote`."""

    def test_entree_en_cours_devient_interrompue_et_revérifiée(self):
        _creer_branche(self.repertoire, "feature-a")
        subprocess.run(["git", "push", "--quiet", "origin", "feature-a"], cwd=self.repertoire, check=True)

        push_arriere_plan.ecrire_entree(
            "projet_local", etat="en_cours", branches=["feature-a"], repertoire=self.repertoire,
            debut="2026-01-01T00:00:00", fin=None, sortie="", vu=False, pid=_pid_mort(), resultats={},
        )

        push_arriere_plan.reconcilier_au_demarrage()

        entree = push_arriere_plan.lire_entree("projet_local")
        self.assertEqual(entree["etat"], "interrompu")
        self.assertIsNotNone(entree["fin"])
        self.assertIsNone(entree["pid"])
        self.assertTrue(entree["resultats"]["feature-a"]["ok"], "le push avait réellement abouti avant le redémarrage")

    def test_entree_en_cours_avec_pid_vivant_nest_pas_touchee(self):
        push_arriere_plan.ecrire_entree(
            "projet_local", etat="en_cours", branches=["feature-a"], repertoire=self.repertoire,
            debut="2026-01-01T00:00:00", fin=None, sortie="", vu=False, pid=os.getpid(), resultats={},
        )

        push_arriere_plan.reconcilier_au_demarrage()

        entree = push_arriere_plan.lire_entree("projet_local")
        self.assertEqual(entree["etat"], "en_cours")

    def test_aucune_entree_en_cours_ne_fait_rien(self):
        push_arriere_plan.reconcilier_au_demarrage()
        self.assertIsNone(push_arriere_plan.lire_entree("projet_local"))


class FichierEtatAbsentOuCorrompuTestCase(BasePushTestCase):
    def test_fichier_absent_degrade_a_aucune_entree(self):
        self.assertFalse(os.path.exists(push_arriere_plan.CHEMIN_ETAT_PUSH))
        self.assertIsNone(push_arriere_plan.lire_entree("projet_local"))
        self.assertFalse(push_arriere_plan.projet_verrouille_par_push("projet_local"))

    def test_fichier_corrompu_degrade_a_aucune_entree(self):
        with open(push_arriere_plan.CHEMIN_ETAT_PUSH, "w", encoding="utf-8") as f:
            f.write("{ceci n'est pas du json valide")
        self.assertIsNone(push_arriere_plan.lire_entree("projet_local"))

    def test_fichier_json_valide_mais_pas_un_objet(self):
        with open(push_arriere_plan.CHEMIN_ETAT_PUSH, "w", encoding="utf-8") as f:
            f.write("[1, 2, 3]")
        self.assertIsNone(push_arriere_plan.lire_entree("projet_local"))

    def test_push_fonctionne_malgre_un_fichier_detat_corrompu_au_depart(self):
        with open(push_arriere_plan.CHEMIN_ETAT_PUSH, "w", encoding="utf-8") as f:
            f.write("du texte quelconque, pas du json")
        _installer_hook_pre_push(self.repertoire, "#!/bin/sh\nexit 0\n")
        _creer_branche(self.repertoire, "feature-a")

        self._poster_push(["feature-a"])
        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "pousse")


class AcquittementVuTestCase(BasePushTestCase):
    """Issue #122, point 5 : pour un refus, la fin de la sortie des tests
    reste affichée jusqu'à ce qu'Alain clique sur « Vu »."""

    def setUp(self):
        super().setUp()
        _installer_hook_pre_push(
            self.repertoire,
            "#!/bin/sh\necho ÉCHEC_TEST_FACTICE 1>&2\nexit 1\n",
        )
        _creer_branche(self.repertoire, "feature-a")

    def test_vu_acquitte_un_refus_sans_changer_letat(self):
        self._poster_push(["feature-a"])
        entree = self._attendre_fin_push()
        self.assertEqual(entree["etat"], "refuse")
        self.assertFalse(entree["vu"])
        self.assertIn("ÉCHEC_TEST_FACTICE", entree["sortie"])
        self.assertIsNone(_hash_distant(self.remote, "feature-a"))

        self.client.post("/projet/projet_local/push/vu")

        entree_apres = push_arriere_plan.lire_entree("projet_local")
        self.assertEqual(entree_apres["etat"], "refuse")
        self.assertTrue(entree_apres["vu"])


if __name__ == "__main__":
    unittest.main()
