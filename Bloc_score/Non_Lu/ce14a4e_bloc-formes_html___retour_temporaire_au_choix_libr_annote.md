ce14a4e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ce14a4e
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 19:40:57 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    bloc-formes.html : retour temporaire au choix libre des 4 pièces (illimité) pour les tests
    
    Revert de la réservation du tirage à 3 pièces (0701b05), conservée
    uniquement pour la logique de placement/aperçu. Le tirage à 3 sera
    réintroduit plus tard une fois les problèmes de placement/rotation/
    lisibilité réglés. bloc-jeu.html non touché.
    
    This reverts commit 0701b054d26c85f2e21f4b803ff8dd4414e924fb.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-formes.html b/bloc-formes.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d9ec933..58aa4b5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-formes.html
# ── Version APRÈS ce commit.
+++ b/bloc-formes.html
# ── Zone modifiée : ligne 113 (7 ligne(s)) dans l'ancienne version → ligne 113 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -113,7 +113,6 @@
     letter-spacing:0.02em;
   }
   .piece-btn.active{border-color:var(--cream);}
-  .piece-btn.empty{opacity:0.35;cursor:default;}
   .piece-icon{display:block;flex:0 0 auto;}
   .units{color:var(--cream-dim);font-size:10px;}
   footer.ft{margin-top:16px;font-size:11px;color:var(--cream-dim);line-height:1.6;}
# ── Zone modifiée : ligne 392 (45 ligne(s)) dans l'ancienne version → ligne 391 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -392,45 +391,21 @@
     return `<svg class="piece-icon" viewBox="${vb}" width="28" height="24" xmlns="http://www.w3.org/2000/svg">${polys}</svg>`;
   }
 
-  // Lot de 3 pièces tirées aléatoirement parmi les 4 types (tirage indépendant
-  // par emplacement, doublons possibles). Un nouveau lot est tiré dès que les
-  // 3 emplacements du lot courant sont vides.
-  const BATCH_SIZE = 3;
-  let currentBatch = [];
-  let selectedSlot = null; // index dans currentBatch, ou null
-
-  function drawBatch(){
-    currentBatch = Array.from({ length: BATCH_SIZE }, () => PIECE_ORDER[randInt(PIECE_ORDER.length)]);
-    selectedSlot = null;
-    selectedPiece = null;
-  }
-
   const reserveEl = document.getElementById('reserve');
-  function renderReserve(){
-    reserveEl.innerHTML = '';
-    currentBatch.forEach((key, i) => {
-      const btn = document.createElement('button');
-      if (key === null){
-        btn.className = 'piece-btn empty';
-        btn.disabled = true;
-        btn.innerHTML = `<span class="units">emplacement vide</span>`;
-      } else {
-        const p = PIECES[key];
-        btn.className = 'piece-btn' + (i === selectedSlot ? ' active' : '');
-        btn.innerHTML = `${pieceIconSVG(key)}${p.name} <span class="units">(${p.cells.length}u)</span>`;
-        btn.addEventListener('click', () => {
-          selectedSlot = (selectedSlot === i) ? null : i;
-          selectedPiece = selectedSlot === null ? null : currentBatch[selectedSlot];
-          renderReserve();
-          clearPreview();
-        });
-      }
-      reserveEl.appendChild(btn);
+  const btnByKey = {};
+  PIECE_ORDER.forEach(key => {
+    const p = PIECES[key];
+    const btn = document.createElement('button');
+    btn.className = 'piece-btn';
+    btn.innerHTML = `${pieceIconSVG(key)}${p.name} <span class="units">(${p.cells.length}u)</span>`;
+    btn.addEventListener('click', () => {
+      selectedPiece = (selectedPiece === key) ? null : key;
+      PIECE_ORDER.forEach(k => btnByKey[k].classList.toggle('active', k === selectedPiece));
+      clearPreview();
     });
-  }
-
-  drawBatch();
-  renderReserve();
+    reserveEl.appendChild(btn);
+    btnByKey[key] = btn;
+  });
 
   // ---------- Score / messages ----------
   const scoreEl = document.getElementById('score');
# ── Zone modifiée : ligne 504 (12 ligne(s)) dans l'ancienne version → ligne 479 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -504,12 +479,7 @@
     scoreEl.textContent = String(score);
     render();
     clearPreview();
-
-    currentBatch[selectedSlot] = null;
-    selectedSlot = null;
-    selectedPiece = null;
-    if (currentBatch.every(k => k === null)) drawBatch();
-    renderReserve();
+    showPreview(anchorR, anchorC);
   });
 })();
 </script>
