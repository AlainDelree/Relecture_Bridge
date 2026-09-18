9d0c783

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9d0c783
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 6 18:19:20 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    chore : panneau flottant — hauteur max calc(100vh - 80px) pour supprimer le scroll

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/css/style.css b/static/css/style.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 56278c4..3437c55 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/css/style.css
# ── Version APRÈS ce commit.
+++ b/static/css/style.css
# ── Zone modifiée : ligne 299 (7 ligne(s)) dans l'ancienne version → ligne 299 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -299,7 +299,7 @@ button.danger:hover{background:#f8d7da}
   box-shadow:0 2px 8px rgba(0,0,0,.12)}
 .pl-toggle.actif{border-color:#185FA5;color:#185FA5}
 .panneau-lateral{position:fixed;top:64px;right:18px;z-index:1000;
-  width:360px;max-height:80vh;overflow-y:auto;
+  width:360px;max-height:calc(100vh - 80px);overflow-y:auto;
   border:1px solid #e0dfda;border-radius:10px;background:#fff;padding:16px;
   box-shadow:0 6px 24px rgba(0,0,0,.18)}
 .panneau-lateral.ferme{display:none}
