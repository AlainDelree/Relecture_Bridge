6a9587a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6a9587a
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 10:54:05 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #305 : colonne mode_belgicisme (migration + persistance + filtrage accueil)
    
    - stockage.py : migration ALTER TABLE idempotente dans _initialiser_schema
      (bases existantes -> défaut 0/France) ; ResumePartie.mode_belgicisme ;
      demarrer_suivi() et lister_parties() lisent/écrivent la colonne.
    - accueil.py : lancer_partie() persiste le mode actif ; lister_parties_en_cours()
      filtre les parties selon config_partie.mode_belgicisme avant sélection.
    - accueil.js : choisirModeDictionnaire() rafraîchit la liste des parties après
      bascule France/Belgicisme.
    - tests : adaptation des mocks demarrer_suivi (nouveau paramètre par mot-clé)
      dans test_accueil.py, test_jeu_pose.py, test_journal_integration.py.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/persistance/stockage.py b/src/scrabble/persistance/stockage.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 15dd304..ee8de0e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/persistance/stockage.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/persistance/stockage.py
# ── Zone modifiée : ligne 106 (6 ligne(s)) dans l'ancienne version → ligne 106 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -106,6 +106,7 @@ class ResumePartie:
     scores_finaux: list[int] | None = None
     gagnants: list[str] | None = None
     scores_actuels: list[int] | None = None
+    mode_belgicisme: bool = False
 
     @property
     def terminee(self) -> bool:
# ── Zone modifiée : ligne 269 (6 ligne(s)) dans l'ancienne version → ligne 270 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -269,6 +270,17 @@ def _initialiser_schema(connexion: sqlite3.Connection) -> None:
             ON actions (id_partie, indice);
         """
     )
+    # Migration (issue #305) : ajoute la colonne ``mode_belgicisme`` aux bases
+    # créées avant son introduction. Les parties existantes reçoivent la
+    # valeur par défaut 0 (France), comportement souhaité.
+    colonnes = [
+        row[1] for row in connexion.execute("PRAGMA table_info(parties)").fetchall()
+    ]
+    if "mode_belgicisme" not in colonnes:
+        connexion.execute(
+            "ALTER TABLE parties ADD COLUMN "
+            "mode_belgicisme INTEGER NOT NULL DEFAULT 0"
+        )
     connexion.commit()
 
 
# ── Zone modifiée : ligne 281 (7 ligne(s)) dans l'ancienne version → ligne 293 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -281,7 +293,11 @@ def _maintenant() -> str:
 # Fonctions principales
 # --------------------------------------------------------------------------- #
 
-def demarrer_suivi(partie: Partie, chemin: _TypeChemin = CHEMIN_DEFAUT) -> int:
+def demarrer_suivi(
+    partie: Partie,
+    chemin: _TypeChemin = CHEMIN_DEFAUT,
+    mode_belgicisme: bool = False,
+) -> int:
     """Enregistre une partie fraîche (graine + joueurs), statut « en cours ».
 
     À appeler juste après :func:`~scrabble.moteur.partie.creer_partie`. Renvoie
# ── Zone modifiée : ligne 301 (14 ligne(s)) dans l'ancienne version → ligne 317 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -301,14 +317,15 @@ def demarrer_suivi(partie: Partie, chemin: _TypeChemin = CHEMIN_DEFAUT) -> int:
     with _connexion(chemin) as connexion:
         curseur = connexion.execute(
             "INSERT INTO parties "
-            "(graine, date_creation, date_maj, joueurs, statut) "
-            "VALUES (?, ?, ?, ?, ?)",
+            "(graine, date_creation, date_maj, joueurs, statut, mode_belgicisme) "
+            "VALUES (?, ?, ?, ?, ?, ?)",
             (
                 partie.graine,
                 horodatage,
                 horodatage,
                 _joueurs_vers_json(partie.joueurs),
                 STATUT_EN_COURS,
+                int(mode_belgicisme),
             ),
         )
         return int(curseur.lastrowid)
# ── Zone modifiée : ligne 461 (7 ligne(s)) dans l'ancienne version → ligne 478 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -461,7 +478,8 @@ def lister_parties(chemin: _TypeChemin = CHEMIN_DEFAUT) -> list[ResumePartie]:
     with _connexion(chemin) as connexion:
         lignes = connexion.execute(
             "SELECT id, statut, graine, date_creation, date_maj, joueurs, "
-            "scores_finaux, gagnants FROM parties ORDER BY date_maj DESC, id DESC"
+            "scores_finaux, gagnants, mode_belgicisme FROM parties "
+            "ORDER BY date_maj DESC, id DESC"
         ).fetchall()
         scores_par_partie = _scores_actuels_par_partie(connexion)
     resumes: list[ResumePartie] = []
# ── Zone modifiée : ligne 482 (6 ligne(s)) dans l'ancienne version → ligne 500 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -482,6 +500,7 @@ def lister_parties(chemin: _TypeChemin = CHEMIN_DEFAUT) -> list[ResumePartie]:
                 scores_finaux=None if scores is None else json.loads(scores),
                 gagnants=None if gagnants is None else json.loads(gagnants),
                 scores_actuels=scores_actuels,
+                mode_belgicisme=bool(ligne["mode_belgicisme"]),
             )
         )
     return resumes
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/accueil.py b/src/scrabble/ui/accueil.py
# (index — ignorable)
index 463e5c0..175e5a0 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/accueil.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/accueil.py
# ── Zone modifiée : ligne 560 (7 ligne(s)) dans l'ancienne version → ligne 560 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -560,7 +560,9 @@ class ApiAccueil:
                 bonus_fin_partie=bonus_fin_partie,
                 dictionnaire_ia=trie_ia,
             )
