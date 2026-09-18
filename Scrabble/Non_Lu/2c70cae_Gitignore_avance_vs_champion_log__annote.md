2c70cae

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2c70cae
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 22:37:25 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Gitignore avance_vs_champion.log

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3ea5c10..ed5c92a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 53 (3 ligne(s)) dans l'ancienne version → ligne 53 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -53,3 +53,4 @@ avance_vs_champion.csv
 # Divers
 .pytest_cache/
 tmp_diag_wiktionnaire/
+avance_vs_champion.log
