0b11763

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0b11763
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 6 11:40:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #377 : panneau lateral monitoring permanent + actions sous la selection
    
    - rendrePanneauLateralMonitoring cible #pl-zone-monitoring, toujours rendue
      (VM CCW, watchers CCL colores par projet + bouton relance groupee des
      eteints, services CCW), meme issue selectionnee.
    - rendrePanneauLateralActions cible #pl-zone-actions, se vide (disparait)
      hors selection au lieu de remplacer le monitoring ; titre fusionne
      Actions - <projet> #<numero>.
    - rafraichirPanneauLateralResultats rend desormais les deux zones au lieu
      de choisir l'une ou l'autre.
    - nouveau sidebarRelancerTousEteints() : /lancer-watcher sequentiel sur
      chaque watcher CCL eteint.
    - templates/index.html : panneau-lateral-resultats scinde en deux
      conteneurs fixes.
    - CSS : classes .pl-projet/.pl-projet-nom/.pl-issue-ref retirees
      (detail par projet redondant avec les pastilles + la pastille projet
      deja presente sur chaque ligne, verifiee sans modification necessaire).
    - CHANGELOG.md : nouvelle entree en tete.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c0227ab..b374a99 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,51 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 6 août 2026 — issue #377
+
+Panneau latéral de l'onglet Résultats (#375/#376) : les deux états
+mutuellement exclusifs (monitoring OU actions) deviennent **deux zones
+empilées non exclusives**, chacune dans son propre conteneur DOM
+(`#pl-zone-monitoring` / `#pl-zone-actions`, sous `#panneau-lateral-resultats`,
+`templates/index.html`) :
+- **Zone haute — monitoring, toujours visible**, même issue sélectionnée
+  (`rendrePanneauLateralMonitoring`, `static/js/app.js`) : VM CCW inchangée ;
+  watchers CCL désormais colorés **par projet** (`couleurProjetResultats`,
+  et non plus vert/rouge générique — pastille sombre `#33322f` = éteint,
+  couleur vive du projet = actif) avec un nouveau bouton « ↺ Relancer tous les
+  éteints » (`sidebarRelancerTousEteints`) qui relit `/watchers` au clic puis
+  relance séquentiellement, un par un via `/lancer-watcher`, chaque watcher
+  éteint (une relance en échec n'interrompt pas les suivantes) ; services CCW
+  inchangés. Le détail par projet (`.pl-projet`, pid, état CCW ligne par
+  ligne) est retiré : redondant avec les pastilles par projet ci-dessus et
+  avec la pastille projet désormais sur chaque ligne de résultat (voir
+  ci-dessous).
+- **Zone basse — actions contextuelles, visible uniquement si une issue est
+  sélectionnée** (`rendrePanneauLateralActions`), avec un séparateur
+  `<hr class="pl-sep">` et un titre unique « Actions — `<projet>` #`<numero>` »
+  (fusion de l'ancien titre + de la référence séparée). Se vide (donc
+  disparaît entièrement, séparateur compris) dès qu'aucune ligne n'est
+  sélectionnée, au lieu de remplacer le monitoring. Boutons inchangés sur le
+  fond (relancer watcher CCL, interrompre l'issue si ouverte et ni `done` ni
+  `needs-human`, relancer watcher CCW, verrous CCW désactivé en attendant
+  #378), icône de relance alignée sur celle du monitoring (« ↺ » au lieu de
+  « 🔁 »).
+- `rafraichirPanneauLateralResultats()` rend désormais TOUJOURS le monitoring
+  puis (re)rend/vide les actions, au lieu de choisir l'un OU l'autre — appelé
+  sans changement par le SSE `fin_issue`, l'intervalle 30s et chaque
+  changement de sélection de ligne.
+
+La pastille colorée de projet sur chaque ligne de résultat
+(`.pastille-ligne`, `construireLigneIssueDOM`) existait déjà (issue #66,
+héritée de l'extraction du frontend) et couvrait déjà le besoin exprimé par
+cette issue pour le filtre « Tous » — aucune modification nécessaire sur ce
+point, vérifié seulement.
+
+CSS (`static/css/style.css`) : classes `.pl-projet`, `.pl-projet-nom` et
+`.pl-issue-ref` retirées (plus aucun appelant après la restructuration) ;
+`.pl-synthese`, `.pl-chips`, `.pl-btn-vm`, `.pl-sep`, `.pl-actions`
+inchangées, réutilisées telles quelles par les deux zones.
+
 ## 6 août 2026 — issue #376
 
 Panneau monitoring de l'onglet Résultats (`rendrePanneauLateralMonitoring`,
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index 07f8707..178be7f 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 287 (8 ligne(s)) dans l'ancienne version → ligne 287 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -287,8 +287,6 @@ button.danger:hover{background:#f8d7da}
   .panneau-lateral{width:100%;max-height:none}
 }
 .pl-sous{font-size:11px;color:#999;margin:-4px 0 12px}
-.pl-projet{border-left:3px solid #ccc;padding:6px 0 6px 10px;margin-bottom:10px}
-.pl-projet-nom{font-size:13px;font-weight:600;color:#1a1a18;margin-bottom:3px}
 .pl-etat{display:flex;align-items:center;gap:6px;font-size:12px;color:#555;margin-bottom:2px}
 .pl-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
 .pl-lien{font-size:12px;color:#185FA5;cursor:pointer;user-select:none;margin-top:8px;display:inline-block}
# ── Zone modifiée : ligne 299 (7 ligne(s)) dans l'ancienne version → ligne 297 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -299,7 +297,6 @@ button.danger:hover{background:#f8d7da}
 .pl-chip{display:inline-flex;align-items:center;gap:5px}
 .pl-btn-vm{margin:6px 0 2px}
 .pl-sep{border:none;border-top:1px solid #e0dfda;margin:14px 0}
-.pl-issue-ref{font-size:12px;color:#999;margin-bottom:12px}
 .pl-actions{display:flex;flex-direction:column;gap:8px}
 .pl-actions button{width:100%}
 .issue-body{background:#f8f8f5;border:1px solid #e0dfda;border-radius:6px;padding:12px;
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index e3aee4e..af597eb 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1731 (14 ligne(s)) dans l'ancienne version → ligne 1731 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1731,14 +1731,17 @@ function arreterStreamFinIssue() {
   if (sourceFinIssue) { sourceFinIssue.close(); sourceFinIssue = null; }
 }
 
-// ─── Panneau latéral droit de l'onglet Résultats (issue #375) ─────────────
-// Deux états mutuellement exclusifs, pilotés par projetCourant/numeroCourant
+// ─── Panneau latéral droit de l'onglet Résultats (issue #375, #377) ───────
+// Deux zones EMPILÉES, non exclusives, pilotées par projetCourant/numeroCourant
 // (mêmes variables que la sélection de ligne, voir selectionnerLigne) :
-//  - aucune sélection → monitoring passif des watchers CCL+CCW de tous les
-//    projets actifs (rendrePanneauLateralMonitoring) ;
-//  - une ligne sélectionnée → actions contextuelles pour SON projet
-//    (rendrePanneauLateralActions), sans fetch réseau (données déjà en
-//    mémoire : listeIssuesResultats + ccwProjetsConnus).
+//  - zone haute (#pl-zone-monitoring) : monitoring passif des watchers CCL+CCW
+//    de tous les projets actifs (rendrePanneauLateralMonitoring), TOUJOURS
+//    rendue, sélection ou non — pour garder l'infra sous les yeux en
+//    travaillant sur une issue (issue #377) ;
+//  - zone basse (#pl-zone-actions) : actions contextuelles pour le projet/
+//    l'issue sélectionnés (rendrePanneauLateralActions), sans fetch réseau
+//    (données déjà en mémoire : listeIssuesResultats + ccwProjetsConnus) —
+//    vidée (donc invisible) quand aucune ligne n'est sélectionnée.
 
 function demarrerPanneauLateral() {
   rafraichirPanneauLateralResultats();
# ── Zone modifiée : ligne 1753 (11 ligne(s)) dans l'ancienne version → ligne 1756 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1753,11 +1756,11 @@ function arreterPanneauLateral() {
 async function rafraichirPanneauLateralResultats() {
   const panneau = document.getElementById('panneau-resultats');
   if (!panneau || !panneau.classList.contains('actif')) return;
-  if (projetCourant && numeroCourant) {
-    rendrePanneauLateralActions();
-  } else {
-    await rendrePanneauLateralMonitoring();
-  }
+  // Les deux zones sont indépendantes (issue #377) : le monitoring se
+  // rafraîchit toujours, les actions contextuelles se (re)rendent — ou se
+  // vident — selon la sélection courante, sans attendre le fetch du monitoring.
+  await rendrePanneauLateralMonitoring();
+  rendrePanneauLateralActions();
 }
 
 // Couleur de la pastille CCW, même code que ccwChargerProjets (onglet CCW) —
# ── Zone modifiée : ligne 1806 (15 ligne(s)) dans l'ancienne version → ligne 1809 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1806,15 +1809,16 @@ async function sidebarDemarrerVm(btn) {
   await rafraichirPanneauLateralResultats();
 }
 
-// Monitoring passif (issue #375/#376, état par défaut). En tête, une vue
-// SYNTHÉTIQUE de l'infrastructure (issue #376) : état de la VM CCW + bouton de
-// démarrage si éteinte, résumé « N/M watchers CCL actifs », résumé « N/M
-// services CCW running ». En dessous, le détail par projet inchangé : watcher
-// CCL (actif/pid, fetch /watchers — local, pas d'appel GitHub) + watcher CCW si
-// un service est déjà connu (ccwProjetsConnus), pour tous les projets actifs
-// (nomsProjetsDisponibles, même source que le reste de l'onglet Résultats).
+// Monitoring de l'infrastructure, TOUJOURS visible en zone haute du panneau
+// (issue #375/#376, restructuré en zone fixe #377), qu'une issue soit
+// sélectionnée ou non : état de la VM CCW + bouton de démarrage si éteinte,
+// pastilles watchers CCL colorées PAR PROJET (couleurProjetResultats — un
+// point sombre = éteint, couleur vive = actif) + bouton de relance groupée des
+// éteints, pastilles services CCW par projet (ou lien de vérification si aucun
+// service encore connu). Cible #pl-zone-monitoring, indépendante de la zone
+// d'actions contextuelles (#pl-zone-actions) — voir le commentaire d'en-tête.
 async function rendrePanneauLateralMonitoring() {
-  const zone = document.getElementById('panneau-lateral-resultats');
+  const zone = document.getElementById('pl-zone-monitoring');
   if (!zone) return;
   const noms = nomsProjetsDisponibles();
   // Deux fetchs locaux en parallèle : /watchers (état CCL) et /ccw/vm-statut
# ── Zone modifiée : ligne 1831 (11 ligne(s)) dans l'ancienne version → ligne 1835 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1831,11 +1835,8 @@ async function rendrePanneauLateralMonitoring() {
     liste.forEach(w => { watchersMap[w.nom] = w; });
     if (repVm) { try { vmStatut = await repVm.json(); } catch(e) { vmStatut = null; } }
   } catch(e) { watchersMap = null; }
-  // Une issue a pu être sélectionnée pendant ces fetchs : ne pas écraser le
-  // panneau d'actions qui a entre-temps pris sa place.
-  if (projetCourant && numeroCourant) return;
 
-  let html = '<div class="titre-section" style="margin-top:0">Monitoring watchers</div>'
+  let html = '<div class="titre-section" style="margin-top:0">Monitoring infrastructure</div>'
            + '<div class="pl-sous">Tous projets actifs — actualisé toutes les 30 s</div>';
   if (!watchersMap) {
     html += '<div class="issue-vide" style="padding:10px 0">Erreur de chargement</div>';
# ── Zone modifiée : ligne 1843 (7 ligne(s)) dans l'ancienne version → ligne 1844 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1843,7 +1844,6 @@ async function rendrePanneauLateralMonitoring() {
     return;
   }
 
-  // ── Bloc synthétique infrastructure (issue #376) ──────────────────────────
   html += '<div class="pl-synthese">';
 
   // 1. VM CCW : allumée (vert) / éteinte (rouge) / inconnu (gris).
# ── Zone modifiée : ligne 1866 (17 ligne(s)) dans l'ancienne version → ligne 1866 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1866,17 +1866,25 @@ async function rendrePanneauLateralMonitoring() {
     html += '<button class="pl-btn-vm" onclick="sidebarDemarrerVm(this)">▶ Démarrer la VM</button>';
   }
 
-  // 2. Résumé watchers CCL : N/M actifs + liste inline actifs/éteints.
+  // 2. Watchers CCL : une pastille PAR PROJET colorée à la couleur du projet
+  // (couleurProjetResultats), pas juste vert/rouge — un point sombre indique
+  // un watcher éteint, la couleur vive du projet indique un watcher actif
+  // (issue #377), pour repérer d'un coup d'œil LEQUEL est éteint. Bouton de
+  // relance groupée si au moins un est éteint.
   const cclActifs  = noms.filter(n => !!(watchersMap[n] && watchersMap[n].actif));
   const cclEteints = noms.filter(n => !(watchersMap[n] && watchersMap[n].actif));
   html += '<div class="pl-resume-titre">' + cclActifs.length + '/' + noms.length
         + ' watchers CCL actifs</div>'
         + '<div class="pl-chips">'
-        + pastillesInline(cclActifs, () => '#2e8b57')
-        + (cclEteints.length ? ' ' + pastillesInline(cclEteints, () => '#c0392b') : '')
+        + pastillesInline(cclActifs, couleurProjetResultats)
+        + (cclEteints.length ? ' ' + pastillesInline(cclEteints, () => '#33322f') : '')
         + '</div>';
+  if (cclEteints.length) {
+    html += '<button class="pl-btn-vm" onclick="sidebarRelancerTousEteints(this)">'
+          + '↺ Relancer tous les éteints</button>';
+  }
 
-  // 3. Résumé watchers CCW : seulement si des services sont déjà connus.
+  // 3. Résumé services CCW : seulement si des services sont déjà connus.
   if (ccwProjetsConnus.length) {
     const ccwRunning = ccwProjetsConnus.filter(p => p.etat === 'running');
     const ccwAutres  = ccwProjetsConnus.filter(p => p.etat !== 'running');
# ── Zone modifiée : ligne 1891 (40 ligne(s)) dans l'ancienne version → ligne 1899 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1891,40 +1899,20 @@ async function rendrePanneauLateralMonitoring() {
     html += '<div class="pl-lien" onclick="sidebarChargerCcw()">🔄 Vérifier les services CCW</div>';
   }
   html += '</div>';  // .pl-synthese
-
-  // ── Séparateur + détail par projet (inchangé, issue #375) ─────────────────
-  html += '<hr class="pl-sep"><div class="titre-section">Détail par projet</div>';
-  for (const nom of noms) {
-    const w = watchersMap[nom];
-    const cclActif = !!(w && w.actif);
-    const service = serviceCcwProjet(nom);
-    html += '<div class="pl-projet" style="border-left-color:' + couleurProjetResultats(nom) + '">'
-          + '<div class="pl-projet-nom">' + escapeHtml(nom) + '</div>'
-          + '<div class="pl-etat"><span class="pl-dot" style="background:'
-          + (cclActif ? '#2e8b57' : '#c0392b') + '"></span>CCL '
-          + (cclActif ? ('actif (pid ' + escapeHtml(w.pid) + ')') : 'arrêté') + '</div>';
-    if (service) {
-      html += '<div class="pl-etat"><span class="pl-dot" style="background:'
-            + couleurEtatCcw(service.etat) + '"></span>CCW '
-            + escapeHtml(service.etat || '?') + '</div>';
-    }
-    html += '</div>';
-  }
-  // Actualisation des services CCW une fois connus (le cas « inconnu » est déjà
-  // couvert par le lien « Vérifier » du bloc de résumé ci-dessus).
-  if (ccwProjetsConnus.length) {
-    html += '<div class="pl-lien" onclick="sidebarChargerCcw()">🔄 Actualiser les services CCW</div>';
-  }
   zone.innerHTML = html;
 }
 
-// Actions contextuelles (issue #375) : projet/issue actuellement sélectionnés
-// (projetCourant/numeroCourant). Aucun fetch réseau — les données viennent de
-// listeIssuesResultats (déjà en mémoire) et ccwProjetsConnus.
+// Actions contextuelles (issue #375, zone basse fixe depuis #377) : projet/
+// issue actuellement sélectionnés (projetCourant/numeroCourant). Aucun fetch
+// réseau — les données viennent de listeIssuesResultats (déjà en mémoire) et
+// ccwProjetsConnus. Cible #pl-zone-actions, sous #pl-zone-monitoring
+// (toujours visible, voir rendrePanneauLateralMonitoring) ; se vide (donc
+// disparaît, séparateur compris) quand aucune ligne n'est sélectionnée.
 function rendrePanneauLateralActions() {
-  const zone = document.getElementById('panneau-lateral-resultats');
+  const zone = document.getElementById('pl-zone-actions');
   if (!zone) return;
   const nom = projetCourant, numero = numeroCourant;
+  if (!nom || !numero) { zone.innerHTML = ''; return; }
   const it = listeIssuesResultats.find(
     x => x.projet === nom && String(x.number) === String(numero));
   const nomsLabels = it ? (it.labels || []).map(l => ((l && l.name) || l || '').toLowerCase()) : [];
# ── Zone modifiée : ligne 1935 (18 ligne(s)) dans l'ancienne version → ligne 1923 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1935,18 +1923,19 @@ function rendrePanneauLateralActions() {
     && !nomsLabels.includes('done') && !nomsLabels.includes('needs-human');
   const service = serviceCcwProjet(nom);
 
-  let html = '<div class="titre-section" style="margin-top:0">Actions</div>'
-           + '<div class="pl-issue-ref">' + escapeHtml(nom) + ' #' + escapeHtml(numero) + '</div>'
+  let html = '<hr class="pl-sep">'
+           + '<div class="titre-section" style="margin-top:0">Actions — '
+           + escapeHtml(nom) + ' #' + escapeHtml(numero) + '</div>'
            + '<div class="pl-actions">'
            + '<button onclick="sidebarRelancerWatcherCCL(\'' + escapeHtml(nom) + '\', this)">'
-           + '🔁 Relancer watcher CCL</button>';
+           + '↺ Relancer watcher CCL</button>';
   if (interromptible) {
     html += '<button class="danger" onclick="interrompreIssue(\'' + escapeHtml(nom) + '\', '
           + Number(numero) + ')">⛔ Interrompre l\'issue</button>';
   }
   if (service) {
     html += '<button onclick="ccwRedemarrerProjet(\'' + escapeHtml(nom) + '\', this)">'
-          + '🔁 Relancer watcher CCW</button>'
+          + '↺ Relancer watcher CCW</button>'
           + '<button disabled title="Prévu par l\'issue #378 (à venir) — pas encore implémenté">'
           + '🔒 Nettoyer verrous CCW + redémarrer</button>';
   }
# ── Zone modifiée : ligne 1978 (6 ligne(s)) dans l'ancienne version → ligne 1967 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1978,6 +1967,38 @@ async function sidebarRelancerWatcherCCL(nom, btn) {
   await rafraichirPanneauLateralResultats();
 }
 
+// Relance séquentiellement TOUS les watchers CCL actuellement éteints (issue
+// #377), un par un via le même endpoint que sidebarRelancerWatcherCCL. Relit
+// /watchers juste avant de lancer les relances plutôt que de réutiliser la
+// liste déjà affichée dans le panneau, potentiellement périmée entre le rendu
+// et le clic.
+async function sidebarRelancerTousEteints(btn) {
+  if (btn) { btn.disabled = true; btn.textContent = 'Relance…'; }
+  try {
+    const repW = await fetch('/watchers');
+    const liste = await repW.json();
+    const watchersMap = {};
+    liste.forEach(w => { watchersMap[w.nom] = w; });
+    const eteints = nomsProjetsDisponibles()
+      .filter(n => !(watchersMap[n] && watchersMap[n].actif));
+    for (const nom of eteints) {
+      try {
+        await fetch('/lancer-watcher', {
+          method: 'POST',
+          headers: {'Content-Type': 'application/json'},
+          body: JSON.stringify({projet: nom, relancer: true})
+        });
+      } catch(e) { /* une relance en échec ne doit pas bloquer les suivantes */ }
+    }
+  } catch(e) {
+    alert('Erreur réseau : ' + e.message);
+  }
+  const panneauWatchers = document.getElementById('panneau-watchers');
+  if (panneauWatchers && panneauWatchers.classList.contains('actif')) await chargerWatchers();
+  if (btn) { btn.disabled = false; btn.textContent = '↺ Relancer tous les éteints'; }
+  await rafraichirPanneauLateralResultats();
+}
+
 // Sélectionne la première ligne encore visible SANS charger son détail (voir
 // selectionnerLigne, issue #261) ; vide le détail s'il n'y a plus rien à
 // afficher. Appelée à l'ouverture de l'onglet, à chaque changement de filtre
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 52997cf..4757cba 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 247 (11 ligne(s)) dans l'ancienne version → ligne 247 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -247,11 +247,17 @@
 
     </div><!-- /resultats-liste-col -->
 
-    <!-- Panneau latéral droit (issue #375) : monitoring passif des watchers
-         (aucune issue sélectionnée) ou actions contextuelles (issue
-         sélectionnée). Peuplé par rafraichirPanneauLateralResultats()
-         (static/js/app.js) — jamais rempli côté serveur. -->
-    <div id="panneau-lateral-resultats" class="panneau-lateral"></div>
+    <!-- Panneau latéral droit (issue #375, restructuré #377) : deux zones
+         empilées, peuplées par rafraichirPanneauLateralResultats()
+         (static/js/app.js) — jamais rempli côté serveur.
+         - #pl-zone-monitoring : monitoring de l'infrastructure, TOUJOURS
+           visible (VM CCW, watchers CCL, services CCW).
+         - #pl-zone-actions : actions contextuelles sur l'issue sélectionnée,
+           vide (donc invisible) tant qu'aucune ligne n'est sélectionnée. -->
+    <div id="panneau-lateral-resultats" class="panneau-lateral">
+      <div id="pl-zone-monitoring"></div>
+      <div id="pl-zone-actions"></div>
+    </div>
 
    </div><!-- /resultats-layout -->
   </div>
