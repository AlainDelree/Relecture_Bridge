817dd3a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 817dd3a
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 6 09:22:33 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #376 (suite) : corriger scrabble.iss côté Linux + topic_ntfy
    
    Report des corrections appliquées côté CCW (build #376) sur ce clone :
    - lecture dynamique du build Actualise via #ifndef ActualiseVersion
      (repli "3" si non injecté par rebuild_scrabble.bat via
      /DActualiseVersion), au lieu de la constante figée MyActualiseVersion.
    - lecture dynamique du build Scrabble via #ifndef ScrabbleBuildInstalle
      (repli "1"), au lieu de la valeur en dur "build_installe": 1 dans le
      JSON généré par CreerConfigActualise.
    - topic_ntfy renseigné à "hippocampe-scrabble-y9htxM7q" (était vide "").

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4b3d911..e2836af 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 22 (8 ligne(s)) dans l'ancienne version → ligne 22 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -22,8 +22,13 @@
 ; utilisateur doit pointer vers lui, jamais directement vers Scrabble.exe.
 ; Version d'Actualise embarquée (Release GitHub AlainDelree/Actualise) :
 ; reflète le "build_installe" écrit dans config.json par CreerConfigActualise
-; ci-dessous (issue #352 — évite la valeur figée en dur).
-#define MyActualiseVersion "3"
+; ci-dessous (issue #352 — évite la valeur figée en dur). Valeur reelle
+; injectee par rebuild_scrabble.bat via /DActualiseVersion=<build lu dans
+; manifest.json du zip Actualise telecharge> ; "3" n'est qu'un repli de
+; secours pour une compilation manuelle isolee de ce script.
+#ifndef ActualiseVersion
+  #define ActualiseVersion "3"
+#endif
 #define MyActualiseExeName "Actualise.exe"
 ; Icône affichée sur les raccourcis (Bureau/menu Démarrer), déployée dans
 ; {app} par la section [Files] ci-dessous (embarquée par PyInstaller, cf.
# ── Zone modifiée : ligne 34 (6 ligne(s)) dans l'ancienne version → ligne 39 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -34,6 +39,13 @@
 ; son dossier _internal\, runtime Python + DLL, mode PyInstaller --onedir).
 #define MyActualiseSrcDir "C:\Temp\ScrabbleBuild\Actualise_dist"
 #define MyActualiseDir "{sd}\Actualise_Scrabble"
+; Numero de build de Scrabble reellement embarque dans ce setup (lu dans
+; version.json a la racine du depot par rebuild_scrabble.bat, injecte via
+; /DScrabbleBuildInstalle=<build>) ; "1" n'est qu'un repli de secours pour
+; une compilation manuelle isolee de ce script.
+#ifndef ScrabbleBuildInstalle
+  #define ScrabbleBuildInstalle "1"
+#endif
 
 [Setup]
 ; GUID fixe et unique à l'application : NE PAS régénérer (sert à Windows pour
# ── Zone modifiée : ligne 116 (19 ligne(s)) dans l'ancienne version → ligne 128 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -116,19 +128,19 @@ begin
   Contenu :=
     '{' + #13#10 +
     '  "actualise": {' + #13#10 +
-    '    "build_installe": {#MyActualiseVersion},' + #13#10 +
+    '    "build_installe": {#ActualiseVersion},' + #13#10 +
     '    "depot_github": "AlainDelree/Actualise"' + #13#10 +
     '  },' + #13#10 +
     '  "application_cible": {' + #13#10 +
     '    "nom": "Scrabble",' + #13#10 +
     '    "depot_github": "AlainDelree/Scrabble",' + #13#10 +
-    '    "build_installe": 1,' + #13#10 +
+    '    "build_installe": {#ScrabbleBuildInstalle},' + #13#10 +
     '    "repertoire_installation": "' + EchapperJSON(RepertoireInstallation) + '",' + #13#10 +
     '    "executable": "Scrabble.exe",' + #13#10 +
     '    "icone": "' + EchapperJSON(ExpandConstant('{app}') + '\scrabble.ico') + '"' + #13#10 +
     '  },' + #13#10 +
     '  "zone_attente": "' + EchapperJSON(ZoneAttente) + '",' + #13#10 +
-    '  "topic_ntfy": ""' + #13#10 +
+    '  "topic_ntfy": "hippocampe-scrabble-y9htxM7q"' + #13#10 +
     '}' + #13#10;
 
   SaveStringToFile(DossierActualise + 'config.json', Contenu, False);
