8505fbe

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8505fbe
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 09:13:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #295 : refonte accueil en zones haute/centrale/basse + tuiles de section
    
    Restructure le panneau d'accueil (commun France/Belgicisme) en trois zones :
    titre + drapeaux (haute), sections Joueurs/Continuer dans un fond commun
    (centrale, avec bande tricolore translucide en Belgicisme), boutons
    d'action regroupés côte à côte (basse). Les titres de section adoptent le
    style tuiles Scrabble, en petit format, sur fond vert (France) ou blanc/
    tricolore (Belgicisme).
    
    Corrige au passage deux régressions de contraste révélées par la capture
    WebKitGTK : `.compteur` et les états vides ".vide" (texte blanc + cadre
    translucide pensés pour le tapis vert direct) devenaient illisibles une
    fois posés sur le fond clair de la nouvelle `.zone-centrale` en mode
    France — ajout d'un texte sombre équivalent à celui déjà utilisé en
    Belgicisme. Corrige aussi le chemin de l'image de fond de la bande
    tricolore (`../images/...` invalide, l'image ne se serait pas chargée
    dans l'app réelle).
    
    Valeurs choisies (médianes de la fourchette demandée, à ajuster si besoin) :
    margin-top 3rem sur .container en Belgicisme, opacité 0.55 pour la bande
    tricolore.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 07c3d20..75ad74d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/accueil.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 194 (8 ligne(s)) dans l'ancienne version → ligne 194 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -194,8 +194,20 @@ body.mode-belgicisme {
    (déterminée par son contenu), jamais celle de la fenêtre — vérifié à la
    fois avec 0 joueur/0 partie et avec plusieurs joueurs/parties (le
    drapeau redevient visible en dessous dès la fin du contenu). */
+/* Marge haute (issue #295) : sans elle, `.container::before` (top: -20px)
+   démarre à quelques pixels du bord de la fenêtre et masque quasiment tout le
+   drapeau de fond. `margin-top` (plutôt que `padding-top`) est essentiel ici :
+   une marge externe déplace la boîte de `.container` elle-même (et donc le
+   `::before`, positionné relativement à cette boîte) plus bas dans le body,
+   ce qui ouvre un espace visible AU-DESSUS du panneau ; un `padding-top`
+   aurait laissé la boîte de `.container` ancrée au même endroit et n'aurait
+   fait qu'agrandir le panneau vers le haut, sans jamais révéler le drapeau.
+   3rem choisi au milieu de la fourchette 2.5-4rem demandée : bande de drapeau
+   nettement visible sans pousser le contenu hors écran à 1280×800 (vérifié
+   par capture WebKitGTK, cf. rapport). */
 body.mode-belgicisme .container {
     position: relative;
+    margin-top: 3rem;
 }
 
 body.mode-belgicisme .container::before {
# ── Zone modifiée : ligne 335 (8 ligne(s)) dans l'ancienne version → ligne 347 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -335,8 +347,12 @@ body.mode-belgicisme .parties-en-cours:has(.vide) {
     border-color: rgba(0, 0, 0, 0.25);
 }
 
+/* Largeur identique France/Belgicisme (issue #295) : auparavant 600px fixe,
+   plus étroite que le panneau translucide du mode Belgicisme (clamp ci-dessous,
+   pensé pour `.container::before`). Reprend désormais la même formule dans les
+   deux modes, `.container` étant lui-même « le panneau » évoqué par l'issue. */
 .container {
-    max-width: 600px;
+    max-width: clamp(620px, 94vw, 720px);
     margin: 0 auto;
     padding: 20px;
 }
# ── Zone modifiée : ligne 502 (6 ligne(s)) dans l'ancienne version → ligne 518 (121 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -502,6 +518,121 @@ section h2 {
     text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
 }
 
