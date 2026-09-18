0722138

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0722138
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 15:17:05 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #350 : renomme bip.py en traitement_fin.py + SSE de fin d'issue
    
    scripts/bip.py -> scripts/traitement_fin.py (SCRIPT_BIP inchangé) ; le
    script POSTe désormais best-effort vers /notifier-fin-issue (--projet/
    --numero) après le bip. Nouveau module app/fin_issue.py (POST
    /notifier-fin-issue + GET /stream, une queue.Queue par onglet Résultats
    ouvert) et static/js/app.js (demarrerStreamFinIssue/arreterStreamFinIssue,
    réutilise verifierIssueApresDepassement de #334). Rafraîchissement de
    l'onglet Résultats en <1s sans polling supplémentaire, opt-in via les
    labels notif_* comme le bip.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9aa8b1d..82e00b5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1699 (11 ligne(s)) dans l'ancienne version → ligne 1699 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1699,11 +1699,15 @@ new_issue.py (ThinkPad) → polling gh → détecte la transition → bip/bulle/
   - **succès** : issue **fermée** portant le label `done` (`closedAt` récent) ;
   - **échec définitif** : label `needs-human` posé, issue restée **ouverte**
     (`updatedAt` récent).
-- **Script bip partagé `scripts/bip.py`** : le bip vivait dans `~/NicLink/bip.py`
+- **Script bip partagé `scripts/traitement_fin.py`** (anciennement
+  `scripts/bip.py`, renommé issue #350) : le bip vivait dans `~/NicLink/bip.py`
   (dépôt AlChess) alors que c'est de l'infrastructure commune à tous les projets.
-  Il a été déplacé/recréé dans `scripts/bip.py` ; le **défaut** de `SCRIPT_BIP`
-  pointe désormais vers lui, et les `configs/*.conf` qui référençaient l'ancien
-  chemin ont été mis à jour.
+  Il a été déplacé/recréé dans `scripts/`, renommé une première fois `bip.py`
+  puis `traitement_fin.py` (#350, une fois devenu aussi le déclencheur du SSE
+  de fin d'issue — voir §17.3) ; le **défaut** de `SCRIPT_BIP` pointe désormais
+  vers lui. **La clé de config reste `SCRIPT_BIP`** (renommer impliquerait de
+  modifier les `configs/*.conf` gitignorés, hors périmètre agent — voir §17.3
+  pour la marche à suivre manuelle).
 
 **Éviter le spam de vieilles issues au démarrage.** Deux garde-fous combinés :
 - **filtre de récence** : seules les transitions horodatées dans les
# ── Zone modifiée : ligne 1788 (6 ligne(s)) dans l'ancienne version → ligne 1792 (53 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1788,6 +1792,53 @@ NOTIFIER_LOCAL = false
 | `BRIDGE_NOTIF_RECENCE_MIN` | `30` | Fenêtre de récence des transitions (minutes). |
 | `BRIDGE_NOTIF_ESPACEMENT` | `2` | Délai (secondes) entre le traitement de deux projets (issue #190) : étale les appels gh du poller au lieu d'une rafale groupée qui rendait le bouton Rafraîchir lent et faisait « sursauter » les badges. `0` = rafale immédiate (ancien comportement). |
 
+### 17.3 SSE de fin d'issue — rafraîchissement instantané de l'onglet Résultats (issue #350)
+
+Avant #350, la ligne d'une issue dans l'onglet Résultats restait figée après sa
+clôture jusqu'au ↻ manuel ou jusqu'au fetch unique post-TIMEOUT de #334 (15 s
+après dépassement du décompte). #350 ajoute un canal de rafraîchissement quasi
+instantané (< 1 s), **sans polling supplémentaire**, en réutilisant
+`scripts/traitement_fin.py` (le script bip partagé, voir plus haut) comme
+déclencheur et un canal SSE dédié comme transport :
+
+- **`scripts/traitement_fin.py --projet <nom> --numero <n>`** : après le bip
+  habituel, POST **best-effort** (timeout 1 s, échec silencieux — new_issue.py
+  peut ne pas être lancé, notamment sur la VM CCW) vers
+  `http://localhost:5100/notifier-fin-issue` avec le corps
+  `{"projet": ..., "numero": ...}`. `notifications.bip()` transmet ces deux
+  arguments dès que `notifications.notifier()` les reçoit — ce qui remonte
+  jusqu'aux enveloppes `bip()`/`notifier()` de `watcher.py` (paramètre
+  `numero` ajouté) et jusqu'à `app/notifications_poller.py` (transitions
+  détectées côté CCW). Comme le bip lui-même, ce POST reste **opt-in via les
+  labels `notif_*`** (§4) : `notifications.notifier()` n'appelle `bip()` que si
+  l'issue en porte un — sans label, la ligne reste soumise au ↻ manuel / au
+  fetch post-TIMEOUT de #334, exactement comme avant #350.
+- **`POST /notifier-fin-issue`** (`app/fin_issue.py`, sans `login_requis` —
+  appelé par un script local, pas par un navigateur, comme `/heartbeat`) :
+  pousse un événement SSE `event: fin_issue\ndata: {"projet": ..., "numero": ...}`
+  à tous les onglets Résultats actuellement ouverts.
+- **`GET /stream`** (`app/fin_issue.py`, protégé par `login_requis` comme
+  `/events`) : générateur Flask SSE dédié, séparé de `/events` (cycle de vie)
+  et de `/journal/<projet>` (log watcher). Mécanisme de diffusion : une
+  **`queue.Queue` par connexion active**, ajoutée à la liste partagée
+  `app.config["FIN_ISSUE_ABONNES"]` à la connexion et retirée (`finally`,
+  couvre le `GeneratorExit` d'une déconnexion navigateur) à la fermeture — pas
+  de broadcast global, car new_issue.py est mono-utilisateur mais plusieurs
+  onglets peuvent être ouverts en même temps. Ping `: ping\n\n` toutes les 30 s
+  pour maintenir la connexion (proxys, navigateur).
+- **Côté navigateur** (`static/js/app.js`) : `demarrerStreamFinIssue()` ouvre
+  l'`EventSource('/stream')` à l'entrée dans l'onglet Résultats
+  (`basculerOnglet`), `arreterStreamFinIssue()` la ferme en le quittant. Sur
+  réception d'un événement `fin_issue` dont le numéro figure dans
+  `listeIssuesResultats`, appelle directement `verifierIssueApresDepassement()`
+  (§ issue #334 dans `app.js`) — même fetch de vérification, même
+  `remplacerLigneIssue()`, aucune logique dupliquée. La reconnexion après
+  coupure est native à `EventSource`, sans code supplémentaire.
+
+**Configuration héritée** : la clé `.conf` reste `SCRIPT_BIP` (voir §17.1
+ci-dessus et §10) — Alain doit mettre à jour manuellement le chemin dans ses
+`configs/*.conf` existants (`.../scripts/bip.py` → `.../scripts/traitement_fin.py`).
+
 ---
 
 ## 18. Pièces jointes image dans les issues (issues #191, #248)
# ── Zone modifiée : ligne 2115 (7 ligne(s)) dans l'ancienne version → ligne 2166 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2115,7 +2166,18 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 2 août 2026 — §11 « Conventions de code » : deux
+*Dernière mise à jour : 3 août 2026 — §17 « Notifications centralisées » :
+nouvelle sous-section 17.3 documentant le SSE de fin d'issue (issue #350) —
+`scripts/bip.py` renommé `scripts/traitement_fin.py` (clé de config
+`SCRIPT_BIP` inchangée, chemin à mettre à jour manuellement dans les
+`configs/*.conf` existants) et devenu, en plus du bip, le déclencheur
+best-effort d'un POST `/notifier-fin-issue` → SSE `GET /stream`
+(`app/fin_issue.py`, une `queue.Queue` par onglet Résultats ouvert) consommé
+côté navigateur par `demarrerStreamFinIssue()`, qui réutilise le fetch de
+vérification de #334 (`verifierIssueApresDepassement`) sans dupliquer sa
+logique. Rafraîchissement toujours opt-in via les labels `notif_*` (comme le
+bip lui-même) ; sans label, la ligne reste soumise au ↻ manuel ou au fetch
+post-TIMEOUT de #334. Précédemment — §11 « Conventions de code » : deux
 notes informant les projets utilisant Bridge_Agent des conséquences de la
 parallélisation `mode_write` par worktrees (issue #337) — risque de conflit
 de merge entre deux issues touchant les mêmes fichiers (recommandation :
# ── Zone modifiée : ligne 2137 (19 ligne(s)) dans l'ancienne version → ligne 2199 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2137,19 +2199,6 @@ vérification bornée de l'arbre de process, suppression conditionnelle des
 (`interrompre_linux()`) : arbre de process retrouvé par remontée
 `/proc/<pid>/status` (PPID, jamais par nom d'exécutable), `SIGKILL`,
 attente confirmée de la mort de l'arbre avant suppression du verrou — ainsi
-que l'équivalent manuel (`kill -9` + suppression du `.lock`). Précédemment
-— §3 « Créer une issue — la méthode normale » et §6 « Champs spéciaux dans
-le corps de l'issue » : documente le champ d'en-tête `MODE` (issue #330),
-auto-détecté par `new_issue.py` (`detecterModeDansCorps`) au même titre que
-`TIMEOUT`/`PROJET`/`MODELE` (issue #326) — pré-sélectionne le radio Mode du
-formulaire puis la ligne est retirée du corps, reconnaissance tolérante
-(casse/accents, plusieurs libellés par valeur), défaut LECTURE si le champ
-est absent ou non reconnu. Seules les deux valeurs fonctionnelles
-`lecture`/`écriture` sont documentées à ces deux endroits ; la troisième
-valeur (lecture active/`mode_scratch`) reste décrite uniquement au §5
-(issue #327), hors périmètre de #330. Précise aussi qu'en mono-issue `MODE`
-est auto-détecté depuis l'en-tête du bloc, alors qu'en mode lot il reste
-commun à tout le lot — choisi une fois au radio du formulaire, jamais lu
-bloc par bloc.*
+que l'équivalent manuel (`kill -9` + suppression du `.lock`).*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 7fc6fce..0087017 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,51 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 3 août 2026 — issue #350
+
+Renommage de `scripts/bip.py` en `scripts/traitement_fin.py` et ajout d'un
+canal SSE de rafraîchissement instantané (< 1 s) de l'onglet Résultats, sans
+polling supplémentaire.
+
+- `scripts/traitement_fin.py` : après le bip habituel, POST **best-effort**
+  (timeout 1 s, échec silencieux si `new_issue.py` n'est pas lancé) vers
+  `http://localhost:5100/notifier-fin-issue` avec `{"projet": ..., "numero": ...}`,
+  lus depuis deux nouveaux arguments CLI `--projet`/`--numero`. La clé de
+  config reste `SCRIPT_BIP` (renommer la clé impliquerait de modifier les
+  `configs/*.conf` gitignorés, hors périmètre agent) — **Alain doit mettre à
+  jour manuellement le chemin dans ses `configs/*.conf` existants**
+  (`.../scripts/bip.py` → `.../scripts/traitement_fin.py`).
+- `notifications.py` (`bip()`/`notifier()`) et les enveloppes correspondantes
+  de `watcher.py` et `app/notifications_poller.py` : ajout d'un paramètre
+  `numero` transmis en CLI au script, pour que le POST identifie précisément
+  l'issue concernée. Comme le bip lui-même, ce déclenchement reste opt-in via
+  les labels `notif_*` — sans label, la ligne reste soumise au ↻ manuel ou au
+  fetch post-TIMEOUT de #334.
+- `app/fin_issue.py` (nouveau module) : route `POST /notifier-fin-issue`
+  (sans authentification, appelée par le script local) qui pousse un
+  événement SSE `event: fin_issue\ndata: {"projet": ..., "numero": ...}` à
+  tous les onglets Résultats ouverts, et route `GET /stream` (protégée par
+  `login_requis`) qui les diffuse — une `queue.Queue` par connexion active
+  (ajoutée/retirée de `app.config["FIN_ISSUE_ABONNES"]`), pas de broadcast
+  global, car plusieurs onglets peuvent être ouverts simultanément. Ping
+  `: ping\n\n` toutes les 30 s pour maintenir la connexion ; nettoyage propre
+  de l'abonné à la déconnexion (`GeneratorExit`).
+- `static/js/app.js` : `demarrerStreamFinIssue()`/`arreterStreamFinIssue()`
+  ouvrent/ferment un `EventSource('/stream')` à l'entrée/sortie de l'onglet
+  Résultats (`basculerOnglet`). Sur réception d'un événement `fin_issue` dont
+  le numéro figure dans `listeIssuesResultats`, réutilise directement
+  `verifierIssueApresDepassement()` (issue #334) — même fetch de vérification,
+  même `remplacerLigneIssue()`, sans dupliquer la logique. Reconnexion
+  automatique gérée nativement par `EventSource`.
+- `BRIDGE_AGENT_DOC.md` : §17 mis à jour (mentions de `bip.py` →
+  `traitement_fin.py`), nouvelle sous-section 17.3 documentant le mécanisme
+  SSE complet.
+- Testé sans `new_issue.py` lancé (bip normal, POST en échec silencieux,
+  aucune exception) et avec un client de test Flask (`app.test_client()`) :
+  `POST /notifier-fin-issue` livre bien l'événement à une connexion
+  `GET /stream` active, et la liste des abonnés est correctement nettoyée à
+  la déconnexion.
+
 ## 2 août 2026 — issue #343
 
 `WORKTREES.md` §3 « Workflow normal d'Alain » (étape 3) et §4
# (diff du fichier suivant)
diff --git a/app/__init__.py b/app/__init__.py
# (index — ignorable)
index a6cb9df..88fc6e5 100644
# (avant — fichier suivant)
--- a/app/__init__.py
# (après — fichier suivant)
+++ b/app/__init__.py
# ── Zone modifiée : ligne 46 (6 ligne(s)) dans l'ancienne version → ligne 46 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -46,6 +46,7 @@ def create_app() -> Flask:
     app.config["LAST_SSE_ACTIVITE"]      = 0.0   # horodatage de la dernière activité SSE (issue #157)
     app.config["SSE_DEJA_VU"]            = False # au moins une connexion SSE a-t-elle eu lieu (issue #157)
     app.config["PROC_TUNNEL"]    = None    # processus cloudflared (mode --externe)
+    app.config["FIN_ISSUE_ABONNES"] = []   # files SSE actives /stream, une par onglet Résultats (issue #350)
 
     _enregistrer_routes(app)
     return app
# ── Zone modifiée : ligne 75 (6 ligne(s)) dans l'ancienne version → ligne 76 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -75,6 +76,7 @@ def _enregistrer_routes(app: Flask) -> None:
                          ccw_arreter_projet)
     from app.interruption import route_interrompre
     from app.cycle_vie import heartbeat, events, quitter
+    from app.fin_issue import notifier_fin_issue, stream_fin_issue
     from app.diag_heartbeat import visibilite as diag_visibilite   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
     from app.vues import index
 
# ── Zone modifiée : ligne 119 (4 ligne(s)) dans l'ancienne version → ligne 121 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -119,4 +121,10 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/heartbeat", "heartbeat", heartbeat, methods=["POST"])
     app.add_url_rule("/events", "events", login_requis(events))
     app.add_url_rule("/quitter", "quitter", login_requis(quitter), methods=["POST"])
+    # ─── SSE de fin d'issue (issue #350) : rafraîchissement instantané de l'onglet
+    # Résultats, déclenché par scripts/traitement_fin.py. /notifier-fin-issue est
+    # appelé par ce script local (pas par un navigateur) : pas de login_requis,
+    # comme /heartbeat.
+    app.add_url_rule("/notifier-fin-issue", "notifier_fin_issue", notifier_fin_issue, methods=["POST"])
+    app.add_url_rule("/stream", "stream_fin_issue", login_requis(stream_fin_issue))
     app.add_url_rule("/diag-visibilite", "diag_visibilite", diag_visibilite, methods=["POST"])   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
# (diff du fichier suivant)
diff --git a/app/fin_issue.py b/app/fin_issue.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..f5ec289
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/app/fin_issue.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (82 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,82 @@
+"""
+app/fin_issue.py — SSE de fin d'issue pour l'onglet Résultats (issue #350).
+
+Objectif : rafraîchir la ligne d'une issue dans l'onglet Résultats en moins
+d'une seconde après sa clôture, sans polling. Le déclencheur est le script
+partagé `scripts/traitement_fin.py` (anciennement bip.py, invoqué par
+watcher.py/notifications.py à chaque transition terminale d'issue) : il POSTe
+ici, en best-effort, juste après avoir émis le bip.
+
+Mécanisme de diffusion : new_issue.py est mono-utilisateur mais plusieurs
+onglets du navigateur peuvent être ouverts en même temps sur la même machine —
+une simple variable globale ne suffirait donc pas à notifier chacun. Chaque
+connexion GET /stream pose sa propre `queue.Queue`, ajoutée à la liste partagée
+`FIN_ISSUE_ABONNES` (app.config) à la connexion et retirée à la déconnexion ;
+POST /notifier-fin-issue pousse l'événement dans TOUTES les files actives (pas
+de broadcast au sens réseau, juste une boucle Python).
+"""
+
+import json
+import queue
+from threading import Lock
+
+from flask import Response, current_app, jsonify, request
+
+from app.auth import login_requis  # noqa: F401 (exporté pour l'enregistrement des routes)
+
+DELAI_PING = 30   # s — garde la connexion /stream ouverte (proxys, navigateur)
+
+_verrou_abonnes = Lock()
+
+
+def notifier_fin_issue():
+    """POST /notifier-fin-issue — appelé par scripts/traitement_fin.py. Corps
+    JSON {"projet": ..., "numero": ...}. Pousse un événement SSE `fin_issue` à
+    tous les onglets Résultats actuellement ouverts. Pas d'authentification
+    (appelé par un script local, pas par un navigateur) — cohérent avec
+    /heartbeat, déjà sans login_requis."""
+    corps = request.get_json(silent=True) or {}
+    projet = corps.get("projet")
+    numero = corps.get("numero")
+    if not projet or numero is None:
+        return jsonify(ok=False, erreur="projet et numero requis"), 400
+
+    evenement = "event: fin_issue\ndata: " + json.dumps({"projet": projet, "numero": numero}) + "\n\n"
+    abonnes = current_app.config.setdefault("FIN_ISSUE_ABONNES", [])
+    with _verrou_abonnes:
+        cibles = list(abonnes)
+    for file_attente in cibles:
+        file_attente.put(evenement)
+    return jsonify(ok=True)
+
+
+def stream_fin_issue():
+    """GET /stream — SSE dédié à l'onglet Résultats (issue #350) : un événement
+    `fin_issue` par transition détectée côté script. Une file dédiée par
+    connexion (plusieurs onglets possibles), ping toutes les DELAI_PING s pour
+    maintenir la connexion. Le try/finally couvre la déconnexion du navigateur
+    (GeneratorExit levée dans le générateur quand Flask cesse de le consommer),
+    pour toujours retirer la file de la liste des abonnés."""
+    config = current_app.config   # capturé dans le contexte de requête
+    file_attente = queue.Queue()
+    abonnes = config.setdefault("FIN_ISSUE_ABONNES", [])
+    with _verrou_abonnes:
+        abonnes.append(file_attente)
+
+    def generer():
+        try:
+            while True:
+                try:
+                    yield file_attente.get(timeout=DELAI_PING)
+                except queue.Empty:
+                    yield ": ping\n\n"
+        finally:
+            with _verrou_abonnes:
+                if file_attente in abonnes:
+                    abonnes.remove(file_attente)
+
+    return Response(
+        generer(),
+        mimetype="text/event-stream",
+        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
+    )
# (diff du fichier suivant)
diff --git a/app/notifications_poller.py b/app/notifications_poller.py
# (index — ignorable)
index 11028a2..5b349a4 100644
# (avant — fichier suivant)
--- a/app/notifications_poller.py
# (après — fichier suivant)
+++ b/app/notifications_poller.py
# ── Zone modifiée : ligne 220 (6 ligne(s)) dans l'ancienne version → ligne 220 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -220,6 +220,7 @@ def _notifier_transition(cfg, tr: dict):
             titre=f"✅ {cfg.nom} #{numero} — traitée",
             message=f"'{titre}' traitée avec succès.",
             urgence_bureau="normal", priorite_ntfy="default",
+            numero=numero,
         )
     else:  # needs-human
         notifications.notifier(
# ── Zone modifiée : ligne 227 (6 ligne(s)) dans l'ancienne version → ligne 228 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -227,6 +228,7 @@ def _notifier_transition(cfg, tr: dict):
             titre=f"❌ {cfg.nom} #{numero} — échec définitif",
             message=f"'{titre}' — intervention humaine requise.",
             urgence_bureau="critical", priorite_ntfy="high",
+            numero=numero,
         )
 
 
# (diff du fichier suivant)
diff --git a/notifications.py b/notifications.py
# (index — ignorable)
index 0eedc68..b5585d0 100644
# (avant — fichier suivant)
--- a/notifications.py
# (après — fichier suivant)
+++ b/notifications.py
# ── Zone modifiée : ligne 45 (15 ligne(s)) dans l'ancienne version → ligne 45 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -45,15 +45,23 @@ def a_un_label_notif(labels: list[str]) -> bool:
             or LABEL_NOTIF_TOUS in labels)
 
 
-def bip(script_bip: Path, fois: int = 1):
-    """Bip sonore via le script bip.py. `script_bip` : chemin du script (le
-    partagé Bridge_Agent/scripts/bip.py par défaut). Silencieux si absent."""
+def bip(script_bip: Path, fois: int = 1, projet: str | None = None, numero=None):
+    """Bip sonore via le script partagé (Bridge_Agent/scripts/traitement_fin.py,
+    anciennement bip.py). `script_bip` : chemin du script. Silencieux si absent.
+    `projet`/`numero`, si tous deux fournis, sont transmis en CLI au script pour
+    qu'il notifie new_issue.py en plus du bip (SSE de rafraîchissement de
+    l'onglet Résultats, issue #350) — best-effort côté script, sans incidence
+    ici en cas d'échec."""
     script_bip = Path(script_bip)
     if not script_bip.exists():
         return
+    argv_supplementaires = []
+    if projet and numero is not None:
+        argv_supplementaires = ["--projet", str(projet), "--numero", str(numero)]
     for _ in range(fois):
         try:
-            subprocess.run(["python3", str(script_bip)], capture_output=True, timeout=10)
+            subprocess.run(["python3", str(script_bip), *argv_supplementaires],
+                           capture_output=True, timeout=10)
         except Exception:
             pass
         time.sleep(0.3)
# ── Zone modifiée : ligne 98 (14 ligne(s)) dans l'ancienne version → ligne 106 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -98,14 +106,15 @@ def notifier_ntfy(url_ntfy: str, titre: str, message: str,
 def notifier(labels: list[str], nom_projet: str, url_ntfy: str, script_bip: Path,
              titre: str, message: str,
              urgence_bureau: str = "normal", priorite_ntfy: str = "default",
-             fois_bip: int = 1, log: logging.Logger = _log_defaut):
+             fois_bip: int = 1, numero=None, log: logging.Logger = _log_defaut):
     """Dispatch de notification selon les labels de l'issue.
     Le bip et les canaux additionnels (notify-send, ntfy) sont opt-in via les
     labels notif_pc / notif_gsm / notif_tous : sans aucun de ces labels, aucun
     signal n'est émis. fois_bip renforce le signal (ex. 3 pour une alerte
-    critique)."""
+    critique). `numero`, si fourni, permet au bip de notifier new_issue.py de
+    la fin de CETTE issue précise (SSE, issue #350)."""
     if a_un_label_notif(labels):
-        bip(script_bip, fois_bip)
+        bip(script_bip, fois_bip, projet=nom_projet, numero=numero)
     if LABEL_NOTIF_PC in labels or LABEL_NOTIF_TOUS in labels:
         notifier_bureau(nom_projet, titre, message, urgence_bureau, log=log)
     if LABEL_NOTIF_GSM in labels or LABEL_NOTIF_TOUS in labels:
# (diff du fichier suivant)
diff --git a/scripts/bip.py b/scripts/bip.py
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index b582517..0000000
# (avant — fichier suivant)
--- a/scripts/bip.py
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (19 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,19 +0,0 @@
-import math, wave, struct, tempfile, os
-
-f = 440       # fréquence Hz
-dur = 0.4     # durée secondes
-sr = 44100    # sample rate
-
-samples = [int(32767 * math.sin(2 * math.pi * f * t / sr)) for t in range(int(sr * dur))]
-data = struct.pack('<' + 'h' * len(samples), *samples)
-
-tmp = tempfile.mktemp(suffix='.wav')
-w = wave.open(tmp, 'w')
-w.setnchannels(1)
-w.setsampwidth(2)
-w.setframerate(sr)
-w.writeframes(data)
-w.close()
-
-os.system(f'aplay {tmp} 2>/dev/null')
-os.remove(tmp)
# (diff du fichier suivant)
diff --git a/scripts/traitement_fin.py b/scripts/traitement_fin.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..53cfeea
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/scripts/traitement_fin.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (84 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,84 @@
+#!/usr/bin/env python3
+"""
+traitement_fin.py — déclencheur de fin de traitement d'une issue, infrastructure
+PARTAGÉE du bridge (issues #187, #350). Anciennement `scripts/bip.py` — la clé
+de config qui le référence reste `SCRIPT_BIP` pour l'instant (voir CHANGELOG).
+
+Émet le bip sonore historique, puis — si `--projet` et `--numero` sont fournis
+— notifie best-effort `new_issue.py` (POST /notifier-fin-issue, issue #350)
+pour que l'onglet Résultats se rafraîchisse quasi instantanément (SSE) au lieu
+d'attendre un ↻ manuel ou le fetch post-TIMEOUT de #334. Le POST est silencieux
+en cas d'échec (new_issue.py non lancé, port fermé, etc.) : le bip reste
+fonctionnel indépendamment de ce canal.
+
+Usage :
+    python3 traitement_fin.py                                   # un bip seul
+    python3 traitement_fin.py --projet bridge_agent --numero 350 # bip + POST
+"""
+
+import argparse
+import json
+import math
+import os
+import struct
+import tempfile
+import urllib.request
+import wave
+
+F   = 440       # fréquence Hz
+DUR = 0.4       # durée secondes
+SR  = 44100     # sample rate
+
+URL_NOTIFIER_FIN_ISSUE     = "http://localhost:5100/notifier-fin-issue"
+TIMEOUT_NOTIFIER_FIN_ISSUE = 1   # s — new_issue.py non lancé ne doit jamais retarder le bip
+
+
+def bip():
+    """Bip sonore court (440 Hz, 0.4 s) via aplay."""
+    samples = [int(32767 * math.sin(2 * math.pi * F * t / SR)) for t in range(int(SR * DUR))]
+    data = struct.pack('<' + 'h' * len(samples), *samples)
+
+    tmp = tempfile.mktemp(suffix='.wav')
+    w = wave.open(tmp, 'w')
+    w.setnchannels(1)
+    w.setsampwidth(2)
+    w.setframerate(SR)
+    w.writeframes(data)
+    w.close()
+
+    os.system(f'aplay {tmp} 2>/dev/null')
+    os.remove(tmp)
+
+
+def notifier_fin_issue(projet: str, numero: str):
+    """POST best-effort vers new_issue.py (issue #350) : pousse un événement SSE
+    `fin_issue` à l'onglet Résultats déjà ouvert. Timeout court et échec
+    silencieux — new_issue.py n'est pas toujours lancé, et ce canal ne doit
+    jamais faire planter l'appelant (le bip a déjà été émis avant cet appel)."""
+    try:
+        corps = json.dumps({"projet": projet, "numero": int(numero)}).encode("utf-8")
+        requete = urllib.request.Request(
+            URL_NOTIFIER_FIN_ISSUE, data=corps,
+            headers={"Content-Type": "application/json"}, method="POST",
+        )
+        urllib.request.urlopen(requete, timeout=TIMEOUT_NOTIFIER_FIN_ISSUE).close()
+    except Exception:
+        pass
+
+
+def main():
+    parser = argparse.ArgumentParser()
+    parser.add_argument("--projet", default=None,
+                        help="Nom du projet (déclenche le POST /notifier-fin-issue avec --numero)")
+    parser.add_argument("--numero", default=None,
+                        help="Numéro de l'issue (déclenche le POST /notifier-fin-issue avec --projet)")
+    args = parser.parse_args()
+
+    bip()
+
+    if args.projet and args.numero:
+        notifier_fin_issue(args.projet, args.numero)
+
+
+if __name__ == "__main__":
+    main()
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index ce8de7d..80adb3c 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2 (6 ligne(s)) dans l'ancienne version → ligne 2 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2,6 +2,10 @@ let sourceSSE = null;
 
 let intervalWatchers = null;
 
+// Connexion SSE dédiée au rafraîchissement instantané des résultats (issue
+// #350) — ouverte à l'entrée dans l'onglet Résultats, fermée en le quittant.
+let sourceFinIssue = null;
+
 // SOURCE UNIQUE DE VÉRITÉ pour la couleur de chaque projet (issue #120).
 // Utilisée à la fois pour l'accent du formulaire (couleurProjet) et pour les
 // pastilles/badges/boutons de l'onglet Résultats (couleurProjetResultats).
# ── Zone modifiée : ligne 59 (8 ligne(s)) dans l'ancienne version → ligne 63 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -59,8 +63,8 @@ function basculerOnglet(nom) {
   noms.forEach(n =>
     document.getElementById('panneau-' + n).classList.toggle('actif', n === nom));
   if (nom === 'journal')  demarrerJournal();
-  if (nom === 'resultats') { chargerListeIssues(); demarrerTempsRestant(); }
-  else arreterTempsRestant();
+  if (nom === 'resultats') { chargerListeIssues(); demarrerTempsRestant(); demarrerStreamFinIssue(); }
+  else { arreterTempsRestant(); arreterStreamFinIssue(); }
   if (nom === 'watchers') {
     chargerWatchers();
     intervalWatchers = setInterval(chargerWatchers, 5000);
# ── Zone modifiée : ligne 1674 (6 ligne(s)) dans l'ancienne version → ligne 1678 (32 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1674,6 +1678,32 @@ function arreterTempsRestant() {
   if (intervalTempsRestant) { clearInterval(intervalTempsRestant); intervalTempsRestant = null; }
 }
 
+// Ouvre le canal SSE de fin d'issue (issue #350), à l'ouverture de l'onglet
+// Résultats. Sur réception d'un événement fin_issue pour une issue affichée
+// dans listeIssuesResultats, réutilise EXACTEMENT le traitement du fetch de
+// vérification de #334 (verifierIssueApresDepassement) — même fetch, même
+// remplacement de ligne — plutôt que de dupliquer cette logique. La
+// reconnexion en cas de coupure est gérée nativement par EventSource, aucun
+// code supplémentaire n'est nécessaire ici.
+function demarrerStreamFinIssue() {
+  if (sourceFinIssue) return;   // déjà ouverte
+  sourceFinIssue = new EventSource('/stream');
+  sourceFinIssue.addEventListener('fin_issue', function(e) {
+    let donnees;
+    try { donnees = JSON.parse(e.data); } catch (err) { return; }
+    const { projet, numero } = donnees;
+    const dansLaListe = listeIssuesResultats.some(
+      it => it.projet === projet && String(it.number) === String(numero));
+    if (dansLaListe) verifierIssueApresDepassement(projet, numero);
+  });
+}
+
+// Ferme le canal SSE de fin d'issue (en quittant l'onglet Résultats) : pas de
+// connexion inutile maintenue quand l'onglet n'est pas affiché.
+function arreterStreamFinIssue() {
+  if (sourceFinIssue) { sourceFinIssue.close(); sourceFinIssue = null; }
+}
+
 // Sélectionne la première ligne encore visible SANS charger son détail (voir
 // selectionnerLigne, issue #261) ; vide le détail s'il n'y a plus rien à
 // afficher. Appelée à l'ouverture de l'onglet, à chaque changement de filtre
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index a0d8e35..5a628d5 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 226 (7 ligne(s)) dans l'ancienne version → ligne 226 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -226,7 +226,7 @@ class Config:
     timeout_claude: int   = 300
     timeout_chef: int     = 1200   # défaut plus généreux pour les issues « Chef : » sans TIMEOUT explicite (issue #106)
     timeout_diagnostic: int = 90   # timeout court et fixe de la passe diagnostique avant abandon non-critique (issue #124)
-    script_bip: Path      = field(default_factory=lambda: DOSSIER_SCRIPT / "scripts" / "bip.py")
+    script_bip: Path      = field(default_factory=lambda: DOSSIER_SCRIPT / "scripts" / "traitement_fin.py")
     log_taille_max_mo: int = 1     # rotation quand le journal dépasse cette taille (Mo)
     log_archives: int      = 5     # nombre d'archives datées conservées
     cmd_backup: str        = ""    # commande de sauvegarde avant modif (mode écriture)
# ── Zone modifiée : ligne 319 (7 ligne(s)) dans l'ancienne version → ligne 319 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -319,7 +319,7 @@ def charger_config(chemin: Path) -> Config:
         timeout_chef   = entier("TIMEOUT_CHEF", 1200),
         timeout_diagnostic = entier("TIMEOUT_DIAGNOSTIC", 90),
         script_bip  = Path(brut["SCRIPT_BIP"]).expanduser() if brut.get("SCRIPT_BIP")
-                      else DOSSIER_SCRIPT / "scripts" / "bip.py",
+                      else DOSSIER_SCRIPT / "scripts" / "traitement_fin.py",
         log_taille_max_mo = entier("LOG_TAILLE_MAX_MO", 1),
         log_archives      = entier("LOG_ARCHIVES", 5),
         cmd_backup        = brut.get("CMD_BACKUP", ""),
# ── Zone modifiée : ligne 435 (9 ligne(s)) dans l'ancienne version → ligne 435 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -435,9 +435,10 @@ def configurer_logs(cfg: Config):
 # du CFG courant (nom, url_ntfy, script_bip) et le logger du watcher. Les sites
 # d'appel existants (succès/échec/alerte critique) restent inchangés.
 
-def bip(fois=1):
-    """Bip sonore via le script bip partagé (Bridge_Agent/scripts/bip.py)."""
-    notifications.bip(CFG.script_bip, fois)
+def bip(fois=1, numero=None):
+    """Bip sonore via le script partagé (Bridge_Agent/scripts/traitement_fin.py,
+    anciennement bip.py)."""
+    notifications.bip(CFG.script_bip, fois, projet=CFG.nom, numero=numero)
 
 def notifier_bureau(titre: str, message: str, urgence: str = "normal"):
     """Bulle de notification bureau via notify-send (voir notifications.py)."""
# ── Zone modifiée : ligne 449 (7 ligne(s)) dans l'ancienne version → ligne 450 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -449,7 +450,7 @@ def notifier_ntfy(titre: str, message: str, priorite: str = "default"):
 
 def notifier(labels: list[str], titre: str, message: str,
              urgence_bureau: str = "normal", priorite_ntfy: str = "default",
-             fois_bip: int = 1):
+             fois_bip: int = 1, numero=None):
     """Dispatch de notification selon les labels de l'issue.
 
     Garde issue #187 : si `NOTIFIER_LOCAL = false` dans le .conf, ce watcher
# ── Zone modifiée : ligne 457 (14 ligne(s)) dans l'ancienne version → ligne 458 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -457,14 +458,17 @@ def notifier(labels: list[str], titre: str, message: str,
     qui détecte la transition par polling GitHub et notifie de façon centralisée
     sur le ThinkPad d'Alain (évite les doublons, et fait remonter les transitions
     CCW dont le bip/notify-send tomberaient sinon dans la VM). Par défaut True :
-    comportement historique préservé (notamment CCL, déjà fonctionnel)."""
+    comportement historique préservé (notamment CCL, déjà fonctionnel).
+
+    `numero`, si fourni, permet au bip de notifier new_issue.py de la fin de
+    CETTE issue précise pour un rafraîchissement SSE instantané (issue #350)."""
     if not CFG.notifier_local:
         return
     notifications.notifier(
         labels, CFG.nom, CFG.url_ntfy, CFG.script_bip,
         titre, message,
         urgence_bureau=urgence_bureau, priorite_ntfy=priorite_ntfy,
-        fois_bip=fois_bip, log=log,
+        fois_bip=fois_bip, numero=numero, log=log,
     )
 
 def alerte_critique(numero, titre, tentative, labels: list[str]):
# ── Zone modifiée : ligne 478 (6 ligne(s)) dans l'ancienne version → ligne 482 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -478,6 +482,7 @@ def alerte_critique(numero, titre, tentative, labels: list[str]):
         urgence_bureau="critical",
         priorite_ntfy="high",
         fois_bip=3,  # 3 bips pour l'alerte critique (au lieu du bip simple par défaut)
+        numero=numero,
     )
 
 def gh(*args) -> dict | list | None:
# ── Zone modifiée : ligne 3024 (6 ligne(s)) dans l'ancienne version → ligne 3029 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3024,6 +3029,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                         message=f"'{titre}' : écriture détectée hors scratch en lecture active, projet restauré.",
                         urgence_bureau="critical",
                         priorite_ntfy="high",
+                        numero=numero,
                     )
                     issues_en_cours.discard(numero)
                     return
# ── Zone modifiée : ligne 3051 (6 ligne(s)) dans l'ancienne version → ligne 3057 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3051,6 +3057,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                                  f"(réseau). Issue laissée ouverte pour reprise au prochain cycle."),
                         urgence_bureau="critical",
                         priorite_ntfy="high",
+                        numero=numero,
                     )
                     issues_en_cours.discard(numero)
                     return
# ── Zone modifiée : ligne 3102 (6 ligne(s)) dans l'ancienne version → ligne 3109 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3102,6 +3109,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                     message=f"'{titre}' traitée avec succès.",
                     urgence_bureau="normal",
                     priorite_ntfy="default",
+                    numero=numero,
                 )
                 return
 
# ── Zone modifiée : ligne 3195 (6 ligne(s)) dans l'ancienne version → ligne 3203 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3195,6 +3203,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                         message=f"'{titre}' abandonnée après {CFG.max_essais} tentatives.\nDernière erreur : {sortie[:200]}",
                         urgence_bureau="critical",
                         priorite_ntfy="high",
+                        numero=numero,
                     )
                     issues_en_cours.discard(numero)
                     return
