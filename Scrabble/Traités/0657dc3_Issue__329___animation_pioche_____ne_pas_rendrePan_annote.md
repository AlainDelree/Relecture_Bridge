0657dc3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0657dc3
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 09:54:15 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #329 : animation pioche — ne pas rendrePanneau pendant l'animation (suite #328)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d58c1ce..ed327d8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.js
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1010 (6 ligne(s)) dans l'ancienne version → ligne 1010 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1010,6 +1010,7 @@ document.addEventListener('DOMContentLoaded', async () => {
         // Le panneau n'est reconstruit qu'au changement de tour ou de contenu du
         // chevalet (échange / nouveau tirage), pas à chaque pose (les lettres ne
         // changent pas en posant).
+        let animationLancee = false;
         const sig = signatureLettres(etatChevalet.lettres);
         if (sig !== panneauSignature) {
             panneauSignature = sig;
# ── Zone modifiée : ligne 1024 (6 ligne(s)) dans l'ancienne version → ligne 1025 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1024,6 +1025,7 @@ document.addEventListener('DOMContentLoaded', async () => {
                 ? []
                 : (etatChevalet.lettres_pioches || []);
             if (arrivees.length > 0) {
+                animationLancee = true;
                 animerNouvellesLettres(arrivees).then(() => {
                     reconstruirePanneau();
                     rendrePanneau();
# ── Zone modifiée : ligne 1039 (7 ligne(s)) dans l'ancienne version → ligne 1041 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1039,7 +1041,9 @@ document.addEventListener('DOMContentLoaded', async () => {
             panneauSelection = null;
         }
 
-        rendrePanneau();
+        if (!animationLancee) {
+            rendrePanneau();
+        }
     }
     window.appliquerEtatChevalet = appliquerEtatChevalet;
 
