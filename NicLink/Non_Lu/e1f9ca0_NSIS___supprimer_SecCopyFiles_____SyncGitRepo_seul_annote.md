e1f9ca0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e1f9ca0
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 17:18:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    NSIS : supprimer SecCopyFiles — SyncGitRepo seul installe le code depuis GitHub

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 91ca993..2857fa4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 5 (7 ligne(s)) dans l'ancienne version → ligne 5 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,7 +5,7 @@
 ## ⚡ Prioritaire
 
 - **Release v1.3.1 à packager** `[Linux/Windows]` — regrouper les correctifs depuis v1.3.0 (dont issue #96) : `./make_release.sh 1.3.1` + tag + `gh release create`.
-- **ACTION ALAIN — Valider installeur standalone** `[Windows]` — lancer `AlChess_Setup.exe` depuis un dossier quelconque, vérifier que l'app s'installe dans `%LOCALAPPDATA%\AlChess` et que le raccourci bureau fonctionne avec l'icône roi noir.
+- **ACTION ALAIN — Valider installeur standalone** `[Windows]` — lancer `AlChess_Setup.exe` seul (sans ZIP), vérifier clone GitHub dans `%LOCALAPPDATA%\AlChess` et raccourci bureau fonctionnel.
 - **Tester une partie réelle Rodent sur Windows** `[Windows]` — sur portable physique (jeu + changement d'Elo + redémarrage).
 - **Tester vc_redist sur un Windows sans le runtime VC++** `[Windows]` — la VM actuelle a déjà le runtime, il faut un Windows propre.
 
# (diff du fichier suivant)
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# (index — ignorable)
index 608996f..ac2728d 100644
# (avant — fichier suivant)
--- a/installer-exe/alchess_setup.nsi
# (après — fichier suivant)
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1349 (10 ligne(s)) dans l'ancienne version → ligne 1349 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1349,10 +1349,8 @@ Function SyncGitRepo
             Return
 
     repo_absent:
-        ; $EXEDIR est deja rempli par le ZIP de release : "git clone" ne peut
-        ; jamais y aboutir (git refuse un dossier non vide). On convertit donc
-        ; le dossier existant en depot git : init + remote add + fetch (shallow,
-        ; tags inclus) + checkout du dernier tag de release (issue #90, suite #89).
+        ; $INSTDIR est vide a la premiere installation : git init + remote add +
+        ; fetch --depth=1 --tags + checkout du dernier tag = equivalent d'un clone.
         DetailPrint "  Aucun depot git dans $INSTDIR — conversion en depot (init+fetch+checkout tag)..."
 
         nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" init'
# ── Zone modifiée : ligne 1411 (51 ligne(s)) dans l'ancienne version → ligne 1409 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1411,51 +1409,6 @@ FunctionEnd
 
 SectionGroup "Configuration AlChess" SecGroupConfig
 
-    ; -- Phase 8 (issue #113) : copie des fichiers vers le dossier fixe ------
-    ; DOIT s'executer EN PREMIER, avant toute autre section : tout le reste du
-    ; SectionGroup travaille sur $INSTDIR, qui doit donc deja contenir l'app
-    ; au moment ou SecGit demarre. Copie via robocopy (gere la fusion/reprise
-    ; mieux qu'un simple CopyFiles NSIS) depuis $EXEDIR (dossier de lancement
-    ; du .exe) vers $INSTDIR (%LOCALAPPDATA%\AlChess, toujours le meme).
-    ;
-    ; Garde-fou : si l'utilisateur a deja extrait le ZIP directement dans
-    ; %LOCALAPPDATA%\AlChess, $EXEDIR == $INSTDIR — la copie est alors inutile
-    ; (et robocopy sur une source == destination n'a de toute facon rien a
-    ; faire), donc on la saute explicitement.
-    ;
-    ; Codes de sortie robocopy : 0-7 = succes (0 = rien a copier, 1 = fichiers
-    ; copies, etc., cumulables en bitmask), 8+ = erreur reelle. On teste donc
-    ; $R0 <= 7, pas $R0 == 0.
-    Section "Copie des fichiers" SecCopyFiles
-        StrCmp "$EXEDIR" "$INSTDIR" copy_skip copy_start
-
-        copy_start:
-            DetailPrint "================================================"
-            DetailPrint "Copie d'AlChess vers $INSTDIR"
-            DetailPrint "================================================"
-            DetailPrint "  Source : $EXEDIR"
-            CreateDirectory "$INSTDIR"
-            nsExec::ExecToLog 'cmd /c robocopy "$EXEDIR" "$INSTDIR" /E /NFL /NDL /NJH /NJS /NC /NS /NP'
-            Pop $R0
-            IntCmp $R0 7 copy_ok copy_ok copy_fail
-
-            copy_fail:
-                DetailPrint "================================================"
-                DetailPrint "ECHEC : la copie vers $INSTDIR a echoue (code robocopy $R0)."
-                DetailPrint "================================================"
-                MessageBox MB_OK|MB_ICONSTOP "La copie des fichiers AlChess vers $INSTDIR a echoue (code robocopy $R0).$\r$\n$\r$\nVerifiez l'espace disque disponible et les droits d'ecriture sur %LOCALAPPDATA%, puis relancez cet installeur."
-                Abort
-
-            copy_ok:
-                DetailPrint "  Copie terminee avec succes."
-                Goto end_copy_files
-
-        copy_skip:
-            DetailPrint "Deja lance depuis $INSTDIR — copie sautee."
-
-        end_copy_files:
-    SectionEnd
-
     ; -- Phase Git (issue #88) : depot git + auto-update ----------------------
     ; DOIT s'executer avant SecPython/SecVenv : requirements.txt (utilise par
     ; SecVenv) doit venir du code deja synchronise ici.
