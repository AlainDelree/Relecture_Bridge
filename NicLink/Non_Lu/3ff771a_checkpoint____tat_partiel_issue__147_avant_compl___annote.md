3ff771a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3ff771a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 18:21:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    checkpoint: état partiel issue #147 avant complétion (TTS toggle JS manquant)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/explorer_session.py b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index db614d5..d0e142b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/explorer_session.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Zone modifiée : ligne 75 (14 ligne(s)) dans l'ancienne version → ligne 75 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -75,14 +75,11 @@ class ExplorerSession:
         return self.get_state()
 
     def choose_move(self, uci: str) -> dict:
-        """Applique un coup spécifique (UCI) au lieu du coup principal.
-        Utilisé quand l'utilisateur clique sur une alternative du tableau.
-        Le coup doit être légal sur le board courant. Retourne get_state()
-        après application, ou get_state() inchangé si le coup est illégal."""
-        # Revenir à la position depuis laquelle les alternatives sont calculées
-        if self._history:
-            self._history.pop()
-            self.board.pop()
+        """Applique un coup spécifique (UCI) choisi dans le tableau des coups
+        suivants. Joue en avant depuis la position courante (ne remplace pas
+        le dernier coup joué). Le coup doit être légal sur le board courant.
+        Retourne get_state() après application, ou get_state() inchangé si
+        le coup est illégal."""
         try:
             move = chess.Move.from_uci(uci)
         except Exception:
# ── Zone modifiée : ligne 121 (30 ligne(s)) dans l'ancienne version → ligne 118 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -121,30 +118,24 @@ class ExplorerSession:
             last_move_uci = None
             move_san      = None
         # Les alternatives représentent les coups candidats DEPUIS la position
-        # avant le dernier coup joué (pour expliquer ce choix) — pas depuis la
-        # position courante. On rejoue donc sur un board temporaire dépilé.
+        # courante (que jouer ensuite), pas depuis la position avant le
+        # dernier coup joué. Si la source n'a rien à proposer (fin de ligne
+        # connue), le tableau reste vide — aucun fallback à 100%.
         alternatives = []
         if self.source is not None:
             try:
-                alt_board = self.board.copy()
-                if self._history:
-                    alt_board.pop()
-                for alt in self.source.get_alternatives(alt_board):
+                for alt in self.source.get_alternatives(self.board):
                     try:
-                        san = san_ep(alt_board, chess.Move.from_uci(alt["uci"]))
+                        san = san_ep(self.board, chess.Move.from_uci(alt["uci"]))
                     except Exception:
                         san = alt["uci"]
                     alternatives.append({"uci": alt["uci"], "san": san, "weight": alt.get("weight", 0)})
             except Exception:
                 alternatives = []
