2bb23a2

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2bb23a2
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Sat Sep 12 18:58:26 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajout du projet gestionmail (§2)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4270de8..92624f2 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 76 (6 ligne(s)) dans l'ancienne version → ligne 76 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -76,6 +76,7 @@ Claude Chat → crée une issue → GitHub → watcher.py détecte → CCL exéc
 | `rummikub` | AlainDelree/Rummikub | ~/Rummikub | (conf local) |
 | `ApiSelect` | AlainDelree/ApiSelect | ~/ApiSelect | (conf local) |
 | `chesscoach` | AlainDelree/Chesscoach | ~/ChessCoach | (conf local) |
+| `gestionmail` | AlainDelree/GestionMail | ~/GestionMail | (conf local) |
 
 Chaque projet a son propre watcher (`watcher.py --config configs/<nom>.conf`)
 et son propre journal de log (`logs/watcher-<nom>.log`).
# ── Zone modifiée : ligne 669 (6 ligne(s)) dans l'ancienne version → ligne 670 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -669,6 +670,7 @@ hors périmètre même si l'issue le demande explicitement :
 | `rummikub` | /home/alain/Rummikub |
 | `ApiSelect` | /home/alain/ApiSelect |
 | `chesscoach` | /home/alain/ChessCoach |
+| `gestionmail` | /home/alain/GestionMail |
 
 ---
 
# ── Zone modifiée : ligne 2895 (7 ligne(s)) dans l'ancienne version → ligne 2897 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2895,7 +2897,7 @@ de création d'issue, seul valable pour du contenu qu'il produit.
 
 ---
 
-*Dernière mise à jour : 10 septembre 2026 — §17 « Tonalité du bip par
+*Dernière mise à jour : 12 septembre 2026 — §17 « Tonalité du bip par
 projet » (issue #526) : nouvelle clé `.conf` optionnelle `TONALITE_BIP`
 (entier en demi-tons, défaut 0), pour distinguer à l'oreille quel projet
 vient de terminer une issue sans gérer de bibliothèque de sons.
