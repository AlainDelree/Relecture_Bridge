1d1a4be

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1d1a4be
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 09:41:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: slider volume TTS explorer, --scale mpg123 (issue #176, suite #174)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/config_manager.py b/nicsoft/core/config_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ff39038..fc08fea 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/config_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/config_manager.py
# ── Zone modifiée : ligne 26 (6 ligne(s)) dans l'ancienne version → ligne 26 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -26,6 +26,7 @@ DEFAULT_CONFIG = {
     "llm_model": "",            # optionnel, laisser vide = modèle par défaut
     "tts_enabled": False,
     "tts_rate": 150,            # débit pyttsx3, mots par minute
+    "tts_volume": 80,           # volume mpg123, 0-100
 }
 
 
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# (index — ignorable)
index c0146f7..590c70b 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 103 (7 ligne(s)) dans l'ancienne version → ligne 103 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -103,7 +103,7 @@ def check_internet() -> bool:
         return False
 
 
-def _speak_edge(text: str, rate: int, language: str, on_playback_start=None) -> bool:
+def _speak_edge(text: str, rate: int, language: str, volume: int = 80, on_playback_start=None) -> bool:
     """Essaie de parler via edge-tts. Retourne True si succès, False sinon."""
     global _tts_generation
     try:
# ── Zone modifiée : ligne 113 (6 ligne(s)) dans l'ancienne version → ligne 113 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -113,6 +113,8 @@ def _speak_edge(text: str, rate: int, language: str, on_playback_start=None) ->
         # rate edge-tts : "+0%" = 150 mots/min ≈ normal
         # on convertit le rate (mots/min) en pourcentage relatif
         rate_pct = f"+{int((rate - 150) / 1.5)}%" if rate != 150 else "+0%"
+        # mpg123 --scale : 0-32768, 32768 = 100%
+        scale = str(int(max(0, min(100, volume)) / 100 * 32768))
         my_gen = _tts_generation
 
         async def _run():
# ── Zone modifiée : ligne 124 (7 ligne(s)) dans l'ancienne version → ligne 126 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -124,7 +126,7 @@ def _speak_edge(text: str, rate: int, language: str, on_playback_start=None) ->
                 await communicate.save(tmp)
                 if _tts_generation != my_gen:
                     return  # stop_speaking() appelé pendant le download
-                proc = subprocess.Popen(["mpg123", "-q", tmp])
+                proc = subprocess.Popen(["mpg123", "-q", "--scale", scale, tmp])
                 _current_tts_process = proc
                 if on_playback_start:
                     on_playback_start()
# ── Zone modifiée : ligne 166 (7 ligne(s)) dans l'ancienne version → ligne 168 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -166,7 +168,7 @@ def stop_speaking() -> None:
         _current_tts_process = None
 
 
