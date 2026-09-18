8c3802c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8c3802c
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 27 18:42:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-496

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/new_issue.py b/new_issue.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7567f0e..6ac6fd8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/new_issue.py
# ── Version APRÈS ce commit.
+++ b/new_issue.py
# ── Zone modifiée : ligne 32 (6 ligne(s)) dans l'ancienne version → ligne 32 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -32,6 +32,8 @@ from app import create_app, etat
 from app.tunnel import demarrer_tunnel, arreter_tunnel
 from app.cycle_vie import surveiller_heartbeat
 from app.notifications_poller import surveiller_transitions
+from app.issues_inbox import (watcher_inbox_actif, demarrer_watcher_inbox,
+                              arreter_watcher_inbox)
 
 DOSSIER_SCRIPT = Path(__file__).resolve().parent
 
