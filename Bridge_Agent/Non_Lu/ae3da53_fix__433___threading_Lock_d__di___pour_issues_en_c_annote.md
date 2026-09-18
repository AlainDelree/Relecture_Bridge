ae3da53

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ae3da53
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 14:08:48 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #433 : threading.Lock dédié pour issues_en_cours (check+add atomique)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/watcher.py b/watcher.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 412248c..3005206 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/watcher.py
# ── Version APRÈS ce commit.
+++ b/watcher.py
# ── Zone modifiée : ligne 2372 (6 ligne(s)) dans l'ancienne version → ligne 2372 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2372,6 +2372,28 @@ probables, sans préambule ni conclusion, et sans tenter de corriger quoi que ce
 
 # Mémoire des issues en cours de traitement (évite les doublons)
 issues_en_cours: set[int] = set()
+# Verrou dédié (issue #433) : le pattern check-then-act (contient → ajouter)
+# reposait implicitement sur le GIL de CPython plutôt que sur une garantie
+# formelle. Chaque opération élémentaire (contient/ajouter/retirer) est
+# désormais atomique via ce verrou — sans changer le comportement observable
+# (la dédup inter-cycles réelle du mode_write parallélisé reste assurée par
+# `_threads_ecriture` + `_verrou_threads_ecriture`, cf. commentaires plus bas).
+_verrou_issues_en_cours = threading.Lock()
+
+
+def _issues_en_cours_contient(numero: int) -> bool:
+    with _verrou_issues_en_cours:
+        return numero in issues_en_cours
+
+
+def _issues_en_cours_ajouter(numero: int) -> None:
+    with _verrou_issues_en_cours:
+        issues_en_cours.add(numero)
+
+
+def _issues_en_cours_retirer(numero: int) -> None:
+    with _verrou_issues_en_cours:
+        issues_en_cours.discard(numero)
 
 
 # ─── Parallélisation mode_write via git worktrees (issue #337) ─────────────────
# ── Zone modifiée : ligne 2873 (7 ligne(s)) dans l'ancienne version → ligne 2895 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2873,7 +2895,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
     titre  = issue["title"]
     body   = issue.get("body") or ""
 
-    if numero in issues_en_cours:
+    if _issues_en_cours_contient(numero):
         return
 
     labels = [l.get("name", "") for l in issue.get("labels", [])]
# ── Zone modifiée : ligne 2896 (7 ligne(s)) dans l'ancienne version → ligne 2918 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2896,7 +2918,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
             log.warning(f"  Finalisation de la fermeture #{numero} toujours incomplète — nouvelle tentative au prochain cycle.")
         return
 
-    issues_en_cours.add(numero)
+    _issues_en_cours_ajouter(numero)
     priorite = extraire_priorite(body)
     critique = priorite in PRIORITES_CRITIQUES
     timeout  = extraire_timeout(body, titre)
# ── Zone modifiée : ligne 2962 (7 ligne(s)) dans l'ancienne version → ligne 2984 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2962,7 +2984,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                 f"pour relancer."
             )
             ajouter_label(numero, LABEL_ECHEC)
-            issues_en_cours.discard(numero)
+            _issues_en_cours_retirer(numero)
             return
 
         valide, raison = valider_repo_cible(repo_cible)
# ── Zone modifiée : ligne 2976 (7 ligne(s)) dans l'ancienne version → ligne 2998 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2976,7 +2998,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                 f"`{LABEL_ECHEC}` pour relancer."
             )
             ajouter_label(numero, LABEL_ECHEC)
-            issues_en_cours.discard(numero)
+            _issues_en_cours_retirer(numero)
             return
 
         repo_cible_resolu  = Path(repo_cible).resolve()
# ── Zone modifiée : ligne 3009 (7 ligne(s)) dans l'ancienne version → ligne 3031 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3009,7 +3031,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
             f"  Issue #{numero} différée : un autre traitement détient déjà le verrou "
             f"sur {cwd_effectif} — collision évitée, reprise au prochain cycle."
         )
-        issues_en_cours.discard(numero)
+        _issues_en_cours_retirer(numero)
         return
 
     try:
# ── Zone modifiée : ligne 3037 (7 ligne(s)) dans l'ancienne version → ligne 3059 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3037,7 +3059,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                     f"Corrigez puis retirez le label `{LABEL_ECHEC}` pour relancer."
                 )
                 ajouter_label(numero, LABEL_ECHEC)
