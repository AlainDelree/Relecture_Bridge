be4d089

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit be4d089
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 07:25:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #293 : retire pause/REBUILD_INTERACTIF + flag /Q du build, ajoute lanceur manuel
    
    - build/rebuild_scrabble.bat : retire le flag /Q de l'appel ISCC (ISCC.exe
      est un compilateur console pur, /Q ne supprimait aucune fenetre - la
      fenetre imaginee appartient a Compil32.exe, jamais appele ici - et
      appauvrissait les logs de build inutilement).
    - build/rebuild_scrabble.bat : retire tous les `pause` conditionnels et la
      variable REBUILD_INTERACTIF associee. Le script principal ne peut plus
      bloquer sur une interaction, quelle que soit la config d'environnement
      (usage automatise CCW-Watcher).
    - build/rebuild_scrabble.bat : remplace `cd /d` par `pushd`/`popd` sur
      tous les chemins de sortie (succes et erreur), pour liberer toute
      session ouverte plus tot - attenuation de la cause reelle du verrou
      identifiee (pushd vers le partage VirtualBox, corrige cote Bridge_Agent).
    - build/rebuild_scrabble_manuel.bat (nouveau, suivi par git malgre le
      gitignore de build/, meme exception que rebuild_scrabble.bat) : lanceur
      interactif pour Alain, appelle rebuild_scrabble.bat, propage son code de
      sortie, puis pause inconditionnelle.
    - installeur/README.md : documente quel script utiliser selon le contexte
      (automatise vs manuel).
    
    Aucune autre reference a REBUILD_INTERACTIF dans le depot (verifie par grep).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 493c0f6..f21e5e7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 1 (7 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,7 +1,7 @@
 @echo off
 setlocal enabledelayedexpansion
 chcp 65001 >nul
-cd /d "%~dp0.."
+pushd "%~dp0.."
 
 echo ============================================
 echo   Rebuild Scrabble.exe
# ── Zone modifiée : ligne 16 (7 ligne(s)) dans l'ancienne version → ligne 16 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -16,7 +16,7 @@ if not exist ".tools\InnoSetup6\ISCC.exe" (
     echo Deposez l'installation portable d'Inno Setup 6 a cet emplacement exact
     echo ^(.tools\InnoSetup6\^) avant de lancer ce script ^(voir installeur\README.md,
     echo section Prerequis^).
-    if "%REBUILD_INTERACTIF%"=="1" pause
+    popd
     exit /b 1
 )
 if not exist "data\dictionnaire\French-Scrabble-ODS8-main" (
# ── Zone modifiée : ligne 25 (7 ligne(s)) dans l'ancienne version → ligne 25 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,7 +25,7 @@ if not exist "data\dictionnaire\French-Scrabble-ODS8-main" (
     echo Deposez le dictionnaire ODS8 a cet emplacement exact
     echo ^(data\dictionnaire\French-Scrabble-ODS8-main\^) avant de lancer ce script
     echo ^(voir data\dictionnaire\README.md^).
-    if "%REBUILD_INTERACTIF%"=="1" pause
+    popd
     exit /b 1
 )
 echo Dependances externes presentes. OK.
# ── Zone modifiée : ligne 39 (7 ligne(s)) dans l'ancienne version → ligne 39 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -39,7 +39,7 @@ if not exist ".venv_build\Scripts\python.exe" (
     if errorlevel 1 (
         echo.
         echo ERREUR : impossible de creer .venv_build. Verifiez l'installation Python.
-        if "%REBUILD_INTERACTIF%"=="1" pause
+        popd
         exit /b 1
     )
     call ".venv_build\Scripts\python.exe" -m pip install --upgrade pip >nul
