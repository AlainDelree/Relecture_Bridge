faef59a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit faef59a
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 08:52:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #323 : animation pioche — animer toutes les lettres du nouveau chevalet (suite #322)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b076425..19a19ef 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.js
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1051 (8 ligne(s)) dans l'ancienne version → ligne 1051 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1051,8 +1051,7 @@ document.addEventListener('DOMContentLoaded', async () => {
             // rebâtit directement pour rester synchrone avec Python).
             const arrivees = (premierAppel || animationPiocheEnCours)
                 ? []
-                : nouvellesLettresArrivees(anciennesLettres,
-                                           etatChevalet.lettres || []);
+                : etatChevalet.lettres || [];
             if (arrivees.length > 0) {
                 animerNouvellesLettres(arrivees).then(() => {
                     reconstruirePanneau();
