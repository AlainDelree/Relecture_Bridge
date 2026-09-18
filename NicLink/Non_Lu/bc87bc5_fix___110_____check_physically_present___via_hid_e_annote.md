bc87bc5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bc87bc5
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 23:08:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #110 — check_physically_present() via hid.enumerate() dans _board_menu_watcher
    
    get_fen() ne détecte pas un débranchement sur Linux (read() timeout
    silencieusement au lieu de lever OSError). check_physically_present()
    interroge directement hid.enumerate() pour confirmer la présence USB
    du Chessnut, sans dépendre d'une lecture FEN.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/niclink/hid_backend.py b/nicsoft/niclink/hid_backend.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b7e481a..7efcd82 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/niclink/hid_backend.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/niclink/hid_backend.py
# ── Zone modifiée : ligne 119 (6 ligne(s)) dans l'ancienne version → ligne 119 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -119,6 +119,27 @@ def is_connected() -> bool:
     return _connected
 
 
+def check_physically_present() -> bool:
+    """Vérifie si un Chessnut est encore visible dans le sous-système USB.
+
+    Contrairement à get_fen(), qui sur Linux ne détecte pas un débranchement
+    (le read() timeout silencieusement au lieu de lever une OSError), cette
+    fonction interroge directement hid.enumerate() pour confirmer la présence
+    physique du périphérique.
+    """
+    global _connected
+    if not _connected or _dev is None:
+        return False
+    try:
+        for info in hid.enumerate(VENDOR_ID, 0):
+            if info['product_id'] in PRODUCT_IDS:
+                return True
+        _connected = False
+        return False
+    except Exception:
+        return False
+
+
 def get_fen() -> str:
     """Lit la position courante depuis l'échiquier USB.
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# (index — ignorable)
index 4968692..e431eb2 100644
# (avant — fichier suivant)
--- a/nicsoft/web/alchess.py
# (après — fichier suivant)
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 165 (8 ligne(s)) dans l'ancienne version → ligne 165 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -165,8 +165,7 @@ def _board_menu_watcher():
             _already_notified = False
             continue
         try:
-            hid_backend.get_fen()  # tente une lecture USB réelle → met _connected=False si déconnecté
-            if not hid_backend.is_connected():
+            if not hid_backend.check_physically_present():
                 if web_server._board_status == "ok" and not _already_notified:
                     send_event("board_error", {
                         "message": "Échiquier déconnecté — vérifiez l'USB et reconnectez le plateau.",
