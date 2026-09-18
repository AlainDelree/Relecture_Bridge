7b6210c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7b6210c
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 23:47:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #342 : §11 informe les projets de la parallélisation mode_write et du workflow de merge/push associé

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 20dad9e..9aa8b1d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 518 (6 ligne(s)) dans l'ancienne version → ligne 518 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -518,6 +518,27 @@ la même opération, en plus du point ci-dessus :
   - *Bon exemple* : « Dans `api.py`, pour les trois méthodes de navigation,
     différer l'appel dans un thread daemon avec `time.sleep(0.05)` avant
     de naviguer. »
+- **Parallélisation `mode_write` (issue #337, information pour les projets
+  utilisant Bridge_Agent)** : depuis #337, plusieurs issues `mode_write` d'un
+  même projet peuvent tourner **en parallèle**, chacune dans son propre
+  `git worktree`. Deux issues touchant les mêmes fichiers ou les mêmes zones
+  de code peuvent donc générer un conflit de merge à résoudre manuellement.
+  **Recommandation** : scoper chaque issue sur un périmètre de fichiers aussi
+  distinct que possible des autres issues `mode_write` en cours.
+- **Workflow de vérification/push après des issues `mode_write` parallèles**
+  (issue #342) : en plus de la relecture habituelle des commits avant push,
+  Alain doit désormais :
+  1. Vérifier `git worktree list` pour repérer les worktrees prêts à être
+     mergés.
+  2. Lancer `python3 scripts/fusionner_changelog.py` **avant tout merge ou
+     push** — intègre les `CHANGELOG-N.md` de chaque worktree dans
+     `CHANGELOG.md` (lancement manuel uniquement, jamais automatique).
+  3. Merger chaque branche `worktree-issue-<N>` dans `master` manuellement,
+     une par une.
+  4. Nettoyer : `git worktree remove <chemin>` puis
+     `git branch -d worktree-issue-<N>`.
+  Détail complet (procédures de récupération incluses) : voir
+  [`WORKTREES.md`](WORKTREES.md).
 
 ---
 
# ── Zone modifiée : ligne 2094 (47 ligne(s)) dans l'ancienne version → ligne 2115 (41 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2094,47 +2115,41 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 2 août 2026 — §13 « Commandes utiles » (nouvelle
-sous-section « Interrompre une issue bloquée ») et §16.4 « Interrompre une
-issue CCW coincée » : les deux boutons ⛔ « Interrompre » (CCL et CCW, issue
-#323) sont désormais documentés comme implémentés et fonctionnels — le
-renvoi mort vers `TACHES.md` du §16.4 est supprimé (issue #333). §16.4
-décrit maintenant au présent ce que fait `interrompre_windows()`
-(`app/interruption.py`) via `provisioning/windows/interrompre_projet_ccw.ps1` :
-arrêt du service NSSM, vérification bornée de l'arbre de process,
-suppression conditionnelle des `.lock`. La nouvelle sous-section de §13
-documente le pendant côté CCL (`interrompre_linux()`) : arbre de process
-retrouvé par remontée `/proc/<pid>/status` (PPID, jamais par nom
-d'exécutable), `SIGKILL`, attente confirmée de la mort de l'arbre avant
-suppression du verrou — ainsi que l'équivalent manuel (`kill -9` + suppression
-du `.lock`). Précédemment — §3 « Créer une issue — la méthode normale » et §6
-« Champs spéciaux dans le corps de l'issue » : documente le champ d'en-tête
-`MODE` (issue #330), auto-détecté par `new_issue.py` (`detecterModeDansCorps`)
-au même titre que `TIMEOUT`/`PROJET`/`MODELE` (issue #326) — pré-sélectionne
-le radio Mode du formulaire puis la ligne est retirée du corps, reconnaissance
-tolérante (casse/accents, plusieurs libellés par valeur), défaut LECTURE si
-le champ est absent ou non reconnu. Seules les deux valeurs fonctionnelles
+*Dernière mise à jour : 2 août 2026 — §11 « Conventions de code » : deux
+notes informant les projets utilisant Bridge_Agent des conséquences de la
+parallélisation `mode_write` par worktrees (issue #337) — risque de conflit
+de merge entre deux issues touchant les mêmes fichiers (recommandation :
+scoper les issues sur des périmètres de fichiers aussi distincts que
+possible) et workflow de vérification/push désormais attendu d'Alain
+(`git worktree list`, `python3 scripts/fusionner_changelog.py` avant tout
+merge ou push, merge manuel de chaque branche `worktree-issue-<N>`,
+nettoyage `git worktree remove`/`git branch -d`) — renvoi vers
+`WORKTREES.md` pour le détail complet (issue #342). Précédemment — §13
+« Commandes utiles » (nouvelle sous-section « Interrompre une issue
+bloquée ») et §16.4 « Interrompre une issue CCW coincée » : les deux
+boutons ⛔ « Interrompre » (CCL et CCW, issue #323) sont désormais
+documentés comme implémentés et fonctionnels — le renvoi mort vers
+`TACHES.md` du §16.4 est supprimé (issue #333). §16.4 décrit maintenant au
+présent ce que fait `interrompre_windows()` (`app/interruption.py`) via
+`provisioning/windows/interrompre_projet_ccw.ps1` : arrêt du service NSSM,
+vérification bornée de l'arbre de process, suppression conditionnelle des
+`.lock`. La nouvelle sous-section de §13 documente le pendant côté CCL
+(`interrompre_linux()`) : arbre de process retrouvé par remontée
+`/proc/<pid>/status` (PPID, jamais par nom d'exécutable), `SIGKILL`,
+attente confirmée de la mort de l'arbre avant suppression du verrou — ainsi
+que l'équivalent manuel (`kill -9` + suppression du `.lock`). Précédemment
+— §3 « Créer une issue — la méthode normale » et §6 « Champs spéciaux dans
+le corps de l'issue » : documente le champ d'en-tête `MODE` (issue #330),
+auto-détecté par `new_issue.py` (`detecterModeDansCorps`) au même titre que
+`TIMEOUT`/`PROJET`/`MODELE` (issue #326) — pré-sélectionne le radio Mode du
+formulaire puis la ligne est retirée du corps, reconnaissance tolérante
+(casse/accents, plusieurs libellés par valeur), défaut LECTURE si le champ
+est absent ou non reconnu. Seules les deux valeurs fonctionnelles
 `lecture`/`écriture` sont documentées à ces deux endroits ; la troisième
-valeur (lecture active/`mode_scratch`) reste décrite uniquement au §5 (issue
-#327), hors périmètre de #330. Précise aussi qu'en mono-issue `MODE` est
-auto-détecté depuis l'en-tête du bloc, alors qu'en mode lot il reste commun
-à tout le lot — choisi une fois au radio du formulaire, jamais lu bloc par
-bloc. Précédemment — §4 « Labels disponibles » et §5, renommé « Modes
-lecture seule / lecture active / écriture » : implémente la « lecture
-active » (label `mode_scratch`) préparée côté formulaire/en-tête par #326
-mais jusqu'ici ignorée par le watcher (issue #327). Le booléen
-`autoriser_ecriture` est remplacé par un MODE à trois valeurs
-(`lecture`/`lecture_active`/`ecriture`), déduit des labels par
-`watcher.py::_deduire_mode` et lu par les cinq points de décision (flag
-`--dangerously-skip-permissions`, bloc de garde-fou du prompt, backup,
-garde-fou `configs/*.conf`, étiquette de calibration TIMEOUT). La lecture
-active écrit UNIQUEMENT dans `/tmp/bridge_scratch_<projet>/` (créé avant
-CCL, nettoyé après, quel que soit le résultat) — défense en profondeur
-niveau 1 (bloc de prompt dédié) + niveau 2 (empreinte de l'état git du
-répertoire de travail avant/après, restauration + échec `needs-human` si
-une écriture est détectée hors scratch, même schéma que le garde-fou
-`configs/*.conf` #318). Le livrable reste un rapport, comme en lecture
-seule. §12 « Règles d'usage » précise que l'interdiction d'écriture sur
-`configs/*.conf` (#318) vaut aussi en lecture active.*
+valeur (lecture active/`mode_scratch`) reste décrite uniquement au §5
+(issue #327), hors périmètre de #330. Précise aussi qu'en mono-issue `MODE`
+est auto-détecté depuis l'en-tête du bloc, alors qu'en mode lot il reste
+commun à tout le lot — choisi une fois au radio du formulaire, jamais lu
+bloc par bloc.*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index b922efe..183ba93 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,27 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #342
+
+§11 « Conventions de code » de `BRIDGE_AGENT_DOC.md` : deux notes ajoutées
+pour informer les projets utilisant Bridge_Agent des conséquences
+pratiques de la parallélisation `mode_write` par worktrees (issue #337),
+jusqu'ici documentée uniquement pour l'infrastructure elle-même (§13 du
+DOC, `WORKTREES.md`). Première note : deux issues `mode_write` touchant
+les mêmes fichiers ou zones de code peuvent désormais générer un conflit
+de merge à résoudre manuellement — recommandation de scoper chaque issue
+sur un périmètre de fichiers aussi distinct que possible. Deuxième note :
+le workflow de vérification/push d'Alain inclut désormais deux étapes
+supplémentaires après une ou plusieurs issues `mode_write` en parallèle —
+`git worktree list` pour repérer les worktrees à traiter,
+`python3 scripts/fusionner_changelog.py` avant tout merge ou push (intègre
+les `CHANGELOG-N.md` des worktrees dans `CHANGELOG.md`), puis merge manuel
+de chaque branche `worktree-issue-<N>` et nettoyage
+(`git worktree remove` + `git branch -d`) ; renvoi vers `WORKTREES.md` pour
+le détail complet plutôt qu'une duplication intégrale. Pied de page du DOC
+mis à jour en conséquence (glissement des trois entrées, #327 sort du pied
+de page).
+
 ## 2 août 2026 — issue #340
 
 Suite #338 : le bouton ⛔ « Interrompre » (`app/interruption.py::interrompre_linux()`)