-            self._id_partie = demarrer_suivi(self._partie)
+            self._id_partie = demarrer_suivi(
+                self._partie, mode_belgicisme=self.config_partie.mode_belgicisme
+            )
             # Détail à rejouer côté Jeu pour l'écran de tirage (issue #170) :
             # l'ordre de création (humains puis ordinateurs) et la graine suffisent
             # à ``detail_tirage_ordre`` pour reproduire exactement le tirage.
# ── Zone modifiée : ligne 612 (6 ligne(s)) dans l'ancienne version → ligne 614 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -612,6 +614,11 @@ class ApiAccueil:
         """
         try:
             toutes = lister_parties()
+            # Filtrage par mode de jeu actif (issue #305) : une partie créée en
+            # mode Belgicisme ne doit pas apparaître à l'accueil en mode France,
+            # et inversement.
+            mode_actif = self.config_partie.mode_belgicisme
+            toutes = [p for p in toutes if p.mode_belgicisme == mode_actif]
             # ``toutes`` est trié date décroissante : le premier de chaque
             # catégorie est le plus récent.
             en_cours = next((p for p in toutes if not p.terminee), None)
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.js b/src/scrabble/ui/web/accueil.js
# (index — ignorable)
index 4ed17a4..6c54f5e 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.js
# ── Zone modifiée : ligne 330 (6 ligne(s)) dans l'ancienne version → ligne 330 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -330,6 +330,7 @@ document.addEventListener('DOMContentLoaded', async () => {
     async function choisirModeDictionnaire(modeBelgicisme) {
         syncModeDictionnaire(modeBelgicisme);
         await api.definir_mode_belgicisme(modeBelgicisme);
+        await chargerPartiesEnCours();
     }
 
     drapeauFrance.addEventListener('click', () => choisirModeDictionnaire(false));
# (diff du fichier suivant)
diff --git a/tests/test_accueil.py b/tests/test_accueil.py
# (index — ignorable)
index e8450ce..15f8ba9 100644
# (avant — fichier suivant)
--- a/tests/test_accueil.py
# (après — fichier suivant)
+++ b/tests/test_accueil.py
# ── Zone modifiée : ligne 331 (7 ligne(s)) dans l'ancienne version → ligne 331 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -331,7 +331,7 @@ class TestApiAccueilLancement:
         # Stub de la persistance pour éviter d'écrire sur disque
         monkeypatch.setattr(
             "scrabble.ui.accueil.demarrer_suivi",
-            lambda partie: 42,
+            lambda partie, **_: 42,
         )
 
         api = ApiAccueil()
# ── Zone modifiée : ligne 481 (7 ligne(s)) dans l'ancienne version → ligne 481 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -481,7 +481,7 @@ class TestSourceDictionnaireAppliquee:
             lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
-        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 7)
+        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie, **_: 7)
 
         api = ApiAccueil()
         api.ajouter_humain("Alice")
# ── Zone modifiée : ligne 535 (7 ligne(s)) dans l'ancienne version → ligne 535 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -535,7 +535,7 @@ class TestSourceDictionnaireAppliquee:
             lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
-        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 1)
+        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie, **_: 1)
 
         api = ApiAccueil()
         api.ajouter_humain("Alice")
# ── Zone modifiée : ligne 606 (7 ligne(s)) dans l'ancienne version → ligne 606 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -606,7 +606,7 @@ class TestSourceDictionnaireAppliquee:
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie", lambda source="ods", **_: tries[source]
         )
-        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 1)
+        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie, **_: 1)
 
         api = ApiAccueil()
         api.ajouter_humain("Alice")
# ── Zone modifiée : ligne 818 (7 ligne(s)) dans l'ancienne version → ligne 818 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -818,7 +818,7 @@ class TestApiAccueilInfosTirage:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.demarrer_suivi",
-            lambda partie: 7,
+            lambda partie, **_: 7,
         )
         return ApiAccueil()
 
# (diff du fichier suivant)
diff --git a/tests/test_jeu_pose.py b/tests/test_jeu_pose.py
# (index — ignorable)
index 1251730..882bffd 100644
# (avant — fichier suivant)
--- a/tests/test_jeu_pose.py
# (après — fichier suivant)
+++ b/tests/test_jeu_pose.py
# ── Zone modifiée : ligne 618 (7 ligne(s)) dans l'ancienne version → ligne 618 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -618,7 +618,7 @@ class TestSourceDictionnaireValidationCoup:
         )
         # Pas de persistance en base pendant le test : id_partie reste None,
         # ce qui neutralise aussi ``_persister_entrees`` côté ApiJeu.
-        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: None)
+        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie, **_: None)
 
         api = ApiAccueil()
         api.ajouter_humain("Alice")
# (diff du fichier suivant)
diff --git a/tests/test_journal_integration.py b/tests/test_journal_integration.py
# (index — ignorable)
index 7bd4ca2..6543b7e 100644
# (avant — fichier suivant)
--- a/tests/test_journal_integration.py
# (après — fichier suivant)
+++ b/tests/test_journal_integration.py
# ── Zone modifiée : ligne 117 (7 ligne(s)) dans l'ancienne version → ligne 117 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -117,7 +117,7 @@ class TestJournalAccueil:
             "scrabble.ui.accueil.obtenir_trie",
             lambda source="ods", **_: Trie.depuis_iterable(["MAISON", "TEST"]),
         )
-        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 42)
+        monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie, **_: 42)
 
         api = ApiAccueil()
         api.ajouter_humain("Alice")
