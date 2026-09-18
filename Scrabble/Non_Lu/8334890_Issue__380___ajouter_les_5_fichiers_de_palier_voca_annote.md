8334890

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8334890
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 20:16:38 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #380 : ajouter les 5 fichiers de palier vocabulaire IA à ELEMENTS_DICTIONNAIRE (scrabble.spec)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scrabble.spec b/scrabble.spec
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b9ee94c..66e0cf5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/scrabble.spec
# ── Version APRÈS ce commit.
+++ b/scrabble.spec
# ── Zone modifiée : ligne 93 (6 ligne(s)) dans l'ancienne version → ligne 93 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -93,6 +93,11 @@ ELEMENTS_DICTIONNAIRE = [
     ("definitions.json", True),
     ("Lexique383.tsv", True),
     ("mots_courants.txt", True),
+    ("mots_courants_debutant.txt", True),
+    ("mots_courants_facile.txt", True),
+    ("mots_courants_intermediaire.txt", True),
+    ("mots_courants_avance.txt", True),
+    ("mots_courants_expert.txt", True),
     ("mots_ajoutes.txt", True),
     ("mots_ajoutes_hunspell.txt", True),
     ("mots_ajoutes_ods.txt", True),
