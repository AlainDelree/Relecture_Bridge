329ec6e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 329ec6e
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 23:03:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    docs: mise à jour TACHES.md — issue #109 (_board_menu_watcher flag unique)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1b3d52c..4e5d5ab 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 24 (6 ligne(s)) dans l'ancienne version → ligne 24 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,6 +24,7 @@
 - **Numéros de lignes échiquier mal alignés (rendu police Windows)** `[Windows]`
 
 ### Bugs résolus récemment
+- **Bouton Connecter clignotant (schéma SVG)** `[Linux]` — issue #109, commit `2e16190`. `_board_menu_watcher` ré-émettait `board_error` toutes les 3s tant que le plateau restait déconnecté, ce qui redéclenchait `_applyBoardBadge()` côté JS à chaque poll → clignotement du schéma/bouton. Ajout d'un flag local `_already_notified` : `board_error` n'est émis qu'une seule fois par déconnexion, remis à `False` à la reconnexion (`else` du `is_connected()`) et en sortie de l'état `menu`.
 - **`_board_menu_watcher` ne détectait jamais la déconnexion au menu** `[Linux]` — issue #108, commit `694d877`. Le watcher n'appelait que `hid_backend.is_connected()`, qui lit le flag `_connected` — flag mis à `False` uniquement par un `OSError` levé dans `get_fen()`. Or personne n'appelait `get_fen()` au menu, donc le flag ne changeait jamais. Ajout de `hid_backend.get_fen()` (dans le `try/except` existant) juste avant le test, pour forcer une lecture USB réelle à chaque poll de 3s.
 - **Schéma SVG connexion — collé au menu-grid au lieu d'être à gauche du titre** `[Linux]` — issue #107, commit `15d8188`. `.schema-connexion` sorti du wrapper flex (qui ne contient plus que `.menu-grid`) et placé directement dans `#screen-menu`, juste avant `.menu-title`. CSS : `#screen-menu` passe en `position:relative` ; `.schema-connexion` passe en `position:absolute; left:20px; top:0` (aligné avec le haut du titre AlChess), `margin-right:8px` supprimé.
 - **Schéma SVG connexion — bandeau horizontal trop large, remplacé par colonne verticale étroite** `[Linux]` — issue #106, commit `9a36804`. `.schema-connexion` déplacé dans `#screen-menu` juste avant `.menu-grid`, enveloppé avec `.menu-grid` dans un div flex ; SVG repensé en viewBox verticale `0 0 50 200` (ordinateur ~36×24, câble ~80px, échiquier ~36×36) ; CSS réduite à `width:60px` ; bouton "Connecter" repositionné en `top:48%`/`width:44px`.
