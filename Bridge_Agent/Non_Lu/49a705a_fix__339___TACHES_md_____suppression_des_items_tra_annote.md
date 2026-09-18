49a705a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 49a705a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 23:34:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #339 : TACHES.md — suppression des items traités ou abandonnés

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1d49444..1cab4e3 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,19 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #339
+
+Nettoyage de `TACHES.md` : suppression de trois items devenus obsolètes.
+« Parallélisation en mode_write via git worktrees » est implémenté depuis
+l'issue #337. « Rafraîchir une seule fois la ligne d'une issue quand son
+décompte atteint zéro » est implémenté depuis l'issue #334. « Concurrence
+limitée aux issues mode_lecture » est abandonné : le cas d'usage est trop
+rare pour justifier une implémentation séparée, et le sujet sera
+naturellement couvert par le système de worktrees si le besoin se
+confirme. Restent inchangés : « Projet dédié à la communication CCL ↔
+CCW » et « Calibration automatique du TIMEOUT — trois défauts à
+corriger ».
+
 ## 2 août 2026 — issue #338
 
 Documentation dédiée à la parallélisation mode_write via git worktrees
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index 1eac810..0e9da13 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 69 (132 ligne(s)) dans l'ancienne version → ligne 69 (3 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -69,132 +69,3 @@ première et sous-estimerait gravement la seconde.
 lancée. À reprendre à froid — le sujet touche des EWMA et des choix de
 modélisation qu'on prendrait mal à la légère.
 
