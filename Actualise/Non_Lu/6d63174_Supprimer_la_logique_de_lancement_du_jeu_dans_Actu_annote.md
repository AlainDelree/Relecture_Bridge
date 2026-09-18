6d63174

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6d63174
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 05:55:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Supprimer la logique de lancement du jeu dans Actualise (issue #42)
    
    Refonte architecturale : c'est désormais le jeu qui lance Actualise à
    son démarrage, plus l'inverse. Actualise ne lance donc plus jamais
    d'application cible.
    
    - Suppression de l'appel lancer_application_cible(nom_app) dans main()
    - Suppression de la fonction lancer_application_cible
    - _relancer_en_enfant : docstring clarifiée, nom_app ne sert plus qu'à
      reconstruire --config <nom> pour l'enfant (auto-mise-à-jour
      d'Actualise), plus jamais à lancer un jeu
    - tests/test_actualise.py : suppression de TestLancerApplicationCible et
      de l'import associé ; adaptation des deux tests de TestMain qui
      simulaient l'échec via lancer_application_cible
    - CONCEPTION.md : mise à jour des sections « Séquence de démarrage » et
      « Cycle de vie du processus Actualise » (renumérotation des étapes,
      suppression des références au lancement de l'application cible par
      Actualise)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index fce43fa..aed4b83 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 257 (13 ligne(s)) dans l'ancienne version → ligne 257 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -257,13 +257,14 @@ actées »).
 
 ## Séquence de démarrage — vérification non bloquante
 
-Principe central : **le lancement de l'application cible n'attend
-jamais le réseau.**
-
-1. Lancement d'Actualise.
-2. Actualise **lance immédiatement** l'application cible dans sa version
-   actuellement installée, sans attendre aucune vérification.
-3. En parallèle, dans une **tâche de fond** (thread ou process séparé),
+Principe central : **Actualise ne bloque jamais, et ne lance plus
+aucune application cible.** Refonte architecturale actée : c'est
+désormais l'application cible qui lance Actualise à son propre
+démarrage (et non l'inverse) ; Actualise se limite à l'auto-mise-à-jour
+et à la vérification/téléchargement en arrière-plan, puis se termine.
+
+1. L'application cible lance Actualise à son démarrage.
+2. En parallèle, dans une **tâche de fond** (thread ou process séparé),
    Actualise :
    - vérifie `version.json` d'Actualise et `version.json` de
      l'application cible (deux vérifications indépendantes, chacune
# ── Zone modifiée : ligne 283 (35 ligne(s)) dans l'ancienne version → ligne 284 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -283,35 +284,34 @@ jamais le réseau.**
    - si une nouvelle version a été téléchargée **et validée**, envoie une
      **notification ntfy informative** (mise à jour prête, effective au
      prochain lancement).
-**Cycle de vie du processus Actualise.** Le lancement de l'application
-cible (étape 2) se fait via un mécanisme **non bloquant** (ex. `Popen`
-sans `wait()`) : Actualise n'attend **jamais** la fermeture de
-l'application cible — leurs cycles de vie sont **indépendants** dès le
-lancement, que l'application cible tourne encore ou se soit déjà
-fermée n'a aucune incidence sur la suite. Une fois l'application cible
-lancée, Actualise attend uniquement la fin de sa propre **tâche de
-fond** (étape 3 ci-dessus), qui va jusqu'au bout de son cycle
-(vérification des deux `version.json`, téléchargement et validation
-SHA-256 si nécessaire, notification ntfy éventuelle). Dès que cette
-tâche de fond se termine, **Actualise se termine à son tour** — que
-l'application cible tourne encore ou non. Actualise n'est donc pas un
-processus permanent : il effectue son travail de vérification/
-téléchargement en arrière-plan puis se ferme, sans attendre une action
-de l'utilisateur ni la fermeture de l'application cible.
-
-4. Au **lancement suivant**, avant de relancer l'application cible,
-   Actualise applique les mises à jour mises en attente. Pour chaque
-   mise à jour en attente (Actualise ou application cible), la bascule
-   comprend désormais trois étapes, dans l'ordre :
+
+**Cycle de vie du processus Actualise.** Actualise ne lance plus
+l'application cible et n'a donc plus aucun lien avec son cycle de vie :
+c'est elle qui le lance, à son propre démarrage. Une fois démarré,
+Actualise attend uniquement la fin de sa propre **tâche de fond**
+(étape 2 ci-dessus), qui va jusqu'au bout de son cycle (vérification
+des deux `version.json`, téléchargement et validation SHA-256 si
+nécessaire, notification ntfy éventuelle). Dès que cette tâche de fond
+se termine, **Actualise se termine à son tour** — que l'application
+cible tourne encore ou se soit déjà fermée entre-temps n'a aucune
+incidence. Actualise n'est donc pas un processus permanent : c'est un
+aller-retour ponctuel déclenché à chaque démarrage de l'application
+cible, qui effectue son travail de vérification/téléchargement en
+arrière-plan puis se ferme, sans attendre une action de l'utilisateur.
+
+3. Au **lancement suivant** (prochain démarrage d'Actualise, déclenché
+   par un nouveau lancement de l'application cible), avant toute autre
+   chose, Actualise applique les mises à jour mises en attente. Pour
+   chaque mise à jour en attente (Actualise ou application cible), la
+   bascule comprend :
    1. **extraction du zip** téléchargé dans le dossier d'installation
       (écrase les fichiers existants de même nom, ajoute les nouveaux) ;
    2. **application du manifeste** : suppression des fichiers listés
-      dans `supprimer` (voir « Manifeste de mise à jour ») ;
-   3. **lancement de l'application** fraîchement mise à jour.
+      dans `supprimer` (voir « Manifeste de mise à jour »).
 
    Le détail selon qu'il s'agit d'Actualise lui-même ou de l'application
    cible :
-   - si une nouvelle version d'Actualise est en attente, ces trois
+   - si une nouvelle version d'Actualise est en attente, ces deux
      étapes sont suivies d'un relancement d'Actualise comme **2ème
      instance** de lui-même (la version fraîchement installée) avec le
      **marqueur explicite** parent → enfant décrit ci-dessous, avant de
# ── Zone modifiée : ligne 319 (8 ligne(s)) dans l'ancienne version → ligne 319 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -319,8 +319,9 @@ de l'utilisateur ni la fermeture de l'application cible.
      zip, suppressions ciblées), donc quasi instantanées — elles ne
      réintroduisent pas d'attente réseau perceptible ;
    - si une nouvelle version de l'application cible est en attente, ces
-     trois étapes sont appliquées avant le lancement (étape 2) de ce
-     lancement.
+     deux étapes suffisent : Actualise n'a plus rien à lancer ensuite,
+     l'application cible tourne déjà dans sa version fraîchement mise à
+     jour dès son prochain démarrage.
 
 **Choix écarté : liste de fichiers attendus post-extraction.** Une
 vérification de type « liste des fichiers attendus après extraction du
# ── Zone modifiée : ligne 348 (13 ligne(s)) dans l'ancienne version → ligne 349 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -348,13 +349,13 @@ comparaison directe avec le `build_installe` correspondant de
 `config.json` (voir « Contenu de `config.json` ») sans avoir à ouvrir
 le zip ni consulter un fichier séparé.
 
-Comportement au démarrage, **avant bascule** (étape 4 de la séquence
+Comportement au démarrage, **avant bascule** (étape 3 de la séquence
 ci-dessus) : pour chaque préfixe connu (`actualise`, nom de
 l'application cible), si un fichier `<préfixe>_<build>.zip` existe dans
 `zone_attente` :
 
 - si `build` > `build_installe` correspondant → mise à jour valide,
-  bascule appliquée (extraction + manifeste, voir étape 4 ci-dessus),
+  bascule appliquée (extraction + manifeste, voir étape 3 ci-dessus),
   puis le zip est **supprimé après succès** de la bascule ;
 - si `build` ≤ `build_installe` correspondant → résidu obsolète (déjà
   appliqué lors d'un cycle précédent, ou périmé pour toute autre
# ── Zone modifiée : ligne 397 (8 ligne(s)) dans l'ancienne version → ligne 398 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -397,8 +398,8 @@ signalant qu'il s'agit d'un enfant : variable d'environnement (ex.
 au choix de l'implémentation. **Si ce marqueur est présent à son
 démarrage, l'instance saute inconditionnellement toute bascule
 d'auto-mise-à-jour supplémentaire — quoi que dise l'état local — et
-passe directement à l'étape 2 de la séquence de démarrage (lancement
-immédiat de l'application cible).**
+passe directement à l'étape 2 de la séquence de démarrage (vérification
+et téléchargement en arrière-plan).**
 
 Ce marqueur est portable Linux/Windows et indépendant de l'état des PID
 au runtime (pas de lecture du parent, pas de dépendance à `psutil` ni au
# ── Zone modifiée : ligne 532 (14 ligne(s)) dans l'ancienne version → ligne 533 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -532,14 +533,14 @@ applications cibles, Scrabble servant de premier exemple concret :
 | `version.json` (stockage) | Reste un petit fichier commité normalement dans le dépôt, pas un asset de Release |
 | Manifeste de mise à jour | `manifest.json` à la racine du zip (`{"build": N, "supprimer": [...]}`) ; `supprimer` est une liste noire optionnelle de chemins à effacer après extraction — fail-safe (un oubli laisse un fichier obsolète, jamais une perte de données) ; script `.bat`/`.sh` exécutable écarté pour portabilité Linux/Windows et sécurité (pas d'exécution de code téléchargé sans supervision) ; **`manifest.json` absent → bloquant** : bascule échoue, non appliquée, zip conservé pour nouvelle tentative ultérieure (zip considéré malformé, pas une absence volontaire de suppression) |
 | Timeout réseau | 2 à 3 secondes sur toute requête de vérification de version ; dépassement traité comme échec réseau |
-| Séquence de démarrage | Non bloquante : lancement immédiat de l'application cible dans sa version installée ; vérification et téléchargement en arrière-plan, appliqués au lancement suivant ; notification ntfy si mise à jour prête |
+| Séquence de démarrage | Non bloquante : Actualise est désormais lancé par l'application cible à son démarrage (et non l'inverse), il ne lance plus aucune application cible ; vérification et téléchargement en arrière-plan, appliqués au lancement suivant ; notification ntfy si mise à jour prête |
 | Vérification SHA-256 du zip | `version.json` porte un champ `sha256` du zip complet publié ; après téléchargement, avant mise en zone d'attente, comparaison du SHA-256 calculé sur le fichier reçu ; non-correspondance → téléchargement rejeté, aucune zone d'attente mise à jour, nouvelle tentative au cycle suivant (même repli que pour un échec réseau) ; liste de fichiers attendus post-extraction écartée (redondante une fois le zip validé, une extraction incomplète relevant d'un problème d'environnement local détectable par vérification d'erreur d'extraction) |
 | Bootstrap séparé | Écarté pour l'instant — Actualise reste un exécutable unique qui se met à jour lui-même, avec le garde-fou par marqueur ci-dessus |
 | Garde-fou anti-boucle | Marqueur explicite transmis parent → enfant (env `ACTUALISE_CHILD=1` ou arg `--child`), déclenché uniquement lors de la bascule d'une mise à jour déjà téléchargée — voir section dédiée ci-dessus |
 | Configuration portable | Dossier résolu **relativement à l'emplacement de l'exécutable `Actualise.exe`** (via `sys.executable` en mode PyInstaller figé) — pas un chemin Windows fixe codé en dur — pour permettre plusieurs installations indépendantes d'Actualise sur la même machine (une par application cible) sans qu'une installation n'écrase le `config.json` d'une autre ; équivalent portable sous Linux inchangé (ex. `~/.config/actualise/` ou variable d'environnement) |
 | Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable`, et `icone` (optionnel, chemin `.ico` documenté pour le setup cible — non lu au runtime par Actualise) ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
 | Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; **ce dossier séparé est exactement le dossier de configuration résolu relativement à l'exécutable** (voir « Configuration portable ») — pas de chemin d'installation distinct du dossier de configuration, `Actualise.exe`/`config.json`/zone d'attente cohabitent ; **le nom de ce dossier n'est plus fixe** (`C:\Actualise\`) mais choisi par chaque setup, convention suggérée `C:\Actualise_<NomApplication>\` (ex. `C:\Actualise_Scrabble\`, `C:\Actualise_Rummikub\`) pour éviter toute collision entre applications cibles différentes ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées ; **icône du raccourci** : le setup de l'application cible déploie son propre fichier `.ico` et l'utilise à la fois pour `IconFilename` du raccourci (qui pointe vers `Actualise.exe` mais affiche l'icône de l'application cible) et pour le champ `icone` de `config.json` — même chemin dans les deux cas — voir « Intégration avec le setup.exe d'une application cible » |
-| Cycle de vie d'Actualise | Lancement non bloquant de l'application cible (`Popen` sans `wait()`) : cycles de vie indépendants dès le lancement ; Actualise attend uniquement la fin de sa propre tâche de fond (vérification, téléchargement, validation SHA-256, notification ntfy), puis se termine à son tour — que l'application cible tourne encore ou non ; Actualise n'est pas un processus permanent |
+| Cycle de vie d'Actualise | Actualise ne lance plus l'application cible — c'est elle qui le lance à son démarrage ; Actualise attend uniquement la fin de sa propre tâche de fond (vérification, téléchargement, validation SHA-256, notification ntfy), puis se termine — indépendamment du cycle de vie de l'application cible ; Actualise n'est pas un processus permanent, c'est un aller-retour ponctuel à chaque démarrage de l'application cible |
 | Nommage versionné des zips en zone d'attente | `<préfixe>_<build>.zip` (ex. `actualise_48.zip`, `scrabble_112.zip`) — comparaison directe avec `build_installe` sans ouvrir le zip ; au démarrage, résidu avec `build` ≤ `build_installe` correspondant supprimé sans être appliqué (nettoyage automatique, garde-fou contre un zip bloqué indéfiniment en zone d'attente) ; **si plusieurs zips du même préfixe coexistent**, seul celui au build le plus élevé est considéré, les autres supprimés sans être appliqués (même logique que pour un résidu obsolète) — voir « Nommage versionné des zips en zone d'attente » |
 
 ## Points de vigilance connus
# (diff du fichier suivant)
diff --git a/actualise.py b/actualise.py
# (index — ignorable)
index 741b18f..d769cef 100644
# (avant — fichier suivant)
--- a/actualise.py
# (après — fichier suivant)
+++ b/actualise.py
# ── Zone modifiée : ligne 111 (8 ligne(s)) dans l'ancienne version → ligne 111 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -111,8 +111,11 @@ def _relancer_en_enfant(nom_app: str) -> None:
 
     Voir CONCEPTION.md, « Garde-fou anti-boucle infinie ». Gère aussi
     bien le cas d'un exécutable PyInstaller gelé (``sys.frozen``) que
-    l'exécution directe du script Python. ``--config nom_app`` est
-    transmis à l'enfant pour qu'il gère la même application cible.
+    l'exécution directe du script Python. ``nom_app`` ne sert plus à
+    lancer une application cible (Actualise ne lance plus aucun jeu) :
+    il est uniquement reconstruit en ``--config nom_app`` pour que
+    l'enfant sache pour quelle application cible poursuivre la
+    vérification/mise à jour en arrière-plan.
     """
     if getattr(sys, "frozen", False):
         commande = [sys.executable, "--child", "--config", nom_app]
# ── Zone modifiée : ligne 339 (10 ligne(s)) dans l'ancienne version → ligne 342 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -339,10 +342,10 @@ def appliquer_mises_a_jour_en_attente(est_enfant: bool, nom_app: str) -> None:
                 # Une nouvelle version d'Actualise vient d'être installée :
                 # on relance la version fraîchement installée comme 2ème
                 # instance (marqueur --child), puis on termine ce process
-                # parent immédiatement, sans lancer l'application cible ni
-                # démarrer la tâche de fond — l'enfant reprend la suite de
-                # la séquence de démarrage à sa place. Voir CONCEPTION.md,
-                # « Garde-fou anti-boucle infinie ».
+                # parent immédiatement, sans démarrer la tâche de fond —
+                # l'enfant reprend la suite de la séquence de démarrage à
+                # sa place. Voir CONCEPTION.md, « Garde-fou anti-boucle
+                # infinie ».
                 _relancer_en_enfant(nom_app)
                 raise SystemExit(0)
     except KeyError:
# ── Zone modifiée : ligne 360 (21 ligne(s)) dans l'ancienne version → ligne 363 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -360,21 +363,6 @@ def appliquer_mises_a_jour_en_attente(est_enfant: bool, nom_app: str) -> None:
         raise
 
 
-def lancer_application_cible(nom_app: str) -> None:
-    """Lance immédiatement l'application cible dans sa version
-    actuellement installée, sans attendre aucune vérification réseau.
-
-    Voir CONCEPTION.md, « Séquence de démarrage », étape 2.
-    """
-    configuration = config.charger_config(nom_app)
-    bloc_config = configuration["application_cible"]
-    chemin_executable = Path(bloc_config["repertoire_installation"]) / bloc_config["executable"]
-
-    # Popen sans wait() : cycles de vie indépendants dès le lancement
-    # (voir CONCEPTION.md, « Cycle de vie du processus Actualise »).
-    subprocess.Popen([str(chemin_executable)])
-
-
 _GABARIT_UPDATER_BAT = """@echo off
 timeout /t 5 /nobreak > nul
 cd /d "{dossier_actualise}"
# ── Zone modifiée : ligne 577 (10 ligne(s)) dans l'ancienne version → ligne 565 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -577,10 +565,6 @@ def main(argv: list[str] | None = None) -> int:
         # fonction termine le process (SystemExit) avant de revenir ici.
         appliquer_mises_a_jour_en_attente(est_enfant=arguments.child, nom_app=nom_app)
 
-        # Étape 2 : lancement immédiat de l'application cible, sans attendre
-        # le réseau.
-        lancer_application_cible(nom_app)
-
         # Étape 3 : vérification et téléchargement en arrière-plan, sans
         # bloquer l'utilisateur.
         thread_verification = threading.Thread(
# (diff du fichier suivant)
diff --git a/tests/test_actualise.py b/tests/test_actualise.py
# (index — ignorable)
index 8df0cb4..41072cf 100644
# (avant — fichier suivant)
--- a/tests/test_actualise.py
# (après — fichier suivant)
+++ b/tests/test_actualise.py
# ── Zone modifiée : ligne 13 (12 ligne(s)) dans l'ancienne version → ligne 13 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -13,12 +13,11 @@ import tempfile
 import unittest
 import zipfile
 from pathlib import Path
-from unittest.mock import MagicMock, call, patch
+from unittest.mock import call, patch
 
 from actualise import (
     appliquer_mises_a_jour_en_attente,
     configurer_logging,
-    lancer_application_cible,
     main,
     tache_verification_arriere_plan,
 )
# ── Zone modifiée : ligne 328 (29 ligne(s)) dans l'ancienne version → ligne 327 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -328,29 +327,6 @@ class TestConfigurerLogging(unittest.TestCase):
         self.assertTrue(dossier_config.is_dir())
 
 
-class TestLancerApplicationCible(unittest.TestCase):
-    @patch("actualise.subprocess.Popen")
-    @patch("actualise.config")
-    def test_popen_appele_avec_le_bon_chemin_sans_wait(self, mock_config, mock_popen):
-        mock_config.charger_config.return_value = {
-            "application_cible": {
-                "repertoire_installation": "/opt/scrabble",
-                "executable": "Scrabble.exe",
-                "nom": "Scrabble",
-                "build_installe": 47,
-                "depot_github": "AlainDelree/Scrabble",
-            }
-        }
-        mock_processus = MagicMock()
-        mock_popen.return_value = mock_processus
-
-        lancer_application_cible("scrabble")
-
-        mock_config.charger_config.assert_called_once_with("scrabble")
-        mock_popen.assert_called_once_with([str(Path("/opt/scrabble") / "Scrabble.exe")])
-        mock_processus.wait.assert_not_called()
-
-
 class TestTacheVerificationArrierePlan(unittest.TestCase):
     def setUp(self):
         self.dossier_temp = tempfile.TemporaryDirectory()
# ── Zone modifiée : ligne 450 (8 ligne(s)) dans l'ancienne version → ligne 426 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -450,8 +426,8 @@ class TestMain(unittest.TestCase):
         self.mock_config.chemin_config_portable.return_value = Path(self.dossier_temp.name)
 
     def test_exception_fatale_dans_main_loguee_et_propagee(self):
-        with patch("actualise.appliquer_mises_a_jour_en_attente"), patch(
-            "actualise.lancer_application_cible", side_effect=RuntimeError("boum fatal")
+        with patch(
+            "actualise.appliquer_mises_a_jour_en_attente", side_effect=RuntimeError("boum fatal")
         ), self.assertLogs("actualise", level="ERROR") as journal:
             with self.assertRaises(RuntimeError):
                 main(["--config", "scrabble"])
# ── Zone modifiée : ligne 459 (15 ligne(s)) dans l'ancienne version → ligne 435 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -459,15 +435,11 @@ class TestMain(unittest.TestCase):
         self.assertTrue(any("erreur fatale" in message for message in journal.output))
 
     def test_systemexit_relance_enfant_non_intercepte_ni_logue_comme_erreur(self):
-        with patch(
-            "actualise.appliquer_mises_a_jour_en_attente", side_effect=SystemExit(0)
-        ), patch("actualise.lancer_application_cible") as mock_lancer:
+        with patch("actualise.appliquer_mises_a_jour_en_attente", side_effect=SystemExit(0)):
             with self.assertNoLogs("actualise", level="ERROR"):
                 with self.assertRaises(SystemExit):
                     main(["--config", "scrabble"])
 
-            mock_lancer.assert_not_called()
-
 
 if __name__ == "__main__":
     unittest.main()
