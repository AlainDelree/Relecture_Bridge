53cedd5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 53cedd5
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 23:03:48 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #410 : correction chemin VirtualBox obsolete dans rebuild_scrabble.bat (Z:\CCW -> C:\CCW_Share\CCW)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0ffaa73..e30a74d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 78 (13 ligne(s)) dans l'ancienne version → ligne 78 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -78,13 +78,12 @@ set "SETUP_NAME=Scrabble-Setup-v!SCRABBLE_BUILD!.exe"
 echo Nom de l'installeur : !SETUP_NAME!
 echo.
 
-REM --- 1. Copier les sources vers un repertoire local de la VM ---------------
-REM Contournement temporaire (~10 jours, avant migration vers PC Windows
-REM physique) : PyInstaller et ISCC produisent des fichiers tronques quand le
-REM build tourne directement sur le partage VirtualBox (\\VBOXSVR\...). On
-REM copie donc tout ce qui est necessaire au build vers un dossier local
-REM (C:\Temp\ScrabbleBuild), on construit entierement la-bas, puis on recopie
-REM uniquement l'installeur final vers le partage.
+REM --- 1. Copier les sources vers un repertoire local -------------------------
+REM Sur le PC fixe physique, PyInstaller et ISCC produisent des fichiers
+REM tronques quand le build tourne directement sur le partage local
+REM (C:\CCW_Share\...). On copie donc tout ce qui est necessaire au build vers
+REM un dossier local (C:\Temp\ScrabbleBuild), on construit entierement la-bas,
+REM puis on recopie uniquement l'installeur final vers le partage.
 echo [1/8] Copie des sources vers le repertoire de build local...
 set "LOCALBUILD=C:\Temp\ScrabbleBuild"
 if exist "%LOCALBUILD%" (
# ── Zone modifiée : ligne 341 (7 ligne(s)) dans l'ancienne version → ligne 340 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -341,7 +340,7 @@ if "%PUBLIER%"=="1" (
     echo.
 ) else (
     echo Nettoyage du clone CCW (reset commits locaux)...
-    git -C Z:\CCW\scrabble reset --hard origin/master
+    git -C C:\CCW_Share\CCW\scrabble reset --hard origin/master
     echo Clone CCW propre.
     echo.
 )
