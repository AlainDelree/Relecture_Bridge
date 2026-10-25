# CHANGELOG — relecture_bridge

Historique complet des évolutions du projet, une section par issue, la
plus récente en premier.

Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
## 2026-09-21 — issue #60 (relecture_web)

## Issue #115 — 2026-10-25

- Correction du défaut découvert au premier usage réel du bouton
  **« Fusionner le changelog »** (#114) : une `UnicodeDecodeError` sur
  l'octet `0xe9` faisait planter la page (« Internal Server Error »). Un
  programme Windows dont la sortie est redirigée (ssh, scp, ou le script
  lancé à distance) n'écrit PAS en UTF-8 par défaut mais dans l'encodage
  de la console Windows (`0xe9` = « é » en cp1252), alors que
  `subprocess.run(text=True)` décodait selon l'encodage préféré du process
  LOCAL (UTF-8 sur le ThinkPad).
- `git_info._decoder_sortie_distante`/`_run_ssh_scp` : décodage tolérant
  (UTF-8, puis repli cp1252, puis cp850 — ce dernier associe un caractère
  à chacun des 256 octets possibles, donc ne lève jamais cette exception)
  appliqué à TOUTE commande ssh/scp touchant le PC fixe —
  `_lancer_git_distant` (donc toute commande git distante, y compris la
  détection des `CHANGELOG-<N>.md`), `tester_connectivite_ccw`,
  `_detecter_interpreteur_python_ccw`, et les trois étapes propres à
  `fusionner_changelog_distant` (création du dossier temporaire, copie du
  script, lancement du script, nettoyage).
- Lancement du script de fusion sur le PC fixe désormais avec l'option
  d'interpréteur `-X utf8`, pour que ses messages accentués soient écrits
  en UTF-8 plutôt que dans l'encodage de console par défaut.
  `scripts/fusionner_changelog.py` précisait déjà `encoding="utf-8"` à
  chaque lecture/écriture de fichier depuis #114 — vérifié à nouveau,
  aucun défaut trouvé là, inchangé.
- `git_info.fusionner_changelog_distant` : toute exception imprévue
  pendant la préparation ou l'exécution (y compris un
  `subprocess.TimeoutExpired` sur une étape distante) est désormais
  attrapée par un `try`/`except` englobant tout le corps de la fonction,
  pour ne jamais laisser remonter de page d'erreur serveur — le message
  produit précise l'étape atteinte (ce qui a pu être fait côté PC fixe) et
  la commande de retour en arrière, affichée mais jamais lancée ; si
  l'exception survient après l'exécution du script mais avant le commit,
  le message le dit explicitement. La copie temporaire du script reste
  supprimée dans tous les cas (nettoyage lui-même protégé contre un
  nouvel échec qui masquerait l'erreur principale).
- Tests (`relecture_web/test_fusion_changelog_distant.py`, +16, 142 → 158
  tests, tous `unittest` autonomes, sans réseau réel) : décodage tolérant
  testé en isolation (`_decoder_sortie_distante`, UTF-8/cp1252/cp850, tous
  les octets 0-255) et via un faux ssh/scp étendu (court-circuit par
  octets bruts imposés en base64, ou relais ré-encodant la sortie
  réellement produite — connectivité, commande git distante, détection des
  CHANGELOG-<N>.md, fusion complète avec sortie cp1252/cp850 du script) ;
  exception forcée à mi-chemin (après script, avant commit) via un
  monkeypatch de `_lancer_git` ; préservation octet pour octet du contenu
  existant de `CHANGELOG.md`/`CHANGELOG-<N>.md` (accents, tirets longs)
  par `scripts/fusionner_changelog.py` même avec `PYTHONIOENCODING=cp1252`
  (seul levier disponible sur un poste Linux pour s'approcher du défaut
  Windows).
- `RELECTURE_WEB_DOC.md` (§11) : décodage tolérant des sorties du PC fixe,
  UTF-8 forcé pour le script, comportement en cas d'exception.

## Issue #114 — 2026-10-25

- Bouton **« Fusionner le changelog »** pour un projet distant (PC fixe
  CCW) : remplace le refus explicite inconditionnel de l'issue #108.
  `git_info.detecter_changelogs_a_fusionner` (via `git ls-tree --name-only
  HEAD`, routé en SSH) détecte, à chaque ouverture de la page du projet,
  les `CHANGELOG-<N>.md` présents à la racine du clone Windows — présence
  détectée, bouton affiché (numéros concernés) ; sinon, pas de bouton.
  Le message après un merge réussi sur un projet distant
  (`fusionner_changelog_worktree`) utilise désormais cette même détection
  (il ne s'affiche plus s'il n'y a réellement rien à fusionner) et invite
  à utiliser ce bouton plutôt qu'à « fusionner manuellement ».
- `git_info.fusionner_changelog_distant` (route POST
  `/projet/<nom_projet>/fusionner-changelog-distant`, confirmation
  « légère » affichant les commandes réelles, comme le reste de l'outil) :
  vérifie que le clone est sur sa branche principale et que `git status`
  ne signale rien d'autre que le CHANGELOG à intégrer, détecte
  l'interpréteur Python disponible sur le PC fixe (« python », repli
  « py »), copie `scripts/fusionner_changelog.py` par `scp` dans un
  dossier temporaire frère des dossiers de projets, l'exécute sur le
  clone, puis committe UNIQUEMENT `CHANGELOG.md` et les `CHANGELOG-<N>.md`
  traités (message `chore: fusionne CHANGELOG-<N>.md dans CHANGELOG.md
  (auto)`, jamais de push) et affiche les trois derniers commits. La copie
  temporaire du script est toujours supprimée du PC fixe, succès ou
  échec ; un échec à mi-chemin ne committe rien et affiche (sans jamais la
  lancer) la commande de retour en arrière. Toute erreur SSH réutilise le
  classement par catégorie de l'issue #111.
- `scripts/fusionner_changelog.py` : correction d'un défaut de fins de
  ligne (le point le plus important de cette issue, même famille que le
  défaut déjà corrigé par #107) — le script lisait/écrivait
  `CHANGELOG.md` en mode texte universel, ce qui aurait converti en bloc
  tout fichier resté en LF vers CRLF une fois exécuté sur le PC fixe
  Windows (`os.linesep` différent du ThinkPad, où le défaut restait
  invisible). Lecture/écriture désormais en `newline=""` : le contenu déjà
  présent dans `CHANGELOG.md` n'est jamais retouché, seul le texte inséré
  (chaque `CHANGELOG-<N>.md`) est ramené à la fin de ligne dominante du
  fichier cible (LF, CRLF, ou mixte).
- Tests ajoutés : `relecture_web/test_fusion_changelog_distant.py` (ssh/scp
  factices exécutant réellement les commandes sur un dépôt git jetable,
  python et le script réels — un seul CHANGELOG-<N>.md, plusieurs, aucun,
  LF/CRLF/mixte, branche non principale, autres modifications présentes,
  python absent, repli « py », script en échec à mi-chemin, nettoyage de
  la copie temporaire, ccw_host non configuré) ; mise à jour de
  `relecture_web/test_chemins_windows_ccw.py` pour la nouvelle détection
  conditionnelle de `fusionner_changelog_worktree`.
- `RELECTURE_WEB_DOC.md` (§11) mis à jour.

## Issue #113 — 2026-10-24

- `confirmation_fichiers_ignores_worktree.html` (page de confirmation
  avant suppression d'un worktree contenant des fichiers ignorés par git,
  issue #112) n'affichait qu'un seul bouton visible (« Confirmer la
  suppression malgré tout ») : avec un seul choix visible, l'impression
  était de n'avoir que celui-là. Un lien **Annuler** (retour simple vers
  la page du projet, rien n'est soumis) est désormais affiché juste avant
  ce bouton, avec le focus par défaut (un appui accidentel sur Entrée ne
  déclenche donc jamais la suppression) — style neutre identique au
  bouton Annuler des fenêtres de confirmation forte existantes
  (`.bouton--annuler`), pendant que le bouton de confirmation garde son
  style de danger. Le formulaire de confirmation (champs cachés, requête
  renvoyée) est inchangé.
- `echec_suppression_worktree.html` (page de suppression forcée après un
  premier échec, issue #103) avait le même défaut pour chaque worktree
  concerné par un bouton « Forcer la suppression » : même correction, même
  ordre (Annuler avant le bouton de forçage), pour chaque worktree —
  seul le premier Annuler de la page reçoit le focus par défaut (un seul
  élément `autofocus` par page, comme l'exige le HTML). Les formulaires de
  forçage (champ caché `branche`, `purger_commit_rejet`) sont inchangés.
- Aucune autre page de confirmation de l'outil n'était concernée : les
  autres actions destructrices (Push, Merger, Supprimer, Rejeter...)
  passent déjà par la fenêtre de confirmation forte commune
  (`#modal-confirmation`, `base.html`), qui propose déjà un bouton Annuler
  avec le focus par défaut depuis l'issue #71/#73.
- Nouveaux tests
  (`relecture_web/test_bouton_annuler_confirmation_suppression.py`,
  9 tests) : sur les deux pages, l'élément Annuler apparaît avant le
  bouton destructeur, pointe vers la page du projet, ne déclenche aucune
  suppression, et le formulaire de confirmation/forçage reste inchangé ;
  un seul `autofocus` sur la page même avec plusieurs worktrees en échec
  simultanément.
- `RELECTURE_WEB_DOC.md`, section 9 : complément sur la ligne « Forcer la
  suppression » — la ligne « Avertissement fichiers ignorés avant
  suppression de worktree » décrivait déjà le bouton Annuler attendu,
  conforme à l'implémentation désormais corrigée.

## Issue #112 — 2026-10-24

- `relecture_web/git_info.py` : nouvelle fonction
  `lister_fichiers_ignores_worktree(chemin_worktree)` — détecte, via
  `git status --porcelain=v1 --ignored` exécuté dans le worktree lui-même
  (donc routé par SSH pour un projet distant comme toute autre commande de
  ce module, issue #94/#109), les fichiers/dossiers ignorés par
  `.gitignore` présents dans un worktree : `git worktree remove`, même sans
  `--force`, les supprime SANS AUCUN AVERTISSEMENT, puisque `git status`
  (sans `--ignored`) et donc le diagnostic d'échec existant
  (`diagnostiquer_echec_suppression_worktree`, issue #103) ne les voient
  jamais. Cas réel ayant motivé cette issue : l'installeur et l'archive
  produits par un build Windows de Rummikub (`installeur\output\`,
  ignorés) auraient été perdus avec le worktree sans que la personne ne
  les ait recopiés à la main avant.
- Bruit sans valeur exclu de cet avertissement (un seul endroit à éditer :
  `DOSSIERS_IGNORES_SANS_VALEUR`/`SUFFIXES_IGNORES_SANS_VALEUR`/
  `NOMS_FICHIERS_IGNORES_SANS_VALEUR`) : `__pycache__`, `.pytest_cache`,
  `.mypy_cache`, `.ruff_cache`, `*.pyc`, `.DS_Store`, `Thumbs.db`,
  `desktop.ini`. Les dossiers d'environnement/dépendances (`venv`,
  `node_modules`...) sont volontairement absents de cette liste : ils
  peuvent représenter un travail d'installation long à refaire, voire un
  outil installé à la main dans le clone, donc restent toujours affichés.
- Tailles : pour un projet local, calculées en octets (`os.walk` plafonné
  en nombre de fichiers ET en temps, partagés entre toutes les entrées
  d'un même appel pour ne jamais bloquer la page), affichées en
  octets/Ko/Mo/Go (`formater_taille_octets`) ; au-delà du plafond ou en
  cas d'échec filesystem, l'entrée retombe sur « taille non calculée »,
  jamais une erreur. Pour un projet distant (PC fixe CCW), aucun calcul de
  taille n'est tenté par SSH (issue #109) — toujours « taille non
  calculée ».
- `relecture_web/app.py` : `supprimer_worktrees_route`,
  `merger_et_supprimer_route` et `rejeter_worktrees_route` appellent
  désormais cette détection AVANT toute tentative de suppression (et avant
  toute fusion pour « Merger et supprimer ») sur l'ensemble des worktrees
  sélectionnés. Dès qu'au moins un worktree concerné contient un fichier
  ignoré qui n'est pas du bruit, rien n'est supprimé ni fusionné pour
  AUCUN worktree du lot : une nouvelle page de confirmation
  (`confirmation_fichiers_ignores_worktree.html`) liste, par worktree
  concerné, ces fichiers/dossiers avec leur taille, et propose Annuler
  (rien n'est soumis) ou Confirmer la suppression malgré tout (ré-envoi de
  la requête d'origine avec un champ caché
  `ignorer_avertissement_fichiers_ignores=on`, après la fenêtre de
  confirmation forte habituelle). Si aucun worktree sélectionné n'est
  concerné, le comportement reste exactement le même qu'avant cette
  issue.
- `echec_suppression_worktree.html` (page de suppression forcée, issue
  #103) affiche en plus, dans une section distincte quand il y en a, ces
  mêmes fichiers ignorés (`_diagnostiquer_echec_pour_forcage` les ajoute
  désormais à l'entrée affichée) — pour que la confirmation forte porte
  sur l'ensemble de ce qui sera réellement perdu, pas seulement les
  fichiers modifiés/non suivis qui ont fait échouer la tentative normale.
- Rien n'est copié ni sauvegardé automatiquement : l'outil prévient, il ne
  décide pas à la place de la personne. Comportement de git et détection
  des worktrees inchangés par ailleurs.
- Nouveaux tests (`relecture_web/test_fichiers_ignores_suppression_worktree.py`,
  21 tests) : détection directe (bruit seul/dossier de build seul/mélange/
  rien, taille, échec gracieux), routage local/distant (faux `ssh`
  comptant ses appels, zéro calcul de taille et zéro appel hors action sur
  le projet distant concerné), et intégration complète des trois routes
  sur de vrais dépôts/worktrees jetables (confirmation avant toute
  suppression/fusion, annulation ne supprimant rien, confirmation
  supprimant/fusionnant bien, plusieurs worktrees sélectionnés dont un
  seul concerné met le lot entier en pause).
- `RELECTURE_WEB_DOC.md`, section 9 : nouvelle ligne « Avertissement
  fichiers ignorés avant suppression de worktree », et complément sur la
  ligne « Forcer la suppression » existante.

## Issue #111 — 2026-10-24

- `git_info.tester_connectivite_ccw()` ne renvoie plus seulement
  vrai/faux : elle analyse désormais le texte d'erreur de `ssh` (même
  code de sortie 255 dans tous les cas) et le classe en cinq catégories
  (`CCW_CLE_HOTE_MODIFIEE`, `CCW_CLE_REFUSEE`, `CCW_CONNEXION_REFUSEE`,
  `CCW_HOTE_INACCESSIBLE`, `CCW_CAUSE_INCONNUE`), avec un libellé et un
  message dédiés par catégorie (`CCW_LIBELLES`, `_classer_echec_ssh_ccw`,
  `_message_echec_ssh_ccw`). Tous ses appelants (production et tests)
  adaptés ensemble au nouveau contrat `(ok, categorie, message)`.
- `charger_etat_projet` stocke `ccw_categorie`/`ccw_message` sur l'entrée
  du projet distant au statut `"injoignable"` ; `templates/projet.html`,
  `templates/index.html` et `_projet_pret` (`app.py`, refus d'action)
  affichent ce message détaillé à la place de l'ancien texte générique
  unique, avec repli sur ce dernier si absent.
- `_lancer_git_distant` applique le même classement à une commande git
  distante qui échoue EN COURS D'ACTION avec le code de sortie 255 (donc
  un échec `ssh`, jamais `git`) : le message de diagnostic est préfixé au
  texte brut de `ssh`, conservé pour le détail.
- L'adresse utilisée dans la commande `ssh-keygen -R <adresse>` (cas
  « clé d'hôte modifiée ») vient toujours de `ccw_host.conf` (partie après
  l'arobase), jamais écrite en dur.
- Premier contact avec un hôte jamais vu : avec
  `StrictHostKeyChecking=accept-new` (déjà en place depuis #94), ce cas
  est accepté silencieusement par `ssh`, sans erreur — il ne peut donc
  jamais se confondre avec « clé d'hôte modifiée » en pratique ; la
  distinction demandée par l'issue n'avait donc pas lieu d'être avec ces
  options.
- Nouveaux tests (`relecture_web/test_diagnostic_echec_ssh_ccw.py`) :
  classement unitaire des cinq catégories + adresse non codée en dur,
  bout en bout avec un faux `ssh` (script shell sur le PATH, aucun réseau
  ni vrai `ssh`) pour chaque catégorie plus le succès, et vérification
  que `charger_etat_projet` n'affecte ni un projet local ni un PC fixe
  joignable. Tests existants (`test_ccw_host_conf.py`,
  `test_chargement_a_la_demande_distant.py`) adaptés au nouveau contrat
  de `tester_connectivite_ccw`.
- Doc : `RELECTURE_WEB_DOC.md` section 11 mise à jour (tableau des cinq
  catégories, texte ssh reconnu par catégorie, libellés alignés avec la
  procédure de réinstallation Windows de Bridge_Agent).

## Issue #110 — 2026-10-24

- `relecture_web/ccw_host.conf` (configuration personnelle du PC fixe
  Windows, issue #94) n'est plus suivi par git — même traitement que
  `secret_key.conf` (issue #92) : le dossier principal du dépôt n'est
  plus signalé comme modifié dès qu'Alain y renseigne sa vraie ligne
  `ccw_host`, et aucun risque de la pousser par accident sur GitHub.
  `git rm --cached relecture_web/ccw_host.conf` (le fichier reste
  inchangé sur le disque de ce worktree, qui n'a jamais contenu de vraie
  valeur), et ajout de `ccw_host.conf` à `relecture_web/.gitignore`.
- Nouveau fichier `relecture_web/ccw_host.conf.example`, suivi par git :
  reprend les lignes d'aide existantes (format, rôle de `ccw_host`/
  `ccw_key`, comportement tant que `ccw_host` n'est pas renseigné), avec
  un exemple générique (`utilisateur@<ip-locale>`, aucune information
  personnelle) et des instructions pour copier ce modèle vers
  `ccw_host.conf` puis y renseigner sa propre configuration.
- `git_info.charger_etat_projet` : nouveau statut `"ccw_non_configure"`,
  distinct de `"injoignable"` — `ccw_host.conf` absent, vide, ou sans
  entrée `ccw_host` (installation neuve, ou après la suppression du
  fichier réel désormais hors git) donne ce statut SANS tenter la moindre
  connexion SSH (`charger_config_ccw()` testé avant
  `tester_connectivite_ccw()`), alors qu'avant ce correctif les deux cas
  étaient confondus sous `"injoignable"` et affichaient le même message
  « PC fixe éteint ou injoignable », trompeur quand aucune connexion n'a
  même été tentée.
- `app.py`/`index.html`/`projet.html` : message dédié pour
  `"ccw_non_configure"` invitant explicitement à copier
  `ccw_host.conf.example` vers `ccw_host.conf` puis à renseigner
  `ccw_host`, au lieu du message de connexion générique
  (`_MESSAGE_CCW_NON_CONFIGURE`, utilisé par `_projet_pret` et les deux
  templates).
- `git_info._lancer_git_distant` : message d'erreur (stderr, hôte non
  configuré) mis à jour pour mentionner `ccw_host.conf.example` —
  chemin défensif, en pratique jamais atteint depuis que
  `charger_etat_projet` court-circuite avant toute commande git distante
  quand l'hôte n'est pas configuré.
- `RELECTURE_WEB_DOC.md` (§11) : configuration décrite comme personnelle
  et hors git, modèle `ccw_host.conf.example` documenté, nouveau statut
  `"ccw_non_configure"` ajouté à côté de `"injoignable"`.
- Tests : nouveau fichier `test_ccw_host_conf.py` (fichier absent,
  fichier renseigné, modèle jamais interprété comme config valide,
  `.gitignore` vérifié par `git check-ignore` dans un dépôt jetable) ;
  `test_chargement_a_la_demande_distant.py` mis à jour (le tableau de
  test ne lit plus jamais le vrai `ccw_host.conf` du disque — nouveau
  flag `CCW_CONFIGURE` sur la config factice) avec une nouvelle classe
  `ProjetDistantNonConfigureTestCase`.
- `installer.sh`, `branches_cibles.conf` : aucune référence à
  `ccw_host.conf`, aucun changement nécessaire (vérifié par recherche
  dans tout le dépôt).
- Essai en scratch (dépôt jetable, nettoyé après coup, jamais dans ce
  worktree de façon durable) : reproduction de la fusion du commit qui
  cesse de suivre `ccw_host.conf` dans un dossier où ce fichier est suivi,
  localement modifié (vraie configuration), avec `--skip-worktree` ou
  `--assume-unchanged` posé — voir le compte rendu de clôture pour le
  résultat détaillé et la procédure sûre à suivre par Alain.

## Issue #109 — 2026-10-24

- `relecture_web` ne contacte plus le PC fixe CCW (test de connectivité
  SSH, commandes git distantes) pour une page ou une action qui ne
  concerne pas spécifiquement un projet distant — avant ce correctif,
  `collect_etat_projets()` chargeait TOUS les projets en entier à CHAQUE
  chargement de page (accueil, barre latérale, page d'un autre projet,
  « Nettoyer tous les projets »...), donc au moins une connexion SSH par
  page dès qu'une ligne `<nom>_ccw` (issue #108) figurait dans le tableau
  §2 — ralentissant sensiblement toutes les pages, même locales.
- `git_info.py` : `collect_etat_projets()` est remplacée, pour toutes les
  pages de `relecture_web`, par `collect_etat_projets_legers()` — les
  projets locaux sont chargés en entier (coût local, inchangé), les
  projets distants sont renvoyés avec seulement nom/dépôt/répertoire/
  couleur et le nouveau statut `"distant_a_charger"`, sans aucun appel
  réseau. Le chargement complet d'un seul projet (test SSH, worktrees...)
  est désormais isolé dans `charger_etat_projet(projet, ...)`, point
  d'entrée unique réutilisé en interne par `collect_etat_projets_legers()`
  pour les projets locaux et, à la demande, pour un projet distant
  précis. `collect_etat_projets()` (toujours exportée) ne charge plus que
  l'usage manuel en ligne de commande de ce module (`if __name__ ==
  "__main__"`), plus aucune page ne l'appelle.
- `app.py` : `_charger_projets()` (accueil, barre latérale, « Nettoyer
  tous les projets », pages d'un AUTRE projet) utilise désormais
  `collect_etat_projets_legers()`. Nouvelle fonction
  `_charger_projet_complet(nom_projet)` — seul point qui déclenche le
  chargement complet (et donc SSH) d'un projet distant, mémoïsé dans `g`
  par nom de projet (un seul test de connectivité par requête même si
  plusieurs morceaux de la page en ont besoin) — appelée directement par
  `projet_route` (ouverture de la page d'un projet) et par
  `_trouver_projet`/`_projet_pret`, donc par toute route d'action qui
  résout son projet par ce biais (push, merge, suppression,
  sécurisation, revert, nettoyage...).
- Revue de `app.py`/`git_info.py` pour tout autre endroit qui parcourait
  la liste complète des projets avec accès PC fixe (partie A5) :
  - `nettoyer_tous_les_projets_route` : déjà sans contact SSH possible
    une fois `_charger_projets()` corrigée — elle ignore tout projet qui
    n'est pas au statut `"ok"`, et un projet distant reste
    `"distant_a_charger"` tant que sa page n'a pas été ouverte. Aucun
    changement de code nécessaire au-delà du switch vers la liste légère.
  - `_verrous_actifs_projets` (verrous Bridge_Agent actifs) : laissée
    telle quelle, elle ne cherche que le répertoire du projet
    `bridge_agent` (toujours local) dans la liste — jamais besoin de
    l'état complet d'un projet distant.
  - `injecter_barre_laterale` (context processor) : adaptée pour
    regrouper locaux puis distants (partie B1), toujours sans aucun
    accès au PC fixe (champs nom/couleur/couleur_texte seulement).
- Partie A4 (suite) : « Nettoyer ce projet » sur un projet distant
  (`nettoyer_projet_route`) était déjà, avant ce correctif, sans effet
  réel sur un projet distant joignable (0 résumé supprimé, silencieusement
  — `Non_Lu/` est cherché sur un chemin LOCAL qui n'existe jamais pour un
  clone Windows, aucun hook post-commit n'y étant installé). Refusée
  maintenant explicitement avec un message clair, et le bouton masqué
  côté template (`projet.html`) pour un projet distant — aucune tentative
  de lecture/écriture sur un chemin local inventé.
- Mise en page (partie B) : à l'accueil et dans la barre latérale, les
  projets locaux sont affichés d'abord (ordre inchangé), puis les
  projets distants du PC fixe CCW, séparés par un intitulé discret
  « PC fixe (Windows) » qui n'apparaît que s'il existe au moins un projet
  distant — affichage strictement inchangé sinon. Un projet distant de
  l'accueil n'affiche plus de décompte de résumés « (0) » (sans intérêt,
  aucun hook post-commit sur le clone Windows) mais la mention « PC fixe,
  chargé à l'ouverture ». La page d'un projet distant affiche en tête une
  indication discrète (chemin du clone Windows, accès par SSH) expliquant
  pourquoi cette page précise est plus lente que les autres. Reprise du
  style existant (`static/style.css`), les projets distants gardent leur
  couleur propre dans la barre latérale.
- `RELECTURE_WEB_DOC.md` : section « Source de la liste des projets »
  corrigée (la liste est relue à CHAQUE chargement de page, pas « au
  démarrage », avec un cache d'environ cinq minutes côté
  `raw.githubusercontent.com` sur le fichier brut) ; section 2 (navigation)
  et section 11 (mode SSH) mises à jour : statut `"distant_a_charger"`,
  chargement à la demande (`charger_etat_projet`/`_charger_projet_complet`),
  regroupement locaux puis distants avec séparateur.
- Tests ajoutés :
  `relecture_web/test_chargement_a_la_demande_distant.py` (unittest
  autonome, stdlib uniquement, aucun accès réseau réel — tableau simulé
  via une fausse `fetch_projets`, faux `tester_connectivite_ccw`/
  `_lancer_git_distant` qui comptent leurs appels sans jamais lancer de
  vrai `ssh`, projets locaux de vrais petits dépôts git temporaires,
  client de test Flask de `relecture_web`). Prouvent : zéro appel SSH
  pour l'accueil, la barre latérale, une page de projet local, une action
  sur un projet local et « Nettoyer tous les projets » en présence d'un
  projet distant ; au moins un appel (et un seul par requête) pour la
  page du projet distant ; statut « injoignable » affiché quand le PC fixe
  ne répond pas ; refus explicite et bouton masqué pour « Nettoyer ce
  projet » sur un projet distant même joignable ; ordre locaux puis
  distants et séparateur présent uniquement s'il existe un projet
  distant ; absence de séparateur et de tout appel SSH quand aucun projet
  distant n'existe dans le tableau.

### Problèmes repérés mais non corrigés (hors périmètre explicite de
cette issue)

- Comme déjà noté par l'issue #108, la résolution de conflit et la fusion
  automatique du changelog restent hors périmètre pour un projet distant
  (refusées explicitement, pas de régression introduite ici).
- Aucune mise en cache de l'état du PC fixe au-delà de la mémoïsation par
  requête (`g`) — explicitement hors périmètre de cette issue ; si la
  page d'un projet distant s'avère encore trop lente à l'usage, ce serait
  une issue séparée.

## Issue #108 — 2026-10-24

- `relecture_web` : préparation aux lignes `<nom>_ccw` du tableau §2 de
  `BRIDGE_AGENT_DOC.md` (suite de l'issue #94), qui référencent le clone
  Windows d'un projet (`C:\CCW\<nom>`) à des fins de relecture uniquement
  (ni watcher ni issue GitHub pour elles).
- `git_info.py` : la reconnaissance du worktree principal d'un projet
  distant (`collect_etat_projets`) comparait deux chemins via
  `os.path.realpath`, qui traite un chemin Windows comme un bloc opaque
  sur ce process Linux — un chemin à barres obliques inverses (celui du
  tableau) et son équivalent à barres obliques normales renvoyé par `git`
  (casse potentiellement différente) étaient donc jugés différents, et le
  dossier principal du clone Windows se serait affiché comme un worktree
  ordinaire, avec des actions de fusion/suppression proposées à tort.
  Nouvelle comparaison dédiée (`chemins_windows_egaux`,
  `worktree_est_principal`) qui ignore barres obliques, casse et barre
  finale pour un projet distant, sans rien changer à la comparaison
  `os.path.realpath` existante pour un projet local. `dossier_relecture`
  (nom du dossier `Relecture_Bridge/<dossier>/Non_Lu`) corrigé de même
  (`nom_dossier_chemin_windows`), bien que sans effet pratique aujourd'hui
  (aucun hook post-commit n'existe sur un clone Windows).
- `fusionner_changelog_worktree` lisait/écrivait directement le filesystem
  local (`os.listdir`, script `fusionner_changelog.py` lancé localement) :
  sur un chemin Windows, elle échouait silencieusement à trouver un
  dossier local inexistant et concluait à tort qu'aucun `CHANGELOG-<N>.md`
  n'attendait de fusion. Refuse maintenant explicitement pour un projet
  distant (`est_projet_distant`), avec un message clair plutôt qu'un faux
  négatif silencieux.
- La résolution de conflit sur un projet distant reste hors périmètre
  (lecture/écriture de fichier, pas des commandes git routées), mais
  `conflit_fichier_route`, `traiter_bloc_conflit_route` et
  `traiter_tous_blocs_conflit_route` refusent maintenant explicitement
  (« Résolution de conflit non disponible pour un projet distant (PC fixe
  CCW). ») avant toute tentative d'accès — avant ce correctif, elles
  laissaient `lire_conflits_fichier`/`resoudre_bloc_conflit` échouer sur un
  chemin local inventé (join d'un chemin Windows), avec un message
  d'erreur système confus mais sans jamais lire/écrire un fichier hors de
  propos (l'échec `OSError` était déjà sans risque, juste peu clair).
- `installer.sh` : une ligne à chemin Windows affiche maintenant
  « ℹ Clone Windows distant (PC fixe CCW) — pas de hook installé par ce
  script : ... », distinct du message « ⚠ Ignoré (pas un dépôt git) : ... »
  réservé à un vrai dossier local sans `.git` — comportement inchangé pour
  les chemins Linux.
- `RELECTURE_WEB_DOC.md` (§11) mis à jour : lignes `<nom>_ccw`, comparaison
  de chemins Windows, refus de la résolution de conflit et de la fusion du
  changelog à distance, comportement d'`installer.sh`.
- Tests ajoutés : `relecture_web/test_chemins_windows_ccw.py` (unittest
  autonome, stdlib uniquement, aucun accès réseau réel) — comparaison de
  chemins (barres obliques, casse, barre finale, chemin réellement
  différent y compris même préfixe), comportement local inchangé, refus de
  `fusionner_changelog_worktree` pour un projet distant, et comportement
  d'`installer.sh` vérifié avec un tableau factice en scratch (`curl`
  simulé, dépôt git jetable, jamais de vrai dépôt touché).

## Issue #107 — 2026-10-23

- `relecture_web` : suite de l'issue #105 — la résolution de conflit
  (`resoudre_bloc_conflit`, `resoudre_tous_blocs_conflit`, `git_info.py`)
  aplatissait tout le fichier en LF dès la résolution d'un seul bloc,
  y compris un fichier entièrement en CRLF depuis l'origine : la lecture
  et l'écriture se faisaient en mode texte Python par défaut, qui traduit
  silencieusement `\r\n`/`\r` en `\n` à la lecture (mode « universal
  newlines ») sans jamais les restituer à l'écriture. `lire_conflits_fichier`,
  `resoudre_bloc_conflit` et `resoudre_tous_blocs_conflit` ouvrent désormais
  le fichier avec `newline=""` (lecture et écriture), qui désactive cette
  traduction — un fichier CRLF reste CRLF, un fichier LF reste LF, un
  fichier mixte garde chaque ligne de contexte (y compris un bloc non
  traité) avec exactement sa terminaison d'origine, seul le bloc remplacé
  change.
- Le texte validé soumis par le formulaire (`texte_final`) est maintenant
  normalisé, avant insertion, vers la fin de ligne **dominante du fichier
  cible** (la plus fréquente entre CRLF et LF ; LF par défaut en cas
  d'égalité ou d'absence de toute fin de ligne — nouvelles fonctions
  `_fin_de_ligne_dominante_fichier`/`_normaliser_fin_de_ligne_texte`).
  Nécessaire parce qu'un navigateur convertit les retours à la ligne d'un
  `<textarea>` en CRLF à la soumission d'un formulaire HTML, quelle que
  soit leur forme dans le DOM — y compris pour un texte composé par une
  flèche de copie (« ours »/« theirs »/« garder les deux »), pas seulement
  pour du texte tapé à la main ; c'est ce qui expliquait le cas réel
  constaté (deux blocs résolus par deux chemins différents, les deux
  ressortis en CRLF dans un fichier historiquement LF).
- Points adjacents corrigés en cours de route (cassés dès que les lignes
  gardent leur terminaison d'origine) : `_trouver_blocs_conflit` utilisait
  `ligne.rstrip("\n")` pour les en-têtes de marqueurs (`<<<<<<<`/`>>>>>>>`),
  laissant un `\r` résiduel sur un fichier CRLF — `rstrip("\r\n")`
  désormais. `_texte_affiche_bloc` (texte précalculé du bouton « Copier ce
  bloc ») normalise maintenant explicitement vers `\n`, pour ne jamais
  exposer de caractère `\r` à l'utilisateur dans le presse-papiers, même
  sur un fichier CRLF. La détection des marqueurs et la numérotation des
  blocs (`_trouver_blocs_conflit`) n'ont pas eu besoin de changement
  (comparaison par `str.startswith`, indépendante de la terminaison de
  ligne) ; l'empreinte sha256 comparée entre l'affichage
  (`lire_conflits_fichier`) et la soumission (`resoudre_tous_blocs_conflit`)
  reste cohérente puisque les deux lisent désormais le fichier de la même
  façon (`newline=""`) — un test dédié vérifie cette cohérence.
- Tests : nouveau fichier autonome `relecture_web/test_resolution_conflit_fin_de_ligne.py`
  (`unittest`, stdlib seule — aucun framework de test externe dans ce
  dépôt au moment de cette issue), 18 tests travaillant chacun dans un
  dépôt git jetable. Couvrent : fichier entièrement LF/CRLF/mixte, un seul
  bloc puis tous les blocs ; texte validé CRLF dans un fichier LF et LF
  dans un fichier CRLF ; chaque origine de texte (saisi, ours, theirs,
  garder les deux, vider) soumise une fois en LF et une fois en CRLF ; un
  fichier à deux blocs résolus par deux chemins différents (l'un « tapé »,
  l'autre « garder les deux »), les deux soumis en CRLF dans un fichier LF
  → fichier final entièrement LF ; un bloc ignoré conserve exactement les
  octets d'origine du reste du fichier ; un conflit dont les deux côtés
  contiennent eux-mêmes du CRLF (îlot CRLF local dans un fichier à
  dominante LF). Vérifié que 16 des 18 tests échouent contre le code
  d'avant cette issue (les 2 restants portaient uniquement sur le
  comportement déjà correct de la suppression de bloc vide), confirmant
  qu'ils couvrent bien la régression corrigée.
- `RELECTURE_WEB_DOC.md` (section 10) : nouveaux paragraphes décrivant la
  préservation des fins de ligne et la règle de normalisation du texte
  validé, plus une puce dédiée dans la description de « Traiter tous les
  blocs » (fin de ligne unique calculée une fois pour tout le fichier).
- Hors périmètre, volontairement non traité (demandé explicitement ainsi) :
  aucune conversion des fichiers déjà existants dans les dépôts, aucun
  changement du hook post-commit, aucun changement d'interface (`app.py`
  et `conflit.html` inchangés — la normalisation est centralisée côté
  `git_info.py`, point de passage unique de toutes les origines de texte
  avant écriture).

## Issue #104 — 2026-10-18

- `scripts/fusionner_changelog.py` : la ligne de titre d'échange en tête
  d'un `CHANGELOG-<N>.md` (« # CHANGELOG-N — à fusionner dans CHANGELOG.md »,
  tiret cadratin ou simple, N quelconque, lignes vides tolérées avant)
  n'était reprise dans `CHANGELOG.md` que parce que `fusionner` insérait le
  contenu du fichier d'échange tel quel — 64 lignes de ce type accumulées
  sur Bridge_Agent au fil des fusions, tous les projets fusionnés via
  relecture_web étant potentiellement concernés (issue #87). Nouvelle
  fonction `_retirer_entete_echange` : retire cette ligne et la ou les
  lignes vides qui la suivent directement avant insertion, si elle est
  présente en tout début de fichier ; absente, le contenu de l'entrée est
  repris intégralement, comme avant (jamais de perte d'une vraie entrée).
  Reste inchangé : tri par N décroissant, points d'insertion (en-tête
  « Convention d'ajout » ou repli), suppression des fichiers traités après
  fusion, idempotence, rapport affiché. Docstring du script et
  `RELECTURE_WEB_DOC.md` (section 9, action Merger) mis à jour en
  conséquence. Testé manuellement (dépôt jetable) : fichier avec en-tête
  tiret cadratin, fichier avec en-tête tiret simple et lignes vides
  avant/après, fichier sans en-tête, lot de plusieurs fichiers — dans tous
  les cas seule la ligne d'en-tête d'échange est retirée, le reste de
  l'entrée et le contenu déjà présent dans `CHANGELOG.md` restent intacts.
  Portée hors périmètre (volontairement non traitée) : nettoyage rétroactif
  des lignes déjà présentes dans les `CHANGELOG.md` d'autres projets
  (Bridge_Agent et autres), qui relèvent d'autres dépôts.

## Issue #103 — 2026-10-06

- `relecture_web` : constat en usage réel (rummikub, worktree-issue-133) —
  « Rejeter » a échoué avec « fatal: '<chemin>' contient des fichiers
  modifiés ou non-suivis, utilisez --force pour le supprimer » (garde-fou
  voulu : `git worktree remove` n'est jamais appelé avec `--force`), mais
  l'interface n'offrait ensuite aucune suite — Alain devait passer par un
  terminal pour comprendre ce que contenait le dossier puis forcer
  lui-même. Nouveau cas géré pour « Rejeter », « Supprimer la/les
  branche(s) fusionnée(s) » et « Merger et supprimer », `app.py`,
  `git_info.py`, nouveau template `echec_suppression_worktree.html` et
  `style.css` :
  - **Détection indépendante de la langue de git** : l'échec de
    `git worktree remove` n'est jamais interprété via le texte de son
    message d'erreur (traduit selon la locale de git). Nouvelle fonction
    `diagnostiquer_echec_suppression_worktree` : revérifie l'état réel du
    dossier via `git status --porcelain` exécuté DANS le worktree lui-même.
    Une sortie non vide confirme le cas « fichiers modifiés ou non
    suivis » (les fichiers ignorés par `.gitignore` n'y figurent jamais,
    comme pour git) ; une sortie vide (verrou, chemin déjà supprimé à la
    main, autre cause) laisse le message d'erreur brut de git s'afficher
    comme avant, sans bouton de forçage.
  - **Page dédiée montrant ce qui serait perdu** avant toute décision,
    `echec_suppression_worktree.html` : liste des fichiers avec leur statut
    (modifié / non suivi), plafonnée à 20 entrées puis « … et N autres »
    (`MAX_FICHIERS_AFFICHES_ECHEC_SUPPRESSION`) ; pour les fichiers suivis
    modifiés, `+ajouts −suppressions` par fichier (`git diff HEAD
    --numstat`) ; bouton « Copier le diff » (`.bouton-copier` existant)
    copiant le diff complet (`git diff HEAD`) des seuls fichiers suivis
    modifiés, plafonné à 2000 lignes et signalé si tronqué
    (`MAX_LIGNES_DIFF_ECHEC_SUPPRESSION`) — pour transmettre le contenu à
    un Claude Chat avant de trancher.
  - **Bouton « Forcer la suppression »**, affiché uniquement sur cette page
    (jamais permanent, jamais une case à cocher qui survivrait à un
    rechargement — leçon de la case « Purger », issue #102) : confirmation
    forte (bandeau rouge, focus par défaut sur Annuler, bouton nommé avec
    la portée réelle « Supprimer <branche> et ses N fichiers concernés »,
    commande équivalente affichée avec `--force`). Deux nouvelles routes,
    une par action d'origine puisque leurs garde-fous d'éligibilité sont
    strictement inverses : `supprimer_worktree_force_route` (branche
    confirmée fusionnée — partagée par « Supprimer » et « Merger et
    supprimer », le merge ayant déjà eu lieu avant cet échec) et
    `rejeter_worktree_force_route` (branche **non** fusionnée, reprend
    l'option « Purger réellement » de #96 via un champ caché). Les deux
    s'appuient sur une nouvelle fonction `supprimer_worktree_force`
    (`git worktree remove --force` puis `branch -D` habituel) et refusent,
    avec message explicite, si le badge « ⚠ CCL travaille ici » (#88) est
    actif sur ce worktree.
  - Si le worktree est en plus verrouillé (`git worktree lock`, qui exige
    alors deux `--force` consécutifs) ou si la suppression forcée échoue
    malgré tout, l'erreur brute de git est affichée telle quelle, sans
    nouvelle tentative automatique.
  - `RELECTURE_WEB_DOC.md` section 9 mise à jour (nouvelle ligne
    « Forcer la suppression »).

## Issue #102 — 2026-10-06

- `relecture_web` : constat en usage réel (rummikub, worktree-issue-133 et
  worktree-issue-133-bis) — après avoir coché la case « Purger réellement
  le(s) commit(s) rejeté(s) » pour une branche, puis décoché cette branche
  et coché une autre (du vrai travail), la case restait cochée. Option
  irréversible et globale au dépôt, elle ne doit jamais survivre à un
  changement de sélection. Trois changements, `templates/projet.html` et
  `static/style.css` (aucun changement côté `app.py`/routes) :
  - **Décochage systématique** : la case `#case-purger-rejet` est décochée
    dès qu'une case de branche change d'état (`change` sur `.checkbox-branche`),
    et sur tout `pageshow` (chargement initial **et** retour via le bfcache
    du navigateur) ; `autocomplete="off"` ajouté sur la case elle-même contre
    une restauration de formulaire par le navigateur. La règle existante
    (issue #97) qui empêche le panneau « Options de rejet » de se refermer
    tant que la case est cochée reste inchangée — elle se referme
    normalement dès que la case est décochée par ce nouveau mécanisme.
  - **Message raccourci** : le paragraphe rouge dense qui expliquait tout
    en permanence est remplacé par une seule ligne lisible d'un coup d'œil —
    verte « ✅ Aucun autre commit menacé. » si aucun autre commit orphelin
    non sécurisé n'est menacé, rouge avec la liste nominative des hashes et
    sujets sinon (classes `.message-purge-rejet--ok`/`--danger`, remplacent
    `.avertissement-purge-rejet`). L'explication détaillée (ce que font
    `git reflog expire --expire=now --all` et `git gc --prune=now`, ce qui
    reste récupérable sans la case) est reléguée dans un bloc repliable
    « Pourquoi ? » (`<details>` imbriqué) à l'intérieur du panneau.
  - **Libellé raccourci** : « Purger définitivement le commit rejeté
    (irréversible, concerne tout le dépôt) », sur une seule ligne, sans
    commande git visible en permanence (déplacées dans le bloc « Pourquoi ? »)
    — corrige aussi la coupure désordonnée des commandes au milieu du
    libellé à largeur réduite (70 %).
  - La confirmation forte au clic sur « Rejeter » rappelle maintenant, en
    première ligne de son avertissement (visible même si le panneau était
    replié au moment du clic), « 🔴 PURGE DÉFINITIVE activée » suivi du nom
    des branches visées, quand la case est cochée — avant, ce rappel était
    ajouté en fin de ligne, moins visible.
  - `RELECTURE_WEB_DOC.md` section 9 (ligne « Rejeter (sans fusionner) ») :
    paragraphe ajouté décrivant le décochage systématique et le nouveau
    format de message.

## Issue #101 — 2026-10-05

- `relecture_web` : suite de l'issue #99, deux défauts d'aspect restants
  dans le panneau repliable « 📄 .gitignore », constatés en usage réel
  (navigateur à 70 %). Deux changements, aucun changement de comportement
  (mêmes routes, mêmes confirmations, même commit limité au `.gitignore`) :
  - Boutons « Ne plus suivre » de taille inégale selon la longueur du
    chemin (le libellé se coupait en deux lignes sur un chemin long,
    rendant le bouton plus haut et plus étroit que ceux des chemins
    courts) — `static/style.css` : `white-space: nowrap` ajouté sur
    `.bouton--ne-plus-suivre`, qui avait déjà `flex-shrink: 0` depuis
    l'issue #99 mais pouvait quand même se faire comprimer et renvoyer à
    la ligne en l'absence de cette propriété. Le chemin à gauche
    (`.chemin-fichier`) garde, lui, le droit de passer à la ligne
    (`overflow-wrap: anywhere`, inchangé).
  - Remplacement de l'ancienne croix rouge discrète `✕` (retrait d'un
    motif du `.gitignore`) par un vrai bouton de la même famille visuelle
    que les autres boutons du panneau (« Ajouter au .gitignore »,
    « Ignorer », « Ne plus suivre »), libellé « Retirer » :
    `templates/projet.html` passe les classes `bouton-retirer-gitignore`
    → `bouton bouton--supprimer bouton-retirer-gitignore` et le texte `✕`
    → `Retirer` ; `static/style.css` retire le style ad hoc (texte rouge
    nu, soulignement au survol) devenu inutile au profit des classes
    `.bouton`/`.bouton--supprimer` déjà utilisées pour « Ne plus suivre »,
    en ne gardant que `flex-shrink: 0` et `white-space: nowrap` pour que
    le bouton reste sur une seule ligne, à la même position qu'aujourd'hui
    (juste après le motif). Mêmes comportements qu'avant : confirmation
    légère identique, mêmes `data-motif`/`data-commande`, mêmes routes
    Flask (seul le commentaire de `retirer_motif_gitignore_route` dans
    `app.py` est mis à jour pour refléter le nouveau libellé).
  - Vérifié qu'aucune autre croix `✕` du même type ne subsiste dans le
    panneau `.gitignore` (recherche dans tout `relecture_web/`) ; la seule
    autre occurrence est le bouton « vider le résultat » de la page
    Conflit (`.fleche--vider`), hors périmètre de cette issue, non touché.
  - `RELECTURE_WEB_DOC.md` mis à jour : la ligne « Ajouter un motif au
    .gitignore » du tableau d'actions mentionnait encore « bouton ✕ sur
    la ligne », corrigée en « bouton « Retirer » sur la ligne ».
  Vérifié par rendu du template réel (CSS + structure HTML identiques à
  la prod) avec Chromium headless : captures d'écran avant/après
  confirmant que les deux boutons « Ne plus suivre » (chemin long et
  chemin court) ont désormais exactement la même hauteur, et que le
  nouveau bouton « Retirer » s'affiche au même endroit qu'avant
  (immédiatement après le motif, sans décalage de mise en page), aussi
  bien sur un motif court que sur un motif très long forçant un retour à
  la ligne du texte.

## Issue #99 — 2026-10-05

- `relecture_web` : correction de la mise en page de l'avertissement
  « fichiers déjà suivis » du panneau repliable « 📄 .gitignore » (issue
  #98), constatée en usage réel (navigateur à 70 %) — le `<li>` d'une
  ligne motif est une rangée flex (motif + ✕ + avertissement), si bien que
  l'avertissement restait écrasé dans une colonne étroite à côté du motif
  au lieu d'occuper toute la largeur du panneau, les fichiers suivis
  concernés s'enchaînaient en ligne séparés par des virgules, et les
  chemins longs débordaient à droite hors du panneau faute de point de
  coupure autorisé. Deux changements :
  - `templates/projet.html` : la liste des fichiers suivis par motif passe
    d'une suite de `<span>` inline séparés par `, ` à une vraie liste
    (`<ul class="liste-gitignore-fichiers-suivis">`, un `<li
    class="gitignore-fichier-suivi">` par fichier) — aucun changement
    d'action, de confirmation ou de donnée affichée, uniquement la
    structure du balisage.
  - `static/style.css` : `.ligne-gitignore` passe en `flex-wrap: wrap` et
    `.avertissement-gitignore-suivi` prend `flex-basis: 100%` pour forcer
    son retour à la ligne sous le motif, en pleine largeur du panneau ;
    chaque `.gitignore-fichier-suivi` s'affiche en rangée
    `justify-content: space-between` (chemin à gauche, bouton « Ne plus
    suivre » à droite, sans séparateur) ; `overflow-wrap: anywhere` sur
    les chemins (`.chemin-fichier`, `min-width: 0` sur le conteneur flex)
    permet la coupure des chemins longs sans espace, pour qu'ils ne
    débordent jamais du panneau. Même traitement appliqué par cohérence à
    la liste « Non suivis et non ignorés » du même panneau (fichiers non
    trackés), qui présentait le même risque de débordement sur un chemin
    long.
  Vérifié par rendu du template avec un chemin volontairement très long
  et capture d'écran (Chromium headless) à largeur pleine et à largeur
  réduite (~70 %) : l'avertissement occupe la largeur du panneau, chaque
  fichier suivi est sur sa propre ligne, et aucun débordement horizontal
  n'apparaît dans le panneau. Aucun changement de comportement : mêmes
  actions, mêmes confirmations, mêmes données.

## Issue #98 — 2026-10-05

- `relecture_web` : nouveau panneau repliable « 📄 .gitignore » sur la page
  projet (même principe que le panneau « Options de rejet » de l'issue
  #97), fermé par défaut, qui agit sur le `.gitignore` à la racine du
  worktree **principal** du projet (jamais ceux des worktrees de CCL, pas
  de `.gitignore` imbriqué). Trois actions :
  - **Ajouter** un motif (champ texte, ou raccourci « Ignorer » depuis la
    liste des fichiers/dossiers non suivis et non ignorés du dépôt, même
    source que le garde-fou Merger de l'issue #74) — validé avant écriture
    (une seule ligne, non vide, pas de doublon exact) ; `/` final ajouté
    automatiquement si le motif désigne un dossier existant du projet.
  - **Retirer** un motif existant (bouton ✕, jamais sur une ligne
    commentaire/vide) — confirmation légère, index et texte revérifiés
    côté serveur contre l'état actuel du fichier avant toute suppression.
  - **Ne plus suivre** (`git rm --cached`) un fichier déjà suivi qui
    correspond à un motif (piège connu de git : ajouter un motif n'arrête
    jamais de suivre un fichier déjà suivi) — jamais automatique,
    confirmation forte, bouton explicite affiché dès qu'un motif
    correspond à un fichier suivi (`git ls-files -i -c --exclude=<motif>`).
  Chaque action modifiant le fichier le committe elle-même, portée stricte
  au seul `.gitignore` (jamais `-a`/`-A`, même principe que le commit
  CHANGELOG de l'issue #74) — nécessaire pour ne jamais bloquer le
  garde-fou Merger de l'issue #74 sur une modification non committée.
  Refus commun aux trois actions, avant toute lecture : projet distant (PC
  fixe CCW, #94 — surface hors-git non traitée), fusion en cours
  (`MERGE_HEAD`), badge « ⚠ CCL travaille ici » actif sur le worktree
  principal, ou `.gitignore` déjà modifié de façon non committée d'origine
  extérieure (jamais embarqué silencieusement dans le commit automatique).
- `git_info.py` : nouvelles fonctions `chemin_gitignore`,
  `lire_lignes_gitignore`/`ecrire_lignes_gitignore` (préservent l'ordre,
  les commentaires et les fins de ligne du fichier existant),
  `classifier_ligne_gitignore`, `ajouter_motif_gitignore`,
  `committer_gitignore`, `gitignore_a_des_modifications_non_committees`,
  `get_fichiers_suivis_correspondant` (simule l'effet d'un motif via
  `git ls-files -i -c --exclude=`, même moteur de correspondance que git),
  `retirer_du_suivi` et `get_fichiers_non_suivis`. `retirer_du_suivi` ne
  committe pas avec un pathspec comme `committer_gitignore` : une fois le
  fichier redevenu non suivi par `rm --cached`, `git commit -- <chemin>`
  répond « rien à valider » au lieu de committer la suppression pourtant
  déjà indexée (vérifié) — un commit sans pathspec est utilisé à la place,
  mais seulement si l'index est déjà vide avant le `rm --cached`, pour
  garantir qu'aucun autre changement tiers n'est embarqué.
- `RELECTURE_WEB_DOC.md` section 9 : une ligne par action (ajout,
  suppression, ne plus suivre) avec son niveau de confirmation, et note
  sur le commit automatique limité au `.gitignore` et le refus commun aux
  trois actions.

## Issue #97 — 2026-10-03

- `relecture_web` : les options propres au bouton « Rejeter (sans
  fusionner) » (case « Purger réellement le(s) commit(s) rejeté(s) » et son
  avertissement nominatif, issue #96) passent dans un panneau repliable
  (`<details>`/`<summary>` « Options de rejet », à côté du bouton Rejeter),
  replié par défaut — les boutons habituels du panneau d'actions (Push,
  Merger, Supprimer, Rejeter, Comparer la sélection, etc.) restent affichés
  en permanence, inchangés. Le panneau s'ouvre automatiquement (et refuse
  de se refermer) tant que la case « Purger » est cochée à l'intérieur,
  pour ne jamais la cocher puis la perdre de vue en repliant par erreur ;
  la confirmation forte au clic sur Rejeter continue de refléter l'état
  réel de la case, que le panneau soit ouvert ou replié au moment du clic.
- Retrait entier de la case « Fermer aussi l'issue GitHub correspondante »
  et de son champ « raison » associé (bouton Rejeter, issue #95) : en usage
  normal, l'issue GitHub correspondant à un worktree est déjà fermée par le
  watcher CCL dès la fin de son traitement (label `done`), bien avant qu'un
  rejet n'intervienne — cette case ne servait quasiment jamais et ajoutait
  de la confusion pour ce cas marginal (issue restée ouverte par exception).
  Toute la logique associée côté `rejeter_worktrees_route` (vérification
  d'état puis `gh issue close`) est retirée avec elle. La logique de
  purge/nettoyage `Non_Lu/` (issue #96), sans rapport avec ce retrait, est
  conservée telle quelle.
- `git_info.py` : `get_etat_issue_github`, `fermer_issue_github` et
  `numero_issue_depuis_nom_branche` supprimées — plus aucun appelant après
  ce retrait (`extraire_numero_issue`, dont dépendait la troisième, reste
  utilisée ailleurs et n'est pas touchée).
- `RELECTURE_WEB_DOC.md` section 9 (ligne « Rejeter (sans fusionner) ») :
  retrait de la mention de fermeture d'issue GitHub, description du
  panneau repliable ajoutée.

## Issue #96 — 2026-10-02

- `relecture_web` : complément au bouton « Rejeter (sans fusionner) »
  (issue #95) — nouvelle case à cocher « Purger réellement le(s) commit(s)
  rejeté(s) », décochée par défaut. Constat fait en testant le geste manuel
  équivalent (chesscoach, worktree-issue-88) : `git branch -D` seul ne fait
  que détacher la branche, le commit reste récupérable via le reflog (90
  jours par défaut) et continue d'apparaître comme commit orphelin
  « ambigu » dans le diagnostic automatique — risque qu'un futur clic sur
  « Sécuriser tous les commits orphelins » l'embarque par erreur alors
  qu'Alain vient justement de décider de s'en débarrasser.
- `git_info.purger_reflog_et_gc` : `git reflog expire --expire=now --all`
  puis `git gc --prune=now`, déclenchée une seule fois après la boucle de
  rejet (jamais par branche) pour n'exécuter qu'un seul `gc` (coûteux) par
  clic. Ces deux commandes sont **globales au dépôt** — aucune option git
  ne permet de n'expirer/purger que le reflog d'une branche déjà supprimée
  — donc tout autre commit orphelin non sécurisé présent par ailleurs dans
  le dépôt serait aussi détruit. Aucune purge ciblée plus fine n'étant
  possible avec les commandes git disponibles, ce comportement est
  documenté explicitement plutôt qu'implémenté à l'aveugle : la case ne
  déclenche la purge qu'après confirmation explicite d'Alain (jamais en
  arrière-plan), et l'avertissement de confirmation liste nommément les
  autres commits orphelins non sécurisés qui seraient perdus en même
  temps (`projet.orphelins_non_securises_menaces`), pour qu'Alain sache ce
  qu'il perd en plus du commit qu'il rejette.
- `git_info.get_hashes_commits_non_fusionnes` (pendant de
  `get_nombre_commits_non_fusionnes` qui retourne les hashes plutôt qu'un
  compte) : capture les hashes propres à chaque branche rejetée **avant**
  le `branch -D`, la plage `principale..branche` ne se résolvant plus une
  fois la branche supprimée.
- `git_info.commit_existe` (`git cat-file -e <hash>^{commit}`) : revalide
  après la purge qu'un commit a réellement disparu avant de nettoyer son
  résumé, plutôt que de le supposer.
- Second résidu constaté lors du même test manuel : même après purge
  réelle du commit, le diagnostic de commits orphelins continuait à
  l'afficher comme « ambigu », car les fichiers résumé déposés par le hook
  post-commit (`Non_Lu/<hash>_*`) survivent à la suppression du commit — le
  diagnostic s'appuie sur leur présence sans revalider que le hash existe
  encore. Le bouton « Rejeter » supprime donc désormais, pour tout commit
  confirmé purgé (ciblé ou collatéral), ses fichiers `Non_Lu/` associés via
  `lister_fichiers_resumes_hash`/`_supprimer_fichiers` (déjà utilisés par
  « Supprimer la/les branche(s) de récupération » et « Nettoyer tous les
  projets »).
- Revalider plus généralement, dans le diagnostic de commits orphelins
  lui-même, qu'un hash trouvé dans `Non_Lu/` existe toujours dans le dépôt
  avant de le lister (plutôt que d'afficher un résumé obsolète comme
  « ambigu ») reste hors périmètre de cette issue — signalé ici comme
  amélioration possible, non traitée : le nettoyage explicite fait par le
  bouton Rejeter couvre le cas concret qui a motivé l'issue.
- Confirmation forte adaptée : cochée, elle rappelle que la purge est
  irréversible et globale, affiche la commande équivalente complète, et
  indique le nombre d'autres commits orphelins non sécurisés qui seraient
  détruits en même temps.
- `RELECTURE_WEB_DOC.md` (section 9, ligne « Rejeter (sans fusionner) »)
  mise à jour en conséquence.

## Issue #95 — 2026-10-02

- `relecture_web` : nouveau bouton « Rejeter (sans fusionner) » sur la page
  « branches d'un projet », pour supprimer un worktree et sa branche sans
  jamais tenter de les fusionner — cas réel : CCL signale lui-même que son
  travail fait doublon avec une autre issue déjà traitée, et que fusionner
  créerait des conflits inutiles. Jusqu'ici, seule une commande manuelle en
  terminal permettait ce geste.
- Garde-fou strictement inverse de « Supprimer la/les branche(s)
  fusionnée(s) » : refuse d'agir sur la branche principale, **et** refuse
  toute branche confirmée fusionnée (message flash renvoyant vers
  « Supprimer » dans ce cas). Même mécanique de suppression (`git worktree
  remove` puis `git branch -D`, ou `git branch -D` seule si le worktree a
  déjà été retiré).
- Confirmation forte dédiée (bandeau rouge, bouton nommé explicitement —
  ex. « Rejeter worktree-issue-88 », focus par défaut sur Annuler) avec un
  avertissement affichant, pour chaque branche concernée, le nombre de
  commits jamais fusionnés (`git log <branche principale>..<branche>`) —
  `git_info.get_nombre_commits_non_fusionnes` — pour que l'ampleur du
  travail perdu soit visible avant de confirmer une suppression réelle et
  définitive.
- Fermeture optionnelle de l'issue GitHub correspondante (case à cocher +
  champ de raison libre pour le commentaire) : numéro extrait du nom de la
  branche `worktree-issue-<N>` ou, à défaut, du sujet de son dernier commit
  (`git_info.numero_issue_depuis_nom_branche`), fermeture seulement si
  l'issue apparaît encore ouverte via `gh issue view`
  (`git_info.get_etat_issue_github` / `fermer_issue_github`) — n'agit pas si
  elle est déjà fermée (cas normal, le watcher CCL la ferme déjà lui-même).
  Cette vérification/fermeture via `gh` est volontairement isolée de la
  suppression du worktree : un échec (gh absent, non authentifié, pas de
  remote GitHub) est seulement rapporté à part, jamais bloquant —
  `relecture_web` ne dépend donc jamais de `gh`/GitHub pour sa fonction
  principale.
- Nouvelle route `/projet/<nom_projet>/rejeter`
  (`rejeter_worktrees_route`, `app.py`), nouvelles fonctions `git_info.py` :
  `get_nombre_commits_non_fusionnes`, `numero_issue_depuis_nom_branche`,
  `get_etat_issue_github`, `fermer_issue_github`.
- `RELECTURE_WEB_DOC.md` section 9 : nouvelle ligne « Rejeter (sans
  fusionner) » documentant le garde-fou et le niveau de confirmation.

## Issue #94 — 2026-09-28

- `relecture_web` : routage local/distant des commandes git vers le PC
  fixe Windows (CCW) via SSH — étape 2 du pilotage des projets CCW depuis
  `relecture_web` (diagnostic issue #91), sur le socle de centralisation
  posé par l'issue #93 (`_lancer_git`). Limité aux commandes git
  elles-mêmes, comme demandé par l'issue.
- Nouveau fichier `relecture_web/ccw_host.conf` (même convention que
  `branches_cibles.conf`) : `ccw_host = utilisateur@hôte` (obligatoire) et
  `ccw_key = <chemin>` (optionnel, défaut `~/.ssh/ccl_ccw`). Tant que
  `ccw_host` n'est pas renseigné, aucune commande distante n'est tentée
  (échec propre, message clair) — fichier livré avec les deux entrées
  commentées, à renseigner par Alain.
- `git_info.py` : `est_projet_distant` (heuristique `^[A-Za-z]:\\` sur
  `repertoire`), `charger_config_ccw`, `_lancer_git_distant`,
  `tester_connectivite_ccw`, `commande_affichee`. `_lancer_git` route
  désormais vers l'exécution locale ou distante (SSH) selon
  `est_projet_distant(repertoire)`, en conservant la même interface de
  retour (`subprocess.CompletedProcess` : code de retour, stdout,
  stderr) — aucun appelant existant n'a eu besoin d'être adapté à cette
  distinction.
- SSH : `ConnectTimeout=6` + `BatchMode=yes` + `StrictHostKeyChecking=
  accept-new`, en plus du timeout applicatif existant
  (`TIMEOUT_GIT`/`TIMEOUT_GIT_LONG`/`TIMEOUT_RESEAU`) — un PC fixe éteint
  échoue vite plutôt que de bloquer le serveur Flask de développement
  (mono-thread).
- Échappement des chemins Windows (`_quoter_argument_distant`) :
  guillemets doubles dès qu'un argument contient un espace, forme
  acceptée aussi bien par `cmd.exe` que par un shell POSIX (Git Bash) —
  le shell distant réel n'ayant pas pu être confirmé par le diagnostic
  #91. Chaque commande git est envoyée seule (jamais enchaînée par `&&`
  au shell distant) : les enchaînements existants
  (`fusionner_worktree` : checkout/merge/checkout retour ;
  worktree remove puis branch -D) le faisaient déjà via des appels
  `_lancer_git` séparés, pas via un `&&` shell — comportement inchangé,
  donc déjà robuste au shell distant réel.
- Commandes prévisualisées à Alain avant confirmation
  (`commande_affichee`) : préfixées par la commande `ssh` réellement
  exécutée pour un projet distant (push, merge, merger-et-supprimer,
  suppression de branche/worktree, revert, sécurisation, finalisation de
  merge), inchangées pour un projet local. Un seul préfixe `ssh` en tête
  des aperçus combinés (« Merger et supprimer », suppression worktree +
  branche), même si plusieurs commandes git sont réellement envoyées
  séparément derrière.
- `collect_etat_projets` : nouveau statut `"injoignable"` (distinct de
  `"introuvable"`, réservé aux projets locaux) pour un projet distant dont
  le PC fixe ne répond pas à un test de connectivité SSH borné
  (`tester_connectivite_ccw`), testé avant toute tentative de commande
  git — sur le modèle du test `os.path.isdir` déjà en place pour les
  projets locaux. `index.html`/`projet.html` affichent alors « 🔌 PC fixe
  éteint ou injoignable — projet indisponible pour le moment » ;
  `_projet_pret` (`app.py`) refuse toute action avec le même message
  flash — même comportement dégradé que l'existant (branches/
  diagnostics/conflits indisponibles), jamais de page cassée.
- Vérifié bout en bout sur ce worktree (aucun accès au PC fixe réel
  nécessaire) : un faux exécutable `ssh` placé en tête de `PATH` (ignore
  les options de connexion, exécute la commande git assemblée via
  `sh -c`) simule un projet distant joignable, avec un `repertoire`
  fictif `C:\CCW\Projet Test` (nom contenant un espace, comme demandé par
  l'issue) pointant en réalité vers un dépôt git local — `_lancer_git`,
  `tester_connectivite_ccw`, `commande_affichee` et `collect_etat_projets`
  testés directement en Python, résultats conformes (log/branche lus à
  travers le routage SSH simulé, aperçu de commande correctement préfixé,
  statut `"ok"`). Cas hôte injoignable testé séparément avec le vrai
  binaire `ssh` pointé vers une IP non routable (`192.0.2.1`,
  TEST-NET-1) : `tester_connectivite_ccw` retourne `False` en ~3s
  (`ConnectTimeout` respecté, aucun blocage) et `collect_etat_projets`
  renvoie bien le statut `"injoignable"`. Cas `ccw_host` non configuré
  testé aussi : échec propre et immédiat, sans tentative de connexion.
- Documentation : nouvelle section 11 de `RELECTURE_WEB_DOC.md` (« Le
  mode SSH vers le PC fixe Windows (CCW, issue #94) »), ancienne section
  11 renumérotée 12 sans changement de contenu.
- Hors périmètre (suivi à prévoir, comme prévu par l'issue) : résolution
  de conflit sur un fichier distant, exécution distante de
  `scripts/fusionner_changelog.py`, équivalent Windows du badge « CCL
  travaille ici » (issue #88) pour un worktree distant.

## Issue #93 — 2026-09-28

- Refactor (`relecture_web/git_info.py`) : centralise derrière
  `_lancer_git` la quinzaine de fonctions qui exécutaient encore leur
  propre `subprocess.run(["git", "-C", ...])` en contournant ce point
  commun (`get_rapport_cherry_brut`, `get_patch_id_commit`,
  `trouver_commit_correspondant`, `get_diff_entre_commits`,
  `securiser_commit_orphelin`, `fusionner_worktree`, `supprimer_worktree`,
  `supprimer_branche`, `supprimer_branche_recuperation`, `revert_commit`,
  `pousser_branche`, `verifier_push_apres_timeout` (partie `git
  ls-remote`), `finaliser_commit_merge`) — `retraiter_fichier_conflit`
  passait déjà par `_lancer_git`, rien à y changer.
- `_lancer_git` a été étendu avec deux paramètres optionnels pour couvrir
  les usages qui ne s'y prêtaient pas encore : `timeout` (les appels à
  durée longue — push, merge, commit --no-edit — ou réseau — ls-remote —
  gardent leur délai propre, `TIMEOUT_GIT_LONG`/`TIMEOUT_RESEAU`, au lieu
  du défaut `TIMEOUT_GIT`) et `entree` (texte transmis sur l'entrée
  standard, pour les pipes entre deux commandes git — `git show`/`git
  log -p` vers `git patch-id`, dans `get_patch_id_commit` et
  `trouver_commit_correspondant`).
- Aucun changement de comportement observable : mêmes commandes, mêmes
  codes de retour, mêmes messages d'erreur, mêmes timeouts — vérifié par
  test manuel sur un dépôt git temporaire (worktree, merge, push vers un
  remote local, conflit + finalisation de merge, branches de récupération,
  et les deux cas de pipe patch-id comparés à la commande brute).
- `fusionner_changelog_worktree` : son `git add`/`git commit` passaient
  déjà par `_lancer_git` avant cette issue ; seul son appel au script
  externe `scripts/fusionner_changelog.py` reste un `subprocess.run`
  distinct (ce n'est pas une commande git) — un commentaire dans le code
  signale désormais explicitement cette deuxième surface d'exécution,
  hors du périmètre de ce refactor.
- Prépare le terrain pour une future issue de routage local/SSH des
  commandes git (diagnostic de l'issue #91) : tout appel git de ce module
  passe maintenant par ce point d'entrée unique.

## 2026-09-28 — issue #92 (relecture_web)

`relecture_web` n'avait jusqu'ici aucune authentification, en écoute
stricte sur `127.0.0.1` — un choix assumé tant que l'outil restait
strictement local, mais un préalable bloquant avant d'envisager un jour un
accès réseau (LAN, ou exposition externe pour piloter un futur PC fixe
Windows) : `relecture_web` peut déclencher merge, push, suppression de
branches et de worktrees, un enjeu plus grand que `new_issue.py` à l'époque
où il n'avait lui non plus aucune protection.

- **Ajout — `relecture_web/auth.py`** : mot de passe haché en sha256
  (`relecture_web/mot_de_passe.conf`, jamais en clair, permissions 0600,
  gitignoré), comparaison en temps constant (`hmac.compare_digest`),
  `SECRET_KEY` Flask persistée (`relecture_web/secret_key.conf`, même
  protection) et génération d'un certificat auto-signé via `openssl`
  (`relecture_web/ssl/`, généré une seule fois puis réutilisé). Aucun code
  partagé avec `bridge_agent`/`new_issue.py` — même principe, implémentation
  propre à ce dépôt.
- **Ajout — `--set-password`** (`app.py`) : demande le mot de passe deux
  fois (confirmation, saisie masquée via `getpass`), puis quitte sans
  lancer le serveur.
- **Ajout — modes `--lan` / `--externe`** (`app.py`), mêmes noms que
  `bridge_agent` pour la cohérence : par défaut inchangé (`127.0.0.1`,
  HTTP, mot de passe jamais exigé) ; `--lan` (`0.0.0.0`, HTTP, sans mot de
  passe, réseau de confiance) ; `--externe` (`0.0.0.0`, HTTPS obligatoire,
  mot de passe obligatoire — refuse de démarrer sans mot de passe configuré,
  avec message clair). `--lan` et `--externe` sont mutuellement exclusifs
  (erreur explicite `argparse`).
- **Ajout — décorateur `@login_requis`** appliqué à toutes les routes
  existantes (`app.py`) : transparent tant que le mode courant n'exige pas
  de mot de passe (défaut, `--lan`), redirige vers `/connexion` sinon
  (`--externe` uniquement).
- **Ajout — routes `/connexion` et `/deconnexion`**, template
  `templates/connexion.html` (page autonome, hors barre latérale) et
  styles associés (`static/style.css`).
- **Session persistante** : `PERMANENT_SESSION_LIFETIME` fixé à 30 jours,
  `session.permanent = True` posé à la connexion réussie — une session
  survit désormais aux redémarrages fréquents de `relecture_web` (usage non
  permanent, relancé manuellement à chaque merge d'issue) sans devenir
  illimitée.
- **Doc** : `RELECTURE_WEB_DOC.md` (section « Lancement et modes réseau »)
  et `relecture_web/README.md` mis à jour — la mention « usage strictement
  local, aucune authentification » ne décrivait plus que le mode par défaut.
- **Hors périmètre** (rappel explicite de l'issue) : le mode SSH vers un
  futur PC fixe Windows (issue #91) n'est pas traité ici — cette issue pose
  seulement l'authentification, prérequis avant d'envisager un jour une
  exposition réelle. Le host d'écoute par défaut ne change pas.

## 2026-09-26 — issue #90 (relecture_web)

Sur la page Conflit, cliquer sur la flèche bleue puis sur la flèche orange
remplaçait le résultat au lieu de l'ajouter — impossible de garder les deux
versions l'une après l'autre, un cas fréquent (deux ajouts indépendants au
même endroit). Par ailleurs, transmettre le contenu d'un gros bloc de
conflit à Claude Chat obligeait à une capture d'écran, imprécise.

- **Ajout — « Garder les deux »** (`templates/conflit.html`) : quatrième
  flèche (⇅, violette) dans le groupe bleu/orange/✕ de chaque bloc. Place
  le contenu HEAD puis celui de la branche entrante à la suite dans le
  `<textarea>` du résultat, avec un saut de ligne entre les deux uniquement
  si le texte HEAD n'en a pas déjà un en fin. Les flèches bleue et orange
  restent des remplacements complets, inchangées.
- **Ajout — « Copier ce bloc »** (`templates/conflit.html`,
  `static/style.css`) : bouton `.bouton-copier` (📋) en coin haut-droit de
  chaque bloc du panneau gauche (lecture seule), copiant tout le texte
  affiché du bloc — en-têtes `<<<<<<<`/`>>>>>>>` et contenu des deux côtés
  compris, tel qu'affiché à l'écran — via le mécanisme `.bouton-copier`
  déjà utilisé ailleurs dans `relecture_web` (retour visuel bref identique).
- **`git_info.py`** : nouvelle fonction `_texte_affiche_bloc`, et nouveau
  champ `texte_affiche` par segment de conflit dans `_extraire_blocs_conflit`
  — précalcule côté serveur le texte exact du panneau gauche pour un bloc
  donné, avec la même règle de saut de ligne que « Garder les deux »
  (jamais de ligne vide dupliquée entre les deux moitiés).
- Le marqueur `=======` d'un conflit brut n'a volontairement pas été
  réintroduit dans l'affichage ni dans le texte copié : le panneau gauche
  remplaçait déjà ce séparateur par l'en-tête `>>>>>>> <branche>` au-dessus
  du contenu de la branche entrante (issue #59), qui joue le même rôle de
  repère visuel sans perdre le nom de la branche — copier « tel qu'affiché »
  respecte ce choix existant plutôt que de le contredire silencieusement.
- **Doc** : `RELECTURE_WEB_DOC.md` section 10 complétée avec les deux
  nouveaux boutons.
- Vérifié : `python3 -m py_compile git_info.py app.py` OK ; sortie de
  `_extraire_blocs_conflit`/`_texte_affiche_bloc` testée manuellement sur un
  conflit simple et sur un bloc à côté HEAD vide (cas des deux ajouts
  indépendants) — aucune ligne vide dupliquée dans les deux cas. Pas de
  suite de tests automatisés existante pour `relecture_web` à étendre.

## 2026-09-26 — issue #89 (relecture_web)

`lire_verrous_actifs` (`git_info.py`, ajoutée par #88) découpait le contenu
de chaque fichier `.lock` par `splitlines()` en supposant une paire
`clé=valeur` par ligne, avec un `partition("=")` ne coupant qu'au premier
signe `=`. En réalité, Bridge_Agent écrit tous les champs d'un verrou sur
une seule ligne séparés par des espaces (ex. `pid=213661 projet=bridge_agent
mode=ecriture rep=/home/alain/bridge_agent-issue649 claude_pgid=214244`) :
sur une seule ligne, `champs["pid"]` récupérait donc toute la fin de la
ligne au lieu du seul numéro, `_pid_vivant` échouait systématiquement, et
`lire_verrous_actifs` retournait toujours une liste vide — le badge « ⚠ CCL
travaille ici » (issue #88) ne s'affichait donc jamais, quel que soit
l'état réel des tâches. Confirmé en conditions réelles (trois worktrees
Bridge_Agent, verrous actifs lus = `[]` côté relecture_web).

- **Fix** (`git_info.py`, `lire_verrous_actifs`) : chaque ligne du fichier
  est d'abord découpée sur les espaces (`ligne.split()`) pour isoler les
  jetons `clé=valeur` individuels, avant de les répartir avec
  `partition("=")` — accepte aussi bien le format réel (tout sur une seule
  ligne) qu'un éventuel format à une paire par ligne, au cas où Bridge_Agent
  évoluerait. `_lignes_deja_pris_watcher` (citée dans le docstring comme
  suivant le même principe) ne fait qu'un test de sous-chaîne `"déjà pris"
  in ligne` — elle ne parse aucune paire `clé=valeur` et n'était pas
  concernée par ce bug.
- **Pourquoi les tests manuels de l'issue #88 ne l'ont pas détecté** : ils
  utilisaient apparemment un fichier `.lock` de test à une paire par ligne
  (`pid=...\nrep=...\nmode=...`), un format qui fonctionnait déjà avec
  l'ancien code — la documentation elle-même (`RELECTURE_WEB_DOC.md`)
  décrivait ce format à tort (« une ligne `pid=<pid>` et une ligne
  `rep=<chemin>` »), sans jamais avoir été confrontée à un vrai fichier
  généré par Bridge_Agent. Corrigée en conséquence.
- Revérifié manuellement les trois scénarios demandés : verrou à une seule
  ligne avec pid vivant → `rep=` retrouvé et `worktree_ccl_actif` renvoie
  `True` pour ce chemin ; pid mort → liste vide ; ancien format à une paire
  par ligne → toujours accepté (non-régression).
- `RELECTURE_WEB_DOC.md` mise à jour (section badges) pour décrire le
  format réel du fichier de verrou.

## 2026-09-26 — issue #88 (relecture_web)

Jusqu'ici, fusionner une branche puis supprimer son worktree sont deux clics
séparés — le second sûr techniquement (`git worktree remove` refuse de
lui-même s'il reste des modifications non commitées, et la suppression
revérifie elle-même à l'instant du clic que la branche est un ancêtre de la
cible), mais avec un vrai risque non couvert : qu'une tâche CCL travaille
encore dans ce worktree (reprise après redémarrage, cf. l'incident #73/#609
sur Bridge_Agent), auquel cas le supprimer romprait sa tâche.

- **Détection d'un worktree où CCL travaille** (`git_info.py`,
  `lire_verrous_actifs`/`worktree_ccl_actif`) : lit les fichiers de verrou
  actifs de Bridge_Agent (`logs/verrous/*.lock`, lignes `pid=`/`rep=`/`mode=`
  — `mode=` ajouté par #609 côté Bridge_Agent), ne retient un verrou que si
  son `pid` correspond à un processus toujours vivant (`os.kill(pid, 0)`),
  et compare son `rep=` au chemin réel du worktree d'une branche. Dégrade
  proprement à liste vide (aucune erreur) si Bridge_Agent n'est pas installé
  au même endroit ou si `logs/verrous/` est inaccessible.
- **Badge rouge « ⚠ CCL travaille ici »** affiché sur la branche concernée,
  dans la page projet, visible avant toute action — simple signal, comme le
  badge « worktree orphelin » existant : n'empêche pas de cliquer sur Merger
  seul (l'utilisateur peut savoir ce qu'il fait), mais le nouveau bouton
  combiné ci-dessous refuse d'agir tant qu'il est actif.
- **Nouveau bouton « Merger et supprimer »** (`app.py`,
  `merger_et_supprimer_route`) : à côté des boutons Merger et Supprimer la/les
  branche(s) fusionnée(s) existants (inchangés), enchaîne les deux dans le
  même clic — mêmes conditions d'éligibilité que le Merger seul aujourd'hui
  (branche pas la cible, pas de contenu doublons uniquement), plus le refus
  explicite (message flash) si le badge ci-dessus est actif pour la branche.
  Si le merge échoue (conflit, timeout non confirmé abouti, erreur), aucune
  suppression n'est tentée — comportement identique à aujourd'hui. Si le
  merge réussit mais que la suppression échoue ensuite (modifications non
  commitées détectées entre-temps par git, cas rare mais réel), les deux
  résultats sont rapportés séparément dans le message flash. Confirmation
  légère unique pour l'ensemble, décrivant les deux étapes.
- Testé de bout en bout sur des dépôts git temporaires avec un faux
  Bridge_Agent (verrou actif avec un pid réellement vivant, puis pid
  terminé) : badge affiché seulement avec verrou actif, bouton combiné
  refusé avec verrou actif (rien touché), accepté et fonctionnel une fois
  le verrou levé (merge + suppression du worktree et de la branche
  confirmés), et Merger seul vérifié toujours autorisé malgré le badge actif.
- Documentation : `RELECTURE_WEB_DOC.md` section 4 (nouveau badge) et
  section 9 (nouvelle ligne « Merger et supprimer »).

## 2026-09-26 — issue #87 (relecture_web)

Après un Merger réussi sur chesscoach, l'intégration automatique du
CHANGELOG échouait avec « script introuvable » : `fusionner_changelog_worktree`
(`git_info.py`) cherchait `scripts/fusionner_changelog.py` **dans le dépôt du
projet fusionné**, alors que seuls quelques projets en possèdent une copie —
la plupart, chesscoach compris, n'en ont pas, bien que CCL y crée bien des
`CHANGELOG-<N>.md`.

- **Le script utilisé est désormais toujours celui de relecture_bridge**
  (`git_info.py`, constante `CHEMIN_SCRIPT_FUSION_CHANGELOG`), résolu à partir
  de l'emplacement de `git_info.py` lui-même (un niveau sous la racine de ce
  dépôt, comme `scripts/`) — plus aucune dépendance à une copie présente dans
  le dépôt cible. `--repo <dépôt fusionné>` continue de cibler le bon dépôt.
- **`scripts/fusionner_changelog.py` rendu robuste aux `CHANGELOG.md` d'autres
  projets**, qui ne suivent pas forcément la convention « Convention
  d'ajout : ... » de relecture_bridge (issue #252) : en-tête absent ->
  insertion après le premier titre de niveau 1 (`# ...`) trouvé, ou en tête de
  fichier si aucun titre ; `CHANGELOG.md` absent -> créé avec pour seul
  contenu les entrées fusionnées. Aucune perte de contenu existant dans tous
  les cas — seul le point d'insertion change.
- **Portée du commit d'intégration (issue #74) inchangée** : toujours
  `git add -- CHANGELOG.md CHANGELOG-<N>.md...` puis `git commit -- <mêmes
  chemins>`, jamais `git commit -a`.
- Testé sur des dépôts temporaires : avec l'en-tête habituel (comportement
  identique à avant), sans en-tête mais avec un titre, fichier vide sans
  titre, et `CHANGELOG.md` absent — dans les quatre cas, fusion réussie sans
  perte de contenu. Vérifié aussi de bout en bout via
  `fusionner_changelog_worktree` sur un faux dépôt sans copie locale du
  script, confirmant la disparition du message « script introuvable ».
- Documentation : `RELECTURE_WEB_DOC.md` section 9 (ligne **Merger**) mise à
  jour pour préciser que le script utilisé est celui de relecture_bridge, et
  le comportement selon la forme du `CHANGELOG.md` cible.

## 2026-09-24 — issue #75 (post-commit)

Le hook `post-commit` construisait le nom des fichiers exportés dans
`<projet>/Non_Lu/` à partir du message de commit en remplaçant chaque
caractère non ASCII par un « _ » : un message en français (donc accentué)
donnait un nom quasi illisible, ex. « docs: régénère le tableau des
projets... » devenait `1963797_docs__r__g__n__re_le_tableau_des_projets...`.

- **Translittération des accents avant construction du nom** (`post-commit`) :
  le message de commit passe désormais par `iconv -f utf-8 -t
  ascii//translit` (é → e, à → a, ç → c, œ → oe...) avant le remplacement des
  caractères restants encore hors `[:alnum:]-_` par un « _ » — seul ce qui
  n'a pas d'équivalent ASCII devient un souligné. `iconv` absent de la
  machine : repli silencieux sur le message brut (comportement identique à
  avant l'issue #75 pour ce cas précis).
- **Soulignés en double et de fin de nom évités** : `tr -cs` (squeeze) ramène
  les runs de soulignés consécutifs (produits par exemple par une ponctuation
  suivie d'un espace) à un seul, et un `sed` final retire un éventuel
  souligné terminal — y compris celui que la troncature à 50 caractères
  pouvait faire apparaître en coupant juste après un souligné. Longueur
  maximale du champ message inchangée (50 caractères).
- **Aucun impact sur `relecture_web`** : vérifié dans `git_info.py` et
  `resumes_info.py` — seuls le hash en tête de nom (`_extraire_hash`,
  découpe sur le premier « _ ») et le suffixe (`.diff`, `_resume.md`,
  `_annote.md`) sont exploités ; le contenu du champ « message » n'est
  jamais reparsé.
- **Fichiers déjà exportés inchangés** : aucun renommage rétroactif, seuls
  les futurs exports bénéficient de la translittération.
- **Déploiement** : `installer.sh` déploie le hook par **copie**
  (`cp "$HOOK_SOURCE" "$projet/.git/hooks/post-commit"`), pas par lien
  symbolique — les projets déjà installés gardent l'ancien hook tant que
  `./installer.sh` n'est pas relancé depuis ce dépôt (`relecture_bridge`)
  pour redéployer la version corrigée sur les 8 projets actifs.
- Testé sur un dépôt temporaire (`git init` + commits avec messages
  accentués, incluant un cas avec tiret cadratin et caractères composés) :
  noms de fichiers lisibles, sans double ni souligné final.
- Documentation : `RELECTURE_WEB_DOC.md` section 8 ne détaille pas la règle
  de remplacement de caractères (seulement le motif générique
  `<hash>_<message>.diff`) — rien à mettre à jour de ce côté.

## 2026-09-24 — issue #74 (relecture_web)

Pendant l'issue #73, CCL avait travaillé directement dans le dossier
principal `~/Relecture_Bridge` (repli sur REP_TRAVAIL, worktree dédié déjà
pris) ; l'intégration automatique du CHANGELOG déclenchée par un Merger
avait alors committé tout l'arbre de travail (`git commit -a`), travail
inachevé de CCL compris, sous le message générique « chore: fusionne
CHANGELOG-<N>.md dans CHANGELOG.md (auto) » (commit 0c477c0).

- **Portée du commit d'intégration du CHANGELOG strictement limitée**
  (`fusionner_changelog_worktree`, `git_info.py`) : `git add -- CHANGELOG.md
  CHANGELOG-<N>.md...` puis `git commit -- <mêmes chemins>`, au lieu de
  `git commit -a` — ne committe plus jamais que `CHANGELOG.md` et les
  `CHANGELOG-<N>.md` réellement consommés, quel que soit le reste de
  l'arbre de travail au même moment.
- **Nouveau garde-fou avant Merger** (`get_modifications_non_committees`,
  `git_info.py` ; `merger_branches_route`, `app.py`) : si le dossier de la
  branche cible contient des modifications non committées (fichiers suivis
  modifiés, ou fichiers non suivis non ignorés), le merge est refusé par
  message flash explicite avant même d'être tenté — plutôt que de fusionner
  par-dessus un travail potentiellement en cours.
- **`.gitignore` racine** : remplace l'entrée `Relecture_Bridge/Non_Lu/`
  (spécifique au dossier auto-référentiel de relecture_bridge) par le motif
  générique `*/Non_Lu/`, qui couvre le dossier d'exports en attente de
  lecture de tous les projets (présents et futurs), pour qu'un `git add -A`
  (backup CCL, ou une future fusion mal scopée) ne puisse jamais les
  embarquer dans un commit sans rapport.
- Documentation : `RELECTURE_WEB_DOC.md` section 9 (ligne Merger) mise à
  jour avec le nouveau garde-fou et la portée exacte du commit
  d'intégration du CHANGELOG.

## 2026-09-24 — issue #73 (relecture_web)

Retours d'un test réel complet des issues #69 à #72 sur un conflit
artificiel (projet `ecole`) : plusieurs frictions d'usage regroupées en
une seule issue (mêmes fichiers que #71/#72, dont un conflit de merge
réel entre ces deux-là avait déjà montré l'intérêt de grouper).

- **« Retraiter ce fichier » repositionné et allégé** : le bouton est
  désormais affiché juste à côté de « ✅ Finaliser le merge » (même bloc
  `.ligne-finaliser-merge`) quand tous les fichiers du merge en cours
  sont résolus, au lieu d'une section séparée plus bas ; il reste à côté
  du fichier concerné tant que d'autres fichiers sont encore en conflit.
  Sa confirmation JS est supprimée (action peu risquée : elle ne fait que
  refaire la résolution de ce fichier). Une fois l'action effectuée,
  `relecture_web` amène directement sur la page Conflit du fichier remis
  en conflit plutôt que sur la page projet (`app.py`,
  `retraiter_fichier_conflit_route`).
- **Page Conflit — zones de résultat agrandies** : chaque `<textarea>` du
  panneau droit prend désormais au moins la hauteur du bloc correspondant
  du panneau gauche (`align-items: stretch` sur la grille CSS partagée,
  `style.css`) — sur un gros bloc de conflit (ex. un tableau de
  documentation), l'édition n'est plus pénible dans une zone restée
  minuscule.
- **Page Conflit — bouton Rafraîchir** : même comportement que celui déjà
  présent sur la page projet (simple lien GET vers l'URL courante, jamais
  de resoumission de formulaire) — utile notamment après le refus « le
  fichier a changé depuis l'affichage » de « Traiter tous les blocs »,
  dont le message demande de recharger la page.
- **Confirmations raccourcies et unifiées** (`ouvrirConfirmation`,
  `base.html`, remplace `confirmationForte`) : une seule ligne principale
  au format « Action + objet + projet » (ex. « Merger worktree-issue-72
  dans main — relecture_bridge ») plutôt qu'un long texte explicatif ; un
  avertissement éventuel (ex. bloc(s) au résultat vide pour « Traiter
  tous les blocs ») affiché en premier et mis en évidence, jamais noyé en
  fin de message ; la commande git équivalente conservée en petit texte
  discret sous la ligne principale ; le bouton de validation continue de
  porter le nom de l'action, jamais un OK générique ; focus par défaut
  sur Annuler dans tous les cas. Les confirmations légères (Merger,
  anomalie de « Traiter tous les blocs ») passent désormais par cette
  même fenêtre `relecture_web` en variante neutre (non rouge) plutôt que
  par le `confirm()` natif du navigateur, pour permettre ce format uniforme
  et coloré ; les confirmations fortes (Push, suppressions) gardent leur
  couleur d'alerte rouge (`modal-confirmation--forte`).
- **Couleur d'accent du projet** (`git_info.py` : `normaliser_couleur_hex`,
  `couleur_texte_lisible`) : lecture tolérante d'une colonne « Couleur »
  optionnelle en dernière position du tableau des projets actifs de
  `BRIDGE_AGENT_DOC.md` (hexadécimal), lors du même chargement réseau que
  le reste de la liste — colonne absente, vide ou invalide -> pas de
  couleur, jamais d'erreur (repli en douceur tant que l'issue bridge_agent
  qui ajoute cette colonne n'est pas encore en place). Utilisée comme
  bandeau dans les fenêtres de confirmation, comme chip dans l'en-tête de
  la page projet et de la page Conflit, et comme pastille dans la barre
  latérale — texte noir ou blanc choisi automatiquement pour rester
  lisible sur la couleur configurée (formule de luminance perçue YIQ), afin
  de ne pas confondre deux projets aux noms proches (`bridge_agent`/
  `relecture_bridge`, `alchess`/`chesscoach`).
- Doc : mise à jour de `RELECTURE_WEB_DOC.md`, sections 1 (nouvelle
  colonne lue), 2 (en-têtes, barre latérale), 9 (format des confirmations,
  « Retraiter » sans confirmation), 10 (repositionnement de « Retraiter »,
  hauteur des zones de résultat, Rafraîchir sur la page Conflit).

## 2026-09-24 — issue #72 (relecture_web)

- **Bouton « Retraiter le fichier en conflit »** : dans la section « ⚠
  Fusion en conflit » de la page projet, chaque fichier déjà résolu
  (`git add` fait) pendant le merge en cours porte désormais un bouton
  « 🔁 Retraiter ce fichier » — que d'autres fichiers restent en conflit
  ou que tous soient résolus (dans ce cas, à côté de « ✅ Finaliser le
  merge »). Le clic exécute `git checkout --conflict=merge --
  <chemin>` (nouvelle fonction `retraiter_fichier_conflit`,
  `relecture_web/git_info.py`), qui recrée les marqueurs de conflit
  d'origine pour ce fichier précis à partir du mécanisme « resolve-undo »
  de git (`git ls-files --resolve-undo`, nouvelle fonction
  `get_fichiers_resolus_merge`) ; le fichier redevient `UU` et réapparaît
  dans la liste des fichiers en conflit, prêt à être rouvert depuis la
  page Conflit.
  - Garde-fous côté serveur, revérifiés à partir de l'état git actuel :
    un merge réellement en cours (`MERGE_HEAD` présent, même principe que
    « Finaliser le merge ») et un chemin figurant dans la liste actuelle
    des fichiers résolus (jamais construit à l'aveugle depuis le seul
    paramètre d'URL, même principe que la page Conflit).
  - Confirmation JS légère avant soumission (efface la résolution déjà
    appliquée à ce fichier, en entier).
  - Message flash signalant que les marqueurs recréés portent les
    libellés génériques `ours`/`theirs` au lieu de `HEAD` et du nom de la
    branche entrante — vérifié que la page Conflit reste lisible dans ce
    cas (les libellés de branche entrante de l'issue #70 affichent alors
    simplement « theirs »).
  - Nouvelle route `POST
    /projet/<nom_projet>/conflit/<chemin_relatif>/retraiter`
    (`relecture_web/app.py`).
- **Correction de documentation (`RELECTURE_WEB_DOC.md`, section 9)** :
  le point de non-retour d'un fichier résolu pendant un merge n'est pas
  le `git add` de résolution — vérifié en local sur un conflit de test
  (git 2.43) : `git ls-files --resolve-undo` conserve les informations
  nécessaires, et `git checkout --conflict=merge -- <chemin>` recrée les
  marqueurs de conflit d'origine même après ce `git add` (seule
  différence : libellés `ours`/`theirs` génériques au lieu de `HEAD` et
  du nom de la branche entrante). La vraie limite reste la finalisation
  du merge (`git commit`, bouton « Finaliser le merge ») : une fois ce
  commit fait, `MERGE_HEAD` disparaît et `git merge --abort` cesse de
  fonctionner (vérifié). Section 10 complétée avec la description de la
  nouvelle action.

## 2026-09-24 — issue #71 (relecture_web)

- **Confirmations graduées selon le risque**, contre la fatigue de
  confirmation constatée en test réel (toutes les actions passaient par
  la même fenêtre native `confirm()`, au point que le clic sur OK
  devenait un réflexe et que le garde-fou ne protégeait plus rien).
  Trois niveaux désormais :
  - **Aucune confirmation** (application directe) : Sécuriser (un ou
    tous), Nettoyer ce projet / tous les projets, Traiter ce bloc,
    Traiter tous les blocs (sauf anomalie, voir ci-dessous), Finaliser
    le merge, Revert, Comparer / Comparer la sélection / Générer
    rapport.
  - **Confirmation légère** (fenêtre native `confirm()` conservée) :
    Merger — modifie la branche cible mais reste local et annulable
    tant que le merge n'est pas finalisé. « Traiter tous les blocs »
    repasse aussi par cette confirmation, mais uniquement si au moins
    un bloc a un résultat vide (anomalie potentielle — suppression de
    bloc), avec le message d'avertissement déjà existant.
  - **Confirmation forte** (nouvelle fenêtre propre à `relecture_web`,
    `#modal-confirmation-forte` dans `templates/base.html`, style
    `.modal-forte*`/`.bouton--danger`/`.bouton--annuler` dans
    `static/style.css`) : Push, Supprimer la/les branche(s)
    fusionnée(s), Supprimer la/les branche(s) de récupération (panneau
    d'actions de la page projet **et** suppression groupée depuis
    « Comparer la sélection »). Visuellement distincte (couleur
    d'alerte rouge), bouton de validation qui décrit l'action réelle
    avec sa portée (ex. « Pousser 2 branches vers GitHub », « Supprimer
    test_conflit_a ») au lieu d'un OK générique, focus par défaut sur
    Annuler pour qu'un Entrée réflexe ne valide rien, commande git
    équivalente toujours affichée. Implémentée en JS pur (fonction
    `confirmationForte()` dans `base.html`, réutilisée par
    `projet.html` et `comparer_selection.html`) — aucune route serveur
    ajoutée, les indicateurs « Push en cours... » / « Fusion en
    cours... » (issue #49) sont inchangés après validation.
  - Fichiers modifiés : `templates/base.html`, `templates/projet.html`,
    `templates/comparer_selection.html`, `templates/conflit.html`,
    `templates/branche.html`, `templates/index.html`,
    `static/style.css`. Aucun fichier Python touché (aucune route ni
    garde-fou serveur n'a changé, seule la confirmation côté
    navigateur est concernée).
- **Vérification de réversibilité** demandée par l'issue pour les
  actions passant en « aucune confirmation » au motif qu'elles sont
  réversibles : « Traiter ce bloc » / « Traiter tous les blocs »
  écrivent directement le fichier, sans fonction d'annulation dans
  `relecture_web` lui-même. Le geste reste réversible en pratique tant
  que le merge n'est pas finalisé, mais uniquement via une commande
  manuelle en terminal (`git checkout --conflict=merge -- <chemin>`
  tant que `git add` n'a pas eu lieu sur ce fichier précis, sinon
  `git merge --abort` qui annule tout le merge, pas seulement ce
  fichier) — jamais un bouton de `relecture_web`. Point documenté dans
  `RELECTURE_WEB_DOC.md` (section 9) plutôt que de retirer la
  confirmation ou d'en ajouter une nouvelle, comme demandé par l'issue.
- `RELECTURE_WEB_DOC.md` (section 9) : remplacement de l'affirmation
  « toutes les actions passent par `confirm()` » par la description des
  trois niveaux, et mise à jour de la colonne Garde-fou de chaque ligne
  du tableau pour indiquer son niveau. Ajout de la ligne « Traiter ce
  bloc », absente du tableau jusqu'ici bien que déjà listée comme
  action existante dans le texte de la section.

## 2026-09-24 — issue #70 (relecture_web)

- Correction de deux problèmes constatés en test réel (suite de
  l'issue #69) sur la page Conflit
  (`relecture_web/templates/conflit.html`) :
  - **Numérotation dans l'avertissement « résultat vide »** : la
    confirmation de « Traiter tous les blocs » listait les blocs vides
    avec leur index interne 0-based (« Bloc(s) au résultat vide : 0, 1 »),
    incohérent avec la navigation de la même page qui affiche « Bloc 1 /
    3 ». Le message affiche désormais la position 1-based (celle de la
    navigation) au lieu de l'index interne — seul l'affichage change, les
    index transmis au serveur (`index_bloc`, champs cachés
    `texte_final_<index>`) restent le 0-based habituel de
    `_trouver_blocs_conflit`.
  - **Libellé « version locale » inversé** : le texte d'en-tête et
    l'infobulle de la flèche orange décrivaient à tort l'orange comme la
    « version locale », alors que la version locale est HEAD (la branche
    actuelle, en bleu) — l'orange est la branche entrante, celle qu'on
    fusionne (portée par le marqueur `>>>>>>>`). Le texte d'en-tête et
    l'infobulle de la flèche orange parlent maintenant de « branche
    entrante », avec son nom affiché entre parenthèses quand il est
    disponible (extrait du marqueur `>>>>>>>` de chaque bloc, resp. du
    premier bloc du fichier pour le texte d'en-tête général) ; l'infobulle
    de la flèche bleue est précisée en « HEAD (branche actuelle) » pour la
    cohérence. `relecture_web/git_info.py` n'a pas été modifié (numérotation
    et format du marqueur `>>>>>>>` déjà exploitables tels quels).
- `RELECTURE_WEB_DOC.md` (section 10) : la terminologie ours/HEAD/bleu et
  theirs/branche entrante/orange était déjà correcte, aucune correction
  nécessaire sur ce point ; ajout d'une précision sur la numérotation
  1-based de la liste des blocs vides dans la confirmation JS, par
  opposition à l'index 0-based interne inchangé.

## 2026-09-24 — issue #69 (relecture_web)

- Ajout d'un bouton « 🔄 Rafraîchir » sur la page « branches d'un projet »
  (`relecture_web/templates/projet.html`) : simple lien GET vers l'URL
  courante de la page (pas un `location.reload()`), pour recharger l'état
  git à jour après une action faite en terminal sans jamais risquer de
  faire réapparaître l'avertissement « resoumettre le formulaire » du
  navigateur qu'un vrai F5 peut déclencher après un POST.
- Ajout d'un bouton « 📋 Copier » réutilisant le composant générique
  `.bouton-copier` déjà utilisé ailleurs (hash, nom de branche) pour
  copier dans le presse-papiers le chemin d'un fichier en conflit tel que
  renvoyé par `git status` : à côté de chaque fichier listé dans la
  section « ⚠ Fusion en conflit » de la page projet, et dans l'en-tête de
  la page Conflit. Purement côté navigateur, aucune route serveur.
- Ajout d'un bouton « Traiter tous les blocs » sur la page Conflit,
  variante « tout ou rien » de « Traiter ce bloc » qui applique en une
  seule opération le contenu de chaque `<textarea>` du panneau droit au
  bloc de conflit correspondant, sans recharger la page entre chaque
  bloc :
  - `relecture_web/git_info.py` : `lire_conflits_fichier` calcule
    désormais aussi une empreinte (sha256 du contenu) transmise à
    l'affichage ; nouvelle fonction `resoudre_tous_blocs_conflit`,
    réutilisant `_trouver_blocs_conflit` (même numérotation que
    l'affichage et que « Traiter ce bloc ») — refuse tout le traitement
    (aucun bloc écrit) si le nombre de blocs ou l'empreinte ne
    correspondent plus à ce qui a été affiché ; applique les
    remplacements du dernier bloc vers le premier pour que les décalages
    d'index provoqués par un remplacement ne perturbent jamais les blocs
    restant à traiter ; `git add` automatique une fois tous les blocs
    remplacés, comme pour le traitement bloc par bloc.
  - `relecture_web/app.py` : nouvelle route
    `POST /projet/<nom_projet>/conflit/<chemin_relatif>/traiter-tous`
    (`traiter_tous_blocs_conflit_route`).
  - `relecture_web/templates/conflit.html` : bouton « Traiter tous les
    blocs (N) », confirmation JavaScript avant soumission qui signale
    explicitement les blocs dont le textarea est vide (suppression du
    bloc). « Traiter ce bloc » reste disponible, inchangé.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` sections 9 et 10 pour les
  trois ajouts.

## 2026-09-23 — issue #68 (relecture_web)

- Ajout d'un bouton « 🧹 Nettoyer ce projet » sur la page « branches d'un
  projet » (`relecture_web/templates/projet.html`), à côté du titre —
  évite de repasser par la liste des projets pour nettoyer les résumés
  `Non_Lu/` déjà pushés du seul projet sur lequel on vient de travailler.
- Nouvelle route `POST /projet/<nom_projet>/nettoyer`
  (`nettoyer_projet_route`, `relecture_web/app.py`) : réutilise la même
  logique et le même garde-fou de sécurité que
  `nettoyer_tous_les_projets_route` (issue #17) — `lister_fichiers_resumes_pushes`
  puis `_supprimer_fichiers` — limitée à `projet['dossier_relecture']` /
  `projet['repertoire']` du seul projet affiché, avec confirmation
  JavaScript avant soumission.
- Le bouton global « Nettoyer tous les projets » (page d'accueil) est
  inchangé.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 9 (nouvelle ligne
  « Nettoyer ce projet » dans le tableau des actions).

## 2026-09-23 — issue #67 (relecture_web)

- Ajout d'un badge dédié `⚠️ worktree orphelin — repli signalé`, distinct
  du badge `worktree` habituel, sur la page « branches d'un projet »
  (`relecture_web/templates/projet.html`) : affiché pour tout worktree
  secondaire dont le chemin apparaît dans une ligne « déjà pris » de
  `logs/watcher-<projet>.log` — le journal que Bridge_Agent écrit
  (issue #589 côté Bridge_Agent) quand une tâche `mode_write` n'a pas pu
  obtenir son propre worktree et est retombée sur `REP_TRAVAIL`.
- `relecture_web/git_info.py` : nouvelles fonctions `_lignes_deja_pris_watcher`
  (lecture seule best-effort de `logs/watcher-<projet>.log` dans le
  répertoire du projet `bridge_agent`, absent/illisible -> liste vide) et
  `worktree_orphelin_signale` (correspondance de chemin dans ces lignes).
  Appelées depuis `collect_etat_projets` pour renseigner
  `worktree["orphelin_signale"]` sur chaque worktree secondaire.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 4 (liste des badges).

## 2026-09-22 — issue #66 (relecture_web)

- Après un timeout de 120s sur Push, Merger ou Finaliser le merge, le
  message flash renvoyait systématiquement Alain vers une vérification
  manuelle en ligne de commande (« a dépassé le délai, mais a pu se
  terminer entre-temps — vérifiez manuellement si besoin »), y compris
  quand l'opération avait en réalité bel et bien abouti — constaté sur
  `bridge_agent` (worktree-issue-588) : message de timeout affiché,
  mais fusion réellement terminée (commit de fusion présent, copie de
  travail propre), vérifié à la main via `git status`/`git log`/`git
  worktree list`.
  - `git_info.py` : trois nouvelles fonctions de vérification post-timeout,
    chacune appelée uniquement depuis le bloc `except
    subprocess.TimeoutExpired:` de l'action correspondante :
    - `verifier_push_apres_timeout(repertoire, branche)` — compare le
      commit local de `branche` au commit réellement exposé par le
      remote via `git ls-remote` (pas le suivi local
      `refs/remotes/...`, qui ne serait mis à jour que par un `fetch` et
      pourrait rester périmé). Retourne `ok` = True (push confirmé),
      False (push non abouti), ou None si la vérification elle-même n'a
      pas pu aboutir (réseau).
    - `verifier_merge_apres_timeout(repertoire, branche_cible,
      branche_source)` — distingue trois états réels via `MERGE_HEAD`
      et `git merge-base --is-ancestor` : fusion aboutie, fusion arrêtée
      sur des conflits (pas un échec, la page de résolution de conflits
      prend le relais normalement), ou fusion non aboutie.
    - `verifier_finalisation_merge_apres_timeout(repertoire)` — dans ce
      flux précis, seul le commit visé par `finaliser_commit_merge` peut
      faire disparaître `MERGE_HEAD` ; sa disparition signale donc de
      façon fiable que le commit a bien été créé avant que le timeout
      Python ne tue le process (probablement resté bloqué dans le hook
      `post-commit`).
  - `app.py` : les trois blocs `except subprocess.TimeoutExpired:`
    (`pousser_branches_route`, `merger_branches_route`,
    `finaliser_merge_route`) appellent désormais la vérification
    correspondante et affichent un message flash final reflétant l'état
    réel constaté (succès confirmé, échec confirmé, conflits en attente,
    ou état indéterminé avec la raison), au lieu du message générique
    précédent.
  - `RELECTURE_WEB_DOC.md` (section 9, lignes **Push**/**Merger**/
    **Finaliser le merge** du tableau des actions, et section 10) mise à
    jour en conséquence.
  - Testé manuellement sur des dépôts git temporaires (push déjà abouti,
    push jamais poussé, merge déjà fusionné, merge en conflit non
    résolu, merge non finalisé) pour valider les trois états retournés
    par chaque fonction de vérification.

## 2026-09-22 — issue #64 (relecture_web)

- `finaliser_commit_merge` (`git_info.py`) plantait avec un
  `subprocess.TimeoutExpired` non rattrapé après seulement 10s
  (`TIMEOUT_GIT`) : le `git commit --no-edit` qu'elle exécute déclenche
  le hook `post-commit` du projet, qui appelle Claude en ligne de
  commande pour générer le résumé fonctionnel (`resumer_diff.py`) — une
  opération pouvant dépasser 10s sur un fichier volumineux (vécu
  concrètement sur `RELECTURE_WEB_DOC.md`). Push et Merger utilisent
  déjà `TIMEOUT_GIT_LONG` (120s) pour cette même raison de fond (issue
  #39), mais `finaliser_commit_merge` n'avait pas été aligné dessus lors
  de sa création (issue #61).
  - `git_info.py` : `finaliser_commit_merge` passe maintenant
    `timeout=TIMEOUT_GIT_LONG` (120s) à l'appel `git commit --no-edit`,
    en cohérence avec `pousser_branche` et `fusionner_worktree`.
  - `app.py` (`finaliser_merge_route`) : ajout d'un `try/except` autour
    de l'appel à `finaliser_commit_merge`, sur le même modèle que
    `pousser_branches_route`/`merger_branches_route` (issues #39/#61) —
    un dépassement du délai malgré tout, ou toute autre erreur
    inattendue, est désormais rapporté par un message flash explicite
    plutôt que de faire planter la requête avec une page d'erreur brute.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne **Finaliser le merge** du
    tableau des actions, et section 10) mise à jour en conséquence.

## 2026-09-22 — issue #63 (relecture_web)

- Correction d'un cas où la fusion automatique du `CHANGELOG-<N>.md`
  (issue #51) réussissait bel et bien côté script, mais restait sans effet
  durable pour un projet dont le worktree du merge n'était pas déjà la
  branche courante (cas de `bridge_agent`, contrairement à
  `relecture_bridge` où la branche courante coïncide généralement avec la
  branche cible) : `CHANGELOG-585.md`/`CHANGELOG-586.md` restaient non
  fusionnés malgré des prérequis (`CHANGELOG.md`, `scripts/
  fusionner_changelog.py`) pourtant bien présents.
  - Cause réelle : `fusionner_changelog_worktree` lançait le script (qui
    modifie `CHANGELOG.md` et supprime les `CHANGELOG-<N>.md` sur disque)
    mais ne commitait jamais ce résultat. `fusionner_worktree` bascule
    ensuite potentiellement sur la branche d'origine (`doit_basculer`,
    quand la branche cible n'a pas de worktree dédié) : un `git checkout`
    avec un `CHANGELOG.md` modifié en local est refusé par git dès que la
    branche de destination diffère sur ce fichier — bascule qui échouait
    silencieusement (retour jamais vérifié), laissant le dépôt dans un état
    non commité que toute opération git ultérieure pouvait écraser sans
    aucun message d'erreur.
  - `git_info.py` : `fusionner_changelog_worktree` commite désormais
    immédiatement (`git commit -a`) le résultat du script dès qu'il a
    réussi, rendant la fusion durable indépendamment de ce que fait
    l'appelant ensuite. `fusionner_worktree` vérifie maintenant le code
    retour du `checkout` de retour et remonte l'échec via un nouveau champ
    `erreur_retour_branche` plutôt que de l'ignorer.
  - `app.py` : nouveau message flash dédié si `erreur_retour_branche` est
    renseigné, pour ne plus jamais laisser un tel échec invisible.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne « Merger ») : documentation de
    la fusion automatique du changelog (jusqu'ici non documentée depuis
    l'issue #51) et de ce correctif de durabilité.

## 2026-09-22 — issue #62 (relecture_web)

- Journalisation persistante des tentatives de fusion automatique du
  CHANGELOG (déclenchée après un merge, issue #51) : jusqu'ici, le
  résultat (succès/échec) n'était visible que via un message flash
  éphémère, affiché une seule fois juste après l'action — vécu
  concrètement quand Alain a mergé deux branches sur `bridge_agent`
  depuis `relecture_web` sans repérer le détail du message, sans moyen
  après coup de confirmer si la fusion automatique avait réellement
  réussi.
  - `git_info.py` : nouveau fichier de log `relecture_web/changelog_fusion.log`
    (non commité, voir `.gitignore`), une ligne par tentative réellement
    lancée (script trouvé ou non) — date/heure ISO, projet, commande
    exécutée, résultat (`SUCCES`/`ECHEC`), message d'erreur le cas
    échéant. Écrite par la nouvelle fonction `_journaliser_fusion_changelog`,
    appelée depuis `fusionner_changelog_worktree` (qui accepte maintenant
    un paramètre optionnel `nom_projet`). Une erreur d'écriture du journal
    reste silencieuse pour l'utilisateur — elle ne doit jamais faire
    échouer la fusion elle-même.
  - `fusionner_worktree` propage `nom_projet` jusqu'à
    `fusionner_changelog_worktree` ; `app.py` passe `projet["nom"]` lors de
    l'appel dans `merger_branches_route`.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne **Merger** du tableau des
    actions) mise à jour en conséquence.

## 2026-09-21 — issue #61 (relecture_web)

- Ajout du bouton **« Finaliser le merge »**, pour clore le dernier geste
  manuel encore nécessaire après une résolution de conflits entièrement
  faite depuis `relecture_web` (issues #55/#56/#59) : la section « Fusion
  en conflit » de la page projet accepte automatiquement chaque fichier
  résolu (`git add`), mais le commit du merge lui-même restait à taper en
  terminal — cassant le flux visé par tout ce chantier.
  - `git_info.py` : deux nouvelles fonctions, `get_merge_en_cours`
    (`git rev-parse --verify --quiet MERGE_HEAD`, distingue un vrai merge en
    cours d'un simple conflit `UU` isolé — cherry-pick/revert en conflit ne
    créent jamais `MERGE_HEAD`) et `finaliser_commit_merge`
    (`git commit --no-edit`, l'équivalent non-interactif de `git commit`
    sans `-m` : accepte tel quel le message déjà préparé par git dans
    `.git/MERGE_MSG`, sans ouvrir d'éditeur inutilisable depuis une page
    web).
  - `app.py` : `projet_route` calcule désormais `merge_en_cours` et
    `peut_finaliser_merge` (= merge en cours ET plus aucun fichier en
    conflit) pour chaque projet. Nouvelle route
    `POST /projet/<nom_projet>/finaliser-merge` — revalide l'état git
    actuel (pas la seule page déjà affichée) avant d'appeler
    `finaliser_commit_merge`, pour ne jamais tenter un commit partiel même
    sur un formulaire soumis depuis une page obsolète.
  - `templates/projet.html` : la section « Fusion en conflit » reste
    affichée tant qu'un merge est en cours, mais bascule d'une liste de
    fichiers à résoudre vers un unique bouton « ✅ Finaliser le merge » une
    fois tous les fichiers résolus — jamais les deux à la fois, et le
    bouton n'apparaît pas tant qu'il reste un seul fichier en conflit.
    Même pattern de confirmation que les autres actions du système
    (`confirm()` JS avec commande équivalente affichée,
    `git -C <repertoire> commit --no-edit`).
  - `RELECTURE_WEB_DOC.md` (section 9, tableau des actions, et section 10)
    mises à jour en conséquence.

- Correction du chevauchement visuel dans l'en-tête de la page **Conflit**
  (`conflit.html`) constaté après le passage à la vue à deux panneaux
  (issue #59) : le libellé « Résultat final — éditable » du panneau droit
  se superposait avec le bouton de navigation « Bloc suivant » (►) et le
  compteur de position (« Bloc n / total »).
  - Cause : la colonne centrale de la grille CSS partagée par l'en-tête
    et le corps (`.conflit-vue__entetes`, `.conflit-vue__corps`) était
    fixée à `72px`, largeur suffisante pour les trois petites flèches du
    corps mais trop étroite pour contenir les boutons de navigation
    (◀ / ▶) et le texte « Bloc n / total » de l'en-tête — ce contenu
    débordait donc visuellement sur la colonne de droite.
  - Correctif (`static/style.css`) : l'en-tête (`.conflit-vue__entetes`)
    utilise désormais sa propre largeur de colonne centrale,
    `minmax(96px, auto)`, qui s'élargit automatiquement pour accueillir
    la navigation sans jamais empiéter sur les colonnes voisines ; le
    corps (`.conflit-vue__corps`, les trois flèches par bloc) conserve
    sa colonne fixe de `72px`, inchangée. Ajout de `min-width: 0` et
    `overflow-wrap: break-word` sur les libellés (`.conflit-vue__entete-titre`)
    et de `flex-wrap: wrap` sur le conteneur de navigation
    (`.conflit-vue__entete-titre--milieu`) pour rester lisible sans
    chevauchement même à largeur de fenêtre réduite.

## 2026-09-21 — issue #59 (relecture_web)

- Page **Conflit** (issues #55, #56) refondue en vue à deux panneaux
  synchronisés, remplaçant entièrement l'ancien bloc isolé + textarea
  séparé (pas un mode alternatif en plus) :
  - Panneau gauche : le fichier complet en lecture seule, bloc de
    conflit affiché à sa vraie place dans le texte environnant (HEAD en
    bleu, version locale en orange), inchangé sur ce point.
  - Panneau droit : le même fichier complet, éditable, avec à
    l'emplacement de chaque bloc le `<textarea>` de composition du
    texte final (mécanisme de résolution par bloc de l'issue #56
    inchangé côté serveur — `resoudre_bloc_conflit` et la route
    `traiter_bloc_conflit_route` ne bougent pas).
  - Trois flèches par bloc entre les deux panneaux : bleue (copie
    « ours »/HEAD dans le résultat), orange (copie « theirs »/version
    locale), verte (vide le résultat). Le texte reste modifiable à la
    main après un transfert — jamais une copie figée.
  - Boutons « ◀ » / « ▶ » dans l'en-tête pour naviguer entre les blocs
    d'un même fichier sans quitter la page (position affichée « Bloc
    n / total », bloc ciblé mis en évidence et centré à l'écran).
- Défilement synchronisé obtenu par construction : les deux panneaux et
  leurs en-têtes partagent une seule grille CSS à trois colonnes
  (gauche / flèches / droite), construite ligne par ligne à partir des
  mêmes segments — une seule barre de défilement pour toute la page,
  pas deux volets indépendants à recaler en JS.
- `base.html` : ajout du bloc Jinja `classe_contenu` (vide par défaut)
  pour permettre à une page de s'afficher plus large ; `conflit.html`
  l'utilise (`contenu-principal--large`, 1500px) pour donner de la
  place aux deux panneaux côte à côte.
- Aucun changement côté serveur (`app.py`, `git_info.py`) : uniquement
  `conflit.html`, `base.html` et `style.css`.
- `RELECTURE_WEB_DOC.md` section 10 mise à jour pour décrire la
  nouvelle vue à deux panneaux (issue #59).
- Vérifié : le template Jinja se parse sans erreur ; relecture visuelle
  du HTML/CSS/JS généré (pas de serveur de test disponible dans ce
  périmètre pour un essai navigateur complet).

## Issue #58 — fetch_projets() doit se replier sur la résolution normale si le forçage IPv4 échoue

- `relecture_web/git_info.py` : extraction du téléchargement de
  `DOC_URL` dans `_telecharger_doc_projets(forcer_ipv4)`, réutilisable
  avec ou sans le monkeypatch IPv4 introduit par l'issue #57.
  `fetch_projets()` tente d'abord l'appel avec IPv4 forcé (rapide dans
  le cas normal) ; s'il échoue pour n'importe quelle raison (coupure
  réseau ponctuelle, IPv4 momentanément indisponible...), une seconde
  tentative est faite en résolution normale (IPv4 ou IPv6, au choix
  d'`urllib`) avant d'abandonner avec `ErreurRecuperationProjets`. Une
  perturbation réseau passagère ne provoque donc plus d'échec total du
  chargement de la liste des projets — au pire un chargement plus lent
  cette fois-là.

## Issue #57 — fetch_projets() met 80s au lieu de 0,4s (résolution IPv6)

- `relecture_web/git_info.py` : `fetch_projets()` force désormais la
  résolution IPv4 le temps de l'appel `urlopen(DOC_URL)`, en remplaçant
  temporairement `socket.getaddrinfo` par une variante qui filtre sur
  `socket.AF_INET`, restaurée dans un `finally` juste après l'appel réseau.
  Corrige un ralentissement de 80s (4x `TIMEOUT_RESEAU`, retries IPv6 en
  série) à 0,2-0,4s, sans toucher aux commandes `git` (qui n'utilisent pas
  ce mécanisme) ni au reste de l'application.

## 2026-09-21 — issue #56 (relecture_web)

- Page **Conflit** (issue #55) : à côté de chaque bloc affiché en
  lecture seule, ajout d'un `<textarea>` éditable pré-rempli avec la
  version « ours », dans lequel Alain compose le texte final à garder
  (copie d'une des deux versions, combinaison, ou tout autre texte, y
  compris vide pour supprimer le bloc). Bouton « Traiter ce bloc »
  (confirmation JS avec aperçu du texte) qui remplace ce bloc précis —
  marqueurs `<<<<<<<`/`=======`/`>>>>>>>` compris — par ce texte dans
  le fichier réel, en local uniquement.
- Nouvelle route `POST /projet/<nom_projet>/conflit/<chemin>/traiter` :
  revalide que le fichier est toujours en conflit avant d'écrire, comme
  la route de lecture voisine. Redirige vers la même page de conflit
  s'il reste des blocs (le suivant apparaît naturellement en premier),
  ou vers la page du projet avec un message clair une fois le fichier
  entièrement résolu.
- `git_info.py` : `_extraire_blocs_conflit` (issue #55) factorisée avec
  une nouvelle `_trouver_blocs_conflit`, partagée avec la nouvelle
  `resoudre_bloc_conflit` — garantit que la numérotation des blocs
  (0-based, ordre d'apparition) est strictement identique entre
  affichage et résolution, pour qu'une soumission ne puisse jamais
  toucher le mauvais bloc. Si le fichier a changé entre l'affichage et
  la soumission au point que le numéro de bloc ne corresponde plus
  (bloc déjà traité, fichier modifié ailleurs), `resoudre_bloc_conflit`
  échoue proprement avec un message d'erreur plutôt que d'écrire à
  l'aveugle. Lecture/écriture strictement UTF-8 (contrairement à la
  lecture seule d'issue #55, qui tolère les octets invalides puisqu'elle
  n'écrit jamais).
- Une fois le dernier bloc d'un fichier traité, `git add <fichier>` est
  lancé automatiquement pour marquer sa résolution — le commit et le
  push restent des gestes manuels d'Alain, volontairement non
  automatisés.
- `RELECTURE_WEB_DOC.md` section 10 mise à jour (titre et contenu :
  détection **et résolution**, suppression de la mention "strictement
  en lecture seule" devenue fausse).
- Testé manuellement (dépôt de test jetable hors périmètre) : bloc
  unique, blocs multiples, texte final vide (suppression du bloc),
  index de bloc obsolète (erreur propre sans écriture) — tous les cas
  se comportent comme attendu, `git add` ne se déclenche qu'au dernier
  bloc.

## 2026-09-21 — issue #55 (relecture_web)

- Nouvelle section **⚠ Fusion en conflit** sur la page « branches d'un
  projet » : détecte, via `git status --porcelain` (codes `UU`, `AA`,
  `DD`, `AU`, `UA`, `DU`, `UD`), les fichiers en conflit d'une fusion
  non résolue et les liste, sans avoir à taper `git status`/`grep` en
  terminal.
- Nouvelle page **Conflit** (`/projet/<nom_projet>/conflit/<chemin>`)
  pour un fichier sélectionné : localise chaque bloc entre `<<<<<<<`,
  `=======` et `>>>>>>>`, affiche les deux versions dans des blocs de
  texte à fond coloré distinct (bleu « ours »/`HEAD`, orange « theirs »
  — volontairement pas un `<textarea>`, qui ne supporte pas le texte en
  couleur), et le texte hors conflit normalement autour pour le
  contexte. Un éventuel marqueur de base commune diff3 (`|||||||`) est
  ignoré, seules les deux versions en conflit sont affichées.
- Strictement en lecture seule : aucune écriture sur le fichier. Le
  chemin demandé n'est accepté que s'il figure dans la liste actuelle
  des fichiers en conflit renvoyée par `git status` (recalculée à
  chaque requête), jamais construit à l'aveugle depuis le paramètre
  d'URL — protège aussi contre un chemin en dehors du dépôt du projet.
  La résolution (choisir/éditer le texte final et l'écrire) fait
  l'objet d'une issue de suivi séparée.
- `git_info.py` : `get_fichiers_en_conflit`, `_extraire_blocs_conflit`,
  `lire_conflits_fichier`.
- `RELECTURE_WEB_DOC.md` mise à jour (nouvelle section 10, ancienne
  section 10 renumérotée 11, mention dans la navigation section 2).

## 2026-09-20 — issue #54 (relecture_web)

- Pour une branche fusionnée sélectionnée dont le worktree est encore
  actif, le bouton « Supprimer » enchaîne désormais `git worktree
  remove` puis `git branch -D` dans le même clic — plus besoin de
  recliquer une seconde fois pour que la branche, alors sans worktree
  détecté, tombe sous le second cas (issue #43). Comportement inchangé
  pour une branche déjà sans worktree (suppression directe de la
  branche).
- Si le retrait du worktree échoue (modifications non commitées), la
  branche n'est pas touchée — même garde-fou qu'avant, juste enchaîné.
  Si le worktree est retiré mais que la suppression de branche échoue
  pour une autre raison, un message flash distinct rapporte cet état
  intermédiaire.
- Message flash rapportant les deux étapes en une seule ligne (même
  principe que la suppression combinée branche + fichiers `Non_Lu/`,
  issues #31/#40). Aperçu de confirmation JavaScript mis à jour pour
  afficher les deux commandes équivalentes.
- `RELECTURE_WEB_DOC.md` mise à jour (tableau des actions, section 9).

## Issue #53 — 2026-09-20

- Doc : `RELECTURE_WEB_DOC.md` section 7 (`branches_cibles.conf`)
  corrigée — le passage affirmait encore que déclarer plusieurs
  branches cibles pour un projet « fait toujours planter la génération
  de la page `/projet/<nom>` », ce que l'issue #50 a corrigé
  (`est_branche_mergee` et `get_diagnostic_doublons_branche` gèrent
  désormais une liste de cibles). Le texte reflète maintenant l'état
  réel : la page s'affiche sans erreur, le badge « fusionnée » est
  correct (vrai si fusionnée dans au moins une cible) ; seul le bouton
  **Merger** reste à corriger, renvoi explicite vers l'issue #51 pour
  ce point précis.

## 2026-09-20 — issue #52 (relecture_web)

- Projet à plusieurs branches cibles configurées (`branches_cibles.conf`,
  ex. `scrabble = master, feature/moteur-strategique`) : le bouton
  Merger ne devine plus aucune cible par défaut — un sélecteur « Cible
  du merge » apparaît dans le panneau d'actions, à choisir explicitement
  avant que la fusion ne soit possible (refus par message flash sinon,
  côté serveur). La confirmation JavaScript affiche la commande
  équivalente correspondant à la cible réellement choisie.
- `est_branche_mergee` accepte désormais une liste de cibles (fusionnée
  si ancêtre d'au moins une d'entre elles), pour que la page
  `/projet/<nom>` ne plante plus pour un projet à plusieurs cibles.
- Comportement inchangé pour un projet à une seule cible configurée (ou
  sans configuration) : pas de sélecteur, bouton Merger identique à
  avant cette issue.
- `RELECTURE_WEB_DOC.md` mise à jour (section 7, tableau des actions
  section 9).

## 20 septembre 2026 — issue #51

Fusion automatique de `CHANGELOG-<N>.md` lors d'un merge depuis
`relecture_web`.

- `fusionner_worktree` (`relecture_web/git_info.py`) appelle désormais
  `fusionner_changelog_worktree` juste après un merge réussi, pendant que
  la branche cible est encore extraite dans le dépôt (avant toute bascule
  de retour) : si la branche fusionnée a introduit un `CHANGELOG-<N>.md` à
  la racine du dépôt, lance `scripts/fusionner_changelog.py` (déjà présent
  dans le projet concerné) pour l'intégrer dans `CHANGELOG.md`.
- Aucun `CHANGELOG-<N>.md` détecté : `changelog` vaut `None`, aucun message
  supplémentaire affiché.
- Résultat de cette étape rapporté par un message flash séparé dans
  `merger_branches_route` (`relecture_web/app.py`) — succès, ou message
  d'erreur explicite (script absent, échec du script) sans jamais faire
  échouer silencieusement la fusion elle-même.
- `RELECTURE_WEB_DOC.md` (section 9, ligne « Merger ») mis à jour en
  conséquence.
- Vérifié par test manuel dans des dépôts temporaires hors du dépôt réel
  (merge avec `CHANGELOG-<N>.md` présent et script présent, merge sans
  `CHANGELOG-<N>.md`, merge avec `CHANGELOG-<N>.md` mais script absent).

## Issue #50 — 2026-09-20

- Fix : `est_branche_mergee` (relecture_web/git_info.py) plantait
  (`TypeError` dans `subprocess.run`) dès qu'une branche cible configurée
  dans `branches_cibles.conf` était une liste (plusieurs cibles, issue
  #41 — cas de `scrabble`). Gère maintenant ce cas : une branche est
  « fusionnée » si elle est ancêtre d'au moins une des cibles candidates
  (`git merge-base --is-ancestor` par candidate).
- Fix connexe (même page, même cause) : `get_diagnostic_doublons_branche`
  plantait pour la même raison sur `git cherry` — retourne désormais
  `False` (pas de verdict automatique) quand la cible est une liste, même
  parti pris que le cas M déjà en place pour le diagnostic des commits
  orphelins (issue #46), pour ne pas multiplier les `git cherry` coûteux
  sur chaque branche locale de la page.
- Résultat : la page `/projet/<nom>` d'un projet à plusieurs cibles
  configurées (ex. `scrabble`) s'affiche sans erreur, badge « fusionnée »
  correct.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 7.

## 2026-09-20 — issue #49 (relecture_web)

- Ajout d'un indicateur visuel « Push en cours... Ns » / « Fusion en
  cours... Ns » (fenêtre superposée avec spinner et compteur de secondes)
  affiché juste après la confirmation d'un push ou d'un merge, tant que la
  page ne s'est pas rechargée avec le résultat. Purement côté navigateur,
  aucun changement de comportement serveur.

