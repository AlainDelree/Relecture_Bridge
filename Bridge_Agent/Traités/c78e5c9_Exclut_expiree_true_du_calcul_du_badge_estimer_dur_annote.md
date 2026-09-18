c78e5c9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c78e5c9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 03:49:45 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Exclut expiree=true du calcul du badge estimer_duree (issue #223)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/issues.py b/app/issues.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d75b1f1..76146c4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/issues.py
# ── Version APRÈS ce commit.
+++ b/app/issues.py
# ── Zone modifiée : ligne 722 (6 ligne(s)) dans l'ancienne version → ligne 722 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -722,6 +722,7 @@ def estimer_duree(historique: list, projet: str, type_issue: str, mode: str) ->
         and r.get("type") == type_issue
         and r.get("mode") == mode
         and isinstance(r.get("duree"), (int, float))
+        and r.get("expiree") is not True
     ]
     n = len(durees)
     if n == 0:
