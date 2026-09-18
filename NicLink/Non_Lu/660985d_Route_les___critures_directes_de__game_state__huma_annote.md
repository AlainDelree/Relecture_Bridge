660985d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 660985d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 10:58:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Route les écritures directes de _game_state (human.py, game_manager.py) à travers le verrou de server.py (issue #214)
    
    Ajoute set_history()/get_history() dans server.py, protégées par
    _game_state_lock, pour remplacer les mutations directes de
    _game_state["history"]/["history_fen"] et les lectures multi-clés
    correspondantes dans human.py, game_manager.py et pedagogique.py.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3542629..92cf1d7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 318 (8 ligne(s)) dans l'ancienne version → ligne 318 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -318,8 +318,7 @@ def _run_humain(white_name, black_name, game_type, _error=None, virtual=False):
         if not virtual:
             _wait_initial_position_web(nl_inst)
         _nl_inst_ref = nl_inst
-        web_server._game_state["history"]     = []
-        web_server._game_state["history_fen"] = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"]
+        web_server.set_history([], ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"])
 
         game = GameWeb(nl_inst, white_name=white_name, black_name=black_name,
                        default_game_type=game_type)
# (diff du fichier suivant)
diff --git a/nicsoft/modes/humain/human.py b/nicsoft/modes/humain/human.py
# (index — ignorable)
index 036c8f4..ce3f6ea 100755
# (avant — fichier suivant)
--- a/nicsoft/modes/humain/human.py
# (après — fichier suivant)
+++ b/nicsoft/modes/humain/human.py
# ── Zone modifiée : ligne 27 (7 ligne(s)) dans l'ancienne version → ligne 27 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -27,7 +27,7 @@ from nicsoft.engine.players import (
     normalize_player_name,
 )
 from nicsoft.engine.board_utils import wait_for_initial_position, san_ep
-from nicsoft.web.server import send_event, get_action, set_app_state, _game_state
+from nicsoft.web.server import send_event, get_action, set_app_state, set_history, get_history
 from nicsoft.niclink import NicLinkManager
 
 logger = logging.getLogger("NL play Human")
# ── Zone modifiée : ligne 889 (9 ligne(s)) dans l'ancienne version → ligne 889 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -889,9 +889,10 @@ class GameWeb(threading.Thread):
     def _handle_pause(self):
         """Gère la pause interactive. Retourne changer_couleur (bool)."""
         self.nl_inst.turn_off_all_leds()
+        history, history_fen = get_history()
         set_app_state("paused", {
-            "history_fen":   _game_state.get("history_fen", []),
-            "history_moves": _game_state.get("history", []),
+            "history_fen":   history_fen,
+            "history_moves": history,
         })
 
         bm = self._get_best_move_quick()
# ── Zone modifiée : ligne 1004 (8 ligne(s)) dans l'ancienne version → ligne 1005 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1004,8 +1005,7 @@ class GameWeb(threading.Thread):
 
         set_app_state("playing")
         # Resynchroniser _game_state avec move_stack (source de vérité)
-        _game_state["history"]     = list(resume_moves)
-        _game_state["history_fen"] = list(resume_fens)
+        set_history(list(resume_moves), list(resume_fens))
         set_app_state("playing")
         send_event("resume", {"history_fen": resume_fens, "history_moves": resume_moves})
         return changer_couleur
# (diff du fichier suivant)
diff --git a/nicsoft/modes/pedagogique/pedagogique.py b/nicsoft/modes/pedagogique/pedagogique.py
# (index — ignorable)
index e098558..32fe09c 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/pedagogique/pedagogique.py
# (après — fichier suivant)
+++ b/nicsoft/modes/pedagogique/pedagogique.py
# ── Zone modifiée : ligne 713 (7 ligne(s)) dans l'ancienne version → ligne 713 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -713,7 +713,7 @@ class Game(threading.Thread):
         Gère la pause interactive — manuelle ou automatique (après blunder/erreur).
         Retourne (changer_couleur: bool, reprendre: bool).
         """
-        from nicsoft.web.server import set_app_state, _game_state
+        from nicsoft.web.server import set_app_state, get_history
 
         auto = qualite is not None
         if DEBUG_MODE: print(f"\n  [PAUSE] Partie suspendue {'(auto: ' + qualite + ')' if auto else '(manuelle)'}.")
# ── Zone modifiée : ligne 721 (9 ligne(s)) dans l'ancienne version → ligne 721 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -721,9 +721,10 @@ class Game(threading.Thread):
 
         bm = best_move or getattr(self, "_last_best_move", None)
 
+        history, history_fen = get_history()
         set_app_state("paused", {
-            "history_fen":   _game_state.get("history_fen", []),
-            "history_moves": _game_state.get("history", []),
+            "history_fen":   history_fen,
+            "history_moves": history,
         })
         send_event("pause", {
             "playing_white":   self.playing_white,
# ── Zone modifiée : ligne 857 (9 ligne(s)) dans l'ancienne version → ligne 858 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -857,9 +858,10 @@ class Game(threading.Thread):
 
         # ── Utiliser _game_state["history"] comme source de vérité ──
         # (move_stack peut être vide si game_board reconstruit depuis FEN)
-        from nicsoft.web.server import _game_state
-        resume_moves = list(_game_state.get("history", []))
-        resume_fens  = list(_game_state.get("history_fen", ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"]))
+        from nicsoft.web.server import get_history
+        _history, _history_fen = get_history()
+        resume_moves = list(_history)
+        resume_fens  = list(_history_fen) if _history_fen else ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"]
 
         if changer_couleur:
             new_human_color = "black" if self.playing_white else "white"
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index 1e6b7a1..3121799 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 87 (9 ligne(s)) dans l'ancienne version → ligne 87 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -87,9 +87,11 @@ _game_state: dict = {}
 # on_connect() lit plusieurs clés (fen/history/move/turn/feedback) qui
 # doivent rester cohérentes entre elles à un instant donné. Ce verrou
 # n'englobe jamais un emit()/put() — uniquement la mutation du dict.
-# Note : _game_state est aussi importé et muté directement (par référence,
-# hors verrou) par human.py, pedagogique.py et game_manager.py — hors
-# périmètre de cette issue, qui porte sur server.py.
+# Note : _game_state est aussi importé et lu directement (par référence,
+# hors verrou) par human.py et pedagogique.py pour des lectures multi-clés
+# (history + history_fen) — voir get_history() ci-dessous, qui protège ces
+# accès sous _game_state_lock. Les écritures directes (human.py,
+# game_manager.py) passent par set_history().
 _game_state_lock = threading.RLock()
 
 # État de l application : menu / config / playing / game_over
# ── Zone modifiée : ligne 1099 (6 ligne(s)) dans l'ancienne version → ligne 1101 (31 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1099,6 +1101,31 @@ def send_event(event_type: str, data: dict) -> None:
     event_queue.put({"type": event_type, "data": data})
 
 
+def set_history(history: list, history_fen: list) -> None:
+    """
+    API publique — remplace atomiquement _game_state["history"] et
+    _game_state["history_fen"]. À utiliser par tout module hors server.py
+    (human.py, game_manager.py) au lieu de muter _game_state directement,
+    pour ne pas s'entrelacer avec les séquences composées de send_event()
+    ou la lecture multi-clés de on_connect().
+    """
+    with _game_state_lock:
+        _game_state["history"] = history
+        _game_state["history_fen"] = history_fen
+
+
+def get_history() -> tuple:
+    """
+    API publique — lit atomiquement (history, history_fen) depuis
+    _game_state. À utiliser par tout module hors server.py au lieu de
+    lire _game_state["history"]/["history_fen"] séparément, pour éviter
+    d'observer les deux clés à des instants différents pendant qu'un
+    thread SocketIO les mute via send_event().
+    """
+    with _game_state_lock:
+        return _game_state.get("history", []), _game_state.get("history_fen", [])
+
+
 def get_action(timeout: float = 0.0):
     """
     API publique — appelée par le module pédagogique pour récupérer
