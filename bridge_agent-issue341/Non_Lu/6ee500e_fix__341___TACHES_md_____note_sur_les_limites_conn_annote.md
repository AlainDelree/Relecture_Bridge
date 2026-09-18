6ee500e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6ee500e
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 23:39:41 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #341 : TACHES.md — note sur les limites connues des worktrees en production

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-341.md b/CHANGELOG-341.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..7455fe1
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-341.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,7 @@
+## 2 août 2026 — issue #341
+
+Ajout dans `TACHES.md`, juste après le bloc d'en-tête, d'une section
+« Worktrees en production — points de surveillance » listant les deux
+limites connues restantes après correction de #340 : pas d'alerte sur
+l'accumulation de worktrees (nettoyage manuel requis) et
+`issues_en_cours` sans verrou explicite inter-process.
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index 0e9da13..dc30e54 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 5 (6 ligne(s)) dans l'ancienne version → ligne 5 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,6 +5,15 @@ Alain peut modifier ce fichier directement, sans passer par une issue.
 
 ---
 
+## Worktrees en production — points de surveillance
+
+**Contexte** : après correction de #340, deux limites connues restent
+sur le mécanisme de parallélisation des issues mode_write via git
+worktrees (cf. `WORKTREES.md`) :
+
+- Pas d'alerte sur l'accumulation de worktrees (nettoyage manuel requis).
+- `issues_en_cours` sans verrou explicite inter-process.
+
 ## Projet dédié à la communication CCL ↔ CCW
 
 **Contexte** : aujourd'hui les issues Windows passent par le projet