-def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr", on_playback_start=None) -> bool:
+def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr", volume: int = 80, on_playback_start=None) -> bool:
     """Prononce `text` à voix haute côté serveur si `enabled` et si internet
     est disponible (edge-tts, voix neuronale). Bloquant — à appeler depuis un
     thread daemon, jamais depuis le thread principal.
# ── Zone modifiée : ligne 181 (4 ligne(s)) dans l'ancienne version → ligne 183 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -181,4 +183,4 @@ def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr
         return False
     if not check_internet():
         return False
-    return _speak_edge(text, rate, language, on_playback_start=on_playback_start)
+    return _speak_edge(text, rate, language, volume=volume, on_playback_start=on_playback_start)
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index 8722a3d..8b03ccc 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 674 (7 ligne(s)) dans l'ancienne version → ligne 674 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -674,7 +674,7 @@ def _emit_explorer_explanation(sid, state, language, my_gen=0):
             socketio.emit("explorer_tts_start", {}, to=sid)
             def on_playing():
                 socketio.emit("explorer_tts_playing", {}, to=sid)
-            tts_ok = speak(expl, rate=cfg.get("tts_rate", 150), enabled=True, language=language, on_playback_start=on_playing)
+            tts_ok = speak(expl, rate=cfg.get("tts_rate", 150), enabled=True, language=language, volume=cfg.get("tts_volume", 80), on_playback_start=on_playing)
             socketio.emit("explorer_tts_end", {}, to=sid)
             if not tts_ok:
                 socketio.emit("explorer_tts_fallback", {"text": expl}, to=sid)
# ── Zone modifiée : ligne 694 (7 ligne(s)) dans l'ancienne version → ligne 694 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -694,7 +694,7 @@ def _emit_explorer_chat_response(sid, question, state, language):
             socketio.emit("explorer_tts_start", {}, to=sid)
             def on_playing():
                 socketio.emit("explorer_tts_playing", {}, to=sid)
-            tts_ok = speak(response, rate=cfg.get("tts_rate", 150), enabled=True, language=language, on_playback_start=on_playing)
+            tts_ok = speak(response, rate=cfg.get("tts_rate", 150), enabled=True, language=language, volume=cfg.get("tts_volume", 80), on_playback_start=on_playing)
             socketio.emit("explorer_tts_end", {}, to=sid)
             if not tts_ok:
                 socketio.emit("explorer_tts_fallback", {"text": response}, to=sid)
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 26f2456..0646bcc 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6021 (6 ligne(s)) dans l'ancienne version → ligne 6021 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6021,6 +6021,9 @@ socket.on("config_data", (data) => {
 
   _explTtsEnabled = !!data.tts_enabled;
   explUpdateTtsToggle();
+
+  const explVolume = document.getElementById("expl-tts-volume");
+  if (explVolume) explVolume.value = data.tts_volume != null ? data.tts_volume : 80;
 });
 
 function parametresSave() {
# ── Zone modifiée : ligne 6082 (6 ligne(s)) dans l'ancienne version → ligne 6085 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6082,6 +6085,10 @@ function explToggleTts() {
   if (!_explTtsEnabled) socket.emit("explorer_tts_stop", {});
 }
 
+function explSetVolume(value) {
+  socket.emit("config_save", { tts_volume: parseInt(value, 10) });
+}
+
 socket.on("app_state", (data) => {
   const selEl  = document.getElementById("screen-opening-explorer-select");
   const playEl = document.getElementById("screen-opening-explorer-play");
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index b8fdc29..8723298 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 256 (6 ligne(s)) dans l'ancienne version → ligne 256 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -256,6 +256,7 @@
   "opening_explorer.chat.no_api": "Konfigurieren Sie einen API-Schlüssel in den Einstellungen",
   "opening_explorer.tts.on": "🔊 Sprache aktiviert",
   "opening_explorer.tts.off": "🔇 Sprache deaktiviert",
+  "opening_explorer.tts.volume": "Lautstärke",
   "outils.titre": "🛠️ Übungs-Tools",
   "outils.import_pgn.titre": "📥 Meine PGN-Linien importieren",
   "outils.import_pgn.desc": "Eine oder mehrere .pgn-Dateien in Ihre persönlichen Übungen importieren (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index fcc1cea..cd9cc85 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 256 (6 ligne(s)) dans l'ancienne version → ligne 256 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -256,6 +256,7 @@
   "opening_explorer.chat.no_api": "Configure an API key in Settings to enable chat",
   "opening_explorer.tts.on": "🔊 Voice enabled",
   "opening_explorer.tts.off": "🔇 Voice disabled",
+  "opening_explorer.tts.volume": "Volume",
   "outils.titre": "🛠️ Exercise Tools",
   "outils.import_pgn.titre": "📥 Import my PGN lines",
   "outils.import_pgn.desc": "Select one or more .pgn files to import into your personal exercises (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index beea283..bc46936 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 256 (6 ligne(s)) dans l'ancienne version → ligne 256 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -256,6 +256,7 @@
   "opening_explorer.chat.no_api": "Configurez une clé API dans Paramètres pour activer le chat",
   "opening_explorer.tts.on": "🔊 Voix activée",
   "opening_explorer.tts.off": "🔇 Voix désactivée",
+  "opening_explorer.tts.volume": "Volume",
   "outils.titre": "🛠️ Outils Exercices",
   "outils.import_pgn.titre": "📥 Importer mes lignes PGN",
   "outils.import_pgn.desc": "Sélectionnez un ou plusieurs fichiers .pgn pour les importer dans vos exercices personnels (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 2dde356..df53c95 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1685 (7 ligne(s)) dans l'ancienne version → ligne 1685 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1685,7 +1685,10 @@
   <!-- Colonne droite : info + tableau des coups + navigation -->
   <div style="display:flex; flex-direction:column; gap:8px; overflow-y:auto; max-height:calc(100vh - 60px);">
 
-    <button id="expl-tts-toggle" onclick="explToggleTts()" style="align-self:flex-start; background:none; border:1px solid #a0b8d0; border-radius:6px; padding:3px 10px; font-size:1rem; line-height:1.4; cursor:pointer;" title="">🔊</button>
+    <div style="display:flex; align-items:center; gap:8px; align-self:flex-start;">
+      <button id="expl-tts-toggle" onclick="explToggleTts()" style="background:none; border:1px solid #a0b8d0; border-radius:6px; padding:3px 10px; font-size:1rem; line-height:1.4; cursor:pointer;" title="">🔊</button>
+      <input type="range" id="expl-tts-volume" min="0" max="100" value="80" step="5" style="width:90px; accent-color:#e94560;" oninput="explSetVolume(this.value)" data-i18n-title="opening_explorer.tts.volume" title="Volume">
+    </div>
 
     <div class="card" style="padding:12px 14px;">
       <h2 id="expl-nom" style="color:#e94560; font-size:0.85rem; margin-bottom:8px;"></h2>
