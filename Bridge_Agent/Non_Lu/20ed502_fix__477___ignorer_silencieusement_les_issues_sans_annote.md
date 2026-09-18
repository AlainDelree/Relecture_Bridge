20ed502

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 20ed502
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 20:52:49 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #477 : ignorer silencieusement les issues sans label for-linux ni for-windows dans lister_issues

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/watcher.py b/watcher.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ad01156..98c6f13 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/watcher.py
# ── Version APRÈS ce commit.
+++ b/watcher.py
# ── Zone modifiée : ligne 706 (6 ligne(s)) dans l'ancienne version → ligne 706 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -706,6 +706,18 @@ def lister_issues():
             log.error(f"Erreur gh issue list : {res.stderr.strip()}")
             return []
         issues = json.loads(res.stdout)
+        # Garde-fou supplémentaire, en amont (issue #477) : ignore
+        # silencieusement (pas de log, pas de tentative de traitement) toute
+        # issue ne portant ni 'for-linux' ni 'for-windows'. Certains dépôts
+        # (ex. FF_Galerie) génèrent leurs propres issues applicatives
+        # (alertes, bugs détectés en production) qui ne sont pas destinées au
+        # bridge. Le filtre existant sur CFG.label (--label ci-dessus) reste
+        # inchangé — celui-ci est un filet de sécurité additionnel.
+        issues = [
+            i for i in issues
+            if any(l.get("name", "") in ("for-linux", "for-windows")
+                   for l in i.get("labels", []))
+        ]
         # Tri FIFO explicite : la plus ancienne issue en premier (issue #134).
         # createdAt est un timestamp ISO 8601 UTC (…Z), donc l'ordre
         # lexicographique croissant équivaut à l'ordre chronologique croissant.
