1d9db0b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1d9db0b
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 21:10:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait onclick/style inline de #screen-labo vers data-action + CSS — accordéon Moteur (issue #238 partie 2/4)
    
    - laboToggleSection('labo-sec-moteur') -> case data-action="labo_toggle_section" paramétré
      par data-section (réutilisable tel quel par les parties 3/4 et 4/4 pour les accordéons
      Config moteur et Position virtuelle)
    - sendAction({type:'best_move'}) -> case data-action="labo_best_move"
    - laboSetAuto(true)/laboSetAuto(false) -> case unique data-action="labo_set_auto"
      paramétré par data-auto="true"/"false" (2 boutons consolidés en 1 case)
    - sendAction({type:'undo_labo'}) -> case data-action="labo_undo"
    - laboReset() -> case data-action="labo_reset"
    - 12 style inline -> classes CSS (.labo-acc-card/-header/-title/-arrow/-body,
      .labo-engine-label, .labo-auto-group/-btn/-btn-play/-btn-stop,
      .labo-btn-undo/-reset ; réutilise .labo-btn-mb0 existant pour margin-bottom:0)
    
    Suite pytest complète (78 passed, 1 skipped, dont les 42 e2e) au vert.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 94d0929..c1d74aa 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 187 (6 ligne(s)) dans l'ancienne version → ligne 187 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -187,6 +187,21 @@ document.addEventListener("click", (e) => {
     case "labo_sync_physique":
       laboSyncPhysique();
       break;
+    case "labo_toggle_section":
+      laboToggleSection(el.dataset.section);
+      break;
+    case "labo_best_move":
+      sendAction({ type: "best_move" });
+      break;
+    case "labo_set_auto":
+      laboSetAuto(el.dataset.auto === "true");
+      break;
+    case "labo_undo":
+      sendAction({ type: "undo_labo" });
+      break;
+    case "labo_reset":
+      laboReset();
+      break;
   }
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index 2429ca7..6b260ef 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 842 (6 ligne(s)) dans l'ancienne version → ligne 842 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -842,6 +842,18 @@
     .labo-last-move { margin-top: 6px; font-size: 1rem; font-weight: bold; color: #3a5a7a; min-height: 1.2rem; text-align: center; }
     .labo-feedback-side { margin-top: 4px; padding: 4px 8px; border-radius: 4px; font-size: 0.82rem; display: none; }
     .labo-btn-mb0 { margin-bottom: 0; }
+    .labo-acc-card { padding: 0; }
+    .labo-acc-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; cursor: pointer; }
+    .labo-acc-title { margin-bottom: 0; }
+    .labo-acc-arrow { color: #3a5a7a; font-size: 0.8rem; }
+    .labo-acc-body { padding: 0 14px 12px; display: flex; flex-direction: column; gap: 7px; }
+    .labo-engine-label { font-size: 0.78rem; color: #3a5a7a; margin-bottom: 2px; }
+    .labo-auto-group { display: flex; border-radius: 6px; overflow: hidden; border: 1px solid #444; }
+    .labo-auto-btn { flex: 1; border: none; padding: 7px 0; font-size: 1.1rem; cursor: pointer; }
+    .labo-auto-btn-play { border-right: 1px solid #444; background: #2a2a2a; color: #555; }
+    .labo-auto-btn-stop { background: #7b1a1a; color: #fff; }
+    .labo-btn-undo { background: #9ab8d8; color: #1a2a3a; border: 1px solid #2a5a8a; }
+    .labo-btn-reset { background: #c2d4e8; color: #1a2a3a; border: 1px solid #a0b8d0; }
 
     .coord-rank {
       display: flex;
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 00aa90d..c242636 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1041 (23 ligne(s)) dans l'ancienne version → ligne 1041 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1041,23 +1041,20 @@
       data-action="labo_sync_physique" data-i18n="labo.btn.source_physique">🔄 Source physique → Virtuel</button>
 
     <!-- ── Moteur (ouvert par défaut) ── -->
-    <div class="card" style="padding:0;">
-      <div onclick="laboToggleSection('labo-sec-moteur')"
-        style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; cursor:pointer;">
-        <h2 style="margin-bottom:0;" data-i18n="labo.h2.moteur">MOTEUR</h2>
-        <span id="labo-sec-moteur-arrow" style="color:#3a5a7a; font-size:0.8rem;">▲</span>
-      </div>
-      <div id="labo-sec-moteur" style="padding:0 14px 12px; display:flex; flex-direction:column; gap:7px;">
-        <div id="labo-engine-label" style="font-size:0.78rem; color:#3a5a7a; margin-bottom:2px;"></div>
-        <button class="btn btn-best" id="labo-btn-best" style="margin-bottom:0;" onclick="sendAction({type:'best_move'})" data-i18n="labo.btn.meilleur">💡 Meilleur coup</button>
-        <div style="display:flex; border-radius:6px; overflow:hidden; border:1px solid #444;">
-          <button id="labo-btn-auto-play" onclick="laboSetAuto(true)"
-            style="flex:1; border:none; border-right:1px solid #444; padding:7px 0; font-size:1.1rem; cursor:pointer; background:#2a2a2a; color:#555;">▶</button>
-          <button id="labo-btn-auto-stop" onclick="laboSetAuto(false)"
-            style="flex:1; border:none; padding:7px 0; font-size:1.1rem; cursor:pointer; background:#7b1a1a; color:#fff;">■</button>
+    <div class="card labo-acc-card">
+      <div class="labo-acc-header" data-action="labo_toggle_section" data-section="labo-sec-moteur">
+        <h2 class="labo-acc-title" data-i18n="labo.h2.moteur">MOTEUR</h2>
+        <span id="labo-sec-moteur-arrow" class="labo-acc-arrow">▲</span>
+      </div>
+      <div id="labo-sec-moteur" class="labo-acc-body">
+        <div id="labo-engine-label" class="labo-engine-label"></div>
+        <button class="btn btn-best labo-btn-mb0" id="labo-btn-best" data-action="labo_best_move" data-i18n="labo.btn.meilleur">💡 Meilleur coup</button>
+        <div class="labo-auto-group">
+          <button id="labo-btn-auto-play" class="labo-auto-btn labo-auto-btn-play" data-action="labo_set_auto" data-auto="true">▶</button>
+          <button id="labo-btn-auto-stop" class="labo-auto-btn labo-auto-btn-stop" data-action="labo_set_auto" data-auto="false">■</button>
         </div>
-        <button class="btn" id="labo-btn-undo" style="margin-bottom:0; background:#9ab8d8; color:#1a2a3a; border:1px solid #2a5a8a;" onclick="sendAction({type:'undo_labo'})" disabled data-i18n="labo.btn.annuler">↩ Annuler coup</button>
-        <button class="btn" style="margin-bottom:0; background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="laboReset()" data-i18n="labo.btn.reinit">🔄 Réinitialiser</button>
+        <button class="btn labo-btn-mb0 labo-btn-undo" id="labo-btn-undo" data-action="labo_undo" disabled data-i18n="labo.btn.annuler">↩ Annuler coup</button>
+        <button class="btn labo-btn-mb0 labo-btn-reset" data-action="labo_reset" data-i18n="labo.btn.reinit">🔄 Réinitialiser</button>
 
       </div>
     </div>
