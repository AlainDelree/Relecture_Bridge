15d8188

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 15d8188
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 22:53:53 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #107 — schéma SVG en position absolute hors du flex menu-grid

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3e835b1..cde0013 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/css/main.css
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 128 (6 ligne(s)) dans l'ancienne version → ligne 128 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -128,6 +128,9 @@
       gap: 20px;
       padding: 40px 20px;
     }
+    #screen-menu {
+      position: relative;
+    }
     #screen-config {
       justify-content: flex-start;
       padding: 0;
# ── Zone modifiée : ligne 164 (12 ligne(s)) dans l'ancienne version → ligne 167 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -164,12 +167,13 @@
 
     /* ── Schéma connexion ordinateur-échiquier (écran menu) ── */
     .schema-connexion {
-      position: relative;
+      position: absolute;
+      left: 20px;
+      top: 0;
       display: none;
       justify-content: center;
       width: 60px;
       flex-shrink: 0;
-      margin-right: 8px;
     }
     .schema-connexion svg {
       width: 100%;
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 5e350fb..b8754cf 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 46 (9 ligne(s)) dans l'ancienne version → ligne 46 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -46,9 +46,6 @@
 
 <!-- ── Écran menu ── -->
 <div id="screen-menu">
-  <div class="menu-title"><span style="font-size:1.3em; line-height:1;">♜</span> AlChess</div>
-
-  <div style="display:flex; align-items:flex-start; justify-content:center;">
   <!-- ── Schéma connexion ordinateur-échiquier ── -->
   <div class="schema-connexion" id="schema-connexion">
     <svg viewBox="0 0 50 200" width="100%" height="100%" aria-hidden="true">
# ── Zone modifiée : ligne 116 (6 ligne(s)) dans l'ancienne version → ligne 113 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -116,6 +113,9 @@
     <button class="btn-connecter" id="btn-connecter" onclick="sendAction({type:'reconnect_board'})" data-i18n="menu.btn.connecter">⟳ Connecter</button>
   </div>
 
+  <div class="menu-title"><span style="font-size:1.3em; line-height:1;">♜</span> AlChess</div>
+
+  <div style="display:flex; align-items:flex-start; justify-content:center;">
   <div class="menu-grid">
 
     <!-- ── Colonne GAUCHE : Jouer ── -->
# ── Zone modifiée : ligne 193 (7 ligne(s)) dans l'ancienne version → ligne 193 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -193,7 +193,7 @@
     </div><!-- fin colonne Outils -->
 
   </div><!-- fin menu-grid -->
-  </div><!-- fin flex schema+menu-grid -->
+  </div><!-- fin flex menu-grid -->
 
   <button class="menu-btn" onclick="ouvrirModal('quit', t('modal.quitter_alchess'), t('modal.quitter_btn'), 'btn-warning')" style="background:#b8cce0; color:#555; border:1px solid #333; font-size:0.85rem; margin-top:8px;" data-i18n="menu.btn.quitter">✕ Quitter</button>
 
