03740af

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 03740af
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 07:24:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #285 : rebuild_scrabble.bat adapté au modèle CCW unifié (chemin relatif + venv auto + pause non bloquante)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b09e081..283f08a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 1 (15 ligne(s)) dans l'ancienne version → ligne 1 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,15 +1,46 @@
 @echo off
 setlocal enabledelayedexpansion
 chcp 65001 >nul
-cd /d C:\CCW\Scrabble
+cd /d "%~dp0.."
 
 echo ============================================
 echo   Rebuild Scrabble.exe
 echo ============================================
 echo.
 
-REM --- 1. Fermer Scrabble.exe s'il tourne encore ---------------------------
-echo [1/4] Fermeture de Scrabble.exe si necessaire...
+REM --- 1. Preparer l'environnement virtuel de build -------------------------
+echo [1/5] Verification de l'environnement virtuel de build...
+if not exist ".venv_build\Scripts\python.exe" (
+    echo .venv_build introuvable : creation en cours...
+    python -m venv .venv_build
+    if errorlevel 1 (
+        echo.
+        echo ERREUR : impossible de creer .venv_build. Verifiez l'installation Python.
+        if "%REBUILD_INTERACTIF%"=="1" pause
+        exit /b 1
+    )
+    call ".venv_build\Scripts\python.exe" -m pip install --upgrade pip >nul
+    call ".venv_build\Scripts\pip.exe" install -r requirements.txt
+    if errorlevel 1 (
+        echo.
+        echo ERREUR : l'installation de requirements.txt a echoue.
+        if "%REBUILD_INTERACTIF%"=="1" pause
+        exit /b 1
+    )
+    call ".venv_build\Scripts\pip.exe" install pyinstaller
+    if errorlevel 1 (
+        echo.
+        echo ERREUR : l'installation de pyinstaller a echoue.
+        if "%REBUILD_INTERACTIF%"=="1" pause
+        exit /b 1
+    )
+) else (
+    echo .venv_build present. OK.
+)
+echo.
+
+REM --- 2. Fermer Scrabble.exe s'il tourne encore ---------------------------
+echo [2/5] Fermeture de Scrabble.exe si necessaire...
 tasklist /fi "imagename eq Scrabble.exe" 2>nul | find /i "Scrabble.exe" >nul
 if not errorlevel 1 (
     echo Scrabble.exe est en cours d'execution : fermeture...
# ── Zone modifiée : ligne 20 (21 ligne(s)) dans l'ancienne version → ligne 51 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -20,21 +51,21 @@ if not errorlevel 1 (
 )
 echo.
 
-REM --- 2. Lancer le build PyInstaller ---------------------------------------
-echo [2/4] Build PyInstaller en cours (peut prendre plusieurs minutes)...
+REM --- 3. Lancer le build PyInstaller ---------------------------------------
+echo [3/5] Build PyInstaller en cours (peut prendre plusieurs minutes)...
 call ".venv_build\Scripts\pyinstaller.exe" scrabble.spec -y
 if errorlevel 1 (
     echo.
     echo ERREUR : le build PyInstaller a echoue. Voir les messages ci-dessus.
-    pause
+    if "%REBUILD_INTERACTIF%"=="1" pause
     exit /b 1
 )
 echo.
 echo Build termine avec succes.
 echo.
 
-REM --- 3. Verifier le resultat ----------------------------------------------
-echo [3/4] Verification du resultat...
+REM --- 4. Verifier le resultat ----------------------------------------------
+echo [4/5] Verification du resultat...
 if exist "dist\Scrabble\Scrabble.exe" (
     echo.
     echo dist\Scrabble\ genere :
# ── Zone modifiée : ligne 47 (24 ligne(s)) dans l'ancienne version → ligne 78 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,24 +78,24 @@ if exist "dist\Scrabble\Scrabble.exe" (
 ) else (
     echo.
     echo ERREUR : Scrabble.exe introuvable dans dist\Scrabble apres le build.
-    pause
+    if "%REBUILD_INTERACTIF%"=="1" pause
     exit /b 1
 )
 
-REM --- 4. Compiler l'installeur Windows (Inno Setup) ------------------------
-echo [4/4] Compilation de l'installeur Inno Setup...
+REM --- 5. Compiler l'installeur Windows (Inno Setup) ------------------------
+echo [5/5] Compilation de l'installeur Inno Setup...
 if not exist ".tools\InnoSetup6\ISCC.exe" (
     echo.
     echo ERREUR : .tools\InnoSetup6\ISCC.exe introuvable. Verifiez l'installation
     echo portable d'Inno Setup sur cette machine ^(voir installeur\README.md^).
-    pause
+    if "%REBUILD_INTERACTIF%"=="1" pause
     exit /b 1
 )
 call ".tools\InnoSetup6\ISCC.exe" installeur\scrabble.iss
 if errorlevel 1 (
     echo.
     echo ERREUR : la compilation Inno Setup a echoue. Voir les messages ci-dessus.
-    pause
+    if "%REBUILD_INTERACTIF%"=="1" pause
     exit /b 1
 )
 echo.
# ── Zone modifiée : ligne 77 (6 ligne(s)) dans l'ancienne version → ligne 108 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -77,6 +108,6 @@ echo.
 echo Rappel : lancez Scrabble.exe vous-meme depuis cette session
 echo interactive pour verifier que tout fonctionne bien
 echo ^(WebView2, dictionnaire, interface^).
-
 echo.
-pause
+if "%REBUILD_INTERACTIF%"=="1" pause
+exit /b 0
