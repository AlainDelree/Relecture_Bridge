94d2838

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 94d2838
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 12:37:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-485 : contrôle watcher issues_inbox (spool) depuis panneau Infrastructure

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/__init__.py b/app/__init__.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 12f1625..89746ae 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/__init__.py
# ── Version APRÈS ce commit.
+++ b/app/__init__.py
# ── Zone modifiée : ligne 78 (7 ligne(s)) dans l'ancienne version → ligne 78 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -78,7 +78,8 @@ def _enregistrer_routes(app: Flask) -> None:
     from app.interruption import route_interrompre, route_relancer
     from app.cycle_vie import heartbeat, events, quitter
     from app.fin_issue import notifier_fin_issue, stream_fin_issue
-    from app.issues_inbox import etat_inbox
+    from app.issues_inbox import (etat_inbox, demarrer_watcher_inbox_route,
+                                  arreter_watcher_inbox_route)
     from app.diag_heartbeat import visibilite as diag_visibilite   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
     from app.vues import index
 
# ── Zone modifiée : ligne 133 (4 ligne(s)) dans l'ancienne version → ligne 134 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -133,4 +134,7 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/stream", "stream_fin_issue", login_requis(stream_fin_issue))
     # ─── Onglet « Résultats inbox » (issue #483) : état du watcher_issues_inbox ─
     app.add_url_rule("/issues-inbox/etat", "etat_inbox", login_requis(etat_inbox))
+    # ─── Pilotage du watcher spool depuis #pl-zone-extras (issue #485) ────────
+    app.add_url_rule("/issues-inbox/demarrer-watcher", "demarrer_watcher_inbox_route", login_requis(demarrer_watcher_inbox_route), methods=["POST"])
+    app.add_url_rule("/issues-inbox/arreter-watcher", "arreter_watcher_inbox_route", login_requis(arreter_watcher_inbox_route), methods=["POST"])
     app.add_url_rule("/diag-visibilite", "diag_visibilite", diag_visibilite, methods=["POST"])   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
# (diff du fichier suivant)
diff --git a/app/issues_inbox.py b/app/issues_inbox.py
# (index — ignorable)
index e58a257..a960f19 100644
# (avant — fichier suivant)
--- a/app/issues_inbox.py
# (après — fichier suivant)
+++ b/app/issues_inbox.py
# ── Zone modifiée : ligne 1 (17 ligne(s)) dans l'ancienne version → ligne 1 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,17 +1,30 @@
-"""État de l'onglet « Résultats inbox » (issue #483).
+"""État de l'onglet « Résultats inbox » + pilotage du watcher spool (issues
+#483, #485).
 
 Lit l'état du watcher_issues_inbox (scripts/watcher_issues_inbox.py) UNIQUEMENT
