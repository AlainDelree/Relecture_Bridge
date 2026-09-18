0ccf4f9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0ccf4f9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 10:48:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: désactive Suivant/Précédent pendant la lecture TTS explorer (issue #171)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 76aee34..8d89454 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/server.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 658 (7 ligne(s)) dans l'ancienne version → ligne 658 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -658,7 +658,11 @@ def _emit_explorer_explanation(sid, state, language):
     )
     if expl:
         socketio.emit("explorer_explanation", {"text": expl, "arrows": [list(a) for a in arrows]}, to=sid)
+        if cfg.get("tts_enabled", False):
+            socketio.emit("explorer_tts_start", {}, to=sid)
         tts_ok = speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
+        if cfg.get("tts_enabled", False):
+            socketio.emit("explorer_tts_end", {}, to=sid)
         if cfg.get("tts_enabled") and not tts_ok:
             socketio.emit("explorer_tts_fallback", {"text": expl}, to=sid)
 
# ── Zone modifiée : ligne 673 (7 ligne(s)) dans l'ancienne version → ligne 677 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -673,7 +677,11 @@ def _emit_explorer_chat_response(sid, question, state, language):
     response, arrows = get_chat_response(question, state, language, cfg)
     if response:
         socketio.emit("explorer_chat_response", {"text": response, "arrows": [list(a) for a in arrows]}, to=sid)
+        if cfg.get("tts_enabled", False):
+            socketio.emit("explorer_tts_start", {}, to=sid)
         tts_ok = speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
+        if cfg.get("tts_enabled", False):
+            socketio.emit("explorer_tts_end", {}, to=sid)
         if cfg.get("tts_enabled") and not tts_ok:
             socketio.emit("explorer_tts_fallback", {"text": response}, to=sid)
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index c15c34a..dba904a 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6299 (6 ligne(s)) dans l'ancienne version → ligne 6299 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6299,6 +6299,16 @@ socket.on("explorer_tts_fallback", (data) => {
   if (data && data.text) explSpeak(data.text);
 });
 
+function explSetNavDisabled(disabled) {
+  const prev = document.getElementById("expl-btn-prev");
+  const next = document.getElementById("expl-btn-next");
+  if (prev) { prev.disabled = disabled; prev.style.opacity = disabled ? "0.4" : "1"; }
+  if (next) { next.disabled = disabled; next.style.opacity = disabled ? "0.4" : "1"; }
+}
+
+socket.on("explorer_tts_start", () => { explSetNavDisabled(true); });
+socket.on("explorer_tts_end",   () => { explSetNavDisabled(false); });
+
 function explRenderMovesTable(data) {
   const wrap = document.getElementById("explorer-moves-table");
   if (!wrap) return;
# ── Zone modifiée : ligne 6351 (6 ligne(s)) dans l'ancienne version → ligne 6361 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6351,6 +6361,7 @@ function explRenderMovesTable(data) {
 socket.on("explorer_state", (data) => {
   if (!data) return;
   window.speechSynthesis.cancel();
+  explSetNavDisabled(false);
   if (data.error) {
     afficherToast(t("opening_explorer.erreur_chargement"), "warning");
     return;
