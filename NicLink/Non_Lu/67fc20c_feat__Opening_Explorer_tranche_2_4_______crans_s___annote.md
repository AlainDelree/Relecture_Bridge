67fc20c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 67fc20c
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 15:00:10 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: Opening Explorer tranche 2/4 — écrans sélecteur/lecteur + fix taille échiquier (issue #140)
    
    Finalise la tranche 2/4 : écrans frontend (sélecteur catalogue/mes ouvertures,
    lecteur avec navigation Prev/Next), fix regroupement des variantes mes_lignes
    (numérotation "Nom N" au lieu d'écraser les doublons par nom), et fix CSS
    critique — #expl-board/#expl-coord-rank absents de la règle de dimensionnement
    --bd-size, ce qui aurait rendu l'échiquier invisible.
    
    Backend (session/sources/handlers) déjà commité en d27c518.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ed7c2b4..3948fb5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 1075 (12 ligne(s)) dans l'ancienne version → ligne 1075 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1075,12 +1075,19 @@ def explorer_get_list() -> dict:
 
     groupes: dict = {}
     for l in get_mes_lignes():
-        groupes.setdefault(l.get("nom", ""), []).append({
-            "id":           l.get("id", ""),
-            "nom":          l.get("nom", ""),
-            "camp_suggere": l.get("camp_suggere", "white"),
-        })
-    mes_lignes = [{"groupe": nom, "variantes": variantes} for nom, variantes in groupes.items()]
+        groupes.setdefault(l.get("nom", ""), []).append(l)
+
+    mes_lignes = []
+    for nom, lignes in groupes.items():
+        variantes = [
+            {
+                "id":           l.get("id", ""),
+                "nom":          f"{nom} {i}" if len(lignes) > 1 else nom,
+                "camp_suggere": l.get("camp_suggere", "white"),
+            }
+            for i, l in enumerate(lignes, start=1)
+        ]
+        mes_lignes.append({"groupe": nom, "variantes": variantes})
 
     return {"catalogue": catalogue, "mes_lignes": mes_lignes}
 
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 5ef57ec..a39b349 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6035 (3 ligne(s)) dans l'ancienne version → ligne 6035 (166 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6035,3 +6035,166 @@ socket.on("config_saved", (data) => {
     afficherToast(t("parametres.toast.erreur"), "warning");
   }
 });
