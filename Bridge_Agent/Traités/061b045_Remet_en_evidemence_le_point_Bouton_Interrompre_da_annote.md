061b045

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 061b045
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 31 10:36:55 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Remet en evidemence le point Bouton Interrompre dans l'onglet CCW

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 132b5b5..d5e19bb 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 4 (6 ligne(s)) dans l'ancienne version → ligne 4 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,6 +4,7 @@ Idées et pistes non prioritaires, à réaliser éventuellement plus tard.
 Alain peut modifier ce fichier directement, sans passer par une issue.
 
 ---
+
 ##Bouton Interrompre dans l'onglet CCW
 
 Procédure : nssm restart CCW-Watcher, puis supprimer le(s) fichier(s)
