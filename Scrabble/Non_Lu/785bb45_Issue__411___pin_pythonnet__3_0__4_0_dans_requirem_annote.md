785bb45

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 785bb45
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 10:13:54 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #411 : pin pythonnet>=3.0,<4.0 dans requirements.txt (compat Python 3.15)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/requirements.txt b/requirements.txt
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c745695..3cdba8a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/requirements.txt
# ── Version APRÈS ce commit.
+++ b/requirements.txt
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 1 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +1,10 @@
 # Dépendances du projet Scrabble.
 pywebview
+# pythonnet est une dépendance transitive de pywebview sous Windows (backend
+# EdgeChromium/WinForms) ; épinglée explicitement en 3.x car 2.5.2 n'a pas de
+# roue précompilée pour les nouvelles versions de Python et sa compilation
+# source échoue (nuget.exe legacy) — issue #411.
+pythonnet>=3.0,<4.0; sys_platform == "win32"
 pyinstaller
 pytest
 # Dépliage ("unmunch") du dictionnaire Hunspell fr-toutesvariantes
