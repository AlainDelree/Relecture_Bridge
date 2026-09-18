9d935f8

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9d935f8
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 16:33:19 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #254 : extraction des helpers _DicoFactice et _partie_simple
    
    Déplace _DicoFactice et _partie_simple vers tests/_aides_test_jeu.py
    (préfixé _ pour éviter la collecte pytest) pour les rendre disponibles
    aux futurs fichiers de tests issus du découpage de test_jeu.py.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/_aides_test_jeu.py b/tests/_aides_test_jeu.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..79df4dd
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/tests/_aides_test_jeu.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,25 @@
+"""Helpers partagés pour les tests de l'écran de jeu (issue #254).
+
+Ce module contient des classes et fonctions utilisées par plusieurs fichiers
+de tests issus du découpage de test_jeu.py. Le préfixe _ évite que pytest ne
+le collecte comme un fichier de tests.
+"""
+
+from scrabble.moteur.ia import Niveau
+from scrabble.moteur.partie import Joueur, Partie
+
+
+class _DicoFactice:
+    """Dictionnaire minimal (accepte tout) — l'écran de jeu ne valide rien."""
+
+    def contient(self, mot: str) -> bool:
+        return True
+
+
+def _partie_simple(graine: int = 42) -> Partie:
+    """Petite partie déterministe à deux joueurs (humain + ordinateur)."""
+    joueurs = [
+        Joueur(nom="Alice", humain=True),
+        Joueur(nom="Robot", humain=False, niveau=Niveau.FACILE),
+    ]
+    return Partie(joueurs, _DicoFactice(), graine=graine)
# (diff du fichier suivant)
diff --git a/tests/test_jeu.py b/tests/test_jeu.py
# (index — ignorable)
index 50dc5dd..2e38b2a 100644
# (avant — fichier suivant)
--- a/tests/test_jeu.py
# (après — fichier suivant)
+++ b/tests/test_jeu.py
# ── Zone modifiée : ligne 17 (6 ligne(s)) dans l'ancienne version → ligne 17 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -17,6 +17,7 @@ import pytest
 from scrabble.dictionnaire.dictionnaire import Trie
 from scrabble.moteur.ia import Niveau
 from scrabble.moteur.partie import Joueur, Partie, creer_partie
+from tests._aides_test_jeu import _DicoFactice, _partie_simple
 from scrabble.moteur.plateau_partie import Coup, Direction, Tuile
 from scrabble.moteur.score import DetailMot, DetailScore
 from scrabble.persistance import (
# ── Zone modifiée : ligne 56 (22 ligne(s)) dans l'ancienne version → ligne 57 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -56,22 +57,6 @@ from scrabble.ui.jeu import (
 )
 
 
-class _DicoFactice:
-    """Dictionnaire minimal (accepte tout) — l'écran de jeu ne valide rien."""
-
-    def contient(self, mot: str) -> bool:
-        return True
-
-
-def _partie_simple(graine: int = 42) -> Partie:
-    """Petite partie déterministe à deux joueurs (humain + ordinateur)."""
-    joueurs = [
-        Joueur(nom="Alice", humain=True),
-        Joueur(nom="Robot", humain=False, niveau=Niveau.FACILE),
-    ]
-    return Partie(joueurs, _DicoFactice(), graine=graine)
-
-
 class TestSerialiserCase:
     """Tests de la sérialisation d'une case du plateau."""
 
