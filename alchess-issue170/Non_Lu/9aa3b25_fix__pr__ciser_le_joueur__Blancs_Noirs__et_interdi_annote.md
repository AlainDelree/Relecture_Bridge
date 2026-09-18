9aa3b25

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9aa3b25
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 10:39:11 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: préciser le joueur (Blancs/Noirs) et interdire les coups futurs dans le prompt llm_explainer (issue #170, suite #168)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/llm_explainer.py b/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 053fe1a..7797432 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Zone modifiée : ligne 135 (16 ligne(s)) dans l'ancienne version → ligne 135 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -135,16 +135,23 @@ def _save_cache(cache: dict) -> None:
 
 
 def _build_user_prompt(fen, move_san, opening_name, alternatives) -> str:
+    import chess as _chess
+    try:
+        board = _chess.Board(fen)
+        player = "Noirs" if board.turn == _chess.WHITE else "Blancs"
+    except Exception:
+        player = "le joueur"
     if alternatives:
         alt_text = ", ".join(a.get("san", a.get("uci", "")) for a in alternatives[:3])
-        alt_line = f"Réponses probables de l'adversaire depuis cette position : {alt_text}.\n"
+        alt_line = f"Réponses probables de l'adversaire : {alt_text}.\n"
     else:
         alt_line = ""
     return (
-        f"Ouverture : {opening_name}. Le coup vient d'être joué : {move_san}.\n"
+        f"Ouverture : {opening_name}. Les {player} viennent de jouer : {move_san}.\n"
         f"Position FEN : {fen}.\n"
         f"{alt_line}"
-        f"Explique pourquoi ce coup est joué ici."
+        f"Explique en 2-3 phrases pourquoi les {player} ont joué {move_san} ici. "
+        f"Parle uniquement de ce coup. Ne mentionne pas les coups futurs de l'adversaire."
     )
 
 
