#!/usr/bin/env python3
"""Tests du bouton « Fusionner le changelog » pour un projet distant (PC fixe
CCW, issue #114, suite du refus explicite de #108) :

- `git_info.detecter_changelogs_a_fusionner` : aucun/un/plusieurs
  `CHANGELOG-<N>.md` à la racine du commit HEAD ;
- `git_info.fusionner_changelog_distant` de bout en bout, avec un FAUX `ssh`
  et un FAUX `scp` (scripts shell posés en tête du PATH, jamais de réseau
  réel) qui exécutent RÉELLEMENT la commande reçue sur un dépôt git jetable
  local jouant le rôle du clone Windows (PC fixe CCW) — `python` et
  `scripts/fusionner_changelog.py` sont les vrais, aucun n'est simulé :
  un seul `CHANGELOG-<N>.md`, plusieurs, aucun, fins de ligne LF/CRLF/mixte
  (commit limité aux lignes ajoutées, convention du fichier conservée),
  branche non principale, autres modifications présentes, python absent,
  script en échec à mi-chemin, nettoyage systématique de la copie
  temporaire ;
- `git_info.fusionner_changelog_worktree` : ne signale plus un projet
  distant comme « à fusionner » quand aucun `CHANGELOG-<N>.md` n'est
  réellement présent (avant l'issue #114, ce refus était inconditionnel).

Pas de framework de test externe dans ce dépôt (voir #107) : fichier
`unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_fusion_changelog_distant -v` depuis
la racine du dépôt, ou directement
`python3 relecture_web/test_fusion_changelog_distant.py`."""

import os
import shutil
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import git_info  # noqa: E402  (après l'ajustement de sys.path ci-dessus)


