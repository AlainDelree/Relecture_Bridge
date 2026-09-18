e92e363

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e92e363
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 14:33:30 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: config_manager centralisé + panneau Paramètres (LLM/TTS) — issue #139
    
    Prérequis Opening Explorer 1/4 : data/config.json passe en lecture/écriture
    via nicsoft/core/config_manager.py (load_config/save_config atomique),
    handlers SocketIO config_get/config_save, et panneau ⚙ Paramètres dans le
    menu principal pour saisir clé API LLM et réglages TTS. Les load_config()
    locaux existants (pedagogique.py, game_manager.py) ne sont pas touchés.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/config_manager.py b/nicsoft/core/config_manager.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..ff39038
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/config_manager.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (58 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,58 @@
+"""
+config_manager.py — AlChess
+
+Point d'accès centralisé à data/config.json.
+
+Ne remplace PAS les load_config() locaux existants (pedagogique.py,
+game_manager.py) — ceux-ci restent en place pour l'instant (hors scope).
+Ce module sert de base commune pour les nouveaux consommateurs (Opening
+Explorer, panneau Paramètres) et regroupe notamment les champs LLM/TTS.
+"""
+
+import json
+import os
+
+from nicsoft.config import DATA_DIR
+
+CONFIG_FILE = DATA_DIR / "config.json"
+
+DEFAULT_CONFIG = {
+    "stockfish_level": 5,
+    "game_type": "Pedagogical",
+    "turn_signal": "both",
+    "pedagogique_pause": "blunder",
+    "llm_provider": "claude",   # "claude" | "openai"
+    "llm_api_key": "",
+    "llm_model": "",            # optionnel, laisser vide = modèle par défaut
+    "tts_enabled": False,
+    "tts_rate": 150,            # débit pyttsx3, mots par minute
+}
+
+
+def load_config() -> dict:
+    """Lit data/config.json avec fallback sur DEFAULT_CONFIG."""
+    if CONFIG_FILE.exists():
+        try:
+            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
+                data = json.load(f)
+            return {**DEFAULT_CONFIG, **data}
+        except Exception:
+            pass
+    return dict(DEFAULT_CONFIG)
+
+
+def save_config(data: dict) -> dict:
+    """
+    Fusionne `data` avec la config existante et l'écrit sur disque.
+    Écriture atomique (fichier temporaire + os.replace) pour éviter
+    la corruption de config.json en cas de crash pendant l'écriture.
+    """
+    merged = {**load_config(), **data}
+
+    DATA_DIR.mkdir(parents=True, exist_ok=True)
+    tmp_path = CONFIG_FILE.with_suffix(".json.tmp")
+    with open(tmp_path, "w", encoding="utf-8") as f:
+        json.dump(merged, f, indent=2, ensure_ascii=False)
+    os.replace(tmp_path, CONFIG_FILE)
+
+    return merged
# (diff du fichier suivant)
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# (index — ignorable)
index e431eb2..6440be1 100644
# (avant — fichier suivant)
--- a/nicsoft/web/alchess.py
# (après — fichier suivant)
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 242 (6 ligne(s)) dans l'ancienne version → ligne 242 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -242,6 +242,8 @@ def main():
                 gm.launch_exercices()
             elif atype == "mode" and action.get("value") == "outils_exercices":
                 set_app_state("outils_exercices")
+            elif atype == "mode" and action.get("value") == "parametres":
+                set_app_state("parametres")
             elif atype == "start_exercice":
                 gm.start_exercice(action)
             elif atype == "start_drill":
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index 0176cc0..d16e975 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 603 (6 ligne(s)) dans l'ancienne version → ligne 603 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -603,6 +603,26 @@ def on_basket_load(data):
         emit("basket_load_result", {"pgn": "", "label": ""})
 
 
+# ── Paramètres (config.json centralisé) ──────────────────────────────────────
+
+@socketio.on("config_get")
+def on_config_get(_data):
+    """Retourne la config courante (y compris champs LLM/TTS)."""
+    from nicsoft.core.config_manager import load_config
+    emit("config_data", load_config())
+
+
+@socketio.on("config_save")
+def on_config_save(data):
+    """Fusionne et sauvegarde la config reçue du navigateur."""
+    from nicsoft.core.config_manager import save_config
+    try:
+        save_config(data or {})
+        emit("config_saved", {"ok": True})
+    except Exception as e:
+        emit("config_saved", {"ok": False, "error": str(e)})
+
+
 # ── Thread de dispatch des événements ────────────────────────────────────────
 
 def _dispatch_loop():
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index a05bc18..5ef57ec 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 799 (6 ligne(s)) dans l'ancienne version → ligne 799 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -799,6 +799,10 @@ socket.on("app_state", (data) => {
   const outilsEl = document.getElementById("screen-outils-exercices");
   if (outilsEl) outilsEl.style.display = data.state === "outils_exercices" ? "flex" : "none";
 
+  // Paramètres
+  const parametresEl = document.getElementById("screen-parametres");
+  if (parametresEl) parametresEl.style.display = data.state === "parametres" ? "flex" : "none";
+
   if (data.state === "exercices") {
     _exLaunching = false;  // reset au retour sur l'écran de sélection
     if (data.ouvertures) {
# ── Zone modifiée : ligne 5984 (3 ligne(s)) dans l'ancienne version → ligne 5988 (50 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5984,3 +5988,50 @@ socket.on("rodent_download_result", (data) => {
     if (btn) btn.disabled = false;
   });
 });
