## Issue #102 — 2026-10-06

- `relecture_web` : constat en usage réel (rummikub, worktree-issue-133 et
  worktree-issue-133-bis) — après avoir coché la case « Purger réellement
  le(s) commit(s) rejeté(s) » pour une branche, puis décoché cette branche
  et coché une autre (du vrai travail), la case restait cochée. Option
  irréversible et globale au dépôt, elle ne doit jamais survivre à un
  changement de sélection. Trois changements, `templates/projet.html` et
  `static/style.css` (aucun changement côté `app.py`/routes) :
  - **Décochage systématique** : la case `#case-purger-rejet` est décochée
    dès qu'une case de branche change d'état (`change` sur `.checkbox-branche`),
    et sur tout `pageshow` (chargement initial **et** retour via le bfcache
    du navigateur) ; `autocomplete="off"` ajouté sur la case elle-même contre
    une restauration de formulaire par le navigateur. La règle existante
    (issue #97) qui empêche le panneau « Options de rejet » de se refermer
    tant que la case est cochée reste inchangée — elle se referme
    normalement dès que la case est décochée par ce nouveau mécanisme.
  - **Message raccourci** : le paragraphe rouge dense qui expliquait tout
    en permanence est remplacé par une seule ligne lisible d'un coup d'œil —
    verte « ✅ Aucun autre commit menacé. » si aucun autre commit orphelin
    non sécurisé n'est menacé, rouge avec la liste nominative des hashes et
    sujets sinon (classes `.message-purge-rejet--ok`/`--danger`, remplacent
    `.avertissement-purge-rejet`). L'explication détaillée (ce que font
    `git reflog expire --expire=now --all` et `git gc --prune=now`, ce qui
    reste récupérable sans la case) est reléguée dans un bloc repliable
    « Pourquoi ? » (`<details>` imbriqué) à l'intérieur du panneau.
  - **Libellé raccourci** : « Purger définitivement le commit rejeté
    (irréversible, concerne tout le dépôt) », sur une seule ligne, sans
    commande git visible en permanence (déplacées dans le bloc « Pourquoi ? »)
    — corrige aussi la coupure désordonnée des commandes au milieu du
    libellé à largeur réduite (70 %).
  - La confirmation forte au clic sur « Rejeter » rappelle maintenant, en
    première ligne de son avertissement (visible même si le panneau était
    replié au moment du clic), « 🔴 PURGE DÉFINITIVE activée » suivi du nom
    des branches visées, quand la case est cochée — avant, ce rappel était
    ajouté en fin de ligne, moins visible.
  - `RELECTURE_WEB_DOC.md` section 9 (ligne « Rejeter (sans fusionner) ») :
    paragraphe ajouté décrivant le décochage systématique et le nouveau
    format de message.
