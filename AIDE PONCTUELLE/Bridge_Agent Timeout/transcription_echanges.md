# Transcription — Discussion estimation de durée / calibration TIMEOUT (Bridge_Agent)

Contexte : Alain travaille sur le projet Scrabble (Bridge_Agent). Un Claude Code
Linux (CCL) rattaché à ce projet lui a soumis une idée d'amélioration, qu'Alain
a relayée à Claude Chat (CC) pour discussion et affinement avant rédaction
d'une issue.

---

## Message initial (rédigé par le CCL du projet Scrabble, relayé par Alain)

> Bonjour,
> Je travaille avec Claude Chat une idée est ressortie d'une discussion qu'il
> vaut la peine que tu étudies.
> Depuis l'issue #108, le watcher calcule déjà la durée réelle de traitement
> de chaque issue et l'enregistre dans `logs/historique_durees.json`, pour
> alimenter l'estimation prédictive affichée dans l'interface (badge de durée
> médiane par projet, type et mode). Le problème, c'est que ce fichier est
> gitignoré : cette information ne vit que sur mon ThinkPad, jamais sur
> GitHub. Résultat, Claude Chat — qui rédige les issues et lit les rapports de
> résultat que je lui colle après coup — n'a aucun moyen de savoir combien de
> temps une issue a réellement pris, et ne peut donc pas bien calibrer ses
> choix de TIMEOUT pour les prochaines.
> L'idée : ajouter la durée réelle de traitement directement dans le
> commentaire de clôture que tu postes sur GitHub à la fin d'une issue
> (succès ou échec), sous une forme lisible du genre « Durée de traitement :
> X min Y s ». Comme cette durée est déjà calculée quelque part dans le code
> pour alimenter l'historique, ça ne devrait pas demander de nouveau calcul —
> juste l'afficher au bon endroit.
> Ce que j'aimerais que tu fasses :
> 1. Regarde où et comment le commentaire de clôture est posté (probablement
>    dans watcher.py, près du calcul de durée existant).
> 2. Vérifie si cette valeur est disponible facilement à cet endroit, avant ou
>    après l'écriture dans historique_durees.json.
> 3. Si c'est faisable sans risque de casser des mécanismes existants qui
>    lisent ce commentaire (le poller de notifications qui détecte les
>    transitions via `done`/`closedAt`, ou la lecture du commentaire ACK pour
>    le badge de temps restant), fais la modification.
> 4. Si tu rencontres un obstacle ou un risque de régression, n'insiste pas —
>    explique-moi clairement ce qui bloque plutôt que de forcer.
> 5. Vérifie bien qu'aucun mécanisme existant (poller de notifications, badge
>    de décompte, historique des durées) n'est cassé par le changement.

---

## Alain (tour 1)

Relaie le message ci-dessus, précise que le CCL Scrabble l'a écrit comme si
c'était Alain qui parlait, mais que l'idée de fond est là. Ajoute un bémol :

- L'estimation reste une moyenne lissée sur toutes les issues abouties (déjà
  il faut intégrer celles finies par timeout).
- Plus le temps passe, moins l'estimation reflète une vérité contextuelle :
  certains jours il y a des problèmes internet / réseau lent (quelques
  heures, 1 ou 2 jours) qui ralentissent les issues nécessitant recherche web
  ou interaction GitHub. Le travail sur la VM peut aussi impacter la vitesse.
- Proposition : avoir deux estimations — une moyenne depuis le début, une
  moyenne sur ce qui se passe actuellement — et le hic est de fusionner ces
  deux informations pour améliorer l'estimation.
- Demande l'avis de CC.

## Claude Chat (tour 1)

Confirme la lecture de `BRIDGE_AGENT_DOC.md` (via curl, conformément aux
préférences), sépare le problème en deux :

1. **Timeouts = données censurées** : une issue qui timeout à 300s a duré *au
   moins* 300s, pas exactement 300s — les inclure telles quelles biaise la
   moyenne à la baisse artificiellement. Propose de les **exclure** du calcul
   de durée et de suivre séparément un **taux d'échec par timeout récent**
   comme métrique de dégradation.
