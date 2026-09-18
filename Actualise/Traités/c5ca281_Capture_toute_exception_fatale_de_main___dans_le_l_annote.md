c5ca281

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c5ca281
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 06:42:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Capture toute exception fatale de main() dans le log (issue #22, suite #9)
    
    Enveloppe le corps de main() (après configurer_logging()) dans un
    try/except Exception global : logue la stack trace complète via
    _LOGGER.exception() puis relève l'exception, pour qu'actualise.log ne
    reste plus vide en --noconsole quand une exception non anticipée
    remonte jusqu'en haut de main(). SystemExit (ex. le SystemExit(0) du
    garde-fou anti-boucle) n'est pas intercepté, hérite de BaseException.
    
    Tests ajoutés dans tests/test_actualise.py (TestMain) : exception
    fatale loguée + propagée, et non-régression du SystemExit(0) de
    relance --child (ni intercepté ni logué comme erreur).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/actualise.py b/actualise.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index af081e7..99efb46 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/actualise.py
# ── Version APRÈS ce commit.
+++ b/actualise.py
# ── Zone modifiée : ligne 318 (29 ligne(s)) dans l'ancienne version → ligne 318 (43 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -318,29 +318,43 @@ def main(argv: list[str] | None = None) -> int:
     """
     configurer_logging()
 
-    arguments = analyser_arguments(argv)
-
-    # Étape 4 : bascule des mises à jour déjà téléchargées et validées
-    # au cycle précédent (sautée pour Actualise si --child est présent).
-    # Si une bascule d'Actualise lui-même vient d'avoir lieu, cette
-    # fonction termine le process (SystemExit) avant de revenir ici.
-    appliquer_mises_a_jour_en_attente(est_enfant=arguments.child)
-
-    # Étape 2 : lancement immédiat de l'application cible, sans attendre
-    # le réseau.
-    lancer_application_cible()
-
-    # Étape 3 : vérification et téléchargement en arrière-plan, sans
-    # bloquer l'utilisateur.
-    thread_verification = threading.Thread(
-        target=tache_verification_arriere_plan, daemon=True
-    )
-    thread_verification.start()
+    # Bloc englobant : sans lui, une exception non anticipée par les
+    # except existants (ex. config.json absent dès le tout premier
+    # lancement) remonte jusqu'à --noconsole sans jamais être loguée —
+    # seule une popup Windows technique s'affiche, sans rien
+    # d'exploitable conservé pour diagnostiquer à distance. On logue ici
+    # la stack trace complète puis on laisse l'exception se propager
+    # (code de sortie non nul inchangé) : le but est d'ajouter la trace
+    # au log, pas de supprimer le crash. ``SystemExit`` (ex. le
+    # ``SystemExit(0)`` volontaire du garde-fou anti-boucle) hérite de
+    # ``BaseException`` et n'est donc jamais intercepté ici.
+    try:
+        arguments = analyser_arguments(argv)
+
+        # Étape 4 : bascule des mises à jour déjà téléchargées et validées
+        # au cycle précédent (sautée pour Actualise si --child est présent).
+        # Si une bascule d'Actualise lui-même vient d'avoir lieu, cette
+        # fonction termine le process (SystemExit) avant de revenir ici.
+        appliquer_mises_a_jour_en_attente(est_enfant=arguments.child)
+
+        # Étape 2 : lancement immédiat de l'application cible, sans attendre
+        # le réseau.
+        lancer_application_cible()
+
+        # Étape 3 : vérification et téléchargement en arrière-plan, sans
+        # bloquer l'utilisateur.
+        thread_verification = threading.Thread(
+            target=tache_verification_arriere_plan, daemon=True
+        )
+        thread_verification.start()
 
-    # Cycle de vie d'Actualise : on attend la fin de la tâche de fond
-    # (pas celle de l'application cible) avant de terminer — voir
-    # CONCEPTION.md, « Cycle de vie du processus Actualise ».
-    thread_verification.join()
+        # Cycle de vie d'Actualise : on attend la fin de la tâche de fond
+        # (pas celle de l'application cible) avant de terminer — voir
+        # CONCEPTION.md, « Cycle de vie du processus Actualise ».
+        thread_verification.join()
+    except Exception:
+        _LOGGER.exception("Actualise s'est arrêté sur une erreur fatale non gérée.")
+        raise
 
     return 0
 
# (diff du fichier suivant)
diff --git a/tests/test_actualise.py b/tests/test_actualise.py
# (index — ignorable)
index f324523..14e2b66 100644
# (avant — fichier suivant)
--- a/tests/test_actualise.py
# (après — fichier suivant)
+++ b/tests/test_actualise.py
# ── Zone modifiée : ligne 19 (6 ligne(s)) dans l'ancienne version → ligne 19 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -19,6 +19,7 @@ from actualise import (
     appliquer_mises_a_jour_en_attente,
     configurer_logging,
     lancer_application_cible,
+    main,
     tache_verification_arriere_plan,
 )
 
# ── Zone modifiée : ligne 336 (5 ligne(s)) dans l'ancienne version → ligne 337 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -336,5 +337,42 @@ class TestTacheVerificationArrierePlan(unittest.TestCase):
             tache_verification_arriere_plan()
 
 
+class TestMain(unittest.TestCase):
+    """Voir CONCEPTION.md : ``main()`` doit loguer toute exception fatale
+    non anticipée par les except existants avant de la laisser se
+    propager (sinon ``actualise.log`` reste vide en ``--noconsole``),
+    sans jamais intercepter le ``SystemExit(0)`` volontaire du garde-fou
+    anti-boucle.
+    """
+
+    def setUp(self):
+        self.dossier_temp = tempfile.TemporaryDirectory()
+        self.addCleanup(self.dossier_temp.cleanup)
+
+        patcher_config = patch("actualise.config")
+        self.mock_config = patcher_config.start()
+        self.addCleanup(patcher_config.stop)
+        self.mock_config.chemin_config_portable.return_value = Path(self.dossier_temp.name)
+
+    def test_exception_fatale_dans_main_loguee_et_propagee(self):
+        with patch("actualise.appliquer_mises_a_jour_en_attente"), patch(
+            "actualise.lancer_application_cible", side_effect=RuntimeError("boum fatal")
+        ), self.assertLogs("actualise", level="ERROR") as journal:
+            with self.assertRaises(RuntimeError):
+                main([])
+
+        self.assertTrue(any("erreur fatale" in message for message in journal.output))
+
+    def test_systemexit_relance_enfant_non_intercepte_ni_logue_comme_erreur(self):
+        with patch(
+            "actualise.appliquer_mises_a_jour_en_attente", side_effect=SystemExit(0)
+        ), patch("actualise.lancer_application_cible") as mock_lancer:
+            with self.assertNoLogs("actualise", level="ERROR"):
+                with self.assertRaises(SystemExit):
+                    main([])
+
+            mock_lancer.assert_not_called()
+
+
 if __name__ == "__main__":
     unittest.main()
