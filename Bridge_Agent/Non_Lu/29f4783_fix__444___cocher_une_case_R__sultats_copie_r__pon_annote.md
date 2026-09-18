29f4783

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 29f4783
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 19:36:48 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #444 : cocher une case Résultats copie réponse+diff de cette issue

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5af95c2..d533348 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1211 (6 ligne(s)) dans l'ancienne version → ligne 1211 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1211,6 +1211,12 @@ function basculerCocheResultat(event, projet, numero) {
   // Pastilles filtre projet (issue #383) : comptent les issues décochées,
   // donc chaque bascule de case doit rafraîchir immédiatement leur compte.
   majPastillesFiltres();
+  // Cocher la case déclenche, pour cette SEULE issue, la même copie
+  // réponse+diff que le badge « All » (issue #444). Décocher ne fait rien
+  // (pas de « décopie »). copierToutEtDiffDepuisBadge gère déjà sans erreur
+  // le cas d'une issue sans réponse/commit (garde « copie vide », feedback
+  // ⚠/∅) : appel sans condition sur l'état de l'issue.
+  if (coche) copierToutEtDiffDepuisBadge(event, projet, numero);
 }
 
 // Construit l'élément DOM d'UNE ligne d'issue (case à cocher, pastille,
