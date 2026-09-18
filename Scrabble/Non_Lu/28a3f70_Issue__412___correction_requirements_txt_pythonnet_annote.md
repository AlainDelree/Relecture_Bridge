28a3f70

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 28a3f70
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 15:40:58 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #412 : correction requirements.txt pythonnet>=3.0.0rc1,<4.0 (pip exclut pre-releases sans borne rc)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/requirements.txt b/requirements.txt
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3cdba8a..0aef32c 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/requirements.txt
# ── Version APRÈS ce commit.
+++ b/requirements.txt
# ── Zone modifiée : ligne 3 (8 ligne(s)) dans l'ancienne version → ligne 3 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3,8 +3,10 @@ pywebview
 # pythonnet est une dépendance transitive de pywebview sous Windows (backend
 # EdgeChromium/WinForms) ; épinglée explicitement en 3.x car 2.5.2 n'a pas de
 # roue précompilée pour les nouvelles versions de Python et sa compilation
-# source échoue (nuget.exe legacy) — issue #411.
-pythonnet>=3.0,<4.0; sys_platform == "win32"
+# source échoue (nuget.exe legacy) — issue #411. Borne basse en 3.0.0rc1 car
+# seule 3.0.0rc6 existe sur PyPI (pre-release) et pip exclut les pre-releases
+# par défaut avec une borne >=3.0 seule — issue #412.
+pythonnet>=3.0.0rc1,<4.0; sys_platform == "win32"
 pyinstaller
 pytest
 # Dépliage ("unmunch") du dictionnaire Hunspell fr-toutesvariantes
