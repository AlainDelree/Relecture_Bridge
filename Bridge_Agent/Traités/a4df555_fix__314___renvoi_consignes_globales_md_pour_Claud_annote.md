a4df555

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a4df555
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 10:51:33 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #314 : renvoi consignes/globales.md pour Claude en conversation

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index fd99322..c786f63 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 507 (6 ligne(s)) dans l'ancienne version → ligne 507 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -507,6 +507,14 @@ les projets) :
 | **Type** | `consignes/type_<type>.md` | Issues d'un TYPE donné (ex. `type_chef.md`) | **Oui** — créé à la demande |
 | **Projet** | `consignes/projet_<projet>.md` | Issues ciblant un projet donné | **Oui** — créé à la demande |
 
+⚠️ **Pour un Claude en conversation** (celui qui rédige une issue avant de
+l'envoyer) : ce tableau décrit une injection qui n'a lieu qu'à l'exécution
+(CCL/CCW) — tu ne vois donc pas ce contenu ici. Avant de proposer une issue,
+consulte `consignes/globales.md` (rappels de sécurité, garde-fous) via :
+```bash
+curl -sL "https://raw.githubusercontent.com/AlainDelree/Bridge_Agent/master/consignes/globales.md"
+```
+
 **Couverture universelle (issue #211).** Une issue peut naître de trois chemins :
 (1) le formulaire web (`new_issue.py`), (2) un CCL « chef » via `gh issue create`
 en ligne de commande (§14, pattern Chef → Ouvrier), (3) une création manuelle
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 2a1498b..af87497 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,19 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #314
+
+`BRIDGE_AGENT_DOC.md` (§12.1, juste après le tableau des trois couches
+de consignes) : ajout d'un renvoi explicite pour un Claude en
+conversation (celui qui rédige une issue avant envoi, ex.
+ClaudeRummikub) vers `consignes/globales.md` via `curl`, sur le même
+modèle que le renvoi déjà existant vers `BRIDGE_AGENT_DOC.md` lui-même
+(§9). Jusqu'ici le tableau décrivait l'injection automatique par
+`watcher.py` à l'exécution (CCL/CCW) sans jamais pointer un Claude en
+conversation vers le contenu réel de `globales.md` — notamment le
+garde-fou backup/reset ajouté par l'issue #313, invisible avant que
+l'issue parte à l'exécution.
+
 ## 2 août 2026 — issue #313
 
 `consignes/globales.md` : ajout de deux garde-fous mutualisés à tous les
