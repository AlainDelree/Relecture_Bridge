eac2126

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit eac2126
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 18:34:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-opening-explorer-select vers data-action + CSS (issue #222)
    
    Remplace l'unique onclick="sendAction({type:'back_menu'})" du bouton retour
    par data-action="back_menu" (case déjà existant dans le listener délégué,
    issue #220), en réutilisant .btn-continuer pour son style (valeurs
    background/color/border identiques à l'inline).
    
    Remplace les 10 style= inline par des classes dédiées dans main.css :
    #screen-opening-explorer-select (conteneur), .expl-select-header,
    .expl-select-h2, .expl-select-card (x2), .expl-select-catalogue-list,
    .expl-select-lignes-list, .expl-select-vide (x2, display:none initial).
    Le display:none initial de .expl-select-vide est sans risque : app.js
    (explRenderCatalogue/explRenderMesLignes) écrit toujours directement
    vide.style.display = ... ? "none" : "block" sans jamais lire la valeur
    courante au préalable.
    
    Aucun sélecteur e2e ne cible ce bloc (grep exhaustif sur
    nicsoft/tests/e2e/*.py) — aucune correction de test nécessaire.
    
    Suite pytest complète (78 passed, 1 skipped) au vert après modification.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f8cfffc..d933723 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/css/main.css
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 153 (6 ligne(s)) dans l'ancienne version → ligne 153 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -153,6 +153,15 @@
       overflow-y: auto;
       width: 100%;
     }
+    #screen-opening-explorer-select {
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
# ── Zone modifiée : ligne 858 (6 ligne(s)) dans l'ancienne version → ligne 867 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -858,6 +867,14 @@
 .ouvertures-card { flex:1 1 280px; max-width:360px; }
 .ouvertures-chk-label { color:#1a2a3a; }
 
+/* ── Écran "Opening Explorer" — sélection ── */
+.expl-select-header { width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
+.expl-select-h2 { margin:0; color:#1a2a3a; font-size:1.4rem; }
+.expl-select-card { width:100%; max-width:860px; }
+.expl-select-catalogue-list { display:flex; flex-direction:column; gap:6px; margin-top:10px; }
+.expl-select-lignes-list { display:flex; flex-direction:column; gap:10px; margin-top:10px; }
+.expl-select-vide { display:none; color:#888; font-size:0.85rem; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 6431824..082223e 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1643 (29 ligne(s)) dans l'ancienne version → ligne 1643 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1643,29 +1643,29 @@
 </div>
 
 <!-- ── Écran Opening Explorer — sélecteur ── -->
-<div id="screen-opening-explorer-select" style="display:none; flex-direction:column; align-items:center; padding:24px; gap:20px; overflow-y:auto; width:100%;">
+<div id="screen-opening-explorer-select">
 
-  <div style="width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
-    <h2 style="margin:0; color:#1a2a3a; font-size:1.4rem;" data-i18n="opening_explorer.titre">♟ Opening Explorer</h2>
-    <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+  <div class="expl-select-header">
+    <h2 class="expl-select-h2" data-i18n="opening_explorer.titre">♟ Opening Explorer</h2>
+    <button class="btn btn-continuer" data-action="back_menu" data-i18n="common.retour_menu">← Retour au menu</button>
   </div>
 
   <!-- Catalogue -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card expl-select-card">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="opening_explorer.catalogue.titre">📚 Catalogue</span>
     </div>
-    <div id="expl-catalogue-list" style="display:flex; flex-direction:column; gap:6px; margin-top:10px;"></div>
-    <div id="expl-catalogue-vide" style="display:none; color:#888; font-size:0.85rem;" data-i18n="opening_explorer.catalogue.vide">Aucune ouverture dans le catalogue.</div>
+    <div id="expl-catalogue-list" class="expl-select-catalogue-list"></div>
+    <div id="expl-catalogue-vide" class="expl-select-vide" data-i18n="opening_explorer.catalogue.vide">Aucune ouverture dans le catalogue.</div>
   </div>
 
   <!-- Mes ouvertures -->
-  <div class="outil-card" style="width:100%; max-width:860px;">
+  <div class="outil-card expl-select-card">
     <div class="outil-card-header">
       <span class="outil-title" data-i18n="opening_explorer.mes_ouvertures.titre">★ Mes ouvertures</span>
     </div>
-    <div id="expl-mes-lignes-list" style="display:flex; flex-direction:column; gap:10px; margin-top:10px;"></div>
-    <div id="expl-mes-lignes-vide" style="display:none; color:#888; font-size:0.85rem;" data-i18n="opening_explorer.mes_ouvertures.vide">Aucune ligne personnelle importée. Utilisez Outils Exercices pour en ajouter.</div>
+    <div id="expl-mes-lignes-list" class="expl-select-lignes-list"></div>
+    <div id="expl-mes-lignes-vide" class="expl-select-vide" data-i18n="opening_explorer.mes_ouvertures.vide">Aucune ligne personnelle importée. Utilisez Outils Exercices pour en ajouter.</div>
   </div>
 
 </div>
