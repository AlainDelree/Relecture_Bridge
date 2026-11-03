## Issue #123 — 2026-11-03

- `relecture_web` : affichage global, sur toutes les pages, du résultat
  d'un push en arrière-plan (issue #122) — pour qu'Alain, parti travailler
  sur un autre projet pendant qu'un push tourne, soit prévenu du résultat
  où qu'il se trouve dans l'interface, sans dépendre d'une notification
  externe. Purement de l'affichage : le moteur de push et son fichier
  d'état (`push_arriere_plan_etat.json`) ne sont pas modifiés, hors
  l'indicateur `vu` déjà prévu par l'issue #122.
- Nouvelle route en lecture seule `GET /push/etat`
  (`push_arriere_plan.etats_a_signaler`) : renvoie, pour chaque projet
  dont un push est en cours ou dont le dernier résultat n'a pas été
  acquitté, son état/branches/horaires/sortie/résultats par branche
  (jamais `repertoire` ni `pid`) — un projet jamais poussé en arrière-plan,
  ou déjà acquitté, n'y figure pas. Même filtre réutilisé côté serveur par
  `app.injecter_barre_laterale` pour le premier rendu de chaque page.
  Sondée en JS par `base.html` toutes les 5 secondes (20 secondes quand
  l'onglet est caché), dès le chargement de la page ; une erreur de
  sondage est ignorée silencieusement et réessayée au tour suivant.
- Barre latérale : pastille bleue animée (`.indicateur-push-en-cours`,
  volontairement distincte de la pastille de couleur statique du projet)
  à droite du nom pendant qu'un push tourne ; remplacée, une fois terminé
  et tant que non acquitté, par un panneau pleine largeur sous le nom —
  rouge « ⚠ ATTENTION — REFUS » pour un refus, orange « ⚠ À VÉRIFIER »
  pour un état interrompu ou indéterminé (le sens repose sur le texte,
  jamais la seule couleur). L'entrée redevient normale dès l'acquittement
  (« Vu », depuis la fenêtre de résultat globale ou la page du projet) ;
  rien n'est affiché pour un projet sans push suivi.
- Nouvelle fenêtre de résultat globale (`#modal-resultat-push`,
  `base.html`), distincte de la fenêtre de confirmation commune
  (`#modal-confirmation`, jamais réutilisée pour autre chose) : verte
  « ✅ Poussé » avec un simple bouton « Fermer » dès qu'un push suivi vient
  d'aboutir, rouge « ❌ Refusé » avec la fin de la sortie des tests et un
  bouton « Vu » — nouvelle route AJAX `POST /push/<nom_projet>/vu`
  (`app.acquitter_push_global_route`, même action que le bouton « Vu » de
  la page projet, sans redirection) — tant qu'il n'est pas acquitté, le
  refus réapparaît à chaque chargement de page et s'efface de partout, y
  compris les autres onglets déjà ouverts, au plus tard à leur sondage
  suivant. Plusieurs résultats en attente s'affichent l'un après l'autre ;
  si la fenêtre de confirmation commune est ouverte, le résultat attend sa
  fermeture avant de s'afficher, pour qu'Alain ne valide jamais un
  résultat de push par réflexe en croyant répondre à une confirmation
  d'action.
- Titre de l'onglet préfixé de `❌ ` (prioritaire) ou `✅ ` tant qu'un
  résultat n'est pas acquitté ou qu'une fenêtre de succès reste à fermer —
  restauré à son texte d'origine une fois acquitté/fermé, pour prévenir
  Alain même depuis un autre onglet du navigateur.
- Garde-fous : aucune action git, aucun son ni notification système (tout
  reste dans la page), comportement et ordre inchangés des liens/boutons
  déjà existants de la barre latérale.
- Nouveau fichier de tests `relecture_web/test_affichage_global_push.py`
  (18 tests) : route `/push/etat` (rien/en cours/refusé non
  acquitté/acquitté/interrompu/indéterminé, champs internes jamais
  exposés), rendu de la barre latérale pour chaque cas (y compris sur la
  page d'un AUTRE projet), acquittement AJAX global qui efface le panneau
  partout sans changer l'état, absence totale d'affichage sans push
  suivi. Suite complète (276 tests) verte, aucun test ne lit ni n'écrit
  les vrais fichiers locaux de relecture_web.
- `RELECTURE_WEB_DOC.md` mis à jour : section 2 (barre latérale) et
  nouvelle sous-section « Affichage global sur toutes les pages » en fin
  de section 13.
