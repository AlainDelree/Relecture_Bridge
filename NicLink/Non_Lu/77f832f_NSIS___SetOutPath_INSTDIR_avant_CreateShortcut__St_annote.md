77f832f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 77f832f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 17:59:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    NSIS : SetOutPath INSTDIR avant CreateShortcut (Start in du raccourci)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f47e3b1..5d9c6eb 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installer-exe/alchess_setup.nsi
# ── Version APRÈS ce commit.
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1934 (6 ligne(s)) dans l'ancienne version → ligne 1934 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1934,6 +1934,11 @@ Section "Raccourci bureau" SecShortcut
     DetailPrint "Creation du raccourci bureau"
     DetailPrint "================================================"
 
+    ; Definir le repertoire de travail (Start in) du raccourci : sans cela,
+    ; le champ "Demarrer dans" du .lnk reste vide et le .bat ne retrouve pas
+    ; ses chemins relatifs.
+    SetOutPath "$INSTDIR"
+
     ; Reinitialiser le flag d'erreur avant CreateShortcut pour que IfErrors
     ; ne remonte pas une erreur laissee par une instruction anterieure.
     ClearErrors
