c45c9c3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c45c9c3
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 24 17:12:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-outils-exercices vers data-action + CSS — ECO Lichess, Explorateur Polyglot (issue #246 partie 2/4)
    
    5 onclick migrés vers data-action : outils_eco_search, outils_eco_import,
    explore_change_book, explore_back, explore_reset (5 nouveaux cases dans le
    listener délégué). 37 style inline extraits vers des classes .outils-eco-*
    et .outils-explore-* dans main.css (outils-btn-secondary réutilisé pour
    les boutons secondaires de l'explorateur). Sélecteurs e2e migrés vers
    data-action : outils_eco_search (×3), explore_reset — dépendances
    identifiées dans l'issue #246 pour test_outils_exercices_e2e.py (issue #211).
    Grep exhaustif sur nicsoft/tests/ confirmant qu'aucune autre dépendance n'a
    été manquée. Section "Ajouter cette ligne au catalogue" (sous-panneau de
    l'explorateur Polyglot) laissée hors périmètre — comptage 5/37 de l'issue
    correspond exactement à la carte ECO + l'explorateur hors ce sous-panneau,
    prévu pour la partie 3/4. Suites pytest (78 passed, 1 skip pré-existant
    hors périmètre) et e2e (42 passed, 1 skip pré-existant) complètes au vert.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/tests/e2e/test_outils_exercices_e2e.py b/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index fa3c5b4..c003b0e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Zone modifiée : ligne 181 (8 ligne(s)) dans l'ancienne version → ligne 181 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -181,8 +181,9 @@ def test_ajouter_effacer_remet_a_zero(at_outils):
 def test_eco_search_c65_renvoie_resultats(at_outils):
     """Recherche 'C65' → au moins une ligne dans le tableau."""
     at_outils.locator("#eco-filter").fill("C65")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsEcoSearch()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #246 partie 2/4)
+    at_outils.locator("button[data-action=\"outils_eco_search\"]").click()
     # eco-results-wrap peut être déjà visible d'un test précédent — attendre une ligne
     at_outils.locator("#eco-results-body tr").first.wait_for(state="visible", timeout=8000)
     assert at_outils.locator("#eco-results-body tr").count() > 0
# ── Zone modifiée : ligne 191 (8 ligne(s)) dans l'ancienne version → ligne 192 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -191,8 +192,9 @@ def test_eco_search_c65_renvoie_resultats(at_outils):
 def test_eco_search_plage_renvoie_resultats(at_outils):
     """Recherche 'C60-C67' → plusieurs lignes."""
     at_outils.locator("#eco-filter").fill("C60-C67")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsEcoSearch()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #246 partie 2/4)
+    at_outils.locator("button[data-action=\"outils_eco_search\"]").click()
     # eco-results-wrap peut être déjà visible d'un test précédent —
     # attendre qu'au moins une ligne soit présente plutôt que la visibilité du wrap
     at_outils.locator("#eco-results-body tr").first.wait_for(state="visible", timeout=8000)
# ── Zone modifiée : ligne 202 (8 ligne(s)) dans l'ancienne version → ligne 204 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -202,8 +204,9 @@ def test_eco_search_plage_renvoie_resultats(at_outils):
 def test_eco_tout_selectionner(at_outils):
     """Checkbox 'Tout sélectionner' coche toutes les lignes cochables (hors doublons disabled)."""
     at_outils.locator("#eco-filter").fill("C65")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsEcoSearch()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #246 partie 2/4)
+    at_outils.locator("button[data-action=\"outils_eco_search\"]").click()
     at_outils.locator("#eco-results-body tr").first.wait_for(state="visible", timeout=8000)
     at_outils.locator("#eco-check-all").check()
     total = at_outils.locator("#eco-results-body input[type=checkbox]:not(:disabled)").count()
# ── Zone modifiée : ligne 246 (8 ligne(s)) dans l'ancienne version → ligne 249 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -246,8 +249,9 @@ def test_explorer_reset_retour_debut(at_outils):
         at_outils.locator("#explore-book-list button").first.wait_for(state="visible", timeout=5000)
         at_outils.locator("#explore-book-list button").first.click()
         panel.wait_for(state="visible", timeout=5000)
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"exploreReset()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #246 partie 2/4)
+    at_outils.locator("button[data-action=\"explore_reset\"]").click()
     at_outils.wait_for_timeout(500)
     # Après reset, l'historique montre la position initiale (traduite) ou est vide
     # — comparaison indépendante de la locale par défaut de Playwright (issue #211).
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index a12c484..86184d5 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 335 (6 ligne(s)) dans l'ancienne version → ligne 335 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -335,6 +335,21 @@ document.addEventListener("click", (e) => {
       document.getElementById("outils-uci-input").value = "";
       document.getElementById("outils-uci-result").style.display = "none";
       break;
+    case "outils_eco_search":
+      outilsEcoSearch();
+      break;
+    case "outils_eco_import":
+      outilsEcoImport();
+      break;
+    case "explore_change_book":
+      exploreChangeBook();
+      break;
+    case "explore_back":
+      exploreBack();
+      break;
+    case "explore_reset":
+      exploreReset();
+      break;
   }
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index e261a19..ed73293 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 1485 (3 ligne(s)) dans l'ancienne version → ligne 1485 (36 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1485,3 +1485,36 @@
 .outils-uci-copy-btn:hover { color:#3a5a7a; }
 .outils-uci-btn-row { display:flex; gap:10px; margin-top:8px; flex-wrap:wrap; }
 .outils-uci-result { display:none; margin-top:12px; }
+
+/* ── Écran #screen-outils-exercices — ECO Lichess, Explorateur Polyglot (issue #246 partie 2/4) ── */
+.outils-eco-filter-row { display:flex; gap:8px; align-items:center; margin-bottom:10px; flex-wrap:wrap; }
+.outils-eco-filter-input { flex:1; min-width:160px; text-transform:uppercase; font-family:monospace; }
+.outils-eco-info-row { display:flex; align-items:center; gap:10px; margin-bottom:6px; flex-wrap:wrap; }
+.outils-eco-info-text { font-size:0.83rem; color:#3a5a7a; }
+.outils-eco-checkall-label { font-size:0.83rem; color:#3a5a7a; display:flex; align-items:center; gap:4px; cursor:pointer; }
+.outils-eco-table-wrap { max-height:280px; overflow-y:auto; border:1px solid #a0b8d0; border-radius:6px; background:#f8fafc; margin-bottom:10px; }
+.outils-eco-table { width:100%; border-collapse:collapse; font-size:0.82rem; }
+.outils-eco-table-head { background:#c2d4e8; position:sticky; top:0; }
+.outils-eco-th { padding:5px 8px; color:#1a2a3a; }
+.outils-eco-th-check { width:28px; }
+.outils-eco-th-left { text-align:left; }
+.outils-eco-camp-row { display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
+.outils-eco-camp-label { margin:0; }
+.outils-eco-camp-select { width:auto; }
+.outils-eco-selected-count { font-size:0.82rem; color:#888; }
+.outils-eco-import-result { margin-top:10px; }
+.outils-explore-book-list { display:flex; gap:10px; flex-wrap:wrap; margin-top:4px; }
+.outils-explore-no-books { color:#e94560; font-size:0.88rem; }
+.outils-explore-panel { margin-top:14px; }
+.outils-explore-name-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; flex-wrap:wrap; }
+.outils-explore-book-name { font-weight:700; color:#1a2a3a; font-size:0.95rem; }
+.outils-explore-btn-sm { padding:4px 10px; font-size:0.82rem; }
+.outils-explore-btn-md { padding:4px 12px; }
+.outils-explore-history { font-family:monospace; font-size:0.88rem; color:#3a5a7a; margin-bottom:10px; min-height:1.2em; }
+.outils-explore-board-row { display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap; }
+.outils-explore-board { line-height:0; }
+.outils-explore-nav-row { display:flex; gap:8px; margin-top:8px; }
+.outils-explore-depth { font-size:0.78rem; color:#888; margin-top:6px; }
+.outils-explore-moves-col { flex:1; min-width:200px; }
+.outils-explore-moves-title { font-size:0.82rem; font-weight:700; color:#3a5a7a; margin-bottom:6px; }
+.outils-explore-in-catalogue { margin-top:8px; font-size:0.83rem; color:#7b1fa2; font-weight:600; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 1e4d483..7c347cb 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1235 (57 ligne(s)) dans l'ancienne version → ligne 1235 (56 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1235,57 +1235,56 @@
   </div>
 
   <!-- Importer depuis ECO Lichess -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card outils-card-w">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="outils.eco.titre">📊 Importer depuis ECO Lichess</span>
     </div>
     <p class="outil-desc" data-i18n-html="outils.eco.desc">Filtrez par code ECO (ex&nbsp;: <code>C65</code>, <code>C60-C67</code>, <code>D</code>, <code>C02,D4</code>) et importez les lignes sélectionnées dans le catalogue.</p>
 
-    <div style="display:flex; gap:8px; align-items:center; margin-bottom:10px; flex-wrap:wrap;">
-      <input id="eco-filter" type="text" class="add-input" placeholder="C65 ou C60-C67 ou D ou C02,D4…" data-i18n-placeholder="outils.eco.filter_placeholder"
-        style="flex:1; min-width:160px; text-transform:uppercase; font-family:monospace;"
+    <div class="outils-eco-filter-row">
+      <input id="eco-filter" type="text" class="add-input outils-eco-filter-input" placeholder="C65 ou C60-C67 ou D ou C02,D4…" data-i18n-placeholder="outils.eco.filter_placeholder"
         onkeydown="if(event.key==='Enter') outilsEcoSearch()">
-      <button class="btn btn-continuer" onclick="outilsEcoSearch()" data-i18n="outils.eco.rechercher">🔍 Rechercher</button>
+      <button class="btn btn-continuer" data-action="outils_eco_search" data-i18n="outils.eco.rechercher">🔍 Rechercher</button>
     </div>
 
-    <div id="eco-results-wrap" style="display:none;">
+    <div id="eco-results-wrap" class="outils-hidden-init">
       <!-- Table des résultats -->
-      <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px; flex-wrap:wrap;">
-        <span id="eco-results-info" style="font-size:0.83rem; color:#3a5a7a;"></span>
-        <label style="font-size:0.83rem; color:#3a5a7a; display:flex; align-items:center; gap:4px; cursor:pointer;">
+      <div class="outils-eco-info-row">
+        <span id="eco-results-info" class="outils-eco-info-text"></span>
+        <label class="outils-eco-checkall-label">
           <input type="checkbox" id="eco-check-all" onchange="outilsEcoToggleAll(this.checked)"> <span data-i18n="outils.eco.tout_sel">Tout sélectionner</span>
         </label>
       </div>
-      <div style="max-height:280px; overflow-y:auto; border:1px solid #a0b8d0; border-radius:6px; background:#f8fafc; margin-bottom:10px;">
-        <table id="eco-results-table" style="width:100%; border-collapse:collapse; font-size:0.82rem;">
-          <thead><tr style="background:#c2d4e8; position:sticky; top:0;">
-            <th style="padding:5px 8px; width:28px;"></th>
-            <th style="padding:5px 8px; text-align:left; color:#1a2a3a;">ECO</th>
-            <th style="padding:5px 8px; text-align:left; color:#1a2a3a;">Nom</th>
-            <th style="padding:5px 8px; color:#1a2a3a;">Coups</th>
-            <th style="padding:5px 8px; color:#1a2a3a;">Statut</th>
+      <div class="outils-eco-table-wrap">
+        <table id="eco-results-table" class="outils-eco-table">
+          <thead><tr class="outils-eco-table-head">
+            <th class="outils-eco-th outils-eco-th-check"></th>
+            <th class="outils-eco-th outils-eco-th-left">ECO</th>
+            <th class="outils-eco-th outils-eco-th-left">Nom</th>
+            <th class="outils-eco-th">Coups</th>
+            <th class="outils-eco-th">Statut</th>
           </tr></thead>
           <tbody id="eco-results-body"></tbody>
         </table>
       </div>
 
       <!-- Camp + import -->
-      <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
-        <label class="add-label" style="margin:0;" data-i18n="outils.label.camp">Camp</label>
-        <select id="eco-camp" class="add-input" style="width:auto;">
+      <div class="outils-eco-camp-row">
+        <label class="add-label outils-eco-camp-label" data-i18n="outils.label.camp">Camp</label>
+        <select id="eco-camp" class="add-input outils-eco-camp-select">
           <option value="white" data-i18n="outils.camp.blancs">Blancs</option>
           <option value="black" data-i18n="outils.camp.noirs">Noirs</option>
         </select>
-        <button class="btn btn-continuer" onclick="outilsEcoImport()" data-i18n="outils.eco.importer_sel">✅ Importer la sélection</button>
-        <span id="eco-selected-count" style="font-size:0.82rem; color:#888;"></span>
+        <button class="btn btn-continuer" data-action="outils_eco_import" data-i18n="outils.eco.importer_sel">✅ Importer la sélection</button>
+        <span id="eco-selected-count" class="outils-eco-selected-count"></span>
       </div>
 
-      <div id="eco-import-result" style="display:none; margin-top:10px;"></div>
+      <div id="eco-import-result" class="outils-hidden-init outils-eco-import-result"></div>
     </div>
   </div>
 
   <!-- Explorer un livre Polyglot -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card outils-card-w">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="outils.polyglot.titre">📖 Explorer un livre Polyglot</span>
     </div>
# ── Zone modifiée : ligne 1293 (36 ligne(s)) dans l'ancienne version → ligne 1292 (36 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1293,36 +1292,36 @@
 
     <!-- Sélecteur de livre -->
     <div id="explore-book-selector">
-      <div id="explore-book-list" style="display:flex; gap:10px; flex-wrap:wrap; margin-top:4px;"></div>
-      <div id="explore-no-books" style="display:none; color:#e94560; font-size:0.88rem;" data-i18n="outils.polyglot.no_books">Aucun livre .bin trouvé dans ~/NicLink/data/books/</div>
+      <div id="explore-book-list" class="outils-explore-book-list"></div>
+      <div id="explore-no-books" class="outils-hidden-init outils-explore-no-books" data-i18n="outils.polyglot.no_books">Aucun livre .bin trouvé dans ~/NicLink/data/books/</div>
     </div>
 
     <!-- Explorateur (affiché après sélection) -->
-    <div id="explore-panel" style="display:none; margin-top:14px;">
-      <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px; flex-wrap:wrap;">
-        <span id="explore-book-name" style="font-weight:700; color:#1a2a3a; font-size:0.95rem;"></span>
-        <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; padding:4px 10px; font-size:0.82rem;" onclick="exploreChangeBook()" data-i18n="outils.polyglot.changer">← Changer</button>
+    <div id="explore-panel" class="outils-hidden-init outils-explore-panel">
+      <div class="outils-explore-name-row">
+        <span id="explore-book-name" class="outils-explore-book-name"></span>
+        <button class="btn outils-btn-secondary outils-explore-btn-sm" data-action="explore_change_book" data-i18n="outils.polyglot.changer">← Changer</button>
       </div>
 
       <!-- Ligne jouée -->
-      <div id="explore-history" style="font-family:monospace; font-size:0.88rem; color:#3a5a7a; margin-bottom:10px; min-height:1.2em;"></div>
+      <div id="explore-history" class="outils-explore-history"></div>
 
-      <div style="display:flex; gap:16px; align-items:flex-start; flex-wrap:wrap;">
+      <div class="outils-explore-board-row">
         <!-- Mini-échiquier -->
         <div>
-          <div id="explore-board" style="line-height:0;"></div>
-          <div style="display:flex; gap:8px; margin-top:8px;">
-            <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; padding:4px 12px;" onclick="exploreBack()" id="explore-btn-back" disabled data-i18n="outils.polyglot.reculer">← Reculer</button>
-            <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; padding:4px 12px;" onclick="exploreReset()" data-i18n="outils.polyglot.debut">↺ Début</button>
+          <div id="explore-board" class="outils-explore-board"></div>
+          <div class="outils-explore-nav-row">
+            <button class="btn outils-btn-secondary outils-explore-btn-md" data-action="explore_back" id="explore-btn-back" disabled data-i18n="outils.polyglot.reculer">← Reculer</button>
+            <button class="btn outils-btn-secondary outils-explore-btn-md" data-action="explore_reset" data-i18n="outils.polyglot.debut">↺ Début</button>
           </div>
-          <div id="explore-depth" style="font-size:0.78rem; color:#888; margin-top:6px;"></div>
+          <div id="explore-depth" class="outils-explore-depth"></div>
         </div>
 
         <!-- Liste des coups -->
-        <div style="flex:1; min-width:200px;">
-          <div style="font-size:0.82rem; font-weight:700; color:#3a5a7a; margin-bottom:6px;" data-i18n="outils.polyglot.coups">Coups du livre :</div>
+        <div class="outils-explore-moves-col">
+          <div class="outils-explore-moves-title" data-i18n="outils.polyglot.coups">Coups du livre :</div>
           <div id="explore-moves-list"></div>
-          <div id="explore-in-catalogue" style="display:none; margin-top:8px; font-size:0.83rem; color:#7b1fa2; font-weight:600;"></div>
+          <div id="explore-in-catalogue" class="outils-hidden-init outils-explore-in-catalogue"></div>
         </div>
       </div>
 
