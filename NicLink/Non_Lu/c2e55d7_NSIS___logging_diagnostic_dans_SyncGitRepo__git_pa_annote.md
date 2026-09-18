c2e55d7

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c2e55d7
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 17:39:43 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    NSIS : logging diagnostic dans SyncGitRepo (git path + codes retour)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ac2728d..a1f6f58 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installer-exe/alchess_setup.nsi
# ── Version APRÈS ce commit.
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1315 (12 ligne(s)) dans l'ancienne version → ligne 1315 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1315,12 +1315,17 @@ Function SyncGitRepo
     DetailPrint "Synchronisation du code AlChess (Git)"
     DetailPrint "================================================"
 
+    nsExec::ExecToLog 'cmd /c where git >> "$INSTDIR\alchess_install_debug.log" 2>&1'
+    Pop $R0
+
     IfFileExists "$INSTDIR\.git\*.*" repo_present repo_absent
 
     repo_present:
         DetailPrint "  Depot git existant detecte — recherche du dernier tag de release..."
         nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" fetch --tags origin'
         Pop $R0
+        StrCpy $LogMsg "SyncGitRepo git fetch : $R0"
+        Call LogCheckpoint
         IntCmp $R0 0 present_fetch_ok present_fetch_fail present_fetch_fail
 
         present_fetch_fail:
# ── Zone modifiée : ligne 1329 (11 ligne(s)) dans l'ancienne version → ligne 1334 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1329,11 +1334,15 @@ Function SyncGitRepo
 
         present_fetch_ok:
             Call GetLatestTag
+            StrCpy $LogMsg "SyncGitRepo GetLatestTag result : $LatestTag"
+            Call LogCheckpoint
             StrCmp $LatestTag "" present_no_tag 0
 
             DetailPrint "  Dernier tag de release : $LatestTag — checkout..."
             nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" checkout "$LatestTag"'
             Pop $R0
+            StrCpy $LogMsg "SyncGitRepo git checkout : $R0"
+            Call LogCheckpoint
             IntCmp $R0 0 present_checkout_ok present_checkout_fail present_checkout_fail
 
         present_checkout_fail:
# ── Zone modifiée : ligne 1355 (6 ligne(s)) dans l'ancienne version → ligne 1364 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1355,6 +1364,8 @@ Function SyncGitRepo
 
         nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" init'
         Pop $R0
+        StrCpy $LogMsg "SyncGitRepo git init : $R0"
+        Call LogCheckpoint
         IntCmp $R0 0 sync_init_ok sync_init_fail sync_init_fail
 
         sync_init_fail:
# ── Zone modifiée : ligne 1364 (6 ligne(s)) dans l'ancienne version → ligne 1375 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1364,6 +1375,8 @@ Function SyncGitRepo
         sync_init_ok:
             nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" remote add origin https://github.com/AlainDelree/AlChess.git'
             Pop $R0
+            StrCpy $LogMsg "SyncGitRepo git remote add : $R0"
+            Call LogCheckpoint
             IntCmp $R0 0 sync_remote_ok sync_remote_fail sync_remote_fail
 
         sync_remote_fail:
# ── Zone modifiée : ligne 1373 (6 ligne(s)) dans l'ancienne version → ligne 1386 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1373,6 +1386,8 @@ Function SyncGitRepo
         sync_remote_ok:
             nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" fetch --depth=1 --tags origin'
             Pop $R0
+            StrCpy $LogMsg "SyncGitRepo git fetch : $R0"
+            Call LogCheckpoint
             IntCmp $R0 0 sync_fetch_ok sync_fetch_fail sync_fetch_fail
 
         sync_fetch_fail:
# ── Zone modifiée : ligne 1381 (11 ligne(s)) dans l'ancienne version → ligne 1396 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1381,11 +1396,15 @@ Function SyncGitRepo
 
         sync_fetch_ok:
             Call GetLatestTag
+            StrCpy $LogMsg "SyncGitRepo GetLatestTag result : $LatestTag"
+            Call LogCheckpoint
             StrCmp $LatestTag "" sync_no_tag 0
 
             DetailPrint "  Dernier tag de release : $LatestTag — checkout..."
             nsExec::ExecToLog 'cmd /c git -C "$INSTDIR" checkout "$LatestTag"'
             Pop $R0
+            StrCpy $LogMsg "SyncGitRepo git checkout : $R0"
+            Call LogCheckpoint
             IntCmp $R0 0 sync_checkout_ok sync_checkout_fail sync_checkout_fail
 
         sync_checkout_fail:
