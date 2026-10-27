# CHANGELOG-117 — à fusionner dans CHANGELOG.md

## Issue #117 — 2026-10-27

- Garde-fou « Modifications non committées » (Merger, Merger et
  supprimer — issue #74) : le message de refus nomme désormais les
  fichiers concernés avec leur statut (`chemin (modifié|non suivi|
  supprimé|renommé|copié|ajouté|conflit)`), plafonné à une dizaine
  d'entrées puis « … et N autres », en précisant qu'il s'agit du dossier
  principal du projet et que ces fichiers peuvent être non suivis par
  git — auparavant, seul leur nombre était donné
  (`git_info.get_modifications_non_committees_detaillees`/
  `decrire_modifications_non_committees`).
- Panneau repliable « 📄 .gitignore » (issue #98) : déplacé du haut de la
  page projet (juste sous les messages flash) vers une nouvelle section
  « 🛠️ Outils du projet » en bas de page, sous la liste des branches —
  cas réel (projet rummikub) où le message de refus ci-dessus, trop
  elliptique, avait fait conclure à tort (y compris à un Claude Chat
  consulté sur capture d'écran) que le fichier `.gitignore` du panneau
  était la cause du refus, alors que ce panneau n'a aucun rapport.
  Identifiant (`#details-gitignore`) et fonctionnalité (ajouter/retirer
  un motif, « Ne plus suivre ») inchangés.
