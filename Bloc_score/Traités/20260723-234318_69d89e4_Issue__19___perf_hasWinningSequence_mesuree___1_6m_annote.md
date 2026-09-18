# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 69d89e465c6279851b28c0df1e432ad0e7af2a34
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 23:43:18 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #19 : perf hasWinningSequence mesuree (~1.6ms pire cas) documentee dans le code

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-jeu.html b/bloc-jeu.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 89f9fb2..6cdc50d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-jeu.html
# ── Version APRÈS ce commit.
+++ b/bloc-jeu.html
# ── Zone modifiée : ligne 1443 (6 ligne(s)) dans l'ancienne version → ligne 1443 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1443,6 +1443,16 @@
   // récursivement avec le reste des pièces. Retourne true dès la première séquence complète
   // trouvée (sortie anticipée). Cas de base : plus aucune pièce → true. Pur : ne touche jamais
   // à l'état réel du jeu.
+  //
+  // Perf (issue #19, point 6) — mesurée sous Node 18, réplique exacte de l'algo, 3 grandes
+  // pièces (3x3 + deux lignes de 5) sur scénarios difficiles (grille quasi-pleine, damier bas
+  // forçant un retour `false` après exploration exhaustive) :
+  //   pire cas ≈ 1,6 ms (max), ≈ 0,4 ms (moyenne) — bien en dessous du seuil ~100–150 ms.
+  // Les effacements de lignes/colonnes simulés font s'effondrer la grille à chaque niveau, ce
+  // qui élague drastiquement l'arbre et déclenche des sorties anticipées : aucune optimisation
+  // (mémoïsation / limite de profondeur / élagage supplémentaire) n'est nécessaire à ce stade.
+  // Piste si le plateau ou le nombre de pièces grossissait : mémoïser sur une empreinte de la
+  // grille + multiset de pièces restantes pour couper les branches équivalentes.
   function hasWinningSequence(pieces, gridSnapshot){
     if(pieces.length === 0) return true;
     for(let i=0;i<pieces.length;i++){
