a231506

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a231506
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 10:12:32 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #414 : suppression artefacts build (Exemples plateau/, build/chevalet_*.png, build/shots/, build/mesure_*.py) + nettoyage .gitignore

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ed5c92a..cd55547 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 31 (9 ligne(s)) dans l'ancienne version → ligne 31 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,9 +31,6 @@ data/*.db
 # Journaux de diagnostic par session (scrabble.journal) — jamais commités
 logs/
 
-# Photos de plateaux réels fournies pour inspiration visuelle (non commitées)
-Exemples plateau/
-
 # Installeur Windows (Inno Setup, issue #217) : setup.exe générés jamais
 # commités (volumineux, régénérables via installeur\scrabble.iss) — seul le
 # script .iss et le README du dossier sont suivis. Voir installeur\README.md.
