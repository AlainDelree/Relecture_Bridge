31d9b75

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 31d9b75
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 16:20:50 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Traite les 19 except Exception: pass silencieux de game_manager.py (issue #216)
    
    Revue individuelle : logging.warning() pour les échecs pouvant masquer une
    fuite de ressource (engine.quit(), disconnect(), fen_reader_stop.set(),
    application de analyse_active) ou casser une fonctionnalité utilisateur
    silencieusement ; logging.debug() pour les lectures de config.json en
    fallback et les boucles de polling FEN best-effort ; commentaire explicite
    pour les 7 cas purement cosmétiques (extinction LED) où le silence reste
    volontaire. Aucun elargissement de except Exception, comportement de
    continuation inchangé.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 92cf1d7..0750754 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 94 (7 ligne(s)) dans l'ancienne version → ligne 94 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -94,7 +94,7 @@ def _wait_initial_position_web(nl_inst, timeout: float = 300.0):
         if first_check:
             first_check = False
             try: nl_inst.signal_lights(1)
-            except Exception: pass
+            except Exception: pass  # signal LED cosmétique — échec sans conséquence fonctionnelle
         set_app_state("position_initiale", {"fen": board_fen})
         time.sleep(0.5)
 
# ── Zone modifiée : ligne 151 (8 ligne(s)) dans l'ancienne version → ligne 151 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -151,8 +151,8 @@ def launch_pedagogique(config):
                 cfg = json.load(f)
             engine_elo  = cfg.get("engine_elo", 1500)
             engine_path = _validated_engine_path(cfg)
-        except Exception:
-            pass
+        except Exception as e:
+            logger.debug(f"Lecture config.json échouée, valeurs par défaut conservées : {e}")
 
     web_server._app_state = "connecting"
     set_app_state("connecting")
# ── Zone modifiée : ligne 270 (7 ligne(s)) dans l'ancienne version → ligne 270 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -270,7 +270,7 @@ def _run_pedagogique(player_name, playing_white, level, pause, analyse_active, b
         set_virtual_board(None)
         if nl_inst:
             try: nl_inst.turn_off_all_leds()
-            except Exception: pass
+            except Exception: pass  # extinction LED best-effort — sans conséquence fonctionnelle
         if web_server._app_state != "game_over":
             web_server._app_state = "menu"
 
# ── Zone modifiée : ligne 363 (7 ligne(s)) dans l'ancienne version → ligne 363 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -363,7 +363,7 @@ def _run_humain(white_name, black_name, game_type, _error=None, virtual=False):
         set_virtual_board(None)
         if nl_inst:
             try: nl_inst.turn_off_all_leds()
-            except Exception: pass
+            except Exception: pass  # extinction LED best-effort — sans conséquence fonctionnelle
         if web_server._app_state not in ("game_over", "menu"):
             web_server._app_state = "menu"
 
# ── Zone modifiée : ligne 509 (12 ligne(s)) dans l'ancienne version → ligne 509 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -509,12 +509,14 @@ def _run_exercice(config: dict) -> None:
         set_virtual_board(None)
         if engine:
             try: engine.quit()
-            except Exception: pass
+            except Exception as e:
+                logger.warning(f"[EXERCICE] Fermeture du moteur échouée (processus potentiellement orphelin) : {e}")
         if nl_inst:
             try: nl_inst.turn_off_all_leds()
-            except Exception: pass
+            except Exception: pass  # extinction LED best-effort — sans conséquence fonctionnelle
             try: nl_inst.disconnect()
-            except Exception: pass
+            except Exception as e:
+                logger.warning(f"[EXERCICE] Déconnexion échiquier échouée : {e}")
         if my_session == _exercice_session and web_server._app_state not in ("menu", "exercices"):
             from nicsoft.modes.exercices.exercices import get_ouvertures, get_mes_lignes
             web_server._app_state = "exercices"
# ── Zone modifiée : ligne 600 (12 ligne(s)) dans l'ancienne version → ligne 602 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -600,12 +602,14 @@ def _run_drill(config: dict) -> None:
         set_virtual_board(None)
         if engine:
             try: engine.quit()
-            except Exception: pass
+            except Exception as e:
+                logger.warning(f"[DRILL] Fermeture du moteur échouée (processus potentiellement orphelin) : {e}")
         if nl_inst:
             try: nl_inst.turn_off_all_leds()
-            except Exception: pass
+            except Exception: pass  # extinction LED best-effort — sans conséquence fonctionnelle
             try: nl_inst.disconnect()
-            except Exception: pass
+            except Exception as e:
+                logger.warning(f"[DRILL] Déconnexion échiquier échouée : {e}")
         if my_session == _exercice_session and web_server._app_state not in ("menu", "exercices"):
             from nicsoft.modes.exercices.exercices import get_ouvertures, get_mes_lignes
             web_server._app_state = "exercices"
# ── Zone modifiée : ligne 650 (15 ligne(s)) dans l'ancienne version → ligne 654 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -650,15 +654,16 @@ def _poll_board_fen_labo():
                 fen = raw.strip().split()[0] if raw else ""
                 if fen:
                     send_event("board_fen_update", {"fen": fen})
-            except Exception:
-                pass
+            except Exception as e:
+                logger.debug(f"[LABO POLL] Lecture FEN échouée : {e}")
             time.sleep(0.3)
     except Exception as e:
         logger.error(f"[LABO POLL] Erreur : {e}")
     finally:
         if nl:
             try: nl._fen_reader_stop.set()
-            except Exception: pass
+            except Exception as e:
+                logger.warning(f"[LABO POLL] Arrêt du thread de lecture FEN échoué : {e}")
 
 
 def _make_labo_session(nl_inst, config: dict):
# ── Zone modifiée : ligne 672 (8 ligne(s)) dans l'ancienne version → ligne 677 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -672,8 +677,8 @@ def _make_labo_session(nl_inst, config: dict):
             with open(cfg_path) as f:
                 cfg = json.load(f)
             engine_path = _validated_engine_path(cfg)
-    except Exception:
-        pass
+    except Exception as e:
+        logger.debug(f"[LABO] Lecture config.json échouée, fallback find_stockfish() : {e}")
     if not engine_path:
         engine_path = find_stockfish() or "stockfish"
 
# ── Zone modifiée : ligne 861 (7 ligne(s)) dans l'ancienne version → ligne 866 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -861,7 +866,8 @@ def _run_labo_session():
         elif atype == "set_analyse":
             session.analyse_active = action.get("value", True)
             try: session.engine.analyse_active = session.analyse_active
-            except Exception: pass
+            except Exception as e:
+                logger.warning(f"[LABO] Application de analyse_active sur le moteur échouée : {e}")
 
         elif atype == "labo_copy_to_board":
             target_fen = action.get("fen", "")
# ── Zone modifiée : ligne 916 (8 ligne(s)) dans l'ancienne version → ligne 922 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -916,8 +922,8 @@ def _do_copy_to_board(target_fen: str) -> None:
                     "physical_fen": board_fen,
                 })
             prev_fen = board_fen
