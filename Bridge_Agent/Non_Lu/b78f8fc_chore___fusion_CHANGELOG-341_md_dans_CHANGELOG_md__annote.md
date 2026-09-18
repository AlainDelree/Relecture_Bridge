b78f8fc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b78f8fc
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 23:48:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    chore : fusion CHANGELOG-341.md dans CHANGELOG.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-341.md b/CHANGELOG-341.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7455fe1..0000000
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG-341.md
# ── Version APRÈS ce commit.
+++ /dev/null
# ── Zone modifiée : ligne 1 (7 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,7 +0,0 @@
-## 2 août 2026 — issue #341
-
-Ajout dans `TACHES.md`, juste après le bloc d'en-tête, d'une section
-« Worktrees en production — points de surveillance » listant les deux
-limites connues restantes après correction de #340 : pas d'alerte sur
-l'accumulation de worktrees (nettoyage manuel requis) et
-`issues_en_cours` sans verrou explicite inter-process.
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 183ba93..0f8bac3 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,14 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #341
+
+Ajout dans `TACHES.md`, juste après le bloc d'en-tête, d'une section
+« Worktrees en production — points de surveillance » listant les deux
+limites connues restantes après correction de #340 : pas d'alerte sur
+l'accumulation de worktrees (nettoyage manuel requis) et
+`issues_en_cours` sans verrou explicite inter-process.
+
 ## 2 août 2026 — issue #342
 
 §11 « Conventions de code » de `BRIDGE_AGENT_DOC.md` : deux notes ajoutées
