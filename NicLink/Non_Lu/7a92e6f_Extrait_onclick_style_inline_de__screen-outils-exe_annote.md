7a92e6f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7a92e6f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 24 17:15:45 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-outils-exercices vers data-action + CSS — Ajouter une ouverture au catalogue (issue #247 partie 3/4)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/tests/e2e/test_outils_exercices_e2e.py b/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c003b0e..e973947 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/tests/e2e/test_outils_exercices_e2e.py
# ── Zone modifiée : ligne 159 (8 ligne(s)) dans l'ancienne version → ligne 159 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -159,8 +159,9 @@ def test_ajouter_verifier_preview(at_outils):
     at_outils.locator("#add-nom").dispatch_event("input")
     at_outils.locator("#add-eco").fill("C65")
     at_outils.locator("#add-moves").fill("e2e4 e7e5 g1f3 b8c6 f1b5")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsAddVerify()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #247 partie 3/4)
+    at_outils.locator("button[data-action=\"outils_add_verify\"]").click()
     preview = at_outils.locator("#outils-add-preview")
     preview.wait_for(state="visible", timeout=5000)
     assert preview.is_visible()
# ── Zone modifiée : ligne 170 (8 ligne(s)) dans l'ancienne version → ligne 171 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -170,8 +171,9 @@ def test_ajouter_effacer_remet_a_zero(at_outils):
     """Bouton ✕ Effacer vide les champs Ajouter."""
     at_outils.locator("#add-nom").fill("Test Effacer")
     at_outils.locator("#add-moves").fill("e2e4 e7e5")
-    # Ciblage par attribut onclick, indépendant de la locale (issue #211, cf. #208)
-    at_outils.locator("button[onclick=\"outilsAddReset()\"]").click()
+    # Ciblage par attribut data-action, indépendant de la locale (issue #211, cf. #208,
+    # migré vers data-action en #247 partie 3/4)
+    at_outils.locator("button[data-action=\"outils_add_reset\"]").click()
     assert at_outils.locator("#add-nom").input_value() == ""
     assert at_outils.locator("#add-moves").input_value() == ""
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 86184d5..4b0074f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 350 (6 ligne(s)) dans l'ancienne version → ligne 350 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -350,6 +350,21 @@ document.addEventListener("click", (e) => {
     case "explore_reset":
       exploreReset();
       break;
+    case "explore_add_verify":
+      exploreAddVerify();
+      break;
+    case "explore_add_cancel":
+      document.getElementById("explore-add-section").style.display = "none";
+      break;
+    case "explore_open_add":
+      exploreOpenAdd();
+      break;
+    case "outils_add_verify":
+      outilsAddVerify();
+      break;
+    case "outils_add_reset":
+      outilsAddReset();
+      break;
   }
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 7c347cb..65ef522 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1326 (20 ligne(s)) dans l'ancienne version → ligne 1326 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1326,20 +1326,20 @@
       </div>
 
       <!-- Section ajout au catalogue -->
-      <div id="explore-add-section" style="display:none; margin-top:16px; border-top:1px solid #a0b8d0; padding-top:14px;">
-        <div style="font-weight:700; color:#1a2a3a; margin-bottom:10px; font-size:0.95rem;" data-i18n="outils.polyglot.ajouter_ligne">➕ Ajouter cette ligne au catalogue</div>
-        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px 18px;">
+      <div id="explore-add-section" class="outils-explore-add-section">
+        <div class="outils-explore-add-title" data-i18n="outils.polyglot.ajouter_ligne">➕ Ajouter cette ligne au catalogue</div>
+        <div class="outils-add-grid">
           <div class="add-field">
-            <label class="add-label" data-i18n="outils.label.nom">Nom <span style="color:#e94560">*</span></label>
+            <label class="add-label" data-i18n="outils.label.nom">Nom <span class="add-required">*</span></label>
             <input id="explore-add-nom" type="text" class="add-input" placeholder="Ruy Lopez — Défense de Berlin" data-i18n-placeholder="outils.ajouter.nom_placeholder" oninput="exploreAutoId()">
           </div>
           <div class="add-field">
-            <label class="add-label" data-i18n="outils.label.id_unique">ID unique <span style="color:#e94560">*</span></label>
+            <label class="add-label" data-i18n="outils.label.id_unique">ID unique <span class="add-required">*</span></label>
             <input id="explore-add-id" type="text" class="add-input">
           </div>
           <div class="add-field">
             <label class="add-label" data-i18n="outils.label.code_eco">Code ECO</label>
-            <input id="explore-add-eco" type="text" class="add-input" placeholder="C65" maxlength="4" style="text-transform:uppercase;">
+            <input id="explore-add-eco" type="text" class="add-input add-input-upper" placeholder="C65" maxlength="4">
           </div>
           <div class="add-field">
             <label class="add-label" data-i18n="outils.label.camp">Camp</label>
# ── Zone modifiée : ligne 1348 (48 ligne(s)) dans l'ancienne version → ligne 1348 (48 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1348,48 +1348,48 @@
               <option value="black" data-i18n="outils.camp.noirs">Noirs</option>
             </select>
           </div>
-          <div class="add-field" style="grid-column:1/-1;">
+          <div class="add-field add-field-full">
             <label class="add-label" data-i18n="outils.label.description">Description</label>
             <input id="explore-add-desc" type="text" class="add-input" placeholder="Description courte" data-i18n-placeholder="outils.polyglot.desc_placeholder">
           </div>
         </div>