+
+// ── Panneau Paramètres (LLM + TTS) ───────────────────────────────────────────
+
+socket.on("app_state", (data) => {
+  if (data.state === "parametres") {
+    socket.emit("config_get", {});
+  }
+});
+
+socket.on("config_data", (data) => {
+  if (!data) return;
+  const provider = document.getElementById("param-llm-provider");
+  const apiKey   = document.getElementById("param-llm-api-key");
+  const model    = document.getElementById("param-llm-model");
+  const ttsOn    = document.getElementById("param-tts-enabled");
+  const ttsRate  = document.getElementById("param-tts-rate");
+  const ttsRateVal = document.getElementById("param-tts-rate-val");
+  if (provider) provider.value = data.llm_provider || "claude";
+  if (apiKey)   apiKey.value   = data.llm_api_key || "";
+  if (model)    model.value    = data.llm_model || "";
+  if (ttsOn)    ttsOn.checked  = !!data.tts_enabled;
+  if (ttsRate)  ttsRate.value  = data.tts_rate || 150;
+  if (ttsRateVal) ttsRateVal.textContent = data.tts_rate || 150;
+});
+
+function parametresSave() {
+  const provider = document.getElementById("param-llm-provider");
+  const apiKey   = document.getElementById("param-llm-api-key");
+  const model    = document.getElementById("param-llm-model");
+  const ttsOn    = document.getElementById("param-tts-enabled");
+  const ttsRate  = document.getElementById("param-tts-rate");
+  socket.emit("config_save", {
+    llm_provider: provider ? provider.value : "claude",
+    llm_api_key:  apiKey ? apiKey.value : "",
+    llm_model:    model ? model.value : "",
+    tts_enabled:  ttsOn ? ttsOn.checked : false,
+    tts_rate:     ttsRate ? parseInt(ttsRate.value, 10) : 150,
+  });
+}
+
+socket.on("config_saved", (data) => {
+  if (data && data.ok) {
+    afficherToast(t("parametres.toast.enregistre"), "success");
+  } else {
+    afficherToast(t("parametres.toast.erreur"), "warning");
+  }
+});
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index 4d849ea..a8645f7 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 30 (6 ligne(s)) dans l'ancienne version → ligne 30 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -30,6 +30,7 @@
   "menu.btn.exercices":        "📚 Übungen",
   "menu.btn.retranscrire":     "✏️ Mitschreiben",
   "menu.btn.outils":           "🛠️ Übungs-Tools",
+  "menu.btn.parametres":       "⚙ Einstellungen",
   "menu.btn.reconnect":        "🔌 Brett neu verbinden",
   "menu.btn.connecter":        "⟳ Verbinden",
   "menu.btn.debloquer":        "⟳ Schaltflächen entsperren",
# ── Zone modifiée : ligne 51 (6 ligne(s)) dans l'ancienne version → ligne 52 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -51,6 +52,7 @@
   "menu.desc.exercices":       "Eröffnungen mit einem Großmeister-Buch trainieren. Züge auf dem Brett spielen — das Buch antwortet und führt durch die Theorie.",
   "menu.desc.retrans":         "Eine auf Papier gespielte Partie mitschreiben. Züge auf dem virtuellen Brett eingeben und das PGN exportieren.",
   "menu.desc.outils":          "PGN-Linien importieren, SAN → UCI konvertieren und den Eröffnungskatalog verwalten.",
