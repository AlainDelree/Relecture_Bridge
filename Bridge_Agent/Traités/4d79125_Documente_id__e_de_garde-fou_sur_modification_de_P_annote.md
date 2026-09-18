4d79125

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4d79125
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 31 20:12:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Documente idée de garde-fou sur modification de PERIMETRE (#298)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d5e19bb..b135f48 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 246 (3 ligne(s)) dans l'ancienne version → ligne 246 (35 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -246,3 +246,35 @@ d'attendre l'échec des 3 tentatives pour le découvrir.
 
 **Statut** : idée en attente, pas de développement lancé. Identifiée lors
 de l'incident du 29/07/2026 (cf. issue #279).
+
+---
+
+## Garde-fou technique sur la modification de PERIMETRE
+
+**Contexte** : PERIMETRE (`configs/*.conf`, ex. `ccw.conf`) est un simple
+champ texte lu par `watcher.py` et injecté tel quel dans le prompt de
+CCL/CCW. Aucun garde-fou technique n'existe sur sa modification — une
+issue pourrait l'élargir ou le restreindre silencieusement (ex. à `C:\`
+entier, ou en retirant le partage lui-même), sans que rien ne le
+signale comme un événement particulier. Le 31/07/2026, le périmètre
+CCW a dû être élargi manuellement (via notepad) pour débloquer un
+build légitime — l'usage de PERIMETRE lui-même n'est pas en cause. Le
+risque identifié porte sur l'absence de contrôle quand une modification
+de cette valeur survient via une issue plutôt qu'à la main.
+
+À noter : le respect du périmètre par CCL/CCW pendant l'exécution est
+déjà appliqué uniquement par consigne textuelle du prompt (non
+déterministe, cf. issues #290/#291 qui l'ont franchi vs #292 qui s'est
+arrêtée). La modification de la valeur elle-même est un problème
+distinct et actuellement sans aucun garde-fou, pas même textuel.
+
+**Idée** : avant toute action qui écrirait une nouvelle valeur de
+PERIMETRE dans `configs/*.conf`, `watcher.py` devrait détecter le
+changement (comparaison ancienne/nouvelle valeur) et refuser
+l'application automatique — exiger une confirmation manuelle explicite
+(ex. fichier de confirmation posé à la main, ou variable
+d'environnement) plutôt que de laisser une issue modifier
+silencieusement son propre périmètre d'exécution.
+
+**Statut** : idée en attente, pas de développement lancé. Diagnostic
+établi le 31/07/2026 (issue #298).
