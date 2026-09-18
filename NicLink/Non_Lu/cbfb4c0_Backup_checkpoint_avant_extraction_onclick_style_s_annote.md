cbfb4c0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit cbfb4c0
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 18:03:41 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Backup checkpoint avant extraction onclick/style screen-ouvertures (issue #221)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/tests/e2e/test_smoke_e2e.py b/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6c1051a..cc795f0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/tests/e2e/test_smoke_e2e.py
# ── Zone modifiée : ligne 125 (12 ligne(s)) dans l'ancienne version → ligne 125 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -125,12 +125,13 @@ def go_exercices(page):
     """Menu → Ouvertures → carte Exercices (chemin en 2 étapes depuis issue #141).
 
     Sélecteurs indépendants de la locale (issue #212, même approche que #208) :
-    #wrap-ouvertures button est un id unique, et le fragment d'attribut
-    onclick*="'exercices'" ne dépend pas du texte affiché à l'écran.
+    #wrap-ouvertures button est un id unique, et l'attribut data-mode="exercices"
+    ne dépend pas du texte affiché à l'écran (issue #221 : bascule de l'ancien
+    onclick*="'exercices'" vers le mécanisme data-action).
     """
     page.locator("#wrap-ouvertures button").click()
     page.wait_for_selector("#screen-ouvertures", state="visible", timeout=5000)
-    page.locator(".outil-card-clickable[onclick*=\"'exercices'\"]").click()
+    page.locator(".outil-card-clickable[data-mode=\"exercices\"]").click()
     page.wait_for_selector("#screen-exercices", state="visible", timeout=5000)
 
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index b3bb59e..8ab2b93 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 56 (6 ligne(s)) dans l'ancienne version → ligne 56 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -56,6 +56,11 @@ function toggleAutoUpdate() {
 // qu'un onclick="...". Modèle à réutiliser tel quel pour les écrans suivants
 // (issue #220) : ajouter simplement un nouveau `case` ci-dessous.
 document.addEventListener("click", (e) => {
+  // Le clic sur le label/checkbox "Mode virtuel" d'une carte ne doit jamais
+  // déclencher l'action de la carte parente (menu_card_launch) — on sort
+  // avant de chercher un data-action plutôt que d'utiliser
+  // event.stopPropagation() sur chaque label (issue #221).
+  if (e.target.closest(".menu-card-chk-label")) return;
   const el = e.target.closest("[data-action]");
   if (!el) return;
   switch (el.dataset.action) {
# ── Zone modifiée : ligne 68 (6 ligne(s)) dans l'ancienne version → ligne 73 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -68,6 +73,9 @@ document.addEventListener("click", (e) => {
     case "send_mode":
       sendAction({ type: "mode", value: el.dataset.mode });
       break;
+    case "back_menu":
+      sendAction({ type: "back_menu" });
+      break;
     case "quit_modal":
       ouvrirModal("quit", t("modal.quitter_alchess"), t("modal.quitter_btn"), "btn-warning");
       break;
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index e4d50c0..f8cfffc 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 144 (6 ligne(s)) dans l'ancienne version → ligne 144 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -144,6 +144,15 @@
       justify-content: flex-start;
       overflow-y: auto;
     }
+    #screen-ouvertures {
+      display: none;
+      flex-direction: column;
+      align-items: center;
+      padding: 40px 20px;
+      gap: 24px;
+      overflow-y: auto;
+      width: 100%;
+    }
     /* Grille unifiée pour tous les écrans avec échiquier */
     .screen-board-layout {
       display: none;
# ── Zone modifiée : ligne 842 (6 ligne(s)) dans l'ancienne version → ligne 851 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -842,6 +851,13 @@
 .outil-title { font-weight:700; font-size:1.05rem; color:#1a2a3a; }
 .outil-desc { color:#3a5a7a; font-size:0.88rem; margin-bottom:10px; }
 
+/* ── Écran intermédiaire "Ouvertures" ── */
+.ouvertures-header { width:100%; max-width:760px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
+.ouvertures-h2 { margin:0; color:#1a2a3a; font-size:1.4rem; }
+.ouvertures-cards { width:100%; max-width:760px; display:flex; gap:20px; flex-wrap:wrap; justify-content:center; }
+.ouvertures-card { flex:1 1 280px; max-width:360px; }
+.ouvertures-chk-label { color:#1a2a3a; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 19704b1..6431824 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1609 (29 ligne(s)) dans l'ancienne version → ligne 1609 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1609,29 +1609,29 @@
 
 
 <!-- ── Écran intermédiaire "Ouvertures" ── -->
-<div id="screen-ouvertures" style="display:none; flex-direction:column; align-items:center; padding:40px 20px; gap:24px; overflow-y:auto; width:100%;">
+<div id="screen-ouvertures">
 
-  <div style="width:100%; max-width:760px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
-    <h2 style="margin:0; color:#1a2a3a; font-size:1.4rem;" data-i18n="ouvertures.titre">📖 Ouvertures</h2>
-    <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+  <div class="ouvertures-header">
+    <h2 class="ouvertures-h2" data-i18n="ouvertures.titre">📖 Ouvertures</h2>
+    <button class="btn btn-continuer" data-action="back_menu" data-i18n="common.retour_menu">← Retour au menu</button>
   </div>
 
-  <div style="width:100%; max-width:760px; display:flex; gap:20px; flex-wrap:wrap; justify-content:center;">
+  <div class="ouvertures-cards">
 
     <!-- Carte Exercices -->
-    <div class="outil-card outil-card-clickable" style="flex:1 1 280px; max-width:360px;" onclick="_menuCardLaunch('exercices', this)">
+    <div class="outil-card outil-card-clickable ouvertures-card" data-action="menu_card_launch" data-mode="exercices">
       <div class="outil-card-header">
         <span class="outil-title" data-i18n="ouvertures.carte_exercices.titre">📚 Exercices</span>
       </div>
       <p class="outil-desc" data-i18n="ouvertures.carte_exercices.desc">Entraînez-vous aux ouvertures sur l'échiquier physique — le livre répond et corrige vos coups.</p>
-      <label class="menu-card-chk-label" style="color:#1a2a3a;" onclick="event.stopPropagation()">
+      <label class="menu-card-chk-label ouvertures-chk-label">
         <input type="checkbox" class="menu-card-chk" checked>
         <span data-i18n="menu.mode_virtuel_label">Mode virtuel</span>
       </label>
     </div>
 
     <!-- Carte Opening Explorer -->
-    <div class="outil-card outil-card-clickable" style="flex:1 1 280px; max-width:360px;" onclick="sendAction({type:'mode', value:'opening_explorer'})">
+    <div class="outil-card outil-card-clickable ouvertures-card" data-action="send_mode" data-mode="opening_explorer">
       <div class="outil-card-header">
         <span class="outil-title" data-i18n="ouvertures.carte_explorer.titre">♟ Opening Explorer</span>
       </div>
