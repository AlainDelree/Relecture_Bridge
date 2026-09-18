357e92b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 357e92b
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 20:33:24 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajout du projet elevage_reine (§2)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e34da1d..d54dd04 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 74 (6 ligne(s)) dans l'ancienne version → ligne 74 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -74,6 +74,7 @@ Claude Chat → crée une issue → GitHub → watcher.py détecte → CCL exéc
 | `actualise` | AlainDelree/Actualise | ~/Actualise | (conf local) |
 | `bloc_score` | AlainDelree/Bloc_score | ~/Bloc_score | (conf local) |
 | `rummikub` | AlainDelree/Rummikub | ~/Rummikub | (conf local) |
+| `elevage_reine` | AlainDelree/Elevage_reine | ~/Elevage_reine | (conf local) |
 
 Chaque projet a son propre watcher (`watcher.py --config configs/<nom>.conf`)
 et son propre journal de log (`logs/watcher-<nom>.log`).
# ── Zone modifiée : ligne 356 (6 ligne(s)) dans l'ancienne version → ligne 357 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -356,6 +357,7 @@ hors périmètre même si l'issue le demande explicitement :
 | `actualise` | /home/alain/Actualise |
 | `bloc_score` | /home/alain/Bloc_score |
 | `rummikub` | /home/alain/Rummikub |
+| `elevage_reine` | /home/alain/Elevage_reine |
 
 ---
 
