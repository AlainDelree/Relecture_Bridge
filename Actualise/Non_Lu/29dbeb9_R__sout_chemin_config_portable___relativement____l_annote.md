29dbeb9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 29dbeb9
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 16:12:49 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Résout chemin_config_portable() relativement à l'exécutable (issue #28, suite #9)
    
    En mode PyInstaller figé (sys.frozen), le dossier de configuration est
    désormais le dossier contenant Actualise.exe (via sys.executable),
    plutôt que %SYSTEMDRIVE%\Actualise\ codé en dur. Permet plusieurs
    installations indépendantes d'Actualise (une par application cible)
    sans collision de config.json.
    
    En mode script non figé (dev/tests, sys.frozen absent), repli inchangé
    sur %SYSTEMDRIVE%\Actualise\ pour ne pas casser les tests/dev existants.
    Linux inchangé.
    
    Tests ajoutés pour le mode figé (sys.executable mocké), tests Windows
    existants renommés pour clarifier qu'ils couvrent le mode non figé.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/config.py b/config.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index dc2f3ea..c714cc7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/config.py
# ── Version APRÈS ce commit.
+++ b/config.py
# ── Zone modifiée : ligne 18 (19 ligne(s)) dans l'ancienne version → ligne 18 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -18,19 +18,34 @@ _NOM_FICHIER_CONFIG = "config.json"
 def chemin_config_portable() -> Path:
     """Retourne le chemin du dossier de configuration selon l'OS.
 
-    Windows : ``%SYSTEMDRIVE%\\Actualise\\`` — la variable
-    d'environnement ``SYSTEMDRIVE`` est préférée à un ``C:`` en dur pour
-    rester correct sur une installation où le disque système n'est pas
-    ``C:`` ; à défaut de cette variable (cas anormal), repli sur
-    ``C:`` (voir CONCEPTION.md, « Configuration portable »).
-
-    Linux (et autres OS non Windows) : variable d'environnement
-    ``ACTUALISE_CONFIG_DIR`` si définie, sinon ``~/.config/actualise/``.
+    Windows, mode PyInstaller figé (``sys.frozen`` vrai) : dossier
+    contenant l'exécutable ``Actualise.exe`` lui-même, obtenu via
+    ``sys.executable`` — et non un chemin Windows fixe. Ceci permet
+    plusieurs installations indépendantes d'Actualise sur la même
+    machine (une par application cible) sans qu'une installation
+    n'écrase le ``config.json`` d'une autre (voir CONCEPTION.md,
+    « Configuration portable »).
+
+    Windows, mode script non figé (développement/tests, ``sys.frozen``
+    absent ou faux) : repli sur l'ancien comportement,
+    ``%SYSTEMDRIVE%\\Actualise\\`` — la variable d'environnement
+    ``SYSTEMDRIVE`` est préférée à un ``C:`` en dur pour rester correct
+    sur une installation où le disque système n'est pas ``C:`` ; à
+    défaut de cette variable (cas anormal), repli sur ``C:``.
+
+    Linux (et autres OS non Windows) : comportement inchangé — variable
+    d'environnement ``ACTUALISE_CONFIG_DIR`` si définie, sinon
+    ``~/.config/actualise/`` ; la problématique de collision
+    multi-installations ne s'y pose pas de la même façon (voir
+    CONCEPTION.md, « Configuration portable »).
 
     Ne crée pas le dossier — résolution de chemin uniquement (voir
     ``sauvegarder_config`` pour la création).
     """
     if sys.platform == "win32":
+        if getattr(sys, "frozen", False):
+            return Path(sys.executable).parent
+
         lecteur_systeme = os.environ.get("SYSTEMDRIVE", "C:")
         return Path(f"{lecteur_systeme}/Actualise")
 
# (diff du fichier suivant)
diff --git a/tests/test_config.py b/tests/test_config.py
# (index — ignorable)
index 1fee2fe..c1a9ef7 100644
# (avant — fichier suivant)
--- a/tests/test_config.py
# (après — fichier suivant)
+++ b/tests/test_config.py
# ── Zone modifiée : ligne 19 (14 ligne(s)) dans l'ancienne version → ligne 19 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -19,14 +19,42 @@ from config import chemin_config_portable, charger_config, sauvegarder_config
 class TestCheminConfigPortable(unittest.TestCase):
     @patch("config.os.environ", {"SYSTEMDRIVE": "D:"})
     @patch("config.sys.platform", "win32")
-    def test_windows_avec_systemdrive(self):
+    def test_windows_non_fige_avec_systemdrive(self):
+        # Mode script non figé (sys.frozen absent) : repli sur
+        # l'ancien comportement, utile pour les tests/développement.
         self.assertEqual(chemin_config_portable(), Path("D:/Actualise"))
 
     @patch("config.os.environ", {})
     @patch("config.sys.platform", "win32")
-    def test_windows_sans_systemdrive_repli_sur_c(self):
+    def test_windows_non_fige_sans_systemdrive_repli_sur_c(self):
         self.assertEqual(chemin_config_portable(), Path("C:/Actualise"))
 
+    @patch("config.sys.executable", "D:/Apps/Actualise_Scrabble/Actualise.exe")
+    @patch("config.sys.frozen", True, create=True)
+    @patch("config.sys.platform", "win32")
+    def test_windows_fige_pyinstaller_relatif_executable(self):
+        # Mode PyInstaller figé : dossier contenant Actualise.exe,
+        # résolu via sys.executable — pas un chemin fixe (voir
+        # CONCEPTION.md, « Configuration portable »).
+        self.assertEqual(
+            chemin_config_portable(),
+            Path("D:/Apps/Actualise_Scrabble"),
+        )
+
+    @patch(
+        "config.sys.executable",
+        "C:/Apps/Actualise_Rummikub/Actualise.exe",
+    )
+    @patch("config.sys.frozen", True, create=True)
+    @patch("config.sys.platform", "win32")
+    def test_windows_fige_pyinstaller_installations_independantes(self):
+        # Deux installations distinctes (une par application cible)
+        # résolvent vers des dossiers différents, sans collision.
+        self.assertEqual(
+            chemin_config_portable(),
+            Path("C:/Apps/Actualise_Rummikub"),
+        )
+
     @patch("config.os.environ", {"ACTUALISE_CONFIG_DIR": "/tmp/config-actualise-test"})
     @patch("config.sys.platform", "linux")
     def test_linux_avec_variable_environnement(self):
