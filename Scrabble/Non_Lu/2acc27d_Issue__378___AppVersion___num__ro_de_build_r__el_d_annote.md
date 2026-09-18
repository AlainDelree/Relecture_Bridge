2acc27d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2acc27d
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 17:24:37 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #378 : AppVersion = numéro de build réel dans scrabble.iss

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e2836af..5d5e5a5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 53 (7 ligne(s)) dans l'ancienne version → ligne 53 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -53,7 +53,7 @@
 ; versions).
 AppId={{EC04D19C-69EA-4116-9EB8-C51A30E56EBA}
 AppName={#MyAppName}
-AppVersion={#MyAppVersion}
+AppVersion={#ScrabbleBuildInstalle}
 AppPublisher={#MyAppPublisher}
 DefaultDirName={autopf}\{#MyAppName}
 DefaultGroupName={#MyAppName}
