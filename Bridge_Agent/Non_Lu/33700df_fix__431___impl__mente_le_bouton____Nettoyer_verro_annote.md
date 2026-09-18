33700df

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 33700df
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 13:47:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #431 : implémente le bouton « Nettoyer verrous CCW + redémarrer » (prévu par #378)
    
    - provisioning/windows/nettoyer_verrous_ccw.ps1 : nssm stop (attente
      confirmée ~5s), suppression de tous les .lock de logs\verrous, nssm
      start, résumé final (nb verrous supprimés + état service). BOM UTF-8.
    - app/ccw.py : route POST /ccw/nettoyer-verrous (ccw_nettoyer_verrous),
      même pattern guestcontrol qu'interrompre_windows() (app/interruption.py).
    - static/js/app.js : bouton du panneau latéral branché sur la route
      (ccwNettoyerVerrous), retire le tooltip « pas encore implémenté ».

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/__init__.py b/app/__init__.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3d63717..132c443 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/__init__.py
# ── Version APRÈS ce commit.
+++ b/app/__init__.py
# ── Zone modifiée : ligne 74 (7 ligne(s)) dans l'ancienne version → ligne 74 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -74,7 +74,7 @@ def _enregistrer_routes(app: Flask) -> None:
     from app.ccw import (ccw_vm_statut, ccw_demarrer_vm, ccw_projets,
                          ccw_ajouter_projet, ccw_finaliser_projet,
                          ccw_redemarrer_projet, ccw_demarrer_projet,
-                         ccw_arreter_projet)
+                         ccw_arreter_projet, ccw_nettoyer_verrous)
     from app.interruption import route_interrompre
     from app.cycle_vie import heartbeat, events, quitter
     from app.fin_issue import notifier_fin_issue, stream_fin_issue
# ── Zone modifiée : ligne 118 (6 ligne(s)) dans l'ancienne version → ligne 118 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -118,6 +118,8 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/ccw/redemarrer-projet", "ccw_redemarrer_projet", login_requis(ccw_redemarrer_projet), methods=["POST"])
     app.add_url_rule("/ccw/demarrer-projet", "ccw_demarrer_projet", login_requis(ccw_demarrer_projet), methods=["POST"])
     app.add_url_rule("/ccw/arreter-projet", "ccw_arreter_projet", login_requis(ccw_arreter_projet), methods=["POST"])
+    # Nettoyage des verrous CCW orphelins (issue #431, prévu par #378).
+    app.add_url_rule("/ccw/nettoyer-verrous", "ccw_nettoyer_verrous", login_requis(ccw_nettoyer_verrous), methods=["POST"])
     # ─── Interruption ciblée d'une issue en cours (issue #323, suite #320) ────
     app.add_url_rule("/interrompre", "route_interrompre", login_requis(route_interrompre), methods=["POST"])
     app.add_url_rule("/heartbeat", "heartbeat", heartbeat, methods=["POST"])
# (diff du fichier suivant)
diff --git a/app/ccw.py b/app/ccw.py
# (index — ignorable)
index 556c6c5..11961f8 100644
# (avant — fichier suivant)
--- a/app/ccw.py
# (après — fichier suivant)
+++ b/app/ccw.py
# ── Zone modifiée : ligne 26 (6 ligne(s)) dans l'ancienne version → ligne 26 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -26,6 +26,7 @@ MOT DE PASSE ccw-admin (point 5 de l'issue) :
 
 import contextlib
 import json
+import ntpath
 import os
 import re
 import shutil
