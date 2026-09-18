7a69faa

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7a69faa
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 20:08:14 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #387 : deploiement ActualiseUI.exe dans scrabble.iss (verif #385 OK)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c03df3a..e9e7183 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 34 (6 ligne(s)) dans l'ancienne version → ligne 34 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -34,6 +34,12 @@
   #define ActualiseVersion "3"
 #endif
 #define MyActualiseExeName "Actualise.exe"
+; Interface graphique optionnelle d'Actualise (mode PyInstaller --onefile,
+; un seul .exe autonome), incluse dans l'instance partagée C:\Actualise\
+; depuis la Release v8 d'Actualise (issue #387). Déposée par
+; build\rebuild_scrabble.bat aux côtés d'Actualise.exe dans le même dossier
+; de staging (cf. MyActualiseSrcDir ci-dessous).
+#define MyActualiseUIExeName "ActualiseUI.exe"
 ; Icône affichée sur les raccourcis (Bureau/menu Démarrer), déployée dans
 ; {app} par la section [Files] ci-dessous (embarquée par PyInstaller, cf.
 ; scrabble.spec) : sans elle, les raccourcis pointant vers Actualise.exe
# ── Zone modifiée : ligne 108 (6 ligne(s)) dans l'ancienne version → ligne 114 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -108,6 +114,12 @@ Source: "{#MyDistDir}\*"; DestDir: "{app}"; Excludes: "config.json,logs\*,data\p
 ; version plus à jour installée entretemps par une autre application
 ; partageant cette même instance.
 Source: "{#MyActualiseSrcDir}\*"; DestDir: "{#MyActualiseDir}"; Flags: recursesubdirs createallsubdirs
+; ActualiseUI.exe (issue #387) : déployé explicitement aux côtés d'Actualise.exe
+; dans l'instance partagée, même logique de non-remplacement que ci-dessus (pas
+; d'"ignoreversion" : on ne remplace que si la version embarquée est plus
+; récente que celle déjà présente, au cas où une autre application partageant
+; C:\Actualise\ en aurait déjà déposé une version plus à jour).
+Source: "{#MyActualiseSrcDir}\{#MyActualiseUIExeName}"; DestDir: "{#MyActualiseDir}"
 
 [Dirs]
 Name: "{#MyActualiseDir}"
