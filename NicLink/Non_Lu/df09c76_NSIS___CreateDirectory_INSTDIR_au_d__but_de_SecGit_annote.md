df09c76

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit df09c76
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 17:51:29 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    NSIS : CreateDirectory INSTDIR au début de SecGit (fix SyncGitRepo)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a1f6f58..f47e3b1 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installer-exe/alchess_setup.nsi
# ── Version APRÈS ce commit.
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1432 (6 ligne(s)) dans l'ancienne version → ligne 1432 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1432,6 +1432,7 @@ SectionGroup "Configuration AlChess" SecGroupConfig
     ; DOIT s'executer avant SecPython/SecVenv : requirements.txt (utilise par
     ; SecVenv) doit venir du code deja synchronise ici.
     Section "Synchronisation Git" SecGit
+        CreateDirectory "$INSTDIR"
         Call EnsureGitInstalled
         Call SyncGitRepo
     SectionEnd
