af18ad3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit af18ad3
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 31 10:08:15 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #338 : rebuild_scrabble.bat — build execute en local VM (contourne corruption UNC)
    
    CCW lance rebuild_scrabble.bat avec un cwd sur le partage VirtualBox
    (\\VBOXSVR\CCW_Share\...), et PyInstaller/ISCC y produisent des fichiers
    tronques (pas seulement l'OutputDir, deja corrige par le fix #332). Le
    script copie desormais les sources vers C:\Temp\ScrabbleBuild (robocopy,
    sources uniquement : exclusion de .git, venv, .venv_build, dist, build,
    caches, logs), execute tout le build (venv, PyInstaller, ISCC) depuis ce
    repertoire local, puis recopie l'installeur valide vers installeur\output\
    sur le partage et nettoie le repertoire local en fin de traitement.
    Solution temporaire (~10 jours) avant migration vers un PC Windows
    physique ; aucun changement a watcher.py ni a scrabble.iss.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4eabd11..148c54b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +1,7 @@
 @echo off
 setlocal enabledelayedexpansion
 pushd "%~dp0.."
+set "ORIGDIR=%CD%"
 
 echo ============================================
 echo   Rebuild Scrabble.exe
# ── Zone modifiée : ligne 8 (7 ligne(s)) dans l'ancienne version → ligne 9 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -8,7 +9,7 @@ echo ============================================
 echo.
 
 REM --- 0. Verifier les dependances externes non versionnees -----------------
-echo [0/5] Verification des dependances externes (hors git)...
+echo [0/7] Verification des dependances externes (hors git)...
 if not exist ".tools\InnoSetup6\ISCC.exe" (
     echo.
     echo ERREUR : .tools\InnoSetup6\ISCC.exe introuvable.
# ── Zone modifiée : ligne 30 (8 ligne(s)) dans l'ancienne version → ligne 31 (40 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -30,8 +31,40 @@ if not exist "data\dictionnaire\French-Scrabble-ODS8-main" (
 echo Dependances externes presentes. OK.
 echo.
 
-REM --- 1. Preparer l'environnement virtuel de build -------------------------
-echo [1/5] Verification de l'environnement virtuel de build...
+REM --- 1. Copier les sources vers un repertoire local de la VM ---------------
+REM Contournement temporaire (~10 jours, avant migration vers PC Windows
+REM physique) : PyInstaller et ISCC produisent des fichiers tronques quand le
+REM build tourne directement sur le partage VirtualBox (\\VBOXSVR\...). On
+REM copie donc tout ce qui est necessaire au build vers un dossier local
+REM (C:\Temp\ScrabbleBuild), on construit entierement la-bas, puis on recopie
+REM uniquement l'installeur final vers le partage.
+echo [1/7] Copie des sources vers le repertoire de build local...
+set "LOCALBUILD=C:\Temp\ScrabbleBuild"
+if exist "%LOCALBUILD%" (
+    echo Nettoyage de l'ancien repertoire de build local...
+    rmdir /s /q "%LOCALBUILD%"
+)
+mkdir "%LOCALBUILD%"
+if errorlevel 1 (
+    echo.
+    echo ERREUR : impossible de creer %LOCALBUILD%.
+    popd
+    exit /b 1
+)
+robocopy "%ORIGDIR%" "%LOCALBUILD%" /E /XD ".git" "venv" ".venv_build" "dist" "build" "__pycache__" ".pytest_cache" "logs" "Exemples plateau" "issue-attachments" /NFL /NDL /NJH /NJS /NC /NS /NP >nul
+if %errorlevel% geq 8 (
+    echo.
+    echo ERREUR : la copie des sources vers %LOCALBUILD% a echoue.
+    popd
+    exit /b 1
+)
+echo Sources copiees vers %LOCALBUILD%. OK.
+echo.
+
+pushd "%LOCALBUILD%"
+
+REM --- 2. Preparer l'environnement virtuel de build -------------------------
+echo [2/7] Verification de l'environnement virtuel de build...
 if not exist ".venv_build\Scripts\python.exe" (
     echo .venv_build introuvable : creation en cours...
     python -m venv .venv_build
# ── Zone modifiée : ligne 39 (6 ligne(s)) dans l'ancienne version → ligne 72 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -39,6 +72,7 @@ if not exist ".venv_build\Scripts\python.exe" (
         echo.
         echo ERREUR : impossible de creer .venv_build. Verifiez l'installation Python.
         popd
+        popd
         exit /b 1
     )
     call ".venv_build\Scripts\python.exe" -m pip install --upgrade pip >nul
# ── Zone modifiée : ligne 47 (6 ligne(s)) dans l'ancienne version → ligne 81 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,6 +81,7 @@ if not exist ".venv_build\Scripts\python.exe" (
         echo.
         echo ERREUR : l'installation de requirements.txt a echoue.
         popd
+        popd
         exit /b 1
     )
     call ".venv_build\Scripts\pip.exe" install pyinstaller
# ── Zone modifiée : ligne 54 (6 ligne(s)) dans l'ancienne version → ligne 89 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -54,6 +89,7 @@ if not exist ".venv_build\Scripts\python.exe" (
         echo.
         echo ERREUR : l'installation de pyinstaller a echoue.
         popd
+        popd
         exit /b 1
     )
 ) else (
# ── Zone modifiée : ligne 61 (8 ligne(s)) dans l'ancienne version → ligne 97 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -61,8 +97,8 @@ if not exist ".venv_build\Scripts\python.exe" (
 )
 echo.
 
