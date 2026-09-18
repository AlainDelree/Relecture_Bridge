d47e418

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d47e418
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 6 17:05:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #380 : panneau monitoring en overlay flottant lisible
    
    - Panneau latéral droit remplacé par un overlay position:fixed (~360px,
      80vh scrollable, bouton toggle #pl-toggle fixe "📊 Infrastructure"),
      ouvert par défaut à l'entrée dans l'onglet Résultats, fermé par défaut
      sur écran étroit. Layout flex .resultats-layout/.resultats-liste-col
      retiré : la liste des issues reprend toute la largeur.
    - Monitoring : une ligne par watcher CCL / service CCW (point vert/gris,
      sans couleur projet) avec bouton individuel Lancer/Relancer, VM CCW en
      ligne unique.
    - Zone #pl-zone-extras réservée aux futurs boutons, volontairement vide.
    - CSS nettoyé (.pl-chip/.pl-chips/.pl-dot/.pl-etat/.pl-synthese retirés).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b374a99..fce5c2a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (37 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,37 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 6 août 2026 — issue #380
+
+Refonte du panneau latéral de l'onglet Résultats (#375/#376/#377) en
+**panneau flottant** (`position:fixed`, `.panneau-lateral`,
+`static/css/style.css`), lisible et extensible :
+- **Layout** : l'ancien layout flex `.resultats-layout` / `.resultats-liste-col`
+  (colonne fixe 280px) est retiré — la liste des issues reprend toute la
+  largeur. Le panneau devient un overlay ~360px, max-height 80vh scrollable,
+  ombre portée, coin haut-droit. Nouveau bouton toggle fixe `#pl-toggle`
+  (« 📊 Infrastructure », `basculerPanneauLateral`) toujours visible dans
+  l'onglet, qui ouvre/ferme le panneau. Ouvert par défaut à chaque entrée
+  dans l'onglet (`ouvrirPanneauLateralParDefaut`), sauf écran étroit
+  (< 900px) où il reste fermé par défaut.
+- **Monitoring lisible** (`rendrePanneauLateralMonitoring`, `static/js/app.js`) :
+  fini les pastilles colorées par projet, illisibles en 280px — chaque
+  watcher CCL a désormais sa propre ligne (`🟢`/`⚫` + nom + bouton individuel
+  « ▶ Lancer » ou « ↺ Relancer », noir et blanc, sans couleur projet), même
+  format pour les services CCW connus. VM CCW en ligne unique
+  (« 🟢 VM allumée » / « 🔴 VM éteinte » + bouton Démarrer si éteinte). Bouton
+  « ↺ Relancer tous les éteints » conservé si au moins un watcher CCL est
+  éteint. Fonctions `pastillesInline`/`couleurEtatCcw` (obsolètes) retirées.
+- **Zone réservée** `#pl-zone-extras` (`.pl-zone-extras`, vide, s'efface via
+  `:empty` tant qu'inutilisée) ajoutée entre le monitoring et les actions
+  contextuelles, prête à accueillir de futurs boutons sans restructurer le
+  panneau — non remplie par cette issue.
+- Zone actions contextuelles (`rendrePanneauLateralActions`) inchangée sur le
+  fond, seule sa position dans le panneau flottant change.
+- CSS : classes `.pl-chip`/`.pl-chips`/`.pl-dot`/`.pl-etat`/`.pl-synthese`
+  devenues inutiles retirées, remplacées par `.pl-ligne`/`.pl-ligne-libelle`/
+  `.pl-btn-mini`.
+
 ## 6 août 2026 — issue #377
 
 Panneau latéral de l'onglet Résultats (#375/#376) : les deux états
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index 178be7f..cbb0323 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 272 (30 ligne(s)) dans l'ancienne version → ligne 272 (44 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -272,30 +272,44 @@ button.danger:hover{background:#f8d7da}
 .legende-resultats{font-size:12px;color:#888;background:#f8f8f5;
   border:1px solid #e0dfda;border-radius:6px;padding:8px 12px;
   margin-bottom:16px;display:flex;flex-direction:column;gap:2px;line-height:1.55}
-/* Panneau latéral droit de l'onglet Résultats (issue #375) : liste des issues
-   à gauche (flex:1, largeur inchangée), panneau ~280px fixe à droite —
-   monitoring passif des watchers sans issue sélectionnée, actions
-   contextuelles une fois une ligne sélectionnée (voir rafraichirPanneauLateral-
-   Resultats dans app.js). Écran étroit : le panneau repasse sous la liste. */
-.resultats-layout{display:flex;gap:20px;align-items:flex-start}
-.resultats-liste-col{flex:1;min-width:0}
-.panneau-lateral{width:280px;flex-shrink:0;align-self:flex-start;
-  max-height:calc(100vh - 160px);overflow-y:auto;
-  border:1px solid #e0dfda;border-radius:8px;background:#f8f8f5;padding:14px}
+/* Panneau flottant de monitoring de l'onglet Résultats (issue #375→#377,
+   refonte overlay lisible #380) : liste des issues pleine largeur (l'ancien
+   layout flex .resultats-layout / .resultats-liste-col à 280px est retiré),
+   panneau en position:fixed haut-droite basculé par #pl-toggle — monitoring
+   passif des watchers (une ligne par watcher) sans issue sélectionnée,
+   actions contextuelles une fois une ligne sélectionnée (voir
+   rafraichirPanneauLateralResultats dans app.js). Ouvert par défaut à
+   l'entrée dans l'onglet (ouvrirPanneauLateralParDefaut), sauf écran étroit
+   où il reste fermé par défaut (même seuil 900px que le media query CSS). */
+.pl-toggle{position:fixed;top:18px;right:18px;z-index:1001;
+  padding:9px 14px;border:1px solid #ccc;border-radius:8px;background:#fff;
+  font-size:13px;font-weight:600;color:#1a1a18;cursor:pointer;
+  box-shadow:0 2px 8px rgba(0,0,0,.12)}
+.pl-toggle.actif{border-color:#185FA5;color:#185FA5}
+.panneau-lateral{position:fixed;top:64px;right:18px;z-index:1000;
+  width:360px;max-height:80vh;overflow-y:auto;
+  border:1px solid #e0dfda;border-radius:10px;background:#fff;padding:16px;
+  box-shadow:0 6px 24px rgba(0,0,0,.18)}
+.panneau-lateral.ferme{display:none}
 @media (max-width:900px){
-  .resultats-layout{flex-direction:column}
-  .panneau-lateral{width:100%;max-height:none}
+  .panneau-lateral{width:auto;left:18px;right:18px}
 }
 .pl-sous{font-size:11px;color:#999;margin:-4px 0 12px}
-.pl-etat{display:flex;align-items:center;gap:6px;font-size:12px;color:#555;margin-bottom:2px}
-.pl-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
 .pl-lien{font-size:12px;color:#185FA5;cursor:pointer;user-select:none;margin-top:8px;display:inline-block}
 .pl-lien:hover{text-decoration:underline}
-.pl-synthese{background:#f8f8f5;border:1px solid #e0dfda;border-radius:6px;padding:10px 12px;margin-bottom:14px}
-.pl-resume-titre{font-size:13px;font-weight:600;color:#1a1a18;margin:10px 0 4px}
-.pl-chips{display:flex;flex-wrap:wrap;gap:4px 10px;font-size:12px;color:#555}
-.pl-chip{display:inline-flex;align-items:center;gap:5px}
+.pl-resume-titre{font-size:13px;font-weight:600;color:#1a1a18;margin:12px 0 4px}
+.pl-ligne{display:flex;align-items:center;justify-content:space-between;gap:10px;
+  font-size:13px;color:#1a1a18;padding:3px 0}
+.pl-ligne-libelle{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
+.pl-btn-mini{flex-shrink:0;padding:3px 9px;font-size:12px;border:1px solid #ccc;
+  border-radius:6px;background:#f8f8f5;color:#1a1a18;cursor:pointer}
+.pl-btn-mini:hover{background:#eee}
 .pl-btn-vm{margin:6px 0 2px}
+/* Zone réservée aux futurs boutons (issue #380) : volontairement vide pour
+   l'instant — s'efface tant qu'elle ne contient rien (:empty) pour ne pas
+   laisser un espace blanc inutile dans le panneau. */
+.pl-zone-extras{margin:10px 0}
+.pl-zone-extras:empty{display:none;margin:0}
 .pl-sep{border:none;border-top:1px solid #e0dfda;margin:14px 0}
 .pl-actions{display:flex;flex-direction:column;gap:8px}
 .pl-actions button{width:100%}
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index af597eb..2e72feb 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1731 (19 ligne(s)) dans l'ancienne version → ligne 1731 (54 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1731,19 +1731,54 @@ function arreterStreamFinIssue() {
   if (sourceFinIssue) { sourceFinIssue.close(); sourceFinIssue = null; }
 }
 
-// ─── Panneau latéral droit de l'onglet Résultats (issue #375, #377) ───────
-// Deux zones EMPILÉES, non exclusives, pilotées par projetCourant/numeroCourant
-// (mêmes variables que la sélection de ligne, voir selectionnerLigne) :
+// ─── Panneau latéral droit de l'onglet Résultats (issue #375, #377, #380) ──
+// Panneau FLOTTANT (position:fixed, voir .panneau-lateral dans style.css),
+// basculé par #pl-toggle, trois zones EMPILÉES, non exclusives, pilotées par
+// projetCourant/numeroCourant (mêmes variables que la sélection de ligne,
+// voir selectionnerLigne) :
 //  - zone haute (#pl-zone-monitoring) : monitoring passif des watchers CCL+CCW
 //    de tous les projets actifs (rendrePanneauLateralMonitoring), TOUJOURS
 //    rendue, sélection ou non — pour garder l'infra sous les yeux en
-//    travaillant sur une issue (issue #377) ;
+//    travaillant sur une issue (issue #377), une ligne par watcher, noir et
+//    blanc, bouton individuel Lancer/Relancer (issue #380) ;
+//  - zone médiane (#pl-zone-extras) : réservée aux futurs boutons, vide,
+//    voir templates/index.html (issue #380) ;
 //  - zone basse (#pl-zone-actions) : actions contextuelles pour le projet/
 //    l'issue sélectionnés (rendrePanneauLateralActions), sans fetch réseau
 //    (données déjà en mémoire : listeIssuesResultats + ccwProjetsConnus) —
 //    vidée (donc invisible) quand aucune ligne n'est sélectionnée.
 
+// Ouvre le panneau flottant par défaut à chaque entrée dans l'onglet
+// Résultats (issue #380) — sauf sur écran étroit, où il reste fermé par
+// défaut pour ne pas masquer la liste (même seuil que le media query CSS
+// associé, 900px). Un panneau déjà ouvert/fermé manuellement par l'utilisateur
+// est donc réinitialisé à chaque changement d'onglet, comportement voulu.
+function ouvrirPanneauLateralParDefaut() {
+  const panneau = document.getElementById('panneau-lateral-resultats');
+  if (!panneau) return;
+  panneau.classList.toggle('ferme', window.innerWidth < 900);
+  mettreAJourToggleLateral();
+}
+
+// Bascule manuel du panneau flottant (clic sur #pl-toggle).
+function basculerPanneauLateral() {
+  const panneau = document.getElementById('panneau-lateral-resultats');
+  if (!panneau) return;
+  panneau.classList.toggle('ferme');
+  mettreAJourToggleLateral();
+}
+
+// Reflète l'état ouvert/fermé du panneau sur le bouton toggle (accent visuel
+// seulement — le bouton reste cliquable et visible dans les deux états).
+function mettreAJourToggleLateral() {
+  const panneau = document.getElementById('panneau-lateral-resultats');
+  const toggle  = document.getElementById('pl-toggle');
+  if (!panneau || !toggle) return;
+  toggle.classList.toggle('actif', !panneau.classList.contains('ferme'));
+}
+
 function demarrerPanneauLateral() {
+  ouvrirPanneauLateralParDefaut();
   rafraichirPanneauLateralResultats();
   arreterPanneauLateral();
   intervalPanneauLateral = setInterval(rafraichirPanneauLateralResultats, 30000);
# ── Zone modifiée : ligne 1763 (13 ligne(s)) dans l'ancienne version → ligne 1798 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1763,13 +1798,6 @@ async function rafraichirPanneauLateralResultats() {
   rendrePanneauLateralActions();
 }
 
-// Couleur de la pastille CCW, même code que ccwChargerProjets (onglet CCW) —
-// répété volontairement ici plutôt que factorisé : deux appelants seulement,
-// une factorisation forcerait à exposer un utilitaire pour si peu.
-function couleurEtatCcw(etat) {
-  return etat === 'running' ? '#2e8b57' : (etat === 'stopped' ? '#c0392b' : '#888');
-}
-
 // Service CCW connu pour ce projet (ou null), depuis la dernière liste chargée
 // (ccwProjetsConnus) — jamais un fetch direct, voir le commentaire sur cette
 // variable en tête de fichier.
# ── Zone modifiée : ligne 1784 (17 ligne(s)) dans l'ancienne version → ligne 1812 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1784,17 +1812,6 @@ async function sidebarChargerCcw() {
   await ccwChargerProjets();
 }
 
-// Fabrique une liste inline de pastilles « nom » (une par projet), sans retour
-// à la ligne par projet — utilisée par les blocs de résumé synthétiques pour
-// montrer d'un coup d'œil qui est actif (vert) / éteint (rouge).
-function pastillesInline(noms, couleurFn) {
-  if (!noms.length) return '<span style="color:#999">aucun</span>';
-  return noms.map(function(nom) {
-    return '<span class="pl-chip"><span class="pl-dot" style="background:'
-      + couleurFn(nom) + '"></span>' + escapeHtml(nom) + '</span>';
-  }).join(' ');
-}
-
 // Démarre la VM CCW depuis le panneau latéral (même endpoint que l'onglet CCW,
 // ccwDemarrerVm) sans dépendre des éléments DOM propres à cet onglet : le
 // bouton vit ici, dans le panneau de monitoring. Re-rend le panneau ensuite
# ── Zone modifiée : ligne 1810 (13 ligne(s)) dans l'ancienne version → ligne 1827 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1810,13 +1827,14 @@ async function sidebarDemarrerVm(btn) {
 }
 
 // Monitoring de l'infrastructure, TOUJOURS visible en zone haute du panneau
-// (issue #375/#376, restructuré en zone fixe #377), qu'une issue soit
+// (issue #375/#376/#377, refonte lisibilité #380), qu'une issue soit
 // sélectionnée ou non : état de la VM CCW + bouton de démarrage si éteinte,
-// pastilles watchers CCL colorées PAR PROJET (couleurProjetResultats — un
-// point sombre = éteint, couleur vive = actif) + bouton de relance groupée des
-// éteints, pastilles services CCW par projet (ou lien de vérification si aucun
-// service encore connu). Cible #pl-zone-monitoring, indépendante de la zone
-// d'actions contextuelles (#pl-zone-actions) — voir le commentaire d'en-tête.
+// UNE LIGNE PAR WATCHER CCL (point vert/gris foncé, sans couleur projet —
+// lisible en noir et blanc, issue #380) avec bouton individuel Lancer/
+// Relancer + bouton de relance groupée des éteints, une ligne par service CCW
+// (ou lien de vérification si aucun service encore connu). Cible
+// #pl-zone-monitoring, indépendante de la zone d'actions contextuelles
+// (#pl-zone-actions) — voir le commentaire d'en-tête.
 async function rendrePanneauLateralMonitoring() {
   const zone = document.getElementById('pl-zone-monitoring');
   if (!zone) return;
# ── Zone modifiée : ligne 1844 (70 ligne(s)) dans l'ancienne version → ligne 1862 (73 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1844,70 +1862,73 @@ async function rendrePanneauLateralMonitoring() {
     return;
   }
 
-  html += '<div class="pl-synthese">';
-
-  // 1. VM CCW : allumée (vert) / éteinte (rouge) / inconnu (gris).
-  let vmCouleur = '#888', vmTexte = 'VM : état inconnu', vmEteinte = false;
+  // 1. VM CCW : ligne unique, allumée/éteinte/inconnue.
+  let vmTexte = '⚪ VM : état inconnu', vmEteinte = false;
   if (vmStatut && vmStatut.succes) {
     if (!vmStatut.existe) {
-      vmCouleur = '#c0392b'; vmTexte = 'VM introuvable (non créée)';
+      vmTexte = '🔴 VM introuvable (non créée)';
     } else if (vmStatut.etat === 'running') {
-      vmCouleur = '#2e8b57'; vmTexte = 'VM allumée';
+      vmTexte = '🟢 VM allumée';
     } else {
-      vmCouleur = '#c0392b'; vmTexte = 'VM éteinte (' + escapeHtml(vmStatut.etat || '?') + ')';
+      vmTexte = '🔴 VM éteinte (' + escapeHtml(vmStatut.etat || '?') + ')';
       vmEteinte = true;
     }
   } else if (vmStatut && vmStatut.erreur) {
-    vmTexte = 'VM : ' + escapeHtml(vmStatut.erreur);
+    vmTexte = '⚪ VM : ' + escapeHtml(vmStatut.erreur);
   }
-  html += '<div class="pl-etat"><span class="pl-dot" style="background:'
-        + vmCouleur + '"></span>' + vmTexte + '</div>';
+  html += '<div class="pl-ligne"><span class="pl-ligne-libelle">' + vmTexte + '</span>';
   if (vmEteinte) {
-    html += '<button class="pl-btn-vm" onclick="sidebarDemarrerVm(this)">▶ Démarrer la VM</button>';
+    html += '<button class="pl-btn-mini" onclick="sidebarDemarrerVm(this)">▶ Démarrer</button>';
   }
+  html += '</div>';
 
-  // 2. Watchers CCL : une pastille PAR PROJET colorée à la couleur du projet
-  // (couleurProjetResultats), pas juste vert/rouge — un point sombre indique
-  // un watcher éteint, la couleur vive du projet indique un watcher actif
-  // (issue #377), pour repérer d'un coup d'œil LEQUEL est éteint. Bouton de
+  // 2. Watchers CCL : une ligne PAR watcher (issue #380) — point vert = actif,
+  // gris foncé = éteint, sans couleur projet (monitoring noir et blanc, à
+  // distinguer des pastilles colorées de la liste des issues). Bouton
+  // individuel à droite (Lancer si éteint, Relancer si actif) + bouton de
   // relance groupée si au moins un est éteint.
-  const cclActifs  = noms.filter(n => !!(watchersMap[n] && watchersMap[n].actif));
-  const cclEteints = noms.filter(n => !(watchersMap[n] && watchersMap[n].actif));
-  html += '<div class="pl-resume-titre">' + cclActifs.length + '/' + noms.length
-        + ' watchers CCL actifs</div>'
-        + '<div class="pl-chips">'
-        + pastillesInline(cclActifs, couleurProjetResultats)
-        + (cclEteints.length ? ' ' + pastillesInline(cclEteints, () => '#33322f') : '')
-        + '</div>';
+  html += '<div class="pl-resume-titre">Watchers CCL</div>';
+  const cclEteints = [];
+  noms.forEach(function(nom) {
+    const actif = !!(watchersMap[nom] && watchersMap[nom].actif);
+    if (!actif) cclEteints.push(nom);
+    html += '<div class="pl-ligne">'
+          + '<span class="pl-ligne-libelle">' + (actif ? '🟢' : '⚫') + ' ' + escapeHtml(nom) + '</span>'
+          + '<button class="pl-btn-mini" onclick="sidebarRelancerWatcherCCL(\'' + escapeHtml(nom) + '\', this)">'
+          + (actif ? '↺ Relancer' : '▶ Lancer') + '</button>'
+          + '</div>';
+  });
   if (cclEteints.length) {
     html += '<button class="pl-btn-vm" onclick="sidebarRelancerTousEteints(this)">'
           + '↺ Relancer tous les éteints</button>';
   }
 
-  // 3. Résumé services CCW : seulement si des services sont déjà connus.
+  // 3. Services CCW : même format ligne par ligne, seulement si des services
+  // sont déjà connus (aucun polling automatique — voir ccwProjetsConnus en
+  // tête de fichier). Pas de bouton individuel ici : la relance CCW d'un
+  // service reste une action contextuelle liée à une issue sélectionnée
+  // (#pl-zone-actions, ccwRedemarrerProjet), inchangé depuis #375.
+  html += '<div class="pl-resume-titre">Services CCW</div>';
   if (ccwProjetsConnus.length) {
-    const ccwRunning = ccwProjetsConnus.filter(p => p.etat === 'running');
-    const ccwAutres  = ccwProjetsConnus.filter(p => p.etat !== 'running');
-    html += '<div class="pl-resume-titre">' + ccwRunning.length + '/' + ccwProjetsConnus.length
-          + ' services CCW running</div>'
-          + '<div class="pl-chips">'
-          + pastillesInline(ccwRunning.map(p => p.projet), () => '#2e8b57')
-          + (ccwAutres.length ? ' ' + pastillesInline(ccwAutres.map(p => p.projet),
-              nom => couleurEtatCcw((ccwAutres.find(p => p.projet === nom) || {}).etat)) : '')
-          + '</div>';
+    ccwProjetsConnus.forEach(function(p) {
+      const actif = p.etat === 'running';
+      html += '<div class="pl-ligne"><span class="pl-ligne-libelle">'
+            + (actif ? '🟢' : '⚫') + ' ' + escapeHtml(p.projet)
+            + (actif ? '' : ' (' + escapeHtml(p.etat || '?') + ')') + '</span></div>';
+    });
   } else {
     html += '<div class="pl-lien" onclick="sidebarChargerCcw()">🔄 Vérifier les services CCW</div>';
   }
-  html += '</div>';  // .pl-synthese
   zone.innerHTML = html;
 }
 
 // Actions contextuelles (issue #375, zone basse fixe depuis #377) : projet/
 // issue actuellement sélectionnés (projetCourant/numeroCourant). Aucun fetch
 // réseau — les données viennent de listeIssuesResultats (déjà en mémoire) et
-// ccwProjetsConnus. Cible #pl-zone-actions, sous #pl-zone-monitoring
-// (toujours visible, voir rendrePanneauLateralMonitoring) ; se vide (donc
-// disparaît, séparateur compris) quand aucune ligne n'est sélectionnée.
+// ccwProjetsConnus. Cible #pl-zone-actions, sous #pl-zone-monitoring et la
+// zone réservée #pl-zone-extras (toujours visible, voir
+// rendrePanneauLateralMonitoring) ; se vide (donc disparaît, séparateur
+// compris) quand aucune ligne n'est sélectionnée.
 function rendrePanneauLateralActions() {
   const zone = document.getElementById('pl-zone-actions');
   if (!zone) return;
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 4757cba..e6335ea 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 191 (9 ligne(s)) dans l'ancienne version → ligne 191 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -191,9 +191,17 @@
 
   <!-- ─── Onglet Résultats : visualisation des issues ──────────────────── -->
   <div id="panneau-resultats" class="panneau">
-   <div class="resultats-layout">
-    <!-- Colonne gauche : liste + détail (contenu inchangé, issue #375). -->
-    <div class="resultats-liste-col">
+
+    <!-- Bouton toggle du panneau flottant de monitoring (issue #380) : fixe,
+         toujours visible dans l'onglet Résultats (scope via .panneau.actif
+         sur l'ancêtre, pas besoin de le masquer explicitement) — ouvre/ferme
+         #panneau-lateral-resultats (basculerPanneauLateral, static/js/app.js). -->
+    <button id="pl-toggle" class="pl-toggle" onclick="basculerPanneauLateral()">📊 Infrastructure</button>
+
+    <!-- Liste + détail, pleine largeur depuis #380 (l'ancien layout flex
+         .resultats-layout / .resultats-liste-col à 280px est retiré : le
+         panneau de monitoring est maintenant un overlay flottant, voir plus
+         bas). -->
 
     <!-- Boutons toggle : un par projet + « Tous ». Générés dynamiquement. -->
     <div id="filtres-projets" class="filtres-projets"></div>
# ── Zone modifiée : ligne 245 (21 ligne(s)) dans l'ancienne version → ligne 253 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -245,21 +253,27 @@
       <div class="issue-vide">Aucune issue à afficher</div>
     </div>
 
-    </div><!-- /resultats-liste-col -->
-
-    <!-- Panneau latéral droit (issue #375, restructuré #377) : deux zones
-         empilées, peuplées par rafraichirPanneauLateralResultats()
-         (static/js/app.js) — jamais rempli côté serveur.
+    <!-- Panneau flottant de monitoring (issue #375, #376, #377, refonte
+         overlay lisible #380) : position:fixed (voir .panneau-lateral,
+         style.css), basculé par #pl-toggle, ouvert par défaut à l'entrée dans
+         l'onglet (ouvrirPanneauLateralParDefaut). Trois zones empilées,
+         peuplées par rafraichirPanneauLateralResultats() (static/js/app.js)
+         — jamais rempli côté serveur.
          - #pl-zone-monitoring : monitoring de l'infrastructure, TOUJOURS
-           visible (VM CCW, watchers CCL, services CCW).
+           visible, une ligne par watcher CCL/service CCW (VM CCW, watchers
+           CCL, services CCW).
+         - #pl-zone-extras : zone réservée aux futurs boutons (issue #380) —
+           volontairement vide, prête à accueillir de nouveaux boutons sans
+           restructurer le panneau. NE PAS remplir dans cette issue.
          - #pl-zone-actions : actions contextuelles sur l'issue sélectionnée,
            vide (donc invisible) tant qu'aucune ligne n'est sélectionnée. -->
     <div id="panneau-lateral-resultats" class="panneau-lateral">
       <div id="pl-zone-monitoring"></div>
+      <!-- Zone réservée aux futurs boutons (issue #380) : vide intentionnellement. -->
+      <div id="pl-zone-extras" class="pl-zone-extras"></div>
       <div id="pl-zone-actions"></div>
     </div>
 
-   </div><!-- /resultats-layout -->
   </div>
 
   <!-- ─── Onglet 2 : gestion des watchers ──────────────────────────────── -->
