9693ae4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9693ae4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 12:09:35 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-319-retrait-taches-perimetre

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 000023a..3687802 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,18 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #319
+
+`TACHES.md` : retrait de l'entrée de backlog « Garde-fou technique sur
+la modification de PERIMETRE » (diagnostic du 31/07/2026, issue #298),
+désormais implémentée — sous une forme différente de l'idée initiale
+(détection/confirmation) : décision finale du 02/08/2026 d'interdire
+purement et simplement toute modification de `configs/*.conf` par
+CCL/CCW (issue #318, commit 65e81c5). Suppression simple, même
+convention que les issues #310/#312. Reste du fichier inchangé,
+notamment « Champ de recherche texte dans l'onglet Résultats de
+new_issue.py » (#317), toujours en attente sans implémentation.
+
 ## 2 août 2026 — issue #318
 
 Interdiction totale de modification de `configs/*.conf` par CCL/CCW, y
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index 51acac2..54996a2 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 187 (38 ligne(s)) dans l'ancienne version → ligne 187 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -187,38 +187,6 @@ d'audit Scrabble le 24/07/2026.
 
 ---
 
-## Garde-fou technique sur la modification de PERIMETRE
-
-**Contexte** : PERIMETRE (`configs/*.conf`, ex. `ccw.conf`) est un simple
-champ texte lu par `watcher.py` et injecté tel quel dans le prompt de
-CCL/CCW. Aucun garde-fou technique n'existe sur sa modification — une
-issue pourrait l'élargir ou le restreindre silencieusement (ex. à `C:\`
-entier, ou en retirant le partage lui-même), sans que rien ne le
-signale comme un événement particulier. Le 31/07/2026, le périmètre
-CCW a dû être élargi manuellement (via notepad) pour débloquer un
-build légitime — l'usage de PERIMETRE lui-même n'est pas en cause. Le
-risque identifié porte sur l'absence de contrôle quand une modification
-de cette valeur survient via une issue plutôt qu'à la main.
-
-À noter : le respect du périmètre par CCL/CCW pendant l'exécution est
-déjà appliqué uniquement par consigne textuelle du prompt (non
-déterministe, cf. issues #290/#291 qui l'ont franchi vs #292 qui s'est
-arrêtée). La modification de la valeur elle-même est un problème
-distinct et actuellement sans aucun garde-fou, pas même textuel.
-
-**Idée** : avant toute action qui écrirait une nouvelle valeur de
-PERIMETRE dans `configs/*.conf`, `watcher.py` devrait détecter le
-changement (comparaison ancienne/nouvelle valeur) et refuser
-l'application automatique — exiger une confirmation manuelle explicite
-(ex. fichier de confirmation posé à la main, ou variable
-d'environnement) plutôt que de laisser une issue modifier
-silencieusement son propre périmètre d'exécution.
-
-**Statut** : idée en attente, pas de développement lancé. Diagnostic
-établi le 31/07/2026 (issue #298).
-
----
-
 ## Champ de recherche texte dans l'onglet Résultats de new_issue.py
 
 **Contexte** : le 02/08/2026, une issue a été envoyée deux fois par
