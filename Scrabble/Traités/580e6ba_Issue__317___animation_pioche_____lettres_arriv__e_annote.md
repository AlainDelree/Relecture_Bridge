580e6ba

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 580e6ba
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 08:22:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #317 : animation pioche — lettres arrivées en grand au centre puis vers le chevalet
    
    Détection des nouvelles lettres (diff multi-ensemble ancien/nouveau chevalet)
    dans appliquerEtatChevalet au moment où sig !== panneauSignature. Calque
    plein écran (.pioche-overlay) affichant une tuile de 72x80px par lettre
    arrivée, visible ~900ms puis glissée vers le bas-gauche (direction chevalet)
    en 400ms avant reconstruirePanneau. Repli silencieux si
    prefers-reduced-motion ou animation déjà en cours.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 893e4b0..f26bdbf 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 2205 (3 ligne(s)) dans l'ancienne version → ligne 2205 (84 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2205,3 +2205,84 @@ body.jeu-en-init #message-plateau {
         animation: none;
     }
 }
+
+/* --------------------------------------------------------------------------- */
+/* Animation de pioche : nouvelles lettres en grand au centre (issue #317)      */
+/* --------------------------------------------------------------------------- */
+/* Quand de nouvelles lettres arrivent sur le chevalet (tirage après une pose,
+   échange, passage de tour), le JS (animerNouvellesLettres, jeu.js) crée ce
+   calque plein écran, y place une grande tuile par lettre arrivée, laisse le
+   tout visible ~900ms puis ajoute ``.pioche-overlay-sortie`` : les tuiles
+   glissent vers le bas-gauche (direction du chevalet, situé dans la marge
+   gauche, ``.zone-chevalet``) en s'estompant sur 400ms, avant que le JS ne
+   retire le calque et reconstruise le panneau. Toujours transparent aux clics
+   (pointer-events: none), comme .scrabble-fete/.victoire-fete. */
+.pioche-overlay {
+    position: fixed;
+    inset: 0;
+    z-index: 60;
+    display: flex;
+    align-items: center;
+    justify-content: center;
+    gap: 12px;
+    pointer-events: none;
+}
+
+/* Tuiles nettement plus grandes que celles du chevalet (.panneau-case, 40×44px)
+   pour bien marquer l'arrivée des nouvelles lettres. */
+.pioche-tuile {
+    width: 72px;
+    height: 80px;
+    flex: 0 0 auto;
+    display: flex;
+    align-items: center;
+    justify-content: center;
+    position: relative;
+    border-radius: 6px;
+    font-weight: 700;
+    font-size: 2.2rem;
+    text-transform: uppercase;
+    background: var(--tuile-fond);
+    border: 2px solid var(--tuile-bordure);
+    color: var(--tuile-texte);
+    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
+    animation: pioche-tuile-apparition 0.25s ease-out both;
+    transition: transform 0.4s ease-in, opacity 0.4s ease-in;
+}
+
+.pioche-tuile.joker {
+    border: 2px dashed var(--tuile-joker-bordure);
+    color: var(--tuile-joker-bordure);
+}
+
+.pioche-tuile .val {
+    position: absolute;
+    right: 6px;
+    bottom: 4px;
+    font-size: 0.85rem;
+    font-weight: 600;
+    opacity: 0.8;
+}
+
+@keyframes pioche-tuile-apparition {
+    0%   { opacity: 0; transform: scale(0.5); }
+    100% { opacity: 1; transform: scale(1); }
+}
+
+/* Sortie vers le chevalet : ajoutée par le JS 900ms après l'apparition,
+   déclenche la transition ci-dessus (transform/opacity) sur 400ms. */
+.pioche-overlay-sortie .pioche-tuile {
+    transform: translate(-45vw, 40vh) scale(0.4);
+    opacity: 0;
+}
+
+/* Accessibilité : le JS ne crée même pas ce calque si prefers-reduced-motion
+   est actif (repli silencieux, direct vers reconstruirePanneau). Cette règle
+   ne reste qu'en filet de sécurité si le calque existait déjà avant un
+   changement de préférence en cours de partie. */
+@media (prefers-reduced-motion: reduce) {
+    .pioche-tuile {
+        animation: none;
+        transition: none;
+    }
+}
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index 52677b6..da84a5f 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 935 (6 ligne(s)) dans l'ancienne version → ligne 935 (88 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -935,6 +935,88 @@ document.addEventListener('DOMContentLoaded', async () => {
         panneauSelection = null;
     }
 
