20cbcfc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 20cbcfc
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 17:14:34 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: tableau des coups candidats dans Opening Explorer (issue #144)
    
    - explorer_session.py : alternatives incluent le SAN (calculé depuis un
      board temporaire dépilé = position avant le coup joué) + champ
      main_move_uci ; fallback [coup joué] à 100% si la source ne fournit
      aucune alternative (PGNLineSource)
    - index.html : carte #explorer-moves-table dans la colonne droite
    - app.js : explRenderMovesTable() (barres de progression, coup joué en
      gras, 6 lignes max), appelée sur explorer_state, vidée dans explLoad()
    - i18n fr/en/de : opening_explorer.moves.titre

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/explorer_session.py b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 71d1d13..6e268be 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/explorer_session.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/explorer_session.py
# ── Zone modifiée : ligne 99 (15 ligne(s)) dans l'ancienne version → ligne 99 (31 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -99,15 +99,31 @@ class ExplorerSession:
         else:
             last_move_uci = None
             move_san      = None
+        # Les alternatives représentent les coups candidats DEPUIS la position
+        # avant le dernier coup joué (pour expliquer ce choix) — pas depuis la
+        # position courante. On rejoue donc sur un board temporaire dépilé.
         alternatives = []
         if self.source is not None:
             try:
-                alternatives = self.source.get_alternatives(self.board)
+                alt_board = self.board.copy()
+                if self._history:
+                    alt_board.pop()
+                for alt in self.source.get_alternatives(alt_board):
+                    try:
+                        san = san_ep(alt_board, chess.Move.from_uci(alt["uci"]))
+                    except Exception:
+                        san = alt["uci"]
+                    alternatives.append({"uci": alt["uci"], "san": san, "weight": alt.get("weight", 0)})
             except Exception:
                 alternatives = []
+        if not alternatives and last_move_uci is not None:
+            # Source sans alternatives (ex. PGNLineSource) : le coup joué
+            # reste la seule entrée du tableau, à 100%.
+            alternatives = [{"uci": last_move_uci, "san": move_san, "weight": 1}]
         return {
             "fen":            self.board.fen(),
             "last_move_uci":  last_move_uci,
+            "main_move_uci":  last_move_uci,
             "move_index":     len(self._history),
             "move_san":       move_san,
             "opening_name":   getattr(self.source, "nom", "") if self.source else "",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 8f841ab..05ef7c7 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 6138 (6 ligne(s)) dans l'ancienne version → ligne 6138 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6138,6 +6138,8 @@ function explRenderMesLignes(groupes) {
 function explLoad(sourceType, openingId) {
   const history = document.getElementById("explorer-chat-history");
   if (history) history.innerHTML = "";
+  const movesTable = document.getElementById("explorer-moves-table");
+  if (movesTable) movesTable.innerHTML = "";
   socket.emit("explorer_load", { source_type: sourceType, opening_id: openingId });
 }
 
# ── Zone modifiée : ligne 6188 (6 ligne(s)) dans l'ancienne version → ligne 6190 (52 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6188,6 +6190,52 @@ socket.on("explorer_chat_response", (data) => {
   history.scrollTop = history.scrollHeight;
 });
 
