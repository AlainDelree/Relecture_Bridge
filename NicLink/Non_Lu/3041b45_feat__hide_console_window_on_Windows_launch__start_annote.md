3041b45

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3041b45
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 22:38:39 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: hide console window on Windows launch (start_silent.vbs)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5d9c6eb..041766b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installer-exe/alchess_setup.nsi
# ── Version APRÈS ce commit.
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1942 (8 ligne(s)) dans l'ancienne version → ligne 1942 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1942,8 +1942,8 @@ Section "Raccourci bureau" SecShortcut
     ; Reinitialiser le flag d'erreur avant CreateShortcut pour que IfErrors
     ; ne remonte pas une erreur laissee par une instruction anterieure.
     ClearErrors
-    CreateShortcut "$DESKTOP\AlChess.lnk" "$INSTDIR\2-Lancer_AlChess.bat" \
-        "" "$INSTDIR\alchess.ico" 0 SW_SHOWNORMAL "" "Launch AlChess"
+    CreateShortcut "$DESKTOP\AlChess.lnk" "wscript.exe" \
+        '"$INSTDIR\start_silent.vbs"' "$INSTDIR\alchess.ico" 0 SW_SHOWNORMAL "" "Launch AlChess"
     IfErrors shortcut_failed shortcut_ok
 
     shortcut_failed:
# (diff du fichier suivant)
diff --git a/make_release.sh b/make_release.sh
# (index — ignorable)
index cc026a6..d9b270e 100755
# (avant — fichier suivant)
--- a/make_release.sh
# (après — fichier suivant)
+++ b/make_release.sh
# ── Zone modifiée : ligne 57 (6 ligne(s)) dans l'ancienne version → ligne 57 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -57,6 +57,7 @@ INCLUDE=(
   bootstrap_linux.sh
   1-Installer.bat
   2-Lancer_AlChess.bat
+  start_silent.vbs
   install_alchess.ps1
   start_alchess.ps1
   99-chessnutair.rules.example
# (diff du fichier suivant)
diff --git a/start_silent.vbs b/start_silent.vbs
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..3435756
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/start_silent.vbs
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,13 @@
+' Lance 2-Lancer_AlChess.bat sans afficher de fenetre console.
+' Le log applicatif va deja dans alchess_log.txt, la console est inutile
+' en usage normal.
+
+Dim objShell, objFSO, strFolder, strBat
+
+Set objShell = CreateObject("WScript.Shell")
+Set objFSO = CreateObject("Scripting.FileSystemObject")
+
+strFolder = objFSO.GetParentFolderName(WScript.ScriptFullName)
+strBat = strFolder & "\2-Lancer_AlChess.bat"
+
+objShell.Run """" & strBat & """", 0, False
