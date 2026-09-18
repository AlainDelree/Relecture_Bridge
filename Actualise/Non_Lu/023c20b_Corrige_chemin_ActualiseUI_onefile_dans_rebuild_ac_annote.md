023c20b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 023c20b
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 11 13:56:04 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige chemin ActualiseUI onefile dans rebuild_actualise_setup.bat et actualise.iss (issue #47)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_actualise_setup.bat b/build/rebuild_actualise_setup.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 67fa8fc..827a01a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_actualise_setup.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_actualise_setup.bat
# ── Zone modifiée : ligne 127 (14 ligne(s)) dans l'ancienne version → ligne 127 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -127,14 +127,14 @@ if not exist "dist\Actualise\Actualise.exe" (
     popd
     exit /b 1
 )
-if not exist "dist\ActualiseUI\ActualiseUI.exe" (
+if not exist "dist\ActualiseUI.exe" (
     echo.
-    echo ERREUR : ActualiseUI.exe introuvable dans dist\ActualiseUI apres le build.
+    echo ERREUR : ActualiseUI.exe introuvable dans dist apres le build.
     popd
     popd
     exit /b 1
 )
-echo dist\Actualise\Actualise.exe et dist\ActualiseUI\ActualiseUI.exe presents. OK.
+echo dist\Actualise\Actualise.exe et dist\ActualiseUI.exe presents. OK.
 echo.
 
 REM --- 7. Compiler l'installeur InnoSetup ------------------------------------
# (diff du fichier suivant)
diff --git a/installeur/actualise.iss b/installeur/actualise.iss
# (index — ignorable)
index cb093f7..f6fc3a6 100644
# (avant — fichier suivant)
--- a/installeur/actualise.iss
# (après — fichier suivant)
+++ b/installeur/actualise.iss
# ── Zone modifiée : ligne 24 (7 ligne(s)) dans l'ancienne version → ligne 24 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,7 +24,7 @@
 ; Scrabble/Rummikub) : PyInstaller/ISCC ne doivent jamais tourner
 ; directement sur le partage VirtualBox (\\VBOXSVR\...).
 #define ActualiseSourceDir "C:\Temp\ActualiseBuild\dist\Actualise"
-#define ActualiseUISourceDir "C:\Temp\ActualiseBuild\dist\ActualiseUI"
+#define ActualiseUISourceDir "C:\Temp\ActualiseBuild\dist"
 
 [Setup]
 AppId={{8556F922-AD4A-4E8D-A7E9-08AD815D5552}
