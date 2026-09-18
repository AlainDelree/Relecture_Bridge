3dc5f6f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3dc5f6f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 10:39:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    docs: entrée CHANGELOG-170 pour issue #170 (llm_explainer prompt)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-170.md b/CHANGELOG-170.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..daecfa6
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-170.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,5 @@
+## Issue #170 — llm_explainer : préciser le joueur et interdire les coups futurs dans le prompt
+
+- `nicsoft/modes/opening_explorer/llm_explainer.py` : `_build_user_prompt` identifie désormais le camp qui vient de jouer (Blancs/Noirs, déduit du FEN) et l'inclut explicitement dans le prompt envoyé au LLM ("Les Blancs viennent de jouer : e4"). Ajout d'une consigne explicite interdisant de mentionner les coups futurs de l'adversaire, pour corriger le comportement où le LLM expliquait la réponse probable de l'adversaire au lieu du coup joué.
+- Cache LLM vidé (`data/explorer_cache.json`) pour forcer la régénération des explications avec le nouveau prompt.
+- Suite de l'issue #168.
