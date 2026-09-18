e33b5cc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e33b5cc
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 09:46:26 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Autoriser explicitement pytest via venv dans .claude/settings.json (issue #207)
    
    Ajoute une règle Bash(venv/bin/python -m pytest *) ciblée en permissions.allow
    pour que les sessions bridge non-interactives puissent exécuter la suite de
    tests sans prompt d'approbation bloquant, sans élargir les permissions
    au-delà de ce cas précis.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.claude/settings.json b/.claude/settings.json
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..2d396e6
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/.claude/settings.json
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,7 @@
+{
+  "permissions": {
+    "allow": [
+      "Bash(venv/bin/python -m pytest *)"
+    ]
+  }
+}
