586a7a2

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 586a7a2
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 09:33:25 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: #87 — bouton Coller PGN (menu Analyse), textarea + parsePgn()

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a14156c..537988f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 45 (6 ligne(s)) dans l'ancienne version → ligne 45 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -45,6 +45,11 @@
 
 ## ✅ Bugs résolus récemment
 
+### Session du 29 juillet
+
+Menu Analyse — bouton 📋 Coller PGN : zone textarea pour coller un PGN
+directement sans fichier intermédiaire, appelle parsePgn() existant. (issue #86)
+
 ### Session du 28 juillet
 
 Documentation Smart App Control Windows 11 ajoutée dans README.md et
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# (index — ignorable)
index 62804e7..56ff37f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/app.js
# (après — fichier suivant)
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 2213 (6 ligne(s)) dans l'ancienne version → ligne 2213 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2213,6 +2213,20 @@ function loadPgnFile(event) {
   reader.readAsText(file);
 }
 
+function toggleCollerPgn() {
+  const zone = document.getElementById('coller-pgn-zone');
+  zone.style.display = zone.style.display === 'none' ? 'block' : 'none';
+}
+
+function chargerPgnColle() {
+  const pgn = document.getElementById('coller-pgn-input').value.trim();
+  if (!pgn) { alert(t('error.pgn_vide') || 'Zone PGN vide.'); return; }
+  // Masquer la zone après chargement
+  document.getElementById('coller-pgn-zone').style.display = 'none';
+  document.getElementById('coller-pgn-input').value = '';
+  parsePgn(pgn);
+}
+
 function parsePgn(pgn) {
   try {
     const chess = new Chess();
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index 8d81bd7..af20a5d 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 401 (6 ligne(s)) dans l'ancienne version → ligne 401 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -401,6 +401,8 @@
 
   "analyse.titre":             "Partieanalyse",
   "analyse.importer_pgn":      "Eine PGN-Datei importieren",
+  "analyse.btn.coller_pgn":    "📋 PGN einfügen",
+  "analyse.btn.charger_pgn_colle": "✅ Laden",
 
   "config.joueur1":            "Spieler 1",
   "config.joueur2":            "Spieler 2",
# ── Zone modifiée : ligne 420 (6 ligne(s)) dans l'ancienne version → ligne 422 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -420,6 +422,7 @@
   "exercices.cliquer_jouer_virtuel": "Auf Ihre Figuren klicken zum Spielen.",
 
   "error.pgn_non_reconnu":     "Ungültiges oder nicht erkanntes PGN.",
+  "error.pgn_vide":            "Der PGN-Bereich ist leer.",
   "error.board.deconnecte":    "Brett getrennt oder ausgeschaltet. Programm neu starten.",
 
   "game.pause_info":           "{player} spielt {color}",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index 76abd55..888aaeb 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 401 (6 ligne(s)) dans l'ancienne version → ligne 401 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -401,6 +401,8 @@
 
   "analyse.titre":             "Game analysis",
   "analyse.importer_pgn":      "Import a PGN file",
+  "analyse.btn.coller_pgn":    "📋 Paste PGN",
+  "analyse.btn.charger_pgn_colle": "✅ Load",
 
   "config.joueur1":            "Player 1",
   "config.joueur2":            "Player 2",
# ── Zone modifiée : ligne 420 (6 ligne(s)) dans l'ancienne version → ligne 422 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -420,6 +422,7 @@
   "exercices.cliquer_jouer_virtuel": "Click on your pieces to play.",
 
   "error.pgn_non_reconnu":     "Invalid or unrecognised PGN.",
+  "error.pgn_vide":            "PGN area is empty.",
   "error.board.deconnecte":    "Board disconnected or off. Restart the program.",
 
   "game.pause_info":           "{player} plays {color}",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index 626e7a7..5f2154f 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 401 (6 ligne(s)) dans l'ancienne version → ligne 401 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -401,6 +401,8 @@
 
   "analyse.titre":             "Analyse de partie",
   "analyse.importer_pgn":      "Importez un fichier PGN",
+  "analyse.btn.coller_pgn":    "📋 Coller PGN",
+  "analyse.btn.charger_pgn_colle": "✅ Charger",
 
   "config.joueur1":            "Joueur 1",
   "config.joueur2":            "Joueur 2",
# ── Zone modifiée : ligne 420 (6 ligne(s)) dans l'ancienne version → ligne 422 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -420,6 +422,7 @@
   "exercices.cliquer_jouer_virtuel": "Cliquez sur vos pièces pour jouer.",
 
   "error.pgn_non_reconnu":     "PGN invalide ou non reconnu.",
+  "error.pgn_vide":            "La zone PGN est vide.",
   "error.board.deconnecte":    "Échiquier déconnecté ou éteint. Relancez le programme.",
 
   "game.pause_info":           "{player} joue les {color}",
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index e4c3039..b70dcdc 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 671 (6 ligne(s)) dans l'ancienne version → ligne 671 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -671,6 +671,12 @@
       <div class="card" style="padding:14px 18px; display:flex; flex-direction:column; gap:8px;">
         <input type="file" id="pgn-file-input" accept=".pgn" style="display:none" onchange="loadPgnFile(event)">
         <button class="btn btn-best"      style="margin-bottom:0;" onclick="document.getElementById('pgn-file-input').click()" data-i18n="labo.btn.importer_pgn">📂 Importer PGN</button>
+        <!-- Coller PGN directement -->
+        <button class="btn btn-best" style="margin-bottom:0;" onclick="toggleCollerPgn()" data-i18n="analyse.btn.coller_pgn">📋 Coller PGN</button>
+        <div id="coller-pgn-zone" style="display:none; margin-top:8px;">
+          <textarea id="coller-pgn-input" rows="8" style="width:100%; font-family:monospace; font-size:12px; resize:vertical;" placeholder="Collez ici le contenu PGN..."></textarea>
+          <button class="btn btn-reprendre" style="margin-top:4px; margin-bottom:0; width:100%;" onclick="chargerPgnColle()" data-i18n="analyse.btn.charger_pgn_colle">✅ Charger</button>
+        </div>
         <!-- Classeur de session -->
         <div id="basket-row-analyse" style="display:flex; gap:6px; align-items:stretch;">
           <span class="aide-panier-icone" onclick="ouvrirAidePanier()" data-i18n-title="aide.panier.icone_title" title="Aide sur le classeur">?</span>
