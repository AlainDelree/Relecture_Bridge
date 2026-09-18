a8fb8f9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a8fb8f9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 14:41:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    chore : mise à jour TACHES-ISSUES.md (modes, labels, format new_issue.py)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES-ISSUES.md b/TACHES-ISSUES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e2481b9..799fe3b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES-ISSUES.md
# ── Version APRÈS ce commit.
+++ b/TACHES-ISSUES.md
# ── Zone modifiée : ligne 1 (159 ligne(s)) dans l'ancienne version → ligne 1 (164 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,159 +1,164 @@
 # Bridge inter-agents AlChess — Référence des tâches (issues)
 
-## Vocabulaire
+Document de référence pour Claude Chat (CC) lors de la création d'issues
+vers Claude Code Linux (CCL) via Bridge_Agent.
 
-Pour SOURCE, DEST, RETOUR : **CC** = Claude Chat, **CCL** = Claude Code Linux, **CCW** = Claude Code Windows.
-Remplacer `for-linux` par `for-windows` selon la cible.
+---
 
 ## Labels disponibles
 
 | Label | Rôle |
 |-------|------|
 | `bridge` | Marque l'issue comme tâche du bridge |
-| `for-linux` | Cible : agent Linux (CCL), traité par `watcher.py` sur le ThinkPad |
+| `for-linux` | Cible : agent Linux (CCL) sur le ThinkPad |
 | `for-windows` | Cible : agent Windows (CCW) sur la VM |
-| `mode_write` | **ARME le mode écriture** (voir ci-dessous). À poser sciemment. |
-| `done` | Ajouté automatiquement par le watcher quand l'issue est traitée |
+| `mode_write` | **ARME le mode écriture** — CCL peut modifier des fichiers et committer |
+| `mode_scratch` | **ARME la lecture active** — CCL peut écrire uniquement dans un dossier scratch temporaire |
+| `done` | Posé automatiquement par le watcher en cas de succès |
+| `needs-human` | Posé automatiquement après 3 échecs — stoppe le retraitement |
+| `notif_pc` | Notification bureau (notify-send) à la clôture |
+| `notif_gsm` | Notification push (ntfy) à la clôture |
+| `notif_tous` | Les deux |
+
+---
+
+## Modes de traitement
+
+| Mode | Label | Ce que CCL peut faire |
+|------|-------|----------------------|
+| **Lecture seule** (défaut) | aucun | Lire, grep, analyser, rapporter. Aucune écriture. |
+| **Lecture active** | `mode_scratch` | Lire + écrire uniquement dans `/tmp/bridge_scratch_alchess/` (outils nécessitant un fichier de config sur disque, ex. linters). Le livrable reste un rapport. |
+| **Écriture** | `mode_write` | Modifier des fichiers, exécuter des commandes, committer. Backup obligatoire avant toute modification. Jamais de `git push`. |
 
-## ⚠️ Mode lecture seule vs mode écriture (IMPORTANT)
+Le mode est visible dans le log du watcher (`MODE ÉCRITURE ARMÉ` ou `MODE LECTURE ACTIVE`) et dans le commentaire ACK de l'issue.
 
-Le watcher lance Claude Code de deux façons selon les labels :
+**Règle** : pour un diagnostic → lecture seule (défaut). Pour un outil nécessitant un fichier temporaire → lecture active. Pour une modification de code → écriture, et toujours relire le diff avant de pousser.
 
-- **Sans `mode_write` (défaut)** → **LECTURE SEULE**. CCL peut lire, `grep`,
-  analyser et rapporter, mais **ne peut pas écrire de fichier, ni exécuter, ni
-  committer**. C'est le mode sûr, idéal pour les diagnostics.
+---
 
-- **Avec `mode_write`** → **MODE ÉCRITURE**. Le watcher ajoute
-  `--dangerously-skip-permissions` : CCL peut écrire des fichiers, exécuter des
-  commandes et committer. Garde-fous inscrits dans le prompt :
-  - backup pinné obligatoire avant toute modification ;
-  - **JAMAIS de `git push`** (Alain pousse lui-même, après vérification) ;
-  - aucune commande destructrice non explicitement demandée.
+## Champs d'en-tête reconnus
 
