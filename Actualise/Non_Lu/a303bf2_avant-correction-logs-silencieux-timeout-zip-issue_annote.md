a303bf2

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a303bf2
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 17:54:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-correction-logs-silencieux-timeout-zip-issue-31

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..01eacad
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (3 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,3 @@
+## TACHES POUR PLUS TARD
+----------------------------
+Backlog Actualise — permettre des noms d'assets versionnés (scrabble-v3.zip au lieu de scrabble.zip), en faisant construire le nom dynamiquement par Actualise à partir du numéro de build, ou en interrogeant la liste des assets de la Release GitHub.
