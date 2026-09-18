f42d9f3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f42d9f3
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 18:26:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #478 : masquer les issues sans label for-linux ni for-windows dans la fenêtre Résultats

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/issues.py b/app/issues.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index db34f7d..3a09bc0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/issues.py
# ── Version APRÈS ce commit.
+++ b/app/issues.py
# ── Zone modifiée : ligne 606 (6 ligne(s)) dans l'ancienne version → ligne 606 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -606,6 +606,20 @@ LIMITE_ISSUES_MIN = 1
 LIMITE_ISSUES_MAX = 50
 
 
+def _filtrer_issues_bridge(issues: list) -> list:
+    """Ignore silencieusement les issues ne portant ni 'for-linux' ni
+    'for-windows' (issue #478, pendant côté affichage du garde-fou #477 dans
+    watcher.py::lister_issues). Certains dépôts (ex. FF_Galerie) génèrent
+    leurs propres issues applicatives qui n'ont aucun rapport avec le bridge
+    et ne doivent pas apparaître dans la fenêtre Résultats, qu'elles soient
+    ouvertes ou fermées."""
+    return [
+        i for i in issues
+        if any(l.get("name", "") in ("for-linux", "for-windows")
+               for l in i.get("labels", []))
+    ]
+
+
 def _limite_issues_requete():
     """Lit le paramètre de requête `limite` (issue #271) : entier borné entre
     LIMITE_ISSUES_MIN et LIMITE_ISSUES_MAX. Toute valeur absente ou invalide
# ── Zone modifiée : ligne 641 (7 ligne(s)) dans l'ancienne version → ligne 655 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -641,7 +655,7 @@ def issues_liste(nom_projet):
         )
         if res.returncode != 0:
             return jsonify(erreur=res.stderr.strip() or "Erreur de gh."), 502
-        return jsonify(json.loads(res.stdout or "[]"))
+        return jsonify(_filtrer_issues_bridge(json.loads(res.stdout or "[]")))
     except subprocess.TimeoutExpired:
         return jsonify(erreur="Timeout (gh n'a pas répondu en 30s)."), 504
     except FileNotFoundError:
# ── Zone modifiée : ligne 692 (6 ligne(s)) dans l'ancienne version → ligne 706 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -692,6 +706,7 @@ def recherche_issues(nom_projet):
         return jsonify(erreur="gh introuvable dans le PATH."), 500
     except Exception as e:
         return jsonify(erreur=str(e)), 500
+    toutes = _filtrer_issues_bridge(toutes)
     if not titre_cherche:
         return jsonify(toutes)
     filtrees = [it for it in toutes
