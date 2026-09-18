affae1f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit affae1f
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 21:59:02 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #383 : gitignore avance_vs_champion.csv (sortie de mesurer_force_niveaux.py)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9a47c22..3ea5c10 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 48 (6 ligne(s)) dans l'ancienne version → ligne 48 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -48,6 +48,7 @@ installeur/output/
 malus.csv
 paliers_bas.csv
 paliers_bas.log
+avance_vs_champion.csv
 
 # Divers
 .pytest_cache/
