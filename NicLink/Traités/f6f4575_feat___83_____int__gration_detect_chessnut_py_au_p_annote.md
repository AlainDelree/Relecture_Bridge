f6f4575

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f6f4575
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Jul 28 01:30:20 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: #83 — intégration detect_chessnut.py au premier démarrage
    
    Appel best-effort de detect_chessnut.py dans _check_board_at_startup()
    (alchess.py) si la connexion à l'échiquier échoue, et appel silencieux
    dans 2-Lancer_AlChess.bat avant le lancement du serveur (Windows).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/2-Lancer_AlChess.bat b/2-Lancer_AlChess.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c5fdee1..0054735 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/2-Lancer_AlChess.bat
# ── Version APRÈS ce commit.
+++ b/2-Lancer_AlChess.bat
# ── Zone modifiée : ligne 60 (7 ligne(s)) dans l'ancienne version → ligne 60 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -60,7 +60,10 @@ echo   (fermer cette fenetre arrete le serveur)
 echo   Journal : "%~dp0alchess_log.txt"
 echo(
 
-"%~dp0venv\Scripts\python.exe" -m nicsoft.web > "%~dp0alchess_log.txt" 2>&1
+rem Detection automatique du modele Chessnut (silencieux si echiquier absent, issue #83)
+"%~dp0venv\Scripts\python.exe" "%~dp0scripts\detect_chessnut.py" > "%~dp0alchess_log.txt" 2>&1
+
+"%~dp0venv\Scripts\python.exe" -m nicsoft.web >> "%~dp0alchess_log.txt" 2>&1
 
 echo(
 echo   AlChess s'est arrete. En cas de probleme, consultez le journal :
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index a80718e..d7f624f 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 47 (6 ligne(s)) dans l'ancienne version → ligne 47 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,6 +47,8 @@
 
 ### Session du 28 juillet
 
+Intégration de detect_chessnut.py au premier démarrage : appel dans web/__main__.py si connect() échoue (best-effort, non bloquant) + appel silencieux dans 2-Lancer_AlChess.bat avant le serveur. (issue #83)
+
 Intégration de detect_chessnut.py dans l'installeur NSIS : section SecChessnut ajoutée après SecVenv, appel avec le Python du venv, message utilisateur selon le code de sortie. makensis : 0 erreur, 0 warning. (issue #82)
 
 - **Support Chessnut Go (idProduct `8501`) — non détecté par l'app** `[Linux]` (issue #78) — Alain utilise un Chessnut Go (modèle de voyage, ref CG100) : `lsusb` a révélé `2d80:8501`, même `idVendor` que tous les modèles Chessnut, `idProduct` inédit. Correctif identique à l'issue #77 (Air Plus) : `0x8501` ajouté à `PRODUCT_IDS` dans `hid_backend.py` (L.12), règle udev ajoutée dans `99-chessnutair.rules.example`, notes ajoutées dans `INSTALLATION_ALCHESS.md` aux côtés du Air (8003) et Air Plus (8202). `py_compile` OK sur `hid_backend.py`. **Test réel décisif à faire** avec l'échiquier branché. Backup pinné avant modif.
# (diff du fichier suivant)
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# (index — ignorable)
index 6180b45..b4ff4e0 100644
# (avant — fichier suivant)
--- a/nicsoft/web/alchess.py
# (après — fichier suivant)
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 4 (11 ligne(s)) dans l'ancienne version → ligne 4 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,11 +4,12 @@ nicsoft/web/__main__.py — Point d'entrée principal NicLink.
 import os
 import time
 import sys
+import subprocess
 import threading
 import webbrowser
 import socket
 import logging
-from nicsoft.config import DATA_DIR, LOGS_DIR
+from nicsoft.config import APP_DIR, DATA_DIR, LOGS_DIR
 from nicsoft.platform_utils import stop_modem_manager, start_modem_manager
 from nicsoft.web.server import start_server, set_app_state, get_menu_action, send_event, set_virtual_board
 from nicsoft.web import server as web_server
# ── Zone modifiée : ligne 93 (6 ligne(s)) dans l'ancienne version → ligne 94 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -93,6 +94,26 @@ def _find_free_port(start=5000):
     return start  # fallback
 
 
+def _run_detect_chessnut():
+    """Best-effort, non bloquant : toute erreur est journalisée et ignorée."""
+    logger = logging.getLogger("niclink")
+    detect_script = APP_DIR / "scripts" / "detect_chessnut.py"
+    if not detect_script.exists():
+        return
+    try:
+        result = subprocess.run(
+            [sys.executable, str(detect_script)], capture_output=True, text=True, timeout=15
+        )
+        if result.returncode == 1:
+            logger.info("Nouveau modèle Chessnut enregistré. Relancez l'application.")
+        elif result.returncode == 0:
+            logger.info("Aucun échiquier Chessnut reconnu branché au démarrage.")
+        else:
+            logger.info(f"detect_chessnut.py — code retour {result.returncode} : {result.stderr.strip()}")
+    except Exception as e:
+        logger.info(f"detect_chessnut.py — appel best-effort échoué : {e}")
+
+
 def _check_board_at_startup():
     if not _board_check_lock.acquire(blocking=False):
         return  # une vérification est déjà en cours
# ── Zone modifiée : ligne 117 (11 ligne(s)) dans l'ancienne version → ligne 138 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -117,11 +138,13 @@ def _check_board_at_startup():
                 return  # succès
             except SystemExit as e:
                 if "board connection error" not in str(e):
+                    _run_detect_chessnut()
                     send_event("board_error", {"message": "Échiquier non détecté — vérifiez l'USB et allumez le plateau."})
                     return
                 # board pas encore prêt — réessayer
             except Exception:
                 pass  # réessayer
+        _run_detect_chessnut()
         send_event("board_error", {"message": "Échiquier non détecté — vérifiez l'USB et allumez le plateau."})
     finally:
         _board_check_lock.release()
