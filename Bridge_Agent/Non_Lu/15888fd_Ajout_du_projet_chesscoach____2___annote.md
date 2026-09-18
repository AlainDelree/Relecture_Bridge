15888fd

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 15888fd
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Sep 7 17:40:05 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajout du projet chesscoach (§2)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0faf082..774563a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 75 (6 ligne(s)) dans l'ancienne version → ligne 75 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -75,6 +75,7 @@ Claude Chat → crée une issue → GitHub → watcher.py détecte → CCL exéc
 | `bloc_score` | AlainDelree/Bloc_score | ~/Bloc_score | (conf local) |
 | `rummikub` | AlainDelree/Rummikub | ~/Rummikub | (conf local) |
 | `ApiSelect` | AlainDelree/ApiSelect | ~/ApiSelect | (conf local) |
+| `chesscoach` | AlainDelree/Chesscoach | ~/ChessCoach | (conf local) |
 
 Chaque projet a son propre watcher (`watcher.py --config configs/<nom>.conf`)
 et son propre journal de log (`logs/watcher-<nom>.log`).
# ── Zone modifiée : ligne 667 (6 ligne(s)) dans l'ancienne version → ligne 668 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -667,6 +668,7 @@ hors périmètre même si l'issue le demande explicitement :
 | `bloc_score` | /home/alain/Bloc_score |
 | `rummikub` | /home/alain/Rummikub |
 | `ApiSelect` | /home/alain/ApiSelect |
+| `chesscoach` | /home/alain/ChessCoach |
 
 ---
 
# ── Zone modifiée : ligne 2808 (7 ligne(s)) dans l'ancienne version → ligne 2810 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2808,7 +2810,7 @@ qu'une sélection manuelle.
 
 ---
 
-*Dernière mise à jour : 30 août 2026 — §3.3 « Format attendu du fichier »
+*Dernière mise à jour : 7 septembre 2026 — §3.3 « Format attendu du fichier »
 (issue #512) : l'en-tête `| CHAMP | Valeur |` et la ligne `#Titre:` sont
 désormais supportés dans l'un ou l'autre ordre, alors que seul « en-tête
 avant `#Titre:` » fonctionnait correctement jusqu'ici. Cause racine :
