## Nature du changement
Ajout d'un flux de suppression de projet côté CCL/local (issue #587) : nouveau script CLI `supprimer_projet.py` (orchestrateur + mode dry-run) et son pendant web `app/supprimer_projet.py` exposant deux routes (`GET /supprimer-projet/verifier/<nom>`, `POST /supprimer-projet`). L'orchestrateur démonte, dans un ordre inverse à la création, le répertoire de travail (contenu + `.git`), le `configs/<nom>.conf`, puis régénère §2/§7 de `BRIDGE_AGENT_DOC.md`. S'y ajoutent l'UI (zone dangereuse + modal de confirmation dans `index.html`/`app.js`), l'enregistrement des routes, la doc et une suite de 9 tests.

## Intention probable
Automatiser le décommissionnement d'un projet, jusqu'ici manuel et risqué (8 cibles à nettoyer), en offrant un pendant symétrique à `nouveau_projet.py`, volontairement limité au côté CCL/local (GitHub et CCW restant hors scope).

## Points d'attention
- **Geste destructeur irréversible** : `shutil.rmtree()` sur `REP_TRAVAIL` lu tel quel dans le `.conf`, avec `expanduser()`. Un `REP_TRAVAIL` vide, `/`, `~` ou pointant vers un chemin sensible entraînerait la suppression d'un arbre non voulu — aucune validation/borne du chemin (ex. vérifier qu'il est bien sous la racine des projets) n'est présente. À vérifier avant de pousser.
- **Sécurité des routes** : `POST /supprimer-projet` est protégé par `login_requis` et revérifie la confirmation côté serveur (bon réflexe), mais aucune protection CSRF n'apparaît sur cette route destructive JSON — à confirmer selon le dispositif global de l'app.
- **Ordre d'application inter-commits/worktrees** : ce commit s'inscrit dans un chantier scindé (issues CCL/CCW coordonnées) ; la régénération de doc relit `configs/*.conf` et modifie `BRIDGE_AGENT_DOC.md` localement — attention aux conflits si d'autres worktrees touchent la même doc/les mêmes configs. Les changements ne sont volontairement jamais poussés : le commit/push de `configs/` et de la doc reste à faire à la main.
- **Validation d'entrée** : `nom` est normalisé (`strip().lower()`) mais n'est pas assaini contre des séparateurs de chemin (`../`, `/`) avant construction de `configs/<nom>.conf` — à vérifier que `DOSSIER_CONFIGS / f"{nom}.conf"` ne permet pas de sortir du dossier `configs/`.
- Test bout-en-bout réel non effectué dans le worktree (pas d'accès réseau) — explicitement laissé à valider par Alain.
