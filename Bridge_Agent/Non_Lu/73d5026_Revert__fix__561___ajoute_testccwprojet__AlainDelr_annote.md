73d5026

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 73d5026
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Thu Sep 17 18:05:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Revert "fix #561 : ajoute testccwprojet (AlainDelree/Testccwprojet) à la réinstallation CCW"
    
    This reverts commit ff032df6529fdfa35233f456aba3e1d4de2fe75e.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/provisioning/windows/REINSTALLATION_CCW.md b/provisioning/windows/REINSTALLATION_CCW.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d07ac42..4a1e736 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/provisioning/windows/REINSTALLATION_CCW.md
# ── Version APRÈS ce commit.
+++ b/provisioning/windows/REINSTALLATION_CCW.md
# ── Zone modifiée : ligne 102 (7 ligne(s)) dans l'ancienne version → ligne 102 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -102,7 +102,6 @@ la réinstallation, puisque le service NSSM et ses tokens ne survivent pas :
 | `actualise` | `AlainDelree/Actualise` |
 | `rummikub` | `AlainDelree/Rummikub` |
 | `scrabble` | `AlainDelree/Scrabble` |
-| `testccwprojet` | `AlainDelree/Testccwprojet` |
 
 Rappel : les fichiers `.conf` de chaque projet (ex. `configs\alchess-ccw.conf`)
 vivent dans le dépôt du projet lui-même, donc **survivent** à la
# (diff du fichier suivant)
diff --git a/provisioning/windows/reinstaller_projets_ccw.ps1 b/provisioning/windows/reinstaller_projets_ccw.ps1
# (index — ignorable)
index e39eb49..ae5b20f 100644
# (avant — fichier suivant)
--- a/provisioning/windows/reinstaller_projets_ccw.ps1
# (après — fichier suivant)
+++ b/provisioning/windows/reinstaller_projets_ccw.ps1
# ── Zone modifiée : ligne 40 (7 ligne(s)) dans l'ancienne version → ligne 40 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -40,7 +40,6 @@ $Projets = @(
     @{ NomProjet = "actualise"; Depot = "AlainDelree/Actualise" }
     @{ NomProjet = "rummikub";  Depot = "AlainDelree/Rummikub" }
     @{ NomProjet = "scrabble";  Depot = "AlainDelree/Scrabble" }
-    @{ NomProjet = "testccwprojet"; Depot = "AlainDelree/Testccwprojet" }
 )
 
 if ($SeulementProjets) {
