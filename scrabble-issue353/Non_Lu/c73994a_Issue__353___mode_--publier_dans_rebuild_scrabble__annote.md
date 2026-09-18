c73994a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c73994a
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 18:57:35 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #353 : mode --publier dans rebuild_scrabble.bat (sha256 + version.json + commit, push manuel)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-353.md b/CHANGELOG-353.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..403f24c
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-353.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,11 @@
+### Ajouté
+
+- **Issue #353** — Mode optionnel `--publier [N]` dans
+  `build/rebuild_scrabble.bat`. Sans paramètre, le script se comporte
+  exactement comme avant. Avec `--publier`, après un build réussi : calcul
+  du SHA-256 de `installeur\output\scrabble.zip` (PowerShell
+  `Get-FileHash`), détermination du numéro de build (celui fourni en
+  paramètre, sinon incrément de 1 du `build` actuel de `version.json` à la
+  racine du clone), écriture de `version.json`, puis `git add` + `git
+  commit`. Le script n'exécute jamais `git push` ni `gh release create` —
+  un rappel explicite les mentionne comme étapes manuelles restantes.
# (diff du fichier suivant)
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# (index — ignorable)
index b70ddf2..6b3f0f7 100644
# (avant — fichier suivant)
--- a/build/rebuild_scrabble.bat
# (après — fichier suivant)
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 3 (6 ligne(s)) dans l'ancienne version → ligne 3 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3,6 +3,14 @@ setlocal enabledelayedexpansion
 pushd "%~dp0.."
 set "ORIGDIR=%CD%"
 
+REM --- Analyse des parametres (mode --publier optionnel) --------------------
+set "PUBLIER=0"
+set "PUBLIER_BUILD="
+if /i "%~1"=="--publier" (
+    set "PUBLIER=1"
+    if not "%~2"=="" set "PUBLIER_BUILD=%~2"
+)
+
 echo ============================================
 echo   Rebuild Scrabble.exe
 echo ============================================
# ── Zone modifiée : ligne 266 (6 ligne(s)) dans l'ancienne version → ligne 274 (71 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -266,6 +274,71 @@ echo Rappel : lancez Scrabble.exe vous-meme depuis cette session
 echo interactive pour verifier que tout fonctionne bien
 echo ^(WebView2, dictionnaire, interface^).
 echo.
+
+if "%PUBLIER%"=="1" (
+    echo ============================================
+    echo   PUBLICATION ^(--publier^)
+    echo ============================================
+    echo.
+    echo [Publier 1/4] Calcul du SHA-256 de installeur\output\scrabble.zip...
+    if not exist "installeur\output\scrabble.zip" (
+        echo.
+        echo ERREUR : installeur\output\scrabble.zip introuvable, publication annulee.
+        popd
+        exit /b 1
+    )
+    set "ZIP_SHA256="
+    for /f "usebackq" %%h in (`powershell -NoProfile -Command "(Get-FileHash -Algorithm SHA256 'installeur\output\scrabble.zip').Hash.ToLower()"`) do set "ZIP_SHA256=%%h"
+    if "!ZIP_SHA256!"=="" (
+        echo.
+        echo ERREUR : le calcul du SHA-256 de scrabble.zip a echoue.
+        popd
+        exit /b 1
+    )
+    echo SHA-256 : !ZIP_SHA256!
+    echo.
+
+    echo [Publier 2/4] Determination du numero de build...
+    if not "%PUBLIER_BUILD%"=="" (
+        set "NOUVEAU_BUILD=%PUBLIER_BUILD%"
+        echo Numero de build fourni en parametre : !NOUVEAU_BUILD!
+    ) else (
+        set "ANCIEN_BUILD="
+        for /f "usebackq" %%b in (`powershell -NoProfile -Command "try { (Get-Content 'version.json' -Raw | ConvertFrom-Json).build } catch { '' }"`) do set "ANCIEN_BUILD=%%b"
+        if "!ANCIEN_BUILD!"=="" (
+            echo.
+            echo ERREUR : impossible de lire le champ build de version.json a la racine du clone.
+            popd
+            exit /b 1
+        )
+        set /a NOUVEAU_BUILD=!ANCIEN_BUILD!+1
+        echo Build actuel dans version.json : !ANCIEN_BUILD! -^> nouveau build : !NOUVEAU_BUILD!
+    )
+    echo.
+
+    echo [Publier 3/4] Ecriture de version.json...
+    echo {"build": !NOUVEAU_BUILD!, "sha256": "!ZIP_SHA256!"}>version.json
+    type version.json
+    echo.
+    echo.
+
+    echo [Publier 4/4] Commit git de version.json...
+    git add version.json
+    git commit -m "version.json : build !NOUVEAU_BUILD!, sha256 scrabble.zip"
+    if errorlevel 1 (
+        echo.
+        echo ERREUR : le commit git de version.json a echoue.
+        popd
+        exit /b 1
+    )
+    echo.
+    echo ============================================
+    echo   RAPPEL : git push et gh release create restent MANUELS.
+    echo   Ce script ne les execute JAMAIS automatiquement.
+    echo ============================================
+    echo.
+)
+
 echo Nettoyage du clone CCW (reset commits locaux)...
 git -C Z:\CCW\scrabble reset --hard origin/master
 echo Clone CCW propre.
