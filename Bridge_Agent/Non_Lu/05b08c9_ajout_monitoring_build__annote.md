05b08c9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 05b08c9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 00:46:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    ajout monitoring build

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index dc30e54..d318f23 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 78 (3 ligne(s)) dans l'ancienne version → ligne 78 (126 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -78,3 +78,126 @@ première et sous-estimerait gravement la seconde.
 lancée. À reprendre à froid — le sujet touche des EWMA et des choix de
 modélisation qu'on prendrait mal à la légère.
 
+##Rapport : nouvel outil surveiller_builds.ps1 — surveillance des builds CCW en temps réel
+
+Contexte : besoin exprimé de suivre visuellement l'avancement d'un build Windows en cours (PyInstaller via Claude Code, ou compilation Inno Setup via ISCC.exe) sans devoir ouvrir le Gestionnaire des tâches ni re-scanner le dossier de sortie à la main.
+
+Ce que fait le script : toutes les N secondes (10 par défaut), affiche :
+
+l'état de chaque processus surveillé (présent/absent, PID, CPU cumulé, mémoire, durée d'exécution) ;
+la taille totale du dossier de build surveillé, avec le delta depuis le dernier passage et depuis le début de la surveillance.
+
+Paramètres : -Dossier (obligatoire, ex. C:\Temp\ActualiseBuild), -Processus (liste, défaut claude, ISCC, python, pyinstaller), -IntervalleSecondes (défaut 10).
+
+Point à vérifier/ajuster à l'intégration : le nom exact du process sous lequel Claude Code tourne sur la VM CCW n'a pas été confirmé (peut être claude.exe natif ou node.exe si lancé via npm/npx) — à vérifier via Get-Process pendant un build réel avant de figer la valeur par défaut du paramètre -Processus.
+
+Fichier joint : script complet ci-dessous, prêt à committer dans le dépôt AlainDelree/Bridge_Agent, probablement dans le même dossier que les autres scripts PowerShell (ajouter_projet_ccw.ps1, provisionner.ps1, etc.), avec documentation correspondante dans BRIDGE_AGENT_DOC.md.
+
+<#
+.SYNOPSIS
+    Surveille en continu les processus de build (Claude Code / ISCC) et la
+    croissance du dossier de sortie d'un build en cours, sur la VM CCW.
+
+.DESCRIPTION
+    Affiche toutes les 10 secondes (paramétrable) :
+      - l'état des processus surveillés (présent/absent, CPU, mémoire, durée)
+      - la taille totale du dossier de build surveillé, et sa croissance
+        depuis le dernier passage.
+
+    Pensé pour suivre en temps réel un build CCW (PyInstaller via Claude Code,
+    ou compilation Inno Setup via ISCC.exe) sans avoir à ouvrir le Gestionnaire
+    des tâches ni à re-scanner le dossier manuellement.
+
+.PARAMETER Dossier
+    Chemin du dossier à surveiller (ex. C:\Temp\ActualiseBuild,
+    C:\Temp\ScrabbleBuild). Obligatoire.
+
+.PARAMETER Processus
+    Noms de processus à surveiller (sans .exe), séparés par une virgule.
+    Par défaut : claude, ISCC, python, pyinstaller.
+    Ajuster selon ce qu'affiche `Get-Process` pendant un build réel — le nom
+    exact du process Claude Code peut varier selon l'installation (souvent
+    "node" si lancé via npm/npx plutôt qu'un binaire natif "claude").
+
+.PARAMETER IntervalleSecondes
+    Fréquence de rafraîchissement. Par défaut 10.
+
+.EXAMPLE
+    .\surveiller_builds.ps1 -Dossier C:\Temp\ActualiseBuild
+
+.EXAMPLE
+    .\surveiller_builds.ps1 -Dossier C:\Temp\ScrabbleBuild -Processus claude,ISCC -IntervalleSecondes 5
+#>
+
+param(
+    [Parameter(Mandatory = $true)]
+    [string]$Dossier,
+
+    [string[]]$Processus = @("claude", "ISCC", "python", "pyinstaller"),
+
+    [int]$IntervalleSecondes = 10
+)
+
+function Obtenir-TailleDossier {
+    param([string]$Chemin)
+    if (-not (Test-Path $Chemin)) {
+        return 0
+    }
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
+    # État des processus surveillés
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
+    # Taille du dossier de build
+    $signeDelta = if ($delta -ge 0) { "+" } else { "" }
+    Write-Host ("  Dossier : {0}  (delta : {1}{2} depuis dernier passage, {3} depuis le début)" -f `
+        (Formater-Taille $tailleActuelle), $signeDelta, (Formater-Taille $delta), (Formater-Taille ($tailleActuelle - $tailleOrigine)))
+    Write-Host ""
+
+    $tailleAvant = $tailleActuelle
+    Start-Sleep -Seconds $IntervalleSecondes
+}
