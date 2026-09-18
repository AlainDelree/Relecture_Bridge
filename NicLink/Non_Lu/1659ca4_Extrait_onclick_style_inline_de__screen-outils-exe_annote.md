1659ca4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1659ca4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 24 17:20:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-outils-exercices vers data-action + CSS — Modifier une ouverture, Mise à jour Wikipedia (issue #248 partie 4/4)
    
    Clôture le chantier F8 (extraction onclick/style des 16 écrans de index.html).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4b0074f..0fbc9fa 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 365 (6 ligne(s)) dans l'ancienne version → ligne 365 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -365,6 +365,19 @@ document.addEventListener("click", (e) => {
     case "outils_add_reset":
       outilsAddReset();
       break;
+    case "outils_edit_refresh":
+      socket.emit('outils_edit_list', {});
+      document.getElementById('edit-list-wrap').innerHTML='<em style=color:#888>Chargement…</em>';
+      break;
+    case "outils_edit_save":
+      outilsEditSave();
+      break;
+    case "outils_edit_cancel":
+      document.getElementById('edit-form').style.display='none';
+      break;
+    case "outils_wiki_update":
+      outilsWikiUpdate();
+      break;
   }
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index db3b036..d239fe5 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 1532 (3 ligne(s)) dans l'ancienne version → ligne 1532 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1532,3 +1532,19 @@
 .outils-explore-btn-add-wrap { margin-top:12px; display:none; }
 .outils-add-btn-row { display:flex; gap:10px; margin-top:12px; flex-wrap:wrap; }
 .outils-add-preview { display:none; margin-top:14px; }
