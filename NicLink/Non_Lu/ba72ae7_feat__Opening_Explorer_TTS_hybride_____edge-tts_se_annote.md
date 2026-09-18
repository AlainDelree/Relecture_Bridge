ba72ae7

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ba72ae7
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 20:53:55 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: Opening Explorer TTS hybride — edge-tts serveur si internet, Web Speech API navigateur sinon (issue #155, suite #154)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index cccba12..3229660 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 1 (8 ligne(s)) dans l'ancienne version → ligne 1 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,8 +1,11 @@
 """
 nicsoft/modes/opening_explorer/tts_engine.py — NicLink
-Synthèse vocale des explications Opening Explorer via edge-tts (voix
-neuronales Microsoft, internet requis), avec fallback automatique sur
-espeak-ng en subprocess direct si edge-tts échoue (pas d'internet, etc.).
+Synthèse vocale des explications Opening Explorer, hybride :
+si internet est disponible, edge-tts (voix neuronales Microsoft) parle
+côté serveur ; sinon speak() ne fait rien et retourne False, laissant
+le navigateur relayer via Web Speech API (voix système, meilleure
+qu'espeak-ng sur Windows/Mac). espeak-ng reste disponible en dernier
+recours mais n'est plus appelé automatiquement par speak().
 pyttsx3 abandonné : le GC détruisait l'engine pendant le callback espeak,
 provoquant des ReferenceError après un ou deux mots.
 """
# ── Zone modifiée : ligne 24 (6 ligne(s)) dans l'ancienne version → ligne 27 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,6 +27,24 @@ VOICE_MAP_EDGE = {
 VOICE_MAP_ESPEAK = {"fr": "fr", "en": "en", "de": "de"}
 
 
+def check_internet() -> bool:
+    """Test rapide (2s max) de connectivité, pour décider edge-tts vs Web Speech API."""
+    try:
+        import urllib.request
+        urllib.request.urlopen("https://api.edge-tts.com", timeout=2)
+        return True
+    except Exception:
+        pass
+    # Fallback : ping un DNS public
+    try:
+        import socket
+        socket.setdefaulttimeout(2)
+        socket.socket().connect(("8.8.8.8", 53))
+        return True
+    except Exception:
+        return False
+
+
 def _speak_edge(text: str, rate: int, language: str) -> bool:
     """Essaie de parler via edge-tts. Retourne True si succès, False sinon."""
     try:
# ── Zone modifiée : ligne 67 (14 ligne(s)) dans l'ancienne version → ligne 88 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -67,14 +88,16 @@ def _speak_espeak(text: str, rate: int, language: str) -> None:
         logger.warning(f"[TTS] espeak-ng échoué : {e}")
 
 
-def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr") -> None:
-    """Prononce `text` à voix haute si `enabled`, dans la langue `language`.
-    Essaie d'abord edge-tts (voix neuronale, internet requis) puis bascule
-    automatiquement sur espeak-ng si edge-tts échoue. Bloquant — à appeler
-    depuis un thread daemon, jamais depuis le thread principal.
-    Erreur silencieuse (ni edge-tts ni espeak-ng disponibles, etc.).
+def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr") -> bool:
+    """Prononce `text` à voix haute côté serveur si `enabled` et si internet
+    est disponible (edge-tts, voix neuronale). Bloquant — à appeler depuis un
+    thread daemon, jamais depuis le thread principal.
+    Retourne True si edge-tts a parlé, False sinon (pas d'internet ou échec
+    edge-tts) — dans ce cas l'appelant doit basculer sur le Web Speech API
+    côté navigateur (pas d'espeak-ng comme fallback serveur).
     """
     if not enabled or not text:
-        return
-    if not _speak_edge(text, rate, language):
-        _speak_espeak(text, rate, language)
+        return False
+    if not check_internet():
+        return False
+    return _speak_edge(text, rate, language)
# (diff du fichier suivant)
diff --git a/nicsoft/web/server.py b/nicsoft/web/server.py
# (index — ignorable)
index c590287..0ff52cf 100644
# (avant — fichier suivant)
--- a/nicsoft/web/server.py
# (après — fichier suivant)
+++ b/nicsoft/web/server.py
# ── Zone modifiée : ligne 639 (6 ligne(s)) dans l'ancienne version → ligne 639 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -639,6 +639,7 @@ def _emit_explorer_explanation(sid, state, language):
     """Génère l'explication LLM du coup en arrière-plan et l'émet au client concerné."""
     from nicsoft.modes.opening_explorer.llm_explainer import get_explanation
     from nicsoft.core.config_manager import load_config
+    from nicsoft.modes.opening_explorer.tts_engine import speak
 
     if not state or state.get("error") or not state.get("move_san"):
         return
# ── Zone modifiée : ligne 656 (17 ligne(s)) dans l'ancienne version → ligne 657 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -656,17 +657,24 @@ def _emit_explorer_explanation(sid, state, language):
     )
     if expl:
         socketio.emit("explorer_explanation", {"text": expl, "arrows": [list(a) for a in arrows]}, to=sid)
+        tts_ok = speak(expl, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
+        if cfg.get("tts_enabled") and not tts_ok:
+            socketio.emit("explorer_tts_fallback", {"text": expl}, to=sid)
 
 
 def _emit_explorer_chat_response(sid, question, state, language):
     """Génère la réponse du LLM à une question libre en arrière-plan et l'émet au client."""
     from nicsoft.modes.opening_explorer.llm_explainer import get_chat_response
     from nicsoft.core.config_manager import load_config
+    from nicsoft.modes.opening_explorer.tts_engine import speak
 
     cfg = load_config()
     response, arrows = get_chat_response(question, state, language, cfg)
     if response:
         socketio.emit("explorer_chat_response", {"text": response, "arrows": [list(a) for a in arrows]}, to=sid)
+        tts_ok = speak(response, rate=cfg.get("tts_rate", 150), enabled=cfg.get("tts_enabled", False), language=language)
+        if cfg.get("tts_enabled") and not tts_ok:
+            socketio.emit("explorer_tts_fallback", {"text": response}, to=sid)
 
 
 @socketio.on("explorer_load")
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index e04ccd7..67ec5b5 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6280 (7 ligne(s)) dans l'ancienne version → ligne 6280 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6280,7 +6280,6 @@ socket.on("explorer_explanation", (data) => {
   if (el) el.innerHTML = markdownToHtml(data && data.text);
   explClearArrows();
   if (data && data.arrows) explDrawArrows(data.arrows);
-  explSpeak(data && data.text);
 });
 
 socket.on("explorer_chat_response", (data) => {
# ── Zone modifiée : ligne 6293 (7 ligne(s)) dans l'ancienne version → ligne 6292 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6293,7 +6292,10 @@ socket.on("explorer_chat_response", (data) => {
   history.scrollTop = history.scrollHeight;
   explClearArrows();
   if (data.arrows) explDrawArrows(data.arrows);
-  explSpeak(data.text);
+});
+
+socket.on("explorer_tts_fallback", (data) => {
+  if (data && data.text) explSpeak(data.text);
 });
 
 function explRenderMovesTable(data) {