+
+// ── Opening Explorer ─────────────────────────────────────────────────────────
+
+let _explAtStart   = true;
+let _explEndOfLine = false;
+
+socket.on("app_state", (data) => {
+  const selEl  = document.getElementById("screen-opening-explorer-select");
+  const playEl = document.getElementById("screen-opening-explorer-play");
+  if (selEl)  selEl.style.display  = "none";
+  if (playEl) playEl.style.display = "none";
+  if (data.state === "opening_explorer") {
+    explShowSelect();
+  }
+});
+
+function explShowSelect() {
+  const selEl  = document.getElementById("screen-opening-explorer-select");
+  const playEl = document.getElementById("screen-opening-explorer-play");
+  if (playEl) playEl.style.display = "none";
+  if (selEl)  selEl.style.display  = "flex";
+  socket.emit("explorer_get_list", {});
+}
+
+function explBackToSelect() {
+  socket.emit("explorer_back", {});
+  explShowSelect();
+}
+
+socket.on("explorer_list", (data) => {
+  explRenderCatalogue((data && data.catalogue) || []);
+  explRenderMesLignes((data && data.mes_lignes) || []);
+});
+
+function explRenderCatalogue(catalogue) {
+  const list = document.getElementById("expl-catalogue-list");
+  const vide = document.getElementById("expl-catalogue-vide");
+  if (!list) return;
+  list.innerHTML = "";
+  if (vide) vide.style.display = catalogue.length ? "none" : "block";
+  for (const o of catalogue) {
+    const row = document.createElement("div");
+    row.style.cssText = "padding:8px 12px; background:#f4f7fb; border:1px solid #a0b8d0; border-radius:6px; cursor:pointer; font-size:0.88rem; color:#1a2a3a;";
+    row.textContent = o.eco ? `${o.nom}  (${o.eco})` : o.nom;
+    row.onclick = () => explLoad("polyglot", o.id);
+    list.appendChild(row);
+  }
+}
+
+function explRenderMesLignes(groupes) {
+  const list = document.getElementById("expl-mes-lignes-list");
+  const vide = document.getElementById("expl-mes-lignes-vide");
+  if (!list) return;
+  list.innerHTML = "";
+  if (vide) vide.style.display = groupes.length ? "none" : "block";
+  for (const g of groupes) {
+    const section = document.createElement("div");
+    section.style.cssText = "border-left:3px solid #e94560; padding-left:10px;";
+    const title = document.createElement("div");
+    title.style.cssText = "font-weight:700; color:#1a2a3a; font-size:0.88rem; margin-bottom:4px;";
+    title.textContent = g.groupe;
+    section.appendChild(title);
+    const variantesWrap = document.createElement("div");
+    variantesWrap.style.cssText = "display:flex; flex-wrap:wrap; gap:6px;";
+    for (const v of (g.variantes || [])) {
+      const item = document.createElement("div");
+      item.style.cssText = "padding:6px 10px; background:#f4f7fb; border:1px solid #a0b8d0; border-radius:6px; cursor:pointer; font-size:0.82rem; color:#1a2a3a;";
+      item.textContent = v.nom;
+      item.onclick = () => explLoad("pgn", v.id);
+      variantesWrap.appendChild(item);
+    }
+    section.appendChild(variantesWrap);
+    list.appendChild(section);
+  }
+}
+
+function explLoad(sourceType, openingId) {
+  socket.emit("explorer_load", { source_type: sourceType, opening_id: openingId });
+}
+
+function explNext() {
+  if (_explEndOfLine) return;
+  socket.emit("explorer_next", {});
+}
+
+function explPrev() {
+  if (_explAtStart) return;
+  socket.emit("explorer_prev", {});
+}
+
+socket.on("explorer_state", (data) => {
+  if (!data) return;
+  if (data.error) {
+    afficherToast(t("opening_explorer.erreur_chargement"), "warning");
+    return;
+  }
+
+  const selEl  = document.getElementById("screen-opening-explorer-select");
+  const playEl = document.getElementById("screen-opening-explorer-play");
+  if (selEl)  selEl.style.display  = "none";
+  if (playEl) playEl.style.display = "grid";
+
+  const nomEl = document.getElementById("expl-nom");
+  if (nomEl) nomEl.textContent = data.opening_name || "";
+
+  const coupEl = document.getElementById("expl-coup-courant");
+  if (coupEl) {
+    coupEl.textContent = data.move_index > 0
+      ? t("opening_explorer.coup_n", { n: data.move_index, san: data.move_san || "" })
+      : t("opening_explorer.position_initiale");
+  }
+
+  const [from, to] = uciToCoords(data.last_move_uci);
+  explRenderBoard(data.fen, from, to);
+
+  _explAtStart   = !!data.at_start;
+  _explEndOfLine = !!data.end_of_line;
+  const prevBtn = document.getElementById("expl-btn-prev");
+  const nextBtn = document.getElementById("expl-btn-next");
+  if (prevBtn) prevBtn.disabled = _explAtStart;
+  if (nextBtn) nextBtn.disabled = _explEndOfLine;
+});
+
+// Échiquier Opening Explorer — lecture seule, coups joués par les deux sources.
+function explBuildBoard() {
+  const board = document.getElementById("expl-board");
+  if (!board || board.children.length) return;
+  const rankCoord = document.getElementById("expl-coord-rank");
+  if (rankCoord) {
+    rankCoord.innerHTML = "";
+    [7,6,5,4,3,2,1,0].forEach(r => { const s = document.createElement("span"); s.textContent = r + 1; rankCoord.appendChild(s); });
+  }
+  const fileCoord = document.getElementById("expl-coord-file");
+  if (fileCoord) {
+    fileCoord.innerHTML = "";
+    "abcdefgh".split("").forEach(f => { const s = document.createElement("span"); s.textContent = f; fileCoord.appendChild(s); });
+  }
+  for (let rank = 7; rank >= 0; rank--) {
+    for (let file = 0; file < 8; file++) {
+      const sq = document.createElement("div");
+      sq.className = `square ${(rank + file) % 2 === 1 ? "light" : "dark"}`;
+      sq.id = `expl-sq-${file}-${rank}`;
+      board.appendChild(sq);
+    }
+  }
+}
+
+function explRenderBoard(fen, from, to) {
+  explBuildBoard();
+  const grid = fenToBoard(fen);
+  for (let rank = 7; rank >= 0; rank--) {
+    for (let file = 0; file < 8; file++) {
+      const id = `${file}-${rank}`;
+      const sq = document.getElementById(`expl-sq-${id}`);
+      if (!sq) continue;
+      const piece = grid[id];
+      sq.innerHTML = piece ? (PIECES[piece] || piece) : "";
+      sq.className = `square ${(rank + file) % 2 === 1 ? "light" : "dark"}`;
+      if (from && id === from) sq.classList.add("last-move-from");
+      if (to   && id === to)   sq.classList.add("last-move-to");
+    }
+  }
+}
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index cde0013..276973b 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 460 (14 ligne(s)) dans l'ancienne version → ligne 460 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -460,14 +460,14 @@
       color: #1a2a3a;
     }
 