+  "menu.desc.parametres":      "LLM-Zugang (API-Schlüssel) und Sprachausgabe (TTS) konfigurieren.",
   "menu.autoupdate.label":     "Automatische Updates",
   "menu.autoupdate.warning":   "Automatische Updates sind deaktiviert. Sie erhalten weder Sicherheitskorrekturen noch neue Funktionen.",
 
# ── Zone modifiée : ligne 242 (6 ligne(s)) dans l'ancienne version → ligne 244 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -242,6 +244,22 @@
   "modal.blancs_abandonnent":  "⚐ Weiß gibt auf",
   "modal.noirs_abandonnent":   "⚐ Schwarz gibt auf",
 
+  "parametres.titre":                 "⚙ Einstellungen",
+  "parametres.llm.titre":             "🤖 LLM-Assistent",
+  "parametres.llm.desc":              "API-Schlüssel, der lokal für Funktionen verwendet wird, die auf einem Sprachmodell basieren.",
+  "parametres.llm.provider":          "Anbieter",
+  "parametres.llm.provider_claude":   "Claude (Anthropic)",
+  "parametres.llm.provider_openai":   "OpenAI",
+  "parametres.llm.api_key":           "API-Schlüssel",
+  "parametres.llm.model":             "Modell (optional)",
+  "parametres.llm.model_placeholder": "claude-sonnet-4-6",
+  "parametres.tts.titre":             "🔊 Sprachausgabe",
+  "parametres.tts.activer":           "Sprachausgabe aktivieren",
+  "parametres.tts.debit":             "Geschwindigkeit (Wörter pro Minute)",
+  "parametres.enregistrer":           "💾 Speichern",
+  "parametres.toast.enregistre":      "Einstellungen gespeichert",
+  "parametres.toast.erreur":          "Fehler beim Speichern der Einstellungen",
+
   "outils.titre":              "🛠️ Übungs-Tools",
   "outils.import_pgn.titre":   "📥 Meine PGN-Linien importieren",
   "outils.import_pgn.desc":    "Eine oder mehrere .pgn-Dateien in Ihre persönlichen Übungen importieren (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index bae5e10..1ae7b40 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 30 (6 ligne(s)) dans l'ancienne version → ligne 30 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -30,6 +30,7 @@
   "menu.btn.exercices":        "📚 Exercises",
   "menu.btn.retranscrire":     "✏️ Transcribe",
   "menu.btn.outils":           "🛠️ Exercise Tools",
+  "menu.btn.parametres":       "⚙ Settings",
   "menu.btn.reconnect":        "🔌 Reconnect board",
   "menu.btn.connecter":        "⟳ Connect",
   "menu.btn.debloquer":        "⟳ Unlock buttons",
# ── Zone modifiée : ligne 51 (6 ligne(s)) dans l'ancienne version → ligne 52 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -51,6 +52,7 @@
   "menu.desc.exercices":       "Train your openings with a Grandmaster book. Play your moves on the physical board — the book responds and guides you through the theory.",
   "menu.desc.retrans":         "Transcribe a game played on paper. Enter moves on the virtual board and export the PGN.",
   "menu.desc.outils":          "Import your PGN lines, convert SAN → UCI and manage the openings catalogue.",
+  "menu.desc.parametres":      "Configure LLM access (API key) and text-to-speech (TTS).",
   "menu.autoupdate.label":     "Automatic updates",
   "menu.autoupdate.warning":   "Automatic updates are disabled. You will not receive security fixes or new features.",
 
# ── Zone modifiée : ligne 242 (6 ligne(s)) dans l'ancienne version → ligne 244 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -242,6 +244,22 @@
   "modal.blancs_abandonnent":  "⚐ White resigns",
   "modal.noirs_abandonnent":   "⚐ Black resigns",
 
