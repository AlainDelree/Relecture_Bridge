0c89f59

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0c89f59
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 16:08:45 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #554 (1/3) : génération de la paire de clés RSA 3072 pour le chiffrement
    des tokens de bootstrap « Projet CCW »
    
    provisionner.ps1 génère désormais (idempotent, une fois par cycle de vie de
    la machine) une paire de clés RSA 3072 bits en PEM via openssl.exe (déjà
    embarqué par Git pour Windows, usr\bin — choix justifié en commentaire :
    écarte .NET natif dont l'export PEM manque en PowerShell 5.1/.NET Framework,
    et age pour ne pas ajouter de dépendance winget). Clé privée stockée dans
    C:\CCW\cles_bootstrap\ (hors clone git, hors C:\CCW_Share), permissions
    restreintes via icacls (SYSTEM + Administrateurs + compte de service en
    lecture). Clé publique affichée en fin de script pour copier-coller, et
    récupérable via la session SSH existante (§16.2).
    
    REINSTALLATION_CCW.md : nouvelle étape 8 documentant le mécanisme, avec
    rappel explicite que la clé privée ne survit pas à une réinstallation et
    qu'une issue de bootstrap chiffrée non traitée à ce moment-là devient
    indéchiffrable.
    
    Déchiffrement côté watcher.py et chiffrement côté formulaire non traités
    ici — suite en #555/#556.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/provisioning/windows/REINSTALLATION_CCW.md b/provisioning/windows/REINSTALLATION_CCW.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b1e7f37..2d047b0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/provisioning/windows/REINSTALLATION_CCW.md
# ── Version APRÈS ce commit.
+++ b/provisioning/windows/REINSTALLATION_CCW.md
# ── Zone modifiée : ligne 64 (7 ligne(s)) dans l'ancienne version → ligne 64 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -64,7 +64,8 @@ précédente) :
 
 Installe Git, GitHub CLI, Python 3, PyInstaller (winget) et Claude Code
 (installeur natif), clone `Bridge_Agent` en lecture seule dans
