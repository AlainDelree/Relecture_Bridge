753883f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 753883f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Jul 28 02:58:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #84 — icône raccourci bureau manquante dans install_alchess.ps1 (IconLocation)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d7f624f..40a5ece 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 47 (6 ligne(s)) dans l'ancienne version → ligne 47 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,6 +47,8 @@
 
 ### Session du 28 juillet
 
+**Icône raccourci bureau — icône `.bat` générique persistante malgré le fix #69** `[Windows]` (issue #84, suite de #69/#39) — Bug validé sur machine Windows physique (test v1.3.0, 28 juillet) : le raccourci bureau affiche toujours l'icône rouge générique des `.bat` au lieu de `niclink_icon.ico`. **Investigation** : `installer-exe/alchess_setup.nsi` (`SecShortcut`, l.1638) référence déjà correctement `"$EXEDIR\niclink_icon.ico" 0` depuis #69 — rien à corriger côté NSIS, `makensis` confirme 0 erreur/0 warning après recompilation de contrôle. **Cause racine réelle trouvée ailleurs** : `install_alchess.ps1` (l.437-454, bloc COM `WScript.Shell` ajouté en #39) crée le **même** raccourci `$DESKTOP\AlChess.lnk` mais sans jamais définir `IconLocation` — or ce script (« Option B », toujours documenté et supporté dans le README depuis #75 comme alternative à `AlChess_Setup.exe`) reste un chemin d'installation valide. Un raccourci créé via cette voie n'a donc **aucune** icône spécifiée et hérite de l'icône générique du `.bat` cible — exactement le symptôme rapporté. **Correctif** : ajout de `$shortcut.IconLocation = "$scriptDir\niclink_icon.ico, 0"` juste après `WorkingDirectory`, avant `Description`/`Save()`. `niclink_icon.ico` est déjà dans la liste blanche `make_release.sh` (depuis #69) et co-localisé avec `install_alchess.ps1` dans le paquet livré → `$scriptDir\niclink_icon.ico` existe bien au runtime, aucune modif de packaging nécessaire. Vérifs sous Linux : accolades 85/85, parenthèses 111/111 (inchangé). Non testable sous Linux (pas de `pwsh`) — test réel décisif à faire par Alain : réinstaller via `1-Installer.bat`/`install_alchess.ps1` (pas `AlChess_Setup.exe`) et vérifier que le raccourci bureau affiche l'icône AlChess. Backup pinné avant modif.
+
 Intégration de detect_chessnut.py au premier démarrage : appel dans web/__main__.py si connect() échoue (best-effort, non bloquant) + appel silencieux dans 2-Lancer_AlChess.bat avant le serveur. (issue #83)
 
 Intégration de detect_chessnut.py dans l'installeur NSIS : section SecChessnut ajoutée après SecVenv, appel avec le Python du venv, message utilisateur selon le code de sortie. makensis : 0 erreur, 0 warning. (issue #82)
# (diff du fichier suivant)
diff --git a/install_alchess.ps1 b/install_alchess.ps1
# (index — ignorable)
index 5b75ac6..55817da 100644
# (avant — fichier suivant)
--- a/install_alchess.ps1
# (après — fichier suivant)
+++ b/install_alchess.ps1
# ── Zone modifiée : ligne 446 (6 ligne(s)) dans l'ancienne version → ligne 446 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -446,6 +446,7 @@ try {
     $shortcut = $wsh.CreateShortcut($lnkPath)
     $shortcut.TargetPath       = "$scriptDir\2-Lancer_AlChess.bat"
     $shortcut.WorkingDirectory = $scriptDir
+    $shortcut.IconLocation     = "$scriptDir\niclink_icon.ico, 0"
     $shortcut.Description       = "Launch AlChess"
     $shortcut.Save()
     Write-Host "Desktop shortcut 'AlChess' created." -ForegroundColor Green