# ── Zone modifiée : ligne 515 (3 ligne(s)) dans l'ancienne version → ligne 516 (97 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -515,3 +516,97 @@ def ccw_arreter_projet():
     arrêter temporairement un service (économie de ressources VM) sans le
     relancer aussitôt. Voir _piloter_service_ccw."""
     return _piloter_service_ccw("stop", "arrêt")
+
+
+def _texte_erreur_json(reponse_json) -> str:
+    """Extrait le champ erreur d'une réponse jsonify(...) d'échec (_preparer,
+    _lister_projets_vm) — même logique que _erreur_de dans app/interruption.py,
+    dupliquée ici pour éviter un import circulaire (interruption.py importe déjà
+    depuis ce module)."""
+    try:
+        return reponse_json.get_json().get("erreur") or "Erreur inconnue."
+    except Exception:
+        return "Erreur inconnue."
+
+
+def ccw_nettoyer_verrous():
+    """Nettoie les verrous CCW orphelins d'un projet (issue #431, bouton
+    « 🔒 Nettoyer verrous CCW + redémarrer » prévu par #378) : arrête le
+    service, supprime tous les .lock de son dossier de verrous, puis relance
+    — un seul aller-retour guestcontrol (copie + exécution de
+    nettoyer_verrous_ccw.ps1), sur le modèle d'interrompre_windows()
+    (app/interruption.py).
+
+    Cas d'usage : un verrou orphelin bloque le watcher CCW sans qu'il y ait
+    d'issue précise à interrompre (le bouton « Interrompre » n'est disponible
+    que sur une issue ouverte précise)."""
+    data = request.json or {}
+    nom  = (data.get("nom") or "").strip()
+    if not nom or re.search(r"[\\/\s]", nom):
+        return jsonify(statut="echec",
+            message="Nom de projet requis, sans espace ni séparateur de chemin.")
+
+    ctx, err = _preparer()
+    if err:
+        return jsonify(statut="echec", message=_texte_erreur_json(err))
+    vbox, mot_de_passe = ctx
+
+    projets, err = _lister_projets_vm(vbox, mot_de_passe)
+    if err:
+        return jsonify(statut="echec", message=_texte_erreur_json(err))
+
+    service = config_path = None
+    for p in projets:
+        if isinstance(p, dict) and str(p.get("projet", "")).strip().lower() == nom.lower():
+            service     = (p.get("service") or "").strip()
+            config_path = (p.get("config") or "").strip()
+            break
+    if not service:
+        return jsonify(statut="echec",
+            message=f"Projet « {nom} » introuvable parmi les services CCW-Watcher de la VM. "
+                    f"Rafraîchissez la liste des projets.")
+    # Même garde-fou que _piloter_service_ccw avant d'injecter le nom du
+    # service dans la commande PowerShell.
+    if not re.match(r"^CCW-Watcher(-\w+)?$", service):
+        return jsonify(statut="echec",
+            message=f"Nom de service inattendu (« {service} ») — abandon par précaution.")
+
+    # RepDepot dérivé du champ « config » (…\<NomProjet>\configs\*.conf) —
+    # même règle que interrompre_windows() (app/interruption.py).
+    rep_depot = (ntpath.dirname(ntpath.dirname(config_path)) if config_path
+                 else ntpath.join("C:\\CCW", nom))
+
+    script = DOSSIER_WINDOWS / "nettoyer_verrous_ccw.ps1"
+    if not script.exists():
+        return jsonify(statut="echec", message=f"Script introuvable : {script.name}")
+
+    try:
+        with _fichier_mot_de_passe(mot_de_passe) as pf:
+            base = _base_guest(vbox, pf)
+            r = _copier(base, script, TIMEOUT_COURT)
+            if r.returncode != 0:
+                return jsonify(statut="echec",
+                    message=_message_echec("copie du script vers la VM", r))
+            r = _executer_ps(base, script.name, ["-Service", service, "-RepDepot", rep_depot], TIMEOUT_LONG)
+    except subprocess.TimeoutExpired:
+        return jsonify(statut="echec",
+            message="Délai dépassé pendant le nettoyage des verrous (guestcontrol).")
+    except subprocess.SubprocessError as e:
+        return jsonify(statut="echec", message=f"Erreur guestcontrol : {e}")
+
+    etapes = _extraire_projets(r.stdout)
+    if etapes is None:
+        return jsonify(statut="echec",
+            message=_message_echec("nettoyage des verrous CCW", r))
+
+    resume = next((e for e in etapes if isinstance(e, dict) and e.get("etape") == "resume"), None)
+    if resume is None:
+        return jsonify(statut="echec", message="Réponse de la VM vide ou illisible.")
+
+    return jsonify(
+        statut=resume.get("statut", "echec"),
+        message=resume.get("message", ""),
+        service=service,
+        etapes=etapes,
+        sortie=_sortie_lisible(r),
+    )
# (diff du fichier suivant)
diff --git a/provisioning/windows/nettoyer_verrous_ccw.ps1 b/provisioning/windows/nettoyer_verrous_ccw.ps1
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..b70f399
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/provisioning/windows/nettoyer_verrous_ccw.ps1
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (125 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,125 @@
+﻿<#
+  nettoyer_verrous_ccw.ps1 — Nettoie les verrous CCW orphelins (issue #431,
+  bouton « 🔒 Nettoyer verrous CCW + redémarrer » prévu par #378) : arrête le
+  service CCW-Watcher, supprime tous les .lock du dossier de verrous, puis
+  relance le service.
+
+  Cas d'usage : un verrou orphelin bloque le watcher CCW SANS qu'il y ait
+  d'issue précise à interrompre — à la différence du bouton « Interrompre »
+  (interrompre_projet_ccw.ps1), disponible uniquement sur une issue ouverte
+  précise. Volontairement PAS de vérification d'arbre de process ici (pas de
+  PID de référence sans issue ciblée) : l'attente bornée de la disparition du
+  service via nssm suffit, l'objectif étant justement de déverrouiller sans
+  dépendre d'une issue précise.
+
+  Exécuté À DISTANCE depuis app/ccw.py (Linux) via « VBoxManage guestcontrol
+  run », après copie du script — jamais interactif. Émis en JSON encadré par
+  les mêmes marqueurs que lister_projets_ccw.ps1 (<<<CCW_JSON>>> /
+  <<<CCW_END>>>), pour réutiliser le même extracteur côté Linux
+  (_extraire_projets).
+
+  $RepDepot est dérivé côté Linux du champ « config » retourné par
+  lister_projets_ccw.ps1 (même règle que interrompre_projet_ccw.ps1) — jamais
+  reconstruit depuis $Service ni depuis le nom du projet Linux, qui peuvent
+  diverger (cf. §"résolution des identités" de l'issue #323).
+
+  Exécution en administrateur, DANS la VM CCW-Build.
+#>
+
+[CmdletBinding()]
+param(
+    [Parameter(Mandatory=$true)][string]$Service,
+    [Parameter(Mandatory=$true)][string]$RepDepot
+)
+
+$ErrorActionPreference = 'Stop'
+Set-StrictMode -Version Latest
+
+$script:etapes = @()
+
+function AjouterEtape([string]$Nom, [string]$Statut, [string]$Message) {
+    $script:etapes += [PSCustomObject]@{ etape = $Nom; statut = $Statut; message = $Message }
+}
+
+function EtatService([string]$Nom) {
+    $svc = Get-CimInstance Win32_Service -Filter "Name='$Nom'" -ErrorAction SilentlyContinue
+    if ($svc) { return $svc.State }
+    return $null
+}
+
+# ─── Étape 1 : arrêt du service, attente confirmée (bornée à ~5s) ──────────
+$etatInitial = EtatService $Service
+if (-not $etatInitial) {
+    AjouterEtape 'arret_service_ccw' 'rien_a_faire' "Service « $Service » introuvable — déjà désinstallé ?"
+} elseif ($etatInitial -ne 'Running') {
+    AjouterEtape 'arret_service_ccw' 'rien_a_faire' "Service « $Service » déjà arrêté (état : $etatInitial)."
+} else {
+    try {
+        $sortie = & nssm stop $Service 2>&1 | Out-String
+        $limite = (Get-Date).AddSeconds(5)
+        $etat   = EtatService $Service
+        while ($etat -eq 'Running' -and (Get-Date) -lt $limite) {
+            Start-Sleep -Milliseconds 250
+            $etat = EtatService $Service
+        }
+        if ($etat -eq 'Running') {
+            AjouterEtape 'arret_service_ccw' 'echec' "nssm stop $Service : toujours « Running » après 5s. Sortie : $($sortie.Trim())"
+        } else {
+            AjouterEtape 'arret_service_ccw' 'succes' "nssm stop $Service : arrêt confirmé (état : $etat). $($sortie.Trim())"
+        }
+    } catch {
+        AjouterEtape 'arret_service_ccw' 'echec' "nssm stop a échoué : $_"
+    }
+}
+
+# ─── Étape 2 : suppression de TOUS les .lock (verrous orphelins) ──────────
+$dossierVerrous = Join-Path $RepDepot 'logs\verrous'
+$nbSupprimes = 0
+if (-not (Test-Path $dossierVerrous)) {
+    AjouterEtape 'suppression_verrous' 'rien_a_faire' "Dossier de verrous introuvable ($dossierVerrous) — rien à supprimer."
+} else {
+    $locks = @(Get-ChildItem -Path $dossierVerrous -Filter '*.lock' -ErrorAction SilentlyContinue)
+    if ($locks.Count -eq 0) {
+        AjouterEtape 'suppression_verrous' 'rien_a_faire' 'Aucun fichier .lock présent.'
+    } else {
+        $echecs = @()
+        foreach ($lock in $locks) {
+            try {
+                Remove-Item -Path $lock.FullName -Force -ErrorAction Stop
+                $nbSupprimes++
+                Write-Output "Verrou supprimé : $($lock.Name)"
+            } catch {
+                $echecs += $lock.Name
+                Write-Output "Échec de suppression de $($lock.Name) : $_"
+            }
+        }
+        $statutGlobal = if ($echecs.Count -eq 0) { 'succes' } else { 'echec' }
+        $msg = "$nbSupprimes verrou(s) supprimé(s) sur $($locks.Count) : $(($locks | ForEach-Object { $_.Name }) -join ', ')."
+        if ($echecs.Count -gt 0) { $msg += " Échecs : $($echecs -join ', ')." }
+        AjouterEtape 'suppression_verrous' $statutGlobal $msg
+    }
+}
+
+# ─── Étape 3 : redémarrage du service ──────────────────────────────────────
+try {
+    $sortie = & nssm start $Service 2>&1 | Out-String
+    Start-Sleep -Milliseconds 500
+    $etatFinal = EtatService $Service
+    if ($etatFinal -eq 'Running') {
+        AjouterEtape 'redemarrage_service_ccw' 'succes' "nssm start $Service : service relancé (état : $etatFinal)."
+    } else {
+        AjouterEtape 'redemarrage_service_ccw' 'echec' "nssm start $Service : état après relance = « $etatFinal ». Sortie : $($sortie.Trim())"
+    }
+} catch {
+    $etatFinal = EtatService $Service
+    AjouterEtape 'redemarrage_service_ccw' 'echec' "nssm start a échoué : $_"
+}
+
+# ─── Résumé final (nb de verrous supprimés + statut final du service) ─────
+$echecEtapes = @($script:etapes | Where-Object { $_.statut -eq 'echec' })
+$statutResume = if ($echecEtapes.Count -eq 0) { 'succes' } else { 'echec' }
+AjouterEtape 'resume' $statutResume "$nbSupprimes verrou(s) supprimé(s) — service « $Service » : $etatFinal."
+
+Write-Output '<<<CCW_JSON>>>'
+Write-Output (ConvertTo-Json -Depth 4 -Compress @($script:etapes))
+Write-Output '<<<CCW_END>>>'
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index ad2b7f2..af5ee8b 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 509 (6 ligne(s)) dans l'ancienne version → ligne 509 (48 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -509,6 +509,48 @@ async function ccwArreterProjet(nom, btn) {
   }
 }
 
+// Nettoie les verrous CCW orphelins d'un projet (issue #431, prévu par #378) :
+// arrête le service, supprime tous les .lock de son dossier de verrous, puis
+// relance — en un seul appel serveur (/ccw/nettoyer-verrous). Cas d'usage :
+// un verrou orphelin bloque le watcher CCW sans issue précise à interrompre
+// (à la différence du bouton « Interrompre l'issue », qui exige une issue
+// ouverte). Même pattern que ccwRedemarrerProjet/ccwArreterProjet, utilisé
+// depuis le panneau latéral (#pl-zone-actions) : la zone #ccw-message de
+// l'onglet CCW n'y existe pas, ccwMessage()/ccwAfficherSortie() y sont donc
+// des no-op silencieux — le retour visuel se fait via le libellé du bouton.
+async function ccwNettoyerVerrous(nom, btn) {
+  if (!nom) return;
+  if (!confirm('Nettoyer les verrous CCW du projet « ' + nom + ' » ?\n\n'
+             + 'Le service sera ARRÊTÉ, tous les fichiers .lock de son dossier de '
+             + 'verrous seront supprimés, puis le service sera relancé.')) return;
+  const labelInitial = btn ? btn.textContent : null;
+  if (btn) { btn.disabled = true; btn.textContent = 'Nettoyage…'; }
+  ccwMessage('ccw-message', 'Nettoyage des verrous de « ' + nom + ' » dans la VM…', '');
+  ccwAfficherSortie('');
+  try {
+    const rep = await fetch('/ccw/nettoyer-verrous', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({nom: nom})
+    });
+    const j = await rep.json();
+    ccwAfficherSortie(j.sortie);
+    if (j.statut === 'succes') {
+      ccwMessage('ccw-message', j.message || 'Verrous nettoyés, service relancé.', 'succes');
+      alert('✅ ' + (j.message || 'Verrous nettoyés, service relancé.'));
+    } else {
+      ccwMessage('ccw-message', j.message || 'Échec du nettoyage des verrous.', 'erreur');
+      alert('❌ ' + (j.message || 'Échec du nettoyage des verrous CCW.'));
+    }
+    ccwChargerProjets();
+  } catch (e) {
+    ccwMessage('ccw-message', 'Erreur réseau : ' + e.message, 'erreur');
+    alert('Erreur réseau : ' + e.message);
+  } finally {
+    if (btn) { btn.disabled = false; if (labelInitial !== null) btn.textContent = labelInitial; }
+  }
+}
+
 async function ccwAjouterProjet() {
   const nom   = document.getElementById('ccw-add-nom').value.trim();
   const depot = document.getElementById('ccw-add-depot').value.trim();
# ── Zone modifiée : ligne 2157 (7 ligne(s)) dans l'ancienne version → ligne 2199 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2157,7 +2199,7 @@ function rendrePanneauLateralActions() {
   if (service) {
     html += '<button onclick="ccwRedemarrerProjet(\'' + escapeHtml(nom) + '\', this)">'
           + '↺ Relancer watcher CCW</button>'
-          + '<button disabled title="Prévu par l\'issue #378 (à venir) — pas encore implémenté">'
+          + '<button class="danger" onclick="ccwNettoyerVerrous(\'' + escapeHtml(nom) + '\', this)">'
           + '🔒 Nettoyer verrous CCW + redémarrer</button>';
   }
   html += '</div>';
