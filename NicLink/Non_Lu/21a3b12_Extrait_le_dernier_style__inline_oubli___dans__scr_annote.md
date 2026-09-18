21a3b12

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 21a3b12
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 24 18:23:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait le dernier style= inline oublié dans #screen-config (colonne Moteur+Options) vers .cfg-ped-col-moteur (issue #249)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d239fe5..8428c1f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/css/main.css
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 513 (6 ligne(s)) dans l'ancienne version → ligne 513 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -513,6 +513,13 @@
     .cfg-ped-card-joueur .color-btns { margin-bottom: 0; }
     .cfg-ped-card-pause  { padding: 14px 16px; grid-column: 1; grid-row: 2; }
     .cfg-ped-card-pause .cfg-input { margin-bottom: 0; }
+    .cfg-ped-col-moteur {
+      display: flex;
+      flex-direction: column;
+      gap: 12px;
+      grid-column: 2;
+      grid-row: 1 / span 2;
+    }
     .cfg-ped-footer {
       width: 100%;
       background: #c2d4e8;
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 6ce9c6f..e6396b4 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 244 (7 ligne(s)) dans l'ancienne version → ligne 244 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -244,7 +244,7 @@
       </div>
 
       <!-- Col 2 : Moteur + Options (wrapper flex) -->
-      <div style="display:flex; flex-direction:column; gap:12px; grid-column:2; grid-row:1 / span 2;">
+      <div class="cfg-ped-col-moteur">
 
         <div class="card cfg-engine-card">
           <h2 data-i18n="config.moteur">Moteur</h2>