+function explRenderMovesTable(data) {
+  const wrap = document.getElementById("explorer-moves-table");
+  if (!wrap) return;
+  wrap.innerHTML = "";
+  const alternatives = (data && data.alternatives) || [];
+  if (!alternatives.length) return;
+
+  const title = document.createElement("h2");
+  title.textContent = t("opening_explorer.moves.titre");
+  wrap.appendChild(title);
+
+  const total = alternatives.reduce((sum, a) => sum + (a.weight || 0), 0) || 1;
+  const sorted = [...alternatives].sort((a, b) => (b.weight || 0) - (a.weight || 0));
+  const mainUci = data.main_move_uci || data.last_move_uci || null;
+
+  const table = document.createElement("div");
+  table.style.cssText = "display:flex; flex-direction:column; gap:6px; margin-top:8px;";
+  for (const alt of sorted.slice(0, 6)) {
+    const pct = Math.round(((alt.weight || 0) / total) * 100);
+    const isMain = mainUci !== null && alt.uci === mainUci;
+
+    const row = document.createElement("div");
+    row.style.cssText = "display:flex; align-items:center; gap:8px; font-size:0.82rem;";
+
+    const sanEl = document.createElement("div");
+    sanEl.style.cssText = `width:52px; flex-shrink:0; color:#1a2a3a; ${isMain ? "font-weight:700;" : ""}`;
+    sanEl.textContent = alt.san || alt.uci;
+    row.appendChild(sanEl);
+
+    const barWrap = document.createElement("div");
+    barWrap.style.cssText = "flex:1; background:#e8f0f8; border-radius:3px; height:6px; overflow:hidden;";
+    const bar = document.createElement("div");
+    bar.style.cssText = `background:#e94560; height:6px; border-radius:3px; width:${pct}%;`;
+    barWrap.appendChild(bar);
+    row.appendChild(barWrap);
+
+    const pctEl = document.createElement("div");
+    pctEl.style.cssText = "width:34px; flex-shrink:0; text-align:right; color:#3a5a7a;";
+    pctEl.textContent = `${pct}%`;
+    row.appendChild(pctEl);
+
+    table.appendChild(row);
+  }
+  wrap.appendChild(table);
+}
+
 socket.on("explorer_state", (data) => {
   if (!data) return;
   if (data.error) {
# ── Zone modifiée : ligne 6218 (6 ligne(s)) dans l'ancienne version → ligne 6266 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6218,6 +6266,7 @@ socket.on("explorer_state", (data) => {
 
   const [from, to] = uciToCoords(data.last_move_uci);
   explRenderBoard(data.fen, from, to);
+  explRenderMovesTable(data);
 
   _explAtStart   = !!data.at_start;
   _explEndOfLine = !!data.end_of_line;
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index 1eb6599..c6ea500 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 246 (6 ligne(s)) dans l'ancienne version → ligne 246 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -246,6 +246,7 @@
   "opening_explorer.btn.suivant": "Weiter →",
   "opening_explorer.btn.autre": "↩ Andere Eröffnung wählen",
   "opening_explorer.h2.explication": "ERKLÄRUNG",
+  "opening_explorer.moves.titre": "Buchzüge",
   "opening_explorer.explication.a_venir": "Die Zugerklärung wird hier bald verfügbar sein.",
   "opening_explorer.position_initiale": "Ausgangsstellung",
   "opening_explorer.coup_n": "Zug {n} — {san}",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index c0d6777..da9bc7e 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 246 (6 ligne(s)) dans l'ancienne version → ligne 246 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -246,6 +246,7 @@
   "opening_explorer.btn.suivant": "Next →",
   "opening_explorer.btn.autre": "↩ Choose another opening",
   "opening_explorer.h2.explication": "EXPLANATION",
+  "opening_explorer.moves.titre": "Book moves",
   "opening_explorer.explication.a_venir": "The move explanation will be available here soon.",
   "opening_explorer.position_initiale": "Starting position",
   "opening_explorer.coup_n": "Move {n} — {san}",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index bebe9e9..554b3ce 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 246 (6 ligne(s)) dans l'ancienne version → ligne 246 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -246,6 +246,7 @@
   "opening_explorer.btn.suivant": "Suivant →",
   "opening_explorer.btn.autre": "↩ Choisir une autre ouverture",
   "opening_explorer.h2.explication": "EXPLICATION",
+  "opening_explorer.moves.titre": "Coups du livre",
   "opening_explorer.explication.a_venir": "L'explication du coup sera disponible ici prochainement.",
   "opening_explorer.position_initiale": "Position initiale",
   "opening_explorer.coup_n": "Coup {n} — {san}",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index b61cdcb..fdd63d5 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1666 (6 ligne(s)) dans l'ancienne version → ligne 1666 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1666,6 +1666,10 @@
   <!-- Colonne droite : explication + actions -->
   <div style="display:flex; flex-direction:column; gap:10px; overflow-y:auto; max-height:calc(100vh - 60px);">
 
+    <div class="card" style="padding:14px 16px;">
+      <div id="explorer-moves-table"></div>
+    </div>
+
     <div class="card" style="padding:14px 16px;">
       <h2 data-i18n="opening_explorer.h2.explication">EXPLICATION</h2>
       <div id="explorer-explanation" style="font-size:0.85rem; color:#3a5a7a; line-height:1.5;"></div>
