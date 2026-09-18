39710e4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 39710e4
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 11:04:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #306 : correction padding-bottom panneau France (40px -> 20px, suite #304)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 20c8639..e2126f8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/accueil.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 400 (22 ligne(s)) dans l'ancienne version → ligne 400 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -400,22 +400,19 @@ body.mode-belgicisme .parties-en-cours:has(.vide) {
    Belgicisme (le panneau y est un pseudo-élément flottant, pas de bord de
    fenêtre proche) mais qui aurait recréé l'écart une fois les deux marges
    externes comparées.
-   `padding-bottom` porté à 40px (issue #304) : en Belgicisme, le panneau visible
-   est `.container::before`, qui déborde de 20px sous le bord réel de
-   `.container` (`bottom: -20px` ci-dessus) — au 20px de padding hérité de
-   `.container` s'ajoutent donc 20px, soit 40px d'air sous le dernier bouton
-   avant le bord du panneau. En France, `.container` EST le panneau (peint
-   directement, pas de pseudo-élément) : ses seuls 20px de padding hérités
-   laissaient le panneau s'arrêter net sous les boutons, sans l'équivalent
-   des 20px de débord belge. 40px explicite ici recrée la même hauteur
-   perçue dans les deux modes. */
+   `padding-bottom` porté un temps à 40px (issue #304) sur l'hypothèse erronée
+   qu'il fallait compenser ici le même débord de 20px que `.container::before`
+   ajoute en Belgicisme. Or en France, `.container` EST directement le
+   panneau peint (pas de pseudo-élément débordant à compenser) : les 20px de
+   padding hérités de `.container` suffisent déjà à égaler la hauteur perçue
+   du panneau Belgicisme. Ramené à 20px implicite (issue #306). */
 body:not(.mode-belgicisme) .container {
     background: white;
     border-radius: 16px;
     overflow: hidden;
     margin-top: 1.5rem;
     margin-bottom: 1.5rem;
-    padding-bottom: 40px;
+    padding-bottom: 20px;
 }
 
 /* En-tête */
