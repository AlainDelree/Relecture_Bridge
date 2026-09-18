58d54e3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 58d54e3
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 19:12:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    bloc-formes.html : aperçu invalide Hexagone/Étoile fidèle + contraste pièces posées
    
    - showPreview dessinait le contour invalide en coloriant les triangles
      réels de la grille avec les offsets bruts de la pièce ; sur un ancrage
      à parité invalide, l'orientation up/down réelle de ces triangles ne
      correspond plus à celle attendue par la pièce, d'où le contour en
      sablier au lieu de l'hexagone (même bug pour l'Étoile, autre pièce à
      parity contrainte).
    - Remplacement par un calque SVG dédié (#preview-layer) qui dessine la
      silhouette avec la géométrie locale trianglePoints(dr, dc), comme
      pieceIconSVG, translatée à la position pixel de l'ancrage : la forme
      affichée est toujours la vraie silhouette de la pièce, verte si
      valide ou rouge si invalide.
    - Pièces posées : fill-opacity à 1 (au lieu de 0.92) et contour clair
      distinct (.cell.occ, stroke cream) pour mieux les distinguer du fond
      de grille et des zones de score, sans toucher aux couleurs des zones.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-formes.html b/bloc-formes.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1bf564c..d9ec933 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-formes.html
# ── Version APRÈS ce commit.
+++ b/bloc-formes.html
# ── Zone modifiée : ligne 87 (8 ligne(s)) dans l'ancienne version → ligne 87 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -87,8 +87,10 @@
     cursor:pointer;
     transition:opacity .12s ease;
   }
-  polygon.cell.preview-ok{stroke:var(--teal);stroke-width:2.4;}
-  polygon.cell.preview-bad{stroke:var(--coral);stroke-width:2.4;}
+  polygon.cell.occ{stroke:var(--cream);stroke-width:1.6;stroke-opacity:0.85;}
+  .piece-preview{pointer-events:none;}
+  .piece-preview.preview-ok{fill:var(--teal);fill-opacity:0.32;stroke:var(--teal);stroke-width:2.4;}
+  .piece-preview.preview-bad{fill:var(--coral);fill-opacity:0.32;stroke:var(--coral);stroke-width:2.4;}
   .reserve{
     display:flex;
     gap:10px;
# ── Zone modifiée : ligne 365 (7 ligne(s)) dans l'ancienne version → ligne 367 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -365,7 +367,8 @@
       const poly = polyById[t.id];
       const occ = occupied[t.id];
       poly.setAttribute('fill', occ ? PIECES[occ].color : baseFillFor(t.id));
-      poly.setAttribute('fill-opacity', occ ? '0.92' : (cellZones[t.id].length ? '0.55' : '1'));
+      poly.setAttribute('fill-opacity', occ ? '1' : (cellZones[t.id].length ? '0.55' : '1'));
+      poly.classList.toggle('occ', Boolean(occ));
     });
   }
   render();
# ── Zone modifiée : ligne 440 (24 ligne(s)) dans l'ancienne version → ligne 443 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -440,24 +443,38 @@
   }
 
   // ---------- Prévisualisation au survol ----------
-  let previewIds = [];
+  // Calque dédié, dessiné par-dessus la grille avec la géométrie locale de la
+  // pièce (trianglePoints(dr, dc), comme pieceIconSVG) plutôt qu'en coloriant
+  // les triangles réels de la grille : leur orientation up/down dépend de la
+  // parité de (anchorR+anchorC), donc sur un ancrage à parité invalide les
+  // offsets (dr, dc) tombent sur des triangles orientés à l'envers et
+  // donnaient un contour en sablier au lieu de la silhouette de la pièce.
+  const previewLayer = document.createElementNS('http://www.w3.org/2000/svg', 'g');
+  previewLayer.setAttribute('id', 'preview-layer');
+  svg.appendChild(previewLayer);
+
   function clearPreview(){
-    previewIds.forEach(id => polyById[id].classList.remove('preview-ok', 'preview-bad'));
-    previewIds = [];
+    previewLayer.innerHTML = '';
   }
+
   function showPreview(anchorR, anchorC){
     clearPreview();
     if (!selectedPiece) return;
+    const piece = PIECES[selectedPiece];
     const res = computeTargetCells(selectedPiece, anchorR, anchorC);
-    const ids = res.ok ? res.targetCells : (
-      // même en cas d'échec, si les offsets restent dans la grille, montrer en rouge
-      PIECES[selectedPiece].cells
-        .map(([dr, dc]) => [anchorR + dr, anchorC + dc])
-        .filter(([r, c]) => r >= 0 && r < ROWS && c >= 0 && c < COLS)
-        .map(([r, c]) => idx(r, c))
-    );
     const cls = res.ok ? 'preview-ok' : 'preview-bad';
-    ids.forEach(id => { polyById[id].classList.add(cls); previewIds.push(id); });
+    const anchorX = anchorC * (CW / 2), anchorY = anchorR * CH;
+    piece.cells.forEach(([dr, dc]) => {
+      const r = anchorR + dr, c = anchorC + dc;
+      if (r < 0 || r >= ROWS || c < 0 || c >= COLS) return;
+      const points = trianglePoints(dr, dc)
+        .map(([x, y]) => `${x + anchorX + PAD},${y + anchorY + PAD}`)
+        .join(' ');
+      const poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
+      poly.setAttribute('points', points);
+      poly.setAttribute('class', 'piece-preview ' + cls);
+      previewLayer.appendChild(poly);
+    });
   }
 
   svg.addEventListener('mousemove', (e) => {
