551bb9f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 551bb9f
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 23:47:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #332 : ISCC ecrit dans C:\Temp\ScrabbleOutput puis copie vers installeur\output
    
    Evite la corruption de Scrabble-Setup.exe lorsque ISCC ecrit directement
    dans le dossier partage VirtualBox : compilation dans un repertoire local
    a la VM, puis copie explicite vers installeur\output apres verification
    d'erreur.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f21e5e7..2491bac 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 121 (6 ligne(s)) dans l'ancienne version → ligne 121 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -121,6 +121,9 @@ if errorlevel 1 (
     popd
     exit /b 1
 )
+if not exist "installeur\output" mkdir "installeur\output"
+copy "C:\Temp\ScrabbleOutput\Scrabble-Setup.exe" "installeur\output\Scrabble-Setup.exe"
+echo [OK] Installeur copié vers installeur\output\
 echo.
 echo installeur\output\Scrabble-Setup.exe genere.
 echo.
# (diff du fichier suivant)
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# (index — ignorable)
index 1e954c7..5d861df 100644
# (avant — fichier suivant)
--- a/installeur/scrabble.iss
# (après — fichier suivant)
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 38 (7 ligne(s)) dans l'ancienne version → ligne 38 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -38,7 +38,7 @@ SetupIconFile=..\assets\scrabble.ico
 UninstallDisplayIcon={app}\{#MyAppExeName}
 Compression=lzma2
 SolidCompression=yes
-OutputDir=output
+OutputDir=C:\Temp\ScrabbleOutput
 OutputBaseFilename=Scrabble-Setup
 ; Application graphique volumineuse (~90 Mo) : pas de mode "onefile", on
 ; installe le contenu tel quel (cf. [Files] ci-dessous).