-depuis le disque — aucun appel gh, aucune dépendance au watcher étant en cours
-d'exécution ou non. L'alarme visuelle de l'onglet est pilotée exclusivement par
-la présence de fichiers dans issues_inbox/rejected/ (pas de parsing de log, cf.
-tâche demandée de l'issue #483) ; l'historique des succès/rejets est une simple
-lecture informative de logs/issues_inbox.log, sans effet sur l'alarme.
+depuis le disque — aucun appel gh. L'alarme visuelle de l'onglet est pilotée
+exclusivement par la présence de fichiers dans issues_inbox/rejected/ (pas de
+parsing de log, cf. tâche demandée de l'issue #483) ; l'historique des succès/
+rejets est une simple lecture informative de logs/issues_inbox.log, sans effet
+sur l'alarme.
+
+Gestion du processus (issue #485) : même principe que chemin_pid/
+watcher_actif/demarrer_watcher/arreter_watcher de app/watchers.py, mais pour
+le watcher spool UNIQUE (pas de paramètre projet, un seul fichier PID). Le
+watcher spool n'a par défaut pas d'auto-extinction (contrairement aux watchers
+de projet, DELAI_INACTIVITE_MIN) : une durée optionnelle peut être choisie au
+démarrage (--duree-min), auto-extinction interne implémentée par le script
+lui-même (voir scripts/watcher_issues_inbox.py::boucle).
 """
 
+import os
+import signal
+import subprocess
 import sys
+import time
 from pathlib import Path
 
-from flask import jsonify
+from flask import jsonify, request
 
 DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
 sys.path.insert(0, str(DOSSIER_SCRIPT / "scripts"))
# ── Zone modifiée : ligne 22 (6 ligne(s)) dans l'ancienne version → ligne 35 (87 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -22,6 +35,87 @@ from watcher_issues_inbox import charger_config_inbox, DEFAUT_CHEMIN_CONFIG  # n
 # déjà borné à MAX_LOG_LINES par le watcher — cf. ConfigInbox.max_log_lines).
 LIGNES_HISTORIQUE_AFFICHEES = 50
 
+# Fichier PID : même convention que les watchers de projet (app/watchers.py::
+# chemin_pid), mais chemin fixe puisqu'il n'existe qu'UN watcher spool.
+CHEMIN_PID = DOSSIER_SCRIPT / "logs" / "watcher-issues_inbox.pid"
+# Échéance d'auto-extinction (epoch, écrite par demarrer_watcher_inbox() si une
+# durée a été choisie) — permet à l'interface d'afficher le temps restant sans
+# dépendre de l'horloge interne (monotone) du process watcher, qui tourne dans
+# un process séparé de Flask. Absente = watcher lancé « indéfiniment ».
+CHEMIN_ECHEANCE = DOSSIER_SCRIPT / "logs" / "watcher-issues_inbox.echeance"
+
+
+# ─── Gestion du processus ──────────────────────────────────────────────────
+
+def watcher_inbox_actif() -> tuple[bool, int | None]:
+    """Retourne (actif, pid) — même logique que app/watchers.py::watcher_actif."""
+    if not CHEMIN_PID.exists():
+        return False, None
+    try:
+        pid = int(CHEMIN_PID.read_text().strip())
+        os.kill(pid, 0)   # lève OSError si le processus est mort
+        return True, pid
+    except (OSError, ProcessLookupError, ValueError):
+        return False, None
+
+
+def _temps_restant_s():
+    """Secondes avant l'auto-extinction, ou None si aucune durée n'a été
+    fixée au démarrage (le watcher tourne indéfiniment)."""
+    if not CHEMIN_ECHEANCE.exists():
+        return None
+    try:
+        echeance = float(CHEMIN_ECHEANCE.read_text().strip())
+    except (OSError, ValueError):
+        return None
+    return max(0.0, echeance - time.time())
+
+
+def demarrer_watcher_inbox(duree_min: int = 0) -> tuple[bool, int]:
+    """Lance (ou relance) le watcher spool. Redémarre TOUJOURS s'il tourne
+    déjà — pas de refus silencieux (issue #485) : la nouvelle durée remplace
+    l'ancienne. duree_min=0 → tourne indéfiniment (comportement historique)."""
+    actif, pid_ancien = watcher_inbox_actif()
+    if actif and pid_ancien:
+        try:
+            os.kill(pid_ancien, signal.SIGTERM)
+            time.sleep(0.8)
+        except OSError:
+            pass
+
+    CHEMIN_PID.parent.mkdir(parents=True, exist_ok=True)
+    watcher_script = DOSSIER_SCRIPT / "scripts" / "watcher_issues_inbox.py"
+    cmd = [sys.executable, str(watcher_script)]
+    if duree_min > 0:
+        cmd += ["--duree-min", str(duree_min)]
+
+    proc = subprocess.Popen(
+        cmd,
+        stdout=subprocess.DEVNULL,
+        stderr=subprocess.DEVNULL,
+        start_new_session=True,
+    )
+    CHEMIN_PID.write_text(str(proc.pid))
+    if duree_min > 0:
+        CHEMIN_ECHEANCE.write_text(str(time.time() + duree_min * 60))
+    else:
+        CHEMIN_ECHEANCE.unlink(missing_ok=True)
+    return True, proc.pid
+
+
+def arreter_watcher_inbox() -> tuple[bool, str]:
+    """Arrête le watcher spool via SIGTERM. Retourne (succès, message)."""
+    actif, pid = watcher_inbox_actif()
+    if not actif:
+        return False, "watcher déjà inactif"
+    try:
+        os.kill(pid, signal.SIGTERM)
+        CHEMIN_PID.unlink(missing_ok=True)
+        CHEMIN_ECHEANCE.unlink(missing_ok=True)
+        return True, f"watcher arrêté (pid {pid})"
+    except OSError as e:
+        return False, str(e)
+
 
 def _config():
     """Relit configs/watcher_issues_inbox.conf à chaque appel (comme
# ── Zone modifiée : ligne 37 (6 ligne(s)) dans l'ancienne version → ligne 131 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -37,6 +131,9 @@ def etat_inbox():
       - rejetes    : [{nom, date}] triés du plus récent au plus ancien
       - historique : dernières lignes de logs/issues_inbox.log (plus récente
                      en premier), purement informatif
+      - watcher_actif, watcher_pid, watcher_restant_s : état du processus
+        watcher spool (issue #485) — restant_s = None si actif sans durée
+        fixée (indéfini) ou si inactif.
     """
     cfg = _config()
 
# ── Zone modifiée : ligne 60 (10 ligne(s)) dans l'ancienne version → ligne 157 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -60,10 +157,38 @@ def etat_inbox():
         except OSError:
             historique = []
 
+    actif, pid = watcher_inbox_actif()
+
     return jsonify(
         alarme=len(rejetes) > 0,
         rejetes=rejetes,
         historique=historique,
         inbox_dir=str(cfg.inbox_dir),
         rejected_dir=str(cfg.rejected_dir),
+        watcher_actif=actif,
+        watcher_pid=pid,
+        watcher_restant_s=_temps_restant_s() if actif else None,
     )
+
+
+def demarrer_watcher_inbox_route():
+    """Démarre (ou relance, si déjà actif) le watcher spool. JSON attendu :
+    {duree_min: N} — 0 ou absent = tourne indéfiniment."""
+    data = request.json or {}
+    try:
+        duree_min = int(data.get("duree_min") or 0)
+    except (TypeError, ValueError):
+        return jsonify(succes=False, erreur="duree_min invalide.")
+    if duree_min < 0:
+        return jsonify(succes=False, erreur="duree_min doit être positif ou nul.")
+    try:
+        _, pid = demarrer_watcher_inbox(duree_min)
+        return jsonify(succes=True, pid=pid, duree_min=duree_min)
+    except Exception as e:
+        return jsonify(succes=False, erreur=str(e))
+
+
+def arreter_watcher_inbox_route():
+    """Arrête le watcher spool."""
+    ok, msg = arreter_watcher_inbox()
+    return jsonify(succes=ok, message=msg)
# (diff du fichier suivant)
diff --git a/scripts/watcher_issues_inbox.py b/scripts/watcher_issues_inbox.py
# (index — ignorable)
index 418f7ac..1a7a473 100644
# (avant — fichier suivant)
--- a/scripts/watcher_issues_inbox.py
# (après — fichier suivant)
+++ b/scripts/watcher_issues_inbox.py
# ── Zone modifiée : ligne 51 (6 ligne(s)) dans l'ancienne version → ligne 51 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -51,6 +51,15 @@ log = logging.getLogger("watcher_issues_inbox")
 
 DEFAUT_CHEMIN_CONFIG = DOSSIER_SCRIPT / "configs" / "watcher_issues_inbox.conf"
 
+# Fichiers PID/échéance — mêmes chemins que app/issues_inbox.py::CHEMIN_PID /
+# CHEMIN_ECHEANCE (issue #485). Ce script ne les CRÉE jamais lui-même (c'est
+# le lanceur, app.issues_inbox.demarrer_watcher_inbox(), qui écrit le PID au
+# lancement — même logique que app/watchers.py::demarrer_watcher) ; il se
+# contente de les supprimer à sa propre auto-extinction, pour que l'interface
+# ne montre pas un PID orphelin.
+CHEMIN_PID      = DOSSIER_SCRIPT / "logs" / "watcher-issues_inbox.pid"
+CHEMIN_ECHEANCE = DOSSIER_SCRIPT / "logs" / "watcher-issues_inbox.echeance"
+
 
 @dataclass
 class ConfigInbox:
# ── Zone modifiée : ligne 423 (15 ligne(s)) dans l'ancienne version → ligne 432 (35 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -423,15 +432,35 @@ def configurer_logs() -> None:
     )
 
 
-def boucle(cfg: ConfigInbox, once: bool = False) -> None:
+def boucle(cfg: ConfigInbox, once: bool = False, duree_min: int = 0) -> None:
     cfg.inbox_dir.mkdir(parents=True, exist_ok=True)
     cfg.rejected_dir.mkdir(parents=True, exist_ok=True)
     log.info(f"watcher_issues_inbox démarré — {cfg.inbox_dir} "
               f"(intervalle {cfg.polling_interval}s, log max {cfg.max_log_lines} lignes)")
+
+    # Auto-extinction interne sur une durée fixe (issue #485), même principe
+    # que l'auto-extinction par inactivité de watcher.py (§20 du DOC) : à
+    # l'écoulement du délai, arrêt propre (sys.exit(0)) et suppression du
+    # fichier PID (+ échéance) pour que l'interface ne montre pas un PID
+    # orphelin. Horloge MONOTONE (comme watcher.py) : insensible à un
+    # changement d'heure système pendant que le watcher tourne.
+    if duree_min > 0:
+        log.info(f"Auto-extinction activée : arrêt après {duree_min} min (issue #485).")
+        echeance_monotone = time.monotonic() + duree_min * 60
+    else:
+        log.info("Auto-extinction désactivée (durée non fixée) — watcher permanent.")
+        echeance_monotone = None
+
     while True:
         traiter_dossier(cfg)
         if once:
             return
+        if echeance_monotone is not None and time.monotonic() >= echeance_monotone:
+            log.info(f"⏻ Auto-extinction : durée de {duree_min} min écoulée — "
+                      f"arrêt propre du watcher.")
+            CHEMIN_PID.unlink(missing_ok=True)
+            CHEMIN_ECHEANCE.unlink(missing_ok=True)
+            sys.exit(0)
         time.sleep(cfg.polling_interval)
 
 
# ── Zone modifiée : ligne 441 (11 ligne(s)) dans l'ancienne version → ligne 470 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -441,11 +470,13 @@ def main() -> None:
                         help="Chemin du .conf (optionnel — défauts sensés sinon)")
     parser.add_argument("--once", action="store_true",
                         help="Un seul cycle de traitement puis quitte (tests)")
+    parser.add_argument("--duree-min", type=int, default=0,
+                        help="Auto-extinction après ce délai en minutes (0/absent = désactivé, tourne indéfiniment ; issue #485)")
     args = parser.parse_args()
 
     configurer_logs()
     cfg = charger_config_inbox(Path(args.config))
-    boucle(cfg, once=args.once)
+    boucle(cfg, once=args.once, duree_min=args.duree_min)
 
 
 if __name__ == "__main__":
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 54e0e3a..cba2202 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1885 (8 ligne(s)) dans l'ancienne version → ligne 1885 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1885,8 +1885,9 @@ function arreterStreamFinIssue() {
 //    rendue, sélection ou non — pour garder l'infra sous les yeux en
 //    travaillant sur une issue (issue #377), une ligne par watcher, noir et
 //    blanc, bouton individuel Lancer/Relancer (issue #380) ;
-//  - zone médiane (#pl-zone-extras) : réservée aux futurs boutons, vide,
-//    voir templates/index.html (issue #380) ;
+//  - zone médiane (#pl-zone-extras) : réservée aux futurs boutons (issue
+//    #380), occupée depuis l'issue #485 par le contrôle du watcher spool
+//    (issues_inbox) — rendrePanneauLateralExtras(), fetch /issues-inbox/etat ;
 //  - zone basse (#pl-zone-actions) : actions contextuelles pour le projet/
 //    l'issue sélectionnés (rendrePanneauLateralActions), sans fetch réseau
 //    (données déjà en mémoire : listeIssuesResultats + ccwProjetsConnus) —
# ── Zone modifiée : ligne 1939 (6 ligne(s)) dans l'ancienne version → ligne 1940 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1939,6 +1940,7 @@ async function rafraichirPanneauLateralResultats() {
   // rafraîchit toujours, les actions contextuelles se (re)rendent — ou se
   // vident — selon la sélection courante, sans attendre le fetch du monitoring.
   await rendrePanneauLateralMonitoring();
+  await rendrePanneauLateralExtras();
   rendrePanneauLateralActions();
 }
 
# ── Zone modifiée : ligne 2096 (6 ligne(s)) dans l'ancienne version → ligne 2098 (120 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2096,6 +2098,120 @@ async function rendrePanneauLateralMonitoring() {
   zone.innerHTML = html;
 }
 
