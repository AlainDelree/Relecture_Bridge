3723897

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3723897
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 11:14:04 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Met à jour CONCEPTION.md : modèle instance unique partagée (issue #54)
    
    CONCEPTION.md documentait encore le modèle intermédiaire "instances
    séparées" (issue #4, un dossier Actualise par application cible) alors
    que le code a depuis évolué vers une instance unique partagée
    (C:\Actualise\), avec config_actualise.json + config_<app>.json et
    sélection via --config <nom> (issue #35), un module ActualiseUI.exe
    dédié au dialogue de mise à jour utilisateur (issue #36), et un
    installeur Actualise-Setup.exe séparé des setups des applications
    cibles (issue #44).
    
    Mis à jour après vérification du code réel (config.py, actualise.py,
    actualise_ui.py, installeur/actualise.iss) : sections "Configuration
    portable", "Intégration avec le setup.exe d'une application cible",
    table "Décisions actées", et "Points de vigilance connus" (ajout de
    l'historique instances séparées → instance unique partagée et de sa
    raison). INTEGRATION.md déjà à jour sur ce modèle, inchangé.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index aed4b83..5ed8b10 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 45 (7 ligne(s)) dans l'ancienne version → ligne 45 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -45,7 +45,8 @@ générer à chaque publication (incrémentation simple).
   lui-même.
 - Un `version.json` dans le **dépôt de chaque application cible** (ex.
   Scrabble) — l'URL de ce fichier est construite à partir des
-  informations du `config.json` local (dépôt GitHub cible).
+  informations du fichier `config_<nom_app>.json` local (dépôt GitHub
+  cible).
 
 Les deux logiques de mise à jour (Actualise vs application cible) sont
 **indépendantes** : chacune a son propre `build` courant, sa propre
# ── Zone modifiée : ligne 136 (48 ligne(s)) dans l'ancienne version → ligne 137 (78 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -136,48 +137,78 @@ supprimer » — un manifeste manquant est plus probablement le signe d'un
 problème de publication (asset incomplet, erreur de packaging) qu'une
 intention volontaire de l'auteur de la Release.
 
-## Contenu de `config.json`
+## Contenu des fichiers de configuration — `config_actualise.json` / `config_<nom_app>.json`
 
-Reprend la base déjà actée (version actuelle, dépôt GitHub cible,
-répertoire d'installation, chemin portable Linux/Windows) et y ajoute
-les champs nécessaires au fonctionnement complet décrit ci-dessus
-(vérification de version, distribution en zip, notifications) :
+**Historique** : la conception initiale (issues #3/#4/#7) prévoyait un
+`config.json` unique regroupant les deux blocs `actualise` et
+`application_cible`. Ce format à fichier unique a été **abandonné**
+(issue #35) au profit de **deux fichiers séparés**, dans le cadre du
+passage au modèle « instance unique partagée » décrit en
+« Configuration portable » ci-dessous — voir aussi « Points de
+vigilance connus » pour l'historique complet de ce changement. Le
+format ci-dessous est celui **actuellement chargé** par
+`config.charger_config(nom_app)`.
+
+**`config_actualise.json`** — un seul exemplaire, **partagé** par
+toutes les applications cibles gérées par cette installation
+d'Actualise :
 
 ```json
 {
-  "actualise": {
-    "build_installe": 12,
-    "depot_github": "AlainDelree/Actualise"
-  },
-  "application_cible": {
-    "nom": "Scrabble",
-    "depot_github": "AlainDelree/Scrabble",
-    "build_installe": 47,
-    "repertoire_installation": "C:\\Scrabble\\",
-    "executable": "Scrabble.exe",
-    "icone": "C:\\Scrabble\\Scrabble.ico"
-  },
-  "zone_attente": "C:\\Actualise\\attente\\",
+  "build_installe": 12,
+  "depot_github": "AlainDelree/Actualise",
+  "zone_attente": "C:\\Actualise\\attente\\"
+}
+```
+
+**`config_<nom_app>.json`** — un exemplaire **par application cible**
+(ex. `config_scrabble.json`, `config_rummikub.json`), `nom_app`
+correspondant à l'argument `--config <nom>` passé à Actualise (voir
+« Configuration portable ») :
+
+```json
+{
+  "nom": "Scrabble",
+  "depot_github": "AlainDelree/Scrabble",
+  "build_installe": 47,
+  "repertoire_installation": "C:\\Scrabble\\",
+  "executable": "Scrabble.exe",
+  "icone": "C:\\Scrabble\\Scrabble.ico",
   "topic_ntfy": "actualise-scrabble"
 }
 ```
 
+`config.charger_config(nom_app)` lit les deux fichiers et les fusionne
+en un seul dict `{"actualise": ..., "application_cible": ...,
+"zone_attente": ..., "topic_ntfy": ...}`, compatible avec la structure
+déjà utilisée par le reste d'Actualise (`zone_attente` extrait de
+`config_actualise.json`, `topic_ntfy` copié depuis
+`application_cible` par commodité pour l'appelant). L'absence de l'un
+ou l'autre fichier, ou un JSON malformé, reste **bloquant** :
+`FileNotFoundError`/`json.JSONDecodeError` remontent telles quelles,
+sans repli silencieux (cohérent avec le choix déjà acté pour l'ancien
+`config.json` unique).
+
 Détail des champs :
 
-- `build_installe` (sous `actualise` **et** sous `application_cible`,
-  séparément) : le numéro de build actuellement installé pour ce
-  programme, directement comparable au champ `build` du `version.json`
-  correspondant (voir « Format de version »).
-- `depot_github` (sous `actualise` **et** sous `application_cible`) :
-  sert à construire l'URL du `version.json` correspondant (voir « Deux
-  fichiers `version.json` distincts »).
-- `executable` : nom/chemin du fichier exécutable à lancer pour
-  l'application cible, une fois la bascule éventuelle effectuée (étape
-  3 de la « Séquence de démarrage »).
-- `repertoire_installation` : dossier cible pour l'extraction du zip de
-  mise à jour de l'application cible.
-- `icone` (sous `application_cible` uniquement, **optionnel**) : chemin
-  vers le fichier `.ico` de l'application cible, déployé par le setup de
+- `build_installe` (dans `config_actualise.json` **et** dans
+  `config_<nom_app>.json`, séparément) : le numéro de build
+  actuellement installé pour ce programme, directement comparable au
+  champ `build` du `version.json` correspondant (voir « Format de
+  version »).
+- `depot_github` (dans `config_actualise.json` **et** dans
+  `config_<nom_app>.json`) : sert à construire l'URL du `version.json`
+  correspondant (voir « Deux fichiers `version.json` distincts »).
+- `executable` (dans `config_<nom_app>.json`) : nom/chemin du fichier
+  exécutable de l'application cible, une fois la bascule éventuelle
+  effectuée (étape 3 de la « Séquence de démarrage »).
+- `repertoire_installation` (dans `config_<nom_app>.json`) : dossier
+  cible pour l'extraction du zip de mise à jour de l'application
+  cible ; c'est aussi dans ce dossier — celui de l'application cible,
+  pas celui d'Actualise — qu'est écrit `actualise_update.flag` (voir
+  section dédiée à `ActualiseUI.exe` ci-dessous).
+- `icone` (dans `config_<nom_app>.json`, **optionnel**) : chemin vers
+  le fichier `.ico` de l'application cible, déployé par le setup de
   cette application à un emplacement connu (ex. à côté de son
   exécutable). Ce champ est **informationnel/documenté pour Actualise**
   — Actualise n'a pas d'interface graphique et ne le lit **pas** au
# ── Zone modifiée : ligne 185 (67 ligne(s)) dans l'ancienne version → ligne 216 (78 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -185,67 +216,78 @@ Détail des champs :
   cible : le même chemin `.ico` doit être utilisé à la fois pour ce
   champ et pour le champ `IconFilename` du raccourci créé par ce setup
   (voir « Intégration avec le setup.exe d'une application cible »),
-  afin que la documentation de `config.json` reste cohérente avec
-  l'icône réellement affichée par le raccourci.
-- `zone_attente` : chemin du dossier où sont stockés les zip
-  téléchargés en arrière-plan avant bascule au lancement suivant —
-  commun à Actualise et à l'application cible. Ceci referme le point
-  resté ouvert dans « Points encore ouverts » sur l'emplacement de la
-  zone d'attente locale.
-- `topic_ntfy` : topic ntfy dédié à ce programme, cohérent avec la
-  décision actée « un topic ntfy dédié par programme géré » (voir
-  « Décisions actées »). **Cas particulier Scrabble** : pour ce projet
-  spécifiquement, `topic_ntfy` réutilise le topic déjà existant des
-  notifications d'issues fermées de Bridge_Agent pour Scrabble — pas de
-  topic dédié séparé créé, car seul Alain est abonné aux deux flux et le
-  préfixe `"MAJ - "` (voir « Décisions actées ») suffit à distinguer
-  visuellement les notifications d'Actualise des notifications de
-  clôture d'issue dans le même flux. Le principe général « un topic
-  ntfy dédié par programme géré » reste la règle par défaut pour de
-  futurs projets ayant un public destinataire différent (ex. un autre
-  utilisateur final abonné) ; Scrabble est un cas particulier documenté
-  comme tel, pas un changement de règle générale.
-
-`repertoire_installation` et `zone_attente` suivent la même logique de
-portabilité déjà actée pour `config.json` lui-même : `zone_attente` est
-un sous-dossier du dossier de configuration d'Actualise, donc résolu
-relativement à celui-ci (ex. `C:\Actualise_Scrabble\attente\` si
-Actualise a été installé dans `C:\Actualise_Scrabble\` — voir
-« Configuration portable » ci-dessous), tandis que
+  afin que la documentation de `config_<nom_app>.json` reste cohérente
+  avec l'icône réellement affichée par le raccourci.
+- `zone_attente` (dans `config_actualise.json` uniquement) : chemin du
+  dossier où sont stockés les zip téléchargés en arrière-plan avant
+  bascule au lancement suivant — **commun** à Actualise et à toutes les
+  applications cibles gérées par cette installation, cohérent avec le
+  fait qu'il n'existe plus qu'une seule installation d'Actualise à
+  gérer (voir « Configuration portable »).
+- `topic_ntfy` (dans `config_<nom_app>.json`) : topic ntfy dédié à ce
+  programme, cohérent avec la décision actée « un topic ntfy dédié par
+  programme géré » (voir « Décisions actées »). **Cas particulier
+  Scrabble** : pour ce projet spécifiquement, `topic_ntfy` réutilise le
+  topic déjà existant des notifications d'issues fermées de
+  Bridge_Agent pour Scrabble — pas de topic dédié séparé créé, car seul
+  Alain est abonné aux deux flux et le préfixe `"MAJ - "` (voir
+  « Décisions actées ») suffit à distinguer visuellement les
+  notifications d'Actualise des notifications de clôture d'issue dans
+  le même flux. Le principe général « un topic ntfy dédié par programme
+  géré » reste la règle par défaut pour de futurs projets ayant un
+  public destinataire différent (ex. un autre utilisateur final
+  abonné) ; Scrabble est un cas particulier documenté comme tel, pas un
+  changement de règle générale.
+
 `repertoire_installation` reste un chemin propre à l'application cible
-(ex. `C:\Scrabble\`), équivalent portable pour Linux (ex.
-`~/.config/actualise/` ou variable d'environnement).
+(ex. `C:\Scrabble\`), indépendant du dossier d'Actualise lui-même
+(ex. `C:\Actualise\`) — équivalent portable pour Linux (ex.
+`~/.config/actualise/` ou variable d'environnement) ; `zone_attente`,
+elle, est désormais toujours un sous-dossier du dossier de
+configuration **partagé** d'Actualise (voir « Configuration portable »
+ci-dessous), plus jamais un sous-dossier d'une installation propre à
+une application cible.
 
 ## Configuration portable
 
-Le dossier de configuration d'Actualise (celui qui contient
-`config.json`, ainsi que la zone d'attente) n'est **pas** un chemin
-Windows fixe codé en dur (ex. `C:\Actualise\`). Il est résolu **au
+**Modèle actuel : instance unique partagée.** Actualise n'est plus
+installé une fois par application cible : une **seule** installation
+d'Actualise (`Actualise.exe`, son dossier `_internal\`, et
+`ActualiseUI.exe`), dans un **dossier partagé et fixe**,
+`C:\Actualise\`, gère toutes les applications cibles présentes sur la
+machine (ex. Scrabble **et** Rummikub à la fois). Chaque application
+cible sait laquelle elle est en passant l'argument obligatoire
+`--config <nom>` (ex. `--config scrabble`) à `Actualise.exe`, qui
+détermine le nom du fichier `config_<nom>.json` à charger (voir
+« Contenu des fichiers de configuration » ci-dessus) — c'est ce
+fichier de configuration par application, et non plus un dossier
+d'installation séparé, qui isole les applications cibles les unes des
+autres.
+
+Techniquement, `config.chemin_config_portable()` résout ce dossier **au
 runtime, relativement à l'emplacement de l'exécutable `Actualise.exe`
 lui-même** : le dossier qui le contient, obtenu via `sys.executable` en
-mode PyInstaller figé (`sys.frozen`).
-
-**Raison de ce choix** : plusieurs applications cibles (ex. Scrabble et
-Rummikub) peuvent être installées indépendamment sur la même machine,
-chacune avec sa propre installation d'Actualise. Si le dossier de
-configuration était un chemin fixe unique, une seconde installation
-d'Actualise écraserait silencieusement le `config.json` de la première,
-lui faisant perdre la gestion de mise à jour de sa propre application
-cible (voir « Points de vigilance connus »). En résolvant ce dossier
-relativement à l'exécutable, chaque installation reste isolée dans son
-propre dossier, choisi indépendamment par le setup de chaque
-application cible, sans risque de collision.
-
-Sous Windows, le dossier concret dépend donc du setup de chaque
-application cible (ex. `C:\Actualise_Scrabble\` pour Scrabble,
-`C:\Actualise_Rummikub\` pour Rummikub — voir « Intégration avec le
-setup.exe d'une application cible »), et non plus systématiquement
-`C:\Actualise\`. Sous Linux, le comportement reste inchangé
-(`~/.config/actualise/` ou variable d'environnement) : l'exécutable
-Linux n'étant pas installé par un setup Windows par application, la
+mode PyInstaller figé (`sys.frozen`) — ce mécanisme de résolution n'a
+**pas changé** depuis la conception initiale (issue #4). Ce qui a
+changé, c'est la **convention de déploiement** : `Actualise.exe`
+n'étant plus installé qu'une seule fois, à un emplacement fixe
+(`C:\Actualise\`, imposé par le setup dédié — voir « Intégration avec
+le setup.exe d'une application cible »), cette résolution relative
+pointe désormais systématiquement vers ce même dossier partagé, quelle
+que soit l'application cible qui a lancé Actualise. En mode script non
+figé (développement/tests), repli sur `%SYSTEMDRIVE%\Actualise\`.
+
+Sous Linux, le comportement reste inchangé (`~/.config/actualise/` ou
+variable d'environnement `ACTUALISE_CONFIG_DIR`) : l'exécutable Linux
+n'étant pas installé par un setup Windows par application, la
 problématique de collision multi-installations ne s'y pose pas de la
 même façon.
 
+Voir « Points de vigilance connus » pour l'historique du modèle
+intermédiaire « instances séparées » (un dossier Actualise par
+application cible, ex. `C:\Actualise_Scrabble\`) qui a précédé ce
+modèle et la raison de son abandon.
+
 ## Vérification réseau — timeout strict
 
 Toute requête HTTP de vérification de version (`version.json`, Actualise
# ── Zone modifiée : ligne 344 (9 ligne(s)) dans l'ancienne version → ligne 386 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -344,9 +386,9 @@ lancement et n'est effective qu'au lancement suivant.
 Convention de nommage dans `zone_attente` : `<préfixe>_<build>.zip` (ex.
 `actualise_48.zip`, `scrabble_112.zip`). Le préfixe identifie à qui
 appartient le zip (`actualise`, ou le nom de l'application cible tel
-que défini dans `config.json`) ; le numéro de build permet la
-comparaison directe avec le `build_installe` correspondant de
-`config.json` (voir « Contenu de `config.json` ») sans avoir à ouvrir
+que défini dans `config_<nom_app>.json`) ; le numéro de build permet la
+comparaison directe avec le `build_installe` correspondant (voir
+« Contenu des fichiers de configuration ») sans avoir à ouvrir
 le zip ni consulter un fichier séparé.
 
 Comportement au démarrage, **avant bascule** (étape 3 de la séquence
# ── Zone modifiée : ligne 452 (71 ligne(s)) dans l'ancienne version → ligne 494 (129 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -452,71 +494,129 @@ Pour Actualise lui-même, la bascule suit désormais ce mécanisme :
    suivant, sans faire planter `main()` — traitement cohérent avec les
    autres cas limites déjà en place (manifeste absent, zip corrompu).
 
+## ActualiseUI.exe — dialogue de mise à jour côté utilisateur final
+
+Module ajouté (issue #36) en complément de la bascule silencieuse
+décrite ci-dessus, pour le même problème de fond (le verrou Windows sur
+`_internal\`/`Actualise.exe` pendant qu'Actualise tourne, voir
+« Garde-fou anti-boucle infinie ») mais en donnant cette fois la main à
+l'utilisateur final plutôt qu'en l'appliquant silencieusement. C'est un
+**exécutable séparé**,
+`ActualiseUI.exe` (`actualise_ui.py`, compilé en `--onefile` via
+`actualise_ui.spec`), jamais importé par `actualise.py` : une petite
+fenêtre tkinter (« Mettre à jour » / « Plus tard »), sans dépendance
+externe, dont le seul rôle est de présenter le choix à l'utilisateur
+final et de déclencher un `.bat` généré par Actualise.
+
+Déroulé :
+
+1. Dès que la tâche de fond (« Séquence de démarrage », étape 2) détecte
+   et télécharge une nouvelle version d'**Actualise lui-même**, elle
+   génère immédiatement, en plus du zip placé en zone d'attente :
+   - `updater.bat`, dans le dossier partagé d'Actualise
+     (`C:\Actualise\`) — script qui effectue la bascule réelle
+     (renommage de `_internal\`/`Actualise.exe` en `.old`, extraction du
+     zip, nettoyage) ;
+   - `actualise_update.flag`, un JSON déposé dans le
+     `repertoire_installation` de **l'application cible** (pas dans le
+     dossier d'Actualise), contenant les chemins vers `ActualiseUI.exe`
+     et vers `updater.bat`.
+2. L'application cible (voir INTEGRATION.md, §6, pour le code exact à
+   intégrer une fois pour toutes) détecte ce flag à son propre
+   démarrage et lance `ActualiseUI.exe --bat ... --flag ... --relancer
+   <son propre exécutable>`, qui affiche la fenêtre de choix.
+   - **« Mettre à jour »** : supprime le flag, lance `updater.bat` (qui
+     relance l'application cible une fois la bascule terminée, via
+     `--relancer`), ferme la fenêtre.
+   - **« Plus tard »** : ferme simplement la fenêtre, flag conservé —
+     le choix sera reproposé au prochain démarrage.
+3. À la **fermeture** de la fenêtre principale de l'application cible,
+   si le flag existe encore (mise à jour jamais validée via la
+   fenêtre), l'application cible lance directement `updater.bat` (sans
+   fenêtre, sans demander confirmation) avant de se fermer. Ceci
+   garantit que la mise à jour d'Actualise finit **toujours** par
+   s'appliquer — au plus tard à la prochaine fermeture normale de
+   l'application cible — même si l'utilisateur ignore systématiquement
+   la fenêtre de choix.
+4. Tant que ce flag existe, `appliquer_mises_a_jour_en_attente` (étape
+   3 de la « Séquence de démarrage ») **saute** la bascule silencieuse
+   par renommage pour Actualise : `ActualiseUI.exe`/`updater.bat` a
+   alors la main exclusive, pour éviter une double bascule concurrente.
+   La bascule silencieuse par renommage (garde-fou anti-boucle
+   infinie ci-dessus) reste le mécanisme de **repli** : si le flag/bat
+   n'a pas pu être généré (`OSError`), Actualise applique la mise à
+   jour lui-même, sans interface, comme avant l'introduction
+   d'`ActualiseUI.exe`.
+
+Ce mécanisme concerne **exclusivement** la mise à jour d'Actualise
+lui-même : la mise à jour d'une application cible n'a jamais eu besoin
+de ce contournement (son exécutable n'est pas en cours d'exécution au
+moment de la bascule, voir « Garde-fou anti-boucle infinie »).
+
 ## Intégration avec le setup.exe d'une application cible
 
-Le `setup.exe` d'une application cible (ex. Scrabble) existe déjà et,
-dans sa forme actuelle, installe uniquement cette application (dossier
-propre, raccourcis Bureau/menu Démarrer pointant directement vers son
-exécutable). Son adaptation pour s'intégrer avec Actualise suit les
-principes suivants — formulés pour être réutilisables avec de futures
-applications cibles, Scrabble servant de premier exemple concret :
-
-1. **Installation dans un dossier séparé.** Actualise s'installe dans
-   son propre dossier, indépendant du dossier d'installation de
-   l'application cible — jamais à l'intérieur du dossier de
-   l'application cible. Ce découplage préserve la réutilisabilité
-   d'Actualise pour d'autres applications futures et sépare le cycle de
-   vie des deux installations : désinstaller l'application cible
-   n'entraîne pas nécessairement la désinstallation d'Actualise, qui
-   peut continuer à gérer d'autres programmes sur la même machine.
-
-   Le nom exact de ce dossier n'est **plus fixe** (ce n'est plus
-   systématiquement `C:\Actualise\`) : il est choisi par chaque setup
-   d'application cible, avec une **convention suggérée**
-   `C:\Actualise_<NomApplication>\` (ex. `C:\Actualise_Scrabble\`,
-   `C:\Actualise_Rummikub\`) pour éviter toute collision entre
-   applications cibles différentes installées sur la même machine (voir
-   « Configuration portable »).
-
-   Ce « propre dossier » d'Actualise **n'est pas distinct** de son
-   dossier de configuration : le répertoire d'installation d'Actualise
-   lui-même est exactement le dossier résolu par « Configuration
-   portable » — c'est-à-dire le dossier contenant `Actualise.exe`
-   lui-même, résolu relativement à l'exécutable via `sys.executable`,
-   pas un chemin codé en dur. `Actualise.exe`, son `config.json` et sa
-   zone d'attente cohabitent dans ce même dossier — il n'existe pas de
-   chemin d'installation séparé pour l'exécutable d'Actualise,
-   contrairement à l'application cible qui a son propre
-   `repertoire_installation` distinct dans `config.json`.
-2. **Raccourcis modifiés.** Les raccourcis Bureau et menu Démarrer créés
-   par le setup pointent vers `Actualise.exe` (dans son dossier séparé),
-   jamais directement vers l'exécutable de l'application cible —
-   conforme à la décision actée dès le « Principe de fonctionnement »
-   (« le raccourci ne doit jamais pointer directement vers l'application
-   cible »).
-
-   Ce raccourci pointant vers `Actualise.exe` afficherait par défaut
-   l'icône générique d'Actualise plutôt que celle de l'application
-   cible. Pour éviter cela, le setup de l'application cible **déploie
-   son propre fichier `.ico`** (ex. à côté de l'exécutable cible) et
-   l'utilise à la fois pour :
-   - le champ `IconFilename` du raccourci créé (Bureau/menu Démarrer),
-     qui continue de pointer vers `Actualise.exe` mais affiche l'icône
-     de l'application cible ;
-   - le champ `icone` du `config.json` généré par ce même setup, avec
-     **le même chemin** dans les deux cas, pour cohérence documentée
-     (voir « Contenu de `config.json` »).
-3. **Déploiement d'Actualise par le setup.** Le setup dépose désormais
-   `Actualise.exe` dans son dossier séparé, en plus des fichiers propres
-   à l'application cible.
-4. **Génération d'un `config.json` initial cohérent.** Le setup génère,
-   au moment de l'installation, un `config.json` reflétant les valeurs
-   réelles de cette installation : `build_installe` d'Actualise et de
-   l'application cible (versions effectivement embarquées dans ce
-   setup), `depot_github` des deux, `repertoire_installation` et
-   `executable` réels de l'application cible, `zone_attente`, et
-   `topic_ntfy` dédié à ce programme (voir « Contenu de `config.json` »
-   pour le format exact).
+Deux setups distincts coexistent désormais, avec des responsabilités
+disjointes (issue #44) — voir aussi INTEGRATION.md pour le guide
+pratique d'intégration complet, à jour sur ce modèle :
+
+1. **`Actualise-Setup.exe`** (`installeur/actualise.iss`) — installeur
+   dédié à Actualise lui-même, indépendant de toute application cible.
+   Il installe l'instance **partagée** dans un dossier **fixe et non
+   modifiable par l'utilisateur** (`DefaultDirName=C:\Actualise`,
+   `DisableDirPage=yes`), avec `PrivilegesRequired=admin` (`C:\` racine
+   du disque système, inaccessible en écriture aux utilisateurs
+   standards ; incident réel documenté avec `PrivilegesRequired=lowest`
+   — voir INTEGRATION.md). Il dépose les trois éléments constitutifs
+   d'Actualise :
+   - `Actualise.exe` ;
+   - `_internal\` (dossier complet, jamais l'exe seul — un `_internal\`
+     manquant provoque `Failed to load Python DLL`) ;
+   - `ActualiseUI.exe` (voir « ActualiseUI.exe » ci-dessus).
+
+   À l'installation (`ssPostInstall`), il crée `config_actualise.json`
+   **uniquement s'il n'existe pas déjà** : ce fichier étant partagé
+   entre toutes les applications cibles, l'écraser ferait perdre le
+   `build_installe`/`zone_attente` déjà à jour d'une installation
+   précédente. À la désinstallation, il supprime le dossier
+   `C:\Actualise\` **seulement si** aucun `config_<nom>.json` d'une
+   autre application cible n'y subsiste (recherche par motif
+   `config_*.json`, `config_actualise.json` exclu) — sinon il
+   désinstallerait Actualise sous des applications qui en dépendent
+   encore. Pas de raccourci créé par ce setup : Actualise n'est jamais
+   lancé directement par l'utilisateur (voir la décision actée « le
+   raccourci ne doit jamais pointer directement vers l'application
+   cible », qui reste — sous une forme adaptée — le raccourci pointe
+   toujours vers `Actualise.exe`, jamais vers l'application cible).
+
+2. **Le setup.exe de chaque application cible** (ex. Scrabble,
+   Rummikub) — **ne déploie plus** `Actualise.exe`/`_internal\`/
+   `ActualiseUI.exe` lui-même (ancien comportement, avant issue #44, où
+   chaque setup cible embarquait et réinstallait sa propre copie
+   d'Actualise). Son rôle se limite désormais à :
+   - déposer son propre `config_<nom>.json` dans `C:\Actualise\`
+     (jamais `config_actualise.json`, propriété exclusive du setup
+     Actualise) ;
+   - créer le raccourci Bureau/menu Démarrer pointant vers
+     `C:\Actualise\Actualise.exe --config <nom>` — jamais directement
+     vers l'exécutable de l'application cible (décision actée dès le
+     « Principe de fonctionnement ») ;
+   - déployer son propre fichier `.ico` et l'utiliser à la fois pour le
+     champ `IconFilename` du raccourci créé (qui pointe vers
+     `Actualise.exe` mais affiche l'icône de l'application cible) et
+     pour le champ `icone` de `config_<nom>.json` — même chemin dans
+     les deux cas, pour cohérence documentée (voir « Contenu des
+     fichiers de configuration »).
+
+   Ce découplage préserve la réutilisabilité d'Actualise pour de
+   futures applications cibles et sépare le cycle de vie des
+   installations : désinstaller une application cible ne désinstalle
+   pas nécessairement Actualise, qui continue de gérer les autres
+   programmes présents sur la machine (voir point 1 ci-dessus).
+
+Historique : voir « Points de vigilance connus » pour le détail complet
+du passage du modèle « instances séparées » (une installation
+d'Actualise par application cible, chacune avec son propre `config.json`
+et son propre dossier) à ce modèle à deux setups distincts.
 
 ## Décisions actées
 
# ── Zone modifiée : ligne 526 (9 ligne(s)) dans l'ancienne version → ligne 626 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -526,9 +626,9 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Comportement hors-ligne / échec réseau | Se rabat silencieusement sur le lancement de la version déjà installée, sans bloquer l'utilisateur final |
 | Raccourci utilisateur | Pointe vers Actualise, jamais directement vers l'application cible |
 | Configuration | Répertoire dédié type `C:\Actualise\` avec un fichier `config.json` reprenant : version actuelle de l'exe cible, dépôt GitHub cible, répertoire d'installation cible, et autres éléments à définir. Prévoir un chemin **portable** pour les tests/usage Linux (ex. `~/.config/actualise/` ou une variable d'environnement) en plus de `C:\Actualise\`, pour ne pas entamer la réutilisabilité Linux visée par le projet |
-| Notifications | Un topic ntfy dédié par programme géré (règle par défaut) ; notification informative envoyée quand une mise à jour a été téléchargée en arrière-plan (effective au prochain lancement), message préfixé par `"MAJ - "` pour se distinguer visuellement d'autres types de notifications pouvant partager le même topic ; **cas particulier Scrabble** : réutilise le topic existant des notifications d'issues fermées Bridge_Agent du projet Scrabble plutôt qu'un topic dédié séparé, car seul Alain est abonné aux deux flux — voir « Contenu de `config.json` » |
+| Notifications | Un topic ntfy dédié par programme géré (règle par défaut) ; notification informative envoyée quand une mise à jour a été téléchargée en arrière-plan (effective au prochain lancement), message préfixé par `"MAJ - "` pour se distinguer visuellement d'autres types de notifications pouvant partager le même topic ; **cas particulier Scrabble** : réutilise le topic existant des notifications d'issues fermées Bridge_Agent du projet Scrabble plutôt qu'un topic dédié séparé, car seul Alain est abonné aux deux flux — voir « Contenu des fichiers de configuration » |
 | Format de version | `version.json` avec entier incrémental `build` (ex. `{"build": 47}`), comparaison `>` entre entiers — pas de semver ni de comparaison de chaînes brute (piège "9" > "10" lexicographique) |
-| Fichiers `version.json` | Deux fichiers distincts et indépendants : un dans le dépôt Actualise, un dans le dépôt de chaque application cible (URL construite depuis `config.json`) |
+| Fichiers `version.json` | Deux fichiers distincts et indépendants : un dans le dépôt Actualise, un dans le dépôt de chaque application cible (URL construite depuis `config_<nom_app>.json`) |
 | Distribution des binaires | Assets de GitHub Releases (URL stable `releases/download/<tag>/<fichier>`), pas commités dans l'historique ; **un seul asset par tag, sous forme d'archive zip** contenant tous les fichiers de la version (exécutable, données, DLL) et le manifeste ; **nom d'asset fixe `<préfixe>.zip`** (ex. `actualise.zip`, `scrabble.zip`), sans numéro de version dans le nom du fichier — chaque nouvelle Release re-uploade un asset de ce même nom ; **tag de Release au format `v<build>`** (ex. `v48`) ; diff binaire écarté (gain marginal, binaires PyInstaller recompilés quasi-intégralement à chaque changement) |
 | `version.json` (stockage) | Reste un petit fichier commité normalement dans le dépôt, pas un asset de Release |
 | Manifeste de mise à jour | `manifest.json` à la racine du zip (`{"build": N, "supprimer": [...]}`) ; `supprimer` est une liste noire optionnelle de chemins à effacer après extraction — fail-safe (un oubli laisse un fichier obsolète, jamais une perte de données) ; script `.bat`/`.sh` exécutable écarté pour portabilité Linux/Windows et sécurité (pas d'exécution de code téléchargé sans supervision) ; **`manifest.json` absent → bloquant** : bascule échoue, non appliquée, zip conservé pour nouvelle tentative ultérieure (zip considéré malformé, pas une absence volontaire de suppression) |
# ── Zone modifiée : ligne 537 (9 ligne(s)) dans l'ancienne version → ligne 637 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -537,9 +637,10 @@ applications cibles, Scrabble servant de premier exemple concret :
 | Vérification SHA-256 du zip | `version.json` porte un champ `sha256` du zip complet publié ; après téléchargement, avant mise en zone d'attente, comparaison du SHA-256 calculé sur le fichier reçu ; non-correspondance → téléchargement rejeté, aucune zone d'attente mise à jour, nouvelle tentative au cycle suivant (même repli que pour un échec réseau) ; liste de fichiers attendus post-extraction écartée (redondante une fois le zip validé, une extraction incomplète relevant d'un problème d'environnement local détectable par vérification d'erreur d'extraction) |
 | Bootstrap séparé | Écarté pour l'instant — Actualise reste un exécutable unique qui se met à jour lui-même, avec le garde-fou par marqueur ci-dessus |
 | Garde-fou anti-boucle | Marqueur explicite transmis parent → enfant (env `ACTUALISE_CHILD=1` ou arg `--child`), déclenché uniquement lors de la bascule d'une mise à jour déjà téléchargée — voir section dédiée ci-dessus |
-| Configuration portable | Dossier résolu **relativement à l'emplacement de l'exécutable `Actualise.exe`** (via `sys.executable` en mode PyInstaller figé) — pas un chemin Windows fixe codé en dur — pour permettre plusieurs installations indépendantes d'Actualise sur la même machine (une par application cible) sans qu'une installation n'écrase le `config.json` d'une autre ; équivalent portable sous Linux inchangé (ex. `~/.config/actualise/` ou variable d'environnement) |
-| Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable`, et `icone` (optionnel, chemin `.ico` documenté pour le setup cible — non lu au runtime par Actualise) ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
-| Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; **ce dossier séparé est exactement le dossier de configuration résolu relativement à l'exécutable** (voir « Configuration portable ») — pas de chemin d'installation distinct du dossier de configuration, `Actualise.exe`/`config.json`/zone d'attente cohabitent ; **le nom de ce dossier n'est plus fixe** (`C:\Actualise\`) mais choisi par chaque setup, convention suggérée `C:\Actualise_<NomApplication>\` (ex. `C:\Actualise_Scrabble\`, `C:\Actualise_Rummikub\`) pour éviter toute collision entre applications cibles différentes ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées ; **icône du raccourci** : le setup de l'application cible déploie son propre fichier `.ico` et l'utilise à la fois pour `IconFilename` du raccourci (qui pointe vers `Actualise.exe` mais affiche l'icône de l'application cible) et pour le champ `icone` de `config.json` — même chemin dans les deux cas — voir « Intégration avec le setup.exe d'une application cible » |
+| Configuration portable | Dossier résolu **relativement à l'emplacement de l'exécutable `Actualise.exe`** (via `sys.executable` en mode PyInstaller figé, `config.chemin_config_portable()`) — mécanisme de résolution inchangé depuis la conception initiale (issue #4) ; ce qui a changé (issue #44), c'est la convention de déploiement : `Actualise.exe` n'est plus installé qu'une seule fois, dans un dossier fixe et **partagé** (`C:\Actualise\`, imposé par `Actualise-Setup.exe`), donc cette résolution relative pointe désormais systématiquement vers ce même dossier partagé quelle que soit l'application cible qui a lancé Actualise ; équivalent portable sous Linux inchangé (`~/.config/actualise/` ou variable d'environnement `ACTUALISE_CONFIG_DIR`) — voir « Configuration portable » et « Points de vigilance connus » pour l'historique complet |
+| Contenu de la configuration | Deux fichiers séparés (issue #35) remplaçant l'ancien `config.json` unique à deux blocs : `config_actualise.json` (un seul exemplaire, **partagé** entre toutes les applications cibles gérées par cette installation — `build_installe`, `depot_github`, `zone_attente` d'Actualise) et `config_<nom_app>.json` (un exemplaire **par application cible** — `nom`, `depot_github`, `build_installe`, `repertoire_installation`, `executable`, `icone` optionnel, `topic_ntfy`) ; sélection du fichier `config_<nom_app>.json` à charger via l'argument obligatoire `--config <nom>` passé à `Actualise.exe` ; `config.charger_config(nom_app)` lit et fusionne les deux fichiers en un seul dict pour le reste d'Actualise — voir « Contenu des fichiers de configuration » |
+| Intégration au setup.exe cible | Modèle actuel (issue #44) : **deux setups distincts**. `Actualise-Setup.exe` (installeur InnoSetup dédié, `installeur/actualise.iss`) installe l'instance partagée d'Actualise une seule fois, dans un dossier fixe et non modifiable `C:\Actualise\` (`DisableDirPage=yes`, `PrivilegesRequired=admin`), et crée `config_actualise.json` seulement s'il n'existe pas déjà. Le setup de chaque application cible **ne déploie plus Actualise lui-même** — seulement son `config_<nom>.json`, son raccourci Bureau/menu Démarrer vers `Actualise.exe --config <nom>` (jamais directement vers l'application cible), et son icône `.ico` (même chemin utilisé pour `IconFilename` du raccourci et pour le champ `icone` de `config_<nom>.json`) — voir « Intégration avec le setup.exe d'une application cible » |
+| ActualiseUI.exe | Module séparé (issue #36), jamais importé par `actualise.py`, compilé en exécutable indépendant (`actualise_ui.py` → `ActualiseUI.exe`) et déployé uniquement par `Actualise-Setup.exe`. Gère le dialogue de mise à jour d'Actualise côté utilisateur final (fenêtre tkinter « Mettre à jour »/« Plus tard »), en repli sur la bascule silencieuse par renommage si le flag/bat n'a pas pu être généré — voir « ActualiseUI.exe — dialogue de mise à jour côté utilisateur final » |
 | Cycle de vie d'Actualise | Actualise ne lance plus l'application cible — c'est elle qui le lance à son démarrage ; Actualise attend uniquement la fin de sa propre tâche de fond (vérification, téléchargement, validation SHA-256, notification ntfy), puis se termine — indépendamment du cycle de vie de l'application cible ; Actualise n'est pas un processus permanent, c'est un aller-retour ponctuel à chaque démarrage de l'application cible |
 | Nommage versionné des zips en zone d'attente | `<préfixe>_<build>.zip` (ex. `actualise_48.zip`, `scrabble_112.zip`) — comparaison directe avec `build_installe` sans ouvrir le zip ; au démarrage, résidu avec `build` ≤ `build_installe` correspondant supprimé sans être appliqué (nettoyage automatique, garde-fou contre un zip bloqué indéfiniment en zone d'attente) ; **si plusieurs zips du même préfixe coexistent**, seul celui au build le plus élevé est considéré, les autres supprimés sans être appliqués (même logique que pour un résidu obsolète) — voir « Nommage versionné des zips en zone d'attente » |
 
# ── Zone modifiée : ligne 562 (4 ligne(s)) dans l'ancienne version → ligne 663 (44 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -562,4 +663,44 @@ applications cibles, Scrabble servant de premier exemple concret :
   constater qu'une des deux applications ne se mettait plus à jour.
   Corrigé en résolvant le dossier de configuration relativement à
   l'emplacement de l'exécutable `Actualise.exe` plutôt qu'un chemin
-  codé en dur (voir « Configuration portable »).
+  codé en dur (voir « Configuration portable »). Ce mécanisme de
+  résolution reste inchangé aujourd'hui ; voir le point suivant pour ce
+  qui a changé depuis dans la façon dont il est exploité.
+- **Passage du modèle « instances séparées » au modèle « instance
+  unique partagée »** (issues #27, #35, #36, #44) : la parade retenue
+  pour l'incident ci-dessus consistait à installer une copie complète
+  et indépendante d'Actualise **par application cible**, chacune dans
+  son propre dossier (convention suggérée `C:\Actualise_<NomApplication>\`,
+  ex. `C:\Actualise_Scrabble\`, `C:\Actualise_Rummikub\`), avec son
+  propre `config.json` complet — modèle documenté dans une révision
+  précédente de cette section. Ce modèle **a depuis été abandonné** au
+  profit d'un refactor plus profond : une **instance unique partagée**
+  d'Actualise (`C:\Actualise\`), avec un fichier de configuration
+  **distinct par application cible** (`config_<nom>.json`) plutôt
+  qu'une installation distincte par application cible. Le mécanisme de
+  résolution relative à l'exécutable (`sys.executable`) qui avait rendu
+  possible le modèle « instances séparées » n'a pas changé ; ce qui
+  change, c'est qu'il n'y a désormais plus qu'un seul `Actualise.exe`
+  installé sur la machine à résoudre, puisqu'une seule installation
+  existe pour toutes les applications cibles.
+
+  Ce refactor a été mené en plusieurs étapes distinctes, chacune
+  correspondant à une issue séparée : séparation de `config.json` en
+  `config_actualise.json` (partagé) et `config_<nom>.json` (par
+  application), avec argument `--config <nom>` obligatoire pour
+  sélectionner lequel charger (issue #35) ; ajout d'`ActualiseUI.exe`,
+  module séparé gérant le dialogue de mise à jour côté utilisateur
+  final et contournant le verrou Windows sur `_internal\` pendant
+  l'exécution d'Actualise (issue #36) ; ajout d'`Actualise-Setup.exe`,
+  installeur InnoSetup dédié et indépendant des setups des applications
+  cibles, qui installe l'instance partagée une seule fois pour toutes
+  (issue #44). Avantage par rapport au modèle « instances séparées » :
+  une seule copie d'Actualise à maintenir et mettre à jour sur la
+  machine, plutôt qu'une par application cible avec son propre cycle de
+  mise à jour indépendant. Contrepartie : réintroduction d'un état
+  partagé (`config_actualise.json`), dont la collision initiale (objet
+  du point précédent) est cette fois évitée non plus par l'isolement
+  des dossiers d'installation, mais par la logique applicative
+  d'`Actualise-Setup.exe` (ne jamais écraser `config_actualise.json`
+  s'il existe déjà) combinée à la séparation stricte des fichiers de
+  configuration par application cible.
