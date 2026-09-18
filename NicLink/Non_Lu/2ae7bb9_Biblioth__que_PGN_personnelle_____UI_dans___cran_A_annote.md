2ae7bb9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2ae7bb9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 21:57:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Bibliothèque PGN personnelle — UI dans écran Analyse de partie (issue #194, suite #193)
    
    Toggle « Mes parties AlChess » / « Bibliothèque PGN » en haut de l'écran
    Analyse (défaut inchangé : Mes parties AlChess). Nouvel onglet bibliothèque :
    dropdown collections + créer (modal input nom) + supprimer (confirmation),
    import PGN via input file caché + FileReader + spinner pendant le parsing
    serveur, liste scrollable des parties (White/Black/Date/Result/Event),
    clic → pgn_lib_load_game → chargé dans le viewer existant via parsePgn().
    Collection active conservée en variable JS module pour la navigation retour.
    Clés i18n pgn_lib.* et analyse.tab.* ajoutées en fr/en/de.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f72d5c9..8422c8a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 226 (6 ligne(s)) dans l'ancienne version → ligne 226 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -226,6 +226,15 @@ let _gameFolders     = null;
 let _lastTurnInfo    = null;  // {type: "move"|"turn"|"echec", player, color, san?}
 let _analyseEmpty    = false; // true quand l'écran analyse est vide (titre + invite import PGN)
 
+// ── Bibliothèque PGN personnelle (écran Analyse de partie, issue #194) ──────
+let _pgnLibActiveTab          = "alchess"; // onglet actif : "alchess" | "library"
+let _pgnLibCollections        = [];
+let _pgnLibCollectionsLoaded  = false;
+let _pgnLibActiveCollectionId = ""; // conservée pour retrouver la dernière sélection au retour sur l'écran
+let _pgnLibGames              = [];
+let _pgnLibCreating           = false;
+let _pgnLibPrevIds            = new Set();
+
 
 // ── MODE VIRTUEL ──────────────────────────────────────────
 
# ── Zone modifiée : ligne 935 (6 ligne(s)) dans l'ancienne version → ligne 944 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -935,6 +944,7 @@ socket.on("app_state", (data) => {
     _retransPlayerData = null;
     _gameSource = "externe";
     _viderAnalyse();
+    pgnLibSelectTab("alchess"); // l'écran Analyse rouvre toujours sur « Mes parties AlChess » par défaut
     _virtDeactivateBoard();
     _chessInstance = null;
     // Quitter le mode virtuel au retour au menu (badge échiquier repasse en mode physique)
# ── Zone modifiée : ligne 1902 (6 ligne(s)) dans l'ancienne version → ligne 1912 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1902,6 +1912,10 @@ function fermerModal() {
   if (sub) sub.textContent = "";
   const cancel = document.getElementById("modal-cancel");
   if (cancel) cancel.style.display = "";
+  const inputRow = document.getElementById("modal-input-row");
+  if (inputRow) inputRow.style.display = "none";
+  const input = document.getElementById("modal-input");
+  if (input) input.value = "";
 }
 
 // ── Aide contextuelle « classeur » ──────────────────────────────────────────
# ── Zone modifiée : ligne 2338 (6 ligne(s)) dans l'ancienne version → ligne 2352 (199 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2338,6 +2352,199 @@ function parsePgn(pgn) {
     alert("Erreur lors du parsing PGN : " + e.message);
   }
 }
