e47c4ad

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e47c4ad
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 19:48:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-retranscription vers data-action + CSS (issue #230)
    
    Remplace les 10 onclick= : retransResume(false)/(true) consolidés en un
    case "retrans_resume" paramétré par data-resume="false"/"true"
    (comparaison === "true" pour le booléen). retransSelectTab('partie'/
    'exercice') consolidés en case "retrans_select_tab" via data-tab, sur le
    même modèle que ex_select_tab (#228). retransSetCamp('white'/'black')
    consolidés en case "retrans_set_camp" via data-camp. Les 2 boutons
    "← Retour" (formulaires Partie et Exercice) rejoignent le case
    "back_menu" déjà existant. Les 2 boutons "▶ Démarrer la partie"
    rejoignent un unique nouveau case "start_retranscription" →
    startRetranscription() inchangée. Toutes les fonctions JS appelées
    restent inchangées ; seul le déclenchement passe par le switch délégué
    d'app.js.
    
    Remplace les 20 style= inline par des classes dans main.css
    (.retrans-resume-banner/-title/-info/-actions/-btn, .retrans-tabs,
    .retrans-tab-btn + -active-init/-inactive-init, .retrans-form-card
    (+ -hidden-init pour le formulaire Exercice), .retrans-form-actions,
    .retrans-btn-flex1/-flex2, .retrans-camp-row, .retrans-camp-btn +
    -white-init/-black-init), valeurs strictement identiques à l'inline
    d'origine. Les bascules dynamiques de couleur (retransSelectTab et
    retransSetCamp modifiant .style.background/.color au clic) restent en
    JS, inchangées — seul l'état initial migre vers les classes *-init,
    même pattern que #228/#229.
    
    Aucun sélecteur e2e ne cible un onclick/style de ce bloc (grep exhaustif
    sur nicsoft/tests/e2e/*.py) — seule la visibilité de
    #screen-retranscription par id est vérifiée, non affectée par ce
    changement.
    
    Suite pytest complète (78 passed, 1 skipped, e2e inclus) au vert après
    modification.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 60016bf..12a2ff9 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 109 (6 ligne(s)) dans l'ancienne version → ligne 109 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -109,6 +109,18 @@ document.addEventListener("click", (e) => {
     case "quit_modal":
       ouvrirModal("quit", t("modal.quitter_alchess"), t("modal.quitter_btn"), "btn-warning");
       break;
+    case "retrans_resume":
+      retransResume(el.dataset.resume === "true");
+      break;
+    case "retrans_select_tab":
+      retransSelectTab(el.dataset.tab);
+      break;
+    case "retrans_set_camp":
+      retransSetCamp(el.dataset.camp);
+      break;
+    case "start_retranscription":
+      startRetranscription();
+      break;
   }
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index f673bc0..9a84e84 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 1005 (6 ligne(s)) dans l'ancienne version → ligne 1005 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1005,6 +1005,26 @@
 .exr-btn-sync { margin-bottom:0; background:#a0b8d0; border:1px solid #4caf50; color:#4caf50; }
 .exr-btn-continuer { margin-bottom:0; display:none; background:#2e7d32; color:#fff; }
 
+/* ── Écran "Retranscription" (issue #230) ── */
+.retrans-resume-banner { display:none; background:#1a3a1a; border:1px solid #4caf50; border-radius:8px; padding:12px 16px; margin-bottom:16px; width:380px; text-align:center; }
+.retrans-resume-title { color:#4caf50; font-weight:bold; margin-bottom:6px; }
+.retrans-resume-info { color:#445; font-size:0.85rem; margin-bottom:10px; }
+.retrans-resume-actions { display:flex; gap:8px; }
+.retrans-resume-btn { flex:1; padding:6px; }
+.retrans-tabs { display:flex; gap:0; border-radius:8px; overflow:hidden; border:1px solid #a0b8d0; margin-bottom:16px; width:380px; }
+.retrans-tab-btn { flex:1; padding:10px; font-size:0.9rem; font-weight:bold; cursor:pointer; border:none; transition:0.15s; }
+.retrans-tab-btn-active-init { background:#e94560; color:white; }
+.retrans-tab-btn-inactive-init { background:#c2d4e8; color:#3a5a7a; }
+.retrans-form-card { width:380px; }
+.retrans-form-card-hidden-init { display:none; }
+.retrans-form-actions { display:flex; gap:8px; margin-top:8px; }
+.retrans-btn-flex1 { flex:1; }
+.retrans-btn-flex2 { flex:2; }
+.retrans-camp-row { display:flex; gap:8px; margin-bottom:16px; }
+.retrans-camp-btn { flex:1; padding:8px; }
+.retrans-camp-btn-white-init { background:#e8c840; border:1px solid #e8c840; color:#d8e4f0; font-weight:bold; }
+.retrans-camp-btn-black-init { background:#c2d4e8; border:1px solid #a0b8d0; color:#3a5a7a; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index c2b3404..1de4bfd 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 424 (29 ligne(s)) dans l'ancienne version → ligne 424 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -424,29 +424,27 @@
   <div class="config-title" data-i18n="retrans.titre">📝 Retranscrire</div>
 
   <!-- Bandeau session en cours -->
-  <div id="retrans-resume-banner" style="display:none; background:#1a3a1a; border:1px solid #4caf50; border-radius:8px; padding:12px 16px; margin-bottom:16px; width:380px; text-align:center;">
-    <div style="color:#4caf50; font-weight:bold; margin-bottom:6px;" data-i18n="retrans.session_en_cours">♻ Session en cours</div>
-    <div id="retrans-resume-info" style="color:#445; font-size:0.85rem; margin-bottom:10px;"></div>
-    <div style="display:flex; gap:8px;">
-      <button class="btn btn-continuer" onclick="retransResume(false)" style="flex:1; padding:6px;" data-i18n="retrans.btn.nouvelle">Nouvelle</button>
-      <button class="btn btn-reprendre" onclick="retransResume(true)" style="flex:1; padding:6px;" data-i18n="retrans.btn.reprendre_session">↩ Reprendre</button>
+  <div id="retrans-resume-banner" class="retrans-resume-banner">
+    <div class="retrans-resume-title" data-i18n="retrans.session_en_cours">♻ Session en cours</div>
+    <div id="retrans-resume-info" class="retrans-resume-info"></div>
+    <div class="retrans-resume-actions">
+      <button class="btn btn-continuer retrans-resume-btn" data-action="retrans_resume" data-resume="false" data-i18n="retrans.btn.nouvelle">Nouvelle</button>
+      <button class="btn btn-reprendre retrans-resume-btn" data-action="retrans_resume" data-resume="true" data-i18n="retrans.btn.reprendre_session">↩ Reprendre</button>
     </div>
   </div>
 
   <!-- Onglets -->
-  <div style="display:flex; gap:0; border-radius:8px; overflow:hidden; border:1px solid #a0b8d0; margin-bottom:16px; width:380px;">
-    <button id="retrans-tab-partie" onclick="retransSelectTab('partie')" data-i18n="retrans.tab.partie"
-      style="flex:1; padding:10px; font-size:0.9rem; font-weight:bold; cursor:pointer; border:none; background:#e94560; color:white; transition:0.15s;">
+  <div class="retrans-tabs">
+    <button id="retrans-tab-partie" class="retrans-tab-btn retrans-tab-btn-active-init" data-action="retrans_select_tab" data-tab="partie" data-i18n="retrans.tab.partie">
       🏆 Partie
     </button>
-    <button id="retrans-tab-exercice" onclick="retransSelectTab('exercice')" data-i18n="retrans.tab.exercice"
-      style="flex:1; padding:10px; font-size:0.9rem; font-weight:bold; cursor:pointer; border:none; background:#c2d4e8; color:#3a5a7a; transition:0.15s;">
+    <button id="retrans-tab-exercice" class="retrans-tab-btn retrans-tab-btn-inactive-init" data-action="retrans_select_tab" data-tab="exercice" data-i18n="retrans.tab.exercice">
       📖 Exercice
     </button>
   </div>
 
   <!-- Formulaire Partie -->
-  <div id="retrans-form-partie" class="card" style="width:380px;">
+  <div id="retrans-form-partie" class="card retrans-form-card">
     <label class="cfg-label" data-i18n="retrans.label.blancs">Blancs</label>
     <input id="retrans-white" class="cfg-input" type="text" data-i18n-placeholder="retrans.placeholder.blancs" placeholder="Nom du joueur Blancs">
 
# ── Zone modifiée : ligne 459 (28 ligne(s)) dans l'ancienne version → ligne 457 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -459,28 +457,26 @@
     <label class="cfg-label" data-i18n="retrans.label.evenement">Événement</label>
     <input id="retrans-event" class="cfg-input" type="text" data-i18n-placeholder="retrans.placeholder.evenement" placeholder="Tournoi, club...">
 
-    <div style="display:flex; gap:8px; margin-top:8px;">
-      <button class="btn btn-continuer" onclick="sendAction({type:'back_menu'})" style="flex:1;" data-i18n="common.retour">← Retour</button>
-      <button class="btn btn-reprendre" onclick="startRetranscription()" style="flex:2;" data-i18n="common.demarrer">▶ Démarrer la partie</button>
+    <div class="retrans-form-actions">
+      <button class="btn btn-continuer retrans-btn-flex1" data-action="back_menu" data-i18n="common.retour">← Retour</button>
+      <button class="btn btn-reprendre retrans-btn-flex2" data-action="start_retranscription" data-i18n="common.demarrer">▶ Démarrer la partie</button>
     </div>
   </div>
 
   <!-- Formulaire Exercice -->
-  <div id="retrans-form-exercice" class="card" style="width:380px; display:none;">
+  <div id="retrans-form-exercice" class="card retrans-form-card retrans-form-card-hidden-init">
     <label class="cfg-label" data-i18n="retrans.label.nom_ligne">Nom de la ligne</label>
     <input id="retrans-nom" class="cfg-input" type="text" data-i18n-placeholder="retrans.placeholder.nom_ligne" placeholder="ex: Chigorine, Ruy Lopez...">
 
     <label class="cfg-label" data-i18n="retrans.label.camp">Camp suggéré</label>
-    <div style="display:flex; gap:8px; margin-bottom:16px;">
-      <button id="retrans-camp-white" class="btn" onclick="retransSetCamp('white')" data-i18n="config.color.blancs"
-        style="flex:1; padding:8px; background:#e8c840; border:1px solid #e8c840; color:#d8e4f0; font-weight:bold;">♔ Blancs</button>
-      <button id="retrans-camp-black" class="btn" onclick="retransSetCamp('black')" data-i18n="config.color.noirs"
-        style="flex:1; padding:8px; background:#c2d4e8; border:1px solid #a0b8d0; color:#3a5a7a;">♚ Noirs</button>
+    <div class="retrans-camp-row">
+      <button id="retrans-camp-white" class="btn retrans-camp-btn retrans-camp-btn-white-init" data-action="retrans_set_camp" data-camp="white" data-i18n="config.color.blancs">♔ Blancs</button>
+      <button id="retrans-camp-black" class="btn retrans-camp-btn retrans-camp-btn-black-init" data-action="retrans_set_camp" data-camp="black" data-i18n="config.color.noirs">♚ Noirs</button>
     </div>
 
-    <div style="display:flex; gap:8px; margin-top:8px;">
-      <button class="btn btn-continuer" onclick="sendAction({type:'back_menu'})" style="flex:1;" data-i18n="common.retour">← Retour</button>
-      <button class="btn btn-reprendre" onclick="startRetranscription()" style="flex:2;" data-i18n="common.demarrer">▶ Démarrer la partie</button>
+    <div class="retrans-form-actions">
+      <button class="btn btn-continuer retrans-btn-flex1" data-action="back_menu" data-i18n="common.retour">← Retour</button>
+      <button class="btn btn-reprendre retrans-btn-flex2" data-action="start_retranscription" data-i18n="common.demarrer">▶ Démarrer la partie</button>
     </div>
   </div>
 </div>
