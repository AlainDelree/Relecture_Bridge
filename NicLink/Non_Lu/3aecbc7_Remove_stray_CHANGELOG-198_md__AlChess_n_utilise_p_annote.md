3aecbc7

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3aecbc7
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 17:30:50 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Remove stray CHANGELOG-198.md (AlChess n'utilise pas ce mecanisme)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-198.md b/CHANGELOG-198.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2493dd2..0000000
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG-198.md
# ── Version APRÈS ce commit.
+++ /dev/null
# ── Zone modifiée : ligne 1 (8 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,8 +0,0 @@
-# Changelog — issue #198
-
-## Fix — Drawer LLM Analyse de partie : champ texte invisible + markdown brut
-
-- **Champ texte invisible** : le bouton `#analyse-llm-send-btn` héritait de `.btn { display:block; width:100% }` (défini dans `main.css`) sans override inline, et occupait donc la quasi-totalité de la ligne flex (`display:flex`) partagée avec l'input. Résultat mesuré (Chromium headless, viewport 1400px) : input réduit à **22×33px** contre 426×33px pour le bouton. Correction : ajout de `width:auto; flex-shrink:0;` dans le style inline du bouton — l'input passe à ~386px de large. `nicsoft/web/templates/index.html`.
-- **Markdown brut affiché** : le drawer utilise `textContent` (pas de rendu HTML) mais recevait le texte brut du LLM (`**gras**`, `- item`, `# titre`). Ajout de `stripMarkdownForChat()` dans `app.js` (inspirée de `stripMarkdownForTts()` déjà présente pour l'Opening Explorer), appliquée sur `data.text` dans le handler `socket.on("analyse_llm_response", ...)` avant poussée dans `_analyseLlmHistory` et rendu de la bulle. Contrairement à la version TTS, les sauts de ligne sont préservés (bulle en `white-space:pre-wrap`) plutôt que collapsés en espaces. `nicsoft/web/static/app.js`.
-
-Vérifié en Chromium headless (Playwright) : dimensions de l'input avant/après, et sortie de `stripMarkdownForChat()` sur un échantillon avec titres/gras/italique/listes.
