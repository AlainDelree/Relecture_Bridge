# Concepts et vocabulaire — session du 25/07/2026

> **Thèmes :** Estimation adaptative (EWMA) · Marge & variabilité · Données
> censurées & backoff · Réglage empirique (backtest) · Mutualisation partielle ·
> Stratification · Instrumenter d'abord · Signal avancé vs retardé
> **Date :** 25/07/2026
> **Contexte :** calibrer automatiquement le TIMEOUT des issues Bridge_Agent.

**Sur base des 2 fichiers sur /home/alain/Relecture_Bridge/AIDE PONCTUELLE/Bridge_Agent Timeout**

## Estimation adaptative : l'EWMA

- **EWMA** (moyenne mobile exponentielle) — une « moyenne récente » qui donne
  plus de poids au neuf sans oublier brutalement le vieux. Formule unique :
  `nouvelle_estimation = α × nouvelle_mesure + (1−α) × ancienne_estimation`.
  On « corrige un peu dans la direction de la nouveauté ».
- **α (alpha)** — poids du neuf (entre 0 et 1). Proche de 1 = nerveux/court de
  mémoire ; proche de 0 = stable/lent. On ne stocke JAMAIS l'historique : une
  seule valeur à mettre à jour.
- **Demi-vie** — le vrai bouton de réglage : au bout de combien de mesures le
  poids d'une vieille valeur tombe de moitié. Court = réactif mais sautille ;
  long = lisse mais lent. C'est l'arbitrage **réactivité ↔ stabilité**.

## Marge de sécurité : durée typique + variabilité

- **Durée typique ≠ suffisante** — deux séries de même moyenne peuvent être
  l'une régulière, l'autre très dispersée. La moyenne dit OÙ est le centre, pas
  COMBIEN ça remue autour.
- **Écart absolu** — `|mesure − durée_typique|` : de combien une mesure tombe à
  côté du typique. `| |` = « en valeur positive ».
- **Variabilité récente** — une **EWMA des écarts absolus** : la même machinerie
  appliquée aux écarts. L'imprévisibilité elle-même bouge dans le temps.
- **Facteur k** — `TIMEOUT = durée_typique + k × variabilité`. `k` = combien de
  « sauts typiques » de marge on s'accorde (curseur prudent ↔ sportif). Vertu :
  la marge est **proportionnelle à la variabilité mesurée**, pas choisie à la
  main → elle ne dérive pas toute seule. + un **plancher absolu** de sécurité.

## Timeouts : données censurées

