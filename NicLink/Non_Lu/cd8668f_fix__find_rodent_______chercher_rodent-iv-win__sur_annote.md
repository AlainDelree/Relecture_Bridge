cd8668f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit cd8668f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 19:12:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: find_rodent() — chercher rodent-iv-win/ sur Windows si rodent-iv/ absent (issue #122)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e68a636..1b0d54a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 23 (6 ligne(s)) dans l'ancienne version → ligne 23 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -23,6 +23,7 @@
 - **Numéros de lignes échiquier mal alignés (rendu police Windows)** `[Windows]`
 
 ### Bugs résolus récemment
+- **Rodent IV indisponible sur installation NSIS standalone (Windows) — `find_rodent()` ignorait `engines/rodent-iv-win/`** — corrigé issue #122.
 - **`_board_menu_watcher` — `get_fen()` ne détecte pas un débranchement sur Linux** `[Linux]` — issue #110, commit `bc87bc5`. Le fix #108 appelait `hid_backend.get_fen()` pour forcer une lecture USB, mais sur Linux `_dev.read()` ne lève pas d'`OSError` au débranchement — il retourne `[]` après le timeout, donc `_connected` ne passait jamais à `False`. Ajout de `hid_backend.check_physically_present()`, qui interroge directement `hid.enumerate()` pour confirmer la présence du périphérique dans le sous-système USB (sans dépendre d'une lecture FEN) ; remplace l'appel `get_fen()` + `is_connected()` dans le watcher.
 - **Bouton Connecter clignotant (schéma SVG)** `[Linux]` — issue #109, commit `2e16190`. `_board_menu_watcher` ré-émettait `board_error` toutes les 3s tant que le plateau restait déconnecté, ce qui redéclenchait `_applyBoardBadge()` côté JS à chaque poll → clignotement du schéma/bouton. Ajout d'un flag local `_already_notified` : `board_error` n'est émis qu'une seule fois par déconnexion, remis à `False` à la reconnexion (`else` du `is_connected()`) et en sortie de l'état `menu`.
 - **`_board_menu_watcher` ne détectait jamais la déconnexion au menu** `[Linux]` — issue #108, commit `694d877`. Le watcher n'appelait que `hid_backend.is_connected()`, qui lit le flag `_connected` — flag mis à `False` uniquement par un `OSError` levé dans `get_fen()`. Or personne n'appelait `get_fen()` au menu, donc le flag ne changeait jamais. Ajout de `hid_backend.get_fen()` (dans le `try/except` existant) juste avant le test, pour forcer une lecture USB réelle à chaque poll de 3s.
# (diff du fichier suivant)
diff --git a/nicsoft/engine/engine_manager.py b/nicsoft/engine/engine_manager.py
# (index — ignorable)
index bb0c3a4..a08fa9e 100755
# (avant — fichier suivant)
--- a/nicsoft/engine/engine_manager.py
# (après — fichier suivant)
+++ b/nicsoft/engine/engine_manager.py
# ── Zone modifiée : ligne 486 (9 ligne(s)) dans l'ancienne version → ligne 486 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -486,9 +486,17 @@ MAIA_LEVELS = {
 def find_rodent() -> str | None:
     """Cherche l'exécutable Rodent IV selon la plateforme."""
     import sys
-    exe = "rodentIV.exe" if sys.platform == "win32" else "rodentIV"
-    path = ENGINES_DIR / "rodent-iv" / exe
-    return str(path) if path.exists() else None
+    if sys.platform == "win32":
+        # Chemin 1 : installation ZIP (make_release.sh renomme le binaire)
+        path = ENGINES_DIR / "rodent-iv" / "rodentIV.exe"
+        if path.exists():
+            return str(path)
+        # Chemin 2 : installation SyncGitRepo (binaire dans rodent-iv-win/)
+        path = ENGINES_DIR / "rodent-iv-win" / "rodent-iv-x64.exe"
+        return str(path) if path.exists() else None
+    else:
+        path = ENGINES_DIR / "rodent-iv" / "rodentIV"
+        return str(path) if path.exists() else None
 
 
 def stockfish_available() -> bool:
