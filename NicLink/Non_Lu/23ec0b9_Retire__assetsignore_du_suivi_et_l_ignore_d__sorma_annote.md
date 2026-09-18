23ec0b9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 23ec0b9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 21:26:02 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Retire .assetsignore du suivi et l'ignore désormais (2e occurrence accidentelle, cf. issue #233) — évite une récidive future

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.assetsignore b/.assetsignore
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c9a2fd3..0000000
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.assetsignore
# ── Version APRÈS ce commit.
+++ /dev/null
# ── Zone modifiée : ligne 1 (1 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1 +0,0 @@
-.wrangler/tmp/**
# (diff du fichier suivant)
diff --git a/.gitignore b/.gitignore
# (index — ignorable)
index 5849dc0..b47a4fd 100755
# (avant — fichier suivant)
--- a/.gitignore
# (après — fichier suivant)
+++ b/.gitignore
# ── Zone modifiée : ligne 52 (3 ligne(s)) dans l'ancienne version → ligne 52 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -52,3 +52,5 @@ logs/
 
 # Parties (données perso / noms de tiers)
 games/
+.assetsignore
+.wrangler/
