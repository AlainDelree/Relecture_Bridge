cb0db42

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit cb0db42
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Sat Sep 12 01:04:01 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #529 : rappel permissions GH_TOKEN quand dépôt privé choisi (CLI + web)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nouveau_projet.py b/nouveau_projet.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a0ae19f..1bdcad0 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nouveau_projet.py
# ── Version APRÈS ce commit.
+++ b/nouveau_projet.py
# ── Zone modifiée : ligne 637 (6 ligne(s)) dans l'ancienne version → ligne 637 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -637,6 +637,11 @@ def etape_depot(nom: str) -> tuple[str, bool]:
         sys.exit(1)
 
     public = demander_oui_non("Dépôt public (non = privé)", defaut=True)
+    if not public:
+        print("   ⚠️  Dépôt privé : vérifier que GH_TOKEN dispose des "
+              "permissions nécessaires sur ce dépôt, sinon la création "
+              "ci-dessous — ou un appel gh/git ultérieur (issues, push) — "
+              "échouera avec une erreur d'authentification.")
 
     print(f"   Création de {depot} ({'public' if public else 'privé'})…")
     ok, err = creer_depot(depot, nom, public=public)
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 4e3d826..1a902e7 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 5460 (6 ligne(s)) dans l'ancienne version → ligne 5460 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5460,6 +5460,7 @@ function ouvrirNouveauProjet() {
   document.getElementById('np-creer-depot-ligne').style.display = 'none';
   document.getElementById('np-public').checked = true;
   document.getElementById('np-public-ligne').style.display = 'none';
+  document.getElementById('np-avertissement-prive').style.display = 'none';
   document.getElementById('np-nom-msg').textContent = '';
   document.getElementById('np-depot-msg').textContent = '';
   document.getElementById('np-compte-rendu').style.display = 'none';
# ── Zone modifiée : ligne 5592 (6 ligne(s)) dans l'ancienne version → ligne 5593 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5592,6 +5593,7 @@ function npAfficherEtatDepot(r) {
     depotMsg.textContent = '';
     ligneCreer.style.display = 'none';
     lignePublic.style.display = 'none';
+    document.getElementById('np-avertissement-prive').style.display = 'none';
     return;
   }
   if (r.depot_existe) {
# ── Zone modifiée : ligne 5599 (14 ligne(s)) dans l'ancienne version → ligne 5601 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5599,14 +5601,23 @@ function npAfficherEtatDepot(r) {
     depotMsg.style.color = '#2e7d32';
     ligneCreer.style.display = 'none';
     lignePublic.style.display = 'none';
+    document.getElementById('np-avertissement-prive').style.display = 'none';
   } else {
     depotMsg.textContent = 'ℹ ' + r.depot + " n'existe pas encore.";
     depotMsg.style.color = '#8a6d00';
     ligneCreer.style.display = 'block';
     lignePublic.style.display = 'block';
+    npMajAvertissementPrive();
   }
 }
 
+// Affiche le rappel GH_TOKEN sous la case publique/privée : visible
+// uniquement quand un dépôt privé est choisi (case décochée) — issue #529.
+function npMajAvertissementPrive() {
+  document.getElementById('np-avertissement-prive').style.display =
+    document.getElementById('np-public').checked ? 'none' : 'block';
+}
+
 function npMsg(texte, type) {
   const el = document.getElementById('np-message');
   el.textContent = texte;
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 6097b19..733af1c 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 610 (10 ligne(s)) dans l'ancienne version → ligne 610 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -610,10 +610,16 @@
     </label>
 
     <label id="np-public-ligne"
-           style="display:none;font-size:13px;color:#333;margin-bottom:12px">
-      <input type="checkbox" id="np-public" checked>
+           style="display:none;font-size:13px;color:#333;margin-bottom:4px">
+      <input type="checkbox" id="np-public" checked onchange="npMajAvertissementPrive()">
       Dépôt public (décocher pour un dépôt privé)
     </label>
+    <div id="np-avertissement-prive"
+         style="display:none;font-size:12px;color:#8a6d00;margin:0 0 12px 24px">
+      ⚠ Dépôt privé : GH_TOKEN doit avoir les permissions nécessaires sur ce
+      dépôt, sinon la création ci-dessous — ou un appel ultérieur (issues,
+      push) — échouera.
+    </div>
 
     <div class="champ" style="margin-bottom:12px">
       <label>Répertoire de travail CCL</label>
