28bee1d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 28bee1d
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 15:02:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #416 : retrait de mots_courants_expert.txt de ELEMENTS_DICTIONNAIRE (scrabble.spec) + mise à jour data/dictionnaire/README.md (4 paliers de fichier, plus 5)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/data/dictionnaire/README.md b/data/dictionnaire/README.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ccfc0f2..06c0552 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/data/dictionnaire/README.md
# ── Version APRÈS ce commit.
+++ b/data/dictionnaire/README.md
# ── Zone modifiée : ligne 28 (17 ligne(s)) dans l'ancienne version → ligne 28 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,17 +28,17 @@ Déposez manuellement ici, à cet emplacement, sans les ajouter au suivi git :
   Se régénère à tout moment ; n'a pas à être déposé manuellement.
 
 - `mots_courants_debutant.txt`, `mots_courants_facile.txt`,
-  `mots_courants_intermediaire.txt`, `mots_courants_avance.txt`,
-  `mots_courants_expert.txt` — vocabulaire IA par palier de difficulté (issue
-  #366, lot A), même croisement ODS8 × Lexique 3 à cinq seuils de fréquence
-  différents (respectivement ≥ 3,0, ≥ 2,0, ≥ 1,0, ≥ 0,5 et l'intersection
-  brute sans seuil pour Expert). Se produisent **tous en une seule commande** :
+  `mots_courants_intermediaire.txt`, `mots_courants_avance.txt` — vocabulaire
+  IA par palier de difficulté (issue #366, lot A ; refonte de l'échelle de
+  niveaux issue #401/#404), même croisement ODS8 × Lexique 3 à quatre seuils
+  de fréquence différents (respectivement ≥ 3,0, ≥ 2,0, ≥ 1,0 et ≥ 0,5). Se
+  produisent **tous en une seule commande** :
 
       python scripts/generer_mots_courants.py --tous
 
-  Le sixième palier, **Champion du monde**, ne nécessite **aucun fichier** :
-  il correspond à l'ODS8 complet, servi directement depuis le Trie déjà
-  chargé (`obtenir_trie()`). Ces cinq fichiers sont des sorties purement
+  Expert et Champion du monde ne nécessitent **aucun fichier** : ils
+  correspondent à l'ODS8 complet, servi directement depuis le Trie déjà
+  chargé (`obtenir_trie()`). Ces quatre fichiers sont des sorties purement
   dérivées (jamais éditées à la main) : la commande ci-dessus les réécrit
   systématiquement, sans confirmation ni `--force`.
 
# (diff du fichier suivant)
diff --git a/scrabble.spec b/scrabble.spec
# (index — ignorable)
index e3090dc..749f688 100644
# (avant — fichier suivant)
--- a/scrabble.spec
# (après — fichier suivant)
+++ b/scrabble.spec
# ── Zone modifiée : ligne 97 (7 ligne(s)) dans l'ancienne version → ligne 97 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -97,7 +97,6 @@ ELEMENTS_DICTIONNAIRE = [
     ("mots_courants_facile.txt", True),
     ("mots_courants_intermediaire.txt", True),
     ("mots_courants_avance.txt", True),
-    ("mots_courants_expert.txt", True),
     ("mots_ajoutes.txt", True),
     ("mots_ajoutes_hunspell.txt", True),
     ("mots_ajoutes_ods.txt", True),
