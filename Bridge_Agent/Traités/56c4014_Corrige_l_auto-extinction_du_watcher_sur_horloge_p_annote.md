56c4014

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 56c4014
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 11:00:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige l'auto-extinction du watcher sur horloge périmée après un traitement long : réarme derniere_activite APRÈS le traitement, pas seulement avant (issue #217)
    
    Cause : derniere_activite (#200) n'était réarmée qu'en tête de cycle,
    avant traiter_issue(). Un traitement long (timeouts+retries > délai
    d'inactivité) laissait l'horloge figée au début du cycle → extinction
    immédiate après un succès réel (log watcher-scrabble 24/07/2026).
    
    Fix : réarmement supplémentaire après la boucle de traitement dès qu'au
    moins une issue traitable a été traitée (flag travail_a_faire). Extinction
    toujours possible quand plus rien n'est traitable.
    
    + tests/test_auto_extinction_217.py : test de non-régression pilotant le
      vrai main() avec time.monotonic mocké (3 scénarios).
    + BRIDGE_AGENT_DOC.md : §13 mécanisme 3 + changelog.
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 69bd188..04b89e5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 521 (15 ligne(s)) dans l'ancienne version → ligne 521 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -521,15 +521,24 @@ par CCW, rien à lancer côté Linux) ; un échec de démarrage n'invalide jamai
 création d'issue, qui reste réussie.
 
 **3. Extinction automatique après inactivité** (issues #199 / #200, réglable
-#201). En tête de chaque cycle, avant de lister les issues, le watcher mesure le
-temps écoulé depuis la dernière issue **traitable** (ni `done`, ni
-`needs-human`). Au-delà de `DELAI_INACTIVITE_MIN` minutes (défaut **20**), il
-s'arrête proprement (`sys.exit(0)`) et nettoie son fichier PID. Le test se fait
-uniquement **entre** deux cycles complets : un cycle de retry en cours (jusqu'à
-~20 min, cf. #183) n'est jamais interrompu. `DELAI_INACTIVITE_MIN = 0` **désactive**
-le mécanisme → watcher permanent (comportement historique). Le réglage est
-exposé par projet dans l'onglet « Configuration » (issue #201) et vit dans le
-`.conf` du projet.
+#201, correctif horloge #217). En tête de chaque cycle, avant de lister les
+issues, le watcher mesure le temps écoulé depuis la dernière issue **traitable**
+(ni `done`, ni `needs-human`). Au-delà de `DELAI_INACTIVITE_MIN` minutes (défaut
+**20**), il s'arrête proprement (`sys.exit(0)`) et nettoie son fichier PID. Le
+test se fait uniquement **entre** deux cycles complets : un cycle de retry en
+cours (jusqu'à ~20 min, cf. #183) n'est jamais interrompu. L'horloge
+d'inactivité (`derniere_activite`) est réarmée **deux fois** par cycle : une fois
+**avant** le traitement (dès qu'une issue traitable est détectée) et une fois
+**après** (dès qu'au moins une issue traitable a été traitée). Ce second
+réarmement (issue #217) date la **fin** réelle du travail : sans lui, le
+traitement d'une seule issue s'étirant au-delà du délai (plusieurs timeouts de
+300 s + retries en cascade — cas réel `watcher-scrabble.log` du 24/07/2026,
+~23 min) laissait l'horloge figée au début du cycle, et le test d'extinction du
+cycle suivant se déclenchait **immédiatement après un succès** (~14 s après), sur
+une horloge périmée ne reflétant pas le travail réel effectué. `DELAI_INACTIVITE_MIN
+= 0` **désactive** le mécanisme → watcher permanent (comportement historique). Le
+réglage est exposé par projet dans l'onglet « Configuration » (issue #201) et vit
+dans le `.conf` du projet.
 
 **Cycle complet.** Watcher éteint pour inactivité → on crée une issue for-linux
 → le watcher est rallumé automatiquement (#202) → il traite la tâche → après
# ── Zone modifiée : ligne 1144 (4 ligne(s)) dans l'ancienne version → ligne 1153 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1144,4 +1153,4 @@ Le nom de fichier est **horodaté** (`AAAAMMJJ-HHMMSS-<nom_original>.png`) pour
 
 ---
 
-*Dernière mise à jour : 24 juillet 2026 — Nouveau rappel global « abandon immédiat au refus de permission » (issue #214) : ajout, à la fin de `consignes/globales.md`, d'un rappel systématique — si une commande/un outil est **refusé par le système de permissions** (session non-interactive, aucune approbation possible) ou **boucle/tarde anormalement** (> 30s sans progrès net), CCL doit **abandonner immédiatement** l'approche et le signaler dans son rapport plutôt que de retenter, en basculant si possible sur un repli plus simple (lecture directe, `grep`, analyse manuelle) et sans jamais insister sur une commande déjà refusée. Motivation : comparaison des issues Scrabble #235 (timeout à 300s, bouclage sur une commande refusée) et #238 (succès) — la seule différence significative était la présence, dans #238, d'une consigne explicite d'abandon-au-lieu-de-retenter ; en session non-interactive, un refus de permission Claude Code est systématique et définitif (aucun utilisateur pour approuver), donc retenter est vain. Consigne volontairement **générale** (pas spécifique à Scrabble ni à JS/eslint) car le problème touche toute commande nécessitant une approbation (installation de paquet, exécution d'un binaire, etc.), quel que soit le projet ou le langage. §12.1 : la parenthèse résumant les rappels globaux dans le tableau des trois couches est complétée (ajout d'« abandon immédiat au refus de permission / boucle anormale ») ; la liste complète des rappels n'étant pas reproduite ailleurs dans la doc, aucune autre duplication à mettre à jour. Précédemment — Déplacement de l'injection des consignes trois couches dans `watcher.py` — couverture universelle (issue #211). Les consignes (globales/type/projet, #209) ne sont plus écrites dans le **corps** de l'issue par `app/issues.py` (chemin qui ne couvrait QUE les issues créées via le formulaire web), mais injectées dans le **prompt donné à CCL au moment du traitement** par `watcher.py` (`lancer_claude` → nouvelles `_consignes_injectees`/`_lire_consigne`, reprises de `app/issues.py`), exactement sur le modèle de `CONTEXTE.md`/`FICHIER_CONTEXTE`. Le point de passage devient **unique** : peu importe le chemin de création — formulaire web, `gh issue create` d'un chef (§14), création manuelle GitHub (§3) — `watcher.py` déduit le TYPE (`deduire_type_issue` sur le titre/corps réels) et le projet (`CFG.nom`), puis ajoute le bloc **après** le bloc `CONTEXTE` et **avant** la clause de périmètre / le garde-fou (regroupement des « règles » en fin de prompt, zone la mieux suivie). Cas particulièrement corrigé : les issues **ouvrières créées par un chef** (chemin 2, vraies tâches `mode_write`) recevaient auparavant zéro consigne — c'est justement là que les rappels de sécurité comptent le plus. `app/issues.py::construire_body` revient à un corps **en-tête + corps rédigé** seulement (suppression de `_consignes_injectees`/`_lire_consigne`/`DOSSIER_CONSIGNES` et de l'import `logging` devenu inutile) — source unique de vérité désormais côté watcher, plus de double injection. Garde-fous inchangés (#209) : `globales.md` absent → `log.warning` sans bloquer le traitement ; `type_*`/`projet_*` absents → silencieux. Conséquence assumée (comme pour `CONTEXTE.md`) : les consignes ne sont plus visibles dans le corps d'une issue sur GitHub. **§12.1 réécrite** (modèle prompt + couverture universelle des 3 chemins + emplacement dans le prompt) et **§10** mis à jour (`consignes/` = injecté dans le prompt CCL, plus « en tête de chaque issue »). Testé de bout en bout par une issue `TYPE=chef` `mode_write` créée **directement en CLI** (`gh issue create`, hors formulaire) : le prompt CCL assemblé par le watcher contient bien les consignes globales + `type_chef.md`. Précédemment — Architecture à trois couches d'injection de consignes (issue #209) : nouveau dossier `consignes/` à la racine, injecté **dans le corps de chaque issue** par `app/issues.py` (`construire_body` → `_consignes_injectees`), entre le tableau d'en-tête et le corps rédigé par Claude Chat. Trois couches, de la plus générale à la plus spécifique : **globales** (`consignes/globales.md`, **NON-optionnel** — rappels de sécurité transversaux : ne jamais pousser, backup avant modif, respect du périmètre — injecté dans TOUTE issue), **type** (`consignes/type_<type>.md`, **facultatif** — ex. `type_chef.md` reprenant la contrainte d'exécution synchrone du #208, injecté selon le TYPE déduit par `watcher.deduire_type_issue`), **projet** (`consignes/projet_<projet>.md`, **facultatif** — aucun créé par défaut). Ordre final : en-tête → globales → type (si présent) → projet (si présent) → corps. Vaut en **mono-issue comme en mode lot** (chaque bloc `#Titre:` passe par `construire_body` avec son propre TYPE). **Choix délibéré anti-piège de maintenance** : contrairement à `CONTEXTE.md`, les couches type/projet sont sans obligation de présence (un projet sans `projet_<nom>.md` fonctionne normalement, rien à créer/maintenir) et créées uniquement à la demande. Garde-fous : fichier `type_*`/`projet_*` absent → aucune injection **sans** log (normal, pas une anomalie) ; `globales.md` introuvable → `logging.warning` clair **sans jamais faire échouer** la création d'issue. Nouvelle sous-section **§12.1** décrivant l'architecture, mise à jour du **§10** (dossier `consignes/`) et du **§14** (la contrainte d'exécution synchrone du chef n'est plus à recopier manuellement — elle est injectée automatiquement via `consignes/type_chef.md`). Testé de bout en bout (issue `TYPE=chef` réelle : corps GitHub contenant, dans l'ordre, globales puis chef puis corps original). Précédemment — Finalisation du nettoyage doc MVC (issue #208, suite #207) : le §14 « Délégation Chef → Ouvrier » gagne un bloc **« ⚠️ Contrainte d'exécution impérative »** rappelant que le chef doit accomplir la TOTALITÉ de sa tâche (attente de fermeture des ouvriers + synthèse finale comprises) en **une seule exécution synchrone et bloquante** — aucune reprise n'étant possible après qu'une issue a été répondue/fermée, ne jamais recourir à une attente différée, une tâche en arrière-plan ou un « je répondrai plus tard » ; si une attente est nécessaire, boucler (`sleep` + `gh issue view`) DANS la même exécution. Cette finalisation confirme aussi l'absence des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` à la racine de bridge_agent (jamais créés ici ; seul `CONTEXTE.md` existe et est conservé). Précédemment — Nettoyage doc MVC (issue #207) : **suppression de l'ancien §15 « Pattern Chef + Specs MVC (évolution future) »**, purement prospectif et jamais implémenté (le watcher ne lit pas le champ `SPECS`, aucun routage par couche Vue/Métier/Persistance n'existe) ; les sections suivantes **ne sont pas renumérotées** (16, 17, 18 restent 16, 17, 18) pour préserver les références croisées existantes. Le **§14 est entièrement réécrit** et recadré « Délégation Chef → Ouvrier (changement d'environnement) » : on ne garde que l'usage réel validé — un CCL « chef » crée lui-même une issue « ouvrier » ciblant un autre environnement (typiquement CCL Linux → CCW Windows) via `gh issue create` et surveille sa fermeture avant de livrer, sur instruction explicite (pas de détection auto du rôle chef, pas de décomposition automatique générique) — avec conseil de `TIMEOUT` généreux côté chef et l'exemple validé du build Scrabble/ouvrier CCW. En complément, l'issue chef #207 délègue à 6 issues « ouvrier » (une par projet actif hors bridge_agent et ff_galerie) la suppression des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` — vestiges du §15 abandonné — `CONTEXTE.md` (mécanisme standard hors MVC) étant conservé partout. Précédemment — §18 (nouveau) « Pièces jointes image dans les issues » (issue #191) : l'onglet « Nouvelle issue » accepte désormais un **upload optionnel PNG/JPEG** (champ fichier + bouton « Joindre une image » à côté du corps). Nouvelle route **`POST /joindre-image`** (`app/issues.py`, `joindre_image()`) : valide le type (Content-Type **et** magic bytes) et la taille (**≤ 5 Mo**), sauvegarde dans **`issue-attachments/`** (racine du `REP_TRAVAIL`) sous un nom **horodaté** anti-collision (`AAAAMMJJ-HHMMSS-<nom>.ext`), puis `git add` + `commit` + **`git push origin HEAD:<branche>`** (branche déduite **dynamiquement**, jamais supposée master/main), et retourne l'URL **`raw.githubusercontent.com/<owner>/<repo>/<branche>/issue-attachments/<fichier>`** — format qui s'affiche correctement dans les issues GitHub. Le frontend (`static/js/app.js`, `joindreImage()`/`insererDansCorps()`) insère alors **automatiquement** `![<nom>](<url>)` dans le corps à la position du curseur. **Exception `push` assumée et documentée (§18.2)** : ce commit+push est déclenché par **ALAIN** via l'outil (son action manuelle), **pas par CCL/le watcher** — la règle « CCL ne pousse jamais » n'est donc pas violée (elle vise les modifications de code de l'agent, pas une image qu'Alain publie lui-même). Gestion d'erreurs (§18.4) : **push échoué → aucune URL insérée** (commit conservé en local, poussable plus tard), **projet sans dépôt git → message clair**, type/taille/contenu invalides refusés proprement. `issue-attachments/` volontairement **hors `.gitignore`** (les images doivent être suivies/poussées). Testé de bout en bout (dépôt jetable + remote bare : succès + URL correcte, et chemins d'échec type/taille/magic/push). Précédemment — §17 (nouveau) « Notifications centralisées — détection serveur des transitions » (issue #187) : `new_issue.py`, qui tourne en permanence sur le ThinkPad, détecte désormais LUI-MÊME par polling `gh` les transitions d'issues (fermeture `done` = succès ; label `needs-human` = échec définitif) de **tous** les projets (for-linux ET for-windows), et déclenche bip/`notify-send`/`ntfy` **localement**, y compris pour les issues traitées par la VM **CCW** — **sans aucun appel réseau initié par la VM** (la VM n'écrit que sur GitHub). Nouveau module partagé `notifications.py` (racine) factorisant `bip`/`notifier_bureau`/`notifier_ntfy`/`notifier`, importé par `watcher.py` (enveloppes minces déléguant, sites d'appel inchangés) ET par le nouveau poller `app/notifications_poller.py` (thread démon lancé par `new_issue.py`). Script bip **déplacé/recréé** de `~/NicLink/bip.py` vers `scripts/bip.py` (infrastructure partagée) ; défaut `SCRIPT_BIP` et `configs/*.conf` mis à jour. Anti-doublon (point 4) : réglage `NOTIFIER_LOCAL` (`.conf`, défaut `true`) coupant la notif du watcher + portée `BRIDGE_NOTIF_SCOPE` (env, défaut `for-windows`) du poller. **Défaut livré sans régression ni doublon** (CCL notifie via son watcher, CCW via le poller — variante propre de l'option b) ; **option (a) « centralisation complète » recommandée mais laissée au choix d'Alain** car elle fait de `new_issue.py` une dépendance dure de toute notification (or il n'a pas encore de service systemd) — implémentée et à un réglage près (`BRIDGE_NOTIF_SCOPE=all` + `NOTIFIER_LOCAL=false` partout). **Action requise côté VM CCW** : poser `NOTIFIER_LOCAL=false` dans `configs\*-ccw.conf` pour éviter un double `ntfy`. Bonus (point 5) : le poller lit les labels COURANTS à la fermeture, donc `notif_pc`/`notif_gsm` ajouté EN COURS de traitement est bien pris en compte. Filtre de récence (`BRIDGE_NOTIF_RECENCE_MIN`, défaut 30 min) + amorçage silencieux au 1er cycle évitent le spam de vieilles issues au démarrage ; état en mémoire process. Précédemment — §1 « Vue d'ensemble » : documentation du **`git pull --ff-only` automatique en début de cycle** de `watcher.py` (issue #186, suite du #185 qui l'a implémenté). Le watcher rafraîchit son clone (`REP_TRAVAIL`) au début de chaque cycle de polling, juste avant `lister_issues()` : fast-forward transparent en cas de succès ; en cas de commits locaux non poussés (divergence) le `--ff-only` échoue proprement sans RIEN écraser et le watcher poursuit sur le code local — donc aucun risque à oublier un `git push`. Comportement **identique CCL (Linux) et CCW (Windows)** puisque `watcher.py` est le script unique partagé ; les projets à périmètre dynamique (dépôt-cible par issue) ne sont pas concernés. Un `git pull`/relance manuel reste possible pour une mise à jour immédiate (confort, plus une nécessité). Aucune instruction obsolète de « git pull manuel obligatoire » à corriger dans le §16 (aucune ne subsistait). Précédemment — §16 « Agent Windows CCW » : **onglet « CCW » dans l'interface web** (issue #174, sous-section §16.2) — pilotage complet de la VM et des projets CCW depuis Linux, sans PowerShell manuel dans la VM. Backend `app/ccw.py` (routes `/ccw/*`) exécutant les scripts existants à distance via `VBoxManage guestcontrol` : état/démarrage de la VM (`demarrer_ccw.sh`), liste des projets (nouveau `lister_projets_ccw.ps1`, sortie JSON encadrée), ajout (`ajouter_projet_ccw.ps1`) et finalisation non interactive (nouveau `finaliser_projet_ccw_auto.ps1` + `mettre_a_jour_tokens_ccw.ps1` doté d'un mode `-FichierTokens`). Sécurité : tokens jamais passés en argument ni journalisés (fichier temporaire `0600` poussé puis supprimé des deux côtés dans un `finally`) ; mot de passe `ccw-admin` lu depuis `CCW_ADMIN_PASSWORD` ou `configs/ccw_admin.secret` (gitignoré). Nouvel onglet + panneau dans `templates/index.html`, fonctions `ccw*` dans `static/js/app.js`, classe `.message.avertissement` dans `style.css`. Précédemment — §16 « Agent Windows CCW » : **finalisation d'un projet CCW en une seule commande** (issue #173, suite #170) — ajout de `provisioning/windows/finaliser_projet_ccw.ps1` qui, à partir du seul `-NomProjet`, dérive le service/dossier/config (même logique qu'`ajouter_projet_ccw.ps1`), vérifie leur existence, demande `TOPIC_NTFY` et l'écrit directement dans le config (remplacement ciblé du placeholder `###TOPIC_NTFY_A_DEFINIR###`, reste du fichier préservé en UTF-8 sans BOM), rappelle avec une pause la marche à suivre pour créer le token GitHub dédié, puis **appelle** `mettre_a_jour_tokens_ccw.ps1` (pas de duplication) pour la saisie masquée + pose des tokens + redémarrage + vérif des logs, et conclut par un résumé ; `mettre_a_jour_tokens_ccw.ps1` gagne un paramètre `-NomLog` pour vérifier le bon log de service (`ccw-<nom>-service.log`) ; les rappels d'`ajouter_projet_ccw.ps1` (en-tête + fin de script) et le §16 pointent désormais vers cette commande unique au lieu des 3 étapes dispersées. Non exécuté contre une VM réelle (test manuel par Alain). Précédemment — §11 « Conventions de code » : **règle BOM UTF-8 obligatoire pour tout script `.ps1`** (issue #172) — ajout du BOM (`EF BB BF`) manquant sur `ajouter_projet_ccw.ps1` (#170) et `mettre_a_jour_tokens_ccw.ps1` (#168), qui plantaient sinon sous Windows PowerShell 5.1 avec des `UnexpectedToken` en cascade sur les accents (même signature que #151) ; règle généralisée en §11 + rappel en tête du §16 pour prévenir la récidive (`provisionner.ps1` déjà OK depuis #151). Précédemment — §16 « Agent Windows CCW » : **généralisation multi-projets de CCW** (issue #170) — ajout de `provisioning/windows/ajouter_projet_ccw.ps1` (un clone + un config `configs\<nom>-ccw.conf` + un service NSSM `CCW-Watcher-<NomProjet>` dédiés par projet, sur le modèle des watchers CCL ; paramétrable `-NomProjet`/`-Depot`, idempotent, `watcher.py` inchangé) ; documentation du modèle « un service par projet » et de la **règle d'expiration alignée** des tokens (un token fine-grained dédié par dépôt, mais tous à la même échéance ≈ 17 octobre 2026) ; commande exacte d'instanciation de Scrabble et marche à suivre pour créer son token dédié (Repository access → Scrabble uniquement, Issues read/write + Metadata read-only). Précédemment — §16 « Agent Windows CCW » : ajout de la sous-section **§16.1 Maintenance périodique (renouvellement à 90 jours)** (issue #169) — runbook séquentiel consolidé pour la fenêtre de maintenance d'octobre 2026 : tableau de repères de dates (install **2026-07-19**, expiration Windows **2026-10-17**, token GitHub aligné ~90 j mais non stocké), puis procédure en 3 étapes renvoyant aux scripts existants — vérifier (`verifier_expiration_ccw.py`), recréer la VM (`creer_vm_ccw.py --recreate` + ré-attacher un ISO frais + `lancer_provisioning.py`), renouveler les tokens (`mettre_a_jour_tokens_ccw.ps1`) — sans dupliquer le détail technique déjà présent dans le §16. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/mettre_a_jour_tokens_ccw.ps1` (issue #168) — renouvellement des tokens `GH_TOKEN`/`CLAUDE_CODE_OAUTH_TOKEN` du service `CCW-Watcher` sans reconstruire à la main la chaîne `AppEnvironmentExtra` : saisie masquée (`Read-Host -AsSecureString`), séparateur `` `n`` impératif entre les deux paires (un espace corrompt `GH_TOKEN` → « Bad credentials »), `nssm set`/`nssm restart`, puis affichage automatique des 10 dernières lignes de `logs\ccw-service.log` pour confirmer l'absence d'erreur d'auth. Précédemment — §16 « Agent Windows CCW » : alerte d'expiration de l'éval 90 jours (issue #167) — ajout de `provisioning/windows/eval-expiration.json` (date d'installation **2026-07-19**, expiration **2026-10-17**) et du script `provisioning/windows/verifier_expiration_ccw.py` (côté Linux : calcule les jours restants, alerte + code de sortie 2 à ≤ 10 j, sinon confirmation calme ; `python3 provisioning/windows/verifier_expiration_ccw.py`) ; rappel `cron` + `ntfy` hebdomadaire proposé mais laissé à l'activation d'Alain. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/demarrer_ccw.sh` (issue #166), wrapper de démarrage de la VM `CCW-Build` depuis CCL (headless par défaut, `--gui`/`--fenetre` pour une fenêtre, `--status` pour l'état sans rien démarrer). Précédemment — §3 « Créer une issue » : ajout d'une note sur la **convention de présentation côté Claude Chat** pour l'envoi en lot (issue #153) — quand Claude Chat prépare plusieurs issues, il les présente toutes à la suite dans un seul bloc de code (pas un bloc par issue) pour un copier-coller en un clic. Précédemment — §16 « Agent Windows CCW » : `REP_TRAVAIL` généré par `provisionner.ps1` pointe désormais vers le **chemin UNC** `\\VBOXSVR\CCW_Share` (et non la lettre automontée `$LettrePartage`), seul accessible au service `CCW-Watcher` tournant sous LocalSystem (issue #149, suite #148) ; `$LettrePartage` conservé pour référence mais plus utilisé pour construire `REP_TRAVAIL`. Précédemment — le watcher CCW tourne comme **vrai service Windows** enregistré via NSSM (issue #148, suite #147) — `provisionner.ps1` installe `NSSM.NSSM` (winget) et enregistre le service `CCW-Watcher` (`SERVICE_AUTO_START` + `AppExit Default Restart` + `AppRestartDelay 5000`, stdout/stderr → `logs\ccw-service.log`, idempotent via `nssm stop`/`remove`), en remplacement de l'ancienne tâche planifiée `-AtLogOn` qui ne redémarrait pas au boot sans session ; équivalent direct des services systemd du §13. Précédemment — provisioning **phase 2** (issue #147, suite #146) — ajout de `provisioning/windows/provisionner.ps1` (installe l'outillage dans la VM via winget + Claude Code natif, clone le dépôt, écrit `ccw.conf`, enregistre la tâche planifiée `CCW-Watcher`) et `lancer_provisioning.py` (pousse/exécute ce script depuis CCL via `VBoxManage guestcontrol`) ; `watcher.py` inchangé (portable, `LABEL` paramétrable) ; limite Task Scheduler vs `Restart=always` documentée. Précédemment — ajout du §16 et du label `for-windows` (issue #146) : provisioning phase 1 de la VM Windows CCW (`provisioning/windows/creer_vm_ccw.py` + `autounattend.xml`) destinée aux builds .exe délégués par CCL. Précédemment — Bridge_Agent v1, 4 projets actifs. §3 « Créer une issue » : ajout de l'**envoi en lot** (issue #135) — coller plusieurs blocs `#Titre:` à la suite dans le même corps déclenche le mode lot (bouton « Envoyer le lot (N issues) »), chaque bloc étant envoyé en séquence comme une issue indépendante (avec ses `PROJET`/`TIMEOUT`/`MODELE` optionnels), sans validation intermédiaire, suivi d'un résumé listant le résultat de chacune. Ajout du projet `ecole` (AlainDelree/Ecole, ~/Ecole) aux tableaux §2 et §7 (issue #101). Section 15 « Chef + Specs MVC » : champ `SPECS` (pluriel, minuscules, combinable en une ligne) — correction du champ `SPEC` introduit par erreur (issue #97, suite #96).*
+*Dernière mise à jour : 24 juillet 2026 — Correctif horloge d'auto-extinction (issue #217) : le watcher pouvait s'éteindre **immédiatement après un traitement réel** lorsque celui-ci s'étirait au-delà du délai d'inactivité (`DELAI_INACTIVITE_MIN`, défaut 20 min). Cause : `derniere_activite` (horloge monotone d'inactivité, #200) n'était réarmée qu'**en tête de cycle**, juste après `lister_issues()` et **avant** de lancer `traiter_issue()` — donc jamais pendant le traitement (potentiellement long : plusieurs timeouts de 300 s + retries en cascade). Si le traitement d'une seule issue dépassait le délai (cas réel `watcher-scrabble.log` du 24/07/2026 : #237/#238 traités sans interruption de 08:59 à 09:22, puis extinction à 09:23:08 — 14 s après le succès de #238), l'horloge restait figée à l'instant du **début** du cycle ; le test d'extinction du cycle suivant se déclenchait alors sur une horloge périmée, ne reflétant pas le travail réellement effectué. **Correctif** (`watcher.py`, boucle principale) : réarmement de `derniere_activite` **aussi APRÈS** la boucle de traitement, dès qu'au moins une issue traitable a été traitée ce cycle (option a du diagnostic — réarmer sur le travail réel, préférée à l'option b « revérifier `lister_issues()` avant `sys.exit` » car elle satisfait plus directement l'objectif « ne jamais éteindre si du travail vient d'avoir lieu », sans appel réseau supplémentaire ni cas où une issue devenue fermée entre-temps laisserait l'extinction filer). Le flag `travail_a_faire` (calculé une fois) conditionne les deux réarmements ; l'extinction reste possible quand plus rien n'est traitable. **Test de non-régression** : `tests/test_auto_extinction_217.py` pilote le vrai `watcher.main()` avec horloge mockée (`time.monotonic`/`time.sleep` patchés) sur 3 scénarios — (1) traitement long ~23 min + issue restante → **pas** d'extinction prématurée (échoue sur le code d'avant #217, passe sur le code corrigé), (2) inactivité réelle → extinction bien déclenchée, (3) issue non-traitable (`done`) → n'empêche pas l'extinction. §13 (mécanisme 3 « Extinction automatique ») mis à jour pour décrire le double réarmement avant/après. Précédemment — Nouveau rappel global « abandon immédiat au refus de permission » (issue #214) : ajout, à la fin de `consignes/globales.md`, d'un rappel systématique — si une commande/un outil est **refusé par le système de permissions** (session non-interactive, aucune approbation possible) ou **boucle/tarde anormalement** (> 30s sans progrès net), CCL doit **abandonner immédiatement** l'approche et le signaler dans son rapport plutôt que de retenter, en basculant si possible sur un repli plus simple (lecture directe, `grep`, analyse manuelle) et sans jamais insister sur une commande déjà refusée. Motivation : comparaison des issues Scrabble #235 (timeout à 300s, bouclage sur une commande refusée) et #238 (succès) — la seule différence significative était la présence, dans #238, d'une consigne explicite d'abandon-au-lieu-de-retenter ; en session non-interactive, un refus de permission Claude Code est systématique et définitif (aucun utilisateur pour approuver), donc retenter est vain. Consigne volontairement **générale** (pas spécifique à Scrabble ni à JS/eslint) car le problème touche toute commande nécessitant une approbation (installation de paquet, exécution d'un binaire, etc.), quel que soit le projet ou le langage. §12.1 : la parenthèse résumant les rappels globaux dans le tableau des trois couches est complétée (ajout d'« abandon immédiat au refus de permission / boucle anormale ») ; la liste complète des rappels n'étant pas reproduite ailleurs dans la doc, aucune autre duplication à mettre à jour. Précédemment — Déplacement de l'injection des consignes trois couches dans `watcher.py` — couverture universelle (issue #211). Les consignes (globales/type/projet, #209) ne sont plus écrites dans le **corps** de l'issue par `app/issues.py` (chemin qui ne couvrait QUE les issues créées via le formulaire web), mais injectées dans le **prompt donné à CCL au moment du traitement** par `watcher.py` (`lancer_claude` → nouvelles `_consignes_injectees`/`_lire_consigne`, reprises de `app/issues.py`), exactement sur le modèle de `CONTEXTE.md`/`FICHIER_CONTEXTE`. Le point de passage devient **unique** : peu importe le chemin de création — formulaire web, `gh issue create` d'un chef (§14), création manuelle GitHub (§3) — `watcher.py` déduit le TYPE (`deduire_type_issue` sur le titre/corps réels) et le projet (`CFG.nom`), puis ajoute le bloc **après** le bloc `CONTEXTE` et **avant** la clause de périmètre / le garde-fou (regroupement des « règles » en fin de prompt, zone la mieux suivie). Cas particulièrement corrigé : les issues **ouvrières créées par un chef** (chemin 2, vraies tâches `mode_write`) recevaient auparavant zéro consigne — c'est justement là que les rappels de sécurité comptent le plus. `app/issues.py::construire_body` revient à un corps **en-tête + corps rédigé** seulement (suppression de `_consignes_injectees`/`_lire_consigne`/`DOSSIER_CONSIGNES` et de l'import `logging` devenu inutile) — source unique de vérité désormais côté watcher, plus de double injection. Garde-fous inchangés (#209) : `globales.md` absent → `log.warning` sans bloquer le traitement ; `type_*`/`projet_*` absents → silencieux. Conséquence assumée (comme pour `CONTEXTE.md`) : les consignes ne sont plus visibles dans le corps d'une issue sur GitHub. **§12.1 réécrite** (modèle prompt + couverture universelle des 3 chemins + emplacement dans le prompt) et **§10** mis à jour (`consignes/` = injecté dans le prompt CCL, plus « en tête de chaque issue »). Testé de bout en bout par une issue `TYPE=chef` `mode_write` créée **directement en CLI** (`gh issue create`, hors formulaire) : le prompt CCL assemblé par le watcher contient bien les consignes globales + `type_chef.md`. Précédemment — Architecture à trois couches d'injection de consignes (issue #209) : nouveau dossier `consignes/` à la racine, injecté **dans le corps de chaque issue** par `app/issues.py` (`construire_body` → `_consignes_injectees`), entre le tableau d'en-tête et le corps rédigé par Claude Chat. Trois couches, de la plus générale à la plus spécifique : **globales** (`consignes/globales.md`, **NON-optionnel** — rappels de sécurité transversaux : ne jamais pousser, backup avant modif, respect du périmètre — injecté dans TOUTE issue), **type** (`consignes/type_<type>.md`, **facultatif** — ex. `type_chef.md` reprenant la contrainte d'exécution synchrone du #208, injecté selon le TYPE déduit par `watcher.deduire_type_issue`), **projet** (`consignes/projet_<projet>.md`, **facultatif** — aucun créé par défaut). Ordre final : en-tête → globales → type (si présent) → projet (si présent) → corps. Vaut en **mono-issue comme en mode lot** (chaque bloc `#Titre:` passe par `construire_body` avec son propre TYPE). **Choix délibéré anti-piège de maintenance** : contrairement à `CONTEXTE.md`, les couches type/projet sont sans obligation de présence (un projet sans `projet_<nom>.md` fonctionne normalement, rien à créer/maintenir) et créées uniquement à la demande. Garde-fous : fichier `type_*`/`projet_*` absent → aucune injection **sans** log (normal, pas une anomalie) ; `globales.md` introuvable → `logging.warning` clair **sans jamais faire échouer** la création d'issue. Nouvelle sous-section **§12.1** décrivant l'architecture, mise à jour du **§10** (dossier `consignes/`) et du **§14** (la contrainte d'exécution synchrone du chef n'est plus à recopier manuellement — elle est injectée automatiquement via `consignes/type_chef.md`). Testé de bout en bout (issue `TYPE=chef` réelle : corps GitHub contenant, dans l'ordre, globales puis chef puis corps original). Précédemment — Finalisation du nettoyage doc MVC (issue #208, suite #207) : le §14 « Délégation Chef → Ouvrier » gagne un bloc **« ⚠️ Contrainte d'exécution impérative »** rappelant que le chef doit accomplir la TOTALITÉ de sa tâche (attente de fermeture des ouvriers + synthèse finale comprises) en **une seule exécution synchrone et bloquante** — aucune reprise n'étant possible après qu'une issue a été répondue/fermée, ne jamais recourir à une attente différée, une tâche en arrière-plan ou un « je répondrai plus tard » ; si une attente est nécessaire, boucler (`sleep` + `gh issue view`) DANS la même exécution. Cette finalisation confirme aussi l'absence des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` à la racine de bridge_agent (jamais créés ici ; seul `CONTEXTE.md` existe et est conservé). Précédemment — Nettoyage doc MVC (issue #207) : **suppression de l'ancien §15 « Pattern Chef + Specs MVC (évolution future) »**, purement prospectif et jamais implémenté (le watcher ne lit pas le champ `SPECS`, aucun routage par couche Vue/Métier/Persistance n'existe) ; les sections suivantes **ne sont pas renumérotées** (16, 17, 18 restent 16, 17, 18) pour préserver les références croisées existantes. Le **§14 est entièrement réécrit** et recadré « Délégation Chef → Ouvrier (changement d'environnement) » : on ne garde que l'usage réel validé — un CCL « chef » crée lui-même une issue « ouvrier » ciblant un autre environnement (typiquement CCL Linux → CCW Windows) via `gh issue create` et surveille sa fermeture avant de livrer, sur instruction explicite (pas de détection auto du rôle chef, pas de décomposition automatique générique) — avec conseil de `TIMEOUT` généreux côté chef et l'exemple validé du build Scrabble/ouvrier CCW. En complément, l'issue chef #207 délègue à 6 issues « ouvrier » (une par projet actif hors bridge_agent et ff_galerie) la suppression des fichiers `CONTEXTE_VUE.md`/`CONTEXTE_METIER.md`/`CONTEXTE_PERSISTANCE.md` — vestiges du §15 abandonné — `CONTEXTE.md` (mécanisme standard hors MVC) étant conservé partout. Précédemment — §18 (nouveau) « Pièces jointes image dans les issues » (issue #191) : l'onglet « Nouvelle issue » accepte désormais un **upload optionnel PNG/JPEG** (champ fichier + bouton « Joindre une image » à côté du corps). Nouvelle route **`POST /joindre-image`** (`app/issues.py`, `joindre_image()`) : valide le type (Content-Type **et** magic bytes) et la taille (**≤ 5 Mo**), sauvegarde dans **`issue-attachments/`** (racine du `REP_TRAVAIL`) sous un nom **horodaté** anti-collision (`AAAAMMJJ-HHMMSS-<nom>.ext`), puis `git add` + `commit` + **`git push origin HEAD:<branche>`** (branche déduite **dynamiquement**, jamais supposée master/main), et retourne l'URL **`raw.githubusercontent.com/<owner>/<repo>/<branche>/issue-attachments/<fichier>`** — format qui s'affiche correctement dans les issues GitHub. Le frontend (`static/js/app.js`, `joindreImage()`/`insererDansCorps()`) insère alors **automatiquement** `![<nom>](<url>)` dans le corps à la position du curseur. **Exception `push` assumée et documentée (§18.2)** : ce commit+push est déclenché par **ALAIN** via l'outil (son action manuelle), **pas par CCL/le watcher** — la règle « CCL ne pousse jamais » n'est donc pas violée (elle vise les modifications de code de l'agent, pas une image qu'Alain publie lui-même). Gestion d'erreurs (§18.4) : **push échoué → aucune URL insérée** (commit conservé en local, poussable plus tard), **projet sans dépôt git → message clair**, type/taille/contenu invalides refusés proprement. `issue-attachments/` volontairement **hors `.gitignore`** (les images doivent être suivies/poussées). Testé de bout en bout (dépôt jetable + remote bare : succès + URL correcte, et chemins d'échec type/taille/magic/push). Précédemment — §17 (nouveau) « Notifications centralisées — détection serveur des transitions » (issue #187) : `new_issue.py`, qui tourne en permanence sur le ThinkPad, détecte désormais LUI-MÊME par polling `gh` les transitions d'issues (fermeture `done` = succès ; label `needs-human` = échec définitif) de **tous** les projets (for-linux ET for-windows), et déclenche bip/`notify-send`/`ntfy` **localement**, y compris pour les issues traitées par la VM **CCW** — **sans aucun appel réseau initié par la VM** (la VM n'écrit que sur GitHub). Nouveau module partagé `notifications.py` (racine) factorisant `bip`/`notifier_bureau`/`notifier_ntfy`/`notifier`, importé par `watcher.py` (enveloppes minces déléguant, sites d'appel inchangés) ET par le nouveau poller `app/notifications_poller.py` (thread démon lancé par `new_issue.py`). Script bip **déplacé/recréé** de `~/NicLink/bip.py` vers `scripts/bip.py` (infrastructure partagée) ; défaut `SCRIPT_BIP` et `configs/*.conf` mis à jour. Anti-doublon (point 4) : réglage `NOTIFIER_LOCAL` (`.conf`, défaut `true`) coupant la notif du watcher + portée `BRIDGE_NOTIF_SCOPE` (env, défaut `for-windows`) du poller. **Défaut livré sans régression ni doublon** (CCL notifie via son watcher, CCW via le poller — variante propre de l'option b) ; **option (a) « centralisation complète » recommandée mais laissée au choix d'Alain** car elle fait de `new_issue.py` une dépendance dure de toute notification (or il n'a pas encore de service systemd) — implémentée et à un réglage près (`BRIDGE_NOTIF_SCOPE=all` + `NOTIFIER_LOCAL=false` partout). **Action requise côté VM CCW** : poser `NOTIFIER_LOCAL=false` dans `configs\*-ccw.conf` pour éviter un double `ntfy`. Bonus (point 5) : le poller lit les labels COURANTS à la fermeture, donc `notif_pc`/`notif_gsm` ajouté EN COURS de traitement est bien pris en compte. Filtre de récence (`BRIDGE_NOTIF_RECENCE_MIN`, défaut 30 min) + amorçage silencieux au 1er cycle évitent le spam de vieilles issues au démarrage ; état en mémoire process. Précédemment — §1 « Vue d'ensemble » : documentation du **`git pull --ff-only` automatique en début de cycle** de `watcher.py` (issue #186, suite du #185 qui l'a implémenté). Le watcher rafraîchit son clone (`REP_TRAVAIL`) au début de chaque cycle de polling, juste avant `lister_issues()` : fast-forward transparent en cas de succès ; en cas de commits locaux non poussés (divergence) le `--ff-only` échoue proprement sans RIEN écraser et le watcher poursuit sur le code local — donc aucun risque à oublier un `git push`. Comportement **identique CCL (Linux) et CCW (Windows)** puisque `watcher.py` est le script unique partagé ; les projets à périmètre dynamique (dépôt-cible par issue) ne sont pas concernés. Un `git pull`/relance manuel reste possible pour une mise à jour immédiate (confort, plus une nécessité). Aucune instruction obsolète de « git pull manuel obligatoire » à corriger dans le §16 (aucune ne subsistait). Précédemment — §16 « Agent Windows CCW » : **onglet « CCW » dans l'interface web** (issue #174, sous-section §16.2) — pilotage complet de la VM et des projets CCW depuis Linux, sans PowerShell manuel dans la VM. Backend `app/ccw.py` (routes `/ccw/*`) exécutant les scripts existants à distance via `VBoxManage guestcontrol` : état/démarrage de la VM (`demarrer_ccw.sh`), liste des projets (nouveau `lister_projets_ccw.ps1`, sortie JSON encadrée), ajout (`ajouter_projet_ccw.ps1`) et finalisation non interactive (nouveau `finaliser_projet_ccw_auto.ps1` + `mettre_a_jour_tokens_ccw.ps1` doté d'un mode `-FichierTokens`). Sécurité : tokens jamais passés en argument ni journalisés (fichier temporaire `0600` poussé puis supprimé des deux côtés dans un `finally`) ; mot de passe `ccw-admin` lu depuis `CCW_ADMIN_PASSWORD` ou `configs/ccw_admin.secret` (gitignoré). Nouvel onglet + panneau dans `templates/index.html`, fonctions `ccw*` dans `static/js/app.js`, classe `.message.avertissement` dans `style.css`. Précédemment — §16 « Agent Windows CCW » : **finalisation d'un projet CCW en une seule commande** (issue #173, suite #170) — ajout de `provisioning/windows/finaliser_projet_ccw.ps1` qui, à partir du seul `-NomProjet`, dérive le service/dossier/config (même logique qu'`ajouter_projet_ccw.ps1`), vérifie leur existence, demande `TOPIC_NTFY` et l'écrit directement dans le config (remplacement ciblé du placeholder `###TOPIC_NTFY_A_DEFINIR###`, reste du fichier préservé en UTF-8 sans BOM), rappelle avec une pause la marche à suivre pour créer le token GitHub dédié, puis **appelle** `mettre_a_jour_tokens_ccw.ps1` (pas de duplication) pour la saisie masquée + pose des tokens + redémarrage + vérif des logs, et conclut par un résumé ; `mettre_a_jour_tokens_ccw.ps1` gagne un paramètre `-NomLog` pour vérifier le bon log de service (`ccw-<nom>-service.log`) ; les rappels d'`ajouter_projet_ccw.ps1` (en-tête + fin de script) et le §16 pointent désormais vers cette commande unique au lieu des 3 étapes dispersées. Non exécuté contre une VM réelle (test manuel par Alain). Précédemment — §11 « Conventions de code » : **règle BOM UTF-8 obligatoire pour tout script `.ps1`** (issue #172) — ajout du BOM (`EF BB BF`) manquant sur `ajouter_projet_ccw.ps1` (#170) et `mettre_a_jour_tokens_ccw.ps1` (#168), qui plantaient sinon sous Windows PowerShell 5.1 avec des `UnexpectedToken` en cascade sur les accents (même signature que #151) ; règle généralisée en §11 + rappel en tête du §16 pour prévenir la récidive (`provisionner.ps1` déjà OK depuis #151). Précédemment — §16 « Agent Windows CCW » : **généralisation multi-projets de CCW** (issue #170) — ajout de `provisioning/windows/ajouter_projet_ccw.ps1` (un clone + un config `configs\<nom>-ccw.conf` + un service NSSM `CCW-Watcher-<NomProjet>` dédiés par projet, sur le modèle des watchers CCL ; paramétrable `-NomProjet`/`-Depot`, idempotent, `watcher.py` inchangé) ; documentation du modèle « un service par projet » et de la **règle d'expiration alignée** des tokens (un token fine-grained dédié par dépôt, mais tous à la même échéance ≈ 17 octobre 2026) ; commande exacte d'instanciation de Scrabble et marche à suivre pour créer son token dédié (Repository access → Scrabble uniquement, Issues read/write + Metadata read-only). Précédemment — §16 « Agent Windows CCW » : ajout de la sous-section **§16.1 Maintenance périodique (renouvellement à 90 jours)** (issue #169) — runbook séquentiel consolidé pour la fenêtre de maintenance d'octobre 2026 : tableau de repères de dates (install **2026-07-19**, expiration Windows **2026-10-17**, token GitHub aligné ~90 j mais non stocké), puis procédure en 3 étapes renvoyant aux scripts existants — vérifier (`verifier_expiration_ccw.py`), recréer la VM (`creer_vm_ccw.py --recreate` + ré-attacher un ISO frais + `lancer_provisioning.py`), renouveler les tokens (`mettre_a_jour_tokens_ccw.ps1`) — sans dupliquer le détail technique déjà présent dans le §16. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/mettre_a_jour_tokens_ccw.ps1` (issue #168) — renouvellement des tokens `GH_TOKEN`/`CLAUDE_CODE_OAUTH_TOKEN` du service `CCW-Watcher` sans reconstruire à la main la chaîne `AppEnvironmentExtra` : saisie masquée (`Read-Host -AsSecureString`), séparateur `` `n`` impératif entre les deux paires (un espace corrompt `GH_TOKEN` → « Bad credentials »), `nssm set`/`nssm restart`, puis affichage automatique des 10 dernières lignes de `logs\ccw-service.log` pour confirmer l'absence d'erreur d'auth. Précédemment — §16 « Agent Windows CCW » : alerte d'expiration de l'éval 90 jours (issue #167) — ajout de `provisioning/windows/eval-expiration.json` (date d'installation **2026-07-19**, expiration **2026-10-17**) et du script `provisioning/windows/verifier_expiration_ccw.py` (côté Linux : calcule les jours restants, alerte + code de sortie 2 à ≤ 10 j, sinon confirmation calme ; `python3 provisioning/windows/verifier_expiration_ccw.py`) ; rappel `cron` + `ntfy` hebdomadaire proposé mais laissé à l'activation d'Alain. Précédemment — §16 « Agent Windows CCW » : ajout du script `provisioning/windows/demarrer_ccw.sh` (issue #166), wrapper de démarrage de la VM `CCW-Build` depuis CCL (headless par défaut, `--gui`/`--fenetre` pour une fenêtre, `--status` pour l'état sans rien démarrer). Précédemment — §3 « Créer une issue » : ajout d'une note sur la **convention de présentation côté Claude Chat** pour l'envoi en lot (issue #153) — quand Claude Chat prépare plusieurs issues, il les présente toutes à la suite dans un seul bloc de code (pas un bloc par issue) pour un copier-coller en un clic. Précédemment — §16 « Agent Windows CCW » : `REP_TRAVAIL` généré par `provisionner.ps1` pointe désormais vers le **chemin UNC** `\\VBOXSVR\CCW_Share` (et non la lettre automontée `$LettrePartage`), seul accessible au service `CCW-Watcher` tournant sous LocalSystem (issue #149, suite #148) ; `$LettrePartage` conservé pour référence mais plus utilisé pour construire `REP_TRAVAIL`. Précédemment — le watcher CCW tourne comme **vrai service Windows** enregistré via NSSM (issue #148, suite #147) — `provisionner.ps1` installe `NSSM.NSSM` (winget) et enregistre le service `CCW-Watcher` (`SERVICE_AUTO_START` + `AppExit Default Restart` + `AppRestartDelay 5000`, stdout/stderr → `logs\ccw-service.log`, idempotent via `nssm stop`/`remove`), en remplacement de l'ancienne tâche planifiée `-AtLogOn` qui ne redémarrait pas au boot sans session ; équivalent direct des services systemd du §13. Précédemment — provisioning **phase 2** (issue #147, suite #146) — ajout de `provisioning/windows/provisionner.ps1` (installe l'outillage dans la VM via winget + Claude Code natif, clone le dépôt, écrit `ccw.conf`, enregistre la tâche planifiée `CCW-Watcher`) et `lancer_provisioning.py` (pousse/exécute ce script depuis CCL via `VBoxManage guestcontrol`) ; `watcher.py` inchangé (portable, `LABEL` paramétrable) ; limite Task Scheduler vs `Restart=always` documentée. Précédemment — ajout du §16 et du label `for-windows` (issue #146) : provisioning phase 1 de la VM Windows CCW (`provisioning/windows/creer_vm_ccw.py` + `autounattend.xml`) destinée aux builds .exe délégués par CCL. Précédemment — Bridge_Agent v1, 4 projets actifs. §3 « Créer une issue » : ajout de l'**envoi en lot** (issue #135) — coller plusieurs blocs `#Titre:` à la suite dans le même corps déclenche le mode lot (bouton « Envoyer le lot (N issues) »), chaque bloc étant envoyé en séquence comme une issue indépendante (avec ses `PROJET`/`TIMEOUT`/`MODELE` optionnels), sans validation intermédiaire, suivi d'un résumé listant le résultat de chacune. Ajout du projet `ecole` (AlainDelree/Ecole, ~/Ecole) aux tableaux §2 et §7 (issue #101). Section 15 « Chef + Specs MVC » : champ `SPECS` (pluriel, minuscules, combinable en une ligne) — correction du champ `SPEC` introduit par erreur (issue #97, suite #96).*
# (diff du fichier suivant)
diff --git a/tests/test_auto_extinction_217.py b/tests/test_auto_extinction_217.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..0cd2bd2
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_auto_extinction_217.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (212 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,212 @@
+#!/usr/bin/env python3
+"""Test de non-régression — issue #217.
+
+Vérifie que l'auto-extinction du watcher (issue #200) ne se déclenche PAS
+immédiatement après un traitement réel, même si ce traitement s'est étiré
+au-delà du délai d'inactivité (plusieurs timeouts/retries en cascade), et
+qu'elle se déclenche bien lorsque plus rien n'est traitable.
+
+Le test pilote le VRAI `watcher.main()` avec une horloge monotone mockée
+(`time.monotonic` / `time.sleep` patchés) et des `lister_issues` /
+`traiter_issue` scriptés. Il reproduit le scénario du log réel
+`watcher-scrabble.log` (24/07/2026) : une issue détectée, traitement long
+(~23 min > délai 20 min) avec succès, puis vérification que le watcher
+poursuit son cycle au lieu de s'éteindre « aussitôt après le succès ».
+
+Exécution :  python3 tests/test_auto_extinction_217.py
+Sortie      :  code 0 si tous les scénarios passent, 1 sinon.
+
+Régression historique : avec le code d'AVANT #217 (réarmement de
+`derniere_activite` uniquement AVANT le traitement, jamais après), le
+scénario 1 provoquait `sys.exit(0)` dès le 2ᵉ cycle — soit une extinction
+14 s après un succès réel. Ce test échoue sur ce code et passe sur le code
+corrigé.
+"""
+
+import sys
+import tempfile
+from pathlib import Path
+from unittest import mock
+
+# Le test vit dans tests/ ; le module watcher.py est à la racine du projet.
+RACINE = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(RACINE))
+
+import watcher  # noqa: E402
+
+
+class StopLoop(Exception):
+    """Sentinelle : simule le sys.exit(0) de l'extinction pour rompre la boucle
+    infinie de main() sans tuer le process de test."""
+
+
+def _issue(numero, traitable=True):
+    """Fabrique une issue minimale. traitable=False => label 'done' (ignorée
+    par issue_traitable, comme une issue déjà finalisée)."""
+    labels = [] if traitable else [{"name": watcher.LABEL_FAIT}]
+    return {"number": numero, "title": f"issue #{numero}", "body": "", "labels": labels}
+
+
+def _ecrire_conf(rep_travail: Path) -> Path:
+    """Écrit un .conf minimal valide dans un fichier temporaire."""
+    conf = tempfile.NamedTemporaryFile(
+        mode="w", suffix=".conf", delete=False, encoding="utf-8"
+    )
+    conf.write(
+        "NOM = test_ext_217\n"
+        "DEPOT = exemple/depot-test\n"
+        f"REP_TRAVAIL = {rep_travail}\n"
+        "TOPIC_NTFY = test-topic\n"
+        "INTERVALLE = 1\n"
+        "DELAI_INACTIVITE_MIN = 20\n"
+    )
+    conf.close()
+    return Path(conf.name)
+
+
+def executer_scenario(plan, sleeps, long_proc_s=1380.0, cap=40):
+    """Exécute watcher.main() sur un scénario scripté et renvoie un rapport.
+
+    plan       : liste de listes d'issues renvoyées par lister_issues(),
+                 une entrée par cycle (au-delà => [] pour toujours).
+    sleeps     : liste des avances d'horloge appliquées par chaque time.sleep()
+                 (une par cycle ; au-delà => dernière valeur répétée).
+    long_proc_s: durée simulée du traitement d'UNE issue traitable (avance
+                 d'horloge dans traiter_issue). 1380 s = ~23 min > délai 20 min.
+    cap        : nombre max de cycles avant abandon (garde anti-boucle).
+
+    Renvoie {"exited": bool, "cycles_avant_exit": int|None}.
+    cycles_avant_exit = nombre de cycles (appels lister_issues) effectués
+    avant que l'extinction ne survienne.
+    """
+    horloge = {"t": 0.0}
+    compteur = {"lister": 0}
+    etat = {"exited": False, "cycles_avant_exit": None}
+
+    def fake_monotonic():
+        return horloge["t"]
+
+    def fake_sleep(_):
+        i = min(compteur["lister"] - 1, len(sleeps) - 1)
+        horloge["t"] += sleeps[i] if sleeps else 1.0
+
+    def fake_lister():
+        i = compteur["lister"]
+        compteur["lister"] += 1
+        if compteur["lister"] > cap:
+            # Garde-fou : si l'extinction ne survient jamais, on rompt.
+            raise StopLoop()
+        return plan[i] if i < len(plan) else []
+
+    def fake_traiter(issue, dry_run):
+        # Simule un traitement long (timeouts + retries en cascade) : seule une
+        # issue réellement traitable consomme du temps.
+        if watcher.issue_traitable(issue):
+            horloge["t"] += long_proc_s
+
+    def fake_exit(code=0):
+        etat["exited"] = True
+        etat["cycles_avant_exit"] = compteur["lister"]
+        raise StopLoop()
+
+    rep_travail = Path(tempfile.mkdtemp(prefix="rep_test_217_"))
+    conf = _ecrire_conf(rep_travail)
+
+    argv = ["watcher.py", "--config", str(conf)]
+    with mock.patch.object(watcher.time, "monotonic", fake_monotonic), \
+         mock.patch.object(watcher.time, "sleep", fake_sleep), \
+         mock.patch.object(watcher, "lister_issues", fake_lister), \
+         mock.patch.object(watcher, "traiter_issue", fake_traiter), \
+         mock.patch.object(watcher, "rafraichir_depot", lambda *a, **k: None), \
+         mock.patch.object(watcher.sys, "exit", fake_exit), \
+         mock.patch.object(watcher.sys, "argv", argv):
+        try:
+            watcher.main()
+        except StopLoop:
+            pass
+
+    conf.unlink(missing_ok=True)
+    return etat
+
+
+def scenario_1_traitement_long_puis_issue_restante():
+    """Reproduit le bug #217 : issue détectée, traitement de ~23 min (> 20 min),
+    succès, PUIS une autre issue reste traitable. Le watcher NE doit PAS
+    s'éteindre au cycle suivant le succès ; il doit poursuivre le travail."""
+    plan = [
+        [_issue(238)],   # cycle 1 : traitable → ~23 min de traitement
+        [_issue(239)],   # cycle 2 : une autre issue reste → ~23 min
+        [],              # cycle 3 : plus rien à traiter
+    ]
+    # Avances d'horloge de time.sleep() par cycle : ~intervalle pendant le
+    # travail, puis un long silence (2000 s) une fois inactif pour laisser
+    # l'horloge dépasser le délai et permettre l'extinction légitime.
+    sleeps = [1.0, 1.0, 2000.0]
+    rap = executer_scenario(plan, sleeps)
+
+    # AVEC le correctif : cycles 2 et 3 s'exécutent (le traitement long ne
+    # provoque pas d'extinction prématurée), l'extinction ne survient qu'au
+    # cycle 4, une fois réellement inactif.
+    # SANS le correctif : extinction dès le cycle 2 (cycles_avant_exit == 1).
+    assert rap["exited"], "Le watcher aurait dû finir par s'éteindre (inactif)."
+    assert rap["cycles_avant_exit"] >= 3, (
+        f"Extinction prématurée : survenue après seulement "
+        f"{rap['cycles_avant_exit']} cycle(s) — le traitement long a déclenché "
+        f"l'extinction alors qu'une issue restait traitable (bug #217 non corrigé)."
+    )
+    return rap
+
+
+def scenario_2_inactivite_reelle_declenche_extinction():
+    """Contrôle négatif : aucune issue traitable, l'horloge vieillit au-delà du
+    délai → l'extinction DOIT bien se déclencher (le correctif ne la neutralise
+    pas)."""
+    plan = [[]]  # jamais rien de traitable
+    sleeps = [2000.0]  # une seule attente > délai (1200 s) suffit
+    rap = executer_scenario(plan, sleeps)
+    assert rap["exited"], "Extinction attendue en inactivité réelle, absente."
+    return rap
+
+
+def scenario_3_issue_non_traitable_ne_bloque_pas():
+    """Une issue présente mais NON traitable (label 'done') ne doit pas empêcher
+    l'extinction : pas de travail réel → pas de réarmement."""
+    plan = [[_issue(300, traitable=False)]]
+    sleeps = [2000.0]
+    rap = executer_scenario(plan, sleeps)
+    assert rap["exited"], (
+        "Une issue non-traitable ('done') ne doit pas empêcher l'extinction."
+    )
+    return rap
+
+
+def main():
+    tests = [
+        ("traitement long puis issue restante (bug #217)",
+         scenario_1_traitement_long_puis_issue_restante),
+        ("inactivité réelle → extinction",
+         scenario_2_inactivite_reelle_declenche_extinction),
+        ("issue non-traitable → extinction non bloquée",
+         scenario_3_issue_non_traitable_ne_bloque_pas),
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
index 7d42a63..5195e81 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 1590 (7 ligne(s)) dans l'ancienne version → ligne 1590 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1590,7 +1590,8 @@ def main():
             # done, ni needs-human). On réarme AVANT le traitement : le cycle qui
             # suit ne testera l'inactivité qu'une fois ce traitement terminé, donc
             # un retry long n'est jamais interrompu (issue #200).
-            if any(issue_traitable(i) for i in issues):
+            travail_a_faire = any(issue_traitable(i) for i in issues)
+            if travail_a_faire:
                 derniere_activite = time.monotonic()
             if issues:
                 log.info(f"{len(issues)} issue(s) en attente.")
# ── Zone modifiée : ligne 1598 (6 ligne(s)) dans l'ancienne version → ligne 1599 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1598,6 +1599,20 @@ def main():
                     traiter_issue(issue, dry_run=args.dry_run)
             else:
                 log.debug("Aucune issue en attente.")
+            # Réarmement APRÈS traitement (issue #217). Le réarme d'avant-cycle
+            # (ci-dessus) date le DÉBUT du travail, pas sa fin : le traitement
+            # d'une (ou plusieurs) issue(s) peut s'étirer bien au-delà du délai
+            # d'inactivité — plusieurs timeouts de 300s + retries en cascade, cf.
+            # log watcher-scrabble 24/07/2026 : ~23 min pour une seule issue. Sans
+            # ce second réarme, l'horloge resterait « périmée » (figée au début du
+            # cycle) et le test d'extinction en tête du cycle SUIVANT se
+            # déclencherait immédiatement après un travail réel qui vient tout
+            # juste de se terminer (extinction ~14 s après un succès). On réarme
+            # donc de nouveau ICI, avec l'instant réel de fin de traitement, dès
+            # qu'au moins une issue traitable a été traitée ce cycle. L'extinction
+            # reste possible quand plus rien n'est traitable (le flag est faux).
+            if travail_a_faire:
+                derniere_activite = time.monotonic()
         except KeyboardInterrupt:
             log.info("Watcher arrêté par l'utilisateur.")
             sys.exit(0)
