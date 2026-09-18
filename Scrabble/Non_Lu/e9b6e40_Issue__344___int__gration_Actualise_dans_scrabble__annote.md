e9b6e40

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e9b6e40
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 01:32:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #344 : intégration Actualise dans scrabble.iss + version.json
    
    Actualise (AlainDelree/Actualise) devient le point d'entrée utilisateur :
    il met Scrabble à jour depuis les GitHub Releases avant de le lancer.
    
    - version.json : build/sha256 consommés par Actualise pour détecter les
      nouvelles releases (sha256 à remplir manuellement après publication).
    - scrabble.iss [Files] : embarque Actualise.exe (déposé par
      rebuild_scrabble.bat dans C:\Temp\ScrabbleBuild\) vers {sd}\Actualise\.
    - scrabble.iss [Dirs] : crée {sd}\Actualise\ et {sd}\Actualise\attente\.
    - scrabble.iss [Icons] : les raccourcis Bureau/menu Démarrer pointent
      désormais vers Actualise.exe, jamais directement vers Scrabble.exe.
    - scrabble.iss [Code] : génère {sd}\Actualise\config.json en post-install
      (dépôts GitHub, répertoire d'installation réel, zone d'attente ;
      topic_ntfy laissé vide, à renseigner manuellement).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5d861df..23320cb 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 16 (6 ligne(s)) dans l'ancienne version → ligne 16 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -16,6 +16,14 @@
 #define MyAppPublisher "Alain Delree"
 #define MyAppExeName "Scrabble.exe"
 #define MyDistDir "..\dist\Scrabble"
+; Actualise (dépôt AlainDelree/Actualise) est l'updater autonome qui met
+; Scrabble à jour depuis les GitHub Releases avant de le lancer (issue #344,
+; architecture complète dans CONCEPTION.md du dépôt Actualise). Le raccourci
+; utilisateur doit pointer vers lui, jamais directement vers Scrabble.exe.
+#define MyActualiseExeName "Actualise.exe"
+; Déposé par build\rebuild_scrabble.bat avant l'appel à ISCC.
+#define MyActualiseExeSource "C:\Temp\ScrabbleBuild\Actualise.exe"
+#define MyActualiseDir "{sd}\Actualise"
 
 [Setup]
 ; GUID fixe et unique à l'application : NE PAS régénérer (sert à Windows pour
# ── Zone modifiée : ligne 60 (10 ligne(s)) dans l'ancienne version → ligne 68 (64 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -60,10 +68,64 @@ Name: "french"; MessagesFile: "compiler:Languages\French.isl"
 ; dans l'installeur : un nouvel utilisateur hériterait sinon des préférences/
 ; de l'historique de parties de quelqu'un d'autre dès la première ouverture.
 Source: "{#MyDistDir}\*"; DestDir: "{app}"; Excludes: "config.json,logs\*,data\parties.db,data\*.db"; Flags: ignoreversion recursesubdirs createallsubdirs
+; Actualise.exe : updater autonome, installé à côté de Scrabble (pas dans
+; {app}) car il survit aux mises à jour/réinstallations de Scrabble lui-même.
+Source: "{#MyActualiseExeSource}"; DestDir: "{#MyActualiseDir}"; Flags: ignoreversion
+
+[Dirs]
+Name: "{#MyActualiseDir}"
+Name: "{#MyActualiseDir}\attente"
 
 [Icons]
-Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
-Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
+; Les raccourcis pointent vers Actualise.exe (jamais directement vers
+; Scrabble.exe) : Actualise met Scrabble à jour depuis les GitHub Releases
+; avant de le lancer, à chaque démarrage.
+Name: "{autoprograms}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"
+Name: "{autodesktop}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"
+
+[Code]
+// Génère le config.json d'Actualise, consommé par Actualise.exe au
+// lancement pour savoir quel dépôt GitHub surveiller, où est installé
+// Scrabble et où stocker les archives téléchargées (issue #344).
+function EchapperJSON(const Texte: String): String;
+begin
+  Result := Texte;
+  StringChangeEx(Result, '\', '\\', True);
+end;
+
+procedure CreerConfigActualise();
+var
+  DossierActualise, RepertoireInstallation, ZoneAttente, Contenu: String;
+begin
+  DossierActualise := ExpandConstant('{#MyActualiseDir}') + '\';
+  RepertoireInstallation := ExpandConstant('{app}') + '\';
+  ZoneAttente := DossierActualise + 'attente\';
+
+  Contenu :=
+    '{' + #13#10 +
+    '  "actualise": {' + #13#10 +
+    '    "build_installe": 1,' + #13#10 +
+    '    "depot_github": "AlainDelree/Actualise"' + #13#10 +
+    '  },' + #13#10 +
+    '  "application_cible": {' + #13#10 +
+    '    "nom": "Scrabble",' + #13#10 +
+    '    "depot_github": "AlainDelree/Scrabble",' + #13#10 +
+    '    "build_installe": 1,' + #13#10 +
+    '    "repertoire_installation": "' + EchapperJSON(RepertoireInstallation) + '",' + #13#10 +
+    '    "executable": "Scrabble.exe"' + #13#10 +
+    '  },' + #13#10 +
+    '  "zone_attente": "' + EchapperJSON(ZoneAttente) + '",' + #13#10 +
+    '  "topic_ntfy": ""' + #13#10 +
+    '}' + #13#10;
+
+  SaveStringToFile(DossierActualise + 'config.json', Contenu, False);
+end;
+
+procedure CurStepChanged(CurStep: TSetupStep);
+begin
+  if CurStep = ssPostInstall then
+    CreerConfigActualise();
+end;
 
 [UninstallDelete]
 ; Nettoyage des fichiers générés à l'usage par le jeu (config.json, logs/,
# (diff du fichier suivant)
diff --git a/version.json b/version.json
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..bcb38fa
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/version.json
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (1 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1 @@
+{"build": 1, "sha256": "SHA256_A_REMPLIR"}
