## Issue #118 — 2026-11-01

- `relecture_web` : nouveau garde-fou avant toute fusion (« Merger » et
  « Merger et supprimer », donc aussi l'intégration automatique du
  CHANGELOG qui la suit) — avertit puis bloque si une issue Bridge_Agent
  travaille déjà dans le dossier où le merge va réellement s'exécuter (le
  worktree dédié de la branche cible choisie s'il en a un, sinon le
  dossier principal du projet). Cas visé : un audit à périmètre dynamique
  dont le `REPO_CIBLE` est justement le dépôt où l'on fusionne — son
  contrôle d'écriture verrait le merge (ou un `git pull`) comme une
  modification extérieure et le restaurerait, avec échec définitif de
  l'issue ; le garde-fou « modifications non committées » de #74/#117 ne
  couvre pas ce cas, le dossier pouvant être parfaitement propre au
  moment du clic.
- Réutilise le code d'analyse des verrous de #88/#89
  (`git_info.lire_verrous_actifs`, même tolérance de format multi-paires,
  même lecture seule de `logs/verrous/*.lock`, même critère pid vivant)
  plutôt que d'en écrire un second — étendu aux champs `projet=`/`mode=`
  déjà posés par Bridge_Agent (#609). Nouvelle fonction
  `git_info.verrous_sur_dossier` : retourne les verrous dont le `rep=`
  (chemin réel) correspond à un dossier donné, pour les nommer dans
  l'avertissement — jamais les worktrees des AUTRES branches du même
  projet, qui ne gênent en rien ce merge précis.
- Nouveau template `confirmation_verrou_fusion.html` (même pattern que
  `echec_suppression_worktree.html`) : liste chaque verrou concerné avec
  son projet et son mode (lecture/écriture), avertit du risque, puis
  **Annuler** (lien simple, focus par défaut, retour à la page du projet)
  ou **« Fusionner quand même »** (confirmation forte, bandeau rouge).
  Contournement par champ caché `forcer_malgre_verrou=on`, jamais
  mémorisé d'une requête à l'autre ni d'un rechargement à l'autre (même
  leçon que la case « Purger », #102) — revérifié côté serveur à
  l'exécution, pas seulement à l'affichage.
- S'ajoute au refus « modifications non committées » (#74/#117) et au
  refus du badge « ⚠ CCL travaille ici » de « Merger et supprimer »
  sans les remplacer, placé avant eux pour éviter d'empiler des messages
  redondants dans une même requête.
- `RELECTURE_WEB_DOC.md` : nouvelle ligne dans le tableau des actions
  (§9) et mention de l'extension `projet=`/`mode=` dans la description du
  badge « ⚠ CCL travaille ici » (§4).
- Tests : nouveau `test_verrou_avant_fusion.py` (17 tests) — verrou vivant
  sur le dossier cible bloqué, pid mort ignoré, verrou sur un autre
  worktree du même projet sans avertissement, dossier de verrous absent,
  contournement confirmé, contournement non confirmé, non persistant
  d'une requête à l'autre. Les 188 tests existants restent verts (205 au
  total).
