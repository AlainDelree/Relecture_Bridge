c257095

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c257095
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 1 23:26:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #342 : CONFIG_DEFAUT — bonus_fin_partie/theme_plateau/vocabulaire_humain par défaut pour Béatrice

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/config.py b/src/scrabble/config.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 34f17a7..e716c27 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/config.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/config.py
# ── Zone modifiée : ligne 48 (23 ligne(s)) dans l'ancienne version → ligne 48 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -48,23 +48,26 @@ CONFIG_DEFAUT: dict[str, Any] = {
     # réparée vers la chaîne vide.
     "avatar_principal": "",
     # Thème visuel (habillage couleurs/étiquettes) du plateau de l'écran de jeu.
-    # Voir THEMES_PLATEAU pour les valeurs acceptées ; défaut = "classique".
-    "theme_plateau": "classique",
+    # Voir THEMES_PLATEAU pour les valeurs acceptées ; défaut = "vert" (issue #342,
+    # préférence de Béatrice, utilisatrice cible).
+    "theme_plateau": "vert",
     # Bonus officiel au finisseur (issue #134) : quand activé, le joueur qui
     # écoule toutes ses lettres en premier reçoit la somme des lettres restant
     # chez les autres joueurs, en plus de la pénalité qui leur est déjà
-    # appliquée. Désactivé par défaut : le comportement historique (pénalité
-    # seule, issue #22) reste inchangé pour qui ne touche pas à ce réglage.
-    "bonus_fin_partie": False,
+    # appliquée. Activé par défaut (issue #342, préférence de Béatrice,
+    # utilisatrice cible) : le comportement historique (pénalité seule,
+    # issue #22) reste accessible en désactivant ce réglage.
+    "bonus_fin_partie": True,
     # Vocabulaire humain de l'IA (issue #206) : quand activé, l'IA (tous niveaux
     # confondus) ne choisit ses coups que parmi les mots « courants »
     # (``mots_courants.txt``, issue #205) et les « classiques du jeu » (statut de
     # l'issue #204, WU/SIX/ZOO…), plutôt que dans tout le dictionnaire. Réglage
-    # global unique, indépendant du niveau de difficulté. Désactivé par défaut :
-    # le comportement historique (IA sur le dictionnaire complet) reste inchangé
-    # tant qu'on n'y touche pas. N'affecte jamais ce que le joueur humain peut
-    # jouer ou vérifier (``valider_coup`` reste sur le dictionnaire complet).
-    "vocabulaire_humain": False,
+    # global unique, indépendant du niveau de difficulté. Activé par défaut
+    # (issue #342, préférence de Béatrice, utilisatrice cible) : le comportement
+    # historique (IA sur le dictionnaire complet) reste accessible en désactivant
+    # ce réglage. N'affecte jamais ce que le joueur humain peut jouer ou
+    # vérifier (``valider_coup`` reste sur le dictionnaire complet).
+    "vocabulaire_humain": True,
     # Type d'échange des lettres autorisé pendant un tour (issue #138) :
     # "complet" (défaut, comportement historique : on remet tout le chevalet et
     # on repioche sept lettres) ou "partiel" (le joueur choisit librement une à
# (diff du fichier suivant)
diff --git a/tests/test_config.py b/tests/test_config.py
# (index — ignorable)
index 6503559..e49a772 100644
# (avant — fichier suivant)
--- a/tests/test_config.py
# (après — fichier suivant)
+++ b/tests/test_config.py
# ── Zone modifiée : ligne 192 (14 ligne(s)) dans l'ancienne version → ligne 192 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -192,14 +192,14 @@ def test_prenom_principal_mauvais_type_repare(tmp_path):
     assert json.loads(chemin.read_text(encoding="utf-8"))["prenom_principal"] == ""
 
 
-def test_theme_plateau_defaut_classique(tmp_path):
-    """Le thème de plateau par défaut est « classique »."""
+def test_theme_plateau_defaut_vert(tmp_path):
+    """Le thème de plateau par défaut est « vert » (issue #342)."""
     chemin = tmp_path / "config.json"
 
     config = charger_config(chemin)
 
-    assert config["theme_plateau"] == "classique"
-    assert CONFIG_DEFAUT["theme_plateau"] == "classique"
+    assert config["theme_plateau"] == "vert"
+    assert CONFIG_DEFAUT["theme_plateau"] == "vert"
     # Le défaut fait partie des thèmes reconnus.
     assert CONFIG_DEFAUT["theme_plateau"] in THEMES_PLATEAU
 
# ── Zone modifiée : ligne 218 (7 ligne(s)) dans l'ancienne version → ligne 218 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -218,7 +218,7 @@ def test_theme_plateau_valeurs_valides_conservees(tmp_path, theme):
 
 
 def test_theme_plateau_valeur_invalide_reparee(tmp_path):