+  "parametres.titre":                 "⚙ Settings",
+  "parametres.llm.titre":             "🤖 LLM assistant",
+  "parametres.llm.desc":              "API key used locally for features relying on a language model.",
+  "parametres.llm.provider":          "Provider",
+  "parametres.llm.provider_claude":   "Claude (Anthropic)",
+  "parametres.llm.provider_openai":   "OpenAI",
+  "parametres.llm.api_key":           "API key",
+  "parametres.llm.model":             "Model (optional)",
+  "parametres.llm.model_placeholder": "claude-sonnet-4-6",
+  "parametres.tts.titre":             "🔊 Text-to-speech",
+  "parametres.tts.activer":           "Enable text-to-speech",
+  "parametres.tts.debit":             "Rate (words per minute)",
+  "parametres.enregistrer":           "💾 Save",
+  "parametres.toast.enregistre":      "Settings saved",
+  "parametres.toast.erreur":          "Error while saving settings",
+
   "outils.titre":              "🛠️ Exercise Tools",
   "outils.import_pgn.titre":   "📥 Import my PGN lines",
   "outils.import_pgn.desc":    "Select one or more .pgn files to import into your personal exercises (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index 0a926d7..08cfe23 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 30 (6 ligne(s)) dans l'ancienne version → ligne 30 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -30,6 +30,7 @@
   "menu.btn.exercices":        "📚 Exercices",
   "menu.btn.retranscrire":     "✏️ Retranscrire",
   "menu.btn.outils":           "🛠️ Outils Exercices",
+  "menu.btn.parametres":       "⚙ Paramètres",
   "menu.btn.reconnect":        "🔌 Reconnecter l'échiquier",
   "menu.btn.connecter":        "⟳ Connecter",
   "menu.btn.debloquer":        "⟳ Débloquer les boutons",
# ── Zone modifiée : ligne 51 (6 ligne(s)) dans l'ancienne version → ligne 52 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -51,6 +52,7 @@
   "menu.desc.exercices":       "Entraînez-vous aux ouvertures avec un livre de Grands Maîtres. Jouez vos coups sur l'échiquier physique — le livre répond et vous guide dans la théorie.",
   "menu.desc.retrans":         "Retranscrivez une partie jouée sur papier. Saisissez les coups sur l'échiquier virtuel et exportez le PGN.",
   "menu.desc.outils":          "Importez vos lignes PGN, convertissez SAN → UCI et gérez le catalogue d'ouvertures.",
+  "menu.desc.parametres":      "Configurez l'accès LLM (clé API) et la synthèse vocale (TTS).",
   "menu.autoupdate.label":     "Mises à jour automatiques",
   "menu.autoupdate.warning":   "Les mises à jour automatiques sont désactivées. Vous ne recevrez pas les correctifs de sécurité ni les nouvelles fonctionnalités.",
 
# ── Zone modifiée : ligne 242 (6 ligne(s)) dans l'ancienne version → ligne 244 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -242,6 +244,22 @@
   "modal.blancs_abandonnent":  "⚐ Blancs abandonnent",
   "modal.noirs_abandonnent":   "⚐ Noirs abandonnent",
 
+  "parametres.titre":                 "⚙ Paramètres",
+  "parametres.llm.titre":             "🤖 Assistant LLM",
+  "parametres.llm.desc":              "Clé API utilisée en local pour les fonctionnalités s'appuyant sur un modèle de langage.",
+  "parametres.llm.provider":          "Fournisseur",
+  "parametres.llm.provider_claude":   "Claude (Anthropic)",
+  "parametres.llm.provider_openai":   "OpenAI",
+  "parametres.llm.api_key":           "Clé API",
+  "parametres.llm.model":             "Modèle (optionnel)",
+  "parametres.llm.model_placeholder": "claude-sonnet-4-6",
+  "parametres.tts.titre":             "🔊 Synthèse vocale",
+  "parametres.tts.activer":           "Activer la synthèse vocale",
+  "parametres.tts.debit":             "Débit (mots par minute)",
+  "parametres.enregistrer":           "💾 Enregistrer",
+  "parametres.toast.enregistre":      "Paramètres enregistrés",
+  "parametres.toast.erreur":          "Erreur lors de l'enregistrement des paramètres",
+
   "outils.titre":              "🛠️ Outils Exercices",
   "outils.import_pgn.titre":   "📥 Importer mes lignes PGN",
   "outils.import_pgn.desc":    "Sélectionnez un ou plusieurs fichiers .pgn pour les importer dans vos exercices personnels (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index e0e6a36..831be0f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 190 (6 ligne(s)) dans l'ancienne version → ligne 190 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -190,6 +190,11 @@
         <div class="menu-btn-desc" id="desc-outils" data-i18n="menu.desc.outils">Importez vos lignes PGN, convertissez SAN&nbsp;→&nbsp;UCI et gérez le catalogue d'ouvertures.</div>
       </div>
 
