b36e086

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b36e086
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 09:50:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #391 : corriger MyActualiseDir hardcodé en C:\Actualise (au lieu de {sd}\Actualise non résolu par le préprocesseur InnoSetup)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ea96364..73ce981 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 42 (10 ligne(s)) dans l'ancienne version → ligne 42 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -42,10 +42,10 @@
 ; Déposé par build\rebuild_scrabble.bat avant l'appel à ISCC (Actualise.exe +
 ; son dossier _internal\, runtime Python + DLL, mode PyInstaller --onedir).
 #define MyActualiseSrcDir "C:\Temp\ScrabbleBuild\Actualise_dist"
-#define MyActualiseDir "{sd}\Actualise"
+#define MyActualiseDir "C:\Actualise"
 ; Ancien emplacement (une instance d'Actualise par application) : nettoyé
 ; avant installation si présent (issue #385, cf. [Code] ci-dessous).
-#define MyOldActualiseDir "{sd}\Actualise_Scrabble"
+#define MyOldActualiseDir "C:\Actualise_Scrabble"
 ; Numero de build de Scrabble reellement embarque dans ce setup (lu dans
 ; version.json a la racine du depot par rebuild_scrabble.bat, injecte via
 ; /DScrabbleBuildInstalle=<build>) ; "1" n'est qu'un repli de secours pour