+// Zone réservée #pl-zone-extras (issue #380), occupée depuis l'issue #485 par
+// le contrôle du watcher spool issues_inbox (scripts/watcher_issues_inbox.py)
+// — un seul watcher, pas de paramètre projet, contrairement aux watchers CCL
+// de #pl-zone-monitoring. Fetch dédié /issues-inbox/etat (même route que
+// l'onglet « Résultats inbox », étendue par l'issue #485 avec watcher_actif/
+// watcher_pid/watcher_restant_s). Contrairement aux watchers CCL, un bouton
+// « Arrêter » explicite est affiché : le watcher spool n'a par défaut aucune
+// auto-extinction (« Indéfiniment »), il doit pouvoir être coupé à tout
+// moment.
+async function rendrePanneauLateralExtras() {
+  const zone = document.getElementById('pl-zone-extras');
+  if (!zone) return;
+  let etat = null;
+  try {
+    const rep = await fetch('/issues-inbox/etat');
+    etat = await rep.json();
+  } catch(e) { etat = null; }
+  if (!etat) { zone.innerHTML = ''; return; }
+
+  const actif = !!etat.watcher_actif;
+  let html = '<div class="pl-resume-titre">Watcher spool</div>';
+  html += '<div class="pl-ligne"><span class="pl-ligne-libelle">'
+        + (actif ? '🟢' : '⚫') + ' Watcher spool (issues_inbox)</span>'
+        + '<button class="pl-btn-mini" onclick="sidebarOuvrirDureeWatcherInbox()">'
+        + (actif ? '↺ Relancer' : '▶ Démarrer') + '</button>'
+        + '</div>';
+  if (actif) {
+    const restant = (etat.watcher_restant_s === null || etat.watcher_restant_s === undefined)
+      ? 'indéfini' : formaterDureeRestante(etat.watcher_restant_s);
+    html += '<div class="pl-sous-projet">Extinction : ' + restant + '</div>';
+    html += '<div class="pl-boutons-ccl">'
+          + '<button class="pl-btn-vm" onclick="sidebarArreterWatcherInbox(this)">⏹ Arrêter</button>'
+          + '</div>';
+  }
+  zone.innerHTML = html;
+}
+
+// Formate un nombre de secondes restant avant auto-extinction en « Xh0Y » /
+// « Y min » (arrondi à la minute supérieure — jamais « 0 min » tant qu'il
+// reste du temps, cohérent avec un compte à rebours affiché toutes les 30s).
+function formaterDureeRestante(secondes) {
+  const totalMin = Math.max(1, Math.ceil(secondes / 60));
+  const h = Math.floor(totalMin / 60);
+  const m = totalMin % 60;
+  return h > 0 ? (h + 'h' + String(m).padStart(2, '0')) : (m + ' min');
+}
+
+// Ouvre le choix de durée (modal-duree-watcher-inbox, issue #485) avant tout
+// démarrage/relance du watcher spool — remis à « Indéfiniment » à chaque
+// ouverture, pour ne jamais reproposer silencieusement un choix précédent.
+function sidebarOuvrirDureeWatcherInbox() {
+  const overlay = document.getElementById('modal-duree-watcher-inbox');
+  if (!overlay) return;
+  const radioIndef = document.getElementById('dwi-indefini');
+  if (radioIndef) radioIndef.checked = true;
+  const champMin = document.getElementById('dwi-minutes');
+  if (champMin) champMin.value = '';
+  overlay.classList.add('actif');
+}
+
+function sidebarFermerDureeWatcherInbox() {
+  const overlay = document.getElementById('modal-duree-watcher-inbox');
+  if (overlay) overlay.classList.remove('actif');
+}
+
+// Lit le choix de durée du modal puis démarre (ou relance) le watcher spool
+// via POST /issues-inbox/demarrer-watcher — le serveur redémarre TOUJOURS s'il
+// tourne déjà (issue #485 : pas de refus silencieux, la nouvelle durée
+// remplace l'ancienne, quel que soit l'état courant).
+async function sidebarConfirmerDureeWatcherInbox(btn) {
+  const choix = document.querySelector('input[name="dwi-choix"]:checked');
+  let dureeMin = 0;
+  if (choix && choix.value === '30') {
+    dureeMin = 30;
+  } else if (choix && choix.value === 'perso') {
+    const champ = document.getElementById('dwi-minutes');
+    dureeMin = parseInt(champ ? champ.value : '', 10);
+    if (!Number.isFinite(dureeMin) || dureeMin <= 0) {
+      alert('Indiquez un nombre de minutes valide (> 0).');
+      return;
+    }
+  }
+  const label = btn ? btn.textContent : null;
+  if (btn) { btn.disabled = true; btn.textContent = 'Démarrage…'; }
+  try {
+    await fetch('/issues-inbox/demarrer-watcher', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({duree_min: dureeMin})
+    });
+  } catch(e) {
+    alert('Erreur réseau : ' + e.message);
+  }
+  if (btn) { btn.disabled = false; if (label !== null) btn.textContent = label; }
+  sidebarFermerDureeWatcherInbox();
+  await rafraichirPanneauLateralResultats();
+}
+
+// Arrête le watcher spool (bouton explicite, issue #485 — à la différence des
+// watchers CCL de projet, ce watcher n'a par défaut aucune auto-extinction,
+// il doit donc pouvoir être coupé manuellement à tout moment).
+async function sidebarArreterWatcherInbox(btn) {
+  if (!confirm('Arrêter le watcher spool (issues_inbox) ?')) return;
+  const label = btn ? btn.textContent : null;
+  if (btn) { btn.disabled = true; btn.textContent = 'Arrêt…'; }
+  try {
+    await fetch('/issues-inbox/arreter-watcher', {method: 'POST'});
+  } catch(e) {
+    alert('Erreur réseau : ' + e.message);
+  }
+  if (btn) { btn.disabled = false; if (label !== null) btn.textContent = label; }
+  await rafraichirPanneauLateralResultats();
+}
+
 // Actions contextuelles (issue #375, zone basse fixe depuis #377) : projet/
 // issue actuellement sélectionnés (projetCourant/numeroCourant). Aucun fetch
 // réseau — les données viennent de listeIssuesResultats (déjà en mémoire) et
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index d2fe6e9..9fc5ddc 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 275 (9 ligne(s)) dans l'ancienne version → ligne 275 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -275,9 +275,9 @@
          - #pl-zone-monitoring : monitoring de l'infrastructure, TOUJOURS
            visible, une ligne par watcher CCL/service CCW (VM CCW, watchers
            CCL, services CCW).
