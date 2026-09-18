5ef6c89

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5ef6c89
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 13:56:57 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #401 : refonte niveaux IA — moteur ia.py (A/4)
    
    Nouveau mapping DEBUTANT/FACILE/INTERMEDIAIRE/AVANCE/EXPERT/CHAMPION_DU_MONDE
    issu de l'issue #400 : chaque niveau reprend la stratégie de sélection d'un
    ancien niveau plus fort (DEBUTANT fusionne top70% ex-Débutant+Facile, FACILE
    = ex-Intermédiaire top33%, INTERMEDIAIRE = ex-Avancé top15%, AVANCE =
    ex-Expert meilleur coup), EXPERT devient un nouveau niveau top5% sur ODS8
    complet, CHAMPION_DU_MONDE inchangé.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/moteur/ia.py b/src/scrabble/moteur/ia.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8e3db81..314a71d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/moteur/ia.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/moteur/ia.py
# ── Zone modifiée : ligne 5 (32 ligne(s)) dans l'ancienne version → ligne 5 (40 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,32 +5,40 @@ exhaustivement par :func:`scrabble.moteur.generateur.generer_coups`.
 La génération est identique quel que soit le niveau ; seule la stratégie
 de sélection dans la liste triée par score varie.
 
-Niveaux de difficulté
----------------------
-* **CHAMPION_DU_MONDE** : même stratégie de sélection qu'EXPERT (meilleur
-  coup) et même tranche de malus/bonus stratégiques. Ne se distingue
-  d'EXPERT que par le vocabulaire — câblé par l'appelant (issue #369, lot C)
-  via :func:`resoudre_palier` : EXPERT reçoit le Trie restreint du palier
-  ``"expert"`` (intersection Lexique), CHAMPION_DU_MONDE le Trie complet
-  (ODS8 sans filtre, ``obtenir_trie()``). Ce module lui-même reste agnostique
-  du dictionnaire reçu (voir « Ordre réel de force » ci-dessous).
-* **EXPERT** : choisit le meilleur coup (premier de la liste triée). En cas
-  d'égalité de score entre plusieurs coups de tête, choix aléatoire parmi eux.
-* **AVANCE** : choix aléatoire uniforme parmi les 15 % meilleurs coups (top
-  15 %). Plus fort qu'INTERMEDIAIRE (top 33 %) mais moins strict qu'EXPERT
-  (coup unique). Niveau intercalaire pour une progression plus fine (issue
-  #202).
-* **INTERMEDIAIRE** : choix aléatoire uniforme parmi le meilleur tiers des
-  coups (top 33 %). Favorise les bons coups sans être optimal.
-* **FACILE** : choix aléatoire uniforme parmi les 60 % meilleurs coups (top
-  60 %), c'est-à-dire en écartant les 40 % de coups les plus faibles. Reste
-  délibérément sous-optimal, mais réellement plus fort que DEBUTANT en score
-  moyen (issue #208, voir la note ci-dessous).
-* **DEBUTANT** : choix aléatoire uniforme parmi les 85 % meilleurs coups (top
-  85 %). N'écarte que les 15 % de coups les plus faibles au sens du score
-  stratégique (typiquement les hooks pénalisés par le malus longueur), ce qui
-  le laisse très proche d'un tirage au hasard tout en garantissant qu'il reste
-  le niveau le plus faible (issue #361).
+Niveaux de difficulté (refonte issue #401, sur la base de l'issue #400)
+-------------------------------------------------------------------------
+:class:`Niveau` garde ses six membres, dans le même ordre — seule la
+logique associée à chaque nom change. Chaque niveau reprend la stratégie
+de sélection d'un ancien niveau plus fort, ce qui resserre l'échelle vers
+le haut ; EXPERT devient un niveau à part entière, intercalé entre l'ancien
+AVANCE (désormais niveau AVANCE, meilleur coup) et CHAMPION_DU_MONDE :
+
+* **CHAMPION_DU_MONDE** : inchangé. Même stratégie de sélection qu'AVANCE
+  (meilleur coup) et même tranche de malus/bonus stratégiques. Ne se
+  distingue d'AVANCE que par le vocabulaire — câblé par l'appelant (issue
+  #369, lot C) via :func:`resoudre_palier` : AVANCE reçoit le Trie restreint
+  du palier ``"avance"``, CHAMPION_DU_MONDE le Trie complet (ODS8 sans
+  filtre, ``obtenir_trie()``). Ce module lui-même reste agnostique du
+  dictionnaire reçu (voir « Ordre réel de force » ci-dessous).
+* **EXPERT** : nouveau niveau (issue #401). Choix aléatoire uniforme parmi
+  les 5 % meilleurs coups (top 5 %, :func:`_choisir_top5`), sur le Trie
+  complet ODS8 — comme CHAMPION_DU_MONDE, EXPERT n'a pas de palier de
+  vocabulaire restreint (voir :func:`resoudre_palier`). Intercalaire entre
+  AVANCE (meilleur coup, vocabulaire restreint) et CHAMPION_DU_MONDE
+  (meilleur coup, vocabulaire complet).
+* **AVANCE** : choisit le meilleur coup (premier de la liste triée), sur le
+  palier de vocabulaire ``"avance"``. En cas d'égalité de score entre
+  plusieurs coups de tête, choix aléatoire parmi eux. Reprend la stratégie
+  de sélection de l'ancien EXPERT (issue #401).
+* **INTERMEDIAIRE** : choix aléatoire uniforme parmi les 15 % meilleurs
+  coups (top 15 %). Reprend la stratégie de sélection de l'ancien AVANCE
+  (issue #401).
+* **FACILE** : choix aléatoire uniforme parmi le meilleur tiers des coups
+  (top 33 %). Reprend la stratégie de sélection de l'ancien INTERMEDIAIRE
+  (issue #401).
+* **DEBUTANT** : choix aléatoire uniforme parmi les 70 % meilleurs coups
+  (top 70 %). Fusionne les anciens DEBUTANT (top 85 %) et FACILE (top 60 %)
+  en un seul niveau d'entrée de gamme (issue #401).
 
 Ordre réel de force (score moyen)
 ---------------------------------
# ── Zone modifiée : ligne 39 (40 ligne(s)) dans l'ancienne version → ligne 47 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -39,40 +47,34 @@ Les stratégies ci-dessus produisent, en moyenne, l'ordre croissant
 — cohérent avec l'ordre de la classe :class:`Niveau` et avec ce que
 suggèrent les noms des niveaux.
 
-Cette monotonie est STRUCTURELLE pour les cinq premiers niveaux : tous
+Cette monotonie est STRUCTURELLE pour les quatre premiers niveaux : tous
 passent par le même mécanisme (tri par score stratégique puis tirage
 uniforme dans une tranche haute), et les tranches sont strictement
-emboîtées — top 85 % (DEBUTANT) ⊃ top 60 % (FACILE) ⊃ top 33 %
-(INTERMEDIAIRE) ⊃ top 15 % (AVANCE) ⊃ meilleur coup (EXPERT). Chaque tranche
-étant un sous-ensemble strictement meilleur de la précédente, les scores
-moyens croissent mécaniquement avec le niveau, indépendamment du dictionnaire
+emboîtées — top 70 % (DEBUTANT) ⊃ top 33 % (FACILE) ⊃ top 15 %
+(INTERMEDIAIRE) ⊃ meilleur coup (AVANCE). Chaque tranche étant un
+sous-ensemble strictement meilleur de la précédente, les scores moyens
+croissent mécaniquement avec le niveau, indépendamment du dictionnaire
 employé. Aucun niveau n'a de filtre dur spécifique : l'issue #359 avait doté
-DEBUTANT d'un filtre sur la longueur (``nb_nouvelles >= 3``) qui le rendait
-plus sélectif que FACILE et cassait la monotonie ; l'issue #361 l'a remplacé
-par la tranche top 85 %.
-
-Le dernier maillon, EXPERT < CHAMPION_DU_MONDE, est de nature DIFFÉRENTE : ce
-n'est pas la stratégie de sélection qui les distingue (:func:`_choisir_expert`
-sert les deux identiquement), mais le vocabulaire reçu en paramètre — câblé
-par l'appelant (issue #369, lot C, voir :func:`resoudre_palier`) : EXPERT
-génère ses coups sur le Trie restreint du palier ``"expert"`` (intersection
-Lexique), CHAMPION_DU_MONDE sur le Trie complet ODS8. Le vocabulaire plus
-large de CHAMPION_DU_MONDE lui ouvre des coups inaccessibles à EXPERT, d'où
-l'inégalité stricte en moyenne. Contrairement aux cinq premiers niveaux, ce
-n'est donc PAS une propriété de ce module : à dictionnaire identique (par
-exemple si l'appelant transmettait le même Trie aux deux), les deux niveaux
-redeviennent mécaniquement égaux, comme le vérifie la fixture de test dédiée.
-
-Pourquoi « top 60 % » pour FACILE plutôt qu'une moitié/tranche centrale ? La
-distribution des scores est fortement asymétrique : quelques coups à très
-fort score (un « scrabble » vaut ~70 pts) tirent la MOYENNE d'un tirage large
-bien au-dessus de la médiane. Une tranche centrée sur la médiane resterait
-donc, en moyenne, SOUS DEBUTANT. Écarter les 40 % les plus faibles garantit
-au contraire ``FACILE > DEBUTANT`` (issue #208).
+l'ancien DEBUTANT d'un filtre sur la longueur (``nb_nouvelles >= 3``) qui le
+rendait plus sélectif que l'ancien FACILE et cassait la monotonie ; l'issue
+#361 l'a remplacé par une tranche haute, principe conservé ici.
+
+Les deux derniers maillons, AVANCE < EXPERT < CHAMPION_DU_MONDE, sont de
+nature DIFFÉRENTE : AVANCE et CHAMPION_DU_MONDE partagent la même stratégie
+de sélection (:func:`_choisir_avance`, meilleur coup) et ne se distinguent
+que par le vocabulaire — câblé par l'appelant (issue #369, lot C, voir
+:func:`resoudre_palier`). EXPERT, lui, change à la fois de stratégie (top
+5 % plutôt que meilleur coup) et de vocabulaire par rapport à AVANCE (Trie
+complet ODS8, comme CHAMPION_DU_MONDE) : ces deux facteurs jouent dans le
+même sens (top 5 % sur vocabulaire plus large ouvre en moyenne de meilleurs
+coups qu'un coup unique sur vocabulaire restreint), d'où l'inégalité
+attendue en moyenne. Contrairement aux quatre premiers niveaux, ce n'est
+donc PAS une propriété purement structurelle de ce module — voir la fixture
+de test dédiée pour la vérification empirique.
 
 Comportement de repli (listes courtes)
 --------------------------------------
-Si la tranche calculée (top 15 %, tiers, top 60 %, top 85 %) est vide, on
+Si la tranche calculée (top 5 %, top 15 %, tiers, top 70 %) est vide, on
 retombe sur la liste complète via ``max(1, ...)``. Cela évite tout crash sur
 des positions avec peu de coups jouables.
 Exemple : 2 coups disponibles, tiers = 0 → on choisit parmi les 2.
# ── Zone modifiée : ligne 131 (8 ligne(s)) dans l'ancienne version → ligne 133 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -131,8 +133,9 @@ class Niveau(Enum):
 # correspondance de test (``test_moteur_ia.py``) vérifie qu'elles restent en
 # phase.
 #
-# :data:`Niveau.CHAMPION_DU_MONDE` n'a volontairement aucune entrée : il ne se
-# résout vers aucun palier restreint mais vers le Trie complet
+# :data:`Niveau.EXPERT` et :data:`Niveau.CHAMPION_DU_MONDE` n'ont
+# volontairement aucune entrée (issue #401) : ils ne se résolvent vers aucun
+# palier restreint mais vers le Trie complet
 # (:func:`~scrabble.dictionnaire.dictionnaire.obtenir_trie`, ODS8 sans
 # filtre) — voir :func:`resoudre_palier`.
 _PALIERS_PAR_NIVEAU: dict[Niveau, str] = {
# ── Zone modifiée : ligne 140 (7 ligne(s)) dans l'ancienne version → ligne 143 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -140,7 +143,6 @@ _PALIERS_PAR_NIVEAU: dict[Niveau, str] = {
     Niveau.FACILE: "facile",
     Niveau.INTERMEDIAIRE: "intermediaire",
     Niveau.AVANCE: "avance",
-    Niveau.EXPERT: "expert",
 }
 
 
# ── Zone modifiée : ligne 148 (10 ligne(s)) dans l'ancienne version → ligne 150 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -148,10 +150,11 @@ def resoudre_palier(niveau: Niveau) -> str | None:
     """Résout un :class:`Niveau` vers sa clé de palier de vocabulaire IA.
 
     Renvoie la clé de palier (``"debutant"``, ``"facile"``… voir
-    :data:`_PALIERS_PAR_NIVEAU`) pour les cinq niveaux filtrés, et ``None``
-    pour :data:`Niveau.CHAMPION_DU_MONDE` : ce niveau n'est câblé sur aucun
-    fichier de vocabulaire restreint, l'appelant doit se rabattre sur le Trie
-    complet (``obtenir_trie()``) plutôt que sur ``obtenir_trie_ia(palier=...)``.
+    :data:`_PALIERS_PAR_NIVEAU`) pour les quatre niveaux filtrés, et ``None``
+    pour :data:`Niveau.EXPERT` et :data:`Niveau.CHAMPION_DU_MONDE` (issue
+    #401) : ces deux niveaux ne sont câblés sur aucun fichier de vocabulaire
+    restreint, l'appelant doit se rabattre sur le Trie complet
+    (``obtenir_trie()``) plutôt que sur ``obtenir_trie_ia(palier=...)``.
     """
     return _PALIERS_PAR_NIVEAU.get(niveau)
 
# ── Zone modifiée : ligne 160 (6 ligne(s)) dans l'ancienne version → ligne 163 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -160,6 +163,11 @@ def resoudre_palier(niveau: Niveau) -> str | None:
 #: (``nb_nouvelles <= 2``), doublé si une seule lettre est posée (« hook
 #: pur »). Croissant en valeur absolue avec le niveau : un niveau fort doit
 #: éviter les hooks encore plus nettement qu'un niveau faible (issue #359).
+#: Valeurs inchangées par la refonte de l'échelle (issue #401) : indexées
+#: par membre de :class:`Niveau` (ordre inchangé), elles restent monotones
+#: avec la force de chaque niveau indépendamment de la stratégie de
+#: sélection qui lui est associée. EXPERT (nouveau niveau) hérite donc des
+#: valeurs de l'ancien EXPERT (-25).
 _MALUS_LONGUEUR: dict[Niveau, int] = {
     Niveau.DEBUTANT: -5,
     Niveau.FACILE: -8,
# ── Zone modifiée : ligne 171 (7 ligne(s)) dans l'ancienne version → ligne 179 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -171,7 +179,9 @@ _MALUS_LONGUEUR: dict[Niveau, int] = {
 
 #: Bonus (positif) appliqué au score de tri d'un coup exploitant au moins
 #: une case premium (mot ou lettre compte double/triple). Croissant avec le
-#: niveau (issue #359).
+#: niveau (issue #359). Valeurs inchangées par la refonte de l'échelle
+#: (issue #401), pour la même raison que :data:`_MALUS_LONGUEUR` : EXPERT
+#: (nouveau niveau) hérite des valeurs de l'ancien EXPERT (20).
 _BONUS_PREMIUM: dict[Niveau, int] = {
     Niveau.DEBUTANT: 3,
     Niveau.FACILE: 5,
# ── Zone modifiée : ligne 236 (7 ligne(s)) dans l'ancienne version → ligne 246 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -236,7 +246,10 @@ _VOYELLES_LEAVE = frozenset("AEIOU")
 #: par niveau (issue #395). Nul pour DEBUTANT/FACILE : ces niveaux
 #: n'anticipent pas la qualité du reliquat, cohérent avec leur tirage très
 #: large. Croissant avec le niveau, plafonné à 1.0 (poids plein) à partir
-#: d'EXPERT.
+#: d'EXPERT. Valeurs inchangées par la refonte de l'échelle (issue #401),
+#: pour la même raison que :data:`_MALUS_LONGUEUR` : indexées par membre de
+#: :class:`Niveau` (ordre inchangé), elles restent monotones avec la force
+#: de chaque niveau.
 _POIDS_LEAVE: dict[Niveau, float] = {
     Niveau.DEBUTANT: 0.0,
     Niveau.FACILE: 0.0,
# ── Zone modifiée : ligne 368 (10 ligne(s)) dans l'ancienne version → ligne 381 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -368,10 +381,10 @@ def choisir_coup(
         reverse=True,
     )
 
-    if niveau in (Niveau.EXPERT, Niveau.CHAMPION_DU_MONDE):
-        return _choisir_expert(coups, rng)
-    if niveau == Niveau.AVANCE:
+    if niveau in (Niveau.AVANCE, Niveau.CHAMPION_DU_MONDE):
         return _choisir_avance(coups, rng)
+    if niveau == Niveau.EXPERT:
+        return _choisir_top5(coups, rng)
     if niveau == Niveau.INTERMEDIAIRE:
         return _choisir_intermediaire(coups, rng)
     if niveau == Niveau.FACILE:
# ── Zone modifiée : ligne 379 (62 ligne(s)) dans l'ancienne version → ligne 392 (69 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -379,62 +392,69 @@ def choisir_coup(
     return _choisir_debutant(coups, rng)
 
 
-def _choisir_expert(coups: list[CoupNote], rng: random.Random) -> Coup:
-    """EXPERT et CHAMPION_DU_MONDE : meilleur coup, aléatoire en cas d'égalité.
+def _choisir_avance(coups: list[CoupNote], rng: random.Random) -> Coup:
+    """AVANCE et CHAMPION_DU_MONDE : meilleur coup, aléatoire en cas d'égalité.
 
     Les deux niveaux partagent exactement la même stratégie de sélection et
     les mêmes tranches de malus/bonus (:data:`_MALUS_LONGUEUR`,
     :data:`_BONUS_PREMIUM`) : seul le vocabulaire reçu en paramètre les
     distingue, câblé par l'appelant (issue #369, lot C, voir
-    :func:`resoudre_palier`).
+    :func:`resoudre_palier`) — AVANCE sur le palier ``"avance"``,
+    CHAMPION_DU_MONDE sur le Trie complet ODS8. Reprend la stratégie de
+    l'ancien EXPERT (issue #401).
     """
     meilleur_score = coups[0].score
     meilleurs = [cn for cn in coups if cn.score == meilleur_score]
     return rng.choice(meilleurs).coup
 
 
-def _choisir_avance(coups: list[CoupNote], rng: random.Random) -> Coup:
-    """AVANCE : aléatoire parmi les 15 % meilleurs coups (top 15 %).
+def _choisir_top5(coups: list[CoupNote], rng: random.Random) -> Coup:
+    """EXPERT : aléatoire parmi les 5 % meilleurs coups (top 5 %).
 
-    Seuil intercalaire entre le top 33 % d'INTERMEDIAIRE et le coup unique
-    d'EXPERT. ``max(1, ...)`` garantit un sous-ensemble non vide (repli sur le
-    seul meilleur coup pour les listes très courtes), comme les autres niveaux.
+    Nouveau niveau (issue #401), intercalaire entre AVANCE (meilleur coup,
+    vocabulaire restreint) et CHAMPION_DU_MONDE (meilleur coup, vocabulaire
+    complet). Généré et joué sur le Trie complet ODS8 (pas de palier de
+    vocabulaire restreint, voir :func:`resoudre_palier`). ``max(1, ...)``
+    garantit un sous-ensemble non vide (repli sur le seul meilleur coup pour
+    les listes très courtes), comme les autres niveaux.
     """
-    taille_haut = max(1, len(coups) * 15 // 100)
+    taille_haut = max(1, len(coups) * 5 // 100)
     return rng.choice(coups[:taille_haut]).coup
 
 
 def _choisir_intermediaire(coups: list[CoupNote], rng: random.Random) -> Coup:
-    """INTERMEDIAIRE : aléatoire parmi le meilleur tiers (top 33 %)."""
-    taille_tiers = max(1, len(coups) // 3)
-    return rng.choice(coups[:taille_tiers]).coup
+    """INTERMEDIAIRE : aléatoire parmi les 15 % meilleurs coups (top 15 %).
+
+    Reprend la stratégie de sélection de l'ancien AVANCE (issue #401).
+    ``max(1, ...)`` garantit un sous-ensemble non vide (repli sur le seul
+    meilleur coup pour les listes très courtes), comme les autres niveaux.
+    """
+    taille_haut = max(1, len(coups) * 15 // 100)
+    return rng.choice(coups[:taille_haut]).coup
 
 
 def _choisir_facile(coups: list[CoupNote], rng: random.Random) -> Coup:
-    """FACILE : aléatoire parmi les 60 % meilleurs coups (top 60 %).
+    """FACILE : aléatoire parmi le meilleur tiers des coups (top 33 %).
 
-    Écarte les 40 % de coups les plus faibles, ce qui remonte le score moyen
-    au-dessus de DEBUTANT (qui tire parmi TOUS les coups) tout en restant
-    nettement sous INTERMEDIAIRE (top 33 %, sous-ensemble strictement meilleur).
+    Reprend la stratégie de sélection de l'ancien INTERMEDIAIRE (issue #401).
     ``max(1, ...)`` garantit un sous-ensemble non vide (repli sur le seul
-    meilleur coup pour les listes très courtes), comme les autres niveaux
-    (issue #208).
+    meilleur coup pour les listes très courtes), comme les autres niveaux.
     """
-    taille_haut = max(1, len(coups) * 60 // 100)
-    return rng.choice(coups[:taille_haut]).coup
+    taille_tiers = max(1, len(coups) // 3)
+    return rng.choice(coups[:taille_tiers]).coup
 
 
 def _choisir_debutant(coups: list[CoupNote], rng: random.Random) -> Coup:
-    """DEBUTANT : aléatoire parmi les 85 % meilleurs coups (top 85 %).
-
-    Tranche la plus large de tous les niveaux : seuls les 15 % de coups les
-    plus faibles au sens du score stratégique sont écartés (le malus longueur
-    y relègue les hooks les plus pauvres). C'est ce qui rend le tri
-    stratégique opérant pour DEBUTANT tout en le maintenant strictement sous
-    FACILE (top 60 %, sous-ensemble strictement meilleur) — issue #361, en
-    remplacement du filtre dur ``nb_nouvelles >= 3`` de l'issue #359 qui
-    cassait la monotonie des niveaux. ``max(1, ...)`` garantit un
-    sous-ensemble non vide, comme les autres niveaux.
+    """DEBUTANT : aléatoire parmi les 70 % meilleurs coups (top 70 %).
+
+    Fusionne les anciens DEBUTANT (top 85 %) et FACILE (top 60 %) en un seul
+    niveau d'entrée de gamme (issue #401) : seuls les 30 % de coups les plus
+    faibles au sens du score stratégique sont écartés (le malus longueur y
+    relègue les hooks les plus pauvres), ce qui laisse ce niveau très proche
+    d'un tirage au hasard tout en garantissant qu'il reste le niveau le plus
+    faible et strictement sous FACILE (top 33 %, sous-ensemble strictement
+    meilleur). ``max(1, ...)`` garantit un sous-ensemble non vide, comme les
+    autres niveaux.
     """
-    taille_haut = max(1, len(coups) * 85 // 100)
+    taille_haut = max(1, len(coups) * 70 // 100)
     return rng.choice(coups[:taille_haut]).coup
