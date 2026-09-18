df0d8e5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit df0d8e5
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 11:05:19 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #394 : enrichir CoupNote avec lettres_du_chevalet (leave value, étape 1/3)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/moteur/generateur.py b/src/scrabble/moteur/generateur.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0806012..07de5cf 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/moteur/generateur.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/moteur/generateur.py
# ── Zone modifiée : ligne 61 (11 ligne(s)) dans l'ancienne version → ligne 61 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -61,11 +61,17 @@ class CoupNote:
         placement, hors lettres déjà présentes sur le plateau). Sert de base
         à la pénalité « hooks » de la sélection IA (voir
         :mod:`scrabble.moteur.ia`).
+    lettres_du_chevalet:
+        Lettres du chevalet effectivement posées par ce coup, dans l'ordre
+        des cases nouvelles : ``JOKER`` (``"*"``) pour un joker, sinon la
+        lettre de la tuile. Sert au calcul de la valeur du reliquat (leave
+        value) de la sélection IA.
     """
 
     coup: Coup
     detail: DetailScore
     nb_nouvelles: int
+    lettres_du_chevalet: tuple[str, ...]
 
     @property
     def score(self) -> int:
# ── Zone modifiée : ligne 284 (7 ligne(s)) dans l'ancienne version → ligne 290 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -284,7 +290,13 @@ def generer_coups(
         if not nouvelles:
             continue
         detail = detailler_score(copie, nouvelles, coup.direction)
-        resultats.append(CoupNote(coup, detail, len(nouvelles)))
+        nouvelles_set = set(nouvelles)
+        lettres_du_chevalet = tuple(
+            JOKER if tuile.joker else tuile.lettre
+            for (l, c, tuile) in coup.cases()
+            if (l, c) in nouvelles_set
+        )
+        resultats.append(CoupNote(coup, detail, len(nouvelles), lettres_du_chevalet))
 
     # Trier par score décroissant
     resultats.sort(key=lambda cn: cn.score, reverse=True)
# (diff du fichier suivant)
diff --git a/tests/test_moteur_ia.py b/tests/test_moteur_ia.py
# (index — ignorable)
index a304f8f..8b79ccd 100644
# (avant — fichier suivant)
--- a/tests/test_moteur_ia.py
# (après — fichier suivant)
+++ b/tests/test_moteur_ia.py
# ── Zone modifiée : ligne 117 (7 ligne(s)) dans l'ancienne version → ligne 117 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -117,7 +117,7 @@ def _coup_note(mot: str, score: int, nb_nouvelles: int, cases_bonus=()) -> CoupN
         bonus_scrabble=0,
         total=score,
     )
-    return CoupNote(coup, detail, nb_nouvelles)
+    return CoupNote(coup, detail, nb_nouvelles, ())
 
 
 class TestScoreStrategique:
