94fc196

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 94fc196
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 14:08:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #243 : toast de fin d'échange/passe visible immédiatement
    
    Le message #message-coup ("Tour passé.", "Lettres échangées. Tour passé.",
    "Toutes vos lettres ont été remises dans le sac. Tour passé.") vivait dans
    #zone-actions-droite, masqué (hidden) pendant le tour de l'ordinateur : le
    message existait dans le DOM mais restait invisible jusqu'au tour humain
    suivant, ou était écrasé par l'action suivante du joueur (même phénomène que #226).
    
    - jeu.html : #message-coup remonté hors des zones masquées, en enfant direct
      de la <section class=zone-actions-humain>.
    - jeu.css : contexte de positionnement (position: relative) déplacé de
      .zone-actions-droite vers .zone-actions-humain (jamais masquée).
    - jeu.js : auto-effacement (4000 ms) ajouté aux trois messages de fin d'action,
      cohérent avec le toast "Coup joué" (#226).
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 489a81e..eda11b6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 345 (6 ligne(s)) dans l'ancienne version → ligne 345 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -345,6 +345,11 @@ body {
 .zone-actions-humain {
     gap: 10px;
     flex: 0 0 auto;
+    /* Contexte de positionnement du message de retour (#message-coup), issue #243.
+       Le message est désormais un enfant direct de cette section (et non plus du
+       groupe « pose » #zone-actions-droite, masqué pendant le tour de l'ordinateur) :
+       il s'ancre en surimpression au bord haut de la section, jamais masquée. */
+    position: relative;
 }
 
 /* --------------------------------------------------------------------------- */
# ── Zone modifiée : ligne 1776 (12 ligne(s)) dans l'ancienne version → ligne 1781 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1776,12 +1781,10 @@ body {
     display: none;
 }
 
-/* Zone de DROITE (issue #160) : contexte de positionnement du message de retour
-   (#message-coup), sorti du flux et ancré en surimpression au-dessus des boutons
-   « Vérifier et calculer » / « Jouer » (voir .message-coup ci-dessous). */
-.zone-actions-droite {
-    position: relative;
-}
+/* Zone de DROITE (issue #160) : groupe « pose » (Annuler / Vérifier / Jouer).
+   Le contexte de positionnement du message de retour (#message-coup) a été
+   remonté sur .zone-actions-humain (issue #243) : ce groupe est masqué pendant
+   le tour de l'ordinateur, ce qui emportait le message avec lui. */
 
 /* Flux d'échange partiel (issue #138) : les deux boutons (valider / annuler)
    apparaissent côte à côte à la place de l'échange complet pendant la sélection. */
# ── Zone modifiée : ligne 1799 (8 ligne(s)) dans l'ancienne version → ligne 1802 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1799,8 +1802,9 @@ body {
    collé au bord bas de la fenêtre plateau maximisée : à la résolution cible du
    portable de test (~1280×728), il débordait sous le bord visible et était
    partiellement coupé (le pied de page + le plateau saturaient déjà la hauteur).