+/* Titres de section en tuiles Scrabble (issue #295) : « Joueurs » et
+   « Continuer » reprennent le principe des tuiles du titre principal (fond
+   crème, contour doré, relief), en plus petit et alignées à gauche plutôt que
+   centrées. Contrairement aux tuiles du `header h1` (réservées au mode
+   Belgicisme, cf. commentaire plus haut), celles-ci sont volontairement NON
+   scopées à `body.mode-belgicisme` : le texte de l'issue demande qu'elles
+   s'affichent aussi en mode France, posées directement sur le tapis vert. */
+.titre-section-tuiles {
+    display: flex;
+    flex-wrap: wrap;
+    gap: 3px;
+    margin: 0.8rem 0 0.5rem;
+    justify-content: flex-start;
+}
+
+.titre-section-tuiles .lettre-scrabble {
+    display: inline-flex;
+    align-items: center;
+    justify-content: center;
+    font-size: clamp(0.9rem, 2vw, 1.15rem);
+    width: clamp(1.4rem, 3vw, 1.8rem);
+    height: clamp(1.4rem, 3vw, 1.8rem);
+    background: #f5e6c8;
+    color: #4a3418;
+    font-weight: 700;
+    line-height: 1;
+    border-radius: 4px;
+    border: 2px solid #caa02c;
+    box-shadow:
+        inset 1px 1px 0 rgba(255, 250, 230, 0.8),
+        inset -1px -1px 0 rgba(120, 80, 10, 0.65),
+        0 2px 3px rgba(0, 0, 0, 0.4);
+}
+
+/* Mode France uniquement : les tuiles reposent directement sur le tapis vert
+   foncé (pas de panneau blanc dessous, contrairement au mode Belgicisme où
+   elles reposent sur `.zone-centrale`) ; un léger drop-shadow supplémentaire
+   les détache mieux du fond que le seul box-shadow ci-dessus. */
+body:not(.mode-belgicisme) .titre-section-tuiles .lettre-scrabble {
+    filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.45));
+}
+
+/* Zone centrale (issue #295) : enveloppe commune aux sections « Joueurs » et
+   « Continuer ». Fond blanc par défaut (France, ajouté ici : la structure
+   cible de l'issue demande explicitement un fond blanc, absent du bloc CSS
+   fourni littéralement pour `.zone-centrale` — valeur ajoutée pour respecter
+   la structure décrite, à ajuster visuellement si besoin). En Belgicisme, ce
+   blanc sert de base sous la bande tricolore translucide (voir plus bas) :
+   l'empilement (panneau translucide du body, blanc de la zone, photo de
+   drapeau à 55%) donne à cette zone une teinte pastel distincte du reste du
+   panneau, qui reste sobre. `overflow: hidden` maintient la bande tricolore
+   dans les coins arrondis. */
+.zone-centrale {
+    position: relative;
+    overflow: hidden;
+    border-radius: 8px;
+    margin: 0.5rem 0;
+    background: #ffffff;
+}
+
+/* Les sections Joueurs/Continuer perdent leur marge de section générique
+   (24px) une fois réunies dans `.zone-centrale` : sans ce nettoyage (issue
+   #295, point 2g), la marge du bas de `.table-joueurs` créait un vide blanc
+   entre les deux sections, et celle de `.reprise` un vide en bas du panneau,
+   avant même d'atteindre `.zone-boutons`. Un padding uniforme remplace ces
+   marges pour garder un espacement net par rapport aux bords arrondis de la
+   zone et à la bande tricolore dessous. */
+.zone-centrale section {
+    margin-bottom: 0;
+    padding: 0.9rem 1rem;
+}
+
+.zone-centrale section + section {
+    padding-top: 0;
+}
+
+/* Bande tricolore (issue #295, Belgicisme uniquement) : reprend la photo de
+   drapeau belge déjà utilisée en fond de body (issue #292), cette fois
+   localisée à la zone centrale seulement, à 55% d'opacité (valeur médiane
+   raisonnable de la fourchette habituelle de ce fichier — 50 à 95% selon les
+   usages — à ajuster visuellement si le rendu WebKitGTK le montre trop pâle
+   ou trop couvrant, cf. rapport). */
+.bande-tricolore {
+    display: none;
+}
+
+body.mode-belgicisme .bande-tricolore {
+    display: block;
+    position: absolute;
+    inset: 0;
+    background-image: url(images/drapeau-belge.jpg);
+    background-size: 100% 100%;
+    z-index: 0;
+    opacity: 0.55;
+}
+
+body.mode-belgicisme .zone-centrale > *:not(.bande-tricolore) {
+    position: relative;
+    z-index: 1;
+}
+
+/* Zone basse (issue #295) : les trois boutons d'action, côte à côte plutôt
+   qu'empilés dans deux sections séparées. */
+.zone-boutons {
+    display: flex;
+    gap: 0.75rem;
+    padding: 0.75rem 0 0.5rem;
+    flex-wrap: wrap;
+}
+
+.zone-boutons .btn {
+    flex: 1;
+    min-width: 10rem;
+}
+
 /* Liste des joueurs */
 .liste-joueurs {
     background: white;
# ── Zone modifiée : ligne 525 (6 ligne(s)) dans l'ancienne version → ligne 656 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -525,6 +656,19 @@ section h2 {
     border: 2px dashed rgba(255, 255, 255, 0.4);
 }
 
