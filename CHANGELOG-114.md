# CHANGELOG-114 — à fusionner dans CHANGELOG.md

## Issue #114 — 2026-10-25

- Bouton **« Fusionner le changelog »** pour un projet distant (PC fixe
  CCW) : remplace le refus explicite inconditionnel de l'issue #108.
  `git_info.detecter_changelogs_a_fusionner` (via `git ls-tree --name-only
  HEAD`, routé en SSH) détecte, à chaque ouverture de la page du projet,
  les `CHANGELOG-<N>.md` présents à la racine du clone Windows — présence
  détectée, bouton affiché (numéros concernés) ; sinon, pas de bouton.
  Le message après un merge réussi sur un projet distant
  (`fusionner_changelog_worktree`) utilise désormais cette même détection
  (il ne s'affiche plus s'il n'y a réellement rien à fusionner) et invite
  à utiliser ce bouton plutôt qu'à « fusionner manuellement ».
- `git_info.fusionner_changelog_distant` (route POST
  `/projet/<nom_projet>/fusionner-changelog-distant`, confirmation
  « légère » affichant les commandes réelles, comme le reste de l'outil) :
  vérifie que le clone est sur sa branche principale et que `git status`
  ne signale rien d'autre que le CHANGELOG à intégrer, détecte
  l'interpréteur Python disponible sur le PC fixe (« python », repli
  « py »), copie `scripts/fusionner_changelog.py` par `scp` dans un
  dossier temporaire frère des dossiers de projets, l'exécute sur le
  clone, puis committe UNIQUEMENT `CHANGELOG.md` et les `CHANGELOG-<N>.md`
  traités (message `chore: fusionne CHANGELOG-<N>.md dans CHANGELOG.md
  (auto)`, jamais de push) et affiche les trois derniers commits. La copie
  temporaire du script est toujours supprimée du PC fixe, succès ou
  échec ; un échec à mi-chemin ne committe rien et affiche (sans jamais la
  lancer) la commande de retour en arrière. Toute erreur SSH réutilise le
  classement par catégorie de l'issue #111.
- `scripts/fusionner_changelog.py` : correction d'un défaut de fins de
  ligne (le point le plus important de cette issue, même famille que le
  défaut déjà corrigé par #107) — le script lisait/écrivait
  `CHANGELOG.md` en mode texte universel, ce qui aurait converti en bloc
  tout fichier resté en LF vers CRLF une fois exécuté sur le PC fixe
  Windows (`os.linesep` différent du ThinkPad, où le défaut restait
  invisible). Lecture/écriture désormais en `newline=""` : le contenu déjà
  présent dans `CHANGELOG.md` n'est jamais retouché, seul le texte inséré
  (chaque `CHANGELOG-<N>.md`) est ramené à la fin de ligne dominante du
  fichier cible (LF, CRLF, ou mixte).
- Tests ajoutés : `relecture_web/test_fusion_changelog_distant.py` (ssh/scp
  factices exécutant réellement les commandes sur un dépôt git jetable,
  python et le script réels — un seul CHANGELOG-<N>.md, plusieurs, aucun,
  LF/CRLF/mixte, branche non principale, autres modifications présentes,
  python absent, repli « py », script en échec à mi-chemin, nettoyage de
  la copie temporaire, ccw_host non configuré) ; mise à jour de
  `relecture_web/test_chemins_windows_ccw.py` pour la nouvelle détection
  conditionnelle de `fusionner_changelog_worktree`.
- `RELECTURE_WEB_DOC.md` (§11) mis à jour.