-                issues_en_cours.discard(numero)
+                _issues_en_cours_retirer(numero)
                 return
             statut_rep_travail_avant = _statut_git_rep_travail(cwd_effectif)
 
# ── Zone modifiée : ligne 3120 (7 ligne(s)) dans l'ancienne version → ligne 3142 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3120,7 +3142,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                         numero=numero,
                     )
                     notifier_fin_sse(numero)
-                    issues_en_cours.discard(numero)
+                    _issues_en_cours_retirer(numero)
                     return
 
             if succes:
# ── Zone modifiée : ligne 3148 (11 ligne(s)) dans l'ancienne version → ligne 3170 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3148,11 +3170,11 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                         priorite_ntfy="high",
                         numero=numero,
                     )
-                    issues_en_cours.discard(numero)
+                    _issues_en_cours_retirer(numero)
                     return
                 if not fermer_issue(numero):
                     log.warning(f"  Fermeture de l'issue #{numero} incomplète (close/label) — sera retentée au prochain cycle via la garde d'idempotence.")
-                issues_en_cours.discard(numero)
+                _issues_en_cours_retirer(numero)
                 # Historique des durées (issue #108) : durée réelle ACK → fermeture,
                 # catégorisée par projet/type/mode, pour l'estimation prédictive.
                 type_issue_close = deduire_type_issue(titre, body)
# ── Zone modifiée : ligne 3248 (7 ligne(s)) dans l'ancienne version → ligne 3270 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3248,7 +3270,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                 if critique:
                     alerte_critique(numero, titre, tentative, labels)
                     log.warning(f"  Issue critique #{numero} — nouvelle tentative au prochain cycle.")
-                    issues_en_cours.discard(numero)  # sera reprise au prochain poll
+                    _issues_en_cours_retirer(numero)  # sera reprise au prochain poll
                     return
                 else:
                     log.error(f"  Issue #{numero} abandonnée après {CFG.max_essais} tentatives.")
# ── Zone modifiée : ligne 3296 (7 ligne(s)) dans l'ancienne version → ligne 3318 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3296,7 +3318,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                         numero=numero,
                     )
                     notifier_fin_sse(numero)
-                    issues_en_cours.discard(numero)
+                    _issues_en_cours_retirer(numero)
                     return
 
             time.sleep(PAUSE_ENTRE_TENTATIVES)  # backoff entre tentatives
# ── Zone modifiée : ligne 3367 (7 ligne(s)) dans l'ancienne version → ligne 3389 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3367,7 +3389,7 @@ def traiter_issue(issue: dict, dry_run: bool) -> None:
     numero = issue["number"]
     labels = [l.get("name", "") for l in issue.get("labels", [])]
 
-    if numero in issues_en_cours:
+    if _issues_en_cours_contient(numero):
         return
 
     # Déjà en cours dans un thread depuis un cycle précédent (mode_write
# ── Zone modifiée : ligne 3390 (7 ligne(s)) dans l'ancienne version → ligne 3412 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3390,7 +3412,7 @@ def traiter_issue(issue: dict, dry_run: bool) -> None:
 
         if not actifs:
             # Premier slot : thread sur REP_TRAVAIL (pas de worktree).
-            # PAS de issues_en_cours.add(numero) ICI : c'est
+            # PAS de _issues_en_cours_ajouter(numero) ICI : c'est
             # _traiter_issue_synchrone, exécutée DANS le thread, qui s'en
             # charge (comportement historique) — l'ajouter ici bloquerait le
             # thread dès sa première ligne (garde d'idempotence en tête de
# ── Zone modifiée : ligne 3412 (7 ligne(s)) dans l'ancienne version → ligne 3434 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3412,7 +3434,7 @@ def traiter_issue(issue: dict, dry_run: bool) -> None:
         if len(actifs) < CFG.max_write_parallele:
             chemin_worktree = _creer_worktree(numero)
             if chemin_worktree is not None:
-                # Même remarque que ci-dessus : pas de issues_en_cours.add ici.
+                # Même remarque que ci-dessus : pas de _issues_en_cours_ajouter ici.
                 thread = threading.Thread(
                     target=_lancer_thread_ecriture, args=(issue, dry_run, chemin_worktree),
                     name=f"ecriture-issue-{numero}", daemon=True,
