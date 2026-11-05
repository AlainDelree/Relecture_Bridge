## Issue #129 — 2026-11-05

- `relecture_web` : sur la page « branches d'un projet », un petit symbole
  apparaît désormais devant le chip coloré du nom du projet quand il est
  équipé d'un crochet `pre-push` — 🪝 avec l'info-bulle « Crochet pre-push
  actif : les tests se lancent avant chaque push ». Réutilise exactement
  `git_info.projet_equipe_hook_pre_push` (la même détection que le push
  lui-même, issue #122) : jamais une seconde logique, le symbole reflète
  toujours fidèlement ce que fera un push réel sur ce projet.
- Nouveau cas d'avertissement, `git_info.
  projet_a_hook_pre_push_non_executable` : ⚠️ avec l'info-bulle « Crochet
  pre-push présent mais non exécutable : ignoré par git, aucun test ne se
  lance » pour un fichier de crochet présent mais privé du droit
  d'exécution (`chmod +x` oublié) — même résolution de chemin que
  `projet_equipe_hook_pre_push` (`chemin_hook_pre_push`), mutuellement
  exclusif avec le cas actif. Rien du tout pour un projet sans crochet, ni
  pour un projet distant du PC fixe CCW.
- Affichage seulement : aucun changement de comportement du push, des
  verrous ni de l'état persistant. Si la détection échoue ou lève une
  exception, elle est absorbée dans `app.projet_route` — aucun symbole
  n'est affiché et la page se charge normalement.
- Volontairement absent de la barre latérale et de la page d'accueil
  (issue #44) : une détection par projet y lancerait une commande git par
  projet sur chaque page, alors que la page du projet n'en fait qu'une
  seule, pour le seul projet affiché.
- Tests (`test_symbole_hook_pre_push.py`, dépôts jetables, aucun accès au
  vrai disque local) : crochet exécutable (symbole actif), crochet non
  exécutable (avertissement), aucun crochet (rien), projet distant (rien,
  au niveau de `git_info`), détection en erreur (page chargée sans
  symbole). Suite complète (315 tests) toujours verte.
- Documentation : `RELECTURE_WEB_DOC.md` mise à jour (section 2 — nouveau
  paragraphe sur le symbole ; section 13 — nouveau paragraphe dans le
  guide d'adoption du crochet).
