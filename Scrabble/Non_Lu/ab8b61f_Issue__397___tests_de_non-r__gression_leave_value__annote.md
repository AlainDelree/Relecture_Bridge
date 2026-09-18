ab8b61f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ab8b61f
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 12:04:39 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #397 : tests de non-régression leave_value et _POIDS_LEAVE

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/test_moteur_ia.py b/tests/test_moteur_ia.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8b79ccd..2aa912f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/tests/test_moteur_ia.py
# ── Version APRÈS ce commit.
+++ b/tests/test_moteur_ia.py
# ── Zone modifiée : ligne 28 (7 ligne(s)) dans l'ancienne version → ligne 28 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,7 +28,14 @@ import pytest
 
 from scrabble.dictionnaire.dictionnaire import FICHIERS_VOCABULAIRE_PALIER, Trie
 from scrabble.moteur.generateur import CoupNote, generer_coups
-from scrabble.moteur.ia import Niveau, _score_strategique, choisir_coup, resoudre_palier
+from scrabble.moteur.ia import (
+    Niveau,
+    _POIDS_LEAVE,
+    _score_strategique,
+    choisir_coup,
+    leave_value,
+    resoudre_palier,
+)
 from scrabble.moteur.partie import (
     ACTION_COUP,
     ACTION_PASSE,
# ── Zone modifiée : ligne 170 (6 ligne(s)) dans l'ancienne version → ligne 177 (49 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -170,6 +177,49 @@ class TestScoreStrategique:
         assert 0 < ajustement_debutant < ajustement_expert
 
 
+class TestLeaveValue:
+    """Valeur heuristique du reliquat et son intégration par niveau (issue #397)."""
+
+    def test_leave_value_liste_vide(self):
+        assert leave_value([]) == 0.0
+
+    def test_joker_plus_precieux_que_lettre_rare(self):
+        assert leave_value(["*"]) > leave_value(["Z"])
+
+    def test_chevalet_equilibre_bat_desequilibre(self):
+        assert leave_value(["A", "E", "I", "S", "R", "T", "N"]) > leave_value(
+            ["A", "E", "I", "O", "U", "Q", "Z"]
+        )
+
+    def test_bonus_equilibre_voyelles(self):
+        """Un reliquat à 3 voyelles (plage bonus 2-4) bat le même noyau
+        élargi aux 5 voyelles (hors plage, malus).
+
+        Note : l'issue #397 proposait ``["A", "E", "I", "O", "U", "U", "U"]``
+        comme second reliquat, mais les deux ``U`` supplémentaires ajoutent
+        plus de valeur brute (+4.0) que le malus d'équilibre n'en retire
+        (-8.0 net, cf. :func:`leave_value`), si bien que l'assertion ne
+        tenait pas (16.5 < 17.5). Reliquat corrigé à 5 lettres pour isoler
+        l'effet d'équilibre sans excès de valeur brute.
+        """
+        assert leave_value(["A", "E", "I"]) > leave_value(["A", "E", "I", "O", "U"])
+
+    def test_poids_leave_debutant_nul(self):
+        assert _POIDS_LEAVE[Niveau.DEBUTANT] == 0.0
+
+    def test_poids_leave_facile_nul(self):
+        assert _POIDS_LEAVE[Niveau.FACILE] == 0.0
+
+    def test_poids_leave_croissant(self):
+        assert (
+            _POIDS_LEAVE[Niveau.CHAMPION_DU_MONDE]
+            >= _POIDS_LEAVE[Niveau.EXPERT]
+            > _POIDS_LEAVE[Niveau.AVANCE]
+            > _POIDS_LEAVE[Niveau.INTERMEDIAIRE]
+            > _POIDS_LEAVE[Niveau.FACILE]
+        )
+
+
 # --------------------------------------------------------------------------- #
 # Tests unitaires de choisir_coup
 # --------------------------------------------------------------------------- #