+
+// ── Bibliothèque PGN personnelle (écran Analyse de partie, issue #194) ──────
+
+function _pgnLibEsc(str) {
+  const div = document.createElement("div");
+  div.textContent = str == null ? "" : String(str);
+  return div.innerHTML;
+}
+
+function pgnLibSelectTab(tab) {
+  _pgnLibActiveTab = tab;
+  const aBtn = document.getElementById("analyse-tab-alchess-btn");
+  const lBtn = document.getElementById("analyse-tab-library-btn");
+  const aContent = document.getElementById("analyse-tab-alchess-content");
+  const lContent = document.getElementById("analyse-tab-library-content");
+  if (aBtn) { aBtn.style.background = tab === "alchess" ? "#e94560" : "#c2d4e8"; aBtn.style.color = tab === "alchess" ? "white" : "#3a5a7a"; }
+  if (lBtn) { lBtn.style.background = tab === "library" ? "#e94560" : "#c2d4e8"; lBtn.style.color = tab === "library" ? "white" : "#3a5a7a"; }
+  if (aContent) aContent.style.display = tab === "alchess" ? "flex" : "none";
+  if (lContent) lContent.style.display = tab === "library" ? "flex" : "none";
+  if (tab === "library") {
+    if (!_pgnLibCollectionsLoaded) {
+      socket.emit("pgn_lib_list_collections", {});
+    } else {
+      pgnLibRenderCollectionsSelect();
+      pgnLibRenderGamesList();
+    }
+  }
+}
+
+function pgnLibRenderCollectionsSelect() {
+  const sel = document.getElementById("pgn-lib-collection-select");
+  if (!sel) return;
+  if (_pgnLibCollections.length === 0) {
+    sel.innerHTML = `<option value="">${t("pgn_lib.select.vide")}</option>`;
+    sel.disabled = true;
+    return;
+  }
+  sel.disabled = false;
+  sel.innerHTML = _pgnLibCollections.map(c =>
+    `<option value="${_pgnLibEsc(c.id)}" ${c.id === _pgnLibActiveCollectionId ? "selected" : ""}>${_pgnLibEsc(c.name)} (${c.game_count})</option>`
+  ).join("");
+}
+
+function pgnLibRenderGamesList() {
+  const list = document.getElementById("pgn-lib-games-list");
+  if (!list) return;
+  if (_pgnLibGames.length === 0) {
+    list.innerHTML = `<div class="pgn-lib-empty" style="color:#778; font-size:0.8rem; text-align:center; padding:12px 0;">${t("pgn_lib.liste_vide")}</div>`;
+    return;
+  }
+  list.innerHTML = _pgnLibGames.map(g => `
+    <div class="pgn-lib-game-row" onclick="pgnLibLoadGame(${g.index})"
+      onmouseover="this.style.background='#a0b8d0'" onmouseout="this.style.background='#c2d4e8'"
+      style="cursor:pointer; padding:6px 8px; border-radius:4px; background:#c2d4e8; font-size:0.78rem; color:#1a2a3a; line-height:1.4;">
+      <div style="font-weight:bold;">${_pgnLibEsc(g.white)} — ${_pgnLibEsc(g.black)}</div>
+      <div style="color:#3a5a7a;">${_pgnLibEsc(g.date)} · ${_pgnLibEsc(g.result)}${g.event ? " · " + _pgnLibEsc(g.event) : ""}</div>
+    </div>
+  `).join("");
+}
+
+function pgnLibSelectCollection(id) {
+  _pgnLibActiveCollectionId = id;
+  _pgnLibGames = [];
+  pgnLibRenderGamesList();
+  if (id) socket.emit("pgn_lib_list_games", { collection_id: id });
+}
+
+function pgnLibOpenCreateModal() {
+  document.getElementById("modal-title").textContent = t("pgn_lib.modal.creer_titre");
+  const sub = document.getElementById("modal-subtitle");
+  if (sub) sub.textContent = "";
+  const inputRow = document.getElementById("modal-input-row");
+  const input = document.getElementById("modal-input");
+  if (inputRow) inputRow.style.display = "block";
+  if (input) input.placeholder = t("pgn_lib.modal.creer_placeholder");
+  const btn = document.getElementById("modal-confirm");
+  btn.textContent = t("pgn_lib.modal.creer_confirmer");
+  btn.className = "btn btn-reprendre";
+  btn.onclick = () => {
+    const name = (input?.value || "").trim();
+    if (!name) return;
+    fermerModal();
+    _pgnLibCreating = true;
+    _pgnLibPrevIds = new Set(_pgnLibCollections.map(c => c.id));
+    socket.emit("pgn_lib_create_collection", { name });
+  };
+  const std  = document.getElementById("modal-btns-standard");
+  const coul = document.getElementById("modal-btns-couleur");
+  if (std)  std.style.display  = "flex";
+  if (coul) coul.style.display = "none";
+  document.getElementById("modal-overlay").classList.add("open");
+  setTimeout(() => input?.focus(), 50);
+}
+
+function pgnLibConfirmDelete() {
+  if (!_pgnLibActiveCollectionId) return;
+  const coll = _pgnLibCollections.find(c => c.id === _pgnLibActiveCollectionId);
+  const name = coll ? coll.name : "";
+  document.getElementById("modal-title").textContent = t("pgn_lib.modal.supprimer_titre", { nom: name });
+  const sub = document.getElementById("modal-subtitle");
+  if (sub) sub.textContent = t("pgn_lib.modal.supprimer_sous");
+  const btn = document.getElementById("modal-confirm");
+  btn.textContent = t("pgn_lib.modal.supprimer_confirmer");
+  btn.className = "btn btn-warning";
+  const collectionId = _pgnLibActiveCollectionId;
+  btn.onclick = () => {
+    fermerModal();
+    socket.emit("pgn_lib_delete_collection", { collection_id: collectionId });
+    _pgnLibActiveCollectionId = "";
+  };
+  const std  = document.getElementById("modal-btns-standard");
+  const coul = document.getElementById("modal-btns-couleur");
+  if (std)  std.style.display  = "flex";
+  if (coul) coul.style.display = "none";
+  document.getElementById("modal-overlay").classList.add("open");
+}
+
+function pgnLibImportFile(event) {
+  const file = event.target.files[0];
+  event.target.value = ""; // permet de réimporter le même fichier ensuite
+  if (!file) return;
+  if (!_pgnLibActiveCollectionId) {
+    afficherToast(t("pgn_lib.import_sans_collection"), "warning");
+    return;
+  }
+  const reader = new FileReader();
+  reader.onload = (e) => {
+    const btn = document.getElementById("pgn-lib-import-btn");
+    const spinner = document.getElementById("pgn-lib-import-spinner");
+    if (btn) btn.style.display = "none";
+    if (spinner) spinner.style.display = "flex";
+    socket.emit("pgn_lib_import_pgn", { collection_id: _pgnLibActiveCollectionId, content: e.target.result });
+  };
+  reader.readAsText(file);
+}
+
+function pgnLibLoadGame(index) {
+  if (!_pgnLibActiveCollectionId) return;
+  socket.emit("pgn_lib_load_game", { collection_id: _pgnLibActiveCollectionId, index });
+}
+
+socket.on("pgn_lib_collections", (data) => {
+  _pgnLibCollections = data.collections || [];
+  _pgnLibCollectionsLoaded = true;
+  if (_pgnLibCreating) {
+    const fresh = _pgnLibCollections.find(c => !_pgnLibPrevIds.has(c.id));
+    if (fresh) _pgnLibActiveCollectionId = fresh.id;
+    _pgnLibCreating = false;
+  }
+  // Retombe sur la première collection dispo si l'active a été supprimée / n'existe plus
+  if (_pgnLibActiveCollectionId && !_pgnLibCollections.some(c => c.id === _pgnLibActiveCollectionId)) {
+    _pgnLibActiveCollectionId = "";
+  }
+  if (!_pgnLibActiveCollectionId && _pgnLibCollections.length > 0) {
+    _pgnLibActiveCollectionId = _pgnLibCollections[0].id;
+  }
+  pgnLibRenderCollectionsSelect();
+  if (_pgnLibActiveCollectionId) {
+    socket.emit("pgn_lib_list_games", { collection_id: _pgnLibActiveCollectionId });
+  } else {
+    _pgnLibGames = [];
+    pgnLibRenderGamesList();
+  }
+});
+
+socket.on("pgn_lib_games", (data) => {
+  if (data.import_result) {
+    const btn = document.getElementById("pgn-lib-import-btn");
+    const spinner = document.getElementById("pgn-lib-import-spinner");
+    if (btn) btn.style.display = "";
+    if (spinner) spinner.style.display = "none";
+    const r = data.import_result;
+    afficherToast(r.ok ? t("pgn_lib.import_ok", { n: r.imported }) : t("pgn_lib.import_echec"), r.ok ? "success" : "warning");
+    // Rafraîchit le compteur de parties affiché dans le dropdown
+    socket.emit("pgn_lib_list_collections", {});
+  }
+  if (data.collection_id !== _pgnLibActiveCollectionId) return;
+  _pgnLibGames = data.games || [];
+  pgnLibRenderGamesList();
+});
+
+socket.on("pgn_lib_game_loaded", (data) => {
+  parsePgn(data.pgn);
+});
+
+socket.on("pgn_lib_error", (data) => {
+  const btn = document.getElementById("pgn-lib-import-btn");
+  const spinner = document.getElementById("pgn-lib-import-spinner");
+  if (btn) btn.style.display = "";
+  if (spinner) spinner.style.display = "none";
+  afficherToast(data.message || t("pgn_lib.erreur_generique"), "warning");
+});
+
 // ── Pause ──────────────────────────────────────────────────────────────────
 
 let _pauseReviewFens    = [];
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index 33fa3f5..ef0499f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 417 (6 ligne(s)) dans l'ancienne version → ligne 417 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -417,6 +417,24 @@
   "analyse.importer_pgn": "Eine PGN-Datei importieren",
   "analyse.btn.coller_pgn": "📋 PGN einfügen",
   "analyse.btn.charger_pgn_colle": "✅ Laden",
