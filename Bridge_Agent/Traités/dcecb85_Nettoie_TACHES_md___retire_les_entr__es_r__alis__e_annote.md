dcecb85

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit dcecb85
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 31 10:34:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Nettoie TACHES.md : retire les entrées réalisées (templates #284, niveau de détail #281)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7ab9d0a..132b5b5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 11 (22 ligne(s)) dans l'ancienne version → ligne 11 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -11,22 +11,6 @@ Procédure : nssm restart CCW-Watcher, puis supprimer le(s) fichier(s)
   Get-ChildItem C:\CCW\Bridge_Agent\logs\verrous\ -Filter "*.lock"
   Remove-Item C:\CCW\Bridge_Agent\logs\verrous\<fichier>.lock
 
-## Issues récurrentes — bibliothèque de templates par projet
-
-**Contexte** : certaines issues reviennent régulièrement à l'identique ou
-quasi-identique (ex. build Scrabble, build Actualise). Aujourd'hui il faut
-soit redemander à Claude Chat de régénérer l'issue, soit fouiller dans les
-conversations passées pour retrouver la dernière version.
-
-**Idée** : un onglet « Templates » dans new_issue.py permettant de gérer
-une bibliothèque d'issues types par projet. Cliquer sur un template
-pré-remplit le formulaire (titre + corps complet), prêt à envoyer en un
-clic. Création/modification des templates depuis l'interface, stockés
-localement (ex. JSON dans configs/ ou dossier dédié templates/, gitignoré
-ou versionné selon le choix d'Alain).
-
-**Statut** : idée en attente, pas de développement lancé.
-
 ---
 
 ## Projet dédié à la communication CCL ↔ CCW
# ── Zone modifiée : ligne 51 (123 ligne(s)) dans l'ancienne version → ligne 35 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -51,123 +35,6 @@ nouveau dépôt, config NSSM), labels à recréer sur le nouveau dépôt.
 **Statut** : idée en attente, setup physique (fixe Windows) pas encore
 en place. À reprendre quand le nouveau hardware sera opérationnel.
 
-## Empecher Claude Chat de créer des issues trop détailler
-Parfois, Claude Chat ecrit de tres longue issue en détaillant beaucoup trop le code et ce faisant fait le travail de CCL.  Il faut trouver un moyen(consigne ou autre) pour le maintenir dans des issues de plus haut niveau.  Exemple d'issue détaillé ci-après:
-
-`#Titre: Fix JavascriptException callback perdu lors navigation pywebview (reprendre_partie / jeu_retour_accueil)
-
-| PROJET | rummikub |
-
-## Contexte
-
-Au lancement du jeu, des `JavascriptException` apparaissent en boucle dans le
-terminal :
-
-    webview.errors.JavascriptException: window.pywebview._returnValuesCallbacks
-    ["reprendre_partie"]["<id>"] is not a function
-
-Même chose pour `jeu_retour_accueil`. Aucun crash visible côté UI, mais les
-erreurs sont répétées et gênent la lisibilité du terminal.
-
-**Cause** : quand JS appelle `api.reprendre_partie()` (ou `jeu_retour_accueil()`
-ou `lancer_nouvelle_partie()`), pywebview traite l'appel dans un thread interne
-`Thread-N (_call)`. Ce thread exécute la méthode Python, qui appelle
-`self._window.load_url(...)` — ce qui navigue immédiatement vers la nouvelle
-page et **détruit le contexte JS de la page source**, y compris les entrées de
-`window.pywebview._returnValuesCallbacks`. Ensuite, pywebview tente d'invoquer
-le callback de retour sur la nouvelle page, où il n'existe pas → `TypeError`.
-
-**Fix standard pour pywebview** : différer l'appel `load_url` dans un thread
-daemon avec `time.sleep(0.05)`, pour laisser pywebview envoyer la valeur de
-retour à la page encore chargée avant de naviguer.
-
-## Tâche demandée
-
-Modifier `src/rummikub/ui/api.py` uniquement.
-
-Ajouter en tête de fichier (après les imports existants) :
-
-```python
-import threading
-import time
-```
-
-Remplacer les trois méthodes de navigation comme suit :
-
-**1. `lancer_nouvelle_partie`**
-
-Avant :
-```python
-def lancer_nouvelle_partie(self, config):
-    self._app.naviguer_vers_jeu(config)
-    return {"ok": True}
-```
-
-Après :
-```python
-def lancer_nouvelle_partie(self, config):
-    def _go():
-        time.sleep(0.05)
-        self._app.naviguer_vers_jeu(config)
-    threading.Thread(target=_go, daemon=True).start()
-    return {"ok": True}
-```
-
-**2. `reprendre_partie`**
-
-Avant :
-```python
-def reprendre_partie(self, pid):
-    etat = Stockage.charger_partie(pid)
-    if not etat:
-        return {"ok": False, "erreur": "Partie introuvable"}
-    self._app.reprendre_jeu(etat)
-    return {"ok": True}
-```
-
-Après :
-```python
-def reprendre_partie(self, pid):
-    etat = Stockage.charger_partie(pid)
-    if not etat:
-        return {"ok": False, "erreur": "Partie introuvable"}
-    def _go():
-        time.sleep(0.05)
-        self._app.reprendre_jeu(etat)
-    threading.Thread(target=_go, daemon=True).start()
-    return {"ok": True}
-```
-
-**3. `jeu_retour_accueil`**
-
-Avant :
-```python
-def jeu_retour_accueil(self):
-    self._app.naviguer_vers_accueil(); return {"ok": True}
-```
-
-Après :
-```python
-def jeu_retour_accueil(self):
-    def _go():
-        time.sleep(0.05)
-        self._app.naviguer_vers_accueil()
-    threading.Thread(target=_go, daemon=True).start()
-    return {"ok": True}
-```
-
-Aucune autre modification. Aucun autre fichier touché.
-
-## Résultat attendu
-
-- `api.py` modifié avec les trois méthodes corrigées et les imports `threading`
-  et `time` ajoutés.
-- Vérifier que le fichier compile sans erreur (`python3 -c "import
-  src.rummikub.ui.api"` ou `python3 -m py_compile
-  src/rummikub/ui/api.py` depuis la racine du projet).
-- Commit de sauvegarde puis commit du fix.
-- Rapport confirmant l'absence d'erreur de compilation.`
-
 ## Calibration automatique du TIMEOUT — trois défauts à corriger
 
 **Contexte** : la formule du §19 est
