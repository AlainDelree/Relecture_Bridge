9ca01a9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9ca01a9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 17:28:37 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: Opening Explorer — dépiler coup courant avant alternative dans choose_move (issue #146)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/explorer_session.py b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9106d3d..db614d5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/explorer_session.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Zone modifiée : ligne 79 (6 ligne(s)) dans l'ancienne version → ligne 79 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -79,6 +79,10 @@ class ExplorerSession:
         Utilisé quand l'utilisateur clique sur une alternative du tableau.
         Le coup doit être légal sur le board courant. Retourne get_state()
         après application, ou get_state() inchangé si le coup est illégal."""
+        # Revenir à la position depuis laquelle les alternatives sont calculées
+        if self._history:
+            self._history.pop()
+            self.board.pop()
         try:
             move = chess.Move.from_uci(uci)
         except Exception:
