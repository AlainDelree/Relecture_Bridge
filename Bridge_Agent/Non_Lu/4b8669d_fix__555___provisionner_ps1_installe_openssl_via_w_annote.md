4b8669d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4b8669d
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 16:38:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #555 : provisionner.ps1 installe openssl via winget (ShiningLight.OpenSSL.Light) au lieu de dépendre de l'hypothèse invalidée d'un embarquement par Git pour Windows
    
    Hypothèse #553 fausse en conditions réelles sur CCW (22/07/2026) : usr\bin
    n'existe pas dans cette installation de Git pour Windows, seulement des DLL
    internes à git.exe. Resoudre-OpenSSL cherche désormais le binaire installé
    par le paquet winget (même éditeur/installeur que le contournement manuel
    qui a débloqué le test) au chemin par défaut C:\Program
    Files\OpenSSL-Win64\bin\openssl.exe, et complète le PATH Machine de
    façon persistante puisque cet installeur ne le fait pas automatiquement
    (nécessaire pour un futur déchiffrement dans watcher.py, #556). Idempotence
    d'Assurer-ClesBootstrap inchangée. Commentaire de justification du choix
    technique réécrit pour refléter la contrainte réelle.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/provisioning/windows/provisionner.ps1 b/provisioning/windows/provisionner.ps1
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 742fe53..7be00ae 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/provisioning/windows/provisionner.ps1
# ── Version APRÈS ce commit.
+++ b/provisioning/windows/provisionner.ps1
# ── Zone modifiée : ligne 15 (7 ligne(s)) dans l'ancienne version → ligne 15 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -15,7 +15,7 @@
   n'a plus lieu d'être sur le PC physique : lancement manuel uniquement.
 
   Ce qu'il fait :
-    1. installe via winget : Git, GitHub CLI (gh), Python 3, NSSM ;
+    1. installe via winget : Git, GitHub CLI (gh), Python 3, NSSM, OpenSSL ;
     2. installe pyinstaller (pip) — requis pour les builds .exe délégués ;
     3. installe Claude Code via l'installeur natif officiel (pas de Node.js) :
          irm https://claude.ai/install.ps1 | iex
# ── Zone modifiée : ligne 384 (10 ligne(s)) dans l'ancienne version → ligne 384 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -384,10 +384,16 @@ if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
     throw "winget introuvable malgré le bootstrap : App Installer indisponible. Abandon."
 }
 
-Installer-Winget 'Git.Git'            'Git'
-Installer-Winget 'GitHub.cli'         'GitHub CLI (gh)'
-Installer-Winget 'Python.Python.3.12' 'Python 3'
-Installer-Winget 'NSSM.NSSM'          'NSSM'
+Installer-Winget 'Git.Git'                'Git'
+Installer-Winget 'GitHub.cli'             'GitHub CLI (gh)'
+Installer-Winget 'Python.Python.3.12'     'Python 3'
+Installer-Winget 'NSSM.NSSM'              'NSSM'
+# ShiningLight.OpenSSL.Light = même éditeur/installeur (Shining Light Productions,
+# Win64 OpenSSL Light, slproweb.com) que celui utilisé à la main pour débloquer le
+# test empirique de l'issue #555 — juste automatisé via winget plutôt qu'un
+# installeur téléchargé/lancé manuellement. Voir Resoudre-OpenSSL plus bas pour la
+# justification complète (le paquet n'ajoute PAS openssl au PATH automatiquement).
+Installer-Winget 'ShiningLight.OpenSSL.Light' 'OpenSSL'
 
 # Rafraîchir le PATH de la session pour voir git/gh/python fraîchement installés.
 $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
# ── Zone modifiée : ligne 431 (19 ligne(s)) dans l'ancienne version → ligne 437 (55 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -431,19 +437,55 @@ if (Test-Path (Join-Path $RepDepot '.git')) {
 #    en dur. La clé PRIVÉE ne quitte jamais cette machine ; la clé PUBLIQUE
 #    n'est pas sensible et doit être récupérable côté CCL pour chiffrer.
 #
