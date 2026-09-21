## 2026-09-21 — issue #60 (relecture_web)

- Correction du chevauchement visuel dans l'en-tête de la page **Conflit**
  (`conflit.html`) constaté après le passage à la vue à deux panneaux
  (issue #59) : le libellé « Résultat final — éditable » du panneau droit
  se superposait avec le bouton de navigation « Bloc suivant » (►) et le
  compteur de position (« Bloc n / total »).
  - Cause : la colonne centrale de la grille CSS partagée par l'en-tête
    et le corps (`.conflit-vue__entetes`, `.conflit-vue__corps`) était
    fixée à `72px`, largeur suffisante pour les trois petites flèches du
    corps mais trop étroite pour contenir les boutons de navigation
    (◀ / ▶) et le texte « Bloc n / total » de l'en-tête — ce contenu
    débordait donc visuellement sur la colonne de droite.
  - Correctif (`static/style.css`) : l'en-tête (`.conflit-vue__entetes`)
    utilise désormais sa propre largeur de colonne centrale,
    `minmax(96px, auto)`, qui s'élargit automatiquement pour accueillir
    la navigation sans jamais empiéter sur les colonnes voisines ; le
    corps (`.conflit-vue__corps`, les trois flèches par bloc) conserve
    sa colonne fixe de `72px`, inchangée. Ajout de `min-width: 0` et
    `overflow-wrap: break-word` sur les libellés (`.conflit-vue__entete-titre`)
    et de `flex-wrap: wrap` sur le conteneur de navigation
    (`.conflit-vue__entete-titre--milieu`) pour rester lisible sans
    chevauchement même à largeur de fenêtre réduite.
