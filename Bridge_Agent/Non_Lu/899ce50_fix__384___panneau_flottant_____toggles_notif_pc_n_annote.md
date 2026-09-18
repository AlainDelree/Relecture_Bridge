899ce50

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 899ce50
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 6 18:10:25 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #384 : panneau flottant — toggles notif_pc/notif_gsm/notif_tous sur l'issue sélectionnée

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 87cf45e..f093999 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (31 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,31 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 6 août 2026 — issue #384
+
+Panneau flottant actions : toggles `notif_pc`/`notif_gsm`/`notif_tous` sur
+l'issue sélectionnée, sans passer par GitHub — ces labels peuvent être
+modifiés pendant le traitement, le watcher les relit au moment de la
+clôture.
+- Nouvelle route `POST /modifier-label-notif` (`app/issues.py`,
+  `modifier_label_notif`) : `gh issue edit --add-label`/`--remove-label`
+  selon `actif`, whitelist stricte sur `notif_pc`/`notif_gsm`/`notif_tous`
+  (constantes `LABEL_NOTIF_*` de `watcher.py`, réutilisées telles quelles) —
+  aucun autre label ne peut être modifié via cette route. Protégée par
+  `login_requis`, enregistrée dans `app/__init__.py`.
+- `rendrePanneauLateralActions()` (`static/js/app.js`) : bloc « 🔔
+  Notifications » (3 checkboxes) inséré sous le mode de l'issue, affiché
+  seulement si l'issue est interrompible (ouverte, ni `done` ni
+  `needs-human` — même condition que les boutons d'interruption). État
+  initial coché/décoché lu depuis `listeIssuesResultats`. Au clic :
+  appel `/modifier-label-notif`, mise à jour locale de
+  `listeIssuesResultats` + re-rendu du panneau si succès ; en cas
+  d'échec, la checkbox revient à son état précédent et un message
+  d'erreur discret (`#pl-notif-erreur`, sans `alert()`) s'affiche puis
+  s'efface après 4 s.
+- CSS : `.pl-notifs`/`.pl-notifs-titre`/`.pl-notif-ligne`/`.pl-notif-erreur`
+  (`static/css/style.css`).
+
 ## 6 août 2026 — issue #383
 
 Correctif suite #381/#382 : les pastilles de notification des boutons de
# (diff du fichier suivant)
diff --git a/app/__init__.py b/app/__init__.py
# (index — ignorable)
index 88fc6e5..3d63717 100644
# (avant — fichier suivant)
--- a/app/__init__.py
# (après — fichier suivant)
+++ b/app/__init__.py
# ── Zone modifiée : ligne 66 (7 ligne(s)) dans l'ancienne version → ligne 66 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -66,7 +66,8 @@ def _enregistrer_routes(app: Flask) -> None:
                               arreter_watcher_route, statut)
     from app.issues import (apercu, envoyer, issues_liste, issue_detail,
                             diff_commit, issues_en_attente, annuler_issue,
-                            fermer_issue, joindre_image, recherche_issues)
+                            fermer_issue, joindre_image, recherche_issues,
+                            modifier_label_notif)
     from app.templates import (templates_liste, templates_sauvegarder,
                                templates_supprimer)
     from app.journal import journal
# ── Zone modifiée : ligne 99 (6 ligne(s)) dans l'ancienne version → ligne 100 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -99,6 +100,7 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/issues-en-attente/<nom_projet>", "issues_en_attente", login_requis(issues_en_attente))
     app.add_url_rule("/annuler-issue/<nom_projet>/<numero>", "annuler_issue", login_requis(annuler_issue), methods=["POST"])
     app.add_url_rule("/fermer-issue/<nom_projet>/<numero>", "fermer_issue", login_requis(fermer_issue), methods=["POST"])
+    app.add_url_rule("/modifier-label-notif", "modifier_label_notif", login_requis(modifier_label_notif), methods=["POST"])
     app.add_url_rule("/config/<nom_projet>", "get_config", login_requis(get_config), methods=["GET"])
     app.add_url_rule("/config/<nom_projet>", "post_config", login_requis(post_config), methods=["POST"])
     app.add_url_rule("/nouveau-projet/verifier", "verifier_nouveau_projet", login_requis(verifier_nouveau_projet), methods=["GET"])
