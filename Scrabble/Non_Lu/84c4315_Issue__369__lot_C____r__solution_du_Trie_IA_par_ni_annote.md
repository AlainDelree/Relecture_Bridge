84c4315

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 84c4315
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Aug 5 18:28:00 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #369 (lot C) : résolution du Trie IA par niveau
    
    Fin du Trie IA unique de Partie (verrou structurel du rapport #366) :
    Partie.dictionnaires_ia est désormais un mapping {Niveau: Trie}, résolu
    via scrabble.moteur.ia.resoudre_palier(Niveau) -> palier|None (None pour
    CHAMPION_DU_MONDE, qui reste sur le Trie complet). ApiAccueil construit
    ce mapping en chargement paresseux (paliers réellement présents à la
    table, à la création comme à la reprise, celle-ci pilotée par les
    niveaux stockés via stockage.niveaux_ia_stockes). Un palier de
    vocabulaire absent est signalé indisponible (dictionnaire.paliers_disponibles,
    message dédié dès la sélection du niveau, reprise sans plantage) plutôt
    que remplacé silencieusement. La monotonie Expert < Champion du monde
    devient stricte (lot D la documentait comme égalité temporaire).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index cfcf68a..367c407 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (82 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,82 @@ Historique des changements notables, par ordre antéchronologique. Voir aussi
 
 ### Ajouté
 
+- **Issue #369** (lot C, suite de #366/#367/#368) — Résolution du Trie IA par
+  niveau : fin du Trie IA unique de `Partie` (verrou structurel identifié par
+  le rapport de lecture #366). `scrabble.moteur.ia.resoudre_palier(Niveau) ->
+  str | None` résout un niveau vers sa clé de palier (`FICHIERS_VOCABULAIRE_PALIER`),
+  `None` pour `CHAMPION_DU_MONDE` (Trie complet, pas de fichier) — placée côté
+  moteur pour respecter le sens unique des dépendances établi au lot A
+  (`dictionnaire.py` n'importe jamais le moteur ; le moteur peut décrire une
+  correspondance vers de simples clés `str` sans importer `dictionnaire.py`).
+  `Partie.dictionnaire_ia` (Trie unique) devient `Partie.dictionnaires_ia`
+  (mapping `{Niveau: Trie}`) ; `jouer_tour_ia` transmet à `ia.choisir_coup` le
+  Trie du **niveau du joueur courant**, avec repli sur `dictionnaire` complet
+  pour un niveau absent du mapping (mapping vide par défaut = comportement
+  historique inchangé, coût nul). `creer_partie`/`recreer_partie_meme_joueurs`
+  et `stockage.reprendre_partie` suivent (paramètre `dictionnaires_ia`) ;
+  nouvelle fonction `stockage.niveaux_ia_stockes(id_partie)` qui lit les
+  niveaux directement dans le blob JSON stocké, sans reconstruire la partie —
+  utilisée par `ApiAccueil.reprendre` pour que les Tries construits à la
+  reprise reflètent les niveaux **stockés**, pas la config courante de
+  l'accueil.
+  `ApiAccueil._construire_trie_ia` construit désormais le mapping des niveaux
+  réellement présents à la table (chargement paresseux : au plus 3 IA, donc au
+  plus 3 paliers chargés, jamais les six), à la création comme à la reprise ;
+  `FICHIERS_CACHE_IA_PALIER[palier]` sert de `chemin_cache` et `palier=palier`
+  est transmis à `obtenir_trie_ia` (chemin distinct **et** défense en
+  profondeur de l'en-tête, recommandation du lot B). `CHAMPION_DU_MONDE`
+  réutilise le Trie complet déjà construit par l'appelant plutôt que d'en
+  reconstruire un second. Le réglage « vocabulaire humain » (issue #206)
+  continue de tout piloter : désactivé, mapping vide, tous les niveaux sur
+  l'ODS8 complet (comportement historique inchangé) ; activé, un Trie par
+  palier.
+  Vocabulaire manquant (point 5) : nouvelle fonction
+  `dictionnaire.paliers_disponibles()` (détecte l'absence, contrairement à
+  `lire_liste_mots` qui la tolère silencieusement). `ApiAccueil.ajouter_ordinateur`
+  refuse désormais un niveau dont le palier est indisponible dès la sélection
+  (pas seulement au lancement), avec le message « <Niveau> en erreur, veuillez
+  choisir un autre niveau. Prévenir Alain pour la réparation. » ; nouvelle
+  méthode `ApiAccueil.obtenir_disponibilite_niveaux()` qui expose l'info pour
+  un futur bouton désactivé d'emblée (rendu visuel laissé au lot F). Pour une
+  partie **sauvegardée** dont le niveau est devenu indisponible, `reprendre()`
+  renvoie `{"succes": False, "erreur": ...}` (même message) au lieu de
+  planter — `ValueError` levée par `_construire_trie_ia` et rattrapée par le
+  `except Exception` déjà en place.
+  La monotonie `EXPERT < CHAMPION_DU_MONDE` devient **stricte** (le lot D la
+  documentait comme égalité temporaire, faute de vocabulaire distinct) :
+  `tests/test_moteur_ia.py` simule le câblage réel (Trie restreint pour
+  EXPERT, Trie complet pour CHAMPION_DU_MONDE) via un nouveau paramètre
+  `dico_champion` de `_moyennes_par_niveau` ; `_PAIRES_EGALITE_ATTENDUE` est
+  retirée (plus aucune paire d'égalité attendue) et les mentions « temporaire »
+  disparaissent des docstrings de `scrabble.moteur.ia`.
+  Mesures `tracemalloc` (que le rapport #366 n'avait pas pu obtenir, sur les
+  vraies données ODS8/Lexique présentes sur cette machine, hors dépôt) : Trie
+  complet ODS8 (411 430 mots) — 5,5 s de construction, **175,7 Mo** de pic
+  mémoire. Trie d'un palier restreint, construit depuis l'ensemble déjà filtré
+  — DEBUTANT (16 818 mots) 0,08 s / **6,9 Mo** ; FACILE (21 784) 0,14 s /
+  **8,8 Mo** ; INTERMEDIAIRE (32 737) 0,20 s / **12,9 Mo** ; AVANCE (45 335)
+  0,39 s / **17,4 Mo** ; EXPERT (112 121) 1,18 s / **41,1 Mo**. Une table à 3
+  IA (le pire cas, ex. Débutant + Facile + Expert) charge donc au plus
+  6,9 + 8,8 + 41,1 ≈ **57 Mo**, contre 175,7 Mo pour le seul Trie complet et
+  ≈263 Mo si les six paliers étaient chargés sans discrimination : le
+  chargement paresseux des paliers présents (point 3) est donc largement
+  justifié. Le coût dominant du **premier** appel (non caché) est le
+  rechargement/normalisation de l'ODS8 depuis disque (`charger_source`, non
+  mise en cache mémoire dans `construire_ensemble_ia`, ~4 s) plutôt que la
+  construction du Trie lui-même ; le cache disque par palier (lot B) absorbe
+  ce coût aux appels suivants (~0,26 s en lecture de cache, mesuré sur le
+  palier EXPERT). Le lot D reste correct à ce stade : le lot C ne l'a pas
+  invalidé.
+  Tests synthétiques uniquement (aucun ODS8/Lexique dans l'environnement
+  CCL) : résolution des six niveaux, deux IA de niveaux différents utilisant
+  deux Tries distincts (test central du lot), chargement paresseux limité aux
+  paliers présents, reprise pilotée par les niveaux stockés, vocabulaire
+  manquant signalé sans repli silencieux, monotonie stricte Expert/Champion.
+  Non touché (hors périmètre, volontairement) : le réglage `vocabulaire_humain`
+  lui-même (lot E) et le rendu visuel de l'écran d'accueil — 6ᵉ bouton,
+  dégradé CSS, bouton désactivé (lot F).
+
 - **Issue #368** (lot D, suite de #366) — Ajout de `Niveau.CHAMPION_DU_MONDE`
   au moteur IA (`scrabble.moteur.ia`), en fin d'énumération (rétro-compatible
   avec les parties existantes, sérialisées par `.name` dans `stockage.py`).
# (diff du fichier suivant)
diff --git a/src/scrabble/dictionnaire/dictionnaire.py b/src/scrabble/dictionnaire/dictionnaire.py
# (index — ignorable)
index e600d76..20dae9e 100644
# (avant — fichier suivant)
--- a/src/scrabble/dictionnaire/dictionnaire.py
# (après — fichier suivant)
+++ b/src/scrabble/dictionnaire/dictionnaire.py
# ── Zone modifiée : ligne 150 (6 ligne(s)) dans l'ancienne version → ligne 150 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -150,6 +150,30 @@ FICHIERS_CACHE_IA_PALIER: dict[str, Path] = {
     for palier in FICHIERS_VOCABULAIRE_PALIER
 }
 
+
+def paliers_disponibles(
+    fichiers: dict[str, Path] = FICHIERS_VOCABULAIRE_PALIER,
+) -> dict[str, bool]:
+    """Disponibilité de chaque palier de vocabulaire IA (issue #369, lot C).
+
+    Un palier est disponible si son fichier de vocabulaire existe sur disque.
+    Contrairement à :func:`lire_liste_mots` (qui tolère silencieusement un
+    fichier absent en renvoyant un ensemble vide), cette fonction sert à
+    **détecter** l'absence plutôt qu'à s'en accommoder : un palier absent doit
+    être signalé à l'utilisatrice (niveau désactivé), pas remplacé
+    silencieusement par un vocabulaire vide ou un autre palier.
+
+    Ne couvre pas le palier ``"champion_du_monde"`` (aucune entrée dans
+    :data:`FICHIERS_VOCABULAIRE_PALIER` : il se résout vers
+    :func:`obtenir_trie`, toujours disponible, sans fichier de vocabulaire).
+    L'appelant qui a besoin de la disponibilité de CHAMPION_DU_MONDE la
+    considère donc ``True`` par construction, en dehors de cette fonction.
+
+    ``fichiers`` par défaut :data:`FICHIERS_VOCABULAIRE_PALIER` ; un mapping
+    explicite reste accepté pour les tests.
+    """
+    return {palier: chemin.exists() for palier, chemin in fichiers.items()}
+
 # Belgicismes à revoir (issue #274) : CSV colonnes ``mot`` /
 # ``définition(s) belge(s)`` / ``origine_wallonne`` / ``existe_sens_standard``,
 # maintenu manuellement. Chargé uniquement quand le mode Belgicisme est actif
# (diff du fichier suivant)
diff --git a/src/scrabble/moteur/ia.py b/src/scrabble/moteur/ia.py
# (index — ignorable)
index 8d480b5..6154874 100644
# (avant — fichier suivant)
--- a/src/scrabble/moteur/ia.py
# (après — fichier suivant)
+++ b/src/scrabble/moteur/ia.py
# ── Zone modifiée : ligne 9 (10 ligne(s)) dans l'ancienne version → ligne 9 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,10 +9,11 @@ Niveaux de difficulté
 ---------------------
 * **CHAMPION_DU_MONDE** : même stratégie de sélection qu'EXPERT (meilleur
   coup) et même tranche de malus/bonus stratégiques. Ne se distingue
-  d'EXPERT que par le vocabulaire (ODS8 complet au lieu de l'intersection
-  Lexique), câblé par le lot C (issue #368, lot D) — tant que ce câblage
-  n'existe pas, CHAMPION_DU_MONDE se comporte à l'identique d'EXPERT, égalité
-  DOCUMENTÉE ET TEMPORAIRE (voir « Ordre réel de force » ci-dessous).
+  d'EXPERT que par le vocabulaire — câblé par l'appelant (issue #369, lot C)
+  via :func:`resoudre_palier` : EXPERT reçoit le Trie restreint du palier
+  ``"expert"`` (intersection Lexique), CHAMPION_DU_MONDE le Trie complet
+  (ODS8 sans filtre, ``obtenir_trie()``). Ce module lui-même reste agnostique
+  du dictionnaire reçu (voir « Ordre réel de force » ci-dessous).
 * **EXPERT** : choisit le meilleur coup (premier de la liste triée). En cas
   d'égalité de score entre plusieurs coups de tête, choix aléatoire parmi eux.
 * **AVANCE** : choix aléatoire uniforme parmi les 15 % meilleurs coups (top
# ── Zone modifiée : ligne 34 (32 ligne(s)) dans l'ancienne version → ligne 35 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -34,32 +35,34 @@ Niveaux de difficulté
 Ordre réel de force (score moyen)
 ---------------------------------
 Les stratégies ci-dessus produisent, en moyenne, l'ordre croissant
-``DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT <= CHAMPION_DU_MONDE``
+``DEBUTANT < FACILE < INTERMEDIAIRE < AVANCE < EXPERT < CHAMPION_DU_MONDE``
 — cohérent avec l'ordre de la classe :class:`Niveau` et avec ce que
 suggèrent les noms des niveaux.
 
-Cette monotonie est STRUCTURELLE : tous les niveaux passent par le même
-mécanisme (tri par score stratégique puis tirage uniforme dans une tranche
-haute), et les tranches sont strictement emboîtées — top 85 % (DEBUTANT) ⊃
-top 60 % (FACILE) ⊃ top 33 % (INTERMEDIAIRE) ⊃ top 15 % (AVANCE) ⊃ meilleur
-coup (EXPERT). Chaque tranche étant un sous-ensemble strictement meilleur de
-la précédente, les scores moyens croissent mécaniquement avec le niveau,
-indépendamment du dictionnaire employé (avec ou sans le filtre de
-« vocabulaire humain », issue #206/#207). Aucun niveau n'a de filtre dur
-spécifique : l'issue #359 avait doté DEBUTANT d'un filtre sur la longueur
-(``nb_nouvelles >= 3``) qui le rendait plus sélectif que FACILE et cassait la
-monotonie ; l'issue #361 l'a remplacé par la tranche top 85 %.
-
-Le dernier maillon, EXPERT <= CHAMPION_DU_MONDE, est une ÉGALITÉ et non une
-inégalité stricte : à ce stade (lot D de l'issue #368), CHAMPION_DU_MONDE
-n'est câblé sur aucun vocabulaire distinct d'EXPERT (le lot C s'en charge),
-et partage exactement la même stratégie et les mêmes tranches de malus/bonus.
-Les deux niveaux produisent donc, à graine égale, EXACTEMENT le même coup —
-l'égalité est mécanique, pas approximative. Cette égalité est TEMPORAIRE :
-une fois le lot C câblé (ODS8 complet pour CHAMPION_DU_MONDE contre
-l'intersection Lexique pour EXPERT), le vocabulaire plus large de
-CHAMPION_DU_MONDE lui ouvrira des coups inaccessibles à EXPERT et l'inégalité
-deviendra stricte.
+Cette monotonie est STRUCTURELLE pour les cinq premiers niveaux : tous
+passent par le même mécanisme (tri par score stratégique puis tirage
+uniforme dans une tranche haute), et les tranches sont strictement
+emboîtées — top 85 % (DEBUTANT) ⊃ top 60 % (FACILE) ⊃ top 33 %
+(INTERMEDIAIRE) ⊃ top 15 % (AVANCE) ⊃ meilleur coup (EXPERT). Chaque tranche
+étant un sous-ensemble strictement meilleur de la précédente, les scores
+moyens croissent mécaniquement avec le niveau, indépendamment du dictionnaire
+employé. Aucun niveau n'a de filtre dur spécifique : l'issue #359 avait doté
+DEBUTANT d'un filtre sur la longueur (``nb_nouvelles >= 3``) qui le rendait
+plus sélectif que FACILE et cassait la monotonie ; l'issue #361 l'a remplacé
+par la tranche top 85 %.
+
+Le dernier maillon, EXPERT < CHAMPION_DU_MONDE, est de nature DIFFÉRENTE : ce
+n'est pas la stratégie de sélection qui les distingue (:func:`_choisir_expert`
+sert les deux identiquement), mais le vocabulaire reçu en paramètre — câblé
+par l'appelant (issue #369, lot C, voir :func:`resoudre_palier`) : EXPERT
+génère ses coups sur le Trie restreint du palier ``"expert"`` (intersection
+Lexique), CHAMPION_DU_MONDE sur le Trie complet ODS8. Le vocabulaire plus
+large de CHAMPION_DU_MONDE lui ouvre des coups inaccessibles à EXPERT, d'où
+l'inégalité stricte en moyenne. Contrairement aux cinq premiers niveaux, ce
+n'est donc PAS une propriété de ce module : à dictionnaire identique (par
+exemple si l'appelant transmettait le même Trie aux deux, ou avec le
+vocabulaire humain désactivé — voir ``ui.accueil``), les deux niveaux
+redeviennent mécaniquement égaux, comme le vérifie la fixture de test dédiée.
 
 Pourquoi « top 60 % » pour FACILE plutôt qu'une moitié/tranche centrale ? La
 distribution des scores est fortement asymétrique : quelques coups à très
# ── Zone modifiée : ligne 112 (6 ligne(s)) dans l'ancienne version → ligne 115 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -112,6 +115,46 @@ class Niveau(Enum):
     CHAMPION_DU_MONDE = auto()
 
 
+# Résolution Niveau → clé de palier de vocabulaire IA (issue #369, lot C).
+#
+# Emplacement volontaire : ce module (``moteur.ia``) connaît :class:`Niveau`,
+# et les clés ci-dessous ne sont que des chaînes — aucune dépendance vers
+# ``scrabble.dictionnaire`` n'est introduite ici. C'est le sens inverse qui est
+# strictement interdit (choix du lot A, issue #366) : ``dictionnaire.py`` ne
+# doit jamais importer le moteur, pour rester utilisable sans lui. Le moteur,
+# lui, peut décrire une correspondance vers des clés de palier sans en
+# importer la définition : ces mêmes clés sont utilisées, côté appelant
+# (``scrabble.ui.accueil``, qui importe déjà les deux modules), pour indexer
+# :data:`scrabble.dictionnaire.dictionnaire.FICHIERS_VOCABULAIRE_PALIER` et
+# :data:`~scrabble.dictionnaire.dictionnaire.FICHIERS_CACHE_IA_PALIER` — une
+# correspondance de test (``test_moteur_ia.py``) vérifie qu'elles restent en
+# phase.
+#
+# :data:`Niveau.CHAMPION_DU_MONDE` n'a volontairement aucune entrée : il ne se
+# résout vers aucun palier restreint mais vers le Trie complet
+# (:func:`~scrabble.dictionnaire.dictionnaire.obtenir_trie`, ODS8 sans
+# filtre) — voir :func:`resoudre_palier`.
+_PALIERS_PAR_NIVEAU: dict[Niveau, str] = {
+    Niveau.DEBUTANT: "debutant",
+    Niveau.FACILE: "facile",
+    Niveau.INTERMEDIAIRE: "intermediaire",
+    Niveau.AVANCE: "avance",
+    Niveau.EXPERT: "expert",
+}
+
+
+def resoudre_palier(niveau: Niveau) -> str | None:
+    """Résout un :class:`Niveau` vers sa clé de palier de vocabulaire IA.
+
+    Renvoie la clé de palier (``"debutant"``, ``"facile"``… voir
+    :data:`_PALIERS_PAR_NIVEAU`) pour les cinq niveaux filtrés, et ``None``
+    pour :data:`Niveau.CHAMPION_DU_MONDE` : ce niveau n'est câblé sur aucun
+    fichier de vocabulaire restreint, l'appelant doit se rabattre sur le Trie
+    complet (``obtenir_trie()``) plutôt que sur ``obtenir_trie_ia(palier=...)``.
+    """
+    return _PALIERS_PAR_NIVEAU.get(niveau)
+
+
 #: Malus (négatif) appliqué au score de tri d'un coup posant peu de lettres
 #: (``nb_nouvelles <= 2``), doublé si une seule lettre est posée (« hook
 #: pur »). Croissant en valeur absolue avec le niveau : un niveau fort doit
# ── Zone modifiée : ligne 228 (9 ligne(s)) dans l'ancienne version → ligne 271 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -228,9 +271,11 @@ def choisir_coup(
 def _choisir_expert(coups: list[CoupNote], rng: random.Random) -> Coup:
     """EXPERT et CHAMPION_DU_MONDE : meilleur coup, aléatoire en cas d'égalité.
 
-    CHAMPION_DU_MONDE réutilise cette fonction tant que le lot C (issue #368)
-    n'a pas câblé son vocabulaire propre (ODS8 complet) : jusque-là, les deux
-    niveaux sont stratégiquement identiques.
+    Les deux niveaux partagent exactement la même stratégie de sélection et
+    les mêmes tranches de malus/bonus (:data:`_MALUS_LONGUEUR`,
+    :data:`_BONUS_PREMIUM`) : seul le vocabulaire reçu en paramètre les
+    distingue, câblé par l'appelant (issue #369, lot C, voir
+    :func:`resoudre_palier`).
     """
     meilleur_score = coups[0].score
     meilleurs = [cn for cn in coups if cn.score == meilleur_score]
# (diff du fichier suivant)
diff --git a/src/scrabble/moteur/partie.py b/src/scrabble/moteur/partie.py
# (index — ignorable)
index f36401e..647a4ff 100644
# (avant — fichier suivant)
--- a/src/scrabble/moteur/partie.py
# (après — fichier suivant)
+++ b/src/scrabble/moteur/partie.py
# ── Zone modifiée : ligne 164 (7 ligne(s)) dans l'ancienne version → ligne 164 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -164,7 +164,7 @@ def creer_partie(
     graine: int | None = None,
     tirage_ordre: bool = False,
     bonus_fin_partie: bool = False,
-    dictionnaire_ia: DictionnaireMots | None = None,
+    dictionnaires_ia: dict[Niveau, DictionnaireMots] | None = None,
 ) -> "Partie":
     """Construit une partie à partir d'une configuration humains/IA.
 
# ── Zone modifiée : ligne 192 (12 ligne(s)) dans l'ancienne version → ligne 192 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -192,12 +192,13 @@ def creer_partie(
     ``bonus_fin_partie`` (défaut ``False``) active le bonus officiel au finisseur
     (issue #134) ; l'appelant UI le renseigne depuis ``config.py``.
 
-    ``dictionnaire_ia`` (défaut ``None``) est le dictionnaire consulté par l'IA
-    pour **générer** ses coups (issue #206, réglage « vocabulaire humain ») :
-    ``None`` signifie « même dictionnaire que le joueur humain » (comportement
-    historique, zéro coût) ; un Trie restreint (mots courants ∪ classiques)
-    limite l'IA à ce vocabulaire. La validation d'un coup (humain **comme** IA)
-    reste toujours sur ``dictionnaire`` complet — voir :class:`Partie`.
+    ``dictionnaires_ia`` (défaut ``None``) associe à chaque :class:`Niveau`
+    présent le Trie consulté par l'IA pour **générer** ses coups (issue #206,
+    étendu par l'issue #369 lot C à un Trie propre par niveau — vocabulaire par
+    palier de fréquence). Un niveau absent du mapping (ou ``dictionnaires_ia``
+    entièrement ``None``) retombe sur ``dictionnaire`` complet (comportement
+    historique, zéro coût). La validation d'un coup (humain **comme** IA) reste
+    toujours sur ``dictionnaire`` complet — voir :class:`Partie`.
 
     :raises ValueError: si aucun humain, si ``nb_ia`` est négatif, ou si le
         total de joueurs sort de l'intervalle 1..:data:`MAX_JOUEURS`.
# ── Zone modifiée : ligne 230 (7 ligne(s)) dans l'ancienne version → ligne 231 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -230,7 +231,7 @@ def creer_partie(
         dictionnaire,
         graine=graine,
         bonus_fin_partie=bonus_fin_partie,
-        dictionnaire_ia=dictionnaire_ia,
+        dictionnaires_ia=dictionnaires_ia,
     )
 
 
# ── Zone modifiée : ligne 247 (9 ligne(s)) dans l'ancienne version → ligne 248 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -247,9 +248,10 @@ def recreer_partie_meme_joueurs(
     (**humain/ordinateur**) et, pour les IA, leur **niveau** de difficulté — et
     reconstruit une partie neuve via :func:`creer_partie`, sans rejouer l'écran
     de configuration. Le réglage ``bonus_fin_partie`` de la partie d'origine est
-    conservé, ainsi que son **vocabulaire d'IA** (issue #206) : si la partie
-    d'origine restreignait l'IA à un Trie distinct, ce même Trie est réutilisé ;
-    sinon (IA sur le dictionnaire complet) la nouvelle partie reste sur son
+    conservé, ainsi que son **vocabulaire d'IA** par niveau (issues #206, #369
+    lot C) : le mapping ``dictionnaires_ia`` de la partie d'origine est repris
+    tel quel (mêmes niveaux d'IA, donc mêmes clés utiles) ; s'il est vide (IA
+    sur le dictionnaire complet), la nouvelle partie reste sur son
     ``dictionnaire``.
 
     C'est le pivot de l'action « Recommencer » de la modale de fin de partie
# ── Zone modifiée : ligne 268 (15 ligne(s)) dans l'ancienne version → ligne 270 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -268,15 +270,10 @@ def recreer_partie_meme_joueurs(
     noms_humains = [j.nom for j in partie.joueurs if j.humain]
     noms_ia = [j.nom for j in partie.joueurs if not j.humain]
     niveaux_ia = [j.niveau for j in partie.joueurs if not j.humain]
-    # Vocabulaire humain (issue #206) : ne repropager que si l'IA d'origine était
-    # bien restreinte à un Trie distinct. Si elle jouait sur le dictionnaire
-    # complet (``dictionnaire_ia is dictionnaire``), on laisse ``None`` pour que
-    # la nouvelle partie retombe sur son propre ``dictionnaire``.
-    dictionnaire_ia = (
-        None
-        if partie.dictionnaire_ia is partie.dictionnaire
-        else partie.dictionnaire_ia
-    )
+    # Vocabulaire IA par niveau (issues #206, #369 lot C) : repropagé tel quel.
+    # Un mapping vide (IA sur le dictionnaire complet) reste vide côté nouvelle
+    # partie — pas besoin de le distinguer explicitement de ``None``, les deux
+    # produisent le même comportement de repli dans ``Partie.__init__``.
     return creer_partie(
         noms_humains=noms_humains,
         dictionnaire=dictionnaire,
# ── Zone modifiée : ligne 286 (7 ligne(s)) dans l'ancienne version → ligne 283 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -286,7 +283,7 @@ def recreer_partie_meme_joueurs(
         graine=graine,
         tirage_ordre=tirage_ordre,
         bonus_fin_partie=partie.bonus_fin_partie,
-        dictionnaire_ia=dictionnaire_ia,
+        dictionnaires_ia=partie.dictionnaires_ia,
     )
 
 
# ── Zone modifiée : ligne 304 (17 ligne(s)) dans l'ancienne version → ligne 301 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -304,17 +301,24 @@ class Partie:
     des actions, qui rend le déroulement d'une partie entièrement reproductible
     (base de la persistance, :mod:`scrabble.persistance.stockage`).
 
-    Deux dictionnaires (issue #206)
-    -------------------------------
+    Validation vs génération : un Trie par niveau d'IA (issues #206, #369 lot C)
+    ----------------------------------------------------------------------------
     ``dictionnaire`` (complet) sert **toujours** à la validation d'un coup
     (:func:`valider_coup`), qu'il soit joué par un humain ou par une IA : le
-    joueur humain n'est jamais restreint. ``dictionnaire_ia`` sert seulement à la
-    **génération** des coups de l'IA (:func:`scrabble.moteur.ia.choisir_coup`).
-    Par défaut (``dictionnaire_ia is None``), il est identique à ``dictionnaire``
-    (même objet, comportement historique strictement inchangé). Le réglage
-    « vocabulaire humain » y injecte un Trie restreint (mots courants ∪
-    classiques), qui élague l'espace de recherche de l'IA sans jamais élargir ni
-    restreindre ce que l'humain peut jouer ou vérifier.
+    joueur humain n'est jamais restreint, et un coup généré par une IA reste
+    soumis à cette même validation. ``dictionnaires_ia`` sert seulement à la
+    **génération** des coups de l'IA (:func:`scrabble.moteur.ia.choisir_coup`) :
+    c'est un mapping ``{Niveau: Trie}`` — plus un Trie unique partagé par toutes
+    les IA de la table (verrou structurel identifié par le rapport de lecture
+    #366, corrigé par le lot C) — puisque deux IA de niveaux différents peuvent
+    désormais jouer sur deux vocabulaires distincts (un palier de fréquence par
+    niveau, voir ``scrabble.moteur.ia.resoudre_palier``). Un niveau **absent**
+    du mapping (dont ``dictionnaires_ia`` vide ou ``None``, tout comme
+    :data:`~scrabble.moteur.ia.Niveau.CHAMPION_DU_MONDE` construit sans entrée)
+    retombe sur ``dictionnaire`` complet — comportement historique inchangé, y
+    compris quand le réglage « vocabulaire humain » (issue #206) est désactivé :
+    l'appelant UI transmet alors un mapping vide et toutes les IA jouent sur
+    l'ODS8 complet.
     """
 
     def __init__(
# ── Zone modifiée : ligne 325 (7 ligne(s)) dans l'ancienne version → ligne 329 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -325,7 +329,7 @@ class Partie:
         graine: int | None = None,
         sac: Sac | None = None,
         bonus_fin_partie: bool = False,
-        dictionnaire_ia: DictionnaireMots | None = None,
+        dictionnaires_ia: dict[Niveau, DictionnaireMots] | None = None,
     ) -> None:
         if not 1 <= len(joueurs) <= MAX_JOUEURS:
             raise ValueError(
# ── Zone modifiée : ligne 334 (12 ligne(s)) dans l'ancienne version → ligne 338 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -334,12 +338,13 @@ class Partie:
             )
         self.joueurs = joueurs
         self.dictionnaire = dictionnaire
-        # Dictionnaire de génération des coups de l'IA (issue #206). ``None`` →
-        # même objet que ``dictionnaire`` (aucun filtre, coût nul) ; un Trie
-        # restreint limite l'IA aux mots courants/classiques. La validation d'un
-        # coup reste toujours sur ``dictionnaire`` complet (humain comme IA).
-        self.dictionnaire_ia = (
-            dictionnaire if dictionnaire_ia is None else dictionnaire_ia
+        # Tries de génération des coups de l'IA, par niveau (issues #206, #369
+        # lot C). Copié défensivement pour ne jamais partager de mutation avec
+        # l'appelant. Un niveau absent (mapping vide par défaut) retombe sur
+        # ``dictionnaire`` complet dans ``jouer_tour_ia`` — aucun filtre, coût
+        # nul, comportement historique inchangé.
+        self.dictionnaires_ia: dict[Niveau, DictionnaireMots] = (
+            dict(dictionnaires_ia) if dictionnaires_ia else {}
         )
         self.graine = graine
         # Réglage câblé par l'appelant (issue #134) : bonus officiel au finisseur
# ── Zone modifiée : ligne 468 (7 ligne(s)) dans l'ancienne version → ligne 473 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -468,7 +473,11 @@ class Partie:
         """Joue le tour du joueur courant s'il est une IA.
 
         L'IA choisit un coup via :func:`scrabble.moteur.ia.choisir_coup` selon
-        son niveau de difficulté, ou passe si aucun coup n'est jouable.
+        son niveau de difficulté, ou passe si aucun coup n'est jouable. Le Trie
+        transmis à :func:`~scrabble.moteur.ia.choisir_coup` est celui du
+        **niveau du joueur courant** (:attr:`dictionnaires_ia`), pas un Trie
+        global partagé par toutes les IA de la table (issue #369, lot C) — un
+        niveau absent du mapping retombe sur ``dictionnaire`` complet.
 
         :raises ActionInvalide: si le joueur courant est humain, n'a pas de
             niveau défini, ou la partie est finie.
# ── Zone modifiée : ligne 483 (8 ligne(s)) dans l'ancienne version → ligne 492 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -483,8 +492,9 @@ class Partie:
             raise ActionInvalide(
                 f"Le joueur IA {joueur.nom!r} n'a pas de niveau défini."
             )
+        dictionnaire_ia = self.dictionnaires_ia.get(joueur.niveau, self.dictionnaire)
         coup = ia.choisir_coup(
-            self.plateau, joueur.chevalet, self.dictionnaire_ia, joueur.niveau
+            self.plateau, joueur.chevalet, dictionnaire_ia, joueur.niveau
         )
         if coup is None:
             return self.passer()
# (diff du fichier suivant)
diff --git a/src/scrabble/persistance/stockage.py b/src/scrabble/persistance/stockage.py
# (index — ignorable)
index ee8de0e..27e7e6a 100644
# (avant — fichier suivant)
--- a/src/scrabble/persistance/stockage.py
# (après — fichier suivant)
+++ b/src/scrabble/persistance/stockage.py
# ── Zone modifiée : ligne 506 (12 ligne(s)) dans l'ancienne version → ligne 506 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -506,12 +506,42 @@ def lister_parties(chemin: _TypeChemin = CHEMIN_DEFAUT) -> list[ResumePartie]:
     return resumes
 
 
+def niveaux_ia_stockes(
+    id_partie: int, chemin: _TypeChemin = CHEMIN_DEFAUT
+) -> list[Niveau]:
+    """Niveaux des IA de la partie stockée ``id_partie``, sans la reconstruire.
+
+    Lit directement la configuration JSON des joueurs (colonne
+    ``parties.joueurs``), sans rejouer les actions ni instancier de
+    :class:`Partie`. Sert à l'appelant (``ui.accueil.ApiAccueil.reprendre``,
+    issue #369 lot C) à savoir quels paliers de vocabulaire IA charger
+    **avant** d'appeler :func:`reprendre_partie` : les niveaux d'une partie
+    reprise doivent venir de la partie **stockée**, pas de la configuration
+    courante de l'accueil (une IA « Expert » restée en base doit continuer à
+    jouer Expert même si l'accueil affiche autre chose entre-temps).
+
+    :raises KeyError: si aucune partie ne porte cet identifiant.
+    """
+    with _connexion(chemin) as connexion:
+        ligne = connexion.execute(
+            "SELECT joueurs FROM parties WHERE id = ?", (id_partie,)
+        ).fetchone()
+    if ligne is None:
+        raise KeyError(f"Aucune partie d'identifiant {id_partie}.")
+    configs = _joueurs_depuis_json(ligne["joueurs"])
+    return [
+        Niveau[donnees["niveau"]]
+        for donnees in configs
+        if donnees.get("niveau") is not None
+    ]
+
+
 def reprendre_partie(
     id_partie: int,
     dictionnaire: DictionnaireMots,
     chemin: _TypeChemin = CHEMIN_DEFAUT,
     *,
-    dictionnaire_ia: DictionnaireMots | None = None,
+    dictionnaires_ia: dict[Niveau, DictionnaireMots] | None = None,
 ) -> Partie:
     """Reconstruit la :class:`Partie` ``id_partie`` en rejouant ses actions.
 
# ── Zone modifiée : ligne 525 (12 ligne(s)) dans l'ancienne version → ligne 555 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -525,12 +555,15 @@ def reprendre_partie(
     ``dictionnaire`` doit être le même (ou en contenir les mots) que celui de la
     partie d'origine, sans quoi le rejeu d'un coup échouerait à la validation.
 
-    ``dictionnaire_ia`` (issue #206, réglage « vocabulaire humain ») est
-    transmis tel quel à la :class:`Partie` reconstruite pour que l'IA d'une
-    partie **reprise** continue de jouer dans son vocabulaire restreint. ``None``
-    (défaut) = IA sur le dictionnaire complet. Le rejeu des actions passe
-    toujours par ``valider_coup`` sur ``dictionnaire`` complet : il n'est donc
-    pas affecté par ce paramètre.
+    ``dictionnaires_ia`` (issues #206, #369 lot C) associe à chaque
+    :class:`~scrabble.moteur.ia.Niveau` présent son Trie restreint, transmis tel
+    quel à la :class:`Partie` reconstruite pour que chaque IA d'une partie
+    **reprise** continue de jouer dans son vocabulaire propre. ``None`` (défaut)
+    = toutes les IA sur le dictionnaire complet. Voir :func:`niveaux_ia_stockes`
+    pour connaître, avant l'appel, les niveaux à couvrir dans ce mapping (les
+    niveaux viennent de la partie stockée, pas de la config courante). Le rejeu
+    des actions passe toujours par ``valider_coup`` sur ``dictionnaire``
+    complet : il n'est donc pas affecté par ce paramètre.
 
     :raises KeyError: si aucune partie ne porte cet identifiant.
     """
# ── Zone modifiée : ligne 551 (7 ligne(s)) dans l'ancienne version → ligne 584 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -551,7 +584,7 @@ def reprendre_partie(
         joueurs,
         dictionnaire,
         graine=ligne["graine"],
-        dictionnaire_ia=dictionnaire_ia,
+        dictionnaires_ia=dictionnaires_ia,
     )
 
     for action in actions:
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/accueil.py b/src/scrabble/ui/accueil.py
# (index — ignorable)
index 175e5a0..b93e51f 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/accueil.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/accueil.py
# ── Zone modifiée : ligne 54 (20 ligne(s)) dans l'ancienne version → ligne 54 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -54,20 +54,24 @@ from scrabble.config import (
     charger_config,
 )
 from scrabble.dictionnaire.dictionnaire import (
+    FICHIERS_CACHE_IA_PALIER,
+    FICHIERS_VOCABULAIRE_PALIER,
     SOURCES,
     marquer_classique,
     modifier_appartenance,
     obtenir_trie,
     obtenir_trie_ia,
+    paliers_disponibles,
     rechercher_statut,
 )
-from scrabble.moteur.ia import Niveau
+from scrabble.moteur.ia import Niveau, resoudre_palier
 from scrabble.moteur.partie import MAX_JOUEURS, Partie, creer_partie
 from scrabble.persistance.stockage import (
     CHEMIN_DEFAUT,
     ResumePartie,
     demarrer_suivi,
     lister_parties,
+    niveaux_ia_stockes,
     reprendre_partie,
 )
 from scrabble.reglages import lire_reglage, modifier_reglage
# ── Zone modifiée : ligne 91 (6 ligne(s)) dans l'ancienne version → ligne 95 (43 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -91,6 +95,43 @@ NIVEAUX_LABELS: dict[str, Niveau] = {
     "Avancé": Niveau.AVANCE,
     "Expert": Niveau.EXPERT,
 }
+# CHAMPION_DU_MONDE (issue #368, lot D) est volontairement absent : le 6e
+# bouton de l'accueil relève du lot F (issue #369, point 7 — hors périmètre
+# de ce lot), qui touchera aussi ``NIVEAUX_LABELS``.
+
+# Libellé français d'un Niveau, inverse de NIVEAUX_LABELS (pour les messages).
+_LIBELLES_NIVEAUX: dict[Niveau, str] = {
+    niveau: label for label, niveau in NIVEAUX_LABELS.items()
+}
+
+
+def _disponibilite_niveau(niveau: Niveau) -> tuple[bool, str | None]:
+    """Disponibilité du vocabulaire IA d'un niveau (issue #369, lot C, point 5).
+
+    Réglage « vocabulaire humain » (issue #206) désactivé (défaut) → toujours
+    disponible : tous les niveaux jouent alors sur l'ODS8 complet (point 7 de
+    l'issue #369), le fichier de vocabulaire d'un palier n'entre donc jamais
+    en jeu et ne doit pas bloquer la sélection d'un niveau. Activé → un
+    niveau est indisponible quand son palier (:func:`resoudre_palier`) est
+    connu mais que le fichier de vocabulaire correspondant est absent du
+    disque (:func:`~scrabble.dictionnaire.dictionnaire.paliers_disponibles`).
+    :data:`~scrabble.moteur.ia.Niveau.CHAMPION_DU_MONDE` (palier ``None``) ne
+    dépend d'aucun fichier : toujours disponible, réglage ou pas.
+
+    Renvoie ``(True, None)`` si disponible, ``(False, message)`` sinon, où
+    ``message`` reprend le libellé retenu par l'issue : « <Niveau> en erreur,
+    veuillez choisir un autre niveau. Prévenir Alain pour la réparation. ».
+    """
+    if not bool(charger_config().get("vocabulaire_humain", False)):
+        return True, None
+    palier = resoudre_palier(niveau)
+    if palier is None or paliers_disponibles().get(palier, False):
+        return True, None
+    label = _LIBELLES_NIVEAUX.get(niveau, niveau.name)
+    return False, (
+        f"{label} en erreur, veuillez choisir un autre niveau. "
+        "Prévenir Alain pour la réparation."
+    )
 
 # Libellés français des valeurs à choix fini pour le panneau Réglages intégré
 # à l'accueil (issue #169, ex-fenêtre autonome ``ui/reglages.py``). Les clés
# ── Zone modifiée : ligne 414 (8 ligne(s)) dans l'ancienne version → ligne 455 (33 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -414,8 +455,33 @@ class ApiAccueil:
         journal.info(f"Accueil : joueur humain ajouté ({nom}).")
         return {"succes": True, "etat": self.obtenir_etat()}
 
+    def obtenir_disponibilite_niveaux(self) -> list[dict[str, Any]]:
+        """Disponibilité de chaque niveau de difficulté (issue #369, lot C).
+
+        Renvoie, pour chaque label de :data:`NIVEAUX_LABELS`, ``{"label",
+        "disponible", "message"}`` — ``message`` étant ``None`` quand
+        ``disponible`` est vrai. Sert de base à un futur bouton désactivé
+        d'emblée à l'accueil (« le contrôle doit se faire à l'affichage de
+        l'accueil, pas au lancement », issue #369 point 5) : ce lot expose
+        l'information côté Python, le rendu visuel (bouton grisé, tooltip)
+        relevant du lot F.
+        """
+        resultat = []
+        for label, niveau in NIVEAUX_LABELS.items():
+            disponible, message = _disponibilite_niveau(niveau)
+            resultat.append(
+                {"label": label, "disponible": disponible, "message": message}
+            )
+        return resultat
+
     def ajouter_ordinateur(self, niveau_label: str) -> dict[str, Any]:
-        """Ajoute un ordinateur avec le niveau donné (label français)."""
+        """Ajoute un ordinateur avec le niveau donné (label français).
+
+        Refuse un niveau dont le vocabulaire IA est indisponible (issue #369,
+        point 5, défense en profondeur : le bouton correspondant doit déjà
+        être désactivé à l'accueil, lot F) avec le message dédié
+        (:func:`_disponibilite_niveau`).
+        """
         if not self.config_partie.peut_ajouter_ordinateur():
             return {
                 "succes": False,
# ── Zone modifiée : ligne 424 (6 ligne(s)) dans l'ancienne version → ligne 490 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -424,6 +490,9 @@ class ApiAccueil:
         niveau = NIVEAUX_LABELS.get(niveau_label)
         if niveau is None:
             return {"succes": False, "erreur": f"Niveau inconnu : {niveau_label}"}
+        disponible, message = _disponibilite_niveau(niveau)
+        if not disponible:
+            return {"succes": False, "erreur": message}
         noms_pris = self.config_partie.noms_utilises()
         try:
             prenoms = tirer_prenoms(1, noms_pris)
# ── Zone modifiée : ligne 463 (28 ligne(s)) dans l'ancienne version → ligne 532 (91 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -463,28 +532,91 @@ class ApiAccueil:
         }
 
     @staticmethod
-    def _construire_trie_ia(source: str, mode_belgicisme: bool = False) -> Any:
-        """Trie restreint de l'IA si « vocabulaire humain » est actif, sinon ``None``.
-
-        Réglage global unique (issue #206), indépendant du niveau de difficulté :
-        désactivé (défaut) → ``None`` (l'IA joue sur le dictionnaire complet,
-        comportement historique inchangé, coût nul). Activé → Trie restreint
-        (:func:`~scrabble.dictionnaire.dictionnaire.obtenir_trie_ia`) construit sur
-        la **même** ``source`` que le Trie complet du jeu.
+    def _construire_trie_ia(
+        source: str,
+        niveaux: list[Niveau],
+        mode_belgicisme: bool = False,
+        trie_complet: Any | None = None,
+    ) -> dict[Niveau, Any]:
+        """Mapping ``{Niveau: Trie}`` pour les niveaux présents (issue #369, lot C).
+
+        Fin du Trie IA unique (rapport de lecture #366) : une partie avec un
+        Débutant et un Expert a besoin de deux Tries distincts. Cette méthode
+        construit le mapping consommé par ``Partie.dictionnaires_ia``,
+        appelée aussi bien à la création (:meth:`lancer_partie`) qu'à la
+        reprise (:meth:`reprendre`) — ``niveaux`` en est le seul point de
+        variation (config courante vs niveaux **stockés**, voir
+        :func:`~scrabble.persistance.stockage.niveaux_ia_stockes`).
+
+        Réglage global « vocabulaire humain » (issue #206), toujours
+        indépendant du niveau de difficulté : désactivé (défaut) → mapping
+        **vide** ; chaque IA retombe alors sur le dictionnaire complet dans
+        ``Partie`` (comportement historique inchangé, coût nul — voir le
+        docstring de ``Partie`` pour ce repli). Activé → un Trie par niveau
+        **présent uniquement** (chargement paresseux, point 3 de l'issue) :
+        au plus 3 IA à une table, donc au plus 3 paliers chargés, jamais les
+        six — le rapport #366 chiffre un Trie complet à plusieurs dizaines de
+        Mo, et les mesures du lot C (voir CHANGELOG) confirment l'écart.
+
+        Chaque niveau se résout vers un palier via
+        :func:`~scrabble.moteur.ia.resoudre_palier` :
+
+        * un palier connu (5 premiers niveaux) → Trie restreint
+          (:func:`~scrabble.dictionnaire.dictionnaire.obtenir_trie_ia`), avec
+          le chemin de vocabulaire et le chemin de cache propres à ce palier
+          (:data:`~scrabble.dictionnaire.dictionnaire.FICHIERS_VOCABULAIRE_PALIER`,
+          :data:`~scrabble.dictionnaire.dictionnaire.FICHIERS_CACHE_IA_PALIER`)
+          et ``palier=palier`` passé à ``obtenir_trie_ia`` — chemin distinct
+          **et** défense en profondeur de l'en-tête, recommandation explicite
+          du lot B ;
+        * ``None`` (CHAMPION_DU_MONDE) → Trie complet
+          (:func:`~scrabble.dictionnaire.dictionnaire.obtenir_trie`), en
+          réutilisant ``trie_complet`` s'il est déjà construit par l'appelant
+          (le Trie de validation de la partie, jamais reconstruit deux fois)
+          plutôt que d'en reconstruire un second.
+
+        Vocabulaire manquant (issue #369, point 5) : si le fichier de
+        vocabulaire d'un palier **requis** (présent dans ``niveaux``) est
+        absent, ``ValueError`` est levée avec le message retenu par l'issue
+        (:func:`_disponibilite_niveau`) plutôt que de rabattre silencieusement
+        ce niveau sur un autre vocabulaire. Le contrôle préventif (empêcher la
+        sélection d'un niveau indisponible) a lieu en amont, à l'affichage de
+        l'accueil (:meth:`ajouter_ordinateur`,
+        :meth:`obtenir_disponibilite_niveaux`) : cette exception ne devrait
+        donc se déclencher qu'à la reprise d'une partie **sauvegardée** dont
+        le niveau est devenu indisponible depuis — ``lancer_partie`` comme
+        ``reprendre`` l'attrapent déjà via leur ``except Exception`` existant
+        et renvoient ``{"succes": False, "erreur": ...}`` au JS, qui revient à
+        l'accueil sans planter.
 
         La source est transmise **en paramètre** par l'appelant (issue #210) —
-        exactement la valeur passée à ``obtenir_trie(source)`` — plutôt que relue
-        ici via un second ``charger_config()`` qui pourrait en théorie diverger.
-        On garantit ainsi que le vocabulaire de l'IA reste un sous-ensemble strict
-        du dictionnaire de validation effectivement utilisé pour la partie.
-
-        ``mode_belgicisme`` (issue #274, défaut ``False``) est transmis de la
-        même façon, pour la même raison : il doit correspondre exactement au
-        mode utilisé pour le Trie complet de la partie.
+        exactement la valeur passée à ``obtenir_trie(source)`` — plutôt que
+        relue ici via un second ``charger_config()`` qui pourrait en théorie
+        diverger. ``mode_belgicisme`` (issue #274) suit la même logique.
         """
         if not bool(charger_config().get("vocabulaire_humain", False)):
-            return None
-        return obtenir_trie_ia(source, mode_belgicisme=mode_belgicisme)
+            return {}
+        resultat: dict[Niveau, Any] = {}
+        for niveau in dict.fromkeys(niveaux):  # dédoublonne, ordre préservé
+            palier = resoudre_palier(niveau)
+            if palier is None:
+                resultat[niveau] = (
+                    trie_complet
+                    if trie_complet is not None
+                    else obtenir_trie(source, mode_belgicisme=mode_belgicisme)
+                )
+                continue
+            disponible, message = _disponibilite_niveau(niveau)
+            if not disponible:
+                raise ValueError(message)
+            resultat[niveau] = obtenir_trie_ia(
+                source,
+                chemin_mots_courants=FICHIERS_VOCABULAIRE_PALIER[palier],
+                chemin_cache=FICHIERS_CACHE_IA_PALIER[palier],
+                mode_belgicisme=mode_belgicisme,
+                palier=palier,
+            )
+        return resultat
 
     def lancer_partie(self) -> dict[str, Any]:
         """Crée et démarre la partie avec la configuration actuelle.
# ── Zone modifiée : ligne 545 (10 ligne(s)) dans l'ancienne version → ligne 677 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -545,10 +677,12 @@ class ApiAccueil:
             # Réglage du bonus officiel au finisseur (issue #134), câblé dans le
             # moteur via creer_partie.
             bonus_fin_partie = bool(config.get("bonus_fin_partie", False))
-            # Réglage « vocabulaire humain » (issue #206) : Trie restreint de l'IA,
-            # construit sur la même source et le même mode que le Trie complet
-            # (issues #210, #274).
-            trie_ia = self._construire_trie_ia(source, mode_belgicisme)
+            # Réglage « vocabulaire humain » (issue #206) : un Trie par niveau
+            # d'IA présent (issue #369, lot C), construit sur la même source et
+            # le même mode que le Trie complet (issues #210, #274).
+            tries_ia = self._construire_trie_ia(
+                source, niveaux_ia, mode_belgicisme, trie_complet=trie
+            )
             self._partie = creer_partie(
                 noms_humains=noms_humains,
                 dictionnaire=trie,
# ── Zone modifiée : ligne 558 (7 ligne(s)) dans l'ancienne version → ligne 692 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -558,7 +692,7 @@ class ApiAccueil:
                 graine=graine,
                 tirage_ordre=True,
                 bonus_fin_partie=bonus_fin_partie,
-                dictionnaire_ia=trie_ia,
+                dictionnaires_ia=tries_ia,
             )
             self._id_partie = demarrer_suivi(
                 self._partie, mode_belgicisme=self.config_partie.mode_belgicisme
# ── Zone modifiée : ligne 655 (6 ligne(s)) dans l'ancienne version → ligne 789 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -655,6 +789,16 @@ class ApiAccueil:
         En cas de succès, le champ ``pret`` vaut ``True`` : le JS doit alors
         fermer la fenêtre d'accueil (``api.fermer_fenetre()``) pour que l'écran
         de jeu puisse s'ouvrir avec la partie reprise.
+
+        Les niveaux d'IA utilisés pour construire les Tries (issue #369, lot C)
+        viennent de la partie **stockée** (:func:`~scrabble.persistance.stockage.
+        niveaux_ia_stockes`), pas de la configuration courante de l'accueil —
+        comportement voulu : une IA « Expert » sauvegardée reste Expert à la
+        reprise, quel que soit l'état de ``config_partie`` entre-temps. Si un
+        niveau stocké est devenu indisponible (fichier de vocabulaire manquant),
+        ``_construire_trie_ia`` lève ``ValueError`` (message dédié), rattrapée
+        ci-dessous par le ``except Exception`` général : retour à l'accueil avec
+        message d'erreur, sans planter (issue #369, point 5).
         """
         try:
             # Source du dictionnaire choisie dans les réglages (issue #210) :
# ── Zone modifiée : ligne 664 (10 ligne(s)) dans l'ancienne version → ligne 808 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -664,10 +808,14 @@ class ApiAccueil:
             trie = obtenir_trie(source)
             # Réglage « vocabulaire humain » (issue #206) : une partie reprise doit
             # continuer de restreindre son IA si le réglage est actif — sur la même
-            # source que le Trie complet (issue #210).
-            trie_ia = self._construire_trie_ia(source)
+            # source que le Trie complet (issue #210), et niveau par niveau
+            # (issue #369, lot C) selon les niveaux **stockés**.
+            niveaux_stockes = niveaux_ia_stockes(id_partie)
+            tries_ia = self._construire_trie_ia(
+                source, niveaux_stockes, trie_complet=trie
+            )
             self._partie = reprendre_partie(
-                id_partie, trie, dictionnaire_ia=trie_ia
+                id_partie, trie, dictionnaires_ia=tries_ia
             )
             self._id_partie = id_partie
             # Reprise = pas de tirage d'ordre à rejouer : on efface tout
# (diff du fichier suivant)
diff --git a/tests/test_accueil.py b/tests/test_accueil.py
# (index — ignorable)
index 5dc4919..7e45b87 100644
# (avant — fichier suivant)
--- a/tests/test_accueil.py
# (après — fichier suivant)
+++ b/tests/test_accueil.py
# ── Zone modifiée : ligne 296 (6 ligne(s)) dans l'ancienne version → ligne 296 (153 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -296,6 +296,153 @@ class TestNiveauxLabels:
         assert NIVEAUX_LABELS["Expert"] == Niveau.EXPERT
 
 
+class TestDisponibiliteNiveaux:
+    """Signalement d'un niveau indisponible (issue #369, lot C, point 5).
+
+    Le vocabulaire manquant d'un palier doit être SIGNALÉ, pas silencieusement
+    remplacé — et le contrôle a lieu à l'affichage de l'accueil (sélection
+    refusée), pas seulement au lancement.
+    """
+
+    def test_obtenir_disponibilite_niveaux_tous_disponibles_par_defaut(
+        self, monkeypatch
+    ):
+        """Réglage désactivé (défaut) : tous les niveaux sont disponibles.
+
+        Comportement retenu quand « vocabulaire humain » est désactivé (issue
+        #369, point 7) : tous les niveaux jouent sur l'ODS8 complet, aucun
+        fichier de palier n'entre en jeu, donc aucun niveau n'est bloqué.
+        """
+        from scrabble.ui.accueil import ApiAccueil
+
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": False}
+        )
+        api = ApiAccueil()
+        disponibilites = api.obtenir_disponibilite_niveaux()
+
+        assert len(disponibilites) == len(NIVEAUX_LABELS)
+        assert all(d["disponible"] for d in disponibilites)
+        assert all(d["message"] is None for d in disponibilites)
+
+    def test_obtenir_disponibilite_niveaux_signale_le_palier_manquant(
+        self, monkeypatch
+    ):
+        """Réglage actif : un palier absent est signalé indisponible, avec message."""
+        from scrabble.ui.accueil import ApiAccueil
+
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.paliers_disponibles",
+            lambda: {
+                "debutant": False,
+                "facile": True,
+                "intermediaire": True,
+                "avance": True,
+                "expert": True,
+            },
+        )
+        api = ApiAccueil()
+        disponibilites = {
+            d["label"]: d for d in api.obtenir_disponibilite_niveaux()
+        }
+
+        assert disponibilites["Débutant"]["disponible"] is False
+        assert disponibilites["Débutant"]["message"] == (
+            "Débutant en erreur, veuillez choisir un autre niveau. "
+            "Prévenir Alain pour la réparation."
+        )
+        assert disponibilites["Facile"]["disponible"] is True
+        assert disponibilites["Facile"]["message"] is None
+
+    def test_ajouter_ordinateur_refuse_un_niveau_indisponible(self, monkeypatch):
+        """Le contrôle a lieu dès la sélection, pas seulement au lancement.
+
+        Béatrice ne doit pas cliquer, attendre, puis échouer : le message est
+        renvoyé immédiatement par ``ajouter_ordinateur``, avant toute création
+        de partie.
+        """
+        from scrabble.ui.accueil import ApiAccueil
+
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.paliers_disponibles", lambda: {"debutant": False}
+        )
+        api = ApiAccueil()
+
+        result = api.ajouter_ordinateur("Débutant")
+
+        assert result["succes"] is False
+        assert result["erreur"] == (
+            "Débutant en erreur, veuillez choisir un autre niveau. "
+            "Prévenir Alain pour la réparation."
+        )
+        assert api.config_partie.nb_ordinateurs == 0
+
+    def test_ajouter_ordinateur_accepte_les_autres_niveaux(self, monkeypatch):
+        """Un niveau dont le palier est indisponible n'affecte pas les autres."""
+        from scrabble.ui.accueil import ApiAccueil
+
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.paliers_disponibles",
+            lambda: {"debutant": False, "expert": True},
+        )
+        api = ApiAccueil()
+
+        result = api.ajouter_ordinateur("Expert")
+
+        assert result["succes"] is True
+        assert api.config_partie.nb_ordinateurs == 1
+
+    def test_champion_du_monde_toujours_disponible(self):
+        """CHAMPION_DU_MONDE ne dépend d'aucun fichier : toujours disponible."""
+        from scrabble.ui.accueil import _disponibilite_niveau
+
+        disponible, message = _disponibilite_niveau(Niveau.CHAMPION_DU_MONDE)
+        assert disponible is True
+        assert message is None
+
+    def test_reprise_avec_niveau_stocke_devenu_indisponible_ne_plante_pas(
+        self, monkeypatch
+    ):
+        """Reprise d'une partie sauvegardée dont le niveau est devenu indisponible.
+
+        Doit renvoyer une erreur exploitable par le JS (retour à l'accueil),
+        pas planter (issue #369, point 5).
+        """
+        from scrabble.dictionnaire.dictionnaire import Trie
+        from scrabble.ui.accueil import ApiAccueil
+
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.obtenir_trie",
+            lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.niveaux_ia_stockes",
+            lambda id_partie: [Niveau.EXPERT],
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.paliers_disponibles", lambda: {"expert": False}
+        )
+
+        api = ApiAccueil()
+        result = api.reprendre(99)
+
+        assert result["succes"] is False
+        assert "Expert en erreur" in result["erreur"]
+        assert api._partie is None
+
+
 class TestExclusionPrenoms:
     """Tests de l'exclusion des prénoms déjà utilisés."""
 
# ── Zone modifiée : ligne 371 (9 ligne(s)) dans l'ancienne version → ligne 518 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -371,9 +518,12 @@ class TestApiAccueilLancement:
             "scrabble.ui.accueil.obtenir_trie",
             lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.niveaux_ia_stockes", lambda id_partie: []
+        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.reprendre_partie",
-            lambda id_partie, trie, dictionnaire_ia=None: partie_reprise,
+            lambda id_partie, trie, dictionnaires_ia=None: partie_reprise,
         )
 
         api = ApiAccueil()
# ── Zone modifiée : ligne 406 (9 ligne(s)) dans l'ancienne version → ligne 556 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -406,9 +556,12 @@ class TestApiAccueilLancement:
             "scrabble.ui.accueil.obtenir_trie",
             lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.niveaux_ia_stockes", lambda id_partie: []
+        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.reprendre_partie",
-            lambda id_partie, trie, dictionnaire_ia=None: partie_reprise,
+            lambda id_partie, trie, dictionnaires_ia=None: partie_reprise,
         )
 
         api = ApiAccueil()
# ── Zone modifiée : ligne 522 (9 ligne(s)) dans l'ancienne version → ligne 675 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -522,9 +675,12 @@ class TestSourceDictionnaireAppliquee:
             lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.niveaux_ia_stockes", lambda id_partie: []
+        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.reprendre_partie",
-            lambda id_partie, trie, dictionnaire_ia=None: partie_reprise,
+            lambda id_partie, trie, dictionnaires_ia=None: partie_reprise,
         )
 
         api = ApiAccueil()
# ── Zone modifiée : ligne 555 (7 ligne(s)) dans l'ancienne version → ligne 711 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -555,7 +711,12 @@ class TestSourceDictionnaireAppliquee:
         assert appels == ["ods"]
 
     def test_construire_trie_ia_utilise_source_transmise(self, monkeypatch):
-        """_construire_trie_ia(source) transmet cette même source à obtenir_trie_ia."""
+        """_construire_trie_ia(source, niveaux) transmet la source à obtenir_trie_ia.
+
+        Vérifie aussi (issue #369, lot C) que le mapping renvoyé indexe le Trie
+        obtenu par le niveau demandé.
+        """
+        from scrabble.moteur.ia import Niveau
         from scrabble.ui.accueil import ApiAccueil
         from scrabble.dictionnaire.dictionnaire import Trie
 
# ── Zone modifiée : ligne 564 (18 ligne(s)) dans l'ancienne version → ligne 725 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -564,18 +725,22 @@ class TestSourceDictionnaireAppliquee:
             "scrabble.ui.accueil.charger_config",
             lambda: {"vocabulaire_humain": True},
         )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.paliers_disponibles", lambda: {"expert": True}
+        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie_ia",
             lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
 
-        trie_ia = ApiAccueil._construire_trie_ia("hunspell")
-        assert trie_ia is not None
+        tries_ia = ApiAccueil._construire_trie_ia("hunspell", [Niveau.EXPERT])
+        assert Niveau.EXPERT in tries_ia
         assert appels == ["hunspell"]
 
-    def test_construire_trie_ia_none_si_vocabulaire_inactif(self, monkeypatch):
-        """_construire_trie_ia renvoie None (et n'appelle pas obtenir_trie_ia) si inactif."""
+    def test_construire_trie_ia_vide_si_vocabulaire_inactif(self, monkeypatch):
+        """_construire_trie_ia renvoie {} (et n'appelle pas obtenir_trie_ia) si inactif."""
+        from scrabble.moteur.ia import Niveau
         from scrabble.ui.accueil import ApiAccueil
 
         appels: list[str] = []
# ── Zone modifiée : ligne 588 (9 ligne(s)) dans l'ancienne version → ligne 753 (97 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -588,9 +753,97 @@ class TestSourceDictionnaireAppliquee:
             lambda source="ods", **_: appels.append(source),
         )
 
-        assert ApiAccueil._construire_trie_ia("hunspell") is None
+        assert ApiAccueil._construire_trie_ia("hunspell", [Niveau.EXPERT]) == {}
         assert appels == []
 
+    def test_construire_trie_ia_champion_du_monde_reutilise_trie_complet(
+        self, monkeypatch
+    ):
+        """CHAMPION_DU_MONDE reçoit le Trie complet, sans appeler obtenir_trie_ia.
+
+        Réutilise ``trie_complet`` (le Trie de validation déjà construit par
+        l'appelant) plutôt que d'en reconstruire un second (issue #369, lot C).
+        """
+        from scrabble.moteur.ia import Niveau
+        from scrabble.ui.accueil import ApiAccueil
+        from scrabble.dictionnaire.dictionnaire import Trie
+
+        appels_ia: list[str] = []
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config",
+            lambda: {"vocabulaire_humain": True},
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.obtenir_trie_ia",
+            lambda source="ods", **_: appels_ia.append(source),
+        )
+        trie_complet = Trie.depuis_iterable(["TEST"])
+
+        tries_ia = ApiAccueil._construire_trie_ia(
+            "ods", [Niveau.CHAMPION_DU_MONDE], trie_complet=trie_complet
+        )
+
+        assert tries_ia == {Niveau.CHAMPION_DU_MONDE: trie_complet}
+        assert appels_ia == []  # jamais de palier restreint pour ce niveau
+
+    def test_construire_trie_ia_charge_uniquement_les_paliers_presents(
+        self, monkeypatch
+    ):
+        """Chargement paresseux (issue #369, point 3) : seuls les paliers PRÉSENTS.
+
+        Une table avec Débutant + Expert (2 IA) ne doit construire que 2
+        paliers, jamais les cinq — le rapport #366 chiffre un Trie complet à
+        plusieurs dizaines de Mo, inutile de charger un palier absent de la
+        table.
+        """
+        from scrabble.moteur.ia import Niveau
+        from scrabble.ui.accueil import ApiAccueil
+        from scrabble.dictionnaire.dictionnaire import Trie
+
+        appels: list[str] = []
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config",
+            lambda: {"vocabulaire_humain": True},
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.paliers_disponibles",
+            lambda: {p: True for p in ("debutant", "facile", "intermediaire", "avance", "expert")},
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.obtenir_trie_ia",
+            lambda source="ods", palier=None, **_: appels.append(palier)
+            or Trie.depuis_iterable(["TEST"]),
+        )
+
+        tries_ia = ApiAccueil._construire_trie_ia(
+            "ods", [Niveau.DEBUTANT, Niveau.EXPERT]
+        )
+
+        assert set(tries_ia) == {Niveau.DEBUTANT, Niveau.EXPERT}
+        assert set(appels) == {"debutant", "expert"}  # jamais facile/intermediaire/avance
+
+    def test_construire_trie_ia_niveau_indisponible_leve(self, monkeypatch):
+        """Un palier requis mais indisponible lève ValueError (issue #369, point 5).
+
+        Filet de sécurité : la sélection est censée être bloquée en amont à
+        l'accueil (:meth:`~scrabble.ui.accueil.ApiAccueil.ajouter_ordinateur`),
+        mais une partie sauvegardée peut redemander un niveau devenu
+        indisponible depuis (ex. reprise).
+        """
+        from scrabble.moteur.ia import Niveau
+        from scrabble.ui.accueil import ApiAccueil
+
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.charger_config",
+            lambda: {"vocabulaire_humain": True},
+        )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.paliers_disponibles", lambda: {"expert": False}
+        )
+
+        with pytest.raises(ValueError, match="Expert en erreur"):
+            ApiAccueil._construire_trie_ia("ods", [Niveau.EXPERT])
+
     def test_lancer_partie_hunspell_valide_mot_hunspell_rejette_ods(
         self, monkeypatch
     ):
# (diff du fichier suivant)
diff --git a/tests/test_dictionnaire.py b/tests/test_dictionnaire.py
# (index — ignorable)
index 4018a57..2e03a14 100644
# (avant — fichier suivant)
--- a/tests/test_dictionnaire.py
# (après — fichier suivant)
+++ b/tests/test_dictionnaire.py
# ── Zone modifiée : ligne 46 (6 ligne(s)) dans l'ancienne version → ligne 46 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -46,6 +46,7 @@ from scrabble.dictionnaire.dictionnaire import (
     normaliser_mot,
     obtenir_trie,
     obtenir_trie_ia,
+    paliers_disponibles,
     rechercher_statut,
     statut_classique,
     statut_source,
# ── Zone modifiée : ligne 102 (6 ligne(s)) dans l'ancienne version → ligne 103 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -102,6 +103,42 @@ def test_fichiers_cache_ia_palier_meme_cles_que_vocabulaire_et_chemins_distincts
     assert len(noms) == 5  # aucun doublon de nom de fichier entre paliers
 
 
+# --------------------------------------------------------------------------- #
+# Disponibilité des paliers de vocabulaire IA (issue #369, lot C)
+# --------------------------------------------------------------------------- #
+
+def test_paliers_disponibles_tous_presents(tmp_path):
+    """Un palier dont le fichier de vocabulaire existe est disponible."""
+    chemin_a = tmp_path / "mots_courants_a.txt"
+    chemin_b = tmp_path / "mots_courants_b.txt"
+    chemin_a.write_text("CHAT\n", encoding="utf-8")
+    chemin_b.write_text("CHIEN\n", encoding="utf-8")
+    assert paliers_disponibles({"a": chemin_a, "b": chemin_b}) == {
+        "a": True,
+        "b": True,
+    }
+
+
+def test_paliers_disponibles_signale_le_fichier_manquant(tmp_path):
+    """Un palier dont le fichier est absent est signalé indisponible, pas ignoré.
+
+    Contrairement à :func:`lire_liste_mots` (fichier absent toléré → ensemble
+    vide, silencieux), cette fonction sert justement à DÉTECTER l'absence — le
+    point 5 de l'issue #369 exige un signalement, pas un repli silencieux.
+    """
+    chemin_present = tmp_path / "mots_courants_present.txt"
+    chemin_present.write_text("CHAT\n", encoding="utf-8")
+    chemin_absent = tmp_path / "mots_courants_absent.txt"
+    assert paliers_disponibles(
+        {"present": chemin_present, "absent": chemin_absent}
+    ) == {"present": True, "absent": False}
+
+
+def test_paliers_disponibles_defaut_utilise_fichiers_vocabulaire_palier():
+    """Sans argument, porte sur les cinq vrais paliers de production."""
+    assert set(paliers_disponibles()) == set(FICHIERS_VOCABULAIRE_PALIER)
+
+
 # --------------------------------------------------------------------------- #
 # Normalisation
 # --------------------------------------------------------------------------- #
# (diff du fichier suivant)
diff --git a/tests/test_journal_integration.py b/tests/test_journal_integration.py
# (index — ignorable)
index 6543b7e..d59ce2e 100644
# (avant — fichier suivant)
--- a/tests/test_journal_integration.py
# (après — fichier suivant)
+++ b/tests/test_journal_integration.py
# ── Zone modifiée : ligne 156 (9 ligne(s)) dans l'ancienne version → ligne 156 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -156,9 +156,12 @@ class TestJournalAccueil:
             "scrabble.ui.accueil.obtenir_trie",
             lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.niveaux_ia_stockes", lambda id_partie: []
+        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.reprendre_partie",
-            lambda id_partie, trie, dictionnaire_ia=None: partie,
+            lambda id_partie, trie, dictionnaires_ia=None: partie,
         )
         api = ApiAccueil()
         res = api.reprendre(99)
# ── Zone modifiée : ligne 171 (8 ligne(s)) dans l'ancienne version → ligne 174 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -171,8 +174,11 @@ class TestJournalAccueil:
             "scrabble.ui.accueil.obtenir_trie",
             lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
+        monkeypatch.setattr(
+            "scrabble.ui.accueil.niveaux_ia_stockes", lambda id_partie: []
+        )
 
-        def _absente(id_partie, trie, dictionnaire_ia=None):
+        def _absente(id_partie, trie, dictionnaires_ia=None):
             raise KeyError(id_partie)
 
         monkeypatch.setattr("scrabble.ui.accueil.reprendre_partie", _absente)
# (diff du fichier suivant)
diff --git a/tests/test_moteur_ia.py b/tests/test_moteur_ia.py
# (index — ignorable)
index 4ab9e4c..a304f8f 100644
# (avant — fichier suivant)
--- a/tests/test_moteur_ia.py
# (après — fichier suivant)
+++ b/tests/test_moteur_ia.py
# ── Zone modifiée : ligne 5 (10 ligne(s)) dans l'ancienne version → ligne 5 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,10 +5,18 @@ FACILE, DEBUTANT) sur la base du générateur exhaustif, la reproductibilité
 avec graine fixée, les cas limites (un seul coup, aucun coup), et
 l'intégration avec Partie/creer_partie.
 
-CHAMPION_DU_MONDE (issue #368, lot D) n'est pas encore câblé sur un
-vocabulaire distinct d'EXPERT (lot C à venir) : les deux niveaux sont
-stratégiquement identiques ici, d'où l'égalité (et non l'inégalité stricte)
-dans les tests de monotonie ci-dessous.
+CHAMPION_DU_MONDE et EXPERT partagent EXACTEMENT la même stratégie de
+sélection (:func:`~scrabble.moteur.ia._choisir_expert`) : à dictionnaire
+identique, les deux niveaux restent mécaniquement égaux — c'est ce que
+vérifient la plupart des tests ci-dessous, qui appellent
+``choisir_coup(..., dico, niveau, ...)`` avec un seul ``dico`` partagé. Ce
+qui les distingue en jeu réel est le vocabulaire reçu en paramètre, câblé par
+l'appelant (issue #369, lot C, voir ``scrabble.moteur.ia.resoudre_palier`` et
+``scrabble.ui.accueil``) : EXPERT sur le Trie restreint du palier
+``"expert"``, CHAMPION_DU_MONDE sur le Trie complet. Les tests de monotonie
+de ``TestProgressionTrieIaRestreint`` simulent ce câblage en donnant
+explicitement un dictionnaire plus large à CHAMPION_DU_MONDE
+(``dico_champion``), pour vérifier l'inégalité stricte qui en résulte.
 """
 
 from __future__ import annotations
# ── Zone modifiée : ligne 18 (9 ligne(s)) dans l'ancienne version → ligne 26 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -18,9 +26,9 @@ import statistics
 
 import pytest
 
-from scrabble.dictionnaire.dictionnaire import Trie
+from scrabble.dictionnaire.dictionnaire import FICHIERS_VOCABULAIRE_PALIER, Trie
 from scrabble.moteur.generateur import CoupNote, generer_coups
-from scrabble.moteur.ia import Niveau, _score_strategique, choisir_coup
+from scrabble.moteur.ia import Niveau, _score_strategique, choisir_coup, resoudre_palier
 from scrabble.moteur.partie import (
     ACTION_COUP,
     ACTION_PASSE,
# ── Zone modifiée : ligne 49 (6 ligne(s)) dans l'ancienne version → ligne 57 (53 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -49,6 +57,53 @@ def _coup_cadre_au_centre() -> Coup:
     return Coup(ligne, colonne, Direction.HORIZONTALE, tuiles_depuis_chaine("CADRE"))
 
 
+# --------------------------------------------------------------------------- #
+# Résolution Niveau → palier de vocabulaire IA (issue #369, lot C)
+# --------------------------------------------------------------------------- #
+
+class TestResoudrePalier:
+    """Résolution :class:`Niveau` → clé de palier (:func:`resoudre_palier`)."""
+
+    @pytest.mark.parametrize(
+        "niveau, palier_attendu",
+        [
+            (Niveau.DEBUTANT, "debutant"),
+            (Niveau.FACILE, "facile"),
+            (Niveau.INTERMEDIAIRE, "intermediaire"),
+            (Niveau.AVANCE, "avance"),
+            (Niveau.EXPERT, "expert"),
+        ],
+    )
+    def test_cinq_premiers_niveaux_resolvent_vers_leur_palier(
+        self, niveau, palier_attendu
+    ):
+        assert resoudre_palier(niveau) == palier_attendu
+
+    def test_champion_du_monde_ne_resout_vers_aucun_palier(self):
+        """CHAMPION_DU_MONDE n'a pas de palier : Trie complet, pas de fichier."""
+        assert resoudre_palier(Niveau.CHAMPION_DU_MONDE) is None
+
+    def test_tous_les_niveaux_sont_couverts(self):
+        """Chaque membre de Niveau reçoit une résolution (palier ou None)."""
+        for niveau in Niveau:
+            resoudre_palier(niveau)  # ne doit jamais lever
+
+    def test_paliers_resolus_correspondent_aux_cles_du_vocabulaire_ia(self):
+        """Les clés produites sont exactement celles de FICHIERS_VOCABULAIRE_PALIER.
+
+        Vérifie la correspondance entre ce module (qui ne connaît que des
+        chaînes, sans importer ``scrabble.dictionnaire``, issue #369) et les
+        clés réelles utilisées côté dictionnaire — la cohérence dépend de la
+        discipline documentée, pas d'un import partagé.
+        """
+        paliers_resolus = {
+            resoudre_palier(niveau)
+            for niveau in Niveau
+            if resoudre_palier(niveau) is not None
+        }
+        assert paliers_resolus == set(FICHIERS_VOCABULAIRE_PALIER)
+
+
 # --------------------------------------------------------------------------- #
 # Score stratégique (issue #359) : pénalité hooks / bonus cases premium
 # --------------------------------------------------------------------------- #
# ── Zone modifiée : ligne 573 (10 ligne(s)) dans l'ancienne version → ligne 628 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -573,10 +628,11 @@ _MOTS_IA_RESTREINT = (
 #     de DEBUTANT mais nettement sous INTERMEDIAIRE ;
 #   * INTERMEDIAIRE (top 33 %), AVANCE (top 15 %), EXPERT (meilleur) → croissant.
 #   * CHAMPION_DU_MONDE réutilise EXACTEMENT la stratégie et les tranches
-#     d'EXPERT tant que le lot C (issue #368) n'a pas câblé son vocabulaire
-#     propre : à graine égale, les deux niveaux choisissent le même coup, donc
-#     leurs scores moyens sont ÉGAUX (pas strictement croissants) — dernier
-#     maillon documenté comme TEMPORAIRE dans la docstring du module.
+#     d'EXPERT (:func:`~scrabble.moteur.ia._choisir_expert` sert les deux
+#     identiquement) : ce qui les distingue est le vocabulaire reçu en
+#     paramètre, câblé par l'appelant (issue #369, lot C) — EXPERT sur le
+#     Trie restreint du palier, CHAMPION_DU_MONDE sur le Trie complet. Les
+#     tests ci-dessous simulent ce câblage via ``dico_champion``.
 # NB : depuis l'issue #208, FACILE n'est plus la moitié INFÉRIEURE (ce qui le
 # plaçait sous DEBUTANT, contrairement à ce que suggèrent les noms) mais le
 # top 60 %. L'ordre réel coïncide désormais avec l'ordre des noms et avec
# ── Zone modifiée : ligne 594 (34 ligne(s)) dans l'ancienne version → ligne 650 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -594,34 +650,51 @@ _ORDRE_CROISSANT_ATTENDU = [
     Niveau.CHAMPION_DU_MONDE,
 ]
 
-#: Paires consécutives de :data:`_ORDRE_CROISSANT_ATTENDU` dont l'ordre est
-#: une ÉGALITÉ attendue (et non une inégalité stricte). Seule la paire
-#: EXPERT/CHAMPION_DU_MONDE l'est, tant que le lot C n'a pas câblé un
-#: vocabulaire propre à CHAMPION_DU_MONDE (issue #368, lot D).
-_PAIRES_EGALITE_ATTENDUE = {(Niveau.EXPERT, Niveau.CHAMPION_DU_MONDE)}
-
 
 def _moyennes_par_niveau(
     plateau: PlateauPartie,
     chevalet: list[str],
     dico: Trie,
     n: int = 400,
+    dico_champion: Trie | None = None,
 ) -> dict[Niveau, float]:
     """Score moyen de chaque niveau sur ``n`` tirages à graines 0..n-1.
 
     Même méthode que les tests statistiques existants : on génère la liste de
-    référence des coups une fois (sur ``dico``, donc restreinte si ``dico`` est
-    le Trie IA), puis on relève le score du coup choisi pour chaque graine. Le
-    score d'un coup ne dépend que des tuiles/plateau, pas du dictionnaire.
+    référence des coups une fois par dictionnaire utilisé, puis on relève le
+    score du coup choisi pour chaque graine. Le score d'un coup ne dépend que
+    des tuiles/plateau, pas du dictionnaire.
+
+    ``dico_champion`` (issue #369, lot C), s'il est fourni, est le
+    dictionnaire utilisé pour :data:`Niveau.CHAMPION_DU_MONDE` à la place de
+    ``dico`` — simule le câblage réel (``scrabble.ui.accueil``), où
+    CHAMPION_DU_MONDE joue sur le Trie complet quand les autres niveaux jouent
+    sur un palier restreint. ``None`` (défaut) : CHAMPION_DU_MONDE partage
+    ``dico`` avec les autres niveaux, comme avant l'issue #369.
     """
     coups_ref = generer_coups(plateau, chevalet, dico)
+    coups_ref_champion = (
+        coups_ref
+        if dico_champion is None
+        else generer_coups(plateau, chevalet, dico_champion)
+    )
     moyennes: dict[Niveau, float] = {}
     for niveau in Niveau:
+        dico_niveau = (
+            dico_champion
+            if niveau is Niveau.CHAMPION_DU_MONDE and dico_champion is not None
+            else dico
+        )
+        reference = (
+            coups_ref_champion if dico_niveau is dico_champion else coups_ref
+        )
         scores = []
         for graine in range(n):
-            coup = choisir_coup(plateau, chevalet, dico, niveau, random.Random(graine))
+            coup = choisir_coup(
+                plateau, chevalet, dico_niveau, niveau, random.Random(graine)
+            )
             if coup is not None:
-                cn = next(c for c in coups_ref if c.coup == coup)
+                cn = next(c for c in reference if c.coup == coup)
                 scores.append(cn.score)
         moyennes[niveau] = statistics.mean(scores) if scores else 0.0
     return moyennes
# ── Zone modifiée : ligne 645 (45 ligne(s)) dans l'ancienne version → ligne 718 (45 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -645,45 +718,45 @@ class TestProgressionTrieIaRestreint:
         assert len({cn.score for cn in coups_ia}) >= 3
 
     def test_progression_monotone_avec_filtre_actif(self):
-        """La progression reste monotone (au sens large) avec le Trie IA restreint.
-
-        Confirme l'hypothèse du rapport #203 : le filtre étant global, la
-        monotonie des scores moyens est préservée une fois le filtre actif.
-        Croissance stricte partout, SAUF sur la paire EXPERT/CHAMPION_DU_MONDE
-        (égalité attendue et temporaire, cf. docstring du module — issue #368,
-        lot D : CHAMPION_DU_MONDE ne sera câblé sur son propre vocabulaire
-        qu'au lot C).
+        """La progression reste STRICTEMENT monotone avec le Trie IA restreint.
+
+        Confirme l'hypothèse du rapport #203 : le filtre étant appliqué
+        uniformément aux cinq premiers niveaux, la monotonie des scores moyens
+        est préservée. Le dernier maillon EXPERT < CHAMPION_DU_MONDE est
+        désormais lui aussi strict (issue #369, lot C) : on simule ici le
+        câblage réel en donnant à CHAMPION_DU_MONDE le Trie complet
+        (``dico_champion``) pendant qu'EXPERT reste sur le Trie restreint —
+        le bingo CARTONS (70 pts, absent de ``_MOTS_IA_RESTREINT``) n'est
+        alors accessible qu'à CHAMPION_DU_MONDE.
         """
         dico_ia = Trie.depuis_iterable(_MOTS_IA_RESTREINT)
-        moy = _moyennes_par_niveau(self.plateau, self.chevalet, dico_ia)
+        dico_complet = Trie.depuis_iterable(_MOTS_COMPLET)
+        moy = _moyennes_par_niveau(
+            self.plateau, self.chevalet, dico_ia, dico_champion=dico_complet
+        )
         ordre = sorted(Niveau, key=lambda niv: moy[niv])
         assert ordre == _ORDRE_CROISSANT_ATTENDU
-        # Croissant le long de l'ordre attendu, strictement sauf aux paires
-        # d'égalité documentées (EXPERT/CHAMPION_DU_MONDE).
         for a, b in zip(_ORDRE_CROISSANT_ATTENDU, _ORDRE_CROISSANT_ATTENDU[1:]):
-            if (a, b) in _PAIRES_EGALITE_ATTENDUE:
-                assert moy[a] == moy[b], f"{a} et {b} devraient être égaux : {moy}"
-            else:
-                assert moy[a] < moy[b], f"{a} devrait être < {b} : {moy}"
+            assert moy[a] < moy[b], f"{a} devrait être < {b} : {moy}"
 
     def test_niveaux_restent_perceptiblement_distincts(self):
         """Aucun niveau ne se confond avec son voisin sous le filtre.
 
-        Point #3 de l'issue : on veut détecter le cas où un niveau ne se
-        distinguerait plus suffisamment d'un autre. On exige un écart d'au moins
-        1 point entre niveaux adjacents dans l'ordre de progression, seuil
-        au-delà duquel la différence reste perceptible en jeu — SAUF pour la
-        paire EXPERT/CHAMPION_DU_MONDE, dont l'égalité est attendue et
-        temporaire (issue #368, lot D ; levée par le lot C).
+        Point #3 de l'issue #207 : on veut détecter le cas où un niveau ne se
+        distinguerait plus suffisamment d'un autre. On exige un écart d'au
+        moins 1 point entre niveaux adjacents dans l'ordre de progression,
+        seuil au-delà duquel la différence reste perceptible en jeu — y
+        compris désormais pour la paire EXPERT/CHAMPION_DU_MONDE (issue #369,
+        lot C, monotonie devenue stricte : voir ``dico_champion``).
         """
         dico_ia = Trie.depuis_iterable(_MOTS_IA_RESTREINT)
-        moy = _moyennes_par_niveau(self.plateau, self.chevalet, dico_ia)
+        dico_complet = Trie.depuis_iterable(_MOTS_COMPLET)
+        moy = _moyennes_par_niveau(
+            self.plateau, self.chevalet, dico_ia, dico_champion=dico_complet
+        )
         for a, b in zip(_ORDRE_CROISSANT_ATTENDU, _ORDRE_CROISSANT_ATTENDU[1:]):
             ecart = moy[b] - moy[a]
-            if (a, b) in _PAIRES_EGALITE_ATTENDUE:
-                assert ecart == 0.0, f"{a} et {b} devraient être égaux : {moy}"
-            else:
-                assert ecart >= 1.0, f"{a} et {b} trop proches sous filtre : {moy}"
+            assert ecart >= 1.0, f"{a} et {b} trop proches sous filtre : {moy}"
 
     def test_ordre_relatif_identique_avec_et_sans_filtre(self):
         """L'ordre RELATIF des niveaux est identique avec et sans filtre.
# (diff du fichier suivant)
diff --git a/tests/test_moteur_partie.py b/tests/test_moteur_partie.py
# (index — ignorable)
index bbba09a..1430eaa 100644
# (avant — fichier suivant)
--- a/tests/test_moteur_partie.py
# (après — fichier suivant)
+++ b/tests/test_moteur_partie.py
# ── Zone modifiée : ligne 494 (31 ligne(s)) dans l'ancienne version → ligne 494 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -494,31 +494,34 @@ def test_jouer_tours_ia_enchaine_jusqu_a_un_humain():
 
 
 # --------------------------------------------------------------------------- #
-# Vocabulaire humain de l'IA (issue #206) : second dictionnaire optionnel
+# Vocabulaire de l'IA par niveau (issues #206, #369 lot C) :
+# mapping {Niveau: Trie} optionnel, fin du Trie IA unique
 # --------------------------------------------------------------------------- #
 
-def test_dictionnaire_ia_defaut_meme_objet():
-    """Par défaut, dictionnaire_ia EST le dictionnaire (même objet, coût nul)."""
+def test_dictionnaires_ia_defaut_vide():
+    """Par défaut, dictionnaires_ia est un mapping vide (coût nul)."""
     trie = _trie("CHAT")
     partie = Partie([Joueur("Alice")], trie, graine=1)
-    assert partie.dictionnaire_ia is partie.dictionnaire
-    assert partie.dictionnaire_ia is trie
+    assert partie.dictionnaires_ia == {}
 
 
-def test_dictionnaire_ia_distinct_quand_fourni():
-    """Un dictionnaire_ia explicite est conservé, distinct du dictionnaire complet."""
+def test_dictionnaire_ia_par_niveau_distinct_quand_fourni():
+    """Un Trie par niveau explicite est conservé, distinct du dictionnaire complet."""
     complet = _trie("CHAT", "CHIEN")
     restreint = _trie("CHAT")
     partie = Partie(
-        [Joueur("Alice")], complet, graine=1, dictionnaire_ia=restreint
+        [Joueur("Alice")],
+        complet,
+        graine=1,
+        dictionnaires_ia={Niveau.EXPERT: restreint},
     )
     assert partie.dictionnaire is complet
-    assert partie.dictionnaire_ia is restreint
-    assert partie.dictionnaire_ia is not partie.dictionnaire
+    assert partie.dictionnaires_ia[Niveau.EXPERT] is restreint
+    assert partie.dictionnaires_ia[Niveau.EXPERT] is not partie.dictionnaire
 
 
-def test_jouer_tour_ia_genere_sur_dictionnaire_ia(monkeypatch):
-    """La génération des coups IA reçoit dictionnaire_ia, pas le dico complet."""
+def test_jouer_tour_ia_genere_sur_dictionnaire_du_niveau(monkeypatch):
+    """La génération des coups IA reçoit le Trie de SON niveau, pas le dico complet."""
     import scrabble.moteur.ia as ia_mod
 
     complet = _trie("CHAT")
# ── Zone modifiée : ligne 527 (7 ligne(s)) dans l'ancienne version → ligne 530 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -527,7 +530,7 @@ def test_jouer_tour_ia_genere_sur_dictionnaire_ia(monkeypatch):
         [Joueur("IA", humain=False, niveau=Niveau.EXPERT)],
         complet,
         graine=1,
-        dictionnaire_ia=restreint,
+        dictionnaires_ia={Niveau.EXPERT: restreint},
     )
     captures: dict = {}
 
# ── Zone modifiée : ligne 540 (13 ligne(s)) dans l'ancienne version → ligne 543 (82 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -540,13 +543,82 @@ def test_jouer_tour_ia_genere_sur_dictionnaire_ia(monkeypatch):
     assert captures["dico"] is restreint
 
 
+def test_jouer_tour_ia_niveau_absent_du_mapping_retombe_sur_dictionnaire(monkeypatch):
+    """Un niveau absent de ``dictionnaires_ia`` retombe sur le dico complet."""
+    import scrabble.moteur.ia as ia_mod
+
+    complet = _trie("CHAT")
+    restreint = _trie("CHIEN")
+    partie = Partie(
+        [Joueur("IA", humain=False, niveau=Niveau.DEBUTANT)],
+        complet,
+        graine=1,
+        # Seul EXPERT a un Trie propre : DEBUTANT (le niveau joué ici) n'y
+        # figure pas et doit retomber sur le dictionnaire complet.
+        dictionnaires_ia={Niveau.EXPERT: restreint},
+    )
+    captures: dict = {}
+
+    def faux_choisir(plateau, chevalet, dictionnaire, niveau):
+        captures["dico"] = dictionnaire
+        return None
+
+    monkeypatch.setattr(ia_mod, "choisir_coup", faux_choisir)
+    partie.jouer_tour_ia()
+    assert captures["dico"] is complet
+
+
+def test_deux_ia_niveaux_differents_utilisent_deux_tries_distincts(monkeypatch):
+    """Test central du lot C : deux IA de niveaux différents, deux Tries distincts.
+
+    Fin du Trie IA unique (rapport de lecture #366) : une partie avec un
+    Débutant et un Expert utilise bien un Trie propre à chacun, pas un Trie
+    global partagé.
+    """
+    import scrabble.moteur.ia as ia_mod
+
+    complet = _trie("CHAT", "CHIEN", "CANOT")
+    trie_debutant = _trie("CHAT")
+    trie_expert = _trie("CHIEN")
+    partie = Partie(
+        [
+            Joueur("Debutant", humain=False, niveau=Niveau.DEBUTANT),
+            Joueur("Expert", humain=False, niveau=Niveau.EXPERT),
+        ],
+        complet,
+        graine=1,
+        dictionnaires_ia={
+            Niveau.DEBUTANT: trie_debutant,
+            Niveau.EXPERT: trie_expert,
+        },
+    )
+    captures: list = []
+
+    def faux_choisir(plateau, chevalet, dictionnaire, niveau):
+        captures.append((niveau, dictionnaire))
+        return None
+
+    monkeypatch.setattr(ia_mod, "choisir_coup", faux_choisir)
+    partie.jouer_tour_ia()  # Débutant (index 0)
+    partie.jouer_tour_ia()  # Expert (index 1)
+
+    assert captures == [
+        (Niveau.DEBUTANT, trie_debutant),
+        (Niveau.EXPERT, trie_expert),
+    ]
+    assert captures[0][1] is not captures[1][1]
+
+
 def test_valider_coup_humain_reste_sur_dictionnaire_complet():
     """Un coup humain est validé sur le dico complet, même IA restreinte (à vide)."""
     complet = _trie("CADRE")
     restreint = _trie()  # vocabulaire IA vide : n'affecte pas l'humain
     joueur = Joueur("Alice")
     partie = Partie(
-        [joueur], complet, graine=1, dictionnaire_ia=restreint
+        [joueur],
+        complet,
+        graine=1,
+        dictionnaires_ia={Niveau.EXPERT: restreint},
     )
     joueur.chevalet[:] = list("CADRE")
 
# ── Zone modifiée : ligne 569 (7 ligne(s)) dans l'ancienne version → ligne 641 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -569,7 +641,7 @@ def test_ia_restreinte_ne_joue_pas_hors_vocabulaire():
         [Joueur("Humain"), Joueur("IA", humain=False, niveau=Niveau.EXPERT)],
         complet,
         graine=1,
-        dictionnaire_ia=restreint,
+        dictionnaires_ia={Niveau.EXPERT: restreint},
     )
     partie.joueurs[0].chevalet[:] = list("CADRE")
     partie.jouer_coup(_coup_cadre_au_centre())   # pose CADRE, main à l'IA
# ── Zone modifiée : ligne 580 (25 ligne(s)) dans l'ancienne version → ligne 652 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -580,25 +652,27 @@ def test_ia_restreinte_ne_joue_pas_hors_vocabulaire():
     assert entree.action == ACTION_PASSE
     # Le vocabulaire humain (dico complet) reste strictement plus large.
     assert partie.dictionnaire.contient("AS")
-    assert not partie.dictionnaire_ia.contient("AS")
+    assert not partie.dictionnaires_ia[Niveau.EXPERT].contient("AS")
 
 
-def test_recreer_partie_conserve_dictionnaire_ia_restreint():
-    """« Recommencer » repropage le Trie restreint quand l'IA était limitée."""
+def test_recreer_partie_conserve_dictionnaires_ia():
+    """« Recommencer » repropage le mapping de Tries restreints tel quel."""
     complet = _trie("CHAT", "CHIEN")
     restreint = _trie("CHAT")
     joueurs = [
         Joueur("Alice"),
         Joueur("IA", humain=False, niveau=Niveau.FACILE),
     ]
-    partie = Partie(joueurs, complet, graine=1, dictionnaire_ia=restreint)
+    partie = Partie(
+        joueurs, complet, graine=1, dictionnaires_ia={Niveau.FACILE: restreint}
+    )
 
     nouvelle = recreer_partie_meme_joueurs(
         partie, complet, graine=2, tirage_ordre=False
     )
 
     assert nouvelle.dictionnaire is complet
-    assert nouvelle.dictionnaire_ia is restreint
+    assert nouvelle.dictionnaires_ia == {Niveau.FACILE: restreint}
 
 
 def test_recreer_partie_sans_restriction_reste_sur_dictionnaire():
# ── Zone modifiée : ligne 608 (8 ligne(s)) dans l'ancienne version → ligne 682 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -608,8 +682,8 @@ def test_recreer_partie_sans_restriction_reste_sur_dictionnaire():
         Joueur("Alice"),
         Joueur("IA", humain=False, niveau=Niveau.FACILE),
     ]
-    partie = Partie(joueurs, complet, graine=1)  # dictionnaire_ia is complet
-    assert partie.dictionnaire_ia is partie.dictionnaire
+    partie = Partie(joueurs, complet, graine=1)  # dictionnaires_ia vide
+    assert partie.dictionnaires_ia == {}
 
     nouveau_complet = _trie("CHAT", "CHIEN")
     nouvelle = recreer_partie_meme_joueurs(
# ── Zone modifiée : ligne 617 (4 ligne(s)) dans l'ancienne version → ligne 691 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -617,4 +691,4 @@ def test_recreer_partie_sans_restriction_reste_sur_dictionnaire():
     )
 
     assert nouvelle.dictionnaire is nouveau_complet
-    assert nouvelle.dictionnaire_ia is nouvelle.dictionnaire
+    assert nouvelle.dictionnaires_ia == {}
# (diff du fichier suivant)
diff --git a/tests/test_persistance.py b/tests/test_persistance.py
# (index — ignorable)
index 5e89d9f..66f6a1b 100644
# (avant — fichier suivant)
--- a/tests/test_persistance.py
# (après — fichier suivant)
+++ b/tests/test_persistance.py
# ── Zone modifiée : ligne 41 (6 ligne(s)) dans l'ancienne version → ligne 41 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -41,6 +41,7 @@ from scrabble.persistance.stockage import (
     enregistrer_action,
     finaliser_partie,
     lister_parties,
+    niveaux_ia_stockes,
     reprendre_partie,
     supprimer_partie,
 )
# ── Zone modifiée : ligne 245 (6 ligne(s)) dans l'ancienne version → ligne 246 (83 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -245,6 +246,83 @@ def test_reprise_tous_les_niveaux_ia(tmp_path, niveau):
     assert reprise.joueurs[1].niveau == niveau
 
 
+# --------------------------------------------------------------------------- #
+# Vocabulaire IA par niveau à la reprise (issue #369, lot C)
+# --------------------------------------------------------------------------- #
+
+def test_niveaux_ia_stockes_reflete_les_niveaux_des_ia_sans_reconstruire(tmp_path):
+    """``niveaux_ia_stockes`` lit les niveaux stockés sans rejouer la partie.
+
+    Doit ignorer les joueurs humains (``niveau`` vaut ``None``) et refléter
+    exactement les niveaux des IA, dans l'ordre des joueurs — c'est ce que
+    ``ui.accueil.ApiAccueil.reprendre`` consulte pour savoir quels paliers de
+    vocabulaire charger, avant de reconstruire la partie.
+    """
+    chemin = tmp_path / "parties.db"
+    trie = _trie()
+    partie = Partie(
+        [
+            Joueur("Humain"),
+            Joueur("Debutant", humain=False, niveau=Niveau.DEBUTANT),
+            Joueur("Champion", humain=False, niveau=Niveau.CHAMPION_DU_MONDE),
+        ],
+        trie,
+        graine=1,
+    )
+    id_partie = demarrer_suivi(partie, chemin)
+
+    assert niveaux_ia_stockes(id_partie, chemin) == [
+        Niveau.DEBUTANT,
+        Niveau.CHAMPION_DU_MONDE,
+    ]
+
+
+def test_niveaux_ia_stockes_partie_inconnue_leve(tmp_path):
+    chemin = tmp_path / "parties.db"
+    with pytest.raises(KeyError):
+        niveaux_ia_stockes(999, chemin)
+
+
+def test_reprise_avec_dictionnaires_ia_par_niveau(tmp_path):
+    """Une partie reprise utilise, par IA, le Trie de son niveau (issue #369).
+
+    Deux IA de niveaux différents (Débutant et Expert) reçoivent chacune un
+    Trie IA distinct via ``dictionnaires_ia`` : la reprise doit préserver
+    cette distinction, pas retomber sur un seul Trie partagé.
+    """
+    chemin = tmp_path / "parties.db"
+    trie = _trie()
+    partie = Partie(
+        [
+            Joueur("Humain"),
+            Joueur("Debutant", humain=False, niveau=Niveau.DEBUTANT),
+            Joueur("Expert", humain=False, niveau=Niveau.EXPERT),
+        ],
+        trie,
+        graine=1,
+    )
+    id_partie = demarrer_suivi(partie, chemin)
+
+    trie_debutant = Trie.depuis_iterable(["CHAT"])
+    trie_expert = Trie.depuis_iterable(["CHIEN"])
+    reprise = reprendre_partie(
+        id_partie,
+        trie,
+        chemin,
+        dictionnaires_ia={
+            Niveau.DEBUTANT: trie_debutant,
+            Niveau.EXPERT: trie_expert,
+        },
+    )
+
+    assert reprise.dictionnaires_ia[Niveau.DEBUTANT] is trie_debutant
+    assert reprise.dictionnaires_ia[Niveau.EXPERT] is trie_expert
+    assert (
+        reprise.dictionnaires_ia[Niveau.DEBUTANT]
+        is not reprise.dictionnaires_ia[Niveau.EXPERT]
+    )
+
+
 def test_reprise_echange_sac_identique(tmp_path):
     """Le sac après reprise doit être identique : preuve que les lettres
 
