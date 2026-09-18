caf5711

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit caf5711
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 19:11:11 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #354 : deplace le git reset --hard du clone CCW avant le bloc --publier
    
    Le reset detruisait le commit version.json produit par --publier (issue #353).
    Le bloc de nettoyage s'execute desormais dans tous les cas (avec ou sans
    --publier), mais avant le bloc de publication.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8775b82..d8b4bfc 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 275 (6 ligne(s)) dans l'ancienne version → ligne 275 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -275,6 +275,11 @@ echo interactive pour verifier que tout fonctionne bien
 echo ^(WebView2, dictionnaire, interface^).
 echo.
 
+echo Nettoyage du clone CCW (reset commits locaux)...
+git -C Z:\CCW\scrabble reset --hard origin/master
+echo Clone CCW propre.
+echo.
+
 if "%PUBLIER%"=="1" (
     echo ============================================
     echo   PUBLICATION ^(--publier^)
# ── Zone modifiée : ligne 339 (9 ligne(s)) dans l'ancienne version → ligne 344 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -339,9 +344,5 @@ if "%PUBLIER%"=="1" (
     echo.
 )
 
-echo Nettoyage du clone CCW (reset commits locaux)...
-git -C Z:\CCW\scrabble reset --hard origin/master
-echo Clone CCW propre.
-echo.
 popd
 exit /b 0
