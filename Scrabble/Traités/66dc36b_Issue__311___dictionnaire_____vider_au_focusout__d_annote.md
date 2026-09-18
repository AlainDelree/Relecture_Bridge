66dc36b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 66dc36b
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 11:48:54 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #311 : dictionnaire — vider au focusout, définition en superposition (suite #310)
    
    - jeu.js : restauration de reinitialiserVerifDictionnaire() (vide champVerif,
      messageBrouillon et masque definitionBrouillon), appelée sur focusout de
      .zone-dico-permanente quand le focus quitte complètement la zone.
    - jeu.css : .zone-dico-permanente devient le contexte de positionnement
      (position: relative). .definition-brouillon (liste de gloses, hauteur
      variable, seule responsable du refoulement des fiches joueurs) sort du
      flux en superposition (position: absolute, sans hauteur maximale, fond
      blanc + ombre). .message-brouillon (verdict, une ligne bornée) reste en
      flux pour éviter un chevauchement visuel avec la définition juste en
      dessous — écart volontaire par rapport au CSS suggéré dans l'issue, qui
      mettait les deux en absolute et les aurait superposés l'un sur l'autre.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2362d7f..893e4b0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/jeu.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 174 (6 ligne(s)) dans l'ancienne version → ligne 174 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -174,6 +174,13 @@ body {
     padding: 8px 10px;
 }
 
+/* Contexte de positionnement pour le verdict/la définition en superposition
+   (issue #311) : ils sortent du flux (voir .message-brouillon/.definition-brouillon
+   plus bas) et ne doivent donc plus pousser les fiches joueurs vers le bas. */
+.zone-dico-permanente {
+    position: relative;
+}
+
 /* Le bouton « Derniers coups » (comportement popover restauré par la
    correction #310) doit occuper toute la largeur de la carte pleine largeur,
    au lieu de sa largeur ``fit-content`` d'origine (issue #144). */
# ── Zone modifiée : ligne 1793 (12 ligne(s)) dans l'ancienne version → ligne 1800 (33 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1793,12 +1800,33 @@ body {
     outline-offset: 1px;
 }
 
+/* La définition en superposition par-dessus les fiches joueurs plutôt qu'en
+   flux (issue #311, suite #310) : c'est elle, potentiellement multi-lignes
+   (liste de gloses), qui poussait le reste de la marge gauche vers le bas ;
+   le verdict (.message-brouillon) reste lui en flux normal — une seule ligne
+   déjà bornée par son min-height (commun.css), il ne posait pas ce problème et
+   le laisser en place évite un chevauchement avec la définition juste en
+   dessous. Ancrée à .zone-dico-permanente (position: relative ci-dessus),
+   sans hauteur maximale. Surclasse le margin-top hérité plus bas, même
+   spécificité mais règle plus tardive. */
+.definition-brouillon {
+    position: absolute;
+    top: 100%;
+    left: 0;
+    right: 0;
+    z-index: 10;
+    background: white;
+    border-radius: 0 0 var(--rayon-bordure) var(--rayon-bordure);
+    box-shadow: var(--ombre);
+    padding: 6px 10px;
+    margin: 0;
+}
+
 /* Définition sous le verdict de vérification (issue #124). Présentation
    compacte, adaptée au faible espace du popover de la gouttière gauche : liste
    ordonnée serrée pour les gloses, message discret en italique quand la
    définition est indisponible (mot Hunspell uniquement / hors index). */
 .definition-brouillon {
-    margin-top: 6px;
     font-size: 0.85rem;
     line-height: 1.35;
 }
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index 3feb0a9..52677b6 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1639 (6 ligne(s)) dans l'ancienne version → ligne 1639 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1639,6 +1639,14 @@ document.addEventListener('DOMContentLoaded', async () => {
         definitionBrouillon.hidden = true;
     }
 
+    // Vide le champ et le verdict/définition affichés quand le focus quitte
+    // complètement la zone dictionnaire (issue #311, suite #308/#310).
+    function reinitialiserVerifDictionnaire() {
+        champVerif.value = '';
+        afficherMessageBrouillon('', null);
+        masquerDefinitionBrouillon();
+    }
+
     async function verifierMotDictionnaire() {
         const mot = champVerif.value;
         if (!mot.trim()) {
# ── Zone modifiée : ligne 1677 (6 ligne(s)) dans l'ancienne version → ligne 1685 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1677,6 +1685,15 @@ document.addEventListener('DOMContentLoaded', async () => {
         }
     });
 
+    // Vide le champ et le verdict/définition dès que le focus quitte
+    // complètement la zone (clic ailleurs sur la page), issue #311.
+    document.querySelector('.zone-dico-permanente')
+        .addEventListener('focusout', (e) => {
+            if (!e.currentTarget.contains(e.relatedTarget)) {
+                reinitialiserVerifDictionnaire();
+            }
+        });
+
     // ------------------------------------------------------------------ //
     // Encart d'historique glissant : ouverture/fermeture + clic sur une ligne
     // ------------------------------------------------------------------ //
