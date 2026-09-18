3c89e72

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3c89e72
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 01:40:37 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Fusionner CHANGELOG-345.md dans CHANGELOG.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-345.md b/CHANGELOG-345.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 294bede..0000000
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG-345.md
# ── Version APRÈS ce commit.
+++ /dev/null
# ── Zone modifiée : ligne 1 (17 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,17 +0,0 @@
-### Ajouté
-
-- **Issue #345** — `build/rebuild_scrabble.bat` produit désormais un second
-  artefact : `installeur\output\scrabble.zip`, destiné à être publié comme
-  asset de Release GitHub et téléchargé/extrait par l'updater Actualise.
-
-  Avant la compilation Inno Setup, le script télécharge `actualise.zip`
-  depuis la Release v1 de `AlainDelree/Actualise` et en extrait
-  `Actualise.exe` vers `C:\Temp\ScrabbleBuild\Actualise.exe` (chemin source
-  attendu par `installeur\scrabble.iss`) ; tout échec de téléchargement ou
-  d'extraction arrête le build avec un message d'erreur explicite.
-
-  Après la compilation, le script génère `manifest.json`
-  (`{"build": 1, "supprimer": []}`) puis zippe le contenu de
-  `dist\Scrabble\` avec ce manifeste vers `installeur\output\scrabble.zip`
-  (nom fixe, sans numéro de version — celui-ci vit dans le tag de la
-  Release GitHub), vérifie sa présence et affiche sa taille.
