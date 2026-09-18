e796571

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e796571
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 14:22:23 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #348 : scrabble.iss — IconFilename raccourcis + champ icone config.json
    
    - [Icons] : IconFilename={app}\scrabble.ico sur les raccourcis Bureau et menu
      Démarrer pour afficher l'icône Scrabble malgré l'exécution d'Actualise.exe.
    - #define MyAppIcoName "scrabble.ico"
    - CreerConfigActualise() : ajout du champ "icone" dans application_cible du
      config.json généré, chemin dynamique vers {app}\scrabble.ico échappé via
      EchapperJSON comme les autres chemins.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e8fe1e4..d556b28 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 21 (6 ligne(s)) dans l'ancienne version → ligne 21 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -21,6 +21,11 @@
 ; architecture complète dans CONCEPTION.md du dépôt Actualise). Le raccourci
 ; utilisateur doit pointer vers lui, jamais directement vers Scrabble.exe.
 #define MyActualiseExeName "Actualise.exe"
+; Icône affichée sur les raccourcis (Bureau/menu Démarrer), déployée dans
+; {app} par la section [Files] ci-dessous (embarquée par PyInstaller, cf.
+; scrabble.spec) : sans elle, les raccourcis pointant vers Actualise.exe
+; afficheraient l'icône générique d'Actualise.
+#define MyAppIcoName "scrabble.ico"
 ; Déposé par build\rebuild_scrabble.bat avant l'appel à ISCC (Actualise.exe +
 ; son dossier _internal\, runtime Python + DLL, mode PyInstaller --onedir).
 #define MyActualiseSrcDir "C:\Temp\ScrabbleBuild\Actualise_dist"
# ── Zone modifiée : ligne 83 (8 ligne(s)) dans l'ancienne version → ligne 88 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -83,8 +88,8 @@ Name: "{#MyActualiseDir}\attente"
 ; Les raccourcis pointent vers Actualise.exe (jamais directement vers
 ; Scrabble.exe) : Actualise met Scrabble à jour depuis les GitHub Releases
 ; avant de le lancer, à chaque démarrage.
-Name: "{autoprograms}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"
-Name: "{autodesktop}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"
+Name: "{autoprograms}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"; IconFilename: "{app}\{#MyAppIcoName}"
+Name: "{autodesktop}\{#MyAppName}"; Filename: "{#MyActualiseDir}\{#MyActualiseExeName}"; IconFilename: "{app}\{#MyAppIcoName}"
 
 [Code]
 // Génère le config.json d'Actualise, consommé par Actualise.exe au
# ── Zone modifiée : ligne 115 (7 ligne(s)) dans l'ancienne version → ligne 120 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -115,7 +120,8 @@ begin
     '    "depot_github": "AlainDelree/Scrabble",' + #13#10 +
     '    "build_installe": 1,' + #13#10 +
     '    "repertoire_installation": "' + EchapperJSON(RepertoireInstallation) + '",' + #13#10 +
-    '    "executable": "Scrabble.exe"' + #13#10 +
+    '    "executable": "Scrabble.exe",' + #13#10 +
+    '    "icone": "' + EchapperJSON(ExpandConstant('{app}') + '\scrabble.ico') + '"' + #13#10 +
     '  },' + #13#10 +
     '  "zone_attente": "' + EchapperJSON(ZoneAttente) + '",' + #13#10 +
     '  "topic_ntfy": ""' + #13#10 +