2. **Fusion global/récent** : propose une **EWMA** (moyenne mobile
   exponentielle) par (projet, TYPE, mode) plutôt que deux fenêtres séparées à
   fusionner après coup — demi-vie ~10-15 issues. Garde la moyenne globale à
   vie comme "plancher de sécurité" : `TIMEOUT = max(EWMA_récent,
   moyenne_globale) × marge`. Argumente que l'enjeu est asymétrique (TIMEOUT
   trop court coûte un échec, trop long ne coûte presque rien), donc mieux
   vaut pécher par excès en cas de divergence. Propose médiane plutôt que
   moyenne arithmétique pour la robustesse aux valeurs extrêmes.

Demande validation avant de rédiger l'issue Scrabble.

## Alain (tour 2)

Recadre sur deux points :

1. **Ce n'est pas le badge d'estimation affiché dans l'interface** qui est
   l'objet principal (même s'il en bénéficiera) — l'objectif est un **outil
   de calcul du TIMEOUT à inscrire dans une issue**, à la rédaction.
2. **Ne pas envoyer ça côté Scrabble** — c'est un système qui doit profiter à
   **tous les projets**, donc côté `bridge_agent`.
3. Sur l'exclusion des timeouts : intuition qu'ils restent informatifs. Cinq
   timeouts d'affilée doit avoir un impact sur l'évaluation du prochain
   TIMEOUT, même sans connaître la durée exacte.
4. Sur "pêcher par excès" : d'accord sur le principe, mais pointe la dérive
   logique — en poussant ce principe à l'absurde, on finit par mettre tous
   les TIMEOUT à 18 000s. Demande de trouver un juste milieu : viser
   l'exactitude tout en gardant une marge, pas être à 300s près mais pas
   dériver sans limite non plus. Demande à CC de dire clairement s'il se
   trompe.

## Claude Chat (tour 2)

Reconnaît les deux corrections comme justes :

1. **Sur l'exclusion des timeouts** : erreur de trop extrapoler — les
   timeouts n'informent pas sur la durée exacte, mais la **fréquence** des
   timeouts est un signal direct et utile (peut-être le plus direct) pour
   juger si la marge actuelle est suffisante.
2. **Sur "pêcher par excès"** : le principe tel qu'énoncé était mal borné —
   sans mécanisme de retour en arrière ni limite, il dérive vers l'absurde.
   Reformule : réagir vite à une preuve concrète d'insuffisance, mais
   redescendre tout aussi activement quand les conditions redeviennent
   normales.

Propose une analogie avec l'algorithme de calcul du **RTO en TCP**
(Jacobson/Karels — `RTO = SRTT + 4×RTTVAR`, avec backoff multiplicatif sur
échec et décroissance sur succès répétés) comme modèle déjà éprouvé pour ce
type de problème (durée typique qui bouge + variabilité qui bouge + besoin
d'une marge dynamique).

Propose un système concret, par (projet, TYPE, mode) :

- **Durée typique récente** : EWMA sur les issues réussies uniquement, demi-
  vie courte (~10-15 issues).
- **Variabilité récente** : EWMA de l'écart absolu à cette durée typique,
  même demi-vie.
- **TIMEOUT suggéré = durée_typique + k × variabilité** (k réglable, ~4 par
  défaut, avec plancher minimum absolu).
- **Sur un timeout constaté** : backoff immédiat et multiplicatif (×1.4-1.5)
  du TIMEOUT suggéré, indépendant du recalcul normal (réaction rapide, sans
  attendre que l'EWMA de durée "rattrape" une info qu'elle ne peut de toute
  façon pas capter puisque la vraie durée du timeout reste inconnue).
- **Sur une série de succès francs** (durée réelle nettement sous le TIMEOUT
  actuel, plusieurs issues d'affilée) : décroissance progressive du backoff
  vers la formule de base — jamais en dessous.

Propose que ce soit un module partagé côté `bridge_agent` (pas `scrabble`),
utilisé par `watcher.py`, appliqué à l'`historique_durees.json` de chaque
projet. Suggère aussi de faire évoluer l'idée initiale du commentaire de
clôture GitHub pour y afficher directement le TIMEOUT suggéré pour la
prochaine issue similaire, plutôt qu'une simple durée brute.

## Alain (tour 3)

Indique que les notions abordées (notamment mathématiques) le dépassent, et
qu'il va consulter un autre Claude, dont le rôle est de lui enseigner les
concepts, avant de revenir décider avec CC. Demande deux fichiers : cette
transcription, et un résumé de la situation vu par CC. Demande aussi s'il
existe un outil pour exporter une conversation en fichier.
