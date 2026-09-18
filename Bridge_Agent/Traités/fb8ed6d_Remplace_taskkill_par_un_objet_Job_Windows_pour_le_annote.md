fb8ed6d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit fb8ed6d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 07:10:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Remplace taskkill par un objet Job Windows pour le nettoyage de l'arbre claude (issue #249, suite #247)
    
    taskkill /PID <pid> /T /F exige que le PID existe encore, or _nettoyer_arbre_claude
    s'exécute après le retour de communicate() : le process claude est déjà mort et
    réapé, donc taskkill échouait silencieusement sur le cas exact visé par #247
    (cmd.exe orphelin verrouillant Scrabble-Setup.exe). Un objet Job noyau
    (CreateJobObjectW + JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE + AssignProcessToJobObject,
    via ctypes pur) assigné au process dès son démarrage garantit la terminaison
    de toute sa descendance, PID vivant ou non au moment du nettoyage.
    
    - watcher.py : nouvelles _creer_job_windows_kill_on_close/_assigner_job_windows/
      _preparer_job_windows ; _nettoyer_arbre_claude accepte job_windows et journalise
      aussi les échecs (branche Windows silencieuse jusqu'ici) ; corps entier enveloppé
      dans un garde-fou try/except (OSError d'iterdir, PermissionError d'os.killpg,
      exceptions ctypes ne doivent jamais s'échapper d'un finally). Branche POSIX
      inchangée.
    - tests/test_nettoyage_arbre_windows_249.py : scénario Windows non exécutable sur
      ce ThinkPad Linux, couvert par mock de ctypes.windll (+ os.name forcé) — vérifie
      l'ordre des appels ctypes et la journalisation succès/échec. Ne remplace pas une
      validation réelle sur la VM CCW.
    - BRIDGE_AGENT_DOC.md : §13 réécrit (la justification "symétrie CCL/CCW" de #247
      est invalidée) + entrée de pied de page.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4ab85fe..b7bdd7a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 584 (44 ligne(s)) dans l'ancienne version → ligne 584 (87 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -584,44 +584,87 @@ issue déjà marquée `done`.
 partager celui du watcher. Un bloc `finally` — donc exécuté dans TOUS les cas
 de sortie (succès, échec, `TimeoutExpired`, exception) et **avant**
 `commenter_resultat_avec_retry`/`fermer_issue` — appelle
-`_nettoyer_arbre_claude(proc)` :
+`_nettoyer_arbre_claude(proc, job_windows)` :
 - **POSIX (CCL)** : `start_new_session=True` garantit que le pgid du process
   claude vaut son propre PID — un groupe forcément neuf, distinct de celui du
   watcher et de tout watcher frère. `_lister_processus_pgid` énumère (lecture
   directe de `/proc`, sans dépendance externe) les process vivants de ce pgid,
   journalise chacun (`log.warning`, PID + ligne de commande), puis
   `os.killpg(pid, SIGKILL)` sur ce seul groupe.
-- **Windows (CCW)** : `taskkill /PID <pid> /T /F` — ne parcourt que l'arbre
-  généalogique de ce PID précis.
-
-**Solution retenue et pourquoi.** Deux options étaient à l'étude : un objet
-Job Windows (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`, natif et sans fenêtre de
-course, mais API Windows pure via `ctypes`/`pywin32`, sans équivalent POSIX) ou
-la terminaison de l'arbre après coup. `watcher.py` étant le script **unique**
-partagé par CCL et CCW, la seconde option a été retenue : elle tient en
-quelques lignes symétriques par plateforme, sans nouvelle dépendance, dans le
-même fichier. Contrepartie assumée : une fenêtre de course de quelques
-millisecondes entre la fin de `communicate()`/l'expiration du timeout et
-l'appel de nettoyage (négligeable en pratique, et strictement meilleure que
-l'absence totale de garantie d'avant #247).
-
-**Journalisation, pas critère d'échec.** Chaque orphelin tué produit un
-`log.warning` explicite (PID + ligne de commande) — c'est le signal qui
-manquait dans le cas Scrabble. Le nettoyage ne fait jamais échouer la tâche :
-c'est une garantie de fin de traitement, pas une condition de succès.
-
-**Point critique vérifié (#247 point 4).** Le nettoyage ne cible **jamais**
-par nom d'exécutable — seulement le groupe/pgid ou l'arbre du PID de CE
-`claude`, garanti distinct de celui du watcher et de tout watcher frère par
-construction (`start_new_session`/nouvelle session). Une erreur ici aurait pu
-arrêter tous les watchers d'une même machine.
-
-**Test de non-régression** : `tests/test_nettoyage_arbre_247.py` — un faux
-`claude` (script shell en tête de `PATH`) lance un vrai enfant bloqué (lecture
-sur un FIFO jamais écrit, équivalent d'une lecture stdin qui n'aboutit jamais)
-puis termine aussitôt ; le test vérifie que l'enfant est mort après le retour
-de `lancer_claude`, que le nettoyage est journalisé, et que le process de test
-(jouant le rôle du watcher) n'est jamais affecté.
+- **Windows (CCW)** : objet Job noyau (`CreateJobObjectW` +
+  `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` + `AssignProcessToJobObject`, via
+  `ctypes`) — voir révision ci-dessous (issue #249).
+
+**Révision Windows — objet Job requis (issue #249).** La première version
+(2026-07-26) retenait un `taskkill /PID <pid> /T /F` tenté depuis
+`_nettoyer_arbre_claude`, par symétrie avec la branche POSIX. Cette approche
+s'est révélée **inopérante dans le cas exact visé par #247** :
+`_nettoyer_arbre_claude` s'exécute dans le `finally` de `lancer_claude`,
+c'est-à-dire **après** le retour de `proc.communicate()` — à cet instant le
+process `claude` est déjà terminé et réapé par l'OS. Or `taskkill /PID <pid>
+/T /F` a besoin que ce PID **existe encore** pour parcourir son arbre
+généalogique ; sur un PID mort, il échoue immédiatement (« process not
+found ») sans toucher un seul descendant. C'est précisément le scénario
+d'origine : le `cmd.exe` orphelin survit à `claude`, donc au moment du
+nettoyage son PID parent n'est plus traçable. `CREATE_NEW_PROCESS_GROUP` ne
+comble pas l'écart : sous Windows les groupes de process ne servent qu'au
+routage de Ctrl+C/Ctrl+Break, pas à la terminaison d'une arborescence.
+
+**Solution retenue.** Un objet Job Windows (`CreateJobObjectW` +
+`SetInformationJobObject(JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)`), créé et
+assigné (`AssignProcessToJobObject`) au process `claude` **juste après son
+démarrage** (`_preparer_job_windows`, appelé dans `lancer_claude`
+immédiatement après le `Popen`, pendant que le process est encore vivant —
+seul moment où l'assignation est possible). Fermer le handle du job
+(`CloseHandle`, dans `_nettoyer_arbre_claude`) termine alors immédiatement
+toute la descendance encore assignée, **qu'un PID cible existe encore ou
+non** : c'est la seule garantie réelle sous Windows, sans la fenêtre de
+course que la solution symétrique précédente laissait subsister. Implémenté
+via `ctypes` pur (pas de nouvelle dépendance, pas de `pywin32`). La branche
+POSIX (`start_new_session` + `os.killpg`) est inchangée : elle était déjà
+correcte et testée.
+
+**Journalisation, pas critère d'échec — désormais aussi les échecs (#249
+point 3).** Chaque orphelin POSIX tué produit un `log.warning` explicite
+(PID + ligne de commande). Côté Windows, la version #247 ne journalisait que
+le succès d'un `taskkill` : un échec silencieux (le cas réel, taskkill
+échouant toujours sur PID mort) ne laissait donc **aucune trace**. Depuis
+#249, `_preparer_job_windows` journalise l'échec de création du job ou
+d'assignation, et `_nettoyer_arbre_claude` journalise l'échec de fermeture du
+handle (ou l'absence de job disponible) — toute tentative de nettoyage laisse
+désormais une trace, succès ou échec. Le nettoyage ne fait jamais échouer la
+tâche : c'est une garantie de fin de traitement, pas une condition de succès.
+
+**Point critique vérifié (#247 point 4, renforcé #249).** Le nettoyage ne
+cible **jamais** par nom d'exécutable — seulement le groupe/pgid POSIX ou
+l'objet Job Windows assigné à CE `claude`, garanti distinct de celui du
+watcher et de tout watcher frère par construction. Une erreur ici aurait pu
+arrêter tous les watchers d'une même machine. #249 a en outre enveloppé
+l'intégralité du corps de `_nettoyer_arbre_claude` dans un garde-fou
+(`try/except Exception`) : `_lister_processus_pgid` peut lever une `OSError`
+sur `iterdir()`, `os.killpg` une `PermissionError`, et l'appel `ctypes`
+Windows n'importe quelle exception — aucune ne doit s'échapper d'une fonction
+appelée depuis un `finally`, sous peine de masquer la valeur de retour de
+`lancer_claude`.
+
+**Tests de non-régression** :
+- `tests/test_nettoyage_arbre_247.py` (POSIX, inchangé) — un faux `claude`
+  (script shell en tête de `PATH`) lance un vrai enfant bloqué (lecture sur
+  un FIFO jamais écrit, équivalent d'une lecture stdin qui n'aboutit jamais)
+  puis termine aussitôt ; le test vérifie que l'enfant est mort après le
+  retour de `lancer_claude`, que le nettoyage est journalisé, et que le
+  process de test (jouant le rôle du watcher) n'est jamais affecté.
+- `tests/test_nettoyage_arbre_windows_249.py` (Windows, ajouté #249) — le
+  scénario réel n'étant pas exécutable sur le ThinkPad (Linux), ce test mocke
+  `ctypes.windll` (et force `os.name = "nt"`) pour vérifier que
+  `_preparer_job_windows` appelle bien `CreateJobObjectW` /
+  `SetInformationJobObject` / `AssignProcessToJobObject` dans le bon ordre,
+  que `_nettoyer_arbre_claude` ferme bien le handle de job et journalise
+  succès/échec, et qu'une exception pendant le nettoyage n'est jamais
+  remontée. ⚠️ **Ce mock ne remplace pas une validation réelle sur la VM
+  CCW** : il vérifie que le code ctypes fait les bons appels, pas que Windows
+  tue effectivement l'arbre de process en pratique — cette validation reste
+  à faire par un build réel.
 
 > **Historique : services systemd (abandonnés).** L'issue #119 avait déployé les
 > watchers en services `systemd --user` (`systemd/watcher@.service`,
# ── Zone modifiée : ligne 1575 (4 ligne(s)) dans l'ancienne version → ligne 1618 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1575,4 +1618,4 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 27 juillet 2026 — Isole le push de la route pièces jointes sur une branche orpheline dédiée, `pieces-jointes` (issue #248). Contexte : la route `POST /joindre-image` (§18, issue #191) terminait par `git push origin HEAD:<branche_courante>` — or git ne peut pas publier un commit sans ses ancêtres, ce push emportait donc AVEC l'image tous les commits locaux non encore poussés de la branche de travail, c'est-à-dire tout travail que CCL avait committé et qu'Alain n'avait pas encore relu : brèche dans le garde-fou central « CCL ne pousse jamais, Alain vérifie puis pousse » puisque rien d'autre n'était censé pousser à sa place ; aggravé par la propagation automatique aux autres clones (watchers en `git pull --ff-only` de début de cycle, dont la VM CCW, en quelques secondes) et par le fait que le fichier était écrit et committé DANS `REP_TRAVAIL` — l'arbre de travail qu'un watcher peut être en train d'utiliser pour une tâche `mode_write` au même instant. **Solution retenue** : commit construit par PLOMBERIE git (`hash-object -w` sur un fichier temporaire hors dépôt, puis `read-tree`/`update-index --cacheinfo`/`write-tree` sur un index TEMPORAIRE isolé via `GIT_INDEX_FILE`, puis `commit-tree`), sans jamais toucher à l'arbre de travail, à l'index réel ni à `HEAD` du dépôt ; racine sans parent à la première publication, sinon enfant du tip précédent (`git fetch origin pieces-jointes` best-effort) ; poussé isolément (`git push origin <sha>:refs/heads/pieces-jointes`) sur une branche **orpheline** ne contenant que `issue-attachments/` — par construction, aucun commit de code ne peut plus jamais être emporté, quel que soit l'état de la branche de travail. URL adaptée en conséquence (`.../pieces-jointes/issue-attachments/<fichier>`) ; le fichier n'est plus jamais écrit dans `REP_TRAVAIL` (transite par un fichier temporaire, nettoyé dans un `finally`). Le repli « garde-fou minimal » (refus si `rev-list --count` > 0) n'a pas été nécessaire, la plomberie s'étant révélée simple à implémenter proprement. **§18 réécrit** (nouvelle sous-section **§18.1bis** détaillant le mécanisme, **§18.2** complété : la justification de l'exception `push` ne repose plus seulement sur l'intention d'Alain mais aussi sur l'impossibilité technique désormais garantie de publier du code par cette voie). **Testé de bout en bout** sur un dépôt jetable (bare + clone) : un commit local « FIX CCL non relu » jamais poussé reste totalement absent d'origin après upload d'image (objet introuvable sur le bare, branche de travail inchangée, `HEAD`/index/arbre de travail du clone intacts — `git status --porcelain` vide) ; branche `pieces-jointes` créée avec un unique fichier sous `issue-attachments/`, sans ancêtre commun avec la branche de travail (`git merge-base` échoue, confirmant l'historique orphelin) ; deuxième upload vérifié en accumulation (2 commits, 2 fichiers, parenté correcte). Aucune section renumérotée hors les ajouts internes au §18. Précédemment — Garantit qu'aucun descendant du process `claude` ne survit au retour de `lancer_claude` (issue #247). Contexte : un `cmd.exe` de build Windows (CCW, `rebuild_scrabble.bat`) était resté vivant après la fermeture de l'issue, verrouillant `Scrabble-Setup.exe` jusqu'à un `taskkill` manuel — sans le moindre signal dans le journal ; défaut de fond, générique : rien ne garantissait qu'un process lancé pendant une tâche soit mort à la fin de celle-ci. **`lancer_claude`** (`watcher.py`) lance désormais `claude` via `subprocess.Popen` (plutôt que `subprocess.run`, pour garder la main sur le PID) avec `start_new_session=True` (POSIX) / `CREATE_NEW_PROCESS_GROUP` (Windows), isolant ce process dans un groupe/une session à lui ; un bloc **`finally`** — donc exécuté quel que soit le mode de sortie (succès, échec, `TimeoutExpired`, exception), et **avant** `commenter_resultat_avec_retry`/`fermer_issue` — appelle la nouvelle `_nettoyer_arbre_claude(proc)` : sous POSIX, `_lister_processus_pgid` énumère (lecture directe de `/proc`, sans dépendance externe) les process vivants du pgid de ce `claude`, journalise chacun en `log.warning` (PID + ligne de commande) puis `os.killpg(pid, SIGKILL)` sur ce seul groupe ; sous Windows, `taskkill /PID <pid> /T /F`. **Solution retenue** (justifiée en détail dans la nouvelle sous-section **§13** « Nettoyage de l'arbre de process après une tâche ») : terminaison de l'arbre après coup plutôt qu'un objet Job Windows (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) — ce dernier est natif et sans fenêtre de course, mais une API Windows pure (`ctypes`/`pywin32`) sans équivalent POSIX, alors que `watcher.py` est le script UNIQUE partagé par CCL et CCW ; fenêtre de course résiduelle de quelques millisecondes entre la fin de `communicate()`/le timeout et l'appel de nettoyage, jugée négligeable et strictement meilleure que l'absence totale de garantie d'avant #247. **Point 4 (critique), vérifié explicitement** : le nettoyage ne cible **jamais** par nom d'exécutable, seulement le pgid/l'arbre du PID de CE `claude`, garanti distinct de celui du watcher et de tout watcher frère par construction (`start_new_session`/nouvelle session) — une erreur ici aurait pu arrêter tous les watchers d'une même machine. **Journalisation, pas critère d'échec** : chaque orphelin tué produit un `log.warning` explicite ; le nettoyage ne fait jamais échouer la tâche, c'est une garantie de fin de traitement. **Test de non-régression** : nouveau `tests/test_nettoyage_arbre_247.py` — un faux `claude` (script en tête de PATH) lance un vrai enfant bloqué sur lecture (FIFO jamais écrite, équivalent stdin qui n'aboutit jamais) puis termine ; le test vérifie que l'enfant est mort après le retour de `lancer_claude`, que le nettoyage est journalisé (PID présent dans un `log.warning`), et que le process de test (rôle du watcher) n'est jamais affecté — passe (`python3 tests/test_nettoyage_arbre_247.py` → ✅). Aucune section renumérotée. Précédemment — Aligne le texte historique du §14 sur l'amendement #244 (issue #245). Contexte : le paragraphe « ⚠️ Contrainte d'exécution synchrone (rappel) », hérité de #208 et volontairement laissé intact par #244 comme référence documentaire, interdisait encore catégoriquement « un mécanisme d'attente différée, de tâche en arrière-plan ou de "je répondrai plus tard" » — formulation contredite par le texte en vigueur de `consignes/globales.md` depuis #244 (l'arrière-plan encadré, avec interrogation de la sortie en boucle DANS la même exécution, y est permis ; seul conclure son tour de parole avant la fin réelle et vérifiée de l'opération reste proscrit). Un Claude Chat consultant le §14 en premier — cas fréquent, section de référence sur la délégation — pouvait lire l'interdiction absolue sans descendre jusqu'à l'encart d'injection qui la nuançait déjà, et reconduire dans une issue de build une consigne que le système n'applique plus. **§14** : le paragraphe est reformulé pour dire une seule chose, alignée sur `globales.md` — proscrit : conclure son tour de parole avant la fin réelle et vérifiée de l'opération ; permis : l'arrière-plan encadré (interrogation de la sortie en boucle DANS la même exécution) ; restent interdits sans changement : « monitor », notification, rappel programmé, formulations « je répondrai plus tard ». Reste du paragraphe conservé tel quel (aucune reprise possible après réponse, boucle `sleep` + `gh issue view` pour l'attente d'un ouvrier) ; l'encart d'injection qui suit (issues #209/#243) n'a pas été touché, sa nuance restant exacte. Recherche `arrière-plan`/`monitor`/`attente différée` sur tout le fichier : une autre occurrence trouvée hors §14 et hors pied de page — **§12.1** (ligne « Globale » du tableau des trois couches : « contrainte d'exécution synchrone et bloquante, sans attente différée, universelle depuis #243 ») — laissée telle quelle, ce résumé reste exact (l'interdit qu'elle nomme est bien l'attente différée pour conclure, pas l'arrière-plan comme technique) ; le pied de page (historique de #244 et antérieurs) laissé tel quel par consigne explicite. Aucune section renumérotée, aucun fichier `.py` ni `consignes/*.md` modifié. Précédemment — Amende la contrainte d'exécution universelle de #243 pour lever une contradiction qu'elle introduisait avec le plafond de timeout de l'outil Bash (issue #244). Contexte : le texte issu de #243 interdisait catégoriquement l'arrière-plan (« Ne lance jamais une commande en arrière-plan ») et proposait comme repli de relancer avec un timeout explicite plus long — or l'outil Bash a un timeout MAXIMUM par appel (de l'ordre de dix minutes) qu'aucun paramètre ne permet de dépasser ; si un build excède ce plafond (hypothèse plausible pour #241/#242, probablement à l'origine du basculement en arrière-plan qui avait motivé #243), l'agent se retrouvait pris entre deux interdits — attendre en un seul appel ou lancer en arrière-plan — et improviserait. Second défaut, dans la même phrase : le repli « boucle sur sa sortie DANS cette même exécution » SUPPOSE une exécution en arrière-plan (on lance, puis on interroge la sortie en boucle) ; la consigne décrivait donc le bon comportement tout en interdisant le mécanisme qui le rend possible. Le fautif n'est pas l'arrière-plan en soi, c'est de conclure son tour de parole sans avoir attendu la fin réelle de l'opération. **`consignes/globales.md`** : la fin du bullet « Contrainte d'exécution » (à partir de « Si une opération dépasse le timeout d'un appel d'outil… ») est réécrite — ce qui est interdit, c'est de CONCLURE le tour de parole avant que l'opération soit terminée et son résultat vérifié, pas l'arrière-plan comme technique ; en cas de dépassement du timeout d'un appel d'outil, deux voies restent permises : relancer avec un timeout explicite plus long tant que le plafond de l'outil le permet, OU lancer en arrière-plan À CONDITION IMPÉRATIVE d'interroger sa sortie en boucle DANS cette même exécution jusqu'à complétion réelle ; restent interdits sans changement le « monitor », la notification, le rappel programmé et toute formulation « je répondrai/j'attends… » en guise de conclusion ; rappel inchangé qu'aucune reprise n'existe (le watcher ferme l'issue dès la réponse postée). **`consignes/type_chef.md`** vérifié : sa formulation (« aucune attente différée, aucun monitor ») reste cohérente avec le nouveau texte — non touché. **§12.1** (ligne « Globale ») et **§14** (encart d'injection automatique) vérifiés : leurs résumés restent exacts sans qu'il soit besoin d'y ajouter la précision arrière-plan/plafond — non touchés. Aucune section renumérotée, aucun fichier `.py` modifié. Précédemment — Généralise l'interdiction d'attente différée à toute issue et distingue opération longue légitime du blocage sans progrès (issue #243). Contexte : les issues #241/#242 (builds Scrabble, CCW) se sont fermées `done` avec un rapport annonçant attendre une notification de fin de build ou un rappel programmé, alors que le build avait réellement abouti (`Scrabble.exe` et `Scrabble-Setup.exe` présents, datés du jour) — pas un échec de build, un rapport ne reflétant pas la réalité, produit par un agent sorti avant la fin. Deux consignes en cause, inversées par rapport à ce qu'exige une tâche longue : `consignes/globales.md` (injecté dans TOUTE issue) demandait d'abandonner toute commande « boucle/tarde anormalement (> 30s sans progrès net) » — écrit pour #214 (commande refusée par le système de permissions, bouclage réel), mais assez général pour couvrir aujourd'hui un build PyInstaller + Inno Setup (plusieurs minutes, peu de sortie visible), appliqué à la lettre ; l'interdiction qui aurait dû s'appliquer (ne jamais recourir à une attente différée, un « monitor », etc.) vivait dans `consignes/type_chef.md`, injecté SEULEMENT pour le TYPE `chef` — une issue de build n'en est pas une. Le mode de défaillance n'ayant rien de spécifique au rôle de chef (il guette toute tâche dont une étape dépasse le timeout d'un appel d'outil), la contrainte est rendue universelle. **`consignes/globales.md`** : le rappel issu de #214 est reformulé pour distinguer une commande refusée par les permissions ou bloquée SANS AUCUN PROGRÈS (→ abandon immédiat, comportement inchangé) d'une opération longue mais qui PROGRESSE normalement (build, compilation, installation de dépendances, suite de tests, clonage volumineux — → ce n'est PAS une anomalie, il faut attendre sa fin) ; le seuil de 30s ne s'applique plus qu'à l'absence de progrès, plus à la durée en soi. Nouveau rappel généralisé depuis `type_chef.md` : accomplir la tâche en une seule exécution synchrone et bloquante, jamais de commande en arrière-plan / « monitor » / notification / rappel programmé / « je répondrai quand… », relancer avec un timeout explicite plus long ou boucler DANS la même exécution en cas de dépassement du timeout d'un appel d'outil, jamais conclure sur une attente — rappel qu'aucune reprise n'existe, le watcher fermant l'issue dès la réponse postée. **`consignes/type_chef.md`** : allégé pour éviter la redondance — ne garde que la spécificité chef (boucler `sleep` + `gh issue view` en attendant la fermeture des issues ouvrières, puis synthèse finale), la contrainte générale étant désormais dans `globales.md`. **TYPE `build`** : vérification de `watcher.deduire_type_issue`/`TYPES_ISSUE` — `build` n'est PAS une valeur reconnue (`TYPES_ISSUE` = chef/ouvrier/spec_vue/spec_metier/spec_persistance/normal, et `_classer_valeur_type` n'a aucune branche pour « build » : même un en-tête explicite `| TYPE | build |` retomberait sur `normal`) ; `consignes/type_build.md` n'a donc PAS été créé — le mécanisme ne s'y prête pas sans modifier `watcher.py` (hors périmètre de cette issue), et de toute façon le vrai correctif (la contrainte universelle dans `globales.md`) couvre déjà le cas des builds sans dépendre d'un TYPE dédié. **§12.1** : la parenthèse résumant les rappels globaux (ligne « Globale ») mise à jour pour refléter la distinction blocage/progrès et la contrainte d'exécution synchrone désormais universelle. **§14** : le bloc « Contrainte d'exécution impérative » renommé « rappel » et son encart d'injection automatique mis à jour pour pointer vers `globales.md` (universel depuis #243) plutôt que `type_chef.md`, qui n'ajoute plus que la spécificité chef. **§1** : rattrapage d'une omission de #240 — la réécriture du paragraphe sur le pull automatique avait fait disparaître la parenthèse sur les projets à **périmètre dynamique** (dépôt-cible défini par issue, dépôts d'audit non rafraîchis par le pull automatique, distincts du clone de travail du watcher) ; réintroduite, adaptée au nouveau texte. Aucune section renumérotée. Précédemment — Correctif documentaire §1/§14/§16 et rattrapage de trois issues committées sans mise à jour du DOC (issue #240). Incident du 26/07 : le clone `C:\CCW\Bridge_Agent` de la VM (celui d'où s'exécute réellement `watcher.py`) avait **80 commits de retard** sur `origin/master`, sans aucun signal — le service tournait avec du code antérieur à l'issue #195, cause probable de l'incident #236 (issue fermée `done` sans commentaire de résultat). **§1** réécrit : le `git pull --ff-only` automatique de début de cycle porte bien sur `REP_TRAVAIL` avec la même logique CCL/CCW, mais ne met à jour le CODE du watcher que lorsque `REP_TRAVAIL` coïncide avec le clone du dépôt Bridge_Agent — vrai côté CCL, **faux** côté CCW en modèle unifié (#231), où `REP_TRAVAIL = \\VBOXSVR\CCW_Share` n'est même pas un dépôt git et où le clone contenant `watcher.py` (`C:\CCW\Bridge_Agent`) vit ailleurs, mis à jour par personne. L'ancienne affirmation « comportement identique CCL et CCW » est supprimée car trompeuse sur ce point précis. **§16** gagne un bloc d'avertissement opérationnel : ce clone n'est **jamais** mis à jour automatiquement ; procédure obligatoire après tout push touchant `watcher.py` — `git pull --ff-only` dans `C:\CCW\Bridge_Agent` **puis redémarrage du service** `CCW-Watcher` (`nssm restart`, un pull seul ne suffit pas : un process Python déjà démarré garde en mémoire le code chargé à son lancement) — avec la commande de contrôle rapide `git status -sb` (ne doit jamais afficher `behind`), et le cas réel des 80 commits de retard comme justification. **§14** corrigé : dans le bloc « Quand NE PAS passer par un chef » (#225), la référence au service `CCW-Watcher-<Projet>` — nom venant du modèle multi-projets abandonné par #231 — est remplacée par `CCW-Watcher`. Rattrapage de trois issues committées sans entrée de pied de page : **#237** — `commenter_issue`/`editer_dernier_commentaire` passent par `--body-file` (fichier temporaire UTF-8) au lieu de `--body`, supprimant la limite argv Windows de 32767 caractères ; `commenter_resultat_avec_retry` vérifie désormais la publication par relecture de l'issue (un exit code 0 de `gh` ne suffit plus, la présence effective du commentaire est exigée) ; nouveau marqueur `MARQUEUR_RESULTAT` (`<!-- bridge:resultat -->`) en tête du commentaire de résultat, utilisé aussi par `resultat_deja_poste` à la place de l'ancienne sous-chaîne `"## Résultat"` qui matchait à tort `"## Résultat attendu"` ; test `tests/test_verification_commentaire_237.py` ; deux effets de bord assumés — deux appels `gh` par tentative, et possibilité d'un commentaire en double si la publication réussit mais que la relecture échoue transitoirement (perte silencieuse échangée contre doublon visible). **#238** — `fermer_issue` inspecte désormais les codes de retour de `close` et `add-label`, retourne un booléen, et journalise explicitement les états incohérents (fermée sans label / label sans fermeture) sans compensation automatique. **#239** — libellé d'agent de l'ACK déduit automatiquement de `platform.system()` (« agent Linux » / « agent Windows »), avec champ optionnel `LIBELLE_AGENT` pour forcer un libellé explicite si la détection automatique ne convient pas ; le §16 avait déjà été modifié par cette issue mais aucune entrée de pied de page n'avait été ajoutée — rattrapée ici. Aucune section renumérotée. Précédemment — §3 « Créer une issue » : ajout d'une **exception `PROJET`** pour les issues `for-windows` (issue #233, suite #231). Rapport remonté par le Claude du projet `actualise` : lors de la génération d'une issue de build Windows, le champ `PROJET` avait été renseigné avec `actualise` au lieu de `bridge_agent`, en appliquant par erreur la règle générale du §3 (« nom exact du projet cible »). Or le §16.3 (modèle CCW unifié, #231) applique correctement `PROJET=bridge_agent` dans son template — c'est la config du watcher CCW unique qui compte, pas le projet réellement construit — mais le §3, consulté en premier par Claude Chat, ne mentionnait pas cette exception. Ajout d'un second bloc d'avertissement juste après celui existant (« Claude Chat doit toujours inclure `| PROJET | <nom> |` ») précisant que pour les issues `for-windows`, `PROJET` reste toujours `bridge_agent`, le nom du projet cible s'exprimant en texte dans le corps (chemins, `git clone`/`git pull`), avec renvoi au template du §16.3. Aucune section renumérotée. Précédemment — §16 « Agent Windows CCW » : documentation du **modèle CCW unifié** (issue #231), qui remplace le modèle multi-projets (#170, un service NSSM par projet). Un seul service NSSM `CCW-Watcher` surveille désormais les issues `for-windows` de `AlainDelree/Bridge_Agent`, `REP_TRAVAIL = \\VBOXSVR\CCW_Share` (accessible depuis Linux à `/home/alain/Bridge_Agent_CCW_Share/`), chaque projet buildé étant cloné dans un sous-dossier dédié `\\VBOXSVR\CCW_Share\CCW\<projet>\` — séquencement strict des builds par construction (un seul process `watcher.py`), zéro contention CPU/RAM entre builds parallèles. Validé en production avec le build PyInstaller d'`actualise`. Introduction du §16 réécrite (titre « (en préparation) » retiré, devenu opérationnel) ; nouvelle sous-section **§16.3 « Procédure — builder un projet Windows »** détaillant le template d'issue en 4 étapes (exception `git config --global --add safe.directory` sur le chemin UNC — obligatoire une seule fois par sous-dossier —, clone ou `git pull --ff-only`, `pip install -r requirements.txt`, build `python -m PyInstaller --noconfirm --onedir --noconsole`), la récupération manuelle des artefacts côté Linux et le rappel qu'aucun token GitHub Contents n'est requis (dépôts publics, seul le token Issues du service `CCW-Watcher` sert). Les scripts `ajouter_projet_ccw.ps1` et `finaliser_projet_ccw.ps1` (tableau de provisioning) marqués **« obsolète — modèle multi-projets abandonné, conservé à titre historique »** — ne plus les utiliser, mais conservés dans le dépôt sans suppression. Reste du §16 (§16.1 maintenance 90 jours, §16.2 onglet CCW, description historique du modèle multi-projets #170) laissé inchangé, hors du périmètre de cette issue. Précédemment — §14 « Délégation Chef → Ouvrier » : ajout d'un bloc **« Quand NE PAS passer par un chef »** (issue #225), inséré juste après le paragraphe « Principe » et avant « Ce n'est pas déclenché automatiquement… ». Contexte : sur le projet `actualise`, une tâche entièrement Windows avait donné lieu à une issue chef CCL dont le seul travail était de créer immédiatement un ouvrier CCW et d'attendre sa fermeture — sans étape réelle côté Linux, correct mais coûteux (deux issues, deux invocations `claude`, TIMEOUT long, attente synchrone bloquante payée pour rien). Le nouveau bloc pose le **critère de décision** : le chef se justifie quand la tâche comporte du travail réel côté Linux (avant et/ou après) dans la même unité de travail ; si la TOTALITÉ de la tâche s'exécute sous Windows, créer directement l'issue avec `| LABELS | for-windows |` (§3) plutôt qu'un chef. **Contre-exemple explicite** : un chef qui se contente de créer un ouvrier puis d'attendre sa fermeture, sans orchestration réelle, est du surcoût pur. Rappel que l'**exemple validé** plus bas dans la section (dictionnaire déposé côté Linux puis rebuild côté Windows) reste un cas où le chef EST justifié — la nouvelle règle ne le contredit pas. **⚠️ Contrepartie opérationnelle** ajoutée dans le même bloc : le rallumage automatique du watcher à la création d'une issue (§13, mécanisme 2) ne vaut QUE pour les issues `for-linux` — une issue `for-windows` directe ne démarre rien, donc vérifier dans l'onglet CCW (§16.2) que la VM `CCW-Build` tourne et que le service `CCW-Watcher-<Projet>` est démarré avant d'en envoyer une, sinon elle reste ouverte sans aucun signal. En miroir, **§3** (paragraphe décrivant le champ `LABELS`, juste après la phrase sur le cas d'usage `| LABELS | for-windows |`) gagne une phrase de renvoi croisé vers ce bloc du §14. Aucune section renumérotée ; reste du §14 (contrainte d'exécution impérative, format des titres, timeout du chef, exemple validé) et reste du §3 inchangés. Précédemment — Nouvelle section **§19 « Calibration automatique du TIMEOUT »** (issue #224), documentant de bout en bout le système mis en place par les issues #220 (extension d'`historique_durees.json`), #221 (mécanique EWMA `etat_timeout.json`/`etat_ambiance.json`), #222 (exposition du `TIMEOUT_suggéré` dans le commentaire de clôture GitHub) et #223 (exclusion des `expiree=true` du badge d'estimation de l'interface). Jusqu'ici ce système n'était documenté nulle part dans `BRIDGE_AGENT_DOC.md` — seul `CONTEXTE.md` en gardait une trace partielle, ajoutée par #221 et jamais mise à jour depuis, de toute façon plafonnée par sa limite de taille pour l'injection prompt (§12.1). La nouvelle section couvre, à partir d'une lecture du code réel de `watcher.py`/`app/issues.py` (pas une paraphrase des rapports d'issue) : l'objectif et le principe d'inspiration (RTO TCP, Jacobson/Karels), la formule complète et chacun de ses termes, les deux fichiers d'état (`logs/etat_timeout.json`, `logs/etat_ambiance.json` — partagés entre watchers, verrouillés, écriture atomique), le tableau des constantes actuelles en soulignant explicitement qu'elles sont des valeurs de DÉPART non backtestées, le canal d'exposition (bloc `⏱️/📊` dans le commentaire de clôture, sans aucune application automatique — le TIMEOUT réellement utilisé reste celui de l'en-tête, `extraire_timeout`), et une liste explicite des limitations connues (`tag_reseau` jamais peuplé donc `F_reseau`/`F_local` neutres, incohérence inerte de `lire_timeout_suggere` sur échec définitif, démarrage à froid trompeusement optimiste, aucun backtest des constantes, distinction avec le badge `estimer_duree` de #223). Aucune autre section renumérotée ni modifiée. Précédemment — Correctif horloge d'auto-extinction (issue #217) : le watcher pouvait s'éteindre **immédiatement après un traitement réel** lorsque celui-ci s'étirait au-delà du délai d'inactivité (`DELAI_INACTIVITE_MIN`, défaut 20 min). Cause : `derniere_activite` (horloge monotone d'inactivité, #200) n'était réarmée qu'**en tête de cycle**, juste après `lister_issues()` et **avant** de lancer `traiter_issue()` — donc jamais pendant le traitement (potentiellement long : plusieurs timeouts de 300 s + retries en cascade). Si le traitement d'une seule issue dépassait le délai (cas réel `watcher-scrabble.log` du 24/07/2026 : #237/#238 traités sans interruption de 08:59 à 09:22, puis extinction à 09:23:08 — 14 s après le succès de #238), l'horloge restait figée à l'instant du **début** du cycle ; le test d'extinction du cycle suivant se déclenchait alors sur une horloge périmée, ne reflétant pas le travail réellement effectué. **Correctif** (`watcher.py`, boucle principale) : réarmement de `derniere_activite` **aussi APRÈS** la boucle de traitement, dès qu'au moins une issue traitable a été traitée ce cycle (option a du diagnostic — réarmer sur le travail réel, préférée à l'option b « revérifier `lister_issues()` avant `sys.exit` » car elle satisfait plus directement l'objectif « ne jamais éteindre si du travail vient d'avoir lieu », sans appel réseau supplémentaire ni cas où une issue devenue fermée entre-temps laisserait l'extinction filer). Le flag `travail_a_faire` (calculé une fois) conditionne les deux réarmements ; l'extinction reste possible quand plus rien n'est traitable. **Test de non-régression** : `tests/test_auto_extinction_217.py` pilote le vrai `watcher.main()` avec horloge mockée (`time.monotonic`/`time.sleep` patchés) sur 3 scénarios — (1) traitement long ~23 min + issue restante → **pas** d'extinction prématurée (échoue sur le code d'avant #217, passe sur le code corrigé), (2) inactivité réelle → extinction bien déclenchée, (3) issue non-traitable (`done`) → n'empêche pas l'extinction. §13 (mécanisme 3 « Extinction automatique ») mis à jour pour décrire le double réarmement avant/après. Précédemment — Nouveau rappel global « abandon immédiat au refus de permission » (issue #214) : ajout, à la fin de `consignes/globales.md`, d'un rappel systématique — si une commande/un outil est **refusé par le système de permissions** (session non-interactive, aucune approbation possible) ou **boucle/tarde anormalement** (> 30s sans progrès net), CCL doit **abandonner immédiatement** l'approche et le signaler dans son rapport plutôt que de retenter, en basculant si possible sur un repli plus simple (lecture directe, `grep`, analyse manuelle) et sans jamais insister sur une commande déjà refusée. Motivation : comparaison des issues Scrabble #235 (timeout à 300s, bouclage sur une commande refusée) et #238 (succès) — la seule différence significative était la présence, dans #238, d'une consigne explicite d'abandon-au-lieu-de-retenter ; en session non-interactive, un refus de permission Claude Code est systématique et définitif (aucun utilisateur pour approuver), donc retenter est vain. Consigne volontairement **générale** (pas spécifique à Scrabble ni à JS/eslint) car le problème touche toute commande nécessitant une approbation (installation de paquet, exécution d'un binaire, etc.), quel que soit le projet ou le langage. §12.1 : la parenthèse résumant les rappels globaux dans le tableau des trois couches est complétée (ajout d'« abandon immédiat au refus de permission / boucle anormale ») ; la liste complète des rappels n'étant pas reproduite ailleurs dans la doc, aucune autre duplication à mettre à jour. Précédemment — Déplacement de l'injection des consignes trois couches dans `watcher.py` — couverture universelle (issue #211). Les consignes (globales/type/projet, #209) ne sont plus écrites dans le **corps** de l'issue par `app/issues.py` (chemin qui ne couvrait QUE les issues créées via le formulaire web), mais injectées dans le **prompt donné à CCL au moment du traitement** par `watcher.py` (`lancer_claude` → nouvelles `_consignes_injectees`/`_lire_consigne`, reprises de `app/issues.py`), exactement sur le modèle de `CONTEXTE.md`/`FICHIER_CONTEXTE`. Le point de passage devient **unique** : peu importe le chemin de création — formulaire web, `gh issue create` d'un chef (§14), création manuelle GitHub (§3) — `watcher.py` déduit le TYPE (`deduire_type_issue` sur le titre/corps réels) et le projet (`CFG.nom`), puis ajoute le bloc **après** le bloc `CONTEXTE` et **avant** la clause de périmètre / le garde-fou (regroupement des « règles » en fin de prompt, zone la mieux suivie). Cas particulièrement corrigé : les issues **ouvrières créées par un chef** (chemin 2, vraies tâches `mode_write`) recevaient auparavant zéro consigne — c'est justement là que les rappels de sécurité comptent le plus. `app/issues.py::construire_body` revient à un corps **en-tête + corps rédigé** seulement (suppression de `_consignes_injectees`/`_lire_consigne`/`DOSSIER_CONSIGNES` et de l'import `logging` devenu inutile) — source unique de vérité désormais côté watcher, plus de double injection. Garde-fous inchangés (#209) : `globales.md` absent → `log.warning` sans bloquer le traitement ; `type_*`/`projet_*` absents → silencieux. Conséquence assumée (comme pour `CONTEXTE.md`) : les consignes ne sont plus visibles dans le corps d'une issue sur GitHub. **§12.1 réécrite** (modèle prompt + couverture universelle des 3 chemins + emplacement dans le prompt) et **§10** mis à jour (`consignes/` = injecté dans le prompt CCL, plus « en tête de chaque issue »). Testé de bout en bout par une issue `TYPE=chef` `mode_write` créée **directement en CLI** (`gh issue create`, hors formulaire) : le prompt CCL assemblé par le watcher contient bien les consignes globales + `type_chef.md`. Précédemment — Architecture à trois couches d'injection de consignes (issue #209) : nouveau dossier `consignes/` à la racine, injecté **dans le corps de chaque issue** par `app/issues.py` (`construire_body` → `_consignes_injectees`), entre le tableau d'en-tête et le corps rédigé par Claude Chat. Trois couches, de la plus générale à la plus spécifique : **globales** (`consignes/globales.md`, **NON-optionnel** — rappels de sécurité transversaux : ne jamais pousser, backup avant modif, respect du périmètre — injecté dans TOUTE issue), **type** (`consignes/type_<type>.md`, **facultatif** — ex. `type_chef.md` reprenant la contrainte d'exécution synchrone du #208, injecté selon le TYPE déduit par `watcher.deduire_type_issue`), **projet** (`consignes/projet_<projet>.md`, **facultatif** — aucun créé par défaut). Ordre final : en-tête → globales → type (si présent) → projet (si présent) → corps. Vaut en **mono-issue comme en mode lot** (chaque bloc `#Titre:` passe par `construire_body` avec son propre TYPE). **Choix délibéré anti-piège de maintenance** : contrairement à `CONTEXTE.md`, les couches type/projet sont sans obligation de présence (un projet sans `projet_<nom>.md` fonctionne normalement, rien à créer/maintenir) et créées uniquement à la demande. Garde-fous : fichier `type_*`/`projet_*` absent → aucune injection **sans** log (normal, pas une anomalie) ; `globales.md` introuvable → `logging.warning` clair **sans jamais faire échouer** la création d'issue. Nouvelle sous-section **§12.1** décrivant l'architecture, mise à jour du **§10** (dossier `consignes/`) et du **§14** (la contrainte d'exécution synchrone du chef n'est plus à recopier manuellement — elle est injectée automatiquement via `consignes/type_chef.md`). Testé de bout en bout (issue `TYPE=chef` réelle : corps GitHub contenant, dans l'ordre, globales puis chef puis corps original). Précédemment — Finalisation du nettoyage doc MVC (issue #208, suite #207) : le §14 « Délégation Chef → Ouvrier » gagne un bloc **« ⚠️ Contrainte d'exécution impérative »** rappelant que le chef doit accomplir la TOTALITÉ de sa tâche (attente de fermeture des ouvriers + synthèse finale comprises) en **une seule exécution synchrone et bloquante** — aucune reprise n'étant possible après qu'une issue a été répondue/fermée, ne jamais recourir à une attente différée, une tâche en arrière-plan ou un « je répondrai plus tard » ; si une attente est nécessaire, boucler (`sleep` + `gh issue view`) DANS la même exécution. Cette finalisation confirme aussi l'absence des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` à la racine de bridge_agent (jamais créés ici ; seul `CONTEXTE.md` existe et est conservé). Précédemment — Nettoyage doc MVC (issue #207) : **suppression de l'ancien §15 « Pattern Chef + Specs MVC (évolution future) »**, purement prospectif et jamais implémenté (le watcher ne lit pas le champ `SPECS`, aucun routage par couche Vue/Métier/Persistance n'existe) ; les sections suivantes **ne sont pas renumérotées** (16, 17, 18 restent 16, 17, 18) pour préserver les références croisées existantes. Le **§14 est entièrement réécrit** et recadré « Délégation Chef → Ouvrier (changement d'environnement) » : on ne garde que l'usage réel validé — un CCL « chef » crée lui-même une issue « ouvrier » ciblant un autre environnement (typiquement CCL Linux → CCW Windows) via `gh issue create` et surveille sa fermeture avant de livrer, sur instruction explicite (pas de détection auto du rôle chef, pas de décomposition automatique générique) — avec conseil de `TIMEOUT` généreux côté chef et l'exemple validé du build Scrabble/ouvrier CCW. En complément, l'issue chef #207 délègue à 6 issues « ouvrier » (une par projet actif hors bridge_agent et ff_galerie) la suppression des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` — vestiges du §15 abandonné — `CONTEXTE.md` (mécanisme standard hors MVC) étant conservé partout. Précédemment — §18 (nouveau) « Pièces jointes image dans les issues » (issue #191) : l'onglet « Nouvelle issue » accepte désormais un **upload optionnel PNG/JPEG** (champ fichier + bouton « Joindre une image » à côté du corps). Nouvelle route **`POST /joindre-image`** (`app/issues.py`, `joindre_image()`) : valide le type (Content-Type **et** magic bytes) et la taille (**≤ 5 Mo**), sauvegarde dans **`issue-attachments/`** (racine du `REP_TRAVAIL`) sous un nom **horodaté** anti-collision (`AAAAMMJJ-HHMMSS-<nom>.ext`), puis `git add` + `commit` + **`git push origin HEAD:<branche>`** (branche déduite **dynamiquement**, jamais supposée master/main), et retourne l'URL **`raw.githubusercontent.com/<owner>/<repo>/<branche>/issue-attachments/<fichier>`** — format qui s'affiche correctement dans les issues GitHub. Le frontend (`static/js/app.js`, `joindreImage()`/`insererDansCorps()`) insère alors **automatiquement** `![<nom>](<url>)` dans le corps à la position du curseur. **Exception `push` assumée et documentée (§18.2)** : ce commit+push est déclenché par **ALAIN** via l'outil (son action manuelle), **pas par CCL/le watcher** — la règle « CCL ne pousse jamais » n'est donc pas violée (elle vise les modifications de code de l'agent, pas une image qu'Alain publie lui-même). Gestion d'erreurs (§18.4) : **push échoué → aucune URL insérée** (commit conservé en local, poussable plus tard), **projet sans dépôt git → message clair**, type/taille/contenu invalides refusés proprement. `issue-attachments/` volontairement **hors `.gitignore`** (les images doivent être suivies/poussées). Testé de bout en bout (dépôt jetable + remote bare : succès + URL correcte, et chemins d'échec type/taille/magic/push). Précédemment — §17 (nouveau) « Notifications centralisées — détection serveur des transitions » (issue #187) : `new_issue.py`, qui tourne en permanence sur le ThinkPad, détecte désormais LUI-MÊME par polling `gh` les transitions d'issues (fermeture `done` = succès ; label `needs-human` = échec définitif) de **tous** les projets (for-linux ET for-windows), et déclenche bip/`notify-send`/`ntfy` **localement**, y compris pour les issues traitées par la VM **CCW** — **sans aucun appel réseau initié par la VM** (la VM n'écrit que sur GitHub). Nouveau module partagé `notifications.py` (racine) factorisant `bip`/`notifier_bureau`/`notifier_ntfy`/`notifier`, importé par `watcher.py` (enveloppes minces déléguant, sites d'appel inchangés) ET par le nouveau poller `app/notifications_poller.py` (thread démon lancé par `new_issue.py`). Script bip **déplacé/recréé** de `~/NicLink/bip.py` vers `scripts/bip.py` (infrastructure partagée) ; défaut `SCRIPT_BIP` et `configs/*.conf` mis à jour. Anti-doublon (point 4) : réglage `NOTIFIER_LOCAL` (`.conf`, défaut `true`) coupant la notif du watcher + portée `BRIDGE_NOTIF_SCOPE` (env, défaut `for-windows`) du poller. **Défaut livré sans régression ni doublon** (CCL notifie via son watcher, CCW via le poller — variante propre de l'option b) ; **option (a) « centralisation complète » recommandée mais laissée au choix d'Alain** car elle fait de `new_issue.py` une dépendance dure de toute notification (or il n'a pas encore de service systemd) — implémentée et à un réglage près (`BRIDGE_NOTIF_SCOPE=all` + `NOTIFIER_LOCAL=false` partout). **Action requise côté VM CCW** : poser `NOTIFIER_LOCAL=false` dans `configs\*-ccw.conf` pour éviter un double `ntfy`. Bonus (point 5) : le poller lit les labels COURANTS à la fermeture, donc `notif_pc`/`notif_gsm` ajouté EN COURS de traitement est bien pris en compte. Filtre de récence (`BRIDGE_NOTIF_RECENCE_MIN`, défaut 30 min) + amorçage silencieux au 1er cycle évitent le spam de vieilles issues au démarrage ; état en mémoire process. Précédemment — §1 « Vue d'ensemble » : documentation du **`git pull --ff-only` automatique en début de cycle** de `watcher.py` (issue #186, suite du #185 qui l'a implémenté). Le watcher rafraîchit son clone (`REP_TRAVAIL`) au début de chaque cycle de polling, juste avant `lister_issues()` : fast-forward transparent en cas de succès ; en cas de commits locaux non poussés (divergence) le `--ff-only` échoue proprement sans RIEN écraser et le watcher poursuit sur le code local — donc aucun risque à oublier un `git push`. Comportement **identique CCL (Linux) et CCW (Windows)** puisque `watcher.py` est le script unique partagé ; les projets à périmètre dynamique (dépôt-cible par issue) ne sont pas concernés. Un `git pull`/relance manuel reste possible pour une mise à jour immédiate (confort, plus une nécessité). Aucune instruction obsolète de « git pull manuel obligatoire » à corriger dans le §16 (aucune ne subsistait). Précédemment — §16 « Agent Windows CCW » : **onglet « CCW » dans l'interface web** (issue #174, sous-section §16.2) — pilotage complet de la VM et des projets CCW depuis Linux, sans PowerShell manuel dans la VM. Backend `app/ccw.py` (routes `/ccw/*`) exécutant les scripts existants à distance via `VBoxManage guestcontrol` : état/démarrage de la VM (`demarrer_ccw.sh`), liste des projets (nouveau `lister_projets_ccw.ps1`, sortie JSON encadrée), ajout (`ajouter_projet_ccw.ps1`) et finalisation non interactive (nouveau `finaliser_projet_ccw_auto.ps1` + `mettre_a_jour_tokens_ccw.ps1` doté d'un mode `-FichierTokens`). Sécurité : tokens jamais passés en argument ni journalisés (fichier temporaire `0600` poussé puis supprimé des deux côtés dans un `finally`) ; mot de passe `ccw-admin` lu depuis `CCW_ADMIN_PASSWORD` ou `configs/ccw_admin.secret` (gitignoré). Nouvel onglet + panneau dans `templates/index.html`, fonctions `ccw*` dans `static/js/app.js`, classe `.message.avertissement` dans `style.css`. Précédemment — §16 « Agent Windows CCW » : **finalisation d'un projet CCW en une seule commande** (issue #173, suite #170) — ajout de `provisioning/windows/finaliser_projet_ccw.ps1` qui, à partir du seul `-NomProjet`, dérive le service/dossier/config (même logique qu'`ajouter_projet_ccw.ps1`), vérifie leur existence, demande `TOPIC_NTFY` et l'écrit directement dans le config (remplacement ciblé du placeholder `###TOPIC_NTFY_A_DEFINIR###`, reste du fichier préservé en UTF-8 sans BOM), rappelle avec une pause la marche à suivre pour créer le token GitHub dédié, puis **appelle** `mettre_a_jour_tokens_ccw.ps1` (pas de duplication) pour la saisie masquée + pose des tokens + redémarrage + vérif des logs, et conclut par un résumé ; `mettre_a_jour_tokens_ccw.ps1` gagne un paramètre `-NomLog` pour vérifier le bon log de service (`ccw-<nom>-service.log`) ; les rappels d'`ajouter_projet_ccw.ps1` (en-tête + fin de script) et le §16 pointent désormais vers cette commande unique au lieu des 3 étapes dispersées. Non exécuté contre une VM réelle (test manuel par Alain). Précédemment — §11 « Conventions de code » : **règle BOM UTF-8 obligatoire pour tout script `.ps1`** (issue #172) — ajout du BOM (`EF BB BF`) manquant sur `ajouter_projet_ccw.ps1` (#170) et `mettre_a_jour_tokens_ccw.ps1` (#168), qui plantaient sinon sous Windows PowerShell 5.1 avec des `UnexpectedToken` en cascade sur les accents (même signature que #151) ; règle généralisée en §11 + rappel en tête du §16 pour prévenir la récidive (`provisionner.ps1` déjà OK depuis #151). Précédemment — §16 « Agent Windows CCW » : **généralisation multi-projets de CCW** (issue #170) — ajout de `provisioning/windows/ajouter_projet_ccw.ps1` (un clone + un config `configs\<nom>-ccw.conf` + un service NSSM `CCW-Watcher-<NomProjet>` dédiés par projet, sur le modèle des watchers CCL ; paramétrable `-NomProjet`/`-Depot`, idempotent, `watcher.py` inchangé) ; documentation du modèle « un service par projet » et de la **règle d'expiration alignée** des tokens (un token fine-grained dédié par dépôt, mais tous à la même échéance ≈ 17 octobre 2026) ; commande exacte d'instanciation de Scrabble et marche à suivre pour créer son token dédié (Repository access → Scrabble uniquement, Issues read/write + Metadata read-only). Précédemment — §16 « Agent Windows CCW » : ajout de la sous-section **§16.1 Maintenance périodique (renouvellement à 90 jours)** (issue #169) — runbook séquentiel consolidé pour la fenêtre de maintenance d'octobre 2026 : tableau de repères de dates (install **2026-07-19**, expiration Windows **2026-10-17**, token GitHub aligné ~90 j mais non stocké), puis procédure en 3 étapes renvoyant aux scripts existants — vérifier (`verifier_expiration_ccw.py`), recréer la VM (`creer_vm_ccw.py --recreate` + ré-attacher un ISO frais + `lancer_provisioning.py`), renouveler les tokens (`mettre_a_jour_tokens_ccw.ps1`) — sans dupliquer le détail technique déjà présent dans le §16. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/mettre_a_jour_tokens_ccw.ps1` (issue #168) — renouvellement des tokens `GH_TOKEN`/`CLAUDE_CODE_OAUTH_TOKEN` du service `CCW-Watcher` sans reconstruire à la main la chaîne `AppEnvironmentExtra` : saisie masquée (`Read-Host -AsSecureString`), séparateur `` `n`` impératif entre les deux paires (un espace corrompt `GH_TOKEN` → « Bad credentials »), `nssm set`/`nssm restart`, puis affichage automatique des 10 dernières lignes de `logs\ccw-service.log` pour confirmer l'absence d'erreur d'auth. Précédemment — §16 « Agent Windows CCW » : alerte d'expiration de l'éval 90 jours (issue #167) — ajout de `provisioning/windows/eval-expiration.json` (date d'installation **2026-07-19**, expiration **2026-10-17**) et du script `provisioning/windows/verifier_expiration_ccw.py` (côté Linux : calcule les jours restants, alerte + code de sortie 2 à ≤ 10 j, sinon confirmation calme ; `python3 provisioning/windows/verifier_expiration_ccw.py`) ; rappel `cron` + `ntfy` hebdomadaire proposé mais laissé à l'activation d'Alain. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/demarrer_ccw.sh` (issue #166), wrapper de démarrage de la VM `CCW-Build` depuis CCL (headless par défaut, `--gui`/`--fenetre` pour une fenêtre, `--status` pour l'état sans rien démarrer). Précédemment — §3 « Créer une issue » : ajout d'une note sur la **convention de présentation côté Claude Chat** pour l'envoi en lot (issue #153) — quand Claude Chat prépare plusieurs issues, il les présente toutes à la suite dans un seul bloc de code (pas un bloc par issue) pour un copier-coller en un clic. Précédemment — §16 « Agent Windows CCW » : `REP_TRAVAIL` généré par `provisionner.ps1` pointe désormais vers le **chemin UNC** `\\VBOXSVR\CCW_Share` (et non la lettre automontée `$LettrePartage`), seul accessible au service `CCW-Watcher` tournant sous LocalSystem (issue #149, suite #148) ; `$LettrePartage` conservé pour référence mais plus utilisé pour construire `REP_TRAVAIL`. Précédemment — le watcher CCW tourne comme **vrai service Windows** enregistré via NSSM (issue #148, suite #147) — `provisionner.ps1` installe `NSSM.NSSM` (winget) et enregistre le service `CCW-Watcher` (`SERVICE_AUTO_START` + `AppExit Default Restart` + `AppRestartDelay 5000`, stdout/stderr → `logs\ccw-service.log`, idempotent via `nssm stop`/`remove`), en remplacement de l'ancienne tâche planifiée `-AtLogOn` qui ne redémarrait pas au boot sans session ; équivalent direct des services systemd du §13. Précédemment — provisioning **phase 2** (issue #147, suite #146) — ajout de `provisioning/windows/provisionner.ps1` (installe l'outillage dans la VM via winget + Claude Code natif, clone le dépôt, écrit `ccw.conf`, enregistre la tâche planifiée `CCW-Watcher`) et `lancer_provisioning.py` (pousse/exécute ce script depuis CCL via `VBoxManage guestcontrol`) ; `watcher.py` inchangé (portable, `LABEL` paramétrable) ; limite Task Scheduler vs `Restart=always` documentée. Précédemment — ajout du §16 et du label `for-windows` (issue #146) : provisioning phase 1 de la VM Windows CCW (`provisioning/windows/creer_vm_ccw.py` + `autounattend.xml`) destinée aux builds .exe délégués par CCL. Précédemment — Bridge_Agent v1, 4 projets actifs. §3 « Créer une issue » : ajout de l'**envoi en lot** (issue #135) — coller plusieurs blocs `#Titre:` à la suite dans le même corps déclenche le mode lot (bouton « Envoyer le lot (N issues) »), chaque bloc étant envoyé en séquence comme une issue indépendante (avec ses `PROJET`/`TIMEOUT`/`MODELE` optionnels), sans validation intermédiaire, suivi d'un résumé listant le résultat de chacune. Ajout du projet `ecole` (AlainDelree/Ecole, ~/Ecole) aux tableaux §2 et §7 (issue #101). Section 15 « Chef + Specs MVC » : champ `SPECS` (pluriel, minuscules, combinable en une ligne) — correction du champ `SPEC` introduit par erreur (issue #97, suite #96).*
+*Dernière mise à jour : 27 juillet 2026 — Remplace, sous Windows, le `taskkill /PID <pid> /T /F` de `_nettoyer_arbre_claude` par un objet Job noyau (issue #249, suite #247). Contexte : le nettoyage livré par #247 était correct sous POSIX mais très probablement inopérant sous Windows — la seule plateforme où le problème d'origine (`cmd.exe` orphelin verrouillant `Scrabble-Setup.exe` après un build CCW) avait été observé. `_nettoyer_arbre_claude` s'exécute dans le `finally` de `lancer_claude`, donc APRÈS le retour de `proc.communicate()` : à cet instant le process `claude` est déjà terminé et réapé, or `taskkill /PID <pid> /T /F` exige que le PID cible existe ENCORE pour parcourir son arbre généalogique — sur un PID mort il échoue immédiatement (« process not found ») sans toucher un seul descendant, exactement le scénario d'origine. `CREATE_NEW_PROCESS_GROUP` ne comble pas l'écart (sous Windows les groupes de process ne servent qu'au routage Ctrl+C/Ctrl+Break, pas à la terminaison d'une arborescence). Aggravation : seul le succès du `taskkill` produisait un `log.warning`, rendant l'échec totalement silencieux sous Windows ; le test de non-régression #247, exécuté sous Linux, ne couvrait que la branche POSIX. **Solution retenue** : objet Job noyau Windows (`CreateJobObjectW` + `SetInformationJobObject(JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)` + `AssignProcessToJobObject`), implémenté en `ctypes` pur (pas de nouvelle dépendance, pas de `pywin32`) — nouvelles fonctions `_creer_job_windows_kill_on_close`/`_assigner_job_windows`/`_preparer_job_windows`. Le job est créé et le process `claude` y est assigné **immédiatement après son démarrage** (`lancer_claude`, juste après le `Popen`, pendant que le process est encore vivant — seul moment où l'assignation est possible) ; fermer le handle du job dans `_nettoyer_arbre_claude(proc, job_windows)` termine alors toute la descendance encore assignée, PID vivant ou non. La branche POSIX (`start_new_session` + `os.killpg`) n'a **pas été touchée** : déjà correcte et testée. **Journalisation des échecs (point 3)** : `_preparer_job_windows` journalise tout échec de création/assignation du job, et `_nettoyer_arbre_claude` journalise tout échec de fermeture du handle (ou l'absence de job disponible) — la plateforme Windows ne peut plus rester silencieuse, succès ou échec. **Garde-fou (point 4)** : l'intégralité du corps de `_nettoyer_arbre_claude` est désormais enveloppée dans un `try/except Exception` — `_lister_processus_pgid` (OSError sur `iterdir()`), `os.killpg` (PermissionError) et les appels `ctypes` Windows ne peuvent plus s'échapper d'une fonction appelée depuis un `finally`, ce qui aurait masqué la valeur de retour de `lancer_claude`. **Test** : nouveau `tests/test_nettoyage_arbre_windows_249.py` — le scénario Windows réel n'étant pas exécutable sur le ThinkPad (Linux), mock de `ctypes.windll` (+ `os.name` forcé à `"nt"`) vérifiant l'ordre des appels ctypes (`CreateJobObjectW` → `SetInformationJobObject` → `OpenProcess` → `AssignProcessToJobObject` → `CloseHandle`), la journalisation succès/échec à chaque étape, et qu'une exception pendant le nettoyage n'est jamais remontée ; `tests/test_nettoyage_arbre_247.py` (POSIX) repassé sans modification — les deux passent (`python3 tests/test_nettoyage_arbre_247.py` et `python3 tests/test_nettoyage_arbre_windows_249.py` → ✅). ⚠️ **Ce mock ne remplace pas une validation réelle sur la VM CCW** : il vérifie que le code ctypes fait les bons appels, pas que Windows tue effectivement l'arbre de process en pratique — validation par build réel sur CCW encore nécessaire avant de considérer le correctif éprouvé en conditions réelles. **§13** réécrit (sous-section « Nettoyage de l'arbre de process ») : la justification de #247 (« symétrie CCL/CCW préférée à l'objet Job, script unique partagé ») est explicitement invalidée — cette symétrie coûtait la correction sous Windows, un objet Job en `ctypes` pur restant parfaitement compatible avec un script unique CCL/CCW (branche POSIX inchangée, aucune divergence de dépendance). Aucune section renumérotée. Précédemment — Isole le push de la route pièces jointes sur une branche orpheline dédiée, `pieces-jointes` (issue #248). Contexte : la route `POST /joindre-image` (§18, issue #191) terminait par `git push origin HEAD:<branche_courante>` — or git ne peut pas publier un commit sans ses ancêtres, ce push emportait donc AVEC l'image tous les commits locaux non encore poussés de la branche de travail, c'est-à-dire tout travail que CCL avait committé et qu'Alain n'avait pas encore relu : brèche dans le garde-fou central « CCL ne pousse jamais, Alain vérifie puis pousse » puisque rien d'autre n'était censé pousser à sa place ; aggravé par la propagation automatique aux autres clones (watchers en `git pull --ff-only` de début de cycle, dont la VM CCW, en quelques secondes) et par le fait que le fichier était écrit et committé DANS `REP_TRAVAIL` — l'arbre de travail qu'un watcher peut être en train d'utiliser pour une tâche `mode_write` au même instant. **Solution retenue** : commit construit par PLOMBERIE git (`hash-object -w` sur un fichier temporaire hors dépôt, puis `read-tree`/`update-index --cacheinfo`/`write-tree` sur un index TEMPORAIRE isolé via `GIT_INDEX_FILE`, puis `commit-tree`), sans jamais toucher à l'arbre de travail, à l'index réel ni à `HEAD` du dépôt ; racine sans parent à la première publication, sinon enfant du tip précédent (`git fetch origin pieces-jointes` best-effort) ; poussé isolément (`git push origin <sha>:refs/heads/pieces-jointes`) sur une branche **orpheline** ne contenant que `issue-attachments/` — par construction, aucun commit de code ne peut plus jamais être emporté, quel que soit l'état de la branche de travail. URL adaptée en conséquence (`.../pieces-jointes/issue-attachments/<fichier>`) ; le fichier n'est plus jamais écrit dans `REP_TRAVAIL` (transite par un fichier temporaire, nettoyé dans un `finally`). Le repli « garde-fou minimal » (refus si `rev-list --count` > 0) n'a pas été nécessaire, la plomberie s'étant révélée simple à implémenter proprement. **§18 réécrit** (nouvelle sous-section **§18.1bis** détaillant le mécanisme, **§18.2** complété : la justification de l'exception `push` ne repose plus seulement sur l'intention d'Alain mais aussi sur l'impossibilité technique désormais garantie de publier du code par cette voie). **Testé de bout en bout** sur un dépôt jetable (bare + clone) : un commit local « FIX CCL non relu » jamais poussé reste totalement absent d'origin après upload d'image (objet introuvable sur le bare, branche de travail inchangée, `HEAD`/index/arbre de travail du clone intacts — `git status --porcelain` vide) ; branche `pieces-jointes` créée avec un unique fichier sous `issue-attachments/`, sans ancêtre commun avec la branche de travail (`git merge-base` échoue, confirmant l'historique orphelin) ; deuxième upload vérifié en accumulation (2 commits, 2 fichiers, parenté correcte). Aucune section renumérotée hors les ajouts internes au §18. Précédemment — Garantit qu'aucun descendant du process `claude` ne survit au retour de `lancer_claude` (issue #247). Contexte : un `cmd.exe` de build Windows (CCW, `rebuild_scrabble.bat`) était resté vivant après la fermeture de l'issue, verrouillant `Scrabble-Setup.exe` jusqu'à un `taskkill` manuel — sans le moindre signal dans le journal ; défaut de fond, générique : rien ne garantissait qu'un process lancé pendant une tâche soit mort à la fin de celle-ci. **`lancer_claude`** (`watcher.py`) lance désormais `claude` via `subprocess.Popen` (plutôt que `subprocess.run`, pour garder la main sur le PID) avec `start_new_session=True` (POSIX) / `CREATE_NEW_PROCESS_GROUP` (Windows), isolant ce process dans un groupe/une session à lui ; un bloc **`finally`** — donc exécuté quel que soit le mode de sortie (succès, échec, `TimeoutExpired`, exception), et **avant** `commenter_resultat_avec_retry`/`fermer_issue` — appelle la nouvelle `_nettoyer_arbre_claude(proc)` : sous POSIX, `_lister_processus_pgid` énumère (lecture directe de `/proc`, sans dépendance externe) les process vivants du pgid de ce `claude`, journalise chacun en `log.warning` (PID + ligne de commande) puis `os.killpg(pid, SIGKILL)` sur ce seul groupe ; sous Windows, `taskkill /PID <pid> /T /F`. **Solution retenue** (justifiée en détail dans la nouvelle sous-section **§13** « Nettoyage de l'arbre de process après une tâche ») : terminaison de l'arbre après coup plutôt qu'un objet Job Windows (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) — ce dernier est natif et sans fenêtre de course, mais une API Windows pure (`ctypes`/`pywin32`) sans équivalent POSIX, alors que `watcher.py` est le script UNIQUE partagé par CCL et CCW ; fenêtre de course résiduelle de quelques millisecondes entre la fin de `communicate()`/le timeout et l'appel de nettoyage, jugée négligeable et strictement meilleure que l'absence totale de garantie d'avant #247. **Point 4 (critique), vérifié explicitement** : le nettoyage ne cible **jamais** par nom d'exécutable, seulement le pgid/l'arbre du PID de CE `claude`, garanti distinct de celui du watcher et de tout watcher frère par construction (`start_new_session`/nouvelle session) — une erreur ici aurait pu arrêter tous les watchers d'une même machine. **Journalisation, pas critère d'échec** : chaque orphelin tué produit un `log.warning` explicite ; le nettoyage ne fait jamais échouer la tâche, c'est une garantie de fin de traitement. **Test de non-régression** : nouveau `tests/test_nettoyage_arbre_247.py` — un faux `claude` (script en tête de PATH) lance un vrai enfant bloqué sur lecture (FIFO jamais écrite, équivalent stdin qui n'aboutit jamais) puis termine ; le test vérifie que l'enfant est mort après le retour de `lancer_claude`, que le nettoyage est journalisé (PID présent dans un `log.warning`), et que le process de test (rôle du watcher) n'est jamais affecté — passe (`python3 tests/test_nettoyage_arbre_247.py` → ✅). Aucune section renumérotée. Précédemment — Aligne le texte historique du §14 sur l'amendement #244 (issue #245). Contexte : le paragraphe « ⚠️ Contrainte d'exécution synchrone (rappel) », hérité de #208 et volontairement laissé intact par #244 comme référence documentaire, interdisait encore catégoriquement « un mécanisme d'attente différée, de tâche en arrière-plan ou de "je répondrai plus tard" » — formulation contredite par le texte en vigueur de `consignes/globales.md` depuis #244 (l'arrière-plan encadré, avec interrogation de la sortie en boucle DANS la même exécution, y est permis ; seul conclure son tour de parole avant la fin réelle et vérifiée de l'opération reste proscrit). Un Claude Chat consultant le §14 en premier — cas fréquent, section de référence sur la délégation — pouvait lire l'interdiction absolue sans descendre jusqu'à l'encart d'injection qui la nuançait déjà, et reconduire dans une issue de build une consigne que le système n'applique plus. **§14** : le paragraphe est reformulé pour dire une seule chose, alignée sur `globales.md` — proscrit : conclure son tour de parole avant la fin réelle et vérifiée de l'opération ; permis : l'arrière-plan encadré (interrogation de la sortie en boucle DANS la même exécution) ; restent interdits sans changement : « monitor », notification, rappel programmé, formulations « je répondrai plus tard ». Reste du paragraphe conservé tel quel (aucune reprise possible après réponse, boucle `sleep` + `gh issue view` pour l'attente d'un ouvrier) ; l'encart d'injection qui suit (issues #209/#243) n'a pas été touché, sa nuance restant exacte. Recherche `arrière-plan`/`monitor`/`attente différée` sur tout le fichier : une autre occurrence trouvée hors §14 et hors pied de page — **§12.1** (ligne « Globale » du tableau des trois couches : « contrainte d'exécution synchrone et bloquante, sans attente différée, universelle depuis #243 ») — laissée telle quelle, ce résumé reste exact (l'interdit qu'elle nomme est bien l'attente différée pour conclure, pas l'arrière-plan comme technique) ; le pied de page (historique de #244 et antérieurs) laissé tel quel par consigne explicite. Aucune section renumérotée, aucun fichier `.py` ni `consignes/*.md` modifié. Précédemment — Amende la contrainte d'exécution universelle de #243 pour lever une contradiction qu'elle introduisait avec le plafond de timeout de l'outil Bash (issue #244). Contexte : le texte issu de #243 interdisait catégoriquement l'arrière-plan (« Ne lance jamais une commande en arrière-plan ») et proposait comme repli de relancer avec un timeout explicite plus long — or l'outil Bash a un timeout MAXIMUM par appel (de l'ordre de dix minutes) qu'aucun paramètre ne permet de dépasser ; si un build excède ce plafond (hypothèse plausible pour #241/#242, probablement à l'origine du basculement en arrière-plan qui avait motivé #243), l'agent se retrouvait pris entre deux interdits — attendre en un seul appel ou lancer en arrière-plan — et improviserait. Second défaut, dans la même phrase : le repli « boucle sur sa sortie DANS cette même exécution » SUPPOSE une exécution en arrière-plan (on lance, puis on interroge la sortie en boucle) ; la consigne décrivait donc le bon comportement tout en interdisant le mécanisme qui le rend possible. Le fautif n'est pas l'arrière-plan en soi, c'est de conclure son tour de parole sans avoir attendu la fin réelle de l'opération. **`consignes/globales.md`** : la fin du bullet « Contrainte d'exécution » (à partir de « Si une opération dépasse le timeout d'un appel d'outil… ») est réécrite — ce qui est interdit, c'est de CONCLURE le tour de parole avant que l'opération soit terminée et son résultat vérifié, pas l'arrière-plan comme technique ; en cas de dépassement du timeout d'un appel d'outil, deux voies restent permises : relancer avec un timeout explicite plus long tant que le plafond de l'outil le permet, OU lancer en arrière-plan À CONDITION IMPÉRATIVE d'interroger sa sortie en boucle DANS cette même exécution jusqu'à complétion réelle ; restent interdits sans changement le « monitor », la notification, le rappel programmé et toute formulation « je répondrai/j'attends… » en guise de conclusion ; rappel inchangé qu'aucune reprise n'existe (le watcher ferme l'issue dès la réponse postée). **`consignes/type_chef.md`** vérifié : sa formulation (« aucune attente différée, aucun monitor ») reste cohérente avec le nouveau texte — non touché. **§12.1** (ligne « Globale ») et **§14** (encart d'injection automatique) vérifiés : leurs résumés restent exacts sans qu'il soit besoin d'y ajouter la précision arrière-plan/plafond — non touchés. Aucune section renumérotée, aucun fichier `.py` modifié. Précédemment — Généralise l'interdiction d'attente différée à toute issue et distingue opération longue légitime du blocage sans progrès (issue #243). Contexte : les issues #241/#242 (builds Scrabble, CCW) se sont fermées `done` avec un rapport annonçant attendre une notification de fin de build ou un rappel programmé, alors que le build avait réellement abouti (`Scrabble.exe` et `Scrabble-Setup.exe` présents, datés du jour) — pas un échec de build, un rapport ne reflétant pas la réalité, produit par un agent sorti avant la fin. Deux consignes en cause, inversées par rapport à ce qu'exige une tâche longue : `consignes/globales.md` (injecté dans TOUTE issue) demandait d'abandonner toute commande « boucle/tarde anormalement (> 30s sans progrès net) » — écrit pour #214 (commande refusée par le système de permissions, bouclage réel), mais assez général pour couvrir aujourd'hui un build PyInstaller + Inno Setup (plusieurs minutes, peu de sortie visible), appliqué à la lettre ; l'interdiction qui aurait dû s'appliquer (ne jamais recourir à une attente différée, un « monitor », etc.) vivait dans `consignes/type_chef.md`, injecté SEULEMENT pour le TYPE `chef` — une issue de build n'en est pas une. Le mode de défaillance n'ayant rien de spécifique au rôle de chef (il guette toute tâche dont une étape dépasse le timeout d'un appel d'outil), la contrainte est rendue universelle. **`consignes/globales.md`** : le rappel issu de #214 est reformulé pour distinguer une commande refusée par les permissions ou bloquée SANS AUCUN PROGRÈS (→ abandon immédiat, comportement inchangé) d'une opération longue mais qui PROGRESSE normalement (build, compilation, installation de dépendances, suite de tests, clonage volumineux — → ce n'est PAS une anomalie, il faut attendre sa fin) ; le seuil de 30s ne s'applique plus qu'à l'absence de progrès, plus à la durée en soi. Nouveau rappel généralisé depuis `type_chef.md` : accomplir la tâche en une seule exécution synchrone et bloquante, jamais de commande en arrière-plan / « monitor » / notification / rappel programmé / « je répondrai quand… », relancer avec un timeout explicite plus long ou boucler DANS la même exécution en cas de dépassement du timeout d'un appel d'outil, jamais conclure sur une attente — rappel qu'aucune reprise n'existe, le watcher fermant l'issue dès la réponse postée. **`consignes/type_chef.md`** : allégé pour éviter la redondance — ne garde que la spécificité chef (boucler `sleep` + `gh issue view` en attendant la fermeture des issues ouvrières, puis synthèse finale), la contrainte générale étant désormais dans `globales.md`. **TYPE `build`** : vérification de `watcher.deduire_type_issue`/`TYPES_ISSUE` — `build` n'est PAS une valeur reconnue (`TYPES_ISSUE` = chef/ouvrier/spec_vue/spec_metier/spec_persistance/normal, et `_classer_valeur_type` n'a aucune branche pour « build » : même un en-tête explicite `| TYPE | build |` retomberait sur `normal`) ; `consignes/type_build.md` n'a donc PAS été créé — le mécanisme ne s'y prête pas sans modifier `watcher.py` (hors périmètre de cette issue), et de toute façon le vrai correctif (la contrainte universelle dans `globales.md`) couvre déjà le cas des builds sans dépendre d'un TYPE dédié. **§12.1** : la parenthèse résumant les rappels globaux (ligne « Globale ») mise à jour pour refléter la distinction blocage/progrès et la contrainte d'exécution synchrone désormais universelle. **§14** : le bloc « Contrainte d'exécution impérative » renommé « rappel » et son encart d'injection automatique mis à jour pour pointer vers `globales.md` (universel depuis #243) plutôt que `type_chef.md`, qui n'ajoute plus que la spécificité chef. **§1** : rattrapage d'une omission de #240 — la réécriture du paragraphe sur le pull automatique avait fait disparaître la parenthèse sur les projets à **périmètre dynamique** (dépôt-cible défini par issue, dépôts d'audit non rafraîchis par le pull automatique, distincts du clone de travail du watcher) ; réintroduite, adaptée au nouveau texte. Aucune section renumérotée. Précédemment — Correctif documentaire §1/§14/§16 et rattrapage de trois issues committées sans mise à jour du DOC (issue #240). Incident du 26/07 : le clone `C:\CCW\Bridge_Agent` de la VM (celui d'où s'exécute réellement `watcher.py`) avait **80 commits de retard** sur `origin/master`, sans aucun signal — le service tournait avec du code antérieur à l'issue #195, cause probable de l'incident #236 (issue fermée `done` sans commentaire de résultat). **§1** réécrit : le `git pull --ff-only` automatique de début de cycle porte bien sur `REP_TRAVAIL` avec la même logique CCL/CCW, mais ne met à jour le CODE du watcher que lorsque `REP_TRAVAIL` coïncide avec le clone du dépôt Bridge_Agent — vrai côté CCL, **faux** côté CCW en modèle unifié (#231), où `REP_TRAVAIL = \\VBOXSVR\CCW_Share` n'est même pas un dépôt git et où le clone contenant `watcher.py` (`C:\CCW\Bridge_Agent`) vit ailleurs, mis à jour par personne. L'ancienne affirmation « comportement identique CCL et CCW » est supprimée car trompeuse sur ce point précis. **§16** gagne un bloc d'avertissement opérationnel : ce clone n'est **jamais** mis à jour automatiquement ; procédure obligatoire après tout push touchant `watcher.py` — `git pull --ff-only` dans `C:\CCW\Bridge_Agent` **puis redémarrage du service** `CCW-Watcher` (`nssm restart`, un pull seul ne suffit pas : un process Python déjà démarré garde en mémoire le code chargé à son lancement) — avec la commande de contrôle rapide `git status -sb` (ne doit jamais afficher `behind`), et le cas réel des 80 commits de retard comme justification. **§14** corrigé : dans le bloc « Quand NE PAS passer par un chef » (#225), la référence au service `CCW-Watcher-<Projet>` — nom venant du modèle multi-projets abandonné par #231 — est remplacée par `CCW-Watcher`. Rattrapage de trois issues committées sans entrée de pied de page : **#237** — `commenter_issue`/`editer_dernier_commentaire` passent par `--body-file` (fichier temporaire UTF-8) au lieu de `--body`, supprimant la limite argv Windows de 32767 caractères ; `commenter_resultat_avec_retry` vérifie désormais la publication par relecture de l'issue (un exit code 0 de `gh` ne suffit plus, la présence effective du commentaire est exigée) ; nouveau marqueur `MARQUEUR_RESULTAT` (`<!-- bridge:resultat -->`) en tête du commentaire de résultat, utilisé aussi par `resultat_deja_poste` à la place de l'ancienne sous-chaîne `"## Résultat"` qui matchait à tort `"## Résultat attendu"` ; test `tests/test_verification_commentaire_237.py` ; deux effets de bord assumés — deux appels `gh` par tentative, et possibilité d'un commentaire en double si la publication réussit mais que la relecture échoue transitoirement (perte silencieuse échangée contre doublon visible). **#238** — `fermer_issue` inspecte désormais les codes de retour de `close` et `add-label`, retourne un booléen, et journalise explicitement les états incohérents (fermée sans label / label sans fermeture) sans compensation automatique. **#239** — libellé d'agent de l'ACK déduit automatiquement de `platform.system()` (« agent Linux » / « agent Windows »), avec champ optionnel `LIBELLE_AGENT` pour forcer un libellé explicite si la détection automatique ne convient pas ; le §16 avait déjà été modifié par cette issue mais aucune entrée de pied de page n'avait été ajoutée — rattrapée ici. Aucune section renumérotée. Précédemment — §3 « Créer une issue » : ajout d'une **exception `PROJET`** pour les issues `for-windows` (issue #233, suite #231). Rapport remonté par le Claude du projet `actualise` : lors de la génération d'une issue de build Windows, le champ `PROJET` avait été renseigné avec `actualise` au lieu de `bridge_agent`, en appliquant par erreur la règle générale du §3 (« nom exact du projet cible »). Or le §16.3 (modèle CCW unifié, #231) applique correctement `PROJET=bridge_agent` dans son template — c'est la config du watcher CCW unique qui compte, pas le projet réellement construit — mais le §3, consulté en premier par Claude Chat, ne mentionnait pas cette exception. Ajout d'un second bloc d'avertissement juste après celui existant (« Claude Chat doit toujours inclure `| PROJET | <nom> |` ») précisant que pour les issues `for-windows`, `PROJET` reste toujours `bridge_agent`, le nom du projet cible s'exprimant en texte dans le corps (chemins, `git clone`/`git pull`), avec renvoi au template du §16.3. Aucune section renumérotée. Précédemment — §16 « Agent Windows CCW » : documentation du **modèle CCW unifié** (issue #231), qui remplace le modèle multi-projets (#170, un service NSSM par projet). Un seul service NSSM `CCW-Watcher` surveille désormais les issues `for-windows` de `AlainDelree/Bridge_Agent`, `REP_TRAVAIL = \\VBOXSVR\CCW_Share` (accessible depuis Linux à `/home/alain/Bridge_Agent_CCW_Share/`), chaque projet buildé étant cloné dans un sous-dossier dédié `\\VBOXSVR\CCW_Share\CCW\<projet>\` — séquencement strict des builds par construction (un seul process `watcher.py`), zéro contention CPU/RAM entre builds parallèles. Validé en production avec le build PyInstaller d'`actualise`. Introduction du §16 réécrite (titre « (en préparation) » retiré, devenu opérationnel) ; nouvelle sous-section **§16.3 « Procédure — builder un projet Windows »** détaillant le template d'issue en 4 étapes (exception `git config --global --add safe.directory` sur le chemin UNC — obligatoire une seule fois par sous-dossier —, clone ou `git pull --ff-only`, `pip install -r requirements.txt`, build `python -m PyInstaller --noconfirm --onedir --noconsole`), la récupération manuelle des artefacts côté Linux et le rappel qu'aucun token GitHub Contents n'est requis (dépôts publics, seul le token Issues du service `CCW-Watcher` sert). Les scripts `ajouter_projet_ccw.ps1` et `finaliser_projet_ccw.ps1` (tableau de provisioning) marqués **« obsolète — modèle multi-projets abandonné, conservé à titre historique »** — ne plus les utiliser, mais conservés dans le dépôt sans suppression. Reste du §16 (§16.1 maintenance 90 jours, §16.2 onglet CCW, description historique du modèle multi-projets #170) laissé inchangé, hors du périmètre de cette issue. Précédemment — §14 « Délégation Chef → Ouvrier » : ajout d'un bloc **« Quand NE PAS passer par un chef »** (issue #225), inséré juste après le paragraphe « Principe » et avant « Ce n'est pas déclenché automatiquement… ». Contexte : sur le projet `actualise`, une tâche entièrement Windows avait donné lieu à une issue chef CCL dont le seul travail était de créer immédiatement un ouvrier CCW et d'attendre sa fermeture — sans étape réelle côté Linux, correct mais coûteux (deux issues, deux invocations `claude`, TIMEOUT long, attente synchrone bloquante payée pour rien). Le nouveau bloc pose le **critère de décision** : le chef se justifie quand la tâche comporte du travail réel côté Linux (avant et/ou après) dans la même unité de travail ; si la TOTALITÉ de la tâche s'exécute sous Windows, créer directement l'issue avec `| LABELS | for-windows |` (§3) plutôt qu'un chef. **Contre-exemple explicite** : un chef qui se contente de créer un ouvrier puis d'attendre sa fermeture, sans orchestration réelle, est du surcoût pur. Rappel que l'**exemple validé** plus bas dans la section (dictionnaire déposé côté Linux puis rebuild côté Windows) reste un cas où le chef EST justifié — la nouvelle règle ne le contredit pas. **⚠️ Contrepartie opérationnelle** ajoutée dans le même bloc : le rallumage automatique du watcher à la création d'une issue (§13, mécanisme 2) ne vaut QUE pour les issues `for-linux` — une issue `for-windows` directe ne démarre rien, donc vérifier dans l'onglet CCW (§16.2) que la VM `CCW-Build` tourne et que le service `CCW-Watcher-<Projet>` est démarré avant d'en envoyer une, sinon elle reste ouverte sans aucun signal. En miroir, **§3** (paragraphe décrivant le champ `LABELS`, juste après la phrase sur le cas d'usage `| LABELS | for-windows |`) gagne une phrase de renvoi croisé vers ce bloc du §14. Aucune section renumérotée ; reste du §14 (contrainte d'exécution impérative, format des titres, timeout du chef, exemple validé) et reste du §3 inchangés. Précédemment — Nouvelle section **§19 « Calibration automatique du TIMEOUT »** (issue #224), documentant de bout en bout le système mis en place par les issues #220 (extension d'`historique_durees.json`), #221 (mécanique EWMA `etat_timeout.json`/`etat_ambiance.json`), #222 (exposition du `TIMEOUT_suggéré` dans le commentaire de clôture GitHub) et #223 (exclusion des `expiree=true` du badge d'estimation de l'interface). Jusqu'ici ce système n'était documenté nulle part dans `BRIDGE_AGENT_DOC.md` — seul `CONTEXTE.md` en gardait une trace partielle, ajoutée par #221 et jamais mise à jour depuis, de toute façon plafonnée par sa limite de taille pour l'injection prompt (§12.1). La nouvelle section couvre, à partir d'une lecture du code réel de `watcher.py`/`app/issues.py` (pas une paraphrase des rapports d'issue) : l'objectif et le principe d'inspiration (RTO TCP, Jacobson/Karels), la formule complète et chacun de ses termes, les deux fichiers d'état (`logs/etat_timeout.json`, `logs/etat_ambiance.json` — partagés entre watchers, verrouillés, écriture atomique), le tableau des constantes actuelles en soulignant explicitement qu'elles sont des valeurs de DÉPART non backtestées, le canal d'exposition (bloc `⏱️/📊` dans le commentaire de clôture, sans aucune application automatique — le TIMEOUT réellement utilisé reste celui de l'en-tête, `extraire_timeout`), et une liste explicite des limitations connues (`tag_reseau` jamais peuplé donc `F_reseau`/`F_local` neutres, incohérence inerte de `lire_timeout_suggere` sur échec définitif, démarrage à froid trompeusement optimiste, aucun backtest des constantes, distinction avec le badge `estimer_duree` de #223). Aucune autre section renumérotée ni modifiée. Précédemment — Correctif horloge d'auto-extinction (issue #217) : le watcher pouvait s'éteindre **immédiatement après un traitement réel** lorsque celui-ci s'étirait au-delà du délai d'inactivité (`DELAI_INACTIVITE_MIN`, défaut 20 min). Cause : `derniere_activite` (horloge monotone d'inactivité, #200) n'était réarmée qu'**en tête de cycle**, juste après `lister_issues()` et **avant** de lancer `traiter_issue()` — donc jamais pendant le traitement (potentiellement long : plusieurs timeouts de 300 s + retries en cascade). Si le traitement d'une seule issue dépassait le délai (cas réel `watcher-scrabble.log` du 24/07/2026 : #237/#238 traités sans interruption de 08:59 à 09:22, puis extinction à 09:23:08 — 14 s après le succès de #238), l'horloge restait figée à l'instant du **début** du cycle ; le test d'extinction du cycle suivant se déclenchait alors sur une horloge périmée, ne reflétant pas le travail réellement effectué. **Correctif** (`watcher.py`, boucle principale) : réarmement de `derniere_activite` **aussi APRÈS** la boucle de traitement, dès qu'au moins une issue traitable a été traitée ce cycle (option a du diagnostic — réarmer sur le travail réel, préférée à l'option b « revérifier `lister_issues()` avant `sys.exit` » car elle satisfait plus directement l'objectif « ne jamais éteindre si du travail vient d'avoir lieu », sans appel réseau supplémentaire ni cas où une issue devenue fermée entre-temps laisserait l'extinction filer). Le flag `travail_a_faire` (calculé une fois) conditionne les deux réarmements ; l'extinction reste possible quand plus rien n'est traitable. **Test de non-régression** : `tests/test_auto_extinction_217.py` pilote le vrai `watcher.main()` avec horloge mockée (`time.monotonic`/`time.sleep` patchés) sur 3 scénarios — (1) traitement long ~23 min + issue restante → **pas** d'extinction prématurée (échoue sur le code d'avant #217, passe sur le code corrigé), (2) inactivité réelle → extinction bien déclenchée, (3) issue non-traitable (`done`) → n'empêche pas l'extinction. §13 (mécanisme 3 « Extinction automatique ») mis à jour pour décrire le double réarmement avant/après. Précédemment — Nouveau rappel global « abandon immédiat au refus de permission » (issue #214) : ajout, à la fin de `consignes/globales.md`, d'un rappel systématique — si une commande/un outil est **refusé par le système de permissions** (session non-interactive, aucune approbation possible) ou **boucle/tarde anormalement** (> 30s sans progrès net), CCL doit **abandonner immédiatement** l'approche et le signaler dans son rapport plutôt que de retenter, en basculant si possible sur un repli plus simple (lecture directe, `grep`, analyse manuelle) et sans jamais insister sur une commande déjà refusée. Motivation : comparaison des issues Scrabble #235 (timeout à 300s, bouclage sur une commande refusée) et #238 (succès) — la seule différence significative était la présence, dans #238, d'une consigne explicite d'abandon-au-lieu-de-retenter ; en session non-interactive, un refus de permission Claude Code est systématique et définitif (aucun utilisateur pour approuver), donc retenter est vain. Consigne volontairement **générale** (pas spécifique à Scrabble ni à JS/eslint) car le problème touche toute commande nécessitant une approbation (installation de paquet, exécution d'un binaire, etc.), quel que soit le projet ou le langage. §12.1 : la parenthèse résumant les rappels globaux dans le tableau des trois couches est complétée (ajout d'« abandon immédiat au refus de permission / boucle anormale ») ; la liste complète des rappels n'étant pas reproduite ailleurs dans la doc, aucune autre duplication à mettre à jour. Précédemment — Déplacement de l'injection des consignes trois couches dans `watcher.py` — couverture universelle (issue #211). Les consignes (globales/type/projet, #209) ne sont plus écrites dans le **corps** de l'issue par `app/issues.py` (chemin qui ne couvrait QUE les issues créées via le formulaire web), mais injectées dans le **prompt donné à CCL au moment du traitement** par `watcher.py` (`lancer_claude` → nouvelles `_consignes_injectees`/`_lire_consigne`, reprises de `app/issues.py`), exactement sur le modèle de `CONTEXTE.md`/`FICHIER_CONTEXTE`. Le point de passage devient **unique** : peu importe le chemin de création — formulaire web, `gh issue create` d'un chef (§14), création manuelle GitHub (§3) — `watcher.py` déduit le TYPE (`deduire_type_issue` sur le titre/corps réels) et le projet (`CFG.nom`), puis ajoute le bloc **après** le bloc `CONTEXTE` et **avant** la clause de périmètre / le garde-fou (regroupement des « règles » en fin de prompt, zone la mieux suivie). Cas particulièrement corrigé : les issues **ouvrières créées par un chef** (chemin 2, vraies tâches `mode_write`) recevaient auparavant zéro consigne — c'est justement là que les rappels de sécurité comptent le plus. `app/issues.py::construire_body` revient à un corps **en-tête + corps rédigé** seulement (suppression de `_consignes_injectees`/`_lire_consigne`/`DOSSIER_CONSIGNES` et de l'import `logging` devenu inutile) — source unique de vérité désormais côté watcher, plus de double injection. Garde-fous inchangés (#209) : `globales.md` absent → `log.warning` sans bloquer le traitement ; `type_*`/`projet_*` absents → silencieux. Conséquence assumée (comme pour `CONTEXTE.md`) : les consignes ne sont plus visibles dans le corps d'une issue sur GitHub. **§12.1 réécrite** (modèle prompt + couverture universelle des 3 chemins + emplacement dans le prompt) et **§10** mis à jour (`consignes/` = injecté dans le prompt CCL, plus « en tête de chaque issue »). Testé de bout en bout par une issue `TYPE=chef` `mode_write` créée **directement en CLI** (`gh issue create`, hors formulaire) : le prompt CCL assemblé par le watcher contient bien les consignes globales + `type_chef.md`. Précédemment — Architecture à trois couches d'injection de consignes (issue #209) : nouveau dossier `consignes/` à la racine, injecté **dans le corps de chaque issue** par `app/issues.py` (`construire_body` → `_consignes_injectees`), entre le tableau d'en-tête et le corps rédigé par Claude Chat. Trois couches, de la plus générale à la plus spécifique : **globales** (`consignes/globales.md`, **NON-optionnel** — rappels de sécurité transversaux : ne jamais pousser, backup avant modif, respect du périmètre — injecté dans TOUTE issue), **type** (`consignes/type_<type>.md`, **facultatif** — ex. `type_chef.md` reprenant la contrainte d'exécution synchrone du #208, injecté selon le TYPE déduit par `watcher.deduire_type_issue`), **projet** (`consignes/projet_<projet>.md`, **facultatif** — aucun créé par défaut). Ordre final : en-tête → globales → type (si présent) → projet (si présent) → corps. Vaut en **mono-issue comme en mode lot** (chaque bloc `#Titre:` passe par `construire_body` avec son propre TYPE). **Choix délibéré anti-piège de maintenance** : contrairement à `CONTEXTE.md`, les couches type/projet sont sans obligation de présence (un projet sans `projet_<nom>.md` fonctionne normalement, rien à créer/maintenir) et créées uniquement à la demande. Garde-fous : fichier `type_*`/`projet_*` absent → aucune injection **sans** log (normal, pas une anomalie) ; `globales.md` introuvable → `logging.warning` clair **sans jamais faire échouer** la création d'issue. Nouvelle sous-section **§12.1** décrivant l'architecture, mise à jour du **§10** (dossier `consignes/`) et du **§14** (la contrainte d'exécution synchrone du chef n'est plus à recopier manuellement — elle est injectée automatiquement via `consignes/type_chef.md`). Testé de bout en bout (issue `TYPE=chef` réelle : corps GitHub contenant, dans l'ordre, globales puis chef puis corps original). Précédemment — Finalisation du nettoyage doc MVC (issue #208, suite #207) : le §14 « Délégation Chef → Ouvrier » gagne un bloc **« ⚠️ Contrainte d'exécution impérative »** rappelant que le chef doit accomplir la TOTALITÉ de sa tâche (attente de fermeture des ouvriers + synthèse finale comprises) en **une seule exécution synchrone et bloquante** — aucune reprise n'étant possible après qu'une issue a été répondue/fermée, ne jamais recourir à une attente différée, une tâche en arrière-plan ou un « je répondrai plus tard » ; si une attente est nécessaire, boucler (`sleep` + `gh issue view`) DANS la même exécution. Cette finalisation confirme aussi l'absence des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` à la racine de bridge_agent (jamais créés ici ; seul `CONTEXTE.md` existe et est conservé). Précédemment — Nettoyage doc MVC (issue #207) : **suppression de l'ancien §15 « Pattern Chef + Specs MVC (évolution future) »**, purement prospectif et jamais implémenté (le watcher ne lit pas le champ `SPECS`, aucun routage par couche Vue/Métier/Persistance n'existe) ; les sections suivantes **ne sont pas renumérotées** (16, 17, 18 restent 16, 17, 18) pour préserver les références croisées existantes. Le **§14 est entièrement réécrit** et recadré « Délégation Chef → Ouvrier (changement d'environnement) » : on ne garde que l'usage réel validé — un CCL « chef » crée lui-même une issue « ouvrier » ciblant un autre environnement (typiquement CCL Linux → CCW Windows) via `gh issue create` et surveille sa fermeture avant de livrer, sur instruction explicite (pas de détection auto du rôle chef, pas de décomposition automatique générique) — avec conseil de `TIMEOUT` généreux côté chef et l'exemple validé du build Scrabble/ouvrier CCW. En complément, l'issue chef #207 délègue à 6 issues « ouvrier » (une par projet actif hors bridge_agent et ff_galerie) la suppression des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` — vestiges du §15 abandonné — `CONTEXTE.md` (mécanisme standard hors MVC) étant conservé partout. Précédemment — §18 (nouveau) « Pièces jointes image dans les issues » (issue #191) : l'onglet « Nouvelle issue » accepte désormais un **upload optionnel PNG/JPEG** (champ fichier + bouton « Joindre une image » à côté du corps). Nouvelle route **`POST /joindre-image`** (`app/issues.py`, `joindre_image()`) : valide le type (Content-Type **et** magic bytes) et la taille (**≤ 5 Mo**), sauvegarde dans **`issue-attachments/`** (racine du `REP_TRAVAIL`) sous un nom **horodaté** anti-collision (`AAAAMMJJ-HHMMSS-<nom>.ext`), puis `git add` + `commit` + **`git push origin HEAD:<branche>`** (branche déduite **dynamiquement**, jamais supposée master/main), et retourne l'URL **`raw.githubusercontent.com/<owner>/<repo>/<branche>/issue-attachments/<fichier>`** — format qui s'affiche correctement dans les issues GitHub. Le frontend (`static/js/app.js`, `joindreImage()`/`insererDansCorps()`) insère alors **automatiquement** `![<nom>](<url>)` dans le corps à la position du curseur. **Exception `push` assumée et documentée (§18.2)** : ce commit+push est déclenché par **ALAIN** via l'outil (son action manuelle), **pas par CCL/le watcher** — la règle « CCL ne pousse jamais » n'est donc pas violée (elle vise les modifications de code de l'agent, pas une image qu'Alain publie lui-même). Gestion d'erreurs (§18.4) : **push échoué → aucune URL insérée** (commit conservé en local, poussable plus tard), **projet sans dépôt git → message clair**, type/taille/contenu invalides refusés proprement. `issue-attachments/` volontairement **hors `.gitignore`** (les images doivent être suivies/poussées). Testé de bout en bout (dépôt jetable + remote bare : succès + URL correcte, et chemins d'échec type/taille/magic/push). Précédemment — §17 (nouveau) « Notifications centralisées — détection serveur des transitions » (issue #187) : `new_issue.py`, qui tourne en permanence sur le ThinkPad, détecte désormais LUI-MÊME par polling `gh` les transitions d'issues (fermeture `done` = succès ; label `needs-human` = échec définitif) de **tous** les projets (for-linux ET for-windows), et déclenche bip/`notify-send`/`ntfy` **localement**, y compris pour les issues traitées par la VM **CCW** — **sans aucun appel réseau initié par la VM** (la VM n'écrit que sur GitHub). Nouveau module partagé `notifications.py` (racine) factorisant `bip`/`notifier_bureau`/`notifier_ntfy`/`notifier`, importé par `watcher.py` (enveloppes minces déléguant, sites d'appel inchangés) ET par le nouveau poller `app/notifications_poller.py` (thread démon lancé par `new_issue.py`). Script bip **déplacé/recréé** de `~/NicLink/bip.py` vers `scripts/bip.py` (infrastructure partagée) ; défaut `SCRIPT_BIP` et `configs/*.conf` mis à jour. Anti-doublon (point 4) : réglage `NOTIFIER_LOCAL` (`.conf`, défaut `true`) coupant la notif du watcher + portée `BRIDGE_NOTIF_SCOPE` (env, défaut `for-windows`) du poller. **Défaut livré sans régression ni doublon** (CCL notifie via son watcher, CCW via le poller — variante propre de l'option b) ; **option (a) « centralisation complète » recommandée mais laissée au choix d'Alain** car elle fait de `new_issue.py` une dépendance dure de toute notification (or il n'a pas encore de service systemd) — implémentée et à un réglage près (`BRIDGE_NOTIF_SCOPE=all` + `NOTIFIER_LOCAL=false` partout). **Action requise côté VM CCW** : poser `NOTIFIER_LOCAL=false` dans `configs\*-ccw.conf` pour éviter un double `ntfy`. Bonus (point 5) : le poller lit les labels COURANTS à la fermeture, donc `notif_pc`/`notif_gsm` ajouté EN COURS de traitement est bien pris en compte. Filtre de récence (`BRIDGE_NOTIF_RECENCE_MIN`, défaut 30 min) + amorçage silencieux au 1er cycle évitent le spam de vieilles issues au démarrage ; état en mémoire process. Précédemment — §1 « Vue d'ensemble » : documentation du **`git pull --ff-only` automatique en début de cycle** de `watcher.py` (issue #186, suite du #185 qui l'a implémenté). Le watcher rafraîchit son clone (`REP_TRAVAIL`) au début de chaque cycle de polling, juste avant `lister_issues()` : fast-forward transparent en cas de succès ; en cas de commits locaux non poussés (divergence) le `--ff-only` échoue proprement sans RIEN écraser et le watcher poursuit sur le code local — donc aucun risque à oublier un `git push`. Comportement **identique CCL (Linux) et CCW (Windows)** puisque `watcher.py` est le script unique partagé ; les projets à périmètre dynamique (dépôt-cible par issue) ne sont pas concernés. Un `git pull`/relance manuel reste possible pour une mise à jour immédiate (confort, plus une nécessité). Aucune instruction obsolète de « git pull manuel obligatoire » à corriger dans le §16 (aucune ne subsistait). Précédemment — §16 « Agent Windows CCW » : **onglet « CCW » dans l'interface web** (issue #174, sous-section §16.2) — pilotage complet de la VM et des projets CCW depuis Linux, sans PowerShell manuel dans la VM. Backend `app/ccw.py` (routes `/ccw/*`) exécutant les scripts existants à distance via `VBoxManage guestcontrol` : état/démarrage de la VM (`demarrer_ccw.sh`), liste des projets (nouveau `lister_projets_ccw.ps1`, sortie JSON encadrée), ajout (`ajouter_projet_ccw.ps1`) et finalisation non interactive (nouveau `finaliser_projet_ccw_auto.ps1` + `mettre_a_jour_tokens_ccw.ps1` doté d'un mode `-FichierTokens`). Sécurité : tokens jamais passés en argument ni journalisés (fichier temporaire `0600` poussé puis supprimé des deux côtés dans un `finally`) ; mot de passe `ccw-admin` lu depuis `CCW_ADMIN_PASSWORD` ou `configs/ccw_admin.secret` (gitignoré). Nouvel onglet + panneau dans `templates/index.html`, fonctions `ccw*` dans `static/js/app.js`, classe `.message.avertissement` dans `style.css`. Précédemment — §16 « Agent Windows CCW » : **finalisation d'un projet CCW en une seule commande** (issue #173, suite #170) — ajout de `provisioning/windows/finaliser_projet_ccw.ps1` qui, à partir du seul `-NomProjet`, dérive le service/dossier/config (même logique qu'`ajouter_projet_ccw.ps1`), vérifie leur existence, demande `TOPIC_NTFY` et l'écrit directement dans le config (remplacement ciblé du placeholder `###TOPIC_NTFY_A_DEFINIR###`, reste du fichier préservé en UTF-8 sans BOM), rappelle avec une pause la marche à suivre pour créer le token GitHub dédié, puis **appelle** `mettre_a_jour_tokens_ccw.ps1` (pas de duplication) pour la saisie masquée + pose des tokens + redémarrage + vérif des logs, et conclut par un résumé ; `mettre_a_jour_tokens_ccw.ps1` gagne un paramètre `-NomLog` pour vérifier le bon log de service (`ccw-<nom>-service.log`) ; les rappels d'`ajouter_projet_ccw.ps1` (en-tête + fin de script) et le §16 pointent désormais vers cette commande unique au lieu des 3 étapes dispersées. Non exécuté contre une VM réelle (test manuel par Alain). Précédemment — §11 « Conventions de code » : **règle BOM UTF-8 obligatoire pour tout script `.ps1`** (issue #172) — ajout du BOM (`EF BB BF`) manquant sur `ajouter_projet_ccw.ps1` (#170) et `mettre_a_jour_tokens_ccw.ps1` (#168), qui plantaient sinon sous Windows PowerShell 5.1 avec des `UnexpectedToken` en cascade sur les accents (même signature que #151) ; règle généralisée en §11 + rappel en tête du §16 pour prévenir la récidive (`provisionner.ps1` déjà OK depuis #151). Précédemment — §16 « Agent Windows CCW » : **généralisation multi-projets de CCW** (issue #170) — ajout de `provisioning/windows/ajouter_projet_ccw.ps1` (un clone + un config `configs\<nom>-ccw.conf` + un service NSSM `CCW-Watcher-<NomProjet>` dédiés par projet, sur le modèle des watchers CCL ; paramétrable `-NomProjet`/`-Depot`, idempotent, `watcher.py` inchangé) ; documentation du modèle « un service par projet » et de la **règle d'expiration alignée** des tokens (un token fine-grained dédié par dépôt, mais tous à la même échéance ≈ 17 octobre 2026) ; commande exacte d'instanciation de Scrabble et marche à suivre pour créer son token dédié (Repository access → Scrabble uniquement, Issues read/write + Metadata read-only). Précédemment — §16 « Agent Windows CCW » : ajout de la sous-section **§16.1 Maintenance périodique (renouvellement à 90 jours)** (issue #169) — runbook séquentiel consolidé pour la fenêtre de maintenance d'octobre 2026 : tableau de repères de dates (install **2026-07-19**, expiration Windows **2026-10-17**, token GitHub aligné ~90 j mais non stocké), puis procédure en 3 étapes renvoyant aux scripts existants — vérifier (`verifier_expiration_ccw.py`), recréer la VM (`creer_vm_ccw.py --recreate` + ré-attacher un ISO frais + `lancer_provisioning.py`), renouveler les tokens (`mettre_a_jour_tokens_ccw.ps1`) — sans dupliquer le détail technique déjà présent dans le §16. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/mettre_a_jour_tokens_ccw.ps1` (issue #168) — renouvellement des tokens `GH_TOKEN`/`CLAUDE_CODE_OAUTH_TOKEN` du service `CCW-Watcher` sans reconstruire à la main la chaîne `AppEnvironmentExtra` : saisie masquée (`Read-Host -AsSecureString`), séparateur `` `n`` impératif entre les deux paires (un espace corrompt `GH_TOKEN` → « Bad credentials »), `nssm set`/`nssm restart`, puis affichage automatique des 10 dernières lignes de `logs\ccw-service.log` pour confirmer l'absence d'erreur d'auth. Précédemment — §16 « Agent Windows CCW » : alerte d'expiration de l'éval 90 jours (issue #167) — ajout de `provisioning/windows/eval-expiration.json` (date d'installation **2026-07-19**, expiration **2026-10-17**) et du script `provisioning/windows/verifier_expiration_ccw.py` (côté Linux : calcule les jours restants, alerte + code de sortie 2 à ≤ 10 j, sinon confirmation calme ; `python3 provisioning/windows/verifier_expiration_ccw.py`) ; rappel `cron` + `ntfy` hebdomadaire proposé mais laissé à l'activation d'Alain. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/demarrer_ccw.sh` (issue #166), wrapper de démarrage de la VM `CCW-Build` depuis CCL (headless par défaut, `--gui`/`--fenetre` pour une fenêtre, `--status` pour l'état sans rien démarrer). Précédemment — §3 « Créer une issue » : ajout d'une note sur la **convention de présentation côté Claude Chat** pour l'envoi en lot (issue #153) — quand Claude Chat prépare plusieurs issues, il les présente toutes à la suite dans un seul bloc de code (pas un bloc par issue) pour un copier-coller en un clic. Précédemment — §16 « Agent Windows CCW » : `REP_TRAVAIL` généré par `provisionner.ps1` pointe désormais vers le **chemin UNC** `\\VBOXSVR\CCW_Share` (et non la lettre automontée `$LettrePartage`), seul accessible au service `CCW-Watcher` tournant sous LocalSystem (issue #149, suite #148) ; `$LettrePartage` conservé pour référence mais plus utilisé pour construire `REP_TRAVAIL`. Précédemment — le watcher CCW tourne comme **vrai service Windows** enregistré via NSSM (issue #148, suite #147) — `provisionner.ps1` installe `NSSM.NSSM` (winget) et enregistre le service `CCW-Watcher` (`SERVICE_AUTO_START` + `AppExit Default Restart` + `AppRestartDelay 5000`, stdout/stderr → `logs\ccw-service.log`, idempotent via `nssm stop`/`remove`), en remplacement de l'ancienne tâche planifiée `-AtLogOn` qui ne redémarrait pas au boot sans session ; équivalent direct des services systemd du §13. Précédemment — provisioning **phase 2** (issue #147, suite #146) — ajout de `provisioning/windows/provisionner.ps1` (installe l'outillage dans la VM via winget + Claude Code natif, clone le dépôt, écrit `ccw.conf`, enregistre la tâche planifiée `CCW-Watcher`) et `lancer_provisioning.py` (pousse/exécute ce script depuis CCL via `VBoxManage guestcontrol`) ; `watcher.py` inchangé (portable, `LABEL` paramétrable) ; limite Task Scheduler vs `Restart=always` documentée. Précédemment — ajout du §16 et du label `for-windows` (issue #146) : provisioning phase 1 de la VM Windows CCW (`provisioning/windows/creer_vm_ccw.py` + `autounattend.xml`) destinée aux builds .exe délégués par CCL. Précédemment — Bridge_Agent v1, 4 projets actifs. §3 « Créer une issue » : ajout de l'**envoi en lot** (issue #135) — coller plusieurs blocs `#Titre:` à la suite dans le même corps déclenche le mode lot (bouton « Envoyer le lot (N issues) »), chaque bloc étant envoyé en séquence comme une issue indépendante (avec ses `PROJET`/`TIMEOUT`/`MODELE` optionnels), sans validation intermédiaire, suivi d'un résumé listant le résultat de chacune. Ajout du projet `ecole` (AlainDelree/Ecole, ~/Ecole) aux tableaux §2 et §7 (issue #101). Section 15 « Chef + Specs MVC » : champ `SPECS` (pluriel, minuscules, combinable en une ligne) — correction du champ `SPEC` introduit par erreur (issue #97, suite #96).*
# (diff du fichier suivant)
diff --git a/tests/test_nettoyage_arbre_windows_249.py b/tests/test_nettoyage_arbre_windows_249.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..077be43
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_nettoyage_arbre_windows_249.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (243 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,243 @@
+#!/usr/bin/env python3
+"""Test de non-régression — issue #249.
+
+Le scénario Windows réel (objet Job, CreateJobObject/AssignProcessToJobObject)
+n'est pas exécutable sur le ThinkPad (Linux). Ce test vérifie, par mock de
+`ctypes.windll` (attribut qui n'existe que sous Windows — `create=True` le
+crée pour la durée du test) et de `os.name` forcé à "nt", que :
+
+- `_preparer_job_windows` appelle bien CreateJobObjectW, SetInformationJobObject
+  puis AssignProcessToJobObject (dans cet ordre), et retourne un handle
+  non-None en cas de succès ;
+- `_nettoyer_arbre_claude` appelée avec ce handle ferme bien le job
+  (CloseHandle) et journalise le succès ;
+- en cas d'échec de CreateJobObjectW (retourne 0/NULL) ou
+  d'AssignProcessToJobObject, `_preparer_job_windows` retourne None et
+  journalise l'échec (issue #249 point 3 : la plateforme ne doit jamais
+  rester silencieuse) — y compris quand `_nettoyer_arbre_claude` est ensuite
+  appelée avec job=None ;
+- une exception inattendue pendant le nettoyage (CloseHandle qui lève) est
+  absorbée et journalisée, jamais remontée (issue #249 point 4).
+
+⚠️ Ce test NE remplace PAS une validation réelle sur la VM CCW : il vérifie
+que le code ctypes effectue les bons appels avec les bons arguments, pas que
+Windows tue effectivement l'arbre de process en pratique. Une validation par
+build réel sur CCW reste nécessaire avant de considérer #249 clos en
+production.
+
+Exécution :  python3 tests/test_nettoyage_arbre_windows_249.py
+Sortie      :  code 0 si le scénario passe, 1 sinon.
+"""
+
+import logging
+import sys
+import types
+from pathlib import Path
+from unittest import mock
+
+RACINE = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(RACINE))
+
+import watcher  # noqa: E402
+
+
+class FausseAPIWindowsKernel32:
+    """Simule kernel32 : CreateJobObjectW/SetInformationJobObject/
+    AssignProcessToJobObject/OpenProcess/CloseHandle, avec un journal des
+    appels pour assertion."""
+
+    def __init__(self, echouer_creation=False, echouer_assignation=False):
+        self.echouer_creation = echouer_creation
+        self.echouer_assignation = echouer_assignation
+        self.appels = []
+        self._prochain_handle = 1000
+
+    def _nouveau_handle(self):
+        self._prochain_handle += 1
+        return self._prochain_handle
+
+    def CreateJobObjectW(self, sec_attrs, name):
+        self.appels.append(("CreateJobObjectW",))
+        if self.echouer_creation:
+            return 0
+        return self._nouveau_handle()
+
+    def SetInformationJobObject(self, job, info_class, info_ptr, info_size):
+        self.appels.append(("SetInformationJobObject", job, info_class))
+        return 1
+
+    def OpenProcess(self, access, inherit, pid):
+        self.appels.append(("OpenProcess", pid))
+        return self._nouveau_handle()
+
+    def AssignProcessToJobObject(self, job, process_handle):
+        self.appels.append(("AssignProcessToJobObject", job, process_handle))
+        return 0 if self.echouer_assignation else 1
+
+    def CloseHandle(self, handle):
+        self.appels.append(("CloseHandle", handle))
+        return 1
+
+
+class FauxProc:
+    def __init__(self, pid):
+        self.pid = pid
+
+    def wait(self, timeout=None):
+        return 0
+
+
+def _capturer_logs():
+    messages = []
+
+    class CaptureHandler(logging.Handler):
+        def emit(self, record):
+            messages.append(record.getMessage())
+
+    handler = CaptureHandler()
+    watcher.log.addHandler(handler)
+    watcher.log.setLevel(logging.DEBUG)
+    return handler, messages
+
+
+def scenario_preparation_et_nettoyage_reussis():
+    kernel32 = FausseAPIWindowsKernel32()
+    faux_windll = types.SimpleNamespace(kernel32=kernel32)
+    handler, messages = _capturer_logs()
+    try:
+        with mock.patch.object(watcher.ctypes, "windll", faux_windll, create=True), \
+             mock.patch.object(watcher.os, "name", "nt"):
+            job = watcher._preparer_job_windows(4242)
+            assert job is not None, "un job aurait dû être créé et assigné avec succès"
+
+            noms_appels = [a[0] for a in kernel32.appels]
+            assert noms_appels == [
+                "CreateJobObjectW", "SetInformationJobObject",
+                "OpenProcess", "AssignProcessToJobObject", "CloseHandle",
+            ], f"ordre d'appels inattendu : {noms_appels}"
+            assignation = next(a for a in kernel32.appels if a[0] == "AssignProcessToJobObject")
+            assert assignation[2] > 0, "AssignProcessToJobObject aurait dû recevoir un handle de process ouvert"
+
+            watcher._nettoyer_arbre_claude(FauxProc(4242), job)
+
+            assert kernel32.appels[-1] == ("CloseHandle", job), (
+                "la fermeture du handle de job (qui tue toute la descendance "
+                "assignée, y compris les process ayant survécu à claude) n'a "
+                "pas été appelée en dernier"
+            )
+    finally:
+        watcher.log.removeHandler(handler)
+
+    assert any("Job" in m and "4242" in m for m in messages), (
+        f"le succès du nettoyage via objet Job aurait dû être journalisé : {messages}"
+    )
+    return {"appels": len(kernel32.appels), "warnings": len(messages)}
+
+
+def scenario_creation_job_echoue_journalise_echec():
+    kernel32 = FausseAPIWindowsKernel32(echouer_creation=True)
+    faux_windll = types.SimpleNamespace(kernel32=kernel32)
+    handler, messages = _capturer_logs()
+    try:
+        with mock.patch.object(watcher.ctypes, "windll", faux_windll, create=True), \
+             mock.patch.object(watcher.os, "name", "nt"):
+            job = watcher._preparer_job_windows(4343)
+            assert job is None, "CreateJobObjectW a échoué (retour 0) : aucun job ne doit être retourné"
+
+            watcher._nettoyer_arbre_claude(FauxProc(4343), job)
+    finally:
+        watcher.log.removeHandler(handler)
+
+    messages_4343 = [m for m in messages if "4343" in m]
+    assert len(messages_4343) >= 2, (
+        f"l'échec de préparation ET l'échec du nettoyage doivent tous deux "
+        f"être journalisés (issue #249 point 3 — pas de plateforme "
+        f"silencieuse), obtenu : {messages}"
+    )
+    return {"warnings": len(messages)}
+
+
+def scenario_assignation_echoue_journalise_et_ferme_le_handle():
+    kernel32 = FausseAPIWindowsKernel32(echouer_assignation=True)
+    faux_windll = types.SimpleNamespace(kernel32=kernel32)
+    handler, messages = _capturer_logs()
+    try:
+        with mock.patch.object(watcher.ctypes, "windll", faux_windll, create=True), \
+             mock.patch.object(watcher.os, "name", "nt"):
+            job = watcher._preparer_job_windows(4444)
+            assert job is None, "AssignProcessToJobObject a échoué : _preparer_job_windows doit retourner None"
+            assert any(a[0] == "CloseHandle" for a in kernel32.appels), (
+                "le job créé mais jamais assigné avec succès doit être fermé "
+                "immédiatement (pas de fuite de handle)"
+            )
+    finally:
+        watcher.log.removeHandler(handler)
+
+    assert any("4444" in m for m in messages)
+    return {"warnings": len(messages)}
+
+
+def scenario_exception_dans_nettoyage_ne_remonte_pas():
+    """Point 4 de #249 : une exception dans le nettoyage (ex. CloseHandle qui
+    lève) ne doit jamais s'échapper de _nettoyer_arbre_claude."""
+
+    class KernelQuiExplose:
+        def CloseHandle(self, *a):
+            raise OSError("échec simulé de CloseHandle")
+
+    faux_windll = types.SimpleNamespace(kernel32=KernelQuiExplose())
+    handler, messages = _capturer_logs()
+    try:
+        with mock.patch.object(watcher.ctypes, "windll", faux_windll, create=True), \
+             mock.patch.object(watcher.os, "name", "nt"):
+            watcher._nettoyer_arbre_claude(FauxProc(5555), 999)
+    finally:
+        watcher.log.removeHandler(handler)
+
+    assert any("5555" in m for m in messages)
+    return {"warnings": len(messages)}
+
+
+def main():
+    if watcher.os.name == "nt":
+        print("  (ce test mocke déjà le cas Windows quelle que soit la plateforme d'exécution)")
+
+    tests = [
+        ("préparation + nettoyage réussis (job créé, assigné, puis fermé)",
+         scenario_preparation_et_nettoyage_reussis),
+        ("échec de CreateJobObjectW → aucun job, échec journalisé",
+         scenario_creation_job_echoue_journalise_echec),
+        ("échec d'AssignProcessToJobObject → job fermé, aucune fuite, échec journalisé",
+         scenario_assignation_echoue_journalise_et_ferme_le_handle),
+        ("exception dans le nettoyage (CloseHandle) → jamais remontée",
+         scenario_exception_dans_nettoyage_ne_remonte_pas),
+    ]
+    echecs = 0
+    for nom, fn in tests:
+        try:
+            rap = fn()
+            print(f"  ✓ {nom}  ({rap})")
+        except AssertionError as e:
+            echecs += 1
+            print(f"  ✗ {nom}\n      {e}")
+        except Exception as e:  # noqa: BLE001
+            echecs += 1
+            print(f"  ✗ {nom} — erreur inattendue : {type(e).__name__}: {e}")
+
+    print(
+        "\n⚠️  Rappel : ces scénarios mockent kernel32 pour vérifier que le "
+        "code ctypes effectue les bons appels — ils ne remplacent PAS une "
+        "validation réelle sur la VM CCW. Seul un build Windows réel peut "
+        "confirmer que l'objet Job tue effectivement l'arbre de process en "
+        "pratique."
+    )
+
+    if echecs:
+        print(f"\n❌ {echecs} scénario(s) en échec.")
+        return 1
+    print("\n✅ Tous les scénarios passent.")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 299d449..ea40c1a 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 27 (6 ligne(s)) dans l'ancienne version → ligne 27 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -27,6 +27,8 @@ import hashlib
 import tempfile
 import platform
 import signal
+import ctypes
+import ctypes.wintypes
 from logging.handlers import RotatingFileHandler
 from dataclasses import dataclass, field
 from pathlib import Path
# ── Zone modifiée : ligne 1512 (10 ligne(s)) dans l'ancienne version → ligne 1514 (123 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1512,10 +1514,123 @@ def _lister_processus_pgid(pgid: int, exclure_pid: int | None = None) -> list[tu
     return resultat
 
 
-def _nettoyer_arbre_claude(proc: subprocess.Popen) -> None:
+_JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
+_JobObjectExtendedLimitInformation = 9
+_PROCESS_ALL_ACCESS = 0x1F0FFF
+
+
+class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
+    _fields_ = [
+        ("PerProcessUserTimeLimit", ctypes.c_int64),
+        ("PerJobUserTimeLimit", ctypes.c_int64),
+        ("LimitFlags", ctypes.wintypes.DWORD),
+        ("MinimumWorkingSetSize", ctypes.c_size_t),
+        ("MaximumWorkingSetSize", ctypes.c_size_t),
+        ("ActiveProcessLimit", ctypes.wintypes.DWORD),
+        ("Affinity", ctypes.c_size_t),
+        ("PriorityClass", ctypes.wintypes.DWORD),
+        ("SchedulingClass", ctypes.wintypes.DWORD),
+    ]
+
+
+class _IO_COUNTERS(ctypes.Structure):
+    _fields_ = [
+        ("ReadOperationCount", ctypes.c_uint64),
+        ("WriteOperationCount", ctypes.c_uint64),
+        ("OtherOperationCount", ctypes.c_uint64),
+        ("ReadTransferCount", ctypes.c_uint64),
+        ("WriteTransferCount", ctypes.c_uint64),
+        ("OtherTransferCount", ctypes.c_uint64),
+    ]
+
+
+class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
+    _fields_ = [
+        ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
+        ("IoInfo", _IO_COUNTERS),
+        ("ProcessMemoryLimit", ctypes.c_size_t),
+        ("JobMemoryLimit", ctypes.c_size_t),
+        ("PeakProcessMemoryUsed", ctypes.c_size_t),
+        ("PeakJobMemoryUsed", ctypes.c_size_t),
+    ]
+
+
+def _creer_job_windows_kill_on_close():
+    """Windows uniquement. Crée un objet Job noyau avec le flag
+    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE : fermer son handle (CloseHandle)
+    termine immédiatement TOUT process qui y est encore assigné, sans avoir
+    besoin de connaître le moindre PID à cet instant-là — à la différence de
+    `taskkill /PID <pid> /T /F`, qui doit reparcourir l'arbre généalogique du
+    PID au moment de l'appel et échoue donc dès que ce PID n'existe plus
+    (voir _nettoyer_arbre_claude). Retourne le handle du job en cas de
+    succès, sinon None (chaque échec est journalisé par l'appelant)."""
+    job = ctypes.windll.kernel32.CreateJobObjectW(None, None)
+    if not job:
+        return None
+
+    info = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
+    info.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
+    ok = ctypes.windll.kernel32.SetInformationJobObject(
+        job, _JobObjectExtendedLimitInformation,
+        ctypes.byref(info), ctypes.sizeof(info),
+    )
+    if not ok:
+        ctypes.windll.kernel32.CloseHandle(job)
+        return None
+    return job
+
+
+def _assigner_job_windows(job, pid: int) -> bool:
+    """Windows uniquement. Assigne le process `pid` au job `job` — doit être
+    appelé pendant que ce process est encore vivant (juste après son
+    démarrage), condition nécessaire et suffisante : une fois assigné, un
+    process reste dans le job jusqu'à sa mort ou la fermeture du job, qu'il
+    ait ou non survécu à claude entre-temps."""
+    handle = ctypes.windll.kernel32.OpenProcess(_PROCESS_ALL_ACCESS, False, pid)
+    if not handle:
+        return False
+    try:
+        return bool(ctypes.windll.kernel32.AssignProcessToJobObject(job, handle))
+    finally:
+        ctypes.windll.kernel32.CloseHandle(handle)
+
+
+def _preparer_job_windows(pid: int):
+    """Windows uniquement. Crée l'objet Job et y assigne immédiatement `pid`
+    (voir _creer_job_windows_kill_on_close / _assigner_job_windows). À
+    appeler juste après le Popen du process claude, PENDANT qu'il est
+    vivant — c'est le seul moment où l'assignation est possible. Retourne
+    le handle à conserver jusqu'à _nettoyer_arbre_claude (qui le fermera),
+    ou None si la préparation a échoué à une étape ou l'autre ; chaque échec
+    est journalisé ici (issue #249 point 3 : ne jamais rester silencieux)."""
+    job = _creer_job_windows_kill_on_close()
+    if job is None:
+        log.warning(
+            f"Objet Job Windows non créé pour claude (PID {pid}) : le "
+            f"nettoyage de fin de tâche ne pourra pas garantir la "
+            f"terminaison de sa descendance si elle survit (issue #249)."
+        )
+        return None
+    if not _assigner_job_windows(job, pid):
+        log.warning(
+            f"Échec d'assignation du process claude (PID {pid}) à l'objet "
+            f"Job Windows : le nettoyage de fin de tâche ne pourra pas "
+            f"garantir la terminaison de sa descendance si elle survit "
+            f"(issue #249)."
+        )
+        try:
+            ctypes.windll.kernel32.CloseHandle(job)
+        except Exception:
+            pass
+        return None
+    return job
+
+
+def _nettoyer_arbre_claude(proc: subprocess.Popen, job_windows=None) -> None:
     """Garantit qu'aucun process de l'arbre engendré par CE claude (proc.pid) ne
-    survive au retour de lancer_claude (issue #247). Appelée depuis un `finally` :
-    couvre indifféremment succès, échec, TimeoutExpired et exception.
+    survive au retour de lancer_claude (issue #247, révisé #249). Appelée
+    depuis un `finally` : couvre indifféremment succès, échec, TimeoutExpired
+    et exception.
 
     Cas réel à l'origine de l'issue : un `cmd.exe` lancé par un script de build
     Windows (pushd + .bat) survivait à la fermeture de l'issue et gardait un
# ── Zone modifiée : ligne 1523 (14 ligne(s)) dans l'ancienne version → ligne 1638 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1523,14 +1638,20 @@ def _nettoyer_arbre_claude(proc: subprocess.Popen) -> None:
     l'exécutable produit injouable jusqu'à un `taskkill` manuel — sans le
     moindre signal dans le journal.
 
-    Solution retenue : terminaison de l'arbre de process après coup (taskkill
-    /T /F sous Windows, groupe de process POSIX sous Linux), plutôt qu'un objet
-    Job Windows. Un Job Object est plus robuste (pas de fenêtre de course) mais
-    est une API Windows pure (ctypes/pywin32) : il aurait fallu une branche
-    entièrement différente, sans équivalent côté Linux, dans un script UNIQUE
-    partagé par CCL et CCW. La fenêtre de course de l'option retenue est
-    négligeable en pratique (quelques millisecondes entre la fin de
-    `communicate()`/l'expiration du timeout et cet appel).
+    Pourquoi `taskkill /PID <pid> /T /F` NE SUFFIT PAS (issue #249) : cette
+    fonction s'exécute dans le `finally` de lancer_claude, donc APRÈS le
+    retour de `proc.communicate()` — à cet instant le process claude est déjà
+    terminé et réapé par l'OS. Or taskkill a besoin que le PID cible EXISTE
+    ENCORE pour remonter son arbre généalogique ; sur un PID mort, il échoue
+    immédiatement (« process not found ») sans toucher un seul descendant.
+    C'est exactement le scénario d'origine : le `cmd.exe` orphelin survit à
+    `claude`, donc au moment du nettoyage son PID parent n'est plus
+    traçable. `CREATE_NEW_PROCESS_GROUP` ne comble pas l'écart : sous
+    Windows les groupes de process ne servent qu'au routage de
+    Ctrl+C/Ctrl+Break, pas à la terminaison d'une arborescence. Seul un objet
+    Job — assigné AVANT que le process ne meure, voir _preparer_job_windows,
+    appelé juste après le Popen dans lancer_claude — garantit la terminaison
+    de toute la descendance, PID vivant ou non au moment de l'appel.
 
     Ne cible QUE la descendance du PID claude de CETTE tâche, jamais par nom
     d'exécutable — point critique (#247 point 4) : une erreur ici tuerait le
# ── Zone modifiée : ligne 1538 (43 ligne(s)) dans l'ancienne version → ligne 1659 (78 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1538,43 +1659,78 @@ def _nettoyer_arbre_claude(proc: subprocess.Popen) -> None:
     - POSIX : proc a été lancé avec start_new_session=True, donc son pgid ==
       son propre pid — un groupe forcément neuf et distinct de celui du
       watcher (et de tout autre watcher). os.killpg cible ce seul groupe.
-    - Windows : `taskkill /PID <pid> /T /F` ne parcourt que l'arbre
-      généalogique de ce PID précis, jamais un process par son nom.
+      Inchangé par #249 : correct et déjà couvert par
+      tests/test_nettoyage_arbre_247.py.
+    - Windows : fermeture du handle de l'objet Job créé/assigné par
+      _preparer_job_windows au démarrage de claude (voir lancer_claude).
+
+    Point 4 (#249) : l'intégralité du corps est enveloppée dans un
+    garde-fou — _lister_processus_pgid peut lever une OSError (iterdir sur
+    /proc), os.killpg une PermissionError, et l'appel ctypes Windows
+    n'importe quelle exception. Aucune de ces exceptions ne doit s'échapper
+    de cette fonction : elle est appelée depuis un `finally`, et une
+    exception à cet endroit remonterait à travers lancer_claude et
+    masquerait sa valeur de retour.
     """
-    pid = proc.pid
-    if os.name == "nt":
-        try:
-            res = subprocess.run(
-                ["taskkill", "/PID", str(pid), "/T", "/F"],
-                capture_output=True, text=True, timeout=15,
-            )
-            sortie = f"{res.stdout} {res.stderr}".upper()
-            if res.returncode == 0 and "SUCCESS" in sortie:
+    pid = getattr(proc, "pid", None)
+    try:
+        if os.name == "nt":
+            if job_windows is None:
                 log.warning(
-                    f"Arbre de process claude (PID {pid}) nettoyé via "
-                    f"'taskkill /PID {pid} /T /F' : un ou plusieurs process de "
-                    f"cette tâche ont survécu au retour de lancer_claude et ont "
-                    f"été terminés."
+                    f"Nettoyage de l'arbre claude (PID {pid}) impossible : "
+                    f"aucun objet Job disponible (échec de préparation "
+                    f"journalisé au démarrage — voir _preparer_job_windows). "
+                    f"Un taskkill de repli n'aurait de toute façon pas pu "
+                    f"aider : le PID {pid} est déjà mort à ce stade."
                 )
-        except Exception as e:
-            log.warning(f"Nettoyage taskkill de l'arbre claude (PID {pid}) impossible : {e}")
-    else:
-        orphelins = _lister_processus_pgid(pid, exclure_pid=pid)
-        encore_vivant = proc.poll() is None
-        for pid_orphelin, cmdline in orphelins:
-            log.warning(
-                f"Descendant orphelin de claude (PID {pid}) tué : PID {pid_orphelin} — {cmdline}"
-            )
-        if orphelins or encore_vivant:
-            try:
-                os.killpg(pid, signal.SIGKILL)
-            except ProcessLookupError:
-                pass  # déjà mort entre l'énumération et le kill : rien à faire
+            else:
+                ok = False
+                try:
+                    ok = bool(ctypes.windll.kernel32.CloseHandle(job_windows))
+                except Exception as e:
+                    log.warning(
+                        f"Exception lors de la fermeture de l'objet Job "
+                        f"Windows pour le nettoyage de l'arbre claude "
+                        f"(PID {pid}) : {e}"
+                    )
+                if ok:
+                    log.warning(
+                        f"Arbre de process claude (PID {pid}) nettoyé via "
+                        f"fermeture de l'objet Job Windows : tout process "
+                        f"encore assigné (y compris ceux ayant survécu à "
+                        f"claude) a été terminé."
+                    )
+                else:
+                    log.warning(
+                        f"Échec de fermeture de l'objet Job Windows pour le "
+                        f"nettoyage de l'arbre claude (PID {pid}) : "
+                        f"CloseHandle a échoué — la descendance a pu "
+                        f"survivre."
+                    )
+        else:
+            orphelins = _lister_processus_pgid(pid, exclure_pid=pid)
+            encore_vivant = proc.poll() is None
+            for pid_orphelin, cmdline in orphelins:
+                log.warning(
+                    f"Descendant orphelin de claude (PID {pid}) tué : PID {pid_orphelin} — {cmdline}"
+                )
+            if orphelins or encore_vivant:
+                try:
+                    os.killpg(pid, signal.SIGKILL)
+                except ProcessLookupError:
+                    pass  # déjà mort entre l'énumération et le kill : rien à faire
+                except PermissionError as e:
+                    log.warning(f"os.killpg refusé pour l'arbre claude (PID {pid}) : {e}")
 
-    try:
-        proc.wait(timeout=5)
-    except Exception:
-        pass  # best-effort : ne jamais faire échouer lancer_claude sur ce nettoyage
+        try:
+            proc.wait(timeout=5)
+        except Exception:
+            pass  # best-effort : ne jamais faire échouer lancer_claude sur ce nettoyage
+    except Exception as e:
+        log.warning(
+            f"Nettoyage de l'arbre de process claude (PID {pid}) a levé une "
+            f"exception inattendue et a été abandonné : {e}"
+        )
 
 
 def lancer_claude(numero: int, titre: str, body: str, dry_run: bool,
# ── Zone modifiée : ligne 1736 (12 ligne(s)) dans l'ancienne version → ligne 1892 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1736,12 +1892,17 @@ Si la tâche échoue, remplace ✅ par ❌ et explique la cause en une ligne.
     cmd.append(prompt)
 
     # Popen (plutôt que subprocess.run) pour garder la main sur le PID : le
-    # nettoyage de l'arbre de process (issue #247) doit s'exécuter dans un
-    # finally, quel que soit le mode de sortie (succès, échec, timeout,
-    # exception), et a besoin du PID pour ne cibler QUE la descendance de CE
-    # claude. start_new_session=True (POSIX) / CREATE_NEW_PROCESS_GROUP
-    # (Windows) donnent à ce process un groupe/une session à lui, préalable
-    # nécessaire à un nettoyage sûr — voir _nettoyer_arbre_claude.
+    # nettoyage de l'arbre de process (issue #247, révisé #249) doit
+    # s'exécuter dans un finally, quel que soit le mode de sortie (succès,
+    # échec, timeout, exception), et a besoin du PID pour ne cibler QUE la
+    # descendance de CE claude.
+    # - POSIX : start_new_session=True donne à ce process une session/un
+    #   pgid à lui, préalable nécessaire à os.killpg — voir
+    #   _nettoyer_arbre_claude.
+    # - Windows : CREATE_NEW_PROCESS_GROUP isole le routage Ctrl+Break de ce
+    #   process de celui du watcher (sans rapport avec la terminaison de
+    #   l'arbre, assurée par l'objet Job créé/assigné juste après le Popen
+    #   ci-dessous — voir _preparer_job_windows).
     kwargs_popen = dict(
         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
         text=True, encoding="utf-8", errors="replace",
# ── Zone modifiée : ligne 1753 (8 ligne(s)) dans l'ancienne version → ligne 1914 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1753,8 +1914,15 @@ Si la tâche échoue, remplace ✅ par ❌ et explique la cause en une ligne.
         kwargs_popen["start_new_session"] = True
 
     proc = None
+    job_windows = None
     try:
         proc = subprocess.Popen(cmd, **kwargs_popen)
+        if os.name == "nt":
+            # Doit être fait ICI, pendant que proc est vivant : l'assignation
+            # au job est la seule chose qui rend le nettoyage fiable (issue
+            # #249) — un `taskkill` tenté plus tard, depuis le `finally`,
+            # arrive systématiquement trop tard (PID déjà mort et réapé).
+            job_windows = _preparer_job_windows(proc.pid)
         try:
             stdout, stderr = proc.communicate(timeout=timeout)
             if proc.returncode == 0:
# ── Zone modifiée : ligne 1769 (7 ligne(s)) dans l'ancienne version → ligne 1937 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1769,7 +1937,7 @@ Si la tâche échoue, remplace ✅ par ❌ et explique la cause en une ligne.
         return False, str(e)
     finally:
         if proc is not None:
-            _nettoyer_arbre_claude(proc)
+            _nettoyer_arbre_claude(proc, job_windows)
 
 
 def diagnostiquer_echec(numero: int, titre: str, body: str,
