76ecbbb

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 76ecbbb
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 22:59:13 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #265 : corriger la docstring de test_jeu.py et ajouter le garde-fou test_jeu_docstring.py

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/test_jeu.py b/tests/test_jeu.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f892053..db16740 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/tests/test_jeu.py
# ── Version APRÈS ce commit.
+++ b/tests/test_jeu.py
# ── Zone modifiée : ligne 8 (14 ligne(s)) dans l'ancienne version → ligne 8 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -8,14 +8,14 @@ Couvre :
 Note : ce fichier historique a été découpé en 10 fichiers spécialisés
 (issues #255 à #264). Les tests se trouvent désormais dans :
 
-- test_jeu_chevalet.py — tests du chevalet et de son affichage
+- test_jeu_brouillon.py — tests du brouillon de coup en cours de saisie
 - test_jeu_core_diffusion.py — tests du cœur de jeu et diffusion d'état
+- test_jeu_coup.py — tests de la validation et soumission d'un coup
 - test_jeu_echange.py — tests de l'échange de lettres
-- test_jeu_etat_public.py — tests de confidentialité de l'état public
-- test_jeu_fenetre.py — tests de la gestion de fenêtre pywebview
 - test_jeu_integration.py — tests de bout en bout (pose/persistance/reprise)
-- test_jeu_joker.py — tests spécifiques aux jokers
 - test_jeu_point_entree.py — tests du point d'entrée de l'écran de jeu
-- test_jeu_pose.py — tests de la pose de mots
+- test_jeu_pose.py — tests de la pose de mots sur le plateau
+- test_jeu_serialisation.py — tests de sérialisation/désérialisation de l'état
+- test_jeu_tirage_ordre.py — tests du tirage initial et de l'ordre des joueurs
 - test_jeu_tour_fin_partie.py — tests de gestion des tours et fin de partie
 """
# (diff du fichier suivant)
diff --git a/tests/test_jeu_docstring.py b/tests/test_jeu_docstring.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..9e89948
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_jeu_docstring.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,28 @@
+"""Garde-fou : vérifie que la docstring de test_jeu.py liste exactement les fichiers test_jeu_*.py existants (issue #265)."""
+
+import glob
+import re
+
+
+def test_docstring_liste_fichiers_coherente():
+    import tests.test_jeu as module_jeu
+
+    docstring = module_jeu.__doc__ or ""
+    mentionnes = set(re.findall(r"(test_jeu_\w+\.py)", docstring))
+
+    existants = {
+        f.split("/")[-1]
+        for f in glob.glob("tests/test_jeu_*.py")
+        if not f.endswith("test_jeu_docstring.py")
+    }
+
+    manquants = existants - mentionnes
+    fantomes = mentionnes - existants
+
+    messages = []
+    if manquants:
+        messages.append(f"Fichiers existants absents de la docstring : {sorted(manquants)}")
+    if fantomes:
+        messages.append(f"Fichiers mentionnés dans la docstring mais inexistants : {sorted(fantomes)}")
+
+    assert not messages, "\n".join(messages)
