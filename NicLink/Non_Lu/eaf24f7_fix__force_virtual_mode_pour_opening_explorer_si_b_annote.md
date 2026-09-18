eaf24f7

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit eaf24f7
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 20:18:23 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: force virtual_mode pour opening_explorer si board_status != ok (issue #164, suite #163)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/alchess.py b/nicsoft/web/alchess.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b5681fe..caa6fe9 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/alchess.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/alchess.py
# ── Zone modifiée : ligne 247 (7 ligne(s)) dans l'ancienne version → ligne 247 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -247,7 +247,8 @@ def main():
             elif atype == "mode" and action.get("value") == "parametres":
                 set_app_state("parametres")
             elif atype == "mode" and action.get("value") == "opening_explorer":
-                gm.set_virtual_mode(action.get("virtual", False))
+                virtual = action.get("virtual", False) or (web_server._board_status != "ok")
+                gm.set_virtual_mode(virtual)
                 set_app_state("opening_explorer")
             elif atype == "start_exercice":
                 gm.start_exercice(action)
