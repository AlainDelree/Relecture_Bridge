#!/usr/bin/env python3
"""Tests de la préservation des fins de ligne lors de la résolution de
conflit (issue #107, suite de l'issue #105) — `resoudre_bloc_conflit`,
`resoudre_tous_blocs_conflit` et `lire_conflits_fichier` de `git_info.py`.

Pas de framework de test externe dans ce dépôt au moment de l'issue #107 :
fichier `unittest` autonome (stdlib uniquement), lançable par
`python3 -m unittest relecture_web.test_resolution_conflit_fin_de_ligne -v`
depuis la racine du dépôt, ou directement
`python3 relecture_web/test_resolution_conflit_fin_de_ligne.py`.

Chaque test travaille dans un dépôt git jetable (créé dans un répertoire
temporaire, détruit en fin de test) — jamais dans un dépôt réel. Les
fonctions testées n'ont besoin d'aucun vrai conflit de fusion en cours :
elles lisent/écrivent le fichier directement sur disque, les marqueurs
`<<<<<<<`/`=======`/`>>>>>>>` étant simplement écrits à la main ; seul le
`git add` final (une fois le fichier entièrement résolu) a besoin d'un
dépôt git valide, ce qu'un `git init` suffit à fournir."""

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import git_info  # noqa: E402  (après l'ajustement de sys.path ci-dessus)


class DepotJetableTestCase(unittest.TestCase):
    """Base commune : un dépôt git jetable par test."""

    def setUp(self):
        self.repertoire = tempfile.mkdtemp(prefix="relecture_bridge_test_eol_")
        subprocess.run(["git", "init", "--quiet"], cwd=self.repertoire, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=self.repertoire, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.repertoire, check=True)

    def tearDown(self):
        shutil.rmtree(self.repertoire, ignore_errors=True)

    def ecrire(self, chemin_relatif, contenu_texte):
        """Écrit `contenu_texte` tel quel, en octets UTF-8 — jamais via le
        mode texte de Python, qui traduirait silencieusement les fins de
        ligne à l'écriture (ce que cette issue corrige justement côté
        production ; le test doit lui-même écrire des octets non ambigus)."""
        chemin_absolu = os.path.join(self.repertoire, chemin_relatif)
        with open(chemin_absolu, "wb") as fichier:
            fichier.write(contenu_texte.encode("utf-8"))
        return chemin_absolu

    def lire_brut(self, chemin_relatif):
        with open(os.path.join(self.repertoire, chemin_relatif), "rb") as fichier:
            return fichier.read().decode("utf-8")


# --- Fichiers de départ, un seul bloc de conflit --------------------------

def _fichier_un_bloc(eol):
    """Fichier à un seul bloc de conflit, entièrement en `eol` (`\\n` ou
    `\\r\\n`) : deux lignes de contexte avant, deux après."""
    lignes = [
        "avant 1", "avant 2",
        "<<<<<<< HEAD", "ligne ours", "=======", "ligne theirs", ">>>>>>> branche",
        "apres 1", "apres 2",
    ]
    return "".join(ligne + eol for ligne in lignes)


CONTENU_LF_UN_BLOC = _fichier_un_bloc("\n")
CONTENU_CRLF_UN_BLOC = _fichier_un_bloc("\r\n")

# Fichier mixte : 3 lignes CRLF, 1 ligne LF autour du bloc (dominante CRLF
# sans ambiguïté), le bloc lui-même en LF — pour vérifier que le contexte
# (y compris le bloc non traité s'il y en avait un autre) garde sa
# terminaison d'origine exacte, indépendamment de la dominante calculée.
CONTENU_MIXTE_UN_BLOC = (
    "avant 1\r\n"
    "avant 2\r\n"
    "<<<<<<< HEAD\n"
    "ligne ours\n"
    "=======\n"
    "ligne theirs\n"
    ">>>>>>> branche\n"
    "apres 1\r\n"
)


