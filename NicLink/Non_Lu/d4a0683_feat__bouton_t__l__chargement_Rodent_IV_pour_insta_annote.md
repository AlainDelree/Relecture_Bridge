d4a0683

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d4a0683
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 22:29:33 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: bouton téléchargement Rodent IV pour installation NSIS Windows (#131)
    
    SyncGitRepo ne télécharge pas les binaires engines/rodent-iv-win/ sur une
    installation NSIS standalone. Ajoute un bouton "Download Rodent IV" (config
    péda + labo, visible uniquement sous Windows) qui les récupère depuis GitHub
    via un handler SocketIO download_rodent (urllib stdlib, events de progression).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7ec3cfb..0176cc0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/server.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 11 (8 ligne(s)) dans l'ancienne version → ligne 11 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -11,8 +11,9 @@ import logging
 import os
 import pathlib
 import queue
+import sys
 import threading
-from nicsoft.config import APP_DIR, DATA_DIR, GAMES_DIR, LOGS_DIR
+from nicsoft.config import APP_DIR, DATA_DIR, ENGINES_DIR, GAMES_DIR, LOGS_DIR
 from flask import Flask, render_template, send_file, abort
 from flask_socketio import SocketIO, emit
 
# ── Zone modifiée : ligne 103 (6 ligne(s)) dans l'ancienne version → ligne 104 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -103,6 +104,46 @@ def _get_rodent_available() -> bool:
     return _rodent_available_cache
 
 
+# URL des binaires Rodent IV Windows sur GitHub — utilisée par download_rodent
+# quand SyncGitRepo n'a pas récupéré ces fichiers (installation NSIS standalone).
+_RODENT_WIN_BASE_URL = "https://raw.githubusercontent.com/AlainDelree/AlChess/master/engines/rodent-iv-win/"
+_RODENT_WIN_FILES = ["rodent-iv-x64.exe", "msvcr120.dll", "msvcp120.dll"]
+
+
+@socketio.on("download_rodent")
+def on_download_rodent(_data):
+    """Télécharge les binaires Rodent IV Windows depuis GitHub (issue #131).
+
+    SyncGitRepo ne récupère pas les binaires sur une installation NSIS
+    standalone ; ce handler les télécharge directement depuis la branche
+    master du dépôt public, dans ENGINES_DIR/rodent-iv-win/.
+    """
+    if sys.platform != "win32":
+        emit("rodent_download_result", {"ok": False, "error": "Téléchargement disponible uniquement sous Windows"})
+        return
+
+    def run():
+        import urllib.request
+        global _rodent_available_cache
+        dest_dir = ENGINES_DIR / "rodent-iv-win"
+        try:
+            dest_dir.mkdir(parents=True, exist_ok=True)
+            total = len(_RODENT_WIN_FILES)
+            for index, filename in enumerate(_RODENT_WIN_FILES, start=1):
+                socketio.emit("rodent_download_progress", {
+                    "file": filename, "index": index, "total": total,
+                })
+                urllib.request.urlretrieve(_RODENT_WIN_BASE_URL + filename, str(dest_dir / filename))
+            _rodent_available_cache = None
+            socketio.emit("rodent_download_result", {"ok": True})
+            socketio.emit("rodent_status", {"available": _get_rodent_available(), "downloadable": True})
+        except Exception as e:
+            logger.error(f"[WEB] Téléchargement Rodent IV échoué : {e}")
+            socketio.emit("rodent_download_result", {"ok": False, "error": str(e)})
+
+    threading.Thread(target=run, daemon=True).start()
+
+
 # ── Routes ────────────────────────────────────────────────────────────────────
 
 @app.route("/")
# ── Zone modifiée : ligne 213 (7 ligne(s)) dans l'ancienne version → ligne 254 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -213,7 +254,7 @@ def on_connect():
     # Disponibilité des moteurs → l'UI grise ceux qui ne sont pas disponibles
     emit("stockfish_status", {"available": _get_stockfish_available()})
     emit("maia_status", {"available": _get_maia_available()})
-    emit("rodent_status", {"available": _get_rodent_available()})
+    emit("rodent_status", {"available": _get_rodent_available(), "downloadable": sys.platform == "win32"})
     # Renvoyer le statut échiquier au navigateur qui arrive/rafraîchit
     if _board_status == "ok":
         emit("board_ok", {})
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index a82e301..4362c32 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 491 (6 ligne(s)) dans l'ancienne version → ligne 491 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -491,6 +491,9 @@ let _selectedEngine = "stockfish";
 let _stockfishAvailable = true;
 let _maiaAvailable = true;
 let _rodentAvailable = true;
+// true si le serveur tourne sous Windows — seul cas où le téléchargement
+// des binaires Rodent IV depuis GitHub est proposé (issue #131).
+let _rodentDownloadable = false;
 
 // Grise les boutons Stockfish (config péda + labo) et affiche le message
 // d'indisponibilité si absent. Ré-appelé au changement de langue.
# ── Zone modifiée : ligne 533 (20 ligne(s)) dans l'ancienne version → ligne 536 (56 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -533,20 +536,56 @@ function _applyMaiaAvailability() {
 // de langue via _refreshDynamicLabels() pour retraduire le tooltip.
 function _applyRodentAvailability() {
   const msg = t("engine.rodent.unavailable");
-  [["cfg-engine-rodent", "cfg-rodent-unavailable"],
-   ["labo-eng-rodent",   "labo-rodent-unavailable"]].forEach(([btnId, msgId]) => {
+  [["cfg-engine-rodent", "cfg-rodent-unavailable", "cfg-rodent-download-btn"],
+   ["labo-eng-rodent",   "labo-rodent-unavailable", "labo-rodent-download-btn"]].forEach(([btnId, msgId, dlBtnId]) => {
     const btn = document.getElementById(btnId);
     const box = document.getElementById(msgId);
+    const dlBtn = document.getElementById(dlBtnId);
     if (btn) {
       btn.classList.toggle("engine-unavailable", !_rodentAvailable);
       if (_rodentAvailable) btn.removeAttribute("title");
       else                  btn.setAttribute("title", msg);
     }
     if (box) box.style.display = _rodentAvailable ? "none" : "";
+    if (dlBtn) dlBtn.style.display = (_rodentDownloadable && !_rodentAvailable) ? "" : "none";
   });
   _checkNoEngineAvailable();
 }
 
+// Télécharge les binaires Rodent IV depuis GitHub (Windows uniquement, issue #131).
+// Déclenché par les boutons cfg-rodent-download-btn / labo-rodent-download-btn.
+function downloadRodent() {
+  ["cfg-rodent-download-btn", "labo-rodent-download-btn"].forEach(id => {
+    const btn = document.getElementById(id);
+    if (btn) btn.disabled = true;
+  });
+  ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
+    const status = document.getElementById(id);
+    if (status) status.textContent = t("engine.rodent.downloading");
+  });
+  socket.emit("download_rodent", {});
+}
+
+socket.on("rodent_download_progress", (data) => {
+  const msg = `${t("engine.rodent.downloading")} (${data.index}/${data.total} ${data.file})`;
+  ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
+    const status = document.getElementById(id);
+    if (status) status.textContent = msg;
+  });
+});
+
+socket.on("rodent_download_result", (data) => {
+  const msg = data && data.ok ? t("engine.rodent.download_ok") : t("engine.rodent.download_error");
+  ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
+    const status = document.getElementById(id);
+    if (status) status.textContent = msg;
+  });
+  ["cfg-rodent-download-btn", "labo-rodent-download-btn"].forEach(id => {
+    const btn = document.getElementById(id);
+    if (btn) btn.disabled = false;
+  });
+});
+
 // Vérifie si aucun moteur n'est disponible — grise le bouton Démarrer et affiche l'alerte.
 function _checkNoEngineAvailable() {
   const noEngine = !_stockfishAvailable && !_maiaAvailable && !_rodentAvailable;
# ── Zone modifiée : ligne 5936 (6 ligne(s)) dans l'ancienne version → ligne 5975 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5936,6 +5975,7 @@ socket.on("maia_status", (data) => {
 // Disponibilité de Rodent IV (handshake UCI côté serveur) → grisage de l'UI
 socket.on("rodent_status", (data) => {
   _rodentAvailable = data && data.available !== false;
+  _rodentDownloadable = !!(data && data.downloadable);
   // Si Rodent était sélectionné alors qu'il est indisponible, repli sur premier disponible
   if (!_rodentAvailable) {
     const fallback = _firstAvailableEngine(false);
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index e7d52a4..4d849ea 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 95 (6 ligne(s)) dans l'ancienne version → ligne 95 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -95,6 +95,10 @@
   "engine.stockfish.unavailable":   "Stockfish ist auf diesem System nicht installiert",
   "engine.maia.unavailable":        "Maia (lc0 + Gewichte) ist auf diesem System nicht installiert",
   "engine.rodent.unavailable":      "Rodent-Engine auf diesem System nicht verfügbar",
+  "engine.rodent.download":         "Rodent IV herunterladen",
+  "engine.rodent.downloading":      "Wird heruntergeladen…",
+  "engine.rodent.download_ok":      "Rodent IV heruntergeladen — einsatzbereit",
+  "engine.rodent.download_error":   "Download fehlgeschlagen — Internetverbindung prüfen",
   "engine.none.available":          "Keine Schach-Engine verfügbar — installieren Sie Stockfish, Maia oder Rodent",
 
   "config.pause.toujours":     "Immer",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index 0a3e67d..bae5e10 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 95 (6 ligne(s)) dans l'ancienne version → ligne 95 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -95,6 +95,10 @@
   "engine.stockfish.unavailable":   "Stockfish not installed on this system",
   "engine.maia.unavailable":        "Maia (lc0 + weights) not installed on this system",
   "engine.rodent.unavailable":      "Rodent engine unavailable on this system",
+  "engine.rodent.download":         "Download Rodent IV",
+  "engine.rodent.downloading":      "Downloading…",
+  "engine.rodent.download_ok":      "Rodent IV downloaded — ready to use",
+  "engine.rodent.download_error":   "Download failed — check your internet connection",
   "engine.none.available":          "No chess engine available — install Stockfish, Maia or Rodent",
 
   "config.pause.toujours":     "Always",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index a915a8b..0a926d7 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 95 (6 ligne(s)) dans l'ancienne version → ligne 95 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -95,6 +95,10 @@
   "engine.stockfish.unavailable":   "Stockfish non installé sur ce système",
   "engine.maia.unavailable":        "Maia (lc0 + poids) non installé sur ce système",
   "engine.rodent.unavailable":      "Moteur Rodent indisponible sur ce système",
+  "engine.rodent.download":         "Télécharger Rodent IV",
+  "engine.rodent.downloading":      "Téléchargement…",
+  "engine.rodent.download_ok":      "Rodent IV téléchargé — prêt à l'emploi",
+  "engine.rodent.download_error":   "Échec du téléchargement — vérifiez votre connexion internet",
   "engine.none.available":          "Aucun moteur d'échecs n'est disponible — installez Stockfish, Maia ou Rodent",
 
   "config.pause.toujours":     "Toujours",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index b8754cf..e0e6a36 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 261 (8 ligne(s)) dans l'ancienne version → ligne 261 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -261,8 +261,13 @@
                data-i18n="engine.stockfish.unavailable">Stockfish non installé sur ce système</div>
           <div id="cfg-maia-unavailable" style="display:none; font-size:0.78rem; color:#c0392b; margin:-8px 0 12px;"
                data-i18n="engine.maia.unavailable">Maia (lc0 + poids) non installé sur ce système</div>
-          <div id="cfg-rodent-unavailable" style="display:none; font-size:0.78rem; color:#c0392b; margin:-8px 0 12px;"
-               data-i18n="engine.rodent.unavailable">Moteur Rodent indisponible sur ce système</div>
+          <div id="cfg-rodent-unavailable" style="display:none; font-size:0.78rem; color:#c0392b; margin:-8px 0 12px;">
+            <span data-i18n="engine.rodent.unavailable">Moteur Rodent indisponible sur ce système</span>
+            <button id="cfg-rodent-download-btn" type="button" onclick="downloadRodent()"
+                    style="display:none; margin-left:8px; font-size:0.75rem; padding:2px 8px; cursor:pointer;"
+                    data-i18n="engine.rodent.download">Télécharger Rodent IV</button>
+            <span id="cfg-rodent-download-status" style="margin-left:6px; color:#3a5a7a;"></span>
+          </div>
           <div id="cfg-no-engine-alert" style="display:none; font-size:0.85rem; color:#c0392b; margin:8px 0; padding:8px; background:#ffe0e0; border-radius:4px; text-align:center;"
                data-i18n="engine.none.available">Aucun moteur d'échecs n'est disponible</div>
 
# ── Zone modifiée : ligne 1069 (8 ligne(s)) dans l'ancienne version → ligne 1074 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1069,8 +1074,13 @@
              data-i18n="engine.stockfish.unavailable">Stockfish non installé sur ce système</div>
         <div id="labo-maia-unavailable" style="display:none; font-size:0.72rem; color:#c0392b;"
              data-i18n="engine.maia.unavailable">Maia (lc0 + poids) non installé sur ce système</div>
-        <div id="labo-rodent-unavailable" style="display:none; font-size:0.72rem; color:#c0392b;"
-             data-i18n="engine.rodent.unavailable">Moteur Rodent indisponible sur ce système</div>
+        <div id="labo-rodent-unavailable" style="display:none; font-size:0.72rem; color:#c0392b;">
+          <span data-i18n="engine.rodent.unavailable">Moteur Rodent indisponible sur ce système</span>
+          <button id="labo-rodent-download-btn" type="button" onclick="downloadRodent()"
+                  style="display:none; margin-left:6px; font-size:0.7rem; padding:2px 6px; cursor:pointer;"
+                  data-i18n="engine.rodent.download">Télécharger Rodent IV</button>
+          <span id="labo-rodent-download-status" style="margin-left:4px; color:#3a5a7a;"></span>
+        </div>
         <div id="labo-cfg-sf">
           <div style="display:flex; align-items:center; gap:5px; margin-bottom:3px;">
             <button onclick="laboAdjElo(-200)" style="width:36px;height:28px;background:#a0b8d0;border:1px solid #333;border-radius:4px;color:#445;cursor:pointer;font-size:0.7rem;">-200</button>
