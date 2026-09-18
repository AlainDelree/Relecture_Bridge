01b0ab9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 01b0ab9
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 23:05:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    implémentation de verifier_version dans version_check.py (issue #10, suite #9)
    
    - Construit l'URL du version.json distant via raw.githubusercontent.com
      en utilisant la référence spéciale HEAD (résout la branche par défaut
      sans appel API supplémentaire).
    - Requête GET avec le timeout strict TIMEOUT_RESEAU_SECONDES déjà défini.
    - Repli silencieux sur None pour tout échec réseau (timeout, connexion,
      HTTP 4xx/5xx via raise_for_status, JSON invalide) avec un log de
      niveau debug pour la traçabilité, sans exception propagée.
    - Comparaison entière stricte distant.build > build_installe (jamais de
      comparaison de chaînes, cf. piège documenté dans CONCEPTION.md).
    - Ajout de tests/test_version_check.py (unittest.mock, sans dépendance
      de test supplémentaire) couvrant : build supérieur, build
      inférieur/égal, timeout réseau, JSON invalide.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/__init__.py b/tests/__init__.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..e69de29
# (diff du fichier suivant)
diff --git a/tests/test_version_check.py b/tests/test_version_check.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..d3a80da
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/tests/test_version_check.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (57 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,57 @@
+"""Tests unitaires pour ``verifier_version`` (version_check.py).
+
+Aucun appel réseau réel : les réponses HTTP sont simulées via
+``unittest.mock``. Voir CONCEPTION.md, « Format de version » et
+« Vérification réseau — timeout strict ».
+"""
+
+import unittest
+from unittest.mock import MagicMock, patch
+
+import requests
+
+from version_check import verifier_version
+
+
+class TestVerifierVersion(unittest.TestCase):
+    @patch("version_check.requests.get")
+    def test_build_superieur_retourne_le_dict_complet(self, mock_get):
+        reponse_simulee = MagicMock()
+        reponse_simulee.json.return_value = {"build": 48, "sha256": "abc123"}
+        mock_get.return_value = reponse_simulee
+
+        resultat = verifier_version("owner/repo", build_installe=47)
+
+        self.assertEqual(resultat, {"build": 48, "sha256": "abc123"})
+
+    @patch("version_check.requests.get")
+    def test_build_inferieur_ou_egal_retourne_none(self, mock_get):
+        reponse_simulee = MagicMock()
+        reponse_simulee.json.return_value = {"build": 47, "sha256": "abc123"}
+        mock_get.return_value = reponse_simulee
+
+        resultat = verifier_version("owner/repo", build_installe=47)
+
+        self.assertIsNone(resultat)
+
+    @patch("version_check.requests.get")
+    def test_timeout_reseau_retourne_none_sans_exception(self, mock_get):
+        mock_get.side_effect = requests.exceptions.Timeout
+
+        resultat = verifier_version("owner/repo", build_installe=47)
+
+        self.assertIsNone(resultat)
+
+    @patch("version_check.requests.get")
+    def test_json_invalide_retourne_none_sans_exception(self, mock_get):
+        reponse_simulee = MagicMock()
+        reponse_simulee.json.side_effect = ValueError("JSON invalide")
+        mock_get.return_value = reponse_simulee
+
+        resultat = verifier_version("owner/repo", build_installe=47)
+
+        self.assertIsNone(resultat)
+
+
+if __name__ == "__main__":
+    unittest.main()
# (diff du fichier suivant)
diff --git a/version_check.py b/version_check.py
# (index — ignorable)
index c4e7347..81cc68c 100644
# (avant — fichier suivant)
--- a/version_check.py
# (après — fichier suivant)
+++ b/version_check.py
# ── Zone modifiée : ligne 4 (8 ligne(s)) dans l'ancienne version → ligne 4 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,8 +4,11 @@ Voir CONCEPTION.md, sections « Format de version », « Deux fichiers
 version.json distincts » et « Vérification réseau — timeout strict ».
 """
 
+import logging
 from typing import Any
 
+import requests
+
 # Timeout strict (2 à 3 secondes) sur toute requête réseau de
 # vérification de version. Au-delà, la vérification est traitée comme
 # un échec réseau et on se rabat silencieusement sur la version
# ── Zone modifiée : ligne 13 (6 ligne(s)) dans l'ancienne version → ligne 16 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -13,6 +16,14 @@ from typing import Any
 # strict » et « Décisions actées »).
 TIMEOUT_RESEAU_SECONDES = 3
 
+_LOGGER = logging.getLogger(__name__)
+
+# ``HEAD`` est une référence spéciale reconnue par raw.githubusercontent.com
+# qui résout toujours vers la branche par défaut du dépôt, sans avoir à la
+# connaître à l'avance ni à passer par l'API GitHub (voir CONCEPTION.md,
+# « Deux fichiers version.json distincts »).
+_GABARIT_URL_VERSION_JSON = "https://raw.githubusercontent.com/{depot}/HEAD/version.json"
+
 
 def verifier_version(depot_github: str, build_installe: int) -> dict[str, Any] | None:
     """Vérifie si une nouvelle version est disponible pour ``depot_github``.
# ── Zone modifiée : ligne 26 (4 ligne(s)) dans l'ancienne version → ligne 37 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -26,4 +37,25 @@ def verifier_version(depot_github: str, build_installe: int) -> dict[str, Any] |
     (pas de mise à jour, ou échec réseau/timeout — repli silencieux,
     voir CONCEPTION.md « Décisions actées »).
     """
-    raise NotImplementedError
+    url = _GABARIT_URL_VERSION_JSON.format(depot=depot_github)
+
+    try:
+        reponse = requests.get(url, timeout=TIMEOUT_RESEAU_SECONDES)
+        reponse.raise_for_status()
+        distant = reponse.json()
+    except (requests.RequestException, ValueError) as erreur:
+        _LOGGER.debug("Échec de vérification de version pour %s : %s", depot_github, erreur)
+        return None
+
+    try:
+        build_distant = distant["build"]
+    except (KeyError, TypeError) as erreur:
+        _LOGGER.debug("version.json invalide pour %s : %s", depot_github, erreur)
+        return None
+
+    # Comparaison entière stricte — jamais de comparaison de chaînes
+    # (voir CONCEPTION.md, piège « "9" > "10" » lexicographique).
+    if int(build_distant) > build_installe:
+        return distant
+
+    return None
