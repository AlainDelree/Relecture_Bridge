e53d2ec

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e53d2ec
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 13:29:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    UX: carte Rodent cliquable = bouton de téléchargement quand indisponible sur Windows (issue #190)
    
    - La carte Rodent (cfg-engine-rodent / labo-eng-rodent) devient elle-même
      le déclencheur du téléchargement quand downloadable=true et available=false :
      icône ⬇ à la place de 🐭, style .engine-downloadable (cliquable, pas grisé),
      onclick délégué à rodentCardClick() qui bascule entre selectEngine/
      laboSelectEngine et downloadRodent() selon l'état.
    - Le div *-rodent-unavailable (message + ancien bouton séparé) est masqué
      dans ce cas ; il reste affiché tel quel si Rodent est indisponible et non
      téléchargeable (Linux, comportement inchangé).
    - Le span *-rodent-download-status est sorti du div unavailable pour rester
      visible sous la carte pendant le téléchargement, même si celle-ci est masquée.
    - Ajout d'un flag _rodentDownloadInProgress + classe .engine-downloading pour
      éviter un second déclenchement pendant un téléchargement en cours.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0646bcc..ea802d8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 494 (6 ligne(s)) dans l'ancienne version → ligne 494 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -494,6 +494,9 @@ let _rodentAvailable = true;
 // true si le serveur tourne sous Windows — seul cas où le téléchargement
 // des binaires Rodent IV depuis GitHub est proposé (issue #131).
 let _rodentDownloadable = false;
+// true pendant un téléchargement Rodent IV en cours (issue #190) — évite un second
+// déclenchement si l'utilisateur reclique sur la carte pendant le téléchargement.
+let _rodentDownloadInProgress = false;
 
 // Grise les boutons Stockfish (config péda + labo) et affiche le message
 // d'indisponibilité si absent. Ré-appelé au changement de langue.
# ── Zone modifiée : ligne 536 (28 ligne(s)) dans l'ancienne version → ligne 539 (47 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -536,28 +539,47 @@ function _applyMaiaAvailability() {
 // de langue via _refreshDynamicLabels() pour retraduire le tooltip.
 function _applyRodentAvailability() {
   const msg = t("engine.rodent.unavailable");
-  [["cfg-engine-rodent", "cfg-rodent-unavailable", "cfg-rodent-download-btn"],
-   ["labo-eng-rodent",   "labo-rodent-unavailable", "labo-rodent-download-btn"]].forEach(([btnId, msgId, dlBtnId]) => {
+  const downloadHint = t("engine.rodent.download");
+  const downloadState = _rodentDownloadable && !_rodentAvailable;
+  [["cfg-engine-rodent", "cfg-rodent-unavailable", "cfg-rodent-icon"],
+   ["labo-eng-rodent",   "labo-rodent-unavailable", "labo-rodent-icon"]].forEach(([btnId, msgId, iconId]) => {
     const btn = document.getElementById(btnId);
     const box = document.getElementById(msgId);
-    const dlBtn = document.getElementById(dlBtnId);
+    const icon = document.getElementById(iconId);
     if (btn) {
-      btn.classList.toggle("engine-unavailable", !_rodentAvailable);
-      if (_rodentAvailable) btn.removeAttribute("title");
-      else                  btn.setAttribute("title", msg);
+      btn.classList.toggle("engine-unavailable", !_rodentAvailable && !downloadState);
+      btn.classList.toggle("engine-downloadable", downloadState);
+      if (_rodentAvailable)   btn.removeAttribute("title");
+      else if (downloadState) btn.setAttribute("title", downloadHint);
+      else                    btn.setAttribute("title", msg);
     }
-    if (box) box.style.display = _rodentAvailable ? "none" : "";
-    if (dlBtn) dlBtn.style.display = (_rodentDownloadable && !_rodentAvailable) ? "" : "none";
+    if (icon) icon.textContent = downloadState ? "⬇" : "🐭";
+    if (box) box.style.display = (!_rodentAvailable && !downloadState) ? "" : "none";
   });
   _checkNoEngineAvailable();
 }
 
+// Point d'entrée onclick des cartes Rodent (config péda + labo) : bascule entre
+// sélection normale du moteur et déclenchement du téléchargement selon l'état
+// courant (issue #190 — la carte elle-même devient le bouton de téléchargement).
+function rodentCardClick(context) {
+  if (_rodentDownloadable && !_rodentAvailable) {
+    downloadRodent();
+    return;
+  }
+  if (context === "labo") laboSelectEngine("rodent");
+  else                     selectEngine("rodent");
+}
+
 // Télécharge les binaires Rodent IV depuis GitHub (Windows uniquement, issue #131).
-// Déclenché par les boutons cfg-rodent-download-btn / labo-rodent-download-btn.
+// Déclenché par un clic sur la carte cfg-engine-rodent / labo-eng-rodent quand
+// Rodent est indisponible mais téléchargeable (issue #190).
 function downloadRodent() {
-  ["cfg-rodent-download-btn", "labo-rodent-download-btn"].forEach(id => {
+  if (_rodentDownloadInProgress) return;
+  _rodentDownloadInProgress = true;
+  ["cfg-engine-rodent", "labo-eng-rodent"].forEach(id => {
     const btn = document.getElementById(id);
-    if (btn) btn.disabled = true;
+    if (btn) btn.classList.add("engine-downloading");
   });
   ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
     const status = document.getElementById(id);
# ── Zone modifiée : ligne 5987 (9 ligne(s)) dans l'ancienne version → ligne 6009 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5987,9 +6009,10 @@ socket.on("rodent_download_result", (data) => {
     const status = document.getElementById(id);
     if (status) status.textContent = msg;
   });
-  ["cfg-rodent-download-btn", "labo-rodent-download-btn"].forEach(id => {
+  _rodentDownloadInProgress = false;
+  ["cfg-engine-rodent", "labo-eng-rodent"].forEach(id => {
     const btn = document.getElementById(id);
-    if (btn) btn.disabled = false;
+    if (btn) btn.classList.remove("engine-downloading");
   });
 });
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index f8bd850..965ffe8 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 410 (6 ligne(s)) dans l'ancienne version → ligne 410 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -410,6 +410,18 @@
       cursor: not-allowed;
       filter: grayscale(1);
     }
+    /* Rodent absent mais téléchargeable (Windows) : carte cliquable = bouton de téléchargement */
+    .color-btn.engine-downloadable {
+      border-color: #3a5a7a;
+      background: #dce8f5;
+      color: #1a2a3a;
+    }
+    .color-btn.engine-downloadable:hover { background: #c2d9ee; }
+    .color-btn.engine-downloading {
+      opacity: 0.6;
+      cursor: wait;
+      pointer-events: none;
+    }
 
     /* ── Colonne gauche (Historique) ── */
     #left-panel {
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index df53c95..40b6bb4 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 251 (7 ligne(s)) dans l'ancienne version → ligne 251 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -251,7 +251,7 @@
           <div style="display:flex; gap:8px; margin-bottom:14px;">
             <button class="color-btn selected" id="cfg-engine-stockfish" onclick="selectEngine('stockfish')">⚡ Stockfish <span class="engine-tagline" data-i18n="config.tagline.stockfish">Best</span></button>
             <button class="color-btn"          id="cfg-engine-maia"      onclick="selectEngine('maia')">🧠 Maia Chess <span class="engine-tagline" data-i18n="config.tagline.maia">Human</span></button>
-            <button class="color-btn"          id="cfg-engine-rodent"    onclick="selectEngine('rodent')">🐭 Rodent <span class="engine-tagline" data-i18n="config.tagline.rodent">Weak</span></button>
+            <button class="color-btn"          id="cfg-engine-rodent"    onclick="rodentCardClick('cfg')"><span id="cfg-rodent-icon">🐭</span> Rodent <span class="engine-tagline" data-i18n="config.tagline.rodent">Weak</span></button>
           </div>
           <div id="cfg-stockfish-unavailable" style="display:none; font-size:0.78rem; color:#c0392b; margin:-8px 0 12px;"
                data-i18n="engine.stockfish.unavailable">Stockfish non installé sur ce système</div>
# ── Zone modifiée : ligne 259 (11 ligne(s)) dans l'ancienne version → ligne 259 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -259,11 +259,8 @@
                data-i18n="engine.maia.unavailable">Maia (lc0 + poids) non installé sur ce système</div>
           <div id="cfg-rodent-unavailable" style="display:none; font-size:0.78rem; color:#c0392b; margin:-8px 0 12px;">
             <span data-i18n="engine.rodent.unavailable">Moteur Rodent indisponible sur ce système</span>
-            <button id="cfg-rodent-download-btn" type="button" onclick="downloadRodent()"
-                    style="display:none; margin-left:8px; font-size:0.75rem; padding:2px 8px; cursor:pointer;"
-                    data-i18n="engine.rodent.download">Télécharger Rodent IV</button>
-            <span id="cfg-rodent-download-status" style="margin-left:6px; color:#3a5a7a;"></span>
           </div>
+          <span id="cfg-rodent-download-status" style="display:block; margin:-8px 0 12px; font-size:0.78rem; color:#3a5a7a;"></span>
           <div id="cfg-no-engine-alert" style="display:none; font-size:0.85rem; color:#c0392b; margin:8px 0; padding:8px; background:#ffe0e0; border-radius:4px; text-align:center;"
                data-i18n="engine.none.available">Aucun moteur d'échecs n'est disponible</div>
 
# ── Zone modifiée : ligne 1064 (7 ligne(s)) dans l'ancienne version → ligne 1061 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1064,7 +1061,7 @@
         <div style="display:flex; gap:6px;">
           <button class="color-btn selected" id="labo-eng-sf"     onclick="laboSelectEngine('stockfish')">⚡ Stockfish</button>
           <button class="color-btn"          id="labo-eng-maia"   onclick="laboSelectEngine('maia')">🧠 Maia</button>
-          <button class="color-btn"          id="labo-eng-rodent" onclick="laboSelectEngine('rodent')">🐭 Rodent</button>
+          <button class="color-btn"          id="labo-eng-rodent" onclick="rodentCardClick('labo')"><span id="labo-rodent-icon">🐭</span> Rodent</button>
         </div>
         <div id="labo-stockfish-unavailable" style="display:none; font-size:0.72rem; color:#c0392b;"
              data-i18n="engine.stockfish.unavailable">Stockfish non installé sur ce système</div>
# ── Zone modifiée : ligne 1072 (11 ligne(s)) dans l'ancienne version → ligne 1069 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1072,11 +1069,8 @@
              data-i18n="engine.maia.unavailable">Maia (lc0 + poids) non installé sur ce système</div>
         <div id="labo-rodent-unavailable" style="display:none; font-size:0.72rem; color:#c0392b;">
           <span data-i18n="engine.rodent.unavailable">Moteur Rodent indisponible sur ce système</span>
-          <button id="labo-rodent-download-btn" type="button" onclick="downloadRodent()"
-                  style="display:none; margin-left:6px; font-size:0.7rem; padding:2px 6px; cursor:pointer;"
-                  data-i18n="engine.rodent.download">Télécharger Rodent IV</button>
-          <span id="labo-rodent-download-status" style="margin-left:4px; color:#3a5a7a;"></span>
         </div>
+        <span id="labo-rodent-download-status" style="display:block; font-size:0.72rem; color:#3a5a7a;"></span>
         <div id="labo-cfg-sf">
           <div style="display:flex; align-items:center; gap:5px; margin-bottom:3px;">
             <button onclick="laboAdjElo(-200)" style="width:36px;height:28px;background:#a0b8d0;border:1px solid #333;border-radius:4px;color:#445;cursor:pointer;font-size:0.7rem;">-200</button>
