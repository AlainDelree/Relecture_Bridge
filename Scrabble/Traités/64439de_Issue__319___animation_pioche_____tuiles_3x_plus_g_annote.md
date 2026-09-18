64439de

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 64439de
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 08:30:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #319 : animation pioche — tuiles 3x plus grandes, toutes les lettres reçues

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f26bdbf..b0b30e1 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 2225 (14 ligne(s)) dans l'ancienne version → ligne 2225 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2225,14 +2225,15 @@ body.jeu-en-init #message-plateau {
     align-items: center;
     justify-content: center;
     gap: 12px;
+    flex-wrap: wrap;
     pointer-events: none;
 }
 
 /* Tuiles nettement plus grandes que celles du chevalet (.panneau-case, 40×44px)
    pour bien marquer l'arrivée des nouvelles lettres. */
 .pioche-tuile {
-    width: 72px;
-    height: 80px;
+    width: 120px;
+    height: 132px;
     flex: 0 0 auto;
     display: flex;
     align-items: center;
# ── Zone modifiée : ligne 2240 (7 ligne(s)) dans l'ancienne version → ligne 2241 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2240,7 +2241,7 @@ body.jeu-en-init #message-plateau {
     position: relative;
     border-radius: 6px;
     font-weight: 700;
-    font-size: 2.2rem;
+    font-size: 3.5rem;
     text-transform: uppercase;
     background: var(--tuile-fond);
     border: 2px solid var(--tuile-bordure);
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index da84a5f..a975a4a 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1051 (7 ligne(s)) dans l'ancienne version → ligne 1051 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1051,7 +1051,7 @@ document.addEventListener('DOMContentLoaded', async () => {
             // rebâtit directement pour rester synchrone avec Python).
             const arrivees = (premierAppel || animationPiocheEnCours)
                 ? []
-                : nouvellesLettresArrivees(anciennesLettres, etatChevalet.lettres);
+                : etatChevalet.lettres || [];
             if (arrivees.length > 0) {
                 animerNouvellesLettres(arrivees).then(() => {
                     reconstruirePanneau();