+
+/* ── Écran #screen-outils-exercices — Modifier une ouverture, Mise à jour Wikipedia (issue #248 partie 4/4) ── */
+.outils-edit-filter-row { display:flex; gap:8px; align-items:center; margin-bottom:10px; flex-wrap:wrap; }
+.outils-edit-filter-input { flex:1; min-width:180px; }
+.outils-edit-refresh-btn { padding:5px 12px; }
+.outils-edit-list-wrap { max-height:260px; overflow-y:auto; border:1px solid #a0b8d0; border-radius:6px; background:#f8fafc; }
+.outils-edit-list-loading { color:#888; padding:10px; display:block; }
+.outils-edit-form { display:none; margin-top:14px; border-top:1px solid #a0b8d0; padding-top:14px; }
+.outils-edit-form-header-row { display:flex; align-items:center; gap:10px; margin-bottom:12px; flex-wrap:wrap; }
+.outils-edit-form-label { font-weight:700; color:#1a2a3a; }
+.outils-edit-form-id { background:#e8eef4; padding:2px 8px; border-radius:4px; font-size:0.88rem; color:#1a2a3a; }
+.outils-edit-form-init { font-family:monospace; font-size:0.8rem; color:#888; }
+.outils-edit-result { display:none; margin-top:10px; }
+.outils-wiki-row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
+.outils-wiki-status { font-size:0.85rem; color:#3a5a7a; }
+.outils-wiki-result { display:none; margin-top:12px; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 65ef522..6ce9c6f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1421 (38 ligne(s)) dans l'ancienne version → ligne 1421 (37 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1421,38 +1421,37 @@
   </div>
 
   <!-- Modifier une ouverture -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card outils-card-w">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="outils.modifier.titre">✏️ Modifier une ouverture du catalogue</span>
     </div>
     <p class="outil-desc" data-i18n-html="outils.modifier.desc">Recherchez une ouverture, cliquez dessus et modifiez ses champs.</p>
 
-    <div style="display:flex; gap:8px; align-items:center; margin-bottom:10px; flex-wrap:wrap;">
-      <input id="edit-search" type="text" class="add-input" placeholder="Filtrer par ID, ECO ou nom…" data-i18n-placeholder="outils.edit.filter_placeholder"
-        style="flex:1; min-width:180px;" oninput="outilsEditFilter()">
-      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; padding:5px 12px;"
-        onclick="socket.emit('outils_edit_list', {}); document.getElementById('edit-list-wrap').innerHTML='<em style=color:#888>Chargement…</em>';" data-i18n="common.actualiser">🔄 Actualiser</button>
+    <div class="outils-edit-filter-row">
+      <input id="edit-search" type="text" class="add-input outils-edit-filter-input" placeholder="Filtrer par ID, ECO ou nom…" data-i18n-placeholder="outils.edit.filter_placeholder"
+        oninput="outilsEditFilter()">
+      <button class="btn outils-btn-secondary outils-edit-refresh-btn" data-action="outils_edit_refresh" data-i18n="common.actualiser">🔄 Actualiser</button>
     </div>
 
-    <div id="edit-list-wrap" style="max-height:260px; overflow-y:auto; border:1px solid #a0b8d0; border-radius:6px; background:#f8fafc;">
-      <em style="color:#888; padding:10px; display:block;">Chargement…</em>
+    <div id="edit-list-wrap" class="outils-edit-list-wrap">
+      <em class="outils-edit-list-loading">Chargement…</em>
     </div>
 
     <!-- Formulaire inline d'édition -->
-    <div id="edit-form" style="display:none; margin-top:14px; border-top:1px solid #a0b8d0; padding-top:14px;">
-      <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px; flex-wrap:wrap;">
-        <span style="font-weight:700; color:#1a2a3a;" data-i18n="outils.edit.titre">Édition :</span>
-        <code id="edit-form-id" style="background:#e8eef4; padding:2px 8px; border-radius:4px; font-size:0.88rem; color:#1a2a3a;"></code>
-        <span id="edit-form-init" style="font-family:monospace; font-size:0.8rem; color:#888;"></span>
+    <div id="edit-form" class="outils-edit-form">
+      <div class="outils-edit-form-header-row">
+        <span class="outils-edit-form-label" data-i18n="outils.edit.titre">Édition :</span>
+        <code id="edit-form-id" class="outils-edit-form-id"></code>
+        <span id="edit-form-init" class="outils-edit-form-init"></span>
       </div>
-      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px 18px;">
+      <div class="outils-add-grid">
         <div class="add-field">
           <label class="add-label" data-i18n="outils.label.nom">Nom</label>
           <input id="edit-nom" type="text" class="add-input">
         </div>
         <div class="add-field">
           <label class="add-label" data-i18n="outils.label.code_eco">Code ECO</label>
-          <input id="edit-eco" type="text" class="add-input" maxlength="4" style="text-transform:uppercase;">
+          <input id="edit-eco" type="text" class="add-input add-input-upper" maxlength="4">
         </div>
         <div class="add-field">
           <label class="add-label" data-i18n="outils.label.camp">Camp</label>
# ── Zone modifiée : ligne 1465 (37 ligne(s)) dans l'ancienne version → ligne 1464 (36 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1465,37 +1464,36 @@
           <label class="add-label" data-i18n="outils.label.livre">Livre (.bin)</label>
           <input id="edit-book" type="text" class="add-input">
         </div>
-        <div class="add-field" style="grid-column:1/-1;">
+        <div class="add-field add-field-full">
           <label class="add-label" data-i18n="outils.label.description">Description</label>
           <input id="edit-desc" type="text" class="add-input">
         </div>
-        <div class="add-field" style="grid-column:1/-1;">
+        <div class="add-field add-field-full">
           <label class="add-label" data-i18n="outils.label.parent_eco">Parent ECO</label>
           <input id="edit-parent-eco" type="text" class="add-input" maxlength="4">
         </div>
       </div>
-      <div style="display:flex; gap:10px; margin-top:12px; flex-wrap:wrap;">
-        <button class="btn btn-continuer" onclick="outilsEditSave()" data-i18n="outils.modifier.enregistrer">💾 Enregistrer</button>
-        <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;"
-          onclick="document.getElementById('edit-form').style.display='none';" data-i18n="common.annuler">Annuler</button>
+      <div class="outils-add-btn-row">
+        <button class="btn btn-continuer" data-action="outils_edit_save" data-i18n="outils.modifier.enregistrer">💾 Enregistrer</button>
+        <button class="btn outils-btn-secondary" data-action="outils_edit_cancel" data-i18n="common.annuler">Annuler</button>
       </div>
-      <div id="edit-result" style="display:none; margin-top:10px;"></div>
+      <div id="edit-result" class="outils-edit-result"></div>
     </div>
   </div>
 
   <!-- Màj ECO Wikipedia -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card outils-card-w">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="outils.wiki.titre">🌐 Mettre à jour eco_hierarchy.json</span>
     </div>
     <p class="outil-desc" data-i18n-html="outils.wiki.desc">Télécharge la liste ECO depuis Wikipedia et reconstruit <code>eco_hierarchy.json</code> — utilisé pour les codes parent ECO lors de l'ajout et l'import ECO.</p>
 
-    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
-      <button id="wiki-btn" class="btn btn-continuer" onclick="outilsWikiUpdate()" data-i18n="outils.wiki.btn">🌐 Mettre à jour depuis Wikipedia</button>
-      <span id="wiki-status" style="font-size:0.85rem; color:#3a5a7a;"></span>
+    <div class="outils-wiki-row">
+      <button id="wiki-btn" class="btn btn-continuer" data-action="outils_wiki_update" data-i18n="outils.wiki.btn">🌐 Mettre à jour depuis Wikipedia</button>
+      <span id="wiki-status" class="outils-wiki-status"></span>
     </div>
 
-    <div id="wiki-result" style="display:none; margin-top:12px;"></div>
+    <div id="wiki-result" class="outils-wiki-result"></div>
   </div>
 
 </div>
