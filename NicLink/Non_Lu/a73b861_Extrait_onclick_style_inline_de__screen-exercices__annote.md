a73b861

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a73b861
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 19:05:25 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-exercices vers data-action + CSS (issue #228)
    
    Remplace les 6 attributs onclick= : les 2 boutons "← Menu" (barre variété
    et barre drill) rejoignent un nouveau case "back" dans le switch délégué
    d'app.js — distinct de "back_menu" déjà existant, appelant
    sendAction({type:'back'}) (case Python déjà présent dans alchess.py,
    inchangé). Les 3 boutons d'onglets (Blancs/Noirs/Mes lignes) sont
    consolidés en un case "ex_select_tab" paramétré par data-tab, appelant
    exSelectTab(el.dataset.tab) inchangée. Le bouton "Drill" passe au
    nouveau case "ex_lancer_drill" → exLancerDrill() inchangée.
    
    Remplace les 18 style= inline par des classes dédiées dans main.css
    (.ex-titre/.ex-soustitre/.ex-variete-bar/.ex-variete-group/.ex-variete-txt/
    .ex-variete-slider/.ex-variete-value/.ex-tabs/.ex-tab-btn +
    .ex-tab-btn-active-init/.ex-tab-btn-inactive-init/.ex-drill-bar/
    .ex-drill-count/.ex-drill-btn-menu/.ex-drill-btn-launch/.ex-ouvertures-list),
    valeurs strictement identiques à l'inline d'origine. Le bouton "← Menu" de
    la barre variété réutilise .btn-continuer (mêmes valeurs exactes que
    l'inline, comme dans #226). Les propriétés du conteneur #screen-exercices
    (flex-direction/align-items/padding/gap/overflow-y) sont fusionnées dans
    la règle #screen-exercices existante dans main.css (même pattern que
    #screen-config-humain dans #227) — la visibilité reste gérée par
    affectation directe de .style.display en JS (app.js), indépendante de ce
    changement. Le oninput="exUpdateVariete()" du slider Variété est laissé
    tel quel, hors périmètre onclick/style.
    
    Aucun sélecteur e2e ne cible un onclick/style de ce bloc (grep exhaustif
    sur nicsoft/tests/e2e/*.py) — seul le texte "Menu" et l'id #screen-exercices
    sont utilisés (test_retour_depuis_exercices), non affectés par ce
    changement.
    
    Suite pytest complète (78 passed, 1 skipped, e2e inclus) au vert après
    modification.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 243f105..5e0a953 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 76 (6 ligne(s)) dans l'ancienne version → ligne 76 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -76,6 +76,15 @@ document.addEventListener("click", (e) => {
     case "back_menu":
       sendAction({ type: "back_menu" });
       break;
+    case "back":
+      sendAction({ type: "back" });
+      break;
+    case "ex_select_tab":
+      exSelectTab(el.dataset.tab);
+      break;
+    case "ex_lancer_drill":
+      exLancerDrill();
+      break;
     case "select_color_hh":
       selectColorHH(el.dataset.color);
       break;
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index 9cd10ea..d0df353 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 119 (6 ligne(s)) dans l'ancienne version → ligne 119 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -119,6 +119,11 @@
     /* ── Écrans ── */
     #screen-exercices {
       display: none;
+      flex-direction: column;
+      align-items: center;
+      padding: 24px;
+      gap: 16px;
+      overflow-y: auto;
     }
     #screen-menu, #screen-config, #screen-config-humain,
     #screen-retranscription, #screen-retrans-game {
# ── Zone modifiée : ligne 945 (6 ligne(s)) dans l'ancienne version → ligne 950 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -945,6 +950,24 @@
 .parametres-tts-rate { width:200px; accent-color:#e94560; }
 .parametres-actions { width:100%; max-width:860px; display:flex; gap:10px; }
 
+/* ── Écran "Exercices" ── */
+.ex-titre { font-size:1.5rem; color:#e94560; font-weight:bold; }
+.ex-soustitre { font-size:0.85rem; color:#3a5a7a; margin-top:-10px; }
+.ex-variete-bar { display:flex; gap:24px; align-items:center; flex-wrap:wrap; justify-content:center; background:#c2d4e8; border:1px solid #a0b8d0; border-radius:8px; padding:12px 20px; }
+.ex-variete-group { display:flex; align-items:center; gap:10px; }
+.ex-variete-txt { color:#445; font-size:0.82rem; }
+.ex-variete-slider { width:90px; accent-color:#e94560; }
+.ex-variete-value { color:#1a2a3a; font-weight:bold; width:16px; }
+.ex-tabs { display:flex; gap:0; border-radius:8px; overflow:hidden; border:1px solid #a0b8d0; }
+.ex-tab-btn { padding:10px 32px; font-size:0.95rem; font-weight:bold; cursor:pointer; border:none; transition:opacity 0.15s; }
+.ex-tab-btn-active-init { background:#e8c840; color:#d8e4f0; }
+.ex-tab-btn-inactive-init { background:#c2d4e8; color:#3a5a7a; }
+.ex-drill-bar { display:none; width:100%; max-width:960px; background:#c2d4e8; border:1px solid #a0b8d0; border-radius:8px; padding:8px 12px; margin-bottom:8px; align-items:center; gap:8px; }
+.ex-drill-count { font-size:0.82rem; color:#3a5a7a; flex:1; }
+.ex-drill-btn-menu { padding:7px 14px; font-size:0.82rem; background:#c2d4e8; color:#1a2a3a; border:1px solid #333; }
+.ex-drill-btn-launch { padding:7px 18px; font-size:0.85rem; }
+.ex-ouvertures-list { width:100%; max-width:960px; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 7de4213..e8cde6f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 860 (47 ligne(s)) dans l'ancienne version → ligne 860 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -860,47 +860,42 @@
   </div>
 </div>
 <!-- ── Écran Exercices — sélection ── -->
-<div id="screen-exercices" style="display:none; flex-direction:column; align-items:center; padding:24px; gap:16px; overflow-y:auto;">
+<div id="screen-exercices">
 
-  <div style="font-size:1.5rem; color:#e94560; font-weight:bold;" data-i18n="exercices.titre_ecran">📚 Exercices — Ouvertures</div>
-  <div style="font-size:0.85rem; color:#3a5a7a; margin-top:-10px;" data-i18n="exercices.sous_titre">Choisissez une ouverture et entraînez-vous avec le livre de GM</div>
+  <div class="ex-titre" data-i18n="exercices.titre_ecran">📚 Exercices — Ouvertures</div>
+  <div class="ex-soustitre" data-i18n="exercices.sous_titre">Choisissez une ouverture et entraînez-vous avec le livre de GM</div>
 
   <!-- Paramètres compacts -->
-  <div id="ex-variete-bar" style="display:flex; gap:24px; align-items:center; flex-wrap:wrap; justify-content:center; background:#c2d4e8; border:1px solid #a0b8d0; border-radius:8px; padding:12px 20px;">
-    <div style="display:flex; align-items:center; gap:10px;">
-      <span style="color:#445; font-size:0.82rem;" data-i18n="exercices.variete">Variété</span>
-      <input type="range" id="ex-variete" min="1" max="8" value="3" style="width:90px; accent-color:#e94560;" oninput="exUpdateVariete()">
-      <span id="ex-variete-label" style="color:#1a2a3a; font-weight:bold; width:16px;">3</span>
+  <div id="ex-variete-bar" class="ex-variete-bar">
+    <div class="ex-variete-group">
+      <span class="ex-variete-txt" data-i18n="exercices.variete">Variété</span>
+      <input type="range" id="ex-variete" min="1" max="8" value="3" class="ex-variete-slider" oninput="exUpdateVariete()">
+      <span id="ex-variete-label" class="ex-variete-value">3</span>
     </div>
-    <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-top:0;" onclick="sendAction({type:'back'})">← Menu</button>
+    <button class="btn btn-continuer" data-action="back">← Menu</button>
   </div>
 
   <!-- Onglets Blancs / Noirs / Mes lignes -->
-  <div style="display:flex; gap:0; border-radius:8px; overflow:hidden; border:1px solid #a0b8d0;">
-    <button id="ex-tab-white" onclick="exSelectTab('white')" data-i18n="exercices.tab.blancs"
-      style="padding:10px 32px; font-size:0.95rem; font-weight:bold; cursor:pointer; border:none; background:#e8c840; color:#d8e4f0; transition:opacity 0.15s;">
+  <div class="ex-tabs">
+    <button id="ex-tab-white" class="ex-tab-btn ex-tab-btn-active-init" data-action="ex_select_tab" data-tab="white" data-i18n="exercices.tab.blancs">
       ♔ Blancs suggérés
     </button>
-    <button id="ex-tab-black" onclick="exSelectTab('black')" data-i18n="exercices.tab.noirs"
-      style="padding:10px 32px; font-size:0.95rem; font-weight:bold; cursor:pointer; border:none; background:#c2d4e8; color:#3a5a7a; transition:opacity 0.15s;">
+    <button id="ex-tab-black" class="ex-tab-btn ex-tab-btn-inactive-init" data-action="ex_select_tab" data-tab="black" data-i18n="exercices.tab.noirs">
       ♚ Noirs suggérés
     </button>
-    <button id="ex-tab-mes-lignes" onclick="exSelectTab('mes-lignes')" data-i18n="exercices.tab.mes_lignes"
-      style="padding:10px 32px; font-size:0.95rem; font-weight:bold; cursor:pointer; border:none; background:#c2d4e8; color:#3a5a7a; transition:opacity 0.15s;">
+    <button id="ex-tab-mes-lignes" class="ex-tab-btn ex-tab-btn-inactive-init" data-action="ex_select_tab" data-tab="mes-lignes" data-i18n="exercices.tab.mes_lignes">
       ★ Mes lignes
     </button>
   </div>
 
   <!-- Liste des ouvertures groupées -->
   <!-- Barre drill compacte -->
-  <div id="ex-drill-bar" style="display:none; width:100%; max-width:960px; background:#c2d4e8; border:1px solid #a0b8d0; border-radius:8px; padding:8px 12px; margin-bottom:8px; align-items:center; gap:8px;">
-    <span id="ex-drill-count" style="font-size:0.82rem; color:#3a5a7a; flex:1;"></span>
-    <button class="btn" onclick="sendAction({type:'back'})"
-      style="padding:7px 14px; font-size:0.82rem; background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; border:1px solid #333;">← Menu</button>
-    <button id="ex-drill-btn" class="btn btn-reprendre" onclick="exLancerDrill()" data-i18n="exercices.drill"
-      style="padding:7px 18px; font-size:0.85rem;">🎲 Drill</button>
+  <div id="ex-drill-bar" class="ex-drill-bar">
+    <span id="ex-drill-count" class="ex-drill-count"></span>
+    <button class="btn ex-drill-btn-menu" data-action="back">← Menu</button>
+    <button id="ex-drill-btn" class="btn btn-reprendre ex-drill-btn-launch" data-action="ex_lancer_drill" data-i18n="exercices.drill">🎲 Drill</button>
   </div>
-  <div id="ex-ouvertures-list" style="width:100%; max-width:960px;"></div>
+  <div id="ex-ouvertures-list" class="ex-ouvertures-list"></div>
 
 </div>
 
