5ce108c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5ce108c
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 11:30:14 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #309 : dictionnaire toujours visible + Derniers coups pleine largeur
    
    Les pastilles "Vérification dictionnaire" et "Derniers coups" (popovers
    absolus de .zone-systeme-ligne) deviennent deux blocs permanents pleine
    largeur dans .colonne-gauche, entre .zone-systeme et .zone-joueurs.
    
    - jeu.html : suppression des blocs .verif-dico-ancre et .historique-menu
      de la zone A ; ajout de .zone-historique-permanente et
      .zone-dico-permanente conservant tous les id existants
      (historique-liste, historique-compte, champ-verif, btn-verifier,
      message-brouillon, definition-brouillon).
    - jeu.js : suppression des deux appels C.configurerPopover (dictionnaire
      et historique) et des variables associées (btnOuvrirVerif, verifPopover,
      btnHistorique) devenues obsolètes ; reinitialiserVerifDictionnaire()
      supprimée (n'était appelée que par le popover disparu). verifierMotDictionnaire(),
      ses listeners et rendreHistorique() restent inchangés (fonctionnent par id).
    - jeu.css : nouveaux styles .zone-historique-permanente/.zone-dico-permanente/
      .zone-titre/.historique-liste-permanente ; suppression des règles du
      popover dictionnaire devenues orphelines (.verif-dico-ancre,
      .btn-verif-dico, .verif-dico-icone/-libelle, .verif-dico-popover) et du
      menu déroulant historique (.historique-menu, .historique-resume*) ;
      .historique-liste est conservée (réutilisée par #joker-popover).
    
    pytest : 778 passed.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c46d556..7b8633e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 158 (6 ligne(s)) dans l'ancienne version → ligne 158 (40 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -158,6 +158,40 @@ body {
     gap: 8px;
 }
 
+/* Derniers coups / Dictionnaire : deux blocs permanents pleine largeur
+   (issue #308/#309), entre la zone A (boutons système) et la zone B (joueurs).
+   Même gabarit que les autres zones (.zone-gauche), empilés en colonne. */
+.zone-historique-permanente,
+.zone-dico-permanente {
+    display: flex;
+    flex-direction: column;
+    gap: 6px;
+}
+
+.zone-titre {
+    font-size: 0.85rem;
+    font-weight: 600;
+    color: var(--couleur-texte-secondaire, #555);
+    margin: 0;
+    display: flex;
+    align-items: center;
+    gap: 6px;
+}
+
+/* Liste des derniers coups en flux normal (remplace le popover .historique-liste
+   ci-dessus) : même contenu (.historique-ligne…), plus de position absolue ni
+   d'ombre, bornée en hauteur et défilante comme avant. */
+.historique-liste-permanente {
+    list-style: none;
+    padding: 0;
+    margin: 0;
+    max-height: 180px;
+    overflow-y: auto;
+    display: flex;
+    flex-direction: column;
+    gap: 2px;
+}
+
 /* Zone B : fiches joueurs empilées. Prend une part de la hauteur libre pour
    rester lisible ; ``align-items: stretch`` laisse chaque fiche occuper la
    largeur de la marge. ``justify-content: center`` (issue #190) répartit la
# ── Zone modifiée : ligne 402 (9 ligne(s)) dans l'ancienne version → ligne 436 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -402,9 +436,10 @@ body {
     display: none;
     position: fixed;
     left: 8px;
-    /* Décalé sous la zone du bouton « Vérification dictionnaire » (issue #87).
-       Ce bouton (.verif-dico-ancre) vit lui aussi en position: fixed dans le
-       coin haut-gauche : top:12px + min-height:40px + ombre → bord bas ≈ 52px.
+    /* Décalé sous la zone du bouton « Vérification dictionnaire » (issue #87,
+       ex-``.verif-dico-ancre``, supprimé depuis #308/#309). Ce bouton vivait lui
+       aussi en position: fixed dans le coin haut-gauche : top:12px +
+       min-height:40px + ombre → bord bas ≈ 52px.
        À la largeur d'ouverture par défaut (1320px) et jusqu'au seuil de 1780px,
        le bouton est en icône seule, épinglé dans le coin, et se superposait au
        haut du décor (le « S » recouvert par la loupe). Plutôt que de dépendre
# ── Zone modifiée : ligne 446 (96 ligne(s)) dans l'ancienne version → ligne 481 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -446,96 +481,22 @@ body {
    historique ; l'Issue C nettoiera ce qui devient définitivement obsolète. */
 
 /* --------------------------------------------------------------------------- */
-/* Vérification dictionnaire déportée à gauche (issue #86)                      */
+/* Vérification dictionnaire (issue #86, bloc permanent depuis #308/#309)       */
 /* --------------------------------------------------------------------------- */
-/* Ancre fixe logée dans l'espace libre en haut à gauche de l'écran, entre le
-   décor « SCRABBLE » (gouttière gauche) et la barre du sac. Comme le décor, elle
-   est en position: fixed → elle ne participe JAMAIS au flux et ne peut donc pas
-   « casser » la mise en page du contenu centré, quelle que soit la largeur.
-   Bord DROIT du bouton calé 8px à gauche du bord gauche du contenu centré
-   (.container, largeur max 1180px → demi-largeur 590px). Le bouton grandit vers
-   la GAUCHE dans la gouttière : il ne recouvre donc JAMAIS le contenu (sac,
-   panneaux, plateau), quelle que soit la largeur. Plancher (100vw − 52px) : sur
-   les fenêtres trop étroites où la gouttière disparaît, le bouton reste épinglé
-   dans le coin haut-gauche (icône seule) plutôt que de sortir de l'écran. */
-/* Depuis la refonte #186 (Issue A) la loupe n'est plus une ancre fixe en
-   gouttière : elle vit désormais DANS la zone A (boutons système) de la marge
-   gauche, en flux normal. ``position: relative`` la garde comme contexte
-   d'ancrage du popover (qui s'ouvre en dessous, en surimpression). z-index élevé
-   pour que le popover passe au-dessus des zones voisines de la marge. */
-.verif-dico-ancre {
-    position: relative;
-    z-index: 6;
-}
-
-/* Bouton discret d'ouverture. Repli par défaut (fenêtres étroites, décor masqué,
-   gouttière quasi nulle) : ICÔNE SEULE, compacte et calée dans le coin, pour ne
-   pas empiéter sur le contenu ni disparaître. Cible cliquable confortable
-   (public 80+) grâce au padding et à min-height. Style cohérent avec les boutons
-   secondaires blancs bien contrastés sur le feutre vert. */
-.btn-verif-dico {
-    display: inline-flex;
-    align-items: center;
-    gap: 8px;
-    min-height: 40px;
-    padding: 8px 12px;
-    background: white;
-    color: #444;
-    border: none;
-    border-radius: 999px;
-    box-shadow: var(--ombre);
-    font-size: 0.9rem;
-    font-weight: 600;
-    cursor: pointer;
-}
-
-.btn-verif-dico:hover {
-    background: #f0f0f0;
-}
-
-.verif-dico-icone {
-    font-size: 1.05rem;
-    line-height: 1;
-}
-
-/* Libellé masqué par défaut (icône seule) ; réaffiché seulement quand la
-   gouttière gauche est assez large (voir media query plus bas). Il reste toujours
-   accessible via aria-label/title. */
-.verif-dico-libelle {
-    display: none;
-}
-
-/* Popover contenant le champ + le bouton de vérification (mêmes éléments qu'avant,
-   simplement déplacés). Ouvert au clic sur le bouton (attribut [hidden] retiré
-   par le JS), fermé au clic extérieur ou à la touche Échap. Ancré sous le bouton,
-   à gauche de l'écran. */
-.verif-dico-popover {
-    position: absolute;
-    top: calc(100% + 8px);
-    left: 0;
-    width: min(320px, calc(100vw - 24px));
-    padding: 12px;
-    background: white;
-    border-radius: var(--rayon-bordure);
-    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.28);
-}
-
-.verif-dico-popover[hidden] {
-    display: none;
-}
-
-/* Depuis la refonte #186 la loupe vit dans la marge gauche étroite (zone A) :
-   on la garde en ICÔNE SEULE (le libellé reste masqué, toujours accessible via
-   aria-label/title) pour ne pas élargir la pastille au point de casser la
-   disposition en lignes de la zone A sur une marge de ~300–340px. */
+/* Le bouton loupe + popover (.verif-dico-ancre/.btn-verif-dico/.verif-dico-popover)
+   ont été retirés du HTML : le champ de vérification est désormais un bloc
+   permanent (.zone-dico-permanente, styles plus bas), plus besoin d'ancre ni de
+   popover flottant. .zone-verif-dico/.champ-verif restent inchangées (voir plus
+   bas), elles fonctionnent telles quelles en flux normal. */
 
 /* Barre globale unique (issue #47, point 2) : sac, accès à l'historique et lien
    « Resynchroniser » fusionnés sur une seule ligne horizontale compacte. Se
    replie proprement si la fenêtre est trop étroite. */
 /* L'ancienne barre globale horizontale (``header`` / ``.barre-globale``) a été
    supprimée du DOM par la refonte #186 : son contenu (retour menu, resync, sac,
-   loupe, derniers coups, joker) est réparti dans la zone A de la marge gauche.
-   Les styles de ce contenu (pastilles .sac, .historique-resume, .btn-verif-dico…)
+   joker) est réparti dans la zone A de la marge gauche (loupe et derniers coups
+   en sont ressortis depuis #308/#309, voir .zone-dico-permanente/
+   .zone-historique-permanente). Les styles de ce contenu (pastille .sac…)
    restent définis plus bas et s'appliquent tels quels dans la zone A. */
 
 /* Bandeau de fin de partie (issue #45, point 2 ; étendu issue #133) : hors
# ── Zone modifiée : ligne 697 (93 ligne(s)) dans l'ancienne version → ligne 658 (33 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -697,93 +658,33 @@ body {
 }
 
 /* --------------------------------------------------------------------------- */
-/* Encart d'historique glissant des derniers coups (issue #37)                  */
+/* Encart d'historique glissant des derniers coups (issue #37, bloc permanent   */
+/* pleine largeur depuis #308/#309)                                              */
 /* --------------------------------------------------------------------------- */
-/* Affiché en permanence sous la barre d'infos, au-dessus de la table. Liste les
-   dernières actions (min(nb_joueurs*2, 8) lignes), la plus récente en haut.
-   Chaque ligne cliquable rouvre le détail du coup dans la modale existante ; la
-   couleur de bord distingue humain (bleu) et ordinateur (violet), comme partout
-   ailleurs à l'écran. */
-/* Menu déroulant fusionné dans la barre globale (issue #47, point 2) :
-   l'historique n'est plus une colonne verticale à gauche de la table (issue #45,
-   point 4) mais un <details> compact dans la barre du haut. Replié, il n'occupe
-   que la hauteur de son résumé ; déplié, sa liste s'ouvre en surimpression sous
-   la barre (position absolue) sans repousser la table.
-   Réorganisation (issue #125) : « Derniers coups » est désormais le PREMIER
-   élément de la barre (à gauche) ; c'est le sac qui porte ``margin-left:auto``
-   (voir .sac) et pousse tout le groupe droit (sac, Resynchroniser, Retour au
-   menu) à droite. Le menu s'ouvrant à gauche (``left:0`` ci-dessous) dispose
-   ainsi de la gouttière libre et ne recouvre plus le plateau. */
-
-.historique-menu {
-    position: relative;
-}
-
-/* Bouton déclencheur (issue #144, ex-<summary>) : une petite pastille discrète
-   cohérente avec le sac et le lien « Resynchroniser ». Un chevron est ajouté
-   après le titre (voir .historique-resume-inner::after). Depuis l'abandon du
-   <details> natif au profit de C.configurerPopover, c'est un vrai <button> : on
-   réinitialise donc bordure et police héritées. La mise en page en ligne reste
-   confiée à `.historique-resume-inner`. */
-.historique-resume {
-    width: fit-content;
-    padding: 6px 12px;
-    border: none;
-    border-radius: 999px;
-    background: white;
-    box-shadow: var(--ombre);
-    font-family: inherit;
-    font-size: 0.85rem;
-    font-weight: 600;
-    color: #555;
-    cursor: pointer;
-    white-space: nowrap;
-}
-
-/* Wrapper interne : c'est LUI qui porte la disposition en ligne (titre,
-   compteur, chevron), pour laisser le <summary> à son display natif. */
-.historique-resume-inner {
-    display: inline-flex;
-    align-items: center;
-    gap: 6px;
-}
-
-.historique-resume-inner::after {
-    content: '▾';
-    font-size: 0.7rem;
-    color: #999;
-    transition: transform 0.15s;
-}
-
-.historique-resume[aria-expanded="true"] .historique-resume-inner::after {
-    transform: rotate(180deg);
-}
-
+/* Liste les dernières actions, la plus récente en haut. Chaque ligne cliquable
+   rouvre le détail du coup dans la modale existante ; la couleur de bord
+   distingue humain (bleu) et ordinateur (violet), comme partout ailleurs à
+   l'écran. Le bouton déclencheur + popover (.historique-menu/.historique-resume/
+   ex-popover .historique-liste) ont été retirés du HTML : voir
+   .zone-historique-permanente/.historique-liste-permanente plus bas pour le
+   nouveau bloc permanent. .historique-resume-compte est réutilisée telle quelle
+   pour le compteur du nouveau titre. */
 .historique-resume-compte {
     color: var(--couleur-primaire);
     font-variant-numeric: tabular-nums;
 }
 
-/* Liste déployée = popover (issue #144) : surimpression sous le bouton, largeur
-   fixe raisonnable, DÉFILEMENT vertical dès que l'historique dépasse la hauteur
-   plafond. Ne consomme aucune hauteur de mise en page (position absolue). Le
-   masquage/affichage est piloté par l'attribut [hidden] (posé/retiré par
-   C.configurerPopover), voir la règle [hidden] plus bas. */
+/* .historique-liste (fond blanc, ombre, coins arrondis, popover absolu) n'est
+   plus utilisée par l'historique permanent (remplacée par
+   .historique-liste-permanente) mais reste nécessaire : le popover du joker
+   (.joker-popover plus bas) en hérite toujours le look popover. */
 .historique-liste {
     position: absolute;
     top: calc(100% + 6px);
     left: 0;
     z-index: 60;
-    /* Largeur réduite (issue #125) : 280px au lieu de 320. Le menu étant
-       désormais ancré tout à gauche de la barre, il s'ouvre dans la gouttière
-       verte à gauche du plateau centré ; à 280px il tient dans cette gouttière
-       (fenêtre maximisée) et ne mord donc plus sur le bord gauche du plateau. */
     width: 280px;
     max-width: 80vw;
-    /* L'historique n'étant plus plafonné à 8 lignes (issue #144), la liste peut
-       devenir longue : on borne sa hauteur (relative au viewport pour ne jamais
-       déborder de l'écran) et on la rend scrollable, la plus récente restant en
-       haut. Aucune limite de hauteur ne casse donc la mise en page. */
     max-height: min(360px, 70vh);
     overflow-y: auto;
     background: white;
# ── Zone modifiée : ligne 796 (7 ligne(s)) dans l'ancienne version → ligne 697 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -796,7 +697,6 @@ body {
     gap: 3px;
 }
 
-/* Fermée, la liste (popover) est retirée du flux et de l'affichage. */
 .historique-liste[hidden] {
     display: none;
 }
# ── Zone modifiée : ligne 1689 (13 ligne(s)) dans l'ancienne version → ligne 1589 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1689,13 +1589,7 @@ body {
 }
 
 /* Boutons de base. CONSERVÉS ICI VOLONTAIREMENT (issue #107) bien qu'identiques à
-   commun.css : le bouton « Vérification dictionnaire » (.btn-verif-dico, défini
-   plus haut) réutilise .btn mais lui ajoute des réglages propres (pilule
-   border-radius: 999px, padding réduit) qui — dans l'ordre du cascade — sont
-   écrasés par cette base .btn placée APRÈS lui. Retirer ce bloc au profit de la
-   version de commun.css (chargée AVANT jeu.css) inverserait l'ordre et ferait
-   gagner les réglages « pilule » de .btn-verif-dico, changeant le rendu du bouton.
-   On garde donc ce doublon précis pour laisser le rendu existant strictement
+   commun.css, pour laisser le rendu existant des boutons de cet écran strictement
    inchangé (les autres doublons de commun.css, eux, ont bien été retirés). */
 .btn {
     padding: 10px 18px;
# ── Zone modifiée : ligne 2002 (13 ligne(s)) dans l'ancienne version → ligne 1896 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2002,13 +1896,13 @@ body {
    ========================================================================= */
 
 /* Masquage de TOUTE l'interface de jeu pendant le tirage. ``.container`` porte
-   la barre globale (header) et la table (plateau + fiches) ; ``.decor-scrabble``,
-   ``.verif-dico-ancre`` et ``#message-plateau`` vivent hors du container : on
-   les masque explicitement pour qu'aucun élément ne subsiste derrière l'écran
-   de tirage (point de vigilance issue #168). */
+   la barre globale (header), la loupe/derniers coups (blocs permanents de
+   .colonne-gauche depuis #308/#309) et la table (plateau + fiches) ;
+   ``.decor-scrabble`` et ``#message-plateau`` vivent hors du container : on les
+   masque explicitement pour qu'aucun élément ne subsiste derrière l'écran de
+   tirage (point de vigilance issue #168). */
 body.tirage-en-cours .container,
 body.tirage-en-cours .decor-scrabble,
-body.tirage-en-cours .verif-dico-ancre,
 body.tirage-en-cours #message-plateau {
     display: none !important;
 }
# ── Zone modifiée : ligne 2024 (7 ligne(s)) dans l'ancienne version → ligne 1918 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2024,7 +1918,6 @@ body.tirage-en-cours #message-plateau {
    sur un plateau intermédiaire incorrect. */
 body.jeu-en-init .container,
 body.jeu-en-init .decor-scrabble,
-body.jeu-en-init .verif-dico-ancre,
 body.jeu-en-init #message-plateau {
     display: none !important;
 }
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.html b/src/scrabble/ui/web/jeu.html
# (index — ignorable)
index d2ae398..4e63543 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.html
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.html
# ── Zone modifiée : ligne 44 (18 ligne(s)) dans l'ancienne version → ligne 44 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -44,18 +44,19 @@
             <!-- ============================================================ -->
             <!-- Regroupe ce qui était dispersé dans l'ancienne « barre globale »
                  horizontale du haut (issue #47/#125) : retour au menu,
-                 resynchroniser, sac de lettres restantes, loupe de vérification
-                 dictionnaire (ex-gouttière, issue #86) et menu « Derniers coups »
-                 (issue #37/#144). Le menu joker (issue #168) reste ici : masqué
-                 tant qu'aucun joker n'est en cours de pose. Contenu et id
-                 strictement inchangés — simple relocalisation. -->
+                 resynchroniser, sac de lettres restantes. Le menu joker (issue
+                 #168) reste ici : masqué tant qu'aucun joker n'est en cours de
+                 pose. La loupe de vérification dictionnaire (issue #86) et le
+                 menu « Derniers coups » (issue #37/#144) ont quitté cette zone
+                 pour devenir deux blocs permanents pleine largeur dans
+                 .colonne-gauche (issue #308/#309). -->
             <!-- Zone A répartie sur 2 lignes explicites (issue #189, croquis d'Alain) :
                  la marge élargie (voir .container) dégage assez de place pour
                  regrouper les pastilles côte à côte au lieu de les empiler. Deux
                  conteneurs ``.zone-systeme-ligne`` (rangées flex) portent le
                  découpage :
                    - Ligne 1 : Retour au menu · Resynchroniser (icône seule) · Sac ;
-                   - Ligne 2 : loupe (vérification dictionnaire) · Derniers coups.
+                   - Ligne 2 : menu joker (masqué hors pose de joker).
                  Contenu et id strictement inchangés — seul le regroupement change. -->
             <section class="zone-gauche zone-systeme" aria-label="Actions système">
                 <!-- Ligne 1 : retour au menu, resynchroniser (icône seule), sac. -->
# ── Zone modifiée : ligne 90 (56 ligne(s)) dans l'ancienne version → ligne 91 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,56 +91,11 @@
                     </div>
                 </div>
 
-                <!-- Ligne 2 : loupe de vérification dictionnaire + Derniers coups
-                     (et le menu joker, masqué tant qu'aucun joker n'est en pose). -->
+                <!-- Ligne 2 : le menu joker (masqué tant qu'aucun joker n'est en
+                     pose). Dictionnaire et Derniers coups ont quitté cette ligne
+                     (issue #308/#309) : ce sont désormais deux blocs permanents
+                     pleine largeur, voir plus bas dans .colonne-gauche. -->
                 <div class="zone-systeme-ligne">
-                <!-- Vérification dictionnaire (issue #86) : le champ + le bouton
-                     de vérification vivent dans un popover ouvert au clic sur une
-                     loupe discrète. MÊME comportement / mêmes id (#champ-verif,
-                     #btn-verifier, #message-brouillon) qu'avant : seul
-                     l'emplacement change (ex-gouttière fixe → zone A, issue #186). -->
-                <div class="verif-dico-ancre">
-                    <button id="btn-ouvrir-verif" class="btn btn-verif-dico"
-                            aria-haspopup="dialog" aria-expanded="false"
-                            title="Vérifier si un mot existe dans le dictionnaire">
-                        <span class="verif-dico-icone" aria-hidden="true">🔎</span>
-                        <span class="verif-dico-libelle">Vérification dictionnaire</span>
-                    </button>
-                    <div id="verif-dico-popover" class="verif-dico-popover" role="dialog"
-                         aria-label="Vérification d'un mot dans le dictionnaire" hidden>
-                        <div class="zone-verif-dico">
-                            <input type="text" id="champ-verif" class="champ-verif"
-                                   placeholder="Tapez un mot à tester…"
-                                   aria-label="Mot à vérifier dans le dictionnaire"
-                                   autocomplete="off" spellcheck="false">
-                            <button id="btn-verifier" class="btn btn-secondaire btn-petit">
-                                🔎 Vérifier le mot dans le dictionnaire
-                            </button>
-                        </div>
-                        <p id="message-brouillon" class="message-brouillon" role="status" aria-live="polite"></p>
-                        <!-- Définition affichée sous le verdict quand le mot est
-                             valide (issue #124). -->
-                        <div id="definition-brouillon" class="definition-brouillon" aria-live="polite" hidden></div>
-                    </div>
-                </div>
-
-                <!-- Accès à l'historique glissant (issue #37/#144). Bouton +
-                     popover (C.configurerPopover) : ouverture/fermeture au clic,
-                     fermeture au clic extérieur ou à Échap. La plus RÉCENTE en
-                     haut ; chaque ligne rouvre le détail du score de CE coup. -->
-                <div class="historique-menu" id="historique-menu">
-                    <button id="btn-historique" class="historique-resume"
-                            aria-haspopup="dialog" aria-expanded="false">
-                        <span class="historique-resume-inner">
-                            <span class="historique-resume-titre">🕑 Derniers coups</span>
-                            <span class="historique-resume-compte" id="historique-compte"></span>
-                        </span>
-                    </button>
-                    <ol id="historique-liste" class="historique-liste" role="dialog"
-                        aria-label="Historique des coups de la partie"
-                        aria-live="polite" hidden></ol>
-                </div>
-
                 <!-- Le sélecteur de lettre du joker n'est plus ancré ici (issue
                      #201) : la marge gauche étroite (refonte #186) tronquait sa
                      grille. Il vit désormais en popover fixe posé sur la case du
# ── Zone modifiée : ligne 147 (6 ligne(s)) dans l'ancienne version → ligne 103 (39 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -147,6 +103,39 @@
                 </div><!-- /zone-systeme-ligne (ligne 2) -->
             </section>
 
+            <!-- Derniers coups (issue #308) : bloc permanent pleine largeur.
+                 Remplace l'ancien menu déroulant (#historique-menu) ; même id
+                 #historique-liste/#historique-compte, rendreHistorique() (jeu.js)
+                 les peuple sans changement. -->
+            <section class="zone-gauche zone-historique-permanente">
+                <h3 class="zone-titre">🕑 Derniers coups
+                    <span class="historique-resume-compte" id="historique-compte"></span>
+                </h3>
+                <ol id="historique-liste" class="historique-liste-permanente"
+                    role="log" aria-live="polite"></ol>
+            </section>
+
+            <!-- Dictionnaire (issue #308) : champ toujours visible. Remplace
+                 l'ancien popover (#verif-dico-popover) ; mêmes id (#champ-verif,
+                 #btn-verifier, #message-brouillon, #definition-brouillon),
+                 verifierMotDictionnaire() (jeu.js) inchangée. -->
+            <section class="zone-gauche zone-dico-permanente">
+                <h3 class="zone-titre">🔎 Dictionnaire</h3>
+                <div class="zone-verif-dico">
+                    <input type="text" id="champ-verif" class="champ-verif"
+                           placeholder="Tapez un mot à tester…"
+                           aria-label="Mot à vérifier dans le dictionnaire"
+                           autocomplete="off" spellcheck="false">
+                    <button id="btn-verifier" class="btn btn-secondaire btn-petit">
+                        Vérifier
+                    </button>
+                </div>
+                <p id="message-brouillon" class="message-brouillon" role="status" aria-live="polite"></p>
+                <!-- Définition affichée sous le verdict quand le mot est valide
+                     (issue #124). -->
+                <div id="definition-brouillon" class="definition-brouillon" aria-live="polite" hidden></div>
+            </section>
+
             <!-- ============================================================ -->
             <!-- Zone B : joueurs                                             -->
             <!-- ============================================================ -->
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index a05bc08..d34a776 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 113 (14 ligne(s)) dans l'ancienne version → ligne 113 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -113,14 +113,12 @@ document.addEventListener('DOMContentLoaded', async () => {
     const btnAnnulerEchange = document.getElementById('btn-annuler-echange');
     const messageCoup = document.getElementById('message-coup');
 
-    // Vérification dictionnaire par saisie libre (issue #50/#86) : champ + bouton
-    // logés derrière un popover discret dans la gouttière gauche.
+    // Vérification dictionnaire par saisie libre (issue #50/#86) : champ +
+    // bouton dans un bloc permanent de la colonne gauche (issue #308/#309).
     const champVerif = document.getElementById('champ-verif');
     const btnVerifier = document.getElementById('btn-verifier');
     const messageBrouillon = document.getElementById('message-brouillon');
     const definitionBrouillon = document.getElementById('definition-brouillon');
-    const btnOuvrirVerif = document.getElementById('btn-ouvrir-verif');
-    const verifPopover = document.getElementById('verif-dico-popover');
 
     // Modale de détail du score (issue #35), ici ouverte depuis l'historique.
     // Contrôleur factorisé dans commun.js (issue #90).
# ── Zone modifiée : ligne 1678 (39 ligne(s)) dans l'ancienne version → ligne 1676 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1678,39 +1676,14 @@ document.addEventListener('DOMContentLoaded', async () => {
             verifierMotDictionnaire();
         }
     });
-    // Remet le popover de vérification à zéro (issue #196) : champ vidé, verdict
-    // et définition effacés, pour qu'une réouverture démarre sur un champ vierge
-    // prêt à recevoir une nouvelle recherche (plus besoin d'effacer à la main).
-    function reinitialiserVerifDictionnaire() {
-        champVerif.value = '';
-        afficherMessageBrouillon('');
-        masquerDefinitionBrouillon();
-    }
-
-    // Popover replié (issue #86) : au clic, focus sur le champ ; à la fermeture,
-    // on efface la recherche précédente (issue #196).
-    C.configurerPopover(
-        btnOuvrirVerif, verifPopover,
-        () => { champVerif.focus(); },
-        reinitialiserVerifDictionnaire,
-    );
 
     // ------------------------------------------------------------------ //
-    // Encart d'historique glissant : ouverture/fermeture + clic sur une ligne
+    // Encart d'historique glissant : clic sur une ligne
     // ------------------------------------------------------------------ //
 
-    // Ouverture/fermeture du menu « Derniers coups » (issue #144) : on réutilise
-    // le MÊME mécanisme que « Vérification dictionnaire » (C.configurerPopover) —
-    // clic sur le bouton pour basculer, fermeture au clic EXTÉRIEUR ou à la touche
-    // Échap, mise à jour d'aria-expanded. Cela remplace l'ancienne logique séparée
-    // qui devait forcer la bascule native du <details> sous WebKitGTK (issues
-    // #49/#56/#60) et ne se fermait pas à la perte de focus. La liste
-    // (``historiqueListe``, id #historique-liste) sert de popover : les clics à
-    // l'intérieur (ouverture du détail d'un coup) ne la ferment pas, configurerPopover
-    // stoppant leur propagation vers document.
-    const btnHistorique = document.getElementById('btn-historique');
-    C.configurerPopover(btnHistorique, historiqueListe);
-
+    // Depuis l'issue #308/#309, #historique-liste est un bloc permanent de la
+    // colonne gauche (plus un popover) : seul le clic sur une ligne (ouverture
+    // du détail du coup) reste à câbler ici.
     function entreeHistoriqueDe(li) {
         if (!li || !etat || !Array.isArray(etat.historique)) {
             return null;