-        <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
-          <button class="btn btn-continuer" onclick="exploreAddVerify()" data-i18n="outils.polyglot.verifier">🔍 Vérifier</button>
-          <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="document.getElementById('explore-add-section').style.display='none';" data-i18n="common.annuler">Annuler</button>
+        <div class="outils-explore-add-btn-row">
+          <button class="btn btn-continuer" data-action="explore_add_verify" data-i18n="outils.polyglot.verifier">🔍 Vérifier</button>
+          <button class="btn outils-btn-secondary" data-action="explore_add_cancel" data-i18n="common.annuler">Annuler</button>
         </div>
-        <div id="explore-add-preview" style="display:none; margin-top:10px;"></div>
+        <div id="explore-add-preview" class="outils-explore-add-preview"></div>
       </div>
 
       <!-- Bouton ouvrir ajout -->
-      <div id="explore-btn-add-wrap" style="margin-top:12px; display:none;">
-        <button class="btn btn-continuer" onclick="exploreOpenAdd()" data-i18n="outils.polyglot.ajouter_btn">➕ Ajouter au catalogue</button>
+      <div id="explore-btn-add-wrap" class="outils-explore-btn-add-wrap">
+        <button class="btn btn-continuer" data-action="explore_open_add" data-i18n="outils.polyglot.ajouter_btn">➕ Ajouter au catalogue</button>
       </div>
     </div>
   </div>
 
   <!-- Ajouter une ouverture manuellement -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card outils-card-w">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="outils.ajouter.titre">➕ Ajouter une ouverture au catalogue</span>
     </div>
     <p class="outil-desc" data-i18n-html="outils.ajouter.desc">Saisissez les informations et les coups (en UCI, ex&nbsp;: <code>e2e4 e7e5 g1f3</code>). Utilisez <strong>Convertir SAN → UCI</strong> ci-dessus pour convertir depuis PGN.</p>
 
-    <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px 18px;">
+    <div class="outils-add-grid">
 
       <div class="add-field">
-        <label class="add-label" data-i18n="outils.label.nom">Nom <span style="color:#e94560">*</span></label>
+        <label class="add-label" data-i18n="outils.label.nom">Nom <span class="add-required">*</span></label>
         <input id="add-nom" type="text" class="add-input" placeholder="Ruy Lopez — Défense de Berlin" data-i18n-placeholder="outils.ajouter.nom_placeholder"
           oninput="outilsAddAutoId()">
       </div>
 
       <div class="add-field">
-        <label class="add-label" data-i18n="outils.label.id_unique">ID unique <span style="color:#e94560">*</span></label>
+        <label class="add-label" data-i18n="outils.label.id_unique">ID unique <span class="add-required">*</span></label>
         <input id="add-id" type="text" class="add-input" placeholder="ruy_lopez_berlin">
       </div>
 
       <div class="add-field">
         <label class="add-label" data-i18n="outils.label.code_eco">Code ECO</label>
-        <input id="add-eco" type="text" class="add-input" placeholder="C65" maxlength="4" style="text-transform:uppercase;">
+        <input id="add-eco" type="text" class="add-input add-input-upper" placeholder="C65" maxlength="4">
       </div>
 
       <div class="add-field">
# ── Zone modifiée : ligne 1400 (24 ligne(s)) dans l'ancienne version → ligne 1400 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1400,24 +1400,24 @@
         </select>
       </div>
 
-      <div class="add-field" style="grid-column:1/-1;">
+      <div class="add-field add-field-full">
         <label class="add-label" data-i18n="outils.label.description">Description</label>
         <input id="add-desc" type="text" class="add-input" placeholder="Description courte de la ligne" data-i18n-placeholder="outils.ajouter.desc_placeholder">
       </div>
 
-      <div class="add-field" style="grid-column:1/-1;">
-        <label class="add-label" data-i18n="outils.label.coups_uci">Coups UCI <span style="color:#e94560">*</span></label>
-        <input id="add-moves" type="text" class="add-input" placeholder="e2e4 e7e5 g1f3 b8c6 f1b5" style="font-family:monospace;">
+      <div class="add-field add-field-full">
+        <label class="add-label" data-i18n="outils.label.coups_uci">Coups UCI <span class="add-required">*</span></label>
+        <input id="add-moves" type="text" class="add-input add-input-mono" placeholder="e2e4 e7e5 g1f3 b8c6 f1b5">
       </div>
 
     </div>
 
-    <div style="display:flex; gap:10px; margin-top:12px; flex-wrap:wrap;">
-      <button class="btn btn-continuer" onclick="outilsAddVerify()" data-i18n="outils.polyglot.verifier">🔍 Vérifier</button>
-      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="outilsAddReset()" data-i18n="common.effacer">✕ Effacer</button>
+    <div class="outils-add-btn-row">
+      <button class="btn btn-continuer" data-action="outils_add_verify" data-i18n="outils.polyglot.verifier">🔍 Vérifier</button>
+      <button class="btn outils-btn-secondary" data-action="outils_add_reset" data-i18n="common.effacer">✕ Effacer</button>
     </div>
 
-    <div id="outils-add-preview" style="display:none; margin-top:14px;"></div>
+    <div id="outils-add-preview" class="outils-add-preview"></div>
   </div>
 
   <!-- Modifier une ouverture -->