class ResolutionUnBlocTestCase(DepotJetableTestCase):

    def test_fichier_entierement_lf(self):
        self.ecrire("f.txt", CONTENU_LF_UN_BLOC)
        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, "resultat")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        self.assertTrue(resultat["fichier_resolu"])
        contenu = self.lire_brut("f.txt")
        self.assertNotIn("\r", contenu)
        self.assertEqual(contenu, "avant 1\navant 2\nresultat\napres 1\napres 2\n")

    def test_fichier_entierement_crlf(self):
        self.ecrire("f.txt", CONTENU_CRLF_UN_BLOC)
        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, "resultat")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        # Toutes les lignes, y compris celles jamais touchées par la
        # résolution (contexte avant/après), doivent rester en CRLF.
        self.assertEqual(
            contenu,
            "avant 1\r\navant 2\r\nresultat\r\napres 1\r\napres 2\r\n",
        )

    def test_fichier_mixte_garde_le_contexte_intact(self):
        self.ecrire("f.txt", CONTENU_MIXTE_UN_BLOC)
        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, "resultat")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        # Dominante du fichier = CRLF (3 lignes CRLF contre 5 lignes LF du
        # bloc/marqueurs... en réalité ici LF domine : 5 lignes LF (les
        # marqueurs + le contenu du bloc) contre 2 lignes CRLF (avant 1/2) +
        # 1 CRLF (apres 1) = 3 CRLF. LF domine donc (5 > 3).
        self.assertEqual(
            contenu,
            "avant 1\r\navant 2\r\nresultat\napres 1\r\n",
        )
        # Le contexte jamais touché par la résolution garde ses octets
        # d'origine exacts (CRLF), la ligne insérée prend la dominante (LF).
        self.assertTrue(contenu.startswith("avant 1\r\navant 2\r\n"))
        self.assertTrue(contenu.endswith("apres 1\r\n"))


# --- Fichiers à deux blocs, pour « Traiter tous les blocs » ---------------

def _fichier_deux_blocs(eol):
    lignes = [
        "avant",
        "<<<<<<< HEAD", "ours 1", "=======", "theirs 1", ">>>>>>> branche",
        "milieu",
        "<<<<<<< HEAD", "ours 2", "=======", "theirs 2", ">>>>>>> branche",
        "apres",
    ]
    return "".join(ligne + eol for ligne in lignes)


CONTENU_LF_DEUX_BLOCS = _fichier_deux_blocs("\n")
CONTENU_CRLF_DEUX_BLOCS = _fichier_deux_blocs("\r\n")


class ResolutionTousLesBlocsTestCase(DepotJetableTestCase):

    def _resoudre_tous(self, chemin_relatif, textes_finaux):
        lecture = git_info.lire_conflits_fichier(self.repertoire, chemin_relatif)
        self.assertEqual(lecture["nb_blocs"], len(textes_finaux))
        return git_info.resoudre_tous_blocs_conflit(
            self.repertoire, chemin_relatif, textes_finaux, lecture["empreinte"]
        )

    def test_fichier_entierement_lf(self):
        self.ecrire("f.txt", CONTENU_LF_DEUX_BLOCS)
        resultat = self._resoudre_tous("f.txt", ["r1", "r2"])
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertEqual(contenu, "avant\nr1\nmilieu\nr2\napres\n")

    def test_fichier_entierement_crlf(self):
        self.ecrire("f.txt", CONTENU_CRLF_DEUX_BLOCS)
        resultat = self._resoudre_tous("f.txt", ["r1", "r2"])
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertEqual(contenu, "avant\r\nr1\r\nmilieu\r\nr2\r\napres\r\n")

    def test_fichier_mixte(self):
        # 2 lignes CRLF (avant, milieu) et 9 lignes LF (marqueurs + contenu
        # des deux blocs + apres) : LF domine très largement.
        contenu_depart = (
            "avant\r\n"
            "<<<<<<< HEAD\n" "ours 1\n" "=======\n" "theirs 1\n" ">>>>>>> branche\n"
            "milieu\r\n"
            "<<<<<<< HEAD\n" "ours 2\n" "=======\n" "theirs 2\n" ">>>>>>> branche\n"
            "apres\n"
        )
        self.ecrire("f.txt", contenu_depart)
        resultat = self._resoudre_tous("f.txt", ["r1", "r2"])
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertEqual(contenu, "avant\r\nr1\nmilieu\r\nr2\napres\n")

    def test_empreinte_coherente_entre_affichage_et_soumission(self):
        """Point d'attention du §3 de l'issue #107 : l'empreinte calculée
        par `lire_conflits_fichier` (affichage) doit rester acceptée par
        `resoudre_tous_blocs_conflit` (soumission) pour un fichier CRLF —
        si l'une des deux fonctions traduisait encore les fins de ligne à
        la lecture (mode texte universel) et l'autre non, les deux
        empreintes divergeraient et toute soumission échouerait à tort."""
        self.ecrire("f.txt", CONTENU_CRLF_DEUX_BLOCS)
        lecture = git_info.lire_conflits_fichier(self.repertoire, "f.txt")
        empreinte_attendue = hashlib.sha256(CONTENU_CRLF_DEUX_BLOCS.encode("utf-8")).hexdigest()
        self.assertEqual(lecture["empreinte"], empreinte_attendue)
        resultat = git_info.resoudre_tous_blocs_conflit(
            self.repertoire, "f.txt", ["r1", "r2"], lecture["empreinte"]
        )
        self.assertTrue(resultat["ok"], resultat.get("erreur"))


