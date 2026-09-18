# relecture_web

Programme web indépendant, propre à `relecture_bridge` : affiche, pour
chaque projet Bridge_Agent listé dans `BRIDGE_AGENT_DOC.md`, ses worktrees
actifs et ses commits locaux en attente de push.

Distinct de `new_issue.py` (dépôt `bridge_agent`) — ne réutilise ni ne
dépend de son code. La lecture git (`git worktree list`, `git log` sur
l'amont configuré) est réimplémentée dans `git_info.py`.

Vocation à devenir la maison des futures actions de relecture (résumés
scannables, merge/suppression de worktree) — pas un simple visualiseur en
lecture seule pour l'instant.

## Lancer

```bash
python3 relecture_web/app.py
```

Sert sur `http://127.0.0.1:5057/`. Usage local uniquement, pas de
protection par mot de passe (même choix que `new_issue.py`).
