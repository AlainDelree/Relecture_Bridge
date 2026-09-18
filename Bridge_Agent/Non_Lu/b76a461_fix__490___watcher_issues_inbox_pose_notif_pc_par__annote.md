b76a461

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b76a461
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 22:37:54 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #490 : watcher_issues_inbox pose notif_pc par défaut (sauf notif_gsm/notif_tous explicite)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2f47a5e..9a25778 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 2321 (6 ligne(s)) dans l'ancienne version → ligne 2321 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2321,6 +2321,15 @@ Même format qu'une issue produite par Claude Chat pour le formulaire web
 | `MODE`    | Reconnu de façon tolérante (§5) — absent/non reconnu → `lecture`     |
 | `LABELS`  | Labels GitHub additionnels, séparés par des virgules                 |
 
+Label de notification par défaut (issue #490) : `construire_labels()` pose
+systématiquement **`notif_pc`** (miroir du comportement le plus courant côté
+formulaire web), sauf si `LABELS` demande déjà explicitement `notif_gsm` ou
+`notif_tous` — dans ce cas `notif_pc` n'est pas ajouté en plus, pour ne
+jamais empiler plusieurs labels de notification. Sans ce label, une issue
+créée via `issues_inbox/` ne déclenchait aucun bip à sa clôture
+(`notifications.bip()`, cf. `watcher.py`), contrairement à celles créées via
+le formulaire.
+
 Le fichier est reparsé avec les mêmes regex que `static/js/app.js` (détection
 de champ d'en-tête à la frappe côté formulaire web), pour ne jamais diverger
 du format déjà produit par Claude Chat.
# (diff du fichier suivant)
diff --git a/scripts/watcher_issues_inbox.py b/scripts/watcher_issues_inbox.py
# (index — ignorable)
index ac5de3d..53bed68 100644
# (avant — fichier suivant)
--- a/scripts/watcher_issues_inbox.py
# (après — fichier suivant)
+++ b/scripts/watcher_issues_inbox.py
# ── Zone modifiée : ligne 48 (7 ligne(s)) dans l'ancienne version → ligne 48 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -48,7 +48,8 @@ from pathlib import Path
 DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
 sys.path.insert(0, str(DOSSIER_SCRIPT))
 
-from watcher import charger_config, lire_conf, est_titre_chef  # noqa: E402
+from watcher import (charger_config, lire_conf, est_titre_chef,  # noqa: E402
+                     LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS)
 from app.watchers import demarrer_watcher  # noqa: E402 (issue #486)
 
 log = logging.getLogger("watcher_issues_inbox")
# ── Zone modifiée : ligne 247 (6 ligne(s)) dans l'ancienne version → ligne 248 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -247,6 +248,9 @@ def valider(champs: dict):
 LABELS_RE = re.compile(r"^\s*\|\s*LABELS\s*\|([^|]*)\|", re.IGNORECASE | re.MULTILINE)
 
 
+LABELS_NOTIF = {LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS}
+
+
 def construire_labels(champs: dict) -> str:
     extras = [lab.strip() for lab in (champs["labels_brut"] or "").split(",") if lab.strip()]
     labels = ["bridge"]
# ── Zone modifiée : ligne 258 (6 ligne(s)) dans l'ancienne version → ligne 262 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -258,6 +262,11 @@ def construire_labels(champs: dict) -> str:
     for extra in extras:
         if extra not in labels:
             labels.append(extra)
+    # Label de notification par défaut (issue #490) : notif_pc, sauf si le
+    # champ LABELS demande déjà explicitement notif_gsm/notif_tous (miroir du
+    # comportement le plus courant côté formulaire, app/issues.py::construire_labels).
+    if not (LABELS_NOTIF & set(labels)):
+        labels.append(LABEL_NOTIF_PC)
     return ",".join(labels)
 
 
