ebaad59

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ebaad59
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 15:09:02 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #407 : retrait d'Actualise du setup InnoSetup Scrabble
    
    Actualise ne sera plus embarqué dans le setup Scrabble : il sera distribué
    via son propre Actualise-Setup.exe indépendant, et le jeu le lance déjà au
    démarrage s'il est présent (main.py). Adapte scrabble.iss en conséquence :
    - retrait de la copie [Files] d'Actualise vers C:\Actualise\
    - retrait de #define MyActualiseSrcDir / ActualiseVersion / MyActualiseExeName
    - retrait du sous-dossier C:\Actualise\attente ([Dirs])
    - retrait de CreerConfigActualiseSiAbsent et CreerActualisePathTxt ([Code])
    - les raccourcis (menu Démarrer/Bureau) pointent désormais directement vers
      Scrabble.exe, sans passer par Actualise.exe --config scrabble
    
    Conservés inchangés : création de C:\Actualise\ (toujours nécessaire pour
    config_scrabble.json), CreerConfigScrabble, et toute la logique d'instance
    partagée (SupprimerAncienneInstanceActualise, ExisteAutreConfigActualise,
    CurUninstallStepChanged).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 73ce981..efa3230 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 16 (32 ligne(s)) dans l'ancienne version → ligne 16 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -16,32 +16,19 @@
 #define MyAppExeName "Scrabble.exe"
 #define MyDistDir "..\dist\Scrabble"
 ; Actualise (dépôt AlainDelree/Actualise) est l'updater autonome qui met
-; Scrabble à jour depuis les GitHub Releases avant de le lancer (issue #344,
-; architecture complète dans CONCEPTION.md du dépôt Actualise). Le raccourci
-; utilisateur doit pointer vers lui, jamais directement vers Scrabble.exe.
+; Scrabble à jour depuis les GitHub Releases avant de le lancer. Depuis
+; l'issue #407, il n'est plus embarqué dans ce setup : il est distribué via
+; son propre Actualise-Setup.exe indépendant. Le jeu le lance lui-même au
+; démarrage s'il est présent (cf. main.py) ; le raccourci utilisateur pointe
+; donc directement vers Scrabble.exe.
 ; Depuis l'issue #385, Actualise est une instance UNIQUE PARTAGEE
 ; (C:\Actualise\) entre toutes les applications qui l'utilisent (Scrabble,
 ; Rummikub, etc.), chacune avec son propre config_*.json ; on ne peut donc
 ; plus supposer que Scrabble est seul propriétaire de ce dossier.
-; Version d'Actualise embarquée (Release GitHub AlainDelree/Actualise) :
-; reflète le "build_installe" écrit dans config_actualise.json par
-; CreerConfigActualiseSiAbsent ci-dessous (issue #352 — évite la valeur
-; figée en dur). Valeur reelle injectee par rebuild_scrabble.bat via
-; /DActualiseVersion=<build lu dans manifest.json du zip Actualise
-; telecharge> ; "3" n'est qu'un repli de secours pour une compilation
-; manuelle isolee de ce script.
-#ifndef ActualiseVersion
-  #define ActualiseVersion "3"
-#endif
-#define MyActualiseExeName "Actualise.exe"
-; Icône affichée sur les raccourcis (Bureau/menu Démarrer), déployée dans
+; Icône affichée sur le raccourci (Bureau/menu Démarrer), déployée dans
 ; {app} par la section [Files] ci-dessous (embarquée par PyInstaller, cf.
-; scrabble.spec) : sans elle, les raccourcis pointant vers Actualise.exe
-; afficheraient l'icône générique d'Actualise.
+; scrabble.spec).
 #define MyAppIcoName "scrabble.ico"
