3024f51

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3024f51
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 15:35:59 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #471 : revenir au bip plat 440 Hz (annuler #437)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/traitement_fin.py b/scripts/traitement_fin.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c1eb8e1..dc8377a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/scripts/traitement_fin.py
# ── Version APRÈS ce commit.
+++ b/scripts/traitement_fin.py
# ── Zone modifiée : ligne 97 (7 ligne(s)) dans l'ancienne version → ligne 97 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -97,7 +97,7 @@ def main():
                         help="Numéro de l'issue (déclenche le POST /notifier-fin-issue avec --projet)")
     args = parser.parse_args()
 
-    bip()
+    bip_plat()
 
     if args.projet and args.numero:
         notifier_fin_issue(args.projet, args.numero)
