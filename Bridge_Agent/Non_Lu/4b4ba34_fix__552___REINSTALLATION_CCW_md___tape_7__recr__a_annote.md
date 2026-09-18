4b4ba34

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4b4ba34
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 15:31:02 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #552 : REINSTALLATION_CCW.md étape 7 (recréation des 4 services multi-projets CCW) + script reinstaller_projets_ccw.ps1 comme source de vérité de la liste ; note prérequis cifs-utils côté Linux
    
    Ajoute l'étape 7 à provisioning/windows/REINSTALLATION_CCW.md, documentant
    la recréation des services dédiés alchess/actualise/rummikub/scrabble
    (dépôts GitHub associés) après réinstallation Windows, en plus du service
    de base CCW-Watcher déjà couvert. Crée
    provisioning/windows/reinstaller_projets_ccw.ps1, qui séquence l'appel à
    creer_projet_ccw_complet.ps1 pour les 4 projets (tokens toujours demandés
    par projet, pas de contournement de la saisie) ; le tableau $Projets du
    script fait foi en cas de divergence avec la reproduction dans la doc.
    Ajoute aussi la note cifs-utils (prérequis Linux/ThinkPad pour le montage
    credentials= du partage réseau CCW), documentée au même endroit bien que
    hors procédure de réinstallation Windows à proprement parler.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/provisioning/windows/REINSTALLATION_CCW.md b/provisioning/windows/REINSTALLATION_CCW.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 03f78cc..b1e7f37 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/provisioning/windows/REINSTALLATION_CCW.md
# ── Version APRÈS ce commit.
+++ b/provisioning/windows/REINSTALLATION_CCW.md
# ── Zone modifiée : ligne 86 (3 ligne(s)) dans l'ancienne version → ligne 86 (60 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -86,3 +86,60 @@ Confirmer que `CCW-Watcher` est bien à l'état `running`, soit localement
 (`nssm status CCW-Watcher` ou services.msc sur le PC fixe), soit depuis
 CCL via l'onglet **CCW** de l'interface web (`new_issue.py`) — voir
 `BRIDGE_AGENT_DOC.md` §16.2.
