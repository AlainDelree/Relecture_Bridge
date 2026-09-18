4d68ac3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4d68ac3
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 21:03:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #100 — ajustements menu accueil suite test réel (issue #99 suite)
    
    - checkbox mode virtuel : clic limité à menu-card-head, état préservé au retour menu
    - tour header : couleur d'origine (suppression override vert)
    - suppression textes menu-subtitle et hh-status-label
    - icône 🖥 dans labels Analyse/Retranscrire (i18n fr/en/de) au lieu du label Mode virtuel
    - bouton de reconnexion visible (au lieu d'un lien discret)
    - bordure verte 3px header + filigrane damier menu-grid selon état échiquier

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6a191e9..36d2519 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 237 (18 ligne(s)) dans l'ancienne version → ligne 237 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -237,18 +237,11 @@ function _launchVirtual(mode) {
 
 function toggleVirtualMode(enabled) {
   _virtualMode = enabled;
-  const sub = document.querySelector(".menu-subtitle");
   const link = document.getElementById("btn-reconnect");
   if (enabled) {
-    if (sub) { sub.textContent = t("menu.sous_titre_virtuel"); }
     if (link) { link.style.display = "none"; }
   } else {
     if (link) { link.style.display = _boardOk ? "none" : ""; }
-    if (_boardOk) {
-      if (sub) { sub.textContent = t("menu.sous_titre_connecte"); }
-    } else {
-      if (sub) { sub.textContent = t("menu.verification_echiquier"); }
-    }
   }
   // Le badge échiquier ne dépend plus de _virtualMode (2 états : connecté / non détecté).
 }
# ── Zone modifiée : ligne 259 (8 ligne(s)) dans l'ancienne version → ligne 252 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -259,8 +252,9 @@ function _syncVirtualCheckboxes() {
 }
 
 // Lance le mode d'une carte (Pédagogique/Labo/Exercices) — virtuel si la case est cochée
-function _menuCardLaunch(mode, cardEl) {
-  const chk = cardEl.querySelector(".menu-card-chk");
+function _menuCardLaunch(mode, headEl) {
+  const card = headEl.closest(".menu-card");
+  const chk = card ? card.querySelector(".menu-card-chk") : null;
   if (chk && chk.checked) {
     _launchVirtual(mode);
   } else {
# ── Zone modifiée : ligne 268 (7 ligne(s)) dans l'ancienne version → ligne 262 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -268,7 +262,7 @@ function _menuCardLaunch(mode, cardEl) {
   }
 }
 
-// Met à jour le header (fond + filigrane + pill) et le statut HH selon l'état de l'échiquier
+// Met à jour le header (fond + filigrane + pill) et le filigrane du menu selon l'état de l'échiquier
 function _applyBoardBadge() {
   const header = document.getElementById("app-header");
   const pill   = document.getElementById("board-status-pill");
# ── Zone modifiée : ligne 280 (11 ligne(s)) dans l'ancienne version → ligne 274 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -280,11 +274,8 @@ function _applyBoardBadge() {
     pill.classList.toggle("pill-disconnected", !_boardOk);
     text.textContent = t(_boardOk ? "status.board.connecte" : "status.board.sans_echiquier");
   }
-  const hhLabel = document.getElementById("hh-status-label");
-  if (hhLabel) {
-    hhLabel.classList.toggle("hh-ready", _boardOk);
-    hhLabel.textContent = t(_boardOk ? "menu.hh.pret" : "menu.hh.requiert_echiquier");
-  }
+  const menuDeco = document.getElementById("menu-grid-deco");
+  if (menuDeco) menuDeco.classList.toggle("deco-connected", _boardOk);
 }
 
 
# ── Zone modifiée : ligne 892 (15 ligne(s)) dans l'ancienne version → ligne 883 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -892,15 +883,8 @@ socket.on("app_state", (data) => {
     // Quitter le mode virtuel au retour au menu (badge échiquier repasse en mode physique)
     if (_virtualMode) {
       _virtualMode = false;
-      const sub = document.querySelector(".menu-subtitle");
       const link = document.getElementById("btn-reconnect");
       if (link) link.style.display = _boardOk ? "none" : "";
-      if (_boardOk) {
-        if (sub) { sub.textContent = t("menu.sous_titre_connecte"); }
-      } else {
-        if (sub) { sub.textContent = t("menu.verification_echiquier"); }
-      }
-      _syncVirtualCheckboxes();
     }
     // Vider les champs de config HH
     const wName = document.getElementById("cfg-white-name");
