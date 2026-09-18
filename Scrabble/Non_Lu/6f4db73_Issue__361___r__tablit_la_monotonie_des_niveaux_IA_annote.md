6f4db73

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6f4db73
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 4 20:08:59 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #361 : rétablit la monotonie des niveaux IA (DEBUTANT en tranche top 85 %)
    
    - Supprime le filtre dur nb_nouvelles >= 3 de DEBUTANT (issue #359) qui le
      rendait plus sélectif que FACILE et cassait la monotonie des niveaux.
    - DEBUTANT tire désormais uniformément dans le top 85 % des coups triés par
      score stratégique, comme les autres niveaux : chaîne d'inclusion stricte
      85 % ⊃ 60 % ⊃ 33 % ⊃ 15 % ⊃ meilleur, monotonie structurelle.
    - Rétablit l'assertion complète moy_debutant < moy_facile < moy_inter.
    - Fixtures TestProgressionTrieIaRestreint enrichies en mots de 2 lettres
      (courants : ON OR AS AN OS dans le vocabulaire humain ; obscurs : RA OC NA
      TA SA dans le seul dico complet) — la monotonie est réellement éprouvée en
      présence de hooks, plus par artefact de fixture.
    - Docstrings ia.py et test_moteur_ia.py mises en cohérence.
    - CHANGELOG : entrée #361 + entrée rétroactive #359 (jamais consignée).
    
    Écarts mesurés (400 tirages, dico restreint) : 1.20 / 1.48 / 2.06 / 3.37,
    tous >= 1.0 — seuil 85 % retenu sans ajustement. 782 tests verts.
    
    Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3a50219..1a9e261 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 7 (8 ligne(s)) dans l'ancienne version → ligne 7 (48 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -7,8 +7,48 @@ Historique des changements notables, par ordre antéchronologique. Voir aussi
 
 ## Non publié
 
+### Modifié
+
+- **Issue #359** — Stratégie IA : ajout d'un score stratégique de tri
+  (`_score_strategique` dans `moteur/ia.py`), distinct du score réel du coup,
+  corrigeant deux biais du tri glouton sur score brut : pénalité sur les
+  coups posant peu de lettres (`nb_nouvelles <= 2`, malus doublé pour un
+  « hook » d'une seule lettre) et bonus pour les coups exploitant une case
+  premium (plein bonus pour MOT_DOUBLE/MOT_TRIPLE/CENTRE, moitié pour les
+  bonus de lettre). Les deux ajustements croissent avec le niveau
+  (`_MALUS_LONGUEUR`, `_BONUS_PREMIUM`). `moteur/generateur.py` expose
+  désormais `nb_nouvelles` (nombre de cases nouvellement posées) dans
+  `CoupNote` pour permettre ce tri, les cases bonus étant déjà portées par
+  `DetailMot`. Entrée rétroactive : le travail avait été committé sous les
+  libellés `avant-issue-359-*` (7efd0d5) sans entrée CHANGELOG. NB : le
+  filtre dur `nb_nouvelles >= 3` que #359 avait donné à DEBUTANT a été
+  remplacé par l'issue #361 (voir ci-dessous).
+
 ### Corrigé
 
+- **Issue #361** — Monotonie des niveaux IA rétablie. Le filtre dur
+  `nb_nouvelles >= 3` introduit par #359 pour DEBUTANT le rendait plus
+  sélectif que FACILE sur ce critère : sa moyenne pouvait dépasser celle de
+  FACILE (une joueuse choisissant « Débutant » pouvait affronter une IA plus
+  forte qu'en « Facile »), et le test `test_score_moyen_superieur_a_debutant`
+  avait été relâché pour tolérer la rupture. DEBUTANT passe désormais par le
+  même mécanisme de tranche que les autres niveaux : tirage uniforme dans le
+  top 85 % des coups triés par score stratégique (`max(1, len(coups) * 85 //
+  100)`). La chaîne d'inclusion des tranches redevient stricte (85 % ⊃ 60 %
+  ⊃ 33 % ⊃ 15 % ⊃ meilleur), ce qui rend la monotonie
+  `DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT` structurelle ; le
+  malus longueur (-5) de DEBUTANT devient opérant (les hooks les plus
+  faibles tombent dans les 15 % écartés). L'assertion complète
+  `moy_debutant < moy_facile < moy_inter` est rétablie, et les fixtures de
+  `TestProgressionTrieIaRestreint` incluent désormais des mots de 2 lettres
+  (courants dans le vocabulaire « humain » : ON, OR, AS, AN, OS ; obscurs
+  dans le seul dico complet : RA, OC, NA, TA, SA) pour que la monotonie soit
+  réellement éprouvée en présence de hooks — elle était auparavant
+  trivialement satisfaite par artefact de fixture (aucun mot < 3 lettres).
+  Écarts mesurés entre niveaux adjacents (400 tirages, dico restreint) :
+  1.20 / 1.48 / 2.06 / 3.37 points — tous ≥ 1.0, seuil 85 % retenu sans
+  ajustement.
+
 - **Issue #345** — `build/rebuild_scrabble.bat` ne téléchargeait pas
   `Actualise.exe` (dépendance de l'installeur, chemin attendu
   `C:\Temp\ScrabbleBuild\Actualise.exe`) et ne produisait pas `scrabble.zip`
# (diff du fichier suivant)
diff --git a/src/scrabble/moteur/ia.py b/src/scrabble/moteur/ia.py
# (index — ignorable)
index 8ffec27..2393f54 100644
# (avant — fichier suivant)
--- a/src/scrabble/moteur/ia.py
# (après — fichier suivant)
+++ b/src/scrabble/moteur/ia.py
# ── Zone modifiée : ligne 19 (8 ligne(s)) dans l'ancienne version → ligne 19 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -19,8 +19,11 @@ Niveaux de difficulté
   60 %), c'est-à-dire en écartant les 40 % de coups les plus faibles. Reste
   délibérément sous-optimal, mais réellement plus fort que DEBUTANT en score
   moyen (issue #208, voir la note ci-dessous).
-* **DEBUTANT** : choix aléatoire uniforme parmi TOUS les coups, sans
-  considération de score. Peut occasionnellement jouer un bon coup par chance.
+* **DEBUTANT** : choix aléatoire uniforme parmi les 85 % meilleurs coups (top
+  85 %). N'écarte que les 15 % de coups les plus faibles au sens du score
+  stratégique (typiquement les hooks pénalisés par le malus longueur), ce qui
+  le laisse très proche d'un tirage au hasard tout en garantissant qu'il reste
+  le niveau le plus faible (issue #361).
 
 Ordre réel de force (score moyen)
 ---------------------------------
# ── Zone modifiée : ligne 28 (21 ligne(s)) dans l'ancienne version → ligne 31 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,21 +31,30 @@ Les stratégies ci-dessus produisent, en moyenne, l'ordre croissant
 ``DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT`` — cohérent avec l'ordre
 de la classe :class:`Niveau` et avec ce que suggèrent les noms des niveaux.
 
-Pourquoi « top 60 % » plutôt qu'une moitié/tranche centrale ? La distribution
-des scores est fortement asymétrique : quelques coups à très fort score (un
-« scrabble » vaut ~70 pts) tirent la MOYENNE de DEBUTANT (qui échantillonne
-tous les coups) bien au-dessus de la médiane. Une tranche centrée sur la
-médiane resterait donc, en moyenne, SOUS DEBUTANT. Écarter les 40 % les plus
-faibles garantit au contraire ``FACILE > DEBUTANT`` (on ne retient que la
-partie haute), tout en gardant ``FACILE < INTERMEDIAIRE`` puisque le top 33 %
-d'INTERMEDIAIRE est un sous-ensemble strictement meilleur du top 60 %. Cette
-monotonie est donc structurelle, indépendante du dictionnaire employé (elle
-vaut avec ou sans le filtre de « vocabulaire humain », issue #206/#207).
+Cette monotonie est STRUCTURELLE : tous les niveaux passent par le même
+mécanisme (tri par score stratégique puis tirage uniforme dans une tranche
+haute), et les tranches sont strictement emboîtées — top 85 % (DEBUTANT) ⊃
+top 60 % (FACILE) ⊃ top 33 % (INTERMEDIAIRE) ⊃ top 15 % (AVANCE) ⊃ meilleur
+coup (EXPERT). Chaque tranche étant un sous-ensemble strictement meilleur de
+la précédente, les scores moyens croissent mécaniquement avec le niveau,
+indépendamment du dictionnaire employé (avec ou sans le filtre de
+« vocabulaire humain », issue #206/#207). Aucun niveau n'a de filtre dur
+spécifique : l'issue #359 avait doté DEBUTANT d'un filtre sur la longueur
+(``nb_nouvelles >= 3``) qui le rendait plus sélectif que FACILE et cassait la
+monotonie ; l'issue #361 l'a remplacé par la tranche top 85 %.
+
+Pourquoi « top 60 % » pour FACILE plutôt qu'une moitié/tranche centrale ? La
+distribution des scores est fortement asymétrique : quelques coups à très
+fort score (un « scrabble » vaut ~70 pts) tirent la MOYENNE d'un tirage large
+bien au-dessus de la médiane. Une tranche centrée sur la médiane resterait
+donc, en moyenne, SOUS DEBUTANT. Écarter les 40 % les plus faibles garantit
+au contraire ``FACILE > DEBUTANT`` (issue #208).
 
 Comportement de repli (listes courtes)
 --------------------------------------
-Si la tranche calculée (top 15 %, tiers, top 60 %) est vide, on retombe sur la liste
-complète. Cela évite tout crash sur des positions avec peu de coups jouables.
+Si la tranche calculée (top 15 %, tiers, top 60 %, top 85 %) est vide, on
+retombe sur la liste complète via ``max(1, ...)``. Cela évite tout crash sur
+des positions avec peu de coups jouables.
 Exemple : 2 coups disponibles, tiers = 0 → on choisit parmi les 2.
 
 Reproductibilité
# ── Zone modifiée : ligne 183 (10 ligne(s)) dans l'ancienne version → ligne 195 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -183,10 +195,7 @@ def choisir_coup(
         return _choisir_intermediaire(coups, rng)
     if niveau == Niveau.FACILE:
         return _choisir_facile(coups, rng)
-    # DEBUTANT : parmi les coups formant un vrai mot (>= 3 lettres posées) si
-    # certains existent, sinon repli sur la liste complète (issue #359).
-    coups_longs = [cn for cn in coups if cn.nb_nouvelles >= 3]
-    return _choisir_debutant(coups_longs if coups_longs else coups, rng)
+    return _choisir_debutant(coups, rng)
 
 
 def _choisir_expert(coups: list[CoupNote], rng: random.Random) -> Coup:
# ── Zone modifiée : ligne 228 (5 ligne(s)) dans l'ancienne version → ligne 237 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -228,5 +237,16 @@ def _choisir_facile(coups: list[CoupNote], rng: random.Random) -> Coup:
 
 
 def _choisir_debutant(coups: list[CoupNote], rng: random.Random) -> Coup:
-    """DEBUTANT : aléatoire parmi tous les coups."""
-    return rng.choice(coups).coup
+    """DEBUTANT : aléatoire parmi les 85 % meilleurs coups (top 85 %).
+
+    Tranche la plus large de tous les niveaux : seuls les 15 % de coups les
+    plus faibles au sens du score stratégique sont écartés (le malus longueur
+    y relègue les hooks les plus pauvres). C'est ce qui rend le tri
+    stratégique opérant pour DEBUTANT tout en le maintenant strictement sous
+    FACILE (top 60 %, sous-ensemble strictement meilleur) — issue #361, en
+    remplacement du filtre dur ``nb_nouvelles >= 3`` de l'issue #359 qui
+    cassait la monotonie des niveaux. ``max(1, ...)`` garantit un
+    sous-ensemble non vide, comme les autres niveaux.
+    """
+    taille_haut = max(1, len(coups) * 85 // 100)
+    return rng.choice(coups[:taille_haut]).coup
# (diff du fichier suivant)
diff --git a/tests/test_moteur_ia.py b/tests/test_moteur_ia.py
# (index — ignorable)
index 5e954ad..1d2d948 100644
# (avant — fichier suivant)
--- a/tests/test_moteur_ia.py
# (après — fichier suivant)
+++ b/tests/test_moteur_ia.py
# ── Zone modifiée : ligne 147 (21 ligne(s)) dans l'ancienne version → ligne 147 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -147,21 +147,28 @@ class TestExpert:
 
 
 class TestDebutant:
-    """DEBUTANT choisit uniformément parmi tous les coups.
-
-    Depuis l'issue #359, DEBUTANT filtre d'abord sur les coups formant un
-    vrai mot (``nb_nouvelles >= 3``) quand il en existe : le dictionnaire de
-    ce test inclut donc plusieurs mots de 3+ lettres (CADRE, ACRE, CAR) pour
-    que la distribution reste observable sur plusieurs coups qualifiants.
+    """DEBUTANT choisit uniformément dans les 85 % meilleurs coups (top 85 %).
+
+    Depuis l'issue #361, DEBUTANT passe par le même mécanisme de tranche que
+    les autres niveaux (il n'a plus le filtre dur ``nb_nouvelles >= 3`` de
+    l'issue #359, qui le rendait plus sélectif que FACILE). Le dictionnaire
+    de ce test mélange mots de 3+ lettres (CADRE, ACRE, CAR) et mots courts
+    pour offrir assez de coups : la tranche top 85 % y écarte réellement les
+    coups les plus faibles au sens du score stratégique.
     """
 
-    def test_distribution_uniforme_tous_coups(self):
+    def test_choisit_dans_le_top_85_pct(self):
         plateau = PlateauPartie()
         chevalet = list("CADRE")
         dico = _trie("CADRE", "ACRE", "CAR", "DE", "RE", "A", "DA")
-        coups = generer_coups(plateau, chevalet, dico)
-        nb_coups = len(coups)
-        assert nb_coups > 1
+        coups = sorted(
+            generer_coups(plateau, chevalet, dico),
+            key=lambda cn: _score_strategique(cn, Niveau.DEBUTANT),
+            reverse=True,
+        )
+        assert len(coups) > 1
+        taille_haut = max(1, len(coups) * 85 // 100)
+        haut = coups[:taille_haut]
 
         choisis: dict[tuple, int] = {}
         tirages = 500
# ── Zone modifiée : ligne 170 (6 ligne(s)) dans l'ancienne version → ligne 177 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -170,6 +177,7 @@ class TestDebutant:
                 plateau, chevalet, dico, Niveau.DEBUTANT, random.Random(graine)
             )
             if coup is not None:
+                assert any(cn.coup == coup for cn in haut)
                 cle = (coup.ligne, coup.colonne, coup.direction.value)
                 choisis[cle] = choisis.get(cle, 0) + 1
         assert len(choisis) > 1
# ── Zone modifiée : ligne 301 (21 ligne(s)) dans l'ancienne version → ligne 309 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -301,21 +309,14 @@ class TestFacile:
                 assert any(cn.coup == coup for cn in haut)
 
     def test_score_moyen_superieur_a_debutant(self):
-        """FACILE reste plus faible qu'INTERMEDIAIRE en score moyen.
+        """FACILE bat DEBUTANT en score moyen, tout en restant sous INTERMEDIAIRE.
 
         Cœur de l'issue #208 : l'ancienne stratégie (moitié inférieure) rendait
-        FACILE plus FAIBLE qu'INTERMEDIAIRE ; le passage au top 60 % corrige
-        cette inversion sur un plateau/chevalet offrant des scores étalés.
-
-        Depuis l'issue #359, DEBUTANT ne tire plus uniformément parmi TOUS les
-        coups : il filtre d'abord sur les coups formant un vrai mot
-        (``nb_nouvelles >= 3``) quand il en existe. Sur ce plateau quasi vide,
-        ce filtre exclut la plupart des hooks faibles (1-2 lettres) que
-        DEBUTANT pouvait tirer avant, si bien que sa moyenne peut désormais
-        dépasser celle de FACILE (dont le top 60 % conserve encore des hooks
-        proches du centre, boostés par les cases premium). La comparaison
-        DEBUTANT < FACILE n'est donc plus une garantie structurelle ; seule la
-        comparaison DEBUTANT < INTERMEDIAIRE < ... reste valide.
+        FACILE plus FAIBLE que DEBUTANT ; le passage au top 60 % corrige cette
+        inversion sur un plateau/chevalet offrant des scores étalés. Depuis
+        l'issue #361, DEBUTANT tire dans le top 85 % (sur-ensemble strict du
+        top 60 % de FACILE), donc la chaîne DEBUTANT < FACILE < INTERMEDIAIRE
+        est structurelle et vérifiée en entier.
         """
         plateau = PlateauPartie()
         chevalet = list("CADRES")
# ── Zone modifiée : ligne 339 (8 ligne(s)) dans l'ancienne version → ligne 340 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -339,8 +340,7 @@ class TestFacile:
         moy_debutant = moyenne_scores(Niveau.DEBUTANT)
         moy_facile = moyenne_scores(Niveau.FACILE)
         moy_inter = moyenne_scores(Niveau.INTERMEDIAIRE)
-        assert moy_facile < moy_inter
-        assert moy_debutant < moy_inter
+        assert moy_debutant < moy_facile < moy_inter
 
 
 # --------------------------------------------------------------------------- #
# ── Zone modifiée : ligne 502 (8 ligne(s)) dans l'ancienne version → ligne 502 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -502,8 +502,13 @@ class TestIntegrationPartie:
 # fois avec un Trie IA strictement plus petit que le dico complet.
 
 # Vocabulaire complet riche autour du chevalet « CARTONS » (plateau vide, ancrage
-# central unique). Offre 118 coups aux scores étalés, dont un « scrabble »
-# (bingo) CARTONS à 70 points.
+# central unique). Offre de nombreux coups aux scores étalés, dont un
+# « scrabble » (bingo) CARTONS à 70 points. Inclut depuis l'issue #361 des mots
+# de 2 lettres — courants (ON, OR, AS, AN, OS) comme obscurs du Scrabble (RA,
+# OC, NA, TA, SA) — afin que les coups courts pénalisés par le malus longueur
+# existent réellement dans les listes de coups : sans eux, la monotonie des
+# niveaux était trivialement satisfaite sur plateau vide (aucun coup < 3
+# lettres, artefact de fixture).
 _MOTS_COMPLET = (
     "CARTON", "CARTONS", "CARTE", "CARTES", "CANOT", "CANOTS", "CARAT",
     "CARATS", "ARC", "ARCS", "ARCON", "ARCONS", "CAR", "CARS", "CAS", "SAC",
# ── Zone modifiée : ligne 514 (6 ligne(s)) dans l'ancienne version → ligne 519 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -514,6 +519,7 @@ _MOTS_COMPLET = (
     "ANT", "RATON", "RATONS", "TANCS", "TANC", "CANT", "CANTS", "NOTA",
     "SONAR", "SONATE", "SCORE", "CROATS", "TARON", "ROTAS", "ROTA", "TROCA",
     "SANTO", "CATOR",
+    "ON", "OR", "AS", "AN", "OS", "RA", "OC", "NA", "TA", "SA",
 )
 
 # Sous-ensemble « vocabulaire humain » : mots courants seulement, sous-ensemble
# ── Zone modifiée : ligne 521 (16 ligne(s)) dans l'ancienne version → ligne 527 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -521,16 +527,21 @@ _MOTS_COMPLET = (
 # toujours intersecté avec le dico complet). On y a retiré les mots rares/peu
 # courants — dont le bingo CARTONS — pour reproduire fidèlement l'effet du
 # filtre : l'IA perd l'accès aux coups à fort score assis sur du vocabulaire
-# rare. Laisse tout de même 44 coups aux scores étalés (6 scores distincts).
+# rare. Les seuls mots de 2 lettres présents ici sont ceux qu'un joueur
+# ordinaire connaît (ON, OR, AS, AN, OS) ; les 2-lettres obscurs du Scrabble
+# (RA, OC, NA...) restent dans _MOTS_COMPLET uniquement — c'est précisément ce
+# que le vocabulaire humain écarte (issues #206/#207, #361).
 _MOTS_IA_RESTREINT = (
     "CARTON", "CARTE", "CARTES", "CANOT", "CAR", "CARS", "CAS", "SAC", "ACRE",
     "RAT", "RATS", "ART", "ARTS", "STAR", "CON", "CONS", "COR", "ROC", "TON",
     "TONS", "SORT", "TRAC", "OCA", "TAO", "SONAR", "SCORE",
+    "ON", "OR", "AS", "AN", "OS",
 )
 
 # Ordre des niveaux par score moyen croissant, tel qu'il découle RÉELLEMENT des
 # stratégies de sélection (cf. ia.py) :
-#   * DEBUTANT tire uniformément parmi TOUS les coups → moyenne la plus basse ;
+#   * DEBUTANT tire dans le top 85 % (n'écarte que les 15 % plus faibles)
+#     → moyenne la plus basse (issue #361) ;
 #   * FACILE tire dans le top 60 % (écarte les 40 % plus faibles) → au-dessus
 #     de DEBUTANT mais nettement sous INTERMEDIAIRE ;
 #   * INTERMEDIAIRE (top 33 %), AVANCE (top 15 %), EXPERT (meilleur) → croissant.
# ── Zone modifiée : ligne 538 (8 ligne(s)) dans l'ancienne version → ligne 549 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -538,8 +549,10 @@ _MOTS_IA_RESTREINT = (
 # plaçait sous DEBUTANT, contrairement à ce que suggèrent les noms) mais le
 # top 60 %. L'ordre réel coïncide désormais avec l'ordre des noms et avec
 # l'énoncé de l'issue #207 : « Débutant < Facile < Intermédiaire < Avancé <
-# Expert ». Cette monotonie est structurelle et vaut donc à l'identique avec et
-# sans le filtre de vocabulaire ; ces tests le vérifient empiriquement.
+# Expert ». Cette monotonie est structurelle — les tranches sont strictement
+# emboîtées (85 % ⊃ 60 % ⊃ 33 % ⊃ 15 % ⊃ meilleur) — et vaut donc à
+# l'identique avec et sans le filtre de vocabulaire ; ces tests le vérifient
+# empiriquement, y compris en présence de mots courts (hooks) depuis #361.
 _ORDRE_CROISSANT_ATTENDU = [
     Niveau.DEBUTANT,
     Niveau.FACILE,
