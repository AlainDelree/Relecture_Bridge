df20620

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit df20620
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 19:57:00 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-opening-explorer-play vers data-action + CSS (issue #232)
    
    Remplace les 6 onclick= : explChatSend() → case "expl_chat_send".
    explPrev()/explNext() sont consolidés en un seul case "expl_nav"
    paramétré par data-direction="prev"/"next", sur le modèle des
    consolidations déjà faites pour retrans_end/retrans_select_tab (#230,
    #231). explToggleTts() → case "expl_toggle_tts" (le title="" vide du
    bouton, mis à jour dynamiquement par explUpdateTtsToggle(), n'est pas
    touché). explBackToSelect() → case "expl_back_to_select".
    sendAction({type:'back_menu'}) rejoint le case "back_menu" déjà
    existant. Le oninput="explSetVolume(this.value)" du slider de volume
    TTS reste inchangé (hors périmètre demandé).
    
    Remplace les 34 style= inline par des classes dans main.css :
    - #screen-opening-explorer-play récupère sa propre règle CSS par id
      (display, grid-template-columns:380px minmax(0,1fr) 240px, gap,
      padding, overflow...), ajoutée juste après #screen-exercice-running
      dans le même bloc de règles par id — même pattern que les écrans
      précédents du chantier F8.
    - .expl-play-left/-right/-center/-explanation-card/-explanation-text/
      -chat-card/-chat-history/-chat-input-row/-chat-input/-chat-send-btn/
      -board-wrapper/-player-row/-player-top/-player-bottom/-board-row/
      -board-pos/-arrows-svg/-coord-file/-nav-row/-btn-prev/-btn-next/
      -tts-row/-tts-toggle/-tts-volume/-info-card/-nom/-coup-courant/
      -moves-card/-actions-card/-btn-back pour la disposition et les
      boutons, valeurs strictement identiques à l'inline d'origine.
    - Le style inline de #expl-board (display:grid;
      grid-template-columns:repeat(8,1fr)) est simplement supprimé plutôt
      que reporté dans une classe : il dupliquait à l'identique la règle
      CSS déjà existante par id (#board, #rv-board, ..., #expl-board),
      qui définit en plus overflow/width/height via --bd-size — aucun
      changement de rendu.
    
    Aucun sélecteur e2e ne cible un onclick/style de ce bloc (grep
    exhaustif sur nicsoft/tests/e2e/*.py — les tests explorer_* de
    test_outils_exercices_e2e.py ciblent l'explorateur Polyglot de
    l'écran "Outils" via #explore-*, un écran distinct non affecté).
    
    Suite pytest complète (78 passed, 1 skipped, e2e inclus) au vert
    après modification.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b20249a..5c56cfd 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 142 (6 ligne(s)) dans l'ancienne version → ligne 142 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -142,6 +142,18 @@ document.addEventListener("click", (e) => {
     case "retrans_quit_sans_sauver":
       retransQuitSansSauver();
       break;
+    case "expl_chat_send":
+      explChatSend();
+      break;
+    case "expl_nav":
+      if (el.dataset.direction === "prev") explPrev(); else explNext();
+      break;
+    case "expl_toggle_tts":
+      explToggleTts();
+      break;
+    case "expl_back_to_select":
+      explBackToSelect();
+      break;
   }
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index 3eec82f..d6ea26a 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 212 (6 ligne(s)) dans l'ancienne version → ligne 212 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -212,6 +212,17 @@
       align-items: start;
       overflow: hidden;
     }
+    #screen-opening-explorer-play {
+      display: none;
+      flex: 1;
+      grid-template-columns: 380px minmax(0, 1fr) 240px;
+      gap: 20px;
+      padding: 16px 20px;
+      width: 100%;
+      max-width: 100vw;
+      align-items: start;
+      overflow: hidden;
+    }
 
     /* ── Schéma connexion ordinateur-échiquier (écran menu) ── */
     .schema-connexion {
# ── Zone modifiée : ligne 1063 (6 ligne(s)) dans l'ancienne version → ligne 1074 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1063,6 +1074,38 @@
 .retrans-game-btn-corbeille { flex:1; margin-bottom:0; font-size:0.82rem; background:#2a5a4a; color:#e0e0e0; border:1px solid #1a4a3a; }
 .retrans-game-btn-quitter { width:100%; font-size:0.82rem; background:#c2d4e8; border:1px solid #333; color:#3a5a7a; }
 
+/* ── Écran "Opening Explorer" — partie en cours (issue #232) ── */
+.expl-play-left { display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px); }
+.expl-play-explanation-card { padding:14px 16px; }
+.expl-play-explanation-text { font-size:0.85rem; color:#3a5a7a; line-height:1.5; }
+.expl-play-chat-card { padding:14px 16px; display:flex; flex-direction:column; gap:8px; }
+.expl-play-chat-history { font-size:0.82rem; color:#3a5a7a; max-height:200px; overflow-y:auto; display:flex; flex-direction:column; gap:6px; }
+.expl-play-chat-input-row { display:flex; gap:6px; }
+.expl-play-chat-input { flex:1; padding:6px 10px; border:1px solid #a0b8d0; border-radius:6px; font-size:0.85rem; }
+.expl-play-chat-send-btn { margin:0; padding:6px 12px; font-size:0.82rem; }
+.expl-play-center { display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:0; max-height:calc(100vh - 60px); overflow:hidden; }
+.expl-play-board-wrapper { min-width:0; display:flex; flex-direction:column; border:2px solid #a0b8d0; border-radius:4px; overflow:hidden; }
+.expl-play-player-row { padding:4px 6px; background:#a0b8d0; }
+.expl-play-player-top { color:#445; font-weight:bold; font-size:0.85rem; }
+.expl-play-player-bottom { color:#1a2a3a; font-weight:bold; font-size:0.85rem; }
+.expl-play-board-row { display:flex; align-items:stretch; }
+.expl-play-board-pos { position:relative; display:inline-block; }
+.expl-play-arrows-svg { position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; overflow:visible; }
+.expl-play-coord-file { width:100%; }
+.expl-play-nav-row { display:flex; gap:10px; margin-top:14px; }
+.expl-play-btn-prev { background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-top:0; }
+.expl-play-btn-next { margin-top:0; }
+.expl-play-right { display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:calc(100vh - 60px); }
+.expl-play-tts-row { display:flex; align-items:center; gap:8px; align-self:flex-start; }
+.expl-play-tts-toggle { background:none; border:1px solid #a0b8d0; border-radius:6px; padding:3px 10px; font-size:1rem; line-height:1.4; cursor:pointer; }
+.expl-play-tts-volume { width:90px; accent-color:#e94560; }
+.expl-play-info-card { padding:12px 14px; }
+.expl-play-nom { color:#e94560; font-size:0.85rem; margin-bottom:8px; }
+.expl-play-coup-courant { font-size:0.9rem; font-weight:600; color:#1a2a3a; }
+.expl-play-moves-card { padding:14px 16px; }
+.expl-play-actions-card { padding:14px 16px; display:flex; flex-direction:column; gap:8px; }
+.expl-play-btn-back { background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 8277fd6..2764bc6 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1647 (35 ligne(s)) dans l'ancienne version → ligne 1647 (35 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1647,35 +1647,35 @@
 </div>
 
 <!-- ── Écran Opening Explorer — lecteur ── -->
-<div id="screen-opening-explorer-play" style="display:none; flex:1; grid-template-columns:380px minmax(0,1fr) 240px; gap:20px; padding:16px 20px; width:100%; max-width:100vw; align-items:start; overflow:hidden;">
+<div id="screen-opening-explorer-play">
 
   <!-- Colonne gauche : panneau IA (explication + chat) -->
-  <div style="display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px);">
+  <div class="expl-play-left">
 
-    <div class="card" style="padding:14px 16px;">
+    <div class="card expl-play-explanation-card">
       <h2 data-i18n="opening_explorer.h2.explication">EXPLICATION</h2>
-      <div id="explorer-explanation" style="font-size:0.85rem; color:#3a5a7a; line-height:1.5;"></div>
+      <div id="explorer-explanation" class="expl-play-explanation-text"></div>
     </div>
 
-    <div class="card" style="padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
-      <div id="explorer-chat-history" style="font-size:0.82rem; color:#3a5a7a; max-height:200px; overflow-y:auto; display:flex; flex-direction:column; gap:6px;"></div>
-      <div style="display:flex; gap:6px;">
-        <input type="text" id="explorer-chat-input" style="flex:1; padding:6px 10px; border:1px solid #a0b8d0; border-radius:6px; font-size:0.85rem;" placeholder="Posez une question..." data-i18n-placeholder="opening_explorer.chat.placeholder">
-        <button id="explorer-chat-send-btn" class="btn btn-continuer" style="margin:0; padding:6px 12px; font-size:0.82rem;" onclick="explChatSend()" data-i18n="opening_explorer.chat.envoyer">Envoyer</button>
+    <div class="card expl-play-chat-card">
+      <div id="explorer-chat-history" class="expl-play-chat-history"></div>
+      <div class="expl-play-chat-input-row">
+        <input type="text" id="explorer-chat-input" class="expl-play-chat-input" placeholder="Posez une question..." data-i18n-placeholder="opening_explorer.chat.placeholder">
+        <button id="explorer-chat-send-btn" class="btn btn-continuer expl-play-chat-send-btn" data-action="expl_chat_send" data-i18n="opening_explorer.chat.envoyer">Envoyer</button>
       </div>
     </div>
 
   </div>
 
   <!-- Colonne centre : échiquier -->
-  <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:0; max-height:calc(100vh - 60px); overflow:hidden;">
-    <div id="expl-board-wrapper" style="min-width:0; display:flex; flex-direction:column; border:2px solid #a0b8d0; border-radius:4px; overflow:hidden;">
-      <div class="player-row" style="padding:4px 6px; background:#a0b8d0;"><span id="expl-player-top" style="color:#445; font-weight:bold; font-size:0.85rem;">Noirs</span></div>
-      <div style="display:flex; align-items:stretch;">
+  <div class="expl-play-center">
+    <div id="expl-board-wrapper" class="expl-play-board-wrapper">
+      <div class="player-row expl-play-player-row"><span id="expl-player-top" class="expl-play-player-top">Noirs</span></div>
+      <div class="expl-play-board-row">
         <div class="coord-rank" id="expl-coord-rank"></div>
-        <div style="position:relative; display:inline-block;">
-          <div id="expl-board" style="display:grid; grid-template-columns:repeat(8,1fr);"></div>
-          <svg id="expl-arrows" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; overflow:visible;">
+        <div class="expl-play-board-pos">
+          <div id="expl-board"></div>
+          <svg id="expl-arrows" class="expl-play-arrows-svg">
             <defs>
               <marker id="expl-arrowhead" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                 <path d="M0,0 L10,5 L0,10 Z" fill="rgba(232,69,96,0.75)"></path>
# ── Zone modifiée : ligne 1684 (36 ligne(s)) dans l'ancienne version → ligne 1684 (36 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1684,36 +1684,36 @@
           </svg>
         </div>
       </div>
-      <div class="coord-file" id="expl-coord-file" style="width:100%;"></div>
-      <div class="player-row" style="padding:4px 6px; background:#a0b8d0;"><span id="expl-player-bottom" style="color:#1a2a3a; font-weight:bold; font-size:0.85rem;">Blancs</span></div>
+      <div class="coord-file expl-play-coord-file" id="expl-coord-file"></div>
+      <div class="player-row expl-play-player-row"><span id="expl-player-bottom" class="expl-play-player-bottom">Blancs</span></div>
     </div>
 
-    <div style="display:flex; gap:10px; margin-top:14px;">
-      <button id="expl-btn-prev" class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-top:0;" onclick="explPrev()" data-i18n="opening_explorer.btn.precedent">← Précédent</button>
-      <button id="expl-btn-next" class="btn btn-continuer" style="margin-top:0;" onclick="explNext()" data-i18n="opening_explorer.btn.suivant">Suivant →</button>
+    <div class="expl-play-nav-row">
+      <button id="expl-btn-prev" class="btn expl-play-btn-prev" data-action="expl_nav" data-direction="prev" data-i18n="opening_explorer.btn.precedent">← Précédent</button>
+      <button id="expl-btn-next" class="btn btn-continuer expl-play-btn-next" data-action="expl_nav" data-direction="next" data-i18n="opening_explorer.btn.suivant">Suivant →</button>
     </div>
   </div>
 
   <!-- Colonne droite : info + tableau des coups + navigation -->
-  <div style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:calc(100vh - 60px);">
+  <div class="expl-play-right">
 
-    <div style="display:flex; align-items:center; gap:8px; align-self:flex-start;">
-      <button id="expl-tts-toggle" onclick="explToggleTts()" style="background:none; border:1px solid #a0b8d0; border-radius:6px; padding:3px 10px; font-size:1rem; line-height:1.4; cursor:pointer;" title="">🔊</button>
-      <input type="range" id="expl-tts-volume" min="0" max="100" value="80" step="5" style="width:90px; accent-color:#e94560;" oninput="explSetVolume(this.value)" data-i18n-title="opening_explorer.tts.volume" title="Volume">
+    <div class="expl-play-tts-row">
+      <button id="expl-tts-toggle" class="expl-play-tts-toggle" data-action="expl_toggle_tts" title="">🔊</button>
+      <input type="range" id="expl-tts-volume" min="0" max="100" value="80" step="5" class="expl-play-tts-volume" oninput="explSetVolume(this.value)" data-i18n-title="opening_explorer.tts.volume" title="Volume">
     </div>
 
-    <div class="card" style="padding:12px 14px;">
-      <h2 id="expl-nom" style="color:#e94560; font-size:0.85rem; margin-bottom:8px;"></h2>
-      <div id="expl-coup-courant" style="font-size:0.9rem; font-weight:600; color:#1a2a3a;">—</div>
+    <div class="card expl-play-info-card">
+      <h2 id="expl-nom" class="expl-play-nom"></h2>
+      <div id="expl-coup-courant" class="expl-play-coup-courant">—</div>
     </div>
 
-    <div class="card" style="padding:14px 16px;">
+    <div class="card expl-play-moves-card">
       <div id="explorer-moves-table"></div>
     </div>
 
-    <div class="card" style="padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
-      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0;" onclick="explBackToSelect()" data-i18n="opening_explorer.btn.autre">↩ Choisir une autre ouverture</button>
-      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+    <div class="card expl-play-actions-card">
+      <button class="btn expl-play-btn-back" data-action="expl_back_to_select" data-i18n="opening_explorer.btn.autre">↩ Choisir une autre ouverture</button>
+      <button class="btn expl-play-btn-back" data-action="back_menu" data-i18n="common.retour_menu">← Retour au menu</button>
     </div>
 
   </div>
