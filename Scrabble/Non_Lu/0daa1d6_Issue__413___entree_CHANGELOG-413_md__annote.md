0daa1d6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0daa1d6
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 15:41:30 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #413 : entree CHANGELOG-413.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-413.md b/CHANGELOG-413.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..2570dd9
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-413.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,7 @@
+# Changelog — Issue #413
+
+## Corrigé
+- `build/rebuild_scrabble.bat` : échappement des parenthèses dans le `echo`
+  du bloc `else` final (branche hors `--publier`), qui cassait
+  l'interpréteur batch (« ... was unexpected at this time. ») et empêchait
+  le `git reset --hard` final de s'exécuter.
