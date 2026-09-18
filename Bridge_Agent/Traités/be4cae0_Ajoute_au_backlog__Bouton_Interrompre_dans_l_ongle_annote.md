be4cae0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit be4cae0
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 21:51:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute au backlog: Bouton Interrompre dans l'onglet CCW

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e9b4c6f..7ab9d0a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 4 (6 ligne(s)) dans l'ancienne version → ligne 4 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,6 +4,13 @@ Idées et pistes non prioritaires, à réaliser éventuellement plus tard.
 Alain peut modifier ce fichier directement, sans passer par une issue.
 
 ---
+##Bouton Interrompre dans l'onglet CCW
+
+Procédure : nssm restart CCW-Watcher, puis supprimer le(s) fichier(s)
+  dans C:\CCW\Bridge_Agent\logs\verrous\ :
+  Get-ChildItem C:\CCW\Bridge_Agent\logs\verrous\ -Filter "*.lock"
+  Remove-Item C:\CCW\Bridge_Agent\logs\verrous\<fichier>.lock
+
 ## Issues récurrentes — bibliothèque de templates par projet
 
 **Contexte** : certaines issues reviennent régulièrement à l'identique ou
