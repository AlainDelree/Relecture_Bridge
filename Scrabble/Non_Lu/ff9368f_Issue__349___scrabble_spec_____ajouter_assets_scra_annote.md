ff9368f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ff9368f
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 14:24:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #349 : scrabble.spec — ajouter assets/scrabble.ico aux datas PyInstaller

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scrabble.spec b/scrabble.spec
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4f115cc..b9ee94c 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/scrabble.spec
# ── Version APRÈS ce commit.
+++ b/scrabble.spec
# ── Zone modifiée : ligne 205 (6 ligne(s)) dans l'ancienne version → ligne 205 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -205,6 +205,13 @@ def verifier_taille_datas(datas, seuil_octets):
 
 
 datas = []
+# Icône du jeu, copiée à la racine de dist/Scrabble/ (aux côtés de Scrabble.exe) :
+# le paramètre icon= de EXE() ci-dessous ne fait que l'intégrer comme ressource
+# de l'exécutable, il ne la copie pas comme fichier de données. Or scrabble.iss
+# référence "{app}\scrabble.ico" via IconFilename pour les raccourcis (issue
+# #348) — sans cette entrée, ce fichier serait absent après installation
+# (issue #349).
+datas += [(os.path.join(RACINE, "assets", "scrabble.ico"), ".")]
 # Assets web (HTML/CSS/JS/avatars SVG + images PNG comme web/images/sac.png)
 # des fenêtres accueil (réglages intégrés)/jeu/chevalet. ``collect_tree`` marche
 # via ``os.walk`` sans filtre d'extension : tout fichier de ``web/`` est embarqué
