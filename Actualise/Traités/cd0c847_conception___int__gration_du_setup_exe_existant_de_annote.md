cd0c847

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit cd0c847
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 22:24:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    conception : intégration du setup.exe existant de Scrabble avec Actualise (issue #8, chef #207)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CONCEPTION.md b/CONCEPTION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f11e691..be0a7a6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CONCEPTION.md
# ── Version APRÈS ce commit.
+++ b/CONCEPTION.md
# ── Zone modifiée : ligne 280 (6 ligne(s)) dans l'ancienne version → ligne 280 (43 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -280,6 +280,43 @@ sans nécessiter de compteur ni d'état persistant à gérer.
   renommé) : écrire à côté puis renommer évite tout verrouillage de
   fichier.
 
+## Intégration avec le setup.exe d'une application cible
+
+Le `setup.exe` d'une application cible (ex. Scrabble) existe déjà et,
+dans sa forme actuelle, installe uniquement cette application (dossier
+propre, raccourcis Bureau/menu Démarrer pointant directement vers son
+exécutable). Son adaptation pour s'intégrer avec Actualise suit les
+principes suivants — formulés pour être réutilisables avec de futures
+applications cibles, Scrabble servant de premier exemple concret :
+
+1. **Installation dans un dossier séparé.** Actualise s'installe dans
+   son propre dossier, indépendant du dossier d'installation de
+   l'application cible (ex. `C:\Actualise\`, cohérent avec la
+   « Configuration portable » déjà actée) — jamais à l'intérieur du
+   dossier de l'application cible. Ce découplage préserve la
+   réutilisabilité d'Actualise pour d'autres applications futures et
+   sépare le cycle de vie des deux installations : désinstaller
+   l'application cible n'entraîne pas nécessairement la désinstallation
+   d'Actualise, qui peut continuer à gérer d'autres programmes sur la
+   même machine.
+2. **Raccourcis modifiés.** Les raccourcis Bureau et menu Démarrer créés
+   par le setup pointent vers `Actualise.exe` (dans son dossier séparé),
+   jamais directement vers l'exécutable de l'application cible —
+   conforme à la décision actée dès le « Principe de fonctionnement »
+   (« le raccourci ne doit jamais pointer directement vers l'application
+   cible »).
+3. **Déploiement d'Actualise par le setup.** Le setup dépose désormais
+   `Actualise.exe` dans son dossier séparé, en plus des fichiers propres
+   à l'application cible.
+4. **Génération d'un `config.json` initial cohérent.** Le setup génère,
+   au moment de l'installation, un `config.json` reflétant les valeurs
+   réelles de cette installation : `build_installe` d'Actualise et de
+   l'application cible (versions effectivement embarquées dans ce
+   setup), `depot_github` des deux, `repertoire_installation` et
+   `executable` réels de l'application cible, `zone_attente`, et
+   `topic_ntfy` dédié à ce programme (voir « Contenu de `config.json` »
+   pour le format exact).
+
 ## Décisions actées
 
 | Point | Décision |
# ── Zone modifiée : ligne 301 (10 ligne(s)) dans l'ancienne version → ligne 338 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -301,10 +338,7 @@ sans nécessiter de compteur ni d'état persistant à gérer.
 | Garde-fou anti-boucle | Marqueur explicite transmis parent → enfant (env `ACTUALISE_CHILD=1` ou arg `--child`), déclenché uniquement lors de la bascule d'une mise à jour déjà téléchargée — voir section dédiée ci-dessus |
 | Configuration portable | `C:\Actualise\` sous Windows, équivalent portable sous Linux (ex. `~/.config/actualise/` ou variable d'environnement) pour préserver la réutilisabilité Linux |
 | Contenu de `config.json` | Deux blocs `actualise`/`application_cible` portant chacun `build_installe` et `depot_github` ; `application_cible` porte en plus `nom`, `repertoire_installation`, `executable` ; `zone_attente` (chemin de la zone d'attente locale) et `topic_ntfy` au niveau racine — voir « Contenu de `config.json` » |
-
-## Points encore ouverts
-
-- Interaction avec le futur `setup.exe` de Scrabble.
+| Intégration au setup.exe cible | Actualise s'installe dans un dossier séparé de l'application cible (jamais dans son dossier) ; les raccourcis créés par le setup sont redirigés vers `Actualise.exe` ; le setup dépose `Actualise.exe` et génère un `config.json` initial cohérent avec les versions réellement embarquées — voir « Intégration avec le setup.exe d'une application cible » |
 
 ## Points de vigilance connus
 
