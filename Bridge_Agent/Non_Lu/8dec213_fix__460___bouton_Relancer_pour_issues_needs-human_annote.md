8dec213

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8dec213
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 20:19:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #460 : bouton Relancer pour issues needs-human (panneau Infrastructure)
    
    - app/interruption.py : _retirer_label_gh() + route_relancer() (POST
      /relancer-issue) — retire needs-human et poste un commentaire de trace.
      Pas de label pending posé : ce label n'existe pas dans ce projet, une
      issue ouverte sans needs-human/done est déjà éligible au watcher.
    - app/__init__.py : enregistrement de la route /relancer-issue.
    - static/js/app.js : bouton 🔄 Relancer dans rendrePanneauLateralActions()
      (panneau flottant Infrastructure), visible uniquement si needs-human et
      issue ouverte ; fonction relancerIssue() (confirm + fetch + rafraîchissement).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/__init__.py b/app/__init__.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8a8cd1b..40766e4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/__init__.py
# ── Version APRÈS ce commit.
+++ b/app/__init__.py
# ── Zone modifiée : ligne 75 (7 ligne(s)) dans l'ancienne version → ligne 75 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -75,7 +75,7 @@ def _enregistrer_routes(app: Flask) -> None:
                          ccw_ajouter_projet, ccw_finaliser_projet,
                          ccw_redemarrer_projet, ccw_demarrer_projet,
                          ccw_arreter_projet, ccw_nettoyer_verrous)
-    from app.interruption import route_interrompre
+    from app.interruption import route_interrompre, route_relancer
     from app.cycle_vie import heartbeat, events, quitter
     from app.fin_issue import notifier_fin_issue, stream_fin_issue
     from app.diag_heartbeat import visibilite as diag_visibilite   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
# ── Zone modifiée : ligne 120 (6 ligne(s)) dans l'ancienne version → ligne 120 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -120,6 +120,7 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/ccw/nettoyer-verrous", "ccw_nettoyer_verrous", login_requis(ccw_nettoyer_verrous), methods=["POST"])
     # ─── Interruption ciblée d'une issue en cours (issue #323, suite #320) ────
     app.add_url_rule("/interrompre", "route_interrompre", login_requis(route_interrompre), methods=["POST"])
+    app.add_url_rule("/relancer-issue", "route_relancer", login_requis(route_relancer), methods=["POST"])
     app.add_url_rule("/heartbeat", "heartbeat", heartbeat, methods=["POST"])
     app.add_url_rule("/events", "events", login_requis(events))
     app.add_url_rule("/quitter", "quitter", login_requis(quitter), methods=["POST"])
# (diff du fichier suivant)
diff --git a/app/interruption.py b/app/interruption.py
# (index — ignorable)
index 95a8d60..66a499a 100644
# (avant — fichier suivant)
--- a/app/interruption.py
# (après — fichier suivant)
+++ b/app/interruption.py
# ── Zone modifiée : ligne 44 (6 ligne(s)) dans l'ancienne version → ligne 44 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -44,6 +44,7 @@ from watcher import _chemin_verrou, DOSSIER_LOGS  # noqa: E402
 
 LABEL_NEEDS_HUMAN         = "needs-human"
 COMMENTAIRE_INTERRUPTION  = "⛔ Interrompu via new_issue.py"
+COMMENTAIRE_RELANCE       = "🔄 Relancée via new_issue.py (retrait de needs-human)."
 
 # Étapes dont un échec rend le statut global 'echec_critique' (arbre de
 # process non confirmé mort → lock volontairement non nettoyé, risque de
# ── Zone modifiée : ligne 70 (6 ligne(s)) dans l'ancienne version → ligne 71 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -70,6 +71,23 @@ def _ajouter_label_gh(depot: str, numero: int, label: str) -> tuple[str, str]:
         return "echec", str(e)
 
 
