7b251e1

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7b251e1
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 09:41:15 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Chef : ajout section mode_tmp_write (écriture scratch limitée hors dépôt pour outillage d'audit) à TACHES.md — idée en attente, sections existantes inchangées (issue #215)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 679a378..8a81a57 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 74 (3 ligne(s)) dans l'ancienne version → ligne 74 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -74,3 +74,38 @@ et lancer deux watchers en parallèle sur ces configs — sans aucun changement
 de code, pour valider le concept avant d'écrire le champ `WORKTREE` natif.
 
 **Statut** : idée en attente, pas de développement lancé. Discuté le 24/07/2026.
+
+---
+
+## Mode mode_tmp_write — écriture scratch limitée pour outillage d'audit
+
+**Contexte** : certains outils d'analyse (eslint flat config pour les
+versions ≥ 9, linters divers) exigent un vrai fichier de config sur disque,
+pas seulement une commande inline. Le mode_lecture actuel interdit toute
+écriture, y compris hors dépôt — ce qui bloque ces outils. Note : ce n'est
+PAS ce qui causait les timeouts observés sur Scrabble (#235 vs #238,
+réglé par une consigne d'abandon immédiat au refus de permission) — c'est
+un besoin distinct et réel, pour les cas où l'outil a effectivement besoin
+d'un fichier de config.
+
+**Proposition** (reçue via rapport d'audit Scrabble) : un troisième mode,
+`mode_tmp_write`, avec :
+- Écriture autorisée uniquement dans un chemin scratch bien défini et
+  validé strictement côté watcher (ex. `/tmp/bridge_scratch_<projet>/`),
+  jamais dans `REP_TRAVAIL` du projet. Validation stricte du chemin pour
+  empêcher tout `../` ou équivalent remontant vers le dépôt.
+- Toujours interdit, comme en lecture seule : `git commit`, `git push`,
+  toute commande destructrice, toute écriture hors du chemin scratch.
+- Nettoyage attendu en fin de tâche par CCL, idéalement complété par un
+  nettoyage automatique du dossier scratch par le watcher en fin de
+  traitement — pour ne pas reposer uniquement sur la consigne donnée à CCL.
+- Conceptuellement plus proche du mode lecture seule que du mode écriture :
+  pas de garde-fou "backup avant modification" nécessaire (aucun fichier du
+  projet n'est jamais en jeu).
+
+**Point de vigilance** : la garantie ne tient que si la validation du
+chemin scratch est réellement stricte côté `watcher.py` — à concevoir avec
+soin, pas seulement en confiance sur la consigne donnée à CCL.
+
+**Statut** : idée en attente, pas de développement lancé. Reçue via rapport
+d'audit Scrabble le 24/07/2026.
