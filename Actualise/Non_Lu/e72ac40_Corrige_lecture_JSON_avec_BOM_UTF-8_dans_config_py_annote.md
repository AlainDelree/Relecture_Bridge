e72ac40

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e72ac40
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 11 13:44:35 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige lecture JSON avec BOM UTF-8 dans config.py (issue #46)
    
    _charger_json utilise désormais utf-8-sig au lieu de utf-8 pour lire
    config_actualise.json / config_<app>.json : InnoSetup écrit ces
    fichiers en UTF-8 avec BOM, ce qui faisait planter json.load avec
    JSONDecodeError. utf-8-sig retire silencieusement le BOM s'il est
    présent et se comporte comme utf-8 sinon.
    
    Ajoute un test couvrant la lecture avec BOM.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/config.py b/config.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c2c9345..cbde3f3 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/config.py
# ── Version APRÈS ce commit.
+++ b/config.py
# ── Zone modifiée : ligne 63 (7 ligne(s)) dans l'ancienne version → ligne 63 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -63,7 +63,7 @@ def _nom_fichier_app(nom_app: str) -> str:
 
 
 def _charger_json(chemin_fichier: Path) -> dict[str, Any]:
-    with open(chemin_fichier, encoding="utf-8") as f:
+    with open(chemin_fichier, encoding="utf-8-sig") as f:
         return json.load(f)
 
 
# (diff du fichier suivant)
diff --git a/tests/test_config.py b/tests/test_config.py
# (index — ignorable)
index 3a1d518..14f0d89 100644
# (avant — fichier suivant)
--- a/tests/test_config.py
# (après — fichier suivant)
+++ b/tests/test_config.py
# ── Zone modifiée : ligne 162 (6 ligne(s)) dans l'ancienne version → ligne 162 (54 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -162,6 +162,54 @@ class TestChargerConfig(unittest.TestCase):
         with self.assertRaises(json.JSONDecodeError):
             charger_config("scrabble")
 
+    def test_fichiers_avec_bom_utf8_sont_lus_correctement(self):
+        # InnoSetup écrit les JSON en UTF-8 avec BOM — voir issue #46.
+        (self.chemin_dossier / "config_actualise.json").write_text(
+            json.dumps(
+                {
+                    "build_installe": 6,
+                    "depot_github": "AlainDelree/Actualise",
+                    "zone_attente": "C:\\Actualise\\attente\\",
+                }
+            ),
+            encoding="utf-8-sig",
+        )
+        (self.chemin_dossier / "config_scrabble.json").write_text(
+            json.dumps(
+                {
+                    "nom": "Scrabble",
+                    "depot_github": "AlainDelree/Scrabble",
+                    "build_installe": 5,
+                    "repertoire_installation": "C:\\Scrabble\\",
+                    "executable": "Scrabble.exe",
+                    "icone": "C:\\Scrabble\\Scrabble.ico",
+                    "topic_ntfy": "actualise-scrabble",
+                }
+            ),
+            encoding="utf-8-sig",
+        )
+
+        self.assertEqual(
+            charger_config("scrabble"),
+            {
+                "actualise": {
+                    "build_installe": 6,
+                    "depot_github": "AlainDelree/Actualise",
+                },
+                "application_cible": {
+                    "nom": "Scrabble",
+                    "depot_github": "AlainDelree/Scrabble",
+                    "build_installe": 5,
+                    "repertoire_installation": "C:\\Scrabble\\",
+                    "executable": "Scrabble.exe",
+                    "icone": "C:\\Scrabble\\Scrabble.ico",
+                    "topic_ntfy": "actualise-scrabble",
+                },
+                "zone_attente": "C:\\Actualise\\attente\\",
+                "topic_ntfy": "actualise-scrabble",
+            },
+        )
+
 
 class TestSauvegarderConfigActualise(unittest.TestCase):
     def setUp(self):
