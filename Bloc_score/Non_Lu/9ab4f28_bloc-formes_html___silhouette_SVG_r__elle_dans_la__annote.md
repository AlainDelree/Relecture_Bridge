9ab4f28

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9ab4f28
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 18:36:49 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    bloc-formes.html : silhouette SVG réelle dans la réserve de pièces (#23)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-formes.html b/bloc-formes.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index dc1f266..b3341d8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-formes.html
# ── Version APRÈS ce commit.
+++ b/bloc-formes.html
# ── Zone modifiée : ligne 111 (7 ligne(s)) dans l'ancienne version → ligne 111 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -111,7 +111,7 @@
     letter-spacing:0.02em;
   }
   .piece-btn.active{border-color:var(--cream);}
-  .swatch{width:14px;height:14px;border-radius:3px;display:inline-block;}
+  .piece-icon{display:block;flex:0 0 auto;}
   .units{color:var(--cream-dim);font-size:10px;}
   footer.ft{margin-top:16px;font-size:11px;color:var(--cream-dim);line-height:1.6;}
 </style>
# ── Zone modifiée : ligne 156 (16 ligne(s)) dans l'ancienne version → ligne 156 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -156,16 +156,20 @@
   function idx(r, c){ return r * COLS + c; }
   function isUp(r, c){ return (r + c) % 2 === 0; }
 
+  // Géométrie d'un triangle de grille à la position logique (r, c) — utilisée
+  // à la fois pour bâtir la grille et pour dessiner l'aperçu des pièces.
+  function trianglePoints(r, c){
+    const x0 = c * (CW / 2);
+    const y0 = r * CH;
+    return isUp(r, c)
+      ? [[x0, y0 + CH], [x0 + CW, y0 + CH], [x0 + CW / 2, y0]]
+      : [[x0, y0], [x0 + CW, y0], [x0 + CW / 2, y0 + CH]];
+  }
+
   const triangles = [];
   for (let r = 0; r < ROWS; r++){
     for (let c = 0; c < COLS; c++){
-      const x0 = c * (CW / 2);
-      const y0 = r * CH;
-      const up = isUp(r, c);
-      const points = up
-        ? [[x0, y0 + CH], [x0 + CW, y0 + CH], [x0 + CW / 2, y0]]
-        : [[x0, y0], [x0 + CW, y0], [x0 + CW / 2, y0 + CH]];
-      triangles.push({ id: idx(r, c), r, c, up, points });
+      triangles.push({ id: idx(r, c), r, c, up: isUp(r, c), points: trianglePoints(r, c) });
     }
   }
 
# ── Zone modifiée : ligne 366 (13 ligne(s)) dans l'ancienne version → ligne 370 (31 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -366,13 +370,31 @@
   render();
 
   // ---------- Réserve de pièces ----------
+  // Aperçu SVG statique d'une pièce : même géométrie (trianglePoints) que
+  // celle utilisée pour la grille et la prévisualisation de placement, donc
+  // la silhouette (y compris les creux concaves de l'étoile) est exacte.
+  function pieceIconSVG(pieceKey){
+    const piece = PIECES[pieceKey];
+    const triPoints = piece.cells.map(([dr, dc]) => trianglePoints(dr, dc));
+    const allPts = triPoints.flat();
+    const xs = allPts.map(p => p[0]), ys = allPts.map(p => p[1]);
+    const minX = Math.min(...xs), maxX = Math.max(...xs);
+    const minY = Math.min(...ys), maxY = Math.max(...ys);
+    const pad = 2;
+    const vb = `${minX - pad} ${minY - pad} ${maxX - minX + pad * 2} ${maxY - minY + pad * 2}`;
+    const polys = triPoints.map(pts =>
+      `<polygon points="${pts.map(p => `${p[0]},${p[1]}`).join(' ')}" fill="${piece.color}" stroke="${piece.color}" stroke-width="1" stroke-linejoin="round"/>`
+    ).join('');
+    return `<svg class="piece-icon" viewBox="${vb}" width="28" height="24" xmlns="http://www.w3.org/2000/svg">${polys}</svg>`;
+  }
+
   const reserveEl = document.getElementById('reserve');
   const btnByKey = {};
   PIECE_ORDER.forEach(key => {
     const p = PIECES[key];
     const btn = document.createElement('button');
     btn.className = 'piece-btn';
-    btn.innerHTML = `<span class="swatch" style="background:${p.color}"></span>${p.name} <span class="units">(${p.cells.length}u)</span>`;
+    btn.innerHTML = `${pieceIconSVG(key)}${p.name} <span class="units">(${p.cells.length}u)</span>`;
     btn.addEventListener('click', () => {
       selectedPiece = (selectedPiece === key) ? null : key;
       PIECE_ORDER.forEach(k => btnByKey[k].classList.toggle('active', k === selectedPiece));
