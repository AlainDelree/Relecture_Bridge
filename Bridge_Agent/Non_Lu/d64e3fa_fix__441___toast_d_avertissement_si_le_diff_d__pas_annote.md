d64e3fa

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d64e3fa
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 18:15:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #441 : toast d'avertissement si le diff dépasse 1000 lignes au clic sur All

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index af5ee8b..5af95c2 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 3299 (6 ligne(s)) dans l'ancienne version → ligne 3299 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3299,6 +3299,14 @@ async function copierToutEtDiffDepuisBadge(event, nom, numero) {
   // silencieuse, pas de ✓ trompeur.
   if (texteCopieVide(texte)) { feedbackBadgeVide(badge, original, titreOriginal); return; }
 
+  // Avertissement diff volumineux (issue #441) : Claude.ai tronque silencieusement
+  // les collages trop longs. La copie a quand même lieu — le toast est purement
+  // informatif, sans bouton de confirmation.
+  const nbLignes = texte.split('\n').length;
+  if (nbLignes > 1000) {
+    afficherToast('⚠ Diff volumineux (' + nbLignes + ' lignes) — Claude.ai pourrait ne pas le lire');
+  }
+
   // Copie dans le presse-papier (fallback silencieux si indisponible / non-HTTPS).
   if (navigator.clipboard && navigator.clipboard.writeText) {
     try {
