c9f760e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c9f760e
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 23:24:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    implémentation de notifications.py (issue #13, suite #9)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/notifications.py b/notifications.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e1f3088..86e200f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/notifications.py
# ── Version APRÈS ce commit.
+++ b/notifications.py
# ── Zone modifiée : ligne 5 (6 ligne(s)) dans l'ancienne version → ligne 5 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,6 +5,16 @@ Voir CONCEPTION.md, section « Contenu de config.json » (champ
 programme géré »).
 """
 
+import logging
+
+import requests
+
+from version_check import TIMEOUT_RESEAU_SECONDES
+
+_LOGGER = logging.getLogger(__name__)
+
+_GABARIT_URL_NTFY = "https://ntfy.sh/{topic}"
+
 
 def notifier_ntfy(topic: str, message: str) -> None:
     """Envoie ``message`` sur le topic ntfy ``topic``.
# ── Zone modifiée : ligne 12 (5 ligne(s)) dans l'ancienne version → ligne 22 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -12,5 +22,15 @@ def notifier_ntfy(topic: str, message: str) -> None:
     Utilisé notamment pour la notification informative envoyée quand une
     mise à jour a été téléchargée et validée en arrière-plan (voir
     CONCEPTION.md, « Séquence de démarrage » étape 3).
+
+    Repli silencieux en cas d'échec (timeout, connexion refusée, erreur
+    HTTP) : une notification ratée ne doit jamais interrompre le flux
+    normal d'Actualise (voir CONCEPTION.md, « Décisions actées »).
     """
-    raise NotImplementedError
+    url = _GABARIT_URL_NTFY.format(topic=topic)
+
+    try:
+        reponse = requests.post(url, data=message.encode("utf-8"), timeout=TIMEOUT_RESEAU_SECONDES)
+        reponse.raise_for_status()
+    except requests.RequestException as erreur:
+        _LOGGER.debug("Échec d'envoi de notification ntfy sur %s : %s", topic, erreur)
# (diff du fichier suivant)
diff --git a/tests/test_notifications.py b/tests/test_notifications.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..15993ed
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_notifications.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,46 @@
+"""Tests unitaires pour ``notifications.py``.
+
+Aucun appel réseau réel : les réponses HTTP sont simulées via
+``unittest.mock``. Voir CONCEPTION.md, « Décisions actées » (repli
+silencieux sur échec réseau).
+"""
+
+import unittest
+from unittest.mock import MagicMock, patch
+
+import requests
+
+from notifications import notifier_ntfy
+
+
+class TestNotifierNtfy(unittest.TestCase):
+    @patch("notifications.requests.post")
+    def test_envoi_reussi_appelle_post_avec_bonne_url_et_message(self, mock_post):
+        reponse = MagicMock()
+        reponse.raise_for_status.return_value = None
+        mock_post.return_value = reponse
+
+        notifier_ntfy("mon-topic", "un message")
+
+        mock_post.assert_called_once()
+        args, kwargs = mock_post.call_args
+        self.assertEqual(args[0], "https://ntfy.sh/mon-topic")
+        self.assertEqual(kwargs["data"], "un message".encode("utf-8"))
+
+    @patch("notifications.requests.post")
+    def test_timeout_reseau_ne_leve_pas_exception(self, mock_post):
+        mock_post.side_effect = requests.exceptions.Timeout
+
+        notifier_ntfy("mon-topic", "un message")
+
+    @patch("notifications.requests.post")
+    def test_erreur_http_ne_leve_pas_exception(self, mock_post):
+        reponse = MagicMock()
+        reponse.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
+        mock_post.return_value = reponse
+
+        notifier_ntfy("mon-topic", "un message")
+
+
+if __name__ == "__main__":
+    unittest.main()
