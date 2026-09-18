bf8a922

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bf8a922
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 19:12:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-exercice-running vers data-action + CSS (issue #229)
    
    Remplace les 5 onclick= par 4 nouveaux case dédiés dans le switch
    délégué d'app.js (exercice_sync/exercice_retry/exercice_continue/
    exercice_back), cohérents avec le style actuel du switch (un case par
    type, comme reconnect_board/back_menu/back) plutôt qu'un case
    générique — chaque case appelle sendAction({type:'exercice_xxx'})
    directement, aucun handler Python touché (types inchangés, gérés dans
    exercices.py). Le 5e bouton ("Retour au menu") rejoint le case
    back_menu déjà existant, et réutilise en prime la classe .btn-continuer
    existante (couleurs identiques à l'inline d'origine) au lieu d'une
    classe dédiée.
    
    Remplace les 30 style= inline par des classes dans main.css :
    - règle #screen-exercice-running dédiée (display/grid/padding du
      conteneur), même pattern que #screen-game — jusqu'ici ce conteneur
      n'avait que des variables CSS (--bd-*), pas de règle de mise en page.
    - 24 classes .exr-* pour les éléments internes (colonnes, cards,
      textes, board wrapper, feedback, boutons), valeurs strictement
      identiques à l'inline d'origine. Réutilise .exr-card-sm/.exr-btn-mb0
      pour les éléments qui partagent exactement la même valeur (mêmes
      patterns .cfg-hh-card/.cfg-hh-title des issues #227/#228).
    - Le style inline de #ex-board (display:grid; grid-template-columns:
      repeat(8,1fr)) était redondant avec la règle #board,#ex-board,...
      déjà présente dans main.css (ligne 580) : simplement supprimé, sans
      remplacement.
    - Les display:none initiaux de #ex-btn-continuer, #ex-feedback sont
      déplacés dans leurs classes .exr-btn-continuer/.exr-feedback — sûr
      car app.js ne fait qu'écrire ces display, jamais les lire au
      préalable (vérifié). #ex-drill-bar n'est pas dans ce bloc (il vit
      dans #screen-exercices, déjà traité par #228) — signalé pour mémoire
      car le corps de l'issue le mentionnait par erreur.
    
    Opportunité notée sans y donner suite (hors périmètre de cette issue,
    comme demandé) : back_menu/back/exercice_back pourraient converger
    vers un case générique data-action="send_type" data-type="..." — pas
    fait ici pour ne pas retoucher rétroactivement les case déjà en place.
    
    Aucune dépendance e2e sur ce bloc (grep exhaustif nicsoft/tests/e2e/*.py,
    confirmé). Suite pytest complète (78 passed, 1 skipped, e2e inclus) au
    vert après modification.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5e0a953..60016bf 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 85 (6 ligne(s)) dans l'ancienne version → ligne 85 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -85,6 +85,18 @@ document.addEventListener("click", (e) => {
     case "ex_lancer_drill":
       exLancerDrill();
       break;
+    case "exercice_sync":
+      sendAction({ type: "exercice_sync" });
+      break;
+    case "exercice_retry":
+      sendAction({ type: "exercice_retry" });
+      break;
+    case "exercice_continue":
+      sendAction({ type: "exercice_continue" });
+      break;
+    case "exercice_back":
+      sendAction({ type: "exercice_back" });
+      break;
     case "select_color_hh":
       selectColorHH(el.dataset.color);
       break;
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index d0df353..f673bc0 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 190 (6 ligne(s)) dans l'ancienne version → ligne 190 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -190,6 +190,17 @@
       align-items: start;
       overflow: hidden;
     }
+    #screen-exercice-running {
+      display: none;
+      flex: 1;
+      grid-template-columns: 220px minmax(0, 1fr) 380px;
+      gap: 20px;
+      padding: 16px 20px;
+      width: 100%;
+      max-width: 100vw;
+      align-items: start;
+      overflow: hidden;
+    }
 
     /* ── Schéma connexion ordinateur-échiquier (écran menu) ── */
     .schema-connexion {
# ── Zone modifiée : ligne 968 (6 ligne(s)) dans l'ancienne version → ligne 979 (32 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -968,6 +979,32 @@
 .ex-drill-btn-launch { padding:7px 18px; font-size:0.85rem; }
 .ex-ouvertures-list { width:100%; max-width:960px; }
 
+/* ── Écran "Exercice en cours" (issue #229) ── */
+.exr-col-left { display:flex; flex-direction:column; gap:8px; }
+.exr-card-sm { padding:12px 14px; }
+.exr-card-md { padding:14px 16px; }
+.exr-card-actions { padding:14px 16px; display:flex; flex-direction:column; gap:8px; }
+.exr-run-nom { color:#e94560; font-size:0.85rem; margin-bottom:8px; }
+.exr-run-status { font-size:0.9rem; font-weight:600; color:#1a2a3a; margin-bottom:8px; }
+.exr-run-info { font-size:0.8rem; color:#445; line-height:1.6; }
+.exr-run-instructions { margin-top:10px; font-size:0.78rem; color:#4caf50; line-height:1.5; padding:8px; background:#0a2a1a; border-radius:4px; border-left:3px solid #4caf50; }
+.exr-run-book-moves { font-size:0.82rem; color:#4caf50; }
+.exr-col-center { display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:0; max-height:calc(100vh - 60px); overflow:hidden; }
+.exr-spinner-text { color:#3a5a7a; font-size:0.85rem; margin-top:14px; }
+.exr-board-wrapper { min-width:0; display:flex; flex-direction:column; border:2px solid #a0b8d0; border-radius:4px; overflow:hidden; }
+.exr-player-row { padding:4px 6px; background:#a0b8d0; }
+.exr-player-top { color:#445; font-weight:bold; font-size:0.85rem; }
+.exr-player-bottom { color:#1a2a3a; font-weight:bold; font-size:0.85rem; }
+.exr-board-row { display:flex; align-items:stretch; }
+.exr-coord-file { width:100%; }
+.exr-feedback { margin-top:8px; padding:8px 16px; border-radius:6px; font-size:0.9rem; display:none; text-align:center; font-weight:600; }
+.exr-col-right { display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px); }
+.exr-run-moves-count { font-size:1.2rem; font-weight:bold; color:#1a2a3a; text-align:center; }
+.exr-run-variete { font-size:0.75rem; color:#3a5a7a; text-align:center; margin-top:4px; }
+.exr-btn-mb0 { margin-bottom:0; }
+.exr-btn-sync { margin-bottom:0; background:#a0b8d0; border:1px solid #4caf50; color:#4caf50; }
+.exr-btn-continuer { margin-bottom:0; display:none; background:#2e7d32; color:#fff; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index e8cde6f..c2b3404 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 900 (58 ligne(s)) dans l'ancienne version → ligne 900 (58 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -900,58 +900,58 @@
 </div>
 
 <!-- ── Écran Exercice en cours ── -->
-<div id="screen-exercice-running" style="display:none; flex:1; grid-template-columns:220px minmax(0,1fr) 380px; gap:20px; padding:16px 20px; width:100%; max-width:100vw; align-items:start; overflow:hidden;">
+<div id="screen-exercice-running">
 
   <!-- Colonne gauche : info -->
-  <div style="display:flex; flex-direction:column; gap:8px;">
-    <div class="card" style="padding:12px 14px;">
-      <h2 id="ex-run-nom" style="color:#e94560; font-size:0.85rem; margin-bottom:8px;"></h2>
-      <div id="ex-run-status" style="font-size:0.9rem; font-weight:600; color:#1a2a3a; margin-bottom:8px;">—</div>
-      <div id="ex-run-info" style="font-size:0.8rem; color:#445; line-height:1.6;"></div>
-      <div id="ex-run-instructions" style="margin-top:10px; font-size:0.78rem; color:#4caf50; line-height:1.5; padding:8px; background:#0a2a1a; border-radius:4px; border-left:3px solid #4caf50;"></div>
-    </div>
-    <div class="card" style="padding:12px 14px;">
+  <div class="exr-col-left">
+    <div class="card exr-card-sm">
+      <h2 id="ex-run-nom" class="exr-run-nom"></h2>
+      <div id="ex-run-status" class="exr-run-status">—</div>
+      <div id="ex-run-info" class="exr-run-info"></div>
+      <div id="ex-run-instructions" class="exr-run-instructions"></div>
+    </div>
+    <div class="card exr-card-sm">
       <h2 data-i18n="exercices.h2.coups_livre">COUPS DU LIVRE</h2>
-      <div id="ex-run-book-moves" style="font-size:0.82rem; color:#4caf50;"></div>
+      <div id="ex-run-book-moves" class="exr-run-book-moves"></div>
     </div>
   </div>
 
   <!-- Colonne centre : échiquier -->
-  <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:0; max-height:calc(100vh - 60px); overflow:hidden;">
+  <div class="exr-col-center">
     <!-- Spinner chargement -->
     <div id="ex-spinner">
       <div class="spinner-ring"></div>
-      <div style="color:#3a5a7a; font-size:0.85rem; margin-top:14px;" data-i18n="labo.loading.echiquier">Connexion à l'échiquier…</div>
+      <div class="exr-spinner-text" data-i18n="labo.loading.echiquier">Connexion à l'échiquier…</div>
     </div>
-    <div id="ex-board-wrapper" style="min-width:0; display:flex; flex-direction:column; border:2px solid #a0b8d0; border-radius:4px; overflow:hidden;">
-      <div class="player-row" style="padding:4px 6px; background:#a0b8d0;"><span id="ex-player-top" style="color:#445; font-weight:bold; font-size:0.85rem;">Noirs</span></div>
-      <div style="display:flex; align-items:stretch;">
+    <div id="ex-board-wrapper" class="exr-board-wrapper">
+      <div class="player-row exr-player-row"><span id="ex-player-top" class="exr-player-top">Noirs</span></div>
+      <div class="exr-board-row">
         <div class="coord-rank" id="ex-coord-rank"></div>
-        <div id="ex-board" style="display:grid; grid-template-columns:repeat(8,1fr);"></div>
+        <div id="ex-board"></div>
       </div>
-      <div class="coord-file" id="ex-coord-file" style="width:100%;"></div>
-      <div class="player-row" style="padding:4px 6px; background:#a0b8d0;"><span id="ex-player-bottom" style="color:#1a2a3a; font-weight:bold; font-size:0.85rem;">Blancs</span></div>
+      <div class="coord-file exr-coord-file" id="ex-coord-file"></div>
+      <div class="player-row exr-player-row"><span id="ex-player-bottom" class="exr-player-bottom">Blancs</span></div>
     </div>
     <!-- Feedback -->
-    <div id="ex-feedback" style="margin-top:8px; padding:8px 16px; border-radius:6px; font-size:0.9rem; display:none; text-align:center; font-weight:600;"></div>
+    <div id="ex-feedback" class="exr-feedback"></div>
   </div>
 
   <!-- Colonne droite : contrôles -->
-  <div style="display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px);">
+  <div class="exr-col-right">
 
-    <div class="card" style="padding:14px 16px;">
+    <div class="card exr-card-md">
       <h2 data-i18n="exercices.h2.progression">PROGRESSION</h2>
-      <div id="ex-run-moves-count" style="font-size:1.2rem; font-weight:bold; color:#1a2a3a; text-align:center;">Coup 0</div>
-      <div id="ex-run-variete" style="font-size:0.75rem; color:#3a5a7a; text-align:center; margin-top:4px;"></div>
+      <div id="ex-run-moves-count" class="exr-run-moves-count">Coup 0</div>
+      <div id="ex-run-variete" class="exr-run-variete"></div>
     </div>
 
-    <div class="card" style="padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
+    <div class="card exr-card-actions">
       <h2 data-i18n="exercices.h2.actions">ACTIONS</h2>
-      <button id="ex-btn-sync" class="btn" style="margin-bottom:0; background:#a0b8d0; border:1px solid #4caf50; color:#4caf50;" onclick="sendAction({type:'exercice_sync'})" data-i18n="exercices.btn.sync">🔄 Synchroniser plateau → Virtuel</button>
-      <button class="btn btn-reprendre" style="margin-bottom:0;" onclick="sendAction({type:'exercice_retry'})" data-i18n="exercices.btn.retry">↺ Recommencer l'exercice</button>
-      <button id="ex-btn-continuer" class="btn" style="margin-bottom:0; display:none; background:#2e7d32; color:#fff;" onclick="sendAction({type:'exercice_continue'})" data-i18n="exercices.btn.continuer_stockfish">▶ Continuer avec Stockfish</button>
-      <button class="btn btn-continuer" style="margin-bottom:0;" onclick="sendAction({type:'exercice_back'})" data-i18n="exercices.btn.choisir">← Choisir autre ouverture</button>
-      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+      <button id="ex-btn-sync" class="btn exr-btn-sync" data-action="exercice_sync" data-i18n="exercices.btn.sync">🔄 Synchroniser plateau → Virtuel</button>
+      <button class="btn btn-reprendre exr-btn-mb0" data-action="exercice_retry" data-i18n="exercices.btn.retry">↺ Recommencer l'exercice</button>
+      <button id="ex-btn-continuer" class="btn exr-btn-continuer" data-action="exercice_continue" data-i18n="exercices.btn.continuer_stockfish">▶ Continuer avec Stockfish</button>
+      <button class="btn btn-continuer exr-btn-mb0" data-action="exercice_back" data-i18n="exercices.btn.choisir">← Choisir autre ouverture</button>
+      <button class="btn btn-continuer exr-btn-mb0" data-action="back_menu" data-i18n="common.retour_menu">← Retour au menu</button>
     </div>
 
   </div>
