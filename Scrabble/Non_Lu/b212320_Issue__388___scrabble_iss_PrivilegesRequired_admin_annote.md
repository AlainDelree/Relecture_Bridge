b212320

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b212320
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 21:15:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #388 : scrabble.iss PrivilegesRequired=admin pour C:\Actualise\
    
    PrivilegesRequired=lowest empêchait l'écriture dans C:\Actualise\ (racine
    du disque système, protégée pour les utilisateurs standard), causant un
    Actualise non déployé et un raccourci cassé en production.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installeur/scrabble.iss b/installeur/scrabble.iss
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c03df3a..1a1cd22 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installeur/scrabble.iss
# ── Version APRÈS ce commit.
+++ b/installeur/scrabble.iss
# ── Zone modifiée : ligne 64 (12 ligne(s)) dans l'ancienne version → ligne 64 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -64,12 +64,12 @@ AppVersion={#ScrabbleBuildInstalle}
 AppPublisher={#MyAppPublisher}
 DefaultDirName={autopf}\{#MyAppName}
 DefaultGroupName={#MyAppName}
-; Aucun droit administrateur requis : installation dans le profil utilisateur
-; courant. Avec PrivilegesRequired=lowest, {autopf}/{autodesktop}/{autoprograms}
-; résolvent respectivement vers %LOCALAPPDATA%\Programs, le Bureau et le menu
-; Démarrer de l'utilisateur courant (pas les emplacements "tous les
-; utilisateurs", qui nécessiteraient des droits admin).
-PrivilegesRequired=lowest
+; Droits administrateur requis (issue #388) : nécessaire pour écrire dans
+; C:\Actualise\ (racine du disque système, protégée pour les utilisateurs
+; standard). Avec PrivilegesRequired=admin, {autopf}/{autodesktop}/
+; {autoprograms} résolvent respectivement vers C:\Program Files\, le Bureau
+; commun et le menu Démarrer commun (emplacements "tous les utilisateurs").
+PrivilegesRequired=admin
 DisableProgramGroupPage=yes
 SetupIconFile=..\assets\scrabble.ico
 UninstallDisplayIcon={app}\{#MyAppExeName}
# ── Zone modifiée : ligne 192 (9 ligne(s)) dans l'ancienne version → ligne 192 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -192,9 +192,8 @@ begin
 end;
 
 // Dépose le chemin de l'instance partagée d'Actualise dans un emplacement
-// fixe, indépendant du dossier d'installation de Scrabble (qui varie selon
-// l'utilisateur avec PrivilegesRequired=lowest) : consommé dans un chantier
-// ultérieur par Scrabble pour localiser ActualiseUI (issue #385).
+// fixe, indépendant du dossier d'installation de Scrabble : consommé dans
+// un chantier ultérieur par Scrabble pour localiser ActualiseUI (issue #385).
 procedure CreerActualisePathTxt();
 var
   DossierScrabble: String;
