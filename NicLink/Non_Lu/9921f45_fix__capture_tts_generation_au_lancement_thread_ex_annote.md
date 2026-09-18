9921f45

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9921f45
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 12:09:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: capture tts_generation au lancement thread explorer, pas après LLM (issue #174, suite #172)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8b9966d..8722a3d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/server.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 15 (6 ligne(s)) dans l'ancienne version → ligne 15 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -15,6 +15,7 @@ import sys
 import threading
 from nicsoft.config import APP_DIR, DATA_DIR, ENGINES_DIR, GAMES_DIR, LOGS_DIR
 from nicsoft.modes.opening_explorer.tts_engine import stop_speaking
+from nicsoft.modes.opening_explorer import tts_engine
 from flask import Flask, render_template, send_file, abort, request
 from flask_socketio import SocketIO, emit
 
# ── Zone modifiée : ligne 65 (11 ligne(s)) dans l'ancienne version → ligne 66 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -65,11 +66,6 @@ _stockfish_available_cache: bool | None = None
 _maia_available_cache: bool | None = None
 _rodent_available_cache: bool | None = None
 
-# Explorer : compteur incrémenté à chaque navigation, pour que les threads
-# d'explication LLM obsolètes (clics rapides) abandonnent sans parler.
-_explanation_request_id: int = 0
-
-
 def _get_stockfish_available() -> bool:
     """Retourne (et mémorise) si Stockfish est présent."""
     global _stockfish_available_cache
# ── Zone modifiée : ligne 640 (11 ligne(s)) dans l'ancienne version → ligne 636 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -640,11 +636,13 @@ def on_explorer_get_list(_data):
     emit("explorer_list", explorer_get_list())
 
 
-def _emit_explorer_explanation(sid, state, language, request_id=0):
+def _emit_explorer_explanation(sid, state, language, my_gen=0):
     """Génère l'explication LLM du coup en arrière-plan et l'émet au client concerné.
 
-    request_id : abandonne silencieusement si une navigation plus récente a eu lieu
-    entre-temps (clics rapides Suivant/Précédent → threads LLM concurrents).
+    my_gen : génération TTS (tts_engine._tts_generation) capturée juste après le
+    stop_speaking() qui a lancé ce thread. Si elle a changé entre-temps (navigation
+    plus récente → clics rapides Suivant/Précédent), on abandonne silencieusement,
+    y compris avant l'appel LLM pour ne pas gaspiller un appel devenu obsolète.
     """
     from nicsoft.modes.opening_explorer.llm_explainer import get_explanation
     from nicsoft.core.config_manager import load_config
# ── Zone modifiée : ligne 652 (6 ligne(s)) dans l'ancienne version → ligne 650 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -652,6 +650,8 @@ def _emit_explorer_explanation(sid, state, language, request_id=0):
 
     if not state or state.get("error") or not state.get("move_san"):
         return
+    if tts_engine._tts_generation != my_gen:
+        return  # navigation plus récente, on abandonne avant l'appel LLM
     cfg = load_config()
     expl, arrows = get_explanation(
         line_id=state.get("line_id", ""),
# ── Zone modifiée : ligne 665 (11 ligne(s)) dans l'ancienne version → ligne 665 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -665,11 +665,11 @@ def _emit_explorer_explanation(sid, state, language, request_id=0):
         config=cfg,
     )
     if expl:
-        if request_id != _explanation_request_id:
+        if tts_engine._tts_generation != my_gen:
             return  # navigation plus récente, on abandonne
         socketio.emit("explorer_explanation", {"text": expl, "arrows": [list(a) for a in arrows]}, to=sid)
         if cfg.get("tts_enabled", False):
-            if request_id != _explanation_request_id:
+            if tts_engine._tts_generation != my_gen:
                 return
             socketio.emit("explorer_tts_start", {}, to=sid)
             def on_playing():
# ── Zone modifiée : ligne 703 (12 ligne(s)) dans l'ancienne version → ligne 703 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -703,12 +703,10 @@ def _emit_explorer_chat_response(sid, question, state, language):
 @socketio.on("explorer_load")
 def on_explorer_load(data):
     """Charge une ouverture (catalogue ou ligne perso) — connexion échiquier en arrière-plan."""
-    global _explanation_request_id
-    stop_speaking()
+    stop_speaking()  # invalide (tts_engine._tts_generation) toute explication LLM encore en vol
     source_type   = data.get("source_type", "polyglot")
     opening_id    = data.get("opening_id", "")
     variant_index = data.get("variant_index")
-    _explanation_request_id += 1  # invalide toute explication LLM encore en vol
 
     def run():
         from nicsoft.core.game_manager import explorer_load
# ── Zone modifiée : ligne 721 (36 ligne(s)) dans l'ancienne version → ligne 719 (32 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -721,36 +719,32 @@ def on_explorer_load(data):
 
 @socketio.on("explorer_next")
 def on_explorer_next(data):
-    global _explanation_request_id
     stop_speaking()
+    my_gen = tts_engine._tts_generation
     from nicsoft.core.game_manager import explorer_next
     state = explorer_next()
     emit("explorer_state", state)
     language = (data or {}).get("language", "fr")
     sid = request.sid
-    _explanation_request_id += 1
-    my_id = _explanation_request_id
-    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language, my_id), daemon=True).start()
+    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language, my_gen), daemon=True).start()
 
 
 @socketio.on("explorer_prev")
 def on_explorer_prev(data):
-    global _explanation_request_id
     stop_speaking()
+    my_gen = tts_engine._tts_generation
     from nicsoft.core.game_manager import explorer_prev
     state = explorer_prev()
     emit("explorer_state", state)
     language = (data or {}).get("language", "fr")
     sid = request.sid
-    _explanation_request_id += 1
-    my_id = _explanation_request_id
-    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language, my_id), daemon=True).start()
+    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language, my_gen), daemon=True).start()
 
 
 @socketio.on("explorer_choose_move")
 def on_explorer_choose_move(data):
-    global _explanation_request_id
     stop_speaking()
+    my_gen = tts_engine._tts_generation
     uci = (data or {}).get("uci", "")
     if not uci:
         return
# ── Zone modifiée : ligne 759 (11 ligne(s)) dans l'ancienne version → ligne 753 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -759,11 +753,9 @@ def on_explorer_choose_move(data):
     emit("explorer_state", state)
     language = (data or {}).get("language", "fr")
     sid = request.sid
-    _explanation_request_id += 1
-    my_id = _explanation_request_id
     threading.Thread(
         target=_emit_explorer_explanation,
-        args=(sid, state, language, my_id),
+        args=(sid, state, language, my_gen),
         daemon=True
     ).start()
 
