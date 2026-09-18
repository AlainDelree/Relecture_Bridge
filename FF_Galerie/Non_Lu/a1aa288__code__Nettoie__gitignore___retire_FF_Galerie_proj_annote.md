a1aa288

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a1aa288
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 10:13:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    [code] Nettoie .gitignore : retire FF_Galerie_projet.md et Notes perso/ (docs perso déménagés) (#103)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index bf52c73..32fdc04 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 1 (10 ligne(s)) dans l'ancienne version → ligne 1 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,10 +1,8 @@
 data/prix.json
 node_modules/
 .DS_Store
-FF_Galerie_projet.md
 
 # Notes et fichiers de travail personnels
-Notes perso/
 Site Fred.md
 *.old.*
 node_modules