-        except Exception:
-            pass
+        except Exception as e:
+            logger.debug(f"[LABO] Lecture FEN échouée pendant copy_to_board : {e}")
         time.sleep(0.3)
     nl.turn_off_all_leds()
 
# ── Zone modifiée : ligne 949 (8 ligne(s)) dans l'ancienne version → ligne 955 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -949,8 +955,8 @@ def launch_labo_libre(config):
                 cfg = json.load(f)
             engine_elo  = cfg.get("engine_elo", 1500)
             engine_path = _validated_engine_path(cfg)
-        except Exception:
-            pass
+        except Exception as e:
+            logger.debug(f"Lecture config.json échouée, valeurs par défaut conservées : {e}")
 
     web_server._app_state = "connecting"
     set_app_state("connecting")
# ── Zone modifiée : ligne 1049 (7 ligne(s)) dans l'ancienne version → ligne 1055 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1049,7 +1055,7 @@ def _run_labo_libre(player_name, playing_white, start_fen, pause, analyse_active
     finally:
         if nl_inst:
             try: nl_inst.turn_off_all_leds()
-            except Exception: pass
+            except Exception: pass  # extinction LED best-effort — sans conséquence fonctionnelle
         if web_server._app_state not in ("menu",):
             web_server._app_state = "menu"
 
# ── Zone modifiée : ligne 1175 (9 ligne(s)) dans l'ancienne version → ligne 1181 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1175,9 +1181,10 @@ def explorer_cleanup() -> None:
     global _explorer_nl_inst, _explorer_session
     if _explorer_nl_inst is not None:
         try: _explorer_nl_inst.turn_off_all_leds()
-        except Exception: pass
+        except Exception: pass  # extinction LED best-effort — sans conséquence fonctionnelle
         try: _explorer_nl_inst.disconnect()
-        except Exception: pass
+        except Exception as e:
+            logger.warning(f"[EXPLORER] Déconnexion échiquier échouée : {e}")
     set_virtual_board(None)
     _explorer_nl_inst = None
     _explorer_session  = None
