674cf12

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 674cf12
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 00:32:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #333 : rebuild_scrabble.bat — retrait chcp 65001 (corruption parsing cmd.exe sur partage reseau)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2491bac..4eabd11 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 1 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +1,5 @@
 @echo off
 setlocal enabledelayedexpansion
-chcp 65001 >nul
 pushd "%~dp0.."
 
 echo ============================================