# (diff du fichier suivant)
diff --git a/app/issues.py b/app/issues.py
# (index — ignorable)
index f1b427b..db34f7d 100644
# (avant — fichier suivant)
--- a/app/issues.py
# (après — fichier suivant)
+++ b/app/issues.py
# ── Zone modifiée : ligne 24 (7 ligne(s)) dans l'ancienne version → ligne 24 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,7 +24,8 @@ from app.auth import login_requis  # noqa: F401 (exporté pour l'enregistrement
 # du watcher fonctionne. On réutilise ses primitives pour éviter toute dérive
 # entre le calcul du watcher et celui du badge (issues #91 et #106).
 from watcher import (est_titre_chef, deduire_type_issue, PAUSE_ENTRE_TENTATIVES,
-                     _est_depot_git, LABEL_ECRITURE, LABEL_SCRATCH)
+                     _est_depot_git, LABEL_ECRITURE, LABEL_SCRATCH,
+                     LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS)
 
 # Racine du projet (dossier parent du package app/).
 DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
# ── Zone modifiée : ligne 1034 (6 ligne(s)) dans l'ancienne version → ligne 1035 (54 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1034,6 +1035,54 @@ def annuler_issue(nom_projet, numero):
         return jsonify(succes=False, message=str(e))
 
 
