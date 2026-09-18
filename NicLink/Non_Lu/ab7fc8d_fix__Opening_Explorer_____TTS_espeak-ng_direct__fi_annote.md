ab7fc8d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ab7fc8d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 19:06:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: Opening Explorer — TTS espeak-ng direct (fin pyttsx3) + rendu Markdown explications LLM (issue #149)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8c345db..8eee0d6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 1 (11 ligne(s)) dans l'ancienne version → ligne 1 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,11 +1,12 @@
 """
 nicsoft/modes/opening_explorer/tts_engine.py — NicLink
-Synthèse vocale des explications Opening Explorer via pyttsx3 (backend
-espeak-ng sur Linux). Aucun singleton global : pyttsx3 est instable en
-mode multi-thread si le moteur est partagé entre appels.
+Synthèse vocale des explications Opening Explorer via espeak-ng en
+subprocess direct. pyttsx3 abandonné : le GC détruisait l'engine pendant
+le callback espeak, provoquant des ReferenceError après un ou deux mots.
 """
 
 import logging
+import subprocess
 
 logger = logging.getLogger("niclink.opening_explorer.tts")
 
# ── Zone modifiée : ligne 17 (21 ligne(s)) dans l'ancienne version → ligne 18 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -17,21 +18,16 @@ def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr
     """Prononce `text` à voix haute si `enabled`, dans la langue `language`
     (voix espeak-ng correspondante si disponible). Bloquant — à appeler
     depuis un thread daemon, jamais depuis le thread principal.
-    Erreur silencieuse (moteur TTS absent, espeak-ng manquant, etc.).
+    Erreur silencieuse (espeak-ng manquant, etc.).
     """
     if not enabled or not text:
         return
+    lang = VOICE_MAP.get(language, "fr")
     try:
-        import pyttsx3
-        engine = pyttsx3.init()
-        engine.setProperty("rate", rate)
-        lang = VOICE_MAP.get(language, "fr")
-        voices = engine.getProperty("voices")
-        for v in voices:
-            if lang in v.id.lower() or lang in (v.name or "").lower():
-                engine.setProperty("voice", v.id)
-                break
-        engine.say(text)
-        engine.runAndWait()
+        subprocess.run(
+            ["espeak-ng", "-v", lang, "-s", str(rate), text],
+            timeout=60,
+            check=False
+        )
     except Exception as e:
-        logger.warning(f"[TTS] Échec synthèse vocale : {e}")
+        logger.warning(f"[TTS] Échec espeak-ng : {e}")
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index e1a4dc5..d2e50d5 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6236 (9 ligne(s)) dans l'ancienne version → ligne 6236 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6236,9 +6236,23 @@ function explDrawArrows(arrows) {
   }
 }
 
+function markdownToHtml(text) {
+  if (!text) return "";
+  let h = text
+    .replace(/^### (.+)$/gm, "<h4>$1</h4>")
+    .replace(/^## (.+)$/gm, "<h3>$1</h3>")
+    .replace(/^# (.+)$/gm, "<h3>$1</h3>")
+    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
+    .replace(/__(.+?)__/g, "<strong>$1</strong>")
+    .replace(/\*(.+?)\*/g, "<em>$1</em>")
+    .replace(/\n\n+/g, "</p><p>")
+    .replace(/\n/g, "<br>");
+  return "<p>" + h + "</p>";
+}
+
 socket.on("explorer_explanation", (data) => {
   const el = document.getElementById("explorer-explanation");
-  if (el) el.textContent = (data && data.text) ? data.text : "";
+  if (el) el.innerHTML = markdownToHtml(data && data.text);
   explClearArrows();
   if (data && data.arrows) explDrawArrows(data.arrows);
 });
# ── Zone modifiée : ligne 6248 (7 ligne(s)) dans l'ancienne version → ligne 6262 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6248,7 +6262,7 @@ socket.on("explorer_chat_response", (data) => {
   if (!history || !data || !data.text) return;
   const r = document.createElement("div");
   r.style.cssText = "background:#f4f7fb; border-radius:6px; padding:4px 8px; align-self:flex-start; max-width:85%;";
-  r.textContent = data.text;
+  r.innerHTML = markdownToHtml(data.text);
   history.appendChild(r);
   history.scrollTop = history.scrollHeight;
   explClearArrows();
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index 17e42c7..f8bd850 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 817 (3 ligne(s)) dans l'ancienne version → ligne 817 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -817,3 +817,16 @@
   transition:background 0.15s;
 }
 .aide-panier-icone:hover { background:#e94560; }
+
+/* ── Opening Explorer — rendu Markdown explications LLM ── */
+#explorer-explanation p, #explorer-chat-history p {
+  margin: 0 0 6px 0;
+}
+#explorer-explanation h3, #explorer-explanation h4,
+#explorer-chat-history h3, #explorer-chat-history h4 {
+  font-size: 0.85rem; font-weight: 700;
+  margin: 6px 0 3px 0; color: #1a2a3a;
+}
+#explorer-explanation strong, #explorer-chat-history strong {
+  color: #1a2a3a; font-weight: 700;
+}
