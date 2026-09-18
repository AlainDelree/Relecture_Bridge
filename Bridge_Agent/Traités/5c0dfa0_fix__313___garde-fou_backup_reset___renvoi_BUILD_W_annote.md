5c0dfa0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5c0dfa0
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 10:38:06 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #313 : garde-fou backup/reset + renvoi BUILD_WINDOWS_CCW.md dans consignes/globales.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 46c991d..2a1498b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,23 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #313
+
+`consignes/globales.md` : ajout de deux garde-fous mutualisés à tous les
+projets (injection automatique, aucune modification de `CONTEXTE.md` par
+projet nécessaire). (1) Garde-fou backup/reset : le commit de sauvegarde
+(`git add -A`) peut faire passer sous suivi git des dossiers auparavant
+non trackés (ex. `.tools/`, `installeur/output/`) ; si le script exécuté
+ensuite se termine par une opération git destructive (`reset --hard`,
+`clean -fd`), ces dossiers seraient effacés du disque — vérifier via
+`git status`/`git show --stat` et détracker (`git rm --cached`) avant de
+lancer un tel script. Problème constaté et corrigé au cas par cas sur
+Scrabble et Rummikub (issues #306, #311). (2) Renvoi vers
+`BUILD_WINDOWS_CCW.md` (dépôt bridge_agent, racine) avant de proposer une
+issue de build ou de modification de pipeline sur un projet ayant un
+script de build Windows (PyInstaller/Inno Setup) — documente le pattern
+de staging local et l'extension du PÉRIMÈTRE associée (issue #297/#299).
+
 ## 2 août 2026 — issue #312
 
 `TACHES.md` : retrait des trois entrées de backlog désormais
# (diff du fichier suivant)
diff --git a/consignes/globales.md b/consignes/globales.md
# (index — ignorable)
index e556e93..cd0482a 100644
# (avant — fichier suivant)
--- a/consignes/globales.md
# (après — fichier suivant)
+++ b/consignes/globales.md
# ── Zone modifiée : ligne 34 (3 ligne(s)) dans l'ancienne version → ligne 34 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -34,3 +34,19 @@
   programmé, et toute formulation du type « je répondrai/poursuivrai quand… »
   / « j'attends la fin de… » en guise de conclusion. Le watcher ferme
   l'issue dès ta réponse postée : il n'existe AUCUNE reprise possible.
+- **Garde-fou backup/reset :** le commit de sauvegarde (`git add -A`)
+  peut faire passer sous suivi git des dossiers auparavant non trackés
+  (ex. `.tools/`, `installeur/output/`). Si le script à exécuter ensuite
+  se termine par une opération git destructive (`reset --hard`, `clean
+  -fd`), ces dossiers fraîchement trackés seraient effacés du disque
+  puisqu'absents de `origin/master`. Avant de lancer un tel script,
+  vérifie si le commit de sauvegarde a capturé des fichiers/dossiers
+  auparavant non suivis (`git status` avant/après le commit, ou `git
+  show --stat` sur ce commit) ; si oui, détracke-les (`git rm --cached`,
+  sans supprimer du disque) avant de lancer le script.
+- **Build Windows :** si le projet courant a un script de build Windows
+  (PyInstaller/Inno Setup ou équivalent), consulte `BUILD_WINDOWS_CCW.md`
+  (dépôt bridge_agent, à la racine) avant de proposer une issue de build
+  ou de modification du pipeline — il documente le pattern de staging
+  local, l'extension du PÉRIMÈTRE associée, et une checklist par projet
+  déjà buildé.
