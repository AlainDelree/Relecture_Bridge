# CHANGELOG-119 — à fusionner dans CHANGELOG.md

## Issue #119 — 2026-11-02

- `relecture_web` : la fenêtre de confirmation forte avant suppression
  d'un worktree, affichée dès qu'au moins un fichier/dossier ignoré par
  `.gitignore` serait perdu (issue #112, suite #116), remplace son menu
  obligatoire « origine de la décision » par une case **« Classer comme
  bruit pour ce projet »** sur chaque fichier/dossier listé — décochée par
  défaut, jamais présélectionnée, sans aucun blocage du bouton de
  validation (celui-ci reste actif tout de suite, contrairement à
  l'ancien menu). Son texte rappelle qu'une case cochée disparaîtra
  désormais SANS AUCUN AVERTISSEMENT avec tout worktree de ce projet
  (tout le contenu, pour un dossier).
- Nouveau mécanisme de bruit **par projet**, en plus du bruit global
  existant (liste fixe dans le code, inchangée) :
  `git_info.CHEMIN_LISTE_BRUIT_PROJETS` (`relecture_web/bruit_projets.log`,
  même emplacement/principe que le journal des décisions existant — hors
  de tout worktree, ignoré par git, créé au premier ajout), lu/écrit par
  `lire_bruit_projets`/`ajouter_bruit_projet`/`retirer_bruit_projet`.
  Fichier texte lisible et modifiable à la main, une entrée par ligne
  (`projet=<nom> | chemin=<chemin exact affiché sur la page>`), relu à
  chaque détection (jamais mis en cache) — aucun redémarrage de
  relecture_web nécessaire pour qu'un ajout/retrait prenne effet.
  Volontairement pas de règle par nom seul valable pour tous les
  projets : un fichier de clé ou de journal portant le même nom dans un
  autre projet reste signalé. `lister_fichiers_ignores_worktree` accepte
  désormais un `nom_projet` optionnel pour appliquer ce filtrage en plus
  du bruit global.
- Entrées initiales pour `relecture_bridge` lui-même :
  `relecture_web/secret_key.conf` et `relecture_web/changelog_fusion.log`
  — les deux fichiers qui revenaient à chaque suppression d'un worktree
  de relecture_bridge et étaient confirmés à la main à chaque fois.
  Aucune autre entrée présumée pour aucun projet (en particulier aucun
  dossier d'environnement/dépendances ni de sorties de build).
- **Dégradation systématique vers la prudence** : fichier de liste
  absent, illisible, ou ligne individuellement mal formée (ignorée SEULE)
  → aucun filtrage supplémentaire, donc plus de signalements, jamais
  moins — exactement le comportement d'avant cette issue.
- **Classement accepté CÔTÉ SERVEUR uniquement dans une requête qui
  porte réellement la confirmation de suppression**
  (`ignorer_avertissement_fichiers_ignores=on`, sans case « à garder »
  cochée) — jamais seul, jamais via une autre route ; une case « à
  garder » cochée bloque toujours la confirmation ET tout classement de
  la même requête.
- **Annuler est redevenu un simple lien `<a>`** vers la page du projet,
  comme avant l'issue #116 : plus de menu obligatoire à remplir, donc
  plus rien à soumettre — aucune requête, aucun enregistrement. La route
  `annuler_fichiers_ignores_route` et le champ `origine_decision` ont
  disparu.
- **Journal des décisions** (`relecture_web/decisions_fichiers_ignores.log`,
  inchangé de lieu) : le champ `origine` disparaît du format de ligne ;
  une ligne « bruit » distincte s'ajoute, en plus de la ligne
  « garder »/« supprimer » du même fichier, lors d'un classement ; plus
  aucune ligne n'est écrite à l'annulation.
- Nouveau panneau repliable **« 🔇 Bruit ignoré pour ce projet »**
  (`#details-bruit`), dans la section « 🛠️ Outils du projet » de la page
  projet, à côté du panneau `.gitignore` (issue #98) — liste les entrées
  du projet affiché avec un bouton « Retirer » (aucune confirmation,
  puisque retirer une entrée ne supprime rien : seulement l'avertissement
  qui réapparaît pour ce chemin). Nouvelle route
  `/projet/<nom_projet>/bruit-fichiers-ignores/retirer`.
- `base.html` : la liste de cases à cocher optionnelle
  (`options.cases = {libelle, items}`) de la fenêtre de confirmation
  remplace le menu obligatoire optionnel (`options.menu`) de l'issue
  #116, désormais sans appelant.
- Les projets distants du PC fixe (`_ccw`) utilisent le même mécanisme et
  la même clé de projet, sans accès SSH ajouté — ce fichier de bruit ne
  dépend jamais du filesystem distant.
- Tests : `test_decisions_fichiers_ignores_worktree.py` adapté (menu
  obligatoire et journalisation à l'annulation retirés des scénarios) ;
  nouveau fichier `test_bruit_fichiers_ignores_projets.py` (22 tests :
  lecture/écriture/dégradation du fichier de bruit, masquage par projet
  uniquement, classement par case cochée/décochée, refus hors requête de
  confirmation ou avec une case « à garder » cochée, panneau
  ajout/retrait, projet distant, entrées initiales de relecture_bridge) ;
  `test_bouton_annuler_confirmation_suppression.py` et
  `test_fichiers_ignores_suppression_worktree.py` adaptés au retour
  d'Annuler à un simple lien. `RELECTURE_WEB_DOC.md` (§9) mis à jour.