-Le mode est visible : le terminal du watcher affiche `MODE ÉCRITURE ARMÉ`, et le
-commentaire ACK sur l'issue indique « Mode : **ÉCRITURE ⚠️** » ou « lecture seule ».
+À placer en tableau markdown en début de corps de l'issue. Tous optionnels sauf `PROJET`.
 
-**Règle d'usage** : pour un diagnostic → ne PAS mettre `mode_write`. Pour une
-modification de code/fichier → ajouter `mode_write`, et toujours relire le diff /
-committer / pusher soi-même ensuite.
+| Champ | Exemple | Effet |
+|-------|---------|-------|
+| `PROJET` | `alchess` | **Obligatoire** — nom du projet cible |
+| `MODE` | `lecture` / `écriture` / `lecture active` | Auto-détecté par new_issue.py, pré-sélectionne le radio Mode |
+| `TIMEOUT` | `600s` | Surcharge le timeout par défaut (300s) |
+| `MODELE` | `claude-sonnet-5` | Force un modèle CCL spécifique |
+| `SUITE_DE` | `#42` | Indique que cette issue fait suite à l'issue #N |
+| `TYPE` | `chef` / `ouvrier` | Rôle dans le pattern multi-agent (§14 de la doc Bridge_Agent) |
+| `LABELS` | `for-windows` | Labels supplémentaires ajoutés à ceux posés d'office |
 
 ---
 
-## MODÈLE — Tâche COMPLÈTE (lecture seule / diagnostic)
-
-```bash
-gh issue create \
-  --repo AlainDelree/AlChess \
-  --title "TITRE COURT" \
-  --label "bridge,for-linux" \
-  --body "## Entête
-
-| Champ | Valeur |
-|-------|--------|
-| SOURCE | CC |
-| DEST | CCL |
-| RETOUR | CC |
-| PARCOURS | CC → CCL |
-| CONV_ID | url_conversation |
-| PRIORITE | normale |
-| ACK_REQUIS | oui |
-| TIMEOUT | 300s |
-| RETRY | 3 |
-| DEPENDS_ON | aucun |
-| CHECKSUM | aucun |
+## Format des issues — new_issue.py
 
-## Contexte
+Toutes les issues passent par l'interface web `new_issue.py` (ou son alias `bridge`).
+Coller le bloc suivant dans le champ **Corps** — le champ `#Titre:` est
+auto-détecté et remplit le titre.
 
+```
+#Titre: Titre court et actionnable
+| PROJET | alchess |
+| MODE   | lecture |
+
+## Contexte
 Pourquoi cette tâche existe.
 
 ## Tâche demandée
-
-Description précise et actionnable. (LECTURE SEULE : ne rien modifier.)
+Description précise. Indiquer explicitement si LECTURE SEULE.
 
 ## Résultat attendu
+Ce que CCL doit produire ou confirmer.
+```
 
-Ce que l'agent doit produire.
+Pour envoyer plusieurs issues en un seul copier-coller (mode lot), enchaîner
+plusieurs blocs `#Titre:` dans le même corps — le bouton devient
+« Envoyer le lot (N issues) ». Le MODE est commun à tout le lot (radio du
+formulaire), les autres champs d'en-tête sont par bloc.
 
-## Retour attendu
+---
 
-Ce que l'agent doit renvoyer une fois terminé."
-```
+## MODÈLE — Tâche lecture seule / diagnostic
 
-## MODÈLE — Tâche LÉGÈRE (lecture seule / diagnostic)
+```
+#Titre: Titre court et actionnable
+| PROJET  | alchess |
+| MODE    | lecture |
+| TIMEOUT | 300s    |
 
-```bash
-gh issue create \
-  --repo AlainDelree/AlChess \
-  --title "TITRE COURT" \
-  --label "bridge,for-linux" \
-  --body "## Entête
+## Contexte
+Pourquoi cette tâche existe.
 
-| Champ | Valeur |
-|-------|--------|
-| SOURCE | CC |
-| DEST | CCL |
-| RETOUR | CC |
+## Tâche demandée
+Description précise et actionnable. LECTURE SEULE : ne rien modifier.
 
-## Tâche
+## Résultat attendu
+Ce que CCL doit produire ou confirmer.
+```
 
