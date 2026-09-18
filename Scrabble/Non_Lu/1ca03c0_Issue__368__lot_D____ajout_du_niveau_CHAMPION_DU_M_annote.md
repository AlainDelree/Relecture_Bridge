1ca03c0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1ca03c0
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Aug 5 17:56:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #368 (lot D) : ajout du niveau CHAMPION_DU_MONDE au moteur IA
    
    Ajoute Niveau.CHAMPION_DU_MONDE en fin d'enum (rétro-compatible avec les
    parties sérialisées par .name). Complète les dicts indexés par Niveau
    (_MALUS_LONGUEUR, _BONUS_PREMIUM) et le dispatch de choisir_coup : il
    réutilise exactement la stratégie et les tranches d'EXPERT tant que le lot C
    n'a pas câblé son propre vocabulaire (ODS8 complet).
    
    Nouveau test paramétré sur tous les membres de Niveau (garde-fou contre
    l'oubli d'un dict lors d'un futur ajout de niveau). Tests de monotonie
    adaptés pour l'ordre DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT <=
    CHAMPION_DU_MONDE (égalité Expert/Champion documentée comme temporaire,
    levée par le lot C). Nouveau test paramétré de rétro-compatibilité de la
    sauvegarde couvrant tous les niveaux.
    
    CHAMPION_DU_MONDE n'est pas proposable au joueur à ce stade (écran d'accueil
    et dégradé CSS réservés au lot F) ; test_accueil.py l'exclut explicitement
    de la vérification des labels pour cette raison précise.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b404d6a..cfcf68a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (31 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,31 @@ Historique des changements notables, par ordre antéchronologique. Voir aussi
 
 ### Ajouté
 
+- **Issue #368** (lot D, suite de #366) — Ajout de `Niveau.CHAMPION_DU_MONDE`
+  au moteur IA (`scrabble.moteur.ia`), en fin d'énumération (rétro-compatible
+  avec les parties existantes, sérialisées par `.name` dans `stockage.py`).
+  Réutilise EXACTEMENT la stratégie et les tranches de malus/bonus d'EXPERT
+  (`_MALUS_LONGUEUR`/`_BONUS_PREMIUM` : -25/+20, sélection du meilleur coup) :
+  il ne s'en distinguera par le vocabulaire (ODS8 complet) qu'à partir du lot
+  C, câblage explicitement hors périmètre de ce lot. Nouveau test paramétré
+  sur tous les membres de `Niveau` (`TestTousLesNiveauxResolventUnCoup`),
+  garde-fou structurel contre l'oubli d'un dict indexé par `Niveau` lors d'un
+  futur ajout de niveau. Tests de monotonie adaptés pour attendre l'ordre
+  `DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT <= CHAMPION_DU_MONDE`
+  (égalité Expert/Champion documentée comme temporaire dans la docstring du
+  module, levée par le lot C) plutôt que relâchés. Nouveau test paramétré de
+  rétro-compatibilité de la sauvegarde (`test_reprise_tous_les_niveaux_ia`,
+  `tests/test_persistance.py`) confirmant que `Niveau[niveau]` résout chaque
+  membre, y compris le nouveau. CHAMPION_DU_MONDE n'est volontairement PAS
+  proposable au joueur à ce stade (écran d'accueil et dégradé CSS réservés au
+  lot F) — `tests/test_accueil.py::TestNiveauxLabels::test_tous_les_niveaux_ont_un_label`
+  l'exclut explicitement de sa vérification pour cette raison. D'autres
+  emplacements indexés par `Niveau` ont été recensés hors périmètre de ce lot
+  et non modifiés : `NIVEAUX_LABELS` (`scrabble.ui.accueil`, lot F) et la map
+  de libellés JS de `scrabble/ui/web/jeu.js` (celle-ci a un filet de repli qui
+  affiche le nom brut de l'enum pour toute clé absente, donc pas de crash ;
+  elle manquait déjà `AVANCE` avant ce lot).
+
 - **Issue #366** (lot A, suite de #205/#206) — `scripts/generer_mots_courants.py
   --tous` : produit en une seule commande les cinq fichiers de vocabulaire IA
   par palier de difficulté (`mots_courants_debutant/facile/intermediaire/
