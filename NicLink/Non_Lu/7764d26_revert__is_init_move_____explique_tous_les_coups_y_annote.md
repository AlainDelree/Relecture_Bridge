7764d26

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7764d26
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 10:24:54 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    revert: is_init_move — explique tous les coups y compris les init_moves (issue #167, suite #165)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/explorer_session.py b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ba93d61..d0e142b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/explorer_session.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Zone modifiée : ligne 142 (7 ligne(s)) dans l'ancienne version → ligne 142 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -142,7 +142,6 @@ class ExplorerSession:
             "camp":           getattr(self.source, "camp_suggere", "white") if self.source else "white",
             "alternatives":   alternatives,
             "line_id":        self.line_id,
-            "is_init_move":   0 < len(self._history) <= len(self._init_moves_list),
         }
 
     # ── Plateau Chessnut (physique ou virtuel) ─────────────────────────────────
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index acfe439..76aee34 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 703 (8 ligne(s)) dans l'ancienne version → ligne 703 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -703,8 +703,7 @@ def on_explorer_next(data):
     emit("explorer_state", state)
     language = (data or {}).get("language", "fr")
     sid = request.sid
-    if not state.get("is_init_move"):
-        threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language), daemon=True).start()
+    threading.Thread(target=_emit_explorer_explanation, args=(sid, state, language), daemon=True).start()
 
 
 @socketio.on("explorer_prev")
