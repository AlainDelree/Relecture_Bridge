7ea31ba

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7ea31ba
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 15:24:29 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #462 : restaurer LocalStorage cases cochées après maj dynamique DOM

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 688b0dc..89ea337 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1165 (6 ligne(s)) dans l'ancienne version → ligne 1165 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1165,6 +1165,23 @@ function basculerCocheResultat(event, projet, numero) {
   if (coche) copierToutEtDiffDepuisBadge(event, projet, numero);
 }
 
+// Relit le LocalStorage et resynchronise l'état de TOUTES les cases à cocher
+// « résultat » actuellement dans le DOM (issue #462). construireLigneIssueDOM
+// lit déjà le LocalStorage à la CONSTRUCTION d'une ligne, mais rien ne
+// garantissait qu'un futur redessin partiel (heartbeat, SSE) passe par cette
+// construction — ce filet de sécurité resynchronise explicitement après
+// coup, pour que l'état coché/décoché survive à toute mise à jour dynamique
+// du DOM exactement comme il survit à un F5.
+function restaurerCasesCocheesResultats() {
+  document.querySelectorAll('.ligne-issue').forEach(ligne => {
+    const cb = ligne.querySelector('.coche-resultat');
+    if (!cb) return;
+    const coche = estResultatCoche(ligne.dataset.projet, ligne.dataset.numero);
+    cb.checked = coche;
+    ligne.classList.toggle('resultat-traite', coche);
+  });
+}
+
 // Construit l'élément DOM d'UNE ligne d'issue (case à cocher, pastille,
 // badges ✅/Diff/All, titre) — markup PARTAGÉ entre la liste principale de
 // l'onglet Résultats (rendreListeIssues) et la fenêtre de recherche par titre
# ── Zone modifiée : ligne 1335 (6 ligne(s)) dans l'ancienne version → ligne 1352 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1335,6 +1352,7 @@ function rendreListeIssues(reset) {
   }
   appliquerFiltresListe();
   appliquerLargeurTitre();
+  restaurerCasesCocheesResultats();
   majBadgesTempsRestant();
   majPastillesFiltres();
   if (reset) selectionnerPremiereVisible();
# ── Zone modifiée : ligne 1711 (6 ligne(s)) dans l'ancienne version → ligne 1729 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1711,6 +1729,7 @@ function formaterBadgeTempsRestant(badge, t, projet, numero) {
 // Actualise tous les badges de temps restant des lignes ouvertes (recalcul pur,
 // aucun appel réseau). Appelée chaque seconde et après chaque rendu de liste.
 function majBadgesTempsRestant() {
+  restaurerCasesCocheesResultats();
   document.querySelectorAll('#liste-issues .ligne-issue').forEach(ligne => {
     const t = timingIssues[cleTiming(ligne.dataset.projet, ligne.dataset.numero)];
     // Estimation prédictive (issue #108) : affichée JUSTE AVANT le décompte.
# ── Zone modifiée : ligne 1753 (6 ligne(s)) dans l'ancienne version → ligne 1772 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1753,6 +1772,7 @@ function remplacerLigneIssue(ligneAncienne, it) {
   if (ligneAncienne.classList.contains('selectionnee')) nouvelle.classList.add('selectionnee');
   ligneAncienne.replaceWith(nouvelle);
   appliquerFiltresListe();
+  restaurerCasesCocheesResultats();
   majBadgesTempsRestant();
   majPastillesFiltres();
 }
# ── Zone modifiée : ligne 2707 (6 ligne(s)) dans l'ancienne version → ligne 2727 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2707,6 +2727,7 @@ function rendreResultatsRecherche(resultats) {
     };
     zone.appendChild(ligne);
   }
+  restaurerCasesCocheesResultats();
 }
 
 function ouvrirModalRechercheTitre() {
