# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ca33c58d44e2303c1399df9e309649152cc6e156
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 23:51:58 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #21 : ghost-piece via transform:translate3d (P3, GPU) + cache des mesures de grille dans dragState (P4, fin du layout thrashing pendant le drag)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-jeu.html b/bloc-jeu.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c630b6e..91473ce 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-jeu.html
# ── Version APRÈS ce commit.
+++ b/bloc-jeu.html
# ── Zone modifiée : ligne 455 (6 ligne(s)) dans l'ancienne version → ligne 455 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -455,6 +455,13 @@
 
   .ghost-piece{
     position:fixed;
+    /* Origine fixée en (0,0) : le positionnement se fait ensuite via
+       transform:translate3d dans positionGhost (P3, issue #21), qui reste
+       sur le compositeur GPU au lieu de déclencher un reflow comme le
+       feraient left/top. */
+    left:0;
+    top:0;
+    will-change:transform;
     pointer-events:none;
     display:grid;
     gap:3px;
# ── Zone modifiée : ligne 1756 (8 ligne(s)) dans l'ancienne version → ligne 1763 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1756,8 +1763,24 @@
 
     const lift = e.pointerType === 'touch' ? 90 : 0;
 
+    // P4 (issue #21) : on mesure la grille UNE SEULE FOIS ici, à la prise de
+    // la pièce (avant le premier mouvement), pour éviter que updateDropTarget
+    // ne rappelle getBoundingClientRect() et ne recalcule cellSize à chaque
+    // pointermove. Combiné à P3 (écriture via transform), cela supprime le
+    // reflow forcé (layout thrashing) provoqué par la lecture juste après
+    // l'écriture à chaque pixel de déplacement.
+    // Cas limite documenté (non géré activement, jugé marginal par l'audit) :
+    // un redimensionnement de la fenêtre PENDANT un glisser en cours rendrait
+    // gridRect/cellSize obsolètes jusqu'à la fin de ce glisser. On ne pose
+    // volontairement pas de listener resize pour invalider le cache : la
+    // grille ne bouge ni ne change de taille pendant un glisser normal.
+    const gridRect = gridEl.getBoundingClientRect();
+    const gridPadding = 6;
+    const cellSize = (gridRect.width - gridPadding*2) / SIZE;
+
     dragState = {
       piece, pieceEl, ghost, cellPx,
+      gridRect, gridPadding, cellSize,
       // Point d'ancrage naturel : position réelle du pointeur par rapport au
       // coin haut-gauche de la pièce, pour que le point attrapé reste sous le
       // curseur pendant tout le déplacement (pas de recentrage à la prise).
# ── Zone modifiée : ligne 1783 (8 ligne(s)) dans l'ancienne version → ligne 1806 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1783,8 +1806,14 @@
 
   function positionGhost(x,y){
     const {ghost, offsetX, offsetY, lift} = dragState;
-    ghost.style.left = (x - offsetX) + 'px';
-    ghost.style.top = (y - offsetY - lift) + 'px';
+    // P3 (issue #21) : positionnement via transform:translate3d plutôt que
+    // left/top, afin de rester sur le compositeur GPU et d'éviter le reflow
+    // à chaque mouvement. X, Y calculés à l'identique (pointeur moins offset,
+    // moins lift éventuel). Aucune transition/easing ici : le suivi doit
+    // rester instantané (un easing introduirait un retard perceptible).
+    const gx = x - offsetX;
+    const gy = y - offsetY - lift;
+    ghost.style.transform = `translate3d(${gx}px, ${gy}px, 0)`;
   }
 
   function clearPreview(){
# ── Zone modifiée : ligne 1796 (11 ligne(s)) dans l'ancienne version → ligne 1825 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1796,11 +1825,11 @@
   }
 
   function updateDropTarget(x,y){
-    const gridRect = gridEl.getBoundingClientRect();
-    const padding = 6;
-    const innerW = gridRect.width - padding*2;
-    const cellSize = innerW / SIZE;
-    const {piece, lift} = dragState;
+    // P4 (issue #21) : mesures de la grille lues depuis le cache posé dans
+    // onPieceDown (gridRect, gridPadding, cellSize) au lieu d'être recalculées
+    // à chaque appel — voir le commentaire en tête de onPieceDown pour le cas
+    // limite du redimensionnement en cours de glisser.
+    const {piece, lift, gridRect, gridPadding: padding, cellSize} = dragState;
     const {h,w} = shapeBounds(piece.shape);
 
     const ghostX = x - dragState.offsetX - (gridRect.left + padding);
