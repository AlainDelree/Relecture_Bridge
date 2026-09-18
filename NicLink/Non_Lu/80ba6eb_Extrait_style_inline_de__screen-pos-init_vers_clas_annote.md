80ba6eb

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 80ba6eb
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 18:54:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait style inline de #screen-pos-init vers classes CSS (issue #225)
    
    Supprime le style="display:none;" redondant sur le conteneur
    #screen-pos-init (déjà géré par .screen-board-layout en CSS,
    main.css ligne 166).
    
    Remplace les 7 autres style= inline par des classes dédiées dans
    main.css (.pos-init-board-col, .pos-init-label, .pos-init-panel,
    .pos-init-texte, .pos-init-attente, .pos-init-spinner), en réutilisant
    @keyframes spin déjà existant pour l'animation du spinner "En
    attente…" (dimensions propres à cet écran : 14px/bordure 2px, pas
    .spinner-ring qui est en 60px/bordure 5px).
    
    Aucun sélecteur e2e ne cible ce bloc (grep exhaustif sur
    nicsoft/tests/e2e/*.py) — aucune correction de test nécessaire.
    
    Suite pytest complète (78 passed, 1 skipped, e2e inclus) au vert
    après modification.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d933723..0628575 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/css/main.css
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 875 (6 ligne(s)) dans l'ancienne version → ligne 875 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -875,6 +875,14 @@
 .expl-select-lignes-list { display:flex; flex-direction:column; gap:10px; margin-top:10px; }
 .expl-select-vide { display:none; color:#888; font-size:0.85rem; }
 
+/* ── Écran position initiale ── */
+.pos-init-board-col { display:flex; flex-direction:column; align-items:center; gap:0; }
+.pos-init-label { display:flex; align-items:center; gap:8px; padding:4px 0; font-size:1em; font-weight:bold; color:#1a2a3a; }
+.pos-init-panel { display:flex; flex-direction:column; gap:16px; }
+.pos-init-texte { color:#1a2a3a; font-size:0.9rem; line-height:1.7; margin-bottom:16px; }
+.pos-init-attente { display:flex; align-items:center; gap:10px; color:#2a3a4a; font-size:0.85rem; }
+.pos-init-spinner { width:14px; height:14px; border:2px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite; flex-shrink:0; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 082223e..2f20b33 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 830 (30 ligne(s)) dans l'ancienne version → ligne 830 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -830,30 +830,30 @@
   </div>
 </div>
 <!-- ── Écran position initiale ── -->
-<div id="screen-pos-init" class="screen-board-layout" style="display:none;">
+<div id="screen-pos-init" class="screen-board-layout">
   <!-- Colonne gauche vide -->
   <div></div>
   <!-- Échiquier centré -->
-  <div id="board-container-pos" style="display:flex; flex-direction:column; align-items:center; gap:0;">
-    <div style="display:flex; align-items:center; gap:8px; padding:4px 0; font-size:1em; font-weight:bold; color:#1a2a3a;">
+  <div id="board-container-pos" class="pos-init-board-col">
+    <div class="pos-init-label">
       <span>♟</span><span data-i18n="pos_init.adversaire">Adversaire</span>
     </div>
     <div id="board-pos-init"></div>
-    <div style="display:flex; align-items:center; gap:8px; padding:4px 0; font-size:1em; font-weight:bold; color:#1a2a3a;">
+    <div class="pos-init-label">
       <span>♙</span><span data-i18n="pos_init.joueur">Joueur</span>
     </div>
   </div>
   <!-- Panel droit contextuel -->
-  <div style="display:flex; flex-direction:column; gap:16px;">
+  <div class="pos-init-panel">
     <div class="card">
       <h2 class="card-title-lg" data-i18n="pos_init.titre">Position incorrecte</h2>
-      <div style="color:#1a2a3a; font-size:0.9rem; line-height:1.7; margin-bottom:16px;" data-i18n-html="pos_init.texte_html">
+      <div class="pos-init-texte" data-i18n-html="pos_init.texte_html">
         Le plateau n'est pas en position initiale.<br>
         Rangez toutes les pièces à leur place de départ.<br><br>
         La partie démarrera automatiquement dès que la position sera correcte.
       </div>
-      <div style="display:flex; align-items:center; gap:10px; color:#2a3a4a; font-size:0.85rem;">
-        <div style="width:14px; height:14px; border:2px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite; flex-shrink:0;"></div>
+      <div class="pos-init-attente">
+        <div class="pos-init-spinner"></div>
         <span data-i18n="pos_init.attente">En attente…</span>
       </div>
     </div>
