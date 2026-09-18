1b4a422

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1b4a422
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 14:20:11 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: explorer_load() attrape SystemExit comme les autres modes (issue #159, suite #158)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4b92773..6e352d5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 1129 (7 ligne(s)) dans l'ancienne version → ligne 1129 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1129,7 +1129,7 @@ def explorer_load(source_type: str, opening_id: str, variant_index=None) -> dict
 
     try:
         nl_inst = create_board(virtual=used_virtual, logger_name="NicLink_explorer")
-    except Exception as e:
+    except (Exception, SystemExit) as e:
         logger.info(f"[EXPLORER] Échiquier physique indisponible, bascule en mode virtuel : {e}")
         nl_inst = create_board(virtual=True, logger_name="NicLink_explorer")
         used_virtual = True
