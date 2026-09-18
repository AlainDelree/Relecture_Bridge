1d157d0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1d157d0
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 14:04:59 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #402 : entrée CHANGELOG-402.md
    
    Co-Authored-By: CCL agent <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-402.md b/CHANGELOG-402.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..b4e5b5f
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-402.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,30 @@
+# Issue #402 : refonte niveaux — dictionnaire, accueil.py, UI HTML/JS (B/4)
+
+Suite de la refonte de l'échelle des niveaux IA (issue #400) : EXPERT
+utilise désormais l'ODS8 complet (comme CHAMPION_DU_MONDE), sans palier de
+vocabulaire restreint.
+
+- `dictionnaire.py` : suppression de la clé `"expert"` de
+  `FICHIERS_VOCABULAIRE_PALIER` (4 entrées restantes : debutant/facile/
+  intermediaire/avance) ; commentaires et docstrings mis à jour partout où
+  seul CHAMPION_DU_MONDE était mentionné comme niveau sans palier ; `VERSION_CACHE`
+  incrémentée (3 → 4) pour invalider les caches Trie IA existants construits
+  sous l'ancien mapping.
+- `accueil.py` : `_disponibilite_niveau()` traite désormais EXPERT comme
+  CHAMPION_DU_MONDE — toujours disponible, sans vérification de fichier
+  palier. `_construire_trie_ia()` corrigé dans la foulée (même défense en
+  profondeur) : sans ce correctif, une partie avec un ordinateur Expert
+  levait un `KeyError: 'expert'` tant que `moteur/ia.py::resoudre_palier`
+  n'a pas lui-même été mis à jour par le lot complémentaire (hors périmètre
+  de cette issue). `NIVEAUX_LABELS` vérifié cohérent (6 entrées, inchangé).
+- `accueil.js` : commentaire de `appliquerDisponibiliteNiveaux` mis à jour
+  (EXPERT + Champion du monde, sans fichier palier). `jeu.js` déjà
+  cohérent, aucun changement nécessaire.
+
+Point d'attention : `moteur/ia.py` (`resoudre_palier`, hors périmètre
+strict de cette issue) mappe encore `Niveau.EXPERT` vers la clé de palier
+`"expert"` — ce module doit être mis à jour par un lot complémentaire pour
+que la cohérence soit complète. Plusieurs tests existants (`test_accueil.py`,
+`test_dictionnaire.py`, `test_moteur_ia.py`, `test_generer_mots_courants.py`)
+vérifient encore l'ancien mapping à 5 paliers et échoueront jusqu'à cette
+mise à jour ; les tests n'étaient pas dans le périmètre de cette issue.
