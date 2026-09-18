d9e7cd2

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d9e7cd2
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 18:37:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Publication v3 : bascule sécurisée par dossier temporaire + renommage (issue #29)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/version.json b/version.json
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5a66145..c8120a6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/version.json
# ── Version APRÈS ce commit.
+++ b/version.json
# ── Zone modifiée : ligne 1 (1 ligne(s)) dans l'ancienne version → ligne 1 (1 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1 +1 @@
-{"build": 2, "sha256": "4ea166fd661df65147ca53f11b6d6ff466f850a2a33a279381db3de9ca6f1cc9"}
+{"build": 3, "sha256": "71e8e0f89ba7811ed982bda6e989df0605f9399e247c066fd884c51c115e46d7"}
