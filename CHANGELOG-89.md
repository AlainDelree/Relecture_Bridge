## 2026-09-26 — issue #89 (relecture_web)

`lire_verrous_actifs` (`git_info.py`, ajoutée par #88) découpait le contenu
de chaque fichier `.lock` par `splitlines()` en supposant une paire
`clé=valeur` par ligne, avec un `partition("=")` ne coupant qu'au premier
signe `=`. En réalité, Bridge_Agent écrit tous les champs d'un verrou sur
une seule ligne séparés par des espaces (ex. `pid=213661 projet=bridge_agent
mode=ecriture rep=/home/alain/bridge_agent-issue649 claude_pgid=214244`) :
sur une seule ligne, `champs["pid"]` récupérait donc toute la fin de la
ligne au lieu du seul numéro, `_pid_vivant` échouait systématiquement, et
`lire_verrous_actifs` retournait toujours une liste vide — le badge « ⚠ CCL
travaille ici » (issue #88) ne s'affichait donc jamais, quel que soit
l'état réel des tâches. Confirmé en conditions réelles (trois worktrees
Bridge_Agent, verrous actifs lus = `[]` côté relecture_web).

- **Fix** (`git_info.py`, `lire_verrous_actifs`) : chaque ligne du fichier
  est d'abord découpée sur les espaces (`ligne.split()`) pour isoler les
  jetons `clé=valeur` individuels, avant de les répartir avec
  `partition("=")` — accepte aussi bien le format réel (tout sur une seule
  ligne) qu'un éventuel format à une paire par ligne, au cas où Bridge_Agent
  évoluerait. `_lignes_deja_pris_watcher` (citée dans le docstring comme
  suivant le même principe) ne fait qu'un test de sous-chaîne `"déjà pris"
  in ligne` — elle ne parse aucune paire `clé=valeur` et n'était pas
  concernée par ce bug.
- **Pourquoi les tests manuels de l'issue #88 ne l'ont pas détecté** : ils
  utilisaient apparemment un fichier `.lock` de test à une paire par ligne
  (`pid=...\nrep=...\nmode=...`), un format qui fonctionnait déjà avec
  l'ancien code — la documentation elle-même (`RELECTURE_WEB_DOC.md`)
  décrivait ce format à tort (« une ligne `pid=<pid>` et une ligne
  `rep=<chemin>` »), sans jamais avoir été confrontée à un vrai fichier
  généré par Bridge_Agent. Corrigée en conséquence.
- Revérifié manuellement les trois scénarios demandés : verrou à une seule
  ligne avec pid vivant → `rep=` retrouvé et `worktree_ccl_actif` renvoie
  `True` pour ce chemin ; pid mort → liste vide ; ancien format à une paire
  par ligne → toujours accepté (non-régression).
- `RELECTURE_WEB_DOC.md` mise à jour (section badges) pour décrire le
  format réel du fichier de verrou.
