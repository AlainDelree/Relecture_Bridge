86e1c38

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 86e1c38
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 17:27:29 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Fix drawer LLM Analyse de partie : champ texte invisible + markdown brut (issue #198)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-198.md b/CHANGELOG-198.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..2493dd2
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-198.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,8 @@
+# Changelog — issue #198
+
+## Fix — Drawer LLM Analyse de partie : champ texte invisible + markdown brut
+
+- **Champ texte invisible** : le bouton `#analyse-llm-send-btn` héritait de `.btn { display:block; width:100% }` (défini dans `main.css`) sans override inline, et occupait donc la quasi-totalité de la ligne flex (`display:flex`) partagée avec l'input. Résultat mesuré (Chromium headless, viewport 1400px) : input réduit à **22×33px** contre 426×33px pour le bouton. Correction : ajout de `width:auto; flex-shrink:0;` dans le style inline du bouton — l'input passe à ~386px de large. `nicsoft/web/templates/index.html`.
+- **Markdown brut affiché** : le drawer utilise `textContent` (pas de rendu HTML) mais recevait le texte brut du LLM (`**gras**`, `- item`, `# titre`). Ajout de `stripMarkdownForChat()` dans `app.js` (inspirée de `stripMarkdownForTts()` déjà présente pour l'Opening Explorer), appliquée sur `data.text` dans le handler `socket.on("analyse_llm_response", ...)` avant poussée dans `_analyseLlmHistory` et rendu de la bulle. Contrairement à la version TTS, les sauts de ligne sont préservés (bulle en `white-space:pre-wrap`) plutôt que collapsés en espaces. `nicsoft/web/static/app.js`.
+
+Vérifié en Chromium headless (Playwright) : dimensions de l'input avant/après, et sortie de `stripMarkdownForChat()` sur un échantillon avec titres/gras/italique/listes.
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index aa8f6d7..5255b8f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 2290 (6 ligne(s)) dans l'ancienne version → ligne 2290 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2290,6 +2290,19 @@ function analyseLlmBuildContext() {
   return { fen, move: move.trim(), pgn: pgn.trim() };
 }
 
+function stripMarkdownForChat(text) {
+  if (!text) return "";
+  return text
+    .replace(/^#{1,6}\s*/gm, "")       // titres #
+    .replace(/\*\*(.+?)\*\*/g, "$1")   // gras **
+    .replace(/__(.+?)__/g, "$1")       // gras __
+    .replace(/\*(.+?)\*/g, "$1")       // italique *
+    .replace(/_(.+?)_/g, "$1")         // italique _
+    .replace(/^[ \t]*[-*+]\s+/gm, "")  // puces de liste
+    .replace(/\n{3,}/g, "\n\n")        // sauts de ligne multiples
+    .trim();
+}
+
 function _analyseLlmRenderBubble(role, text) {
   const history = document.getElementById("analyse-llm-history");
   if (!history) return;
# ── Zone modifiée : ligne 2341 (7 ligne(s)) dans l'ancienne version → ligne 2354 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2341,7 +2354,7 @@ function _analyseLlmDone() {
 }
 
 socket.on("analyse_llm_response", (data) => {
-  const text = (data && data.text) || "";
+  const text = stripMarkdownForChat((data && data.text) || "");
   if (text) {
     _analyseLlmHistory.push({ role: "assistant", content: text });
     _analyseLlmRenderBubble("assistant", text);
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 5b8590b..072e702 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1802 (7 ligne(s)) dans l'ancienne version → ligne 1802 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1802,7 +1802,7 @@
   </div>
   <div style="display:flex; gap:8px; padding:10px 16px; border-top:1px solid #a0b8d0; flex-shrink:0;">
     <input type="text" id="analyse-llm-input" style="flex:1; min-width:0; padding:8px 10px; border:1px solid #a0b8d0; border-radius:6px; font-size:0.85rem;" data-i18n-placeholder="analyse_llm.placeholder" placeholder="Posez une question...">
-    <button id="analyse-llm-send-btn" class="btn btn-continuer" style="margin:0; padding:8px 14px; font-size:0.82rem; white-space:nowrap;" onclick="analyseLlmSend()" data-i18n="analyse_llm.envoyer">Envoyer</button>
+    <button id="analyse-llm-send-btn" class="btn btn-continuer" style="margin:0; width:auto; padding:8px 14px; font-size:0.82rem; white-space:nowrap; flex-shrink:0;" onclick="analyseLlmSend()" data-i18n="analyse_llm.envoyer">Envoyer</button>
   </div>
 </div>
 
