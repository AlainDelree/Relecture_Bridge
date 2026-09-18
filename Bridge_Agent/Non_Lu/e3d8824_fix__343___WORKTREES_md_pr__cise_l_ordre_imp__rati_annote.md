e3d8824

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e3d8824
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 23:51:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #343 : WORKTREES.md précise l'ordre impératif fusionner_changelog.py avant merge

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0f8bac3..7fc6fce 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,23 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #343
+
+`WORKTREES.md` §3 « Workflow normal d'Alain » (étape 3) et §4
+« Procédures de récupération » : précisions suite à un cas vécu lors du
+premier workflow complet avec worktrees (issues #340/#341, session du
+02/08/2026) — `fusionner_changelog.py` lancé depuis `master` avant le
+merge n'a rien trouvé, car le script scanne la racine du dépôt qu'on lui
+indique et `CHANGELOG-341.md` n'existait alors qu'à la racine du
+worktree ; le fichier s'est donc retrouvé dans `master` via le merge
+sans être intégré, nécessitant un commit de rattrapage. L'étape 3
+documente désormais l'ordre impératif (script avant merge) et deux
+méthodes : lancer `--repo .` depuis le worktree lui-même (recommandé),
+ou copier `CHANGELOG-<N>.md` dans master avant de fusionner depuis
+`REP_TRAVAIL`. Le §4 précise la procédure de rattrapage si le merge a
+eu lieu avant le script (relancer le script depuis `REP_TRAVAIL`,
+vérifier `git diff CHANGELOG.md`, committer).
+
 ## 2 août 2026 — issue #341
 
 Ajout dans `TACHES.md`, juste après le bloc d'en-tête, d'une section