+  "analyse.tab.alchess": "♟ Meine AlChess-Partien",
+  "analyse.tab.library": "📚 PGN-Bibliothek",
+  "pgn_lib.select.vide": "— Keine Sammlung —",
+  "pgn_lib.btn.creer_title": "Sammlung erstellen",
+  "pgn_lib.btn.supprimer_title": "Sammlung löschen",
+  "pgn_lib.btn.importer": "📂 PGN importieren",
+  "pgn_lib.import_en_cours": "Import läuft…",
+  "pgn_lib.liste_vide": "Keine Partien in dieser Sammlung.",
+  "pgn_lib.modal.creer_titre": "Neue Sammlung",
+  "pgn_lib.modal.creer_placeholder": "Name der Sammlung (z. B. Carlsen)",
+  "pgn_lib.modal.creer_confirmer": "✅ Erstellen",
+  "pgn_lib.modal.supprimer_titre": "„{nom}“ löschen?",
+  "pgn_lib.modal.supprimer_sous": "Alle Partien dieser Sammlung werden endgültig gelöscht.",
+  "pgn_lib.modal.supprimer_confirmer": "🗑 Löschen",
+  "pgn_lib.import_sans_collection": "Zuerst eine Sammlung auswählen oder erstellen.",
+  "pgn_lib.import_ok": "✅ {n} Partie(n) importiert",
+  "pgn_lib.import_echec": "Import fehlgeschlagen — keine gültige Partie gefunden.",
+  "pgn_lib.erreur_generique": "Fehler in der PGN-Bibliothek.",
   "config.joueur1": "Spieler 1",
   "config.joueur2": "Spieler 2",
   "config.joueur_blancs": "Spieler Weiß",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index 7f3de64..9b10c57 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 417 (6 ligne(s)) dans l'ancienne version → ligne 417 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -417,6 +417,24 @@
   "analyse.importer_pgn": "Import a PGN file",
   "analyse.btn.coller_pgn": "📋 Paste PGN",
   "analyse.btn.charger_pgn_colle": "✅ Load",
