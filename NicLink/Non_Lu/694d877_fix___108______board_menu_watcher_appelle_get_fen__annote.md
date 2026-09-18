694d877

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 694d877
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 23:00:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #108 — _board_menu_watcher appelle get_fen() pour détecter la déconnexion

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e5a36fb..1b976e9 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/alchess.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 163 (6 ligne(s)) dans l'ancienne version → ligne 163 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -163,6 +163,7 @@ def _board_menu_watcher():
         if web_server._app_state != "menu":
             continue
         try:
+            hid_backend.get_fen()  # tente une lecture USB réelle → met _connected=False si déconnecté
             if not hid_backend.is_connected() and web_server._board_status == "ok":
                 send_event("board_error", {
                     "message": "Échiquier déconnecté — vérifiez l'USB et reconnectez le plateau.",
