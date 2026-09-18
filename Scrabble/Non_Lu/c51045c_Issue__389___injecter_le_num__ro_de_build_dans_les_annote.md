c51045c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c51045c
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 21:59:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #389 : injecter le numéro de build dans les métadonnées de Scrabble-Setup.exe et Scrabble.exe

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9b94fd6..dab8acf 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 155 (7 ligne(s)) dans l'ancienne version → ligne 155 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -155,7 +155,18 @@ if not errorlevel 1 (
 echo.
 
 REM --- 4. Lancer le build PyInstaller ---------------------------------------
-echo [4/9] Build PyInstaller en cours (peut prendre plusieurs minutes)...
+echo [4/9] Injection du numero de build dans version_info.txt...
+powershell -NoProfile -Command "(Get-Content 'version_info.txt' -Raw) -replace 'BUILD', '!SCRABBLE_BUILD!' | Set-Content 'version_info.txt' -NoNewline"
+if errorlevel 1 (
+    echo.
+    echo ERREUR : l'injection du numero de build dans version_info.txt a echoue.
+    popd
+    popd
+    exit /b 1
+)
+echo Numero de build !SCRABBLE_BUILD! injecte dans version_info.txt. OK.
+echo.
+echo Build PyInstaller en cours (peut prendre plusieurs minutes)...
 call ".venv_build\Scripts\pyinstaller.exe" scrabble.spec -y
 if errorlevel 1 (
     echo.
# (diff du fichier suivant)
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# (index — ignorable)
index 1a1cd22..309767a 100644
# (avant — fichier suivant)
--- a/installeur/scrabble.iss
# (après — fichier suivant)
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 62 (6 ligne(s)) dans l'ancienne version → ligne 62 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -62,6 +62,13 @@ AppId={{EC04D19C-69EA-4116-9EB8-C51A30E56EBA}
 AppName={#MyAppName}
 AppVersion={#ScrabbleBuildInstalle}
 AppPublisher={#MyAppPublisher}
+; Numéro de build visible dans les métadonnées Windows de Scrabble-Setup.exe
+; (clic droit -> Propriétés -> Détails -> Version du fichier), issue #389 :
+; sans cela, impossible de distinguer visuellement deux exécutables sans les
+; ouvrir.
+VersionInfoVersion={#ScrabbleBuildInstalle}.0.0.0
+VersionInfoProductName=Scrabble
+VersionInfoDescription=Scrabble Setup build {#ScrabbleBuildInstalle}
 DefaultDirName={autopf}\{#MyAppName}
 DefaultGroupName={#MyAppName}
 ; Droits administrateur requis (issue #388) : nécessaire pour écrire dans
# (diff du fichier suivant)
diff --git a/scrabble.spec b/scrabble.spec
# (index — ignorable)
index 66e0cf5..e3090dc 100644
# (avant — fichier suivant)
--- a/scrabble.spec
# (après — fichier suivant)
+++ b/scrabble.spec
# ── Zone modifiée : ligne 259 (6 ligne(s)) dans l'ancienne version → ligne 259 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -259,6 +259,11 @@ exe = EXE(
     codesign_identity=None,
     entitlements_file=None,
     icon=os.path.join(RACINE, "assets", "scrabble.ico"),
+    # Métadonnées Windows (clic droit -> Propriétés -> Détails -> Version du
+    # fichier) du .exe produit, issue #389 : version_info.txt à la racine du
+    # dépôt, dont build\rebuild_scrabble.bat substitue le numéro de build réel
+    # avant cet appel PyInstaller.
+    version=os.path.join(RACINE, "version_info.txt"),
     # Désactive le sous-dossier "_internal" (nouveau défaut depuis PyInstaller
     # 6.0) : sys._MEIPASS reste alors le dossier de l'exe lui-même, à côté
     # duquel scrabble.config.RACINE_PROJET écrit config.json/logs/data en mode
# (diff du fichier suivant)
diff --git a/version_info.txt b/version_info.txt
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..ee3ebbd
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/version_info.txt
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,30 @@
+# Métadonnées Windows injectées dans Scrabble.exe par PyInstaller (issue #389).
+#
+# Gabarit texte : le mot-clé ci-dessous (répété 4 fois plus bas, dans filevers/
+# prodvers/FileVersion/ProductVersion) est remplacé par le numéro de build réel
+# (lu dans version.json) par build\rebuild_scrabble.bat avant chaque appel à
+# PyInstaller (voir scrabble.spec, paramètre version= de EXE()). Ne pas
+# committer ce fichier avec un numéro déjà substitué.
+VSVersionInfo(
+  ffi=FixedFileInfo(
+    filevers=(BUILD, 0, 0, 0),
+    prodvers=(BUILD, 0, 0, 0),
+    mask=0x3f,
+    flags=0x0,
+    OS=0x4,
+    fileType=0x1,
+    subtype=0x0,
+    date=(0, 0)
+  ),
+  kids=[
+    StringFileInfo([
+      StringTable(
+        u'040C04B0',
+        [StringStruct(u'FileDescription', u'Scrabble'),
+         StringStruct(u'FileVersion', u'BUILD.0.0.0'),
+         StringStruct(u'ProductName', u'Scrabble'),
+         StringStruct(u'ProductVersion', u'BUILD.0.0.0')])
+    ]),
+    VarFileInfo([VarStruct(u'Translation', [0x040C, 1200])])
+  ]
+)
