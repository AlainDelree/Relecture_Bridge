360bc07

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 360bc07
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 10:13:01 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Supprime le secret .env local et nettoie .gitignore (retire .env, comptes_test.md)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ecb19f4..4209c0a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 22 (7 ligne(s)) dans l'ancienne version → ligne 22 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -22,7 +22,6 @@ staticfiles/
 local_settings.py
 
 # Variables d'environnement
-.env
 .env.local
 
 # Éditeurs
# ── Zone modifiée : ligne 34 (4 ligne(s)) dans l'ancienne version → ligne 33 (3 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -34,4 +33,3 @@ local_settings.py
 # OS
 .DS_Store
 Thumbs.db
-comptes_test.md
