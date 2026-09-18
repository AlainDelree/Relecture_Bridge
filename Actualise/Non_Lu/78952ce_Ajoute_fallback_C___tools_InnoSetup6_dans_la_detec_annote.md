78952ce

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 78952ce
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 17:34:04 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute fallback C:\.tools\InnoSetup6 dans la detection ISCC (issue #45)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_actualise_setup.bat b/build/rebuild_actualise_setup.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6490ecd..67fa8fc 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_actualise_setup.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_actualise_setup.bat
# ── Zone modifiée : ligne 148 (10 ligne(s)) dans l'ancienne version → ligne 148 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -148,10 +148,13 @@ if errorlevel 1 (
         set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
     ) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
         set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
+    ) else if exist "C:\.tools\InnoSetup6\ISCC.exe" (
+        set "ISCC=C:\.tools\InnoSetup6\ISCC.exe"
     ) else (
         echo.
         echo ERREUR : ISCC.exe introuvable ^(ni sur le PATH, ni dans
-        echo "Program Files\Inno Setup 6"^). Verifiez l'installation d'Inno Setup.
+        echo "Program Files\Inno Setup 6", ni dans C:\.tools\InnoSetup6^).
+        echo Verifiez l'installation d'Inno Setup.
         popd
         popd
         exit /b 1
