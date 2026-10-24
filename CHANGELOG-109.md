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
