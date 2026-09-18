# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 51578b6599991f5ce38d73ffe3d1c6958a1927d3
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 20:49:16 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #227 : animation de feu d'artifice enrichie à la victoire du joueur
    
    Ajoute une célébration de fin de partie GAGNÉE par le joueur humain, plus
    longue et plus fournie que le feu d'artifice d'un Scrabble.
    
    - jeu.html : nouveau calque plein écran #victoire-fete (pointer-events: none),
      au-dessus de la modale de fin, purement décoratif.
    - jeu.js : fonction celebrerVictoire() — 9 salves étalées sur ~5 s, chacune
      avec éclair central et 26-37 particules (formes carrées/rondes, 12 couleurs,
      retombée gravitaire). Déclenchée dans rendreFinPartie() uniquement si le
      joueur humain figure parmi les gagnants, à l'ouverture unique de la modale.
      Repli sobre (toast seul) en prefers-reduced-motion.
    - jeu.css : styles .victoire-fete / .eclat-flash / .particule-victoire /
      .victoire-toast + keyframes, et neutralisation en mouvement réduit.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9b8c9ba..6674a80 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 1423 (6 ligne(s)) dans l'ancienne version → ligne 1423 (125 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1423,6 +1423,125 @@ body {
     }
 }
 
+/* --------------------------------------------------------------------------- */
+/* Célébration de fin de partie GAGNÉE : feu d'artifice enrichi (issue #227)    */
+/* --------------------------------------------------------------------------- */
+/* Calque plein écran, TOUJOURS transparent aux clics (pointer-events: none). À
+   la différence du Scrabble (#scrabble-fete, z-index 50, SOUS les modales), ce
+   calque est placé AU-DESSUS de la modale de fin (z-index 100) pour que le feu
+   d'artifice reste pleinement visible par-dessus le fond assombri de la modale,
+   sans jamais bloquer l'accès au score final ni aux boutons (les particules sont
+   éparses, brèves et non interactives). Le JS (celebrerVictoire) y injecte
+   plusieurs salves étalées sur ~5 s, puis vide le calque. */
+.victoire-fete {
+    position: fixed;
+    inset: 0;
+    z-index: 110;            /* au-dessus de .modale (100) — décor non bloquant */
+    pointer-events: none;    /* n'intercepte jamais un clic */
+    overflow: hidden;
+}
+
+/* Éclair d'ouverture d'une salve : petit halo radial qui gonfle et s'efface,
+   marquant le point d'explosion. left/top (position de la salve) sont fixés par
+   le JS en pourcentage du viewport. */
+.victoire-fete .eclat-flash {
+    position: absolute;
+    width: 26px;
+    height: 26px;
+    margin: -13px 0 0 -13px;   /* centre le halo sur le point (left, top) */
+    border-radius: 50%;
+    background: radial-gradient(circle, var(--col, #fff) 0%, transparent 70%);
+    opacity: 0;
+    will-change: transform, opacity;
+    animation: victoire-flash 0.6s ease-out both;
+}
+
+@keyframes victoire-flash {
+    0%   { transform: scale(0.2); opacity: 0.9; }
+    100% { transform: scale(3.6); opacity: 0; }
+}
+
+/* Une particule de la gerbe. Carré par défaut, ronde avec .etincelle-ronde, pour
+   varier les formes. Sa position d'explosion (left/top), sa trajectoire radiale
+   (--dx, --dy), sa retombée gravitaire (--chute), sa rotation (--rot) et sa
+   couleur (--col) sont fixées par le JS. */
+.victoire-fete .particule-victoire {
+    position: absolute;
+    width: 11px;
+    height: 11px;
+    margin: -5px 0 0 -5px;     /* centre la particule sur le point d'explosion */
+    background: var(--col, var(--couleur-primaire));
+    border-radius: 2px;
+    opacity: 0;
+    will-change: transform, opacity;
+    animation: victoire-eclat 1.8s ease-out both;
+}
+
+.victoire-fete .particule-victoire.etincelle-ronde {
+    border-radius: 50%;
+}
+
+@keyframes victoire-eclat {
+    0% {
+        transform: translate(0, 0) scale(0.3) rotate(0deg);
+        opacity: 1;
+    }
+    12% {
+        opacity: 1;
+    }
+    100% {
+        /* jaillissement radial (--dx, --dy) + retombée gravitaire (--chute) */
+        transform:
+            translate(var(--dx, 0px), calc(var(--dy, 0px) + var(--chute, 80px)))
+            scale(1) rotate(var(--rot, 180deg));
+        opacity: 0;
+    }
+}
+
+/* Bandeau festif « 🏆 Victoire ! », en complément du feu d'artifice et de la
+   modale de fin. Centré en haut, purement décoratif (calque en pointer-events:
+   none). Reste visible ~5 s le temps de la célébration. */
+.victoire-fete .victoire-toast {
+    position: absolute;
+    top: 8%;
+    left: 50%;
+    transform: translateX(-50%);
+    padding: 0.7rem 1.7rem;
+    background: var(--couleur-primaire);
+    color: #fff;
+    font-size: clamp(1.3rem, 5vw, 2.2rem);
+    font-weight: 800;
+    letter-spacing: 0.02em;
+    border-radius: var(--rayon-bordure);
+    box-shadow: var(--ombre);
+    white-space: nowrap;
+    animation: victoire-toast-apparition 5s ease-out both;
+}
+
+@keyframes victoire-toast-apparition {
+    0%   { opacity: 0; transform: translateX(-50%) translateY(-14px) scale(0.9); }
+    5%   { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
+    90%  { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
+    100% { opacity: 0; transform: translateX(-50%) translateY(-8px) scale(0.98); }
+}
+
+/* Accessibilité : en mouvement réduit, le JS n'injecte ni salves ni particules
+   (seul le toast est affiché). On neutralise par sécurité toute animation
+   résiduelle et on fige le toast statiquement le temps du nettoyage. */
+@media (prefers-reduced-motion: reduce) {
+    .victoire-fete .particule-victoire,
+    .victoire-fete .eclat-flash {
+        animation: none;
+        opacity: 0;
+    }
+
+    .victoire-fete .victoire-toast {
+        animation: none;
+        opacity: 1;
+        transform: translateX(-50%);
+    }
+}
+
 /* --------------------------------------------------------------------------- */
 /* Toast « +X points » près du panneau du joueur (issue #136)                  */
 /* --------------------------------------------------------------------------- */
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.html b/src/scrabble/ui/web/jeu.html
# (index — ignorable)
index 7d70003..512abc2 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.html
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.html
# ── Zone modifiée : ligne 452 (6 ligne(s)) dans l'ancienne version → ligne 452 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -452,6 +452,16 @@
          est lui aussi plein écran et transparent aux clics. -->
     <div id="points-toasts" class="points-toasts" aria-hidden="true"></div>
 
+    <!-- Calque de célébration de fin de partie GAGNÉE par le joueur humain
+         (issue #227). Feu d'artifice plus long et plus fourni que celui d'un
+         Scrabble : plusieurs salves colorées étalées dans le temps. Superposé
+         plein écran AU-DESSUS de la modale de fin (z-index > .modale) mais
+         totalement transparent aux clics (pointer-events: none via
+         .victoire-fete) : les particules décorent l'écran sans jamais bloquer
+         l'accès au score final ni aux boutons de la modale. En mouvement réduit,
+         seul un message sobre « 🏆 Victoire ! » est affiché. -->
+    <div id="victoire-fete" class="victoire-fete" aria-hidden="true"></div>
+
     <script src="commun.js"></script>
     <script src="jeu.js"></script>
 </body>
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index 6c8d7bd..9909a43 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 354 (6 ligne(s)) dans l'ancienne version → ligne 354 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -354,6 +354,16 @@ document.addEventListener('DOMContentLoaded', async () => {
             modaleFin.hidden = false;
             // Le focus part sur « Rester » : l'action neutre par défaut.
             btnFinRester.focus();
+
+            // Célébration (issue #227) : feu d'artifice de victoire UNIQUEMENT si
+            // le joueur humain de référence figure parmi les gagnants (victoire ou
+            // ex æquo). On ne fête pas une partie perdue par l'humain. Déclenché
+            // ici, dans l'ouverture unique, pour ne jouer qu'une seule fois.
+            const humainGagne = Array.isArray(gagnants) && gagnants.length
+                && (joueurs || []).some((j) => j.humain && gagnants.includes(j.nom));
+            if (humainGagne) {
+                celebrerVictoire();
+            }
         }
     }
 
# ── Zone modifiée : ligne 1827 (6 ligne(s)) dans l'ancienne version → ligne 1837 (109 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1827,6 +1837,109 @@ document.addEventListener('DOMContentLoaded', async () => {
         setTimeout(() => { calque.innerHTML = ''; }, 2600);
     }
 
+    /**
+     * Célébration de FIN DE PARTIE gagnée par le joueur humain (issue #227) :
+     * un feu d'artifice volontairement plus long et plus fourni que celui d'un
+     * Scrabble (``celebrerScrabble``). Là où le Scrabble tire ~32 particules en
+     * une seule salve centrale de ~1,6 s, la victoire enchaîne plusieurs SALVES
+     * (``NB_SALVES``) réparties sur ~5 s, chacune jaillissant d'un point différent
+     * de l'écran avec son propre éclair (flash) et une pluie de particules aux
+     * formes (carrés/ronds) et couleurs variées, avec retombée gravitaire.
+     *
+     * Le calque ``#victoire-fete`` est plein écran, AU-DESSUS de la modale de fin,
+     * mais toujours ``pointer-events: none`` : les particules décorent l'écran
+     * sans jamais masquer durablement ni bloquer le score final et les boutons.
+     * En mouvement réduit, seul le toast statique « 🏆 Victoire ! » est affiché.
+     */
+    function celebrerVictoire() {
+        const calque = document.getElementById('victoire-fete');
+        if (!calque) {
+            return;
+        }
+        calque.innerHTML = '';
+        const reduit = window.matchMedia
+            && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
+
+        const toast = document.createElement('div');
+        toast.className = 'victoire-toast';
+        toast.textContent = '🏆 Victoire ! Bravo 🎉';
+        calque.appendChild(toast);
+
+        if (reduit) {
+            setTimeout(() => { calque.innerHTML = ''; }, 4000);
+            return;
+        }
+
+        // Palette plus riche que celle du Scrabble (6 teintes) : on ajoute or,
+        // orange, rose, cyan, magenta, lime et blanc pour un rendu festif varié.
+        const couleurs = [
+            '#2e7d32', '#1565c0', '#6a1b9a', '#ffd54f', '#ef6d86', '#d21f24',
+            '#ff8f00', '#00bcd4', '#e91e63', '#8bc34a', '#ffffff', '#ffca28',
+        ];
+        const NB_SALVES = 9;         // nombre de salves successives
+        const INTERVALLE = 550;      // ms entre deux salves
+        const DUREE_PARTICULE = 1800; // durée d'animation d'une particule (ms)
+
+        // Lance une salve : un éclair central + une gerbe de particules radiales,
+        // à une position (ox, oy) exprimée en pourcentage du viewport. On évite les
+        // bords extrêmes et on privilégie la moitié haute pour un effet « ciel ».
+        function lancerSalve() {
+            if (!document.body.contains(calque)) {
+                return;
+            }
+            const ox = 12 + Math.random() * 76;   // 12 %..88 % en largeur
+            const oy = 14 + Math.random() * 46;   // 14 %..60 % en hauteur
+            const base = couleurs[Math.floor(Math.random() * couleurs.length)];
+
+            const flash = document.createElement('div');
+            flash.className = 'eclat-flash';
+            flash.style.left = `${ox}%`;
+            flash.style.top = `${oy}%`;
+            flash.style.setProperty('--col', base);
+            calque.appendChild(flash);
+            setTimeout(() => flash.remove(), 700);
+
+            const nb = 26 + Math.floor(Math.random() * 12); // 26..37 particules
+            for (let i = 0; i < nb; i += 1) {
+                const p = document.createElement('div');
+                p.className = 'particule-victoire';
+                if (Math.random() < 0.45) {
+                    p.classList.add('etincelle-ronde');
+                }
+                const angle = Math.random() * Math.PI * 2;
+                const distance = 90 + Math.random() * 160;
+                const dx = Math.cos(angle) * distance;
+                const dy = Math.sin(angle) * distance;
+                p.style.left = `${ox}%`;
+                p.style.top = `${oy}%`;
+                p.style.setProperty('--dx', `${Math.round(dx)}px`);
+                p.style.setProperty('--dy', `${Math.round(dy)}px`);
+                // Retombée gravitaire (chute verticale supplémentaire).
+                p.style.setProperty('--chute', `${60 + Math.round(Math.random() * 100)}px`);
+                p.style.setProperty('--rot', `${Math.round((Math.random() - 0.5) * 720)}deg`);
+                p.style.setProperty('--col', couleurs[Math.floor(Math.random() * couleurs.length)]);
+                calque.appendChild(p);
+                // Retrait individuel après l'animation pour éviter l'accumulation
+                // de nœuds pendant les ~5 s de célébration.
+                setTimeout(() => p.remove(), DUREE_PARTICULE + 200);
+            }
+        }
+
+        lancerSalve();
+        let salves = 1;
+        const minuteur = setInterval(() => {
+            lancerSalve();
+            salves += 1;
+            if (salves >= NB_SALVES) {
+                clearInterval(minuteur);
+            }
+        }, INTERVALLE);
+
+        // Nettoyage final : après la dernière salve et le temps qu'elle s'éteigne.
+        const dureeTotale = NB_SALVES * INTERVALLE + DUREE_PARTICULE + 400;
+        setTimeout(() => { calque.innerHTML = ''; }, dureeTotale);
+    }
+
     /**
      * Toast éphémère « +X points » (issue #136) affiché ~3 s près de la fiche du
      * joueur qui vient de jouer, pour tout coup rapportant des points (humain ou
