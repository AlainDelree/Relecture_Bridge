f1ec3d4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f1ec3d4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 30 16:31:39 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #507 : CONTEXTE.md — remplace les deux mentions de VM Windows par PC Windows physique

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-507.md b/CHANGELOG-507.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..d237a87
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-507.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,8 @@
+## #507 — CONTEXTE.md : correction de deux mentions obsolètes de "VM Windows"
+
+`CONTEXTE.md` mentionnait encore « VM Windows » à deux endroits (description
+du module `app/ccw` et entrée changelog §16), alors que la migration vers un
+PC fixe physique est actée depuis longtemps (`BRIDGE_AGENT_DOC.md` §16,
+issue #446). Remplacé par « PC Windows physique », cohérent avec le
+vocabulaire de `BRIDGE_AGENT_DOC.md`. Vérifié qu'aucune autre mention de VM
+ne subsiste dans le fichier.
# (diff du fichier suivant)
diff --git a/CONTEXTE.md b/CONTEXTE.md
# (index — ignorable)
index 8220c61..88cf051 100644
# (avant — fichier suivant)
--- a/CONTEXTE.md
# (après — fichier suivant)
+++ b/CONTEXTE.md
# ── Zone modifiée : ligne 24 (7 ligne(s)) dans l'ancienne version → ligne 24 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,7 +24,7 @@ Bridge_Agent se développe lui-même par ses propres issues (dogfooding).
   dans `app.config`, routes via `add_url_rule`. Modules : `auth`, `projets`
   (config `.conf`), `watchers` (start/stop/état), `issues` (création/suivi,
   pièces jointes image), `journal`, `cycle_vie` (heartbeat/SSE), `ccw`
-  (onglet pilotage VM Windows), `notifications_poller` (thread démon
+  (onglet pilotage PC Windows physique), `notifications_poller` (thread démon
   détectant les transitions d'issues pour bip/notify-send/ntfy), `tunnel`,
   `etat`, `vues`.
 - **`templates/`** (`index.html`, Jinja2), **`static/`** (css/js/img).
# ── Zone modifiée : ligne 65 (7 ligne(s)) dans l'ancienne version → ligne 65 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -65,7 +65,7 @@ Bridge_Agent se développe lui-même par ses propres issues (dogfooding).
   formats/limite dans l'UI.
 - §17 (#187) : notifications centralisées — `new_issue.py` détecte lui-même les
   transitions d'issues (tous projets, y compris CCW) et notifie localement.
-- §16 (#174…) : onglet « CCW » — pilotage complet de la VM Windows depuis Linux.
+- §16 (#174…) : onglet « CCW » — pilotage complet du PC Windows physique depuis Linux.
 - #186/#185 : `git pull --ff-only` automatique en début de cycle du watcher.
 
 ## Maintenance de ce fichier
