bb64c5d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bb64c5d
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 09:42:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #328 : suppression code mort animation pioche (compterLettres, nouvellesLettresArrivees, anciennesLettres)
    
    Ces fonctions et cette variable étaient devenues obsolètes suite aux
    itérations #325-#327 sur l'animation de pioche (Python fournit désormais
    directement lettres_pioches).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5ce06fe..d58c1ce 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.js
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 935 (36 ligne(s)) dans l'ancienne version → ligne 935 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -935,36 +935,6 @@ document.addEventListener('DOMContentLoaded', async () => {
         panneauSelection = null;
     }
 
-    /** Table d'effectifs {lettre|valeur -> nombre} pour comparer deux chevalets
-     *  sans être sensible à l'ordre (issue #317). */
-    function compterLettres(lettres) {
-        const compte = new Map();
-        (lettres || []).forEach((l) => {
-            const cle = (l.joker ? '*' : l.lettre) + '|' + l.valeur;
-            compte.set(cle, (compte.get(cle) || 0) + 1);
-        });
-        return compte;
-    }
-
-    /** Lettres présentes dans ``nouvelles`` en plus de ``anciennes`` (multi-
-     *  ensemble, issue #317) : celles qui viennent d'arriver sur le chevalet
-     *  (tirage après une pose, échange…), à distinguer des lettres déjà là qui
-     *  n'ont fait que changer de position dans le tableau. */
-    function nouvellesLettresArrivees(anciennes, nouvelles) {
-        const restantes = compterLettres(anciennes);
-        const arrivees = [];
-        (nouvelles || []).forEach((l) => {
-            const cle = (l.joker ? '*' : l.lettre) + '|' + l.valeur;
-            const dispo = restantes.get(cle) || 0;
-            if (dispo > 0) {
-                restantes.set(cle, dispo - 1);
-            } else {
-                arrivees.push(l);
-            }
-        });
-        return arrivees;
-    }
-
     let animationPiocheEnCours = false;
 
     /**
# ── Zone modifiée : ligne 1026 (7 ligne(s)) dans l'ancienne version → ligne 996 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1026,7 +996,6 @@ document.addEventListener('DOMContentLoaded', async () => {
      */
     function appliquerEtatChevalet(payload) {
         const premierAppel = etatChevalet === null;
-        const anciennesLettres = etatChevalet ? etatChevalet.lettres : [];
         etatChevalet = payload || {};
 
         // Changement de tour (issue #100) : ``index_reference`` étant constant pour
