f6ef420

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f6ef420
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 18:23:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: Opening Explorer — complète toggle TTS écran lecteur (issue #147)
    
    Le HTML (bouton #expl-tts-toggle) et le CSS (layout inversé, hover
    tableau coups) étaient déjà en place, ainsi que la langue de la voix
    (tts_engine.py/server.py) et les coups suivants (explorer_session.py).
    Il manquait la logique JS : variable _explTtsEnabled, mise à jour de
    l'icône/tooltip (explUpdateTtsToggle) et bascule + config_save au clic
    (explToggleTts). Ajout clés i18n opening_explorer.tts.on/off (FR/EN/DE).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 833a93a..34b6d6e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6053 (6 ligne(s)) dans l'ancienne version → ligne 6053 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6053,6 +6053,7 @@ let _explEndOfLine   = false;
 let _explFlipped     = false;  // true = noirs en bas
 let _explFlippedBuilt = null;
 let _explHasApiKey   = false;
+let _explTtsEnabled  = false;
 
 function explUpdateChatAvailability() {
   const input   = document.getElementById("explorer-chat-input");
# ── Zone modifiée : ligne 6067 (6 ligne(s)) dans l'ancienne version → ligne 6068 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6067,6 +6068,19 @@ function explUpdateChatAvailability() {
   if (sendBtn) sendBtn.disabled = !_explHasApiKey;
 }
 
+function explUpdateTtsToggle() {
+  const btn = document.getElementById("expl-tts-toggle");
+  if (!btn) return;
+  btn.textContent = _explTtsEnabled ? "🔊" : "🔇";
+  btn.title = t(_explTtsEnabled ? "opening_explorer.tts.on" : "opening_explorer.tts.off");
+}
+
+function explToggleTts() {
+  _explTtsEnabled = !_explTtsEnabled;
+  explUpdateTtsToggle();
+  socket.emit("config_save", { tts_enabled: _explTtsEnabled });
+}
+
 socket.on("app_state", (data) => {
   const selEl  = document.getElementById("screen-opening-explorer-select");
   const playEl = document.getElementById("screen-opening-explorer-play");
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index c6ea500..b8fdc29 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 254 (6 ligne(s)) dans l'ancienne version → ligne 254 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -254,6 +254,8 @@
   "opening_explorer.chat.placeholder": "Stellen Sie eine Frage...",
   "opening_explorer.chat.envoyer": "Senden",
   "opening_explorer.chat.no_api": "Konfigurieren Sie einen API-Schlüssel in den Einstellungen",
+  "opening_explorer.tts.on": "🔊 Sprache aktiviert",
+  "opening_explorer.tts.off": "🔇 Sprache deaktiviert",
   "outils.titre": "🛠️ Übungs-Tools",
   "outils.import_pgn.titre": "📥 Meine PGN-Linien importieren",
   "outils.import_pgn.desc": "Eine oder mehrere .pgn-Dateien in Ihre persönlichen Übungen importieren (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index da9bc7e..fcc1cea 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 254 (6 ligne(s)) dans l'ancienne version → ligne 254 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -254,6 +254,8 @@
   "opening_explorer.chat.placeholder": "Ask a question...",
   "opening_explorer.chat.envoyer": "Send",
   "opening_explorer.chat.no_api": "Configure an API key in Settings to enable chat",
+  "opening_explorer.tts.on": "🔊 Voice enabled",
+  "opening_explorer.tts.off": "🔇 Voice disabled",
   "outils.titre": "🛠️ Exercise Tools",
   "outils.import_pgn.titre": "📥 Import my PGN lines",
   "outils.import_pgn.desc": "Select one or more .pgn files to import into your personal exercises (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index 554b3ce..b729664 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 254 (6 ligne(s)) dans l'ancienne version → ligne 254 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -254,6 +254,8 @@
   "opening_explorer.chat.placeholder": "Posez une question...",
   "opening_explorer.chat.envoyer": "Envoyer",
   "opening_explorer.chat.no_api": "Configurez une clé API dans Paramètres pour activer le chat",
+  "opening_explorer.tts.on": "🔊 Voix activée",
+  "opening_explorer.tts.off": "🔇 Voix désactivée",
   "outils.titre": "🛠️ Outils Exercices",
   "outils.import_pgn.titre": "📥 Importer mes lignes PGN",
   "outils.import_pgn.desc": "Sélectionnez un ou plusieurs fichiers .pgn pour les importer dans vos exercices personnels (<em>mes_lignes.json</em>).",