-#    Choix technique : RSA 3072 bits en PEM, généré via openssl.exe — déjà
-#    disponible sans installation supplémentaire puisque Git pour Windows
-#    (étape 1 winget ci-dessus) l'embarque dans son sous-dossier usr\bin
-#    (couche MSYS/MinGW). Écarté : .NET natif
-#    (System.Security.Cryptography), dont les méthodes d'export PEM
-#    (ExportPkcs8PrivateKey / ExportSubjectPublicKeyInfo) ne sont disponibles
-#    qu'à partir de .NET 5+ — absentes de Windows PowerShell 5.1 (.NET
-#    Framework) utilisé par défaut sur ce PC, ce qui aurait exigé de
-#    reconstruire l'encodage ASN.1/DER à la main. Écarté aussi : `age`, pour
-#    éviter d'imposer une dépendance winget supplémentaire alors qu'openssl
-#    est déjà présent de facto. Le format PEM (norme ouverte, contrairement
-#    au XML natif .NET) reste directement exploitable côté CCL (Python) pour
-#    le chiffrement à venir en #555.
+#    Choix technique : RSA 3072 bits en PEM, généré via openssl.exe.
+#
+#    ATTENTION — hypothèse initiale INVALIDÉE empiriquement (issue #555) :
+#    contrairement à ce qui était supposé ici, Git pour Windows n'embarque PAS
+#    forcément openssl.exe dans un sous-dossier usr\bin. Constaté sur
+#    l'installation CCW du 22/07/2026 : ce dossier usr\bin n'existe même pas —
+#    seules des DLL internes à git.exe (libssl-3-x64.dll, libcrypto-3-x64.dll,
+#    dans mingw64\libexec\git-core) sont présentes, pas de binaire autonome.
+#    La présence d'openssl.exe dépend donc de la version/variante de Git pour
+#    Windows installée, ce qui n'est pas une base fiable pour un script de
+#    provisioning rejoué à chaque réinstallation complète.
+#
+#    Solution retenue : installer OpenSSL comme paquet winget à part entière
+#    (ShiningLight.OpenSSL.Light, étape 1 ci-dessus) plutôt que de dépendre
+#    d'un embarquement accessoire de Git. Justification du choix :
+#      • même éditeur/installeur (Shining Light Productions, Win64 OpenSSL
+#        Light, slproweb.com) que celui déjà validé À LA MAIN pour débloquer
+#        le test de #555 — pas un nouveau binaire à faire confiance, juste son
+#        déploiement automatisé ;
+#      • réutilise l'infrastructure winget déjà en place et déjà bootstrappée
+#        plus haut pour Git/gh/Python/NSSM (Bootstrap-Winget) — pas de
+#        dépendance en cascade supplémentaire propre à LTSC/IoT (le bootstrap
+#        de winget lui-même, seul point qui aurait de telles dépendances en
+#        cascade — msixbundle, Windows App Runtime —, est déjà fait à ce
+#        stade du script) ;
+#      • évite d'introduire un NOUVEAU pattern de cache de binaire téléchargé
+#        (C:\CCW_Share\cache\…) avec un lien figé à re-vérifier à chaque
+#        évolution (pattern déjà jugé fragile pour Windows App Runtime,
+#        cf. commentaire plus haut) — winget gère lui-même la résolution de
+#        version et la vérification de l'installeur.
+#    CONSTAT IMPORTANT (issue #555) : cet installeur, comme à la main,
+#    N'AJOUTE PAS openssl au PATH automatiquement. Resoudre-OpenSSL (ci-dessous)
+#    gère donc explicitement ce cas : détection du chemin d'installation par
+#    défaut (C:\Program Files\OpenSSL-Win64\bin\openssl.exe) puis ajout
+#    PERSISTANT (PATH Machine, pas seulement la session) — nécessaire pour
+#    qu'un futur traitement de déchiffrement dans watcher.py (#556) retrouve
+#    openssl sans dépendre de la session interactive qui a lancé ce script.
+#
+#    Écarté : .NET natif (System.Security.Cryptography), dont les méthodes
+#    d'export PEM (ExportPkcs8PrivateKey / ExportSubjectPublicKeyInfo) ne sont
+#    disponibles qu'à partir de .NET 5+ — confirmé absentes de Windows
+#    PowerShell 5.1 (.NET Framework), seule version actuellement en place sur
+#    CCW, ce qui aurait exigé soit de reconstruire l'encodage ASN.1/DER à la
+#    main, soit d'installer PowerShell 7+/.NET 5+ en supplément — pas plus
+#    simple que d'ajouter un seul paquet winget déjà validé par ailleurs.
+#    Écarté aussi : `age`, pour éviter d'imposer une dépendance
+#    supplémentaire alors qu'openssl (via winget) couvre déjà le besoin. Le
+#    format PEM (norme ouverte, contrairement au XML natif .NET) reste
+#    directement exploitable côté CCL (Python) pour le chiffrement à venir.
 #
 #    Stockage : C:\CCW\cles_bootstrap\, un dossier LOCAL au PC fixe, frère de
 #    $RepDepot mais HORS du clone git (jamais committé) et hors de
