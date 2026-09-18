167c535

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 167c535
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 19:28:24 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #569 : onglet Git — worktrees actifs et commits non poussés, par projet
    
    Nouvelle route GET /git-etat (app/git_etat.py) et onglet dédié dans
    new_issue.py : pour chaque projet actif (lister_projets()), liste ses
    worktrees git secondaires (réutilise watcher.py::_lister_worktrees_secondaires,
    désormais paramétrée par rep_travail au lieu du seul CFG global) et ses
    commits locaux non poussés (git log --oneline @{u}..HEAD, best-effort).
    Lecture seule, chargé à l'ouverture de l'onglet comme CCW (pas de polling).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/__init__.py b/app/__init__.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 836803b..44893dc 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/__init__.py
# ── Version APRÈS ce commit.
+++ b/app/__init__.py
# ── Zone modifiée : ligne 85 (6 ligne(s)) dans l'ancienne version → ligne 85 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -85,6 +85,7 @@ def _enregistrer_routes(app: Flask) -> None:
     from app.diag_heartbeat import visibilite as diag_visibilite   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
     from app.son import get_son_actif, post_son_actif, tester_son
     from app.vues import index
+    from app.git_etat import etat_git
 
     app.add_url_rule("/login", "login", login, methods=["GET"])
     app.add_url_rule("/login", "login_post", login_post, methods=["POST"])
# ── Zone modifiée : ligne 154 (3 ligne(s)) dans l'ancienne version → ligne 155 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -154,3 +155,6 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/son-actif", "get_son_actif", login_requis(get_son_actif), methods=["GET"])
     app.add_url_rule("/son-actif", "post_son_actif", login_requis(post_son_actif), methods=["POST"])
     app.add_url_rule("/tester-son", "tester_son", login_requis(tester_son), methods=["POST"])