-        if not alternatives and last_move_uci is not None:
-            # Source sans alternatives (ex. PGNLineSource) : le coup joué
-            # reste la seule entrée du tableau, à 100%.
-            alternatives = [{"uci": last_move_uci, "san": move_san, "weight": 1}]
         return {
             "fen":            self.board.fen(),
             "last_move_uci":  last_move_uci,
-            "main_move_uci":  last_move_uci,
+            "main_move_uci":  None,
             "move_index":     len(self._history),
             "move_san":       move_san,
             "opening_name":   getattr(self.source, "nom", "") if self.source else "",
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# (index — ignorable)
index f116a9f..8c345db 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 10 (8 ligne(s)) dans l'ancienne version → ligne 10 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -10,8 +10,12 @@ import logging
 logger = logging.getLogger("niclink.opening_explorer.tts")
 
 
-def speak(text: str, rate: int = 150, enabled: bool = False) -> None:
-    """Prononce `text` à voix haute si `enabled`. Bloquant — à appeler
+VOICE_MAP = {"fr": "fr", "en": "en", "de": "de"}
+
+
+def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr") -> None:
+    """Prononce `text` à voix haute si `enabled`, dans la langue `language`
+    (voix espeak-ng correspondante si disponible). Bloquant — à appeler
     depuis un thread daemon, jamais depuis le thread principal.
     Erreur silencieuse (moteur TTS absent, espeak-ng manquant, etc.).
     """
# ── Zone modifiée : ligne 21 (6 ligne(s)) dans l'ancienne version → ligne 25 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -21,6 +25,12 @@ def speak(text: str, rate: int = 150, enabled: bool = False) -> None:
         import pyttsx3
         engine = pyttsx3.init()
         engine.setProperty("rate", rate)
+        lang = VOICE_MAP.get(language, "fr")
+        voices = engine.getProperty("voices")
+        for v in voices:
+            if lang in v.id.lower() or lang in (v.name or "").lower():
+                engine.setProperty("voice", v.id)
+                break
         engine.say(text)
         engine.runAndWait()
     except Exception as e:
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index 84364d0..9493cf1 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 657 (7 ligne(s)) dans l'ancienne version → ligne 657 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -657,7 +657,7 @@ def _emit_explorer_explanation(sid, state, language):
     )
     if expl:
         socketio.emit("explorer_explanation", {"text": expl}, to=sid)
-        speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False))
+        speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
 
 
 def _emit_explorer_chat_response(sid, question, state, language):
# ── Zone modifiée : ligne 670 (7 ligne(s)) dans l'ancienne version → ligne 670 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -670,7 +670,7 @@ def _emit_explorer_chat_response(sid, question, state, language):
     response = get_chat_response(question, state, language, cfg)
     if response:
         socketio.emit("explorer_chat_response", {"text": response}, to=sid)
-        speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False))
+        speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
 
 
 @socketio.on("explorer_load")
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 52ad0b8..833a93a 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6018 (6 ligne(s)) dans l'ancienne version → ligne 6018 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6018,6 +6018,9 @@ socket.on("config_data", (data) => {
 
   _explHasApiKey = !!(data.llm_api_key && data.llm_api_key.trim());
   explUpdateChatAvailability();
+
+  _explTtsEnabled = !!data.tts_enabled;
+  explUpdateTtsToggle();
 });
 
 function parametresSave() {
# ── Zone modifiée : ligne 6203 (26 ligne(s)) dans l'ancienne version → ligne 6206 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6203,26 +6206,22 @@ function explRenderMovesTable(data) {
 
   const total = alternatives.reduce((sum, a) => sum + (a.weight || 0), 0) || 1;
   const sorted = [...alternatives].sort((a, b) => (b.weight || 0) - (a.weight || 0));
-  const mainUci = data.main_move_uci || data.last_move_uci || null;
 
   const table = document.createElement("div");
   table.style.cssText = "display:flex; flex-direction:column; gap:6px; margin-top:8px;";
   for (const alt of sorted.slice(0, 6)) {
     const pct = Math.round(((alt.weight || 0) / total) * 100);
-    const isMain = mainUci !== null && alt.uci === mainUci;
 
     const row = document.createElement("div");
+    row.className = "expl-move-row";
     row.style.cssText = "display:flex; align-items:center; gap:8px; font-size:0.82rem;";
-    if (!isMain) {
-      row.style.cursor = "pointer";
-      row.title = alt.san || alt.uci;
-      row.addEventListener("click", () => {
-        socket.emit("explorer_choose_move", { uci: alt.uci, language: i18n.locale() });
-      });
-    }
+    row.title = alt.san || alt.uci;
+    row.addEventListener("click", () => {
+      socket.emit("explorer_choose_move", { uci: alt.uci, language: i18n.locale() });
+    });
 
     const sanEl = document.createElement("div");
-    sanEl.style.cssText = `width:52px; flex-shrink:0; color:#1a2a3a; ${isMain ? "font-weight:700;" : ""}`;
+    sanEl.style.cssText = "width:52px; flex-shrink:0; color:#1a2a3a;";
     sanEl.textContent = alt.san || alt.uci;
     row.appendChild(sanEl);
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index b1a3564..17e42c7 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 16 (7 ligne(s)) dans l'ancienne version → ligne 16 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -16,7 +16,7 @@
     #screen-retrans-game            { --bd-min: 280px; --bd-max: 460px; --bd-vw-offset: 460px; }
     #screen-exercice-running        { --bd-min: 280px; --bd-max: 460px; --bd-vw-offset: 660px; --bd-vh-offset: 220px; }
     #screen-labo                    { --bd-min: 280px; --bd-max: 500px; --bd-vw-offset: 740px; --bd-vh-offset: 190px; }
-    #screen-opening-explorer-play   { --bd-min: 280px; --bd-max: 460px; --bd-vw-offset: 660px; --bd-vh-offset: 220px; }
+    #screen-opening-explorer-play   { --bd-min: 280px; --bd-max: 460px; --bd-vw-offset: 680px; --bd-vh-offset: 220px; }
 
     /* Taille calculée — héritée par tous les descendants */
     #screen-game, .screen-board-layout,
# ── Zone modifiée : ligne 744 (8 ligne(s)) dans l'ancienne version → ligne 744 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -744,8 +744,8 @@
     .res-medium .screen-board-layout,
     .res-medium #screen-game,
     .res-medium #screen-exercice-running,
-    .res-medium #screen-labo,
-    .res-medium #screen-opening-explorer-play { grid-template-columns: 180px minmax(0,1fr) 320px !important; gap: 14px !important; padding: 12px 14px !important; }
+    .res-medium #screen-labo { grid-template-columns: 180px minmax(0,1fr) 320px !important; gap: 14px !important; padding: 12px 14px !important; }
+    .res-medium #screen-opening-explorer-play { grid-template-columns: 320px minmax(0,1fr) 200px !important; gap: 14px !important; padding: 12px 14px !important; }
     .res-medium #left-panel            { width: 180px; }
     .res-medium #panel                 { width: 320px; }
 
# ── Zone modifiée : ligne 771 (6 ligne(s)) dans l'ancienne version → ligne 771 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -771,6 +771,9 @@
     .res-small #left-panel             { width: 100%; }
     .res-small #panel                  { width: 100%; }
 
+.expl-move-row { cursor: pointer; transition: opacity 0.15s; }
+.expl-move-row:hover { opacity: 0.8; }
+
 @keyframes spin { to { transform: rotate(360deg); } }
 #modal-overlay { display: none; }
 #modal-overlay.open { display: flex; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index fdd63d5..967a30b 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1635 (14 ligne(s)) dans l'ancienne version → ligne 1635 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1635,14 +1635,24 @@
 </div>
 
 <!-- ── Écran Opening Explorer — lecteur ── -->
-<div id="screen-opening-explorer-play" style="display:none; flex:1; grid-template-columns:220px minmax(0,1fr) 380px; gap:20px; padding:16px 20px; width:100%; max-width:100vw; align-items:start; overflow:hidden;">
+<div id="screen-opening-explorer-play" style="display:none; flex:1; grid-template-columns:380px minmax(0,1fr) 240px; gap:20px; padding:16px 20px; width:100%; max-width:100vw; align-items:start; overflow:hidden;">
 
-  <!-- Colonne gauche : info -->
-  <div style="display:flex; flex-direction:column; gap:8px;">
-    <div class="card" style="padding:12px 14px;">
-      <h2 id="expl-nom" style="color:#e94560; font-size:0.85rem; margin-bottom:8px;"></h2>
-      <div id="expl-coup-courant" style="font-size:0.9rem; font-weight:600; color:#1a2a3a;">—</div>
+  <!-- Colonne gauche : panneau IA (explication + chat) -->
+  <div style="display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px);">
+
+    <div class="card" style="padding:14px 16px;">
+      <h2 data-i18n="opening_explorer.h2.explication">EXPLICATION</h2>
+      <div id="explorer-explanation" style="font-size:0.85rem; color:#3a5a7a; line-height:1.5;"></div>
     </div>
+
+    <div class="card" style="padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
+      <div id="explorer-chat-history" style="font-size:0.82rem; color:#3a5a7a; max-height:200px; overflow-y:auto; display:flex; flex-direction:column; gap:6px;"></div>
+      <div style="display:flex; gap:6px;">
+        <input type="text" id="explorer-chat-input" style="flex:1; padding:6px 10px; border:1px solid #a0b8d0; border-radius:6px; font-size:0.85rem;" placeholder="Posez une question..." data-i18n-placeholder="opening_explorer.chat.placeholder">
+        <button id="explorer-chat-send-btn" class="btn btn-continuer" style="margin:0; padding:6px 12px; font-size:0.82rem;" onclick="explChatSend()" data-i18n="opening_explorer.chat.envoyer">Envoyer</button>
+      </div>
+    </div>
+
   </div>
 
   <!-- Colonne centre : échiquier -->
# ── Zone modifiée : ligne 1663 (24 ligne(s)) dans l'ancienne version → ligne 1673 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1663,24 +1673,18 @@
     </div>
   </div>
 
-  <!-- Colonne droite : explication + actions -->
-  <div style="display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px);">
+  <!-- Colonne droite : info + tableau des coups + navigation -->
+  <div style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:calc(100vh - 60px);">
 
-    <div class="card" style="padding:14px 16px;">
-      <div id="explorer-moves-table"></div>
-    </div>
+    <button id="expl-tts-toggle" onclick="explToggleTts()" style="align-self:flex-start; background:none; border:1px solid #a0b8d0; border-radius:6px; padding:3px 10px; font-size:1rem; line-height:1.4; cursor:pointer;" title="">🔊</button>
 
-    <div class="card" style="padding:14px 16px;">
-      <h2 data-i18n="opening_explorer.h2.explication">EXPLICATION</h2>
-      <div id="explorer-explanation" style="font-size:0.85rem; color:#3a5a7a; line-height:1.5;"></div>
+    <div class="card" style="padding:12px 14px;">
+      <h2 id="expl-nom" style="color:#e94560; font-size:0.85rem; margin-bottom:8px;"></h2>
+      <div id="expl-coup-courant" style="font-size:0.9rem; font-weight:600; color:#1a2a3a;">—</div>
     </div>
 
-    <div class="card" style="padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
-      <div id="explorer-chat-history" style="font-size:0.82rem; color:#3a5a7a; max-height:200px; overflow-y:auto; display:flex; flex-direction:column; gap:6px;"></div>
-      <div style="display:flex; gap:6px;">
-        <input type="text" id="explorer-chat-input" style="flex:1; padding:6px 10px; border:1px solid #a0b8d0; border-radius:6px; font-size:0.85rem;" placeholder="Posez une question..." data-i18n-placeholder="opening_explorer.chat.placeholder">
-        <button id="explorer-chat-send-btn" class="btn btn-continuer" style="margin:0; padding:6px 12px; font-size:0.82rem;" onclick="explChatSend()" data-i18n="opening_explorer.chat.envoyer">Envoyer</button>
-      </div>
+    <div class="card" style="padding:14px 16px;">
+      <div id="explorer-moves-table"></div>
     </div>
 
     <div class="card" style="padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