# ── Zone modifiée : ligne 1285 (18 ligne(s)) dans l'ancienne version → ligne 1269 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1285,18 +1269,6 @@ function _refreshDynamicLabels() {
   const reconnectLink = document.getElementById("btn-reconnect");
   if (reconnectLink) reconnectLink.textContent = t("menu.btn.reconnect_label");
 
-  // Sous-titre menu (plus de message d'erreur rouge — le header communique l'état)
-  const sub = document.querySelector(".menu-subtitle");
-  if (sub) {
-    if (_virtualMode) {
-      sub.textContent = t("menu.sous_titre_virtuel");
-    } else if (_boardOk) {
-      sub.textContent = t("menu.sous_titre_connecte");
-    } else {
-      sub.textContent = t("menu.verification_echiquier");
-    }
-  }
-
   // Titre bouton flip
   const flipBtn = document.getElementById("btn-flip");
   if (flipBtn) flipBtn.title = t(_boardFlipped ? "game.flip_blancs" : "game.flip_noirs");
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index af81fc5..893bf1b 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 48 (14 ligne(s)) dans l'ancienne version → ligne 48 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -48,14 +48,13 @@
       border-bottom: 2px solid #a0b8d0;
       transition: background 0.3s;
     }
-    header.header-connected { background: #E1F5EE; }
+    header.header-connected { background: #E1F5EE; border-bottom: 3px solid #0F6E56; }
 
     header h1 {
       font-size: 1.4rem;
       color: #e94560;
       letter-spacing: 1px;
     }
-    header.header-connected #header-icon { color: #0F6E56; }
 
     /* Filigrane décoratif — grille d'échiquier 5×4 en coin droit */
     .board-deco {
# ── Zone modifiée : ligne 170 (10 ligne(s)) dans l'ancienne version → ligne 169 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -170,10 +169,6 @@
       letter-spacing: 3px;
       margin-bottom: 8px;
     }
-    .menu-subtitle {
-      color: #1a2a3a;
-      margin-bottom: 20px;
-    }
     .menu-btn {
       width: 300px;
       padding: 14px 20px;
# ── Zone modifiée : ligne 225 (28 ligne(s)) dans l'ancienne version → ligne 220 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -225,28 +220,13 @@
     .menu-card-primary   .menu-card-sep { background: rgba(255,255,255,0.25); }
     .menu-card-secondary { background: #c2d4e8; color: #1a2a3a; }
 
-    /* Label statique "Mode virtuel" (Analyse, Retranscription) + statut HH */
-    .menu-static-label, .menu-hh-status {
-      font-size: 0.78rem;
-      font-weight: 500;
-      color: #6a7a8a;
-      text-align: center;
-      margin-top: 6px;
-    }
-    .menu-hh-status.hh-ready { color: #0F6E56; font-weight: 600; }
-
-    /* Lien discret de reconnexion manuelle (remplace l'ancien bouton) */
-    .menu-reconnect-link {
+    /* Bouton de reconnexion manuelle — visible uniquement si échiquier non détecté */
+    .menu-btn-reconnect {
       display: none;
+      background: #e94560;
+      color: white;
       margin-top: 8px;
-      font-size: 0.8rem;
-      color: #3a5a7a;
-      text-decoration: underline;
-      cursor: pointer;
-      opacity: 0.75;
-      transition: opacity 0.2s;
     }
-    .menu-reconnect-link:hover { opacity: 1; }
 
     .menu-btn-wrap {
       display: flex; flex-direction: column; align-items: center; gap: 0;
# ── Zone modifiée : ligne 294 (6 ligne(s)) dans l'ancienne version → ligne 274 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -294,6 +274,7 @@
 
     /* ── Menu 2 colonnes (Jouer / Outils) ── */
     .menu-grid {
+      position: relative;
       display: grid;
       grid-template-columns: repeat(2, auto);
       justify-content: center;
# ── Zone modifiée : ligne 301 (6 ligne(s)) dans l'ancienne version → ligne 282 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -301,6 +282,28 @@
       column-gap: 48px;
       row-gap: 20px;
     }
+
+    /* Filigrane décoratif — grille d'échiquier en damier, à gauche de la colonne Jouer.
+       Change de couleur selon l'état de l'échiquier (voir _applyBoardBadge en JS). */
+    .menu-grid-deco {
+      position: absolute;
+      top: 0;
+      left: -110px;
+      width: 90px;
+      height: 100%;
+      background-image:
+        linear-gradient(45deg, #8a97a6 25%, transparent 25%, transparent 75%, #8a97a6 75%),
+        linear-gradient(45deg, #8a97a6 25%, transparent 25%, transparent 75%, #8a97a6 75%);
+      background-size: 26px 26px;
+      background-position: 0 0, 13px 13px;
+      opacity: 0.12;
+      pointer-events: none;
+    }
+    .menu-grid-deco.deco-connected {
+      background-image:
+        linear-gradient(45deg, #0F6E56 25%, transparent 25%, transparent 75%, #0F6E56 75%),
+        linear-gradient(45deg, #0F6E56 25%, transparent 25%, transparent 75%, #0F6E56 75%);
+    }
     .menu-col {
       display: flex;
       flex-direction: column;
# ── Zone modifiée : ligne 332 (6 ligne(s)) dans l'ancienne version → ligne 335 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -332,6 +335,7 @@
     @media (max-width: 700px) {
       .menu-grid { grid-template-columns: 1fr; row-gap: 10px; }
       .menu-col-outils .menu-col-title { margin-top: 10px; }
+      .menu-grid-deco { display: none; }
     }
 
     /* ── Écran config ── */
# ── Zone modifiée : ligne 732 (6 ligne(s)) dans l'ancienne version → ligne 736 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -732,6 +736,7 @@
     .res-medium #panel                 { width: 320px; }
 
     /* ── res-small : < 1100px ── */
+    .res-small .menu-grid-deco         { display: none; }
     .res-small .menu-btn               { width: 240px; font-size: 0.85rem; }
     .res-small .menu-btn-wrap          { width: 240px; margin-bottom: 4px; }
     .res-small .menu-card               { width: 240px; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index 812fb05..de701f7 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 25 (10 ligne(s)) dans l'ancienne version → ligne 25 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,10 +25,10 @@
   "menu.sous_titre_attente":   "Warte auf Brett…",
   "menu.btn.pedagogique":      "🎓 Trainingsmodus",
   "menu.btn.humain":           "⚔️ Mensch gegen Mensch",
-  "menu.btn.analyse":          "📊 Partieanalyse",
+  "menu.btn.analyse":          "🖥 📊 Partieanalyse",
   "menu.btn.labo":             "🔬 Labor",
   "menu.btn.exercices":        "📚 Übungen",
-  "menu.btn.retranscrire":     "✏️ Mitschreiben",
+  "menu.btn.retranscrire":     "🖥 ✏️ Mitschreiben",
   "menu.btn.outils":           "🛠️ Übungs-Tools",
   "menu.btn.reconnect":        "🔌 Brett neu verbinden",
   "menu.btn.debloquer":        "⟳ Schaltflächen entsperren",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index 7f7bcc6..9f928b4 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 25 (10 ligne(s)) dans l'ancienne version → ligne 25 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,10 +25,10 @@
   "menu.sous_titre_attente":   "Waiting for board…",
   "menu.btn.pedagogique":      "🎓 Training Mode",
   "menu.btn.humain":           "⚔️ Human vs Human",
-  "menu.btn.analyse":          "📊 Game Analysis",
+  "menu.btn.analyse":          "🖥 📊 Game Analysis",
   "menu.btn.labo":             "🔬 Laboratory",
   "menu.btn.exercices":        "📚 Exercises",
-  "menu.btn.retranscrire":     "✏️ Transcribe",
+  "menu.btn.retranscrire":     "🖥 ✏️ Transcribe",
   "menu.btn.outils":           "🛠️ Exercise Tools",
   "menu.btn.reconnect":        "🔌 Reconnect board",
   "menu.btn.debloquer":        "⟳ Unlock buttons",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index 5dc6e52..75219f5 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 25 (10 ligne(s)) dans l'ancienne version → ligne 25 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,10 +25,10 @@
   "menu.sous_titre_attente":   "En attente de l'échiquier…",
   "menu.btn.pedagogique":      "🎓 Mode Pédagogique",
   "menu.btn.humain":           "⚔️ Humain vs Humain",
-  "menu.btn.analyse":          "📊 Analyse de partie",
+  "menu.btn.analyse":          "🖥 📊 Analyse de partie",
   "menu.btn.labo":             "🔬 Laboratoire",
   "menu.btn.exercices":        "📚 Exercices",
-  "menu.btn.retranscrire":     "✏️ Retranscrire",
+  "menu.btn.retranscrire":     "🖥 ✏️ Retranscrire",
   "menu.btn.outils":           "🛠️ Outils Exercices",
   "menu.btn.reconnect":        "🔌 Reconnecter l'échiquier",
   "menu.btn.debloquer":        "⟳ Débloquer les boutons",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index bd068c2..ea830ad 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 47 (19 ligne(s)) dans l'ancienne version → ligne 47 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,19 +47,19 @@
 <!-- ── Écran menu ── -->
 <div id="screen-menu">
   <div class="menu-title"><span style="font-size:1.3em; line-height:1;">♜</span> AlChess</div>
-  <div class="menu-subtitle" data-i18n="menu.verification_echiquier">Vérification de l'échiquier…</div>
 
   <div class="menu-grid">
+    <div class="menu-grid-deco" id="menu-grid-deco" aria-hidden="true"></div>
 
     <!-- ── Colonne GAUCHE : Jouer ── -->
     <div class="menu-col menu-col-jouer">
       <div class="menu-col-title" data-i18n="menu.col.jouer">Jouer</div>
 
       <div class="menu-btn-wrap">
-        <div class="menu-card menu-card-primary" onclick="_menuCardLaunch('pedagogique', this)">
-          <div class="menu-card-head">♟ <span data-i18n="menu.btn.pedagogique">🎓 Mode Pédagogique</span></div>
+        <div class="menu-card menu-card-primary">
+          <div class="menu-card-head" onclick="_menuCardLaunch('pedagogique', this)">♟ <span data-i18n="menu.btn.pedagogique">🎓 Mode Pédagogique</span></div>
           <div class="menu-card-sep"></div>
-          <div class="menu-card-foot" onclick="event.stopPropagation()">
+          <div class="menu-card-foot">
             <label class="menu-card-chk-label">
               <input type="checkbox" class="menu-card-chk" checked>
               <span data-i18n="menu.mode_virtuel_label">Mode virtuel</span>
# ── Zone modifiée : ligne 71 (15 ligne(s)) dans l'ancienne version → ligne 71 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -71,15 +71,14 @@
 
       <div class="menu-btn-wrap">
         <button class="menu-btn menu-btn-humain" data-needs-board data-physical-only disabled onclick="sendAction({type:'mode', value:'humain'})" data-i18n="menu.btn.humain">⚔️ Humain vs Humain</button>
-        <div class="menu-hh-status" id="hh-status-label" data-i18n="menu.hh.requiert_echiquier">Échiquier requis</div>
         <div class="menu-btn-desc" id="desc-humain" data-i18n="menu.desc.humain">Deux joueurs s'affrontent sur l'échiquier physique. L'ordinateur vérifie la légalité des coups et enregistre la partie pour analyse ultérieure.</div>
       </div>
 
       <div class="menu-btn-wrap">
-        <div class="menu-card menu-card-secondary" onclick="_menuCardLaunch('labo', this)">
-          <div class="menu-card-head">♟ <span data-i18n="menu.btn.labo">🔬 Laboratoire</span></div>
+        <div class="menu-card menu-card-secondary">
+          <div class="menu-card-head" onclick="_menuCardLaunch('labo', this)">♟ <span data-i18n="menu.btn.labo">🔬 Laboratoire</span></div>
           <div class="menu-card-sep"></div>
-          <div class="menu-card-foot" onclick="event.stopPropagation()">
+          <div class="menu-card-foot">
             <label class="menu-card-chk-label">
               <input type="checkbox" class="menu-card-chk" checked>
               <span data-i18n="menu.mode_virtuel_label">Mode virtuel</span>
# ── Zone modifiée : ligne 90 (10 ligne(s)) dans l'ancienne version → ligne 89 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,10 +89,10 @@
       </div>
 
       <div class="menu-btn-wrap">
-        <div class="menu-card menu-card-secondary" onclick="_menuCardLaunch('exercices', this)">
-          <div class="menu-card-head">♟ <span data-i18n="menu.btn.exercices">📚 Exercices</span></div>
+        <div class="menu-card menu-card-secondary">
+          <div class="menu-card-head" onclick="_menuCardLaunch('exercices', this)">♟ <span data-i18n="menu.btn.exercices">📚 Exercices</span></div>
           <div class="menu-card-sep"></div>
-          <div class="menu-card-foot" onclick="event.stopPropagation()">
+          <div class="menu-card-foot">
             <label class="menu-card-chk-label">
               <input type="checkbox" class="menu-card-chk" checked>
               <span data-i18n="menu.mode_virtuel_label">Mode virtuel</span>
# ── Zone modifiée : ligne 110 (14 ligne(s)) dans l'ancienne version → ligne 109 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -110,14 +109,12 @@
       <div class="menu-col-title" data-i18n="menu.col.outils">Outils</div>
 
       <div class="menu-btn-wrap">
-        <button class="menu-btn menu-btn-analyse" onclick="sendAction({type:'mode', value:'analyse'})" data-i18n="menu.btn.analyse">📊 Analyse de partie</button>
-        <div class="menu-static-label" data-i18n="menu.mode_virtuel_label">Mode virtuel</div>
+        <button class="menu-btn menu-btn-analyse" onclick="sendAction({type:'mode', value:'analyse'})" data-i18n="menu.btn.analyse">🖥 📊 Analyse de partie</button>
         <div class="menu-btn-desc" id="desc-analyse" data-i18n="menu.desc.analyse">Importez un fichier PGN (depuis Chess.com, Lichess…) et rejouez la partie coup par coup avec l'analyse du moteur.</div>
       </div>
 
       <div class="menu-btn-wrap">
-        <button class="menu-btn menu-btn-retrans" onclick="sendAction({type:'mode', value:'retranscription'})" data-i18n="menu.btn.retranscrire">✏️ Retranscrire</button>
-        <div class="menu-static-label" data-i18n="menu.mode_virtuel_label">Mode virtuel</div>
+        <button class="menu-btn menu-btn-retrans" onclick="sendAction({type:'mode', value:'retranscription'})" data-i18n="menu.btn.retranscrire">🖥 ✏️ Retranscrire</button>
         <div class="menu-btn-desc" id="desc-retrans" data-i18n="menu.desc.retrans">Retranscrivez une partie jouée sur papier. Saisissez les coups sur l'échiquier virtuel et exportez le PGN.</div>
       </div>
 
# ── Zone modifiée : ligne 130 (7 ligne(s)) dans l'ancienne version → ligne 127 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -130,7 +127,7 @@
 
   </div><!-- fin menu-grid -->
 
-  <a href="#" id="btn-reconnect" class="menu-reconnect-link" onclick="sendAction({type:'reconnect_board'}); return false;" data-i18n="menu.btn.reconnect_label">⟳ Reconnecter l'échiquier</a>
+  <button id="btn-reconnect" class="menu-btn menu-btn-reconnect" onclick="sendAction({type:'reconnect_board'})" data-i18n="menu.btn.reconnect_label">⟳ Reconnecter l'échiquier</button>
 
 
   <button class="menu-btn" onclick="ouvrirModal('quit', t('modal.quitter_alchess'), t('modal.quitter_btn'), 'btn-warning')" style="background:#b8cce0; color:#555; border:1px solid #333; font-size:0.85rem; margin-top:8px;" data-i18n="menu.btn.quitter">✕ Quitter</button>
