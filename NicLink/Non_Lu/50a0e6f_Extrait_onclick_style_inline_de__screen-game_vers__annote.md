50a0e6f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 50a0e6f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 22:00:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-game vers data-action + CSS — onglets Mes parties AlChess / Bibliothèque PGN (issue #244 partie 4/4)
    
    13 onclick → data-action (11 nouveaux cases, réutilise aide_panier de #231 et
    back_menu déjà existant — seul appel back_menu authentique de tout l'écran,
    confirmé par grep e2e). 32 style inline → classes .game-gameover-* /
    .basket-sel-list-up dans main.css.
    
    Point de vigilance : toggleCollerPgn()/chargerPgnColle() lisaient
    zone.style.display en inline pour décider de l'ouverture — passage à une
    classe CSS aurait cassé le toggle au premier clic (style vide ≠ 'none').
    Migré vers classList.toggle('is-open')/classList.remove('is-open').
    
    e2e : #panel-gameover button[onclick*="back_menu"] → button[data-action="back_menu"]
    dans test_smoke_e2e.py (2 occurrences, seules à cibler cette section — grep
    exhaustif sur nicsoft/tests/e2e/*.py, #screen-outils-exercices non concerné).
    
    Ceci clôt les 4 parties de l'extraction #screen-game (issues #241-244).
    Suites pytest (78 passed, 1 skipped) et e2e (42 passed, 1 skipped) au vert.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/tests/e2e/test_smoke_e2e.py b/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 874a07b..47d3281 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Zone modifiée : ligne 116 (8 ligne(s)) dans l'ancienne version → ligne 116 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -116,8 +116,8 @@ def test_retour_depuis_analyse(at_menu):
         at_menu.locator("button.menu-btn-analyse").click()
         at_menu.wait_for_selector("#panel-gameover", state="visible", timeout=5000)
 
-    # Ciblage par attribut onclick, indépendant de la locale (issue #208)
-    at_menu.locator("#panel-gameover button[onclick*=\"back_menu\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #208, migré #244)
+    at_menu.locator("#panel-gameover button[data-action=\"back_menu\"]").click()
     at_menu.wait_for_selector("#screen-menu", state="visible", timeout=5000)
     assert at_menu.locator("#screen-menu").is_visible()
 
# ── Zone modifiée : ligne 169 (10 ligne(s)) dans l'ancienne version → ligne 169 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -169,10 +169,10 @@ def test_retranscription_formulaire(at_menu):
 
 def test_transition_analyse_puis_menu(at_menu):
     """Analyse → Retour → Pédagogique config — pas de résidu."""
-    # Analyse — ciblage par classe CSS / attribut onclick, indépendant de la locale (issue #208)
+    # Analyse — ciblage par classe CSS / attribut data-action, indépendant de la locale (issue #208, migré #244)
     at_menu.locator("button.menu-btn-analyse").click()
     at_menu.wait_for_selector("#panel-gameover", state="visible", timeout=5000)
-    at_menu.locator("#panel-gameover button[onclick*=\"back_menu\"]").click()
+    at_menu.locator("#panel-gameover button[data-action=\"back_menu\"]").click()
     at_menu.wait_for_selector("#screen-menu", state="visible", timeout=5000)
 
     # Pédagogique config → vérifier état propre
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 44d4141..56dfc33 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 277 (6 ligne(s)) dans l'ancienne version → ligne 277 (39 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -277,6 +277,39 @@ document.addEventListener("click", (e) => {
     case "pgn_lib_select_tab":
       pgnLibSelectTab(el.dataset.tab);
       break;
+    case "trigger_pgn_file_input":
+      document.getElementById("pgn-file-input").click();
+      break;
+    case "toggle_coller_pgn":
+      toggleCollerPgn();
+      break;
+    case "charger_pgn_colle":
+      chargerPgnColle();
+      break;
+    case "basket_load_to_analyse":
+      basketLoadToAnalyse();
+      break;
+    case "pgn_lib_open_create_modal":
+      pgnLibOpenCreateModal();
+      break;
+    case "pgn_lib_confirm_delete":
+      pgnLibConfirmDelete();
+      break;
+    case "trigger_pgn_lib_file_input":
+      document.getElementById("pgn-lib-file-input").click();
+      break;
+    case "lancer_analyse":
+      lancerAnalyse();
+      break;
+    case "jouer_sequence_review":
+      jouerSequenceReview();
+      break;
+    case "telecharger_pgn":
+      telechargerPgn();
+      break;
+    case "vider_analyse":
+      _viderAnalyse();
+      break;
   }
 });
 
# ── Zone modifiée : ligne 2617 (15 ligne(s)) dans l'ancienne version → ligne 2650 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2617,15 +2650,14 @@ function loadPgnFile(event) {
 }
 
 function toggleCollerPgn() {
-  const zone = document.getElementById('coller-pgn-zone');
-  zone.style.display = zone.style.display === 'none' ? 'block' : 'none';
+  document.getElementById('coller-pgn-zone').classList.toggle('is-open');
 }
 
 function chargerPgnColle() {
   const pgn = document.getElementById('coller-pgn-input').value.trim();
   if (!pgn) { alert(t('error.pgn_vide') || 'Zone PGN vide.'); return; }
   // Masquer la zone après chargement
-  document.getElementById('coller-pgn-zone').style.display = 'none';
+  document.getElementById('coller-pgn-zone').classList.remove('is-open');
   document.getElementById('coller-pgn-input').value = '';
   parsePgn(pgn);
 }
# ── Zone modifiée : ligne 2746 (7 ligne(s)) dans l'ancienne version → ligne 2778 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2746,7 +2778,7 @@ function pgnLibRenderGamesList() {
   const list = document.getElementById("pgn-lib-games-list");
   if (!list) return;
   if (_pgnLibGames.length === 0) {
-    list.innerHTML = `<div class="pgn-lib-empty" style="color:#778; font-size:0.8rem; text-align:center; padding:12px 0;">${t("pgn_lib.liste_vide")}</div>`;
+    list.innerHTML = `<div class="pgn-lib-empty">${t("pgn_lib.liste_vide")}</div>`;
     return;
   }
   list.innerHTML = _pgnLibGames.map(g => `
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index d7167ea..a7c8a02 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 890 (6 ligne(s)) dans l'ancienne version → ligne 890 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -890,6 +890,7 @@
     .basket-sel-arrow { font-size: 0.6rem; margin-left: 4px; color: #1a2a3a; flex-shrink: 0; }
     .basket-sel-list { position: absolute; left: 0; right: 0; background: #1a2a3a; border: 1px solid #a0b8d0; z-index: 200; max-height: 180px; overflow-y: auto; }
     .basket-sel-list-down { top: 100%; border-top: none; border-radius: 0 0 4px 4px; }
+    .basket-sel-list-up { bottom: 100%; border-bottom: none; border-radius: 4px 4px 0 0; }
     .basket-load-btn { margin-bottom: 0; padding: 0 12px; white-space: nowrap; height: 34px; box-sizing: border-box; }
 
     .coord-rank {
# ── Zone modifiée : ligne 1431 (3 ligne(s)) dans l'ancienne version → ligne 1432 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1431,3 +1432,27 @@
 .game-gameover-tab-btn { flex:1; padding:8px 4px; font-size:0.78rem; font-weight:bold; cursor:pointer; border:none; transition:opacity 0.15s; }
 .game-gameover-tab-btn-active { background:#e94560; color:white; }
 .game-gameover-tab-btn-inactive { background:#c2d4e8; color:#3a5a7a; }
+
+/* ── Écran #screen-game — onglets "Mes parties AlChess" / "Bibliothèque PGN" (issue #244 partie 4/4) ── */
+.game-gameover-tab-content { display:flex; flex-direction:column; gap:8px; }
+.game-gameover-tab-content-hidden { display:none; flex-direction:column; gap:8px; }
+.game-gameover-file-input { display:none; }
+.game-gameover-btn-mb0 { margin-bottom:0; }
+.game-gameover-coller-pgn-zone { display:none; margin-top:8px; }
+.game-gameover-coller-pgn-zone.is-open { display:block; }
+.game-gameover-coller-pgn-textarea { width:100%; font-family:monospace; font-size:12px; resize:vertical; }
+.game-gameover-coller-pgn-charger-btn { margin-top:4px; margin-bottom:0; width:100%; }
+.game-gameover-basket-row { display:flex; gap:6px; align-items:stretch; }
+.game-gameover-lib-select { flex:1; min-width:0; background:#a0b8d0; color:#1a2a3a; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; height:34px; box-sizing:border-box; }
+.game-gameover-lib-create-btn { margin-bottom:0; padding:0 10px; white-space:nowrap; height:34px; box-sizing:border-box; background:#2e7d32; color:white; }
+.game-gameover-lib-delete-btn { margin-bottom:0; padding:0 10px; white-space:nowrap; height:34px; box-sizing:border-box; }
+.game-gameover-lib-spinner { display:none; align-items:center; gap:8px; color:#3a5a7a; font-size:0.8rem; }
+.game-gameover-lib-spinner-circle { width:14px; height:14px; border:2px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite; }
+.game-gameover-lib-games-list { max-height:260px; overflow-y:auto; display:flex; flex-direction:column; gap:4px; border:1px solid #a0b8d0; border-radius:6px; padding:6px; background:#eef4fa; }
+.pgn-lib-empty { color:#778; font-size:0.8rem; text-align:center; padding:12px 0; }
+.game-gameover-seq-row { display:none; align-items:center; gap:8px; }
+.game-gameover-seq-label { font-size:0.8rem; color:#3a5a7a; white-space:nowrap; }
+.game-gameover-seq-select { flex:1; background:#a0b8d0; color:#1a2a3a; border:1px solid #2a5a8a; border-radius:4px; padding:4px 8px; font-size:0.82rem; }
+.game-gameover-hidden-init { margin-bottom:0; display:none; }
+.game-gameover-btn-sequence { background:#9ab8d8; color:#1a2a3a; border:1px solid #2a5a8a; }
+.game-gameover-btn-retour { background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 8b10a7f..fafd973 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 736 (67 ligne(s)) dans l'ancienne version → ligne 736 (66 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -736,67 +736,66 @@
         </div>
 
         <!-- Onglet « Mes parties AlChess » (comportement existant, inchangé) -->
-        <div id="analyse-tab-alchess-content" style="display:flex; flex-direction:column; gap:8px;">
-          <input type="file" id="pgn-file-input" accept=".pgn" style="display:none" onchange="loadPgnFile(event)">
-          <button class="btn btn-best"      style="margin-bottom:0;" onclick="document.getElementById('pgn-file-input').click()" data-i18n="labo.btn.importer_pgn">📂 Importer PGN</button>
+        <div id="analyse-tab-alchess-content" class="game-gameover-tab-content">
+          <input type="file" id="pgn-file-input" accept=".pgn" class="game-gameover-file-input" onchange="loadPgnFile(event)">
+          <button class="btn btn-best game-gameover-btn-mb0" data-action="trigger_pgn_file_input" data-i18n="labo.btn.importer_pgn">📂 Importer PGN</button>
           <!-- Coller PGN directement -->
-          <button class="btn btn-best" style="margin-bottom:0;" onclick="toggleCollerPgn()" data-i18n="analyse.btn.coller_pgn">📋 Coller PGN</button>
-          <div id="coller-pgn-zone" style="display:none; margin-top:8px;">
-            <textarea id="coller-pgn-input" rows="8" style="width:100%; font-family:monospace; font-size:12px; resize:vertical;" placeholder="Collez ici le contenu PGN..."></textarea>
-            <button class="btn btn-reprendre" style="margin-top:4px; margin-bottom:0; width:100%;" onclick="chargerPgnColle()" data-i18n="analyse.btn.charger_pgn_colle">✅ Charger</button>
+          <button class="btn btn-best game-gameover-btn-mb0" data-action="toggle_coller_pgn" data-i18n="analyse.btn.coller_pgn">📋 Coller PGN</button>
+          <div id="coller-pgn-zone" class="game-gameover-coller-pgn-zone">
+            <textarea id="coller-pgn-input" rows="8" class="game-gameover-coller-pgn-textarea" placeholder="Collez ici le contenu PGN..."></textarea>
+            <button class="btn btn-reprendre game-gameover-coller-pgn-charger-btn" data-action="charger_pgn_colle" data-i18n="analyse.btn.charger_pgn_colle">✅ Charger</button>
           </div>
           <!-- Classeur de session -->
-          <div id="basket-row-analyse" style="display:flex; gap:6px; align-items:stretch;">
-            <span class="aide-panier-icone" onclick="ouvrirAidePanier()" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
-            <div id="basket-select-analyse" class="basket-select" data-value="" style="flex:1; position:relative; height:34px; box-sizing:border-box; background:#a0b8d0; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; display:flex; align-items:center; justify-content:space-between; cursor:pointer; user-select:none;">
-              <span class="basket-sel-label" data-i18n="common.corbeille_vide" style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#556;">— classeur vide —</span>
-              <span style="font-size:0.6rem; margin-left:4px; color:#1a2a3a; flex-shrink:0;">▼</span>
-              <div class="basket-sel-list" style="display:none; position:absolute; bottom:100%; left:0; right:0; background:#1a2a3a; border:1px solid #a0b8d0; border-bottom:none; border-radius:4px 4px 0 0; z-index:200; max-height:180px; overflow-y:auto;"></div>
+          <div id="basket-row-analyse" class="game-gameover-basket-row">
+            <span class="aide-panier-icone" data-action="aide_panier" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
+            <div id="basket-select-analyse" class="basket-select" data-value="">
+              <span class="basket-sel-label" data-i18n="common.corbeille_vide">— classeur vide —</span>
+              <span class="basket-sel-arrow">▼</span>
+              <div class="basket-sel-list basket-sel-list-up" style="display:none;"></div>
             </div>
-            <button class="btn basket-load-btn" style="margin-bottom:0; padding:0 12px; white-space:nowrap; height:34px; box-sizing:border-box;" disabled onclick="basketLoadToAnalyse()" data-i18n="common.charger">🗂️ Charger</button>
+            <button class="btn basket-load-btn" disabled data-action="basket_load_to_analyse" data-i18n="common.charger">🗂️ Charger</button>
           </div>
         </div>
 
         <!-- Onglet « Bibliothèque PGN » (nouveau, issue #194) -->
-        <div id="analyse-tab-library-content" style="display:none; flex-direction:column; gap:8px;">
+        <div id="analyse-tab-library-content" class="game-gameover-tab-content-hidden">
           <!-- Sélection collection + créer/supprimer -->
-          <div style="display:flex; gap:6px; align-items:stretch;">
-            <select id="pgn-lib-collection-select" onchange="pgnLibSelectCollection(this.value)"
-              style="flex:1; min-width:0; background:#a0b8d0; color:#1a2a3a; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; height:34px; box-sizing:border-box;">
+          <div class="game-gameover-basket-row">
+            <select id="pgn-lib-collection-select" class="game-gameover-lib-select" onchange="pgnLibSelectCollection(this.value)">
               <option value="" data-i18n="pgn_lib.select.vide">— Aucune collection —</option>
             </select>
-            <button class="btn" style="margin-bottom:0; padding:0 10px; white-space:nowrap; height:34px; box-sizing:border-box; background:#2e7d32; color:white;" onclick="pgnLibOpenCreateModal()" data-i18n-title="pgn_lib.btn.creer_title" title="Créer une collection">＋</button>
-            <button class="btn btn-warning" style="margin-bottom:0; padding:0 10px; white-space:nowrap; height:34px; box-sizing:border-box;" onclick="pgnLibConfirmDelete()" data-i18n-title="pgn_lib.btn.supprimer_title" title="Supprimer la collection">🗑</button>
+            <button class="btn game-gameover-lib-create-btn" data-action="pgn_lib_open_create_modal" data-i18n-title="pgn_lib.btn.creer_title" title="Créer une collection">＋</button>
+            <button class="btn btn-warning game-gameover-lib-delete-btn" data-action="pgn_lib_confirm_delete" data-i18n-title="pgn_lib.btn.supprimer_title" title="Supprimer la collection">🗑</button>
           </div>
 
           <!-- Import PGN dans la collection active -->
-          <input type="file" id="pgn-lib-file-input" accept=".pgn,text/plain" style="display:none" onchange="pgnLibImportFile(event)">
-          <button class="btn btn-best" id="pgn-lib-import-btn" style="margin-bottom:0;" onclick="document.getElementById('pgn-lib-file-input').click()" data-i18n="pgn_lib.btn.importer">📂 Importer PGN</button>
-          <div id="pgn-lib-import-spinner" style="display:none; align-items:center; gap:8px; color:#3a5a7a; font-size:0.8rem;">
-            <div style="width:14px; height:14px; border:2px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite;"></div>
+          <input type="file" id="pgn-lib-file-input" accept=".pgn,text/plain" class="game-gameover-file-input" onchange="pgnLibImportFile(event)">
+          <button class="btn btn-best game-gameover-btn-mb0" id="pgn-lib-import-btn" data-action="trigger_pgn_lib_file_input" data-i18n="pgn_lib.btn.importer">📂 Importer PGN</button>
+          <div id="pgn-lib-import-spinner" class="game-gameover-lib-spinner">
+            <div class="game-gameover-lib-spinner-circle"></div>
             <span data-i18n="pgn_lib.import_en_cours">Import en cours…</span>
           </div>
 
           <!-- Liste des parties de la collection active -->
-          <div id="pgn-lib-games-list" style="max-height:260px; overflow-y:auto; display:flex; flex-direction:column; gap:4px; border:1px solid #a0b8d0; border-radius:6px; padding:6px; background:#eef4fa;">
-            <div class="pgn-lib-empty" style="color:#778; font-size:0.8rem; text-align:center; padding:12px 0;" data-i18n="pgn_lib.liste_vide">Aucune partie dans cette collection.</div>
+          <div id="pgn-lib-games-list" class="game-gameover-lib-games-list">
+            <div class="pgn-lib-empty" data-i18n="pgn_lib.liste_vide">Aucune partie dans cette collection.</div>
           </div>
         </div>
 
         <!-- Sélecteur nombre de coups séquence -->
-        <div id="rv-seq-row" style="display:none; align-items:center; gap:8px;">
-          <label data-i18n="game.label.sequence" style="font-size:0.8rem; color:#3a5a7a; white-space:nowrap;">Séquence :</label>
-          <select id="rv-seq-moves" style="flex:1; background:#a0b8d0; color:#1a2a3a; border:1px solid #2a5a8a; border-radius:4px; padding:4px 8px; font-size:0.82rem;">
+        <div id="rv-seq-row" class="game-gameover-seq-row">
+          <label data-i18n="game.label.sequence" class="game-gameover-seq-label">Séquence :</label>
+          <select id="rv-seq-moves" class="game-gameover-seq-select">
             <option value="3" selected>3 coups</option>
             <option value="4">4 coups</option>
             <option value="5">5 coups</option>
           </select>
         </div>
-        <button class="btn btn-reprendre" style="margin-bottom:0; display:none;" id="btn-analyser"     onclick="lancerAnalyse()" data-i18n="labo.btn.analyser">🔍 Analyser la partie</button>
-        <button class="btn" style="margin-bottom:0; display:none; background:#9ab8d8; color:#1a2a3a; border:1px solid #2a5a8a;" id="btn-rv-sequence" onclick="jouerSequenceReview()" data-i18n="game.btn.sequence">🎬 Voir la séquence</button>
-        <button class="btn btn-reprendre" style="margin-bottom:0; display:none;" id="btn-telecharger"  onclick="telechargerPgn()" data-i18n="labo.btn.telecharger">⬇️ Télécharger PGN analysé</button>
-        <button class="btn btn-continuer" style="margin-bottom:0; display:none;" id="btn-vider-analyse" onclick="_viderAnalyse()" data-i18n="labo.btn.vider">🗑 Enlever la partie chargée</button>
-        <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+        <button class="btn btn-reprendre game-gameover-hidden-init" id="btn-analyser" data-action="lancer_analyse" data-i18n="labo.btn.analyser">🔍 Analyser la partie</button>
+        <button class="btn game-gameover-hidden-init game-gameover-btn-sequence" id="btn-rv-sequence" data-action="jouer_sequence_review" data-i18n="game.btn.sequence">🎬 Voir la séquence</button>
+        <button class="btn btn-reprendre game-gameover-hidden-init" id="btn-telecharger" data-action="telecharger_pgn" data-i18n="labo.btn.telecharger">⬇️ Télécharger PGN analysé</button>
+        <button class="btn btn-continuer game-gameover-hidden-init" id="btn-vider-analyse" data-action="vider_analyse" data-i18n="labo.btn.vider">🗑 Enlever la partie chargée</button>
+        <button class="btn game-gameover-btn-retour" data-action="back_menu" data-i18n="common.retour_menu">← Retour au menu</button>
       </div>
     </div>
   </div>
