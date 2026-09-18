# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 69e8843db64099cea2d2dce263a089c83b5f8805
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 23:21:38 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Fluidite drag Lot 1 (issue #18): hysteresis sur l'ancre dans updateDropTarget + neutralisation transition CSS pendant le glisser
    
    P1: updateDropTarget sort immediatement si l'ancre (r,c) et sa validite
    sont identiques au dernier passage, evitant clearPreview + reconstruction
    du surlignage a chaque pixel dans une meme cellule (nouveau champ
    dragState.lastProcessed, distinct de lastAnchor).
    
    P2: classe .dragging posee sur #grid dans onPieceDown, retiree dans endDrag,
    avec regle #grid.dragging .cell{transition:none} pour un surlignage net
    sans trainee pendant le drag (transition normale inchangee hors drag).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-jeu.html b/bloc-jeu.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5e18b61..c4c8637 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-jeu.html
# ── Version APRÈS ce commit.
+++ b/bloc-jeu.html
# ── Zone modifiée : ligne 410 (6 ligne(s)) dans l'ancienne version → ligne 410 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -410,6 +410,10 @@
     background:rgba(243,234,216,0.05);
     transition:background 0.12s ease, transform 0.12s ease;
   }
+  /* Pendant un glisser actif, on neutralise la transition du surlignage pour
+     qu'il s'affiche net sous le curseur (pas de fondu/traînée de 120ms). La
+     transition normale (placement, effacement de ligne) reste inchangée hors drag. */
+  #grid.dragging .cell{ transition:none; }
   .cell.filled{box-shadow:inset 0 -3px 0 rgba(0,0,0,0.25), inset 0 2px 0 rgba(255,255,255,0.18);}
   .cell.ghost-ok{background:rgba(63,167,150,0.35) !important;}
   .cell.ghost-bad{background:rgba(232,93,78,0.30) !important;}
# ── Zone modifiée : ligne 1554 (6 ligne(s)) dans l'ancienne version → ligne 1558 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1554,6 +1558,9 @@
     document.body.appendChild(ghost);
 
     pieceEl.classList.add('dragging');
+    // Neutralise la transition CSS du surlignage pendant le glisser (P2) :
+    // classe posée ici, retirée dans endDrag (toutes fins de glisser).
+    gridEl.classList.add('dragging');
     pieceEl.setPointerCapture && pieceEl.setPointerCapture(e.pointerId);
     // Filet de sécurité : toute perte de capture du pointeur (menu contextuel,
     // alt-tab, interruption navigateur…) déclenche un nettoyage SANS placement.
# ── Zone modifiée : ligne 1573 (7 ligne(s)) dans l'ancienne version → ligne 1580 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1573,7 +1580,11 @@
       offsetY: e.clientY - rect.top,
       lift,
       lastAnchor: null,
-      lastCells: []
+      lastCells: [],
+      // Mémorise la dernière ancre + validité effectivement traitées, pour
+      // l'hystérésis dans updateDropTarget (P1). Distinct de lastAnchor, qui
+      // vaut null quand la dépose est invalide et sert au commit.
+      lastProcessed: null
     };
 
     positionGhost(e.clientX, e.clientY);
# ── Zone modifiée : ligne 1614 (9 ligne(s)) dans l'ancienne version → ligne 1625 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1614,9 +1625,22 @@
     anchorR = Math.max(0, Math.min(SIZE-h, anchorR));
     anchorC = Math.max(0, Math.min(SIZE-w, anchorC));
 
+    const valid = canPlace(piece.shape, anchorR, anchorC);
+
+    // Hystérésis (P1) : si l'ancre calculée ET sa validité sont identiques au
+    // dernier passage, aucun changement visuel n'est possible. On sort sans
+    // toucher au surlignage plutôt que de le reconstruire (clearPreview +
+    // ghost-ok/bad/will-clear) à chaque pixel dans une même cellule. La
+    // validité fait partie de la comparaison : un même (r,c) qui bascule
+    // valide↔invalide (ou lastAnchor null↔non-null) redéclenche bien le calcul.
+    const prev = dragState.lastProcessed;
+    if(prev && prev.r === anchorR && prev.c === anchorC && prev.valid === valid){
+      return;
+    }
+    dragState.lastProcessed = { r: anchorR, c: anchorC, valid };
+
     clearPreview();
 
-    const valid = canPlace(piece.shape, anchorR, anchorC);
     const cells = piece.shape.map(([dr,dc])=>[anchorR+dr, anchorC+dc])
       .filter(([r,c])=>r>=0&&r<SIZE&&c>=0&&c<SIZE);
 
# ── Zone modifiée : ligne 1657 (6 ligne(s)) dans l'ancienne version → ligne 1681 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1657,6 +1681,7 @@
     const {piece, pieceEl, ghost, lastAnchor} = dragState;
     ghost.remove();
     pieceEl.classList.remove('dragging');
+    gridEl.classList.remove('dragging');
 
     document.removeEventListener('pointermove', onPointerMove);
     document.removeEventListener('pointerup', onPointerUp);
