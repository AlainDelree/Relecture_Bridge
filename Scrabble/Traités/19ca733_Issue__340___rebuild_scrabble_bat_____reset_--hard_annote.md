19ca733

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 19ca733
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 31 17:47:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #340 : rebuild_scrabble.bat — reset --hard origin/master du clone CCW en fin de build

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 148c54b..71a8e99 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 192 (5 ligne(s)) dans l'ancienne version → ligne 192 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -192,5 +192,9 @@ echo Rappel : lancez Scrabble.exe vous-meme depuis cette session
 echo interactive pour verifier que tout fonctionne bien
 echo ^(WebView2, dictionnaire, interface^).
 echo.
+echo Nettoyage du clone CCW (reset commits locaux)...
+git -C Z:\CCW\scrabble reset --hard origin/master
+echo Clone CCW propre.
+echo.
 popd
 exit /b 0
