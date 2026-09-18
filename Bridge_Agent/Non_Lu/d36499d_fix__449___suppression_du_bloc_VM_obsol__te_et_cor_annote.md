d36499d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d36499d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 12:37:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #449 : suppression du bloc VM obsolète et correction texte token SCP (onglet CCW)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/templates/index.html b/templates/index.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e6335ea..d82fd38 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/templates/index.html
# ── Version APRÈS ce commit.
+++ b/templates/index.html
# ── Zone modifiée : ligne 389 (23 ligne(s)) dans l'ancienne version → ligne 389 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -389,23 +389,9 @@
     </div>
   </div>
 
-  <!-- ─── Onglet CCW : pilotage de la VM Windows et de ses projets (issue #174) ─ -->
+  <!-- ─── Onglet CCW : pilotage du PC fixe Windows et de ses projets (issue #174) ─ -->
   <div id="panneau-ccw" class="panneau">
 
-    <!-- Section 1 : état + démarrage de la VM -->
-    <div class="titre-section">Machine virtuelle CCW-Build</div>
-    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;
-         padding:8px 12px;background:#f8f8f5;border:1px solid #e0dfda;border-radius:6px">
-      <span id="ccw-dot-vm" style="width:9px;height:9px;border-radius:50%;
-            background:#ccc;flex-shrink:0"></span>
-      <span id="ccw-etat-vm" style="font-size:13px;color:#666">Vérification…</span>
-      <div style="margin-left:auto;display:flex;gap:8px">
-        <button id="ccw-btn-demarrer" onclick="ccwDemarrerVm()"
-                style="display:none">Démarrer (headless)</button>
-        <button onclick="ccwRafraichirVm()">Rafraîchir</button>
-      </div>
-    </div>
-
     <!-- Section 2 : projets CCW existants -->
     <div class="titre-section" style="display:flex;align-items:center">
       <span>Projets CCW existants</span>
# ── Zone modifiée : ligne 493 (8 ligne(s)) dans l'ancienne version → ligne 479 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -493,8 +479,8 @@
     </div>
     <div style="font-size:12px;color:#999;margin-bottom:8px">
       🔒 Les tokens ne transitent jamais en argument de commande ni dans un log :
-      fichier temporaire poussé dans la VM, lu par PowerShell, puis supprimé des
-      deux côtés. Créez d'abord le token GitHub dédié (repo unique, Issues R/W,
+      fichier temporaire poussé sur le PC fixe via SCP, lu par PowerShell, puis
+      supprimé des deux côtés. Créez d'abord le token GitHub dédié (repo unique, Issues R/W,
       expiration alignée — cf. §16).
     </div>
     <div class="barre-envoi">