+# ─── Toggle des labels de notification depuis le panneau flottant (issue #384) ─
+# Les labels notif_pc/notif_gsm/notif_tous peuvent être modifiés en cours de
+# traitement — le watcher les relit au moment de la clôture (voir LABEL_NOTIF_*
+# dans watcher.py). Cette route permet de les basculer sans passer par GitHub.
+# Whitelist STRICTE : aucun autre label ne peut être posé/retiré via cette route.
+LABELS_NOTIF_AUTORISES = {LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS}
+
+
+def modifier_label_notif():
+    """Pose ou retire un label de notification (notif_pc/notif_gsm/notif_tous)
+    sur une issue GitHub, depuis le panneau flottant d'actions.
+
+    Paramètres JSON : projet, numero, label, actif (bool). Retourne
+    {succes: true} ou {succes: false, erreur: ...}."""
+    data       = request.json or {}
+    nom_projet = (data.get("projet") or "").strip()
+    numero     = data.get("numero")
+    label      = (data.get("label") or "").strip()
+    actif      = bool(data.get("actif"))
+
+    cfg = projet_par_nom(nom_projet)
+    if not cfg:
+        return jsonify(succes=False, erreur="Projet introuvable.")
+    if not str(numero).isdigit():
+        return jsonify(succes=False, erreur="Numéro d'issue invalide.")
+    if label not in LABELS_NOTIF_AUTORISES:
+        return jsonify(succes=False, erreur=f"Label non autorisé : « {label} ».")
+
+    option = "--add-label" if actif else "--remove-label"
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "edit", str(numero),
+             "--repo", cfg.depot,
+             option,   label],
+            capture_output=True, text=True, timeout=30
+        )
+        if res.returncode == 0:
+            return jsonify(succes=True)
+        return jsonify(succes=False,
+                       erreur=res.stderr.strip() or "Erreur inconnue de gh.")
+    except subprocess.TimeoutExpired:
+        return jsonify(succes=False, erreur="Timeout (gh n'a pas répondu en 30s).")
+    except FileNotFoundError:
+        return jsonify(succes=False, erreur="gh introuvable dans le PATH.")
+    except Exception as e:
+        return jsonify(succes=False, erreur=str(e))
+
+
 def fermer_issue(nom_projet, numero):
     """Ferme définitivement une issue en échec (label needs-human).
 
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index aac0c97..56278c4 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 334 (6 ligne(s)) dans l'ancienne version → ligne 334 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -334,6 +334,12 @@ button.danger:hover{background:#f8d7da}
 .pl-sep{border:none;border-top:1px solid #e0dfda;margin:14px 0}
 .pl-actions{display:flex;flex-direction:column;gap:8px}
 .pl-actions button{width:100%}
+/* Toggles notif_pc/notif_gsm/notif_tous de l'issue sélectionnée (issue #384). */
+.pl-notifs{margin-bottom:10px}
+.pl-notifs-titre{font-size:13px;font-weight:600;color:#1a1a18;margin-bottom:4px}
+.pl-notif-ligne{display:block;font-size:13px;color:#1a1a18;padding:2px 0;cursor:pointer}
+.pl-notif-ligne input{margin-right:6px}
+.pl-notif-erreur{font-size:12px;color:#b3261e;min-height:14px;margin-top:2px}
 .issue-body{background:#f8f8f5;border:1px solid #e0dfda;border-radius:6px;padding:12px;
   font-family:monospace;font-size:12px;white-space:pre-wrap;word-break:break-word;
   max-height:200px;overflow-y:auto;line-height:1.6;margin-bottom:16px}
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 5ba6560..b8d5554 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2096 (6 ligne(s)) dans l'ancienne version → ligne 2096 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2096,6 +2096,19 @@ function rendrePanneauLateralActions() {
   if (it) {
     html += '<div class="pl-mode-issue">' + libelleModeIssue(nomsLabels) + '</div>';
   }
+  // Toggles des labels de notification (issue #384) : mêmes conditions que les
+  // boutons d'interruption (issue ouverte, ni done ni needs-human) — pas de
+  // notification à reconfigurer sur une issue déjà terminée. État initial
+  // coché/décoché reflète les labels actuels de l'issue (listeIssuesResultats).
+  if (interromptible) {
+    html += '<div class="pl-notifs">'
+          + '<div class="pl-notifs-titre">🔔 Notifications</div>'
+          + rendreCheckboxNotif(nom, numero, 'notif_pc',   'Bureau', nomsLabels)
+          + rendreCheckboxNotif(nom, numero, 'notif_gsm',  'GSM',    nomsLabels)
+          + rendreCheckboxNotif(nom, numero, 'notif_tous', 'Tous',   nomsLabels)
+          + '<div id="pl-notif-erreur" class="pl-notif-erreur"></div>'
+          + '</div>';
+  }
   html += '<div class="pl-actions">'
         + '<button onclick="sidebarRelancerWatcherCCL(\'' + escapeHtml(nom) + '\', this)">'
         + '↺ Relancer watcher CCL</button>';
# ── Zone modifiée : ligne 2125 (6 ligne(s)) dans l'ancienne version → ligne 2138 (73 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2125,6 +2138,73 @@ function rendrePanneauLateralActions() {
   zone.innerHTML = html;
 }
 
+// Une ligne « ☐ Libellé » du bloc Notifications (issue #384). Coché si `label`
+// (ex. notif_pc) figure parmi les labels actuels de l'issue (nomsLabels, déjà
+// en minuscules — voir rendrePanneauLateralActions).
+function rendreCheckboxNotif(nom, numero, label, libelle, nomsLabels) {
+  const coche = nomsLabels.includes(label) ? ' checked' : '';
+  return '<label class="pl-notif-ligne">'
+       + '<input type="checkbox"' + coche + ' onchange="toggleLabelNotif(\''
+       + escapeHtml(nom) + '\', ' + Number(numero) + ', \'' + label + '\', this)"> '
+       + escapeHtml(libelle) + '</label>';
+}
+
+// Bascule un label de notification (notif_pc/notif_gsm/notif_tous) sur l'issue
+// sélectionnée via /modifier-label-notif (issue #384), sans passer par GitHub.
+// En cas d'échec (réseau ou refus serveur) : la checkbox revient à son état
+// précédent et un message d'erreur discret s'affiche brièvement sous les
+// toggles, sans bloquer l'interface (pas d'alert()).
+async function toggleLabelNotif(nom, numero, label, cb) {
+  const actif = cb.checked;
+  cb.disabled = true;
+  let ok = false, erreur = '';
+  try {
+    const rep = await fetch('/modifier-label-notif', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({projet: nom, numero: numero, label: label, actif: actif})
+    });
+    const json = await rep.json();
+    ok = !!json.succes;
+    if (!ok) erreur = json.erreur || 'échec de la mise à jour du label.';
+  } catch(e) {
+    erreur = 'Erreur réseau : ' + e.message;
+  }
+  cb.disabled = false;
+  if (!ok) {
+    cb.checked = !actif;
+    afficherErreurNotifDiscrete(erreur);
+    return;
+  }
+  // Mise à jour locale de listeIssuesResultats (sans refetch réseau), puis
+  // re-rendu du panneau d'actions pour rester cohérent avec l'état affiché
+  // ailleurs (ex. si un autre widget lit aussi les labels de cette issue).
+  const it = listeIssuesResultats.find(
+    x => x.projet === nom && String(x.number) === String(numero));
+  if (it) {
+    const dejaPresent = (it.labels || []).some(
+      l => ((l && l.name) || l || '').toLowerCase() === label);
+    if (actif && !dejaPresent) {
+      it.labels = (it.labels || []).concat([{name: label}]);
+    } else if (!actif && dejaPresent) {
+      it.labels = (it.labels || []).filter(
+        l => ((l && l.name) || l || '').toLowerCase() !== label);
+    }
+  }
+  rendrePanneauLateralActions();
+}
+
+// Message d'erreur discret (pas d'alert()) sous les toggles de notification —
+// s'efface tout seul après quelques secondes.
+function afficherErreurNotifDiscrete(message) {
+  const zone = document.getElementById('pl-notif-erreur');
+  if (!zone) return;
+  zone.textContent = '⚠ ' + message;
+  setTimeout(function() {
+    if (zone.textContent === '⚠ ' + message) zone.textContent = '';
+  }, 4000);
+}
+
 // Relance (ou lance) le watcher CCL du projet donné — même endpoint que
 // l'onglet Watchers (actionWatchers → /lancer-watcher), appelé ici pour un
 // seul projet directement depuis le panneau latéral.
