ff043b0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ff043b0
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 01:35:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #284 : comparaison de chemins indépendante de la plateforme dans test_docstring_liste_fichiers_coherente
    
    os.path.basename(f) remplace f.split("/")[-1] pour extraire le nom de
    fichier, robuste sous Windows (chemins avec \\) et Linux (chemins avec /).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/test_jeu_docstring.py b/tests/test_jeu_docstring.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9e89948..7aa5bad 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/tests/test_jeu_docstring.py
# ── Version APRÈS ce commit.
+++ b/tests/test_jeu_docstring.py
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +1,7 @@
 """Garde-fou : vérifie que la docstring de test_jeu.py liste exactement les fichiers test_jeu_*.py existants (issue #265)."""
 
 import glob
+import os
 import re
 
 
# ── Zone modifiée : ligne 11 (7 ligne(s)) dans l'ancienne version → ligne 12 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -11,7 +12,7 @@ def test_docstring_liste_fichiers_coherente():
     mentionnes = set(re.findall(r"(test_jeu_\w+\.py)", docstring))
 
     existants = {
-        f.split("/")[-1]
+        os.path.basename(f)
         for f in glob.glob("tests/test_jeu_*.py")
         if not f.endswith("test_jeu_docstring.py")
     }
