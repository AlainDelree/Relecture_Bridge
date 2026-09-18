4937775

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4937775
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 16:28:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Traite les 21 except Exception: pass silencieux de human.py (issue #217)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/humain/human.py b/nicsoft/modes/humain/human.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ce3f6ea..29cdc29 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/humain/human.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/humain/human.py
# ── Zone modifiée : ligne 47 (8 ligne(s)) dans l'ancienne version → ligne 47 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,8 +47,8 @@ def load_config() -> dict:
             with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                 data = json.load(f)
             return {**DEFAULT_CONFIG, **data}
-        except Exception:
-            pass
+        except Exception as exc:
+            logger.warning(f"Lecture config.json impossible, defaults utilises: {exc}")
     return dict(DEFAULT_CONFIG)
 
 
# ── Zone modifiée : ligne 214 (7 ligne(s)) dans l'ancienne version → ligne 214 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -214,7 +214,7 @@ class Game(threading.Thread):
         try:
             self.nl_inst.set_led(king_name, True)
         except Exception:
-            pass
+            pass  # LED indicative best-effort, sans impact fonctionnel
         while True:
             hardware = self.get_hardware_piece_placement()
             if hardware:
# ── Zone modifiée : ligne 225 (11 ligne(s)) dans l'ancienne version → ligne 225 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -225,11 +225,11 @@ class Game(threading.Thread):
                         try:
                             self.nl_inst.turn_off_all_leds()
                         except Exception:
-                            pass
+                            pass  # LED best-effort, sans impact fonctionnel
                         print(f"  Roi replace en {king_name}. La partie continue.")
                         return
-                except Exception:
-                    pass
+                except Exception as exc:
+                    logger.debug(f"Detection roi replace echouee (retry): {exc}")
             time.sleep(0.2)
 
     # ── Fin de partie ─────────────────────────────────────────────────────
# ── Zone modifiée : ligne 254 (7 ligne(s)) dans l'ancienne version → ligne 254 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -254,7 +254,7 @@ class Game(threading.Thread):
         try:
             self.nl_inst.turn_off_all_leds()
         except Exception:
-            pass
+            pass  # LED best-effort, sans impact fonctionnel
 
         self.game_over = True
         sys.exit(0)
# ── Zone modifiée : ligne 341 (8 ligne(s)) dans l'ancienne version → ligne 341 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -341,8 +341,8 @@ class Game(threading.Thread):
                         absent_color = color
                         absent_sq = ksq
                         break
-            except Exception:
-                pass
+            except Exception as exc:
+                logger.debug(f"Detection roi absent (abandon) echouee: {exc}")
 
             if king_absent:
                 if self._king_absent_since is None:
# ── Zone modifiée : ligne 359 (7 ligne(s)) dans l'ancienne version → ligne 359 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -359,7 +359,7 @@ class Game(threading.Thread):
             try:
                 self.nl_inst.turn_off_all_leds()
             except Exception:
-                pass
+                pass  # LED best-effort, sans impact fonctionnel
             self._leds_showing_turn = False
 
         if hardware == self._last_raw_fen:
# ── Zone modifiée : ligne 384 (7 ligne(s)) dans l'ancienne version → ligne 384 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -384,7 +384,7 @@ class Game(threading.Thread):
                 try:
                     self.nl_inst.turn_off_all_leds()
                 except Exception:
-                    pass
+                    pass  # LED best-effort, sans impact fonctionnel
                 self._leds_showing_turn = False
 
             is_white_turn = (self.board.turn == chess.WHITE)
# ── Zone modifiée : ligne 423 (21 ligne(s)) dans l'ancienne version → ligne 423 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -423,21 +423,21 @@ class Game(threading.Thread):
                     king_sq = chess.square_name(self.board.king(self.board.turn))
                     self.nl_inst.set_led(king_sq, True)
                 except Exception:
-                    pass
+                    pass  # LED/affichage diff best-effort, sans impact fonctionnel
         elif diffs > 4:
             print("⚠  Plusieurs pieces ont bouge -- remettez l'échiquier en ordre.")
             if hw_board:
                 try:
                     self.nl_inst.show_board_diff(self.board, hw_board)
                 except Exception:
-                    pass
+                    pass  # LED/affichage diff best-effort, sans impact fonctionnel
         else:
             print("⚠  Coup illegal -- remettez la piece a sa place.")
             if hw_board:
                 try:
                     self.nl_inst.show_board_diff(self.board, hw_board)
                 except Exception:
-                    pass
+                    pass  # LED/affichage diff best-effort, sans impact fonctionnel
         print(f"   Position attendue : {expected}")
         print(f"   Position detectee : {hardware}")
         print()
# ── Zone modifiée : ligne 579 (14 ligne(s)) dans l'ancienne version → ligne 579 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -579,14 +579,14 @@ def main():
             try:
                 _nl_ref[0].turn_off_all_leds()
             except Exception:
-                pass
+                pass  # LED best-effort, sans impact fonctionnel
         # Nettoyage du fichier tmp si la partie n'a pas ete sauvegardee
         g = _game_ref[0]
         if g and os.path.exists(g.tmp_path):
             try:
                 os.remove(g.tmp_path)
-            except Exception:
-                pass
+            except Exception as exc:
+                logger.warning(f"Suppression fichier tmp echouee ({g.tmp_path}): {exc}")
         sys.exit(0)
 
     signal.signal(signal.SIGINT, _emergency_shutdown)
# ── Zone modifiée : ligne 618 (7 ligne(s)) dans l'ancienne version → ligne 618 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -618,7 +618,7 @@ def main():
             try:
                 nl_inst.turn_off_all_leds()
             except Exception:
-                pass
+                pass  # LED best-effort, sans impact fonctionnel
 
 
 
# ── Zone modifiée : ligne 692 (7 ligne(s)) dans l'ancienne version → ligne 692 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -692,7 +692,7 @@ class GameWeb(threading.Thread):
             sig = 3 if is_white else 2
             self.nl_inst.signal_lights(sig)
         except Exception:
-            pass
+            pass  # LED best-effort, sans impact fonctionnel
 
         fen_avant = self.board.fen()
         expected  = self.board.board_fen()
# ── Zone modifiée : ligne 734 (7 ligne(s)) dans l'ancienne version → ligne 734 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -734,7 +734,7 @@ class GameWeb(threading.Thread):
                             self.nl_inst.set_led(from_sq, True)
                             self.nl_inst.set_led(to_sq, True)
                         except Exception:
-                            pass
+                            pass  # LED best-effort, sans impact fonctionnel
                         self.save_pgn_tmp()
                         send_event("undo_move", {
                             "fen":     self.board.board_fen(),
# ── Zone modifiée : ligne 806 (7 ligne(s)) dans l'ancienne version → ligne 806 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -806,7 +806,7 @@ class GameWeb(threading.Thread):
                         time.sleep(0.15)
                         self.nl_inst.beep()
                     except Exception:
-                        pass
+                        pass  # Bip best-effort, sans impact fonctionnel
                     send_event("illegal_position", msg)
 
         pos_watcher = threading.Thread(target=watch_position, daemon=True)
# ── Zone modifiée : ligne 821 (8 ligne(s)) dans l'ancienne version → ligne 821 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -821,8 +821,8 @@ class GameWeb(threading.Thread):
         try:
             move = self.nl_inst.await_move()
             tlog("[TIMING] await_move: %.2fs — move=%s", time.time()-_t_await, move)
-        except Exception:
-            pass
+        except Exception as exc:
+            logger.error(f"await_move a echoue, coup non detecte: {exc}")
         finally:
             watch_stop.set()
             watcher.join(timeout=1.0)
# ── Zone modifiée : ligne 926 (7 ligne(s)) dans l'ancienne version → ligne 926 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -926,7 +926,7 @@ class GameWeb(threading.Thread):
                     try:
                         self.nl_inst.set_move_leds(bm)
                     except Exception:
-                        pass
+                        pass  # LED best-effort, sans impact fonctionnel
                     send_event("best_move", {"uci": bm, "san": best_san})
                 continue
             elif atype in ("abandonner", "back_menu"):
# ── Zone modifiée : ligne 1129 (8 ligne(s)) dans l'ancienne version → ligne 1129 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1129,8 +1129,8 @@ class GameWeb(threading.Thread):
                 # Réarmer le kill_switch pour que await_move fonctionne à nouveau
                 try:
                     self.nl_inst.kill_switch.clear()
-                except Exception:
-                    pass
+                except Exception as exc:
+                    logger.warning(f"kill_switch.clear() (post-pause) a echoue, await_move pourrait rester bloque: {exc}")
                 continue
 
             if self._abandon_demande:
# ── Zone modifiée : ligne 1171 (8 ligne(s)) dans l'ancienne version → ligne 1171 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1171,8 +1171,8 @@ class GameWeb(threading.Thread):
                 self._undo_pending = False
                 try:
                     self.nl_inst.kill_switch.clear()
-                except Exception:
-                    pass
+                except Exception as exc:
+                    logger.warning(f"kill_switch.clear() (post-undo) a echoue, await_move pourrait rester bloque: {exc}")
                 # Attendre que le joueur replace la pièce et clique Confirmer
                 expected = self.board.board_fen()
                 from nicsoft.web.server import action_queue as _aq
