0f3ab56

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0f3ab56
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 10:33:19 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: alternatives en SAN + libellé réponses adverses dans llm_explainer (issue #168, suite #167)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/llm_explainer.py b/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3de82ea..053fe1a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Zone modifiée : ligne 136 (13 ligne(s)) dans l'ancienne version → ligne 136 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -136,13 +136,14 @@ def _save_cache(cache: dict) -> None:
 
 def _build_user_prompt(fen, move_san, opening_name, alternatives) -> str:
     if alternatives:
-        alt_text = ", ".join(a.get("uci", "") for a in alternatives[:2])
+        alt_text = ", ".join(a.get("san", a.get("uci", "")) for a in alternatives[:3])
+        alt_line = f"Réponses probables de l'adversaire depuis cette position : {alt_text}.\n"
     else:
-        alt_text = "aucune"
+        alt_line = ""
     return (
         f"Ouverture : {opening_name}. Le coup vient d'être joué : {move_san}.\n"
         f"Position FEN : {fen}.\n"
-        f"Alternatives connues : {alt_text}.\n"
+        f"{alt_line}"
         f"Explique pourquoi ce coup est joué ici."
     )
 
