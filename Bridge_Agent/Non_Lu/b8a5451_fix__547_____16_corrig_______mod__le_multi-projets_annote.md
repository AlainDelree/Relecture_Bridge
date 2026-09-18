b8a5451

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b8a5451
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 12:06:26 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #547 : §16 corrigé — modèle multi-projets CCW actif (5 services NSSM), pas abandonné ; documentation de creer_projet_ccw_complet.ps1 (§16.5) et de l'architecture watcher.py partagé

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 80fd646..1ae7ae2 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1617 (8 ligne(s)) dans l'ancienne version → ligne 1617 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1617,8 +1617,10 @@ create`, puis surveille sa fermeture avant de livrer sa réponse.
   `for-windows`. Avant d'envoyer une issue `for-windows` directe, vérifier
   dans l'onglet CCW (§16.2) que le PC fixe est joignable et que le service
   `CCW-Watcher` est démarré ; sinon l'issue restera ouverte sans aucun
-  signal. (Le nom `CCW-Watcher-<Projet>` venait du modèle multi-projets,
-  abandonné par #231 — voir §16.)
+  signal. (Ne pas confondre avec les services `CCW-Watcher-<Projet>` du
+  modèle multi-projets — actif, voir §16 : ceux-là surveillent les issues
+  du dépôt du projet cible directement, pas les issues `for-windows` de
+  Bridge_Agent.)
 
 **Ce n'est pas déclenché automatiquement par `watcher.py`** : le chef agit
 sur instruction explicite de l'issue qui le mandate (pas de détection auto
# ── Zone modifiée : ligne 1700 (15 ligne(s)) dans l'ancienne version → ligne 1702 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1700,15 +1702,27 @@ Windows natif.
 > `CCW-Watcher` tourne sous le compte **`AlainW`** (utilisateur non-admin) et
 > non plus sous `LocalSystem`.
 
-**Modèle actuel (PC physique).** Un seul service NSSM `CCW-Watcher`
-surveille les issues `for-windows` du dépôt `AlainDelree/Bridge_Agent`.
-`REP_TRAVAIL = C:\CCW_Share` — répertoire de travail **local** sur le PC
-physique, partagé entre CCL (qui y accède via le réseau local) et CCW (qui
-y accède en chemin local direct). Chaque projet buildé est cloné dans un
-sous-dossier dédié : `C:\CCW_Share\CCW\<projet>\`. Ce modèle garantit le
-séquencement strict des builds par construction (un seul process
-`watcher.py`, une issue à la fois) et supprime tout risque de contention
-CPU/RAM entre deux builds parallèles.
+**Modèle de build partagé (PC physique) — issues `for-windows` dans
+Bridge_Agent.** Le service NSSM `CCW-Watcher` (service de base, sans
+suffixe de projet) surveille les issues `for-windows` du dépôt
+`AlainDelree/Bridge_Agent` — c'est le canal utilisé pour les builds
+PyInstaller ponctuels (procédure détaillée en §16.3). `REP_TRAVAIL =
+C:\CCW_Share` — répertoire de travail **local** sur le PC physique, partagé
+entre CCL (qui y accède via le réseau local) et CCW (qui y accède en
+chemin local direct). Chaque projet buildé est cloné dans un sous-dossier
+dédié : `C:\CCW_Share\CCW\<projet>\`. Ce modèle garantit le séquencement
+strict des builds par construction (un seul process `watcher.py` sur ce
+canal, une issue à la fois) et supprime tout risque de contention CPU/RAM
+entre deux builds parallèles.
+
+> **Ce canal de build coexiste avec le modèle multi-projets (issue #170,
+> actif — voir plus bas dans ce §16).** Des services NSSM **additionnels**
+> `CCW-Watcher-<Projet>` surveillent chacun les issues **directement dans
+> le dépôt du projet concerné** (ex. `AlainDelree/Scrabble`), indépendamment
+> du canal `for-windows`/Bridge_Agent décrit ci-dessus. Les deux modèles ne
+> s'excluent pas : `CCW-Watcher` (build, Bridge_Agent) et
+> `CCW-Watcher-<Projet>` (agent dédié par projet) tournent **simultanément**
+> sur le même PC physique.
 
 > **⚠️ Le clone `C:\CCW\Bridge_Agent` n'est JAMAIS mis à jour automatiquement
 > (issue #240).** Le `git pull --ff-only` automatique de début de cycle (§1)
# ── Zone modifiée : ligne 1741 (11 ligne(s)) dans l'ancienne version → ligne 1755 (37 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1741,11 +1755,37 @@ CPU/RAM entre deux builds parallèles.
 > clone en retard, donc potentiellement un service tournant sur du code
 > obsolète.
 
-**Modèle précédent abandonné.** Le modèle multi-projets (#170) — un clone
-`C:\CCW\<Projet>` + un config `configs\<nom>-ccw.conf` + un service NSSM
-`CCW-Watcher-<Projet>` par projet — est abandonné. Les scripts
-`ajouter_projet_ccw.ps1` et `finaliser_projet_ccw.ps1` sont conservés dans
-le dépôt à titre historique uniquement ; ne pas les utiliser.
+**Modèle multi-projets — actif en production (#170 ; correction issue
+#547).** ⚠️ Contrairement à ce qu'affirmait une version antérieure de ce
+document, le modèle multi-projets — un clone `C:\CCW\<Projet>` + un config
+`configs\<nom>-ccw.conf` + un service NSSM `CCW-Watcher-<Projet>` par
+projet — n'est **pas** abandonné : il est **actif et utilisé en
+production**, avec 5 services NSSM confirmés à l'état `running` (constat
+empirique via l'onglet CCW de `new_issue.py`, issue #547) : `CCW-Watcher`
+(base, Bridge_Agent) + `CCW-Watcher-actualise`, `-alchess`, `-rummikub`,
+`-scrabble`. Les scripts `ajouter_projet_ccw.ps1` et
+`finaliser_projet_ccw.ps1` (`provisioning\windows\`) restent les scripts
+**de référence** pour tout nouveau projet — voir aussi
+`creer_projet_ccw_complet.ps1` (§16.5), qui les orchestre (le premier des
+deux) en une seule commande.
+
+> **Architecture confirmée : un seul `watcher.py` partagé par tous les
+> services (issue #547).** Les 5 services NSSM ci-dessus exécutent tous le
+> **même** fichier source `C:\CCW\Bridge_Agent\watcher.py` — chaque service
+> se contente de passer un `--config configs\<projet>-ccw.conf` différent
+> en paramètre (`AppParameters`, vérifié via `nssm get <Service>
+> AppParameters`). Les dossiers `C:\CCW\<projet>\` (créés par
+> `ajouter_projet_ccw.ps1`) contiennent **uniquement** le code du projet
+> cible lui-même (pour builds/traitement) — **jamais** une copie de
+> `watcher.py`. **Conséquence pratique :** un correctif apporté à
+> `C:\CCW\Bridge_Agent\watcher.py` s'applique **à tous les projets** dès que
+> chaque service concerné est redémarré (`nssm restart
+> CCW-Watcher-<Projet>`) — inutile de repousser du code dans chaque
+> sous-dossier `C:\CCW\<projet>\`. Cohérent avec la mise en garde plus haut
+> sur `C:\CCW\Bridge_Agent` (jamais mis à jour automatiquement, issue
+> #240) : un `git pull --ff-only` dans ce clone unique, suivi du
+> redémarrage des services concernés, suffit à propager le correctif
+> partout.
 
 **Provisioning** (dossier `provisioning/windows/`) :
 
# ── Zone modifiée : ligne 1759 (12 ligne(s)) dans l'ancienne version → ligne 1799 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1759,12 +1799,17 @@ le dépôt à titre historique uniquement ; ne pas les utiliser.
 | `eval-expiration.json` | **(obsolète — liée à l'éval 90 jours de la VM, conservé à titre historique)** Métadonnées de l'évaluation 90 jours (issue #167) : `date_installation` (**2026-07-19**), `eval_jours` (90), `date_expiration` (informative, **2026-10-17**). Sans objet sur PC physique (licence Windows normale, pas d'éval à durée limitée). |
 | `verifier_expiration_ccw.py` | **(obsolète — vérifiait l'expiration de l'éval de la VM, conservé à titre historique)** **(côté Linux)** Lit `eval-expiration.json`, recalcule l'expiration (`date_installation` + `eval_jours`) et le nombre de jours restants. À ≤ 10 j restants (ou déjà expiré) : avertissement + **code de sortie 2** (intégrable à une vérif automatisée) ; sinon confirmation calme + code 0. Sans dépendance externe. Sans objet sur PC physique. |
 | `mettre_a_jour_tokens_ccw.ps1` | **(dans la VM)** Renouvellement des tokens d'un service CCW sans manipuler à la main la chaîne PowerShell (issue #168). Demande `GH_TOKEN` puis `CLAUDE_CODE_OAUTH_TOKEN` en `Read-Host -AsSecureString` (jamais affichés en clair), reconstruit `AppEnvironmentExtra` avec le saut de ligne `` `n`` **impératif** entre les deux (un simple espace corrompt silencieusement `GH_TOKEN` → « Bad credentials »), applique via `nssm set … AppEnvironmentExtra`, fait `nssm restart`, attend puis affiche les 10 dernières lignes du log de service et conclut OK / à vérifier (code 2 si `ERROR`). Paramétrable (`-NomService`, `-RepDepot`, et `-NomLog` pour cibler le bon log de service, ex. `ccw-scrabble-service.log`, issue #173) : sert aussi bien à `CCW-Watcher` qu'aux services multi-projets `CCW-Watcher-<NomProjet>` (issue #170). Depuis l'issue #174, accepte aussi `-FichierTokens <chemin>` : les deux valeurs sont alors **lues dans un fichier** « clé=valeur » (au lieu de `Read-Host`), ce qui permet à l'onglet CCW de poser les tokens à distance sans saisie dans la VM et sans jamais les passer en argument de commande. |
-| `ajouter_projet_ccw.ps1` | **(obsolète — modèle multi-projets abandonné, conservé à titre historique)** **(dans la VM)** Instancie un projet CCW **supplémentaire** sur le modèle multi-projets (issue #170), sans rien réinstaller. Paramétrable (`-NomProjet`, `-Depot owner/repo`, ou prompt interactif) : clone le dépôt en lecture seule dans `C:\CCW\<NomProjet>`, écrit `configs\<nom>-ccw.conf` (`NOM=<nom>-ccw`, `LABEL=for-windows`, `REP_TRAVAIL`/`PERIMETRE`=`C:\CCW\<NomProjet>`, `TOPIC_NTFY` placeholder), et enregistre un service NSSM dédié `CCW-Watcher-<NomProjet>` (mêmes réglages que `CCW-Watcher` : `SERVICE_AUTO_START`, `AppExit Default Restart`, `AppRestartDelay`, `logs\ccw-<nom>-service.log`). Idempotent (clone mis à jour par pull, service arrêté/supprimé avant recréation). Ne configure **pas** `AppEnvironmentExtra` : chaque projet a son propre token dédié, posé ensuite en **une seule commande** via `finaliser_projet_ccw.ps1` (rappel affiché en fin de script). |
+| `ajouter_projet_ccw.ps1` | **(dans la VM — actif, modèle multi-projets #170 ; voir aussi `creer_projet_ccw_complet.ps1`, §16.5, qui l'appelle)** Instancie un projet CCW **supplémentaire** sur le modèle multi-projets (issue #170), sans rien réinstaller. Paramétrable (`-NomProjet`, `-Depot owner/repo`, ou prompt interactif) : clone le dépôt en lecture seule dans `C:\CCW\<NomProjet>`, écrit `configs\<nom>-ccw.conf` (`NOM=<nom>-ccw`, `LABEL=for-windows`, `REP_TRAVAIL`/`PERIMETRE`=`C:\CCW\<NomProjet>`, `TOPIC_NTFY` placeholder), et enregistre un service NSSM dédié `CCW-Watcher-<NomProjet>` (mêmes réglages que `CCW-Watcher` : `SERVICE_AUTO_START`, `AppExit Default Restart`, `AppRestartDelay`, `logs\ccw-<nom>-service.log`). Idempotent (clone mis à jour par pull, service arrêté/supprimé avant recréation). Ne configure **pas** `AppEnvironmentExtra` : chaque projet a son propre token dédié, posé ensuite en **une seule commande** via `finaliser_projet_ccw.ps1` (rappel affiché en fin de script). |
 | `lister_projets_ccw.ps1` | **(dans la VM, appelé à distance — issue #174)** Inventaire **JSON** des projets CCW : énumère les services `CCW-Watcher*` (NSSM), et pour chacun émet le nom du service, le projet dérivé, l'état (`running`/`stopped`) et le statut du placeholder `TOPIC_NTFY` (lu dans le config, sans jamais renvoyer la valeur réelle du topic). Sortie encadrée par `<<<CCW_JSON>>>…<<<CCW_END>>>` pour extraction fiable côté Linux. Exécuté par l'onglet CCW de l'interface web. |
 | `finaliser_projet_ccw_auto.ps1` | **(dans la VM, appelé à distance — issue #174)** Variante **non interactive** de `finaliser_projet_ccw.ps1` : lit `TOPIC_NTFY` + les deux tokens dans un **fichier « clé=valeur »** poussé par l'appelant (jamais en argument de commande), remplace le placeholder `TOPIC_NTFY` dans le config (édition ciblée) puis **appelle** `mettre_a_jour_tokens_ccw.ps1 -FichierTokens` (aucune duplication de la logique des tokens). Supprime le fichier de valeurs dans un `finally` (nettoyage côté VM). Code de sortie = celui du script de tokens (0/2/1). |
-| `finaliser_projet_ccw.ps1` | **(obsolète — modèle multi-projets abandonné, conservé à titre historique)** **(dans la VM)** Finalise en **une seule commande** un projet déjà créé par `ajouter_projet_ccw.ps1` (issue #173, suite #170), regroupant les 3 étapes manuelles auparavant dispersées. À partir du seul `-NomProjet` (argument ou prompt), **dérive** `CCW-Watcher-<NomProjet>`, `C:\CCW\<NomProjet>` et `configs\<nom>-ccw.conf` (même logique qu'`ajouter_projet_ccw.ps1`) et **vérifie** leur existence (sinon renvoie vers `ajouter_projet_ccw.ps1`). Puis : (1) demande `TOPIC_NTFY` (`Read-Host`, pas un secret) et remplace le placeholder `###TOPIC_NTFY_A_DEFINIR###` **dans** le config par édition ciblée (le reste du fichier préservé, UTF-8 sans BOM) ; (2) rappelle les réglages du token dédié à créer (repo unique, permissions, expiration alignée) avec une **pause** ; (3) **appelle** `mettre_a_jour_tokens_ccw.ps1` (pas de duplication) avec les paramètres déduits — dont `-NomLog ccw-<nom>-service.log` — pour la saisie masquée + pose des tokens + redémarrage + vérif des logs ; (4) résumé final selon le code renvoyé. |
+| `finaliser_projet_ccw.ps1` | **(dans la VM — actif, modèle multi-projets #170)** Finalise en **une seule commande** un projet déjà créé par `ajouter_projet_ccw.ps1` (issue #173, suite #170), regroupant les 3 étapes manuelles auparavant dispersées. À partir du seul `-NomProjet` (argument ou prompt), **dérive** `CCW-Watcher-<NomProjet>`, `C:\CCW\<NomProjet>` et `configs\<nom>-ccw.conf` (même logique qu'`ajouter_projet_ccw.ps1`) et **vérifie** leur existence (sinon renvoie vers `ajouter_projet_ccw.ps1`). Puis : (1) demande `TOPIC_NTFY` (`Read-Host`, pas un secret) et remplace le placeholder `###TOPIC_NTFY_A_DEFINIR###` **dans** le config par édition ciblée (le reste du fichier préservé, UTF-8 sans BOM) ; (2) rappelle les réglages du token dédié à créer (repo unique, permissions, expiration alignée) avec une **pause** ; (3) **appelle** `mettre_a_jour_tokens_ccw.ps1` (pas de duplication) avec les paramètres déduits — dont `-NomLog ccw-<nom>-service.log` — pour la saisie masquée + pose des tokens + redémarrage + vérif des logs ; (4) résumé final selon le code renvoyé. |
 | `surveiller_builds.ps1` | **(dans la VM, lancé manuellement — issue #370)** Surveille en continu, pendant un build en cours (PyInstaller/ISCC), les processus de build et la croissance du dossier de sortie. Paramètre `-Dossier` **obligatoire** (chemin du dossier de sortie à surveiller, ex. `installeur\output`) ; `-Processus` optionnel (liste de noms de process à surveiller, défaut `claude, ISCC, python, pyinstaller`) ; `-IntervalleSecondes` optionnel (défaut `10`). À chaque passage : affiche pour chaque process surveillé son PID/CPU/mémoire/durée de vie s'il est actif, et la taille du dossier avec le delta depuis le dernier passage et depuis le début. Exemple : `powershell -ExecutionPolicy Bypass -File provisioning\windows\surveiller_builds.ps1 -Dossier C:\CCW\actualise\installeur\output -IntervalleSecondes 15`. **Attention** : le nom de process Claude Code (`claude` par défaut dans `-Processus`) est une hypothèse à vérifier via `Get-Process` pendant un build réel — l'installeur natif Windows peut l'enregistrer sous un nom différent, auquel cas le passer explicitement en paramètre. |
 
+**Script d'orchestration complémentaire, hors dossier `provisioning/windows/`.**
+`creer_projet_ccw_complet.ps1`, placé à la **racine** du dépôt (pas dans
+`provisioning/windows/`), enchaîne les scripts ci-dessus en une seule
+commande pour créer un nouveau projet CCW de bout en bout — voir §16.5.
+
 > **⚠️ Obsolète (PC physique, issue #446).** Les deux paragraphes qui suivent
 > décrivent l'ancienne VM **Windows 11 IoT Enterprise LTSC 2024 en évaluation
 > 90 jours** et sa procédure de recréation. Le PC fixe physique tourne sous
# ── Zone modifiée : ligne 1893 (6 ligne(s)) dans l'ancienne version → ligne 1938 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1893,6 +1938,13 @@ powershell -ExecutionPolicy Bypass -File provisioning\windows\ajouter_projet_ccw
 `REP_TRAVAIL` sont pilotés par config, donc un deuxième service qui pointe vers
 `configs\scrabble-ccw.conf` suffit — aucune modification de code.
 
+**État actuel (issue #547).** 5 services NSSM tournent ainsi en
+production, tous confirmés à l'état `running` via l'onglet CCW : `CCW-Watcher`
+(base, Bridge_Agent) + `CCW-Watcher-actualise`, `-alchess`, `-rummikub`,
+`-scrabble`. Voir §16.5 pour `creer_projet_ccw_complet.ps1`, qui orchestre
+en une commande la création (ce paragraphe) et la finalisation (topic +
+tokens + `PATH`, ci-dessous) d'un nouveau projet.
+
 **Finaliser en une seule commande (issue #173).** Là où il fallait auparavant
 trois étapes manuelles dispersées (éditer `TOPIC_NTFY` à la main dans le config,
 créer le token GitHub, puis relancer `mettre_a_jour_tokens_ccw.ps1` avec les bons
# ── Zone modifiée : ligne 2219 (6 ligne(s)) dans l'ancienne version → ligne 2271 (59 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2219,6 +2271,59 @@ CCW n'est **jamais** relancé automatiquement (relance manuelle via l'onglet
 CCW). Voir § « Interrompre une issue bloquée » (§13) pour le pendant côté CCL
 et le détail commun de l'interface (bouton, route Flask, statuts).
 
+### 16.5 Créer un nouveau projet CCW en une commande (`creer_projet_ccw_complet.ps1`, issue #492)
+
+**Rôle.** Script d'orchestration qui enchaîne, en **une seule commande**,
+les 3 étapes mécaniques nécessaires pour ajouter un projet au modèle
+multi-projets actif (#170, cf. plus haut dans ce §16) :
+
+1. Clone + `.conf` + service NSSM, via le script existant
+   `provisioning\windows\ajouter_projet_ccw.ps1` — **appelé**, pas
+   dupliqué.
+2. Remplacement ciblé du placeholder `TOPIC_NTFY` dans le `.conf`
+   fraîchement créé.
+3. Saisie masquée des deux tokens (`GH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`),
+   **testés à blanc avant application** (`gh repo view <Depot>` /
+   `claude --print "réponds juste OK"` — échouer vite et clairement plutôt
+   que découvrir un 401 après coup) ; puis écriture de
+   `AppEnvironmentExtra` avec un **`PATH` explicite** incluant
+   `C:\Users\AlainW\.local\bin` (fix du piège PATH-au-boot constaté avec
+   Scrabble : un service NSSM démarré au boot n'hérite pas du `PATH`
+   utilisateur, donc pas de `claude.exe`) ; et redémarrage du service avec
+   affichage des 10 dernières lignes de son log.
+
+Contrairement à `finaliser_projet_ccw.ps1` (tableau de provisioning
+ci-dessus), les étapes 2 et 3 ne délèguent pas à
+`mettre_a_jour_tokens_ccw.ps1` : elles sont réimplémentées directement dans
+ce script, pour intégrer le test à blanc des tokens et le correctif `PATH`
+— deux besoins apparus après coup (issue #492 bis) que le script de tokens
+historique ne couvrait pas.
+
+**Emplacement et usage.** Placé à la **racine** du dépôt (pas dans
+`provisioning\windows\`), à exécuter depuis `C:\CCW\Bridge_Agent` :
+
+```powershell
+cd C:\CCW\Bridge_Agent
+powershell -ExecutionPolicy Bypass -File creer_projet_ccw_complet.ps1 `
+    -NomProjet actualise -Depot AlainDelree/Actualise -TopicNtfy <topic>
+```
+
+- `-NomProjet` (obligatoire) — dérive `CCW-Watcher-<NomProjet>`,
+  `C:\CCW\<NomProjet>` et `configs\<nom>-ccw.conf` (même logique
+  qu'`ajouter_projet_ccw.ps1`/`finaliser_projet_ccw.ps1`).
+- `-Depot` (obligatoire) — dépôt GitHub du projet, au format `owner/repo`.
+- `-TopicNtfy` (optionnel — une valeur de secours est câblée dans le
+  script) — topic ntfy dédié au projet.
+
+**Prérequis manuel (hors périmètre du script).** Créer **au préalable**, à
+la main sur GitHub (Settings → Developer settings → Fine-grained tokens),
+le token GitHub **dédié** au projet — repository access limité à `<Depot>`
+uniquement, permissions *Issues* = Read and write, *Metadata* = Read-only,
+expiration alignée sur les autres tokens CCW (cf. règle d'or plus haut) —
+et avoir `claude setup-token` prêt à lancer pour générer le second token.
+Le script s'arrête (code de sortie 1) et invite à vérifier/recréer le
+token concerné si l'un des deux manque ou échoue au test à blanc.
+
 ---
 
 ## 17. Notifications centralisées — détection serveur des transitions (issue #187)
