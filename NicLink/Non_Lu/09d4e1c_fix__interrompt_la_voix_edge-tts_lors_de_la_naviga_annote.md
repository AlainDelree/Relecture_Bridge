09d4e1c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 09d4e1c
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 19:28:35 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: interrompt la voix edge-tts lors de la navigation et du toggle 🔇 (issue #161, suite #160)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1e2a79b..6052b6c 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 19 (6 ligne(s)) dans l'ancienne version → ligne 19 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -19,6 +19,8 @@ import tempfile
 
 logger = logging.getLogger("niclink.opening_explorer.tts")
 
+_current_tts_process: "subprocess.Popen | None" = None
+
 
 VOICE_MAP_EDGE = {
     "fr": "fr-FR-DeniseNeural",
# ── Zone modifiée : ligne 115 (7 ligne(s)) dans l'ancienne version → ligne 117 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -115,7 +117,11 @@ def _speak_edge(text: str, rate: int, language: str) -> bool:
             try:
                 communicate = edge_tts.Communicate(text, voice, rate=rate_pct)
                 await communicate.save(tmp)
-                subprocess.run(["mpg123", "-q", tmp], check=False, timeout=60)
+                global _current_tts_process
+                proc = subprocess.Popen(["mpg123", "-q", tmp])
+                _current_tts_process = proc
+                proc.wait()
+                _current_tts_process = None
             finally:
                 try:
                     os.unlink(tmp)
# ── Zone modifiée : ligne 142 (6 ligne(s)) dans l'ancienne version → ligne 148 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -142,6 +148,15 @@ def _speak_espeak(text: str, rate: int, language: str) -> None:
         logger.warning(f"[TTS] espeak-ng échoué : {e}")
 
 
+def stop_speaking() -> None:
+    """Interrompt immédiatement la lecture mpg123 en cours, si active."""
+    global _current_tts_process
+    proc = _current_tts_process
+    if proc is not None and proc.poll() is None:
+        proc.terminate()
+        _current_tts_process = None
+
+
 def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr") -> bool:
     """Prononce `text` à voix haute côté serveur si `enabled` et si internet
     est disponible (edge-tts, voix neuronale). Bloquant — à appeler depuis un
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index 0ff52cf..76aee34 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 14 (6 ligne(s)) dans l'ancienne version → ligne 14 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -14,6 +14,7 @@ import queue
 import sys
 import threading
 from nicsoft.config import APP_DIR, DATA_DIR, ENGINES_DIR, GAMES_DIR, LOGS_DIR
+from nicsoft.modes.opening_explorer.tts_engine import stop_speaking
 from flask import Flask, render_template, send_file, abort, request
 from flask_socketio import SocketIO, emit
 
# ── Zone modifiée : ligne 680 (6 ligne(s)) dans l'ancienne version → ligne 681 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -680,6 +681,7 @@ def _emit_explorer_chat_response(sid, question, state, language):
 @socketio.on("explorer_load")
 def on_explorer_load(data):
     """Charge une ouverture (catalogue ou ligne perso) — connexion échiquier en arrière-plan."""
+    stop_speaking()
     source_type   = data.get("source_type", "polyglot")
     opening_id    = data.get("opening_id", "")
     variant_index = data.get("variant_index")
# ── Zone modifiée : ligne 695 (6 ligne(s)) dans l'ancienne version → ligne 697 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -695,6 +697,7 @@ def on_explorer_load(data):
 
 @socketio.on("explorer_next")
 def on_explorer_next(data):
+    stop_speaking()
     from nicsoft.core.game_manager import explorer_next
     state = explorer_next()
     emit("explorer_state", state)
# ── Zone modifiée : ligne 705 (6 ligne(s)) dans l'ancienne version → ligne 708 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -705,6 +708,7 @@ def on_explorer_next(data):
 
 @socketio.on("explorer_prev")
 def on_explorer_prev(data):
+    stop_speaking()
     from nicsoft.core.game_manager import explorer_prev
     state = explorer_prev()
     emit("explorer_state", state)
# ── Zone modifiée : ligne 715 (6 ligne(s)) dans l'ancienne version → ligne 719 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -715,6 +719,7 @@ def on_explorer_prev(data):
 
 @socketio.on("explorer_choose_move")
 def on_explorer_choose_move(data):
+    stop_speaking()
     uci = (data or {}).get("uci", "")
     if not uci:
         return
# ── Zone modifiée : ligne 757 (6 ligne(s)) dans l'ancienne version → ligne 762 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -757,6 +762,12 @@ def on_explorer_back(_data):
     explorer_cleanup()
 
 
+@socketio.on("explorer_tts_stop")
+def on_explorer_tts_stop(_data):
+    """Arrête immédiatement la lecture TTS en cours (toggle 🔇 pendant lecture)."""
+    stop_speaking()
+
+
 # ── Thread de dispatch des événements ────────────────────────────────────────
 
 def _dispatch_loop():
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 67ec5b5..c15c34a 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6079 (6 ligne(s)) dans l'ancienne version → ligne 6079 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6079,6 +6079,7 @@ function explToggleTts() {
   _explTtsEnabled = !_explTtsEnabled;
   explUpdateTtsToggle();
   socket.emit("config_save", { tts_enabled: _explTtsEnabled });
+  if (!_explTtsEnabled) socket.emit("explorer_tts_stop", {});
 }
 
 socket.on("app_state", (data) => {