-    #board, #rv-board, #board-pos-init, #retrans-board, #ex-board, #labo-board {
+    #board, #rv-board, #board-pos-init, #retrans-board, #ex-board, #labo-board, #expl-board {
       display: grid;
       grid-template-columns: repeat(8, 1fr);
       overflow: hidden;
       width: var(--bd-size);
       height: var(--bd-size);
     }
-    #ex-coord-rank, #labo-coord-rank { height: auto; align-self: stretch; }
+    #ex-coord-rank, #labo-coord-rank, #expl-coord-rank { height: auto; align-self: stretch; }
 
     .square {
       display: flex;
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index a8645f7..1733a98 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 31 (6 ligne(s)) dans l'ancienne version → ligne 31 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,6 +31,7 @@
   "menu.btn.retranscrire":     "✏️ Mitschreiben",
   "menu.btn.outils":           "🛠️ Übungs-Tools",
   "menu.btn.parametres":       "⚙ Einstellungen",
+  "menu.btn.opening_explorer": "♟ Eröffnungs-Explorer",
   "menu.btn.reconnect":        "🔌 Brett neu verbinden",
   "menu.btn.connecter":        "⟳ Verbinden",
   "menu.btn.debloquer":        "⟳ Schaltflächen entsperren",
# ── Zone modifiée : ligne 53 (6 ligne(s)) dans l'ancienne version → ligne 54 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -53,6 +54,7 @@
   "menu.desc.retrans":         "Eine auf Papier gespielte Partie mitschreiben. Züge auf dem virtuellen Brett eingeben und das PGN exportieren.",
   "menu.desc.outils":          "PGN-Linien importieren, SAN → UCI konvertieren und den Eröffnungskatalog verwalten.",
   "menu.desc.parametres":      "LLM-Zugang (API-Schlüssel) und Sprachausgabe (TTS) konfigurieren.",
+  "menu.desc.opening_explorer": "Eine Eröffnung Zug für Zug durchgehen — theoretischer Katalog oder eigene Linien.",
   "menu.autoupdate.label":     "Automatische Updates",
   "menu.autoupdate.warning":   "Automatische Updates sind deaktiviert. Sie erhalten weder Sicherheitskorrekturen noch neue Funktionen.",
 
# ── Zone modifiée : ligne 260 (6 ligne(s)) dans l'ancienne version → ligne 262 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -260,6 +262,20 @@
   "parametres.toast.enregistre":      "Einstellungen gespeichert",
   "parametres.toast.erreur":          "Fehler beim Speichern der Einstellungen",
 
+  "opening_explorer.titre":                "♟ Eröffnungs-Explorer",
+  "opening_explorer.catalogue.titre":      "📚 Katalog",
+  "opening_explorer.catalogue.vide":       "Keine Eröffnungen im Katalog.",
+  "opening_explorer.mes_ouvertures.titre": "★ Meine Eröffnungen",
+  "opening_explorer.mes_ouvertures.vide":  "Keine persönliche Linie importiert. Nutzen Sie die Übungs-Tools, um eine hinzuzufügen.",
+  "opening_explorer.btn.precedent":        "← Zurück",
+  "opening_explorer.btn.suivant":          "Weiter →",
+  "opening_explorer.btn.autre":            "↩ Andere Eröffnung wählen",
+  "opening_explorer.h2.explication":       "ERKLÄRUNG",
+  "opening_explorer.explication.a_venir":  "Die Zugerklärung wird hier bald verfügbar sein.",
+  "opening_explorer.position_initiale":    "Ausgangsstellung",
+  "opening_explorer.coup_n":               "Zug {n} — {san}",
+  "opening_explorer.erreur_chargement":    "Diese Eröffnung konnte nicht geladen werden.",
+
   "outils.titre":              "🛠️ Übungs-Tools",
   "outils.import_pgn.titre":   "📥 Meine PGN-Linien importieren",
   "outils.import_pgn.desc":    "Eine oder mehrere .pgn-Dateien in Ihre persönlichen Übungen importieren (<em>mes_lignes.json</em>).",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 59627c0..26f3520 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1586 (6 ligne(s)) dans l'ancienne version → ligne 1586 (80 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1586,6 +1586,80 @@
 </div>
 
 
+<!-- ── Écran Opening Explorer — sélecteur ── -->
+<div id="screen-opening-explorer-select" style="display:none; flex-direction:column; align-items:center; padding:24px; gap:20px; overflow-y:auto; width:100%;">
+
+  <div style="width:100%; max-width:860px; display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
+    <h2 style="margin:0; color:#1a2a3a; font-size:1.4rem;" data-i18n="opening_explorer.titre">♟ Opening Explorer</h2>
+    <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+  </div>
+
+  <!-- Catalogue -->
+  <div class="outil-card" style="width:100%; max-width:860px;">
+    <div class="outil-card-header">
+      <span class="outil-title" data-i18n="opening_explorer.catalogue.titre">📚 Catalogue</span>
+    </div>
+    <div id="expl-catalogue-list" style="display:flex; flex-direction:column; gap:6px; margin-top:10px;"></div>
+    <div id="expl-catalogue-vide" style="display:none; color:#888; font-size:0.85rem;" data-i18n="opening_explorer.catalogue.vide">Aucune ouverture dans le catalogue.</div>
+  </div>
+
+  <!-- Mes ouvertures -->
+  <div class="outil-card" style="width:100%; max-width:860px;">
+    <div class="outil-card-header">
+      <span class="outil-title" data-i18n="opening_explorer.mes_ouvertures.titre">★ Mes ouvertures</span>
+    </div>
+    <div id="expl-mes-lignes-list" style="display:flex; flex-direction:column; gap:10px; margin-top:10px;"></div>
+    <div id="expl-mes-lignes-vide" style="display:none; color:#888; font-size:0.85rem;" data-i18n="opening_explorer.mes_ouvertures.vide">Aucune ligne personnelle importée. Utilisez Outils Exercices pour en ajouter.</div>
+  </div>
+
+</div>
+
+<!-- ── Écran Opening Explorer — lecteur ── -->
+<div id="screen-opening-explorer-play" style="display:none; flex:1; grid-template-columns:220px minmax(0,1fr) 380px; gap:20px; padding:16px 20px; width:100%; max-width:100vw; align-items:start; overflow:hidden;">
+
+  <!-- Colonne gauche : info -->
+  <div style="display:flex; flex-direction:column; gap:8px;">
+    <div class="card" style="padding:12px 14px;">
+      <h2 id="expl-nom" style="color:#e94560; font-size:0.85rem; margin-bottom:8px;"></h2>
+      <div id="expl-coup-courant" style="font-size:0.9rem; font-weight:600; color:#1a2a3a;">—</div>
+    </div>
+  </div>
+
+  <!-- Colonne centre : échiquier -->
+  <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-width:0; max-height:calc(100vh - 60px); overflow:hidden;">
+    <div id="expl-board-wrapper" style="min-width:0; display:flex; flex-direction:column; border:2px solid #a0b8d0; border-radius:4px; overflow:hidden;">
+      <div class="player-row" style="padding:4px 6px; background:#a0b8d0;"><span id="expl-player-top" style="color:#445; font-weight:bold; font-size:0.85rem;">Noirs</span></div>
+      <div style="display:flex; align-items:stretch;">
+        <div class="coord-rank" id="expl-coord-rank"></div>
+        <div id="expl-board" style="display:grid; grid-template-columns:repeat(8,1fr);"></div>
+      </div>
+      <div class="coord-file" id="expl-coord-file" style="width:100%;"></div>
+      <div class="player-row" style="padding:4px 6px; background:#a0b8d0;"><span id="expl-player-bottom" style="color:#1a2a3a; font-weight:bold; font-size:0.85rem;">Blancs</span></div>
+    </div>
+
+    <div style="display:flex; gap:10px; margin-top:14px;">
+      <button id="expl-btn-prev" class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-top:0;" onclick="explPrev()" data-i18n="opening_explorer.btn.precedent">← Précédent</button>
+      <button id="expl-btn-next" class="btn btn-continuer" style="margin-top:0;" onclick="explNext()" data-i18n="opening_explorer.btn.suivant">Suivant →</button>
+    </div>
+  </div>
+
+  <!-- Colonne droite : explication + actions -->
+  <div style="display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px);">
+
+    <div class="card" style="padding:14px 16px;">
+      <h2 data-i18n="opening_explorer.h2.explication">EXPLICATION</h2>
+      <div id="explorer-explanation" style="font-size:0.85rem; color:#3a5a7a; line-height:1.5;"></div>
+    </div>
+
+    <div class="card" style="padding:14px 16px; display:flex; flex-direction:column; gap:8px;">
+      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0;" onclick="explBackToSelect()" data-i18n="opening_explorer.btn.autre">↩ Choisir une autre ouverture</button>
+      <button class="btn" style="background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0;" onclick="sendAction({type:'back_menu'})" data-i18n="common.retour_menu">← Retour au menu</button>
+    </div>
+
+  </div>
+</div>
+
+
 <!-- ── Écran connexion échiquier ── -->
 <div id="screen-connecting" style="display:none; flex:1; flex-direction:column; align-items:center; justify-content:center; gap:20px;">
   <div style="font-size:2rem;">♜</div>
