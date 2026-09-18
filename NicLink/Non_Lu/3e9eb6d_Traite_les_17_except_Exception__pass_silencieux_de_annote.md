3e9eb6d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3e9eb6d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 16:44:01 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Traite les 17 except Exception: pass silencieux de pedagogique.py (issue #218)
    
    Revue individuelle : logging.warning() pour les échecs pouvant masquer une
    fuite de ressource (engine.quit()) ou casser une fonctionnalité utilisateur
    silencieusement (poll_abandon — équivalent kill_switch/actions web,
    restauration terminal) ; logging.debug() pour les cas dégradés sans impact
    critique (lecture config.json en fallback, popup best-effort, détection
    promotion en boucle WAIT_FISH, menu terminal legacy) ; commentaire explicite
    pour les LEDs/bips réellement cosmétiques (même motif que #216/#217).
    Comportement de continuation strictement inchangé.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/pedagogique/pedagogique.py b/nicsoft/modes/pedagogique/pedagogique.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 32fe09c..c267231 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/pedagogique/pedagogique.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/pedagogique/pedagogique.py
# ── Zone modifiée : ligne 75 (8 ligne(s)) dans l'ancienne version → ligne 75 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -75,8 +75,8 @@ def load_config() -> dict:
             with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                 data = json.load(f)
             return {**DEFAULT_CONFIG, **data}
-        except Exception:
-            pass
+        except Exception as exc:
+            logger.warning(f"Lecture config.json impossible, defaults utilises: {exc}")
     return dict(DEFAULT_CONFIG)
 
 
# ── Zone modifiée : ligne 135 (7 ligne(s)) dans l'ancienne version → ligne 135 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -135,7 +135,7 @@ def _led_bon_coup(nl_inst: NicLinkManager, dest_sq: int) -> None:
         time.sleep(1.5)
         nl_inst.turn_off_all_leds()
     except Exception:
-        pass
+        pass  # LED best-effort, sans impact fonctionnel
 
 
 def _led_clignote(nl_inst: NicLinkManager, dest_sq: int,
# ── Zone modifiée : ligne 149 (7 ligne(s)) dans l'ancienne version → ligne 149 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -149,7 +149,7 @@ def _led_clignote(nl_inst: NicLinkManager, dest_sq: int,
             nl_inst.turn_off_all_leds()
             time.sleep(interval)
     except Exception:
-        pass
+        pass  # LED best-effort, sans impact fonctionnel
 
 
 def _led_imprecision(nl_inst: NicLinkManager, dest_sq: int) -> None:
# ── Zone modifiée : ligne 192 (7 ligne(s)) dans l'ancienne version → ligne 192 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -192,7 +192,7 @@ def _led_blunder(nl_inst: NicLinkManager, dest_sq: int) -> None:
             nl_inst.turn_off_all_leds()
             time.sleep(0.2)
     except Exception:
-        pass
+        pass  # LED best-effort, sans impact fonctionnel
 
 
 def _led_meilleur_coup(nl_inst: NicLinkManager, best_move: str) -> None:
# ── Zone modifiée : ligne 202 (7 ligne(s)) dans l'ancienne version → ligne 202 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -202,7 +202,7 @@ def _led_meilleur_coup(nl_inst: NicLinkManager, best_move: str) -> None:
         time.sleep(5.0)
         nl_inst.turn_off_all_leds()
     except Exception:
-        pass
+        pass  # LED best-effort, sans impact fonctionnel
 
 
 # ──────────────────────────────────────────────
# ── Zone modifiée : ligne 336 (8 ligne(s)) dans l'ancienne version → ligne 336 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -336,8 +336,8 @@ class Game(threading.Thread):
         # Arrêter proprement le moteur
         try:
             self.engine.quit()
-        except Exception:
-            pass
+        except Exception as exc:
+            logger.warning(f"Fermeture du moteur echouee (processus potentiellement orphelin): {exc}")
         # Notifier le navigateur
         send_event("game_over", {"result": result, "reason": reason or "Fin de partie", "source": "niclink", "skip": skip_save})
         from nicsoft.web.server import set_app_state, _game_state
# ── Zone modifiée : ligne 432 (8 ligne(s)) dans l'ancienne version → ligne 432 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -432,8 +432,8 @@ class Game(threading.Thread):
                 _sio.emit("popup", {"message": "♚ Échec et mat !", "message_key": "server.popup.mat", "type": "gameover"})
             elif "stalemate" in reason.lower():
                 _sio.emit("popup", {"message": "Pat !", "message_key": "server.popup.pat", "type": "gameover"})
-        except Exception:
-            pass
+        except Exception as exc:
+            logger.debug(f"Envoi popup fin de partie echoue: {exc}")
         self._end_game(result, reason)
 
     # ── Signaux ───────────────────────────────────────────────────────────
# ── Zone modifiée : ligne 467 (13 ligne(s)) dans l'ancienne version → ligne 467 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -467,13 +467,13 @@ class Game(threading.Thread):
             sig = 3 if self.playing_white == chess.WHITE else 2
             self.nl_inst.signal_lights(sig)
         except Exception:
-            pass
+            pass  # LED/bip best-effort, sans impact fonctionnel
 
     def _shutdown_leds(self) -> None:
         try:
             self.nl_inst.turn_off_all_leds()
         except Exception:
-            pass
+            pass  # LED best-effort, sans impact fonctionnel
 
     # ── Analyse et feedback ───────────────────────────────────────────────
 
# ── Zone modifiée : ligne 493 (7 ligne(s)) dans l'ancienne version → ligne 493 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -493,7 +493,7 @@ class Game(threading.Thread):
             try:
                 self.nl_inst.beep()
             except Exception:
-                pass
+                pass  # Bip best-effort, sans impact fonctionnel
 
     def _doit_pause(self, qualite: str) -> bool:
         """Détermine si on doit faire une pause interactive."""
# ── Zone modifiée : ligne 631 (13 ligne(s)) dans l'ancienne version → ligne 631 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -631,13 +631,13 @@ class Game(threading.Thread):
                         break
                     elif ch == 'q':
                         break
-        except Exception:
-            pass
+        except Exception as exc:
+            logger.debug(f"Boucle menu pause (mode terminal) interrompue: {exc}")
         finally:
             try:
                 termios.tcsetattr(fd, termios.TCSADRAIN, old_attr)
-            except Exception:
-                pass
+            except Exception as exc:
+                logger.warning(f"Restauration attributs terminal echouee (terminal possiblement laisse en mode raw): {exc}")
         return result
     # ── Abandon ───────────────────────────────────────────────────────────
 
# ── Zone modifiée : ligne 1044 (7 ligne(s)) dans l'ancienne version → ligne 1044 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1044,7 +1044,7 @@ class Game(threading.Thread):
                         time.sleep(0.15)
                         self.nl_inst.beep()
                     except Exception:
-                        pass
+                        pass  # Bip best-effort, sans impact fonctionnel
                     send_event("illegal_position", {"message": msg})
 
                 if check_tab_press() and warning_shown and last_tmp_board:
# ── Zone modifiée : ligne 1090 (8 ligne(s)) dans l'ancienne version → ligne 1090 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1090,8 +1090,8 @@ class Game(threading.Thread):
                         else:
                             from nicsoft.web.server import action_queue
                             action_queue.put(action)
-                except Exception:
-                    pass
+                except Exception as exc:
+                    logger.warning(f"Erreur polling action web (abandon/nulle/pause): {exc}")
 
         abandon_watcher = threading.Thread(target=poll_abandon, daemon=True)
         abandon_watcher.start()
# ── Zone modifiée : ligne 1204 (7 ligne(s)) dans l'ancienne version → ligne 1204 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1204,7 +1204,7 @@ class Game(threading.Thread):
             try:
                 self.nl_inst.beep()
             except Exception:
-                pass
+                pass  # Bip best-effort, sans impact fonctionnel
 
         # Toujours informer le navigateur (pour activer btn-reprendre et afficher qualité)
         # Calculer la séquence punitive si blunder/erreur
# ── Zone modifiée : ligne 1460 (7 ligne(s)) dans l'ancienne version → ligne 1460 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1460,7 +1460,7 @@ class Game(threading.Thread):
                             try:
                                 cancel_ref.nl_inst.turn_off_all_leds()
                             except Exception:
-                                pass
+                                pass  # LED best-effort, sans impact fonctionnel
                     threading.Thread(target=_do_led_off, daemon=True).start()
                     if warning_shown or _warning_sent:
                         send_event("turn", {
# ── Zone modifiée : ligne 1484 (8 ligne(s)) dans l'ancienne version → ligne 1484 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1484,8 +1484,8 @@ class Game(threading.Thread):
                                 tmp_promo.piece_at(dest_sq).color == promo_color and
                                 tmp_promo.piece_at(src_sq) is None):
                             return
-                    except Exception:
-                        pass
+                    except Exception as exc:
+                        logger.debug(f"Detection promotion echouee (retry sur prochaine iteration): {exc}")
 
                 try:
                     tmp_board  = chess.Board(board_fen + " w - - 0 1")
