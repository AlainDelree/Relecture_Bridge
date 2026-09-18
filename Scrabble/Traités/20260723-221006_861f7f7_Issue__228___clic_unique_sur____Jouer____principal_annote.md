# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 861f7f7920d17c833b483af119755caa30380b02
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 22:10:06 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #228 : clic unique sur « Jouer » principal depuis la modale de score
    
    Le calque plein écran de #score-modale captait le premier clic sur
    #btn-valider comme un « clic dehors » et se contentait de fermer la
    modale, imposant un second clic pour poser le coup (double clic résiduel
    de #225).
    
    creerModaleScore (commun.js) accepte désormais un hook facultatif
    surClicDehors(evt) appelé avant la fermeture par défaut. jeu.js le
    fournit : si le clic tombe sur le rectangle de #btn-valider et qu'un
    coup est en attente (bouton actif), jouerCoup() est appelé (il referme
    lui-même la modale) et la pose se fait en un seul clic. Sinon,
    comportement inchangé (fermeture simple).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/commun.js b/src/scrabble/ui/web/commun.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index cdeb92d..d9a98e5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/commun.js
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/commun.js
# ── Zone modifiée : ligne 305 (7 ligne(s)) dans l'ancienne version → ligne 305 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -305,7 +305,11 @@
      * ``auFermer`` (facultatif, issue #128) est appelé à chaque fermeture, quelle
      * qu'en soit l'origine (bouton, clic sur le fond) : l'écran de jeu s'en sert
      * pour retirer la surbrillance du coup consulté et rendre la main au dernier
-     * coup réel. Renvoie un objet {afficher, afficherSansDetail, fermer}.
+     * coup réel. ``surClicDehors(evt)`` (facultatif, issue #228) intercepte le
+     * clic sur le calque de fond avant la fermeture : s'il renvoie ``true``, il a
+     * traité le clic lui-même (p. ex. poser le coup quand le clic vise le
+     * « Jouer » principal masqué) et la fermeture par défaut est annulée.
+     * Renvoie un objet {afficher, afficherSansDetail, fermer}.
      */
     function creerModaleScore(refs) {
         function fermer() {
# ── Zone modifiée : ligne 368 (6 ligne(s)) dans l'ancienne version → ligne 372 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -368,6 +372,17 @@
         }
         refs.modale.addEventListener('click', (evt) => {
             if (evt.target === refs.modale) {
+                // Clic sur le calque de fond : par défaut on ferme simplement.
+                // Mais le consommateur peut fournir ``surClicDehors`` (issue #228)
+                // pour intercepter d'abord ce clic : le calque plein écran masque
+                // les boutons du bandeau, et un clic « dehors » peut en réalité
+                // viser le « Jouer » principal. Si le hook renvoie ``true``, il a
+                // pris le clic en charge (et refermé la modale lui-même) ; sinon
+                // on conserve la fermeture simple habituelle.
+                if (typeof refs.surClicDehors === 'function'
+                    && refs.surClicDehors(evt)) {
+                    return;
+                }
                 fermer();
             }
         });
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index 9909a43..09b8ecd 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 139 (6 ligne(s)) dans l'ancienne version → ligne 139 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -139,6 +139,23 @@ document.addEventListener('DOMContentLoaded', async () => {
             retirerSurbrillanceCoupConsulte();
             if (btnScoreJouer) btnScoreJouer.hidden = true;
         },
+        // Clic « dehors » sur le calque de la modale (issue #228, suite de #225).
+        // Ce calque plein écran (z-index 100) recouvre le bandeau d'actions : un
+        // clic sur le bouton « Jouer » principal (#btn-valider) est alors capté
+        // ici comme un clic dehors et ne faisait que fermer la modale, imposant
+        // un second clic pour poser réellement le coup. Si le clic tombe sur le
+        // rectangle de #btn-valider et qu'un coup est en attente (bouton actif),
+        // on pose le coup en un seul clic ; jouerCoup() referme lui-même la
+        // modale. Sinon on renvoie false : fermeture simple habituelle.
+        surClicDehors: (evt) => {
+            if (btnValider.disabled) return false;
+            const r = btnValider.getBoundingClientRect();
+            const surBouton = evt.clientX >= r.left && evt.clientX <= r.right
+                && evt.clientY >= r.top && evt.clientY <= r.bottom;
+            if (!surBouton) return false;
+            jouerCoup();
+            return true;
+        },
     });
 
     // Thèmes reconnus (alignés avec scrabble.config.THEMES_PLATEAU et le CSS).