-Description courte et actionnable. (LECTURE SEULE : ne rien modifier.)
+---
 
-## Résultat attendu
+## MODÈLE — Tâche lecture active (outil nécessitant un fichier temporaire)
 
-Ce que l'agent doit produire ou confirmer."
 ```
+#Titre: Titre court et actionnable
+| PROJET  | alchess         |
+| MODE    | lecture active  |
+| TIMEOUT | 300s            |
 
-## MODÈLE — Tâche ÉCRITURE (modification de code/fichier)
+## Contexte
+Pourquoi cet outil nécessite de la lecture active plutôt que la lecture seule.
+
+## Tâche demandée
+Description précise. CCL peut écrire dans /tmp/bridge_scratch_alchess/ uniquement.
+Le livrable attendu est un rapport, pas une modification du projet.
 
-> Ajouter le label `mode_write`. Toujours exiger un backup pinné et interdire le push.
+## Résultat attendu
+Rapport produit par l'outil (ex. liste d'erreurs de lint, résultats d'analyse).
+```
 
-```bash
-gh issue create \
-  --repo AlainDelree/AlChess \
-  --title "TITRE COURT" \
-  --label "bridge,for-linux,mode_write" \
-  --body "## Entête
+---
 
-| Champ | Valeur |
-|-------|--------|
-| SOURCE | CC |
-| DEST | CCL |
-| RETOUR | CC |
-| MODE | ÉCRITURE |
+## MODÈLE — Tâche écriture (modification de code/fichier)
 
-## Contexte
+```
+#Titre: Titre court et actionnable
+| PROJET  | alchess  |
+| MODE    | écriture |
+| TIMEOUT | 300s     |
 
+## Contexte
 Pourquoi cette modification est nécessaire.
 
 ## Tâche demandée
-
 Modification précise à appliquer (fichier(s), logique attendue).
+Ne pas fournir le code complet — décrire le problème et l'intention ;
+CCL lit les fichiers source et fait l'implémentation lui-même.
 
-## Contraintes de sécurité
+## Résultat attendu
+- Diff des modifications appliquées.
+- Confirmation qu'aucun push n'a été fait.
+```
 
-- Faire un backup pinné AVANT toute modification :
-  python -m nicsoft.utils.backup_manager --pin --label \"avant-<description>\"
-- NE PAS committer.
-- NE PAS faire git push.
-- Aucune commande destructrice.
+---
 
-## Retour attendu
+## Parallélisation mode_write (depuis #337)
 
-- Le diff complet des modifications appliquées (pour validation par Alain).
-- Confirmation qu'aucun commit ni push n'a été fait."
-```
+Plusieurs issues `mode_write` d'un même projet peuvent tourner **en parallèle**
+via git worktrees. Deux issues touchant les mêmes fichiers ou zones de code
+peuvent générer un conflit de merge à résoudre manuellement.
+
+**Recommandation** : scoper chaque issue sur un périmètre de fichiers aussi
+distinct que possible des autres issues `mode_write` en cours.
 
 ---
 
 ## Prérequis d'exécution
 
-- `watcher.py` doit tourner : `python3 ~/bridge-agent/watcher.py`
-- Le label `mode_write` doit exister sur le dépôt (créé une fois via `gh label create`).
-- Le watcher lance CCL depuis `~/NicLink` comme répertoire de travail.
-
-## Historique — capacités validées
-
-- **2026-07-03** : mode écriture (`mode_write`) ajouté au watcher et **validé** par
-  un test (issue #10 : création d'un fichier bidon, sans commit ni push — garde-fous
-  confirmés). Le bridge diagnostique en lecture seule par défaut, et n'écrit que sur
-  issue explicitement armée.
+- Le watcher AlChess démarre **automatiquement** à la création d'une issue
+  `for-linux` via new_issue.py — aucune action manuelle requise.
+- Il s'éteint automatiquement après `DELAI_INACTIVITE_MIN` minutes d'inactivité
+  (défaut : 20 min).
+- Périmètre CCL : `/home/alain/NicLink` — CCL refuse tout travail hors de ce dossier.