# (diff du fichier suivant)
diff --git a/src/scrabble/moteur/ia.py b/src/scrabble/moteur/ia.py
# (index — ignorable)
index 2393f54..8d480b5 100644
# (avant — fichier suivant)
--- a/src/scrabble/moteur/ia.py
# (après — fichier suivant)
+++ b/src/scrabble/moteur/ia.py
# ── Zone modifiée : ligne 7 (6 ligne(s)) dans l'ancienne version → ligne 7 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -7,6 +7,12 @@ de sélection dans la liste triée par score varie.
 
 Niveaux de difficulté
 ---------------------
+* **CHAMPION_DU_MONDE** : même stratégie de sélection qu'EXPERT (meilleur
+  coup) et même tranche de malus/bonus stratégiques. Ne se distingue
+  d'EXPERT que par le vocabulaire (ODS8 complet au lieu de l'intersection
+  Lexique), câblé par le lot C (issue #368, lot D) — tant que ce câblage
+  n'existe pas, CHAMPION_DU_MONDE se comporte à l'identique d'EXPERT, égalité
+  DOCUMENTÉE ET TEMPORAIRE (voir « Ordre réel de force » ci-dessous).
 * **EXPERT** : choisit le meilleur coup (premier de la liste triée). En cas
   d'égalité de score entre plusieurs coups de tête, choix aléatoire parmi eux.
 * **AVANCE** : choix aléatoire uniforme parmi les 15 % meilleurs coups (top
# ── Zone modifiée : ligne 28 (8 ligne(s)) dans l'ancienne version → ligne 34 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,8 +34,9 @@ Niveaux de difficulté
 Ordre réel de force (score moyen)
 ---------------------------------
 Les stratégies ci-dessus produisent, en moyenne, l'ordre croissant
-``DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT`` — cohérent avec l'ordre
-de la classe :class:`Niveau` et avec ce que suggèrent les noms des niveaux.
+``DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT <= CHAMPION_DU_MONDE``
+— cohérent avec l'ordre de la classe :class:`Niveau` et avec ce que
+suggèrent les noms des niveaux.
 
 Cette monotonie est STRUCTURELLE : tous les niveaux passent par le même
 mécanisme (tri par score stratégique puis tirage uniforme dans une tranche
# ── Zone modifiée : ligne 43 (6 ligne(s)) dans l'ancienne version → ligne 50 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -43,6 +50,17 @@ spécifique : l'issue #359 avait doté DEBUTANT d'un filtre sur la longueur
 (``nb_nouvelles >= 3``) qui le rendait plus sélectif que FACILE et cassait la
 monotonie ; l'issue #361 l'a remplacé par la tranche top 85 %.
 
+Le dernier maillon, EXPERT <= CHAMPION_DU_MONDE, est une ÉGALITÉ et non une
+inégalité stricte : à ce stade (lot D de l'issue #368), CHAMPION_DU_MONDE
+n'est câblé sur aucun vocabulaire distinct d'EXPERT (le lot C s'en charge),
+et partage exactement la même stratégie et les mêmes tranches de malus/bonus.
+Les deux niveaux produisent donc, à graine égale, EXACTEMENT le même coup —
+l'égalité est mécanique, pas approximative. Cette égalité est TEMPORAIRE :
+une fois le lot C câblé (ODS8 complet pour CHAMPION_DU_MONDE contre
+l'intersection Lexique pour EXPERT), le vocabulaire plus large de
+CHAMPION_DU_MONDE lui ouvrira des coups inaccessibles à EXPERT et l'inégalité
+deviendra stricte.
+
 Pourquoi « top 60 % » pour FACILE plutôt qu'une moitié/tranche centrale ? La
 distribution des scores est fortement asymétrique : quelques coups à très
 fort score (un « scrabble » vaut ~70 pts) tirent la MOYENNE d'un tirage large
# ── Zone modifiée : ligne 78 (13 ligne(s)) dans l'ancienne version → ligne 96 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -78,13 +96,20 @@ if TYPE_CHECKING:
 
 
 class Niveau(Enum):
-    """Niveaux de difficulté IA, du plus faible au plus fort."""
+    """Niveaux de difficulté IA, du plus faible au plus fort.
+
+    :attr:`CHAMPION_DU_MONDE` est ajouté en fin de liste (issue #368, lot D) :
+    la position en fin garantit la rétro-compatibilité des parties existantes
+    sérialisées par ``.name`` (voir ``stockage.py``), la position des
+    ``auto()`` précédents n'ayant aucun impact sur les données stockées.
+    """
 
     DEBUTANT = auto()
     FACILE = auto()
     INTERMEDIAIRE = auto()
     AVANCE = auto()
     EXPERT = auto()
+    CHAMPION_DU_MONDE = auto()
 
 
 #: Malus (négatif) appliqué au score de tri d'un coup posant peu de lettres
# ── Zone modifiée : ligne 97 (6 ligne(s)) dans l'ancienne version → ligne 122 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -97,6 +122,7 @@ _MALUS_LONGUEUR: dict[Niveau, int] = {
     Niveau.INTERMEDIAIRE: -12,
     Niveau.AVANCE: -18,
     Niveau.EXPERT: -25,
+    Niveau.CHAMPION_DU_MONDE: -25,
 }
 
 #: Bonus (positif) appliqué au score de tri d'un coup exploitant au moins
# ── Zone modifiée : ligne 108 (6 ligne(s)) dans l'ancienne version → ligne 134 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -108,6 +134,7 @@ _BONUS_PREMIUM: dict[Niveau, int] = {
     Niveau.INTERMEDIAIRE: 8,
     Niveau.AVANCE: 12,
     Niveau.EXPERT: 20,
+    Niveau.CHAMPION_DU_MONDE: 20,
 }
 
 #: Cases dont le bonus porte sur le mot entier (plus précieuses que les
# ── Zone modifiée : ligne 187 (7 ligne(s)) dans l'ancienne version → ligne 214 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -187,7 +214,7 @@ def choisir_coup(
 
     coups = sorted(coups, key=lambda cn: _score_strategique(cn, niveau), reverse=True)
 
-    if niveau == Niveau.EXPERT:
+    if niveau in (Niveau.EXPERT, Niveau.CHAMPION_DU_MONDE):
         return _choisir_expert(coups, rng)
     if niveau == Niveau.AVANCE:
         return _choisir_avance(coups, rng)
# ── Zone modifiée : ligne 199 (7 ligne(s)) dans l'ancienne version → ligne 226 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -199,7 +226,12 @@ def choisir_coup(
 
 
 def _choisir_expert(coups: list[CoupNote], rng: random.Random) -> Coup:
-    """EXPERT : meilleur coup, aléatoire en cas d'égalité de score."""
+    """EXPERT et CHAMPION_DU_MONDE : meilleur coup, aléatoire en cas d'égalité.
+
+    CHAMPION_DU_MONDE réutilise cette fonction tant que le lot C (issue #368)
+    n'a pas câblé son vocabulaire propre (ODS8 complet) : jusque-là, les deux
+    niveaux sont stratégiquement identiques.
+    """
     meilleur_score = coups[0].score
     meilleurs = [cn for cn in coups if cn.score == meilleur_score]
     return rng.choice(meilleurs).coup
# (diff du fichier suivant)
diff --git a/tests/test_accueil.py b/tests/test_accueil.py
# (index — ignorable)
index 15f8ba9..5dc4919 100644
# (avant — fichier suivant)
--- a/tests/test_accueil.py
# (après — fichier suivant)
+++ b/tests/test_accueil.py
# ── Zone modifiée : ligne 271 (8 ligne(s)) dans l'ancienne version → ligne 271 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -271,8 +271,18 @@ class TestNiveauxLabels:
     """Tests du mapping des labels de niveau."""
 
     def test_tous_les_niveaux_ont_un_label(self):
-        """Chaque niveau de l'enum a un label français."""
+        """Chaque niveau proposable à l'écran d'accueil a un label français.
+
+        Niveau.CHAMPION_DU_MONDE (issue #368, lot D) est volontairement exclu
+        de cette vérification : il n'est pas encore proposable au joueur, ce
+        câblage étant réservé au lot F. Le retirer de la liste plutôt que de
+        toucher ``NIVEAUX_LABELS``/``accueil.py`` respecte le périmètre du
+        lot D tout en gardant ce test représentatif de son intention réelle
+        (« tout niveau sélectionnable a un label »).
+        """
         for niveau in Niveau:
+            if niveau is Niveau.CHAMPION_DU_MONDE:
+                continue
             label_trouve = any(
                 NIVEAUX_LABELS[label] == niveau for label in NIVEAUX_LABELS
             )
# (diff du fichier suivant)
diff --git a/tests/test_moteur_ia.py b/tests/test_moteur_ia.py
# (index — ignorable)
index 1d2d948..4ab9e4c 100644
# (avant — fichier suivant)
--- a/tests/test_moteur_ia.py
# (après — fichier suivant)
+++ b/tests/test_moteur_ia.py
# ── Zone modifiée : ligne 1 (8 ligne(s)) dans l'ancienne version → ligne 1 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,8 +1,14 @@
 """Tests des stratégies IA à niveaux de difficulté.
 
-Couvre les 5 niveaux (EXPERT, AVANCE, INTERMEDIAIRE, FACILE, DEBUTANT) sur la
-base du générateur exhaustif, la reproductibilité avec graine fixée, les cas
-limites (un seul coup, aucun coup), et l'intégration avec Partie/creer_partie.
+Couvre les 6 niveaux (EXPERT, CHAMPION_DU_MONDE, AVANCE, INTERMEDIAIRE,
+FACILE, DEBUTANT) sur la base du générateur exhaustif, la reproductibilité
+avec graine fixée, les cas limites (un seul coup, aucun coup), et
+l'intégration avec Partie/creer_partie.
+
+CHAMPION_DU_MONDE (issue #368, lot D) n'est pas encore câblé sur un
+vocabulaire distinct d'EXPERT (lot C à venir) : les deux niveaux sont
+stratégiquement identiques ici, d'où l'égalité (et non l'inégalité stricte)
+dans les tests de monotonie ci-dessous.
 """
 
 from __future__ import annotations
# ── Zone modifiée : ligne 348 (6 ligne(s)) dans l'ancienne version → ligne 354 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -348,6 +354,27 @@ class TestFacile:
 # --------------------------------------------------------------------------- #
 
 
+class TestTousLesNiveauxResolventUnCoup:
+    """Garde-fou structurel contre l'oubli d'un dict indexé par Niveau.
+
+    Paramétré sur TOUS les membres de :class:`Niveau` (plutôt qu'une liste en
+    dur) : tout futur ajout de niveau est automatiquement couvert sans
+    modifier ce test, et un ``KeyError`` sur un dict comme
+    ``_MALUS_LONGUEUR``/``_BONUS_PREMIUM`` oublié lors d'un ajout est détecté
+    immédiatement (issue #368, lot D).
+    """
+
+    @pytest.mark.parametrize("niveau", list(Niveau))
+    def test_resout_un_coup_sans_exception(self, niveau):
+        plateau = PlateauPartie()
+        chevalet = list("CADRES")
+        dico = _trie("CADRE", "CADRES", "AS", "A", "SA", "DE", "RE", "DA", "ES")
+        coup = choisir_coup(plateau, chevalet, dico, niveau, random.Random(42))
+        assert coup is not None
+        coups = generer_coups(plateau, chevalet, dico)
+        assert any(cn.coup == coup for cn in coups)
+
+
 class TestCasLimites:
     """Comportement sur listes courtes ou vides."""
 
# ── Zone modifiée : ligne 545 (6 ligne(s)) dans l'ancienne version → ligne 572 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -545,6 +572,11 @@ _MOTS_IA_RESTREINT = (
 #   * FACILE tire dans le top 60 % (écarte les 40 % plus faibles) → au-dessus
 #     de DEBUTANT mais nettement sous INTERMEDIAIRE ;
 #   * INTERMEDIAIRE (top 33 %), AVANCE (top 15 %), EXPERT (meilleur) → croissant.
+#   * CHAMPION_DU_MONDE réutilise EXACTEMENT la stratégie et les tranches
+#     d'EXPERT tant que le lot C (issue #368) n'a pas câblé son vocabulaire
+#     propre : à graine égale, les deux niveaux choisissent le même coup, donc
+#     leurs scores moyens sont ÉGAUX (pas strictement croissants) — dernier
+#     maillon documenté comme TEMPORAIRE dans la docstring du module.
 # NB : depuis l'issue #208, FACILE n'est plus la moitié INFÉRIEURE (ce qui le
 # plaçait sous DEBUTANT, contrairement à ce que suggèrent les noms) mais le
 # top 60 %. L'ordre réel coïncide désormais avec l'ordre des noms et avec
# ── Zone modifiée : ligne 559 (8 ligne(s)) dans l'ancienne version → ligne 591 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -559,8 +591,15 @@ _ORDRE_CROISSANT_ATTENDU = [
     Niveau.INTERMEDIAIRE,
     Niveau.AVANCE,
     Niveau.EXPERT,
+    Niveau.CHAMPION_DU_MONDE,
 ]
 
+#: Paires consécutives de :data:`_ORDRE_CROISSANT_ATTENDU` dont l'ordre est
+#: une ÉGALITÉ attendue (et non une inégalité stricte). Seule la paire
+#: EXPERT/CHAMPION_DU_MONDE l'est, tant que le lot C n'a pas câblé un
+#: vocabulaire propre à CHAMPION_DU_MONDE (issue #368, lot D).
+_PAIRES_EGALITE_ATTENDUE = {(Niveau.EXPERT, Niveau.CHAMPION_DU_MONDE)}
+
 
 def _moyennes_par_niveau(
     plateau: PlateauPartie,
# ── Zone modifiée : ligne 606 (18 ligne(s)) dans l'ancienne version → ligne 645 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -606,18 +645,26 @@ class TestProgressionTrieIaRestreint:
         assert len({cn.score for cn in coups_ia}) >= 3
 
     def test_progression_monotone_avec_filtre_actif(self):
-        """La progression reste strictement monotone avec le Trie IA restreint.
+        """La progression reste monotone (au sens large) avec le Trie IA restreint.
 
         Confirme l'hypothèse du rapport #203 : le filtre étant global, la
         monotonie des scores moyens est préservée une fois le filtre actif.
+        Croissance stricte partout, SAUF sur la paire EXPERT/CHAMPION_DU_MONDE
+        (égalité attendue et temporaire, cf. docstring du module — issue #368,
+        lot D : CHAMPION_DU_MONDE ne sera câblé sur son propre vocabulaire
+        qu'au lot C).
         """
         dico_ia = Trie.depuis_iterable(_MOTS_IA_RESTREINT)
         moy = _moyennes_par_niveau(self.plateau, self.chevalet, dico_ia)
         ordre = sorted(Niveau, key=lambda niv: moy[niv])
         assert ordre == _ORDRE_CROISSANT_ATTENDU
-        # Strictement croissant le long de l'ordre attendu.
-        valeurs = [moy[niv] for niv in _ORDRE_CROISSANT_ATTENDU]
-        assert all(a < b for a, b in zip(valeurs, valeurs[1:]))
+        # Croissant le long de l'ordre attendu, strictement sauf aux paires
+        # d'égalité documentées (EXPERT/CHAMPION_DU_MONDE).
+        for a, b in zip(_ORDRE_CROISSANT_ATTENDU, _ORDRE_CROISSANT_ATTENDU[1:]):
+            if (a, b) in _PAIRES_EGALITE_ATTENDUE:
+                assert moy[a] == moy[b], f"{a} et {b} devraient être égaux : {moy}"
+            else:
+                assert moy[a] < moy[b], f"{a} devrait être < {b} : {moy}"
 
     def test_niveaux_restent_perceptiblement_distincts(self):
         """Aucun niveau ne se confond avec son voisin sous le filtre.
# ── Zone modifiée : ligne 625 (13 ligne(s)) dans l'ancienne version → ligne 672 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -625,13 +672,18 @@ class TestProgressionTrieIaRestreint:
         Point #3 de l'issue : on veut détecter le cas où un niveau ne se
         distinguerait plus suffisamment d'un autre. On exige un écart d'au moins
         1 point entre niveaux adjacents dans l'ordre de progression, seuil
-        au-delà duquel la différence reste perceptible en jeu.
+        au-delà duquel la différence reste perceptible en jeu — SAUF pour la
+        paire EXPERT/CHAMPION_DU_MONDE, dont l'égalité est attendue et
+        temporaire (issue #368, lot D ; levée par le lot C).
         """
         dico_ia = Trie.depuis_iterable(_MOTS_IA_RESTREINT)
         moy = _moyennes_par_niveau(self.plateau, self.chevalet, dico_ia)
-        valeurs = [moy[niv] for niv in _ORDRE_CROISSANT_ATTENDU]
-        ecarts = [b - a for a, b in zip(valeurs, valeurs[1:])]
-        assert min(ecarts) >= 1.0, f"Niveaux trop proches sous filtre : {ecarts}"
+        for a, b in zip(_ORDRE_CROISSANT_ATTENDU, _ORDRE_CROISSANT_ATTENDU[1:]):
+            ecart = moy[b] - moy[a]
+            if (a, b) in _PAIRES_EGALITE_ATTENDUE:
+                assert ecart == 0.0, f"{a} et {b} devraient être égaux : {moy}"
+            else:
+                assert ecart >= 1.0, f"{a} et {b} trop proches sous filtre : {moy}"
 
     def test_ordre_relatif_identique_avec_et_sans_filtre(self):
         """L'ordre RELATIF des niveaux est identique avec et sans filtre.
# (diff du fichier suivant)
diff --git a/tests/test_persistance.py b/tests/test_persistance.py
# (index — ignorable)
index fdf6905..5e89d9f 100644
# (avant — fichier suivant)
--- a/tests/test_persistance.py
# (après — fichier suivant)
+++ b/tests/test_persistance.py
# ── Zone modifiée : ligne 26 (7 ligne(s)) dans l'ancienne version → ligne 26 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -26,7 +26,7 @@ import pytest
 
 from scrabble.dictionnaire.dictionnaire import Trie
 from scrabble.moteur.ia import Niveau
-from scrabble.moteur.partie import Partie, creer_partie
+from scrabble.moteur.partie import Joueur, Partie, creer_partie
 from scrabble.moteur.plateau_partie import (
     CENTRE,
     Coup,
# ── Zone modifiée : ligne 222 (6 ligne(s)) dans l'ancienne version → ligne 222 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -222,6 +222,29 @@ def test_reprise_partie_partiellement_jouee(tmp_path):
     assert not reprise.terminee
 
 
+@pytest.mark.parametrize("niveau", list(Niveau))
+def test_reprise_tous_les_niveaux_ia(tmp_path, niveau):
+    """Une partie sauvegardée avec n'importe quel niveau IA reste chargeable.
+
+    Paramétré sur TOUS les membres de :class:`Niveau` (plutôt qu'une liste en
+    dur) pour garantir que ``Niveau[niveau]`` (``stockage.py``) résout
+    correctement chaque valeur, y compris ``CHAMPION_DU_MONDE`` ajouté par
+    l'issue #368 (lot D) — rétro-compatibilité du blob JSON stocké par
+    ``.name``, garde-fou contre un futur ajout de niveau non résolvable.
+    """
+    chemin = tmp_path / "parties.db"
+    trie = _trie()
+    partie = Partie(
+        [Joueur("Humain"), Joueur("IA", humain=False, niveau=niveau)],
+        trie,
+        graine=1,
+    )
+    id_partie = demarrer_suivi(partie, chemin)
+
+    reprise = reprendre_partie(id_partie, trie, chemin)
+    assert reprise.joueurs[1].niveau == niveau
+
+
 def test_reprise_echange_sac_identique(tmp_path):
     """Le sac après reprise doit être identique : preuve que les lettres
 
