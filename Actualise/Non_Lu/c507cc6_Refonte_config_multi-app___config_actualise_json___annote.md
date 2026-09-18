c507cc6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c507cc6
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 10:54:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Refonte config multi-app : config_actualise.json + config_<app>.json + --config (issue #35)
    
    Remplace config.json unique par config_actualise.json (bloc Actualise
    partagé + zone_attente) et config_<nom_app>.json (un par application
    cible), pour préparer le passage d'une instance par app à une instance
    Actualise unique partagée.
    
    - config.py : charger_config(nom_app) fusionne les deux fichiers ;
      sauvegarder_config() remplacée par sauvegarder_config_actualise() et
      sauvegarder_config_app(nom_app).
    - actualise.py : --config <nom> obligatoire, propagé à
      appliquer_mises_a_jour_en_attente, lancer_application_cible,
      tache_verification_arriere_plan et _relancer_en_enfant.
    - Tests adaptés à la nouvelle signature et aux nouvelles fonctions de
      sauvegarde.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/actualise.py b/actualise.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9ee147b..56d99fb 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/actualise.py
# ── Version APRÈS ce commit.
+++ b/actualise.py
# ── Zone modifiée : ligne 49 (6 ligne(s)) dans l'ancienne version → ligne 49 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -49,6 +49,12 @@ def analyser_arguments(argv: list[str] | None = None) -> argparse.Namespace:
         action="store_true",
         help="Marqueur interne : instance relancée après bascule d'auto-mise-à-jour (voir CONCEPTION.md)",
     )
+    analyseur.add_argument(
+        "--config",
+        required=True,
+        type=str.lower,
+        help="Nom de l'application cible gérée par cette instance (ex. scrabble, rummikub)",
+    )
     return analyseur.parse_args(argv)
 
 
# ── Zone modifiée : ligne 100 (17 ligne(s)) dans l'ancienne version → ligne 106 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -100,17 +106,18 @@ def _chercher_zip_en_attente(zone_attente: Path, prefixe: str) -> tuple[Path, in
     return meilleur
 
 
-def _relancer_en_enfant() -> None:
+def _relancer_en_enfant(nom_app: str) -> None:
     """Relance une 2ème instance d'Actualise avec le marqueur ``--child``.
 
     Voir CONCEPTION.md, « Garde-fou anti-boucle infinie ». Gère aussi
     bien le cas d'un exécutable PyInstaller gelé (``sys.frozen``) que
-    l'exécution directe du script Python.
+    l'exécution directe du script Python. ``--config nom_app`` est
+    transmis à l'enfant pour qu'il gère la même application cible.
     """
     if getattr(sys, "frozen", False):
-        commande = [sys.executable, "--child"]
+        commande = [sys.executable, "--child", "--config", nom_app]
     else:
-        commande = [sys.executable, str(Path(__file__).resolve()), "--child"]
+        commande = [sys.executable, str(Path(__file__).resolve()), "--child", "--config", nom_app]
 
     subprocess.Popen(commande)
 
# ── Zone modifiée : ligne 200 (7 ligne(s)) dans l'ancienne version → ligne 207 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -200,7 +207,7 @@ def _nettoyer_ancien_executable() -> None:
         shutil.rmtree(dossier_internal_ancien, ignore_errors=True)
 
 
-def appliquer_mises_a_jour_en_attente(est_enfant: bool) -> None:
+def appliquer_mises_a_jour_en_attente(est_enfant: bool, nom_app: str) -> None:
     """Applique, au lancement, les mises à jour mises en attente au
     cycle précédent (étape 4 de la séquence de démarrage).
 
# ── Zone modifiée : ligne 211 (7 ligne(s)) dans l'ancienne version → ligne 218 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -211,7 +218,7 @@ def appliquer_mises_a_jour_en_attente(est_enfant: bool) -> None:
     if est_enfant:
         return
 
-    configuration = config.charger_config()
+    configuration = config.charger_config(nom_app)
 
     try:
         zone_attente = Path(configuration["zone_attente"])
# ── Zone modifiée : ligne 304 (7 ligne(s)) dans l'ancienne version → ligne 311 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -304,7 +311,12 @@ def appliquer_mises_a_jour_en_attente(est_enfant: bool) -> None:
                 mise_a_jour.appliquer_manifeste(manifest, repertoire_installation)
 
             bloc_config["build_installe"] = build_zip
-            config.sauvegarder_config(configuration)
+            if prefixe == "actualise":
+                config.sauvegarder_config_actualise(
+                    configuration["actualise"], configuration["zone_attente"]
+                )
+            else:
+                config.sauvegarder_config_app(nom_app, configuration["application_cible"])
 
             chemin_zip.unlink()
 
# ── Zone modifiée : ligne 316 (28 ligne(s)) dans l'ancienne version → ligne 328 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -316,28 +328,30 @@ def appliquer_mises_a_jour_en_attente(est_enfant: bool) -> None:
                 # démarrer la tâche de fond — l'enfant reprend la suite de
                 # la séquence de démarrage à sa place. Voir CONCEPTION.md,
                 # « Garde-fou anti-boucle infinie ».
-                _relancer_en_enfant()
+                _relancer_en_enfant(nom_app)
                 raise SystemExit(0)
     except KeyError:
-        # Champ obligatoire manquant dans config.json : cohérent avec le
-        # choix déjà acté pour charger_config (config invalide = erreur
-        # bloquante, pas de repli silencieux) — la KeyError continue de
-        # remonter, mais avec un log explicite pour éviter une exception
-        # cryptique sans contexte.
+        # Champ obligatoire manquant dans config_actualise.json ou
+        # config_<nom_app>.json : cohérent avec le choix déjà acté pour
+        # charger_config (config invalide = erreur bloquante, pas de
+        # repli silencieux) — la KeyError continue de remonter, mais
+        # avec un log explicite pour éviter une exception cryptique sans
+        # contexte.
         _LOGGER.error(
-            "config.json incomplet : champ obligatoire manquant lors de "
-            "l'application des mises à jour en attente."
+            "config_actualise.json/config_%s.json incomplet : champ obligatoire "
+            "manquant lors de l'application des mises à jour en attente.",
+            nom_app,
         )
         raise
 
 
-def lancer_application_cible() -> None:
+def lancer_application_cible(nom_app: str) -> None:
     """Lance immédiatement l'application cible dans sa version
     actuellement installée, sans attendre aucune vérification réseau.
 
     Voir CONCEPTION.md, « Séquence de démarrage », étape 2.
     """
-    configuration = config.charger_config()
+    configuration = config.charger_config(nom_app)
     bloc_config = configuration["application_cible"]
     chemin_executable = Path(bloc_config["repertoire_installation"]) / bloc_config["executable"]
 
# ── Zone modifiée : ligne 359 (7 ligne(s)) dans l'ancienne version → ligne 373 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -359,7 +373,7 @@ def _url_asset_release(depot_github: str, build: int, prefixe: str) -> str:
     return _GABARIT_URL_RELEASE.format(depot=depot_github, build=build, fichier=f"{prefixe}-v{build}.zip")
 
 
-def tache_verification_arriere_plan() -> None:
+def tache_verification_arriere_plan(nom_app: str) -> None:
     """Tâche de fond : vérifie et télécharge les mises à jour
     (Actualise et application cible), notifie via ntfy si une mise à
     jour est prête.
# ── Zone modifiée : ligne 372 (7 ligne(s)) dans l'ancienne version → ligne 386 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -372,7 +386,7 @@ def tache_verification_arriere_plan() -> None:
     try:
         _LOGGER.info("Démarrage de la vérification des mises à jour en arrière-plan.")
 
-        configuration = config.charger_config()
+        configuration = config.charger_config(nom_app)
         zone_attente = Path(configuration["zone_attente"])
         zone_attente.mkdir(parents=True, exist_ok=True)
 
# ── Zone modifiée : ligne 418 (8 ligne(s)) dans l'ancienne version → ligne 432 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -418,8 +432,9 @@ def configurer_logging() -> None:
     fenêtre console, écrire sur stdout/stderr peut échouer silencieusement
     sous Windows, d'où l'écriture vers un fichier plutôt que la console.
     Le dossier de ``config.chemin_config_portable()`` peut ne pas encore