- **Donnée censurée** — observation dont on ne connaît qu'une **borne**, pas la
  valeur exacte. Un timeout à 300s = « a duré **≥ 300s** », vraie durée inconnue.
  Terme exact : **censure à droite** (comme un patient encore vivant en fin
  d'étude médicale).
- **Poison pour la moyenne** — injecter « 300 » comme une vraie durée ment à la
  baisse → cercle vicieux. Mais on ne peut pas non plus injecter la vraie valeur
  (on ne l'a pas).
- **Exploitées par la FRÉQUENCE** — un timeout n'informe pas sur la durée, mais
  sa fréquence dit directement « la marge est insuffisante ». On ne les jette
  pas : on les **réoriente** vers le backoff.

## Réagir : backoff & décroissance

- **Asymétrie des coûts** — TIMEOUT trop court = échec coûteux ; trop long =
  attente quasi gratuite. Donc : **monter vite, redescendre lentement**.
- **Backoff multiplicatif** — sur un timeout, ×1,4–1,5 immédiat. Multiplicatif
  car ça s'adapte à l'échelle et les échecs répétés **se composent** (1,4 → 1,96
  → 2,7…) : panique proportionnelle à la gravité.
- **Décroissance** — sur une série de succès francs, on rabote le backoff vers la
  formule de base, **jamais en dessous**. Une seule réussite ne suffit pas.
- **Double garde-fou anti-dérive** — la marge est attachée à la variabilité
  mesurée ET le backoff décroît activement → pas de dérive à l'absurde.

## Le modèle éprouvé : le RTO de TCP

- **RTO = SRTT + 4 × RTTVAR** (Jacobson/Karels, 1988) — le délai avant de
  déclarer un paquet perdu. Même problème structurel que le TIMEOUT.
- **SRTT** (*Smoothed Round-Trip Time*) = RTT lissé = **EWMA des durées** = notre
  durée typique. « Smoothed » = « passé à l'EWMA ».
- **RTTVAR** (*Round-Trip Time Variation*) = **EWMA des écarts** = notre
  variabilité. Le « 4 » = notre `k`.
- **Leçon** — on hérite de la **structure** (transposable), on **re-mesure les
  constantes** chez soi. Copier un chiffre sans comprendre = culte du cargo.

## Régler les constantes : le backtest

- **Backtest** — rejouer son historique réel pour tester un réglage. Pour un `k`
  candidat : compter le **taux d'échec** (timeouts → `k` trop petit) et le
  **gaspillage moyen** (marge en trop → `k` trop grand). Balayer `k` de 2 à 8,
  choisir le compromis. Idem pour la demi-vie (5 à 30).
- **Le bon réglage vient de SES données**, pas d'un article.

## Faire circuler l'info : mutualisation partielle

- **Mutualisation partielle** (*partial pooling*) / **modèle hiérarchique** —
  entre « tout séparé » (chaque projet aveugle) et « tout confondu » (une seule
  estimation pour tous) : chaque unité garde son estimation, **tirée vers** une
  estimation commune. Répond au **démarrage à froid** (*cold start*).
- **Climat vs météo** — la durée typique d'un projet = son **climat** (identité
  propre, lente, PERSONNELLE) ; l'état de la machine « maintenant » = la
  **météo** (partagée, rapide). Prévoir = climat × météo.
- **Facteur d'ambiance F** — EWMA globale, tous projets confondus, du **ratio**
  `r = durée_réelle / durée_typique_du_projet`. `F ≈ 1` normal, monte quand ça
  rame partout. `TIMEOUT = (typique + k×variabilité) × F`.
- **Partager le RELATIF, pas l'absolu** — un ratio (sans unité) est transférable
  entre projets d'ordres de grandeur différents ; des secondes ne le sont pas.
  Diviser par le typique = « oublier la taille pour ne garder que le combien-de-
  fois-plus-lent ». Le même mécanisme marche AUSSI entre modes d'un même projet.

## Découper finement : la stratification

- **Stratifier / conditionner** — découper une population en sous-groupes plus
  homogènes selon un critère. Déjà prévu : EWMA par `(projet, TYPE, mode)`.
- **Variable explicative / prédicteur** — un critère (ex. mode) qui **déplace**
  l'estimation en probabilité, sans la **dicter**. « Mode écriture » n'impose pas
  une durée, il indique.
- **Granularité ↔ rareté des données** — chaque critère ajouté découpe en cases
  plus fines → moins de données par case → estimation plus bruitée. Pousser à
  l'absurde = re-tomber dans le cold start. Même arbitrage que la demi-vie.
- **Bon critère = 3 tests** — (1) connu D'AVANCE et objectif ; (2) corrélé à la
  durée ; (3) faible cardinalité (peu de valeurs). Contre-exemples : « lignes
  changées » (connu seulement APRÈS) ; « heure de la journée » (déjà capté par
  F). « Un bon signal qui arrive trop tard n'est pas exploitable. »
- **Catégorie vs nombre** — un nombre (longueur d'issue, nb d'étapes) ne se range
  pas en cases directement : soit le **découper en tranches**, soit passer à une
  petite **régression**. Décision à repousser → logger le nombre brut.
- **Arbre de décision (principe)** — ne couper une population que si les morceaux
  sont plus homogènes que l'ensemble.

## Méthode : instrumenter d'abord

- **Enregistrer ≠ utiliser** — logger une étiquette (gratuit, réversible, sans
  engagement) est un autre geste que stratifier dessus (coûteux, structurant).
  Politique : **instrumenter généreusement, s'engager prudemment.**
- **Logger AVANT de savoir** — on ne peut pas évaluer a posteriori un signal
  jamais noté. Le regret de logger pour rien est minuscule ; celui de ne pas
  avoir loggé est irréparable (pas de retour dans le temps).
- **Compter ET comparer** — un compteur d'occurrences répond au VOLUME (« assez
  de données ? ») ; il faut AUSSI comparer les durées entre cases pour le SIGNAL
  (« vraie différence ? »). Un critère mérite sa case si les deux sont vrais.

## Signal avancé vs signal retardé

- **Retardé (*lagging*)** — `F` ne « voit » la lenteur qu'APRÈS que des issues
  soient revenues lentes. Angle mort : le **début d'une rafale** (machine calme
  → F≈1 → premières issues sous-protégées).
- **Avancé (*leading*)** — un signal connu au moment du lancement anticipe. Ex. :
  le **nombre de projets actifs** à l'instant du dispatch (concurrence
  inter-projets ⇒ contention RAM/CPU/disque ⇒ lenteur). Connu d'avance → gonfle
  le TIMEOUT tout de suite, couvre l'angle mort de F.
- **Ne pas compter deux fois** — séparer la part **prévisible** (concurrence →
  anticipée par le compteur) du **résidu imprévisible** (réseau, swap → réagi par
  F). Chacun son domaine.

## Index détaillé (repère de couverture)

> **Thèmes :** Estimation adaptative (EWMA, α, demi-vie, réactivité vs stabilité,
> pas de stockage d'historique) · Marge (durée typique vs variabilité, écart
> absolu, EWMA des écarts, facteur k, plancher) · Données censurées (censure à
> droite, borne inférieure, biais de moyenne, exploitation par fréquence) ·
> Backoff (asymétrie des coûts, multiplicatif, composition, décroissance, double
> garde-fou anti-dérive) · RTO TCP (Jacobson/Karels, SRTT, RTTVAR, structure vs
> constantes, culte du cargo) · Backtest (taux d'échec vs gaspillage, balayage de
> k et de la demi-vie) · Mutualisation partielle (partial pooling, modèle
> hiérarchique, cold start, climat vs météo, facteur d'ambiance F, ratio vs
> secondes, relatif transférable) · Stratification (conditionner, variable
> explicative/prédicteur, granularité vs rareté, 3 tests d'un bon critère,
> catégorie vs nombre, binning, régression, principe de l'arbre de décision) ·
> Instrumenter d'abord (enregistrer ≠ utiliser, logger avant de savoir, compter
> ET comparer, volume vs signal) · Avancé vs retardé (leading/lagging, angle mort
> de F, concurrence inter-projets, double comptage)
> **Date :** 25/07/2026

