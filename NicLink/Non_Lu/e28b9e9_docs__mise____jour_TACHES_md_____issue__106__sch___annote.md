e28b9e9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e28b9e9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 22:43:45 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    docs: mise à jour TACHES.md — issue #106 (schéma SVG colonne verticale)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a7d2ac2..db23a5c 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 24 (6 ligne(s)) dans l'ancienne version → ligne 24 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,6 +24,7 @@
 - **Numéros de lignes échiquier mal alignés (rendu police Windows)** `[Windows]`
 
 ### Bugs résolus récemment
+- **Schéma SVG connexion — bandeau horizontal trop large, remplacé par colonne verticale étroite** `[Linux]` — issue #106, commit `9a36804`. `.schema-connexion` déplacé dans `#screen-menu` juste avant `.menu-grid`, enveloppé avec `.menu-grid` dans un div flex ; SVG repensé en viewBox verticale `0 0 50 200` (ordinateur ~36×24, câble ~80px, échiquier ~36×36) ; CSS réduite à `width:60px` ; bouton "Connecter" repositionné en `top:48%`/`width:44px`.
 - **Icônes 🖥 résiduelles sur Analyse/Retranscrire + déconnexion plateau en session non détectée** `[Linux]` — issue #102, commit `fcb51e1`. `hid_backend.get_fen()` avalait les `OSError` de lecture USB sans jamais le signaler ; ajout de `is_connected()`/`_connected` côté backend, comptage des échecs consécutifs dans `_fen_reader_loop` (driver.py), callback `_board_lost_cb` câblé sur `board_error` dans `board_adapter.create_board()`, et `reconnect_board` intercepté dans `server.py::on_action` pour fonctionner aussi bien au menu qu'en cours de partie.
 - **Déconnexion plateau non détectée au menu + retours menu forcés silencieux** `[Linux]` — issue #103. Thread daemon `_board_menu_watcher` (alchess.py) qui poll `hid_backend.is_connected()` toutes les 3s tant que `_app_state == "menu"` ; retour menu depuis HH re-déclenche `_check_board_at_startup()`. Toasts d'erreur (`toast_message_key`/`toast_message`/`toast_type` dans `set_app_state("menu", ...)`) ajoutés dans `game_manager.py` pour `launch_pedagogique`/`launch_humain`/`launch_labo_libre` (échiquier non détecté, timeout position, moteur KO, exception non catégorisée) ; affichage côté `app.js` (handler `app_state`) déjà en place. **Non traité** : la perte du plateau en cours de partie active (`_board_lost_cb`) n'entraîne toujours pas de retour menu forcé — le thread `_fen_reader_loop` s'arrête et notifie `board_error`, mais les boucles de jeu (human.py/pedagogique.py) ne consomment pas ce signal pour interrompre `game.start()`. Corriger proprement nécessiterait un flag d'abandon consulté par la boucle de jeu ; risque de régression trop élevé pour être fait sans test matériel dans cette session.
 
