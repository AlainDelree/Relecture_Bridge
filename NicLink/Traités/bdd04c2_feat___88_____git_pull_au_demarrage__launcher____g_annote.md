bdd04c2

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bdd04c2
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 01:43:00 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: #88 — git pull au demarrage (launcher) + git clone/pull dans l'installeur NSIS
    
    2-Lancer_AlChess.bat : bloc git pull --ff-only silencieux en tete de fichier,
    tolerant a l'absence de git ou de depot (fallback version locale).
    
    alchess_setup.nsi : nouvelle Section "Synchronisation Git" (SecGit), executee
    en tete du SectionGroup, avant SecPython/SecVenv. EnsureGitInstalled detecte
    git et l'installe via winget si absent (meme pattern que Python phase 3bis).
    SyncGitRepo fait git pull --ff-only si $EXEDIR est deja un depot, sinon tente
    un git clone (n'aboutit que sur dossier vide, sans Abort en cas d'echec).
    
    Adaptation assumee vs la demande #88 : ce .nsi n'a pas d'InstallDir ni
    d'extraction ZIP de l'app (architecture $EXEDIR co-localise, cf. phase 1) —
    SyncGitRepo utilise $EXEDIR partout ou la demande parlait de $INSTDIR. Voir
    commentaires de tete de section pour le detail.
    
    Compile OK (makensis -WX, Linux) — non teste sur Windows.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/2-Lancer_AlChess.bat b/2-Lancer_AlChess.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0054735..5ba021b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/2-Lancer_AlChess.bat
# ── Version APRÈS ce commit.
+++ b/2-Lancer_AlChess.bat
# ── Zone modifiée : ligne 1 (4 ligne(s)) dans l'ancienne version → ligne 1 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,4 +1,20 @@
 @echo off
