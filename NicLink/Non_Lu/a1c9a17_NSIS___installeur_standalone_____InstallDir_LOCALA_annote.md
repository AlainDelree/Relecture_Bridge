a1c9a17

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a1c9a17
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Aug 12 20:42:29 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    NSIS : installeur standalone — InstallDir LOCALAPPDATA\AlChess

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7c9bd95..91ca993 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 5 (7 ligne(s)) dans l'ancienne version → ligne 5 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,7 +5,7 @@
 ## ⚡ Prioritaire
 
 - **Release v1.3.1 à packager** `[Linux/Windows]` — regrouper les correctifs depuis v1.3.0 (dont issue #96) : `./make_release.sh 1.3.1` + tag + `gh release create`.
-- **ACTION ALAIN — Valider nouveau raccourci Windows** `[Windows]` — relancer `AlChess_Setup.exe` sur VM Windows et vérifier que le raccourci bureau affiche bien l'icône roi noir.
+- **ACTION ALAIN — Valider installeur standalone** `[Windows]` — lancer `AlChess_Setup.exe` depuis un dossier quelconque, vérifier que l'app s'installe dans `%LOCALAPPDATA%\AlChess` et que le raccourci bureau fonctionne avec l'icône roi noir.
 - **Tester une partie réelle Rodent sur Windows** `[Windows]` — sur portable physique (jeu + changement d'Elo + redémarrage).
 - **Tester vc_redist sur un Windows sans le runtime VC++** `[Windows]` — la VM actuelle a déjà le runtime, il faut un Windows propre.
 
# (diff du fichier suivant)
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# (index — ignorable)
index 9fe0c3a..608996f 100644
# (avant — fichier suivant)
--- a/installer-exe/alchess_setup.nsi
# (après — fichier suivant)
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 142 (11 ligne(s)) dans l'ancienne version → ligne 142 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -142,11 +142,16 @@ Name "AlChess - Windows Installer"
 BrandingText "AlChess - Windows Installer"
 OutFile "AlChess_Setup.exe"
 
-; Pas de InstallDir : on ne s'installe pas, on configure sur place ($EXEDIR).
-; RequestExecutionLevel user : aucune ecriture hors du dossier de l'app.
+; Phase 8 (issue #113) : installeur standalone, dossier fixe et permanent.
+; L'app est copiee depuis $EXEDIR (dossier de lancement du .exe, potentiellement
+; temporaire — Telechargements, ZIP extrait, etc.) vers $INSTDIR, qui pointe
+; TOUJOURS sur %LOCALAPPDATA%\AlChess. Le raccourci bureau reste donc valide
+; meme si l'utilisateur deplace ou supprime le dossier d'ou il a lance le .exe.
+; RequestExecutionLevel user : aucune ecriture hors du profil utilisateur.
 ; (Les phases 3-5 pourront relever le niveau si l'install de Python/VC++ le
 ;  necessite ; a evaluer le moment venu.)
 RequestExecutionLevel user
+InstallDir "$LOCALAPPDATA\AlChess"
 ShowInstDetails show
 
 ; ---------------------------------------------------------------------------
# ── Zone modifiée : ligne 202 (7 ligne(s)) dans l'ancienne version → ligne 207 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -202,7 +207,7 @@ FunctionEnd
 ;  en continu (le .bat n'a volontairement pas de "pause" final).
 ; ---------------------------------------------------------------------------
 Function LaunchAlChess
-    Exec '"$EXEDIR\2-Lancer_AlChess.bat"'
+    Exec '"$INSTDIR\2-Lancer_AlChess.bat"'
 FunctionEnd
 
 ; ============================================================================
# ── Zone modifiée : ligne 230 (7 ligne(s)) dans l'ancienne version → ligne 235 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -230,7 +235,7 @@ FunctionEnd
 ; ---------------------------------------------------------------------------
 Function LogCheckpoint
     Push $0
-    nsExec::ExecToLog 'cmd /c echo %date% %time% - $LogMsg >> "$EXEDIR\alchess_install_debug.log"'
+    nsExec::ExecToLog 'cmd /c echo %date% %time% - $LogMsg >> "$INSTDIR\alchess_install_debug.log"'
     Pop $0   ; code de sortie nsExec (ignore)
     Pop $0   ; restaure la valeur d'origine de $0
 FunctionEnd
# ── Zone modifiée : ligne 242 (7 ligne(s)) dans l'ancienne version → ligne 247 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -242,7 +247,7 @@ FunctionEnd
 ;  Aucun registre utilise (au-dela de ceux preserves par LogCheckpoint).
 ; ---------------------------------------------------------------------------
 Function LogVenvState
-    IfFileExists "$EXEDIR\${VENV_SUBDIR}\Scripts\python.exe" lvs_present lvs_absent
+    IfFileExists "$INSTDIR\${VENV_SUBDIR}\Scripts\python.exe" lvs_present lvs_absent
     lvs_present:
         StrCpy $LogMsg "$LogMsg : PRESENT"
         Goto lvs_log
# ── Zone modifiée : ligne 1018 (11 ligne(s)) dans l'ancienne version → ligne 1023 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1018,11 +1023,11 @@ Function CleanupStockfishVariant
     ; On veut supprimer $EXEDIR\engines\stockfish\ mais JAMAIS $EXEDIR\engines\
     ; Strategie : supprimer uniquement $EXEDIR\${ENGINES_SUBDIR}\stockfish (chemin fixe)
     ; car c'est toujours le dossier d'extraction de l'asset officiel
-    IfFileExists "$EXEDIR\${ENGINES_SUBDIR}\stockfish\*.*" do_cleanup skip_cleanup
+    IfFileExists "$INSTDIR\${ENGINES_SUBDIR}\stockfish\*.*" do_cleanup skip_cleanup
 
     do_cleanup:
         DetailPrint "  Nettoyage du dossier stockfish echoue..."
-        RMDir /r "$EXEDIR\${ENGINES_SUBDIR}\stockfish"
+        RMDir /r "$INSTDIR\${ENGINES_SUBDIR}\stockfish"
         Return
 
     skip_cleanup:
# ── Zone modifiée : ligne 1059 (10 ligne(s)) dans l'ancienne version → ligne 1064 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1059,10 +1064,10 @@ Function TryStockfishVariant
         DetailPrint "  Telechargement reussi."
 
         ; 2. Creer le dossier engines s'il n'existe pas
-        IfFileExists "$EXEDIR\${ENGINES_SUBDIR}\*.*" extract_zip create_engines_dir
+        IfFileExists "$INSTDIR\${ENGINES_SUBDIR}\*.*" extract_zip create_engines_dir
 
         create_engines_dir:
-            CreateDirectory "$EXEDIR\${ENGINES_SUBDIR}"
+            CreateDirectory "$INSTDIR\${ENGINES_SUBDIR}"
 
         extract_zip:
             ; ============================================================
# ── Zone modifiée : ligne 1076 (7 ligne(s)) dans l'ancienne version → ligne 1081 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1076,7 +1081,7 @@ Function TryStockfishVariant
             ; deux auraient convenu ; nsisunz privilegie par prudence.
             ; ============================================================
             DetailPrint "  Extraction..."
-            nsisunz::UnzipToLog "$TEMP\stockfish.zip" "$EXEDIR\${ENGINES_SUBDIR}"
+            nsisunz::UnzipToLog "$TEMP\stockfish.zip" "$INSTDIR\${ENGINES_SUBDIR}"
             Pop $R6  ; "success" ou message d'erreur
             StrCmp $R6 "success" extract_ok extract_fail
 
# ── Zone modifiée : ligne 1090 (7 ligne(s)) dans l'ancienne version → ligne 1095 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1090,7 +1095,7 @@ Function TryStockfishVariant
 
         ; 3. Trouver l'executable (apres extraction)
         ; L'asset Stockfish s'extrait dans stockfish/stockfish-windows-x86-64[-variante].exe
-        FindFirst $R6 $R7 "$EXEDIR\${ENGINES_SUBDIR}\stockfish\stockfish*.exe"
+        FindFirst $R6 $R7 "$INSTDIR\${ENGINES_SUBDIR}\stockfish\stockfish*.exe"
         StrCmp $R6 "" no_exe_found found_exe
 
         no_exe_found:
# ── Zone modifiée : ligne 1109 (7 ligne(s)) dans l'ancienne version → ligne 1114 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1109,7 +1114,7 @@ Function TryStockfishVariant
             Return
 
         found_exe:
-            StrCpy $R0 "$EXEDIR\${ENGINES_SUBDIR}\stockfish\$R7"
+            StrCpy $R0 "$INSTDIR\${ENGINES_SUBDIR}\stockfish\$R7"
             FindClose $R6
             DetailPrint "  Executable trouve : $R0"
 
# ── Zone modifiée : ligne 1245 (7 ligne(s)) dans l'ancienne version → ligne 1250 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1245,7 +1250,7 @@ FunctionEnd
 Function GetLatestTag
     StrCpy $LatestTag ""
 
-    nsExec::ExecToStack 'cmd /c git -C "$EXEDIR" tag --sort=-version:refname > "$TEMP\alchess_tags.txt" 2>NUL'
+    nsExec::ExecToStack 'cmd /c git -C "$INSTDIR" tag --sort=-version:refname > "$TEMP\alchess_tags.txt" 2>NUL'
     Pop $R0  ; exit code
     Pop $R1  ; output (vide car redirige)
     IntCmp $R0 0 tags_listed tags_list_fail tags_list_fail
# ── Zone modifiée : ligne 1310 (11 ligne(s)) dans l'ancienne version → ligne 1315 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1310,11 +1315,11 @@ Function SyncGitRepo
     DetailPrint "Synchronisation du code AlChess (Git)"
     DetailPrint "================================================"
 
-    IfFileExists "$EXEDIR\.git\*.*" repo_present repo_absent
+    IfFileExists "$INSTDIR\.git\*.*" repo_present repo_absent
 
     repo_present:
         DetailPrint "  Depot git existant detecte — recherche du dernier tag de release..."
-        nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" fetch --tags origin'
+        nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" fetch --tags origin'
         Pop $R0
         IntCmp $R0 0 present_fetch_ok present_fetch_fail present_fetch_fail
 
# ── Zone modifiée : ligne 1327 (7 ligne(s)) dans l'ancienne version → ligne 1332 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1327,7 +1332,7 @@ Function SyncGitRepo
             StrCmp $LatestTag "" present_no_tag 0
 
             DetailPrint "  Dernier tag de release : $LatestTag — checkout..."
-            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" checkout "$LatestTag"'
+            nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" checkout "$LatestTag"'
             Pop $R0
             IntCmp $R0 0 present_checkout_ok present_checkout_fail present_checkout_fail
 
# ── Zone modifiée : ligne 1348 (9 ligne(s)) dans l'ancienne version → ligne 1353 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1348,9 +1353,9 @@ Function SyncGitRepo
         ; jamais y aboutir (git refuse un dossier non vide). On convertit donc
         ; le dossier existant en depot git : init + remote add + fetch (shallow,
         ; tags inclus) + checkout du dernier tag de release (issue #90, suite #89).
-        DetailPrint "  Aucun depot git dans $EXEDIR — conversion en depot (init+fetch+checkout tag)..."
+        DetailPrint "  Aucun depot git dans $INSTDIR — conversion en depot (init+fetch+checkout tag)..."
 
-        nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" init'
+        nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" init'
         Pop $R0
         IntCmp $R0 0 sync_init_ok sync_init_fail sync_init_fail
 
# ── Zone modifiée : ligne 1359 (7 ligne(s)) dans l'ancienne version → ligne 1364 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1359,7 +1364,7 @@ Function SyncGitRepo
             Return
 
         sync_init_ok:
-            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" remote add origin https://github.com/AlainDelree/AlChess.git'
+            nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" remote add origin https://github.com/AlainDelree/AlChess.git'
             Pop $R0
             IntCmp $R0 0 sync_remote_ok sync_remote_fail sync_remote_fail
 
# ── Zone modifiée : ligne 1368 (7 ligne(s)) dans l'ancienne version → ligne 1373 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1368,7 +1373,7 @@ Function SyncGitRepo
             Return
 
         sync_remote_ok:
-            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" fetch --depth=1 --tags origin'
+            nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" fetch --depth=1 --tags origin'
             Pop $R0
             IntCmp $R0 0 sync_fetch_ok sync_fetch_fail sync_fetch_fail
 
# ── Zone modifiée : ligne 1381 (7 ligne(s)) dans l'ancienne version → ligne 1386 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1381,7 +1386,7 @@ Function SyncGitRepo
             StrCmp $LatestTag "" sync_no_tag 0
 
             DetailPrint "  Dernier tag de release : $LatestTag — checkout..."
-            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" checkout "$LatestTag"'
+            nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" checkout "$LatestTag"'
             Pop $R0
             IntCmp $R0 0 sync_checkout_ok sync_checkout_fail sync_checkout_fail
 
# ── Zone modifiée : ligne 1390 (7 ligne(s)) dans l'ancienne version → ligne 1395 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1390,7 +1395,7 @@ Function SyncGitRepo
             Return
 
         sync_checkout_ok:
-            DetailPrint "  Depot git initialise avec succes : $EXEDIR est maintenant un vrai clone AlChess (version $LatestTag)."
+            DetailPrint "  Depot git initialise avec succes : $INSTDIR est maintenant un vrai clone AlChess (version $LatestTag)."
             Return
 
         sync_no_tag:
# ── Zone modifiée : ligne 1400 (11 ligne(s)) dans l'ancienne version → ligne 1405 (57 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1400,11 +1405,57 @@ FunctionEnd
 
 ; ============================================================================
 ;  SECTIONS DE CONFIGURATION
-;  Toutes co-localisees sur $EXEDIR. Remplies progressivement (phases 3-5).
+;  Toutes co-localisees sur $INSTDIR (%LOCALAPPDATA%\AlChess). Remplies
+;  progressivement (phases 3-5).
 ; ============================================================================
 
 SectionGroup "Configuration AlChess" SecGroupConfig
 
+    ; -- Phase 8 (issue #113) : copie des fichiers vers le dossier fixe ------
+    ; DOIT s'executer EN PREMIER, avant toute autre section : tout le reste du
+    ; SectionGroup travaille sur $INSTDIR, qui doit donc deja contenir l'app
+    ; au moment ou SecGit demarre. Copie via robocopy (gere la fusion/reprise
+    ; mieux qu'un simple CopyFiles NSIS) depuis $EXEDIR (dossier de lancement
+    ; du .exe) vers $INSTDIR (%LOCALAPPDATA%\AlChess, toujours le meme).
+    ;
+    ; Garde-fou : si l'utilisateur a deja extrait le ZIP directement dans
+    ; %LOCALAPPDATA%\AlChess, $EXEDIR == $INSTDIR — la copie est alors inutile
+    ; (et robocopy sur une source == destination n'a de toute facon rien a
+    ; faire), donc on la saute explicitement.
+    ;
+    ; Codes de sortie robocopy : 0-7 = succes (0 = rien a copier, 1 = fichiers
+    ; copies, etc., cumulables en bitmask), 8+ = erreur reelle. On teste donc
+    ; $R0 <= 7, pas $R0 == 0.
+    Section "Copie des fichiers" SecCopyFiles
+        StrCmp "$EXEDIR" "$INSTDIR" copy_skip copy_start
+
+        copy_start:
+            DetailPrint "================================================"
+            DetailPrint "Copie d'AlChess vers $INSTDIR"
+            DetailPrint "================================================"
+            DetailPrint "  Source : $EXEDIR"
+            CreateDirectory "$INSTDIR"
+            nsExec::ExecToLog 'cmd /c robocopy "$EXEDIR" "$INSTDIR" /E /NFL /NDL /NJH /NJS /NC /NS /NP'
+            Pop $R0
+            IntCmp $R0 7 copy_ok copy_ok copy_fail
+
+            copy_fail:
+                DetailPrint "================================================"
+                DetailPrint "ECHEC : la copie vers $INSTDIR a echoue (code robocopy $R0)."
+                DetailPrint "================================================"
+                MessageBox MB_OK|MB_ICONSTOP "La copie des fichiers AlChess vers $INSTDIR a echoue (code robocopy $R0).$\r$\n$\r$\nVerifiez l'espace disque disponible et les droits d'ecriture sur %LOCALAPPDATA%, puis relancez cet installeur."
+                Abort
+
+            copy_ok:
+                DetailPrint "  Copie terminee avec succes."
+                Goto end_copy_files
+
+        copy_skip:
+            DetailPrint "Deja lance depuis $INSTDIR — copie sautee."
+
+        end_copy_files:
+    SectionEnd
+
     ; -- Phase Git (issue #88) : depot git + auto-update ----------------------
     ; DOIT s'executer avant SecPython/SecVenv : requirements.txt (utilise par
     ; SecVenv) doit venir du code deja synchronise ici.
# ── Zone modifiée : ligne 1415 (7 ligne(s)) dans l'ancienne version → ligne 1466 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1415,7 +1466,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
 
     ; -- Phase 3 : portage de Get-Python312 / Install-Python312 --------------
     Section "Verification Python" SecPython
-        DetailPrint "Racine de configuration (EXEDIR) : $EXEDIR"
+        DetailPrint "Racine de configuration (EXEDIR) : $INSTDIR"
         DetailPrint "================================================"
         DetailPrint "Recherche de Python ${MIN_PYTHON_MAJOR}.${MIN_PYTHON_MINOR}+..."
         DetailPrint "================================================"
# ── Zone modifiée : ligne 1441 (7 ligne(s)) dans l'ancienne version → ligne 1492 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1441,7 +1492,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
             DetailPrint "================================================"
             DetailPrint "Python detecte : $PythonExe"
             DetailPrint "================================================"
-            DetailPrint "  venv cible : $EXEDIR\${VENV_SUBDIR}"
+            DetailPrint "  venv cible : $INSTDIR\${VENV_SUBDIR}"
             Goto end_python_section
 
         no_python:
# ── Zone modifiée : ligne 1461 (7 ligne(s)) dans l'ancienne version → ligne 1512 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1461,7 +1512,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
             DetailPrint "================================================"
             DetailPrint "Python installe automatiquement avec succes : $PythonExe"
             DetailPrint "================================================"
-            DetailPrint "  venv cible : $EXEDIR\${VENV_SUBDIR}"
+            DetailPrint "  venv cible : $INSTDIR\${VENV_SUBDIR}"
 
         end_python_section:
     SectionEnd
# ── Zone modifiée : ligne 1495 (7 ligne(s)) dans l'ancienne version → ligne 1546 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1495,7 +1546,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
         DetailPrint "================================================"
         DetailPrint "Creation de l'environnement virtuel (venv)"
         DetailPrint "================================================"
-        DetailPrint "  venv cible : $EXEDIR\${VENV_SUBDIR}"
+        DetailPrint "  venv cible : $INSTDIR\${VENV_SUBDIR}"
         DetailPrint "  Python utilise : $PythonExe"
 
         ; -- DIAGNOSTIC #65 (suite #64) ---------------------------------------
# ── Zone modifiée : ligne 1512 (27 ligne(s)) dans l'ancienne version → ligne 1563 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1512,27 +1563,27 @@ SectionGroup "Configuration AlChess" SecGroupConfig
 
         ; Test direct et independant : "$PythonExe" --version, sortie (stdout +
         ; stderr) redirigee dans le fichier log via cmd /c, puis code de sortie.
-        nsExec::ExecToLog 'cmd /c ""$PythonExe" --version >> "$EXEDIR\alchess_install_debug.log" 2>&1"'
+        nsExec::ExecToLog 'cmd /c ""$PythonExe" --version >> "$INSTDIR\alchess_install_debug.log" 2>&1"'
         Pop $R0
         StrCpy $LogMsg "CODE SORTIE python --version : $R0"
         Call LogCheckpoint
 
         ; 1. Le venv existe-t-il deja ? (equivalent Test-Path venv\Scripts\python.exe)
-        IfFileExists "$EXEDIR\${VENV_SUBDIR}\Scripts\python.exe" venv_present venv_needed
+        IfFileExists "$INSTDIR\${VENV_SUBDIR}\Scripts\python.exe" venv_present venv_needed
 
         venv_needed:
             ; 2. Creer le venv. ExecToLog (pas ExecToStack) pour afficher la
             ;    progression : la creation d'un venv prend quelques secondes,
             ;    utile de montrer que ca travaille (comme winget en phase 3bis).
             DetailPrint "Creation du venv en cours (peut prendre quelques secondes)..."
-            nsExec::ExecToLog '"$PythonExe" -m venv "$EXEDIR\${VENV_SUBDIR}"'
+            nsExec::ExecToLog '"$PythonExe" -m venv "$INSTDIR\${VENV_SUBDIR}"'
             Pop $R0  ; code de sortie (ExecToLog ne pousse que le code)
             ; -- DIAGNOSTIC #65 : code de sortie exact (pas 0/non-0 traduit) --
             StrCpy $LogMsg "CODE SORTIE creation venv : $R0"
             Call LogCheckpoint
             ; Le DOSSIER venv existe-t-il (meme vide) ? Distingue "rien cree du
             ; tout" de "dossier cree mais python.exe/pip.exe manquants dedans".
-            IfFileExists "$EXEDIR\${VENV_SUBDIR}\*.*" venv_dir_present venv_dir_absent
+            IfFileExists "$INSTDIR\${VENV_SUBDIR}\*.*" venv_dir_present venv_dir_absent
             venv_dir_present:
                 StrCpy $LogMsg "DOSSIER VENV : PRESENT"
                 Goto venv_dir_logged
# ── Zone modifiée : ligne 1563 (7 ligne(s)) dans l'ancienne version → ligne 1614 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1563,7 +1614,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
         ;    pip du .ps1 (upgrade pip, puis install -r requirements.txt).
         install_deps:
             DetailPrint "Mise a jour de pip..."
-            nsExec::ExecToLog '"$EXEDIR\${VENV_SUBDIR}\Scripts\pip.exe" install --upgrade pip --quiet'
+            nsExec::ExecToLog '"$INSTDIR\${VENV_SUBDIR}\Scripts\pip.exe" install --upgrade pip --quiet'
             Pop $R0  ; code de sortie
             ; -- DIAGNOSTIC #65 : code de sortie exact --
             StrCpy $LogMsg "CODE SORTIE pip upgrade : $R0"
# ── Zone modifiée : ligne 1578 (7 ligne(s)) dans l'ancienne version → ligne 1629 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1578,7 +1629,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
 
         pip_upgrade_ok:
             DetailPrint "Installation des dependances (requirements.txt)..."
-            nsExec::ExecToLog '"$EXEDIR\${VENV_SUBDIR}\Scripts\pip.exe" install -r "$EXEDIR\requirements.txt" --quiet'
+            nsExec::ExecToLog '"$INSTDIR\${VENV_SUBDIR}\Scripts\pip.exe" install -r "$INSTDIR\requirements.txt" --quiet'
             Pop $R0  ; code de sortie
             ; -- DIAGNOSTIC #65 : code de sortie exact --
             StrCpy $LogMsg "CODE SORTIE pip install -r requirements : $R0"
# ── Zone modifiée : ligne 1634 (7 ligne(s)) dans l'ancienne version → ligne 1685 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1634,7 +1685,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
     ;   2 = erreur (script absent, echiquier illisible, etc.)
     Section "Detection Chessnut" SecChessnut
         DetailPrint "Detection du modele Chessnut branche..."
-        nsExec::ExecToLog '"$EXEDIR\${VENV_SUBDIR}\Scripts\python.exe" "$EXEDIR\scripts\detect_chessnut.py"'
+        nsExec::ExecToLog '"$INSTDIR\${VENV_SUBDIR}\Scripts\python.exe" "$INSTDIR\scripts\detect_chessnut.py"'
         Pop $R0
         ${If} $R0 == 0
             DetailPrint "Echiquier detecte et deja reconnu, ou aucun echiquier branche."
# ── Zone modifiée : ligne 1662 (18 ligne(s)) dans l'ancienne version → ligne 1713 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1662,18 +1713,18 @@ SectionGroup "Configuration AlChess" SecGroupConfig
         DetailPrint "================================================"
         DetailPrint "Installation de Stockfish"
         DetailPrint "================================================"
-        DetailPrint "  dossier moteurs : $EXEDIR\${ENGINES_SUBDIR}"
+        DetailPrint "  dossier moteurs : $INSTDIR\${ENGINES_SUBDIR}"
 
         ; Initialiser le flag de succes
         StrCpy $StockfishOK 0
 
         ; Verifier si Stockfish est deja present
-        FindFirst $R8 $R9 "$EXEDIR\${ENGINES_SUBDIR}\stockfish\stockfish*.exe"
+        FindFirst $R8 $R9 "$INSTDIR\${ENGINES_SUBDIR}\stockfish\stockfish*.exe"
         StrCmp $R8 "" check_avx2 already_present
 
         already_present:
             FindClose $R8
-            DetailPrint "Stockfish deja present : $EXEDIR\${ENGINES_SUBDIR}\stockfish\$R9"
+            DetailPrint "Stockfish deja present : $INSTDIR\${ENGINES_SUBDIR}\stockfish\$R9"
             DetailPrint "Installation sautee."
             StrCpy $StockfishOK 1
             Goto end_stockfish
# ── Zone modifiée : ligne 1913 (14 ligne(s)) dans l'ancienne version → ligne 1964 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1913,14 +1964,14 @@ Section "Raccourci bureau" SecShortcut
     ; Reinitialiser le flag d'erreur avant CreateShortcut pour que IfErrors
     ; ne remonte pas une erreur laissee par une instruction anterieure.
     ClearErrors
-    CreateShortcut "$DESKTOP\AlChess.lnk" "$EXEDIR\2-Lancer_AlChess.bat" \
-        "" "$EXEDIR\alchess.ico" 0 SW_SHOWNORMAL "" "Launch AlChess"
+    CreateShortcut "$DESKTOP\AlChess.lnk" "$INSTDIR\2-Lancer_AlChess.bat" \
+        "" "$INSTDIR\alchess.ico" 0 SW_SHOWNORMAL "" "Launch AlChess"
     IfErrors shortcut_failed shortcut_ok
 
     shortcut_failed:
         DetailPrint "AVERTISSEMENT : impossible de creer le raccourci bureau."
         DetailPrint "  Vous pourrez lancer AlChess directement via :"
-        DetailPrint "  $EXEDIR\2-Lancer_AlChess.bat"
+        DetailPrint "  $INSTDIR\2-Lancer_AlChess.bat"
         Goto end_shortcut
 
     shortcut_ok:
