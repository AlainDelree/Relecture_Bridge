4ed5def

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4ed5def
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 17:19:53 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: Opening Explorer — clic sur coup alternatif pour bifurquer sur la ligne (issue #145)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 315cec0..6c0266f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 1154 (6 ligne(s)) dans l'ancienne version → ligne 1154 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1154,6 +1154,15 @@ def explorer_prev() -> dict:
     return state
 
 
+def explorer_choose_move(uci: str) -> dict:
+    if _explorer_session is None:
+        return {}
+    state = _explorer_session.choose_move(uci)
+    state["end_of_line"] = not _explorer_session.has_more()
+    state["at_start"]    = _explorer_session.is_at_start()
+    return state
+
+
 def explorer_get_state() -> dict:
     """Retourne l'état courant de la session Opening Explorer active, ou None."""
     if _explorer_session is None:
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/explorer_session.py b/nicsoft/modes/opening_explorer/explorer_session.py
# (index — ignorable)
index 6e268be..9106d3d 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/opening_explorer/explorer_session.py
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Zone modifiée : ligne 74 (6 ligne(s)) dans l'ancienne version → ligne 74 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -74,6 +74,23 @@ class ExplorerSession:
         self._update_board_display()
         return self.get_state()
 
+    def choose_move(self, uci: str) -> dict:
+        """Applique un coup spécifique (UCI) au lieu du coup principal.
+        Utilisé quand l'utilisateur clique sur une alternative du tableau.
+        Le coup doit être légal sur le board courant. Retourne get_state()
+        après application, ou get_state() inchangé si le coup est illégal."""
+        try:
+            move = chess.Move.from_uci(uci)
+        except Exception:
+            return self.get_state()
+        if move not in self.board.legal_moves:
+            return self.get_state()
+        san = san_ep(self.board, move)
+        self.board.push(move)
+        self._history.append((move, san))
+        self._update_board_display()
+        return self.get_state()
+
     def prev_move(self) -> dict:
         """Dépile le dernier coup joué. No-op si déjà à la position de départ."""
         if self.is_at_start():
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index 648c1ca..84364d0 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 709 (6 ligne(s)) dans l'ancienne version → ligne 709 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -709,6 +709,23 @@ def on_explorer_prev(data):
     threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language), daemon=True).start()
 
 
+@socketio.on("explorer_choose_move")
+def on_explorer_choose_move(data):
+    uci = (data or {}).get("uci", "")
+    if not uci:
+        return
+    from nicsoft.core.game_manager import explorer_choose_move
+    state = explorer_choose_move(uci)
+    emit("explorer_state", state)
+    language = (data or {}).get("language", "fr")
+    sid = request.sid
+    threading.Thread(
+        target=_emit_explorer_explanation,
+        args=(sid, state, language),
+        daemon=True
+    ).start()
+
+
 @socketio.on("explorer_chat")
 def on_explorer_chat(data):
     """Question libre de l'utilisateur sur la position courante — réponse LLM en arrière-plan."""
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 05ef7c7..52ad0b8 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6213 (6 ligne(s)) dans l'ancienne version → ligne 6213 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6213,6 +6213,13 @@ function explRenderMovesTable(data) {
 
     const row = document.createElement("div");
     row.style.cssText = "display:flex; align-items:center; gap:8px; font-size:0.82rem;";
+    if (!isMain) {
+      row.style.cursor = "pointer";
+      row.title = alt.san || alt.uci;
+      row.addEventListener("click", () => {
+        socket.emit("explorer_choose_move", { uci: alt.uci, language: i18n.locale() });
+      });
+    }
 
     const sanEl = document.createElement("div");
     sanEl.style.cssText = `width:52px; flex-shrink:0; color:#1a2a3a; ${isMain ? "font-weight:700;" : ""}`;
