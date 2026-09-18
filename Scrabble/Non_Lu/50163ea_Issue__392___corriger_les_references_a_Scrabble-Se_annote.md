50163ea

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 50163ea
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 10:26:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #392 : corriger les references a Scrabble-Setup.exe dans rebuild_scrabble.bat (nom versionne + injection du build a ISCC)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index dab8acf..ef260fd 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 74 (6 ligne(s)) dans l'ancienne version → ligne 74 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -74,6 +74,8 @@ if /i "%PUBLIER%"=="1" (
 )
 set "ZIP_NAME=scrabble-v!SCRABBLE_BUILD!.zip"
 echo Nom du zip : !ZIP_NAME!
+set "SETUP_NAME=Scrabble-Setup-v!SCRABBLE_BUILD!.exe"
+echo Nom de l'installeur : !SETUP_NAME!
 echo.
 
 REM --- 1. Copier les sources vers un repertoire local de la VM ---------------
# ── Zone modifiée : ligne 246 (7 ligne(s)) dans l'ancienne version → ligne 248 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -246,7 +248,7 @@ if not exist ".tools\InnoSetup6\ISCC.exe" (
     popd
     exit /b 1
 )
-call ".tools\InnoSetup6\ISCC.exe" installeur\scrabble.iss
+call ".tools\InnoSetup6\ISCC.exe" /DScrabbleBuildInstalle=!SCRABBLE_BUILD! installeur\scrabble.iss
 if errorlevel 1 (
     echo.
     echo ERREUR : la compilation Inno Setup a echoue. Voir les messages ci-dessus.
# ── Zone modifiée : ligne 255 (7 ligne(s)) dans l'ancienne version → ligne 257 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -255,7 +257,7 @@ if errorlevel 1 (
     exit /b 1
 )
 if not exist "installeur\output" mkdir "installeur\output"
-copy "C:\Temp\ScrabbleOutput\Scrabble-Setup.exe" "installeur\output\Scrabble-Setup.exe"
+copy "C:\Temp\ScrabbleOutput\!SETUP_NAME!" "installeur\output\!SETUP_NAME!"
 echo [OK] Installeur copié vers installeur\output\ ^(local^)
 echo.
 
# ── Zone modifiée : ligne 291 (7 ligne(s)) dans l'ancienne version → ligne 293 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -291,7 +293,7 @@ echo.
 REM --- 9. Recopier l'installeur et le zip vers le partage, nettoyer le local -
 echo [9/9] Recopie vers le partage et nettoyage du local...
 if not exist "%ORIGDIR%\installeur\output" mkdir "%ORIGDIR%\installeur\output"
-copy /y "installeur\output\Scrabble-Setup.exe" "%ORIGDIR%\installeur\output\Scrabble-Setup.exe"
+copy /y "installeur\output\!SETUP_NAME!" "%ORIGDIR%\installeur\output\!SETUP_NAME!"
 if errorlevel 1 (
     echo.
     echo ERREUR : la recopie de l'installeur vers le partage a echoue.
# ── Zone modifiée : ligne 314 (7 ligne(s)) dans l'ancienne version → ligne 316 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -314,7 +316,7 @@ popd
 rmdir /s /q "%LOCALBUILD%"
 echo [OK] Repertoire de build local nettoye ^(%LOCALBUILD%^)
 echo.
-echo installeur\output\Scrabble-Setup.exe et installeur\output\%ZIP_NAME% generes.
+echo installeur\output\%SETUP_NAME% et installeur\output\%ZIP_NAME% generes.
 echo.
 echo ============================================
 echo   REBUILD TERMINE AVEC SUCCES