# ── Zone modifiée : ligne 464 (20 ligne(s)) dans l'ancienne version → ligne 506 (33 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -464,20 +506,33 @@ function Resoudre-OpenSSL {
     $cmd = Get-Command openssl -ErrorAction SilentlyContinue
     if ($cmd) { return $cmd.Source }
 
-    # Pas sur le PATH : Git pour Windows l'embarque quand même dans son
-    # sous-dossier usr\bin (couche MSYS/MinGW), déjà installé à l'étape 1.
-    try {
-        $execPath  = (git --exec-path).Trim()
-        $racineGit = Split-Path (Split-Path $execPath -Parent) -Parent
-        $candidat  = Join-Path $racineGit 'usr\bin\openssl.exe'
-        if (Test-Path $candidat) { return $candidat }
-    } catch {
-        # Ignoré : on tombe sur l'erreur explicite ci-dessous.
+    # Pas sur le PATH : le paquet winget ShiningLight.OpenSSL.Light (étape 1
+    # ci-dessus) installe openssl.exe SANS l'ajouter au PATH automatiquement
+    # (constaté à la main puis via winget, issue #555) — chemin d'installation
+    # par défaut de cet installeur (Shining Light Productions, Win64 OpenSSL
+    # Light) :
+    $candidat = Join-Path $env:ProgramFiles 'OpenSSL-Win64\bin\openssl.exe'
+    if (Test-Path $candidat) {
+        # Complète le PATH Machine de façon PERSISTANTE (pas seulement la
+        # session courante) : un futur traitement de déchiffrement dans
+        # watcher.py (#556), lancé par le service NSSM dans une session
+        # distincte, doit retrouver openssl sans dépendre de ce script.
+        $dossierBin  = Split-Path $candidat -Parent
+        $pathMachine = [System.Environment]::GetEnvironmentVariable('Path', 'Machine')
+        if (($pathMachine -split ';') -notcontains $dossierBin) {
+            Info "Ajout de $dossierBin au PATH Machine (persistant) pour openssl…"
+            [System.Environment]::SetEnvironmentVariable('Path', "$pathMachine;$dossierBin", 'Machine')
+        }
+        # Rafraîchit le PATH de la session courante pour l'usage immédiat ci-dessous.
+        $env:Path = [System.Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
+                    [System.Environment]::GetEnvironmentVariable('Path', 'User')
+        return $candidat
     }
 
-    throw ("openssl introuvable (ni sur le PATH, ni dans le sous-dossier " +
-           "usr\bin de Git) — impossible de générer la paire de clés de " +
-           "bootstrap. Vérifier l'installation de Git (étape 1).")
+    throw ("openssl introuvable (ni sur le PATH, ni dans le dossier d'installation " +
+           "par défaut de ShiningLight.OpenSSL.Light : $candidat) — impossible de " +
+           "générer la paire de clés de bootstrap. Vérifier l'installation winget " +
+           "à l'étape 1 (winget list --id ShiningLight.OpenSSL.Light).")
 }
 
 function Assurer-ClesBootstrap {
