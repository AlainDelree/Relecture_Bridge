f737425

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f737425
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 08:48:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Retirer le fallback _niclink/pybind11 mort, backend hidapi seul (issue #203)
    
    - driver.py : suppression du try/except de repli vers l'extension C++
      _niclink.so (pybind11), remplacé par un ImportError explicite si
      hidapi/hid_backend.py ne peut pas être chargé.
    - pyproject.toml : retrait de pybind11>=2.10.0 du build-system, plus
      nécessaire (les sources C++/CMake ont déjà été supprimées du dépôt
      par le commit 26c8205 'chore: nettoyage dossiers et fichiers obsolètes').
    - __init__.py : commentaire mis à jour (plus de fallback .so).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/niclink/__init__.py b/nicsoft/niclink/__init__.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9fbf5f8..96a20cf 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/niclink/__init__.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/niclink/__init__.py
# ── Zone modifiée : ligne 1 (2 ligne(s)) dans l'ancienne version → ligne 1 (2 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,2 +1,2 @@
 from . import driver
-from .driver import NicLinkManager, _niclink  # _niclink = hid_backend ou .so selon disponibilité
+from .driver import NicLinkManager, _niclink  # _niclink = hid_backend (backend hidapi)
# (diff du fichier suivant)
diff --git a/nicsoft/niclink/driver.py b/nicsoft/niclink/driver.py
# (index — ignorable)
index 4208bda..5a953f0 100755
# (avant — fichier suivant)
--- a/nicsoft/niclink/driver.py
# (après — fichier suivant)
+++ b/nicsoft/niclink/driver.py
# ── Zone modifiée : ligne 28 (9 ligne(s)) dans l'ancienne version → ligne 28 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,9 +28,12 @@ import numpy as np
 import numpy.typing as npt
 
 try:
-    from . import hid_backend as _niclink  # backend Python pur, multiplateforme
-except ImportError:
-    from . import _niclink  # fallback : extension C++ compilée (.so)
+    from . import hid_backend as _niclink  # backend Python pur (hidapi), multiplateforme
+except ImportError as exc:
+    raise ImportError(
+        "Impossible de charger le backend hidapi (nicsoft/niclink/hid_backend.py). "
+        "Vérifiez que le paquet 'hidapi' est installé (pip install hidapi)."
+    ) from exc
 
 # mine
 from .nl_exceptions import ExitNicLink, IllegalMove, NoMove, NoNicLinkFen
# (diff du fichier suivant)
diff --git a/nicsoft/pyproject.toml b/nicsoft/pyproject.toml
# (index — ignorable)
index 4f71d17..0ec8865 100755
# (avant — fichier suivant)
--- a/nicsoft/pyproject.toml
# (après — fichier suivant)
+++ b/nicsoft/pyproject.toml
# ── Zone modifiée : ligne 6 (7 ligne(s)) dans l'ancienne version → ligne 6 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6,7 +6,6 @@
 [build-system]
 requires = [
     "setuptools>=42",
-    "pybind11>=2.10.0",
 ]
 build-backend = "setuptools.build_meta"
 
