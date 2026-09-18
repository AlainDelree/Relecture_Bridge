dccf066

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit dccf066
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 09:53:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Finalise le travail de l'issue #205 : config pytest, CORS dynamique par port, sélecteurs e2e à jour

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/tests/e2e/conftest.py b/nicsoft/tests/e2e/conftest.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 00c5497..0c46b5d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/tests/e2e/conftest.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/tests/e2e/conftest.py
# ── Zone modifiée : ligne 82 (12 ligne(s)) dans l'ancienne version → ligne 82 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -82,12 +82,12 @@ def page(server_url):
         # L'overlay de démarrage disparaît 5s après la connexion SocketIO
         pg.wait_for_selector("#startup-overlay", state="hidden", timeout=15000)
 
-        # Activer le mode virtuel (côté JS — active immédiatement les boutons)
-        pg.check("#chk-virtual-mode")
-
-        # Vérifier que le bouton Pédagogique est débloqué
+        # Mode virtuel coché par défaut sur la carte Pédagogique (issue #205 —
+        # le bouton unique "menu-btn-primary" + checkbox globale #chk-virtual-mode
+        # ont été remplacés par une checkbox "Mode virtuel" par carte lors du
+        # refactoring des cartes menu Pédagogique/Labo).
         pg.wait_for_selector(
-            "button.menu-btn-primary:not([disabled])",
+            ".menu-card-primary .menu-card-head",
             timeout=5000,
         )
 
# (diff du fichier suivant)
diff --git a/nicsoft/tests/e2e/test_smoke_e2e.py b/nicsoft/tests/e2e/test_smoke_e2e.py
# (index — ignorable)
index f57cceb..83c796e 100644
# (avant — fichier suivant)
--- a/nicsoft/tests/e2e/test_smoke_e2e.py
# (après — fichier suivant)
+++ b/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Zone modifiée : ligne 33 (7 ligne(s)) dans l'ancienne version → ligne 33 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -33,7 +33,7 @@ def test_titre_alchess(at_menu):
 
 def test_mode_virtuel_active_bouton_pedagogique(at_menu):
     """Mode virtuel coché → bouton Pédagogique non-disabled."""
-    btn = at_menu.locator("button.menu-btn-primary")
+    btn = at_menu.locator(".menu-card-primary .menu-card-head")
     assert not btn.is_disabled(), "Le bouton Pédagogique doit être actif en mode virtuel"
 
 
# ── Zone modifiée : ligne 41 (7 ligne(s)) dans l'ancienne version → ligne 41 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -41,7 +41,7 @@ def test_mode_virtuel_active_bouton_pedagogique(at_menu):
 
 def test_clic_pedagogique_ouvre_config(at_menu):
     """Clic Pédagogique → écran config affiché."""
-    at_menu.locator("button.menu-btn-primary").click()
+    at_menu.locator(".menu-card-primary .menu-card-head").click()
     at_menu.wait_for_selector("#screen-config", state="visible", timeout=5000)
     assert at_menu.locator("#screen-config").is_visible()
     go_menu(at_menu)
# ── Zone modifiée : ligne 49 (7 ligne(s)) dans l'ancienne version → ligne 49 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -49,7 +49,7 @@ def test_clic_pedagogique_ouvre_config(at_menu):
 
 def test_retour_depuis_config(at_menu):
     """Config pédagogique → Retour → menu."""
-    at_menu.locator("button.menu-btn-primary").click()
+    at_menu.locator(".menu-card-primary .menu-card-head").click()
     at_menu.wait_for_selector("#screen-config", state="visible", timeout=5000)
     at_menu.locator("#screen-config button", has_text="Retour").click()
     at_menu.wait_for_selector("#screen-menu", state="visible", timeout=5000)
# ── Zone modifiée : ligne 58 (7 ligne(s)) dans l'ancienne version → ligne 58 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -58,7 +58,7 @@ def test_retour_depuis_config(at_menu):
 
 def test_pedagogique_demarrer_puis_retour_menu(at_menu):
     """Config pédagogique → Démarrer → écran jeu → Retour au menu."""
-    at_menu.locator("button.menu-btn-primary").click()
+    at_menu.locator(".menu-card-primary .menu-card-head").click()
     at_menu.wait_for_selector("#screen-config", state="visible", timeout=5000)
 
     # Démarrer la partie (VirtualBoard + Stockfish) — cibler le bouton dans l'écran config pédagogique
# ── Zone modifiée : ligne 158 (7 ligne(s)) dans l'ancienne version → ligne 158 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -158,7 +158,7 @@ def test_transition_analyse_puis_menu(at_menu):
     at_menu.wait_for_selector("#screen-menu", state="visible", timeout=5000)
 
     # Pédagogique config → vérifier état propre
-    at_menu.locator("button.menu-btn-primary").click()
+    at_menu.locator(".menu-card-primary .menu-card-head").click()
     at_menu.wait_for_selector("#screen-config", state="visible", timeout=5000)
     assert at_menu.locator("#screen-config").is_visible()
     go_menu(at_menu)
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index b818939..c6a6218 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 11 (6 ligne(s)) dans l'ancienne version → ligne 11 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -11,6 +11,7 @@ import logging
 import os
 import pathlib
 import queue
+import re
 import secrets
 import sys
 import threading
# ── Zone modifiée : ligne 55 (16 ligne(s)) dans l'ancienne version → ligne 56 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -55,16 +56,21 @@ def _get_or_create_secret_key() -> str:
 
 
 # Origines autorisées pour les connexions SocketIO — le serveur ne sert
-# l'interface qu'en local (127.0.0.1:5000), donc pas besoin d'ouvrir le
-# CORS à "*" (issue #202).
-CORS_ALLOWED_ORIGINS = [
-    "http://127.0.0.1:5000",
-    "http://localhost:5000",
-]
+# l'interface qu'en local (127.0.0.1/localhost), donc pas besoin d'ouvrir le
+# CORS à "*" (issue #202). Le port est choisi dynamiquement au démarrage
+# (voir alchess._find_free_port), donc validé par motif plutôt que par une
+# liste figée sur 5000 — sinon toute connexion SocketIO est rejetée dès que
+# le port par défaut est occupé (issue #205).
+_ALLOWED_ORIGIN_RE = re.compile(r"^https?://(127\.0\.0\.1|localhost):\d+$")
+
+
+def _is_allowed_origin(origin: str) -> bool:
+    return bool(origin) and bool(_ALLOWED_ORIGIN_RE.match(origin))
+
 
 app = Flask(__name__)
 app.config["SECRET_KEY"] = _get_or_create_secret_key()
-socketio = SocketIO(app, cors_allowed_origins=CORS_ALLOWED_ORIGINS, async_mode="threading", )
+socketio = SocketIO(app, cors_allowed_origins=_is_allowed_origin, async_mode="threading", )
 
 # Queue pour recevoir les événements du module Python
 event_queue: queue.Queue = queue.Queue()
# (diff du fichier suivant)
diff --git a/pytest.ini b/pytest.ini
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..cda3ddd
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/pytest.ini
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,4 @@
+[pytest]
+testpaths = nicsoft/tests
+markers =
+    hardware: nécessite un échiquier Chessnut Air physiquement connecté en USB (non exécuté en CI)
