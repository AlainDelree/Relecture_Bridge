c8ca1ed

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c8ca1ed
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 02:58:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #90 (suite #89) — auto-update sur dernier tag de release plutot que master
    
    Launcher (2-Lancer_AlChess.bat) : "git pull --ff-only origin master"
    remplace par git fetch --tags + checkout du dernier tag (tri
    version:refname), avec fallback si deja a jour / aucun tag / hors ligne.
    
    NSIS (SyncGitRepo) : meme logique cote installeur — fetch --tags +
    checkout du dernier tag (depot existant), ou init + fetch --depth=1
    --tags + checkout du dernier tag (conversion du dossier ZIP en depot).
    Nouvelle fonction GetLatestTag (FileOpen/FileRead, coherente avec
    TryPy0p). Compilation verifiee avec makensis -WX.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/2-Lancer_AlChess.bat b/2-Lancer_AlChess.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5ba021b..91ea345 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/2-Lancer_AlChess.bat
# ── Version APRÈS ce commit.
+++ b/2-Lancer_AlChess.bat
# ── Zone modifiée : ligne 1 (18 ligne(s)) dans l'ancienne version → ligne 1 (55 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,18 +1,55 @@
 @echo off
-rem --- Verification des mises a jour (issue #88) ---
+rem --- Verification des mises a jour : dernier tag de release (issue #90, suite #89) ---
+rem  Auparavant "git pull --ff-only origin master" (issue #88) : tirait CHAQUE
+rem  commit de master. Pour la securite, on ne tire desormais que les versions
+rem  explicitement taguees (ex: v1.3.0) : fetch des tags, puis checkout du plus
+rem  recent (tri "version:refname", donc le premier resultat = le plus recent).
+rem  Structure en goto (pas de parenthesage imbrique) pour eviter le piege des
+rem  variables lues/ecrites dans le meme bloc () sans "setlocal enabledelayedexpansion".
 echo Verification des mises a jour AlChess...
 where git >nul 2>&1
+if not %errorlevel% equ 0 goto :maj_no_git
+
+cd /d "%~dp0"
+git fetch --tags origin >nul 2>&1
+if not %errorlevel% equ 0 goto :maj_fetch_fail
+
+set "LATEST_TAG="
+for /f "delims=" %%T in ('git tag --sort=-version:refname 2^>nul') do (
+    set "LATEST_TAG=%%T"
+    goto :maj_got_tag
+)
+goto :maj_no_tag
+
+:maj_got_tag
+set "CURRENT_TAG="
+for /f "delims=" %%C in ('git describe --tags --exact-match 2^>nul') do set "CURRENT_TAG=%%C"
+if "%CURRENT_TAG%"=="%LATEST_TAG%" goto :maj_already_latest
+
+git checkout "%LATEST_TAG%" >nul 2>&1
 if %errorlevel% equ 0 (
-    cd /d "%~dp0"
-    git pull --ff-only origin master >nul 2>&1
-    if %errorlevel% equ 0 (
-        echo Mise a jour OK.
-    ) else (
-        echo Mise a jour impossible ^(hors ligne ou conflit local^) - version locale conservee.
-    )
+    echo Mise a jour OK ^(version %LATEST_TAG%^).
 ) else (
-    echo Git non trouve - verification des mises a jour ignoree.
+    echo Mise a jour impossible ^(checkout %LATEST_TAG% echoue^) - version locale conservee.
 )
+goto :maj_fin
+
+:maj_already_latest
+echo Deja a jour ^(version %LATEST_TAG%^).
+goto :maj_fin
+
+:maj_no_tag
+echo Aucun tag de version trouve - version locale conservee.
+goto :maj_fin
+
+:maj_fetch_fail
+echo Mise a jour impossible ^(hors ligne ou depot local^) - version locale conservee.
+goto :maj_fin
+
+:maj_no_git
+echo Git non trouve - verification des mises a jour ignoree.
+
+:maj_fin
 rem --- Fin verification ---
 
 rem ============================================================================
# (diff du fichier suivant)
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# (index — ignorable)
index 86f20f7..a20a1aa 100644
# (avant — fichier suivant)
--- a/installer-exe/alchess_setup.nsi
# (après — fichier suivant)
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 41 (14 ligne(s)) dans l'ancienne version → ligne 41 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -41,14 +41,16 @@
 ;                              fin. Le code des 6 phases est desormais COMPLET.
 ;                              => VALIDATION VM WINDOWS RESTE A FAIRE (aucune
 ;                                 phase n'a jamais tourne sur un vrai Windows).
-;  Phase 7 (#88) : Section "Synchronisation Git" (SecGit), executee en tete du
-;                  SectionGroup. Detecte/installe git, puis git pull (depot
-;                  deja clone) ou git clone (dossier vide) sur $EXEDIR — voir
-;                  fonctions EnsureGitInstalled / SyncGitRepo. ADAPTATION : la
-;                  demande #88 visait $INSTDIR et un remplacement de ZIP ; ce
-;                  fichier n'a ni l'un ni l'autre (architecture $EXEDIR
-;                  co-localise, cf. phase 1 ci-dessus), donc le clone ne peut
-;                  aboutir que sur un dossier vide — non teste sur Windows.
+;  Phase 7 (#88, #89, #90) : Section "Synchronisation Git" (SecGit), executee
+;                  en tete du SectionGroup. Detecte/installe git, puis fetch
+;                  des tags + checkout du dernier tag de release (pas master,
+;                  pour la securite — issue #90, suite #89) sur $EXEDIR — voir
+;                  fonctions EnsureGitInstalled / GetLatestTag / SyncGitRepo.
+;                  ADAPTATION : la demande #88 visait $INSTDIR et un
+;                  remplacement de ZIP ; ce fichier n'a ni l'un ni l'autre
+;                  (architecture $EXEDIR co-localise, cf. phase 1 ci-dessus),
+;                  donc SyncGitRepo convertit le dossier en depot git plutot
+;                  que d'y faire un "git clone" — non teste sur Windows.
 ;
 ;  --- AVERTISSEMENT PHASE 3 --------------------------------------------------
 ;  Cette section SecPython a ete validee uniquement par COMPILATION (makensis
# ── Zone modifiée : ligne 95 (6 ligne(s)) dans l'ancienne version → ligne 97 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -95,6 +97,9 @@ Var VCRedistOK       ; 1 si VC++ installe avec succes, 0 sinon
 ; Variable pour les points de controle horodates (diagnostic #64, suite #62)
 Var LogMsg           ; Message a ecrire dans alchess_install_debug.log
 
+; Variable pour la synchronisation Git sur tag de release (issue #90, suite #89)
+Var LatestTag        ; Dernier tag de version trouve (ex: "v1.3.0"), "" si aucun
+
 ; ---------------------------------------------------------------------------
 ;  Variables de chemin — equivalents des chemins de install_alchess.ps1.
 ;  Toutes les references sont relatives a $EXEDIR (dossier du .exe execute),
# ── Zone modifiée : ligne 1226 (18 ligne(s)) dans l'ancienne version → ligne 1231 (79 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1226,18 +1231,79 @@ Function EnsureGitInstalled
             Return
 FunctionEnd
 
+; ---------------------------------------------------------------------------
+;  GetLatestTag
+;  Execute "git tag --sort=-version:refname" dans $EXEDIR (tri decroissant :
+;  le plus recent en premier), redirige la sortie vers un fichier temporaire
+;  et n'en lit que la premiere ligne — memes FileOpen/FileRead/FileClose que
+;  TryPy0p ci-dessus, pour rester coherent avec le reste du fichier plutot que
+;  de jongler avec des boucles "for /f" imbriquees dans une commande nsExec
+;  (issue #90, suite #89).
+;  Sortie : $LatestTag = nom du tag le plus recent (ex. "v1.3.0"), ou "" si
+;  aucun tag n'existe ou si la commande a echoue.
+; ---------------------------------------------------------------------------
+Function GetLatestTag
+    StrCpy $LatestTag ""
+
+    nsExec::ExecToStack 'cmd /c git -C "$EXEDIR" tag --sort=-version:refname > "$TEMP\alchess_tags.txt" 2>NUL'
+    Pop $R0  ; exit code
+    Pop $R1  ; output (vide car redirige)
+    IntCmp $R0 0 tags_listed tags_list_fail tags_list_fail
+
+    tags_list_fail:
+        Delete "$TEMP\alchess_tags.txt"
+        Return
+
+    tags_listed:
+        FileOpen $R2 "$TEMP\alchess_tags.txt" r
+        ${If} $R2 == ""
+            Delete "$TEMP\alchess_tags.txt"
+            Return
+        ${EndIf}
+
+        FileRead $R2 $TempLine
+        FileClose $R2
+        Delete "$TEMP\alchess_tags.txt"
+
+        StrCmp $TempLine "" no_tag_found 0
+
+        ; FileRead conserve la fin de ligne ($\r$\n) : la retirer.
+        StrLen $R3 $TempLine
+        ${If} $R3 > 0
+            IntOp $R3 $R3 - 1
+            trim_tag_loop:
+                IntCmp $R3 0 trim_tag_done 0 trim_tag_done
+                StrCpy $R4 $TempLine 1 $R3
+                StrCmp $R4 "$\r" do_trim_tag 0
+                StrCmp $R4 "$\n" do_trim_tag 0
+                Goto trim_tag_done
+                do_trim_tag:
+                    StrCpy $TempLine $TempLine $R3
+                    IntOp $R3 $R3 - 1
+                    Goto trim_tag_loop
+        ${EndIf}
+        trim_tag_done:
+        StrCpy $LatestTag $TempLine
+        Return
+
+    no_tag_found:
+        Return
+FunctionEnd
+
 ; ---------------------------------------------------------------------------
 ;  SyncGitRepo
-;  Transforme $EXEDIR en depot git a jour : "git pull --ff-only" si $EXEDIR
-;  est deja un depot (dossier .git present), sinon convertit le dossier
-;  existant en depot git via "git init" + "git remote add" + "git fetch
-;  --depth=1" + "git reset --hard" (issue #89, suite #88) — "git clone"
-;  ne peut jamais aboutir ici car $EXEDIR est deja rempli par le ZIP de
-;  release (git refuse de cloner dans un dossier non vide). Chaque etape
-;  est testee individuellement ; en cas d'echec sur l'une d'elles, on
-;  logue l'erreur et on Return SANS Abort (voir note d'adaptation en tete
-;  de section) — l'app deja presente reste utilisable, seule la mise a
-;  jour auto est indisponible tant que $EXEDIR n'est pas un vrai clone git.
+;  Transforme $EXEDIR en depot git a jour sur le DERNIER TAG DE RELEASE (pas
+;  master : pour la securite, on ne tire que les versions explicitement
+;  taguees — issue #90, suite #89) : fetch des tags + checkout du plus recent
+;  si $EXEDIR est deja un depot (dossier .git present), sinon convertit le
+;  dossier existant en depot git via "git init" + "git remote add" + "git
+;  fetch --depth=1 --tags" + checkout du dernier tag — "git clone" ne peut
+;  jamais aboutir ici car $EXEDIR est deja rempli par le ZIP de release (git
+;  refuse de cloner dans un dossier non vide). Chaque etape est testee
+;  individuellement ; en cas d'echec sur l'une d'elles, on logue l'erreur et
+;  on Return SANS Abort (voir note d'adaptation en tete de section) — l'app
+;  deja presente reste utilisable, seule la mise a jour auto est indisponible
+;  tant que $EXEDIR n'est pas un vrai clone git avec au moins un tag distant.
 ; ---------------------------------------------------------------------------
 Function SyncGitRepo
     DetailPrint "================================================"
# ── Zone modifiée : ligne 1247 (25 ligne(s)) dans l'ancienne version → ligne 1313 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1247,25 +1313,42 @@ Function SyncGitRepo
     IfFileExists "$EXEDIR\.git\*.*" repo_present repo_absent
 
     repo_present:
-        DetailPrint "  Depot git existant detecte — mise a jour (git pull --ff-only)..."
-        nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" pull --ff-only origin master'
+        DetailPrint "  Depot git existant detecte — recherche du dernier tag de release..."
+        nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" fetch --tags origin'
         Pop $R0
-        IntCmp $R0 0 pull_ok pull_fail pull_fail
+        IntCmp $R0 0 present_fetch_ok present_fetch_fail present_fetch_fail
+
+        present_fetch_fail:
+            DetailPrint "  AVERTISSEMENT : git fetch --tags a echoue (code $R0) — version locale conservee."
+            Return
+
+        present_fetch_ok:
+            Call GetLatestTag
+            StrCmp $LatestTag "" present_no_tag 0
 
-        pull_fail:
-            DetailPrint "  AVERTISSEMENT : git pull a echoue (code $R0) — version locale conservee."
+            DetailPrint "  Dernier tag de release : $LatestTag — checkout..."
+            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" checkout "$LatestTag"'
+            Pop $R0
+            IntCmp $R0 0 present_checkout_ok present_checkout_fail present_checkout_fail
+
+        present_checkout_fail:
+            DetailPrint "  AVERTISSEMENT : git checkout a echoue (code $R0) — version locale conservee."
+            Return
+
+        present_checkout_ok:
+            DetailPrint "  Code AlChess a jour (version $LatestTag)."
             Return
 
-        pull_ok:
-            DetailPrint "  Code AlChess a jour."
+        present_no_tag:
+            DetailPrint "  AVERTISSEMENT : aucun tag de version trouve sur le depot distant — version locale conservee."
             Return
 
     repo_absent:
         ; $EXEDIR est deja rempli par le ZIP de release : "git clone" ne peut
         ; jamais y aboutir (git refuse un dossier non vide). On convertit donc
-        ; le dossier existant en depot git : init + remote add + fetch (shallow)
-        ; + reset --hard sur origin/master (issue #89, suite #88).
-        DetailPrint "  Aucun depot git dans $EXEDIR — conversion en depot (init+fetch+reset)..."
+        ; le dossier existant en depot git : init + remote add + fetch (shallow,
+        ; tags inclus) + checkout du dernier tag de release (issue #90, suite #89).
+        DetailPrint "  Aucun depot git dans $EXEDIR — conversion en depot (init+fetch+checkout tag)..."
 
         nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" init'
         Pop $R0
# ── Zone modifiée : ligne 1285 (7 ligne(s)) dans l'ancienne version → ligne 1368 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1285,7 +1368,7 @@ Function SyncGitRepo
             Return
 
         sync_remote_ok:
-            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" fetch --depth=1 origin master'
+            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" fetch --depth=1 --tags origin'
             Pop $R0
             IntCmp $R0 0 sync_fetch_ok sync_fetch_fail sync_fetch_fail
 
# ── Zone modifiée : ligne 1294 (16 ligne(s)) dans l'ancienne version → ligne 1377 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1294,16 +1377,24 @@ Function SyncGitRepo
             Return
 
         sync_fetch_ok:
-            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" reset --hard origin/master'
+            Call GetLatestTag
+            StrCmp $LatestTag "" sync_no_tag 0
+
+            DetailPrint "  Dernier tag de release : $LatestTag — checkout..."
+            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" checkout "$LatestTag"'
             Pop $R0
-            IntCmp $R0 0 sync_reset_ok sync_reset_fail sync_reset_fail
+            IntCmp $R0 0 sync_checkout_ok sync_checkout_fail sync_checkout_fail
+
+        sync_checkout_fail:
+            DetailPrint "  AVERTISSEMENT : git checkout a echoue (code $R0) — l'application deja presente est conservee."
+            Return
 
-        sync_reset_fail:
-            DetailPrint "  AVERTISSEMENT : git reset --hard a echoue (code $R0) — l'application deja presente est conservee."
+        sync_checkout_ok:
+            DetailPrint "  Depot git initialise avec succes : $EXEDIR est maintenant un vrai clone AlChess (version $LatestTag)."
             Return
 
-        sync_reset_ok:
-            DetailPrint "  Depot git initialise avec succes : $EXEDIR est maintenant un vrai clone AlChess."
+        sync_no_tag:
+            DetailPrint "  AVERTISSEMENT : aucun tag de version trouve — depot git initialise sans checkout, application deja presente conservee."
             Return
 FunctionEnd
 
