f5cd2de

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f5cd2de
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 16:24:58 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Publication v2 : chemin de config relatif à l'exécutable (multi-instances)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/version.json b/version.json
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0c05d7a..5a66145 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/version.json
# ── Version APRÈS ce commit.
+++ b/version.json
# ── Zone modifiée : ligne 1 (1 ligne(s)) dans l'ancienne version → ligne 1 (1 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1 +1 @@
-{"build": 1, "sha256": "adcef67c4c66779a4e09df4c43c15124476b66411d05e1b1847c10b772f06ac8"}
+{"build": 2, "sha256": "4ea166fd661df65147ca53f11b6d6ff466f850a2a33a279381db3de9ca6f1cc9"}
