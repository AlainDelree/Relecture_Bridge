8b7fec9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8b7fec9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 12:53:14 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #455 : nettoyage cosmétique PC physique (eval-expiration.json, provisionner.ps1, BRIDGE_AGENT_DOC.md)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a2d1ecc..2ffd650 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1147 (7 ligne(s)) dans l'ancienne version → ligne 1147 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1147,7 +1147,7 @@ create`, puis surveille sa fermeture avant de livrer sa réponse.
 - **⚠️ Contrepartie opérationnelle** : le rallumage automatique du watcher à
   la création d'issue (§13, mécanisme 2) ne s'applique PAS aux issues
   `for-windows`. Avant d'envoyer une issue `for-windows` directe, vérifier
-  dans l'onglet CCW (§16.2) que la VM `CCW-Build` tourne et que le service
+  dans l'onglet CCW (§16.2) que le PC fixe est joignable et que le service
   `CCW-Watcher` est démarré ; sinon l'issue restera ouverte sans aucun
   signal. (Le nom `CCW-Watcher-<Projet>` venait du modèle multi-projets,
   abandonné par #231 — voir §16.)
# (diff du fichier suivant)
diff --git a/provisioning/windows/eval-expiration.json b/provisioning/windows/eval-expiration.json
# (index — ignorable)
index ccbb944..f20218a 100644
# (avant — fichier suivant)
--- a/provisioning/windows/eval-expiration.json
# (après — fichier suivant)
+++ b/provisioning/windows/eval-expiration.json
# ── Zone modifiée : ligne 1 (6 ligne(s)) dans l'ancienne version → ligne 1 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,6 +1,6 @@
 {
   "_commentaire": "Métadonnées de l'évaluation 90 jours de la VM CCW-Build (Windows 11 IoT Enterprise LTSC 2024). Lu par verifier_expiration_ccw.py. Voir BRIDGE_AGENT_DOC.md §16 et issue #167.",
-  "vm": "CCW-Build",
+  "machine": "PC-fixe-CCW",
   "windows": "Windows 11 IoT Enterprise LTSC 2024",
   "eval_jours": 90,
   "date_installation": "2026-08-17",
# (diff du fichier suivant)
diff --git a/provisioning/windows/provisionner.ps1 b/provisioning/windows/provisionner.ps1
# (index — ignorable)
index 2979cfa..9deec66 100644
# (avant — fichier suivant)
--- a/provisioning/windows/provisionner.ps1
# (après — fichier suivant)
+++ b/provisioning/windows/provisionner.ps1
# ── Zone modifiée : ligne 129 (12 ligne(s)) dans l'ancienne version → ligne 129 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -129,12 +129,12 @@ function Installer-Winget($id, $nom) {
 #     https://learn.microsoft.com/windows/apps/windows-app-sdk/deploy-unpackaged-apps
 #
 #   Cache : MÊME pattern que le msixbundle (issue #158) — sous-dossier dédié du
-#   partage CCW_Share (\\VBOXSVR\CCW_Share\cache\windows-app-runtime\), réutilisé
+#   partage CCW_Share (C:\CCW_Share\cache\windows-app-runtime\), réutilisé
 #   si présent, peuplé sinon. Idempotent : si les paquets sont déjà là,
 #   l'installeur ne fait rien. Pour forcer une nouvelle version : VIDER le cache.
 # ---------------------------------------------------------------------------
 function Install-WindowsAppRuntime {
-    $cacheDir   = '\\VBOXSVR\CCW_Share\cache\windows-app-runtime'
+    $cacheDir   = 'C:\CCW_Share\cache\windows-app-runtime'
     $exeName    = 'WindowsAppRuntimeInstall-x64.exe'
     $cacheExe   = Join-Path $cacheDir $exeName
     # Runtime x64, dernière 1.8 stable vérifiée le 2026-07-19 (voir commentaire ci-dessus).
# ── Zone modifiée : ligne 223 (17 ligne(s)) dans l'ancienne version → ligne 223 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -223,17 +223,17 @@ function Bootstrap-Winget {
     # -----------------------------------------------------------------------
     # CACHE PERSISTANT du msixbundle + licence (issue #158, suite #152).
     #
-    #   Le partage CCW_Share (\\VBOXSVR\CCW_Share, monté en phase 1) vit côté
-    #   hôte Linux et SURVIT aux resets/redémarrages de la VM : c'est un
-    #   emplacement de cache idéal. Le téléchargement du msixbundle est la
-    #   partie la plus longue du bootstrap ; le mettre en cache évite de le
-    #   retélécharger à chaque test rapproché de lancer_provisioning.py.
+    #   Le partage CCW_Share (C:\CCW_Share, local au PC fixe) SURVIT aux
+    #   redémarrages : c'est un emplacement de cache idéal. Le téléchargement
+    #   du msixbundle est la partie la plus longue du bootstrap ; le mettre en
+    #   cache évite de le retélécharger à chaque test rapproché de
+    #   lancer_provisioning.py.
     #
     #   PAS d'invalidation automatique (aucune vérification de version) : pour
     #   forcer un nouveau téléchargement (nouvelle version d'App Installer), il
     #   suffit de VIDER MANUELLEMENT le dossier de cache ci-dessous.
     # -----------------------------------------------------------------------
-    $cacheDir   = '\\VBOXSVR\CCW_Share\cache\winget-bootstrap'
+    $cacheDir   = 'C:\CCW_Share\cache\winget-bootstrap'
     $msixName   = 'Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle'
     $cacheMsix  = Join-Path $cacheDir $msixName
 