# --- Normalisation du texte validé vers la fin de ligne du fichier cible --

class NormalisationTexteValideTestCase(DepotJetableTestCase):

    def test_texte_valide_crlf_dans_fichier_lf(self):
        self.ecrire("f.txt", CONTENU_LF_UN_BLOC)
        texte_crlf = "ligne a\r\nligne b\r\n"
        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, texte_crlf)
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertNotIn("\r", contenu)
        self.assertEqual(contenu, "avant 1\navant 2\nligne a\nligne b\napres 1\napres 2\n")

    def test_texte_valide_lf_dans_fichier_crlf(self):
        self.ecrire("f.txt", CONTENU_CRLF_UN_BLOC)
        texte_lf = "ligne a\nligne b\n"
        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, texte_lf)
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertEqual(
            contenu,
            "avant 1\r\navant 2\r\nligne a\r\nligne b\r\napres 1\r\napres 2\r\n",
        )

    def test_texte_valide_sans_fin_de_ligne_finale(self):
        """Un texte final sans retour à la ligne terminal doit tout de même
        recevoir la fin de ligne du fichier cible, pas systématiquement
        `\\n` (comportement d'avant cette issue)."""
        self.ecrire("f.txt", CONTENU_CRLF_UN_BLOC)
        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, "sans fin")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertIn("sans fin\r\napres 1\r\n", contenu)


# --- Chaque origine du texte soumis, en LF puis en CRLF --------------------

class OrigineDuTexteTestCase(DepotJetableTestCase):
    """Au niveau de `resoudre_bloc_conflit`, l'origine du texte (saisi à la
    main, bouton ours/theirs/garder les deux/vider) n'est qu'une valeur de
    chaîne parmi d'autres : ce qui compte est que CHAQUE valeur plausible
    soit normalisée pareillement, qu'elle arrive en LF ou en CRLF — un test
    qui ne soumettrait que du LF pour les boutons ne prouverait rien
    (c'est précisément le cas réel qui a motivé cette issue)."""

    def _verifier_normalisation(self, texte_lf, texte_crlf_equivalent):
        for texte_final in (texte_lf, texte_crlf_equivalent):
            with self.subTest(texte_final=texte_final):
                self.ecrire("f.txt", CONTENU_LF_UN_BLOC)
                resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, texte_final)
                self.assertTrue(resultat["ok"], resultat.get("erreur"))
                contenu = self.lire_brut("f.txt")
                self.assertNotIn("\r", contenu)
                self.assertIn(texte_lf, contenu)

    def test_origine_saisie(self):
        self._verifier_normalisation("texte tape\na la main\n", "texte tape\r\na la main\r\n")

    def test_origine_ours(self):
        # Reprend exactement le texte "ours" du bloc affiché.
        self._verifier_normalisation("ligne ours\n", "ligne ours\r\n")

    def test_origine_theirs(self):
        self._verifier_normalisation("ligne theirs\n", "ligne theirs\r\n")

    def test_origine_garder_les_deux(self):
        # Même construction que le JS de conflit.html (ours puis theirs,
        # une jointure \n si besoin).
        self._verifier_normalisation("ligne ours\nligne theirs\n", "ligne ours\r\nligne theirs\r\n")

    def test_origine_vider(self):
        # « Vider » soumet une chaîne vide quel que soit le fichier cible —
        # rien à normaliser, le bloc disparaît simplement.
        self.ecrire("f.txt", CONTENU_CRLF_UN_BLOC)
        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, "")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertEqual(contenu, "avant 1\r\navant 2\r\napres 1\r\napres 2\r\n")


# --- Deux blocs résolus par deux chemins différents, soumis en CRLF -------

