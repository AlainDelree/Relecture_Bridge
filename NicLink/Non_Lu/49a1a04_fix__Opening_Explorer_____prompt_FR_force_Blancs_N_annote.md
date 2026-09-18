49a1a04

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 49a1a04
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 20:02:06 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: Opening Explorer — prompt FR force Blancs/Noirs (issue #151)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/llm_explainer.py b/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 26342bf..748cc94 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Zone modifiée : ligne 44 (7 ligne(s)) dans l'ancienne version → ligne 44 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -44,7 +44,9 @@ _SYSTEM_PROMPTS = {
     "fr": (
         "Tu es un entraîneur d'échecs pédagogue. Explique les coups d'une "
         "ouverture à un joueur débutant. Sois concis (3-4 phrases maximum), "
-        "clair et encourageant. Réponds uniquement en français."
+        "clair et encourageant. Réponds uniquement en français. "
+        "Utilise toujours les termes français : Blancs (jamais White), "
+        "Noirs (jamais Black), cavalier, fou, tour, dame, roi."
         + _ARROWS_INSTRUCTION["fr"]
     ),
     "en": (