----
-
-## Concurrence limitée aux issues mode_lecture
-
-**Contexte** : `watcher.py` est aujourd'hui strictement séquentiel (une issue à
-la fois, tous modes confondus, cf. §3 de BRIDGE_AGENT_DOC.md). Pour des tâches
-en `mode_lecture` (ex. plusieurs audits Python/JS/CSS sur un même projet), ce
-séquentiel n'est pas motivé par un risque réel : sans écriture disque, plusieurs
-CCL peuvent lire le même dépôt simultanément sans conflit.
-
-**Idée** : permettre à `watcher.py` de traiter plusieurs issues en **parallèle**
-uniquement si elles sont **toutes** en `mode_lecture` — garde-fou strict
-interdisant toute concurrence dès qu'une issue `mode_write` est impliquée (là,
-le risque de conflit d'accès fichier reste réel).
-
-**Points à concevoir avant implémentation** :
-- Limites de débit API (Claude, GitHub) si plusieurs CCL appellent en même temps.
-- Charge CPU/RAM du ThinkPad avec plusieurs CCL simultanés.
-- Entremêlement des logs (un fichier de log par issue en cours ?).
-- Détection fiable que TOUTES les issues d'un lot sont bien en mode_lecture avant
-  d'autoriser le parallélisme (une seule mode_write dans le lot → tout repasse en
-  séquentiel).
-
-**Statut** : idée en attente, pas de développement lancé. Discuté le 24/07/2026,
-suite à un timeout sur un audit Scrabble.
-
----
-
-## Parallélisation en mode_write via git worktrees
-
-**Contexte** : contrairement au cas précédent, paralléliser des tâches
-`mode_write` sur un même dépôt pose un vrai risque de conflit d'accès fichier
-si plusieurs CCL écrivent en même temps dans le même répertoire de travail.
-
-**Idée** : utiliser les *git worktrees* — un dépôt git peut avoir plusieurs
-répertoires de travail simultanés, chacun sur sa propre branche, tous rattachés
-au même `.git` (pas de duplication lourde comme un clone complet) :
-
-```bash
-git worktree add ../Projet-tache1 -b tache-1-issue-XXX
-git worktree add ../Projet-tache2 -b tache-2-issue-YYY
-```
-
-Chaque tâche parallèle travaille dans son propre dossier physique, sur sa
-propre branche → zéro conflit d'accès fichier pendant l'exécution. Le risque
-est déplacé au moment du **merge**, où git gère nativement les conflits
-(visibles, résolubles), plutôt que de risquer une corruption silencieuse
-pendant l'exécution.
-
-**Ce qu'il faudrait construire** :
-- Un champ dans l'en-tête d'issue (ex. `WORKTREE`, ou dérivé automatiquement du
-  numéro d'issue) pour que le watcher sache dans quel worktree travailler,
-  plutôt que dans le `REP_TRAVAIL` fixe du projet.
-- Une étape de création/nettoyage des worktrees (`git worktree add` au
-  démarrage, `git worktree remove` + `git branch -d` après merge — sinon ils
-  s'accumulent).
-- Rien à inventer côté verrouillage/détection de conflit : c'est le travail
-  natif de git.
-
-**Ce qu'il ne faut PAS automatiser** : le merge lui-même doit rester une étape
-manuelle (ou explicitement validée par Alain), cohérente avec la règle actuelle
-de vérification avant push — un merge automatique sans supervision humaine est
-le genre d'endroit où l'autonomie de CCL doit rester limitée.
-
-**Piste de test avant d'investir dans l'intégration native** : créer les
-worktrees manuellement pour deux issues connues indépendantes, pointer les
-`REP_TRAVAIL`/`PERIMETRE` de deux `.conf` temporaires vers ces deux worktrees,
-et lancer deux watchers en parallèle sur ces configs — sans aucun changement
-de code, pour valider le concept avant d'écrire le champ `WORKTREE` natif.
-
-**Statut** : idée en attente, pas de développement lancé. Discuté le 24/07/2026.
-
----
-
-## Rafraîchir une seule fois la ligne d'une issue quand son décompte atteint zéro
-
-**Contexte** : le décompte de temps restant affiché pour une issue tourne
-uniquement côté navigateur (timer local à 1 s, `majBadgesTempsRestant`) et
-ne re-interroge jamais GitHub. Quand le budget est épuisé,
-`formaterBadgeTempsRestant` affiche « ⌛ 0 s — budget épuisé » qui reste figé
-indéfiniment, même si l'issue est en réalité déjà terminée côté serveur.
-Ça donne l'illusion qu'une issue tourne encore et pousse à aller vérifier
-au log « pour être sûr » à chaque fois — repéré à plusieurs reprises le
-02/08/2026 (#320/#322/#323), où le décompte figé a fait douter à répétition
-de l'état réel d'issues déjà closes.
-
-Ce n'est pas un bug : c'est le comportement assumé depuis #270, qui a
-retiré le re-fetch périodique de toutes les issues (~3840 pts/h de quota
-GraphQL, premier poste de consommation, cf. #263) au profit d'un
-rafraîchissement uniquement manuel (bouton ↻). Le bip et le ↻ restent
-fiables — seul le décompte non rafraîchi ment.
-
-**Idée** : quand le décompte d'une issue atteint zéro, déclencher UN SEUL
-fetch ciblé de CETTE issue pour connaître son état réel, au lieu de laisser
-le badge figé jusqu'au ↻ manuel. La route existe déjà :
-`/issue/<projet>/<numero>` (`issue_detail`) renvoie state/labels/closedAt —
-pas de nouvelle route serveur nécessaire. Selon le résultat :
-- issue réellement fermée (done/needs-human) → mettre à jour la ligne
-  (badge terminal, retrait du décompte) ;
-- issue encore ouverte (dépassement légitime : l'estimation est une
-  médiane, pas une limite) → ne pas re-décompter indéfiniment.
-
-**Pourquoi ce n'est pas un retour à #270** : #270 a supprimé le re-fetch
-PÉRIODIQUE de TOUTES les issues, en continu (~240 cycles/h × N projets).
-Ici c'est UN fetch, d'UNE issue, UNE fois, au moment précis où son décompte
-expire — quelques appels par heure au maximum, négligeable devant ce que
-#270 a supprimé. Une future implémentation ne doit pas réintroduire, même
-partiellement, le polling banni par #270.
-
-**Point de conception à trancher (le seul vrai) — comportement au
-dépassement légitime** : si le fetch dit « toujours ouverte », que faire ?
-Deux options à documenter comme alternatives, sans trancher ici :
-- (a) re-tenter le fetch à intervalle LONG (ex. toutes les quelques
-  minutes) tant que l'issue traîne — un décompte honnête, au prix de
-  quelques appels espacés ;
-- (b) basculer le badge en « ⌛ dépassement — rafraîchir » (invite
-  explicite au ↻, zéro appel supplémentaire).
-
-Compromis à peser : (a) est plus confortable mais rouvre un mini-polling
-borné ; (b) est strictement fidèle à l'esprit #270 mais laisse une action
-manuelle à Alain.
-
-**Anti-abus à prévoir** (si l'option a est retenue un jour) : borner le
-nombre de re-fetch par issue, pour qu'une issue qui expire et traîne en
-boucle ne génère pas d'appels sans fin.
-
-**Statut** : idée en attente, pas de développement lancé. Née le
-02/08/2026 d'une session où le décompte figé a fait douter à répétition de
-l'état réel d'issues déjà terminées (#320/#322/#323).
