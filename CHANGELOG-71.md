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