+/* Depuis #295, ces cartes vivent dans `.zone-centrale` (fond blanc dans les
+   deux modes) plutôt que directement sur le tapis vert : le cadre translucide
+   blanc ci-dessus (pensé pour ressortir sur le vert) devenait quasi invisible
+   sur ce fond clair en mode France (constaté par capture WebKitGTK). Reprend
+   le traitement déjà utilisé par le mode Belgicisme (bordure sombre, fond plus
+   couvrant) — moins spécifique que `body.mode-belgicisme ...` ci-dessus, donc
+   sans effet sur ce mode, où l'ancienne règle continue de s'appliquer. */
+.zone-centrale .liste-joueurs:has(.vide),
+.zone-centrale .parties-en-cours:has(.vide) {
+    background: rgba(255, 255, 255, 0.55);
+    border-color: rgba(0, 0, 0, 0.25);
+}
+
 /* Texte de l'état vide : blanc légèrement adouci + ombre portée, lisible sur le
    cadre translucide comme sur le tapis (issue #77). */
 .liste-joueurs .vide {
# ── Zone modifiée : ligne 535 (6 ligne(s)) dans l'ancienne version → ligne 679 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -535,6 +679,13 @@ section h2 {
     text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
 }
 
+/* Même correction que ci-dessus pour le texte : illisible en blanc sur le
+   fond clair de `.zone-centrale` en mode France (#295). */
+.zone-centrale .liste-joueurs .vide {
+    color: #1a1a1a;
+    text-shadow: none;
+}
+
 .joueur-item {
     display: flex;
     align-items: center;
# ── Zone modifiée : ligne 619 (17 ligne(s)) dans l'ancienne version → ligne 770 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -619,17 +770,14 @@ section h2 {
     text-align: center;
     margin-top: 10px;
     font-size: 0.9rem;
-    /* Sur le tapis vert (issue #77) : gris #666 illisible, passé en blanc adouci
-       + ombre portée, comme les autres textes libres de l'écran. */
-    color: rgba(255, 255, 255, 0.9);
-    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
-}
-
-/* Actions */
-.actions {
-    display: flex;
-    gap: 12px;
-    justify-content: center;
+    /* Depuis #295, `.compteur` vit dans `.zone-centrale` (fond blanc dans les
+       deux modes) plutôt que directement sur le tapis vert (#77) : le blanc
+       adouci d'origine y devenait illisible en mode France (constaté par
+       capture WebKitGTK). #333 garde un contraste net sur fond blanc/pastel,
+       cohérent avec le traitement déjà appliqué au reste du texte de
+       `.zone-centrale` en mode Belgicisme. */
+    color: #333;
+    text-shadow: none;
 }
 
 /* Boutons */
# ── Zone modifiée : ligne 670 (10 ligne(s)) dans l'ancienne version → ligne 818 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -670,10 +818,13 @@ section h2 {
     background: #4a148c;
 }
 
+/* `width: 100%` retiré (issue #295) : le bouton vit désormais dans
+   `.zone-boutons` (flex, côte à côte avec les deux autres boutons) plutôt que
+   seul dans sa propre section pleine largeur ; `.zone-boutons .btn` fixe déjà
+   `flex: 1` pour un partage équitable de la largeur disponible. */
 .btn-lancer {
     background: var(--couleur-primaire);
     color: white;
-    width: 100%;
     font-size: 1.1rem;
     padding: 14px;
 }
# ── Zone modifiée : ligne 716 (6 ligne(s)) dans l'ancienne version → ligne 867 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -716,6 +867,12 @@ section h2 {
     text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
 }
 
