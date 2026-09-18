ecb9a1a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ecb9a1a
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 08:41:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #321 : animation pioche — restaurer diff + guard mon_tour (suite #319)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 19a19ef..13ef2f8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.js
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1049 (9 ligne(s)) dans l'ancienne version → ligne 1049 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1049,9 +1049,11 @@ document.addEventListener('DOMContentLoaded', async () => {
             // premier affichage (rien n'est « arrivé », c'est l'état initial), ni
             // si une animation est déjà en cours (mise à jour rapprochée : on
             // rebâtit directement pour rester synchrone avec Python).
-            const arrivees = (premierAppel || animationPiocheEnCours)
+            const arrivees = (premierAppel || animationPiocheEnCours
+                              || !etatChevalet.mon_tour)
                 ? []
-                : etatChevalet.lettres || [];
+                : nouvellesLettresArrivees(anciennesLettres,
+                                           etatChevalet.lettres || []);
             if (arrivees.length > 0) {
                 animerNouvellesLettres(arrivees).then(() => {
                     reconstruirePanneau();
