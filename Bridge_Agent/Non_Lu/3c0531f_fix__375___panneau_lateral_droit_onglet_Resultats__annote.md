3c0531f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3c0531f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 6 10:34:37 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #375 : panneau lateral droit onglet Resultats (monitoring + actions)
    
    Ajoute un panneau ~280px a droite de la liste d'issues, deux etats pilotes
    par la selection de ligne : monitoring passif des watchers CCL+CCW (rafraichi
    toutes les 30s + sur chaque SSE fin_issue, sans appel GitHub) sans issue
    selectionnee, actions contextuelles (relancer CCL/CCW, interrompre) avec une
    issue selectionnee. Reutilise entierement les endpoints/fonctions existants
    (/watchers, /lancer-watcher, /interrompre, ccwRedemarrerProjet) — aucune
    nouvelle route Flask. Fenetre elargie 860->1160px pour l'accueillir sans
    ecraser la liste.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c1a8b81..c12e8c4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (35 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,35 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 6 août 2026 — issue #375
+
+Onglet Résultats : panneau latéral droit (~280px, scrollable, repasse sous la
+liste en écran étroit) ajouté à droite de la liste des issues
+(`.resultats-layout` / `.resultats-liste-col` / `.panneau-lateral`), qui
+utilisait mal l'espace disponible dans la fenêtre (`.fenetre` élargie
+860→1160px pour l'accueillir sans écraser la liste). Deux états, pilotés par
+la sélection de ligne existante (`selectionnerLigne`) :
+- **Aucune issue sélectionnée** : monitoring passif, tous les projets actifs —
+  watcher CCL (actif/pid via `/watchers`, appel Flask local) et watcher CCW
+  (état NSSM) pour les projets ayant un service CCW connu. Rafraîchi toutes
+  les 30s et à chaque événement SSE `fin_issue` (#350), sans appel GitHub
+  supplémentaire.
+- **Issue sélectionnée** : actions contextuelles — relancer le watcher CCL
+  (`/lancer-watcher`, comme l'onglet Watchers), interrompre l'issue (bouton
+  identique à celui du détail, `/interrompre`, affiché seulement si l'issue
+  est ouverte et ni `done` ni `needs-human`), relancer le watcher CCW
+  (`ccwRedemarrerProjet`, réutilisée telle quelle depuis l'onglet CCW) et un
+  emplacement pour « Nettoyer verrous CCW + redémarrer », désactivé en
+  attendant l'issue #378 — ces deux derniers boutons seulement si le projet a
+  un service CCW connu.
+- L'état des services CCW (`ccwProjetsConnus`) n'est JAMAIS interrogé
+  directement par ce panneau (guestcontrol coûteux) : il ne fait que lire le
+  résultat du dernier appel à `ccwChargerProjets()` (onglet CCW ou lien
+  manuel « Vérifier les services CCW » du panneau) — aucun nouveau polling.
+- Aucune route Flask ajoutée : tout reprend les endpoints existants
+  (`/watchers`, `/lancer-watcher`, `/interrompre`, `/ccw/projets`,
+  `/ccw/redemarrer-projet`).
+
 ## 3 août 2026 — issue #370
 
 Script PowerShell `surveiller_builds.ps1` (issu d'une session Claude Chat
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index 1734938..39b3cf5 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 1 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +1,11 @@
 *{box-sizing:border-box;margin:0;padding:0}
 body{font-family:system-ui,sans-serif;font-size:14px;background:#f0efe9;color:#1a1a18;min-height:100vh;padding:28px 16px;position:relative}
-.fenetre{max-width:860px;margin:0 auto;background:#fff;border:1px solid #ddd;border-radius:12px;overflow:hidden}
+/* 860px→1160px (issue #375) : l'ancienne largeur laissait l'onglet Résultats
+   sans place pour le panneau latéral droit (~280px + espacement) sans écraser
+   la liste des issues. Élargie globalement plutôt que pour ce seul onglet —
+   les autres onglets (formulaires flex, tableaux width:100%) s'en accommodent
+   sans régression, juste un peu plus de confort de lecture. */
+.fenetre{max-width:1160px;margin:0 auto;background:#fff;border:1px solid #ddd;border-radius:12px;overflow:hidden}
 .entete{padding:14px 20px;border-bottom:1px solid #dad9d2;display:flex;align-items:center;gap:9px;background:#e7e6e0}
 .entete h1{font-size:15px;font-weight:500}
 .entete .statut{margin-left:auto;font-size:12px;color:#888}
# ── Zone modifiée : ligne 267 (6 ligne(s)) dans l'ancienne version → ligne 272 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -267,6 +272,30 @@ button.danger:hover{background:#f8d7da}
 .legende-resultats{font-size:12px;color:#888;background:#f8f8f5;
   border:1px solid #e0dfda;border-radius:6px;padding:8px 12px;
   margin-bottom:16px;display:flex;flex-direction:column;gap:2px;line-height:1.55}
+/* Panneau latéral droit de l'onglet Résultats (issue #375) : liste des issues
+   à gauche (flex:1, largeur inchangée), panneau ~280px fixe à droite —
+   monitoring passif des watchers sans issue sélectionnée, actions
+   contextuelles une fois une ligne sélectionnée (voir rafraichirPanneauLateral-
+   Resultats dans app.js). Écran étroit : le panneau repasse sous la liste. */
+.resultats-layout{display:flex;gap:20px;align-items:flex-start}
+.resultats-liste-col{flex:1;min-width:0}
+.panneau-lateral{width:280px;flex-shrink:0;align-self:flex-start;
+  max-height:calc(100vh - 160px);overflow-y:auto;
+  border:1px solid #e0dfda;border-radius:8px;background:#f8f8f5;padding:14px}
+@media (max-width:900px){
+  .resultats-layout{flex-direction:column}
+  .panneau-lateral{width:100%;max-height:none}
+}
+.pl-sous{font-size:11px;color:#999;margin:-4px 0 12px}
+.pl-projet{border-left:3px solid #ccc;padding:6px 0 6px 10px;margin-bottom:10px}
+.pl-projet-nom{font-size:13px;font-weight:600;color:#1a1a18;margin-bottom:3px}
+.pl-etat{display:flex;align-items:center;gap:6px;font-size:12px;color:#555;margin-bottom:2px}
+.pl-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
+.pl-lien{font-size:12px;color:#185FA5;cursor:pointer;user-select:none;margin-top:8px;display:inline-block}
+.pl-lien:hover{text-decoration:underline}
+.pl-issue-ref{font-size:12px;color:#999;margin-bottom:12px}
+.pl-actions{display:flex;flex-direction:column;gap:8px}
+.pl-actions button{width:100%}
 .issue-body{background:#f8f8f5;border:1px solid #e0dfda;border-radius:6px;padding:12px;
   font-family:monospace;font-size:12px;white-space:pre-wrap;word-break:break-word;
   max-height:200px;overflow-y:auto;line-height:1.6;margin-bottom:16px}
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 80adb3c..4fba6b2 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2 (6 ligne(s)) dans l'ancienne version → ligne 2 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2,6 +2,18 @@ let sourceSSE = null;
 
 let intervalWatchers = null;
 
+// ─── Panneau latéral droit de l'onglet Résultats (issue #375) ─────────────
+// Rafraîchi toutes les 30s (intervalPanneauLateral) + sur chaque événement SSE
+// fin_issue (#350) + sur chaque changement de sélection de ligne. Dernière
+// liste connue des services CCW (projet/service/etat), alimentée par
+// ccwChargerProjets() — jamais interrogée directement depuis ce panneau, pour
+// ne pas ajouter un second polling des appels guestcontrol coûteux de l'onglet
+// CCW (voir ccwOuvrirOnglet) : seul un clic sur le lien « Vérifier les
+// services CCW » du panneau (sidebarChargerCcw) ou une action déjà existante
+// de l'onglet CCW la met à jour.
+let ccwProjetsConnus = [];
+let intervalPanneauLateral = null;
+
 // Connexion SSE dédiée au rafraîchissement instantané des résultats (issue
 // #350) — ouverte à l'entrée dans l'onglet Résultats, fermée en le quittant.
 let sourceFinIssue = null;
# ── Zone modifiée : ligne 63 (8 ligne(s)) dans l'ancienne version → ligne 75 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -63,8 +75,12 @@ function basculerOnglet(nom) {
   noms.forEach(n =>
     document.getElementById('panneau-' + n).classList.toggle('actif', n === nom));
   if (nom === 'journal')  demarrerJournal();
-  if (nom === 'resultats') { chargerListeIssues(); demarrerTempsRestant(); demarrerStreamFinIssue(); }
-  else { arreterTempsRestant(); arreterStreamFinIssue(); }
+  if (nom === 'resultats') {
+    chargerListeIssues(); demarrerTempsRestant(); demarrerStreamFinIssue();
+    demarrerPanneauLateral();
+  } else {
+    arreterTempsRestant(); arreterStreamFinIssue(); arreterPanneauLateral();
+  }
   if (nom === 'watchers') {
     chargerWatchers();
     intervalWatchers = setInterval(chargerWatchers, 5000);
# ── Zone modifiée : ligne 312 (6 ligne(s)) dans l'ancienne version → ligne 328 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -312,6 +328,11 @@ async function ccwChargerProjets() {
       return;
     }
     const projets = j.projets || [];
+    // Seul point d'écriture de ccwProjetsConnus (issue #375) : le panneau
+    // latéral de l'onglet Résultats lit cette variable sans jamais fetcher
+    // /ccw/projets lui-même (pas de second polling des appels guestcontrol).
+    ccwProjetsConnus = projets;
+    rafraichirPanneauLateralResultats();
     // Mémorise la sélection courante pour la restaurer si le projet existe encore.
     const selectionCourante = selectFin ? selectFin.value : '';
     if (projets.length === 0) {
# ── Zone modifiée : ligne 1695 (6 ligne(s)) dans l'ancienne version → ligne 1716 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1695,6 +1716,12 @@ function demarrerStreamFinIssue() {
     const dansLaListe = listeIssuesResultats.some(
       it => it.projet === projet && String(it.number) === String(numero));
     if (dansLaListe) verifierIssueApresDepassement(projet, numero);
+    // Panneau latéral (issue #375) : une fin d'issue change potentiellement
+    // l'état « ouvert/fermé » de l'issue sélectionnée (bouton Interrompre) et
+    // peut coïncider avec un arrêt de watcher — rafraîchi à chaque événement,
+    // sans coût supplémentaire (le fetch /watchers est local, pas d'appel
+    // GitHub, cf. issue #375).
+    rafraichirPanneauLateralResultats();
   });
 }
 
# ── Zone modifiée : ligne 1704 (6 ligne(s)) dans l'ancienne version → ligne 1731 (163 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1704,6 +1731,163 @@ function arreterStreamFinIssue() {
   if (sourceFinIssue) { sourceFinIssue.close(); sourceFinIssue = null; }
 }
 
+// ─── Panneau latéral droit de l'onglet Résultats (issue #375) ─────────────
+// Deux états mutuellement exclusifs, pilotés par projetCourant/numeroCourant
+// (mêmes variables que la sélection de ligne, voir selectionnerLigne) :
+//  - aucune sélection → monitoring passif des watchers CCL+CCW de tous les
+//    projets actifs (rendrePanneauLateralMonitoring) ;
+//  - une ligne sélectionnée → actions contextuelles pour SON projet
+//    (rendrePanneauLateralActions), sans fetch réseau (données déjà en
+//    mémoire : listeIssuesResultats + ccwProjetsConnus).
+
+function demarrerPanneauLateral() {
+  rafraichirPanneauLateralResultats();
+  arreterPanneauLateral();
+  intervalPanneauLateral = setInterval(rafraichirPanneauLateralResultats, 30000);
+}
+
+function arreterPanneauLateral() {
+  if (intervalPanneauLateral) { clearInterval(intervalPanneauLateral); intervalPanneauLateral = null; }
+}
+
+async function rafraichirPanneauLateralResultats() {
+  const panneau = document.getElementById('panneau-resultats');
+  if (!panneau || !panneau.classList.contains('actif')) return;
+  if (projetCourant && numeroCourant) {
+    rendrePanneauLateralActions();
+  } else {
+    await rendrePanneauLateralMonitoring();
+  }
+}
+
+// Couleur de la pastille CCW, même code que ccwChargerProjets (onglet CCW) —
+// répété volontairement ici plutôt que factorisé : deux appelants seulement,
+// une factorisation forcerait à exposer un utilitaire pour si peu.
+function couleurEtatCcw(etat) {
+  return etat === 'running' ? '#2e8b57' : (etat === 'stopped' ? '#c0392b' : '#888');
+}
+
+// Service CCW connu pour ce projet (ou null), depuis la dernière liste chargée
+// (ccwProjetsConnus) — jamais un fetch direct, voir le commentaire sur cette
+// variable en tête de fichier.
+function serviceCcwProjet(nom) {
+  return ccwProjetsConnus.find(p => (p.projet || '').toLowerCase() === nom.toLowerCase()) || null;
+}
+
+// Déclenche (à la demande, sur clic) le seul fetch de l'état des services CCW
+// utilisé par ce panneau : ccwChargerProjets(), qui alimente ccwProjetsConnus
+// et re-rend elle-même ce panneau une fois la réponse reçue.
+async function sidebarChargerCcw() {
+  await ccwChargerProjets();
+}
+
+// Monitoring passif (issue #375, état par défaut) : watcher CCL (actif/pid,
+// fetch /watchers — local, pas d'appel GitHub) + watcher CCW si un service est
+// déjà connu pour ce projet (ccwProjetsConnus), pour tous les projets actifs
+// (nomsProjetsDisponibles, même source que le reste de l'onglet Résultats).
+async function rendrePanneauLateralMonitoring() {
+  const zone = document.getElementById('panneau-lateral-resultats');
+  if (!zone) return;
+  const noms = nomsProjetsDisponibles();
+  let watchersMap = null;
+  try {
+    const rep = await fetch('/watchers');
+    const liste = await rep.json();
+    watchersMap = {};
+    liste.forEach(w => { watchersMap[w.nom] = w; });
+  } catch(e) { watchersMap = null; }
+  // Une issue a pu être sélectionnée pendant ce fetch : ne pas écraser le
+  // panneau d'actions qui a entre-temps pris sa place.
+  if (projetCourant && numeroCourant) return;
+
+  let html = '<div class="titre-section" style="margin-top:0">Monitoring watchers</div>'
+           + '<div class="pl-sous">Tous projets actifs — actualisé toutes les 30 s</div>';
+  if (!watchersMap) {
+    html += '<div class="issue-vide" style="padding:10px 0">Erreur de chargement</div>';
+  } else {
+    for (const nom of noms) {
+      const w = watchersMap[nom];
+      const cclActif = !!(w && w.actif);
+      const service = serviceCcwProjet(nom);
+      html += '<div class="pl-projet" style="border-left-color:' + couleurProjetResultats(nom) + '">'
+            + '<div class="pl-projet-nom">' + escapeHtml(nom) + '</div>'
+            + '<div class="pl-etat"><span class="pl-dot" style="background:'
+            + (cclActif ? '#2e8b57' : '#c0392b') + '"></span>CCL '
+            + (cclActif ? ('actif (pid ' + escapeHtml(w.pid) + ')') : 'arrêté') + '</div>';
+      if (service) {
+        html += '<div class="pl-etat"><span class="pl-dot" style="background:'
+              + couleurEtatCcw(service.etat) + '"></span>CCW '
+              + escapeHtml(service.etat || '?') + '</div>';
+      }
+      html += '</div>';
+    }
+    html += '<div class="pl-lien" onclick="sidebarChargerCcw()">🔄 '
+          + (ccwProjetsConnus.length ? 'Actualiser les services CCW' : 'Vérifier les services CCW')
+          + '</div>';
+  }
+  zone.innerHTML = html;
+}
+
+// Actions contextuelles (issue #375) : projet/issue actuellement sélectionnés
+// (projetCourant/numeroCourant). Aucun fetch réseau — les données viennent de
+// listeIssuesResultats (déjà en mémoire) et ccwProjetsConnus.
+function rendrePanneauLateralActions() {
+  const zone = document.getElementById('panneau-lateral-resultats');
+  if (!zone) return;
+  const nom = projetCourant, numero = numeroCourant;
+  const it = listeIssuesResultats.find(
+    x => x.projet === nom && String(x.number) === String(numero));
+  const nomsLabels = it ? (it.labels || []).map(l => ((l && l.name) || l || '').toLowerCase()) : [];
+  const ferme = !!(it && (it.state || '').toUpperCase() === 'CLOSED');
+  // Même condition que le bouton « Interrompre » du détail d'issue
+  // (construireHtmlIssue, issue #323) : issue ouverte, ni done ni needs-human.
+  const interromptible = !!it && !ferme
+    && !nomsLabels.includes('done') && !nomsLabels.includes('needs-human');
+  const service = serviceCcwProjet(nom);
+
+  let html = '<div class="titre-section" style="margin-top:0">Actions</div>'
+           + '<div class="pl-issue-ref">' + escapeHtml(nom) + ' #' + escapeHtml(numero) + '</div>'
+           + '<div class="pl-actions">'
+           + '<button onclick="sidebarRelancerWatcherCCL(\'' + escapeHtml(nom) + '\', this)">'
+           + '🔁 Relancer watcher CCL</button>';
+  if (interromptible) {
+    html += '<button class="danger" onclick="interrompreIssue(\'' + escapeHtml(nom) + '\', '
+          + Number(numero) + ')">⛔ Interrompre l\'issue</button>';
+  }
+  if (service) {
+    html += '<button onclick="ccwRedemarrerProjet(\'' + escapeHtml(nom) + '\', this)">'
+          + '🔁 Relancer watcher CCW</button>'
+          + '<button disabled title="Prévu par l\'issue #378 (à venir) — pas encore implémenté">'
+          + '🔒 Nettoyer verrous CCW + redémarrer</button>';
+  }
+  html += '</div>';
+  if (!ccwProjetsConnus.length) {
+    html += '<div class="pl-lien" onclick="sidebarChargerCcw()">🔄 Vérifier le service CCW de ce projet</div>';
+  }
+  zone.innerHTML = html;
+}
+
+// Relance (ou lance) le watcher CCL du projet donné — même endpoint que
+// l'onglet Watchers (actionWatchers → /lancer-watcher), appelé ici pour un
+// seul projet directement depuis le panneau latéral.
+async function sidebarRelancerWatcherCCL(nom, btn) {
+  const label = btn ? btn.textContent : null;
+  if (btn) { btn.disabled = true; btn.textContent = 'Relance…'; }
+  try {
+    await fetch('/lancer-watcher', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({projet: nom, relancer: true})
+    });
+  } catch(e) {
+    alert('Erreur réseau : ' + e.message);
+  }
+  const panneauWatchers = document.getElementById('panneau-watchers');
+  if (panneauWatchers && panneauWatchers.classList.contains('actif')) await chargerWatchers();
+  if (btn) { btn.disabled = false; if (label !== null) btn.textContent = label; }
+  await rafraichirPanneauLateralResultats();
+}
+
 // Sélectionne la première ligne encore visible SANS charger son détail (voir
 // selectionnerLigne, issue #261) ; vide le détail s'il n'y a plus rien à
 // afficher. Appelée à l'ouverture de l'onglet, à chaque changement de filtre
# ── Zone modifiée : ligne 1965 (11 ligne(s)) dans l'ancienne version → ligne 2149 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1965,11 +2149,13 @@ function selectionnerLigne(nom, numero) {
     projetCourant = null;
     numeroCourant = null;
     zone.innerHTML = '<div class="issue-vide">Aucune issue à afficher</div>';
+    rafraichirPanneauLateralResultats();
     return;
   }
   projetCourant = nom;
   numeroCourant = numero;
   zone.innerHTML = '<div class="issue-vide">Double-cliquez une issue pour afficher son détail.</div>';
+  rafraichirPanneauLateralResultats();
 }
 
 async function afficherIssue(nom, numero) {
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 61e857b..52997cf 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 191 (6 ligne(s)) dans l'ancienne version → ligne 191 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -191,6 +191,9 @@
 
   <!-- ─── Onglet Résultats : visualisation des issues ──────────────────── -->
   <div id="panneau-resultats" class="panneau">
+   <div class="resultats-layout">
+    <!-- Colonne gauche : liste + détail (contenu inchangé, issue #375). -->
+    <div class="resultats-liste-col">
 
     <!-- Boutons toggle : un par projet + « Tous ». Générés dynamiquement. -->
     <div id="filtres-projets" class="filtres-projets"></div>
# ── Zone modifiée : ligne 241 (6 ligne(s)) dans l'ancienne version → ligne 244 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -241,6 +244,16 @@
     <div id="zone-issue" class="zone-issue">
       <div class="issue-vide">Aucune issue à afficher</div>
     </div>
+
+    </div><!-- /resultats-liste-col -->
+
+    <!-- Panneau latéral droit (issue #375) : monitoring passif des watchers
+         (aucune issue sélectionnée) ou actions contextuelles (issue
+         sélectionnée). Peuplé par rafraichirPanneauLateralResultats()
+         (static/js/app.js) — jamais rempli côté serveur. -->
+    <div id="panneau-lateral-resultats" class="panneau-lateral"></div>
+
+   </div><!-- /resultats-layout -->
   </div>
 
   <!-- ─── Onglet 2 : gestion des watchers ──────────────────────────────── -->
