3cadc96

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3cadc96
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 09:38:24 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #390 : nommer le setup avec le numéro de build (OutputBaseFilename versionné)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 309767a..ea96364 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 83 (7 ligne(s)) dans l'ancienne version → ligne 83 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -83,7 +83,7 @@ UninstallDisplayIcon={app}\{#MyAppExeName}
 Compression=lzma2
 SolidCompression=yes
 OutputDir=C:\Temp\ScrabbleOutput
-OutputBaseFilename=Scrabble-Setup
+OutputBaseFilename=Scrabble-Setup-v{#ScrabbleBuildInstalle}
 ; Application graphique volumineuse (~90 Mo) : pas de mode "onefile", on
 ; installe le contenu tel quel (cf. [Files] ci-dessous).
 ArchitecturesInstallIn64BitMode=x64compatible
