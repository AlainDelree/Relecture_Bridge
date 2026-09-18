# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 31a5ea670a0413cbf31b898d69a73aba95ac6d6e
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 20:45:13 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #226 : le toast "Coup joué (+X points)" disparaît automatiquement (timeout 3 s)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7ba41be..6c8d7bd 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.js
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 616 (9 ligne(s)) dans l'ancienne version → ligne 616 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -616,9 +616,27 @@ document.addEventListener('DOMContentLoaded', async () => {
     }
 
     /** Message de retour des actions de tour (issue #101), sous les boutons. */
-    function afficherMessageCoup(texte, type) {
+    let messageCoupTimer = null;
+    function afficherMessageCoup(texte, type, dureeMs) {
+        if (messageCoupTimer) {
+            clearTimeout(messageCoupTimer);
+            messageCoupTimer = null;
+        }
         messageCoup.textContent = texte || '';
         messageCoup.className = 'message-coup' + (texte ? ' ' + (type || 'info') : '');
+        // Auto-effacement optionnel (issue #226) : le message « Coup joué » est posé
+        // APRÈS le rendu déclenché par le push d'état (qui, passé au tour de
+        // l'ordinateur, a déjà vidé la zone via majActionsTour). Plus aucun rendu ne
+        // survient ensuite tant qu'aucun bouton n'est cliqué, si bien que le message
+        // resterait affiché indéfiniment. On le fait disparaître de lui-même, comme
+        // le toast « +N points » du joueur humain (3 s, cf. afficherToastPoints).
+        if (texte && dureeMs) {
+            messageCoupTimer = setTimeout(() => {
+                messageCoup.textContent = '';
+                messageCoup.className = 'message-coup';
+                messageCoupTimer = null;
+            }, dureeMs);
+        }
     }
 
     /** Message éphémère de pose (issue #90), affiché en surimpression. */
# ── Zone modifiée : ligne 1407 (7 ligne(s)) dans l'ancienne version → ligne 1425 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1407,7 +1425,7 @@ document.addEventListener('DOMContentLoaded', async () => {
         }
         if (res && res.succes) {
             const points = res.points != null ? res.points : 0;
-            afficherMessageCoup(`Coup joué (+${points} point${points > 1 ? 's' : ''}).`, 'succes');
+            afficherMessageCoup(`Coup joué (+${points} point${points > 1 ? 's' : ''}).`, 'succes', 3000);
             // Python rediffuse l'état (nouveau tour) : le rendu suit via le push.
         } else {
             afficherMessageCoup((res && res.erreur) ? res.erreur : 'Coup refusé.', 'erreur');
