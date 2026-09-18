0701b05

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0701b05
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 18:46:18 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    bloc-formes.html : réserve remplacée par un tirage de 3 pièces aléatoires (#24)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-formes.html b/bloc-formes.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b3341d8..1bf564c 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-formes.html
# ── Version APRÈS ce commit.
+++ b/bloc-formes.html
# ── Zone modifiée : ligne 111 (6 ligne(s)) dans l'ancienne version → ligne 111 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -111,6 +111,7 @@
     letter-spacing:0.02em;
   }
   .piece-btn.active{border-color:var(--cream);}
+  .piece-btn.empty{opacity:0.35;cursor:default;}
   .piece-icon{display:block;flex:0 0 auto;}
   .units{color:var(--cream-dim);font-size:10px;}
   footer.ft{margin-top:16px;font-size:11px;color:var(--cream-dim);line-height:1.6;}
# ── Zone modifiée : ligne 388 (21 ligne(s)) dans l'ancienne version → ligne 389 (45 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -388,21 +389,45 @@
     return `<svg class="piece-icon" viewBox="${vb}" width="28" height="24" xmlns="http://www.w3.org/2000/svg">${polys}</svg>`;
   }
 
+  // Lot de 3 pièces tirées aléatoirement parmi les 4 types (tirage indépendant
+  // par emplacement, doublons possibles). Un nouveau lot est tiré dès que les
+  // 3 emplacements du lot courant sont vides.
+  const BATCH_SIZE = 3;
+  let currentBatch = [];
+  let selectedSlot = null; // index dans currentBatch, ou null
+
+  function drawBatch(){
+    currentBatch = Array.from({ length: BATCH_SIZE }, () => PIECE_ORDER[randInt(PIECE_ORDER.length)]);
+    selectedSlot = null;
+    selectedPiece = null;
+  }
+
   const reserveEl = document.getElementById('reserve');
-  const btnByKey = {};
-  PIECE_ORDER.forEach(key => {
-    const p = PIECES[key];
-    const btn = document.createElement('button');
-    btn.className = 'piece-btn';
-    btn.innerHTML = `${pieceIconSVG(key)}${p.name} <span class="units">(${p.cells.length}u)</span>`;
-    btn.addEventListener('click', () => {
-      selectedPiece = (selectedPiece === key) ? null : key;
-      PIECE_ORDER.forEach(k => btnByKey[k].classList.toggle('active', k === selectedPiece));
-      clearPreview();
+  function renderReserve(){
+    reserveEl.innerHTML = '';
+    currentBatch.forEach((key, i) => {
+      const btn = document.createElement('button');
+      if (key === null){
+        btn.className = 'piece-btn empty';
+        btn.disabled = true;
+        btn.innerHTML = `<span class="units">emplacement vide</span>`;
+      } else {
+        const p = PIECES[key];
+        btn.className = 'piece-btn' + (i === selectedSlot ? ' active' : '');
+        btn.innerHTML = `${pieceIconSVG(key)}${p.name} <span class="units">(${p.cells.length}u)</span>`;
+        btn.addEventListener('click', () => {
+          selectedSlot = (selectedSlot === i) ? null : i;
+          selectedPiece = selectedSlot === null ? null : currentBatch[selectedSlot];
+          renderReserve();
+          clearPreview();
+        });
+      }
+      reserveEl.appendChild(btn);
     });
-    reserveEl.appendChild(btn);
-    btnByKey[key] = btn;
-  });
+  }
+
+  drawBatch();
+  renderReserve();
 
   // ---------- Score / messages ----------
   const scoreEl = document.getElementById('score');
# ── Zone modifiée : ligne 462 (7 ligne(s)) dans l'ancienne version → ligne 487 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -462,7 +487,12 @@
     scoreEl.textContent = String(score);
     render();
     clearPreview();
-    showPreview(anchorR, anchorC);
+
+    currentBatch[selectedSlot] = null;
+    selectedSlot = null;
+    selectedPiece = null;
+    if (currentBatch.every(k => k === null)) drawBatch();
+    renderReserve();
   });
 })();
 </script>
