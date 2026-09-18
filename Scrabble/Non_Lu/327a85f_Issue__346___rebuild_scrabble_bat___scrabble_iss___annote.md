327a85f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 327a85f
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 02:13:16 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #346 : rebuild_scrabble.bat + scrabble.iss — deployer _internal\ avec Actualise.exe

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 93fdc2f..3c41fad 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 142 (11 ligne(s)) dans l'ancienne version → ligne 142 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -142,11 +142,12 @@ if exist "dist\Scrabble\Scrabble.exe" (
     exit /b 1
 )
 
-REM --- 6. Telecharger et extraire Actualise.exe (issue #345) -----------------
-REM Actualise.exe est l'updater embarque dans l'installeur (cf. scrabble.iss,
-REM Source attendue : C:\Temp\ScrabbleBuild\Actualise.exe). Recupere depuis la
-REM Release v1 du depot AlainDelree/Actualise.
-echo [6/9] Telechargement d'Actualise.exe (updater)...
+REM --- 6. Telecharger et extraire Actualise (issue #345, issue #346) ---------
+REM Actualise.exe + son dossier _internal\ (runtime Python + DLL, mode
+REM PyInstaller --onedir) sont l'updater embarque dans l'installeur (cf.
+REM scrabble.iss, Source attendue : C:\Temp\ScrabbleBuild\Actualise_dist\).
+REM Recupere depuis la Release v1 du depot AlainDelree/Actualise.
+echo [6/9] Telechargement d'Actualise (updater)...
 set "ACTUALISE_URL=https://github.com/AlainDelree/Actualise/releases/download/v1/actualise.zip"
 set "ACTUALISE_ZIP=%LOCALBUILD%\actualise.zip"
 set "ACTUALISE_EXTRACT=%LOCALBUILD%\actualise_extract"
# ── Zone modifiée : ligne 166 (15 ligne(s)) dans l'ancienne version → ligne 167 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -166,15 +167,15 @@ if errorlevel 1 (
     popd
     exit /b 1
 )
-powershell -NoProfile -Command "try { $exe = Get-ChildItem -Path '%ACTUALISE_EXTRACT%' -Recurse -Filter 'Actualise.exe' | Select-Object -First 1; if (-not $exe) { exit 1 }; Copy-Item -Path $exe.FullName -Destination '%LOCALBUILD%\Actualise.exe' -Force } catch { exit 1 }"
-if errorlevel 1 (
+robocopy "%ACTUALISE_EXTRACT%" "%LOCALBUILD%\Actualise_dist" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
+if %errorlevel% geq 8 (
     echo.
-    echo ERREUR : Actualise.exe introuvable dans actualise.zip, ou copie vers %LOCALBUILD% echouee.
+    echo ERREUR : la copie de %ACTUALISE_EXTRACT% vers %LOCALBUILD%\Actualise_dist a echoue.
     popd
     popd
     exit /b 1
 )
-echo Actualise.exe pret : %LOCALBUILD%\Actualise.exe
+echo Actualise pret : %LOCALBUILD%\Actualise_dist
 echo.
 
 REM --- 7. Compiler l'installeur Windows (Inno Setup) ------------------------
# (diff du fichier suivant)
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# (index — ignorable)
index 23320cb..e8fe1e4 100644
# (avant — fichier suivant)
--- a/installeur/scrabble.iss
# (après — fichier suivant)
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 21 (8 ligne(s)) dans l'ancienne version → ligne 21 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -21,8 +21,9 @@
 ; architecture complète dans CONCEPTION.md du dépôt Actualise). Le raccourci
 ; utilisateur doit pointer vers lui, jamais directement vers Scrabble.exe.
 #define MyActualiseExeName "Actualise.exe"
-; Déposé par build\rebuild_scrabble.bat avant l'appel à ISCC.
-#define MyActualiseExeSource "C:\Temp\ScrabbleBuild\Actualise.exe"
+; Déposé par build\rebuild_scrabble.bat avant l'appel à ISCC (Actualise.exe +
+; son dossier _internal\, runtime Python + DLL, mode PyInstaller --onedir).
+#define MyActualiseSrcDir "C:\Temp\ScrabbleBuild\Actualise_dist"
 #define MyActualiseDir "{sd}\Actualise"
 
 [Setup]
# ── Zone modifiée : ligne 68 (9 ligne(s)) dans l'ancienne version → ligne 69 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -68,9 +69,11 @@ Name: "french"; MessagesFile: "compiler:Languages\French.isl"
 ; dans l'installeur : un nouvel utilisateur hériterait sinon des préférences/
 ; de l'historique de parties de quelqu'un d'autre dès la première ouverture.
 Source: "{#MyDistDir}\*"; DestDir: "{app}"; Excludes: "config.json,logs\*,data\parties.db,data\*.db"; Flags: ignoreversion recursesubdirs createallsubdirs
-; Actualise.exe : updater autonome, installé à côté de Scrabble (pas dans
-; {app}) car il survit aux mises à jour/réinstallations de Scrabble lui-même.
-Source: "{#MyActualiseExeSource}"; DestDir: "{#MyActualiseDir}"; Flags: ignoreversion
+; Actualise : updater autonome, installé à côté de Scrabble (pas dans {app})
+; car il survit aux mises à jour/réinstallations de Scrabble lui-même. Copie
+; récursive (Actualise.exe + _internal\, runtime Python + DLL, mode
+; PyInstaller --onedir).
+Source: "{#MyActualiseSrcDir}\*"; DestDir: "{#MyActualiseDir}"; Flags: ignoreversion recursesubdirs createallsubdirs
 
 [Dirs]
 Name: "{#MyActualiseDir}"
