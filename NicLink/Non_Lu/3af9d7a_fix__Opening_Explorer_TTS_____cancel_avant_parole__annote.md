3af9d7a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3af9d7a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 19:57:53 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: Opening Explorer TTS — cancel avant parole + strip Markdown (issue #150)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3af0fa8..c590287 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/server.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 639 (7 ligne(s)) dans l'ancienne version → ligne 639 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -639,7 +639,6 @@ def _emit_explorer_explanation(sid, state, language):
     """Génère l'explication LLM du coup en arrière-plan et l'émet au client concerné."""
     from nicsoft.modes.opening_explorer.llm_explainer import get_explanation
     from nicsoft.core.config_manager import load_config
-    from nicsoft.modes.opening_explorer.tts_engine import speak
 
     if not state or state.get("error") or not state.get("move_san"):
         return
# ── Zone modifiée : ligne 657 (20 ligne(s)) dans l'ancienne version → ligne 656 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -657,20 +656,17 @@ def _emit_explorer_explanation(sid, state, language):
     )
     if expl:
         socketio.emit("explorer_explanation", {"text": expl, "arrows": [list(a) for a in arrows]}, to=sid)
-        speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
 
 
 def _emit_explorer_chat_response(sid, question, state, language):
     """Génère la réponse du LLM à une question libre en arrière-plan et l'émet au client."""
     from nicsoft.modes.opening_explorer.llm_explainer import get_chat_response
     from nicsoft.core.config_manager import load_config
-    from nicsoft.modes.opening_explorer.tts_engine import speak
 
     cfg = load_config()
     response, arrows = get_chat_response(question, state, language, cfg)
     if response:
         socketio.emit("explorer_chat_response", {"text": response, "arrows": [list(a) for a in arrows]}, to=sid)
-        speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
 
 
 @socketio.on("explorer_load")
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index d2e50d5..e04ccd7 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6153 (6 ligne(s)) dans l'ancienne version → ligne 6153 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6153,6 +6153,7 @@ function explRenderMesLignes(groupes) {
 }
 
 function explLoad(sourceType, openingId) {
+  window.speechSynthesis.cancel();
   const history = document.getElementById("explorer-chat-history");
   if (history) history.innerHTML = "";
   const movesTable = document.getElementById("explorer-moves-table");
# ── Zone modifiée : ligne 6236 (6 ligne(s)) dans l'ancienne version → ligne 6237 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6236,6 +6237,30 @@ function explDrawArrows(arrows) {
   }
 }
 
+function stripMarkdownForTts(text) {
+  if (!text) return "";
+  return text
+    .replace(/#{1,6}\s*/g, "")       // titres #
+    .replace(/\*\*(.+?)\*\*/g, "$1") // gras **
+    .replace(/__(.+?)__/g, "$1")     // gras __
+    .replace(/\*(.+?)\*/g, "$1")     // italique *
+    .replace(/_(.+?)_/g, "$1")       // italique _
+    .replace(/\n+/g, " ")            // sauts de ligne → espace
+    .trim();
+}
+
+function explSpeak(text) {
+  if (!_explTtsEnabled) return;
+  const clean = stripMarkdownForTts(text);
+  if (!clean) return;
+  window.speechSynthesis.cancel();
+  const utterance = new SpeechSynthesisUtterance(clean);
+  utterance.lang = i18n.locale() === "fr" ? "fr-FR"
+                 : i18n.locale() === "de" ? "de-DE" : "en-GB";
+  utterance.rate = 1.0;
+  window.speechSynthesis.speak(utterance);
+}
+
 function markdownToHtml(text) {
   if (!text) return "";
   let h = text
# ── Zone modifiée : ligne 6255 (6 ligne(s)) dans l'ancienne version → ligne 6280 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6255,6 +6280,7 @@ socket.on("explorer_explanation", (data) => {
   if (el) el.innerHTML = markdownToHtml(data && data.text);
   explClearArrows();
   if (data && data.arrows) explDrawArrows(data.arrows);
+  explSpeak(data && data.text);
 });
 
 socket.on("explorer_chat_response", (data) => {
# ── Zone modifiée : ligne 6267 (6 ligne(s)) dans l'ancienne version → ligne 6293 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6267,6 +6293,7 @@ socket.on("explorer_chat_response", (data) => {
   history.scrollTop = history.scrollHeight;
   explClearArrows();
   if (data.arrows) explDrawArrows(data.arrows);
+  explSpeak(data.text);
 });
 
 function explRenderMovesTable(data) {
# ── Zone modifiée : ligne 6320 (6 ligne(s)) dans l'ancienne version → ligne 6347 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6320,6 +6347,7 @@ function explRenderMovesTable(data) {
 
 socket.on("explorer_state", (data) => {
   if (!data) return;
+  window.speechSynthesis.cancel();
   if (data.error) {
     afficherToast(t("opening_explorer.erreur_chargement"), "warning");
     return;