-    exister au tout premier lancement (avant même que ``config.json`` n'y
-    soit écrit) : il est créé si nécessaire. ``force=True`` garantit que
+    exister au tout premier lancement (avant même que les fichiers de
+    configuration n'y soient écrits) : il est créé si nécessaire.
+    ``force=True`` garantit que
     cette configuration s'applique même si le logging a déjà été
     configuré (ex. appels répétés dans les tests).
     """
# ── Zone modifiée : ligne 443 (8 ligne(s)) dans l'ancienne version → ligne 458 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -443,8 +458,9 @@ def main(argv: list[str] | None = None) -> int:
     _nettoyer_ancien_executable()
 
     # Bloc englobant : sans lui, une exception non anticipée par les
-    # except existants (ex. config.json absent dès le tout premier
-    # lancement) remonte jusqu'à --noconsole sans jamais être loguée —
+    # except existants (ex. config_actualise.json ou config_<app>.json
+    # absent dès le tout premier lancement) remonte jusqu'à --noconsole
+    # sans jamais être loguée —
     # seule une popup Windows technique s'affiche, sans rien
     # d'exploitable conservé pour diagnostiquer à distance. On logue ici
     # la stack trace complète puis on laisse l'exception se propager
# ── Zone modifiée : ligne 454 (21 ligne(s)) dans l'ancienne version → ligne 470 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -454,21 +470,22 @@ def main(argv: list[str] | None = None) -> int:
     # ``BaseException`` et n'est donc jamais intercepté ici.
     try:
         arguments = analyser_arguments(argv)
+        nom_app = arguments.config
 
         # Étape 4 : bascule des mises à jour déjà téléchargées et validées
         # au cycle précédent (sautée pour Actualise si --child est présent).
         # Si une bascule d'Actualise lui-même vient d'avoir lieu, cette
         # fonction termine le process (SystemExit) avant de revenir ici.
-        appliquer_mises_a_jour_en_attente(est_enfant=arguments.child)
+        appliquer_mises_a_jour_en_attente(est_enfant=arguments.child, nom_app=nom_app)
 
         # Étape 2 : lancement immédiat de l'application cible, sans attendre
         # le réseau.
-        lancer_application_cible()
+        lancer_application_cible(nom_app)
 
         # Étape 3 : vérification et téléchargement en arrière-plan, sans
         # bloquer l'utilisateur.
         thread_verification = threading.Thread(
-            target=tache_verification_arriere_plan, daemon=True
+            target=tache_verification_arriere_plan, args=(nom_app,), daemon=True
         )
         thread_verification.start()
 
# (diff du fichier suivant)
diff --git a/config.py b/config.py
# (index — ignorable)
index c714cc7..c2c9345 100644
# (avant — fichier suivant)
--- a/config.py
# (après — fichier suivant)
+++ b/config.py
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 1 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +1,5 @@
-"""Lecture/écriture de config.json et résolution du chemin de
-configuration portable (Windows/Linux).
+"""Lecture/écriture de config_actualise.json / config_<app>.json et
+résolution du chemin de configuration portable (Windows/Linux).
 
 Voir CONCEPTION.md, sections « Contenu de config.json » et
 « Configuration portable ».
# ── Zone modifiée : ligne 12 (7 ligne(s)) dans l'ancienne version → ligne 12 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -12,7 +12,8 @@ import tempfile
 from pathlib import Path
 from typing import Any
 
-_NOM_FICHIER_CONFIG = "config.json"
+_NOM_FICHIER_ACTUALISE = "config_actualise.json"
+_GABARIT_NOM_FICHIER_APP = "config_{nom}.json"
 
 
 def chemin_config_portable() -> Path:
# ── Zone modifiée : ligne 40 (7 ligne(s)) dans l'ancienne version → ligne 41 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -40,7 +41,8 @@ def chemin_config_portable() -> Path:
     CONCEPTION.md, « Configuration portable »).
 
     Ne crée pas le dossier — résolution de chemin uniquement (voir
-    ``sauvegarder_config`` pour la création).
+    ``sauvegarder_config_actualise``/``sauvegarder_config_app`` pour la
+    création).
     """
     if sys.platform == "win32":
         if getattr(sys, "frozen", False):
# ── Zone modifiée : ligne 56 (53 ligne(s)) dans l'ancienne version → ligne 58 (97 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -56,53 +58,97 @@ def chemin_config_portable() -> Path:
     return Path.home() / ".config" / "actualise"
 
 
-def charger_config() -> dict[str, Any]:
-    """Charge et retourne le contenu de config.json.
+def _nom_fichier_app(nom_app: str) -> str:
+    return _GABARIT_NOM_FICHIER_APP.format(nom=nom_app)
 
-    Voir CONCEPTION.md, section « Contenu de config.json », pour le
-    format attendu (blocs ``actualise`` / ``application_cible``,
-    ``zone_attente``, ``topic_ntfy``).
 
-    L'absence de configuration valide est bloquante pour Actualise (à
-    la différence de ``verifier_version``, pas de repli silencieux
-    ici) : les exceptions standard ``FileNotFoundError`` (fichier
-    absent) et ``json.JSONDecodeError`` (JSON malformé) sont laissées
-    se propager telles quelles à l'appelant, plutôt que d'introduire
-    une exception dédiée.
-    """
-    chemin_fichier = chemin_config_portable() / _NOM_FICHIER_CONFIG
+def _charger_json(chemin_fichier: Path) -> dict[str, Any]:
     with open(chemin_fichier, encoding="utf-8") as f:
         return json.load(f)
 
 
-def sauvegarder_config(config: dict[str, Any]) -> None:
-    """Écrit le contenu de ``config`` dans config.json.
-
-    Voir CONCEPTION.md, section « Contenu de config.json ».
+def _ecrire_json_atomique(chemin_fichier: Path, contenu: dict[str, Any]) -> None:
+    """Écrit ``contenu`` en JSON dans ``chemin_fichier``, atomiquement.
 
     Crée le dossier de configuration si nécessaire. Écriture atomique :
     le contenu est d'abord écrit dans un fichier temporaire du même
     dossier, puis basculé via ``os.replace`` — un fichier temporaire
     partiellement écrit (interruption en cours de route) ne peut donc
-    jamais remplacer un ``config.json`` déjà valide.
+    jamais remplacer un fichier de configuration déjà valide.
     """
-    dossier_config = chemin_config_portable()
+    dossier_config = chemin_fichier.parent
     dossier_config.mkdir(parents=True, exist_ok=True)
-    chemin_fichier = dossier_config / _NOM_FICHIER_CONFIG
 
     fichier_temp = tempfile.NamedTemporaryFile(
         mode="w",
         encoding="utf-8",
         dir=dossier_config,
-        prefix=f".{_NOM_FICHIER_CONFIG}.",
+        prefix=f".{chemin_fichier.name}.",
         suffix=".tmp",
         delete=False,
     )
     chemin_temp = Path(fichier_temp.name)
     try:
         with fichier_temp:
-            json.dump(config, fichier_temp, indent=2, ensure_ascii=False)
+            json.dump(contenu, fichier_temp, indent=2, ensure_ascii=False)
         os.replace(chemin_temp, chemin_fichier)
     except BaseException:
         chemin_temp.unlink(missing_ok=True)
         raise
+
+
+def charger_config(nom_app: str) -> dict[str, Any]:
+    """Charge et fusionne config_actualise.json et config_<nom_app>.json.
+
+    Voir CONCEPTION.md, section « Contenu de config.json », pour le
+    format attendu. Retourne un dict compatible avec la structure
+    utilisée par ``actualise.py`` :
+
+    - ``actualise`` : contenu de config_actualise.json sans zone_attente
+    - ``application_cible`` : contenu entier de config_<nom_app>.json
+    - ``zone_attente`` : depuis config_actualise.json
+    - ``topic_ntfy`` : copié depuis ``application_cible``, pour
+      compatibilité avec l'appelant actuel
+
+    L'absence de configuration valide est bloquante pour Actualise (à
+    la différence de ``verifier_version``, pas de repli silencieux
+    ici) : les exceptions standard ``FileNotFoundError`` (fichier
+    absent) et ``json.JSONDecodeError`` (JSON malformé) sont laissées
+    se propager telles quelles à l'appelant, plutôt que d'introduire
+    une exception dédiée.
+    """
+    dossier_config = chemin_config_portable()
+
+    config_actualise = _charger_json(dossier_config / _NOM_FICHIER_ACTUALISE)
+    config_app = _charger_json(dossier_config / _nom_fichier_app(nom_app))
+
+    zone_attente = config_actualise["zone_attente"]
+    bloc_actualise = {cle: valeur for cle, valeur in config_actualise.items() if cle != "zone_attente"}
+
+    return {
+        "actualise": bloc_actualise,
+        "application_cible": config_app,
+        "zone_attente": zone_attente,
+        "topic_ntfy": config_app["topic_ntfy"],
+    }
+
+
+def sauvegarder_config_actualise(bloc_actualise: dict[str, Any], zone_attente: str) -> None:
+    """Sauvegarde config_actualise.json (build_installe Actualise,
+    depot_github, zone_attente).
+
+    Voir CONCEPTION.md, section « Contenu de config.json ».
+    """
+    contenu = {**bloc_actualise, "zone_attente": zone_attente}
+    chemin_fichier = chemin_config_portable() / _NOM_FICHIER_ACTUALISE
+    _ecrire_json_atomique(chemin_fichier, contenu)
+
+
+def sauvegarder_config_app(nom_app: str, bloc_app: dict[str, Any]) -> None:
+    """Sauvegarde config_<nom_app>.json (tous les champs
+    application_cible).
+
+    Voir CONCEPTION.md, section « Contenu de config.json ».
+    """
+    chemin_fichier = chemin_config_portable() / _nom_fichier_app(nom_app)
+    _ecrire_json_atomique(chemin_fichier, bloc_app)
# (diff du fichier suivant)
diff --git a/tests/test_actualise.py b/tests/test_actualise.py
# (index — ignorable)
index b696198..8df0cb4 100644
# (avant — fichier suivant)
--- a/tests/test_actualise.py
# (après — fichier suivant)
+++ b/tests/test_actualise.py
# ── Zone modifiée : ligne 35 (7 ligne(s)) dans l'ancienne version → ligne 35 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -35,7 +35,7 @@ class TestAppliquerMisesAJourEnAttenteEnfant(unittest.TestCase):
     @patch("actualise.mise_a_jour")
     @patch("actualise.config")
     def test_est_enfant_ne_fait_rien(self, mock_config, mock_mise_a_jour):
-        appliquer_mises_a_jour_en_attente(est_enfant=True)
+        appliquer_mises_a_jour_en_attente(est_enfant=True, nom_app="scrabble")
 
         mock_config.charger_config.assert_not_called()
         mock_mise_a_jour.extraire_zip.assert_not_called()
# ── Zone modifiée : ligne 79 (7 ligne(s)) dans l'ancienne version → ligne 79 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -79,7 +79,7 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
         _creer_zip_avec_manifest(chemin_zip, build=48)
 
         with patch("actualise.mise_a_jour") as mock_mise_a_jour:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_called_once_with(
                 chemin_zip, self.repertoire_cible
# ── Zone modifiée : ligne 90 (21 ligne(s)) dans l'ancienne version → ligne 90 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,21 +90,25 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
 
         self.assertFalse(chemin_zip.exists())
         self.assertEqual(self.configuration["application_cible"]["build_installe"], 48)
-        self.mock_config.sauvegarder_config.assert_called_once_with(self.configuration)
+        self.mock_config.sauvegarder_config_app.assert_called_once_with(
+            "scrabble", self.configuration["application_cible"]
+        )
+        self.mock_config.sauvegarder_config_actualise.assert_not_called()
 
     def test_zip_obsolete_supprime_sans_bascule(self):
         chemin_zip = self.zone_attente / "scrabble_40.zip"
         _creer_zip_avec_manifest(chemin_zip, build=40)
 
         with patch("actualise.mise_a_jour") as mock_mise_a_jour:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_not_called()
             mock_mise_a_jour.appliquer_manifeste.assert_not_called()
 
         self.assertFalse(chemin_zip.exists())
         self.assertEqual(self.configuration["application_cible"]["build_installe"], 47)
-        self.mock_config.sauvegarder_config.assert_not_called()
+        self.mock_config.sauvegarder_config_actualise.assert_not_called()
+        self.mock_config.sauvegarder_config_app.assert_not_called()
 
     def test_zip_actualise_valide_relance_enfant_et_termine(self):
         chemin_zip = self.zone_attente / "actualise_11.zip"
# ── Zone modifiée : ligne 114 (7 ligne(s)) dans l'ancienne version → ligne 118 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -114,7 +118,7 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
             "actualise._relancer_en_enfant"
         ) as mock_relancer:
             with self.assertRaises(SystemExit):
-                appliquer_mises_a_jour_en_attente(est_enfant=False)
+                appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             # L'extraction se fait dans un dossier temporaire distinct
             # (sous repertoire_installation), jamais directement dans
# ── Zone modifiée : ligne 128 (7 ligne(s)) dans l'ancienne version → ligne 132 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -128,7 +132,7 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
             mock_mise_a_jour.appliquer_manifeste.assert_called_once_with(
                 {"build": 11, "supprimer": []}, self.dossier_actualise
             )
-            mock_relancer.assert_called_once()
+            mock_relancer.assert_called_once_with("scrabble")
 
         self.assertFalse(chemin_zip.exists())
         self.assertEqual(self.configuration["actualise"]["build_installe"], 11)
# ── Zone modifiée : ligne 143 (9 ligne(s)) dans l'ancienne version → ligne 147 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -143,9 +147,9 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
 
         with patch("actualise._relancer_en_enfant") as mock_relancer:
             with self.assertRaises(SystemExit):
-                appliquer_mises_a_jour_en_attente(est_enfant=False)
+                appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
-            mock_relancer.assert_called_once()
+            mock_relancer.assert_called_once_with("scrabble")
 
         fichier_bascule = self.dossier_actualise / "fichier.txt"
         self.assertTrue(fichier_bascule.exists())
# ── Zone modifiée : ligne 170 (13 ligne(s)) dans l'ancienne version → ligne 174 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -170,13 +174,14 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
         ), patch("actualise._relancer_en_enfant") as mock_relancer, self.assertLogs(
             "actualise", level="ERROR"
         ) as journal:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_relancer.assert_not_called()
 
         self.assertTrue(chemin_zip.exists())
         self.assertEqual(self.configuration["actualise"]["build_installe"], 10)
-        self.mock_config.sauvegarder_config.assert_not_called()
+        self.mock_config.sauvegarder_config_actualise.assert_not_called()
+        self.mock_config.sauvegarder_config_app.assert_not_called()
         self.assertTrue(
             any("renommage" in message.lower() for message in journal.output)
         )
# ── Zone modifiée : ligne 191 (7 ligne(s)) dans l'ancienne version → ligne 196 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -191,7 +196,7 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
         with patch("actualise.mise_a_jour") as mock_mise_a_jour, patch(
             "actualise._basculer_par_renommage"
         ) as mock_basculer:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_called_once_with(
                 chemin_zip, self.repertoire_cible
# ── Zone modifiée : ligne 205 (12 ligne(s)) dans l'ancienne version → ligne 210 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -205,12 +210,13 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
 
     def test_aucun_zip_ne_fait_rien(self):
         with patch("actualise.mise_a_jour") as mock_mise_a_jour:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_not_called()
             mock_mise_a_jour.appliquer_manifeste.assert_not_called()
 
-        self.mock_config.sauvegarder_config.assert_not_called()
+        self.mock_config.sauvegarder_config_actualise.assert_not_called()
+        self.mock_config.sauvegarder_config_app.assert_not_called()
 
     def test_plusieurs_zips_meme_prefixe_le_plus_eleve_applique_lautre_supprime(self):
         chemin_zip_bas = self.zone_attente / "scrabble_48.zip"
# ── Zone modifiée : ligne 219 (7 ligne(s)) dans l'ancienne version → ligne 225 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -219,7 +225,7 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
         _creer_zip_avec_manifest(chemin_zip_haut, build=49)
 
         with patch("actualise.mise_a_jour") as mock_mise_a_jour:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_called_once_with(
                 chemin_zip_haut, self.repertoire_cible
# ── Zone modifiée : ligne 235 (39 ligne(s)) dans l'ancienne version → ligne 241 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -235,39 +241,42 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
             archive.writestr("fichier.txt", "contenu")
 
         with patch("actualise.mise_a_jour") as mock_mise_a_jour:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_not_called()
             mock_mise_a_jour.appliquer_manifeste.assert_not_called()
 
         self.assertTrue(chemin_zip.exists())
         self.assertEqual(self.configuration["application_cible"]["build_installe"], 47)
-        self.mock_config.sauvegarder_config.assert_not_called()
+        self.mock_config.sauvegarder_config_actualise.assert_not_called()
+        self.mock_config.sauvegarder_config_app.assert_not_called()
 
     def test_zip_corrompu_zip_conserve_aucune_bascule(self):
         chemin_zip = self.zone_attente / "scrabble_48.zip"
         chemin_zip.write_text("ceci n'est pas un zip")
 
         with patch("actualise.mise_a_jour") as mock_mise_a_jour:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_not_called()
             mock_mise_a_jour.appliquer_manifeste.assert_not_called()
 
         self.assertTrue(chemin_zip.exists())
         self.assertEqual(self.configuration["application_cible"]["build_installe"], 47)
-        self.mock_config.sauvegarder_config.assert_not_called()
+        self.mock_config.sauvegarder_config_actualise.assert_not_called()
+        self.mock_config.sauvegarder_config_app.assert_not_called()
 
     def test_zone_attente_inexistante_aucune_exception(self):
         self.zone_attente.rmdir()
 
         with patch("actualise.mise_a_jour") as mock_mise_a_jour:
-            appliquer_mises_a_jour_en_attente(est_enfant=False)
+            appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
             mock_mise_a_jour.extraire_zip.assert_not_called()
             mock_mise_a_jour.appliquer_manifeste.assert_not_called()
 
-        self.mock_config.sauvegarder_config.assert_not_called()
+        self.mock_config.sauvegarder_config_actualise.assert_not_called()
+        self.mock_config.sauvegarder_config_app.assert_not_called()
 
     def test_config_incomplete_keyerror_levee_avec_log_derreur(self):
         del self.configuration["application_cible"]
# ── Zone modifiée : ligne 276 (9 ligne(s)) dans l'ancienne version → ligne 285 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -276,9 +285,9 @@ class TestAppliquerMisesAJourEnAttente(unittest.TestCase):
             "actualise", level="ERROR"
         ) as journal:
             with self.assertRaises(KeyError):
-                appliquer_mises_a_jour_en_attente(est_enfant=False)
+                appliquer_mises_a_jour_en_attente(est_enfant=False, nom_app="scrabble")
 
-        self.assertTrue(any("config.json" in message for message in journal.output))
+        self.assertTrue(any("config_actualise.json" in message for message in journal.output))
 
 
 class TestConfigurerLogging(unittest.TestCase):
# ── Zone modifiée : ligne 335 (8 ligne(s)) dans l'ancienne version → ligne 344 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -335,8 +344,9 @@ class TestLancerApplicationCible(unittest.TestCase):
         mock_processus = MagicMock()
         mock_popen.return_value = mock_processus
 
-        lancer_application_cible()
+        lancer_application_cible("scrabble")
 
+        mock_config.charger_config.assert_called_once_with("scrabble")
         mock_popen.assert_called_once_with([str(Path("/opt/scrabble") / "Scrabble.exe")])
         mock_processus.wait.assert_not_called()
 
# ── Zone modifiée : ligne 383 (7 ligne(s)) dans l'ancienne version → ligne 393 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -383,7 +393,7 @@ class TestTacheVerificationArrierePlan(unittest.TestCase):
                 chemin_temp_scrabble,
             ]
 
-            tache_verification_arriere_plan()
+            tache_verification_arriere_plan("scrabble")
 
             self.assertEqual(mock_mise_a_jour.telecharger_zip.call_count, 2)
             mock_notifications.notifier_ntfy.assert_has_calls(
# ── Zone modifiée : ligne 408 (7 ligne(s)) dans l'ancienne version → ligne 418 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -408,7 +418,7 @@ class TestTacheVerificationArrierePlan(unittest.TestCase):
         ) as mock_mise_a_jour, patch("actualise.notifications") as mock_notifications:
             mock_version_check.verifier_version.return_value = None
 
-            tache_verification_arriere_plan()
+            tache_verification_arriere_plan("scrabble")
 
             mock_mise_a_jour.telecharger_zip.assert_not_called()
             mock_notifications.notifier_ntfy.assert_not_called()
# ── Zone modifiée : ligne 419 (7 ligne(s)) dans l'ancienne version → ligne 429 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -419,7 +429,7 @@ class TestTacheVerificationArrierePlan(unittest.TestCase):
         with patch("actualise.config") as mock_config:
             mock_config.charger_config.side_effect = RuntimeError("boom")
 
-            tache_verification_arriere_plan()
+            tache_verification_arriere_plan("scrabble")
 
 
 class TestMain(unittest.TestCase):
# ── Zone modifiée : ligne 444 (7 ligne(s)) dans l'ancienne version → ligne 454 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -444,7 +454,7 @@ class TestMain(unittest.TestCase):
             "actualise.lancer_application_cible", side_effect=RuntimeError("boum fatal")
         ), self.assertLogs("actualise", level="ERROR") as journal:
             with self.assertRaises(RuntimeError):
-                main([])
+                main(["--config", "scrabble"])
 
         self.assertTrue(any("erreur fatale" in message for message in journal.output))
 
# ── Zone modifiée : ligne 454 (7 ligne(s)) dans l'ancienne version → ligne 464 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -454,7 +464,7 @@ class TestMain(unittest.TestCase):
         ), patch("actualise.lancer_application_cible") as mock_lancer:
             with self.assertNoLogs("actualise", level="ERROR"):
                 with self.assertRaises(SystemExit):
-                    main([])
+                    main(["--config", "scrabble"])
 
             mock_lancer.assert_not_called()
 
# (diff du fichier suivant)
diff --git a/tests/test_config.py b/tests/test_config.py
# (index — ignorable)
index c1a9ef7..3a1d518 100644
# (avant — fichier suivant)
--- a/tests/test_config.py
# (après — fichier suivant)
+++ b/tests/test_config.py
# ── Zone modifiée : ligne 13 (7 ligne(s)) dans l'ancienne version → ligne 13 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -13,7 +13,12 @@ import unittest
 from pathlib import Path
 from unittest.mock import patch
 
-from config import chemin_config_portable, charger_config, sauvegarder_config
+from config import (
+    chemin_config_portable,
+    charger_config,
+    sauvegarder_config_actualise,
+    sauvegarder_config_app,
+)
 
 
 class TestCheminConfigPortable(unittest.TestCase):
# ── Zone modifiée : ligne 79 (26 ligne(s)) dans l'ancienne version → ligne 84 (125 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -79,26 +84,125 @@ class TestChargerConfig(unittest.TestCase):
         self.mock_chemin = patcher.start()
         self.addCleanup(patcher.stop)
 
-    def test_chargement_valide_retourne_le_dict(self):
-        config_attendue = {"actualise": {"build_installe": 12}, "topic_ntfy": "actualise-scrabble"}
-        (self.chemin_dossier / "config.json").write_text(
-            json.dumps(config_attendue), encoding="utf-8"
+    def _ecrire_config_actualise(self, contenu):
+        (self.chemin_dossier / "config_actualise.json").write_text(
+            json.dumps(contenu), encoding="utf-8"
         )
 
-        self.assertEqual(charger_config(), config_attendue)
+    def _ecrire_config_app(self, nom_app, contenu):
+        (self.chemin_dossier / f"config_{nom_app}.json").write_text(
+            json.dumps(contenu), encoding="utf-8"
+        )
+
+    def test_chargement_valide_fusionne_les_deux_fichiers(self):
+        self._ecrire_config_actualise(
+            {
+                "build_installe": 6,
+                "depot_github": "AlainDelree/Actualise",
+                "zone_attente": "C:\\Actualise\\attente\\",
+            }
+        )
+        self._ecrire_config_app(
+            "scrabble",
+            {
+                "nom": "Scrabble",
+                "depot_github": "AlainDelree/Scrabble",
+                "build_installe": 5,
+                "repertoire_installation": "C:\\Scrabble\\",
+                "executable": "Scrabble.exe",
+                "icone": "C:\\Scrabble\\Scrabble.ico",
+                "topic_ntfy": "actualise-scrabble",
+            },
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
+    def test_fichier_actualise_absent_leve_une_exception(self):
+        self._ecrire_config_app("scrabble", {"topic_ntfy": "actualise-scrabble"})
+
+        with self.assertRaises(FileNotFoundError):
+            charger_config("scrabble")
+
+    def test_fichier_app_absent_leve_une_exception(self):
+        self._ecrire_config_actualise(
+            {
+                "build_installe": 6,
+                "depot_github": "AlainDelree/Actualise",
+                "zone_attente": "C:\\Actualise\\attente\\",
+            }
+        )
 
-    def test_fichier_absent_leve_une_exception(self):
         with self.assertRaises(FileNotFoundError):
-            charger_config()
+            charger_config("scrabble")
 
     def test_json_invalide_leve_une_exception(self):
-        (self.chemin_dossier / "config.json").write_text("{ceci n'est pas du json", encoding="utf-8")
+        (self.chemin_dossier / "config_actualise.json").write_text(
+            "{ceci n'est pas du json", encoding="utf-8"
+        )
 
         with self.assertRaises(json.JSONDecodeError):
-            charger_config()
+            charger_config("scrabble")
+
+
+class TestSauvegarderConfigActualise(unittest.TestCase):
+    def setUp(self):
+        self.dossier_temp = tempfile.TemporaryDirectory()
+        self.addCleanup(self.dossier_temp.cleanup)
+        self.chemin_dossier = Path(self.dossier_temp.name) / "sous_dossier" / "actualise"
+        patcher = patch("config.chemin_config_portable", return_value=self.chemin_dossier)
+        self.mock_chemin = patcher.start()
+        self.addCleanup(patcher.stop)
+
+    def test_ecrit_le_bloc_actualise_et_la_zone_attente(self):
+        sauvegarder_config_actualise(
+            {"build_installe": 12, "depot_github": "AlainDelree/Actualise"},
+            "/tmp/attente",
+        )
+
+        chemin_fichier = self.chemin_dossier / "config_actualise.json"
+        self.assertEqual(
+            json.loads(chemin_fichier.read_text(encoding="utf-8")),
+            {
+                "build_installe": 12,
+                "depot_github": "AlainDelree/Actualise",
+                "zone_attente": "/tmp/attente",
+            },
+        )
 
+    def test_cree_le_dossier_parent_si_absent(self):
+        self.assertFalse(self.chemin_dossier.exists())
 
-class TestSauvegarderConfig(unittest.TestCase):
+        sauvegarder_config_actualise({"build_installe": 1}, "/tmp/attente")
+
+        self.assertTrue((self.chemin_dossier / "config_actualise.json").is_file())
+
+    def test_aucun_fichier_temporaire_residuel(self):
+        sauvegarder_config_actualise({"build_installe": 1}, "/tmp/attente")
+
+        fichiers = list(self.chemin_dossier.iterdir())
+        self.assertEqual(fichiers, [self.chemin_dossier / "config_actualise.json"])
+
+
+class TestSauvegarderConfigApp(unittest.TestCase):
     def setUp(self):
         self.dossier_temp = tempfile.TemporaryDirectory()
         self.addCleanup(self.dossier_temp.cleanup)
# ── Zone modifiée : ligne 107 (25 ligne(s)) dans l'ancienne version → ligne 211 (67 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -107,25 +211,67 @@ class TestSauvegarderConfig(unittest.TestCase):
         self.mock_chemin = patcher.start()
         self.addCleanup(patcher.stop)
 
-    def test_aller_retour_avec_charger_config(self):
-        config = {"actualise": {"build_installe": 12}, "topic_ntfy": "actualise-scrabble"}
+    def test_ecrit_le_fichier_du_bon_nom(self):
+        bloc_app = {
+            "nom": "Scrabble",
+            "depot_github": "AlainDelree/Scrabble",
+            "build_installe": 5,
+            "repertoire_installation": "C:\\Scrabble\\",
+            "executable": "Scrabble.exe",
+            "topic_ntfy": "actualise-scrabble",
+        }
 
-        sauvegarder_config(config)
+        sauvegarder_config_app("scrabble", bloc_app)
 
-        self.assertEqual(charger_config(), config)
+        chemin_fichier = self.chemin_dossier / "config_scrabble.json"
+        self.assertEqual(json.loads(chemin_fichier.read_text(encoding="utf-8")), bloc_app)
 
     def test_cree_le_dossier_parent_si_absent(self):
         self.assertFalse(self.chemin_dossier.exists())
 
-        sauvegarder_config({"cle": "valeur"})
+        sauvegarder_config_app("rummikub", {"cle": "valeur"})
 
-        self.assertTrue((self.chemin_dossier / "config.json").is_file())
+        self.assertTrue((self.chemin_dossier / "config_rummikub.json").is_file())
 
     def test_aucun_fichier_temporaire_residuel(self):
-        sauvegarder_config({"cle": "valeur"})
+        sauvegarder_config_app("rummikub", {"cle": "valeur"})
 
         fichiers = list(self.chemin_dossier.iterdir())
-        self.assertEqual(fichiers, [self.chemin_dossier / "config.json"])
+        self.assertEqual(fichiers, [self.chemin_dossier / "config_rummikub.json"])
+
+
+class TestChargerConfigSauvegarderConfigAllerRetour(unittest.TestCase):
+    def setUp(self):
+        self.dossier_temp = tempfile.TemporaryDirectory()
+        self.addCleanup(self.dossier_temp.cleanup)
+        self.chemin_dossier = Path(self.dossier_temp.name)
+        patcher = patch("config.chemin_config_portable", return_value=self.chemin_dossier)
+        self.mock_chemin = patcher.start()
+        self.addCleanup(patcher.stop)
+
+    def test_aller_retour(self):
+        sauvegarder_config_actualise(
+            {"build_installe": 6, "depot_github": "AlainDelree/Actualise"},
+            "/tmp/attente",
+        )
+        sauvegarder_config_app(
+            "scrabble",
+            {
+                "nom": "Scrabble",
+                "depot_github": "AlainDelree/Scrabble",
+                "build_installe": 5,
+                "repertoire_installation": "C:\\Scrabble\\",
+                "executable": "Scrabble.exe",
+                "topic_ntfy": "actualise-scrabble",
+            },
+        )
+
+        configuration = charger_config("scrabble")
+
+        self.assertEqual(configuration["actualise"]["build_installe"], 6)
+        self.assertEqual(configuration["application_cible"]["nom"], "Scrabble")
+        self.assertEqual(configuration["zone_attente"], "/tmp/attente")
+        self.assertEqual(configuration["topic_ntfy"], "actualise-scrabble")
 
 
 if __name__ == "__main__":
