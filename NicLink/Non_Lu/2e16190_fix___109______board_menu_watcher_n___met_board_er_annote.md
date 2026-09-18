2e16190

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2e16190
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 23:03:14 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #109 — _board_menu_watcher n'émet board_error qu'une seule fois par déconnexion

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1b976e9..4968692 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/alchess.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 158 (17 ligne(s)) dans l'ancienne version → ligne 158 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -158,17 +158,23 @@ def _board_menu_watcher():
     détectée alors que l'utilisateur est resté sur l'écran menu.
     """
     from nicsoft.niclink import hid_backend
+    _already_notified = False
     while True:
         time.sleep(3.0)
         if web_server._app_state != "menu":
+            _already_notified = False
             continue
         try:
             hid_backend.get_fen()  # tente une lecture USB réelle → met _connected=False si déconnecté
-            if not hid_backend.is_connected() and web_server._board_status == "ok":
-                send_event("board_error", {
-                    "message": "Échiquier déconnecté — vérifiez l'USB et reconnectez le plateau.",
-                    "message_key": "error.board.deconnecte",
-                })
+            if not hid_backend.is_connected():
+                if web_server._board_status == "ok" and not _already_notified:
+                    send_event("board_error", {
+                        "message": "Échiquier déconnecté — vérifiez l'USB et reconnectez le plateau.",
+                        "message_key": "error.board.deconnecte",
+                    })
+                    _already_notified = True
+            else:
+                _already_notified = False  # plateau reconnecté
         except Exception:
             pass
 