+def _retirer_label_gh(depot: str, numero: int, label: str) -> tuple[str, str]:
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "edit", str(numero), "--repo", depot, "--remove-label", label],
+            capture_output=True, text=True, timeout=30,
+        )
+        if res.returncode == 0:
+            return "succes", f"Label « {label} » retiré."
+        return "echec", (res.stderr or res.stdout or "erreur gh inconnue").strip()
+    except subprocess.TimeoutExpired:
+        return "echec", "Timeout (gh n'a pas répondu en 30s)."
+    except FileNotFoundError:
+        return "echec", "gh introuvable dans le PATH."
+    except Exception as e:
+        return "echec", str(e)
+
+
 def _commenter_gh(depot: str, numero: int, message: str) -> tuple[str, str]:
     try:
         res = subprocess.run(
# ── Zone modifiée : ligne 422 (3 ligne(s)) dans l'ancienne version → ligne 440 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -422,3 +440,34 @@ def route_interrompre():
 
     reponse = dict(succes=True, agent=agent, statut_global=statut_global, etapes=etapes)
     return jsonify(**reponse)
+
+
+def route_relancer():
+    """POST /relancer-issue — remet en file d'attente une issue bloquée en
+    needs-human (issue #460), sans recréer une nouvelle issue.
+
+    Il n'existe PAS de label « pending » dans ce projet : le watcher
+    (watcher.py) traite déjà toute issue OUVERTE for-linux/for-windows tant
+    qu'elle ne porte ni `done` ni `needs-human` (voir LABEL_ECHEC/LABEL_FAIT
+    dans watcher.py) — retirer needs-human suffit donc à la rendre de nouveau
+    éligible au prochain cycle. Ne relance PAS le watcher lui-même (même
+    esprit que route_interrompre ci-dessus : action manuelle séparée si le
+    watcher est éteint)."""
+    data   = request.json or {}
+    depot  = (data.get("depot") or "").strip()
+    numero = data.get("numero")
+
+    if not depot:
+        return jsonify(succes=False, erreur="Dépôt GitHub manquant."), 400
+    if not str(numero).isdigit():
+        return jsonify(succes=False, erreur="Numéro d'issue invalide."), 400
+    numero = int(numero)
+
+    statut_label, msg_label = _retirer_label_gh(depot, numero, LABEL_NEEDS_HUMAN)
+    etapes = [{"etape": "retrait_label_needs_human", "statut": statut_label, "message": msg_label}]
+
+    statut_comment, msg_comment = _commenter_gh(depot, numero, COMMENTAIRE_RELANCE)
+    etapes.append({"etape": "commentaire", "statut": statut_comment, "message": msg_comment})
+
+    statut_global = "echec" if any(e["statut"] == "echec" for e in etapes) else "ok"
+    return jsonify(succes=True, statut_global=statut_global, etapes=etapes)
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index c9f5d0a..688b0dc 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2131 (6 ligne(s)) dans l'ancienne version → ligne 2131 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2131,6 +2131,8 @@ function rendrePanneauLateralActions() {
   // détail (construireHtmlIssue, issue #80) — /fermer-issue via fermerIssue(),
   // réutilisée à l'identique, aucune nouvelle route.
   if (!ferme && nomsLabels.includes('needs-human')) {
+    html += '<button onclick="relancerIssue(\'' + escapeHtml(nom) + '\', '
+          + Number(numero) + ')">🔄 Relancer</button>';
     html += '<button class="danger-plein" onclick="fermerIssue(\'' + escapeHtml(nom) + '\', '
           + Number(numero) + ')">✖ Fermer l\'issue</button>';
   }
# ── Zone modifiée : ligne 3587 (6 ligne(s)) dans l'ancienne version → ligne 3589 (50 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3587,6 +3589,50 @@ async function interrompreEtRelancer(nom, numero) {
   }
 }
 
+// Relance une issue bloquée en needs-human (issue #460) : retire simplement
+// ce label côté GitHub (route Flask /relancer-issue, app/interruption.py) —
+// il n'existe PAS de label « pending » dans ce projet, une issue ouverte
+// sans needs-human ni done est déjà éligible au prochain cycle du watcher
+// (voir watcher.py). Ne relance PAS le watcher lui-même : si celui-ci est
+// éteint, une relance manuelle depuis l'onglet Watchers reste nécessaire.
+async function relancerIssue(nom, numero) {
+  const depot = depotDuProjet(nom);
+  if (!depot) {
+    alert('Dépôt GitHub introuvable pour le projet « ' + nom + ' » — impossible de relancer.');
+    return;
+  }
+  if (!confirm("Relancer l'issue #" + numero + " ?\n\n"
+             + "Le label needs-human sera retiré : l'issue sera reprise par le watcher "
+             + "à son prochain cycle (s'il tourne).")) return;
+
+  let resultat;
+  try {
+    const rep = await fetch('/relancer-issue', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({depot: depot, numero: Number(numero)})
+    });
+    resultat = await rep.json();
+  } catch(e) {
+    alert('Erreur réseau : ' + e.message);
+    return;
+  }
+  if (!resultat.succes || resultat.statut_global === 'echec') {
+    const detail = (resultat.etapes || []).map(e => e.message).filter(Boolean).join(' / ');
+    alert('Erreur : ' + (resultat.erreur || detail || 'échec de la relance.'));
+    return;
+  }
+
+  // Recharge la liste (l'issue a perdu needs-human) puis réaffiche si visible.
+  await chargerListeIssues();
+  const numStr = String(numero);
+  const ligne = [...document.querySelectorAll('#liste-issues .ligne-issue')]
+    .find(l => l.dataset.projet === nom && l.dataset.numero === numStr);
+  if (ligne && ligne.style.display !== 'none') {
+    await afficherIssue(nom, numStr);
+  }
+}
+
 const LIBELLES_STATUT_INTERROMPRE = {
   ok:              {icone: '✅', texte: 'Interruption effectuée'},
   succes_partiel:  {icone: '⚠️', texte: 'Interruption partielle — certaines étapes ont échoué'},
