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
