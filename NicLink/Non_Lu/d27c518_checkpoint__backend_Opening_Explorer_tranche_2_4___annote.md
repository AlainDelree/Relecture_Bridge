d27c518

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d27c518
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 14:53:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    checkpoint: backend Opening Explorer tranche 2/4 (session/sources/handlers) avant frontend

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 93f5bc7..ed7c2b4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 1053 (3 ligne(s)) dans l'ancienne version → ligne 1053 (108 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1053,3 +1053,108 @@ def _run_labo_libre(player_name, playing_white, start_fen, pause, analyse_active
             except Exception: pass
         if web_server._app_state not in ("menu",):
             web_server._app_state = "menu"
+
+
+# ── Opening Explorer ─────────────────────────────────────────────────────────
+# Session unique active à la fois — même pattern que _nl_inst_ref pour les
+# autres modes. Le plateau (physique ou virtuel) est ouvert à explorer_load()
+# et refermé à explorer_cleanup() (retour sélecteur ou retour menu).
+_explorer_nl_inst = None
+_explorer_session  = None
+
+
+def explorer_get_list() -> dict:
+    """Construit dynamiquement la liste catalogue + mes_lignes pour le sélecteur."""
+    from nicsoft.modes.exercices._catalogue import parse_ouvertures
+    from nicsoft.modes.exercices.exercices import get_mes_lignes
+
+    catalogue = [
+        {"id": o.get("id", ""), "nom": o.get("nom", ""), "eco": o.get("eco", "")}
+        for o in parse_ouvertures()
+    ]
+
+    groupes: dict = {}
+    for l in get_mes_lignes():
+        groupes.setdefault(l.get("nom", ""), []).append({
+            "id":           l.get("id", ""),
+            "nom":          l.get("nom", ""),
+            "camp_suggere": l.get("camp_suggere", "white"),
+        })
+    mes_lignes = [{"groupe": nom, "variantes": variantes} for nom, variantes in groupes.items()]
+
+    return {"catalogue": catalogue, "mes_lignes": mes_lignes}
+
+
+def explorer_load(source_type: str, opening_id: str, variant_index=None) -> dict:
+    """Charge une source (catalogue Polyglot ou ligne perso) dans une nouvelle ExplorerSession."""
+    global _explorer_nl_inst, _explorer_session
+    from nicsoft.modes.opening_explorer.explorer_session import ExplorerSession
+    from nicsoft.modes.opening_explorer.sources import PolyglotSource, PGNLineSource
+    from nicsoft.modes.exercices._catalogue import parse_ouvertures, BOOKS_DIR
+    from nicsoft.modes.exercices.exercices import get_mes_lignes, BOOK_DEFAULT
+
+    explorer_cleanup()  # referme une éventuelle session/connexion précédente
+
+    if source_type == "pgn":
+        entry = next((l for l in get_mes_lignes() if l.get("id") == opening_id), None)
+        if entry is None:
+            return {"error": "Ligne introuvable."}
+        source = PGNLineSource(entry)
+    else:
+        ouverture = next((o for o in parse_ouvertures() if o.get("id") == opening_id), None)
+        if ouverture is None:
+            return {"error": "Ouverture introuvable."}
+        book_name = ouverture.get("book", "")
+        book_candidate = BOOKS_DIR / book_name if book_name else None
+        book_path = str(book_candidate if book_candidate and book_candidate.exists() else BOOK_DEFAULT)
+        source = PolyglotSource(ouverture, book_path)
+
+    try:
+        nl_inst = create_board(virtual=_virtual_mode, logger_name="NicLink_explorer")
+    except Exception as e:
+        logger.error(f"[EXPLORER] Échiquier non détecté : {e}")
+        send_event("board_error", {"message": "Échiquier non détecté — vérifiez l'USB et allumez le plateau."})
+        return {"error": "Échiquier non détecté."}
+
+    if _virtual_mode:
+        set_virtual_board(nl_inst)
+    _explorer_nl_inst = nl_inst
+
+    session = ExplorerSession(nl_inst)
+    state = session.load(source)
+    _explorer_session = session
+
+    state["end_of_line"] = not session.has_more()
+    state["at_start"]    = session.is_at_start()
+    return state
+
+
+def explorer_next() -> dict:
+    if _explorer_session is None:
+        return {"error": "Aucune session Opening Explorer active."}
+    state = _explorer_session.next_move()
+    state["end_of_line"] = not _explorer_session.has_more()
+    state["at_start"]    = _explorer_session.is_at_start()
+    return state
+
+
+def explorer_prev() -> dict:
+    if _explorer_session is None:
+        return {"error": "Aucune session Opening Explorer active."}
+    state = _explorer_session.prev_move()
+    state["end_of_line"] = not _explorer_session.has_more()
+    state["at_start"]    = _explorer_session.is_at_start()
+    return state
+
+
+def explorer_cleanup() -> None:
+    """Referme la connexion échiquier de l'Opening Explorer (retour sélecteur/menu)."""
+    global _explorer_nl_inst, _explorer_session
+    if _explorer_nl_inst is not None:
+        try: _explorer_nl_inst.turn_off_all_leds()
+        except Exception: pass
+        try: _explorer_nl_inst.disconnect()
+        except Exception: pass
+    set_virtual_board(None)
+    _explorer_nl_inst = None
+    _explorer_session  = None
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/__init__.py b/nicsoft/modes/opening_explorer/__init__.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..342c347
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/__init__.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,6 @@
+"""
+nicsoft/modes/opening_explorer/ — NicLink
+Module Opening Explorer : navigation Prev/Next dans une ouverture (livre
+Polyglot ou ligne PGN personnelle), sans interaction humaine — les deux
+camps jouent la ligne, l'utilisateur navigue coup par coup.
+"""
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/explorer_session.py b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..f24fe5b
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (115 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,115 @@
+"""
+nicsoft/modes/opening_explorer/explorer_session.py — NicLink
+Session de navigation Opening Explorer : position courante, historique de
+coups (pour Prev), source active. Aucune interaction humaine — next_move()
+et prev_move() sont déclenchés uniquement par les boutons Prev/Next de l'UI.
+"""
+
+import logging
+
+import chess
+
+from nicsoft.engine.board_utils import san_ep
+
+logger = logging.getLogger("niclink.opening_explorer")
+
+
+class ExplorerSession:
+    """
+    nl_inst : échiquier connecté (physique ou VirtualBoard) — peut être None.
+    source  : PolyglotSource ou PGNLineSource, assignée par load().
+    """
+
+    def __init__(self, nl_inst=None):
+        self.nl_inst = nl_inst
+        self.board   = chess.Board()
+        self.source  = None
+        # Coups joués après les init_moves — (chess.Move, san) — pile pour prev_move().
+        # Les init_moves eux-mêmes ne sont jamais dépilés (position plancher de la navigation).
+        self._history: list = []
+
+    def load(self, source) -> dict:
+        """Charge une source, rejoue ses init_moves (sans pause), émet l'état initial."""
+        self.source   = source
+        self.board    = chess.Board()
+        self._history = []
+        for uci in getattr(source, "init_moves", []):
+            try:
+                move = chess.Move.from_uci(uci)
+            except Exception:
+                continue
+            if move in self.board.legal_moves:
+                self.board.push(move)
+        self._update_board_display()
+        return self.get_state()
+
+    def next_move(self) -> dict:
+        """Applique le prochain coup de la source. No-op si la ligne est terminée."""
+        if not self.has_more():
+            return self.get_state()
+        move = self.source.get_main_move(self.board)
+        if move is None:
+            return self.get_state()
+        san = san_ep(self.board, move)
+        self.board.push(move)
+        self._history.append((move, san))
+        self._update_board_display()
+        return self.get_state()
+
+    def prev_move(self) -> dict:
+        """Dépile le dernier coup joué. No-op si déjà à la position post-init."""
+        if self.is_at_start():
+            return self.get_state()
+        self._history.pop()
+        self.board.pop()
+        self._update_board_display()
+        return self.get_state()
+
+    def is_at_start(self) -> bool:
+        return len(self._history) == 0
+
+    def has_more(self) -> bool:
+        return self.source is not None and self.source.has_more(self.board)
+
+    def get_state(self) -> dict:
+        if self._history:
+            last_move, last_san = self._history[-1]
+            last_move_uci = last_move.uci()
+            move_san      = last_san
+        else:
+            last_move_uci = None
+            move_san      = None
+        alternatives = []
+        if self.source is not None:
+            try:
+                alternatives = self.source.get_alternatives(self.board)
+            except Exception:
+                alternatives = []
+        return {
+            "fen":            self.board.fen(),
+            "last_move_uci":  last_move_uci,
+            "move_index":     len(self._history),
+            "move_san":       move_san,
+            "opening_name":   getattr(self.source, "nom", "") if self.source else "",
+            "camp":           getattr(self.source, "camp_suggere", "white") if self.source else "white",
+            "alternatives":   alternatives,
+        }
+
+    # ── Plateau Chessnut (physique ou virtuel) ─────────────────────────────────
+
+    def _update_board_display(self) -> None:
+        """Reproduit le mécanisme LED utilisé par pédagogique/exercices (set_move_leds)."""
+        if self.nl_inst is None:
+            return
+        try:
+            self.nl_inst.set_game_board(self.board.copy())
+        except Exception as e:
+            logger.debug(f"set_game_board échoué : {e}")
+        try:
+            if self._history:
+                last_move, _ = self._history[-1]
+                self.nl_inst.set_move_leds(last_move.uci())
+            else:
+                self.nl_inst.turn_off_all_leds()
+        except Exception as e:
+            logger.debug(f"mise à jour LEDs échouée : {e}")
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/sources.py b/nicsoft/modes/opening_explorer/sources.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..2442315
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/sources.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (74 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,74 @@
+"""
+nicsoft/modes/opening_explorer/sources.py — NicLink
+Sources de coups pour l'Opening Explorer : livre Polyglot (catalogue
+OUVERTURES) ou ligne PGN personnelle figée (mes_lignes.json).
+
+Interface commune (duck typing) utilisée par ExplorerSession :
+  get_main_move(board)    → chess.Move | None
+  get_alternatives(board) → list[{"uci": str, "weight": int}]
+  has_more(board)         → bool
+Attributs communs : nom, camp_suggere, init_moves.
+"""
+
+import chess
+import chess.polyglot
+
+
+class PolyglotSource:
+    """Coups théoriques tirés d'un livre Polyglot pour une entrée du catalogue OUVERTURES."""
+
+    def __init__(self, ouverture: dict, book_path: str):
+        self.ouverture    = ouverture
+        self.book_path    = book_path
+        self.nom          = ouverture.get("nom", "")
+        self.camp_suggere = ouverture.get("camp_suggere", "white")
+        self.init_moves   = ouverture.get("init", [])
+
+    def _entries(self, board: chess.Board) -> list:
+        try:
+            with chess.polyglot.open_reader(self.book_path) as reader:
+                entries = list(reader.find_all(board))
+        except Exception:
+            return []
+        entries.sort(key=lambda e: e.weight, reverse=True)
+        return entries
+
+    def get_main_move(self, board: chess.Board):
+        entries = self._entries(board)
+        return entries[0].move if entries else None
+
+    def get_alternatives(self, board: chess.Board) -> list:
+        return [{"uci": e.move.uci(), "weight": e.weight} for e in self._entries(board)]
+
+    def has_more(self, board: chess.Board) -> bool:
+        return self.get_main_move(board) is not None
+
+
+class PGNLineSource:
+    """Ligne fixe importée depuis mes_lignes.json — aucune alternative."""
+
+    def __init__(self, ligne: dict):
+        self.ligne        = ligne
+        self.nom          = ligne.get("nom", "")
+        self.camp_suggere = ligne.get("camp_suggere", "white")
+        self.init_moves   = ligne.get("init", [])
+        # "line" inclut déjà les init_moves en préfixe (format mes_lignes.json) —
+        # l'indexation se fait directement sur len(board.move_stack), comme
+        # dans ExerciceSession._get_book_moves (mode init_only).
+        self.line         = ligne.get("line", self.init_moves)
+
+    def get_main_move(self, board: chess.Board):
+        idx = len(board.move_stack)
+        if idx >= len(self.line):
+            return None
+        try:
+            move = chess.Move.from_uci(self.line[idx])
+        except Exception:
+            return None
+        return move if move in board.legal_moves else None
+
+    def get_alternatives(self, board: chess.Board) -> list:
+        return []
+
+    def has_more(self, board: chess.Board) -> bool:
+        return self.get_main_move(board) is not None
# (diff du fichier suivant)
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# (index — ignorable)
index 6440be1..7ac5df8 100644
# (avant — fichier suivant)
--- a/nicsoft/web/alchess.py
# (après — fichier suivant)
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 244 (6 ligne(s)) dans l'ancienne version → ligne 244 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -244,6 +244,8 @@ def main():
                 set_app_state("outils_exercices")
             elif atype == "mode" and action.get("value") == "parametres":
                 set_app_state("parametres")
+            elif atype == "mode" and action.get("value") == "opening_explorer":
+                set_app_state("opening_explorer")
             elif atype == "start_exercice":
                 gm.start_exercice(action)
             elif atype == "start_drill":
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index d16e975..7690a50 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 335 (6 ligne(s)) dans l'ancienne version → ligne 335 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -335,6 +335,9 @@ def on_action(data):
     if atype == "back_menu":
         prev_state = _app_state  # sauvegarder AVANT de changer
         set_app_state("menu")
+        if prev_state == "opening_explorer":
+            from nicsoft.core.game_manager import explorer_cleanup
+            explorer_cleanup()
         # Mettre dans action_queue seulement si un thread actif écoute
         if prev_state in ("playing", "connecting", "game_over", "paused", "labo",
                           "exercice_running", "retrans_playing"):
# ── Zone modifiée : ligne 623 (6 ligne(s)) dans l'ancienne version → ligne 626 (49 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -623,6 +626,49 @@ def on_config_save(data):
         emit("config_saved", {"ok": False, "error": str(e)})
 
 
+# ── Opening Explorer ──────────────────────────────────────────────────────────
+
+@socketio.on("explorer_get_list")
+def on_explorer_get_list(_data):
+    """Retourne catalogue Polyglot + mes_lignes groupées pour le sélecteur."""
+    from nicsoft.core.game_manager import explorer_get_list
+    emit("explorer_list", explorer_get_list())
+
+
+@socketio.on("explorer_load")
+def on_explorer_load(data):
+    """Charge une ouverture (catalogue ou ligne perso) — connexion échiquier en arrière-plan."""
+    source_type   = data.get("source_type", "polyglot")
+    opening_id    = data.get("opening_id", "")
+    variant_index = data.get("variant_index")
+
+    def run():
+        from nicsoft.core.game_manager import explorer_load
+        state = explorer_load(source_type, opening_id, variant_index)
+        socketio.emit("explorer_state", state)
+
+    threading.Thread(target=run, daemon=True).start()
+
+
+@socketio.on("explorer_next")
+def on_explorer_next(_data):
+    from nicsoft.core.game_manager import explorer_next
+    emit("explorer_state", explorer_next())
+
+
+@socketio.on("explorer_prev")
+def on_explorer_prev(_data):
+    from nicsoft.core.game_manager import explorer_prev
+    emit("explorer_state", explorer_prev())
+
+
+@socketio.on("explorer_back")
+def on_explorer_back(_data):
+    """Referme la connexion échiquier de l'Opening Explorer (retour sélecteur ou menu)."""
+    from nicsoft.core.game_manager import explorer_cleanup
+    explorer_cleanup()
+
+
 # ── Thread de dispatch des événements ────────────────────────────────────────
 
 def _dispatch_loop():
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index 1ae7b40..4994149 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 31 (6 ligne(s)) dans l'ancienne version → ligne 31 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,6 +31,7 @@
   "menu.btn.retranscrire":     "✏️ Transcribe",
   "menu.btn.outils":           "🛠️ Exercise Tools",
   "menu.btn.parametres":       "⚙ Settings",
+  "menu.btn.opening_explorer": "♟ Opening Explorer",
   "menu.btn.reconnect":        "🔌 Reconnect board",
   "menu.btn.connecter":        "⟳ Connect",
   "menu.btn.debloquer":        "⟳ Unlock buttons",
# ── Zone modifiée : ligne 53 (6 ligne(s)) dans l'ancienne version → ligne 54 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -53,6 +54,7 @@
   "menu.desc.retrans":         "Transcribe a game played on paper. Enter moves on the virtual board and export the PGN.",
   "menu.desc.outils":          "Import your PGN lines, convert SAN → UCI and manage the openings catalogue.",
   "menu.desc.parametres":      "Configure LLM access (API key) and text-to-speech (TTS).",
+  "menu.desc.opening_explorer": "Browse an opening move by move — theoretical catalogue or your own lines.",
   "menu.autoupdate.label":     "Automatic updates",
   "menu.autoupdate.warning":   "Automatic updates are disabled. You will not receive security fixes or new features.",
 
# ── Zone modifiée : ligne 260 (6 ligne(s)) dans l'ancienne version → ligne 262 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -260,6 +262,20 @@
   "parametres.toast.enregistre":      "Settings saved",
   "parametres.toast.erreur":          "Error while saving settings",
 
+  "opening_explorer.titre":                "♟ Opening Explorer",
+  "opening_explorer.catalogue.titre":      "📚 Catalogue",
+  "opening_explorer.catalogue.vide":       "No openings in the catalogue.",
+  "opening_explorer.mes_ouvertures.titre": "★ My openings",
+  "opening_explorer.mes_ouvertures.vide":  "No personal line imported. Use Exercise Tools to add one.",
+  "opening_explorer.btn.precedent":        "← Previous",
+  "opening_explorer.btn.suivant":          "Next →",
+  "opening_explorer.btn.autre":            "↩ Choose another opening",
+  "opening_explorer.h2.explication":       "EXPLANATION",
+  "opening_explorer.explication.a_venir":  "The move explanation will be available here soon.",
+  "opening_explorer.position_initiale":    "Starting position",
+  "opening_explorer.coup_n":               "Move {n} — {san}",
+  "opening_explorer.erreur_chargement":    "Unable to load this opening.",
+
   "outils.titre":              "🛠️ Exercise Tools",
   "outils.import_pgn.titre":   "📥 Import my PGN lines",
   "outils.import_pgn.desc":    "Select one or more .pgn files to import into your personal exercises (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index 08cfe23..d5dbfba 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 31 (6 ligne(s)) dans l'ancienne version → ligne 31 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,6 +31,7 @@
   "menu.btn.retranscrire":     "✏️ Retranscrire",
   "menu.btn.outils":           "🛠️ Outils Exercices",
   "menu.btn.parametres":       "⚙ Paramètres",
+  "menu.btn.opening_explorer": "♟ Opening Explorer",
   "menu.btn.reconnect":        "🔌 Reconnecter l'échiquier",
   "menu.btn.connecter":        "⟳ Connecter",
   "menu.btn.debloquer":        "⟳ Débloquer les boutons",
# ── Zone modifiée : ligne 53 (6 ligne(s)) dans l'ancienne version → ligne 54 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -53,6 +54,7 @@
   "menu.desc.retrans":         "Retranscrivez une partie jouée sur papier. Saisissez les coups sur l'échiquier virtuel et exportez le PGN.",
   "menu.desc.outils":          "Importez vos lignes PGN, convertissez SAN → UCI et gérez le catalogue d'ouvertures.",
   "menu.desc.parametres":      "Configurez l'accès LLM (clé API) et la synthèse vocale (TTS).",
+  "menu.desc.opening_explorer": "Parcourez une ouverture coup par coup — catalogue théorique ou vos lignes personnelles.",
   "menu.autoupdate.label":     "Mises à jour automatiques",
   "menu.autoupdate.warning":   "Les mises à jour automatiques sont désactivées. Vous ne recevrez pas les correctifs de sécurité ni les nouvelles fonctionnalités.",
 
# ── Zone modifiée : ligne 260 (6 ligne(s)) dans l'ancienne version → ligne 262 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -260,6 +262,20 @@
   "parametres.toast.enregistre":      "Paramètres enregistrés",
   "parametres.toast.erreur":          "Erreur lors de l'enregistrement des paramètres",
 
+  "opening_explorer.titre":                "♟ Opening Explorer",
+  "opening_explorer.catalogue.titre":      "📚 Catalogue",
+  "opening_explorer.catalogue.vide":       "Aucune ouverture dans le catalogue.",
+  "opening_explorer.mes_ouvertures.titre": "★ Mes ouvertures",
+  "opening_explorer.mes_ouvertures.vide":  "Aucune ligne personnelle importée. Utilisez Outils Exercices pour en ajouter.",
+  "opening_explorer.btn.precedent":        "← Précédent",
+  "opening_explorer.btn.suivant":          "Suivant →",
+  "opening_explorer.btn.autre":            "↩ Choisir une autre ouverture",
+  "opening_explorer.h2.explication":       "EXPLICATION",
+  "opening_explorer.explication.a_venir":  "L'explication du coup sera disponible ici prochainement.",
+  "opening_explorer.position_initiale":    "Position initiale",
+  "opening_explorer.coup_n":               "Coup {n} — {san}",
+  "opening_explorer.erreur_chargement":    "Impossible de charger cette ouverture.",
+
   "outils.titre":              "🛠️ Outils Exercices",
   "outils.import_pgn.titre":   "📥 Importer mes lignes PGN",
   "outils.import_pgn.desc":    "Sélectionnez un ou plusieurs fichiers .pgn pour les importer dans vos exercices personnels (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 831be0f..59627c0 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 195 (6 ligne(s)) dans l'ancienne version → ligne 195 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -195,6 +195,11 @@
         <div class="menu-btn-desc" id="desc-parametres" data-i18n="menu.desc.parametres">Configurez l'accès LLM (clé API) et la synthèse vocale (TTS).</div>
       </div>
 
+      <div class="menu-btn-wrap">
+        <button class="menu-btn menu-btn-secondary" onclick="sendAction({type:'mode', value:'opening_explorer'})" data-i18n="menu.btn.opening_explorer">♟ Opening Explorer</button>
+        <div class="menu-btn-desc" id="desc-opening-explorer" data-i18n="menu.desc.opening_explorer">Parcourez une ouverture coup par coup — catalogue théorique ou vos lignes personnelles.</div>
+      </div>
+
     </div><!-- fin colonne Outils -->
 
   </div><!-- fin menu-grid -->
