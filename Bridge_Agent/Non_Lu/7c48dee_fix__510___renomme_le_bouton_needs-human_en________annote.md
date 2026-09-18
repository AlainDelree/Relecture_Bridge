7c48dee

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7c48dee
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 30 17:00:25 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #510 : renomme le bouton needs-human en '🔄 Retirer needs-human' pour lever l'ambiguïté avec 'Relancer watcher CCL'

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ad41e25..3c2a949 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2285 (7 ligne(s)) dans l'ancienne version → ligne 2285 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2285,7 +2285,7 @@ function rendrePanneauLateralActions() {
   // réutilisée à l'identique, aucune nouvelle route.
   if (!ferme && nomsLabels.includes('needs-human')) {
     html += '<button onclick="relancerIssue(\'' + escapeHtml(nom) + '\', '
-          + Number(numero) + ')">🔄 Relancer</button>';
+          + Number(numero) + ')">🔄 Retirer needs-human</button>';
     html += '<button class="danger-plein" onclick="fermerIssue(\'' + escapeHtml(nom) + '\', '
           + Number(numero) + ')">✖ Fermer l\'issue</button>';
   }
# ── Zone modifiée : ligne 3756 (8 ligne(s)) dans l'ancienne version → ligne 3756 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3756,8 +3756,8 @@ async function relancerIssue(nom, numero) {
     alert('Dépôt GitHub introuvable pour le projet « ' + nom + ' » — impossible de relancer.');
     return;
   }
-  if (!confirm("Relancer l'issue #" + numero + " ?\n\n"
-             + "Le label needs-human sera retiré : l'issue sera reprise par le watcher "
+  if (!confirm("Retirer le label needs-human de l'issue #" + numero + " ?\n\n"
+             + "L'issue sera reprise par le watcher "
              + "à son prochain cycle (s'il tourne).")) return;
 
   let resultat;