+    # ─── Onglet « Git » (issue #569) : worktrees actifs + commits non poussés,
+    # par projet, lecture seule ────────────────────────────────────────────
+    app.add_url_rule("/git-etat", "etat_git", login_requis(etat_git), methods=["GET"])
# (diff du fichier suivant)
diff --git a/app/git_etat.py b/app/git_etat.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..6197c2a
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/app/git_etat.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (64 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,64 @@
+"""Vue « Git » (issue #569) : worktrees actifs et commits locaux non poussés,
+par projet — lecture seule, aucune écriture git.
+
+Première brique d'une évolution plus large de Relecture_Bridge (résumé de
+diff, actions de merge) ; sert de fondation, sans dépendre des autres
+briques. Remplace la nécessité de lancer `git worktree list` et
+`git log --oneline @{u}..HEAD` à la main, projet par projet — dans le même
+esprit que l'alerte de log de `watcher.py::verifier_accumulation_worktrees`
+(issue #432), mais visible depuis l'interface plutôt que dans le seul log
+brut du watcher.
+"""
+
+import subprocess
+import sys
+from pathlib import Path
+
+from flask import jsonify
+
+# app.projets ajoute la racine du projet au sys.path lors de son import (pour
+# « from watcher import ») ; on l'importe donc avant watcher.
+from app.projets import lister_projets
+from app.auth import login_requis  # noqa: F401 (exporté pour l'enregistrement des routes)
+from watcher import _lister_worktrees_secondaires, _est_depot_git
+
+
+def commits_non_pousses(rep_travail: Path) -> list[str]:
+    """Liste (résumé oneline, du plus récent au plus ancien) les commits de
+    HEAD absents de la branche amont (`@{u}`) — équivalent de
+    `git log --oneline origin/master..HEAD`, mais basé sur l'amont réellement
+    configuré plutôt qu'un nom de branche figé (tous les projets ne
+    s'appellent pas forcément « master »).
+
+    Best-effort : dossier absent, pas un dépôt git, aucune amont configurée,
+    ou toute erreur d'exécution git → liste vide, jamais d'exception
+    propagée."""
+    if not rep_travail.is_dir() or not _est_depot_git(rep_travail):
+        return []
+    try:
+        res = subprocess.run(
+            ["git", "-C", str(rep_travail), "log", "--oneline", "@{u}..HEAD"],
+            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
+        )
+    except (OSError, subprocess.SubprocessError):
+        return []
+    if res.returncode != 0:
+        return []  # pas d'amont configurée, ou autre erreur — silence, best-effort
+    return [ligne for ligne in res.stdout.splitlines() if ligne.strip()]
+
+
+def etat_git():
+    """Retourne, pour chaque projet actif (`lister_projets()`) : ses
+    worktrees secondaires actifs (hors REP_TRAVAIL) et ses commits locaux non
+    poussés. Lecture seule (aucune commande git d'écriture)."""
+    resultat = []
+    for cfg in lister_projets():
+        worktrees = _lister_worktrees_secondaires(cfg.rep_travail)
+        commits   = commits_non_pousses(cfg.rep_travail)
+        resultat.append({
+            "nom":       cfg.nom,
+            "depot":     cfg.depot,
+            "worktrees": worktrees,
+            "commits":   commits,
+        })
+    return jsonify(projets=resultat)
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 208de7a..eab45a2 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 146 (7 ligne(s)) dans l'ancienne version → ligne 146 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -146,7 +146,7 @@ function appliquerAccentProjet(nom) {
 }
 
 function basculerOnglet(nom) {
-  const noms = ['creation', 'resultats', 'inbox', 'journal', 'config', 'watchers', 'ccw'];
+  const noms = ['creation', 'resultats', 'inbox', 'journal', 'config', 'watchers', 'git', 'ccw'];
   document.querySelectorAll('.onglet').forEach((o, i) =>
     o.classList.toggle('actif', noms[i] === nom));
   noms.forEach(n =>
# ── Zone modifiée : ligne 173 (6 ligne(s)) dans l'ancienne version → ligne 173 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -173,6 +173,10 @@ function basculerOnglet(nom) {
   // (chaque requête déclenche des appels SSH coûteux — l'utilisateur
   // rafraîchit à la demande via les boutons dédiés).
   if (nom === 'ccw') ccwOuvrirOnglet();
+  // Onglet « Git » (issue #569) : chargé à l'ouverture, PAS de polling
+  // automatique (une commande git par projet et par worktree à chaque appel) —
+  // même principe que l'onglet CCW ci-dessus, rafraîchi à la demande.
+  if (nom === 'git') chargerGitEtat();
   // Onglet « Résultats inbox » (issue #483) : rafraîchissement immédiat à
   // l'ouverture — le polling continu (rafraichirInbox, tout en bas de ce
   // fichier) garde le badge de l'onglet à jour même hors de cette vue.
# ── Zone modifiée : ligne 4685 (6 ligne(s)) dans l'ancienne version → ligne 4689 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4685,6 +4689,46 @@ async function chargerWatchers() {
   mettreAJourCompte();
 }
 
+// ─── Onglet « Git » (issue #569) : worktrees actifs + commits locaux non
+// poussés, par projet, lecture seule ────────────────────────────────────────
+async function chargerGitEtat() {
+  const corps = document.getElementById('git-corps-projets');
+  const msg   = document.getElementById('git-msg');
+  msg.textContent = 'Interrogation des dépôts…';
+  msg.className = 'message';
+  corps.innerHTML = '';
+  try {
+    const rep = await fetch('/git-etat');
+    const j   = await rep.json();
+    const projets = j.projets || [];
+    msg.textContent = '';
+    corps.innerHTML = projets.map(function(p) {
+      const worktreesHtml = p.worktrees.length === 0
+        ? '<span style="color:#aaa">aucun</span>'
+        : '<ul style="margin:4px 0 0 18px;padding:0">' + p.worktrees.map(function(w) {
+            return '<li>' + escapeHtml(w.chemin)
+              + (w.branche ? ' <span style="color:#888">(branche ' + escapeHtml(w.branche) + ')</span>' : '')
+              + '</li>';
+          }).join('') + '</ul>';
+      const commitsHtml = p.commits.length === 0
+        ? '<span style="color:#aaa">aucun</span>'
+        : '<ul style="margin:4px 0 0 18px;padding:0;font-family:monospace;font-size:12px">'
+          + p.commits.map(function(c) { return '<li>' + escapeHtml(c) + '</li>'; }).join('') + '</ul>';
+      return '<div style="padding:12px 0;border-bottom:1px solid #f0efe9">'
+        + '<div style="font-size:13px;font-weight:600">' + escapeHtml(p.nom)
+        + ' <span style="font-weight:400;color:#888">— ' + escapeHtml(p.depot) + '</span></div>'
+        + '<div style="margin-top:6px;font-size:12.5px">'
+        + '<b>Worktrees actifs (' + p.worktrees.length + ')</b>' + worktreesHtml + '</div>'
+        + '<div style="margin-top:8px;font-size:12.5px">'
+        + '<b>Commits non poussés (' + p.commits.length + ')</b>' + commitsHtml + '</div>'
+        + '</div>';
+    }).join('') || '<div style="color:#aaa;padding:12px 0">Aucun projet.</div>';
+  } catch (e) {
+    msg.textContent = 'Erreur réseau lors de la lecture de l\'état git.';
+    msg.className = 'message erreur';
+  }
+}
+
 function selectionnerTous(cb) {
   document.querySelectorAll('.cb-watcher').forEach(c => c.checked = cb.checked);
   mettreAJourCompte();
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 851ece8..76b0f5c 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 79 (6 ligne(s)) dans l'ancienne version → ligne 79 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -79,6 +79,7 @@
     <div class="onglet" onclick="basculerOnglet('journal')">Journal watcher</div>
     <div class="onglet" onclick="basculerOnglet('config')">Configuration</div>
     <div class="onglet" onclick="basculerOnglet('watchers')">Watchers</div>
+    <div class="onglet" onclick="basculerOnglet('git')">Git</div>
     <div class="onglet" onclick="basculerOnglet('ccw')">CCW</div>
   </div>
 
# ── Zone modifiée : ligne 375 (6 ligne(s)) dans l'ancienne version → ligne 376 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -375,6 +376,20 @@
     </div>
   </div>
 
+  <!-- ─── Onglet « Git » (issue #569) : worktrees actifs + commits locaux non
+       poussés, par projet — lecture seule, chargé à l'ouverture de l'onglet
+       (pas de polling automatique, comme l'onglet CCW : chaque rafraîchissement
+       lance des commandes git par projet). ──────────────────────────────── -->
+  <div id="panneau-git" class="panneau">
+    <div class="titre-section" style="display:flex;align-items:center">
+      <span>Worktrees et commits en attente de push, par projet</span>
+      <button onclick="chargerGitEtat()"
+              style="margin-left:auto;font-size:12px;padding:4px 10px">Rafraîchir</button>
+    </div>
+    <div id="git-msg" class="message"></div>
+    <div id="git-corps-projets"></div>
+  </div>
+
   <!-- ─── Onglet 3 : configuration ────────────────────────────────────── -->
   <div id="panneau-config" class="panneau">
 
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 2e3d7c4..37de8e0 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 760 (19 ligne(s)) dans l'ancienne version → ligne 760 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -760,19 +760,26 @@ def rafraichir_depot(rep: Path, dry_run: bool = False):
         log.warning(f"  [pull] échoué : {premiere} — poursuite sur le code local.")
 
 
-def _lister_worktrees_secondaires() -> list[dict]:
+def _lister_worktrees_secondaires(rep_travail: Path = None) -> list[dict]:
     """Liste les worktrees git du projet AUTRES que le worktree principal
-    (`CFG.rep_travail`) — les répertoires frères créés pour la
-    parallélisation mode_write (issue #337), via `git worktree list
-    --porcelain`. Chaque entrée : {"chemin": str, "branche": str}.
+    (`rep_travail`, par défaut `CFG.rep_travail`) — les répertoires frères
+    créés pour la parallélisation mode_write (issue #337), via `git worktree
+    list --porcelain`. Chaque entrée : {"chemin": str, "branche": str}.
+
+    Paramètre explicite (plutôt que le seul `CFG` global) depuis l'issue
+    #569 : permet à l'interface web (app/git_etat.py) de réutiliser cette
+    fonction pour lister les worktrees de N'IMPORTE QUEL projet, pas
+    seulement celui du watcher courant.
 
     Best-effort : dossier absent ou pas un dépôt git, ou toute erreur
     d'exécution git → liste vide, jamais d'exception propagée."""
-    if not CFG.rep_travail.is_dir() or not _est_depot_git(CFG.rep_travail):
+    if rep_travail is None:
+        rep_travail = CFG.rep_travail
+    if not rep_travail.is_dir() or not _est_depot_git(rep_travail):
         return []
     try:
         res = subprocess.run(
-            ["git", "-C", str(CFG.rep_travail), "worktree", "list", "--porcelain"],
+            ["git", "-C", str(rep_travail), "worktree", "list", "--porcelain"],
             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
         )
     except (OSError, subprocess.SubprocessError):
# ── Zone modifiée : ligne 796 (7 ligne(s)) dans l'ancienne version → ligne 803 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -796,7 +803,7 @@ def _lister_worktrees_secondaires() -> list[dict]:
     if courant:
         worktrees.append(courant)
 
-    principal = str(CFG.rep_travail.resolve())
+    principal = str(rep_travail.resolve())
     return [
         w for w in worktrees
         if w.get("chemin") and str(Path(w["chemin"]).resolve()) != principal