# ── Zone modifiée : ligne 47 (14 ligne(s)) dans l'ancienne version → ligne 47 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,14 +47,14 @@ if not exist ".venv_build\Scripts\python.exe" (
     if errorlevel 1 (
         echo.
         echo ERREUR : l'installation de requirements.txt a echoue.
-        if "%REBUILD_INTERACTIF%"=="1" pause
+        popd
         exit /b 1
     )
     call ".venv_build\Scripts\pip.exe" install pyinstaller
     if errorlevel 1 (
         echo.
         echo ERREUR : l'installation de pyinstaller a echoue.
-        if "%REBUILD_INTERACTIF%"=="1" pause
+        popd
         exit /b 1
     )
 ) else (
# ── Zone modifiée : ligne 80 (7 ligne(s)) dans l'ancienne version → ligne 80 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -80,7 +80,7 @@ call ".venv_build\Scripts\pyinstaller.exe" scrabble.spec -y
 if errorlevel 1 (
     echo.
     echo ERREUR : le build PyInstaller a echoue. Voir les messages ci-dessus.
-    if "%REBUILD_INTERACTIF%"=="1" pause
+    popd
     exit /b 1
 )
 echo.
# ── Zone modifiée : ligne 101 (7 ligne(s)) dans l'ancienne version → ligne 101 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -101,7 +101,7 @@ if exist "dist\Scrabble\Scrabble.exe" (
 ) else (
     echo.
     echo ERREUR : Scrabble.exe introuvable dans dist\Scrabble apres le build.
-    if "%REBUILD_INTERACTIF%"=="1" pause
+    popd
     exit /b 1
 )
 
# ── Zone modifiée : ligne 111 (14 ligne(s)) dans l'ancienne version → ligne 111 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -111,14 +111,14 @@ if not exist ".tools\InnoSetup6\ISCC.exe" (
     echo.
     echo ERREUR : .tools\InnoSetup6\ISCC.exe introuvable. Verifiez l'installation
     echo portable d'Inno Setup sur cette machine ^(voir installeur\README.md^).
-    if "%REBUILD_INTERACTIF%"=="1" pause
+    popd
     exit /b 1
 )
-call ".tools\InnoSetup6\ISCC.exe" /Q installeur\scrabble.iss
+call ".tools\InnoSetup6\ISCC.exe" installeur\scrabble.iss
 if errorlevel 1 (
     echo.
     echo ERREUR : la compilation Inno Setup a echoue. Voir les messages ci-dessus.
-    if "%REBUILD_INTERACTIF%"=="1" pause
+    popd
     exit /b 1
 )
 echo.
# ── Zone modifiée : ligne 132 (5 ligne(s)) dans l'ancienne version → ligne 132 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -132,5 +132,5 @@ echo Rappel : lancez Scrabble.exe vous-meme depuis cette session
 echo interactive pour verifier que tout fonctionne bien
 echo ^(WebView2, dictionnaire, interface^).
 echo.
-if "%REBUILD_INTERACTIF%"=="1" pause
+popd
 exit /b 0
# (diff du fichier suivant)
diff --git a/build/rebuild_scrabble_manuel.bat b/build/rebuild_scrabble_manuel.bat
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..011e000
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/build/rebuild_scrabble_manuel.bat
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,10 @@
+@echo off
+REM Lanceur interactif : appelle rebuild_scrabble.bat puis garde la fenetre
+REM ouverte pour lecture du resultat. Ne jamais utiliser ce script en contexte
+REM automatise (service CCW) : c'est rebuild_scrabble.bat qu'il faut appeler
+REM directement dans ce cas (voir installeur\README.md).
+call "%~dp0rebuild_scrabble.bat"
+set "CODE_SORTIE=%errorlevel%"
+echo.
+pause
+exit /b %CODE_SORTIE%
# (diff du fichier suivant)
diff --git a/installeur/README.md b/installeur/README.md
# (index — ignorable)
index 65e9375..88ce917 100644
# (avant — fichier suivant)
--- a/installeur/README.md
# (après — fichier suivant)
+++ b/installeur/README.md
# ── Zone modifiée : ligne 19 (6 ligne(s)) dans l'ancienne version → ligne 19 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -19,6 +19,18 @@ build, déposez-les avant de lancer un build complet :
   utilisés) — voir `data\dictionnaire\README.md` pour le détail complet et
   la justification (licence floue, contenu tiers non redistribuable).
 
+## Quel script lancer
+
+Le pipeline complet (venv, PyInstaller, ISCC) est dans `build\rebuild_scrabble.bat`.
+Ce script ne s'arrête jamais sur une interaction (aucun `pause`, aucune
+dépendance à une variable d'environnement) : c'est celui à utiliser en
+contexte automatisé (service CCW-Watcher).
+
+Pour un lancement manuel par Alain (double-clic ou terminal interactif),
+utiliser `build\rebuild_scrabble_manuel.bat` : il appelle
+`rebuild_scrabble.bat`, propage son code de sortie, puis fait un `pause`
+inconditionnel pour garder la fenêtre ouverte le temps de lire le résultat.
+
 ## Prérequis
 
 1. [Inno Setup 6](https://jrsoftware.org/isdl.php) installé (ou disponible en