-REM --- 2. Fermer Scrabble.exe s'il tourne encore ---------------------------
-echo [2/5] Fermeture de Scrabble.exe si necessaire...
+REM --- 3. Fermer Scrabble.exe s'il tourne encore ---------------------------
+echo [3/7] Fermeture de Scrabble.exe si necessaire...
 tasklist /fi "imagename eq Scrabble.exe" 2>nul | find /i "Scrabble.exe" >nul
 if not errorlevel 1 (
     echo Scrabble.exe est en cours d'execution : fermeture...
# ── Zone modifiée : ligne 73 (21 ligne(s)) dans l'ancienne version → ligne 109 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -73,21 +109,22 @@ if not errorlevel 1 (
 )
 echo.
 
-REM --- 3. Lancer le build PyInstaller ---------------------------------------
-echo [3/5] Build PyInstaller en cours (peut prendre plusieurs minutes)...
+REM --- 4. Lancer le build PyInstaller ---------------------------------------
+echo [4/7] Build PyInstaller en cours (peut prendre plusieurs minutes)...
 call ".venv_build\Scripts\pyinstaller.exe" scrabble.spec -y
 if errorlevel 1 (
     echo.
     echo ERREUR : le build PyInstaller a echoue. Voir les messages ci-dessus.
     popd
+    popd
     exit /b 1
 )
 echo.
 echo Build termine avec succes.
 echo.
 
-REM --- 4. Verifier le resultat ----------------------------------------------
-echo [4/5] Verification du resultat...
+REM --- 5. Verifier le resultat ----------------------------------------------
+echo [5/7] Verification du resultat...
 if exist "dist\Scrabble\Scrabble.exe" (
     echo.
     echo dist\Scrabble\ genere :
# ── Zone modifiée : ligne 101 (16 ligne(s)) dans l'ancienne version → ligne 138 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -101,16 +138,18 @@ if exist "dist\Scrabble\Scrabble.exe" (
     echo.
     echo ERREUR : Scrabble.exe introuvable dans dist\Scrabble apres le build.
     popd
+    popd
     exit /b 1
 )
 
-REM --- 5. Compiler l'installeur Windows (Inno Setup) ------------------------
-echo [5/5] Compilation de l'installeur Inno Setup...
+REM --- 6. Compiler l'installeur Windows (Inno Setup) ------------------------
+echo [6/7] Compilation de l'installeur Inno Setup...
 if not exist ".tools\InnoSetup6\ISCC.exe" (
     echo.
     echo ERREUR : .tools\InnoSetup6\ISCC.exe introuvable. Verifiez l'installation
     echo portable d'Inno Setup sur cette machine ^(voir installeur\README.md^).
     popd
+    popd
     exit /b 1
 )
 call ".tools\InnoSetup6\ISCC.exe" installeur\scrabble.iss
# ── Zone modifiée : ligne 118 (11 ligne(s)) dans l'ancienne version → ligne 157 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -118,11 +157,30 @@ if errorlevel 1 (
     echo.
     echo ERREUR : la compilation Inno Setup a echoue. Voir les messages ci-dessus.
     popd
+    popd
     exit /b 1
 )
 if not exist "installeur\output" mkdir "installeur\output"
 copy "C:\Temp\ScrabbleOutput\Scrabble-Setup.exe" "installeur\output\Scrabble-Setup.exe"
-echo [OK] Installeur copié vers installeur\output\
+echo [OK] Installeur copié vers installeur\output\ ^(local^)
+echo.
+
+REM --- 7. Recopier l'installeur vers le partage et nettoyer le local --------
+echo [7/7] Recopie de l'installeur vers le partage et nettoyage du local...
+if not exist "%ORIGDIR%\installeur\output" mkdir "%ORIGDIR%\installeur\output"
+copy /y "installeur\output\Scrabble-Setup.exe" "%ORIGDIR%\installeur\output\Scrabble-Setup.exe"
+if errorlevel 1 (
+    echo.
+    echo ERREUR : la recopie de l'installeur vers le partage a echoue.
+    popd
+    popd
+    exit /b 1
+)
+echo [OK] Installeur copié vers %ORIGDIR%\installeur\output\
+
+popd
+rmdir /s /q "%LOCALBUILD%"
+echo [OK] Repertoire de build local nettoye ^(%LOCALBUILD%^)
 echo.
 echo installeur\output\Scrabble-Setup.exe genere.
 echo.