+/* Même correction que pour `.liste-joueurs .vide` ci-dessus (#295). */
+.zone-centrale .parties-en-cours .vide {
+    color: #1a1a1a;
+    text-shadow: none;
+}
+
 .partie-item {
     display: flex;
     align-items: center;
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.html b/src/scrabble/ui/web/accueil.html
# (index — ignorable)
index 8192822..11cb72e 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.html
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.html
# ── Zone modifiée : ligne 53 (38 ligne(s)) dans l'ancienne version → ligne 53 (65 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -53,38 +53,65 @@
         </div>
 
         <main>
-            <section class="table-joueurs">
-                <h2>Joueurs autour de la table</h2>
-                <div id="liste-joueurs" class="liste-joueurs">
-                    <p class="vide" id="message-vide">Aucun joueur. Ajoutez des joueurs pour commencer.</p>
-                </div>
-                <div class="compteur" id="compteur">
-                    <span id="nb-humains">0</span> humain(s),
-                    <span id="nb-ordinateurs">0</span> ordinateur(s)
-                </div>
-            </section>
+            <!-- Zone centrale (issue #295) : fond blanc (France) ou bande
+                 tricolore (Belgicisme) commun aux sections Joueurs/Continuer,
+                 distinct de la zone haute (titre/drapeaux) et de la zone basse
+                 (boutons) qui restent posées directement sur le tapis vert ou
+                 le fond drapeau. -->
+            <div class="zone-centrale">
+                <div class="bande-tricolore" aria-hidden="true"></div>
+
+                <section class="table-joueurs">
+                    <h2 class="titre-section-tuiles">
+                      <span class="lettre-scrabble">J</span><span
+                      class="lettre-scrabble">o</span><span
+                      class="lettre-scrabble">u</span><span
+                      class="lettre-scrabble">e</span><span
+                      class="lettre-scrabble">u</span><span
+                      class="lettre-scrabble">r</span><span
+                      class="lettre-scrabble">s</span>
+                    </h2>
+                    <div id="liste-joueurs" class="liste-joueurs">
+                        <p class="vide" id="message-vide">Aucun joueur. Ajoutez des joueurs pour commencer.</p>
+                    </div>
+                    <div class="compteur" id="compteur">
+                        <span id="nb-humains">0</span> humain(s),
+                        <span id="nb-ordinateurs">0</span> ordinateur(s)
+                    </div>
+                </section>
+
+                <section class="reprise" id="section-reprise">
+                    <h2 class="titre-section-tuiles">
+                      <span class="lettre-scrabble">C</span><span
+                      class="lettre-scrabble">o</span><span
+                      class="lettre-scrabble">n</span><span
+                      class="lettre-scrabble">t</span><span
+                      class="lettre-scrabble">i</span><span
+                      class="lettre-scrabble">n</span><span
+                      class="lettre-scrabble">u</span><span
+                      class="lettre-scrabble">e</span><span
+                      class="lettre-scrabble">r</span>
+                    </h2>
+                    <div id="parties-en-cours" class="parties-en-cours">
+                        <p class="vide">Aucune partie enregistrée.</p>
+                    </div>
+                </section>
+            </div><!-- /.zone-centrale -->
 
-            <section class="actions">
+            <!-- Zone basse (issue #295) : les trois boutons d'action, réunis
+                 côte à côte hors des sections Joueurs/Continuer. Logique de
+                 visibilité/désactivation inchangée (accueil.js). -->
+            <div class="zone-boutons">
                 <button id="btn-ajouter-humain" class="btn btn-humain">
                     Ajouter un joueur
                 </button>
                 <button id="btn-ajouter-ordinateur" class="btn btn-ordinateur">
                     Ajouter un ordinateur
                 </button>
-            </section>
-
-            <section class="lancement">
                 <button id="btn-lancer" class="btn btn-lancer" disabled>
                     Lancer la partie
                 </button>
-            </section>
-
-            <section class="reprise" id="section-reprise">
-                <h2>Reprendre une partie</h2>
-                <div id="parties-en-cours" class="parties-en-cours">
-                    <p class="vide">Aucune partie enregistrée.</p>
-                </div>
-            </section>
+            </div>
         </main>
       </div><!-- /#vue-config -->
 
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.js b/src/scrabble/ui/web/accueil.js
# (index — ignorable)
index 8d0924b..cb84720 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.js
# ── Zone modifiée : ligne 141 (7 ligne(s)) dans l'ancienne version → ligne 141 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -141,7 +141,7 @@ document.addEventListener('DOMContentLoaded', async () => {
             const p = document.createElement('p');
             p.className = 'message-limite';
             p.textContent = messageLimite;
-            document.querySelector('.actions').after(p);
+            document.querySelector('.zone-boutons').after(p);
         }
 
         // Suivre si un humain a été ajouté
