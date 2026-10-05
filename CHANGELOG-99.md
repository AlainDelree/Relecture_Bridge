## Issue #99 — 2026-10-05

- `relecture_web` : correction de la mise en page de l'avertissement
  « fichiers déjà suivis » du panneau repliable « 📄 .gitignore » (issue
  #98), constatée en usage réel (navigateur à 70 %) — le `<li>` d'une
  ligne motif est une rangée flex (motif + ✕ + avertissement), si bien que
  l'avertissement restait écrasé dans une colonne étroite à côté du motif
  au lieu d'occuper toute la largeur du panneau, les fichiers suivis
  concernés s'enchaînaient en ligne séparés par des virgules, et les
  chemins longs débordaient à droite hors du panneau faute de point de
  coupure autorisé. Deux changements :
  - `templates/projet.html` : la liste des fichiers suivis par motif passe
    d'une suite de `<span>` inline séparés par `, ` à une vraie liste
    (`<ul class="liste-gitignore-fichiers-suivis">`, un `<li
    class="gitignore-fichier-suivi">` par fichier) — aucun changement
    d'action, de confirmation ou de donnée affichée, uniquement la
    structure du balisage.
  - `static/style.css` : `.ligne-gitignore` passe en `flex-wrap: wrap` et
    `.avertissement-gitignore-suivi` prend `flex-basis: 100%` pour forcer
    son retour à la ligne sous le motif, en pleine largeur du panneau ;
    chaque `.gitignore-fichier-suivi` s'affiche en rangée
    `justify-content: space-between` (chemin à gauche, bouton « Ne plus
    suivre » à droite, sans séparateur) ; `overflow-wrap: anywhere` sur
    les chemins (`.chemin-fichier`, `min-width: 0` sur le conteneur flex)
    permet la coupure des chemins longs sans espace, pour qu'ils ne
    débordent jamais du panneau. Même traitement appliqué par cohérence à
    la liste « Non suivis et non ignorés » du même panneau (fichiers non
    trackés), qui présentait le même risque de débordement sur un chemin
    long.
  Vérifié par rendu du template avec un chemin volontairement très long
  et capture d'écran (Chromium headless) à largeur pleine et à largeur
  réduite (~70 %) : l'avertissement occupe la largeur du panneau, chaque
  fichier suivi est sur sa propre ligne, et aucun débordement horizontal
  n'apparaît dans le panneau. Aucun changement de comportement : mêmes
  actions, mêmes confirmations, mêmes données.
