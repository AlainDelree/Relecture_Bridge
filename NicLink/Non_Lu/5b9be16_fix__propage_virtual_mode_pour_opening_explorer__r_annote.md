5b9be16

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5b9be16
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 19:58:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: propage virtual_mode pour opening_explorer, retire checks _board_status explorer_load (issue #163, suite #162)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 75154bd..3542629 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 1117 (11 ligne(s)) dans l'ancienne version → ligne 1117 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1117,11 +1117,6 @@ def explorer_load(source_type: str, opening_id: str, variant_index=None) -> dict
         source = PolyglotSource(ouverture, book_path)
 
     used_virtual = _virtual_mode
-    if not used_virtual:
-        from nicsoft.web import server as web_server
-        if getattr(web_server, "_board_status", None) == "error":
-            logger.info("[EXPLORER] Plateau en erreur au démarrage, accès direct en mode virtuel.")
-            used_virtual = True
     try:
         nl_inst = create_board(virtual=used_virtual, logger_name="NicLink_explorer")
     except (Exception, SystemExit) as e:
# (diff du fichier suivant)
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# (index — ignorable)
index e0613cb..b5681fe 100644
# (avant — fichier suivant)
--- a/nicsoft/web/alchess.py
# (après — fichier suivant)
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 247 (6 ligne(s)) dans l'ancienne version → ligne 247 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -247,6 +247,7 @@ def main():
             elif atype == "mode" and action.get("value") == "parametres":
                 set_app_state("parametres")
             elif atype == "mode" and action.get("value") == "opening_explorer":
+                gm.set_virtual_mode(action.get("virtual", False))
                 set_app_state("opening_explorer")
             elif atype == "start_exercice":
                 gm.start_exercice(action)
