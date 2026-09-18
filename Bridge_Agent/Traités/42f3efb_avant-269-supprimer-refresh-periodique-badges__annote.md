42f3efb

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 42f3efb
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 04:56:04 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-269-supprimer-refresh-periodique-badges

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c455cb9..98ae8cd 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1271 (6 ligne(s)) dans l'ancienne version → ligne 1271 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1271,6 +1271,7 @@ function formaterDuree(s) {
 // Récupère, pour tous les projets, les débuts de traitement + timeouts des
 // issues ouvertes, puis rafraîchit immédiatement les badges.
 async function chargerTimingIssues() {
+  console.error('[DEBUG-269-TRACE]', new Error().stack);
   const noms = nomsProjetsDisponibles();
   // On repart de l'état COURANT, pas d'un map vide (issue #190). Avant, chaque
   // appel reconstruisait le map à partir de zéro : dès qu'un fetch
