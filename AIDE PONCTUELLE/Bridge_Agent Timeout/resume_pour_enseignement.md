# Résumé de situation — à l'intention du Claude qui va m'enseigner les concepts

Rédigé par Claude Chat (l'assistant avec qui Alain a eu la discussion jointe en
transcription), pour poser le contexte sans reproduire toute la pédagogie ici.

## Qui est Alain, et qu'est-ce que Bridge_Agent

Alain est un développeur francophone qui a conçu et maintient seul
**Bridge_Agent** : un système d'orchestration où Claude Chat (moi) rédige des
tâches sous forme de GitHub Issues, qu'un Claude Code tournant en local sur son
ThinkPad (« CCL ») détecte et exécute automatiquement via un watcher. Chaque
issue porte un champ `TIMEOUT` (ex. `600s`) qui borne le temps alloué au
traitement ; au-delà, l'issue échoue par expiration. Le système existe depuis
plusieurs mois, gère plusieurs projets actifs (dont `scrabble`, sur lequel la
discussion jointe a démarré), et Alain vérifie/pousse lui-même chaque
modification de code après coup — rien n'est automatisé côté Git push.

Le watcher enregistre déjà, pour chaque issue traitée, sa durée réelle dans un
fichier local `historique_durees.json` (par projet, type de tâche, mode
lecture/écriture), utilisé pour afficher une estimation de durée dans
l'interface. Ce fichier n'est pas versionné sur GitHub.

## Le problème concret qu'on essaie de résoudre

Aujourd'hui, la valeur du `TIMEOUT` mise dans chaque nouvelle issue est choisie
« à la main » par moi (Claude Chat), sans accès fiable à l'historique réel des
durées. Alain veut un **outil de calcul systématique du TIMEOUT à inscrire dans
une issue**, qui s'applique à tous les projets Bridge_Agent (pas un cas
particulier pour un seul projet), et qui tienne compte de deux réalités :

1. **Le rythme de traitement varie dans le temps** — un ralentissement réseau
   ponctuel (quelques heures à deux jours) ou une VM chargée peuvent faire
   grimper la durée réelle des issues qui font de la recherche web ou
   interagissent avec GitHub. Une simple moyenne « depuis le début » masque
   ces épisodes.
2. **Les issues qui expirent (timeout) sont quand même informatives**, même si
   on ne connaît pas leur durée réelle exacte (on sait juste qu'elles ont pris
   *au moins* la durée du TIMEOUT fixé). Une série de timeouts d'affilée doit
   influencer le calcul du prochain TIMEOUT, pas être ignorée.

## Où en est la réflexion (le point qui reste flou pour Alain)

Dans la discussion, Claude Chat a proposé un système inspiré du calcul du
**RTO (retransmission timeout) en TCP** — l'algorithme de Jacobson/Karels,
utilisé depuis des décennies pour un problème structurellement identique :
estimer un délai d'attente approprié quand la durée "normale" d'une opération
varie dans le temps et que la variabilité elle-même varie.

L'idée esquissée combine plusieurs briques mathématiques qu'Alain ne maîtrise
pas encore et veut comprendre avant de valider quoi que ce soit :

- **Moyenne mobile exponentielle (EWMA — Exponentially Weighted Moving
  Average)** : une façon de calculer une "moyenne récente" qui donne plus de
  poids aux données récentes sans totalement oublier les anciennes, sans
  fenêtre fixe ni discontinuité brutale. Notion de "demi-vie" du poids.
- **Données censurées** : notion statistique où une observation ne donne
  qu'une borne (ici : "au moins 300s") plutôt qu'une valeur exacte, et
  pourquoi ça biaise une moyenne classique si on la traite comme une valeur
  exacte, tout en restant exploitable autrement (ex. via la fréquence des
  occurrences plutôt que leur valeur).
- **Estimation de variabilité en plus d'une moyenne** (écart-type ou écart
  absolu moyen) : pourquoi une "durée typique" seule ne suffit pas pour fixer
  une marge de sécurité, et comment la variabilité elle-même peut être
  suivie dans le temps de façon dynamique (mobile), pas figée.
- **Backoff multiplicatif / décroissance progressive** : mécanisme classique
  (aussi issu de TCP, et des stratégies de retry en général) pour réagir vite
  à un échec (augmenter fort et tout de suite) mais revenir prudemment à la
  normale seulement après plusieurs signaux positifs répétés — évite à la
  fois la sous-réaction et la dérive sans fin vers des valeurs absurdes.

## Ce qu'Alain a déjà bien identifié tout seul (pour calibrer le niveau)

Alain a lui-même repéré, sans vocabulaire technique, deux failles réelles dans
la première proposition de Claude Chat :
- que jeter les timeouts revient à perdre une information utile ;
- que "pécher par excès de marge" sans borne ni mécanisme de retour est un
  raisonnement qui, poussé à l'absurde, mène à des valeurs n'ayant plus aucun
  sens (ex. un TIMEOUT de plusieurs heures).

Ces deux intuitions sont justes et correspondent exactement à des limitations
connues des approches naïves de moyenne glissante — ça vaut la peine de partir
de ces deux intuitions déjà solides plutôt que de tout réexpliquer depuis zéro.

## Objectif de la session pédagogique

Comprendre suffisamment ces notions (EWMA, censure statistique, variabilité
dynamique, backoff/décroissance) pour pouvoir, en revenant discuter avec
Claude Chat, évaluer et ajuster en connaissance de cause une proposition de
calcul automatique du TIMEOUT à intégrer dans `bridge_agent` — pas
nécessairement pour l'implémenter soi-même, mais pour valider ou remettre en
question les choix (demi-vie de l'EWMA, facteur k de marge, taux de
backoff/décroissance) avant de faire rédiger l'issue correspondante.
