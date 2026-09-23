## 2026-09-23 — issue #68 (relecture_web)

- Ajout d'un bouton « 🧹 Nettoyer ce projet » sur la page « branches d'un
  projet » (`relecture_web/templates/projet.html`), à côté du titre —
  évite de repasser par la liste des projets pour nettoyer les résumés
  `Non_Lu/` déjà pushés du seul projet sur lequel on vient de travailler.
- Nouvelle route `POST /projet/<nom_projet>/nettoyer`
  (`nettoyer_projet_route`, `relecture_web/app.py`) : réutilise la même
  logique et le même garde-fou de sécurité que
  `nettoyer_tous_les_projets_route` (issue #17) — `lister_fichiers_resumes_pushes`
  puis `_supprimer_fichiers` — limitée à `projet['dossier_relecture']` /
  `projet['repertoire']` du seul projet affiché, avec confirmation
  JavaScript avant soumission.
- Le bouton global « Nettoyer tous les projets » (page d'accueil) est
  inchangé.
- Doc : mise à jour de `RELECTURE_WEB_DOC.md` section 9 (nouvelle ligne
  « Nettoyer ce projet » dans le tableau des actions).
