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
