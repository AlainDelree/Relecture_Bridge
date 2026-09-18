a1f9bbc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a1f9bbc
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 11:06:38 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: annule explications LLM obsolètes sur navigation rapide explorer (issue #173, suite #172)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7320598..8b9966d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/server.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 65 (6 ligne(s)) dans l'ancienne version → ligne 65 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -65,6 +65,10 @@ _stockfish_available_cache: bool | None = None
 _maia_available_cache: bool | None = None
 _rodent_available_cache: bool | None = None
 
+# Explorer : compteur incrémenté à chaque navigation, pour que les threads
+# d'explication LLM obsolètes (clics rapides) abandonnent sans parler.
+_explanation_request_id: int = 0
+
 
 def _get_stockfish_available() -> bool:
     """Retourne (et mémorise) si Stockfish est présent."""
# ── Zone modifiée : ligne 636 (8 ligne(s)) dans l'ancienne version → ligne 640 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -636,8 +640,12 @@ def on_explorer_get_list(_data):
     emit("explorer_list", explorer_get_list())
 
 
-def _emit_explorer_explanation(sid, state, language):
-    """Génère l'explication LLM du coup en arrière-plan et l'émet au client concerné."""
+def _emit_explorer_explanation(sid, state, language, request_id=0):
+    """Génère l'explication LLM du coup en arrière-plan et l'émet au client concerné.
+
+    request_id : abandonne silencieusement si une navigation plus récente a eu lieu
+    entre-temps (clics rapides Suivant/Précédent → threads LLM concurrents).
+    """
     from nicsoft.modes.opening_explorer.llm_explainer import get_explanation
     from nicsoft.core.config_manager import load_config
     from nicsoft.modes.opening_explorer.tts_engine import speak
# ── Zone modifiée : ligne 657 (8 ligne(s)) dans l'ancienne version → ligne 665 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -657,8 +665,12 @@ def _emit_explorer_explanation(sid, state, language):
         config=cfg,
     )
     if expl:
+        if request_id != _explanation_request_id:
+            return  # navigation plus récente, on abandonne
         socketio.emit("explorer_explanation", {"text": expl, "arrows": [list(a) for a in arrows]}, to=sid)
         if cfg.get("tts_enabled", False):
+            if request_id != _explanation_request_id:
+                return
             socketio.emit("explorer_tts_start", {}, to=sid)
             def on_playing():
                 socketio.emit("explorer_tts_playing", {}, to=sid)
# ── Zone modifiée : ligne 691 (10 ligne(s)) dans l'ancienne version → ligne 703 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -691,10 +703,12 @@ def _emit_explorer_chat_response(sid, question, state, language):
 @socketio.on("explorer_load")
 def on_explorer_load(data):
     """Charge une ouverture (catalogue ou ligne perso) — connexion échiquier en arrière-plan."""
+    global _explanation_request_id
     stop_speaking()
     source_type   = data.get("source_type", "polyglot")
     opening_id    = data.get("opening_id", "")
     variant_index = data.get("variant_index")
+    _explanation_request_id += 1  # invalide toute explication LLM encore en vol
 
     def run():
         from nicsoft.core.game_manager import explorer_load
# ── Zone modifiée : ligne 707 (28 ligne(s)) dans l'ancienne version → ligne 721 (35 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -707,28 +721,35 @@ def on_explorer_load(data):
 
 @socketio.on("explorer_next")
 def on_explorer_next(data):
+    global _explanation_request_id
     stop_speaking()
     from nicsoft.core.game_manager import explorer_next
     state = explorer_next()
     emit("explorer_state", state)
     language = (data or {}).get("language", "fr")
     sid = request.sid
-    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language), daemon=True).start()
+    _explanation_request_id += 1
+    my_id = _explanation_request_id
+    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language, my_id), daemon=True).start()
 
 
 @socketio.on("explorer_prev")
 def on_explorer_prev(data):
+    global _explanation_request_id
     stop_speaking()
     from nicsoft.core.game_manager import explorer_prev
     state = explorer_prev()
     emit("explorer_state", state)
     language = (data or {}).get("language", "fr")
     sid = request.sid
-    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language), daemon=True).start()
+    _explanation_request_id += 1
+    my_id = _explanation_request_id
+    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language, my_id), daemon=True).start()
 
 
 @socketio.on("explorer_choose_move")
 def on_explorer_choose_move(data):
+    global _explanation_request_id
     stop_speaking()
     uci = (data or {}).get("uci", "")
     if not uci:
# ── Zone modifiée : ligne 738 (9 ligne(s)) dans l'ancienne version → ligne 759 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -738,9 +759,11 @@ def on_explorer_choose_move(data):
     emit("explorer_state", state)
     language = (data or {}).get("language", "fr")
     sid = request.sid
+    _explanation_request_id += 1
+    my_id = _explanation_request_id
     threading.Thread(
         target=_emit_explorer_explanation,
-        args=(sid, state, language),
+        args=(sid, state, language, my_id),
         daemon=True
     ).start()
 
