bcbb822

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bcbb822
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 10:08:30 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige les tests e2e dépendants de textes traduits (issue #208)
    
    Remplace les filtres has_text sur du texte français par des sélecteurs
    stables (onclick/classe/id) dans test_smoke_e2e.py, indépendants de la
    locale par défaut EN de Playwright. TACHES.md (local, non suivi git)
    liste les cas non corrigés : bug de navigation structurel séparé
    (bouton Exercices devenu une carte, plus un <button>) et
    test_outils_exercices_e2e.py qui présente le même risque sur
    la quasi-totalité de ses tests.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/tests/e2e/test_smoke_e2e.py b/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 83c796e..64a81ba 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Zone modifiée : ligne 51 (7 ligne(s)) dans l'ancienne version → ligne 51 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -51,7 +51,9 @@ def test_retour_depuis_config(at_menu):
     """Config pédagogique → Retour → menu."""
     at_menu.locator(".menu-card-primary .menu-card-head").click()
     at_menu.wait_for_selector("#screen-config", state="visible", timeout=5000)
-    at_menu.locator("#screen-config button", has_text="Retour").click()
+    # Ciblage par attribut onclick plutôt que par texte traduit (issue #208) —
+    # le texte du bouton dépend de la locale (FR "Retour" / EN "Back").
+    at_menu.locator("#screen-config button[onclick*=\"type:'back'\"]").click()
     at_menu.wait_for_selector("#screen-menu", state="visible", timeout=5000)
     assert at_menu.locator("#screen-menu").is_visible()
 
# ── Zone modifiée : ligne 61 (15 ligne(s)) dans l'ancienne version → ligne 63 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -61,15 +63,15 @@ def test_pedagogique_demarrer_puis_retour_menu(at_menu):
     at_menu.locator(".menu-card-primary .menu-card-head").click()
     at_menu.wait_for_selector("#screen-config", state="visible", timeout=5000)
 
-    # Démarrer la partie (VirtualBoard + Stockfish) — cibler le bouton dans l'écran config pédagogique
-    at_menu.locator("#screen-config button", has_text="Démarrer la partie").click()
+    # Démarrer la partie (VirtualBoard + Stockfish) — id stable, indépendant de la locale (issue #208)
+    at_menu.locator("#btn-start-peda").click()
 
     # Attendre le panel-playing (state=playing)
     at_menu.wait_for_selector("#panel-playing", state="visible", timeout=30000)
     assert at_menu.locator("#panel-playing").is_visible()
 
-    # Retour au menu — cibler panel-playing pour éviter l'ambiguïté avec les autres panels
-    at_menu.locator("#panel-playing button", has_text="Retour au menu").click()
+    # Retour au menu — ciblage par attribut onclick, indépendant de la locale (issue #208)
+    at_menu.locator("#panel-playing button[onclick*=\"back_menu\"]").click()
     # Confirmer dans la modal
     modal = at_menu.locator("#modal-overlay")
     if modal.is_visible():
# ── Zone modifiée : ligne 84 (7 ligne(s)) dans l'ancienne version → ligne 86 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -84,7 +86,8 @@ def test_pedagogique_demarrer_puis_retour_menu(at_menu):
 def test_hh_ouvre_config(at_menu):
     """Clic HH → écran config HH (non disponible en mode virtuel — bouton absent)."""
     # HH a data-physical-only donc désactivé en mode virtuel
-    btn_hh = at_menu.locator("button", has_text="Humain vs Humain")
+    # Ciblage par classe CSS, indépendant de la locale (issue #208)
+    btn_hh = at_menu.locator("button.menu-btn-humain")
     if not btn_hh.is_visible() or btn_hh.is_disabled():
         pytest.skip("HH désactivé en mode virtuel (data-physical-only) — OK")
     btn_hh.click()
# ── Zone modifiée : ligne 97 (7 ligne(s)) dans l'ancienne version → ligne 100 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -97,7 +100,8 @@ def test_hh_ouvre_config(at_menu):
 
 def test_analyse_accessible_sans_board(at_menu):
     """Analyse de partie accessible sans échiquier (pas de data-needs-board)."""
-    at_menu.locator("button", has_text="Analyse de partie").click()
+    # Ciblage par classe CSS, indépendant de la locale (issue #208)
+    at_menu.locator("button.menu-btn-analyse").click()
     # Analyse → app_state = game_over (écran de review)
     at_menu.wait_for_selector("#screen-game", state="visible", timeout=5000)
     assert at_menu.locator("#panel-gameover").is_visible()
# ── Zone modifiée : ligne 106 (10 ligne(s)) dans l'ancienne version → ligne 110 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -106,10 +110,11 @@ def test_analyse_accessible_sans_board(at_menu):
 def test_retour_depuis_analyse(at_menu):
     """Analyse → Retour au menu → menu propre."""
     if not at_menu.locator("#panel-gameover").is_visible():
-        at_menu.locator("button", has_text="Analyse de partie").click()
+        at_menu.locator("button.menu-btn-analyse").click()
         at_menu.wait_for_selector("#panel-gameover", state="visible", timeout=5000)
 
-    at_menu.locator("#panel-gameover button", has_text="Retour au menu").click()
+    # Ciblage par attribut onclick, indépendant de la locale (issue #208)
+    at_menu.locator("#panel-gameover button[onclick*=\"back_menu\"]").click()
     at_menu.wait_for_selector("#screen-menu", state="visible", timeout=5000)
     assert at_menu.locator("#screen-menu").is_visible()
 
# ── Zone modifiée : ligne 141 (7 ligne(s)) dans l'ancienne version → ligne 146 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -141,7 +146,8 @@ def test_retour_depuis_exercices(at_menu):
 
 def test_retranscription_formulaire(at_menu):
     """Retranscrire → formulaire visible."""
-    at_menu.locator("button", has_text="Retranscrire").click()
+    # Ciblage par classe CSS, indépendant de la locale (issue #208)
+    at_menu.locator("button.menu-btn-retrans").click()
     at_menu.wait_for_selector("#screen-retranscription", state="visible", timeout=5000)
     assert at_menu.locator("#screen-retranscription").is_visible()
     go_menu(at_menu)
# ── Zone modifiée : ligne 151 (10 ligne(s)) dans l'ancienne version → ligne 157 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -151,10 +157,10 @@ def test_retranscription_formulaire(at_menu):
 
 def test_transition_analyse_puis_menu(at_menu):
     """Analyse → Retour → Pédagogique config — pas de résidu."""
-    # Analyse
-    at_menu.locator("button", has_text="Analyse de partie").click()
+    # Analyse — ciblage par classe CSS / attribut onclick, indépendant de la locale (issue #208)
+    at_menu.locator("button.menu-btn-analyse").click()
     at_menu.wait_for_selector("#panel-gameover", state="visible", timeout=5000)
-    at_menu.locator("#panel-gameover button", has_text="Retour au menu").click()
+    at_menu.locator("#panel-gameover button[onclick*=\"back_menu\"]").click()
     at_menu.wait_for_selector("#screen-menu", state="visible", timeout=5000)
 
     # Pédagogique config → vérifier état propre