+  "analyse.tab.alchess": "♟ My AlChess games",
+  "analyse.tab.library": "📚 PGN library",
+  "pgn_lib.select.vide": "— No collection —",
+  "pgn_lib.btn.creer_title": "Create a collection",
+  "pgn_lib.btn.supprimer_title": "Delete the collection",
+  "pgn_lib.btn.importer": "📂 Import PGN",
+  "pgn_lib.import_en_cours": "Importing…",
+  "pgn_lib.liste_vide": "No games in this collection.",
+  "pgn_lib.modal.creer_titre": "New collection",
+  "pgn_lib.modal.creer_placeholder": "Collection name (e.g. Carlsen)",
+  "pgn_lib.modal.creer_confirmer": "✅ Create",
+  "pgn_lib.modal.supprimer_titre": "Delete \"{nom}\"?",
+  "pgn_lib.modal.supprimer_sous": "All games in this collection will be permanently deleted.",
+  "pgn_lib.modal.supprimer_confirmer": "🗑 Delete",
+  "pgn_lib.import_sans_collection": "Select or create a collection first.",
+  "pgn_lib.import_ok": "✅ {n} game(s) imported",
+  "pgn_lib.import_echec": "Import failed — no valid game found.",
+  "pgn_lib.erreur_generique": "PGN library error.",
   "config.joueur1": "Player 1",
   "config.joueur2": "Player 2",
   "config.joueur_blancs": "White player",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index 6ae4b26..36fe985 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 417 (6 ligne(s)) dans l'ancienne version → ligne 417 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -417,6 +417,24 @@
   "analyse.importer_pgn": "Importez un fichier PGN",
   "analyse.btn.coller_pgn": "📋 Coller PGN",
   "analyse.btn.charger_pgn_colle": "✅ Charger",