+rem --- Verification des mises a jour (issue #88) ---
+echo Verification des mises a jour AlChess...
+where git >nul 2>&1
+if %errorlevel% equ 0 (
+    cd /d "%~dp0"
+    git pull --ff-only origin master >nul 2>&1
+    if %errorlevel% equ 0 (
+        echo Mise a jour OK.
+    ) else (
+        echo Mise a jour impossible ^(hors ligne ou conflit local^) - version locale conservee.
+    )
+) else (
+    echo Git non trouve - verification des mises a jour ignoree.
+)
+rem --- Fin verification ---
+
 rem ============================================================================
 rem  2-Lancer_AlChess.bat  --  Lanceur AlChess, 100%% batch pur (issue #70)
 rem ----------------------------------------------------------------------------
# (diff du fichier suivant)
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# (index — ignorable)
index 9606ddc..4cd917f 100644
# (avant — fichier suivant)
--- a/installer-exe/alchess_setup.nsi
# (après — fichier suivant)
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 41 (6 ligne(s)) dans l'ancienne version → ligne 41 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -41,6 +41,14 @@
 ;                              fin. Le code des 6 phases est desormais COMPLET.
 ;                              => VALIDATION VM WINDOWS RESTE A FAIRE (aucune
 ;                                 phase n'a jamais tourne sur un vrai Windows).
+;  Phase 7 (#88) : Section "Synchronisation Git" (SecGit), executee en tete du
+;                  SectionGroup. Detecte/installe git, puis git pull (depot
+;                  deja clone) ou git clone (dossier vide) sur $EXEDIR — voir
+;                  fonctions EnsureGitInstalled / SyncGitRepo. ADAPTATION : la
+;                  demande #88 visait $INSTDIR et un remplacement de ZIP ; ce
+;                  fichier n'a ni l'un ni l'autre (architecture $EXEDIR
+;                  co-localise, cf. phase 1 ci-dessus), donc le clone ne peut
+;                  aboutir que sur un dossier vide — non teste sur Windows.
 ;
 ;  --- AVERTISSEMENT PHASE 3 --------------------------------------------------
 ;  Cette section SecPython a ete validee uniquement par COMPILATION (makensis
# ── Zone modifiée : ligne 1128 (6 ligne(s)) dans l'ancienne version → ligne 1136 (147 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1128,6 +1136,147 @@ Function TryStockfishVariant
             Return
 FunctionEnd
 
+; ============================================================================
+;  FONCTIONS UTILITAIRES POUR GIT (issue #88 — auto-update via git pull)
+; ============================================================================
+;  Contexte : le lanceur 2-Lancer_AlChess.bat fait desormais un "git pull"
+;  silencieux a chaque demarrage (issue #88) pour que les mises a jour
+;  d'AlChess arrivent sans telechargement manuel. Pour que ce pull fonctionne,
+;  $EXEDIR doit etre un vrai depot git — ces fonctions detectent/installent
+;  git, puis transforment $EXEDIR en depot (clone si absent, pull sinon).
+;
+;  ADAPTATION A L'ARCHITECTURE REELLE (ecart assume avec la demande #88) :
+;  la demande #88 parle de $INSTDIR et de remplacer "l'extraction ZIP" de
+;  l'app par un git clone. Ce .nsi n'a PAS d'InstallDir ni d'extraction ZIP
+;  de l'app (voir architecture en tete de fichier, issue #52) : il se
+;  co-localise sur $EXEDIR, dossier DEJA rempli par l'app (ZIP de release
+;  extrait manuellement par l'utilisateur avant de lancer AlChess_Setup.exe).
+;  SyncGitRepo utilise donc $EXEDIR partout ou la demande disait $INSTDIR, et
+;  NE FAIT PAS Abort si le clone echoue parce que $EXEDIR est deja rempli
+;  (cas actuel normal) : le code deja present reste utilise tel quel, sans
+;  auto-update tant que $EXEDIR n'est pas un vrai clone git. Un vrai clone
+;  "premiere installation" necessitera un futur chantier de packaging
+;  (bootstrapper minimal livre seul, sans le ZIP de l'app) — voir issue #88.
+; ---------------------------------------------------------------------------
+
+; ---------------------------------------------------------------------------
+;  EnsureGitInstalled
+;  Teste "git --version" ; si absent, installe via winget (meme pattern que
+;  InstallPython312NSIS, phase 3bis, issue #60). Abort avec message clair si
+;  git reste indisponible apres tentative winget.
+; ---------------------------------------------------------------------------
+Function EnsureGitInstalled
+    DetailPrint "================================================"
+    DetailPrint "Verification de Git"
+    DetailPrint "================================================"
+
+    nsExec::ExecToStack 'cmd /c git --version'
+    Pop $R0
+    Pop $R1
+    IntCmp $R0 0 git_present git_absent git_absent
+
+    git_present:
+        DetailPrint "  Git detecte : $R1"
+        Return
+
+    git_absent:
+        DetailPrint "  Git non trouve. Tentative d'installation via winget..."
+        nsExec::ExecToStack 'cmd /c winget --version'
+        Pop $R0
+        Pop $R1
+        IntCmp $R0 0 winget_available winget_unavailable winget_unavailable
+
+        winget_unavailable:
+            DetailPrint "================================================"
+            DetailPrint "ECHEC : ni Git ni winget ne sont disponibles."
+            DetailPrint "================================================"
+            MessageBox MB_OK|MB_ICONSTOP "Git n'est pas installe et winget n'est pas disponible pour l'installer automatiquement.$\r$\n$\r$\nInstallez Git manuellement depuis :$\r$\nhttps://git-scm.com/download/win$\r$\n$\r$\npuis relancez cet installeur."
+            Abort
+
+        winget_available:
+            DetailPrint "  Installation de Git via winget (le telechargement peut prendre un moment)..."
+            nsExec::ExecToLog 'cmd /c winget install --id Git.Git -e --silent --accept-source-agreements --accept-package-agreements'
+            Pop $R0
+            IntCmp $R0 0 winget_git_ok winget_git_fail winget_git_fail
+
+        winget_git_fail:
+            DetailPrint "================================================"
+            DetailPrint "ECHEC : l'installation de Git via winget a echoue (code $R0)."
+            DetailPrint "================================================"
+            MessageBox MB_OK|MB_ICONSTOP "L'installation de Git via winget a echoue (code $R0).$\r$\n$\r$\nInstallez Git manuellement depuis :$\r$\nhttps://git-scm.com/download/win$\r$\n$\r$\npuis relancez cet installeur."
+            Abort
+
+        winget_git_ok:
+            ; PATH pas forcement rafraichi dans ce process (meme remarque que
+            ; pour Python, phase 3bis) : re-tester directement.
+            nsExec::ExecToStack 'cmd /c git --version'
+            Pop $R0
+            Pop $R1
+            IntCmp $R0 0 git_now_ok git_still_missing git_still_missing
+
+        git_still_missing:
+            DetailPrint "================================================"
+            DetailPrint "Git installe mais pas encore detecte dans ce process."
+            DetailPrint "================================================"
+            MessageBox MB_OK|MB_ICONEXCLAMATION "Git a ete installe mais n'est pas encore detecte par l'installeur.$\r$\n$\r$\nRedemarrez votre PC puis relancez cet installeur."
+            Abort
+
+        git_now_ok:
+            DetailPrint "  Git installe et detecte : $R1"
+            Return
+FunctionEnd
+
+; ---------------------------------------------------------------------------
+;  SyncGitRepo
+;  Transforme $EXEDIR en depot git a jour : "git pull --ff-only" si $EXEDIR
+;  est deja un depot (dossier .git present), sinon tente un "git clone".
+;  Le clone n'aboutit que si $EXEDIR est vide (dossier "co-localise" actuel,
+;  deja rempli par le ZIP de release) : dans ce cas on logue et on continue
+;  SANS Abort (voir note d'adaptation en tete de section) — l'app deja
+;  presente reste utilisee telle quelle, seule la mise a jour auto est
+;  indisponible tant que $EXEDIR n'est pas un vrai clone git.
+; ---------------------------------------------------------------------------
+Function SyncGitRepo
+    DetailPrint "================================================"
+    DetailPrint "Synchronisation du code AlChess (Git)"
+    DetailPrint "================================================"
+
+    IfFileExists "$EXEDIR\.git\*.*" repo_present repo_absent
+
+    repo_present:
+        DetailPrint "  Depot git existant detecte — mise a jour (git pull --ff-only)..."
+        nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" pull --ff-only origin master'
+        Pop $R0
+        IntCmp $R0 0 pull_ok pull_fail pull_fail
+
+        pull_fail:
+            DetailPrint "  AVERTISSEMENT : git pull a echoue (code $R0) — version locale conservee."
+            Return
+
+        pull_ok:
+            DetailPrint "  Code AlChess a jour."
+            Return
+
+    repo_absent:
+        DetailPrint "  Aucun depot git dans $EXEDIR — tentative de clonage..."
+        nsExec::ExecToLog 'cmd /c git clone --branch master https://github.com/AlainDelree/AlChess.git "$EXEDIR"'
+        Pop $R0
+        IntCmp $R0 0 clone_ok clone_fail clone_fail
+
+        clone_fail:
+            ; Cas normal actuel : $EXEDIR deja rempli par le ZIP de release
+            ; (git refuse de cloner dans un dossier non vide). Non bloquant :
+            ; l'app deja presente reste utilisee, simplement sans auto-update
+            ; tant qu'elle n'a pas ete (re)installee via un vrai clone.
+            DetailPrint "  Clonage impossible (code $R0) — dossier probablement deja rempli."
+            DetailPrint "  L'application deja presente est conservee (pas de mise a jour automatique)."
+            Return
+
+        clone_ok:
+            DetailPrint "  Code AlChess clone avec succes."
+            Return
+FunctionEnd
+
 ; ============================================================================
 ;  SECTIONS DE CONFIGURATION
 ;  Toutes co-localisees sur $EXEDIR. Remplies progressivement (phases 3-5).
# ── Zone modifiée : ligne 1135 (6 ligne(s)) dans l'ancienne version → ligne 1284 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1135,6 +1284,14 @@ FunctionEnd
 
 SectionGroup "Configuration AlChess" SecGroupConfig
 
+    ; -- Phase Git (issue #88) : depot git + auto-update ----------------------
+    ; DOIT s'executer avant SecPython/SecVenv : requirements.txt (utilise par
+    ; SecVenv) doit venir du code deja synchronise ici.
+    Section "Synchronisation Git" SecGit
+        Call EnsureGitInstalled
+        Call SyncGitRepo
+    SectionEnd
+
     ; -- Phase 3 : portage de Get-Python312 / Install-Python312 --------------
     Section "Verification Python" SecPython
         DetailPrint "Racine de configuration (EXEDIR) : $EXEDIR"
