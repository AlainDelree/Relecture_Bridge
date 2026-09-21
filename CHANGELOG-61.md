## 2026-09-21 — issue #61 (relecture_web)

- Ajout du bouton **« Finaliser le merge »**, pour clore le dernier geste
  manuel encore nécessaire après une résolution de conflits entièrement
  faite depuis `relecture_web` (issues #55/#56/#59) : la section « Fusion
  en conflit » de la page projet accepte automatiquement chaque fichier
  résolu (`git add`), mais le commit du merge lui-même restait à taper en
  terminal — cassant le flux visé par tout ce chantier.
  - `git_info.py` : deux nouvelles fonctions, `get_merge_en_cours`
    (`git rev-parse --verify --quiet MERGE_HEAD`, distingue un vrai merge en
    cours d'un simple conflit `UU` isolé — cherry-pick/revert en conflit ne
    créent jamais `MERGE_HEAD`) et `finaliser_commit_merge`
    (`git commit --no-edit`, l'équivalent non-interactif de `git commit`
    sans `-m` : accepte tel quel le message déjà préparé par git dans
    `.git/MERGE_MSG`, sans ouvrir d'éditeur inutilisable depuis une page
    web).
  - `app.py` : `projet_route` calcule désormais `merge_en_cours` et
    `peut_finaliser_merge` (= merge en cours ET plus aucun fichier en
    conflit) pour chaque projet. Nouvelle route
    `POST /projet/<nom_projet>/finaliser-merge` — revalide l'état git
    actuel (pas la seule page déjà affichée) avant d'appeler
    `finaliser_commit_merge`, pour ne jamais tenter un commit partiel même
    sur un formulaire soumis depuis une page obsolète.
  - `templates/projet.html` : la section « Fusion en conflit » reste
    affichée tant qu'un merge est en cours, mais bascule d'une liste de
    fichiers à résoudre vers un unique bouton « ✅ Finaliser le merge » une
    fois tous les fichiers résolus — jamais les deux à la fois, et le
    bouton n'apparaît pas tant qu'il reste un seul fichier en conflit.
    Même pattern de confirmation que les autres actions du système
    (`confirm()` JS avec commande équivalente affichée,
    `git -C <repertoire> commit --no-edit`).
  - `RELECTURE_WEB_DOC.md` (section 9, tableau des actions, et section 10)
    mises à jour en conséquence.
