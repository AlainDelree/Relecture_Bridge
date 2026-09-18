b3cbd4c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b3cbd4c
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 08:06:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Inspecte les codes de retour de close et add-label dans fermer_issue (issue #238)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/watcher.py b/watcher.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2de32a7..9420220 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/watcher.py
# ── Version APRÈS ce commit.
+++ b/watcher.py
# ── Zone modifiée : ligne 1425 (23 ligne(s)) dans l'ancienne version → ligne 1425 (52 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1425,23 +1425,52 @@ def resultat_deja_poste(numero: int) -> bool:
     de sauter à tort une issue réellement non traitée."""
     return _commentaire_marque_present(numero)
 
-def fermer_issue(numero: int):
-    """Ferme une issue et ajoute le label 'done'."""
+def fermer_issue(numero: int) -> bool:
+    """Ferme une issue et ajoute le label 'done'.
+
+    Retourne True seulement si les DEUX sous-commandes (`close` puis
+    `add-label`) ont réussi (issue #238, sur le modèle de `commenter_issue`
+    depuis #195) : avant #238 aucun des deux codes de retour n'était
+    inspecté, si bien qu'une issue pouvait être fermée sans recevoir le
+    label 'done', ou le recevoir sans être fermée, en silence complet — deux
+    états incohérents ensuite mal interprétés par la garde d'idempotence
+    (LABEL_FAIT / resultat_deja_poste en tête de `traiter_issue`) et par
+    l'interface web.
+
+    Les deux sous-commandes sont tentées inconditionnellement (comme avant
+    #238), pour ne pas transformer un échec de `close` en un label manquant
+    évitable. Aucune compensation automatique en cas d'échec partiel : on se
+    contente de journaliser l'état incohérent obtenu, pour diagnostic."""
     try:
-        subprocess.run(
+        res_close = subprocess.run(
             ["gh", "issue", "close", str(numero), "--repo", CFG.depot],
             capture_output=True, text=True,
             encoding="utf-8", errors="replace", timeout=30
         )
-        subprocess.run(
+        close_ok = res_close.returncode == 0
+        if not close_ok:
+            log.error(f"Erreur fermeture issue #{numero} (code {res_close.returncode}) : {res_close.stderr.strip()}")
+
+        res_label = subprocess.run(
             ["gh", "issue", "edit", str(numero),
              "--repo", CFG.depot,
              "--add-label", LABEL_FAIT],
             capture_output=True, text=True,
             encoding="utf-8", errors="replace", timeout=30
         )
+        label_ok = res_label.returncode == 0
+        if not label_ok:
+            log.error(f"Erreur ajout label '{LABEL_FAIT}' sur issue #{numero} (code {res_label.returncode}) : {res_label.stderr.strip()}")
+
+        if close_ok and not label_ok:
+            log.error(f"  État incohérent issue #{numero} : FERMÉE mais SANS le label '{LABEL_FAIT}' (pas de compensation automatique).")
+        elif label_ok and not close_ok:
+            log.error(f"  État incohérent issue #{numero} : label '{LABEL_FAIT}' posé mais issue NON fermée (pas de compensation automatique).")
+
+        return close_ok and label_ok
     except Exception as e:
         log.error(f"Erreur fermeture issue #{numero} : {e}")
+        return False
 
 def lancer_claude(numero: int, titre: str, body: str, dry_run: bool,
                   autoriser_ecriture: bool = False,
# ── Zone modifiée : ligne 1813 (7 ligne(s)) dans l'ancienne version → ligne 1842 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1813,7 +1842,8 @@ def traiter_issue(issue: dict, dry_run: bool):
     # se contente de re-tenter la fermeture, puis on rend la main.
     if LABEL_FAIT in labels or resultat_deja_poste(numero):
         log.info(f"  Issue #{numero} déjà traitée (résultat commenté) — finalisation de la fermeture, pas de retraitement.")
-        fermer_issue(numero)
+        if not fermer_issue(numero):
+            log.warning(f"  Finalisation de la fermeture #{numero} toujours incomplète — nouvelle tentative au prochain cycle.")
         return
 
     issues_en_cours.add(numero)
# ── Zone modifiée : ligne 1952 (7 ligne(s)) dans l'ancienne version → ligne 1982 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1952,7 +1982,8 @@ def traiter_issue(issue: dict, dry_run: bool):
                     )
                     issues_en_cours.discard(numero)
                     return
-                fermer_issue(numero)
+                if not fermer_issue(numero):
+                    log.warning(f"  Fermeture de l'issue #{numero} incomplète (close/label) — sera retentée au prochain cycle via la garde d'idempotence.")
                 issues_en_cours.discard(numero)
                 # Historique des durées (issue #108) : durée réelle ACK → fermeture,
                 # catégorisée par projet/type/mode, pour l'estimation prédictive.
