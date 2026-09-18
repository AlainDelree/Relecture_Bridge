174d295

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 174d295
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 09:33:33 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #327 : animation pioche — forcer reflow avant transition de sortie (suite #326)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 317c806..5ce06fe 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.js
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1008 (10 ligne(s)) dans l'ancienne version → ligne 1008 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1008,10 +1008,10 @@ document.addEventListener('DOMContentLoaded', async () => {
                 resolve();
             };
             setTimeout(() => {
+                // Forcer le reflow pour que la transition CSS se déclenche
+                // correctement après l'animation d'apparition.
+                overlay.getBoundingClientRect();
                 overlay.classList.add('pioche-overlay-sortie');
-                overlay.addEventListener('transitionend', terminer, { once: true });
-                // Filet de sécurité si l'événement de transition ne se déclenche
-                // pas (calque sans tuile, focus perdu…).
                 setTimeout(terminer, 800);
             }, 900);
         });
