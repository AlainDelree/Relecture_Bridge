7b187d6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7b187d6
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 18:56:26 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-parametres vers data-action + CSS (issue #226)
    
    Remplace les 2 attributs onclick= du bloc #screen-parametres par le
    mécanisme data-action (issue #220) : bouton retour → case "back_menu"
    existant, réutilise .btn-continuer (mêmes valeurs exactes que l'ancien
    style inline). Bouton "Enregistrer" → nouveau case "parametres_save"
    dans le switch délégué d'app.js, appelant parametresSave() inchangée.
    
    Remplace les 12 style= inline par des classes dédiées dans main.css
    (.screen-parametres, .parametres-header/.parametres-h2/.parametres-card/
    .parametres-llm-fields/.parametres-tts-toggle/.parametres-tts-checkbox/
    .parametres-tts-rate-row/.parametres-tts-rate/.parametres-actions).
    
    Le oninput="document.getElementById('param-tts-rate-val').textContent =
    this.value" du slider de débit TTS est laissé tel quel (hors périmètre
    onclick/style, même traitement que oninput/onchange dans #220/#225).
    
    Aucun sélecteur e2e ne cible ce bloc (grep exhaustif sur
    nicsoft/tests/e2e/*.py) — aucune correction de test nécessaire.
    
    Suite pytest complète (78 passed, 1 skipped, e2e inclus) au vert
    après modification.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8ab2b93..f3c7e33 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 76 (6 ligne(s)) dans l'ancienne version → ligne 76 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -76,6 +76,9 @@ document.addEventListener("click", (e) => {
     case "back_menu":
       sendAction({ type: "back_menu" });
       break;
+    case "parametres_save":
+      parametresSave();
+      break;
     case "quit_modal":
       ouvrirModal("quit", t("modal.quitter_alchess"), t("modal.quitter_btn"), "btn-warning");
       break;
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index 0628575..a6e6f15 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 883 (6 ligne(s)) dans l'ancienne version → ligne 883 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -883,6 +883,18 @@
 .pos-init-attente { display:flex; align-items:center; gap:10px; color:#2a3a4a; font-size:0.85rem; }
 .pos-init-spinner { width:14px; height:14px; border:2px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite; flex-shrink:0; }
 
+/* ── Écran "Paramètres" ── */
+.screen-parametres { display:none; flex-direction:column; align-items:center; padding:24px; gap:20px; overflow-y:auto; width:100%; }
+.parametres-header { width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
+.parametres-h2 { margin:0; color:#1a2a3a; font-size:1.4rem; }
+.parametres-card { width:100%; max-width:860px; }
+.parametres-llm-fields { display:flex; flex-direction:column; gap:12px; }
+.parametres-tts-toggle { display:flex; align-items:center; gap:8px; margin-bottom:12px; }
+.parametres-tts-checkbox { width:16px; height:16px; cursor:pointer; accent-color:#e94560; }
+.parametres-tts-rate-row { display:flex; align-items:center; gap:10px; }
+.parametres-tts-rate { width:200px; accent-color:#e94560; }
+.parametres-actions { width:100%; max-width:860px; display:flex; gap:10px; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 2f20b33..ccafaa2 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1548 (21 ligne(s)) dans l'ancienne version → ligne 1548 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1548,21 +1548,21 @@
 
 
 <!-- ── Écran Paramètres ── -->
-<div id="screen-parametres" style="display:none; flex-direction:column; align-items:center; padding:24px; gap:20px; overflow-y:auto; width:100%;">
+<div id="screen-parametres" class="screen-parametres">
 
-  <div style="width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
-    <h2 style="margin:0; color:#1a2a3a; font-size:1.4rem;" data-i18n="parametres.titre">⚙ Paramètres</h2>
-    <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+  <div class="parametres-header">
+    <h2 class="parametres-h2" data-i18n="parametres.titre">⚙ Paramètres</h2>
+    <button class="btn btn-continuer" data-action="back_menu" data-i18n="common.retour_menu">← Retour au menu</button>
   </div>
 
   <!-- Assistant LLM -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card parametres-card">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="parametres.llm.titre">🤖 Assistant LLM</span>
     </div>
     <p class="outil-desc" data-i18n="parametres.llm.desc">Clé API utilisée en local pour les fonctionnalités s'appuyant sur un modèle de langage.</p>
 
-    <div style="display:flex; flex-direction:column; gap:12px;">
+    <div class="parametres-llm-fields">
       <div class="add-field">
         <label class="add-label" for="param-llm-provider" data-i18n="parametres.llm.provider">Fournisseur</label>
         <select id="param-llm-provider" class="add-input">
# ── Zone modifiée : ligne 1584 (25 ligne(s)) dans l'ancienne version → ligne 1584 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1584,25 +1584,25 @@
   </div>
 
   <!-- Synthèse vocale (TTS) -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card parametres-card">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="parametres.tts.titre">🔊 Synthèse vocale</span>
     </div>
 
-    <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
-      <input type="checkbox" id="param-tts-enabled" style="width:16px; height:16px; cursor:pointer; accent-color:#e94560;">
+    <div class="parametres-tts-toggle">
+      <input type="checkbox" id="param-tts-enabled" class="parametres-tts-checkbox">
       <label for="param-tts-enabled" data-i18n="parametres.tts.activer">Activer la synthèse vocale</label>
     </div>
 
     <label class="add-label" for="param-tts-rate" data-i18n="parametres.tts.debit">Débit (mots par minute)</label>
-    <div style="display:flex; align-items:center; gap:10px;">
-      <input type="range" id="param-tts-rate" min="80" max="300" value="150" step="10" style="width:200px; accent-color:#e94560;" oninput="document.getElementById('param-tts-rate-val').textContent = this.value">
+    <div class="parametres-tts-rate-row">
+      <input type="range" id="param-tts-rate" min="80" max="300" value="150" step="10" class="parametres-tts-rate" oninput="document.getElementById('param-tts-rate-val').textContent = this.value">
       <span id="param-tts-rate-val">150</span>
     </div>
   </div>
 
-  <div style="width:100%; max-width:860px; display:flex; gap:10px;">
-    <button class="btn btn-continuer" onclick="parametresSave()" data-i18n="parametres.enregistrer">💾 Enregistrer</button>
+  <div class="parametres-actions">
+    <button class="btn btn-continuer" data-action="parametres_save" data-i18n="parametres.enregistrer">💾 Enregistrer</button>
   </div>
 
 </div>
