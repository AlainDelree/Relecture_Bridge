# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2862c959932712d87a780b3d96166b8a97f9bb40
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 05:58:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #229 : nettoyage — suppression des stubs morts, du squelette web/ orphelin et des README de test
    
    Supprime les fichiers reliquats jamais importés ni référencés (vérifié par grep -rn) :
    - stubs Python non implémentés : moteur/regles.py, generateur/{generateur,__init__}.py,
      ia/{ia,__init__}.py, interface/{app,__init__}.py (+ dossiers vides)
    - squelette web/ racine orphelin : app.js, index.html, style.css (+ dossier)
    - README de test artefacts : README.md et README2.md (contenu unique '# test hook')
    
    pytest : 746 passed, 1 failed préexistant sans rapport
    (TestCalculerAvatars, échoue déjà sur le commit précédent).
    py_compile src/ + main.py : OK.
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/README.md b/README.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1bc64c4..0000000
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/README.md
# ── Version APRÈS ce commit.
+++ /dev/null
# ── Zone modifiée : ligne 1 (2 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,2 +0,0 @@
-# test hook
-# test hook
# (diff du fichier suivant)
diff --git a/README2.md b/README2.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 2d9884b..0000000
# (avant — fichier suivant)
--- a/README2.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (1 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1 +0,0 @@
-# test hook
# (diff du fichier suivant)
diff --git a/src/scrabble/generateur/__init__.py b/src/scrabble/generateur/__init__.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index a5086ed..0000000
# (avant — fichier suivant)
--- a/src/scrabble/generateur/__init__.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +0,0 @@
-"""Sous-paquet générateur de coups.
-
-Rôle : énumérer les coups légaux possibles à partir d'un chevalet et de l'état
-du plateau, en s'appuyant sur le dictionnaire et le moteur. Non implémenté à
-ce stade.
-"""
# (diff du fichier suivant)
diff --git a/src/scrabble/generateur/generateur.py b/src/scrabble/generateur/generateur.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 48fcb51..0000000
# (avant — fichier suivant)
--- a/src/scrabble/generateur/generateur.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +0,0 @@
-"""Génération des coups légaux.
-
-Rôle : produire l'ensemble des placements valides (mot, position, direction,
-score) pour un chevalet donné. Non implémenté à ce stade.
-"""
# (diff du fichier suivant)
diff --git a/src/scrabble/ia/__init__.py b/src/scrabble/ia/__init__.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 2db4b1e..0000000
# (avant — fichier suivant)
--- a/src/scrabble/ia/__init__.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +0,0 @@
-"""Sous-paquet IA.
-
-Rôle : choisir un coup parmi ceux proposés par le générateur selon un niveau
-de jeu (``debutant``, ``amateur``, ``expert`` — voir ``scrabble.config``).
-Non implémenté à ce stade.
-"""
# (diff du fichier suivant)
diff --git a/src/scrabble/ia/ia.py b/src/scrabble/ia/ia.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 996fa53..0000000
# (avant — fichier suivant)
--- a/src/scrabble/ia/ia.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +0,0 @@
-"""Stratégie de l'adversaire artificiel.
-
-Rôle : sélectionner un coup en fonction du niveau configuré (du plus faible au
-plus fort), à partir des coups fournis par le générateur. Non implémenté à ce
-stade.
-"""
# (diff du fichier suivant)
diff --git a/src/scrabble/interface/__init__.py b/src/scrabble/interface/__init__.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index ce77996..0000000
# (avant — fichier suivant)
--- a/src/scrabble/interface/__init__.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +0,0 @@
-"""Sous-paquet interface.
-
-Rôle : exposer l'interface graphique via pywebview (pont entre le front web du
-dossier ``web/`` et le moteur Python). Non implémenté à ce stade.
-"""
# (diff du fichier suivant)
diff --git a/src/scrabble/interface/app.py b/src/scrabble/interface/app.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index f4fdaa1..0000000
# (avant — fichier suivant)
--- a/src/scrabble/interface/app.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +0,0 @@
-"""Point d'entrée de l'interface pywebview.
-
-Rôle : créer la fenêtre pywebview chargeant ``web/index.html`` et exposer une
-API Python au front (mode de saisie clic/clavier selon ``scrabble.config``).
-Non implémenté à ce stade.
-"""
# (diff du fichier suivant)
diff --git a/src/scrabble/moteur/regles.py b/src/scrabble/moteur/regles.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index b8010c7..0000000
# (avant — fichier suivant)
--- a/src/scrabble/moteur/regles.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +0,0 @@
-"""Règles et calcul des scores.
-
-Rôle : valider un coup (mots croisés formés, connexité), calculer le score
-d'un placement et gérer le déroulement d'une partie. Non implémenté à ce stade.
-"""
# (diff du fichier suivant)
diff --git a/web/app.js b/web/app.js
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 1715a26..0000000
# (avant — fichier suivant)
--- a/web/app.js
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (3 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,3 +0,0 @@
-// Logique côté front du Scrabble (chargée par pywebview).
-// Rôle : rendu du plateau et dialogue avec l'API Python exposée par
-// scrabble.interface. Squelette sans logique.
# (diff du fichier suivant)
diff --git a/web/index.html b/web/index.html
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index bd76b52..0000000
# (avant — fichier suivant)
--- a/web/index.html
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (18 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,18 +0,0 @@
-<!DOCTYPE html>
-<!--
-  Front web du Scrabble (chargé par pywebview).
-  Rôle : affichage du plateau et des chevalets. Squelette sans logique.
--->
-<html lang="fr">
-  <head>
-    <meta charset="utf-8" />
-    <meta name="viewport" content="width=device-width, initial-scale=1" />
-    <title>Scrabble</title>
-    <link rel="stylesheet" href="style.css" />
-  </head>
-  <body>
-    <!-- Le plateau et les chevalets seront injectés ici. -->
-    <div id="app"></div>
-    <script src="app.js"></script>
-  </body>
-</html>
# (diff du fichier suivant)
diff --git a/web/style.css b/web/style.css
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 0c64f01..0000000
# (avant — fichier suivant)
--- a/web/style.css
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (4 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,4 +0,0 @@
-/*
- * Feuille de style du front web du Scrabble.
- * Rôle : mise en page du plateau et des chevalets. Squelette sans styles réels.
- */
