f2504a0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f2504a0
Merge: f6ef420 b25e292
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 18:59:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    merge: Opening Explorer flèches SVG (#148) + résolution conflit server.py

diff --cc nicsoft/web/server.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9493cf1,458c55b..3af0fa8
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/server.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/server.py
@@@ -656,8 -656,8 +656,8 @@@ def _emit_explorer_explanation(sid, sta
          config=cfg,
      )
      if expl:
-         socketio.emit("explorer_explanation", {"text": expl}, to=sid)
+         socketio.emit("explorer_explanation", {"text": expl, "arrows": [list(a) for a in arrows]}, to=sid)
 -        speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False))
 +        speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
  
  
  def _emit_explorer_chat_response(sid, question, state, language):
@@@ -667,10 -667,10 +667,10 @@@
      from nicsoft.modes.opening_explorer.tts_engine import speak
  
      cfg = load_config()
-     response = get_chat_response(question, state, language, cfg)
+     response, arrows = get_chat_response(question, state, language, cfg)
      if response:
-         socketio.emit("explorer_chat_response", {"text": response}, to=sid)
+         socketio.emit("explorer_chat_response", {"text": response, "arrows": [list(a) for a in arrows]}, to=sid)
 -        speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False))
 +        speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
  
  
  @socketio.on("explorer_load")
