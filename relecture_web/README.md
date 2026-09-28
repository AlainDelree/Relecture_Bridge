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
python3 relecture_web/app.py             # 127.0.0.1, HTTP, sans mot de passe (défaut)
python3 relecture_web/app.py --lan       # 0.0.0.0, HTTP, sans mot de passe
python3 relecture_web/app.py --externe   # 0.0.0.0, HTTPS, mot de passe obligatoire
python3 relecture_web/app.py --set-password
```

Sert sur le port `5057/`. Voir `RELECTURE_WEB_DOC.md` (section « Lancement
et modes réseau ») pour le détail de l'authentification (issue #92) —
mêmes noms de modes que `new_issue.py`, implémentation propre à
`relecture_bridge` (`relecture_web/auth.py`), sans code partagé.
