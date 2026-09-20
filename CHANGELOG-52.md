## 2026-09-20 — issue #52 (relecture_web)

- Projet à plusieurs branches cibles configurées (`branches_cibles.conf`,
  ex. `scrabble = master, feature/moteur-strategique`) : le bouton
  Merger ne devine plus aucune cible par défaut — un sélecteur « Cible
  du merge » apparaît dans le panneau d'actions, à choisir explicitement
  avant que la fusion ne soit possible (refus par message flash sinon,
  côté serveur). La confirmation JavaScript affiche la commande
  équivalente correspondant à la cible réellement choisie.
- `est_branche_mergee` accepte désormais une liste de cibles (fusionnée
  si ancêtre d'au moins une d'entre elles), pour que la page
  `/projet/<nom>` ne plante plus pour un projet à plusieurs cibles.
- Comportement inchangé pour un projet à une seule cible configurée (ou
  sans configuration) : pas de sélecteur, bouton Merger identique à
  avant cette issue.
- `RELECTURE_WEB_DOC.md` mise à jour (section 7, tableau des actions
  section 9).
