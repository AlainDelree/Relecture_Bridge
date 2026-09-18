6d4709f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6d4709f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 15:32:50 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #463 : ne plus resynchroniser les cases cochées Résultats chaque seconde (régression #462)
    
    - restaurerCasesCocheesResultats() ignore désormais la case en cours de
      focus (document.activeElement), pour ne jamais interférer avec un clic
      en cours de traitement dans basculerCocheResultat.
    - majBadgesTempsRestant() (setInterval 1s) n'appelle plus
      restaurerCasesCocheesResultats() : cette fonction ne reconstruit jamais
      les nœuds DOM des cases, l'appel était donc à la fois superflu et
      source de la course cochage/copie sur Edge/Firefox Windows. La
      restauration reste faite après chaque reconstruction réelle du DOM
      (rendreListeIssues, remplacerLigneIssue, rendreResultatsRecherche).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 89ea337..5e75ba6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1176 (6 ligne(s)) dans l'ancienne version → ligne 1176 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1176,6 +1176,12 @@ function restaurerCasesCocheesResultats() {
   document.querySelectorAll('.ligne-issue').forEach(ligne => {
     const cb = ligne.querySelector('.coche-resultat');
     if (!cb) return;
+    // Garde #463 : ne jamais écraser la case sur laquelle l'utilisateur est
+    // EN TRAIN d'agir (focus actif au moment de l'appel). basculerCocheResultat
+    // gère déjà cette case précise ; la resynchroniser ici en pleine bascule
+    // recréerait la course qui, sur Edge/Firefox Windows, pouvait annuler le
+    // clic avant même que le onchange ne déclenche la copie (régression #462).
+    if (document.activeElement === cb) return;
     const coche = estResultatCoche(ligne.dataset.projet, ligne.dataset.numero);
     cb.checked = coche;
     ligne.classList.toggle('resultat-traite', coche);
# ── Zone modifiée : ligne 1728 (8 ligne(s)) dans l'ancienne version → ligne 1734 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1728,8 +1734,15 @@ function formaterBadgeTempsRestant(badge, t, projet, numero) {
 
 // Actualise tous les badges de temps restant des lignes ouvertes (recalcul pur,
 // aucun appel réseau). Appelée chaque seconde et après chaque rendu de liste.
+// Ne resynchronise PAS les cases cochées (issue #463) : cette fonction ne
+// reconstruit jamais les nœuds DOM des cases, donc rien à restaurer ici — cet
+// appel superflu, exécuté chaque seconde via setInterval, créait une fenêtre
+// de course avec le clic utilisateur (annulait parfois la coche AVANT que le
+// onchange ne déclenche la copie résultat+diff, régression Windows-only
+// introduite par #462). La restauration reste faite là où le DOM est
+// effectivement reconstruit : rendreListeIssues, remplacerLigneIssue,
+// rendreResultatsRecherche.
 function majBadgesTempsRestant() {
-  restaurerCasesCocheesResultats();
   document.querySelectorAll('#liste-issues .ligne-issue').forEach(ligne => {
     const t = timingIssues[cleTiming(ligne.dataset.projet, ligne.dataset.numero)];
     // Estimation prédictive (issue #108) : affichée JUSTE AVANT le décompte.