+    /** Table d'effectifs {lettre|valeur -> nombre} pour comparer deux chevalets
+     *  sans être sensible à l'ordre (issue #317). */
+    function compterLettres(lettres) {
+        const compte = new Map();
+        (lettres || []).forEach((l) => {
+            const cle = (l.joker ? '*' : l.lettre) + '|' + l.valeur;
+            compte.set(cle, (compte.get(cle) || 0) + 1);
+        });
+        return compte;
+    }
+
+    /** Lettres présentes dans ``nouvelles`` en plus de ``anciennes`` (multi-
+     *  ensemble, issue #317) : celles qui viennent d'arriver sur le chevalet
+     *  (tirage après une pose, échange…), à distinguer des lettres déjà là qui
+     *  n'ont fait que changer de position dans le tableau. */
+    function nouvellesLettresArrivees(anciennes, nouvelles) {
+        const restantes = compterLettres(anciennes);
+        const arrivees = [];
+        (nouvelles || []).forEach((l) => {
+            const cle = (l.joker ? '*' : l.lettre) + '|' + l.valeur;
+            const dispo = restantes.get(cle) || 0;
+            if (dispo > 0) {
+                restantes.set(cle, dispo - 1);
+            } else {
+                arrivees.push(l);
+            }
+        });
+        return arrivees;
+    }
+
+    let animationPiocheEnCours = false;
+
+    /**
+     * Anime l'arrivée de nouvelles lettres sur le chevalet (issue #317) : un
+     * calque plein écran affiche brièvement chaque lettre en grande tuile au
+     * centre de l'écran, puis les fait disparaître vers le bas-gauche (direction
+     * du chevalet, ``.zone-chevalet`` étant dans la marge gauche) avant que
+     * l'appelant ne reconstruise le panneau. Repli silencieux (aucun calque) si
+     * ``prefers-reduced-motion`` est actif — voir ``.panneau-case-vide`` et les
+     * autres animations du fichier pour le même traitement.
+     */
+    function animerNouvellesLettres(lettres) {
+        return new Promise((resolve) => {
+            if (!Array.isArray(lettres) || lettres.length === 0) {
+                resolve();
+                return;
+            }
+            const reduit = window.matchMedia
+                && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
+            if (reduit) {
+                resolve();
+                return;
+            }
+
+            animationPiocheEnCours = true;
+            const overlay = document.createElement('div');
+            overlay.className = 'pioche-overlay';
+            overlay.setAttribute('aria-hidden', 'true');
+            lettres.forEach((l) => {
+                const tuile = document.createElement('div');
+                tuile.className = 'pioche-tuile' + (l.joker ? ' joker' : '');
+                const lettreAffichee = l.joker ? '★' : C.escapeHtml(l.lettre);
+                tuile.innerHTML = `${lettreAffichee}<span class="val">${l.valeur}</span>`;
+                overlay.appendChild(tuile);
+            });
+            document.body.appendChild(overlay);
+
+            const terminer = () => {
+                overlay.remove();
+                animationPiocheEnCours = false;
+                resolve();
+            };
+            setTimeout(() => {
+                overlay.classList.add('pioche-overlay-sortie');
+                overlay.addEventListener('transitionend', terminer, { once: true });
+                // Filet de sécurité si l'événement de transition ne se déclenche
+                // pas (calque sans tuile, focus perdu…).
+                setTimeout(terminer, 500);
+            }, 900);
+        });
+    }
+
     /**
      * Applique un état PRIVÉ du chevalet (lettres du joueur de référence). Poussé
      * par Python via ``window.appliquerEtatChevalet`` après toute mutation, ou
# ── Zone modifiée : ligne 943 (6 ligne(s)) dans l'ancienne version → ligne 1025 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -943,6 +1025,8 @@ document.addEventListener('DOMContentLoaded', async () => {
      * déroulant du plateau (issue #168) : rien à faire ici.
      */
     function appliquerEtatChevalet(payload) {
+        const premierAppel = etatChevalet === null;
+        const anciennesLettres = etatChevalet ? etatChevalet.lettres : [];
         etatChevalet = payload || {};
 
         // Changement de tour (issue #100) : ``index_reference`` étant constant pour
# ── Zone modifiée : ligne 959 (8 ligne(s)) dans l'ancienne version → ligne 1043 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -959,8 +1043,23 @@ document.addEventListener('DOMContentLoaded', async () => {
         // changent pas en posant).
         const sig = signatureLettres(etatChevalet.lettres);
         if (sig !== panneauSignature) {
-            reconstruirePanneau();
             panneauSignature = sig;
+            // Lettres tout juste arrivées (pose/échange/passage de tour, issue
+            // #317) : animées au centre avant de rejoindre le panneau. Ni au tout
+            // premier affichage (rien n'est « arrivé », c'est l'état initial), ni
+            // si une animation est déjà en cours (mise à jour rapprochée : on
+            // rebâtit directement pour rester synchrone avec Python).
+            const arrivees = (premierAppel || animationPiocheEnCours)
+                ? []
+                : nouvellesLettresArrivees(anciennesLettres, etatChevalet.lettres);
+            if (arrivees.length > 0) {
+                animerNouvellesLettres(arrivees).then(() => {
+                    reconstruirePanneau();
+                    rendrePanneau();
+                });
+            } else {
+                reconstruirePanneau();
+            }
         }
 
         // Toute pose/annulation remet la sélection Python à null : on aligne la
