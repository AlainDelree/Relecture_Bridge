3d0cd72

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3d0cd72
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 15:18:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #286 : pré-vérification des dépendances externes (ISCC, dictionnaire) avant le build
    
    - build/rebuild_scrabble.bat : nouvelle étape 0 qui contrôle .tools\InnoSetup6\ISCC.exe et data\dictionnaire\French-Scrabble-ODS8-main\ avant de lancer le venv/PyInstaller, avec message d'erreur précis et exit /b 1 immédiat en cas d'absence.
    - installeur/README.md : nouvelle section listant explicitement les deux dépendances externes à déposer manuellement sur un nouveau clone/poste, avec renvoi vers data/dictionnaire/README.md (déjà cohérent, pas de duplication).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 283f08a..f0cdfee 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 8 (6 ligne(s)) dans l'ancienne version → ligne 8 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -8,6 +8,29 @@ echo   Rebuild Scrabble.exe
 echo ============================================
 echo.
 
+REM --- 0. Verifier les dependances externes non versionnees -----------------
+echo [0/5] Verification des dependances externes (hors git)...
+if not exist ".tools\InnoSetup6\ISCC.exe" (
+    echo.
+    echo ERREUR : .tools\InnoSetup6\ISCC.exe introuvable.
+    echo Deposez l'installation portable d'Inno Setup 6 a cet emplacement exact
+    echo ^(.tools\InnoSetup6\^) avant de lancer ce script ^(voir installeur\README.md,
+    echo section Prerequis^).
+    if "%REBUILD_INTERACTIF%"=="1" pause
+    exit /b 1
+)
+if not exist "data\dictionnaire\French-Scrabble-ODS8-main" (
+    echo.
+    echo ERREUR : data\dictionnaire\French-Scrabble-ODS8-main introuvable.
+    echo Deposez le dictionnaire ODS8 a cet emplacement exact
+    echo ^(data\dictionnaire\French-Scrabble-ODS8-main\^) avant de lancer ce script
+    echo ^(voir data\dictionnaire\README.md^).
+    if "%REBUILD_INTERACTIF%"=="1" pause
+    exit /b 1
+)
+echo Dependances externes presentes. OK.
+echo.
+
 REM --- 1. Preparer l'environnement virtuel de build -------------------------
 echo [1/5] Verification de l'environnement virtuel de build...
 if not exist ".venv_build\Scripts\python.exe" (
# (diff du fichier suivant)
diff --git a/installeur/README.md b/installeur/README.md
# (index — ignorable)
index 093566b..65e9375 100644
# (avant — fichier suivant)
--- a/installeur/README.md
# (après — fichier suivant)
+++ b/installeur/README.md
# ── Zone modifiée : ligne 6 (6 ligne(s)) dans l'ancienne version → ligne 6 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6,6 +6,19 @@ sont jamais commités dans le dépôt git** (volumineux, régénérables à tout
 moment à partir du build PyInstaller + de ce script) : seuls `scrabble.iss`
 et ce `README.md` sont suivis par git.
 
+## Dépendances externes à déposer manuellement (nouveau clone/poste)
+
+`build\rebuild_scrabble.bat` vérifie leur présence en étape 0 et s'arrête
+immédiatement si l'une manque. Sur un nouveau clone ou un nouveau poste de
+build, déposez-les avant de lancer un build complet :
+
+- `.tools\InnoSetup6\ISCC.exe` — installation portable d'Inno Setup 6 (voir
+  section Prérequis ci-dessous). Non suivi par git (`.gitignore` ignore
+  `.tools\`).
+- `data\dictionnaire\French-Scrabble-ODS8-main\` (et les autres dictionnaires
+  utilisés) — voir `data\dictionnaire\README.md` pour le détail complet et
+  la justification (licence floue, contenu tiers non redistribuable).
+
 ## Prérequis
 
 1. [Inno Setup 6](https://jrsoftware.org/isdl.php) installé (ou disponible en
