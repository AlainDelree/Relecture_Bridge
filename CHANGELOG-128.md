# CHANGELOG-128 — à fusionner dans CHANGELOG.md

## Issue #128 — 2026-11-04

- `relecture_web` : le nettoyage des résumés déjà pushés (jusqu'ici
  réservé aux boutons « Nettoyer ce projet »/« Nettoyer tous les
  projets », issues #16/#17/#68) se déclenche désormais automatiquement
  après un push confirmé abouti depuis cette interface — plus besoin de
  recliquer pour que le compteur de résumés en attente redevienne juste.
  Réutilise exactement la même fonction (`resumes_info.
  nettoyer_resumes_pousses`, nouvelle factorisation de
  `lister_fichiers_resumes_pushes` + suppression, sans seconde
  implémentation), donc le même garde-fou : seul un résumé dont le commit
  est déjà un ancêtre d'une branche distante est supprimé.
- **Push synchrone** (projet sans crochet pre-push,
  `app.pousser_branches_route`) : nettoyage tenté juste après la
  confirmation du résultat de chaque branche poussée avec succès (push
  direct ou vérification après dépassement de délai, issue #66), nombre
  de résumés supprimés ajouté au message flash de succès existant
  (`_suffixe_nettoyage_auto_apres_push`).
- **Push en arrière-plan** (projet équipé d'un crochet pre-push, issue
  #122, `push_arriere_plan._executer_push_arriere_plan`) : nettoyage
  tenté une seule fois à la fin du thread, seulement si l'état final est
  `pousse` — sans aucun message et sans aucun effet sur l'entrée d'état
  persistante ni sur l'acquittement (`vu`).
- Aucun nettoyage pour un push refusé, interrompu ou indéterminé, ni pour
  un projet distant du PC fixe CCW (pas de dossier `Non_Lu` local sur un
  clone Windows, même refus que « Nettoyer ce projet »). Une erreur
  pendant le nettoyage est systématiquement absorbée, sur les deux
  chemins : elle ne remonte jamais dans le message affiché et ne change
  jamais le résultat du push rapporté.
- Les boutons « Nettoyer ce projet » et « Nettoyer tous les projets »
  restent entièrement inchangés — ce déclenchement automatique ne voit
  pas un push fait directement en terminal.
- Tests (`relecture_web/test_nettoyage_auto_apres_push.py`, dépôts et
  dossier `Non_Lu` jetables, aucun fichier réel touché) : nettoyage
  déclenché après un push synchrone abouti et après un push en
  arrière-plan abouti, non déclenché après un refus/un état interrompu/un
  état indéterminé/pour un projet distant, résumé d'un commit non encore
  poussé conservé, erreur de nettoyage sans effet sur le résultat du push
  (synchrone et arrière-plan). Suite complète toujours verte.
- Documentation : `RELECTURE_WEB_DOC.md` — lignes « Push » et « Nettoyer
  ce projet » du tableau §9 mises à jour, nouvelle sous-section « Nettoyage
  automatique des résumés déjà pushés après un push (issue #128) » dans la
  section 13.
