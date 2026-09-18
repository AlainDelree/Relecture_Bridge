c089f30

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c089f30
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 23:23:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #337 : parallélisation des issues mode_write via git worktrees
    
    Plusieurs issues mode_write peuvent désormais tourner en parallèle, chacune
    dans un worktree git isolé sur sa propre branche, au lieu du traitement
    strictement séquentiel historique. Nouvelle clé MAX_WRITE_PARALLELE (défaut
    2, 1 ou 0 = comportement historique inchangé) ; verrou anti-collision posé
    par chemin de travail effectif (REP_TRAVAIL ou worktree) plutôt que par
    REP_TRAVAIL seul ; worktrees jamais supprimés automatiquement (fusion/push
    manuels par Alain) ; auto-extinction différée tant qu'un thread mode_write
    tourne. Doc §13 + CHANGELOG-337.md + test de non-régression.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d6a5777..7ac4e2b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1028 (6 ligne(s)) dans l'ancienne version → ligne 1028 (60 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1028,6 +1028,60 @@ a été remplacée par les deux seuls droits que documente Microsoft pour
   dans l'en-tête de l'issue (l'appel reste bloqué à attendre une réponse qui
   ne vient jamais, jusqu'à expiration).
 
+### Parallélisation mode_write via git worktrees (issue #337)
+
+Par défaut, plusieurs issues `mode_write` peuvent désormais tourner **en
+parallèle**, chacune dans son propre `git worktree` (répertoire frère isolé,
+sur sa propre branche) — au lieu du traitement strictement séquentiel
+historique (un seul `mode_write` à la fois, dans `REP_TRAVAIL`). Les issues
+`mode_lecture`/`mode_scratch` restent, elles, toujours traitées
+séquentiellement dans `REP_TRAVAIL` (hors périmètre de cette issue).
+
+- **`MAX_WRITE_PARALLELE`** (`.conf`, entier, défaut **2**) — nombre maximum
+  de tâches `mode_write` concurrentes. `1` = comportement séquentiel
+  historique intégral (aucun thread, aucun worktree créé, `traiter_issue`
+  reste synchrone). `0` = désactivé, identique à `1`.
+- **Décision de parallélisation** (`traiter_issue`, point d'entrée public
+  appelé pour chaque issue) : la **première** issue `mode_write` détectée
+  sans autre tâche `mode_write` déjà en cours est dispatchée dans un thread
+  Python ciblant `REP_TRAVAIL` directement — **sans worktree** — nécessaire
+  pour que la boucle principale (mono-thread) reste libre de détecter une
+  éventuelle deuxième issue `mode_write` pendant que la première tourne
+  encore ; sans cela, un `traiter_issue` bloquant sur la première tâche
+  empêcherait à jamais d'en atteindre une seconde. Les issues `mode_write`
+  **suivantes**, détectées pendant qu'au moins un thread est déjà actif et
+  sous `MAX_WRITE_PARALLELE`, obtiennent chacune un worktree dédié.
+- **Worktree** : chemin `<REP_TRAVAIL>/../<NOM_PROJET>-issue<N>` (répertoire
+  frère de `REP_TRAVAIL`), branche `worktree-issue-<N>`, créés par
+  `git -C <REP_TRAVAIL> worktree add <chemin> -b worktree-issue-<N>`. Si le
+  chemin ou la branche existe déjà, ou si `git worktree add` échoue pour
+  toute autre raison, repli propre sur le traitement séquentiel classique
+  (l'issue attend qu'un slot se libère au prochain cycle) — jamais
+  d'exception propagée.
+- **CHANGELOG** : dans un worktree, CCL reçoit une consigne de prompt dédiée
+  lui demandant d'écrire son entrée dans `CHANGELOG-<N>.md` à la racine du
+  worktree plutôt que dans `CHANGELOG.md` directement, pour éviter un
+  conflit systématique sur ce fichier unique entre worktrees actifs en
+  parallèle — voir `scripts/fusionner_changelog.py` (issue #336), qui
+  intègre ces fichiers dans `CHANGELOG.md` avant le push d'Alain (lancement
+  manuel, pas encore appelé automatiquement par `watcher.py`).
+- **Verrou anti-collision (issue #189/#322)** : posé par `chemin_travail`
+  (le `REP_TRAVAIL` ou le worktree effectif de CETTE tâche), et non plus
+  systématiquement par `REP_TRAVAIL` seul — deux worktrees du même projet
+  obtiennent donc deux verrous distincts et peuvent tourner sans s'attendre,
+  tandis qu'une issue `mode_lecture`/`mode_scratch` visant `REP_TRAVAIL`
+  pendant qu'un worktree y tourne encore (premier slot) reste bloquée par
+  le même verrou qu'avant, reprise au cycle suivant.
+- **Fin de tâche** : le worktree n'est **jamais** supprimé automatiquement
+  (ni `git worktree remove`, ni suppression de la branche) — Alain merge et
+  pousse manuellement une fois le travail relu. Le numéro d'issue, le
+  chemin du worktree et la branche sont journalisés clairement en fin de
+  traitement.
+- **Auto-extinction (§13 ci-dessus)** : le watcher ne s'éteint jamais tant
+  qu'un thread `mode_write` tourne encore, même si `DELAI_INACTIVITE_MIN`
+  est dépassé — réévalué à chaque cycle, dès qu'un thread se termine
+  l'extinction redevient possible.
+
 ---
 
 ## 14. Délégation Chef → Ouvrier (changement d'environnement)
# (diff du fichier suivant)
diff --git a/CHANGELOG-337.md b/CHANGELOG-337.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..c695c89
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/CHANGELOG-337.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (57 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,57 @@
+## 2 août 2026 — issue #337
+
+Parallélisation des issues `mode_write` via `git worktree` : `watcher.py`
+peut désormais traiter plusieurs tâches d'écriture **en parallèle**, chacune
+dans un répertoire isolé sur sa propre branche, au lieu du traitement
+strictement séquentiel historique. Les issues `mode_lecture`/`mode_scratch`
+restent traitées séquentiellement dans `REP_TRAVAIL`, inchangées.
+
+- Nouvelle clé `.conf` `MAX_WRITE_PARALLELE` (entier, défaut `2`) : nombre
+  maximum de tâches `mode_write` concurrentes. `1` (ou `0`) = comportement
+  séquentiel historique intégral, aucun thread ni worktree créé.
+- `traiter_issue` (nouveau point d'entrée public) décide, pour chaque issue
+  `mode_write` prête, entre traitement séquentiel classique et
+  parallélisation : la première tâche détectée sans autre `mode_write` déjà
+  en cours est dispatchée dans un thread ciblant `REP_TRAVAIL` directement
+  (sans worktree, nécessaire pour que la boucle principale reste libre de
+  détecter une deuxième tâche pendant que la première tourne) ; les
+  suivantes, sous `MAX_WRITE_PARALLELE`, obtiennent chacune un worktree
+  dédié (`<REP_TRAVAIL>/../<PROJET>-issue<N>`, branche
+  `worktree-issue-<N>`, créés via `git worktree add`). Le corps de
+  traitement existant (`_traiter_issue_synchrone`) est inchangé, à
+  l'exception du chemin de travail effectif qu'il reçoit désormais en
+  paramètre.
+- Liste thread-safe (`threading.Lock` + liste) des tâches `mode_write`
+  actuellement en thread (numéro, chemin du worktree ou `None`, thread
+  Python), purgée des threads terminés à chaque décision de dispatch et en
+  tête de boucle principale.
+- Garde-fous à la création du worktree : chemin ou branche déjà existants,
+  ou tout autre échec de `git worktree add` → repli propre sur le
+  traitement séquentiel (l'issue attend qu'un slot se libère), jamais
+  d'exception propagée.
+- `lancer_claude` reçoit `chemin_worktree` : injecte dans le prompt, en
+  worktree uniquement, un bloc d'avertissement (chemin, branche, consigne
+  d'écrire l'entrée changelog dans `CHANGELOG-<N>.md` plutôt que
+  `CHANGELOG.md` — voir `scripts/fusionner_changelog.py`, issue #336).
+  Toutes les opérations déjà paramétrées par `cwd`/`perimetre` (backup,
+  clause de périmètre du prompt, opérations git de garde-fou) reçoivent
+  déjà le chemin de travail effectif (worktree ou `REP_TRAVAIL`) — aucun
+  changement de signature nécessaire sur ces fonctions.
+- Verrou anti-collision (#189/#322) posé par le chemin de travail effectif
+  de la tâche (`REP_TRAVAIL` ou le worktree), et non plus systématiquement
+  par `REP_TRAVAIL` seul : deux worktrees du même projet obtiennent deux
+  verrous distincts et tournent sans s'attendre l'un l'autre.
+- Fin de tâche en worktree : **aucune suppression automatique** (ni
+  `git worktree remove`, ni suppression de branche) — Alain merge et pousse
+  manuellement une fois le travail relu. Numéro d'issue, chemin du worktree
+  et branche journalisés clairement.
+- Auto-extinction (#199/#200) : ne se déclenche plus tant qu'un thread
+  `mode_write` tourne encore, même au-delà de `DELAI_INACTIVITE_MIN` —
+  réévaluée à chaque cycle.
+- `BRIDGE_AGENT_DOC.md` §13 documente le mécanisme et `MAX_WRITE_PARALLELE`.
+- Test de non-régression `tests/test_worktree_parallelisation_337.py` :
+  nommage chemin/branche, création + replis (chemin/branche déjà pris),
+  purge des threads terminés, scénario de bout en bout à deux issues
+  `mode_write` concurrentes (première dans `REP_TRAVAIL`, seconde dans un
+  worktree dédié, worktree conservé après coup), et non-régression avec
+  `MAX_WRITE_PARALLELE = 1`.
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 3f365d6..a0d8e35 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 28 (6 ligne(s)) dans l'ancienne version → ligne 28 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,6 +28,7 @@ import tempfile
 import platform
 import signal
 import shutil
+import threading
 import ctypes
 import ctypes.wintypes
 from logging.handlers import RotatingFileHandler
# ── Zone modifiée : ligne 238 (6 ligne(s)) dans l'ancienne version → ligne 239 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -238,6 +239,7 @@ class Config:
     notifier_local: bool   = True  # ce watcher émet-il lui-même bip/notify-send/ntfy à la fin d'une issue (issue #187) ? True = comportement historique. Mettre à False sur la VM CCW (et éventuellement CCL) pour laisser new_issue.py notifier de façon centralisée sur le ThinkPad, sans doublon.
     delai_inactivite_min: int = 20  # auto-extinction : minutes sans aucune issue traitable avant que le watcher ne s'arrête proprement (issue #200). 0 = désactivé (le watcher tourne indéfiniment, comportement historique).
     libelle_agent: str     = ""    # libellé de l'agent affiché dans l'ACK (ex. "agent Linux", "agent Windows") — vide = déduit automatiquement de la plateforme (issue #239)
+    max_write_parallele: int = 2   # parallélisation mode_write via git worktrees (issue #337) : nombre max de tâches mode_write concurrentes. 1 = comportement séquentiel historique (aucun worktree, aucun thread). 0 = désactivé (identique à 1).
 
     @property
     def url_ntfy(self) -> str:
# ── Zone modifiée : ligne 330 (6 ligne(s)) dans l'ancienne version → ligne 332 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -330,6 +332,7 @@ def charger_config(chemin: Path) -> Config:
         notifier_local      = booleen("NOTIFIER_LOCAL", True),
         delai_inactivite_min = entier("DELAI_INACTIVITE_MIN", 20),
         libelle_agent       = brut.get("LIBELLE_AGENT", ""),
+        max_write_parallele = entier("MAX_WRITE_PARALLELE", 2),
     )
 
 
# ── Zone modifiée : ligne 1899 (7 ligne(s)) dans l'ancienne version → ligne 1902 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1899,7 +1902,8 @@ def lancer_claude(numero: int, titre: str, body: str, dry_run: bool,
                   perimetre: str = None,
                   cwd: Path = None,
                   verrou: Path = None,
-                  chemin_scratch: Path = None) -> tuple[bool, str]:
+                  chemin_scratch: Path = None,
+                  chemin_worktree: Path = None) -> tuple[bool, str]:
     """
     Lance Claude Code en mode non-interactif sur une issue.
 
# ── Zone modifiée : ligne 1934 (6 ligne(s)) dans l'ancienne version → ligne 1938 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1934,6 +1938,13 @@ def lancer_claude(numero: int, titre: str, body: str, dry_run: bool,
     brutalement avant la fin du traitement. None = pas de verrou associé (ex.
     passe diagnostique) : aucun pgid n'est consigné, comportement inchangé.
 
+    chemin_worktree : chemin du worktree git isolé de cette tâche (issue #337),
+    si la parallélisation mode_write y a placé CCL. Sert uniquement à injecter
+    dans le prompt un bloc d'avertissement dédié (worktree/branche/consigne
+    CHANGELOG-<N>.md) — `cwd` porte déjà le répertoire RÉEL du subprocess
+    (worktree ou REP_TRAVAIL). None = traitement hors worktree (comportement
+    inchangé, aucun bloc injecté).
+
     Retourne (succès, sortie).
     """
     if mode == MODE_LECTURE_ACTIVE and chemin_scratch is None:
# ── Zone modifiée : ligne 2010 (7 ligne(s)) dans l'ancienne version → ligne 2021 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2010,7 +2021,11 @@ fichier, n'exécute aucune commande modifiant l'état du système ou du dépôt.
     if CFG.fichier_contexte:
         chemin_ctx = Path(CFG.fichier_contexte).expanduser()
         if not chemin_ctx.is_absolute():
-            chemin_ctx = CFG.rep_travail / chemin_ctx
+            # cwd_effectif (pas CFG.rep_travail) : en worktree (issue #337), le
+            # fichier de contexte relatif doit être lu depuis le worktree — un
+            # `git worktree` contient une copie complète des fichiers suivis,
+            # CONTEXTE.md y est donc présent au même chemin relatif.
+            chemin_ctx = cwd_effectif / chemin_ctx
         if chemin_ctx.exists():
             try:
                 contenu = chemin_ctx.read_text(encoding="utf-8", errors="replace")
# ── Zone modifiée : ligne 2051 (6 ligne(s)) dans l'ancienne version → ligne 2066 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2051,6 +2066,23 @@ fichier, n'exécute aucune commande modifiant l'état du système ou du dépôt.
     else:
         clause_perimetre = ""
 
+    # Bloc d'avertissement worktree (issue #337) : injecté UNIQUEMENT quand
+    # cette tâche mode_write tourne dans un worktree git isolé (parallélisation
+    # active), pour que CCL sache où il se trouve réellement et respecte la
+    # convention CHANGELOG-<N>.md (fusionnée plus tard par
+    # scripts/fusionner_changelog.py, avant le push d'Alain — jamais dans
+    # CHANGELOG.md directement, qui provoquerait un conflit avec les autres
+    # worktrees actifs en parallèle).
+    bloc_worktree = ""
+    if chemin_worktree is not None:
+        bloc_worktree = (
+            f"\n⚠️ Tu travailles dans un worktree isolé : {chemin_worktree}\n"
+            f"Branche : worktree-issue-{numero}\n"
+            f"CHANGELOG : écris ton entrée dans CHANGELOG-{numero}.md à la racine de ce "
+            f"worktree, PAS dans CHANGELOG.md. Le script fusionner_changelog.py "
+            f"intégrera CHANGELOG-{numero}.md dans CHANGELOG.md avant le push.\n"
+        )
+
     if prompt_perso is not None:
         prompt = prompt_perso
     else:
# ── Zone modifiée : ligne 2061 (7 ligne(s)) dans l'ancienne version → ligne 2093 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2061,7 +2093,7 @@ TITRE : {titre}
 
 BODY :
 {body}
-{bloc_contexte}{bloc_consignes}{clause_perimetre}{garde_fou}
+{bloc_contexte}{bloc_consignes}{clause_perimetre}{bloc_worktree}{garde_fou}
 Instructions :
 1. Lis attentivement la tâche demandée
 2. Effectue le travail demandé (dans les limites du mode ci-dessus)
# ── Zone modifiée : ligne 2249 (6 ligne(s)) dans l'ancienne version → ligne 2281 (101 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2249,6 +2281,101 @@ probables, sans préambule ni conclusion, et sans tenter de corriger quoi que ce
 issues_en_cours: set[int] = set()
 
 
+# ─── Parallélisation mode_write via git worktrees (issue #337) ─────────────────
+# But : permettre à plusieurs issues mode_write de tourner EN PARALLÈLE, chacune
+# dans son propre worktree git (répertoire frère isolé, sur sa propre branche),
+# sans conflit d'accès fichier — au lieu du traitement strictement séquentiel
+# historique (un seul mode_write à la fois, dans REP_TRAVAIL).
+#
+# `_threads_ecriture` : liste thread-safe (protégée par `_verrou_threads_ecriture`,
+# un `threading.Lock` — SANS RAPPORT avec les verrous FICHIER inter-process de
+# #189/#322, cf. `acquerir_verrou`) des tâches mode_write actuellement dispatchées
+# dans un thread Python. Chaque entrée : {"numero", "worktree" (None si la tâche
+# tourne dans REP_TRAVAIL, cf. décision ci-dessous), "thread"}.
+#
+# Décision de parallélisation (voir `traiter_issue`, point d'entrée public) :
+# la PREMIÈRE tâche mode_write d'un lot est dispatchée dans un thread ciblant
+# REP_TRAVAIL (worktree=None) — nécessaire pour que la boucle principale reste
+# libre de détecter une deuxième tâche mode_write pendant que la première
+# tourne encore (une boucle `while True` mono-thread ne peut sinon jamais
+# atteindre une deuxième issue tant que `traiter_issue` bloque sur la
+# première). Les tâches mode_write SUIVANTES, détectées pendant qu'au moins un
+# thread mode_write est déjà actif et que `MAX_WRITE_PARALLELE` n'est pas
+# atteint, obtiennent chacune un worktree dédié. `MAX_WRITE_PARALLELE <= 1`
+# désactive tout le mécanisme : traitement strictement séquentiel historique,
+# aucun thread, aucun worktree — comportement identique à avant #337.
+_verrou_threads_ecriture = threading.Lock()
+_threads_ecriture: list[dict] = []
+
+
+def _nettoyer_threads_ecriture_termines() -> None:
+    """Purge, sous verrou, les entrées dont le thread Python est terminé."""
+    with _verrou_threads_ecriture:
+        _threads_ecriture[:] = [t for t in _threads_ecriture if t["thread"].is_alive()]
+
+
+def _threads_ecriture_actifs() -> list[dict]:
+    """Instantané des tâches mode_write actuellement en thread, APRÈS purge
+    des threads terminés. Best-effort de lecture cohérente : le nettoyage et
+    la copie sont deux opérations séparées (léger risque qu'un thread se
+    termine entre les deux, sans conséquence — juste une entrée fantôme lue
+    une fois, purgée au prochain appel)."""
+    _nettoyer_threads_ecriture_termines()
+    with _verrou_threads_ecriture:
+        return list(_threads_ecriture)
+
+
+def _nb_threads_ecriture_actifs() -> int:
+    return len(_threads_ecriture_actifs())
+
+
+def _chemin_worktree(numero: int) -> Path:
+    """Chemin du worktree d'une issue mode_write (issue #337) : répertoire
+    FRÈRE de REP_TRAVAIL, nommé d'après le NOM du projet (CFG.nom, pas le nom
+    du dossier REP_TRAVAIL — ce sont deux choses potentiellement différentes)."""
+    return CFG.rep_travail.parent / f"{CFG.nom}-issue{numero}"
+
+
+def _branche_worktree(numero: int) -> str:
+    return f"worktree-issue-{numero}"
+
+
+def _creer_worktree(numero: int) -> Path | None:
+    """Crée le worktree git dédié à l'issue mode_write `numero` (issue #337) :
+    `git -C <REP_TRAVAIL> worktree add <chemin> -b worktree-issue-<numero>`.
+
+    Garde-fous (échec propre, jamais d'exception propagée) : chemin déjà
+    existant (vérifié AVANT l'appel git, évite une tentative vouée à
+    l'échec), ou `git worktree add` en échec pour toute autre raison (branche
+    déjà existante, etc.) — dans les deux cas, retourne None et journalise ;
+    l'appelant retombe alors sur le traitement séquentiel (l'issue attend
+    qu'un slot se libère)."""
+    chemin = _chemin_worktree(numero)
+    branche = _branche_worktree(numero)
+    if chemin.exists():
+        log.warning(
+            f"  Worktree #{numero} : {chemin} existe déjà — fallback séquentiel "
+            f"(l'issue attend qu'un slot se libère)."
+        )
+        return None
+    try:
+        res = subprocess.run(
+            ["git", "-C", str(CFG.rep_travail), "worktree", "add", str(chemin), "-b", branche],
+            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
+        )
+    except (OSError, subprocess.SubprocessError) as e:
+        log.warning(f"  Worktree #{numero} : exception à la création ({e}) — fallback séquentiel.")
+        return None
+    if res.returncode != 0:
+        log.warning(
+            f"  Worktree #{numero} : échec de création (branche '{branche}' déjà "
+            f"existante ?) — {res.stderr.strip()} — fallback séquentiel."
+        )
+        return None
+    log.info(f"  Worktree #{numero} créé : {chemin} (branche {branche}).")
+    return chemin
+
+
 def _chemin_verrou(rep_travail: Path) -> Path:
     """Chemin du fichier de verrou associé à un répertoire de travail donné.
 
# ── Zone modifiée : ligne 2642 (7 ligne(s)) dans l'ancienne version → ligne 2769 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2642,7 +2769,13 @@ def _restaurer_rep_travail_modifie(numero: int, cwd: Path,
     return list(nouveaux.keys())
 
 
-def traiter_issue(issue: dict, dry_run: bool):
+def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path | None = None):
+    """Corps du traitement d'une issue — inchangé depuis avant #337, à
+    l'exception du paramètre `chemin_worktree` (issue #337) : chemin du
+    worktree git isolé où cette tâche mode_write doit tourner, ou None pour le
+    traitement classique dans REP_TRAVAIL. Appelée soit directement (issues
+    lecture/lecture active, ou mode_write hors parallélisation), soit depuis un
+    thread dédié via `traiter_issue` (point d'entrée public, voir plus bas)."""
     numero = issue["number"]
     titre  = issue["title"]
     body   = issue.get("body") or ""
# ── Zone modifiée : ligne 2686 (6 ligne(s)) dans l'ancienne version → ligne 2819 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2686,6 +2819,11 @@ def traiter_issue(issue: dict, dry_run: bool):
     log.info(f"→ Issue #{numero} détectée : '{titre}' [priorité: {priorite}] [mode: {mode_txt}]")
     if mode == MODE_ECRITURE:
         log.warning(f"  ⚠️  MODE ÉCRITURE ARMÉ pour #{numero} (label '{LABEL_ECRITURE}') — actions permises, push interdit.")
+        if chemin_worktree is not None:
+            log.info(
+                f"  Issue #{numero} : traitement en worktree isolé {chemin_worktree} "
+                f"(branche {_branche_worktree(numero)}) — parallélisation mode_write, issue #337."
+            )
     elif mode == MODE_LECTURE_ACTIVE:
         log.warning(
             f"  ⚠️  MODE LECTURE ACTIVE ARMÉ pour #{numero} (label '{LABEL_SCRATCH}') — "
# ── Zone modifiée : ligne 2707 (6 ligne(s)) dans l'ancienne version → ligne 2845 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2707,6 +2845,16 @@ def traiter_issue(issue: dict, dry_run: bool):
     cwd_effectif       = CFG.rep_travail
     avertissement_conflit = ""
 
+    # Worktree isolé (issue #337) : chemin_travail effectif de CETTE tâche —
+    # remplace REP_TRAVAIL comme cwd du subprocess ET comme périmètre du
+    # prompt (Claude tourne physiquement dans ce dossier frère, un périmètre
+    # resté sur REP_TRAVAIL le bloquerait en pratique). Hors périmètre
+    # dynamique uniquement (#125) : les deux mécanismes ne se combinent pas,
+    # REPO_CIBLE reste seul décisif si les deux sont actifs par erreur.
+    if chemin_worktree is not None and not CFG.perimetre_dynamique:
+        cwd_effectif       = chemin_worktree
+        perimetre_effectif = str(chemin_worktree)
+
     if CFG.perimetre_dynamique:
         repo_cible = extraire_repo_cible(body)
         if not repo_cible:
# ── Zone modifiée : ligne 2839 (7 ligne(s)) dans l'ancienne version → ligne 2987 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2839,7 +2987,8 @@ def traiter_issue(issue: dict, dry_run: bool):
             succes, sortie = lancer_claude(numero, titre, body, dry_run, mode,
                                            timeout, modele,
                                            perimetre=perimetre_effectif, cwd=cwd_effectif,
-                                           verrou=verrou, chemin_scratch=chemin_scratch)
+                                           verrou=verrou, chemin_scratch=chemin_scratch,
+                                           chemin_worktree=chemin_worktree)
 
             if empreinte_configs_avant is not None:
                 _restaurer_configs_modifies(numero, empreinte_configs_avant)
# ── Zone modifiée : ligne 3063 (6 ligne(s)) dans l'ancienne version → ligne 3212 (127 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3063,6 +3212,127 @@ def traiter_issue(issue: dict, dry_run: bool):
         # `try` ci-dessus.
         if chemin_scratch is not None:
             _nettoyer_scratch(numero, chemin_scratch)
+        # Fin de tâche en worktree (issue #337) : PAS de `git worktree remove`
+        # ni de suppression de branche automatique — Alain merge et pousse
+        # manuellement. On se contente de journaliser clairement l'état final
+        # (numéro, chemin, branche) pour qu'il sache quoi retrouver ; le
+        # statut succès/échec de CETTE tentative est visible sur la ligne de
+        # log immédiatement précédente (même numéro d'issue).
+        if chemin_worktree is not None:
+            log.info(
+                f"  Issue #{numero} : fin de traitement en worktree {chemin_worktree} "
+                f"(branche {_branche_worktree(numero)}) — worktree CONSERVÉ (aucune "
+                f"suppression automatique), fusion/push manuels par Alain."
+            )
+
+# ─── Point d'entrée public : dispatch séquentiel / parallèle (issue #337) ──────
+
+def _lancer_thread_ecriture(issue: dict, dry_run: bool, chemin_worktree: Path | None) -> None:
+    """Cible du thread Python dédié à une tâche mode_write parallélisée (issue
+    #337). Appelle simplement `_traiter_issue_synchrone` — toute la logique
+    (ACK, verrou par chemin_travail, retries, fermeture, notifications) reste
+    identique, seul le chemin de travail change. `_threads_ecriture` n'a PAS
+    besoin d'être purgé ici explicitement : `_nettoyer_threads_ecriture_termines`
+    (appelée à chaque décision de dispatch et en tête de boucle principale)
+    détecte `thread.is_alive() == False` dès que cette fonction retourne."""
+    _traiter_issue_synchrone(issue, dry_run, chemin_worktree=chemin_worktree)
+
+
+def traiter_issue(issue: dict, dry_run: bool) -> None:
+    """Point d'entrée public, appelé par la boucle principale pour CHAQUE
+    issue. Décide, pour une issue mode_write prête, entre traitement
+    séquentiel classique et parallélisation via git worktree (issue #337) ;
+    délègue tout le reste (lecture, lecture active, mode_write hors
+    parallélisation) tel quel à `_traiter_issue_synchrone`, comportement
+    inchangé depuis avant #337.
+
+    Décision de parallélisation (voir commentaire de section au-dessus de
+    `_threads_ecriture`) :
+      - `MAX_WRITE_PARALLELE <= 1`, dry-run, ou projet à périmètre dynamique
+        (#125, hors périmètre de #337) → jamais de thread/worktree, chemin
+        historique intégral.
+      - Aucun thread mode_write actif → PREMIER slot : thread dédié ciblant
+        REP_TRAVAIL (pas de worktree) — nécessaire pour que la boucle
+        principale reste libre de détecter une éventuelle deuxième tâche
+        mode_write pendant que celle-ci tourne encore.
+      - Au moins un thread actif et sous `MAX_WRITE_PARALLELE` → worktree dédié
+        + thread. Échec de création du worktree (déjà existant, erreur git) →
+        repli sur `_traiter_issue_synchrone` direct : le verrou par
+        chemin_travail (#189/#322, désormais posé sur REP_TRAVAIL ou le
+        worktree selon le cas, voir #337 point 7) fait alors office de garde-
+        fou — si REP_TRAVAIL est occupé par le premier slot, cette issue est
+        simplement différée au prochain cycle, sans double écriture possible.
+      - À `MAX_WRITE_PARALLELE` déjà atteint → même repli (différée par le
+        verrou si REP_TRAVAIL est occupé, traitée directement s'il est libre)."""
+    numero = issue["number"]
+    labels = [l.get("name", "") for l in issue.get("labels", [])]
+
+    if numero in issues_en_cours:
+        return
+
+    # Déjà en cours dans un thread depuis un cycle précédent (mode_write
+    # parallélisé) : ne pas re-dispatcher, laisser ce thread poursuivre.
+    if any(t["numero"] == numero for t in _threads_ecriture_actifs()):
+        return
+
+    # Issue déjà finalisée (échec définitif ou résultat déjà posté) : chemin
+    # rapide direct, pas de worktree à créer pour une issue qui ne va de toute
+    # façon rien exécuter (_traiter_issue_synchrone le détecte immédiatement).
+    if LABEL_ECHEC in labels or LABEL_FAIT in labels:
+        _traiter_issue_synchrone(issue, dry_run)
+        return
+
+    mode = _deduire_mode(labels)
+
+    if (mode == MODE_ECRITURE and not dry_run and not CFG.perimetre_dynamique
+            and CFG.max_write_parallele > 1):
+        actifs = _threads_ecriture_actifs()
+
+        if not actifs:
+            # Premier slot : thread sur REP_TRAVAIL (pas de worktree).
+            # PAS de issues_en_cours.add(numero) ICI : c'est
+            # _traiter_issue_synchrone, exécutée DANS le thread, qui s'en
+            # charge (comportement historique) — l'ajouter ici bloquerait le
+            # thread dès sa première ligne (garde d'idempotence en tête de
+            # _traiter_issue_synchrone). La déduplication inter-cycles est
+            # déjà assurée par `_threads_ecriture` (vérifié plus haut).
+            thread = threading.Thread(
+                target=_lancer_thread_ecriture, args=(issue, dry_run, None),
+                name=f"ecriture-issue-{numero}", daemon=True,
+            )
+            with _verrou_threads_ecriture:
+                _threads_ecriture.append({"numero": numero, "worktree": None, "thread": thread})
+            log.info(
+                f"  Issue #{numero} : lancement dans REP_TRAVAIL en tâche de fond "
+                f"(1/{CFG.max_write_parallele}) — parallélisation mode_write active (issue #337)."
+            )
+            thread.start()
+            return
+
+        if len(actifs) < CFG.max_write_parallele:
+            chemin_worktree = _creer_worktree(numero)
+            if chemin_worktree is not None:
+                # Même remarque que ci-dessus : pas de issues_en_cours.add ici.
+                thread = threading.Thread(
+                    target=_lancer_thread_ecriture, args=(issue, dry_run, chemin_worktree),
+                    name=f"ecriture-issue-{numero}", daemon=True,
+                )
+                with _verrou_threads_ecriture:
+                    _threads_ecriture.append({"numero": numero, "worktree": chemin_worktree, "thread": thread})
+                log.info(
+                    f"  Issue #{numero} : lancement dans le worktree {chemin_worktree} "
+                    f"({len(actifs) + 1}/{CFG.max_write_parallele}) — parallélisation mode_write (issue #337)."
+                )
+                thread.start()
+                return
+            # Échec de création du worktree : repli séquentiel ci-dessous.
+        else:
+            log.info(
+                f"  Issue #{numero} : MAX_WRITE_PARALLELE ({CFG.max_write_parallele}) déjà "
+                f"atteint — traitement séquentiel (différé si REP_TRAVAIL est occupé)."
+            )
+
+    _traiter_issue_synchrone(issue, dry_run)
 
 # ─── Boucle principale ─────────────────────────────────────────────────────────
 
# ── Zone modifiée : ligne 3104 (6 ligne(s)) dans l'ancienne version → ligne 3374 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3104,6 +3374,11 @@ def main():
     else:
         log.info("Auto-extinction désactivée (DELAI_INACTIVITE_MIN = 0) — watcher permanent.")
 
+    if CFG.max_write_parallele > 1:
+        log.info(f"Parallélisation mode_write via worktrees activée (issue #337) : MAX_WRITE_PARALLELE={CFG.max_write_parallele}.")
+    else:
+        log.info(f"Parallélisation mode_write désactivée (MAX_WRITE_PARALLELE={CFG.max_write_parallele}) — traitement séquentiel historique.")
+
     # Horloge monotone d'inactivité (issue #200). Initialisée AVANT la boucle
     # pour qu'un watcher fraîchement démarré ne s'éteigne pas au premier cycle,
     # puis réarmée à chaque cycle comportant au moins une issue traitable.
# ── Zone modifiée : ligne 3116 (16 ligne(s)) dans l'ancienne version → ligne 3391 (31 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3116,16 +3391,31 @@ def main():
         # interrompu : on ne teste qu'entre deux cycles complets. delai 0 =
         # mécanisme désactivé.
         if CFG.delai_inactivite_min > 0:
-            inactif_s = time.monotonic() - derniere_activite
-            if inactif_s > CFG.delai_inactivite_min * 60:
-                log.info(f"⏻ Auto-extinction : aucune issue traitable depuis "
-                         f"{CFG.delai_inactivite_min} min — arrêt propre du watcher.")
-                # Nettoyage du fichier PID, par cohérence avec arreter_watcher()
-                # (app/watchers.py) : sans ça l'interface afficherait un PID
-                # orphelin au lieu de « inactif ».
-                pid_file = DOSSIER_LOGS / f"watcher-{CFG.nom}.pid"
-                pid_file.unlink(missing_ok=True)
-                sys.exit(0)
+            # Garde-fou parallélisation mode_write (issue #337, point 8) :
+            # jamais d'extinction tant qu'un thread mode_write tourne encore,
+            # même si le délai d'inactivité est dépassé — un worktree en
+            # thread n'est pas nécessairement reflété par `issue_traitable`
+            # au même instant (labels re-synchronisés au poll suivant).
+            # `_threads_ecriture_actifs()` purge les threads terminés à
+            # chaque appel : réévalué à CHAQUE cycle, donc dès qu'un thread se
+            # termine, l'extinction redevient possible au cycle suivant.
+            threads_ecriture_actifs = _threads_ecriture_actifs()
+            if threads_ecriture_actifs:
+                log.debug(
+                    f"Auto-extinction différée : {len(threads_ecriture_actifs)} "
+                    f"tâche(s) mode_write encore active(s) en thread (issue #337)."
+                )
+            else:
+                inactif_s = time.monotonic() - derniere_activite
+                if inactif_s > CFG.delai_inactivite_min * 60:
+                    log.info(f"⏻ Auto-extinction : aucune issue traitable depuis "
+                             f"{CFG.delai_inactivite_min} min — arrêt propre du watcher.")
+                    # Nettoyage du fichier PID, par cohérence avec arreter_watcher()
+                    # (app/watchers.py) : sans ça l'interface afficherait un PID
+                    # orphelin au lieu de « inactif ».
+                    pid_file = DOSSIER_LOGS / f"watcher-{CFG.nom}.pid"
+                    pid_file.unlink(missing_ok=True)
+                    sys.exit(0)
 
         try:
             # Rafraîchissement automatique du clone local en début de cycle
