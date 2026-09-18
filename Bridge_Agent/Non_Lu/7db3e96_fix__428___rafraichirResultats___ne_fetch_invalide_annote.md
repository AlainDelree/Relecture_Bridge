7db3e96

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7db3e96
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 13:31:50 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #428 : rafraichirResultats() ne fetch/invalide que les projets actifs dans le filtre Résultats

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0bd39ef..ad2b7f2 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 767 (7 ligne(s)) dans l'ancienne version → ligne 767 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -767,7 +767,7 @@ function appliquerListeIssues(liste, noms) {
   rendreListeIssues(true);
 }
 
-async function chargerListeIssues() {
+async function chargerListeIssues(nomsAFetcher) {
   const zone = document.getElementById('liste-issues');
   const noms = nomsProjetsDisponibles();
   if (!noms.length) {
# ── Zone modifiée : ligne 775 (6 ligne(s)) dans l'ancienne version → ligne 775 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -775,6 +775,17 @@ async function chargerListeIssues() {
     return;
   }
 
+  // Restriction optionnelle des projets réellement fetchés (issue #428) :
+  // seul rafraichirResultats() passe ce paramètre (liste des projets actifs
+  // dans le filtre), pour éviter un fetch par projet disponible quand
+  // l'utilisateur n'en regarde qu'un seul. Tous les autres appelants
+  // (chargement initial, SSE fin d'issue…) laissent nomsAFetcher indéfini →
+  // comportement inchangé (tous les projets disponibles).
+  const nomsFetch = Array.isArray(nomsAFetcher)
+    ? nomsAFetcher.filter(nom => noms.includes(nom))
+    : noms;
+  const nomsFetchSet = new Set(nomsFetch);
+
   // 1) Affichage immédiat depuis le cache localStorage, s'il existe.
   let cache = null;
   try { cache = JSON.parse(localStorage.getItem(CLE_CACHE_ISSUES) || 'null'); } catch(e) {}
# ── Zone modifiée : ligne 785 (15 ligne(s)) dans l'ancienne version → ligne 796 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -785,15 +796,16 @@ async function chargerListeIssues() {
     zone.innerHTML = '<div class="issue-vide">Chargement…</div>';
   }
 
-  // 2) Fetch d'arrière-plan des issues de chaque projet (jusqu'à la limite
-  //    par projet réglée par l'utilisateur côté backend, issue #271 — 5 par
-  //    défaut). Le nombre réellement affiché par projet est ensuite plafonné
-  //    par un quota adaptatif dans appliquerFiltresListe() (issue #136), selon
-  //    le nombre de projets actifs dans le filtre — plus de troncature ici.
+  // 2) Fetch d'arrière-plan des issues de chaque projet à recharger (jusqu'à
+  //    la limite par projet réglée par l'utilisateur côté backend, issue #271
+  //    — 5 par défaut). Le nombre réellement affiché par projet est ensuite
+  //    plafonné par un quota adaptatif dans appliquerFiltresListe() (issue
+  //    #136), selon le nombre de projets actifs dans le filtre — plus de
+  //    troncature ici.
   const limite = limiteIssuesProjet();
   majIndicateurListe(true);
   try {
-    const listes = await Promise.all(noms.map(async nom => {
+    const listes = await Promise.all(nomsFetch.map(async nom => {
       try {
         const rep = await fetch('/issues-liste/' + encodeURIComponent(nom)
           + '?limite=' + encodeURIComponent(limite));
# ── Zone modifiée : ligne 810 (8 ligne(s)) dans l'ancienne version → ligne 822 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -810,8 +822,15 @@ async function chargerListeIssues() {
         return [];
       }
     }));
-    // Fusion + tri global par date de création décroissante (plus récentes en premier).
-    const nouvelle = listes.flat().sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
+    // Fusion avec les issues des projets NON refetchés cette fois (fetch
+    // restreint, issue #428) : conservées telles quelles depuis l'état le
+    // plus à jour déjà connu (cache tout juste lu, sinon liste en mémoire),
+    // pour ne pas les faire disparaître de l'onglet Résultats. Puis tri
+    // global par date de création décroissante (plus récentes en premier).
+    const anterieures = (cacheAffiche ? cache : listeIssuesResultats)
+      .filter(it => !nomsFetchSet.has(it.projet));
+    const nouvelle = anterieures.concat(listes.flat())
+      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
 
     // Ne re-render que si la liste a réellement changé : évite de perdre la
     // sélection courante quand le cache était déjà à jour.
# ── Zone modifiée : ligne 1079 (6 ligne(s)) dans l'ancienne version → ligne 1098 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1079,6 +1098,16 @@ function basculerTousLesFiltres() {
   if (!sel || sel.style.display === 'none') selectionnerPremiereVisible();
 }
 
+// Projets actifs dans le filtre de l'onglet Résultats (issue #428) : le
+// sous-ensemble réellement affiché — égal à nomsProjetsDisponibles() quand
+// « Tous » est actif (rien à restreindre), un sous-ensemble strict sinon (y
+// compris vide si tous les projets sont masqués). Utilisé par
+// rafraichirResultats() pour ne fetcher/invalider que ce qui est visible,
+// au lieu de systématiquement tous les projets disponibles.
+function projetsActifsDansFiltreResultats() {
+  return nomsProjetsDisponibles().filter(nom => projetsFiltresActifs.has(nom));
+}
+
 function majClassesBoutonsFiltre() {
   document.querySelectorAll('#filtres-projets .filtre-projet[data-projet]')
     .forEach(btn => {
# ── Zone modifiée : ligne 2808 (19 ligne(s)) dans l'ancienne version → ligne 2837 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2808,19 +2837,38 @@ async function rafraichirResultats() {
   const projet = projetCourant;
   const numero = numeroCourant;
   const etaitCharge = detailCourantCharge;
-  // 1) Cache de la liste.
-  try { localStorage.removeItem(CLE_CACHE_ISSUES); } catch(e) {}
-  // 2) Toutes les clés de cache détail « bridge_cache_detail_* ».
+
+  // Restreint le rechargement aux seuls projets actifs dans le filtre de
+  // l'onglet Résultats (issue #428) : évite un fetch « gh issue list » par
+  // projet DISPONIBLE quand l'utilisateur n'en regarde qu'un sous-ensemble.
+  // « Tous » actif (ou aucun filtre spécifique) → comportement inchangé.
+  const nomsDisponibles = nomsProjetsDisponibles();
+  const nomsActifs = projetsActifsDansFiltreResultats();
+  const rechargeTout = nomsActifs.length === nomsDisponibles.length;
+
+  // 1) Cache de la liste : purge globale seulement si on recharge tout —
+  //    sinon la fusion de chargerListeIssues() préserve les projets non
+  //    refetchés depuis ce même cache, donc pas besoin (ni souhaitable) de
+  //    le vider ici.
+  if (rechargeTout) {
+    try { localStorage.removeItem(CLE_CACHE_ISSUES); } catch(e) {}
+  }
+  // 2) Clés de cache détail « bridge_cache_detail_<projet>_* » — toutes si on
+  //    recharge tout, sinon seulement celles des projets actifs du filtre.
   try {
     const aSupprimer = [];
     for (let i = 0; i < localStorage.length; i++) {
       const cle = localStorage.key(i);
-      if (cle && cle.indexOf(CLE_CACHE_DETAIL) === 0) aSupprimer.push(cle);
+      if (!cle || cle.indexOf(CLE_CACHE_DETAIL) !== 0) continue;
+      if (rechargeTout || nomsActifs.some(nom => cle.indexOf(CLE_CACHE_DETAIL + nom + '_') === 0)) {
+        aSupprimer.push(cle);
+      }
     }
     aSupprimer.forEach(cle => localStorage.removeItem(cle));
   } catch(e) {}
-  // 3) Recharge la liste depuis GitHub.
-  await chargerListeIssues();
+  // 3) Recharge la liste depuis GitHub — restreinte aux projets filtrés,
+  //    sauf si « Tous » est actif (undefined → comportement par défaut).
+  await chargerListeIssues(rechargeTout ? undefined : nomsActifs);
   // 3bis) Recharge aussi les badges de temps restant (issue #270) : depuis la
   // suppression du re-fetch périodique, c'est le SEUL geste qui les remet à
   // jour — sans cet appel, le bouton actualiserait les états d'issues en