+      <div class="menu-btn-wrap">
+        <button class="menu-btn menu-btn-secondary" onclick="sendAction({type:'mode', value:'parametres'})" data-i18n="menu.btn.parametres">⚙ Paramètres</button>
+        <div class="menu-btn-desc" id="desc-parametres" data-i18n="menu.desc.parametres">Configurez l'accès LLM (clé API) et la synthèse vocale (TTS).</div>
+      </div>
+
     </div><!-- fin colonne Outils -->
 
   </div><!-- fin menu-grid -->
# ── Zone modifiée : ligne 1515 (6 ligne(s)) dans l'ancienne version → ligne 1520 (67 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1515,6 +1520,67 @@
 </div>
 
 
+<!-- ── Écran Paramètres ── -->
+<div id="screen-parametres" style="display:none; flex-direction:column; align-items:center; padding:24px; gap:20px; overflow-y:auto; width:100%;">
+
+  <div style="width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
+    <h2 style="margin:0; color:#1a2a3a; font-size:1.4rem;" data-i18n="parametres.titre">⚙ Paramètres</h2>
+    <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+  </div>
+
+  <!-- Assistant LLM -->
+  <div class="outil-card" style="width:100%; max-width:860px;">
+    <div class="outil-card-header">
+      <span class="outil-title" data-i18n="parametres.llm.titre">🤖 Assistant LLM</span>
+    </div>
+    <p class="outil-desc" data-i18n="parametres.llm.desc">Clé API utilisée en local pour les fonctionnalités s'appuyant sur un modèle de langage.</p>
+
+    <div style="display:flex; flex-direction:column; gap:12px;">
+      <div class="add-field">
+        <label class="add-label" for="param-llm-provider" data-i18n="parametres.llm.provider">Fournisseur</label>
+        <select id="param-llm-provider" class="add-input">
+          <option value="claude" data-i18n="parametres.llm.provider_claude">Claude (Anthropic)</option>
+          <option value="openai" data-i18n="parametres.llm.provider_openai">OpenAI</option>
+        </select>
+      </div>
+
+      <div class="add-field">
+        <label class="add-label" for="param-llm-api-key" data-i18n="parametres.llm.api_key">Clé API</label>
+        <input type="password" id="param-llm-api-key" class="add-input" autocomplete="off">
+      </div>
+
+      <div class="add-field">
+        <label class="add-label" for="param-llm-model" data-i18n="parametres.llm.model">Modèle (optionnel)</label>
+        <input type="text" id="param-llm-model" class="add-input" placeholder="claude-sonnet-4-6" data-i18n-placeholder="parametres.llm.model_placeholder">
+      </div>
+    </div>
+  </div>
+
+  <!-- Synthèse vocale (TTS) -->
+  <div class="outil-card" style="width:100%; max-width:860px;">
+    <div class="outil-card-header">
+      <span class="outil-title" data-i18n="parametres.tts.titre">🔊 Synthèse vocale</span>
+    </div>
+
+    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
+      <input type="checkbox" id="param-tts-enabled" style="width:16px; height:16px; cursor:pointer; accent-color:#e94560;">
+      <label for="param-tts-enabled" data-i18n="parametres.tts.activer">Activer la synthèse vocale</label>
+    </div>
+
+    <label class="add-label" for="param-tts-rate" data-i18n="parametres.tts.debit">Débit (mots par minute)</label>
+    <div style="display:flex; align-items:center; gap:10px;">
+      <input type="range" id="param-tts-rate" min="80" max="300" value="150" step="10" style="width:200px; accent-color:#e94560;" oninput="document.getElementById('param-tts-rate-val').textContent = this.value">
+      <span id="param-tts-rate-val">150</span>
+    </div>
+  </div>
+
+  <div style="width:100%; max-width:860px; display:flex; gap:10px;">
+    <button class="btn btn-continuer" onclick="parametresSave()" data-i18n="parametres.enregistrer">💾 Enregistrer</button>
+  </div>
+
+</div>
+
+
 <!-- ── Écran connexion échiquier ── -->
 <div id="screen-connecting" style="display:none; flex:1; flex-direction:column; align-items:center; justify-content:center; gap:20px;">
   <div style="font-size:2rem;">♜</div>
