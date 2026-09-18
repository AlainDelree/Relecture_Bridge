edd154b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit edd154b
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 21:50:55 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #358 : ajoute l'en-tête fixe au CHANGELOG et reconstitue l'entrée #345

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0613243..3a50219 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +1,7 @@
 # Changelog — Projet Scrabble
 
+Convention d'ajout : voir §10 de BRIDGE_AGENT_DOC.md.
+
 Historique des changements notables, par ordre antéchronologique. Voir aussi
 `git log` pour le détail commit par commit (convention `Issue #NNN : ...`).
 
# ── Zone modifiée : ligne 7 (6 ligne(s)) dans l'ancienne version → ligne 9 (32 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -7,6 +9,32 @@ Historique des changements notables, par ordre antéchronologique. Voir aussi
 
 ### Corrigé
 
+- **Issue #345** — `build/rebuild_scrabble.bat` ne téléchargeait pas
+  `Actualise.exe` (dépendance de l'installeur, chemin attendu
+  `C:\Temp\ScrabbleBuild\Actualise.exe`) et ne produisait pas `scrabble.zip`
+  (archive de mise à jour consommée par l'updater), seulement
+  `Scrabble-Setup.exe`.
+
+  Deux étapes ajoutées au script (renumérotation `[n/7]` → `[n/9]`) : une
+  nouvelle étape 6 (avant ISCC) télécharge `actualise.zip` depuis
+  `github.com/AlainDelree/Actualise/releases/download/v1/actualise.zip` via
+  `Invoke-WebRequest`, l'extrait et copie `Actualise.exe` vers
+  `C:\Temp\ScrabbleBuild\Actualise.exe`, avec vérification `errorlevel` à
+  chaque sous-étape ; une nouvelle étape 8 (après ISCC) écrit
+  `manifest.json` (`{"build": 1, "supprimer": []}`) puis zippe
+  `dist\Scrabble\*` et `manifest.json` (sans dossier englobant, l'updater
+  extrayant directement par-dessus le dossier installé) vers
+  `installeur\output\scrabble.zip`. L'étape finale recopie désormais aussi
+  `scrabble.zip` vers `%ORIGDIR%\installeur\output\`, en plus de
+  `Scrabble-Setup.exe`.
+
+  `installeur\scrabble.iss` n'a pas été modifié : il ne référence
+  actuellement aucun `Actualise.exe` dans sa section `[Files]`, et la tâche
+  portait explicitement sur `rebuild_scrabble.bat` seul. Script non testé à
+  l'exécution (pas d'environnement Windows/cmd.exe disponible côté agent) ;
+  la syntaxe PowerShell suit le pattern déjà utilisé ailleurs dans le
+  fichier.
+
 - **Issue #339** — `scrabble.spec` embarquait tout le contenu de
   `data/dictionnaire/` sans filtre (`collect_tree` = `os.walk` récursif sur
   ce que contenait le disque local au moment du build). Un dump de travail de
