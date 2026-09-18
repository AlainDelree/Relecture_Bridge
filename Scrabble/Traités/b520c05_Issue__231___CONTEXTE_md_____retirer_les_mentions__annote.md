b520c05

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b520c05
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 07:32:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #231 : CONTEXTE.md — retirer les mentions des sous-paquets supprimés (#229)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONTEXTE.md b/CONTEXTE.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 69af22f..269efd0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONTEXTE.md
# ── Version APRÈS ce commit.
+++ b/CONTEXTE.md
# ── Zone modifiée : ligne 31 (9 ligne(s)) dans l'ancienne version → ligne 31 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,9 +31,11 @@ table, réglages) puis enchaîne vers l'écran de jeu.
 - **`config.py`** (config auto-réparante `config.json`), `reglages.py`,
   `journal.py` (logs dans `logs/`).
 
-Hérité/non utilisé (ne pas s'y fier) : `src/scrabble/interface/` (stub « non
-implémenté »), `src/scrabble/ia/`, `src/scrabble/generateur/` et le dossier
-racine **`web/`** — vestiges d'une ancienne interface web abandonnée.
+Note : les anciens sous-paquets reliquats `src/scrabble/interface/`,
+`src/scrabble/ia/`, `src/scrabble/generateur/` et le dossier racine `web/`
+(vestiges d'une interface web abandonnée) ont été supprimés (issue #229). Le
+vrai code vit désormais dans `scrabble.moteur.generateur`, `scrabble.moteur.ia`,
+`scrabble.ui.application` et `src/scrabble/ui/web/` respectivement.
 
 `scripts/` = outils hors-jeu (génération d'avatars/icônes, construction du
 dictionnaire de définitions, filtres Wiktionnaire) et `_harness_jeu/`
