427f89f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 427f89f
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 17:48:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #559 (3/3) : case « Projet CCW » sur le formulaire — chiffrement des tokens et génération automatique des 2 issues croisées
    
    - app/projet_ccw.py (nouveau) : module dédié (comme app/ccw.py) — cache
      local de la clé publique de bootstrap (configs/ccw_bootstrap_publique.pem,
      gitignoré, rafraîchi manuellement via SSH plutôt qu'à chaque soumission),
      chiffrement RSA/OAEP-SHA256 des 2 tokens (miroir exact de
      dechiffrer_token_bootstrap, watcher.py #556), génération des issues CCL
      (réinstallation) + CCW (bootstrap CREATION, format §16.6) avec référence
      croisée, réutilisant _issue_ouverte_meme_titre (anti-double-soumission).
    - templates/index.html / static/js/app.js : case « Projet CCW », bloc
      d'instructions + 2 champs token, validation stricte client+serveur,
      appel post-création, confirmation avec liens vers les 2 issues.
    - BRIDGE_AGENT_DOC.md §16.7 (nouveau) + REINSTALLATION_CCW.md §8 : mécanisme
      de cache documenté.
    - tests/test_projet_ccw_559.py : chemin complet sans vraie machine CCW ni
      vraie issue GitHub (faux gh), y compris la vérification que le corps de
      l'issue CCW est bien parsable par watcher.py (#556).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d361111..02e634b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 14 (3 ligne(s)) dans l'ancienne version → ligne 14 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -14,3 +14,8 @@ configs/templates_*.json
 # Dossier inbox du watcher_issues_inbox (issue #483) : fichiers .txt déposés
 # par Claude Chat / traités par le watcher — état transitoire, pas du code.
 issues_inbox/
+# Cache local de la clé publique de bootstrap CCW (case « Projet CCW »,
+# issue #559) — pas secrète, mais spécifique à l'instance CCW courante et
+# sans intérêt dans l'historique git (régénérée à chaque réinstallation de
+# CCW, cf. REINSTALLATION_CCW.md §8). Rafraîchie manuellement, jamais committée.
+configs/ccw_bootstrap_publique.pem
# (diff du fichier suivant)
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# (index — ignorable)
index f94ca48..ce7f49e 100644
# (avant — fichier suivant)
--- a/BRIDGE_AGENT_DOC.md
# (après — fichier suivant)
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 2501 (11 ligne(s)) dans l'ancienne version → ligne 2501 (107 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2501,11 +2501,107 @@ faux `powershell` sur le `PATH`), et un scénario bout en bout via
 `traiter_issue` vérifiant qu'un faux `claude` marqueur n'est **jamais**
 touché.
 
-**Reste à faire (issue 3/3, #559 ou suivant, hors périmètre de #556) :** le
-formulaire web qui génère automatiquement ces 6 champs (récupération de
-`bootstrap_publique.pem`, chiffrement des deux tokens, remplissage du
-corps) — cette issue a été testée avec une issue `for-windows` créée à la
-main, sans attendre le formulaire.
+**Formulaire web générant ces 6 champs automatiquement : voir §16.7
+(issue #559, 3/3 — chantier complet).**
+
+### 16.7 Case « Projet CCW » du formulaire de création de projet (issue #559, 3/3)
+
+**But.** Dernière brique du chantier « Projet CCW » (#553 conception → #554
+clés → #555/#556/#557 traitement `CREATION` validé en conditions réelles) :
+une case à cocher dans le modal « Nouveau projet » (`templates/index.html`)
+qui automatise ce que §16.6 documentait comme fait « à la main » —
+récupérer la clé publique, chiffrer les 2 tokens, construire le corps de
+l'issue `CREATION`, créer les 2 issues croisées. Module dédié
+`app/projet_ccw.py` (même séparation que `app/ccw.py`), **jamais** de
+modification de `app/nouveau_projet.py` : appelé par le front-end
+JUSTE APRÈS le succès de la création classique du projet CCL
+(`POST /nouveau-projet`, `np_cli.creer_projet`), jamais avant.
+
+**Décision — cache local de la clé publique de bootstrap (point le plus
+ouvert de la conception #553).** La clé publique
+(`C:\CCW\cles_bootstrap\bootstrap_publique.pem`, #554) n'est **pas**
+récupérée par un aller-retour SSH à chaque création de projet — cela
+réintroduirait exactement la dépendance à « CCW allumé » que ce chantier
+vise à éviter (la case doit fonctionner même PC éteint). Elle est mise en
+cache localement dans `configs/ccw_bootstrap_publique.pem` (gitignoré :
+état local de la machine CCL, spécifique à l'instance CCW courante, sans
+intérêt dans l'historique git — régénérée à chaque réinstallation de CCW,
+cf. `REINSTALLATION_CCW.md` §8). **Rafraîchissement MANUEL** : bouton « 🔄
+Rafraîchir la clé publique » dans le bloc d'instructions du formulaire
+(`GET /projet-ccw/cle-publique/etat` pour l'état affiché avant soumission,
+`POST /projet-ccw/rafraichir-cle` pour le rafraîchir), réutilisant le
+mécanisme SSH déjà en place et testé (`app/ccw.py::_charger_config_ssh` /
+`OPTIONS_SSH`, scp `C:/CCW/cles_bootstrap/bootstrap_publique.pem` →
+cache local) — **seul** point de `app/projet_ccw.py` qui exige CCW allumé.
+À relancer après une (première génération ou) rotation de la paire de
+clés côté CCW. Si le cache est absent au moment de la soumission :
+`/projet-ccw/bootstrap` refuse proprement (message explicite), aucune
+issue n'est créée.
+
+**Formulaire (`templates/index.html`, `static/js/app.js`).** Case
+« Projet CCW » à côté des options existantes du modal. Cochée → affichage
+immédiat (JS pur, aucun aller-retour serveur) d'un bloc d'instructions
+(repo dédié, permissions `Issues: Read and write` / `Metadata: Read-only`,
+`claude setup-token`) et de 2 champs `type="password"` (GH_TOKEN,
+CLAUDE_CODE_OAUTH_TOKEN). Validation stricte **côté client ET serveur** :
+case cochée → topic ntfy + 2 tokens obligatoires avant l'appel à
+`/projet-ccw/bootstrap` (le topic est **exigé explicitement** côté client,
+plutôt que de résoudre le défaut serveur silencieusement — évite toute
+divergence entre le topic CCL réellement écrit dans le `.conf` du nouveau
+projet et celui transmis à l'issue CCW).
+
+**Séquence côté serveur (`app/projet_ccw.py::bootstrap_projet_ccw`,
+`POST /projet-ccw/bootstrap`, appelée par le JS après le succès de
+`/nouveau-projet`) :**
+1. Validation (nom/dépôt/topic transmis, 2 tokens non vides, cache de clé
+   publique présent) — sinon échec propre, aucune issue créée.
+2. Chiffrement des 2 tokens (`_chiffrer_token`, RSA/OAEP-SHA256, base64 sur
+   une seule ligne) — miroir exact, côté chiffrement, de
+   `dechiffrer_token_bootstrap` (`watcher.py`, §16.6) : même padding, même
+   encodage, vérifié par aller-retour réel en test (voir plus bas).
+3. Issue **CCL** créée en premier sur `AlainDelree/Bridge_Agent`
+   (`bridge,for-linux,mode_write`) : met à jour
+   `reinstaller_projets_ccw.ps1` (tableau `$Projets`) et le tableau de
+   `REINSTALLATION_CCW.md` §7.
+4. Issue **CCW** créée ensuite, même dépôt (`bridge,for-windows,mode_write`,
+   canal unifié) : corps au format EXACT du §16.6 (les 6 champs
+   `CREATION*`), référence l'issue CCL. Traitée par `watcher.py` (#556)
+   sans aucune session `claude` (décision #554 §2.5) — si CCW est éteint,
+   elle attend simplement dans la file.
+5. Commentaire de référence croisée posté sur l'issue CCL (numéro de
+   l'issue CCW). Best-effort : un échec ici ne remet pas en cause le
+   succès des 2 créations.
+6. Démarrage best-effort du watcher `for-linux` de `bridge_agent` (même
+   logique que `app.issues.envoyer`, issue #202).
+
+**Anti-double-soumission :** `_issue_ouverte_meme_titre` (`app/issues.py`,
+#189, déjà en place) réutilisé avec un titre déterministe par projet
+(`_titre_issue_ccl`/`_titre_issue_ccw`), plus désactivation du bouton
+« Créer » côté JS dès le premier clic (mécanisme déjà existant du modal,
+issue #99).
+
+**Échec partiel assumé** (§4 de la conception #553, pas de mécanisme
+transactionnel) : si l'issue CCW échoue après que l'issue CCL a réussi, la
+réponse renvoie quand même le numéro/l'URL de l'issue CCL déjà créée —
+Alain peut réessayer manuellement le volet CCW sans dupliquer le volet CCL.
+
+**Confirmation utilisateur :** encart dédié (`static/js/app.js::
+npCcwBootstrap`) affichant les liens directs vers les 2 issues créées, avec
+le rappel explicite que l'issue CCW attend simplement dans la file si CCW
+est éteint — aucune action supplémentaire nécessaire.
+
+**Test sans vraie machine CCW ni vraie issue GitHub** (même technique que
+`tests/test_creation_bootstrap_ccw_556.py`) :
+`tests/test_projet_ccw_559.py` — chiffrement réel (aller-retour avec
+`watcher.dechiffrer_token_bootstrap`, y compris le cas mauvaise clé),
+corps des 2 issues (celui de l'issue CCW vérifié **parsable** par
+`watcher.creation_demandee`/`extraire_champs_creation` — le verrou anti-
+régression le plus important de ce fichier), titres déterministes,
+création d'issue via un faux `gh` (succès + anti-doublon), et la route
+`bootstrap_projet_ccw` complète de bout en bout (validations, chemin de
+succès avec déchiffrement réel des tokens postés, cross-référence,
+démarrage du watcher neutralisé pour ne jamais lancer un vrai sous-
+processus pendant le test).
 
 ---
 
# (diff du fichier suivant)
diff --git a/app/__init__.py b/app/__init__.py
# (index — ignorable)
index 082be7b..836803b 100644
# (avant — fichier suivant)
--- a/app/__init__.py
# (après — fichier suivant)
+++ b/app/__init__.py
# ── Zone modifiée : ligne 62 (6 ligne(s)) dans l'ancienne version → ligne 62 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -62,6 +62,8 @@ def _enregistrer_routes(app: Flask) -> None:
     from app.auth import login_requis, login, login_post, logout
     from app.projets import get_config, post_config, tester_bip
     from app.nouveau_projet import verifier_nouveau_projet, creer_nouveau_projet
+    from app.projet_ccw import (etat_cle_publique, rafraichir_cle_publique,
+                                bootstrap_projet_ccw)
     from app.watchers import (watchers, lancer_watcher,
                               arreter_watcher_route, statut)
     from app.issues import (apercu, envoyer, issues_liste, issue_detail,
# ── Zone modifiée : ligne 110 (6 ligne(s)) dans l'ancienne version → ligne 112 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -110,6 +112,10 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/tester-bip/<nom_projet>", "tester_bip", login_requis(tester_bip), methods=["POST"])
     app.add_url_rule("/nouveau-projet/verifier", "verifier_nouveau_projet", login_requis(verifier_nouveau_projet), methods=["GET"])
     app.add_url_rule("/nouveau-projet", "creer_nouveau_projet", login_requis(creer_nouveau_projet), methods=["POST"])
+    # ─── Case « Projet CCW » (issue #559, 3/3) : chiffrement + 2 issues croisées ─
+    app.add_url_rule("/projet-ccw/cle-publique/etat", "etat_cle_publique", login_requis(etat_cle_publique), methods=["GET"])
+    app.add_url_rule("/projet-ccw/rafraichir-cle", "rafraichir_cle_publique", login_requis(rafraichir_cle_publique), methods=["POST"])
+    app.add_url_rule("/projet-ccw/bootstrap", "bootstrap_projet_ccw", login_requis(bootstrap_projet_ccw), methods=["POST"])
     app.add_url_rule("/watchers", "watchers", login_requis(watchers))
     app.add_url_rule("/lancer-watcher", "lancer_watcher", login_requis(lancer_watcher), methods=["POST"])
     app.add_url_rule("/arreter-watcher", "arreter_watcher_route", login_requis(arreter_watcher_route), methods=["POST"])
# (diff du fichier suivant)
diff --git a/app/projet_ccw.py b/app/projet_ccw.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..fa79c32
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/app/projet_ccw.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (398 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,398 @@
+"""Case « Projet CCW » — chiffrement des tokens et génération automatique des
+2 issues croisées (issue #559, 3/3 de la conception #553/#554).
+
+Brique finale du chantier « Projet CCW » : relie l'interface web à ce qui
+existe déjà — la paire de clés générée côté CCW (issue #554, 1/3) et le
+traitement déterministe du champ `CREATION` dans `watcher.py` (#556, 2/3,
+déjà validé en conditions réelles sur `rummikub`, #557). Module DÉDIÉ plutôt
+que d'alourdir `app/nouveau_projet.py` (même séparation que `app/ccw.py`) :
+appelé par le front-end APRÈS le succès de la création classique du projet
+CCL (`np_cli.creer_projet`, route `/nouveau-projet`), jamais avant — voir
+`bootstrap_projet_ccw` plus bas.
+
+DÉCISION — cache local de la clé publique de bootstrap (point le plus ouvert
+de la conception, #553 §5 point 1 implicite / #559 tâche 1) :
+  La clé publique (`C:\\CCW\\cles_bootstrap\\bootstrap_publique.pem`, #554)
+  n'est PAS récupérée par un aller-retour SSH à CHAQUE création de projet —
+  cela réintroduirait exactement la dépendance à « CCW allumé » que ce
+  chantier vise justement à éviter (la case doit fonctionner même PC
+  éteint, #553 point 3). Elle est au contraire mise en CACHE localement,
+  dans `configs/ccw_bootstrap_publique.pem` (gitignoré : état local de la
+  machine CCL, pas du code — la clé n'est pas secrète en elle-même, mais
+  spécifique à l'instance CCW courante et sans intérêt dans l'historique
+  git, cf. REINSTALLATION_CCW.md §8 sur sa régénération à chaque
+  réinstallation). Rafraîchissement MANUEL (bouton dédié dans le bloc
+  d'instructions du formulaire → `rafraichir_cle_publique` ci-dessous),
+  PAS automatique à chaque soumission — à déclencher après une (première
+  génération ou) rotation de la paire de clés côté CCW. Réutilise le
+  mécanisme SSH déjà en place et déjà testé (`app/ccw.py` :
+  `_charger_config_ssh`/`OPTIONS_SSH`) pour le SEUL cas où une connexion à
+  CCW est nécessaire dans tout ce module.
+
+Chiffrement (BRIDGE_AGENT_DOC.md §16.6, à respecter EXACTEMENT — convention
+déjà VALIDÉE par le déchiffrement réel côté `watcher.py`, #556/#557) :
+RSA/OAEP-SHA256 via `openssl pkeyutl -encrypt`, sortie encodée en base64 sur
+UNE SEULE ligne. `_chiffrer_token` ci-dessous est le miroir exact, côté
+chiffrement, de `dechiffrer_token_bootstrap` (watcher.py).
+
+Génération des 2 issues (modèle #553 §2.1) : deux issues INDÉPENDANTES sur
+le dépôt Bridge_Agent (jamais celui du nouveau projet — c'est le canal
+unifié `for-windows` de Bridge_Agent qui porte le bootstrap, cf. §16 du
+DOC), liées par référence croisée une fois les deux numéros connus. Anti-
+double-soumission : `_issue_ouverte_meme_titre` (app/issues.py, déjà en
+place, #189), avec un titre déterministe par projet.
+"""
+
+import base64
+import datetime
+import os
+import shutil
+import subprocess
+import tempfile
+from pathlib import Path
+
+from flask import jsonify, request
+
+DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
+
+# Cache local de la clé publique de bootstrap (voir décision en tête de
+# fichier) — hors de configs/*.conf (le garde-fou §11 sur les .conf projets
+# ne s'y applique pas, et ce n'est de toute façon pas un fichier projet).
+CHEMIN_CLE_PUBLIQUE_CACHE = DOSSIER_SCRIPT / "configs" / "ccw_bootstrap_publique.pem"
+
+# Chemin de la clé publique côté CCW — DOIT rester synchronisé avec
+# $CheminPublique de provisioning/windows/provisionner.ps1 (issue #554, 1/3).
+CHEMIN_CLE_PUBLIQUE_DISTANT = "C:/CCW/cles_bootstrap/bootstrap_publique.pem"
+
+TIMEOUT_OPENSSL   = 30
+TIMEOUT_SSH_CLE   = 30
+TIMEOUT_GH        = 30
+
+NOM_PROJET_BRIDGE_AGENT = "bridge_agent"
+
+
+def _config_bridge_agent():
+    """Config du projet bridge_agent lui-même (configs/bridge_agent.conf) —
+    les 2 issues générées ci-dessous vivent TOUJOURS sur ce dépôt (canal
+    unifié `for-windows`, jamais le dépôt du nouveau projet), cf. docstring
+    de tête. Import différé (évite tout cycle avec app/projets.py)."""
+    from app.projets import projet_par_nom
+    return projet_par_nom(NOM_PROJET_BRIDGE_AGENT)
+
+
+# ─── Cache local de la clé publique de bootstrap ───────────────────────────
+
+def etat_cle_publique():
+    """GET /projet-ccw/cle-publique/etat — présence/date du cache local, pour
+    que le formulaire informe l'utilisateur AVANT la soumission plutôt que de
+    découvrir l'absence de clé après coup (les 2 tokens auraient déjà été
+    saisis pour rien)."""
+    if not CHEMIN_CLE_PUBLIQUE_CACHE.is_file():
+        return jsonify(presente=False)
+    horodatage = datetime.datetime.fromtimestamp(CHEMIN_CLE_PUBLIQUE_CACHE.stat().st_mtime)
+    return jsonify(presente=True, derniere_maj=horodatage.strftime("%Y-%m-%d %H:%M"))
+
+
+def rafraichir_cle_publique():
+    """POST /projet-ccw/rafraichir-cle — récupère `bootstrap_publique.pem`
+    depuis CCW (SSH/scp) et rafraîchit le cache local. SEUL point de ce
+    module qui exige CCW allumé — jamais appelé automatiquement à la
+    création d'un projet (voir décision en tête de fichier). À relancer
+    après une (première génération ou) rotation de la paire de clés côté
+    CCW (#554, REINSTALLATION_CCW.md §8)."""
+    from app.ccw import _charger_config_ssh, OPTIONS_SSH
+    ctx, erreur = _charger_config_ssh()
+    if erreur:
+        return jsonify(succes=False, erreur=erreur)
+    hote, utilisateur, cle_privee = ctx
+
+    CHEMIN_CLE_PUBLIQUE_CACHE.parent.mkdir(parents=True, exist_ok=True)
+    fd, chemin_tmp = tempfile.mkstemp(prefix="ccw-cle-pub-", suffix=".pem",
+                                       dir=str(CHEMIN_CLE_PUBLIQUE_CACHE.parent))
+    os.close(fd)
+    try:
+        res = subprocess.run(
+            ["scp", "-i", cle_privee, *OPTIONS_SSH,
+             f"{utilisateur}@{hote}:{CHEMIN_CLE_PUBLIQUE_DISTANT}", chemin_tmp],
+            capture_output=True, text=True, timeout=TIMEOUT_SSH_CLE,
+        )
+    except subprocess.TimeoutExpired:
+        return jsonify(succes=False,
+            erreur="Délai dépassé en récupérant la clé publique (SSH) — CCW est-il allumé ?")
+    except subprocess.SubprocessError as e:
+        return jsonify(succes=False, erreur=f"Erreur SSH : {e}")
+
+    if res.returncode != 0:
+        Path(chemin_tmp).unlink(missing_ok=True)
+        detail = (res.stderr or res.stdout or "").strip()
+        return jsonify(succes=False,
+            erreur=f"Échec de la récupération (code {res.returncode}). {detail} — "
+                   "la paire de clés a-t-elle bien été générée côté CCW (provisionner.ps1, #554) ?")
+
+    contenu = Path(chemin_tmp).read_text(encoding="utf-8", errors="replace")
+    Path(chemin_tmp).unlink(missing_ok=True)
+    if "BEGIN PUBLIC KEY" not in contenu:
+        return jsonify(succes=False,
+            erreur="Le fichier récupéré ne ressemble pas à une clé publique PEM — cache NON modifié.")
+
+    CHEMIN_CLE_PUBLIQUE_CACHE.write_text(contenu, encoding="utf-8")
+    return jsonify(succes=True, message="Clé publique de bootstrap rafraîchie.")
+
+
+# ─── Chiffrement des tokens (§16.6 du DOC — miroir de dechiffrer_token_bootstrap) ─
+
+def _chiffrer_token(token: str, chemin_cle_publique: Path) -> str:
+    """Chiffre `token` avec la clé PUBLIQUE de bootstrap (RSA/OAEP-SHA256)
+    puis encode le résultat en base64 SANS retour à la ligne (issue #556,
+    BRIDGE_AGENT_DOC.md §16.6) — convention à NE PAS FAIRE DÉVIER : un
+    mauvais padding ferait ÉCHOUER le déchiffrement côté watcher.py plutôt
+    que de produire un résultat corrompu (propriété volontaire d'OAEP).
+    Lève RuntimeError si openssl est absent ou échoue."""
+    openssl = shutil.which("openssl")
+    if not openssl:
+        raise RuntimeError("openssl introuvable sur le PATH (CCL) — impossible de chiffrer les tokens.")
+    res = subprocess.run(
+        [openssl, "pkeyutl", "-encrypt",
+         "-pubin", "-inkey", str(chemin_cle_publique),
+         "-pkeyopt", "rsa_padding_mode:oaep", "-pkeyopt", "rsa_oaep_md:sha256"],
+        input=token.encode("utf-8"), capture_output=True, timeout=TIMEOUT_OPENSSL,
+    )
+    if res.returncode != 0:
+        raise RuntimeError(
+            f"openssl pkeyutl -encrypt a échoué (code {res.returncode}) : "
+            f"{res.stderr.decode('utf-8', errors='replace').strip()}"
+        )
+    return base64.b64encode(res.stdout).decode("ascii")
+
+
+# ─── Construction des 2 issues (modèle #553 §2.1/§2.2/§2.3) ────────────────
+
+def _titre_issue_ccl(nom: str) -> str:
+    return f"Projet CCW — ajout de « {nom} » à la réinstallation (reinstaller_projets_ccw.ps1)"
+
+
+def _titre_issue_ccw(nom: str) -> str:
+    return f"Projet CCW — création du service dédié « {nom} »"
+
+
+def _corps_issue_ccl(nom: str, depot: str, numero_ccw: int | None) -> str:
+    entete = "\n".join([
+        "## En-tête\n",
+        "| Champ    | Valeur |",
+        "|----------|--------|",
+        "| SOURCE   | CC |",
+        "| DEST     | CCL |",
+        "| RETOUR   | CC |",
+        "| MODE     | écriture |",
+        "| PRIORITE | normale |",
+        "| TIMEOUT  | 300s |",
+        "| PROJET   | bridge_agent |",
+        "",
+        "| COMPLEXITE | rapide |",
+    ])
+    reference = f"\nIssue CCW liée (création du service) : #{numero_ccw}.\n" if numero_ccw else ""
+    corps = (
+        "## Tâche\n\n"
+        f"Ajouter le projet « {nom} » (dépôt {depot}) à la liste de "
+        "réinstallation CCW (case « Projet CCW » du formulaire, issue #559) :\n\n"
+        "1. `provisioning/windows/reinstaller_projets_ccw.ps1` — ajouter une "
+        f'entrée `@{{ NomProjet = "{nom}"; Depot = "{depot}" }}` au tableau '
+        "`$Projets` (source de vérité, issue #552).\n"
+        "2. `provisioning/windows/REINSTALLATION_CCW.md` (§7) — ajouter la "
+        "ligne correspondante au tableau de rappel (simple reproduction du "
+        "tableau `$Projets` pour la lecture).\n"
+        f"{reference}"
+    )
+    return f"{entete}\n\n{corps}"
+
+
+def _corps_issue_ccw(nom: str, depot: str, topic: str,
+                      gh_chiffre: str, oauth_chiffre: str, numero_ccl: int) -> str:
+    # Format EXACT attendu par watcher.py::extraire_champs_creation /
+    # creation_demandee (BRIDGE_AGENT_DOC.md §16.6) — six champs, dont les 4
+    # premiers après COMPLEXITE forment le bloc CREATION_*, séparé du reste
+    # de l'en-tête standard par une ligne vide (même mise en page que
+    # l'issue de test réelle #557, déjà traitée avec succès par #556).
+    entete = "\n".join([
+        "## En-tête\n",
+        "| Champ    | Valeur |",
+        "|----------|--------|",
+        "| SOURCE   | CC |",
+        "| DEST     | CCL |",
+        "| RETOUR   | CC |",
+        "| MODE     | écriture |",
+        "| PRIORITE | normale |",
+        "| TIMEOUT  | 600s |",
+        "| PROJET   | bridge_agent |",
+        "",
+        "| COMPLEXITE | normal |",
+        "",
+        "| CREATION              | oui |",
+        f"| CREATION_NOM_PROJET   | {nom} |",
+        f"| CREATION_DEPOT        | {depot} |",
+        f"| CREATION_TOPIC_NTFY   | {topic} |",
+        f"| CREATION_GH_TOKEN     | {gh_chiffre} |",
+        f"| CREATION_OAUTH_TOKEN  | {oauth_chiffre} |",
+    ])
+    corps = (
+        f"\nBootstrap automatique d'un service CCW dédié pour « {nom} » "
+        "(case « Projet CCW », issue #559) — traitement ENTIÈREMENT "
+        "déterministe par `watcher.py` (#556), AUCUNE session `claude` "
+        "invoquée (décision #554 §2.5). Si CCW est éteint à la réception : "
+        "cette issue attend simplement dans la file, aucune action "
+        "supplémentaire nécessaire.\n\n"
+        f"Issue CCL liée (mise à jour de la réinstallation) : #{numero_ccl}.\n"
+    )
+    return f"{entete}\n{corps}"
+
+
+# ─── Création d'issue via gh (anti-doublon + gh issue create) ──────────────
+
+def _creer_issue_gh(cfg, titre: str, labels: str, corps: str) -> dict:
+    """Crée une issue sur `cfg.depot` — même patron que `app.issues.envoyer`
+    (anti-doublon `_issue_ouverte_meme_titre`, `--body-file` pour éviter tout
+    enfer d'échappement/troncature argv), dupliqué ici plutôt qu'appelé à
+    travers la route Flask (qui lit `request.json`, non réutilisable
+    directement pour une création pilotée en Python). Retourne
+    {succes, numero, url} ou {succes: False, erreur}."""
+    from app.issues import _issue_ouverte_meme_titre
+
+    titre = titre.strip()
+    doublon = _issue_ouverte_meme_titre(cfg, titre)
+    if doublon is not None:
+        return {"succes": False, "erreur": f"Une issue portant ce titre est déjà ouverte : #{doublon}"}
+
+    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
+        f.write(corps)
+        chemin_body = f.name
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "create",
+             "--repo",      cfg.depot,
+             "--title",     titre,
+             "--label",     labels,
+             "--body-file", chemin_body],
+            capture_output=True, text=True, timeout=TIMEOUT_GH,
+        )
+        if res.returncode != 0:
+            return {"succes": False, "erreur": res.stderr.strip() or "Erreur inconnue de gh."}
+        url = res.stdout.strip()
+        try:
+            numero = int(url.rsplit("/", 1)[-1])
+        except ValueError:
+            numero = None
+        return {"succes": True, "url": url, "numero": numero}
+    except subprocess.TimeoutExpired:
+        return {"succes": False, "erreur": "Timeout (gh n'a pas répondu en 30s)."}
+    except FileNotFoundError:
+        return {"succes": False, "erreur": "gh introuvable dans le PATH."}
+    except Exception as e:  # noqa: BLE001
+        return {"succes": False, "erreur": str(e)}
+    finally:
+        os.unlink(chemin_body)
+
+
+def _commenter_issue_gh(depot: str, numero: int, message: str) -> bool:
+    """Poste un commentaire (référence croisée) — mêmes garanties que
+    `watcher.commenter_issue` (--body-file), dupliqué ici car ce module
+    tourne dans le processus Flask, pas dans un watcher.py déjà configuré
+    sur ce dépôt précis."""
+    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
+        f.write(message)
+        chemin_body = f.name
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "comment", str(numero), "--repo", depot, "--body-file", chemin_body],
+            capture_output=True, text=True, timeout=TIMEOUT_GH,
+        )
+        return res.returncode == 0
+    except subprocess.SubprocessError:
+        return False
+    finally:
+        os.unlink(chemin_body)
+
+
+# ─── Route principale ───────────────────────────────────────────────────────
+
+def bootstrap_projet_ccw():
+    """POST /projet-ccw/bootstrap — chiffrement des 2 tokens + génération des
+    2 issues croisées. Appelée par le front-end JUSTE APRÈS le succès de la
+    création classique du projet CCL (`POST /nouveau-projet`), jamais avant
+    (§2 de la conception #553) : reçoit {nom, depot, topic, gh_token,
+    oauth_token} — les 3 premiers identiques à ceux déjà validés/soumis à
+    `/nouveau-projet`, pas resaisis.
+
+    Validation stricte (déjà faite côté client, revérifiée ici — jamais
+    confiance seule au JS) : les 2 tokens sont obligatoires. Échec partiel
+    assumé (§4 de la conception #553, pas de mécanisme transactionnel) :
+    si l'issue CCW échoue après que l'issue CCL a réussi, l'issue CCL reste
+    (son numéro est renvoyé) — Alain peut réessayer manuellement le volet
+    CCW sans dupliquer le volet CCL."""
+    data        = request.json or {}
+    nom         = (data.get("nom")   or "").strip()
+    depot       = (data.get("depot") or "").strip()
+    topic       = (data.get("topic") or "").strip()
+    gh_token    = data.get("gh_token")    or ""
+    oauth_token = data.get("oauth_token") or ""
+
+    if not nom or not depot or not topic:
+        return jsonify(succes=False, erreur="nom/depot/topic requis (projet CCL non transmis correctement).")
+    if not gh_token or not oauth_token:
+        return jsonify(succes=False,
+            erreur="Les deux tokens (GH_TOKEN et CLAUDE_CODE_OAUTH_TOKEN) sont requis pour « Projet CCW ».")
+
+    if not CHEMIN_CLE_PUBLIQUE_CACHE.is_file():
+        return jsonify(succes=False,
+            erreur="Clé publique de bootstrap absente du cache local — cliquez « Rafraîchir la "
+                   "clé » (CCW doit être allumé et joignable en SSH) avant de soumettre « Projet CCW ».")
+
+    try:
+        gh_chiffre    = _chiffrer_token(gh_token, CHEMIN_CLE_PUBLIQUE_CACHE)
+        oauth_chiffre = _chiffrer_token(oauth_token, CHEMIN_CLE_PUBLIQUE_CACHE)
+    except RuntimeError as e:
+        return jsonify(succes=False, erreur=f"Chiffrement des tokens impossible : {e}")
+
+    cfg_ba = _config_bridge_agent()
+    if not cfg_ba:
+        return jsonify(succes=False,
+            erreur="Projet bridge_agent introuvable côté CCL (configs/bridge_agent.conf) — impossible "
+                   "de créer les issues de bootstrap.")
+
+    # 1. Issue CCL (mise à jour de la réinstallation) — créée en premier,
+    #    sans encore connaître le numéro de l'issue CCW (référence croisée
+    #    ajoutée en commentaire une fois celle-ci créée, cf. §2.1 de #553).
+    res_ccl = _creer_issue_gh(cfg_ba, _titre_issue_ccl(nom),
+                               "bridge,for-linux,mode_write", _corps_issue_ccl(nom, depot, None))
+    if not res_ccl["succes"]:
+        return jsonify(succes=False, erreur=f"Issue CCL (réinstallation) : {res_ccl['erreur']}")
+
+    # 2. Issue CCW (canal unifié for-windows) — porte le bootstrap réel.
+    res_ccw = _creer_issue_gh(cfg_ba, _titre_issue_ccw(nom),
+                               "bridge,for-windows,mode_write",
+                               _corps_issue_ccw(nom, depot, topic, gh_chiffre, oauth_chiffre,
+                                                 res_ccl["numero"]))
+    if not res_ccw["succes"]:
+        return jsonify(succes=False,
+            erreur=f"Issue CCL #{res_ccl['numero']} créée, mais l'issue CCW a échoué : "
+                   f"{res_ccw['erreur']} — relancer manuellement la création du service CCW.",
+            issue_ccl_numero=res_ccl["numero"], issue_ccl_url=res_ccl["url"])
+
+    # 3. Référence croisée dans l'autre sens (best-effort — un échec ici ne
+    #    remet pas en cause le succès des 2 créations).
+    _commenter_issue_gh(cfg_ba.depot, res_ccl["numero"],
+                         f"Issue CCW liée (création du service) : #{res_ccw['numero']}.")
+
+    # 4. Démarrage automatique du watcher for-linux de bridge_agent (même
+    #    logique que app.issues.envoyer pour toute issue for-linux, issue
+    #    #202) — best-effort, ne doit jamais transformer un succès en échec.
+    try:
+        from app.watchers import demarrer_watcher
+        demarrer_watcher(cfg_ba, forcer=False)
+    except Exception:
+        pass
+
+    return jsonify(
+        succes=True,
+        issue_ccl_numero=res_ccl["numero"], issue_ccl_url=res_ccl["url"],
+        issue_ccw_numero=res_ccw["numero"], issue_ccw_url=res_ccw["url"],
+    )
# (diff du fichier suivant)
diff --git a/provisioning/windows/REINSTALLATION_CCW.md b/provisioning/windows/REINSTALLATION_CCW.md
# (index — ignorable)
index 2d047b0..4a1e736 100644
# (avant — fichier suivant)
--- a/provisioning/windows/REINSTALLATION_CCW.md
# (après — fichier suivant)
+++ b/provisioning/windows/REINSTALLATION_CCW.md
# ── Zone modifiée : ligne 148 (8 ligne(s)) dans l'ancienne version → ligne 148 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -148,8 +148,13 @@ stade** : cette étape ne fait que poser la paire de clés elle-même).
   la clé privée n'a rien à y faire).
 - **Clé publique** : `C:\CCW\cles_bootstrap\bootstrap_publique.pem` — pas
   sensible, à récupérer côté CCL pour chiffrer les tokens avant inclusion
-  dans le corps d'une future issue. Deux façons de la récupérer, aucune
-  automatisée pour l'instant :
+  dans le corps d'une future issue. Trois façons de la récupérer :
+  - **automatique (recommandé, issue #559)** : bouton « 🔄 Rafraîchir la clé
+    publique » dans le bloc d'instructions de la case « Projet CCW » du
+    formulaire de création de projet (`POST /projet-ccw/rafraichir-cle`,
+    `app/projet_ccw.py`) — met à jour le cache local
+    `configs/ccw_bootstrap_publique.pem` via la session SSH existante. À
+    relancer après CETTE étape de réinstallation (nouvelle paire de clés) ;
   - **copier-coller manuel** : `provisionner.ps1` affiche son contenu PEM
     intégral en toute fin d'exécution ;
   - **via la session SSH existante** (étape 3 ci-dessus, voir aussi
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index e86eaad..a228ae0 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 5584 (6 ligne(s)) dans l'ancienne version → ligne 5584 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5584,6 +5584,15 @@ function ouvrirNouveauProjet() {
   document.getElementById('np-message').style.display = 'none';
   document.getElementById('np-rappel-git').style.display = 'none';
   document.getElementById('np-rappel-projet').style.display = 'none';
+  // Case « Projet CCW » (issue #559) : toujours décochée à l'ouverture, tokens
+  // jamais pré-remplis d'une session à l'autre.
+  document.getElementById('np-ccw').checked = false;
+  document.getElementById('np-ccw-bloc').style.display = 'none';
+  document.getElementById('np-ccw-gh-token').value = '';
+  document.getElementById('np-ccw-oauth-token').value = '';
+  document.getElementById('np-ccw-msg').textContent = '';
+  document.getElementById('np-ccw-cle-etat').textContent = '';
+  document.getElementById('np-rappel-ccw').style.display = 'none';
   const btn = document.getElementById('np-creer');
   btn.disabled = false; btn.textContent = 'Créer le projet';
   document.getElementById('np-fermer').textContent = 'Fermer';
# ── Zone modifiée : ligne 5742 (6 ligne(s)) dans l'ancienne version → ligne 5751 (108 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5742,6 +5751,108 @@ function npMsg(texte, type) {
   el.style.display = 'block';
 }
 
+// Case « Projet CCW » (issue #559, 3/3) : affiche/masque le bloc
+// d'instructions + les 2 champs tokens, et vérifie l'état du cache local de
+// la clé publique de bootstrap (sans bloquer la saisie — juste informatif,
+// la validation réelle a lieu à la soumission côté serveur).
+function npCcwToggle() {
+  const actif = document.getElementById('np-ccw').checked;
+  document.getElementById('np-ccw-bloc').style.display = actif ? 'block' : 'none';
+  if (actif) npCcwChargerEtatCle();
+}
+
+async function npCcwChargerEtatCle() {
+  const etat = document.getElementById('np-ccw-cle-etat');
+  etat.textContent = 'Vérification de la clé publique de bootstrap…';
+  etat.style.color = '#555';
+  let r;
+  try {
+    r = await (await fetch('/projet-ccw/cle-publique/etat')).json();
+  } catch (e) {
+    etat.textContent = '⚠ Impossible de vérifier la clé publique (erreur réseau).';
+    etat.style.color = '#a32d2d';
+    return;
+  }
+  if (r.presente) {
+    etat.textContent = '✓ Clé publique en cache (rafraîchie le ' + r.derniere_maj + ').';
+    etat.style.color = '#2e7d32';
+  } else {
+    etat.textContent = '⚠ Aucune clé publique en cache — cliquez « Rafraîchir la clé » '
+                      + 'ci-dessous avant de soumettre (CCW doit être allumé et joignable en SSH).';
+    etat.style.color = '#a32d2d';
+  }
+}
+
+// Rafraîchissement MANUEL du cache local (SSH vers CCW) — jamais déclenché
+// automatiquement à la soumission (voir décision documentée dans
+// app/projet_ccw.py) : à utiliser après une (première génération ou)
+// rotation de la paire de clés côté CCW.
+async function npCcwRafraichirCle(btn) {
+  const avant = btn.textContent;
+  btn.disabled = true; btn.textContent = 'Récupération…';
+  const msg = document.getElementById('np-ccw-msg');
+  msg.textContent = '';
+  let r;
+  try {
+    const rep = await fetch('/projet-ccw/rafraichir-cle', {method: 'POST'});
+    r = await rep.json();
+  } catch (e) {
+    btn.disabled = false; btn.textContent = avant;
+    msg.textContent = 'Erreur réseau : ' + e.message;
+    msg.style.color = '#a32d2d';
+    return;
+  }
+  btn.disabled = false; btn.textContent = avant;
+  if (r.succes) {
+    msg.textContent = '✓ ' + (r.message || 'Clé rafraîchie.');
+    msg.style.color = '#2e7d32';
+    npCcwChargerEtatCle();
+  } else {
+    msg.textContent = '❌ ' + (r.erreur || 'Échec.');
+    msg.style.color = '#a32d2d';
+  }
+}
+
+// Chiffrement + génération des 2 issues croisées, appelé APRÈS le succès de
+// la création classique du projet CCL (jamais avant — cf. app/projet_ccw.py).
+// Échec ici n'annule pas la création du projet CCL déjà faite : affiché dans
+// un encart séparé, le projet reste utilisable normalement côté CCL.
+async function npCcwBootstrap(nom, depot, topic, ghToken, oauthToken) {
+  const box = document.getElementById('np-rappel-ccw');
+  box.innerHTML = '<div class="titre">⏳ Projet CCW — génération des 2 issues…</div>';
+  box.style.display = 'block';
+  let r;
+  try {
+    const rep = await fetch('/projet-ccw/bootstrap', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({nom, depot, topic, gh_token: ghToken, oauth_token: oauthToken}),
+    });
+    r = await rep.json();
+  } catch (e) {
+    box.innerHTML = '<div class="titre">❌ Projet CCW — erreur réseau</div><div>'
+                   + escapeHtml(e.message) + '</div>';
+    return;
+  }
+  if (r.succes) {
+    box.innerHTML =
+      '<div class="titre">✅ Projet CCW — 2 issues créées</div>'
+      + '<div>Issue CCL (réinstallation) : <a href="' + escapeHtml(r.issue_ccl_url) + '" target="_blank">#'
+      + r.issue_ccl_numero + '</a></div>'
+      + '<div>Issue CCW (création du service) : <a href="' + escapeHtml(r.issue_ccw_url) + '" target="_blank">#'
+      + r.issue_ccw_numero + '</a></div>'
+      + '<div style="margin-top:6px">Si CCW est éteint, l\'issue CCW attend simplement dans la '
+      + 'file — aucune action supplémentaire nécessaire.</div>';
+  } else {
+    let html = '<div class="titre">❌ Projet CCW — échec</div><div>' + escapeHtml(r.erreur || 'Erreur inconnue.') + '</div>';
+    if (r.issue_ccl_numero) {
+      html += '<div>Issue CCL déjà créée : <a href="' + escapeHtml(r.issue_ccl_url) + '" target="_blank">#'
+            + r.issue_ccl_numero + '</a></div>';
+    }
+    box.innerHTML = html;
+  }
+}
+
 async function soumettreNouveauProjet() {
   const nom = document.getElementById('np-nom').value.trim().toLowerCase();
   const cr  = document.getElementById('np-compte-rendu');
# ── Zone modifiée : ligne 5749 (8 ligne(s)) dans l'ancienne version → ligne 5860 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5749,8 +5860,24 @@ async function soumettreNouveauProjet() {
   cr.style.display = 'none';
   document.getElementById('np-rappel-git').style.display = 'none';
   document.getElementById('np-rappel-projet').style.display = 'none';
+  document.getElementById('np-rappel-ccw').style.display = 'none';
   if (!nom) { npMsg('Un nom de projet est requis.', 'erreur'); return; }
 
+  // Validation stricte (client) de la case « Projet CCW » (issue #559) :
+  // revérifiée aussi côté serveur (app/projet_ccw.py), jamais confiance seule
+  // au JS — le topic est exigé explicitement ici (pas de résolution du
+  // défaut serveur côté client, pour ne jamais transmettre un topic CCW qui
+  // ne correspondrait pas à celui réellement écrit dans le .conf CCL).
+  const ccwActif = document.getElementById('np-ccw').checked;
+  const ccwTopic = document.getElementById('np-topic').value.trim();
+  const ccwGh    = document.getElementById('np-ccw-gh-token').value;
+  const ccwOauth = document.getElementById('np-ccw-oauth-token').value;
+  if (ccwActif && (!ccwTopic || !ccwGh || !ccwOauth)) {
+    npMsg('« Projet CCW » coché : le topic ntfy et les 2 tokens (GH_TOKEN, '
+        + 'CLAUDE_CODE_OAUTH_TOKEN) sont obligatoires.', 'erreur');
+    return;
+  }
+
   const btn = document.getElementById('np-creer');
   const avant = btn.textContent;
   btn.disabled = true; btn.textContent = 'Création…';
# ── Zone modifiée : ligne 5809 (6 ligne(s)) dans l'ancienne version → ligne 5936 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5809,6 +5936,12 @@ async function soumettreNouveauProjet() {
     // #257 — sans eux l'encart ci-dessus, seul affiché jusque-là, laissait
     // croire à tort que rien d'autre n'était à faire.
     afficherRappelProjet(res);
+    // Case « Projet CCW » (issue #559) : chiffrement + génération des 2
+    // issues croisées, APRÈS le succès ci-dessus, jamais avant — un échec
+    // ici n'annule pas la création CCL déjà faite (encart séparé).
+    if (ccwActif) {
+      npCcwBootstrap(res.nom, res.depot, ccwTopic, ccwGh, ccwOauth);
+    }
     // Création réussie : on verrouille « Créer » (évite un double envoi) et on
     // renomme « Fermer » en « Terminé ».
     btn.disabled = true;
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 5e2a923..e91b382 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 654 (10 ligne(s)) dans l'ancienne version → ligne 654 (48 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -654,10 +654,48 @@
       Pattern Specs MVC (§15) — crée aussi CONTEXTE_VUE / METIER / PERSISTANCE
     </label>
 
+    <!-- ─── Case « Projet CCW » (issue #559, 3/3) ────────────────────────────
+         Cochée → bootstrap automatique (après la création CCL classique) d'un
+         service CCW dédié : chiffrement des 2 tokens + génération des 2
+         issues croisées (CCL réinstallation + CCW création de service). -->
+    <label style="display:block;font-size:13px;color:#333;margin-bottom:8px">
+      <input type="checkbox" id="np-ccw" onchange="npCcwToggle()">
+      Projet CCW — provisionner aussi un service CCW dédié (Windows)
+    </label>
+    <div id="np-ccw-bloc" style="display:none;margin:0 0 16px 24px;padding:10px 12px;
+         background:#f5f7fa;border:1px solid #d8dee6;border-radius:6px;font-size:12.5px;color:#333">
+      <div id="np-ccw-cle-etat" style="margin-bottom:8px"></div>
+      <div style="margin-bottom:8px">
+        Avant de cocher : crée un token GitHub <b>fine-grained</b> DÉDIÉ à ce
+        projet (GitHub → Settings → Developer settings → Fine-grained tokens) :
+        <ul style="margin:4px 0 4px 18px;padding:0">
+          <li>Repository access → ce nouveau dépôt UNIQUEMENT</li>
+          <li>Permissions : <code>Issues = Read and write</code>,
+              <code>Metadata = Read-only</code></li>
+          <li>Expiration : alignée sur les tokens CCW en cours (cf. §16.1 de
+              BRIDGE_AGENT_DOC.md)</li>
+        </ul>
+        Génère aussi un <code>CLAUDE_CODE_OAUTH_TOKEN</code> (<code>claude
+        setup-token</code>), puis colle les deux valeurs ci-dessous.
+      </div>
+      <div class="champ" style="margin-bottom:8px">
+        <label>GH_TOKEN (token GitHub fine-grained dédié)</label>
+        <input type="password" id="np-ccw-gh-token" autocomplete="off">
+      </div>
+      <div class="champ" style="margin-bottom:4px">
+        <label>CLAUDE_CODE_OAUTH_TOKEN</label>
+        <input type="password" id="np-ccw-oauth-token" autocomplete="off">
+      </div>
+      <button type="button" id="np-ccw-rafraichir-cle" onclick="npCcwRafraichirCle(this)"
+              style="margin-top:4px;font-size:12px">🔄 Rafraîchir la clé publique (CCW allumé requis)</button>
+      <div id="np-ccw-msg" style="font-size:12px;min-height:14px;margin-top:6px"></div>
+    </div>
+
     <div id="np-compte-rendu" class="modal-liste" style="display:none"></div>
     <div id="np-message" class="message" style="display:none;margin-bottom:14px"></div>
     <div id="np-rappel-projet" class="np-rappel-projet" style="display:none"></div>
     <div id="np-rappel-git" class="np-rappel-git" style="display:none"></div>
+    <div id="np-rappel-ccw" class="np-rappel-projet" style="display:none"></div>
 
     <div class="modal-boutons">
       <button id="np-fermer" onclick="fermerNouveauProjet()">Fermer</button>
# (diff du fichier suivant)
diff --git a/tests/test_projet_ccw_559.py b/tests/test_projet_ccw_559.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..31c86aa
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_projet_ccw_559.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (442 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,442 @@
+#!/usr/bin/env python3
+"""Test de non-régression — issue #559 (3/3) : case « Projet CCW » sur le
+formulaire de création de projet — chiffrement et génération automatique
+des 2 issues (app/projet_ccw.py).
+
+Couvre, SANS vraie machine CCW ni vraie issue GitHub (même technique que
+tests/test_creation_bootstrap_ccw_556.py — `gh` remplacé par un faux
+exécutable sur le PATH) :
+- `_chiffrer_token` : aller-retour réel via openssl avec
+  `watcher.dechiffrer_token_bootstrap` (#556) — vérifie que le chiffrement
+  côté formulaire est le MIROIR EXACT du déchiffrement déjà validé côté
+  watcher.py, padding OAEP/SHA-256 compris ;
+- `_corps_issue_ccw` : le corps produit est parsable par
+  `watcher.creation_demandee`/`extraire_champs_creation` — format EXACT
+  attendu par #556 (BRIDGE_AGENT_DOC.md §16.6), verrou anti-régression le
+  plus important de ce fichier ;
+- `_corps_issue_ccl` : référence le script/la doc de réinstallation et la
+  cross-référence vers l'issue CCW une fois son numéro connu ;
+- `_titre_issue_ccl`/`_titre_issue_ccw` : déterministes (même nom → même
+  titre), condition nécessaire à la réutilisation de
+  `_issue_ouverte_meme_titre` (anti-double-soumission, #189) ;
+- `_creer_issue_gh` : création réussie (numéro extrait de l'URL `gh`) ET
+  anti-doublon (aucun `gh issue create` déclenché si une issue ouverte
+  porte déjà ce titre) ;
+- `bootstrap_projet_ccw` (route Flask complète, via test_request_context) :
+  validations (tokens manquants, clé publique absente du cache), puis
+  chemin de succès bout en bout — les 2 issues sont créées avec les BONS
+  labels/corps, la référence croisée est postée, et le démarrage du
+  watcher (best-effort) est neutralisé pour ne jamais lancer un vrai
+  sous-processus watcher.py pendant le test.
+
+Exécution :  python3 tests/test_projet_ccw_559.py
+Sortie      :  code 0 si tous les scénarios passent, 1 sinon.
+"""
+
+import base64
+import os
+import stat
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+from types import SimpleNamespace
+
+RACINE = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(RACINE))
+
+import flask  # noqa: E402
+
+import watcher  # noqa: E402
+from app import projet_ccw  # noqa: E402
+
+APP_FLASK = flask.Flask(__name__)
+
+
+# ─── Aides crypto (openssl réel, disponible sur CCL) ────────────────────────
+
+def _generer_paire_cles(tmp: Path) -> tuple[Path, Path]:
+    tmp.mkdir(parents=True, exist_ok=True)
+    priv = tmp / "bootstrap_privee.pem"
+    pub = tmp / "bootstrap_publique.pem"
+    subprocess.run(["openssl", "genpkey", "-algorithm", "RSA",
+                     "-pkeyopt", "rsa_keygen_bits:3072", "-out", str(priv)],
+                    check=True, capture_output=True)
+    subprocess.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)],
+                    check=True, capture_output=True)
+    return priv, pub
+
+
+# ─── Scénarios : chiffrement (miroir de dechiffrer_token_bootstrap) ────────
+
+def scenario_chiffrement_aller_retour_watcher(tmp_path_factory):
+    """_chiffrer_token (app/projet_ccw.py) chiffre avec la clé publique ;
+    watcher.dechiffrer_token_bootstrap (#556, déjà validé en conditions
+    réelles) doit pouvoir déchiffrer avec la clé privée correspondante et
+    retrouver exactement le texte en clair — c'est LE point de compatibilité
+    critique entre le formulaire (3/3) et le traitement watcher.py (2/3)."""
+    tmp = tmp_path_factory()
+    priv, pub = _generer_paire_cles(tmp)
+    clair = "ghp_TokenSecretDeTest1234567890"
+    b64 = projet_ccw._chiffrer_token(clair, pub)
+    # Une seule ligne (issue #16.6 : base64 -w0 ou équivalent).
+    assert "\n" not in b64, "le base64 ne doit tenir que sur une seule ligne"
+    retrouve = watcher.dechiffrer_token_bootstrap(b64, priv)
+    assert retrouve == clair, (retrouve, clair)
+    return {}
+
+
+def scenario_chiffrement_mauvaise_cle_echoue(tmp_path_factory):
+    """Chiffré avec la clé publique A, déchiffré avec la clé privée B (sans
+    rapport) → RuntimeError côté watcher.py, jamais un résultat corrompu
+    silencieux (propriété OAEP, déjà couverte côté déchiffrement par #556 —
+    revérifiée ici du point de vue du chiffrement)."""
+    tmp = tmp_path_factory()
+    _priv_a, pub_a = _generer_paire_cles(tmp / "a")
+    priv_b, _pub_b = _generer_paire_cles(tmp / "b")
+    b64 = projet_ccw._chiffrer_token("peu importe", pub_a)
+    try:
+        watcher.dechiffrer_token_bootstrap(b64, priv_b)
+        assert False, "RuntimeError attendue"
+    except RuntimeError:
+        pass
+    return {}
+
+
+# ─── Scénarios : construction des corps d'issue ─────────────────────────────
+
+def scenario_corps_issue_ccw_parsable_par_watcher():
+    """Le corps produit par _corps_issue_ccw doit être EXACTEMENT ce
+    qu'attendent creation_demandee/extraire_champs_creation (watcher.py,
+    #556) — sinon la case « Projet CCW » produirait une issue CCW jamais
+    traitée automatiquement, silencieusement."""
+    corps = projet_ccw._corps_issue_ccw(
+        "monprojet", "AlainDelree/MonProjet", "bridge-monprojet",
+        "QUFBQg==", "Q0NDRA==", numero_ccl=123,
+    )
+    assert watcher.creation_demandee(corps), "champ CREATION non détecté"
+    champs = watcher.extraire_champs_creation(corps)
+    assert champs["CREATION_NOM_PROJET"] == "monprojet", champs
+    assert champs["CREATION_DEPOT"] == "AlainDelree/MonProjet", champs
+    assert champs["CREATION_TOPIC_NTFY"] == "bridge-monprojet", champs
+    assert champs["CREATION_GH_TOKEN"] == "QUFBQg==", champs
+    assert champs["CREATION_OAUTH_TOKEN"] == "Q0NDRA==", champs
+    assert "#123" in corps, "référence croisée vers l'issue CCL absente"
+    return {"champs": list(champs)}
+
+
+def scenario_corps_issue_ccl_contenu():
+    """Le corps de l'issue CCL référence bien les 2 cibles (script +
+    tableau de la doc) et, une fois le numéro CCW connu, la cross-référence."""
+    sans_ref = projet_ccw._corps_issue_ccl("monprojet", "AlainDelree/MonProjet", None)
+    assert "reinstaller_projets_ccw.ps1" in sans_ref
+    assert "REINSTALLATION_CCW.md" in sans_ref
+    assert "monprojet" in sans_ref and "AlainDelree/MonProjet" in sans_ref
+    assert "Issue CCW liée" not in sans_ref
+
+    avec_ref = projet_ccw._corps_issue_ccl("monprojet", "AlainDelree/MonProjet", 456)
+    assert "#456" in avec_ref
+    return {}
+
+
+def scenario_titres_deterministes():
+    """Même nom de projet → même titre (nécessaire à la réutilisation
+    correcte de _issue_ouverte_meme_titre, anti-double-soumission #189)."""
+    assert projet_ccw._titre_issue_ccl("scrabble") == projet_ccw._titre_issue_ccl("scrabble")
+    assert projet_ccw._titre_issue_ccw("scrabble") == projet_ccw._titre_issue_ccw("scrabble")
+    assert projet_ccw._titre_issue_ccl("scrabble") != projet_ccw._titre_issue_ccl("rummikub")
+    assert projet_ccw._titre_issue_ccl("scrabble") != projet_ccw._titre_issue_ccw("scrabble")
+    return {}
+
+
+# ─── Scénarios : _creer_issue_gh (faux `gh`) ────────────────────────────────
+
+FAUX_GH = """#!/bin/bash
+# Faux `gh` — issue #559. issue list : renvoie $TEST_559_LISTE_OUVERTES
+# (JSON, defaut []) pour piloter l'anti-doublon. issue create : journalise
+# repo/titre/label/corps dans $TEST_559_LOG_CREATE, renvoie une URL avec un
+# numero incremental ($TEST_559_COMPTEUR). issue comment : journalise dans
+# $TEST_559_LOG_COMMENT.
+if [ "$1" = "issue" ] && [ "$2" = "list" ]; then
+    if [ -n "$TEST_559_LISTE_OUVERTES" ] && [ -f "$TEST_559_LISTE_OUVERTES" ]; then
+        cat "$TEST_559_LISTE_OUVERTES"
+    else
+        echo "[]"
+    fi
+    exit 0
+fi
+if [ "$1" = "issue" ] && [ "$2" = "create" ]; then
+    depot=""; titre=""; label=""; bodyfile=""
+    prev=""
+    for arg in "$@"; do
+        if [ "$prev" = "--repo" ]; then depot="$arg"; fi
+        if [ "$prev" = "--title" ]; then titre="$arg"; fi
+        if [ "$prev" = "--label" ]; then label="$arg"; fi
+        if [ "$prev" = "--body-file" ]; then bodyfile="$arg"; fi
+        prev="$arg"
+    done
+    n=$(cat "$TEST_559_COMPTEUR" 2>/dev/null || echo 1000)
+    n=$((n + 1))
+    echo "$n" > "$TEST_559_COMPTEUR"
+    {
+        echo "=== create #$n ==="
+        echo "DEPOT=$depot"
+        echo "TITRE=$titre"
+        echo "LABEL=$label"
+        echo "BODY-BEGIN"
+        cat "$bodyfile"
+        echo "BODY-END"
+    } >> "$TEST_559_LOG_CREATE"
+    echo "https://github.com/$depot/issues/$n"
+    exit 0
+fi
+if [ "$1" = "issue" ] && [ "$2" = "comment" ]; then
+    depot=""; bodyfile=""; numero="$3"
+    prev=""
+    for arg in "$@"; do
+        if [ "$prev" = "--repo" ]; then depot="$arg"; fi
+        if [ "$prev" = "--body-file" ]; then bodyfile="$arg"; fi
+        prev="$arg"
+    done
+    {
+        echo "=== comment on #$numero ($depot) ==="
+        cat "$bodyfile"
+    } >> "$TEST_559_LOG_COMMENT"
+    exit 0
+fi
+exit 0
+"""
+
+
+def _preparer_bin(tmp: Path) -> Path:
+    bin_dir = tmp / "bin"
+    bin_dir.mkdir(exist_ok=True)
+    chemin = bin_dir / "gh"
+    chemin.write_text(FAUX_GH, encoding="utf-8")
+    chemin.chmod(chemin.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
+    return bin_dir
+
+
+def scenario_creer_issue_gh_succes(tmp_path_factory):
+    """Chemin de succès : le numéro est correctement extrait de l'URL
+    renvoyée par gh, le corps/labels transmis sont ceux du fichier
+    temporaire (pas tronqués/déformés)."""
+    tmp = tmp_path_factory()
+    bin_dir = _preparer_bin(tmp)
+    ancien_path = os.environ.get("PATH", "")
+    log_create = tmp / "log_create.txt"
+    compteur = tmp / "compteur.txt"
+    os.environ["TEST_559_LOG_CREATE"] = str(log_create)
+    os.environ["TEST_559_COMPTEUR"] = str(compteur)
+    os.environ.pop("TEST_559_LISTE_OUVERTES", None)
+    try:
+        os.environ["PATH"] = f"{bin_dir}:{ancien_path}"
+        cfg = SimpleNamespace(depot="AlainDelree/Bridge_Agent", nom="bridge_agent")
+        res = projet_ccw._creer_issue_gh(cfg, "Un titre de test #559",
+                                          "bridge,for-linux,mode_write", "corps de test")
+        assert res["succes"], res
+        assert res["numero"] == 1001, res
+        assert res["url"] == "https://github.com/AlainDelree/Bridge_Agent/issues/1001", res
+        contenu = log_create.read_text()
+        assert "TITRE=Un titre de test #559" in contenu, contenu
+        assert "corps de test" in contenu, contenu
+    finally:
+        os.environ["PATH"] = ancien_path
+        for var in ("TEST_559_LOG_CREATE", "TEST_559_COMPTEUR", "TEST_559_LISTE_OUVERTES"):
+            os.environ.pop(var, None)
+    return {}
+
+
+def scenario_creer_issue_gh_anti_doublon(tmp_path_factory):
+    """Une issue OUVERTE portant déjà ce titre → refus, AUCUN `gh issue
+    create` déclenché (vérifié par l'absence du fichier de log — le faux gh
+    n'écrit dedans QUE sur la branche create)."""
+    tmp = tmp_path_factory()
+    bin_dir = _preparer_bin(tmp)
+    ancien_path = os.environ.get("PATH", "")
+    log_create = tmp / "log_create.txt"
+    liste = tmp / "liste_ouvertes.json"
+    liste.write_text('[{"number": 42, "title": "Titre déjà pris #559"}]', encoding="utf-8")
+    os.environ["TEST_559_LOG_CREATE"] = str(log_create)
+    os.environ["TEST_559_LISTE_OUVERTES"] = str(liste)
+    try:
+        os.environ["PATH"] = f"{bin_dir}:{ancien_path}"
+        cfg = SimpleNamespace(depot="AlainDelree/Bridge_Agent", nom="bridge_agent")
+        res = projet_ccw._creer_issue_gh(cfg, "Titre déjà pris #559", "bridge,for-linux", "corps")
+        assert not res["succes"], res
+        assert "42" in res["erreur"], res
+        assert not log_create.exists(), "gh issue create n'aurait pas dû être invoqué"
+    finally:
+        os.environ["PATH"] = ancien_path
+        for var in ("TEST_559_LOG_CREATE", "TEST_559_LISTE_OUVERTES"):
+            os.environ.pop(var, None)
+    return {}
+
+
+# ─── Scénarios : route bootstrap_projet_ccw (Flask) ─────────────────────────
+
+def _appeler_bootstrap(payload: dict):
+    with APP_FLASK.test_request_context("/projet-ccw/bootstrap", json=payload):
+        return projet_ccw.bootstrap_projet_ccw().get_json()
+
+
+def scenario_bootstrap_tokens_manquants():
+    r = _appeler_bootstrap({"nom": "monprojet", "depot": "AlainDelree/MonProjet",
+                             "topic": "bridge-monprojet", "gh_token": "", "oauth_token": ""})
+    assert not r["succes"], r
+    assert "tokens" in r["erreur"].lower(), r
+    return {}
+
+
+def scenario_bootstrap_champs_absents():
+    r = _appeler_bootstrap({"gh_token": "a", "oauth_token": "b"})
+    assert not r["succes"], r
+    return {}
+
+
+def scenario_bootstrap_cle_publique_absente(tmp_path_factory):
+    tmp = tmp_path_factory()
+    ancien_cle = projet_ccw.CHEMIN_CLE_PUBLIQUE_CACHE
+    projet_ccw.CHEMIN_CLE_PUBLIQUE_CACHE = tmp / "n-existe-pas.pem"
+    try:
+        r = _appeler_bootstrap({"nom": "monprojet", "depot": "AlainDelree/MonProjet",
+                                 "topic": "bridge-monprojet",
+                                 "gh_token": "ghp_x", "oauth_token": "oauth_y"})
+        assert not r["succes"], r
+        assert "Rafraîchir la clé" in r["erreur"], r
+    finally:
+        projet_ccw.CHEMIN_CLE_PUBLIQUE_CACHE = ancien_cle
+    return {}
+
+
+def scenario_bootstrap_succes_complet(tmp_path_factory):
+    """Chemin complet, succès : les 2 issues sont créées (labels/corps
+    attendus, format CREATION parsable par watcher.py), la référence
+    croisée est postée sur l'issue CCL, et demarrer_watcher (best-effort)
+    est neutralisé — jamais un vrai sous-processus lancé pendant le test."""
+    tmp = tmp_path_factory()
+    bin_dir = _preparer_bin(tmp)
+    priv, pub = _generer_paire_cles(tmp / "cles")
+
+    ancien_path = os.environ.get("PATH", "")
+    ancien_cle = projet_ccw.CHEMIN_CLE_PUBLIQUE_CACHE
+    ancien_config_ba = projet_ccw._config_bridge_agent
+
+    log_create = tmp / "log_create.txt"
+    log_comment = tmp / "log_comment.txt"
+    compteur = tmp / "compteur.txt"
+    os.environ["TEST_559_LOG_CREATE"] = str(log_create)
+    os.environ["TEST_559_LOG_COMMENT"] = str(log_comment)
+    os.environ["TEST_559_COMPTEUR"] = str(compteur)
+    os.environ.pop("TEST_559_LISTE_OUVERTES", None)
+
+    import app.watchers as watchers_mod
+    ancien_demarrer = watchers_mod.demarrer_watcher
+    appels_demarrer = []
+    watchers_mod.demarrer_watcher = lambda cfg, forcer=False: (appels_demarrer.append(cfg.nom), (False, 0))[1]
+
+    try:
+        os.environ["PATH"] = f"{bin_dir}:{ancien_path}"
+        projet_ccw.CHEMIN_CLE_PUBLIQUE_CACHE = pub
+        cfg_ba = SimpleNamespace(depot="AlainDelree/Bridge_Agent", nom="bridge_agent")
+        projet_ccw._config_bridge_agent = lambda: cfg_ba
+
+        r = _appeler_bootstrap({
+            "nom": "monprojet", "depot": "AlainDelree/MonProjet",
+            "topic": "bridge-monprojet",
+            "gh_token": "ghp_secretGH", "oauth_token": "oauth_secretCC",
+        })
+        assert r["succes"], r
+        numero_ccl = r["issue_ccl_numero"]
+        numero_ccw = r["issue_ccw_numero"]
+        assert numero_ccw == numero_ccl + 1, r
+        assert r["issue_ccl_url"].endswith(f"/issues/{numero_ccl}"), r
+        assert r["issue_ccw_url"].endswith(f"/issues/{numero_ccw}"), r
+
+        contenu_create = log_create.read_text()
+        # Issue CCL : label for-linux, sans champ CREATION.
+        assert "LABEL=bridge,for-linux,mode_write" in contenu_create, contenu_create
+        # Issue CCW : label for-windows, avec le bloc CREATION complet.
+        assert "LABEL=bridge,for-windows,mode_write" in contenu_create, contenu_create
+        assert "CREATION_NOM_PROJET   | monprojet" in contenu_create, contenu_create
+        assert "CREATION_DEPOT        | AlainDelree/MonProjet" in contenu_create, contenu_create
+        assert "CREATION_TOPIC_NTFY   | bridge-monprojet" in contenu_create, contenu_create
+        # Les tokens en clair ne doivent JAMAIS apparaître dans le corps posté.
+        assert "ghp_secretGH" not in contenu_create, "token GH en clair dans le corps de l'issue"
+        assert "oauth_secretCC" not in contenu_create, "token OAuth en clair dans le corps de l'issue"
+
+        # Déchiffrement réel des valeurs CREATION_* extraites du corps loggé,
+        # pour vérifier que ce qui a été réellement chiffré/posté redonne les
+        # tokens d'origine via le déchiffrement déjà validé côté watcher.py.
+        bloc_ccw = contenu_create.split(f"=== create #{numero_ccw} ===", 1)[1]
+        champs = watcher.extraire_champs_creation(bloc_ccw)
+        assert watcher.dechiffrer_token_bootstrap(champs["CREATION_GH_TOKEN"], priv) == "ghp_secretGH"
+        assert watcher.dechiffrer_token_bootstrap(champs["CREATION_OAUTH_TOKEN"], priv) == "oauth_secretCC"
+
+        contenu_comment = log_comment.read_text()
+        assert f"=== comment on #{numero_ccl}" in contenu_comment, contenu_comment
+        assert f"#{numero_ccw}" in contenu_comment, contenu_comment
+
+        assert appels_demarrer == ["bridge_agent"], appels_demarrer
+    finally:
+        os.environ["PATH"] = ancien_path
+        for var in ("TEST_559_LOG_CREATE", "TEST_559_LOG_COMMENT", "TEST_559_COMPTEUR",
+                    "TEST_559_LISTE_OUVERTES"):
+            os.environ.pop(var, None)
+        projet_ccw.CHEMIN_CLE_PUBLIQUE_CACHE = ancien_cle
+        projet_ccw._config_bridge_agent = ancien_config_ba
+        watchers_mod.demarrer_watcher = ancien_demarrer
+    return {}
+
+
+def main():
+    tmp = tempfile.TemporaryDirectory()
+    compteur = {"n": 0}
+
+    def _tmp_path_factory():
+        compteur["n"] += 1
+        p = Path(tmp.name) / f"scenario{compteur['n']}"
+        p.mkdir(parents=True, exist_ok=True)
+        return p
+
+    tests = [
+        ("_chiffrer_token : aller-retour réel avec dechiffrer_token_bootstrap (#556)",
+         lambda: scenario_chiffrement_aller_retour_watcher(_tmp_path_factory)),
+        ("_chiffrer_token : mauvaise clé privée → RuntimeError (pas de résultat corrompu)",
+         lambda: scenario_chiffrement_mauvaise_cle_echoue(_tmp_path_factory)),
+        ("_corps_issue_ccw : parsable par watcher.creation_demandee/extraire_champs_creation",
+         scenario_corps_issue_ccw_parsable_par_watcher),
+        ("_corps_issue_ccl : référence script + doc + cross-référence", scenario_corps_issue_ccl_contenu),
+        ("_titre_issue_ccl/_titre_issue_ccw : déterministes par projet", scenario_titres_deterministes),
+        ("_creer_issue_gh : succès, numéro extrait de l'URL", lambda: scenario_creer_issue_gh_succes(_tmp_path_factory)),
+        ("_creer_issue_gh : anti-doublon, aucun gh issue create déclenché",
+         lambda: scenario_creer_issue_gh_anti_doublon(_tmp_path_factory)),
+        ("bootstrap_projet_ccw : tokens manquants → échec propre", scenario_bootstrap_tokens_manquants),
+        ("bootstrap_projet_ccw : nom/depot/topic absents → échec propre", scenario_bootstrap_champs_absents),
+        ("bootstrap_projet_ccw : clé publique absente du cache → échec propre",
+         lambda: scenario_bootstrap_cle_publique_absente(_tmp_path_factory)),
+        ("bootstrap_projet_ccw : chemin complet, succès (2 issues, format CREATION, cross-réf, watcher neutralisé)",
+         lambda: scenario_bootstrap_succes_complet(_tmp_path_factory)),
+    ]
+    echecs = 0
+    for nom, fn in tests:
+        try:
+            rap = fn()
+            print(f"  ✓ {nom}  ({rap})")
+        except AssertionError as e:
+            echecs += 1
+            print(f"  ✗ {nom}\n      {e}")
+        except Exception as e:  # noqa: BLE001
+            echecs += 1
+            print(f"  ✗ {nom} — erreur inattendue : {type(e).__name__}: {e}")
+
+    tmp.cleanup()
+    if echecs:
+        print(f"\n❌ {echecs} scénario(s) en échec.")
+        return 1
+    print("\n✅ Tous les scénarios passent.")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
