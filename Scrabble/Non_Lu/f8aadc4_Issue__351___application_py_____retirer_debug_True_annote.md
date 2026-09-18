f8aadc4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f8aadc4
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 17:35:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #351 : application.py — retirer debug=True de webview.start()

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/application.py b/src/scrabble/ui/application.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d8ec791..2d90ae0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/application.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/application.py
# ── Zone modifiée : ligne 560 (9 ligne(s)) dans l'ancienne version → ligne 560 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -560,9 +560,7 @@ def lancer_application_unifiee(routeur: ApiRouteur | None = None) -> ApiRouteur:
             "Application unifiée : fenêtre unique ouverte sur l'accueil."
         )
         # UNE seule boucle pywebview pour toute l'application (issue #179).
-        # debug=True (issue #343) : ouvre les DevTools (F12) pour diagnostiquer
-        # l'animation de pioche sur WebView2 Windows, absente sous WebKitGTK Linux.
-        webview.start(deployer_fenetre_maximisee, (window, "application"), debug=True)
+        webview.start(deployer_fenetre_maximisee, (window, "application"))
         return routeur
     finally:
         journal.cloturer_session()