-    """Un thème inconnu retombe sur le défaut « classique » et le fichier est réparé."""
+    """Un thème inconnu retombe sur le défaut « vert » et le fichier est réparé."""
     chemin = tmp_path / "config.json"
     chemin.write_text(
         json.dumps({"theme_plateau": "fluo-arc-en-ciel"}), encoding="utf-8"
# ── Zone modifiée : ligne 226 (10 ligne(s)) dans l'ancienne version → ligne 226 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -226,10 +226,10 @@ def test_theme_plateau_valeur_invalide_reparee(tmp_path):
 
     config = charger_config(chemin)
 
-    assert config["theme_plateau"] == "classique"
+    assert config["theme_plateau"] == "vert"
     # La réparation est persistée sur disque.
     releu = json.loads(chemin.read_text(encoding="utf-8"))
-    assert releu["theme_plateau"] == "classique"
+    assert releu["theme_plateau"] == "vert"
 
 
 def test_theme_plateau_vide_repare(tmp_path):
# ── Zone modifiée : ligne 239 (17 ligne(s)) dans l'ancienne version → ligne 239 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -239,17 +239,17 @@ def test_theme_plateau_vide_repare(tmp_path):
 
     config = charger_config(chemin)
 
-    assert config["theme_plateau"] == "classique"
+    assert config["theme_plateau"] == "vert"
 
 
 def test_theme_plateau_mauvais_type_repare(tmp_path):
-    """Un thème du mauvais type retombe sur le défaut « classique »."""
+    """Un thème du mauvais type retombe sur le défaut « vert »."""
     chemin = tmp_path / "config.json"
     chemin.write_text(json.dumps({"theme_plateau": 7}), encoding="utf-8")
 
     config = charger_config(chemin)
 
-    assert config["theme_plateau"] == "classique"
+    assert config["theme_plateau"] == "vert"
 
 
 def test_type_echange_complet_par_defaut(tmp_path):
# ── Zone modifiée : ligne 301 (14 ligne(s)) dans l'ancienne version → ligne 301 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -301,14 +301,14 @@ def test_type_echange_vide_repare(tmp_path):
     assert config["type_echange"] == "complet"
 
 
-def test_bonus_fin_partie_desactive_par_defaut(tmp_path):
-    """Le bonus au finisseur (issue #134) est désactivé par défaut."""
+def test_bonus_fin_partie_active_par_defaut(tmp_path):
+    """Le bonus au finisseur (issue #134) est activé par défaut (issue #342)."""
     chemin = tmp_path / "config.json"
 
     config = charger_config(chemin)
 
-    assert config["bonus_fin_partie"] is False
-    assert CONFIG_DEFAUT["bonus_fin_partie"] is False
+    assert config["bonus_fin_partie"] is True
+    assert CONFIG_DEFAUT["bonus_fin_partie"] is True
 
 
 @pytest.mark.parametrize("valeur", [True, False])
# ── Zone modifiée : ligne 334 (23 ligne(s)) dans l'ancienne version → ligne 334 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -334,23 +334,23 @@ def test_bonus_fin_partie_valeur_non_booleenne_reparee(tmp_path, invalide):
 
     config = charger_config(chemin)
 
-    assert config["bonus_fin_partie"] is False
+    assert config["bonus_fin_partie"] is True
     releu = json.loads(chemin.read_text(encoding="utf-8"))
-    assert releu["bonus_fin_partie"] is False
+    assert releu["bonus_fin_partie"] is True
 
 
 # --------------------------------------------------------------------------- #
 # Vocabulaire humain de l'IA (issue #206)
 # --------------------------------------------------------------------------- #
 
-def test_vocabulaire_humain_desactive_par_defaut(tmp_path):
-    """Le réglage « vocabulaire humain » (issue #206) est désactivé par défaut."""
+def test_vocabulaire_humain_active_par_defaut(tmp_path):
+    """Le réglage « vocabulaire humain » (issue #206) est activé par défaut (issue #342)."""
     chemin = tmp_path / "config.json"
 
     config = charger_config(chemin)
 
-    assert config["vocabulaire_humain"] is False
-    assert CONFIG_DEFAUT["vocabulaire_humain"] is False
+    assert config["vocabulaire_humain"] is True
+    assert CONFIG_DEFAUT["vocabulaire_humain"] is True
 
 
 @pytest.mark.parametrize("valeur", [True, False])
# ── Zone modifiée : ligne 376 (9 ligne(s)) dans l'ancienne version → ligne 376 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -376,9 +376,9 @@ def test_vocabulaire_humain_valeur_non_booleenne_reparee(tmp_path, invalide):
 
     config = charger_config(chemin)
 
-    assert config["vocabulaire_humain"] is False
+    assert config["vocabulaire_humain"] is True
     releu = json.loads(chemin.read_text(encoding="utf-8"))
-    assert releu["vocabulaire_humain"] is False
+    assert releu["vocabulaire_humain"] is True
 
 
 # --------------------------------------------------------------------------- #
# (diff du fichier suivant)
diff --git a/tests/test_reglages.py b/tests/test_reglages.py
# (index — ignorable)
index 089ac66..7a63dd4 100644
# (avant — fichier suivant)
--- a/tests/test_reglages.py
# (après — fichier suivant)
+++ b/tests/test_reglages.py
# ── Zone modifiée : ligne 81 (13 ligne(s)) dans l'ancienne version → ligne 81 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -81,13 +81,13 @@ def test_modifier_theme_plateau_valide(tmp_path):
 
 
 def test_modifier_theme_plateau_invalide_retombe_sur_defaut(tmp_path):
-    """Un thème inconnu est normalisé vers le défaut « classique »."""
+    """Un thème inconnu est normalisé vers le défaut « vert »."""
     chemin = tmp_path / "config.json"
 
     retenue = modifier_reglage("theme_plateau", "inexistant", chemin)
 
-    assert retenue == "classique"
-    assert lire_reglage("theme_plateau", chemin) == "classique"
+    assert retenue == "vert"
+    assert lire_reglage("theme_plateau", chemin) == "vert"
 
 
 @pytest.mark.parametrize("valeur", [True, False])
