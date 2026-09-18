3b0b66e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3b0b66e
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 03:08:54 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: #91 (suite #90) — checkbox desactivation mises a jour automatiques
    
    Ajoute un fichier sentinelle no-update.txt a la racine du projet : sa
    presence fait sauter la verification de mise a jour du launcher
    (2-Lancer_AlChess.bat). Bascule via une checkbox dans l'ecran menu
    (cochee par defaut), qui appelle POST /toggle-autoupdate (Flask) pour
    creer/supprimer le fichier. Avertissement rouge affiche quand la
    checkbox est decochee. Cles i18n ajoutees dans fr/en/de.json.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/2-Lancer_AlChess.bat b/2-Lancer_AlChess.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 91ea345..874735b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/2-Lancer_AlChess.bat
# ── Version APRÈS ce commit.
+++ b/2-Lancer_AlChess.bat
# ── Zone modifiée : ligne 1 (4 ligne(s)) dans l'ancienne version → ligne 1 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,4 +1,8 @@
 @echo off
+if exist "%~dp0no-update.txt" (
+    echo Mises a jour automatiques desactivees.
+    goto :fin_update
+)
 rem --- Verification des mises a jour : dernier tag de release (issue #90, suite #89) ---
 rem  Auparavant "git pull --ff-only origin master" (issue #88) : tirait CHAQUE
 rem  commit de master. Pour la securite, on ne tire desormais que les versions
# ── Zone modifiée : ligne 50 (6 ligne(s)) dans l'ancienne version → ligne 54 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -50,6 +54,7 @@ goto :maj_fin
 echo Git non trouve - verification des mises a jour ignoree.
 
 :maj_fin
+:fin_update
 rem --- Fin verification ---
 
 rem ============================================================================
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index f2b93ba..b141be6 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 12 (13 ligne(s)) dans l'ancienne version → ligne 12 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -12,13 +12,17 @@ import os
 import pathlib
 import queue
 import threading
-from nicsoft.config import DATA_DIR, GAMES_DIR, LOGS_DIR
+from nicsoft.config import APP_DIR, DATA_DIR, GAMES_DIR, LOGS_DIR
 from flask import Flask, render_template, send_file, abort
 from flask_socketio import SocketIO, emit
 
 logger = logging.getLogger("niclink.server")
 LOG_FILE = LOGS_DIR / "niclink.log"
 
+# Fichier sentinelle : sa presence desactive la verification des mises a
+# jour automatiques faite par 2-Lancer_AlChess.bat au demarrage (issue #91).
+NO_UPDATE_FILE = APP_DIR / "no-update.txt"
+
 # Mode debug — activé via variable d'environnement NICLINK_LOG=DEBUG
 DEBUG_MODE = os.environ.get("NICLINK_LOG", "").upper() == "DEBUG"
 
# ── Zone modifiée : ligne 103 (7 ligne(s)) dans l'ancienne version → ligne 107 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -103,7 +107,7 @@ def _get_rodent_available() -> bool:
 
 @app.route("/")
 def index():
-    return render_template("index.html", test_mode=TEST_MODE)
+    return render_template("index.html", test_mode=TEST_MODE, autoupdate_active=not NO_UPDATE_FILE.exists())
 
 @app.route("/logs")
 def get_logs():
# ── Zone modifiée : ligne 134 (6 ligne(s)) dans l'ancienne version → ligne 138 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -134,6 +138,22 @@ def debug_mode_status():
     from flask import jsonify
     return jsonify({"debug": DEBUG_MODE})
 
+@app.route("/toggle-autoupdate", methods=["POST"])
+def toggle_autoupdate():
+    """Active/désactive les mises à jour automatiques du launcher (issue #91).
+
+    Bascule via la présence de NO_UPDATE_FILE à la racine du projet,
+    lu par 2-Lancer_AlChess.bat au démarrage.
+    """
+    from flask import jsonify
+    if NO_UPDATE_FILE.exists():
+        NO_UPDATE_FILE.unlink()
+        active = True
+    else:
+        NO_UPDATE_FILE.write_text("Presence de ce fichier = mises a jour automatiques desactivees.\n", encoding="utf-8")
+        active = False
+    return jsonify({"active": active})
+
 TEST_CONFIG_DIR = LOGS_DIR / "Test config"
 
 @app.route("/test/save-config", methods=["POST"])
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 56ff37f..e807fb3 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 36 (6 ligne(s)) dans l'ancienne version → ligne 36 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -36,6 +36,19 @@ function debugMark(e) {
     .catch(() => {});
 }
 
+// ── MISES À JOUR AUTOMATIQUES (issue #91) ─────────────────
+function toggleAutoUpdate() {
+  fetch("/toggle-autoupdate", { method: "POST" })
+    .then(r => r.json())
+    .then(data => {
+      const chk = document.getElementById("chk-autoupdate");
+      const warning = document.getElementById("autoupdate-warning");
+      if (chk) chk.checked = data.active;
+      if (warning) warning.style.display = data.active ? "none" : "block";
+    })
+    .catch(() => {});
+}
+
 // ── MODE TEST ALÉATOIRE ───────────────────────────────────
 const _testMode = (window._NICLINK_TEST || "") === "random";
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index af20a5d..766592e 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 47 (6 ligne(s)) dans l'ancienne version → ligne 47 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,6 +47,8 @@
   "menu.desc.exercices":       "Eröffnungen mit einem Großmeister-Buch trainieren. Züge auf dem Brett spielen — das Buch antwortet und führt durch die Theorie.",
   "menu.desc.retrans":         "Eine auf Papier gespielte Partie mitschreiben. Züge auf dem virtuellen Brett eingeben und das PGN exportieren.",
   "menu.desc.outils":          "PGN-Linien importieren, SAN → UCI konvertieren und den Eröffnungskatalog verwalten.",
+  "menu.autoupdate.label":     "Automatische Updates",
+  "menu.autoupdate.warning":   "Automatische Updates sind deaktiviert. Sie erhalten weder Sicherheitskorrekturen noch neue Funktionen.",
 
   "config.titre.pedagogique":  "Trainingsmodus",
   "config.titre.humain":       "Mensch gegen Mensch",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index 888aaeb..8f7cc82 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 47 (6 ligne(s)) dans l'ancienne version → ligne 47 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,6 +47,8 @@
   "menu.desc.exercices":       "Train your openings with a Grandmaster book. Play your moves on the physical board — the book responds and guides you through the theory.",
   "menu.desc.retrans":         "Transcribe a game played on paper. Enter moves on the virtual board and export the PGN.",
   "menu.desc.outils":          "Import your PGN lines, convert SAN → UCI and manage the openings catalogue.",
+  "menu.autoupdate.label":     "Automatic updates",
+  "menu.autoupdate.warning":   "Automatic updates are disabled. You will not receive security fixes or new features.",
 
   "config.titre.pedagogique":  "Training Mode",
   "config.titre.humain":       "Human vs Human",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index 5f2154f..0f2eaa2 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 47 (6 ligne(s)) dans l'ancienne version → ligne 47 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,6 +47,8 @@
   "menu.desc.exercices":       "Entraînez-vous aux ouvertures avec un livre de Grands Maîtres. Jouez vos coups sur l'échiquier physique — le livre répond et vous guide dans la théorie.",
   "menu.desc.retrans":         "Retranscrivez une partie jouée sur papier. Saisissez les coups sur l'échiquier virtuel et exportez le PGN.",
   "menu.desc.outils":          "Importez vos lignes PGN, convertissez SAN → UCI et gérez le catalogue d'ouvertures.",
+  "menu.autoupdate.label":     "Mises à jour automatiques",
+  "menu.autoupdate.warning":   "Les mises à jour automatiques sont désactivées. Vous ne recevrez pas les correctifs de sécurité ni les nouvelles fonctionnalités.",
 
   "config.titre.pedagogique":  "Mode Pédagogique",
   "config.titre.humain":       "Humain vs Humain",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index b70dcdc..f9434c4 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 122 (6 ligne(s)) dans l'ancienne version → ligne 122 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -122,6 +122,16 @@
 
 
   <button class="menu-btn" onclick="ouvrirModal('quit', t('modal.quitter_alchess'), t('modal.quitter_btn'), 'btn-warning')" style="background:#b8cce0; color:#555; border:1px solid #333; font-size:0.85rem; margin-top:8px;" data-i18n="menu.btn.quitter">✕ Quitter</button>
+
+  <div style="margin-top:12px; font-size:0.8rem; color:#3a5a7a; text-align:center;">
+    <label style="cursor:pointer;">
+      <input type="checkbox" id="chk-autoupdate" {% if autoupdate_active %}checked{% endif %} onchange="toggleAutoUpdate()">
+      <span data-i18n="menu.autoupdate.label">Mises à jour automatiques</span>
+    </label>
+    <div id="autoupdate-warning" style="display:{% if autoupdate_active %}none{% else %}block{% endif %}; color:#c0392b; font-size:0.75rem; margin-top:4px; max-width:420px; margin-left:auto; margin-right:auto;" data-i18n="menu.autoupdate.warning">
+      Les mises à jour automatiques sont désactivées. Vous ne recevrez pas les correctifs de sécurité ni les nouvelles fonctionnalités.
+    </div>
+  </div>
 </div>
 
 <!-- ── Écran config ── -->
