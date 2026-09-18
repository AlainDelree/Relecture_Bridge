7b96f70

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7b96f70
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 30 18:51:58 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #513 : préciser le chemin absolu du dossier de travail dans le rapport de fin de tâche

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d6b7928..4a4805b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 523 (6 ligne(s)) dans l'ancienne version → ligne 523 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -523,6 +523,20 @@ Garde-fous automatiques :
 - Aucune commande destructrice sans demande explicite
 - Périmètre strict : CCL ne travaille que dans le dossier configuré
 
+> **Rapport de fin de tâche (issue #513)** : le format de réponse imposé par
+> le prompt (`lancer_claude`, `watcher.py`) précise désormais le chemin
+> absolu du dossier de travail effectivement utilisé pour cette exécution
+> (`Commits (dans <chemin>) : xxx (backup) + yyy (fix)`) — ce chemin est
+> `cwd_effectif`, c'est-à-dire `REP_TRAVAIL` du `.conf`, ou le worktree
+> git isolé de la tâche (parallélisation `mode_write`, voir plus bas), ou le
+> `REPO_CIBLE` d'un périmètre dynamique (§7), selon le cas. Même mécanisme
+> côté CCL et CCW (`watcher.py` est un script unique partagé par les deux
+> plateformes) : le chemin affiché est toujours celui du clone réel où les
+> commits ont été effectués, ce qui évite de chercher au mauvais endroit
+> quand plusieurs worktrees/clones du même dépôt coexistent (incident vécu
+> sur le projet Scrabble, commits faits dans le clone CCW `C:\CCW\scrabble`
+> alors qu'ils étaient cherchés dans le worktree CCL habituel).
+
 > `configs/*.conf` reste interdit à l'écriture **quel que soit le mode**
 > (lecture active comme écriture) — garde-fou technique #318, voir §11.
 
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 98c6f13..fc5ce2b 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 2244 (7 ligne(s)) dans l'ancienne version → ligne 2244 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2244,7 +2244,7 @@ Instructions :
 Réponds avec ce format exact, sans rien ajouter avant ni après :
 
 ✅ Tâche terminée — [résumé en une ligne de ce qui a été fait]
-Commits : [hash backup] (backup) + [hash fix] (fix) — ou "aucun" si lecture seule
+Commits (dans {cwd_effectif}) : [hash backup] (backup) + [hash fix] (fix) — ou "aucun" si lecture seule
 py_compile : OK / N/A — push : aucun
 
 <details>
