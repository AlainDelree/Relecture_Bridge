8d8210b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8d8210b
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 21:20:01 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #287 : mode silencieux (/Q) pour l'appel ISCC dans rebuild_scrabble.bat
    
    En Session 0 (service Windows CCW-Watcher, sans bureau interactif),
    ISCC.exe sans flag peut afficher une fenetre de progression graphique
    attendant une interaction, laissant le process cmd.exe vivant
    indefiniment et un verrou sur Scrabble-Setup.exe malgre une
    compilation terminee avec succes. Le flag /Q supprime totalement
    cette fenetre, sans impact sur l'usage manuel d'Alain (le script
    affiche deja ses propres messages de progression via echo).
    
    Verification : installeur\scrabble.iss ne contient aucune section
    [Run] ni action de post-compilation susceptible de causer un
    comportement similaire independamment de ce flag.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f0cdfee..493c0f6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 114 (7 ligne(s)) dans l'ancienne version → ligne 114 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -114,7 +114,7 @@ if not exist ".tools\InnoSetup6\ISCC.exe" (
     if "%REBUILD_INTERACTIF%"=="1" pause
     exit /b 1
 )
-call ".tools\InnoSetup6\ISCC.exe" installeur\scrabble.iss
+call ".tools\InnoSetup6\ISCC.exe" /Q installeur\scrabble.iss
 if errorlevel 1 (
     echo.
     echo ERREUR : la compilation Inno Setup a echoue. Voir les messages ci-dessus.
