a6b6781

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a6b6781
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 08:24:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Retirer du suivi git REARCHITECTURE_ALAIN.md et REARCHITECTURE_CLAUDE_CODE.md (gitignorés, issue #199)
    
    Ces fichiers étaient listés dans .gitignore sous 'ne jamais publier' mais
    avaient été committés avant l'ajout de la règle, restant donc suivis et
    visibles sur le dépôt public. Retrait du suivi uniquement (git rm --cached) ;
    fichiers conservés sur disque. Ne purge pas l'historique existant (hors scope).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/REARCHITECTURE_ALAIN.md b/REARCHITECTURE_ALAIN.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4336bda..0000000
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/REARCHITECTURE_ALAIN.md
# ── Version APRÈS ce commit.
+++ /dev/null
# ── Zone modifiée : ligne 1 (129 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,129 +0,0 @@
-# Plan de réarchitecture AlChess — Version Alain
-
----
-
-## Pourquoi réarchitecturer ?
-
-Actuellement AlChess est conçu pour Linux uniquement. Pour qu'il tourne aussi sur Windows et Android, il faut séparer clairement ce qui est "universel" de ce qui est "spécifique Linux".
-
-La bonne nouvelle : la logique de jeu (règles, moteurs, PGN) n'a rien de spécifique Linux. Seul le bas niveau USB/Bluetooth l'est.
-
----
-
-## Ce qui change — vue d'ensemble
-
-```
-AVANT (tout mélangé) :
-┌─────────────────────────────────────┐
-│  alchess.py + server.py + driver.py │
-│  Logique jeu + USB + Web + OS       │
-│  → Linux uniquement                 │
-└─────────────────────────────────────┘
-
-APRÈS (séparé proprement) :
-┌─────────────────────────────────────┐
-│         CORE (Python pur)           │
-│  Logique jeu, moteurs, PGN          │
-│  → tourne sur Linux ET Windows      │
-└──────────────┬──────────────────────┘
-               │ API WebSocket
-       ┌───────┴──────────┐
-       ▼                  ▼
-  Web (HTML/JS)      Flutter (futur)
-  Linux + Windows    Android/iOS
-       │
-  ┌────┴────┐
-  ▼         ▼
-Driver    Driver
-USB/Linux USB/Win
-(hidapi)  (hidapi)
-```
-
----
-
-## Prérequis — Avant de commencer
-
-### Créer une VM Windows
-
-Avoir une VM Windows prête avant de démarrer l'étape 1 évite une interruption en cours de route.
-
-1. Télécharger une image VM officielle Microsoft (gratuite, pour développeurs) :
-   **https://developer.microsoft.com/windows/downloads/virtual-machines/**
-2. L'installer dans VirtualBox (gratuit) : **https://www.virtualbox.org/**
-3. Vérifier que la VM démarre et qu'on peut y installer Python
-
-> ℹ️ Pas besoin de licence Windows — l'image gratuite fonctionne avec un watermark
-> "Activer Windows" mais c'est sans importance pour tester AlChess.
-
----
-
-## Les 4 étapes dans l'ordre
-
-### Étape 1 — Remplacer `_niclink.so` par `hidapi` Python
-**Ce que c'est :** le fichier `_niclink.so` est un composant compilé en Rust qui communique avec l'échiquier via USB. Il ne fonctionne que sur Linux.
-
-**Ce qu'on fait :** le remplacer par une bibliothèque Python appelée `hidapi` qui fait la même chose mais fonctionne sur Linux ET Windows ET Mac, sans compilation.
-
-**Pour toi :** après cette étape, AlChess fonctionne exactement comme avant sur Linux, mais le composant problématique est supprimé. L'installation sur un nouveau PC devient aussi plus simple (plus besoin de compiler).
-
-**Risque :** il faudra tester soigneusement que la communication avec l'échiquier est identique. C'est l'étape la plus incertaine.
-
----
-
-### Étape 2 — Séparer la logique de jeu du serveur web
-**Ce que c'est :** actuellement `alchess.py` mélange la logique de jeu (règles, tours, moteurs) et le serveur web (Flask). C'est difficile à porter sur d'autres plateformes.
-
-**Ce qu'on fait :** extraire la logique pure dans un module `core/` indépendant, qui ne sait rien de Flask ni de web. Le serveur Flask devient juste une "interface" qui utilise ce core.
-
-**Pour toi :** rien ne change visuellement. Mais le code devient beaucoup plus propre et portable.
-
----
-
-### Étape 3 — Portage Windows
-**Ce que c'est :** une fois les étapes 1 et 2 faites, Windows devient faisable.
-
-**Ce qu'on fait :**
-- Adapter les chemins (plus de `/home/alain/` en dur)
-- Supprimer les appels Linux-only (ModemManager, udev)
-- Tester sur Windows avec un Chessnut Air
-
-**Pour toi :** AlChess tourne sur Windows. Le plus grand public potentiel.
-
----
-
-### Étape 4 — App Android (futur)
-**Ce que c'est :** une application mobile autonome qui se connecte à l'échiquier via Bluetooth.
-
-**Ce qu'on fait :** développer une app Flutter séparée qui utilise le même "core" Python (ou une version équivalente) et se connecte au Chessnut Air via Bluetooth.
-
-**Pour toi :** projet séparé, à envisager quand Linux et Windows sont stables.
-
----
-
-## Ordre recommandé
-
-| Étape | Durée estimée | Risque | Gain |
-|-------|--------------|--------|------|
-| 1. hidapi | 1-2 sessions | Moyen (tester USB) | Installation simplifiée + multiplateforme |
-| 2. Core séparé | 2-3 sessions | Faible (refactoring) | Code propre + Windows facilité |
-| 3. Windows | 2-3 sessions | Faible après étapes 1+2 | Grand public |
-| 4. Android | Projet séparé | Nouveau projet | Mobile |
-
----
-
-## Ce qui NE change PAS
-
-- L'interface web (HTML/JS) — identique
-- Les moteurs (Stockfish, Maia, Rodent) — identiques
-- La logique de jeu — identique
-- Les fichiers PGN, exercices, base SQLite — identiques
-- L'expérience utilisateur — identique
-
----
-
-## Comment travailler
-
-- Chaque étape se fait sur la branche `dev`
-- On merge sur `master` uniquement quand l'étape est validée et testée
-- Un backup pinné avant chaque étape
-- Claude Code s'occupe du code, tu testes après chaque étape
# (diff du fichier suivant)
diff --git a/REARCHITECTURE_CLAUDE_CODE.md b/REARCHITECTURE_CLAUDE_CODE.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index a38c1f9..0000000
# (avant — fichier suivant)
--- a/REARCHITECTURE_CLAUDE_CODE.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (206 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,206 +0,0 @@
-# Plan de réarchitecture AlChess — Document technique pour Claude Code
-
-**À lire avant de commencer tout travail de réarchitecture.**
-**Lire aussi CLAUDE.md, TACHES.md et CONTEXTE.md.**
-
----
-
-## Contexte
-
-AlChess est une application Python/Flask-SocketIO connectant un échiquier physique Chessnut Air (USB) à une interface web. L'objectif de cette réarchitecture est de rendre le projet multiplateforme (Linux → Windows → Android) sans réécrire l'essentiel.
-
-**Contrainte absolue :** chaque étape doit laisser AlChess entièrement fonctionnel sur Linux. Jamais de régression entre les étapes.
-
----
-
-## État actuel — problèmes identifiés
-
-### 1. `_niclink.so` — dépendance Linux-only
-`nicsoft/niclink/driver.py` importe `from . import _niclink` — une extension C++ compilée via pybind11/Rust, spécifique Linux (`.so`). Elle expose :
-- `_niclink.lights_out()`
-- `_niclink.set_all_leds(r0..r7)`
-- `_niclink.set_led(row, col, val)`
-- `_niclink.beep()`
-- `_niclink.gameover_lights()`
-- La connexion USB au Chessnut Air (`idVendor=0x2d80, idProduct=0x8003`)
-
-**Solution :** remplacer par `hidapi` (Python pur, multiplateforme).
-
-### 2. Chemins hardcodés
-`pathlib.Path.home() / "NicLink" / ...` apparaît dans `alchess.py`, `server.py`, et plusieurs modules. Sur Windows, le dossier s'appelle probablement autrement.
-
-**Solution :** centraliser dans un module `nicsoft/config.py` avec une constante `APP_DIR`.
-
-### 3. Appels OS Linux-only dans `alchess.py`
-- `subprocess.run(["sudo", "systemctl", "stop", "ModemManager"])` — Linux uniquement
-- `os.dup2(devnull_fd, 1)` — redirige stdout, fonctionne aussi sur Windows mais fragile
-- `signal.SIGINT` dans `on_disconnect` — fonctionne sur Windows mais à vérifier
-
-### 4. Mélange logique/transport dans `alchess.py`
-`alchess.py` (1350 lignes) contient à la fois :
-- La boucle principale de menu et dispatch des modes
-- Le lancement et la gestion des threads de jeu
-- Des accès directs à `web_server._app_state` (couplage fort)
-- Des instanciations de `NicLinkManager` (USB) directement dans les `_run_*` functions
-
----
-
-## Étape 1 — Remplacer `_niclink.so` par `hidapi`
-
-### Objectif
-Rendre `driver.py` indépendant de `_niclink.so` en communiquant directement avec le Chessnut Air via `hid` (Python hidapi).
-
-### Protocole Chessnut Air (connu)
-- USB HID, `idVendor=0x2d80`, `idProduct=0x8003`
-- Lecture position : envoyer une commande, lire 64 bytes en retour → FEN
-- LEDs : commandes de type `set_all_leds` avec 8 rangées de bits
-- Beep : commande dédiée
-
-**À vérifier en premier :** le protocole exact est dans `src/niclink_src/` (sources C++). Lire `src/niclink_src/` pour extraire les commandes USB brutes avant de coder quoi que ce soit.
-
-### Plan d'implémentation
-
-1. **Créer `nicsoft/niclink/hid_backend.py`** — nouveau backend hidapi
-   ```python
-   import hid
-   VENDOR_ID  = 0x2d80
-   PRODUCT_ID = 0x8003  # Air ; Air+ peut différer
-   
-   class ChessnutHID:
-       def connect(self): ...
-       def get_raw_position(self) -> bytes: ...
-       def set_leds(self, pattern: list[str]): ...
-       def lights_out(self): ...
-       def beep(self): ...
-   ```
-
-2. **Modifier `driver.py`** — remplacer `from . import _niclink` par `from .hid_backend import ChessnutHID` et adapter les appels.
-
-3. **Garder `_niclink.so` comme fallback** pendant la période de transition :
-   ```python
-   try:
-       from .hid_backend import ChessnutHID as _backend
-   except ImportError:
-       from . import _niclink as _backend  # fallback legacy
-   ```
-
-4. **Tests** : vérifier que `get_fen()`, LEDs et beep fonctionnent identiquement.
-
-### Dépendance à ajouter
-```
-hidapi==0.14.0
-```
-(`pip install hidapi` — fonctionne sur Linux, Windows, Mac sans compilation)
-
----
-
-## Étape 2 — Centraliser les chemins dans `config.py`
-
-### Créer `nicsoft/config.py`
-```python
-import pathlib, os
-
-# Dossier de base de l'application
-# Peut être surchargé via variable d'environnement ALCHESS_DIR
-_default = pathlib.Path.home() / "NicLink"
-APP_DIR = pathlib.Path(os.environ.get("ALCHESS_DIR", str(_default)))
-
-LOGS_DIR    = APP_DIR / "logs"
-DATA_DIR    = APP_DIR / "data"
-GAMES_DIR   = APP_DIR / "games"
-ENGINES_DIR = APP_DIR / "engines"
-```
-
-### Remplacements dans le code
-Chercher toutes les occurrences de `pathlib.Path.home() / "NicLink"` et `os.path.expanduser("~/NicLink")` dans :
-- `alchess.py` (nombreuses occurrences)
-- `server.py` (LOG_FILE, TEST_CONFIG_DIR, _get_game_folders)
-- Tous les modules sous `nicsoft/modes/`
-
-Remplacer par `from nicsoft.config import APP_DIR, LOGS_DIR, DATA_DIR, GAMES_DIR`.
-
----
-
-## Étape 3 — Isoler les appels OS dans `alchess.py`
-
-### Créer `nicsoft/platform_utils.py`
-```python
-import sys, subprocess
-
-def stop_modem_manager():
-    """No-op sur Windows."""
-    if sys.platform != "linux":
-        return
-    try:
-        subprocess.run(["sudo", "systemctl", "stop", "ModemManager"],
-                       capture_output=True, timeout=5)
-    except Exception:
-        pass
-
-def start_modem_manager():
-    if sys.platform != "linux":
-        return
-    try:
-        subprocess.run(["sudo", "systemctl", "start", "ModemManager"],
-                       capture_output=True, timeout=5)
-    except Exception:
-        pass
-```
-
-Remplacer les appels directs dans `alchess.py` par ces fonctions.
-
----
-
-## Étape 4 — Séparer Core et Transport (optionnel pour Windows, requis pour Android)
-
-### Objectif
-Extraire la logique de jeu pure dans `nicsoft/core/` indépendant de Flask.
-
-### Structure cible
-```
-nicsoft/
-├── core/                    # Nouveau — logique pure, pas de Flask
-│   ├── game_manager.py      # Machine d'état, dispatch modes
-│   ├── board_interface.py   # Abstraction échiquier (physique ou virtuel)
-│   └── engine_runner.py     # Lancement moteurs UCI
-├── web/                     # Inchangé — Flask/SocketIO
-│   ├── server.py
-│   ├── alchess.py           # Devient un adaptateur web → core
-│   └── ...
-└── niclink/                 # Inchangé — driver échiquier
-    └── driver.py
-```
-
-**Note :** cette étape est la plus longue (2-3 sessions). Ne pas la commencer avant que l'étape 1 soit validée en production.
-
----
-
-## Ordre d'exécution
-
-```
-Étape 1 : hidapi          → branche dev → tester → merger master
-Étape 2 : config.py       → branche dev → tester → merger master  
-Étape 3 : platform_utils  → branche dev → tester → merger master
-Étape 4 : core/           → branche dev → tester → merger master
-Portage Windows           → branche windows → tester → merger master
-```
-
----
-
-## Règles de travail
-
-- **Backup pinné avant chaque étape** : `python -m nicsoft.utils.backup_manager --pin --label "avant-etape-N-..."`
-- **Ne jamais casser Linux** : tester après chaque modification
-- **Un commit par sous-étape** avec message descriptif
-- **Modifier `TACHES.md`** après chaque étape terminée
-- **Signaler les fins de tâche** par : `python3 ~/NicLink/bip.py`
-
----
-
-## Points d'attention critiques
-
-- **`NicLinkManager` fait un `sys.exit()` si l'échiquier n'est pas détecté** (driver.py ligne 128) — à remplacer par une exception custom pour ne pas tuer Flask.
-- **`web_server._app_state` est accédé directement** depuis `alchess.py` — couplage fort à réduire progressivement.
-- **Le FEN reader thread tourne à 50ms** — la performance doit être identique avec hidapi.
-- **`os.dup2(devnull_fd, 1)`** dans plusieurs `_run_*` de `alchess.py` — redirection stdout pour masquer les logs C++ de lc0. Avec hidapi, plus besoin de ça.
-- **Chessnut Air+** a peut-être un `idProduct` différent de `0x8003` — prévoir une config ou auto-détection dans `hid_backend.py`.