RACINE_DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Faux `ssh` (issue #114) : reçoit `-i <cle> -o ... -o ... -o ... <host>
# "<commande distante>"` — le dernier argument est TOUJOURS la commande
# distante complète (une seule chaîne, jamais enchaînée par `&&`, voir
# `_commande_ssh_ccw`/`_lancer_git_distant`). `FAUX_SSH_CODE`/
# `FAUX_SSH_STDERR` (même mécanisme que test_diagnostic_echec_ssh_ccw.py)
# permettent de simuler un échec SSH (code 255) sans jamais l'exécuter.
# Sinon, substitue le préfixe Windows commun (`C:\\CCW`, voir
# `FAUX_CCW_PREFIX_WINDOWS`) par la racine du dépôt jetable local
# (`FAUX_CCW_ROOT_REEL`) partout dans la commande, découpe la commande en
# arguments (`shlex.split(..., posix=False)` : préserve les antislashs tels
# quels, contrairement à un `bash -c` qui les interpréterait comme des
# échappements — un chemin Windows non protégé par des guillemets,
# `_quoter_argument_distant` ne le fait que s'il contient un espace, s'en
# retrouverait tronqué), puis l'exécute RÉELLEMENT (git, python... tous
# réels), jamais via un sous-shell."""
FAUX_SSH = textwrap.dedent("""\
    #!/usr/bin/env python3
    import os
    import shlex
    import subprocess
    import sys

    code = os.environ.get("FAUX_SSH_CODE")
    if code and code != "0":
        stderr = os.environ.get("FAUX_SSH_STDERR", "")
        if stderr:
            sys.stderr.write(stderr)
        sys.exit(int(code))

    commande = sys.argv[-1]
    commande = commande.replace(os.environ["FAUX_CCW_PREFIX_WINDOWS"], os.environ["FAUX_CCW_ROOT_REEL"])
    commande = commande.replace(chr(92), "/")
    tokens = shlex.split(commande, posix=False)
    tokens = [t[1:-1] if len(t) >= 2 and t[0] == t[-1] == '"' else t for t in tokens]
    sys.exit(subprocess.run(tokens).returncode)
""")

# Faux `scp` (issue #114) : reçoit `-i <cle> -o ... -o ... -o ... <source
# locale> <host>:<destination distante>` — copie réellement `<source
# locale>` vers la destination, une fois le préfixe Windows substitué de la
# même façon que le faux ssh.
FAUX_SCP = textwrap.dedent("""\
    #!/usr/bin/env python3
    import os
    import shutil
    import sys

    code = os.environ.get("FAUX_SCP_CODE")
    if code and code != "0":
        stderr = os.environ.get("FAUX_SCP_STDERR", "")
        if stderr:
            sys.stderr.write(stderr)
        sys.exit(int(code))

    local_src = sys.argv[-2]
    dest = sys.argv[-1]
    remote_path = dest.split(":", 1)[1]
    remote_path = remote_path.replace(os.environ["FAUX_CCW_PREFIX_WINDOWS"], os.environ["FAUX_CCW_ROOT_REEL"])
    remote_path = remote_path.replace(chr(92), "/")
    os.makedirs(os.path.dirname(remote_path), exist_ok=True)
    shutil.copyfile(local_src, remote_path)
""")

# Faux lanceur Windows « py » (issue #114) : simple relais vers le vrai
# interpréteur Python du système, pour les tests du repli « py » (quand
# « python » seul n'est pas trouvé) — jamais un faux interpréteur, le script
# de fusion réel tourne derrière.
FAUX_PY = "#!/bin/bash\nexec {python} \"$@\"\n"


def _ecrire_executable(chemin, contenu):
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write(contenu)
    st = os.stat(chemin)
    os.chmod(chemin, st.st_mode | stat.S_IEXEC)


class DepotDistantSimuleTestCase(unittest.TestCase):
    """Base commune : un dépôt git jetable (`self.depot`) joue le rôle du
    clone Windows du PC fixe CCW, accessible sous
    `self.repertoire_windows` (« C:\\CCW\\testproj ») via le faux ssh/scp.
    `git_info.CHEMIN_CONFIG_CCW` est redirigée vers un fichier temporaire
    (jamais le vrai `ccw_host.conf` du dépôt, même principe que
    test_ccw_host_conf.py)."""

    def setUp(self):
        self.scratch = tempfile.mkdtemp(prefix="relecture_bridge_test_fusion_changelog_")
        self.addCleanup(shutil.rmtree, self.scratch, ignore_errors=True)

        self.ccw_root_reel = os.path.join(self.scratch, "ccw_root_reel")
        self.depot = os.path.join(self.ccw_root_reel, "testproj")
        os.makedirs(self.depot)
        subprocess.run(["git", "init", "--quiet"], cwd=self.depot, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.depot, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.depot, check=True)

        self.repertoire_windows = "C:\\CCW\\testproj"
        self.prefixe_windows = "C:\\CCW"

        bin_factice = os.path.join(self.scratch, "bin_factice")
        os.makedirs(bin_factice)
        _ecrire_executable(os.path.join(bin_factice, "ssh"), FAUX_SSH)
        _ecrire_executable(os.path.join(bin_factice, "scp"), FAUX_SCP)

        bin_python = os.path.join(self.scratch, "bin_python")
        os.makedirs(bin_python)
        _ecrire_executable(os.path.join(bin_python, "python"), FAUX_PY.format(python=sys.executable))

        self._path_original = os.environ.get("PATH", "")
        os.environ["PATH"] = os.pathsep.join([bin_factice, bin_python, "/usr/bin", "/bin"])
        os.environ["FAUX_CCW_PREFIX_WINDOWS"] = self.prefixe_windows
        os.environ["FAUX_CCW_ROOT_REEL"] = self.ccw_root_reel
        self.addCleanup(self._restaurer_env)

        self._config_original = git_info.CHEMIN_CONFIG_CCW
        self.chemin_config = os.path.join(self.scratch, "ccw_host.conf")
        with open(self.chemin_config, "w", encoding="utf-8") as fichier:
            fichier.write("ccw_host = test@192.0.2.1\nccw_key = /chemin/factice/cle\n")
        git_info.CHEMIN_CONFIG_CCW = self.chemin_config
        self.addCleanup(self._restaurer_config)

    def _restaurer_env(self):
        os.environ["PATH"] = self._path_original
        for cle in (
            "FAUX_SSH_CODE", "FAUX_SSH_STDERR", "FAUX_SCP_CODE", "FAUX_SCP_STDERR",
            "FAUX_CCW_PREFIX_WINDOWS", "FAUX_CCW_ROOT_REEL",
        ):
            os.environ.pop(cle, None)

    def _restaurer_config(self):
        git_info.CHEMIN_CONFIG_CCW = self._config_original

    def _enlever_python_du_path(self):
        # Retire le dossier bin_python (seul endroit où « python »/« py »
        # pourrait exister) — simule un PC fixe sans aucun interpréteur.
        morceaux = [m for m in os.environ["PATH"].split(os.pathsep) if "bin_python" not in m]
        os.environ["PATH"] = os.pathsep.join(morceaux)

    def _ajouter_repli_py(self):
        # Ajoute un « py » (sans « python ») en tête de PATH, pour tester le
        # repli (issue #114, point c).
        self._enlever_python_du_path()
        bin_py = os.path.join(self.scratch, "bin_py_repli")
        os.makedirs(bin_py, exist_ok=True)
        _ecrire_executable(os.path.join(bin_py, "py"), FAUX_PY.format(python=sys.executable))
        os.environ["PATH"] = bin_py + os.pathsep + os.environ["PATH"]

    def _ecrire(self, nom_relatif, contenu):
        with open(os.path.join(self.depot, nom_relatif), "w", encoding="utf-8", newline="") as fichier:
            fichier.write(contenu)

    def _lire_brut(self, nom_relatif):
        with open(os.path.join(self.depot, nom_relatif), "rb") as fichier:
            return fichier.read()

    def _commit(self, message, *chemins):
        subprocess.run(["git", "add", "--"] + list(chemins), cwd=self.depot, check=True)
        subprocess.run(["git", "commit", "--quiet", "-m", message], cwd=self.depot, check=True)

    def _branche_courante(self):
        return git_info.get_branche_courante(self.depot)

    def _log_fichiers_dernier_commit(self):
        resultat = subprocess.run(
            ["git", "show", "--name-only", "--pretty=format:", "HEAD"],
            cwd=self.depot, capture_output=True, text=True, check=True,
        )
        return sorted(l for l in resultat.stdout.splitlines() if l.strip())


class DetecterChangelogsATestCase(DepotDistantSimuleTestCase):
    """`detecter_changelogs_a_fusionner` — passe par git (routé en SSH pour
    un chemin Windows), jamais par le filesystem local."""

    def test_aucun(self):
        self._ecrire("CHANGELOG.md", "# CHANGELOG\n")
        self._commit("initial", "CHANGELOG.md")
        self.assertEqual(git_info.detecter_changelogs_a_fusionner(self.repertoire_windows), [])

    def test_un_seul(self):
        self._ecrire("CHANGELOG.md", "# CHANGELOG\n")
        self._ecrire("CHANGELOG-42.md", "## entree\n")
        self._commit("initial", "CHANGELOG.md", "CHANGELOG-42.md")
        self.assertEqual(
            git_info.detecter_changelogs_a_fusionner(self.repertoire_windows), [(42, "CHANGELOG-42.md")],
        )

    def test_plusieurs_tries_decroissant(self):
        self._ecrire("CHANGELOG.md", "# CHANGELOG\n")
        self._ecrire("CHANGELOG-10.md", "## a\n")
        self._ecrire("CHANGELOG-99.md", "## b\n")
        self._commit("initial", "CHANGELOG.md", "CHANGELOG-10.md", "CHANGELOG-99.md")
        self.assertEqual(
            git_info.detecter_changelogs_a_fusionner(self.repertoire_windows),
            [(99, "CHANGELOG-99.md"), (10, "CHANGELOG-10.md")],
        )

    def test_ignore_les_chemins_non_racine(self):
        self._ecrire("CHANGELOG.md", "# CHANGELOG\n")
        os.makedirs(os.path.join(self.depot, "sous_dossier"), exist_ok=True)
        self._ecrire("sous_dossier/CHANGELOG-5.md", "## x\n")
        self._commit("initial", "CHANGELOG.md", "sous_dossier/CHANGELOG-5.md")
        self.assertEqual(git_info.detecter_changelogs_a_fusionner(self.repertoire_windows), [])


class FusionnerChangelogDistantTestCase(DepotDistantSimuleTestCase):
    """`fusionner_changelog_distant` de bout en bout."""

    def _preparer(self, contenu_changelog, extensions):
        self._ecrire("CHANGELOG.md", contenu_changelog)
        chemins = ["CHANGELOG.md"]
        for n, texte in extensions.items():
            self._ecrire(f"CHANGELOG-{n}.md", texte)
            chemins.append(f"CHANGELOG-{n}.md")
        self._commit("initial", *chemins)

    def test_un_seul_changelog_succes(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {42: "## nouveau\n- b\n"})
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        self.assertEqual([n for n, _ in resultat["traites"]], [42])
        self.assertTrue(resultat["derniers_commits"])
        self.assertFalse(os.path.exists(os.path.join(self.depot, "CHANGELOG-42.md")))
        contenu = self._lire_brut("CHANGELOG.md").decode("utf-8")
        self.assertIn("## nouveau", contenu)
        self.assertIn("## ancien", contenu)
        # Commit limité à CHANGELOG.md (la suppression de CHANGELOG-42.md
        # apparaît aussi, c'est le même commit).
        self.assertEqual(self._log_fichiers_dernier_commit(), ["CHANGELOG-42.md", "CHANGELOG.md"])

    def test_plusieurs_changelogs_succes(self):
        self._preparer(
            "# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n",
            {10: "## dix\n- x\n", 20: "## vingt\n- y\n"},
        )
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        self.assertEqual(sorted(n for n, _ in resultat["traites"]), [10, 20])
        self.assertEqual(
            self._log_fichiers_dernier_commit(),
            ["CHANGELOG-10.md", "CHANGELOG-20.md", "CHANGELOG.md"],
        )
        resultat_message = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"], cwd=self.depot, capture_output=True, text=True, check=True,
        ).stdout.strip()
        self.assertEqual(resultat_message, "chore: fusionne CHANGELOG-<N>.md dans CHANGELOG.md (auto)")

    def test_aucun_changelog_refuse(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {})
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertFalse(resultat["ok"])
        self.assertIn("aucun CHANGELOG", resultat["erreur"])

    def test_fins_de_ligne_lf_preservees(self):
        self._preparer(
            "# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- ligne ancienne LF\n", {7: "## nouveau\n- x\n"},
        )
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        data = self._lire_brut("CHANGELOG.md")
        self.assertNotIn(b"\r\n", data)
        self.assertIn(b"- ligne ancienne LF", data)
        self.assertIn(b"## nouveau", data)

    def test_fins_de_ligne_crlf_preservees(self):
        self._preparer(
            "# CHANGELOG\r\n\r\nConvention d'ajout : x.\r\n\r\n## ancien\r\n- ligne ancienne CRLF\r\n",
            {7: "## nouveau\n- entree en LF a la source\n"},
        )
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        data = self._lire_brut("CHANGELOG.md")
        # Chaque \n doit faire partie d'un \r\n — aucune ligne (ancienne ou
        # nouvelle) n'est restée/devenue un simple LF isolé.
        self.assertTrue(all(data[i - 1:i + 1] == b"\r\n" for i in range(len(data)) if data[i:i + 1] == b"\n"))
        self.assertIn(b"- ligne ancienne CRLF", data)
        self.assertIn(b"## nouveau", data)

    def test_fins_de_ligne_mixte_conservees_sauf_ajout(self):
        # Fichier cible mixte (dominante CRLF, une ligne isolée en LF) :
        # l'ajout (source LF) doit se conformer à la dominante CRLF ; le
        # contenu déjà présent (en-tête, puis bloc « ## ancien », inchangé
        # par construction puisque l'insertion a lieu juste après l'en-tête)
        # ne doit pas bouger d'un octet.
        en_tete = "# CHANGELOG\r\n\r\nConvention d'ajout : x.\r\n\r\n"
        ancien = "## ancien\r\n- a\n- b\r\n"
        self._ecrire("CHANGELOG.md", en_tete + ancien)
        self._ecrire("CHANGELOG-9.md", "## nouveau\n- c\n")
        self._commit("initial", "CHANGELOG.md", "CHANGELOG-9.md")

        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        apres = self._lire_brut("CHANGELOG.md")
        self.assertTrue(apres.startswith(en_tete.encode("utf-8")))
        self.assertTrue(apres.endswith(ancien.encode("utf-8")))
        self.assertIn(b"## nouveau\r\n- c\r\n", apres)

    def test_branche_non_principale_refusee(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {1: "## x\n- y\n"})
        branche_principale = self._branche_courante()
        subprocess.run(["git", "checkout", "-b", "autre-branche"], cwd=self.depot, check=True, capture_output=True)
        # `branches_cibles` configuré explicitement pour ce projet (comme un
        # vrai `branches_cibles.conf`) : sans ça, `get_branche_cible_
        # comparaison` retombe par défaut sur la branche ACTUELLEMENT
        # extraite (voir sa docstring), rendant la vérification tautologique
        # pour un projet sans configuration explicite — seule une HEAD
        # détachée serait alors détectée, pas un changement de branche.
        resultat = git_info.fusionner_changelog_distant(
            self.repertoire_windows, "testproj", branches_cibles={"testproj": branche_principale},
        )
        self.assertFalse(resultat["ok"])
        self.assertIn("branche principale", resultat["erreur"])
        # Rien n'a été modifié : toujours sur l'autre branche, CHANGELOG-1.md
        # toujours présent.
        self.assertEqual(self._branche_courante(), "autre-branche")
        self.assertTrue(os.path.exists(os.path.join(self.depot, "CHANGELOG-1.md")))
        self.assertNotEqual(branche_principale, "autre-branche")

    def test_autres_modifications_refusees(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {1: "## x\n- y\n"})
        with open(os.path.join(self.depot, "autre_fichier.txt"), "w", encoding="utf-8") as fichier:
            fichier.write("travail en cours non lié au changelog\n")
        subprocess.run(["git", "add", "autre_fichier.txt"], cwd=self.depot, check=True)
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertFalse(resultat["ok"])
        self.assertIn("autre_fichier.txt", resultat["erreur"])
        self.assertTrue(os.path.exists(os.path.join(self.depot, "CHANGELOG-1.md")))

    def test_python_absent_erreur_explicite_rien_modifie(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {1: "## x\n- y\n"})
        self._enlever_python_du_path()
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertFalse(resultat["ok"])
        self.assertIn("interpréteur Python", resultat["erreur"])
        self.assertTrue(os.path.exists(os.path.join(self.depot, "CHANGELOG-1.md")))
        self.assertFalse(
            os.path.exists(os.path.join(self.ccw_root_reel, "_relecture_bridge_tmp_fusion_changelog"))
        )

    def test_repli_py_quand_python_absent(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {1: "## x\n- y\n"})
        self._ajouter_repli_py()
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))

    def test_script_en_echec_rien_committe(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {1: "## x\n- y\n"})
        chemin_original = git_info.CHEMIN_SCRIPT_FUSION_CHANGELOG
        git_info.CHEMIN_SCRIPT_FUSION_CHANGELOG = os.path.join(self.scratch, "script_introuvable.py")
        try:
            resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        finally:
            git_info.CHEMIN_SCRIPT_FUSION_CHANGELOG = chemin_original
        self.assertFalse(resultat["ok"])
        self.assertIn("échoué", resultat["erreur"])
        # Rien n'a été ajouté à l'index ni committé.
        resultat_status = subprocess.run(
            ["git", "status", "--porcelain=v1"], cwd=self.depot, capture_output=True, text=True, check=True,
        )
        self.assertEqual(resultat_status.stdout.strip(), "")
        self.assertTrue(os.path.exists(os.path.join(self.depot, "CHANGELOG-1.md")))

    def test_nettoyage_copie_temporaire_apres_succes(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {1: "## x\n- y\n"})
        git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        chemin_copie = os.path.join(
            self.ccw_root_reel, "_relecture_bridge_tmp_fusion_changelog", "fusionner_changelog.py",
        )
        self.assertFalse(os.path.exists(chemin_copie))

    def test_nettoyage_copie_temporaire_apres_echec(self):
        self._preparer("# CHANGELOG\n\nConvention d'ajout : x.\n\n## ancien\n- a\n", {1: "## x\n- y\n"})
        chemin_original = git_info.CHEMIN_SCRIPT_FUSION_CHANGELOG
        git_info.CHEMIN_SCRIPT_FUSION_CHANGELOG = os.path.join(self.scratch, "script_introuvable.py")
        try:
            git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        finally:
            git_info.CHEMIN_SCRIPT_FUSION_CHANGELOG = chemin_original
        chemin_copie = os.path.join(
            self.ccw_root_reel, "_relecture_bridge_tmp_fusion_changelog", "fusionner_changelog.py",
        )
        self.assertFalse(os.path.exists(chemin_copie))

    def test_ccw_host_non_configure(self):
        os.remove(self.chemin_config)
        resultat = git_info.fusionner_changelog_distant(self.repertoire_windows, "testproj")
        self.assertFalse(resultat["ok"])
        self.assertIn("ccw_host non configuré", resultat["erreur"])


class FusionnerChangelogWorktreeDistantTestCase(DepotDistantSimuleTestCase):
    """`fusionner_changelog_worktree` (appelée juste après un merge) ne doit
    plus signaler un projet distant comme « à fusionner » sans vérifier
    qu'un CHANGELOG-<N>.md y est réellement présent (issue #114 — avant
    cette issue, le refus était inconditionnel)."""

    def test_rien_a_signaler_sans_changelog(self):
        self._ecrire("CHANGELOG.md", "# CHANGELOG\n")
        self._commit("initial", "CHANGELOG.md")
        self.assertIsNone(git_info.fusionner_changelog_worktree(self.repertoire_windows, "testproj"))

    def test_signale_avec_message_vers_le_bouton(self):
        self._ecrire("CHANGELOG.md", "# CHANGELOG\n")
        self._ecrire("CHANGELOG-1.md", "## x\n")
        self._commit("initial", "CHANGELOG.md", "CHANGELOG-1.md")
        resultat = git_info.fusionner_changelog_worktree(self.repertoire_windows, "testproj")
        self.assertIsNotNone(resultat)
        self.assertFalse(resultat["ok"])
        self.assertIn("Fusionner le changelog", resultat["erreur"])


if __name__ == "__main__":
    unittest.main()