+
+### 7. Recréer les services multi-projets dédiés
+
+Les étapes 1 à 6 ne remettent en place que le service de **base**
+`CCW-Watcher` (canal `for-windows` de Bridge_Agent). En production tournent
+en plus **4 services dédiés**, un par projet du modèle multi-projets actif
+(issue #170, cf. `BRIDGE_AGENT_DOC.md` §16) — eux aussi recréés à zéro par
+la réinstallation, puisque le service NSSM et ses tokens ne survivent pas :
+
+| Projet | Dépôt GitHub |
+|--------|--------------|
+| `alchess` | `AlainDelree/AlChess` |
+| `actualise` | `AlainDelree/Actualise` |
+| `rummikub` | `AlainDelree/Rummikub` |
+| `scrabble` | `AlainDelree/Scrabble` |
+
+Rappel : les fichiers `.conf` de chaque projet (ex. `configs\alchess-ccw.conf`)
+vivent dans le dépôt du projet lui-même, donc **survivent** à la
+réinstallation — rien à reconstruire de ce côté. Seuls la recréation du
+service NSSM et la resaisie des deux tokens (GitHub dédié + Claude Code)
+par projet restent nécessaires.
+
+Cette liste est maintenue à un seul endroit : le tableau `$Projets` dans
+`reinstaller_projets_ccw.ps1` (ce dossier) fait foi en cas de divergence —
+le tableau ci-dessus n'en est qu'une reproduction pour la lecture. Toujours
+en admin sur le PC fixe, depuis `C:\CCW\Bridge_Agent` :
+
+```powershell
+.\provisioning\windows\reinstaller_projets_ccw.ps1
+```
+
+Ce script séquence l'appel à `creer_projet_ccw_complet.ps1` (racine du
+dépôt, §16.5 de `BRIDGE_AGENT_DOC.md`) pour chacun des 4 projets — évitant
+de devoir taper 4 commandes séparées de mémoire. Les deux tokens restent
+demandés **par projet**, à l'intérieur de la boucle : le script structure
+la séquence, il ne contourne pas la saisie. En cas d'échec sur un projet,
+il s'arrête et affiche comment reprendre uniquement les projets restants
+(`-SeulementProjets`).
+
+Vérifier ensuite l'état des 5 services (base + 4 dédiés) via
+`provisioning\windows\lister_projets_ccw.ps1`, ou depuis CCL via l'onglet
+**CCW** de l'interface web.
+
+---
+
+## Prérequis côté Linux (ThinkPad) — `cifs-utils`
+
+Sans rapport direct avec la réinstallation Windows, mais lié à
+l'infrastructure CCW et à garder en mémoire au même endroit : le montage du
+partage réseau avec l'option `credentials=` (utilisé pour accéder au PC fixe
+CCW depuis le ThinkPad) nécessite le paquet **`cifs-utils`** côté Linux.
+Sans lui, le montage échoue silencieusement ou avec une erreur peu explicite
+sur `credentials=`. À installer une fois sur le ThinkPad si absent :
+
+```bash
+sudo apt install cifs-utils
+```
# (diff du fichier suivant)
diff --git a/provisioning/windows/reinstaller_projets_ccw.ps1 b/provisioning/windows/reinstaller_projets_ccw.ps1
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..ae5b20f
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/provisioning/windows/reinstaller_projets_ccw.ps1
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (73 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,73 @@
+﻿<#
+  reinstaller_projets_ccw.ps1 — Recréer en séquence les services multi-projets
+  CCW après une réinstallation Windows (issue #552, suite de #547/#451).
+
+  CONTEXTE : REINSTALLATION_CCW.md (étape 7) couvre la remise sur pied du
+  service de base CCW-Watcher, mais les 4 services dédiés actifs en
+  production (CCW-Watcher-alchess, -actualise, -rummikub, -scrabble, §16 de
+  BRIDGE_AGENT_DOC.md) doivent eux aussi être recréés — sans quoi il faut se
+  souvenir de mémoire de la liste exacte des projets à relancer avec
+  creer_projet_ccw_complet.ps1.
+
+  Ce script se contente de SÉQUENCER l'appel à creer_projet_ccw_complet.ps1
+  (racine du dépôt) pour chacun des projets ci-dessous. Il ne contourne
+  aucune saisie : les deux tokens (GH_TOKEN, CLAUDE_CODE_OAUTH_TOKEN) restent
+  demandés PAR PROJET, à l'intérieur de la boucle — pas de token partagé.
+
+  SOURCE DE VÉRITÉ DE LA LISTE : le tableau $Projets ci-dessous est la seule
+  liste maintenue des projets multi-projets CCW actifs. REINSTALLATION_CCW.md
+  (étape 7) la reproduit à titre indicatif pour la lecture humaine, mais en
+  cas de divergence (nouveau projet ajouté/retiré), CE tableau fait foi —
+  mettre à jour ici en premier, puis répercuter dans la doc.
+
+  Usage (depuis C:\CCW\Bridge_Agent, après l'étape 6 de REINSTALLATION_CCW.md
+  — service de base CCW-Watcher déjà vérifié) :
+    powershell -ExecutionPolicy Bypass -File provisioning\windows\reinstaller_projets_ccw.ps1
+
+  Pour ne rejouer qu'un sous-ensemble (ex. reprise après interruption) :
+    powershell -ExecutionPolicy Bypass -File provisioning\windows\reinstaller_projets_ccw.ps1 -SeulementProjets scrabble,rummikub
+#>
+
+param(
+    [string[]]$SeulementProjets
+)
+
+$ErrorActionPreference = "Stop"
+
+# Liste de référence — voir bloc de commentaire ci-dessus.
+$Projets = @(
+    @{ NomProjet = "alchess";   Depot = "AlainDelree/AlChess" }
+    @{ NomProjet = "actualise"; Depot = "AlainDelree/Actualise" }
+    @{ NomProjet = "rummikub";  Depot = "AlainDelree/Rummikub" }
+    @{ NomProjet = "scrabble";  Depot = "AlainDelree/Scrabble" }
+)
+
+if ($SeulementProjets) {
+    $Projets = $Projets | Where-Object { $SeulementProjets -contains $_.NomProjet }
+    if ($Projets.Count -eq 0) {
+        Write-Host "[reinstaller-projets-ccw] ERREUR : aucun des projets demandés ($($SeulementProjets -join ', ')) n'est dans la liste de référence."
+        exit 1
+    }
+}
+
+Write-Host "[reinstaller-projets-ccw] Projets à (re)créer, dans l'ordre : $($Projets.NomProjet -join ', ')"
+Write-Host "[reinstaller-projets-ccw] Chaque projet demandera SES DEUX propres tokens (GH_TOKEN + CLAUDE_CODE_OAUTH_TOKEN)."
+Write-Host ""
+
+$CheminScript = Join-Path $PSScriptRoot "..\..\creer_projet_ccw_complet.ps1"
+
+foreach ($p in $Projets) {
+    Write-Host "========================================================================"
+    Write-Host "[reinstaller-projets-ccw] Projet : $($p.NomProjet)  (dépôt $($p.Depot))"
+    Write-Host "========================================================================"
+    powershell -ExecutionPolicy Bypass -File $CheminScript -NomProjet $p.NomProjet -Depot $p.Depot
+    if ($LASTEXITCODE -ne 0) {
+        Write-Host "[reinstaller-projets-ccw] ERREUR sur le projet $($p.NomProjet) (code $LASTEXITCODE). Arrêt de la séquence."
+        Write-Host "[reinstaller-projets-ccw] Reprise possible avec -SeulementProjets une fois le problème corrigé."
+        exit 1
+    }
+    Write-Host ""
+}
+
+Write-Host "[reinstaller-projets-ccw] Terminé — $($Projets.Count) projet(s) traité(s) : $($Projets.NomProjet -join ', ')"
+Write-Host "[reinstaller-projets-ccw] Vérif globale : provisioning\windows\lister_projets_ccw.ps1"