-         - #pl-zone-extras : zone réservée aux futurs boutons (issue #380) —
-           volontairement vide, prête à accueillir de nouveaux boutons sans
-           restructurer le panneau. NE PAS remplir dans cette issue.
+         - #pl-zone-extras : zone réservée aux futurs boutons (issue #380),
+           occupée depuis l'issue #485 par le contrôle du watcher spool
+           (issues_inbox) — rendrePanneauLateralExtras() (static/js/app.js).
          - #pl-zone-actions : actions contextuelles sur l'issue sélectionnée,
            vide (donc invisible) tant qu'aucune ligne n'est sélectionnée. -->
     <div id="panneau-lateral-resultats" class="panneau-lateral">
# ── Zone modifiée : ligne 651 (6 ligne(s)) dans l'ancienne version → ligne 651 (35 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -651,6 +651,35 @@
   </div>
 </div>
 
+<!-- ─── Modal « Durée du watcher spool » (issue #485) ─────────────────────────
+     Ouverte au clic sur Démarrer/Relancer dans #pl-zone-extras
+     (sidebarOuvrirDureeWatcherInbox) : choix par case à cocher (radio) de la
+     durée avant auto-extinction du watcher — Indéfiniment (défaut),
+     30 min, ou un nombre de minutes libre. Transmis à POST
+     /issues-inbox/demarrer-watcher (sidebarConfirmerDureeWatcherInbox). -->
+<div id="modal-duree-watcher-inbox" class="modal-overlay">
+  <div class="modal-carte" style="max-width:420px">
+    <div class="modal-titre" id="dwi-titre">▶ Démarrer le watcher spool (issues_inbox)</div>
+    <label style="display:block;margin-bottom:10px;font-size:13px;color:#333">
+      <input type="radio" name="dwi-choix" id="dwi-indefini" value="indefini" checked>
+      Indéfiniment
+    </label>
+    <label style="display:block;margin-bottom:10px;font-size:13px;color:#333">
+      <input type="radio" name="dwi-choix" value="30">
+      30 min
+    </label>
+    <label style="display:block;margin-bottom:14px;font-size:13px;color:#333">
+      <input type="radio" name="dwi-choix" value="perso">
+      Choix en minutes :
+      <input type="number" id="dwi-minutes" min="1" step="1" style="width:70px;margin-left:6px">
+    </label>
+    <div class="modal-boutons">
+      <button id="dwi-annuler" onclick="sidebarFermerDureeWatcherInbox()">Annuler</button>
+      <button class="primaire" id="dwi-confirmer" onclick="sidebarConfirmerDureeWatcherInbox(this)">Confirmer</button>
+    </div>
+  </div>
+</div>
+
 <!-- ─── Overlay « serveur arrêté » ────────────────────────────────────────── -->
 <div id="overlay-arret" class="overlay-arret">
   <div class="msg">🔴 Serveur arrêté — relancez new_issue.py puis rechargez</div>
