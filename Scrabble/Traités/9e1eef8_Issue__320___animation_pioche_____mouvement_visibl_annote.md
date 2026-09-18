9e1eef8

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9e1eef8
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 08:40:24 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #320 : animation pioche — mouvement visible vers le chevalet (suite #319)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b0b30e1..48036ee 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 2248 (7 ligne(s)) dans l'ancienne version → ligne 2248 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2248,7 +2248,7 @@ body.jeu-en-init #message-plateau {
     color: var(--tuile-texte);
     box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
     animation: pioche-tuile-apparition 0.25s ease-out both;
-    transition: transform 0.4s ease-in, opacity 0.4s ease-in;
+    transition: transform 0.7s ease-in, opacity 0.5s ease-in 0.2s;
 }
 
 .pioche-tuile.joker {
# ── Zone modifiée : ligne 2273 (7 ligne(s)) dans l'ancienne version → ligne 2273 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2273,7 +2273,7 @@ body.jeu-en-init #message-plateau {
 /* Sortie vers le chevalet : ajoutée par le JS 900ms après l'apparition,
    déclenche la transition ci-dessus (transform/opacity) sur 400ms. */
 .pioche-overlay-sortie .pioche-tuile {
-    transform: translate(-45vw, 40vh) scale(0.4);
+    transform: translate(-80vw, 60vh) scale(0.15);
     opacity: 0;
 }
 
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index a975a4a..19a19ef 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1012 (7 ligne(s)) dans l'ancienne version → ligne 1012 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1012,7 +1012,7 @@ document.addEventListener('DOMContentLoaded', async () => {
                 overlay.addEventListener('transitionend', terminer, { once: true });
                 // Filet de sécurité si l'événement de transition ne se déclenche
                 // pas (calque sans tuile, focus perdu…).
-                setTimeout(terminer, 500);
+                setTimeout(terminer, 800);
             }, 900);
         });
     }
