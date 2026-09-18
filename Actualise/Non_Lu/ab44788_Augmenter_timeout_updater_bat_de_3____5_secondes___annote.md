ab44788

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ab44788
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 16:54:01 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Augmenter timeout updater.bat de 3 à 5 secondes (issue #40)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/actualise.py b/actualise.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index cb669bb..741b18f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/actualise.py
# ── Version APRÈS ce commit.
+++ b/actualise.py
# ── Zone modifiée : ligne 376 (7 ligne(s)) dans l'ancienne version → ligne 376 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -376,7 +376,7 @@ def lancer_application_cible(nom_app: str) -> None:
 
 
 _GABARIT_UPDATER_BAT = """@echo off
-timeout /t 3 /nobreak > nul
+timeout /t 5 /nobreak > nul
 cd /d "{dossier_actualise}"
 if exist "_internal.old" rmdir /s /q "_internal.old"
 if exist "Actualise.exe.old" del /f "Actualise.exe.old"
