cf69349

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit cf69349
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 10:54:19 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: réactive Suivant/Précédent dès le début de la lecture mpg123 explorer (issue #172, suite #171)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2a1f64d..c0146f7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 103 (7 ligne(s)) dans l'ancienne version → ligne 103 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -103,7 +103,7 @@ def check_internet() -> bool:
         return False
 
 
-def _speak_edge(text: str, rate: int, language: str) -> bool:
+def _speak_edge(text: str, rate: int, language: str, on_playback_start=None) -> bool:
     """Essaie de parler via edge-tts. Retourne True si succès, False sinon."""
     global _tts_generation
     try:
# ── Zone modifiée : ligne 126 (6 ligne(s)) dans l'ancienne version → ligne 126 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -126,6 +126,8 @@ def _speak_edge(text: str, rate: int, language: str) -> bool:
                     return  # stop_speaking() appelé pendant le download
                 proc = subprocess.Popen(["mpg123", "-q", tmp])
                 _current_tts_process = proc
+                if on_playback_start:
+                    on_playback_start()
                 proc.wait()
                 _current_tts_process = None
             finally:
# ── Zone modifiée : ligne 164 (7 ligne(s)) dans l'ancienne version → ligne 166 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -164,7 +166,7 @@ def stop_speaking() -> None:
         _current_tts_process = None
 
 
-def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr") -> bool:
+def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr", on_playback_start=None) -> bool:
     """Prononce `text` à voix haute côté serveur si `enabled` et si internet
     est disponible (edge-tts, voix neuronale). Bloquant — à appeler depuis un
     thread daemon, jamais depuis le thread principal.
# ── Zone modifiée : ligne 179 (4 ligne(s)) dans l'ancienne version → ligne 181 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -179,4 +181,4 @@ def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr
         return False
     if not check_internet():
         return False
-    return _speak_edge(text, rate, language)
+    return _speak_edge(text, rate, language, on_playback_start=on_playback_start)
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index 8d89454..7320598 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 660 (11 ligne(s)) dans l'ancienne version → ligne 660 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -660,11 +660,12 @@ def _emit_explorer_explanation(sid, state, language):
         socketio.emit("explorer_explanation", {"text": expl, "arrows": [list(a) for a in arrows]}, to=sid)
         if cfg.get("tts_enabled", False):
             socketio.emit("explorer_tts_start", {}, to=sid)
-        tts_ok = speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
-        if cfg.get("tts_enabled", False):
+            def on_playing():
+                socketio.emit("explorer_tts_playing", {}, to=sid)
+            tts_ok = speak(expl, rate=cfg.get("tts_rate", 150), enabled=True, language=language, on_playback_start=on_playing)
             socketio.emit("explorer_tts_end", {}, to=sid)
-        if cfg.get("tts_enabled") and not tts_ok:
-            socketio.emit("explorer_tts_fallback", {"text": expl}, to=sid)
+            if not tts_ok:
+                socketio.emit("explorer_tts_fallback", {"text": expl}, to=sid)
 
 
 def _emit_explorer_chat_response(sid, question, state, language):
# ── Zone modifiée : ligne 679 (11 ligne(s)) dans l'ancienne version → ligne 680 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -679,11 +680,12 @@ def _emit_explorer_chat_response(sid, question, state, language):
         socketio.emit("explorer_chat_response", {"text": response, "arrows": [list(a) for a in arrows]}, to=sid)
         if cfg.get("tts_enabled", False):
             socketio.emit("explorer_tts_start", {}, to=sid)
-        tts_ok = speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
-        if cfg.get("tts_enabled", False):
+            def on_playing():
+                socketio.emit("explorer_tts_playing", {}, to=sid)
+            tts_ok = speak(response, rate=cfg.get("tts_rate", 150), enabled=True, language=language, on_playback_start=on_playing)
             socketio.emit("explorer_tts_end", {}, to=sid)
-        if cfg.get("tts_enabled") and not tts_ok:
-            socketio.emit("explorer_tts_fallback", {"text": response}, to=sid)
+            if not tts_ok:
+                socketio.emit("explorer_tts_fallback", {"text": response}, to=sid)
 
 
 @socketio.on("explorer_load")
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index dba904a..26f2456 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6306 (8 ligne(s)) dans l'ancienne version → ligne 6306 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6306,8 +6306,9 @@ function explSetNavDisabled(disabled) {
   if (next) { next.disabled = disabled; next.style.opacity = disabled ? "0.4" : "1"; }
 }
 
-socket.on("explorer_tts_start", () => { explSetNavDisabled(true); });
-socket.on("explorer_tts_end",   () => { explSetNavDisabled(false); });
+socket.on("explorer_tts_start",   () => { explSetNavDisabled(true); });
+socket.on("explorer_tts_playing", () => { explSetNavDisabled(false); });
+socket.on("explorer_tts_end",     () => { explSetNavDisabled(false); });
 
 function explRenderMovesTable(data) {
   const wrap = document.getElementById("explorer-moves-table");
