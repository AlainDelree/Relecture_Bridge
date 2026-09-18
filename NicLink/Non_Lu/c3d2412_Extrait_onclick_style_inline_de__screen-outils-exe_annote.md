c3d2412

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c3d2412
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 24 17:07:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-outils-exercices vers data-action + CSS — en-tête, Importer PGN, Convertir SAN→UCI (issue #245 partie 1/4)
    
    11 onclick migrés vers data-action (back_menu et aide_panier réutilisés,
    7 nouveaux cases dont outils_uci_copy et outils_uci_clear qui conservent
    le code JS exact). 32 style inline extraits vers des classes .outils-*
    dans main.css (dont suppression de styles redondants avec .basket-select/
    .basket-sel-label/.basket-sel-arrow déjà en place). Sélecteurs e2e migrés
    vers data-action : back_menu, outils_san_to_uci (×3), basket_load_to_outils_pgn/
    uci (×6) — dépendances identifiées dans l'issue #245 pour test_outils_exercices_e2e.py
    (issue #211). Grep exhaustif sur nicsoft/tests/e2e/*.py confirmant qu'aucune
    autre dépendance n'a été manquée. Suites pytest (78 passed) et e2e
    (42 passed) complètes au vert.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/tests/e2e/test_outils_exercices_e2e.py b/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6f121f9..fa3c5b4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Zone modifiée : ligne 69 (8 ligne(s)) dans l'ancienne version → ligne 69 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -69,8 +69,9 @@ def test_outils_exercices_accessible(at_menu):
 
 def test_retour_menu_depuis_outils(at_outils):
     """Outils Exercices → Retour au menu → menu propre."""
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("#screen-outils-exercices button[onclick*=\"back_menu\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #245 partie 1/4)
+    at_outils.locator("#screen-outils-exercices button[data-action=\"back_menu\"]").click()
     at_outils.wait_for_selector("#screen-menu", state="visible", timeout=5000)
     assert at_outils.locator("#screen-menu").is_visible()
 
# ── Zone modifiée : ligne 97 (8 ligne(s)) dans l'ancienne version → ligne 98 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -97,8 +98,9 @@ def test_ordre_des_outils(at_outils):
 def test_convertir_san_uci_valide(at_outils):
     """SAN valide '1. e4 e5 2. Nf3 Nc6 3. Bb5' → résultat UCI contient 'e2e4'."""
     at_outils.locator("#outils-uci-input").fill("1. e4 e5 2. Nf3 Nc6 3. Bb5")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsSanToUci()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #245 partie 1/4)
+    at_outils.locator("button[data-action=\"outils_san_to_uci\"]").click()
     result = at_outils.locator("#outils-uci-result")
     result.wait_for(state="visible", timeout=5000)
     # Attendre la réponse socket (le div montre "Conversion…" pendant le traitement)
# ── Zone modifiée : ligne 108 (8 ligne(s)) dans l'ancienne version → ligne 110 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -108,8 +110,9 @@ def test_convertir_san_uci_valide(at_outils):
 def test_convertir_san_uci_resultat_complet(at_outils):
     """Conversion '1. d4 d5' → résultat contient d2d4 et d7d5."""
     at_outils.locator("#outils-uci-input").fill("1. d4 d5")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsSanToUci()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #245 partie 1/4)
+    at_outils.locator("button[data-action=\"outils_san_to_uci\"]").click()
     result = at_outils.locator("#outils-uci-result")
     result.wait_for(state="visible", timeout=5000)
     expect(result).to_contain_text("d2d4", timeout=5000)
# ── Zone modifiée : ligne 119 (8 ligne(s)) dans l'ancienne version → ligne 122 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -119,8 +122,9 @@ def test_convertir_san_uci_resultat_complet(at_outils):
 def test_convertir_san_uci_sans_coups(at_outils):
     """PGN non reconnu → résultat chargé mais InitMoves vide (pas de coups UCI)."""
     at_outils.locator("#outils-uci-input").fill("xxx yyy zzz")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsSanToUci()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #245 partie 1/4)
+    at_outils.locator("button[data-action=\"outils_san_to_uci\"]").click()
     result = at_outils.locator("#outils-uci-result")
     result.wait_for(state="visible", timeout=5000)
     # Attendre que "Conversion…" disparaisse (réponse reçue)
# ── Zone modifiée : ligne 334 (28 ligne(s)) dans l'ancienne version → ligne 338 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -334,28 +338,28 @@ def test_corbeille_labels_vides(at_outils):
 
 def test_corbeille_boutons_charger_desactives_si_vide(at_outils):
     """Boutons 🧺 Charger désactivés quand la corbeille est vide."""
-    assert at_outils.locator("button[onclick='basketLoadToOutilsPgn()']").is_disabled()
-    assert at_outils.locator("button[onclick='basketLoadToOutilsUci()']").is_disabled()
+    assert at_outils.locator('button[data-action="basket_load_to_outils_pgn"]').is_disabled()
+    assert at_outils.locator('button[data-action="basket_load_to_outils_uci"]').is_disabled()
 
 
 def test_corbeille_boutons_actives_apres_ajout(at_outils):
     """Après ajout d'une partie en corbeille, les boutons Charger s'activent."""
     at_outils.evaluate("socket.emit('basket_add', {label: 'test_e2e.pgn', pgn: '1. e4 e5 *'})")
     at_outils.wait_for_function("typeof _basket !== 'undefined' && _basket.length > 0", timeout=5000)
-    assert not at_outils.locator("button[onclick='basketLoadToOutilsPgn()']").is_disabled()
-    assert not at_outils.locator("button[onclick='basketLoadToOutilsUci()']").is_disabled()
+    assert not at_outils.locator('button[data-action="basket_load_to_outils_pgn"]').is_disabled()
+    assert not at_outils.locator('button[data-action="basket_load_to_outils_uci"]').is_disabled()
 
 
 def test_corbeille_charger_uci_remplit_textarea(at_outils):
     """Charger depuis corbeille dans 'Convertir SAN → UCI' remplit le textarea."""
     at_outils.locator("#outils-uci-input").fill("")
-    at_outils.locator("button[onclick='basketLoadToOutilsUci()']").click()
+    at_outils.locator('button[data-action="basket_load_to_outils_uci"]').click()
     at_outils.wait_for_function("document.getElementById('outils-uci-input').value.length > 0", timeout=5000)
     assert len(at_outils.locator("#outils-uci-input").input_value()) > 0
 
 
 def test_corbeille_charger_pgn_affiche_preview(at_outils):
     """Charger depuis corbeille dans 'Importer mes lignes PGN' affiche la prévisualisation."""
-    at_outils.locator("button[onclick='basketLoadToOutilsPgn()']").click()
+    at_outils.locator('button[data-action="basket_load_to_outils_pgn"]').click()
     at_outils.locator("#outils-pgn-preview-list").wait_for(state="visible", timeout=8000)
     assert at_outils.locator("#outils-pgn-preview-list").is_visible()
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 56dfc33..a12c484 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 310 (6 ligne(s)) dans l'ancienne version → ligne 310 (31 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -310,6 +310,31 @@ document.addEventListener("click", (e) => {
     case "vider_analyse":
       _viderAnalyse();
       break;
+    case "outils_trigger_pgn_input":
+      document.getElementById("outils-pgn-input").click();
+      break;
+    case "basket_load_to_outils_pgn":
+      basketLoadToOutilsPgn();
+      break;
+    case "outils_pgn_import":
+      outilsPgnImport();
+      break;
+    case "outils_pgn_clear":
+      outilsPgnClear();
+      break;
+    case "basket_load_to_outils_uci":
+      basketLoadToOutilsUci();
+      break;
+    case "outils_uci_copy":
+      navigator.clipboard.writeText(document.getElementById("outils-uci-input").value).then(() => afficherToast("Copié !", "success"));
+      break;
+    case "outils_san_to_uci":
+      outilsSanToUci();
+      break;
+    case "outils_uci_clear":
+      document.getElementById("outils-uci-input").value = "";
+      document.getElementById("outils-uci-result").style.display = "none";
+      break;
   }
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index a7c8a02..e261a19 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 169 (6 ligne(s)) dans l'ancienne version → ligne 169 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -169,6 +169,15 @@
       overflow-y: auto;
       width: 100%;
     }
+    #screen-outils-exercices {
+      display: none;
+      flex-direction: column;
+      align-items: center;
+      padding: 24px;
+      gap: 20px;
+      overflow-y: auto;
+      width: 100%;
+    }
     /* Grille unifiée pour tous les écrans avec échiquier */
     .screen-board-layout {
       display: none;
# ── Zone modifiée : ligne 1456 (3 ligne(s)) dans l'ancienne version → ligne 1465 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1456,3 +1465,23 @@
 .game-gameover-hidden-init { margin-bottom:0; display:none; }
 .game-gameover-btn-sequence { background:#9ab8d8; color:#1a2a3a; border:1px solid #2a5a8a; }
 .game-gameover-btn-retour { background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0; }
+
+/* ── Écran #screen-outils-exercices — en-tête, Importer PGN, Convertir SAN→UCI (issue #245 partie 1/4) ── */
+.outils-header-row { width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
+.outils-header-title { margin:0; color:#1a2a3a; font-size:1.4rem; }
+.outils-btn-secondary { background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; }
+.outils-card-w { width:100%; max-width:860px; }
+.outils-pgn-dropzone { border:2px dashed #a0b8d0; border-radius:8px; padding:20px; text-align:center; cursor:pointer; color:#3a5a7a; margin-bottom:12px; }
+.outils-pgn-dropzone-icon { font-size:1.8rem; margin-bottom:6px; }
+.outils-pgn-file-input { display:none; }
+.outils-basket-row { display:flex; gap:6px; align-items:stretch; margin-bottom:12px; }
+.outils-pgn-preview-list { display:none; margin-bottom:12px; }
+.outils-btn-row { display:flex; gap:10px; flex-wrap:wrap; }
+.outils-hidden-init { display:none; }
+.outils-pgn-result { display:none; margin-top:12px; padding:12px; border-radius:6px; }
+.outils-uci-textarea-wrap { position:relative; }
+.outils-uci-textarea { width:100%; box-sizing:border-box; font-family:monospace; font-size:0.9rem; padding:8px 36px 8px 8px; border:1px solid #a0b8d0; border-radius:6px; background:#f0f4f8; color:#1a2a3a; resize:vertical; }
+.outils-uci-copy-btn { position:absolute; top:6px; right:6px; background:none; border:none; cursor:pointer; font-size:0.95rem; color:#a0b8d0; padding:2px 4px; line-height:1; border-radius:4px; transition:color 0.15s; }
+.outils-uci-copy-btn:hover { color:#3a5a7a; }
+.outils-uci-btn-row { display:flex; gap:10px; margin-top:8px; flex-wrap:wrap; }
+.outils-uci-result { display:none; margin-top:12px; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index fafd973..1e4d483 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1156 (84 ligne(s)) dans l'ancienne version → ligne 1156 (82 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1156,84 +1156,82 @@
 
 
 <!-- ── Écran Outils Exercices ── -->
-<div id="screen-outils-exercices" style="display:none; flex-direction:column; align-items:center; padding:24px; gap:20px; overflow-y:auto; width:100%;">
+<div id="screen-outils-exercices">
 
-  <div style="width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
-    <h2 style="margin:0; color:#1a2a3a; font-size:1.4rem;" data-i18n="outils.titre">🛠️ Outils Exercices</h2>
-    <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+  <div class="outils-header-row">
+    <h2 class="outils-header-title" data-i18n="outils.titre">🛠️ Outils Exercices</h2>
+    <button class="btn outils-btn-secondary" data-action="back_menu" data-i18n="common.retour_menu">← Retour au menu</button>
   </div>
 
   <!-- Importer mes lignes PGN -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card outils-card-w">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="outils.import_pgn.titre">📥 Importer mes lignes PGN</span>
     </div>
     <p class="outil-desc" data-i18n-html="outils.import_pgn.desc">Sélectionnez un ou plusieurs fichiers .pgn pour les importer dans vos exercices personnels (<em>mes_lignes.json</em>).</p>
 
     <!-- Zone d'upload -->
-    <div id="outils-pgn-dropzone" style="border:2px dashed #a0b8d0; border-radius:8px; padding:20px; text-align:center; cursor:pointer; color:#3a5a7a; margin-bottom:12px;"
-         onclick="document.getElementById('outils-pgn-input').click()"
+    <div id="outils-pgn-dropzone" class="outils-pgn-dropzone"
+         data-action="outils_trigger_pgn_input"
          ondragover="event.preventDefault(); this.style.borderColor='#e94560';"
          ondragleave="this.style.borderColor='#a0b8d0';"
          ondrop="outilsPgnDrop(event)">
-      <div style="font-size:1.8rem; margin-bottom:6px;">📄</div>
+      <div class="outils-pgn-dropzone-icon">📄</div>
       <div data-i18n-html="outils.pgn.drop_zone">Cliquez ou déposez vos fichiers <strong>.pgn</strong> ici</div>
     </div>
-    <input type="file" id="outils-pgn-input" accept=".pgn" multiple style="display:none;" onchange="outilsPgnFilesSelected(this.files)">
+    <input type="file" id="outils-pgn-input" accept=".pgn" multiple class="outils-pgn-file-input" onchange="outilsPgnFilesSelected(this.files)">
 
     <!-- Classeur de session -->
-    <div style="display:flex; gap:6px; align-items:stretch; margin-bottom:12px;">
-      <span class="aide-panier-icone" onclick="ouvrirAidePanier()" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
-      <div id="basket-select-outils-pgn" class="basket-select" data-value="" style="flex:1; position:relative; height:34px; box-sizing:border-box; background:#a0b8d0; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; display:flex; align-items:center; justify-content:space-between; cursor:pointer; user-select:none;">
-        <span class="basket-sel-label" data-i18n="common.corbeille_vide" style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#556;">— classeur vide —</span>
-        <span style="font-size:0.6rem; margin-left:4px; color:#1a2a3a; flex-shrink:0;">▼</span>
-        <div class="basket-sel-list" style="display:none; position:absolute; bottom:100%; left:0; right:0; background:#1a2a3a; border:1px solid #a0b8d0; border-bottom:none; border-radius:4px 4px 0 0; z-index:200; max-height:180px; overflow-y:auto;"></div>
+    <div class="outils-basket-row">
+      <span class="aide-panier-icone" data-action="aide_panier" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
+      <div id="basket-select-outils-pgn" class="basket-select" data-value="">
+        <span class="basket-sel-label" data-i18n="common.corbeille_vide">— classeur vide —</span>
+        <span class="basket-sel-arrow">▼</span>
+        <div class="basket-sel-list basket-sel-list-up" style="display:none;"></div>
       </div>
-      <button class="btn basket-load-btn" style="margin-bottom:0; padding:0 12px; white-space:nowrap; height:34px; box-sizing:border-box;" disabled onclick="basketLoadToOutilsPgn()" data-i18n="common.charger">🗂️ Charger</button>
+      <button class="btn basket-load-btn" disabled data-action="basket_load_to_outils_pgn" data-i18n="common.charger">🗂️ Charger</button>
     </div>
 
     <!-- Liste de prévisualisation -->
-    <div id="outils-pgn-preview-list" style="display:none; margin-bottom:12px;"></div>
+    <div id="outils-pgn-preview-list" class="outils-pgn-preview-list"></div>
 
     <!-- Boutons d'action -->
-    <div style="display:flex; gap:10px; flex-wrap:wrap;">
-      <button id="outils-pgn-btn-import" class="btn btn-continuer" style="display:none;" onclick="outilsPgnImport()" data-i18n="outils.import_pgn.btn">✅ Importer</button>
-      <button id="outils-pgn-btn-clear" class="btn" style="display:none; background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="outilsPgnClear()" data-i18n="common.effacer">✕ Effacer</button>
+    <div class="outils-btn-row">
+      <button id="outils-pgn-btn-import" class="btn btn-continuer outils-hidden-init" data-action="outils_pgn_import" data-i18n="outils.import_pgn.btn">✅ Importer</button>
+      <button id="outils-pgn-btn-clear" class="btn outils-btn-secondary outils-hidden-init" data-action="outils_pgn_clear" data-i18n="common.effacer">✕ Effacer</button>
     </div>
 
     <!-- Résultat import -->
-    <div id="outils-pgn-result" style="display:none; margin-top:12px; padding:12px; border-radius:6px;"></div>
+    <div id="outils-pgn-result" class="outils-pgn-result"></div>
   </div>
 
   <!-- Convertir SAN → UCI -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card outils-card-w">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="outils.convertir.titre">🔄 Convertir SAN → UCI</span>
     </div>
     <p class="outil-desc" data-i18n-html="outils.convertir.desc">Collez une ligne PGN (ex&nbsp;: <code>1. e4 e5 2. Nf3 Nc6 3. Bb5</code>) et obtenez les codes UCI pour le champ <code>[InitMoves]</code>.</p>
     <!-- Classeur de session -->
-    <div style="display:flex; gap:6px; align-items:stretch; margin-bottom:12px;">
-      <span class="aide-panier-icone" onclick="ouvrirAidePanier()" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
-      <div id="basket-select-outils-uci" class="basket-select" data-value="" style="flex:1; position:relative; height:34px; box-sizing:border-box; background:#a0b8d0; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; display:flex; align-items:center; justify-content:space-between; cursor:pointer; user-select:none;">
-        <span class="basket-sel-label" data-i18n="common.corbeille_vide" style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#556;">— classeur vide —</span>
-        <span style="font-size:0.6rem; margin-left:4px; color:#1a2a3a; flex-shrink:0;">▼</span>
-        <div class="basket-sel-list" style="display:none; position:absolute; bottom:100%; left:0; right:0; background:#1a2a3a; border:1px solid #a0b8d0; border-bottom:none; border-radius:4px 4px 0 0; z-index:200; max-height:180px; overflow-y:auto;"></div>
+    <div class="outils-basket-row">
+      <span class="aide-panier-icone" data-action="aide_panier" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
+      <div id="basket-select-outils-uci" class="basket-select" data-value="">
+        <span class="basket-sel-label" data-i18n="common.corbeille_vide">— classeur vide —</span>
+        <span class="basket-sel-arrow">▼</span>
+        <div class="basket-sel-list basket-sel-list-up" style="display:none;"></div>
       </div>
-      <button class="btn basket-load-btn" style="margin-bottom:0; padding:0 12px; white-space:nowrap; height:34px; box-sizing:border-box;" disabled onclick="basketLoadToOutilsUci()" data-i18n="common.charger">🗂️ Charger</button>
+      <button class="btn basket-load-btn" disabled data-action="basket_load_to_outils_uci" data-i18n="common.charger">🗂️ Charger</button>
     </div>
 
-    <div style="position:relative;">
+    <div class="outils-uci-textarea-wrap">
       <textarea id="outils-uci-input" placeholder="Collez votre PGN ici…" data-i18n-placeholder="outils.convertir.pgn_placeholder" rows="3"
-        style="width:100%; box-sizing:border-box; font-family:monospace; font-size:0.9rem; padding:8px 36px 8px 8px; border:1px solid #a0b8d0; border-radius:6px; background:#f0f4f8; color:#1a2a3a; resize:vertical;"></textarea>
-      <button title="Copier" onclick="navigator.clipboard.writeText(document.getElementById('outils-uci-input').value).then(()=>afficherToast('Copié !','success'))"
-        style="position:absolute; top:6px; right:6px; background:none; border:none; cursor:pointer; font-size:0.95rem; color:#a0b8d0; padding:2px 4px; line-height:1; border-radius:4px; transition:color 0.15s;"
-        onmouseover="this.style.color='#3a5a7a'" onmouseout="this.style.color='#a0b8d0'">📋</button>
+        class="outils-uci-textarea"></textarea>
+      <button title="Copier" data-action="outils_uci_copy" class="outils-uci-copy-btn">📋</button>
     </div>
-    <div style="display:flex; gap:10px; margin-top:8px; flex-wrap:wrap;">
-      <button class="btn btn-continuer" onclick="outilsSanToUci()" data-i18n="outils.uci.convertir">Convertir</button>
-      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="document.getElementById('outils-uci-input').value=''; document.getElementById('outils-uci-result').style.display='none';" data-i18n="common.effacer">Effacer</button>
+    <div class="outils-uci-btn-row">
+      <button class="btn btn-continuer" data-action="outils_san_to_uci" data-i18n="outils.uci.convertir">Convertir</button>
+      <button class="btn outils-btn-secondary" data-action="outils_uci_clear" data-i18n="common.effacer">Effacer</button>
     </div>
-    <div id="outils-uci-result" style="display:none; margin-top:12px;"></div>
+    <div id="outils-uci-result" class="outils-uci-result"></div>
   </div>
 
   <!-- Importer depuis ECO Lichess -->
