01c2398

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 01c2398
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 17:34:35 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #408 : retrait du téléchargement d'Actualise dans rebuild_scrabble.bat + log stderr sur échec de lancement d'Actualise

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ef260fd..0ffaa73 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 17 (7 ligne(s)) dans l'ancienne version → ligne 17 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -17,7 +17,7 @@ echo ============================================
 echo.
 
 REM --- 0. Verifier les dependances externes non versionnees -----------------
-echo [0/9] Verification des dependances externes (hors git)...
+echo [0/8] Verification des dependances externes (hors git)...
 if not exist ".tools\InnoSetup6\ISCC.exe" (
     echo.
     echo ERREUR : .tools\InnoSetup6\ISCC.exe introuvable.
# ── Zone modifiée : ligne 85 (7 ligne(s)) dans l'ancienne version → ligne 85 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -85,7 +85,7 @@ REM build tourne directement sur le partage VirtualBox (\\VBOXSVR\...). On
 REM copie donc tout ce qui est necessaire au build vers un dossier local
 REM (C:\Temp\ScrabbleBuild), on construit entierement la-bas, puis on recopie
 REM uniquement l'installeur final vers le partage.
-echo [1/9] Copie des sources vers le repertoire de build local...
+echo [1/8] Copie des sources vers le repertoire de build local...
 set "LOCALBUILD=C:\Temp\ScrabbleBuild"
 if exist "%LOCALBUILD%" (
     echo Nettoyage de l'ancien repertoire de build local...
# ── Zone modifiée : ligne 111 (7 ligne(s)) dans l'ancienne version → ligne 111 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -111,7 +111,7 @@ echo.
 pushd "%LOCALBUILD%"
 
 REM --- 2. Preparer l'environnement virtuel de build -------------------------
-echo [2/9] Verification de l'environnement virtuel de build...
+echo [2/8] Verification de l'environnement virtuel de build...
 if not exist ".venv_build\Scripts\python.exe" (
     echo .venv_build introuvable : creation en cours...
     python -m venv .venv_build
# ── Zone modifiée : ligne 145 (7 ligne(s)) dans l'ancienne version → ligne 145 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -145,7 +145,7 @@ if not exist ".venv_build\Scripts\python.exe" (
 echo.
 
 REM --- 3. Fermer Scrabble.exe s'il tourne encore ---------------------------
-echo [3/9] Fermeture de Scrabble.exe si necessaire...
+echo [3/8] Fermeture de Scrabble.exe si necessaire...
 tasklist /fi "imagename eq Scrabble.exe" 2>nul | find /i "Scrabble.exe" >nul
 if not errorlevel 1 (
     echo Scrabble.exe est en cours d'execution : fermeture...
# ── Zone modifiée : ligne 157 (7 ligne(s)) dans l'ancienne version → ligne 157 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -157,7 +157,7 @@ if not errorlevel 1 (
 echo.
 
 REM --- 4. Lancer le build PyInstaller ---------------------------------------
-echo [4/9] Injection du numero de build dans version_info.txt...
+echo [4/8] Injection du numero de build dans version_info.txt...
 powershell -NoProfile -Command "(Get-Content 'version_info.txt' -Raw) -replace 'BUILD', '!SCRABBLE_BUILD!' | Set-Content 'version_info.txt' -NoNewline"
 if errorlevel 1 (
     echo.
# ── Zone modifiée : ligne 182 (7 ligne(s)) dans l'ancienne version → ligne 182 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -182,7 +182,7 @@ echo Build termine avec succes.
 echo.
 
 REM --- 5. Verifier le resultat ----------------------------------------------
-echo [5/9] Verification du resultat...
+echo [5/8] Verification du resultat...
 if exist "dist\Scrabble\Scrabble.exe" (
     echo.
     echo dist\Scrabble\ genere :
# ── Zone modifiée : ligne 200 (46 ligne(s)) dans l'ancienne version → ligne 200 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -200,46 +200,8 @@ if exist "dist\Scrabble\Scrabble.exe" (
     exit /b 1
 )
 
-REM --- 6. Telecharger et extraire Actualise (issue #345, issue #346) ---------
-REM Actualise.exe + son dossier _internal\ (runtime Python + DLL, mode
-REM PyInstaller --onedir) sont l'updater embarque dans l'installeur (cf.
-REM scrabble.iss, Source attendue : C:\Temp\ScrabbleBuild\Actualise_dist\).
-REM Recupere depuis la Release v8 du depot AlainDelree/Actualise (issue #408 :
-REM v8 ajoute ActualiseUI.exe, requis par la detection du flag ActualiseUI
-REM cote Scrabble, issue #386).
-echo [6/9] Telechargement d'Actualise (updater)...
-set "ACTUALISE_URL=https://github.com/AlainDelree/Actualise/releases/download/v8/actualise-v8.zip"
-set "ACTUALISE_ZIP=%LOCALBUILD%\actualise.zip"
-set "ACTUALISE_EXTRACT=%LOCALBUILD%\actualise_extract"
-powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri '%ACTUALISE_URL%' -OutFile '%ACTUALISE_ZIP%' -UseBasicParsing } catch { exit 1 }"
-if errorlevel 1 (
-    echo.
-    echo ERREUR : le telechargement d'actualise.zip a echoue ^(%ACTUALISE_URL%^).
-    popd
-    popd
-    exit /b 1
-)
-powershell -NoProfile -Command "try { Expand-Archive -Path '%ACTUALISE_ZIP%' -DestinationPath '%ACTUALISE_EXTRACT%' -Force } catch { exit 1 }"
-if errorlevel 1 (
-    echo.
-    echo ERREUR : l'extraction d'actualise.zip a echoue.
-    popd
-    popd
-    exit /b 1
-)
-robocopy "%ACTUALISE_EXTRACT%" "%LOCALBUILD%\Actualise_dist" /E /NFL /NDL /NJH /NJS /NC /NS /NP >nul
-if %errorlevel% geq 8 (
-    echo.
-    echo ERREUR : la copie de %ACTUALISE_EXTRACT% vers %LOCALBUILD%\Actualise_dist a echoue.
-    popd
-    popd
-    exit /b 1
-)
-echo Actualise pret : %LOCALBUILD%\Actualise_dist
-echo.
-
-REM --- 7. Compiler l'installeur Windows (Inno Setup) ------------------------
-echo [7/9] Compilation de l'installeur Inno Setup...
+REM --- 6. Compiler l'installeur Windows (Inno Setup) ------------------------
+echo [6/8] Compilation de l'installeur Inno Setup...
 if not exist ".tools\InnoSetup6\ISCC.exe" (
     echo.
     echo ERREUR : .tools\InnoSetup6\ISCC.exe introuvable. Verifiez l'installation
# ── Zone modifiée : ligne 261 (12 ligne(s)) dans l'ancienne version → ligne 223 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -261,12 +223,12 @@ copy "C:\Temp\ScrabbleOutput\!SETUP_NAME!" "installeur\output\!SETUP_NAME!"
 echo [OK] Installeur copié vers installeur\output\ ^(local^)
 echo.
 
-REM --- 8. Creer manifest.json et zipper vers scrabble-vN.zip (issue #345, issue #396)
+REM --- 7. Creer manifest.json et zipper vers scrabble-vN.zip (issue #345, issue #396)
 REM scrabble-vN.zip = dist\Scrabble\ + manifest.json, sans dossier englobant
 REM (l'updater Actualise l'extrait directement par-dessus le dossier installe).
 REM N = SCRABBLE_BUILD/NOUVEAU_BUILD, determine plus haut (etape 0bis), pour
 REM que le nom du zip soit coherent avec le tag de la Release GitHub (vN).
-echo [8/9] Creation de manifest.json et de %ZIP_NAME%...
+echo [7/8] Creation de manifest.json et de %ZIP_NAME%...
 echo {"build": 1, "supprimer": []}>manifest.json
 if not exist "installeur\output" mkdir "installeur\output"
 if exist "installeur\output\%ZIP_NAME%" del /f /q "installeur\output\%ZIP_NAME%"
# ── Zone modifiée : ligne 290 (8 ligne(s)) dans l'ancienne version → ligne 252 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -290,8 +252,8 @@ for /f "usebackq" %%s in (`powershell -NoProfile -Command "'{0:N2} Mo' -f ((Get-
 )
 echo.
 
-REM --- 9. Recopier l'installeur et le zip vers le partage, nettoyer le local -
-echo [9/9] Recopie vers le partage et nettoyage du local...
+REM --- 8. Recopier l'installeur et le zip vers le partage, nettoyer le local -
+echo [8/8] Recopie vers le partage et nettoyage du local...
 if not exist "%ORIGDIR%\installeur\output" mkdir "%ORIGDIR%\installeur\output"
 copy /y "installeur\output\!SETUP_NAME!" "%ORIGDIR%\installeur\output\!SETUP_NAME!"
 if errorlevel 1 (
# (diff du fichier suivant)
diff --git a/main.py b/main.py
# (index — ignorable)
index d5467f4..da6f522 100644
# (avant — fichier suivant)
--- a/main.py
# (après — fichier suivant)
+++ b/main.py
# ── Zone modifiée : ligne 75 (7 ligne(s)) dans l'ancienne version → ligne 75 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -75,7 +75,7 @@ if __name__ == "__main__":
     if _actualise_exe.exists():
         try:
             subprocess.Popen([str(_actualise_exe), "--config", "scrabble"])
-        except Exception:
-            pass  # ne jamais bloquer le démarrage de Scrabble
+        except Exception as exc:
+            print(f"[Scrabble] Lancement d'Actualise ignoré : {exc}", file=sys.stderr)
 
     raise SystemExit(main())
