## Issue #98 — 2026-10-05

- `relecture_web` : nouveau panneau repliable « 📄 .gitignore » sur la page
  projet (même principe que le panneau « Options de rejet » de l'issue
  #97), fermé par défaut, qui agit sur le `.gitignore` à la racine du
  worktree **principal** du projet (jamais ceux des worktrees de CCL, pas
  de `.gitignore` imbriqué). Trois actions :
  - **Ajouter** un motif (champ texte, ou raccourci « Ignorer » depuis la
    liste des fichiers/dossiers non suivis et non ignorés du dépôt, même
    source que le garde-fou Merger de l'issue #74) — validé avant écriture
    (une seule ligne, non vide, pas de doublon exact) ; `/` final ajouté
    automatiquement si le motif désigne un dossier existant du projet.
  - **Retirer** un motif existant (bouton ✕, jamais sur une ligne
    commentaire/vide) — confirmation légère, index et texte revérifiés
    côté serveur contre l'état actuel du fichier avant toute suppression.
  - **Ne plus suivre** (`git rm --cached`) un fichier déjà suivi qui
    correspond à un motif (piège connu de git : ajouter un motif n'arrête
    jamais de suivre un fichier déjà suivi) — jamais automatique,
    confirmation forte, bouton explicite affiché dès qu'un motif
    correspond à un fichier suivi (`git ls-files -i -c --exclude=<motif>`).
  Chaque action modifiant le fichier le committe elle-même, portée stricte
  au seul `.gitignore` (jamais `-a`/`-A`, même principe que le commit
  CHANGELOG de l'issue #74) — nécessaire pour ne jamais bloquer le
  garde-fou Merger de l'issue #74 sur une modification non committée.
  Refus commun aux trois actions, avant toute lecture : projet distant (PC
  fixe CCW, #94 — surface hors-git non traitée), fusion en cours
  (`MERGE_HEAD`), badge « ⚠ CCL travaille ici » actif sur le worktree
  principal, ou `.gitignore` déjà modifié de façon non committée d'origine
  extérieure (jamais embarqué silencieusement dans le commit automatique).
- `git_info.py` : nouvelles fonctions `chemin_gitignore`,
  `lire_lignes_gitignore`/`ecrire_lignes_gitignore` (préservent l'ordre,
  les commentaires et les fins de ligne du fichier existant),
  `classifier_ligne_gitignore`, `ajouter_motif_gitignore`,
  `committer_gitignore`, `gitignore_a_des_modifications_non_committees`,
  `get_fichiers_suivis_correspondant` (simule l'effet d'un motif via
  `git ls-files -i -c --exclude=`, même moteur de correspondance que git),
  `retirer_du_suivi` et `get_fichiers_non_suivis`. `retirer_du_suivi` ne
  committe pas avec un pathspec comme `committer_gitignore` : une fois le
  fichier redevenu non suivi par `rm --cached`, `git commit -- <chemin>`
  répond « rien à valider » au lieu de committer la suppression pourtant
  déjà indexée (vérifié) — un commit sans pathspec est utilisé à la place,
  mais seulement si l'index est déjà vide avant le `rm --cached`, pour
  garantir qu'aucun autre changement tiers n'est embarqué.
- `RELECTURE_WEB_DOC.md` section 9 : une ligne par action (ajout,
  suppression, ne plus suivre) avec son niveau de confirmation, et note
  sur le commit automatique limité au `.gitignore` et le refus commun aux
  trois actions.
