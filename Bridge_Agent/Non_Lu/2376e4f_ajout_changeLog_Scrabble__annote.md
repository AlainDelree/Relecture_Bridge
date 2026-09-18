2376e4f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2376e4f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 01:48:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    ajout changeLog Scrabble

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 41b857b..dae0bd7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 201 (3 ligne(s)) dans l'ancienne version → ligne 201 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -201,3 +201,12 @@ while ($true) {
     $tailleAvant = $tailleActuelle
     Start-Sleep -Seconds $IntervalleSecondes
 }
+## ChangeLog Scrabble
+Le CHANGELOG.md du projet Scrabble (~\Scrabble/CHANGELOG.md) ne contient
+pas la ligne « Convention d'ajout : ... » attendue par
+scripts/fusionner_changelog.py (issue #336). Lors de la fusion de
+CHANGELOG-345.md, le script a supprimé le fichier sans fusionner son
+contenu (erreur : "en-tête fixe introuvable"). Tant que ce n'est pas
+corrigé, toutes les futures entrées de worktree Scrabble seront perdues
+à la fusion.
+
