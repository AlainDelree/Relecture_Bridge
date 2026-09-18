bd54a1f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bd54a1f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 15:44:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #352 : POST /notifier-fin-issue découplé des labels notif_*
    
    watcher.py appelle désormais traitement_fin.notifier_fin_issue()
    directement à chaque fin définitive d'issue (succès ou échec définitif),
    indépendamment de notifier()/bip() et donc des labels notif_pc/notif_gsm/
    notif_tous. Le rafraîchissement SSE de l'onglet Résultats devient
    universel. Bip et labels notif_* inchangés.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0087017..86e60b0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,28 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 3 août 2026 — issue #352
+
+Le POST `/notifier-fin-issue` (#350) était déclenché via `notifications.bip()`,
+donc uniquement pour les issues portant un label `notif_pc`/`notif_gsm`/
+`notif_tous` — le rafraîchissement SSE de l'onglet Résultats restait soumis
+au ↻ manuel pour toutes les autres. Il doit être universel, indépendamment
+des labels notif.
+
+- `watcher.py` : import direct de `scripts/traitement_fin.py` (ajout de
+  `scripts/` au `sys.path`, ce dossier n'étant pas un package) et nouvelle
+  enveloppe `notifier_fin_sse(numero)` qui appelle
+  `traitement_fin.notifier_fin_issue(CFG.nom, numero)` sans passer par
+  `notifier()`/`bip()` — donc sans dépendre des labels `notif_*`. Appelée
+  dans `_traiter_issue_synchrone` aux trois points de fin définitive d'une
+  issue : succès, échec définitif (garde-fou lecture active niveau 2, issue
+  #327), échec définitif après épuisement des tentatives (`max_essais`, non
+  critique). Non appelée sur les fins non définitives (retry différé d'une
+  issue critique, commentaire de résultat non posté) — l'issue reste ouverte
+  et sera retraitée.
+- Le bip et les labels `notif_*` restent inchangés — seul le POST est
+  découplé, comme demandé par l'issue.
+
 ## 3 août 2026 — issue #350
 
 Renommage de `scripts/bip.py` en `scripts/traitement_fin.py` et ajout d'un
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 5a628d5..42be1da 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 49 (6 ligne(s)) dans l'ancienne version → ligne 49 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -49,6 +49,13 @@ import notifications
 DOSSIER_SCRIPT = Path(__file__).resolve().parent
 DOSSIER_LOGS   = DOSSIER_SCRIPT / "logs"
 
+# scripts/traitement_fin.py (issue #352) : notifier_fin_issue() y est importée
+# directement (pas via subprocess comme le bip) pour pouvoir la déclencher à
+# chaque fin d'issue indépendamment des labels notif_* — voir notifier_fin_sse
+# ci-dessous. scripts/ n'est pas un package : on l'ajoute au sys.path.
+sys.path.insert(0, str(DOSSIER_SCRIPT / "scripts"))
+import traitement_fin
+
 # Consignes injectées dans le PROMPT donné à CCL (architecture à trois couches,
 # issues #209 puis #211). Vivent à côté du watcher (racine du dépôt), PAS dans le
 # rep_travail du projet piloté : elles sont communes à tous les projets. Trois
# ── Zone modifiée : ligne 440 (6 ligne(s)) dans l'ancienne version → ligne 447 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -440,6 +447,15 @@ def bip(fois=1, numero=None):
     anciennement bip.py)."""
     notifications.bip(CFG.script_bip, fois, projet=CFG.nom, numero=numero)
 
+def notifier_fin_sse(numero):
+    """POST direct vers /notifier-fin-issue (issue #352), appelé à CHAQUE fin
+    d'issue (succès ou échec définitif), DÉCOUPLÉ des labels notif_* : à la
+    différence de notifier() ci-dessous (bip/notify-send/ntfy, opt-in par
+    label), le rafraîchissement SSE de l'onglet Résultats doit être universel.
+    Best-effort, timeout court, échec silencieux — voir
+    traitement_fin.notifier_fin_issue."""
+    traitement_fin.notifier_fin_issue(CFG.nom, numero)
+
 def notifier_bureau(titre: str, message: str, urgence: str = "normal"):
     """Bulle de notification bureau via notify-send (voir notifications.py)."""
     notifications.notifier_bureau(CFG.nom, titre, message, urgence, log=log)
# ── Zone modifiée : ligne 3031 (6 ligne(s)) dans l'ancienne version → ligne 3047 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3031,6 +3047,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                         priorite_ntfy="high",
                         numero=numero,
                     )
+                    notifier_fin_sse(numero)
                     issues_en_cours.discard(numero)
                     return
 
# ── Zone modifiée : ligne 3111 (6 ligne(s)) dans l'ancienne version → ligne 3128 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3111,6 +3128,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                     priorite_ntfy="default",
                     numero=numero,
                 )
+                notifier_fin_sse(numero)
                 return
 
             # Échec
# ── Zone modifiée : ligne 3205 (6 ligne(s)) dans l'ancienne version → ligne 3223 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3205,6 +3223,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                         priorite_ntfy="high",
                         numero=numero,
                     )
+                    notifier_fin_sse(numero)
                     issues_en_cours.discard(numero)
                     return
 