+  "analyse.tab.alchess": "♟ Mes parties AlChess",
+  "analyse.tab.library": "📚 Bibliothèque PGN",
+  "pgn_lib.select.vide": "— Aucune collection —",
+  "pgn_lib.btn.creer_title": "Créer une collection",
+  "pgn_lib.btn.supprimer_title": "Supprimer la collection",
+  "pgn_lib.btn.importer": "📂 Importer PGN",
+  "pgn_lib.import_en_cours": "Import en cours…",
+  "pgn_lib.liste_vide": "Aucune partie dans cette collection.",
+  "pgn_lib.modal.creer_titre": "Nouvelle collection",
+  "pgn_lib.modal.creer_placeholder": "Nom de la collection (ex. Carlsen)",
+  "pgn_lib.modal.creer_confirmer": "✅ Créer",
+  "pgn_lib.modal.supprimer_titre": "Supprimer « {nom} » ?",
+  "pgn_lib.modal.supprimer_sous": "Toutes les parties de cette collection seront définitivement supprimées.",
+  "pgn_lib.modal.supprimer_confirmer": "🗑 Supprimer",
+  "pgn_lib.import_sans_collection": "Sélectionnez ou créez d'abord une collection.",
+  "pgn_lib.import_ok": "✅ {n} partie(s) importée(s)",
+  "pgn_lib.import_echec": "Échec de l'import — aucune partie valide trouvée.",
+  "pgn_lib.erreur_generique": "Erreur bibliothèque PGN.",
   "config.joueur1": "Joueur 1",
   "config.joueur2": "Joueur 2",
   "config.joueur_blancs": "Joueur Blancs",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 40b6bb4..c67af24 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 751 (24 ligne(s)) dans l'ancienne version → ligne 751 (66 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -751,24 +751,66 @@
       </div>
       <!-- Actions analyse + retour menu -->
       <div class="card" style="padding:14px 18px; display:flex; flex-direction:column; gap:8px;">
-        <input type="file" id="pgn-file-input" accept=".pgn" style="display:none" onchange="loadPgnFile(event)">
-        <button class="btn btn-best"      style="margin-bottom:0;" onclick="document.getElementById('pgn-file-input').click()" data-i18n="labo.btn.importer_pgn">📂 Importer PGN</button>
-        <!-- Coller PGN directement -->
-        <button class="btn btn-best" style="margin-bottom:0;" onclick="toggleCollerPgn()" data-i18n="analyse.btn.coller_pgn">📋 Coller PGN</button>
-        <div id="coller-pgn-zone" style="display:none; margin-top:8px;">
-          <textarea id="coller-pgn-input" rows="8" style="width:100%; font-family:monospace; font-size:12px; resize:vertical;" placeholder="Collez ici le contenu PGN..."></textarea>
-          <button class="btn btn-reprendre" style="margin-top:4px; margin-bottom:0; width:100%;" onclick="chargerPgnColle()" data-i18n="analyse.btn.charger_pgn_colle">✅ Charger</button>
+        <!-- Toggle Mes parties AlChess / Bibliothèque PGN -->
+        <div style="display:flex; gap:0; border-radius:6px; overflow:hidden; border:1px solid #a0b8d0; margin-bottom:2px;">
+          <button id="analyse-tab-alchess-btn" onclick="pgnLibSelectTab('alchess')" data-i18n="analyse.tab.alchess"
+            style="flex:1; padding:8px 4px; font-size:0.78rem; font-weight:bold; cursor:pointer; border:none; background:#e94560; color:white; transition:opacity 0.15s;">
+            ♟ Mes parties AlChess
+          </button>
+          <button id="analyse-tab-library-btn" onclick="pgnLibSelectTab('library')" data-i18n="analyse.tab.library"
+            style="flex:1; padding:8px 4px; font-size:0.78rem; font-weight:bold; cursor:pointer; border:none; background:#c2d4e8; color:#3a5a7a; transition:opacity 0.15s;">
+            📚 Bibliothèque PGN
+          </button>
         </div>
-        <!-- Classeur de session -->
-        <div id="basket-row-analyse" style="display:flex; gap:6px; align-items:stretch;">
-          <span class="aide-panier-icone" onclick="ouvrirAidePanier()" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
-          <div id="basket-select-analyse" class="basket-select" data-value="" style="flex:1; position:relative; height:34px; box-sizing:border-box; background:#a0b8d0; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; display:flex; align-items:center; justify-content:space-between; cursor:pointer; user-select:none;">
-            <span class="basket-sel-label" data-i18n="common.corbeille_vide" style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#556;">— classeur vide —</span>
-            <span style="font-size:0.6rem; margin-left:4px; color:#1a2a3a; flex-shrink:0;">▼</span>
-            <div class="basket-sel-list" style="display:none; position:absolute; bottom:100%; left:0; right:0; background:#1a2a3a; border:1px solid #a0b8d0; border-bottom:none; border-radius:4px 4px 0 0; z-index:200; max-height:180px; overflow-y:auto;"></div>
+
+        <!-- Onglet « Mes parties AlChess » (comportement existant, inchangé) -->
+        <div id="analyse-tab-alchess-content" style="display:flex; flex-direction:column; gap:8px;">
+          <input type="file" id="pgn-file-input" accept=".pgn" style="display:none" onchange="loadPgnFile(event)">
+          <button class="btn btn-best"      style="margin-bottom:0;" onclick="document.getElementById('pgn-file-input').click()" data-i18n="labo.btn.importer_pgn">📂 Importer PGN</button>
+          <!-- Coller PGN directement -->
+          <button class="btn btn-best" style="margin-bottom:0;" onclick="toggleCollerPgn()" data-i18n="analyse.btn.coller_pgn">📋 Coller PGN</button>
+          <div id="coller-pgn-zone" style="display:none; margin-top:8px;">
+            <textarea id="coller-pgn-input" rows="8" style="width:100%; font-family:monospace; font-size:12px; resize:vertical;" placeholder="Collez ici le contenu PGN..."></textarea>
+            <button class="btn btn-reprendre" style="margin-top:4px; margin-bottom:0; width:100%;" onclick="chargerPgnColle()" data-i18n="analyse.btn.charger_pgn_colle">✅ Charger</button>
+          </div>
+          <!-- Classeur de session -->
+          <div id="basket-row-analyse" style="display:flex; gap:6px; align-items:stretch;">
+            <span class="aide-panier-icone" onclick="ouvrirAidePanier()" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
+            <div id="basket-select-analyse" class="basket-select" data-value="" style="flex:1; position:relative; height:34px; box-sizing:border-box; background:#a0b8d0; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; display:flex; align-items:center; justify-content:space-between; cursor:pointer; user-select:none;">
+              <span class="basket-sel-label" data-i18n="common.corbeille_vide" style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#556;">— classeur vide —</span>
+              <span style="font-size:0.6rem; margin-left:4px; color:#1a2a3a; flex-shrink:0;">▼</span>
+              <div class="basket-sel-list" style="display:none; position:absolute; bottom:100%; left:0; right:0; background:#1a2a3a; border:1px solid #a0b8d0; border-bottom:none; border-radius:4px 4px 0 0; z-index:200; max-height:180px; overflow-y:auto;"></div>
+            </div>
+            <button class="btn basket-load-btn" style="margin-bottom:0; padding:0 12px; white-space:nowrap; height:34px; box-sizing:border-box;" disabled onclick="basketLoadToAnalyse()" data-i18n="common.charger">🗂️ Charger</button>
+          </div>
+        </div>
+
+        <!-- Onglet « Bibliothèque PGN » (nouveau, issue #194) -->
+        <div id="analyse-tab-library-content" style="display:none; flex-direction:column; gap:8px;">
+          <!-- Sélection collection + créer/supprimer -->
+          <div style="display:flex; gap:6px; align-items:stretch;">
+            <select id="pgn-lib-collection-select" onchange="pgnLibSelectCollection(this.value)"
+              style="flex:1; min-width:0; background:#a0b8d0; color:#1a2a3a; border:1px solid #333; border-radius:4px; padding:4px 8px; font-size:0.82rem; height:34px; box-sizing:border-box;">
+              <option value="" data-i18n="pgn_lib.select.vide">— Aucune collection —</option>
+            </select>
+            <button class="btn" style="margin-bottom:0; padding:0 10px; white-space:nowrap; height:34px; box-sizing:border-box; background:#2e7d32; color:white;" onclick="pgnLibOpenCreateModal()" data-i18n-title="pgn_lib.btn.creer_title" title="Créer une collection">＋</button>
+            <button class="btn btn-warning" style="margin-bottom:0; padding:0 10px; white-space:nowrap; height:34px; box-sizing:border-box;" onclick="pgnLibConfirmDelete()" data-i18n-title="pgn_lib.btn.supprimer_title" title="Supprimer la collection">🗑</button>
+          </div>
+
+          <!-- Import PGN dans la collection active -->
+          <input type="file" id="pgn-lib-file-input" accept=".pgn,text/plain" style="display:none" onchange="pgnLibImportFile(event)">
+          <button class="btn btn-best" id="pgn-lib-import-btn" style="margin-bottom:0;" onclick="document.getElementById('pgn-lib-file-input').click()" data-i18n="pgn_lib.btn.importer">📂 Importer PGN</button>
+          <div id="pgn-lib-import-spinner" style="display:none; align-items:center; gap:8px; color:#3a5a7a; font-size:0.8rem;">
+            <div style="width:14px; height:14px; border:2px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite;"></div>
+            <span data-i18n="pgn_lib.import_en_cours">Import en cours…</span>
+          </div>
+
+          <!-- Liste des parties de la collection active -->
+          <div id="pgn-lib-games-list" style="max-height:260px; overflow-y:auto; display:flex; flex-direction:column; gap:4px; border:1px solid #a0b8d0; border-radius:6px; padding:6px; background:#eef4fa;">
+            <div class="pgn-lib-empty" style="color:#778; font-size:0.8rem; text-align:center; padding:12px 0;" data-i18n="pgn_lib.liste_vide">Aucune partie dans cette collection.</div>
           </div>
-          <button class="btn basket-load-btn" style="margin-bottom:0; padding:0 12px; white-space:nowrap; height:34px; box-sizing:border-box;" disabled onclick="basketLoadToAnalyse()" data-i18n="common.charger">🗂️ Charger</button>
         </div>
+
         <!-- Sélecteur nombre de coups séquence -->
         <div id="rv-seq-row" style="display:none; align-items:center; gap:8px;">
           <label data-i18n="game.label.sequence" style="font-size:0.8rem; color:#3a5a7a; white-space:nowrap;">Séquence :</label>
# ── Zone modifiée : ligne 1717 (6 ligne(s)) dans l'ancienne version → ligne 1759 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1717,6 +1759,10 @@
   <div style="background:#c2d4e8; border:1px solid #e94560; border-radius:10px; padding:28px 32px; min-width:300px; max-width:520px; text-align:center;">
     <div id="modal-title" style="font-size:1.1rem; color:#1a2a3a; margin-bottom:8px;"></div>
     <div id="modal-subtitle" style="font-size:0.78rem; color:#3a5a7a; margin-bottom:20px; white-space:pre-line; word-break:break-all;"></div>
+    <!-- Champ texte optionnel (ex. nom de collection bibliothèque PGN) -->
+    <div id="modal-input-row" style="display:none; margin-bottom:16px;">
+      <input type="text" id="modal-input" maxlength="60" style="width:100%; box-sizing:border-box; padding:8px 10px; border:1px solid #a0b8d0; border-radius:4px; font-size:0.9rem; background:#eef4fa; color:#1a2a3a;">
+    </div>
     <!-- Boutons standard (confirmation simple) -->
     <div id="modal-btns-standard" style="display:flex; gap:12px; justify-content:center;">
       <button id="modal-confirm" class="btn" style="min-width:120px;"></button>
