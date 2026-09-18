153d6cf

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 153d6cf
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 8 13:19:34 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #525 : _debut_traitement ignore les ACK antérieurs au dernier échec définitif

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/issues.py b/app/issues.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6e10a3f..c5c2ec3 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/issues.py
# ── Version APRÈS ce commit.
+++ b/app/issues.py
# ── Zone modifiée : ligne 874 (11 ligne(s)) dans l'ancienne version → ligne 874 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -874,11 +874,21 @@ def _debut_traitement(commentaires: list) -> str | None:
     cas de reprise après interruption du watcher (crash, reset, Éteindre/
     Relancer), plusieurs ACK coexistent et seule la plus récente reflète le
     vrai début de la tentative en cours — sinon le badge inclurait à tort le
-    temps mort de l'interruption."""
+    temps mort de l'interruption.
+
+    Issue #525 : une issue relancée après un échec définitif (label
+    needs-human retiré) conserve dans son historique les ACK du cycle
+    précédent. watcher.py poste, juste avant de poser needs-human, un
+    commentaire d'échec définitif ("Échec après N tentatives" —
+    watcher.py:3442) : on borne donc la recherche d'ACK aux commentaires
+    postés APRÈS ce marqueur. Si aucun ACK ne suit ce marqueur, le
+    traitement actuel n'a pas encore repris (issue "en file") → None."""
     debut = None
     for c in commentaires:
         corps = c.get("body") or ""
-        if "ACK —" in corps and "watcher.py" in corps:
+        if "Échec après" in corps and "tentatives" in corps:
+            debut = None
+        elif "ACK —" in corps and "watcher.py" in corps:
             debut = c.get("createdAt")
     return debut
 