-`C:\CCW\Bridge_Agent`, écrit `configs\ccw.conf` (avec un placeholder
+`C:\CCW\Bridge_Agent`, génère la paire de clés de bootstrap « Projet CCW »
+(voir étape 8 ci-dessous), écrit `configs\ccw.conf` (avec un placeholder
 `TOPIC_NTFY`) et enregistre le service Windows `CCW-Watcher` via NSSM.
 
 ### 5. Renseigner le topic ntfy et poser les tokens
# ── Zone modifiée : ligne 129 (6 ligne(s)) dans l'ancienne version → ligne 130 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -129,6 +130,51 @@ Vérifier ensuite l'état des 5 services (base + 4 dédiés) via
 `provisioning\windows\lister_projets_ccw.ps1`, ou depuis CCL via l'onglet
 **CCW** de l'interface web.
 
+### 8. Paire de clés de bootstrap « Projet CCW » (issue #554, 1/3)
+
+`provisionner.ps1` (étape 4 ci-dessus) génère automatiquement, la première
+fois, une paire de clés **RSA 3072 bits** destinée au futur chiffrement des
+tokens (`GH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`) transmis par la case
+« Projet CCW » du formulaire de création de projet (conception #554,
+mécanisme complet à suivre en #555/#556 — **pas encore implémenté à ce
+stade** : cette étape ne fait que poser la paire de clés elle-même).
+
+- **Clé privée** : `C:\CCW\cles_bootstrap\bootstrap_privee.pem` — ne quitte
+  **jamais** le PC fixe. Permissions restreintes par `icacls` (SYSTEM +
+  Administrateurs + le compte de service `AlainW` en lecture seule),
+  héritage coupé. Ce dossier est volontairement **hors** du clone git
+  `C:\CCW\Bridge_Agent` (jamais committé) et hors de `C:\CCW_Share` (point
+  de montage réseau accédé depuis CCL, cf. `BRIDGE_AGENT_DOC.md` §16.3 —
+  la clé privée n'a rien à y faire).
+- **Clé publique** : `C:\CCW\cles_bootstrap\bootstrap_publique.pem` — pas
+  sensible, à récupérer côté CCL pour chiffrer les tokens avant inclusion
+  dans le corps d'une future issue. Deux façons de la récupérer, aucune
+  automatisée pour l'instant :
+  - **copier-coller manuel** : `provisionner.ps1` affiche son contenu PEM
+    intégral en toute fin d'exécution ;
+  - **via la session SSH existante** (étape 3 ci-dessus, voir aussi
+    `BRIDGE_AGENT_DOC.md` §16.2) :
+    ```bash
+    ssh -i ~/.ssh/ccl_ccw AlainW@<ip> type C:\CCW\cles_bootstrap\bootstrap_publique.pem
+    ```
+
+Génération via `openssl.exe` (déjà présent : embarqué par Git pour Windows,
+sous-dossier `usr\bin`) plutôt que `.NET` natif ou `age` — voir le
+commentaire détaillé en tête de la section correspondante dans
+`provisionner.ps1` pour la justification complète du choix.
+
+> ⚠️ **La clé privée ne survit PAS à une réinstallation.** Comme le reste de
+> l'état local du PC fixe, `C:\CCW\cles_bootstrap\` disparaît avec le disque
+> effacé à l'étape 1 (réinstallation Windows) ; la paire de clés régénérée
+> par l'étape 4 suivante n'a **aucun rapport** avec l'ancienne. Conséquence
+> pratique à ne
+> pas oublier (cas déjà identifié dans la conception #554) : **toute issue
+> de bootstrap chiffrée avec l'ancienne clé publique, encore en attente de
+> traitement au moment d'une réinstallation, devient définitivement
+> indéchiffrable** — il faudra la ré-émettre depuis le formulaire une fois
+> la nouvelle clé publique récupérée côté CCL. Ne pas soumettre une case
+> « Projet CCW » juste avant une réinstallation planifiée du PC fixe.
+
 ---
 
 ## Prérequis côté Linux (ThinkPad) — `cifs-utils`
# (diff du fichier suivant)
diff --git a/provisioning/windows/provisionner.ps1 b/provisioning/windows/provisionner.ps1
# (index — ignorable)
index 9deec66..742fe53 100644
# (avant — fichier suivant)
--- a/provisioning/windows/provisionner.ps1
# (après — fichier suivant)
+++ b/provisioning/windows/provisionner.ps1
# ── Zone modifiée : ligne 20 (8 ligne(s)) dans l'ancienne version → ligne 20 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -20,8 +20,11 @@
     3. installe Claude Code via l'installeur natif officiel (pas de Node.js) :
          irm https://claude.ai/install.ps1 | iex
     4. clone AlainDelree/Bridge_Agent (lecture seule) dans C:\CCW\Bridge_Agent ;
-    5. écrit configs\ccw.conf (LABEL=for-windows, NOM=ccw, …) ;
-    6. enregistre un vrai service Windows (via NSSM) qui lance le watcher au
+    5. génère (une seule fois) la paire de clés RSA de chiffrement des tokens
+       de bootstrap « Projet CCW » (issue #554, 1/3) — clé privée jamais
+       exposée hors de la machine, voir section dédiée plus bas ;
+    6. écrit configs\ccw.conf (LABEL=for-windows, NOM=ccw, …) ;
+    7. enregistre un vrai service Windows (via NSSM) qui lance le watcher au
        démarrage de la machine (sans session ouverte), avec redémarrage
        automatique en cas d'échec.
 
# ── Zone modifiée : ligne 417 (7 ligne(s)) dans l'ancienne version → ligne 420 (99 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -417,7 +420,99 @@ if (Test-Path (Join-Path $RepDepot '.git')) {
 }
 
 # ---------------------------------------------------------------------------
-# 5. Écriture de configs\ccw.conf.
+# 5. Paire de clés de chiffrement des tokens de bootstrap « Projet CCW »
+#    (issue #554, 1/3 — brique clés seule ; le chiffrement côté formulaire et
+#    le déchiffrement côté watcher.py font l'objet de #555/#556 à suivre).
+#
+#    Contexte : la future case « Projet CCW » du formulaire de création de
+#    projet transmettra GH_TOKEN et CLAUDE_CODE_OAUTH_TOKEN dans le corps
+#    d'une issue GitHub traitée de façon ASYNCHRONE par CCW (PC potentiellement
+#    éteint à la soumission) — chiffrement asymétrique retenu plutôt que clair
+#    en dur. La clé PRIVÉE ne quitte jamais cette machine ; la clé PUBLIQUE
+#    n'est pas sensible et doit être récupérable côté CCL pour chiffrer.
+#
+#    Choix technique : RSA 3072 bits en PEM, généré via openssl.exe — déjà
+#    disponible sans installation supplémentaire puisque Git pour Windows
+#    (étape 1 winget ci-dessus) l'embarque dans son sous-dossier usr\bin
+#    (couche MSYS/MinGW). Écarté : .NET natif
+#    (System.Security.Cryptography), dont les méthodes d'export PEM
+#    (ExportPkcs8PrivateKey / ExportSubjectPublicKeyInfo) ne sont disponibles
+#    qu'à partir de .NET 5+ — absentes de Windows PowerShell 5.1 (.NET
+#    Framework) utilisé par défaut sur ce PC, ce qui aurait exigé de
+#    reconstruire l'encodage ASN.1/DER à la main. Écarté aussi : `age`, pour
+#    éviter d'imposer une dépendance winget supplémentaire alors qu'openssl
+#    est déjà présent de facto. Le format PEM (norme ouverte, contrairement
+#    au XML natif .NET) reste directement exploitable côté CCL (Python) pour
+#    le chiffrement à venir en #555.
+#
+#    Stockage : C:\CCW\cles_bootstrap\, un dossier LOCAL au PC fixe, frère de
+#    $RepDepot mais HORS du clone git (jamais committé) et hors de
+#    C:\CCW_Share (ce dernier est un point de montage réseau accédé depuis
+#    CCL, cf. BRIDGE_AGENT_DOC.md §16.3 — la clé privée n'y a rien à faire).
+#    Permissions restrictives sur le fichier de clé PRIVÉE (icacls,
+#    héritage coupé) : SYSTEM + Administrateurs (lecture/écriture), et
+#    $CompteService en lecture seule (compte sous lequel tourne
+#    CCW-Watcher, futur lecteur de cette clé pour le déchiffrement en #556).
+#
+#    Idempotent : si la paire existe déjà (réinstallations rapprochées lors
+#    d'un test), la génération est sautée — reste UNE clé par cycle de vie
+#    de la machine, régénérée à chaque réinstallation Windows complète (cf.
+#    rappel dans REINSTALLATION_CCW.md sur les issues de bootstrap en vol au
+#    moment d'une réinstallation).
+# ---------------------------------------------------------------------------
+function Resoudre-OpenSSL {
+    $cmd = Get-Command openssl -ErrorAction SilentlyContinue
+    if ($cmd) { return $cmd.Source }
+
+    # Pas sur le PATH : Git pour Windows l'embarque quand même dans son
+    # sous-dossier usr\bin (couche MSYS/MinGW), déjà installé à l'étape 1.
+    try {
+        $execPath  = (git --exec-path).Trim()
+        $racineGit = Split-Path (Split-Path $execPath -Parent) -Parent
+        $candidat  = Join-Path $racineGit 'usr\bin\openssl.exe'
+        if (Test-Path $candidat) { return $candidat }
+    } catch {
+        # Ignoré : on tombe sur l'erreur explicite ci-dessous.
+    }
+
+    throw ("openssl introuvable (ni sur le PATH, ni dans le sous-dossier " +
+           "usr\bin de Git) — impossible de générer la paire de clés de " +
+           "bootstrap. Vérifier l'installation de Git (étape 1).")
+}
+
+function Assurer-ClesBootstrap {
+    $RepCles        = Join-Path $RepCCW 'cles_bootstrap'
+    $CheminPrivee   = Join-Path $RepCles 'bootstrap_privee.pem'
+    $CheminPublique = Join-Path $RepCles 'bootstrap_publique.pem'
+
+    if ((Test-Path $CheminPrivee) -and (Test-Path $CheminPublique)) {
+        Info "Paire de clés de bootstrap déjà présente ($RepCles) — génération sautée (idempotent)."
+        return $CheminPublique
+    }
+
+    Info 'Génération de la paire de clés RSA de bootstrap (chiffrement tokens « Projet CCW », issue #554)…'
+    $openssl = Resoudre-OpenSSL
+    if (-not (Test-Path $RepCles)) { New-Item -ItemType Directory -Path $RepCles | Out-Null }
+
+    & $openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:3072 -out $CheminPrivee
+    if ($LASTEXITCODE -ne 0) { throw "openssl genpkey a échoué (code $LASTEXITCODE)." }
+    & $openssl pkey -in $CheminPrivee -pubout -out $CheminPublique
+    if ($LASTEXITCODE -ne 0) { throw "openssl pkey (extraction de la clé publique) a échoué (code $LASTEXITCODE)." }
+
+    Info 'Restriction des permissions de la clé privée (icacls)…'
+    icacls.exe $CheminPrivee /inheritance:r | Out-Null
+    icacls.exe $CheminPrivee /grant 'SYSTEM:F' | Out-Null
+    icacls.exe $CheminPrivee /grant 'BUILTIN\Administrators:F' | Out-Null
+    icacls.exe $CheminPrivee /grant "${CompteService}:R" | Out-Null
+
+    Info "Paire de clés de bootstrap générée dans $RepCles."
+    return $CheminPublique
+}
+
+$CheminCleBootstrapPublique = Assurer-ClesBootstrap
+
+# ---------------------------------------------------------------------------
+# 6. Écriture de configs\ccw.conf.
 #    REP_TRAVAIL pointe vers C:\CCW_Share, un chemin LOCAL au PC fixe
 #    (issue #446, suite #447) — plus de partage réseau VirtualBox.
 #    TOPIC_NTFY est un placeholder à renseigner (comme le mot de passe phase 1).
# ── Zone modifiée : ligne 463 (7 ligne(s)) dans l'ancienne version → ligne 558 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -463,7 +558,7 @@ Info "Écriture de $CheminConf…"
 [System.IO.File]::WriteAllText($CheminConf, $contenuConf, (New-Object System.Text.UTF8Encoding($false)))
 
 # ---------------------------------------------------------------------------
-# 6. Service Windows (NSSM) : lance le watcher au démarrage de la machine
+# 7. Service Windows (NSSM) : lance le watcher au démarrage de la machine
 #    (sans session ouverte), avec redémarrage automatique en cas d'échec.
 #
 #    ✅ Équivalent DIRECT des services systemd --user du §13 : démarrage au
# ── Zone modifiée : ligne 530 (3 ligne(s)) dans l'ancienne version → ligne 625 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -530,3 +625,9 @@ Info '  • interactif : claude auth login'
 Info ''
 Info "RAPPEL — renseigner TOPIC_NTFY dans $CheminConf (placeholder actuel)."
 Info "Le service « $NomService » lance le watcher au démarrage (vérif : nssm status $NomService / Get-Service $NomService)."
+Info ''
+Info "RAPPEL — clé publique de bootstrap « Projet CCW » (issue #554) à récupérer côté CCL :"
+Info "  fichier : $CheminCleBootstrapPublique"
+Info '  (copier-coller le contenu ci-dessous, ou la récupérer via la session SSH — §16.2) :'
+Info ''
+Get-Content $CheminCleBootstrapPublique | ForEach-Object { Info "  $_" }
