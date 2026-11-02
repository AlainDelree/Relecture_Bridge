# CHANGELOG-120 — à fusionner dans CHANGELOG.md

## Issue #120 — 2026-11-02

- `relecture_web` : `ouvrirConfirmation` (`base.html`, fenêtre commune à
  toutes les actions de confirmation, issue #73) grise désormais son
  propre bouton de validation dès le clic de validation — jamais à
  l'ouverture — avec un libellé qui dit ce qui se passe (« <action> en
  cours... ») ; son bouton Annuler est bloqué en même temps. Jusqu'ici,
  entre ce clic et le résultat (suppression de worktree, fusion), rien
  n'indiquait que l'envoi avait été pris en compte — seul l'onglet du
  navigateur le montrait — ce qui pouvait pousser à recliquer pendant que
  la première suppression/fusion tournait encore.
- Nouvelle option `options.boutonDeclencheur` : référence facultative vers
  le bouton « Confirmer » de la page derrière la fenêtre (celui qui l'a
  ouverte), bloqué lui aussi dès ce même clic, pour qu'aucun second envoi
  ne parte par ce chemin non plus. Reliée dans les 12 appels existants de
  `ouvrirConfirmation` (7 dans `projet.html`, et un dans chacun de
  `confirmation_fichiers_ignores_worktree.html`,
  `echec_suppression_worktree.html`, `confirmation_verrou_fusion.html`,
  `conflit.html`, `comparer_selection.html`).
- La fenêtre reste affichée tant que la vraie navigation déclenchée par le
  formulaire n'a pas eu lieu (elle ne se ferme plus au clic de
  validation) : pour les trois pages de confirmation forte dédiées sans
  aucun autre indicateur (fichiers ignorés avant suppression de worktree,
  forçage de suppression, avertissement de verrou avant fusion), c'est
  elle qui sert désormais d'indicateur « en cours ». Là où un indicateur
  « ... en cours... Ns » existe déjà (Push, Merger, issue #49), il reste
  conservé tel quel, affiché par-dessus ce grisage (`.overlay-action`
  passé à un z-index supérieur à `.modal-confirmation`, `style.css`) — le
  grisage s'y ajoute, il ne le remplace pas.
- Garde-fou de restauration : un `pageshow` global réinitialise les trois
  boutons (validation et Annuler de la fenêtre, déclencheur de la page)
  si une restauration par le bouton « précédent » du navigateur (bfcache)
  les avait figés désactivés juste avant la navigation réelle — jamais de
  bouton resté grisé qui rendrait une action impossible à relancer. Un
  rechargement de page (nouvel appel à `ouvrirConfirmation`) les
  réinitialise de la même façon à l'ouverture.
- Aucune modification de route ni de logique serveur — changement
  d'affichage côté navigateur uniquement.
- Tests : nouveau fichier `test_bouton_grise_confirmation_en_cours.py`
  (8 tests — présence du grisage/réinitialisation dans le script commun,
  non-régression de l'indicateur « ... en cours... Ns » existant, et
  câblage de `options.boutonDeclencheur` sur les trois pages de
  confirmation forte dédiées) ; aucun test existant modifié. `RELECTURE_WEB_DOC.md`
  (§9, paragraphe commun à `ouvrirConfirmation`) mis à jour.
