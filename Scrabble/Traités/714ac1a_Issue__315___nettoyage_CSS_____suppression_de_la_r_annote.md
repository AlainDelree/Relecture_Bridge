714ac1a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 714ac1a
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 07:06:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #315 : nettoyage CSS — suppression de la règle morte .joueur-icone (suite #314)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e2126f8..3d3d76c 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/accueil.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 956 (13 ligne(s)) dans l'ancienne version → ligne 956 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -956,13 +956,6 @@ body.mode-belgicisme .zone-centrale > *:not(.bande-tricolore) {
     border-left: 4px solid var(--couleur-ordinateur);
 }
 
-.joueur-icone {
-    font-size: 1.3rem;
-    margin-right: 10px;
-    width: 28px;
-    text-align: center;
-}
-
 /* Portrait de l'avatar configuré du joueur humain (issue #148) : même gabarit
    que l'icône générique (28 px, marge droite identique) pour ne pas décaler le
    nom, avec le rendu rond « pastille » repris des panneaux de l'écran de jeu. */
