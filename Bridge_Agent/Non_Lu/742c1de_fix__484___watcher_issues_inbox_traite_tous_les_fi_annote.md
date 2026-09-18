742c1de

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 742c1de
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 12:21:14 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #484 : watcher issues_inbox traite tous les fichiers, rejette les extensions non-.txt

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/watcher_issues_inbox.py b/scripts/watcher_issues_inbox.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0a5aee6..418f7ac 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/scripts/watcher_issues_inbox.py
# ── Version APRÈS ce commit.
+++ b/scripts/watcher_issues_inbox.py
# ── Zone modifiée : ligne 2 (13 ligne(s)) dans l'ancienne version → ligne 2 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2,13 +2,16 @@
 """
 watcher_issues_inbox.py — Watcher centralisé du dossier issues_inbox/ (issue #483).
 
-Scrute en continu ~/Bridge_Agent/issues_inbox/ : chaque fichier .txt déposé
-(par Claude Chat ou manuellement) est parsé, validé, puis transformé en issue
-GitHub via `gh issue create` — même format d'en-tête et de labels que
-app/issues.py (construire_body/construire_labels), pour rester cohérent avec
-le flux du formulaire web. Le fichier traité est supprimé après création
-réussie ; un fichier invalide (PROJET inconnu, titre vide, etc.) est déplacé
-vers issues_inbox/rejected/ avec le détail de l'erreur en suffixe de nom.
+Scrute en continu ~/Bridge_Agent/issues_inbox/ : TOUT fichier déposé (par
+Claude Chat ou manuellement, quelle que soit son extension — issue #484,
+le dossier fonctionne comme un pool d'impression, rien n'y traîne
+silencieusement) est examiné. Un fichier .txt est parsé, validé, puis
+transformé en issue GitHub via `gh issue create` — même format d'en-tête et
+de labels que app/issues.py (construire_body/construire_labels), pour rester
+cohérent avec le flux du formulaire web. Le fichier traité est supprimé
+après création réussie ; un fichier invalide (PROJET inconnu, titre vide,
+extension différente de .txt, etc.) est déplacé vers issues_inbox/rejected/
+avec le détail de l'erreur en suffixe de nom.
 
 Usage :
     python3 scripts/watcher_issues_inbox.py
# ── Zone modifiée : ligne 363 (6 ligne(s)) dans l'ancienne version → ligne 366 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -363,6 +366,10 @@ def _fichier_pret(chemin: Path) -> bool:
 
 
 def traiter_fichier(cfg: ConfigInbox, chemin: Path) -> None:
+    if chemin.suffix.lower() != ".txt":
+        _rejeter(cfg, chemin, "", "", "extension invalide : attendu .txt")
+        return
+
     try:
         contenu = chemin.read_text(encoding="utf-8")
     except OSError as e:
# ── Zone modifiée : ligne 395 (7 ligne(s)) dans l'ancienne version → ligne 402 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -395,7 +402,9 @@ def traiter_fichier(cfg: ConfigInbox, chemin: Path) -> None:
 def traiter_dossier(cfg: ConfigInbox) -> None:
     if not cfg.inbox_dir.is_dir():
         return
-    for chemin in sorted(cfg.inbox_dir.glob("*.txt")):
+    for chemin in sorted(cfg.inbox_dir.glob("*")):
+        if chemin == cfg.rejected_dir:
+            continue
         if not chemin.is_file() or not _fichier_pret(chemin):
             continue
         try:
