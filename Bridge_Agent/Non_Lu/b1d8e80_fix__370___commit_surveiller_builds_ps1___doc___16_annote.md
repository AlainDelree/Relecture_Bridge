b1d8e80

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b1d8e80
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 21:58:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #370 : commit surveiller_builds.ps1 + doc §16 + changelog

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 82e00b5..6c105d5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1263 (6 ligne(s)) dans l'ancienne version → ligne 1263 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1263,6 +1263,7 @@ le dépôt à titre historique uniquement ; ne pas les utiliser.
 | `lister_projets_ccw.ps1` | **(dans la VM, appelé à distance — issue #174)** Inventaire **JSON** des projets CCW : énumère les services `CCW-Watcher*` (NSSM), et pour chacun émet le nom du service, le projet dérivé, l'état (`running`/`stopped`) et le statut du placeholder `TOPIC_NTFY` (lu dans le config, sans jamais renvoyer la valeur réelle du topic). Sortie encadrée par `<<<CCW_JSON>>>…<<<CCW_END>>>` pour extraction fiable côté Linux. Exécuté par l'onglet CCW de l'interface web. |
 | `finaliser_projet_ccw_auto.ps1` | **(dans la VM, appelé à distance — issue #174)** Variante **non interactive** de `finaliser_projet_ccw.ps1` : lit `TOPIC_NTFY` + les deux tokens dans un **fichier « clé=valeur »** poussé par l'appelant (jamais en argument de commande), remplace le placeholder `TOPIC_NTFY` dans le config (édition ciblée) puis **appelle** `mettre_a_jour_tokens_ccw.ps1 -FichierTokens` (aucune duplication de la logique des tokens). Supprime le fichier de valeurs dans un `finally` (nettoyage côté VM). Code de sortie = celui du script de tokens (0/2/1). |
 | `finaliser_projet_ccw.ps1` | **(obsolète — modèle multi-projets abandonné, conservé à titre historique)** **(dans la VM)** Finalise en **une seule commande** un projet déjà créé par `ajouter_projet_ccw.ps1` (issue #173, suite #170), regroupant les 3 étapes manuelles auparavant dispersées. À partir du seul `-NomProjet` (argument ou prompt), **dérive** `CCW-Watcher-<NomProjet>`, `C:\CCW\<NomProjet>` et `configs\<nom>-ccw.conf` (même logique qu'`ajouter_projet_ccw.ps1`) et **vérifie** leur existence (sinon renvoie vers `ajouter_projet_ccw.ps1`). Puis : (1) demande `TOPIC_NTFY` (`Read-Host`, pas un secret) et remplace le placeholder `###TOPIC_NTFY_A_DEFINIR###` **dans** le config par édition ciblée (le reste du fichier préservé, UTF-8 sans BOM) ; (2) rappelle les réglages du token dédié à créer (repo unique, permissions, expiration alignée) avec une **pause** ; (3) **appelle** `mettre_a_jour_tokens_ccw.ps1` (pas de duplication) avec les paramètres déduits — dont `-NomLog ccw-<nom>-service.log` — pour la saisie masquée + pose des tokens + redémarrage + vérif des logs ; (4) résumé final selon le code renvoyé. |
+| `surveiller_builds.ps1` | **(dans la VM, lancé manuellement — issue #370)** Surveille en continu, pendant un build en cours (PyInstaller/ISCC), les processus de build et la croissance du dossier de sortie. Paramètre `-Dossier` **obligatoire** (chemin du dossier de sortie à surveiller, ex. `installeur\output`) ; `-Processus` optionnel (liste de noms de process à surveiller, défaut `claude, ISCC, python, pyinstaller`) ; `-IntervalleSecondes` optionnel (défaut `10`). À chaque passage : affiche pour chaque process surveillé son PID/CPU/mémoire/durée de vie s'il est actif, et la taille du dossier avec le delta depuis le dernier passage et depuis le début. Exemple : `powershell -ExecutionPolicy Bypass -File provisioning\windows\surveiller_builds.ps1 -Dossier C:\CCW\actualise\installeur\output -IntervalleSecondes 15`. **Attention** : le nom de process Claude Code (`claude` par défaut dans `-Processus`) est une hypothèse à vérifier via `Get-Process` pendant un build réel — l'installeur natif Windows peut l'enregistrer sous un nom différent, auquel cas le passer explicitement en paramètre. |
 
 La VM cible **Windows 11 IoT Enterprise LTSC 2024** en évaluation 90 jours,
 d'où la recréation facile prévue.
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 86e60b0..c1a8b81 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,18 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 3 août 2026 — issue #370
+
+Script PowerShell `surveiller_builds.ps1` (issu d'une session Claude Chat
+précédente) committé dans `provisioning/windows/` : surveille en temps réel,
+pendant un build CCW (PyInstaller/ISCC), les processus de build et la
+croissance du dossier de sortie (taille + delta par passage et depuis le
+début). Paramètre `-Dossier` obligatoire, `-Processus` et
+`-IntervalleSecondes` optionnels. Documenté au §16 de `BRIDGE_AGENT_DOC.md`
+(tableau de provisioning), avec la note que le nom de process Claude Code
+(`claude` par défaut) reste à confirmer via `Get-Process` pendant un build
+réel.
+
 ## 3 août 2026 — issue #352
 
 Le POST `/notifier-fin-issue` (#350) était déclenché via `notifications.bip()`,
# (diff du fichier suivant)
diff --git a/provisioning/windows/surveiller_builds.ps1 b/provisioning/windows/surveiller_builds.ps1
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100755
# (index — ignorable)
index 0000000..1270131
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/provisioning/windows/surveiller_builds.ps1
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (73 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,73 @@
+﻿<#
+.SYNOPSIS
+    Surveille en continu les processus de build (Claude Code / ISCC) et la
+    croissance du dossier de sortie d'un build en cours, sur la VM CCW.
+#>
+
+param(
+    [Parameter(Mandatory = $true)]
+    [string]$Dossier,
+    [string[]]$Processus = @("claude", "ISCC", "python", "pyinstaller"),
+    [int]$IntervalleSecondes = 10
+)
+
+function Obtenir-TailleDossier {
+    param([string]$Chemin)
+    if (-not (Test-Path $Chemin)) { return 0 }
+    $mesure = Get-ChildItem -Path $Chemin -Recurse -File -ErrorAction SilentlyContinue |
+        Measure-Object -Property Length -Sum
+    if ($null -eq $mesure.Sum) { return 0 }
+    return $mesure.Sum
+}
+
+function Formater-Taille {
+    param([long]$Octets)
+    if ($Octets -ge 1GB) { return "{0:N2} Go" -f ($Octets / 1GB) }
+    if ($Octets -ge 1MB) { return "{0:N2} Mo" -f ($Octets / 1MB) }
+    if ($Octets -ge 1KB) { return "{0:N2} Ko" -f ($Octets / 1KB) }
+    return "$Octets o"
+}
+
+Write-Host "=== Surveillance de build ===" -ForegroundColor Cyan
+Write-Host "Dossier surveillé   : $Dossier"
+Write-Host "Processus surveillés: $($Processus -join ', ')"
+Write-Host "Intervalle          : ${IntervalleSecondes}s"
+Write-Host "Ctrl+C pour arrêter."
+Write-Host ""
+
+$tailleOrigine = Obtenir-TailleDossier -Chemin $Dossier
+$tailleAvant = $tailleOrigine
+$debut = Get-Date
+
+while ($true) {
+    $horodatage = Get-Date -Format "HH:mm:ss"
+    $tailleActuelle = Obtenir-TailleDossier -Chemin $Dossier
+    $delta = $tailleActuelle - $tailleAvant
+    $ecouleTotal = (Get-Date) - $debut
+
+    Write-Host "--- $horodatage (écoulé : $($ecouleTotal.ToString('hh\:mm\:ss'))) ---" -ForegroundColor Yellow
+
+    foreach ($nom in $Processus) {
+        $procs = Get-Process -Name $nom -ErrorAction SilentlyContinue
+        if ($procs) {
+            foreach ($p in $procs) {
+                $dureeVie = (Get-Date) - $p.StartTime
+                $cpuSec = [Math]::Round($p.CPU, 1)
+                $memMo = [Math]::Round($p.WorkingSet64 / 1MB, 1)
+                Write-Host ("  [ACTIF] {0,-12} PID={1,-6} CPU={2,7}s  Mem={3,7} Mo  Durée={4}" -f `
+                    $p.ProcessName, $p.Id, $cpuSec, $memMo, $dureeVie.ToString('hh\:mm\:ss'))
+            }
+        } else {
+            Write-Host ("  [absent] {0}" -f $nom) -ForegroundColor DarkGray
+        }
+    }
+
+    $signeDelta = if ($delta -ge 0) { "+" } else { "" }
+    Write-Host ("  Dossier : {0}  (delta : {1}{2} depuis dernier passage, {3} depuis le début)" -f `
+        (Formater-Taille $tailleActuelle), $signeDelta, (Formater-Taille $delta),
+        (Formater-Taille ($tailleActuelle - $tailleOrigine)))
+    Write-Host ""
+
+    $tailleAvant = $tailleActuelle
+    Start-Sleep -Seconds $IntervalleSecondes
+}
