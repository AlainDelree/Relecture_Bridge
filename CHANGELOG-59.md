## 2026-09-21 — issue #59 (relecture_web)

- Page **Conflit** (issues #55, #56) refondue en vue à deux panneaux
  synchronisés, remplaçant entièrement l'ancien bloc isolé + textarea
  séparé (pas un mode alternatif en plus) :
  - Panneau gauche : le fichier complet en lecture seule, bloc de
    conflit affiché à sa vraie place dans le texte environnant (HEAD en
    bleu, version locale en orange), inchangé sur ce point.
  - Panneau droit : le même fichier complet, éditable, avec à
    l'emplacement de chaque bloc le `<textarea>` de composition du
    texte final (mécanisme de résolution par bloc de l'issue #56
    inchangé côté serveur — `resoudre_bloc_conflit` et la route
    `traiter_bloc_conflit_route` ne bougent pas).
  - Trois flèches par bloc entre les deux panneaux : bleue (copie
    « ours »/HEAD dans le résultat), orange (copie « theirs »/version
    locale), verte (vide le résultat). Le texte reste modifiable à la
    main après un transfert — jamais une copie figée.
  - Boutons « ◀ » / « ▶ » dans l'en-tête pour naviguer entre les blocs
    d'un même fichier sans quitter la page (position affichée « Bloc
    n / total », bloc ciblé mis en évidence et centré à l'écran).
- Défilement synchronisé obtenu par construction : les deux panneaux et
  leurs en-têtes partagent une seule grille CSS à trois colonnes
  (gauche / flèches / droite), construite ligne par ligne à partir des
  mêmes segments — une seule barre de défilement pour toute la page,
  pas deux volets indépendants à recaler en JS.
- `base.html` : ajout du bloc Jinja `classe_contenu` (vide par défaut)
  pour permettre à une page de s'afficher plus large ; `conflit.html`
  l'utilise (`contenu-principal--large`, 1500px) pour donner de la
  place aux deux panneaux côte à côte.
- Aucun changement côté serveur (`app.py`, `git_info.py`) : uniquement
  `conflit.html`, `base.html` et `style.css`.
- `RELECTURE_WEB_DOC.md` section 10 mise à jour pour décrire la
  nouvelle vue à deux panneaux (issue #59).
- Vérifié : le template Jinja se parse sans erreur ; relecture visuelle
  du HTML/CSS/JS généré (pas de serveur de test disponible dans ce
  périmètre pour un essai navigateur complet).