-   On le sort du flux et on l'ancre juste AU-DESSUS de la zone d'actions de droite
-   (issue #160), aligné à droite sur « Vérifier et calculer »/« Jouer » : il reste
+   On le sort du flux et on l'ancre juste AU-DESSUS de la zone d'actions humaine
+   (issue #160 ; ancrage remonté du groupe « pose » à la section entière en #243),
+   aligné à droite sur « Vérifier et calculer »/« Jouer » : il reste
    clairement associé à ces boutons, n'allonge plus le pied de page (donc ne pousse
    plus rien sous le bord) et reste entièrement visible sans redimensionner ni
    défiler. Un message
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.html b/src/scrabble/ui/web/jeu.html
# (index — ignorable)
index 512abc2..d2ae398 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.html
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.html
# ── Zone modifiée : ligne 220 (8 ligne(s)) dans l'ancienne version → ligne 220 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -220,8 +220,7 @@
                  bascule leur attribut [hidden] pendant le seul tour humain. -->
             <section class="zone-gauche zone-actions-humain" aria-label="Vos actions">
                 <!-- Groupe « pose » (ex-zone de droite, issue #160) : Annuler /
-                     Vérifier et calculer / Jouer. Le message de retour dédié
-                     (#message-coup) reste ancré à cette zone (voir jeu.css). -->
+                     Vérifier et calculer / Jouer. -->
                 <div id="zone-actions-droite" class="zone-actions zone-actions-droite" hidden>
                     <button id="btn-annuler" class="btn btn-secondaire" disabled>
                         ✗ Annuler
# ── Zone modifiée : ligne 233 (7 ligne(s)) dans l'ancienne version → ligne 232 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -233,7 +232,6 @@
                     <button id="btn-valider" class="btn btn-primaire" disabled>
                         ✓ Jouer
                     </button>
-                    <p id="message-coup" class="message-coup" role="status" aria-live="polite"></p>
                 </div>
 
                 <!-- Groupe « échange / passe » (ex-zone de gauche, issue #160) :
# ── Zone modifiée : ligne 263 (6 ligne(s)) dans l'ancienne version → ligne 261 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -263,6 +261,16 @@
                         ⏭ Passer son tour
                     </button>
                 </div>
+
+                <!-- Message de retour dédié (#message-coup, issue #101). Il est
+                     rattaché à la SECTION (et non plus au groupe « pose »
+                     #zone-actions-droite) : ce dernier est masqué (hidden) pendant
+                     le tour de l'ordinateur, ce qui rendait le message d'échange /
+                     de passe invisible jusqu'au tour humain suivant (issue #243,
+                     même phénomène que #226). Placé ici, hors des zones masquées,
+                     il s'affiche immédiatement. Reste ancré en surimpression au
+                     bord haut de la zone d'actions (voir .message-coup, jeu.css). -->
+                <p id="message-coup" class="message-coup" role="status" aria-live="polite"></p>
             </section>
 
         </aside>
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index 2fcd4f3..d3a817f 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 90 (9 ligne(s)) dans l'ancienne version → ligne 90 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,9 +90,10 @@ document.addEventListener('DOMContentLoaded', async () => {
     // fenêtre chevalet, désormais réparties de part et d'autre de la fiche du joueur
     // humain (gauche : échange + passer ; droite : annuler + vérifier + jouer). Les
     // deux zones ne sont visibles/actives que pendant le tour du joueur humain (voir
-    // majActionsTour). Le message de retour dédié (#message-coup) s'affiche en
-    // surimpression au-dessus des boutons de droite, distinct du message éphémère de
-    // pose (#message-plateau). L'ancien cadre d'attente d'un tour d'ordinateur
+    // majActionsTour). Le message de retour dédié (#message-coup) est rattaché à la
+    // SECTION parente, hors des zones masquées (issue #243), pour rester visible même
+    // pendant le tour de l'ordinateur ; il s'affiche en surimpression au-dessus des
+    // boutons, distinct du message éphémère de pose (#message-plateau). L'ancien cadre d'attente d'un tour d'ordinateur
     // (#zone-attente-ia et son message) est supprimé (issue #160) : le tour d'un
     // ordinateur se déclenche via le bouton « ▶ Jouer » de sa fiche (issue #149).
     const zoneActionsGauche = document.getElementById('zone-actions-gauche');
# ── Zone modifiée : ligne 1484 (7 ligne(s)) dans l'ancienne version → ligne 1485 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1484,7 +1485,13 @@ document.addEventListener('DOMContentLoaded', async () => {
             return;
         }
         if (res && res.succes) {
-            afficherMessageCoup('Tour passé.', 'succes');
+            // Auto-effacement (issue #243, cohérent avec #226) : le message est posé
+            // APRÈS le push d'état (passé au tour de l'ordinateur, majActionsTour a
+            // masqué les boutons et vidé la zone). Sans minuterie il resterait figé
+            // jusqu'au prochain clic. Il vit désormais hors du conteneur masqué
+            // (#message-coup remonté sur la section, cf. jeu.html) : il est donc
+            // visible immédiatement, puis disparaît de lui-même.
+            afficherMessageCoup('Tour passé.', 'succes', 4000);
             // Python rediffuse l'état (tour suivant ou fin de partie) : le rendu
             // suit via le push.
         } else {
# ── Zone modifiée : ligne 1512 (7 ligne(s)) dans l'ancienne version → ligne 1519 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1512,7 +1519,9 @@ document.addEventListener('DOMContentLoaded', async () => {
             return;
         }
         if (res && res.succes) {
-            afficherMessageCoup('Toutes vos lettres ont été remises dans le sac. Tour passé.', 'succes');
+            // Idem « Tour passé » : visible tout de suite (message hors du conteneur
+            // masqué) puis auto-effacé (issue #243).
+            afficherMessageCoup('Toutes vos lettres ont été remises dans le sac. Tour passé.', 'succes', 4000);
         } else {
             afficherMessageCoup((res && res.erreur) || 'Échange impossible.', 'erreur');
             majActionsTour();
# ── Zone modifiée : ligne 1553 (7 ligne(s)) dans l'ancienne version → ligne 1562 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1553,7 +1562,9 @@ document.addEventListener('DOMContentLoaded', async () => {
             return;
         }
         if (res && res.succes) {
-            afficherMessageCoup('Lettres échangées. Tour passé.', 'succes');
+            // Idem « Tour passé » : visible tout de suite (message hors du conteneur
+            // masqué) puis auto-effacé (issue #243).
+            afficherMessageCoup('Lettres échangées. Tour passé.', 'succes', 4000);
         } else {
             afficherMessageCoup((res && res.erreur) || 'Échange impossible.', 'erreur');
             majActionsTour();
