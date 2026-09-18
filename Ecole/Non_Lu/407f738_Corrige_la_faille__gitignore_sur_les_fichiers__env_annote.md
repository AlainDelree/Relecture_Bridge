407f738

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 407f738
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 12:27:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige la faille .gitignore sur les fichiers .env

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4209c0a..c5c8993 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 22 (7 ligne(s)) dans l'ancienne version → ligne 22 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -22,7 +22,8 @@ staticfiles/
 local_settings.py
 
 # Variables d'environnement
-.env.local
+.env*
+!.env.example
 
 # Éditeurs
 .vscode/
