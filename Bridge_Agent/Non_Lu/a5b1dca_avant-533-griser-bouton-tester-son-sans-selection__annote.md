a5b1dca

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a5b1dca
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Sat Sep 12 16:11:06 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-533-griser-bouton-tester-son-sans-selection

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/css/style.css b/static/css/style.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 68f9403..0dba545 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/css/style.css
# ── Version APRÈS ce commit.
+++ b/static/css/style.css
# ── Zone modifiée : ligne 326 (6 ligne(s)) dans l'ancienne version → ligne 326 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -326,6 +326,8 @@ button.danger:hover{background:#f8d7da}
 .pl-btn-mini{flex-shrink:0;padding:3px 9px;font-size:12px;border:1px solid #ccc;
   border-radius:6px;background:#f8f8f5;color:#1a1a18;cursor:pointer}
 .pl-btn-mini:hover{background:#eee}
+.pl-btn-mini:disabled{background:#f0f0ed;color:#999;cursor:not-allowed}
+.pl-btn-mini:disabled:hover{background:#f0f0ed}
 .pl-btn-vm{margin:6px 0 2px}
 /* Résumé « en cours/en file » sous chaque watcher CCL (issue #381). */
 .pl-sous-projet{font-size:11px;color:#999;margin:-2px 0 6px;padding-left:1px}
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 9a74abd..7c23d05 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2179 (6 ligne(s)) dans l'ancienne version → ligne 2179 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2179,6 +2179,18 @@ function refleterSonActif(son) {
   if (optCloche) optCloche.classList.toggle('actif', son === 'cloche');
 }
 
+// Grise le bouton « Tester le son » tant qu'aucune ligne n'est sélectionnée
+// (projetCourant null) : sinon testerSonActif() jouerait une tonalité neutre
+// qui ne correspond à aucune notification réelle (issue #533, suite à #532).
+// Appelée à l'initialisation (disabled déjà posé dans le HTML) et à chaque
+// changement de sélection (selectionnerLigne/selectionnerPremiereVisible).
+function majBoutonTesterSonActif() {
+  const btn = document.getElementById('pl-btn-tester-son');
+  if (!btn) return;
+  btn.disabled = !projetCourant;
+  btn.title = projetCourant ? '' : 'Aucune ligne sélectionnée';
+}
+
 // Écrit le choix dans son_actif.txt au clic — effectif au bip suivant, sans
 // rechargement de page (traitement_fin.py relit le fichier à chaque bip).
 async function choisirSonActif(son) {
# ── Zone modifiée : ligne 2198 (10 ligne(s)) dans l'ancienne version → ligne 2210 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2198,10 +2210,11 @@ async function choisirSonActif(son) {
 // tonalité du projet actif (projetCourant, celui de la ligne sélectionnée
 // dans la liste des issues — voir sa déclaration plus haut), pour que ce test
 // reflète fidèlement le son entendu à la clôture d'une issue de ce projet
-// (issue #532). Neutre si aucune ligne n'est sélectionnée (projetCourant
-// null) : le backend applique alors le même repli (même principe que
-// testerBip() pour la tonalité par projet, issue #526).
+// (issue #532). Le bouton est disabled tant que projetCourant est null
+// (majBoutonTesterSonActif, issue #533) ; ce garde-fou est une redondance
+// défensive au cas où l'appel serait déclenché autrement qu'au clic.
 async function testerSonActif() {
+  if (!projetCourant) return;
   try {
     await fetch('/tester-son', {
       method: 'POST',
# ── Zone modifiée : ligne 2584 (6 ligne(s)) dans l'ancienne version → ligne 2597 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2584,6 +2597,7 @@ function selectionnerPremiereVisible() {
     numeroCourant = null;
     document.getElementById('zone-issue').innerHTML =
       '<div class="issue-vide">Aucune issue à afficher</div>';
+    majBoutonTesterSonActif();
   }
 }
 
# ── Zone modifiée : ligne 2823 (12 ligne(s)) dans l'ancienne version → ligne 2837 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2823,12 +2837,14 @@ function selectionnerLigne(nom, numero) {
     projetCourant = null;
     numeroCourant = null;
     zone.innerHTML = '<div class="issue-vide">Aucune issue à afficher</div>';
+    majBoutonTesterSonActif();
     rafraichirPanneauLateralResultats();
     return;
   }
   projetCourant = nom;
   numeroCourant = numero;
   zone.innerHTML = '<div class="issue-vide">Double-cliquez une issue pour afficher son détail.</div>';
+  majBoutonTesterSonActif();
   rafraichirPanneauLateralResultats();
 }
 
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 733af1c..5e2a923 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 283 (7 ligne(s)) dans l'ancienne version → ligne 283 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -283,7 +283,13 @@
            PAS reconstruit à chaque cycle de rafraichirPanneauLateralResultats
            (contrairement aux autres zones ci-dessous) : rien ne le ferait
            diverger de l'état réel puisque cette zone est la seule à écrire
-           dans son_actif.txt depuis l'interface.
+           dans son_actif.txt depuis l'interface. Le bouton #pl-btn-tester-son
+           joue la tonalité du projet actif (projetCourant, issue #532) : il
+           est disabled par défaut (attribut posé dans ce HTML) et
+           réactivé/regrisé par majBoutonTesterSonActif() (static/js/app.js)
+           à chaque changement de sélection, tant qu'aucune ligne n'est
+           sélectionnée (issue #533) — un son neutre ne correspondrait à
+           aucune notification réelle.
          - #pl-zone-extras : zone réservée aux futurs boutons (issue #380),
            occupée depuis l'issue #485 par le contrôle du watcher spool
            (issues_inbox) — rendrePanneauLateralExtras() (static/js/app.js).
# ── Zone modifiée : ligne 299 (7 ligne(s)) dans l'ancienne version → ligne 305 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -299,7 +305,7 @@
             <button type="button" class="pl-son-opt" id="pl-son-opt-plat" onclick="choisirSonActif('plat')">Plat</button>
             <button type="button" class="pl-son-opt" id="pl-son-opt-cloche" onclick="choisirSonActif('cloche')">Cloche</button>
           </span>
-          <button type="button" class="pl-btn-mini" onclick="testerSonActif()">Tester le son</button>
+          <button type="button" class="pl-btn-mini" id="pl-btn-tester-son" onclick="testerSonActif()" disabled title="Aucune ligne sélectionnée">Tester le son</button>
         </div>
       </div>
       <!-- Zone réservée aux futurs boutons (issue #380) : vide intentionnellement. -->
