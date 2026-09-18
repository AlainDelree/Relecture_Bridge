# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 21867f53f58257299ed9937c2bbadbf831d5576e
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 09:33:38 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Test du hook de relecture

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/README.md b/README.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2d9884b..1bc64c4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/README.md
# ── Version APRÈS ce commit.
+++ b/README.md
# ── Zone modifiée : ligne 1 (1 ligne(s)) dans l'ancienne version → ligne 1 (2 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1 +1,2 @@
 # test hook
+# test hook
# (diff du fichier suivant)
diff --git a/README2.md b/README2.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..2d9884b
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/README2.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (1 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1 @@
+# test hook