-; Déposé par build\rebuild_scrabble.bat avant l'appel à ISCC (Actualise.exe +
-; son dossier _internal\, runtime Python + DLL, mode PyInstaller --onedir).
-#define MyActualiseSrcDir "C:\Temp\ScrabbleBuild\Actualise_dist"
 #define MyActualiseDir "C:\Actualise"
 ; Ancien emplacement (une instance d'Actualise par application) : nettoyé
 ; avant installation si présent (issue #385, cf. [Code] ci-dessous).
# ── Zone modifiée : ligne 104 (31 ligne(s)) dans l'ancienne version → ligne 91 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -104,31 +91,17 @@ Name: "french"; MessagesFile: "compiler:Languages\French.isl"
 ; dans l'installeur : un nouvel utilisateur hériterait sinon des préférences/
 ; de l'historique de parties de quelqu'un d'autre dès la première ouverture.
 Source: "{#MyDistDir}\*"; DestDir: "{app}"; Excludes: "config.json,logs\*,data\parties.db,data\*.db"; Flags: ignoreversion recursesubdirs createallsubdirs
-; Actualise : updater autonome, installé dans l'instance partagée
-; C:\Actualise\ (pas dans {app}) car il survit aux mises à jour/
-; réinstallations de Scrabble lui-même, et peut déjà être présent si une
-; autre application (Rummikub, etc.) l'a installé avant. Copie récursive
-; (Actualise.exe + _internal\, runtime Python + DLL, mode PyInstaller
-; --onedir). Pas de "ignoreversion" ici (issue #385) : on laisse Inno Setup
-; comparer nativement la version du fichier embarqué à celle déjà présente
-; et ne remplacer que si elle est plus récente, pour ne pas écraser une
-; version plus à jour installée entretemps par une autre application
-; partageant cette même instance.
-Source: "{#MyActualiseSrcDir}\*"; DestDir: "{#MyActualiseDir}"; Flags: recursesubdirs createallsubdirs
 
 [Dirs]
 Name: "{#MyActualiseDir}"
-Name: "{#MyActualiseDir}\attente"
 
 [Icons]
-; Les raccourcis pointent vers Actualise.exe (jamais directement vers
-; Scrabble.exe) : Actualise met Scrabble à jour depuis les GitHub Releases
-; avant de le lancer, à chaque démarrage. L'instance C:\Actualise\ étant
-; partagée entre plusieurs applications (issue #385), l'argument
-; "--config scrabble" indique à Actualise.exe de lire config_scrabble.json
-; plutôt que celui d'une autre application installée à côté.
-Name: "{autoprograms}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"; Parameters: "--config scrabble"; IconFilename: "{app}\{#MyAppIcoName}"
-Name: "{autodesktop}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"; Parameters: "--config scrabble"; IconFilename: "{app}\{#MyAppIcoName}"
+; Les raccourcis pointent directement vers Scrabble.exe (issue #407) :
+; Actualise n'est plus embarqué dans ce setup, il est distribué séparément
+; via son propre Actualise-Setup.exe. Le jeu le lance lui-même au démarrage
+; s'il est présent (cf. main.py).
+Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcoName}"
+Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\{#MyAppIcoName}"
 
 [Code]
 function EchapperJSON(const Texte: String): String;
# ── Zone modifiée : ligne 174 (52 ligne(s)) dans l'ancienne version → ligne 147 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -174,52 +147,12 @@ begin
   SaveStringToFile(DossierActualise + 'config_scrabble.json', Contenu, False);
 end;
 
-// Génère config_actualise.json dans l'instance partagée, mais seulement s'il
-// n'existe pas déjà : une autre application (Rummikub, etc.) partageant la
-// même instance C:\Actualise\ a pu le créer avant nous ; il ne faut pas
-// écraser ses réglages (issue #385).
-procedure CreerConfigActualiseSiAbsent();
-var
-  DossierActualise, ZoneAttente, Contenu: String;
-begin
-  DossierActualise := ExpandConstant('{#MyActualiseDir}') + '\';
-  if FileExists(DossierActualise + 'config_actualise.json') then
-    Exit;
-
-  ZoneAttente := DossierActualise + 'attente\';
-
-  Contenu :=
-    '{' + #13#10 +
-    '  "build_installe": {#ActualiseVersion},' + #13#10 +
-    '  "depot_github": "AlainDelree/Actualise",' + #13#10 +
-    '  "zone_attente": "' + EchapperJSON(ZoneAttente) + '"' + #13#10 +
-    '}' + #13#10;
-
-  SaveStringToFile(DossierActualise + 'config_actualise.json', Contenu, False);
-end;
-
-// Dépose le chemin de l'instance partagée d'Actualise dans un emplacement
-// fixe, indépendant du dossier d'installation de Scrabble : consommé dans
-// un chantier ultérieur par Scrabble pour localiser ActualiseUI (issue #385).
-procedure CreerActualisePathTxt();
-var
-  DossierScrabble: String;
-begin
-  DossierScrabble := 'C:\Scrabble\';
-  ForceDirectories(DossierScrabble);
-  SaveStringToFile(DossierScrabble + 'actualise_path.txt', ExpandConstant('{#MyActualiseDir}') + '\', False);
-end;
-
 procedure CurStepChanged(CurStep: TSetupStep);
 begin
   if CurStep = ssInstall then
     SupprimerAncienneInstanceActualise();
   if CurStep = ssPostInstall then
-  begin
     CreerConfigScrabble();
-    CreerConfigActualiseSiAbsent();
-    CreerActualisePathTxt();
-  end;
 end;
 
 // Indique si un autre config_*.json (une autre application partageant
