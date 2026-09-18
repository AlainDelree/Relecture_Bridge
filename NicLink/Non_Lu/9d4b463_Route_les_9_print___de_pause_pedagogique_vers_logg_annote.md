9d4b463

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9d4b463
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 16:53:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Route les 9 print() de pause pedagogique vers logger.info (issue #219)
    
    Les print() de debug de handle_pause/_check_web_abandon sont invisibles en
    usage web normal (aucun terminal attache a ce thread). Remplaces par
    logger.info() sous le meme garde if DEBUG_MODE, pour atterrir dans
    niclink.log au lieu de disparaitre. logger.info() choisi plutot que
    logger.debug() car le logger du module est regle sur INFO.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/pedagogique/pedagogique.py b/nicsoft/modes/pedagogique/pedagogique.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c267231..617484d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/pedagogique/pedagogique.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/pedagogique/pedagogique.py
# ── Zone modifiée : ligne 660 (7 ligne(s)) dans l'ancienne version → ligne 660 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -660,7 +660,7 @@ class Game(threading.Thread):
         elif atype == "set_pause":
             val = action.get("value", "blunder")
             self.pedagogique_pause = val
-            if DEBUG_MODE: print(f"[WEB] Pause pédagogique changée : {val}")
+            if DEBUG_MODE: logger.info(f"[WEB] Pause pédagogique changée : {val}")
         elif atype == "pause":
             self._pause_demandee = True
     def _traiter_nulle(self, board=None) -> None:
# ── Zone modifiée : ligne 716 (7 ligne(s)) dans l'ancienne version → ligne 716 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -716,7 +716,7 @@ class Game(threading.Thread):
         from nicsoft.web.server import set_app_state, get_history
 
         auto = qualite is not None
-        if DEBUG_MODE: print(f"\n  [PAUSE] Partie suspendue {'(auto: ' + qualite + ')' if auto else '(manuelle)'}.")
+        if DEBUG_MODE: logger.info(f"\n  [PAUSE] Partie suspendue {'(auto: ' + qualite + ')' if auto else '(manuelle)'}.")
         self.nl_inst.turn_off_all_leds()
 
         bm = best_move or getattr(self, "_last_best_move", None)
# ── Zone modifiée : ligne 754 (17 ligne(s)) dans l'ancienne version → ligne 754 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -754,17 +754,17 @@ class Game(threading.Thread):
                 changer_couleur = action.get("changer_couleur", False)
                 target_fen      = action.get("fen", None)
                 reprendre       = True
-                if DEBUG_MODE: print(f"  [PAUSE] Reprendre le coup — changer_couleur={changer_couleur}")
+                if DEBUG_MODE: logger.info(f"  [PAUSE] Reprendre le coup — changer_couleur={changer_couleur}")
                 break
 
             elif atype == "continuer":
                 # Pause auto : accepter le coup, continuer la partie
-                if DEBUG_MODE: print("  [PAUSE] Continuer — coup accepté.")
+                if DEBUG_MODE: logger.info("  [PAUSE] Continuer — coup accepté.")
                 break
 
             elif atype == "resume_pause":
                 # Pause manuelle : reprendre la partie sans rien changer
-                if DEBUG_MODE: print("  [PAUSE] Reprendre la partie.")
+                if DEBUG_MODE: logger.info("  [PAUSE] Reprendre la partie.")
                 break
 
             elif atype == "meilleur":
# ── Zone modifiée : ligne 774 (7 ligne(s)) dans l'ancienne version → ligne 774 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -774,7 +774,7 @@ class Game(threading.Thread):
                         best_san = san_ep(tmp, chess.Move.from_uci(bm))
                     except Exception:
                         best_san = bm
-                    if DEBUG_MODE: print(f"  [PAUSE] Meilleur coup : {best_san}")
+                    if DEBUG_MODE: logger.info(f"  [PAUSE] Meilleur coup : {best_san}")
                     _led_meilleur_coup(self.nl_inst, bm)
                     send_event("best_move", {"uci": bm, "san": best_san})
                 continue
# ── Zone modifiée : ligne 813 (9 ligne(s)) dans l'ancienne version → ligne 813 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -813,9 +813,9 @@ class Game(threading.Thread):
                 self.nl_inst.game_board = chess.Board()
                 for mv in move_stack[:target_idx]:
                     self.nl_inst.game_board.push(mv)
-                if DEBUG_MODE: print(f"  [PAUSE] Historique tronqué au coup {target_idx}.")
+                if DEBUG_MODE: logger.info(f"  [PAUSE] Historique tronqué au coup {target_idx}.")
             else:
-                if DEBUG_MODE: print("  [PAUSE] FEN cible introuvable dans l'historique, reprise depuis position courante.")
+                if DEBUG_MODE: logger.info("  [PAUSE] FEN cible introuvable dans l'historique, reprise depuis position courante.")
 
         # ── Vérifier que le plateau physique correspond à la position cible ──
         expected_fen = self.nl_inst.game_board.board_fen()
# ── Zone modifiée : ligne 823 (7 ligne(s)) dans l'ancienne version → ligne 823 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -823,7 +823,7 @@ class Game(threading.Thread):
         current_fen  = current_raw.strip().split()[0] if current_raw else ""
 
         if current_fen != expected_fen:
-            if DEBUG_MODE: print("  [PAUSE] Position incorrecte — attendu :", expected_fen)
+            if DEBUG_MODE: logger.info("  [PAUSE] Position incorrecte — attendu : %s", expected_fen)
             from nicsoft.web.server import action_queue as _aq
             while not _aq.empty():
                 try: _aq.get_nowait()
