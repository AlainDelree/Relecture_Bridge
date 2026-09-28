## 2026-09-28 — issue #92 (relecture_web)

`relecture_web` n'avait jusqu'ici aucune authentification, en écoute
stricte sur `127.0.0.1` — un choix assumé tant que l'outil restait
strictement local, mais un préalable bloquant avant d'envisager un jour un
accès réseau (LAN, ou exposition externe pour piloter un futur PC fixe
Windows) : `relecture_web` peut déclencher merge, push, suppression de
branches et de worktrees, un enjeu plus grand que `new_issue.py` à l'époque
où il n'avait lui non plus aucune protection.

- **Ajout — `relecture_web/auth.py`** : mot de passe haché en sha256
  (`relecture_web/mot_de_passe.conf`, jamais en clair, permissions 0600,
  gitignoré), comparaison en temps constant (`hmac.compare_digest`),
  `SECRET_KEY` Flask persistée (`relecture_web/secret_key.conf`, même
  protection) et génération d'un certificat auto-signé via `openssl`
  (`relecture_web/ssl/`, généré une seule fois puis réutilisé). Aucun code
  partagé avec `bridge_agent`/`new_issue.py` — même principe, implémentation
  propre à ce dépôt.
- **Ajout — `--set-password`** (`app.py`) : demande le mot de passe deux
  fois (confirmation, saisie masquée via `getpass`), puis quitte sans
  lancer le serveur.
- **Ajout — modes `--lan` / `--externe`** (`app.py`), mêmes noms que
  `bridge_agent` pour la cohérence : par défaut inchangé (`127.0.0.1`,
  HTTP, mot de passe jamais exigé) ; `--lan` (`0.0.0.0`, HTTP, sans mot de
  passe, réseau de confiance) ; `--externe` (`0.0.0.0`, HTTPS obligatoire,
  mot de passe obligatoire — refuse de démarrer sans mot de passe configuré,
  avec message clair). `--lan` et `--externe` sont mutuellement exclusifs
  (erreur explicite `argparse`).
- **Ajout — décorateur `@login_requis`** appliqué à toutes les routes
  existantes (`app.py`) : transparent tant que le mode courant n'exige pas
  de mot de passe (défaut, `--lan`), redirige vers `/connexion` sinon
  (`--externe` uniquement).
- **Ajout — routes `/connexion` et `/deconnexion`**, template
  `templates/connexion.html` (page autonome, hors barre latérale) et
  styles associés (`static/style.css`).
- **Session persistante** : `PERMANENT_SESSION_LIFETIME` fixé à 30 jours,
  `session.permanent = True` posé à la connexion réussie — une session
  survit désormais aux redémarrages fréquents de `relecture_web` (usage non
  permanent, relancé manuellement à chaque merge d'issue) sans devenir
  illimitée.
- **Doc** : `RELECTURE_WEB_DOC.md` (section « Lancement et modes réseau »)
  et `relecture_web/README.md` mis à jour — la mention « usage strictement
  local, aucune authentification » ne décrivait plus que le mode par défaut.
- **Hors périmètre** (rappel explicite de l'issue) : le mode SSH vers un
  futur PC fixe Windows (issue #91) n'est pas traité ici — cette issue pose
  seulement l'authentification, prérequis avant d'envisager un jour une
  exposition réelle. Le host d'écoute par défaut ne change pas.
