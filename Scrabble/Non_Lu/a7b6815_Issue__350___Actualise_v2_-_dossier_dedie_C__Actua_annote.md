a7b6815

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a7b6815
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 16:28:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #350 : Actualise v2 - dossier dedie C:\Actualise_Scrabble (multi-jeux)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3c41fad..b70ddf2 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 146 (9 ligne(s)) dans l'ancienne version → ligne 146 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -146,9 +146,9 @@ REM --- 6. Telecharger et extraire Actualise (issue #345, issue #346) ---------
 REM Actualise.exe + son dossier _internal\ (runtime Python + DLL, mode
 REM PyInstaller --onedir) sont l'updater embarque dans l'installeur (cf.
 REM scrabble.iss, Source attendue : C:\Temp\ScrabbleBuild\Actualise_dist\).
-REM Recupere depuis la Release v1 du depot AlainDelree/Actualise.
+REM Recupere depuis la Release v2 du depot AlainDelree/Actualise.
 echo [6/9] Telechargement d'Actualise (updater)...
-set "ACTUALISE_URL=https://github.com/AlainDelree/Actualise/releases/download/v1/actualise.zip"
+set "ACTUALISE_URL=https://github.com/AlainDelree/Actualise/releases/download/v2/actualise.zip"
 set "ACTUALISE_ZIP=%LOCALBUILD%\actualise.zip"
 set "ACTUALISE_EXTRACT=%LOCALBUILD%\actualise_extract"
 powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri '%ACTUALISE_URL%' -OutFile '%ACTUALISE_ZIP%' -UseBasicParsing } catch { exit 1 }"
# (diff du fichier suivant)
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# (index — ignorable)
index d556b28..9fe3c1b 100644
# (avant — fichier suivant)
--- a/installeur/scrabble.iss
# (après — fichier suivant)
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 29 (7 ligne(s)) dans l'ancienne version → ligne 29 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -29,7 +29,7 @@
 ; Déposé par build\rebuild_scrabble.bat avant l'appel à ISCC (Actualise.exe +
 ; son dossier _internal\, runtime Python + DLL, mode PyInstaller --onedir).
 #define MyActualiseSrcDir "C:\Temp\ScrabbleBuild\Actualise_dist"
-#define MyActualiseDir "{sd}\Actualise"
+#define MyActualiseDir "{sd}\Actualise_Scrabble"
 
 [Setup]
 ; GUID fixe et unique à l'application : NE PAS régénérer (sert à Windows pour