class DeuxCheminsDifferentsTestCase(DepotJetableTestCase):

    def test_deux_blocs_deux_chemins_differents_soumis_en_crlf_dans_fichier_lf(self):
        """Reproduit le cas réel rapporté (un bloc tapé à la main, l'autre
        produit par « Garder les deux »), les deux soumis en CRLF dans un
        fichier LF — le fichier final doit être entièrement LF."""
        self.ecrire("f.txt", CONTENU_LF_DEUX_BLOCS)
        texte_tape_crlf = "texte tape a la main\r\n"
        texte_garder_les_deux_crlf = "ours 1\r\ntheirs 1\r\n"
        lecture = git_info.lire_conflits_fichier(self.repertoire, "f.txt")
        resultat = git_info.resoudre_tous_blocs_conflit(
            self.repertoire, "f.txt",
            [texte_tape_crlf, texte_garder_les_deux_crlf],
            lecture["empreinte"],
        )
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu = self.lire_brut("f.txt")
        self.assertNotIn("\r", contenu)
        self.assertEqual(
            contenu,
            "avant\ntexte tape a la main\nmilieu\nours 1\ntheirs 1\napres\n",
        )


# --- Bloc ignoré : le reste du fichier garde ses octets d'origine ---------

class BlocIgnoreTestCase(DepotJetableTestCase):

    def test_bloc_ignore_conserve_les_octets_d_origine(self):
        self.ecrire("f.txt", CONTENU_CRLF_DEUX_BLOCS)
        contenu_avant = self.lire_brut("f.txt")

        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, "resultat")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        self.assertFalse(resultat["fichier_resolu"])  # le 2e bloc reste

        contenu_apres = self.lire_brut("f.txt")
        # Tout ce qui suit le premier bloc (y compris le 2e bloc, encore
        # non traité) doit être strictement identique, octet pour octet.
        suffixe_attendu = contenu_avant[contenu_avant.index("milieu"):]
        self.assertTrue(contenu_apres.endswith(suffixe_attendu))
        self.assertTrue(contenu_apres.startswith("avant\r\nresultat\r\n"))


# --- Conflit dont les deux côtés contiennent eux-mêmes du CRLF ------------

class ConflitAvecCrlfDesDeuxCotesTestCase(DepotJetableTestCase):

    def test_conflit_avec_crlf_des_deux_cotes(self):
        # Fichier globalement en LF (7 lignes LF contre 4 lignes CRLF
        # internes au bloc) — îlot CRLF local à l'intérieur d'un fichier LF.
        contenu = (
            "ligne 1\n"
            "ligne 2\n"
            "<<<<<<< HEAD\n"
            "ours ligne A\r\n"
            "ours ligne B\r\n"
            "=======\n"
            "theirs ligne A\r\n"
            "theirs ligne B\r\n"
            ">>>>>>> branche\n"
            "ligne 3\n"
            "ligne 4\n"
        )
        self.ecrire("f.txt", contenu)

        lecture = git_info.lire_conflits_fichier(self.repertoire, "f.txt")
        self.assertEqual(lecture["nb_blocs"], 1)
        segment = next(s for s in lecture["segments"] if s["type"] == "conflit")
        # Affiché/lu correctement malgré le CRLF local (marqueurs détectés,
        # contenu préservé tel quel pour les deux panneaux).
        self.assertIn("\r\n", segment["texte_ours"])
        self.assertIn("\r\n", segment["texte_theirs"])
        self.assertEqual(segment["entete_ours"], "<<<<<<< HEAD")
        self.assertEqual(segment["entete_theirs"], ">>>>>>> branche")
        # Le texte précalculé pour le bouton « Copier ce bloc » ne doit
        # jamais exposer de \r à l'utilisateur (issue #107, §3).
        self.assertNotIn("\r", segment["texte_affiche"])

        resultat = git_info.resoudre_bloc_conflit(self.repertoire, "f.txt", 0, "resultat final")
        self.assertTrue(resultat["ok"], resultat.get("erreur"))
        contenu_final = self.lire_brut("f.txt")
        # Le fichier (dominante LF) ressort entièrement en LF : le texte
        # validé, et le reste du fichier (déjà en LF) qui ne contenait pas
        # ce CRLF local.
        self.assertNotIn("\r", contenu_final)
        self.assertEqual(
            contenu_final,
            "ligne 1\nligne 2\nresultat final\nligne 3\nligne 4\n",
        )


if __name__ == "__main__":
    unittest.main()
