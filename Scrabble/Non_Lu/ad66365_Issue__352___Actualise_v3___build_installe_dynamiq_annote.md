ad66365

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ad66365
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 18:55:58 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #352 : Actualise v3 + build_installe dynamique dans scrabble.iss
    
    - rebuild_scrabble.bat : URL de telechargement Actualise v2 -> v3
    - scrabble.iss : ajoute #define MyActualiseVersion "3" en tete des
      defines Actualise, utilise dans CreerConfigActualise() pour le champ
      "build_installe" du bloc "actualise" (au lieu de la valeur figee 1)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/build/rebuild_scrabble.bat b/build/rebuild_scrabble.bat
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b70ddf2..964a354 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/build/rebuild_scrabble.bat
# ── Version APRÈS ce commit.
+++ b/build/rebuild_scrabble.bat
# ── Zone modifiée : ligne 146 (9 ligne(s)) dans l'ancienne version → ligne 146 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -146,9 +146,9 @@ REM --- 6. Telecharger et extraire Actualise (issue #345, issue #346) ---------
 REM Actualise.exe + son dossier _internal\ (runtime Python + DLL, mode
 REM PyInstaller --onedir) sont l'updater embarque dans l'installeur (cf.
 REM scrabble.iss, Source attendue : C:\Temp\ScrabbleBuild\Actualise_dist\).
-REM Recupere depuis la Release v2 du depot AlainDelree/Actualise.
+REM Recupere depuis la Release v3 du depot AlainDelree/Actualise.
 echo [6/9] Telechargement d'Actualise (updater)...
-set "ACTUALISE_URL=https://github.com/AlainDelree/Actualise/releases/download/v2/actualise.zip"
+set "ACTUALISE_URL=https://github.com/AlainDelree/Actualise/releases/download/v3/actualise.zip"
 set "ACTUALISE_ZIP=%LOCALBUILD%\actualise.zip"
 set "ACTUALISE_EXTRACT=%LOCALBUILD%\actualise_extract"
 powershell -NoProfile -Command "$ProgressPreference='SilentlyContinue'; try { Invoke-WebRequest -Uri '%ACTUALISE_URL%' -OutFile '%ACTUALISE_ZIP%' -UseBasicParsing } catch { exit 1 }"
# (diff du fichier suivant)
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# (index — ignorable)
index 9fe3c1b..4b3d911 100644
# (avant — fichier suivant)
--- a/installeur/scrabble.iss
# (après — fichier suivant)
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 20 (6 ligne(s)) dans l'ancienne version → ligne 20 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -20,6 +20,10 @@
 ; Scrabble à jour depuis les GitHub Releases avant de le lancer (issue #344,
 ; architecture complète dans CONCEPTION.md du dépôt Actualise). Le raccourci
 ; utilisateur doit pointer vers lui, jamais directement vers Scrabble.exe.
+; Version d'Actualise embarquée (Release GitHub AlainDelree/Actualise) :
+; reflète le "build_installe" écrit dans config.json par CreerConfigActualise
+; ci-dessous (issue #352 — évite la valeur figée en dur).
+#define MyActualiseVersion "3"
 #define MyActualiseExeName "Actualise.exe"
 ; Icône affichée sur les raccourcis (Bureau/menu Démarrer), déployée dans
 ; {app} par la section [Files] ci-dessous (embarquée par PyInstaller, cf.
# ── Zone modifiée : ligne 112 (7 ligne(s)) dans l'ancienne version → ligne 116 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -112,7 +116,7 @@ begin
   Contenu :=
     '{' + #13#10 +
     '  "actualise": {' + #13#10 +
-    '    "build_installe": 1,' + #13#10 +
+    '    "build_installe": {#MyActualiseVersion},' + #13#10 +
     '    "depot_github": "AlainDelree/Actualise"' + #13#10 +
     '  },' + #13#10 +
     '  "application_cible": {' + #13#10 +
