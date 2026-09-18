b170ed4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b170ed4
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Aug 5 20:29:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #370 (lot E) : suppression du réglage « vocabulaire humain »
    
    Retire le réglage global booléen vocabulaire_humain (issue #206), rendu
    redondant et contradictoire par le lot C (#369) : chaque niveau IA joue
    maintenant sur son propre palier de vocabulaire ; la case décochée annulait
    toute cette différenciation en repliant tous les niveaux sur l'ODS8 complet.
    
    - config.py : clé retirée de CONFIG_DEFAUT et CLES_BOOLEENNES.
    - ui/accueil.py : _construire_trie_ia construit désormais inconditionnellement
      le mapping par niveau ; _disponibilite_niveau ne dépend plus que du fichier
      de palier ; obtenir_reglages_generaux n'expose plus la clé.
    - ui/web/accueil.html / accueil.js : case à cocher, aide et handler retirés.
    - Config auto-réparante : une config.json existante avec la clé orpheline
      (cas d'Alain, sa mère, Béatrice) est nettoyée silencieusement au premier
      chargement, sans planter ni la réintroduire — nouveau test dédié.
    - Tests adaptés/retirés dans test_reglages.py, test_config.py,
      test_accueil.py, test_jeu_pose.py, test_reglages_ui.py. Suite complète :
      833 tests verts.
    - Non touché (lot F) : écran d'accueil visuel (6e bouton, dégradé CSS).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 367c407..22e9611 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (44 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,44 @@ Historique des changements notables, par ordre antéchronologique. Voir aussi
 
 ### Ajouté
 
+- **Issue #370** (lot E, suite de #366/#369) — Suppression du réglage global
+  « vocabulaire humain » (issue #206), devenu redondant et contradictoire
+  depuis le lot C (#369) : chaque niveau joue désormais sur son propre palier
+  de vocabulaire, et la case décochée (défaut historique du réglage avant
+  #342) faisait retomber **tous** les niveaux sur l'ODS8 complet, annulant
+  toute la différenciation introduite par le lot C. `config.py` : clé
+  `vocabulaire_humain` retirée de `CONFIG_DEFAUT` et de `CLES_BOOLEENNES`.
+  `ui/accueil.py` : `_construire_trie_ia` construit désormais
+  inconditionnellement le mapping des niveaux présents (fin de la branche
+  « réglage désactivé → mapping vide ») ; `_disponibilite_niveau` ne dépend
+  plus que de la présence du fichier de vocabulaire du palier ;
+  `obtenir_reglages_generaux` n'expose plus la clé. Écran d'accueil
+  (`ui/web/accueil.html`/`.js`) : case à cocher, texte d'aide et gestionnaire
+  JS retirés. Le repli défensif sur le dictionnaire complet pour un niveau
+  absent du mapping (`Partie.__init__`/`jouer_tour_ia`) n'est PAS touché : il
+  reste le filet de sécurité générique (mapping `None`, ou niveau non couvert
+  par un futur ajout), indépendamment de tout réglage désormais.
+  Risque principal validé (rapport #366) : une `config.json` **existante**
+  contenant encore la clé (celles d'Alain, de sa mère et de Béatrice
+  l'avaient toutes) se charge sans planter ni la réintroduire — la clé
+  orpheline est traitée comme toute clé inconnue par la config
+  auto-réparante (`_fusionner_defauts` ne construit `config` qu'à partir de
+  `CONFIG_DEFAUT.items()`, et marque `doit_reparer=True` dès qu'une clé du
+  fichier n'en fait pas partie), donc silencieusement nettoyée au premier
+  chargement. Nouveau test dédié
+  (`test_config.py::test_vocabulaire_humain_orpheline_ignoree`).
+  Tests adaptés/retirés dans `test_reglages.py`, `test_config.py`,
+  `test_accueil.py`, `test_jeu_pose.py`, `test_reglages_ui.py` : les tests qui
+  testaient spécifiquement le réglage (round-trip booléen, exposition dans
+  `obtenir_reglages_generaux`, branche « mapping vide si inactif ») sont
+  supprimés ; ceux qui testaient autre chose au passage (disponibilité par
+  palier, refus d'un niveau indisponible, reprise d'un niveau devenu
+  indisponible, source du dictionnaire jusqu'à la validation d'un coup) sont
+  conservés, débarrassés de la clé désormais inerte. Suite complète : 833
+  tests verts.
+  Non touché (hors périmètre, lot F) : écran d'accueil visuel — 6ᵉ bouton,
+  dégradé CSS, boutons désactivés.
+
 - **Issue #369** (lot C, suite de #366/#367/#368) — Résolution du Trie IA par
   niveau : fin du Trie IA unique de `Partie` (verrou structurel identifié par
   le rapport de lecture #366). `scrabble.moteur.ia.resoudre_palier(Niveau) ->
# (diff du fichier suivant)
diff --git a/src/scrabble/config.py b/src/scrabble/config.py
# (index — ignorable)
index e716c27..93e5d9d 100644
# (avant — fichier suivant)
--- a/src/scrabble/config.py
# (après — fichier suivant)
+++ b/src/scrabble/config.py
# ── Zone modifiée : ligne 58 (16 ligne(s)) dans l'ancienne version → ligne 58 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -58,16 +58,6 @@ CONFIG_DEFAUT: dict[str, Any] = {
     # utilisatrice cible) : le comportement historique (pénalité seule,
     # issue #22) reste accessible en désactivant ce réglage.
     "bonus_fin_partie": True,
-    # Vocabulaire humain de l'IA (issue #206) : quand activé, l'IA (tous niveaux
-    # confondus) ne choisit ses coups que parmi les mots « courants »
-    # (``mots_courants.txt``, issue #205) et les « classiques du jeu » (statut de
-    # l'issue #204, WU/SIX/ZOO…), plutôt que dans tout le dictionnaire. Réglage
-    # global unique, indépendant du niveau de difficulté. Activé par défaut
-    # (issue #342, préférence de Béatrice, utilisatrice cible) : le comportement
-    # historique (IA sur le dictionnaire complet) reste accessible en désactivant
-    # ce réglage. N'affecte jamais ce que le joueur humain peut jouer ou
-    # vérifier (``valider_coup`` reste sur le dictionnaire complet).
-    "vocabulaire_humain": True,
     # Type d'échange des lettres autorisé pendant un tour (issue #138) :
     # "complet" (défaut, comportement historique : on remet tout le chevalet et
     # on repioche sept lettres) ou "partiel" (le joueur choisit librement une à
# ── Zone modifiée : ligne 91 (9 ligne(s)) dans l'ancienne version → ligne 81 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -91,9 +81,7 @@ CLES_TEXTE_LIBRE: frozenset[str] = frozenset({"prenom_principal", "avatar_princi
 
 # Clés dont la valeur est un booléen (et non une chaîne) : validées à part,
 # toute valeur non booléenne déclenchant une réparation vers le défaut.
-CLES_BOOLEENNES: frozenset[str] = frozenset(
-    {"bonus_fin_partie", "vocabulaire_humain"}
-)
+CLES_BOOLEENNES: frozenset[str] = frozenset({"bonus_fin_partie"})
 
 # Thèmes visuels de plateau reconnus. Doivent rester alignés avec les classes
 # CSS ``theme-<nom>`` de ``ui/web/jeu.css`` et les libellés de ``ui/web/jeu.js``.
# (diff du fichier suivant)
diff --git a/src/scrabble/moteur/ia.py b/src/scrabble/moteur/ia.py
# (index — ignorable)
index 6154874..9f35cb0 100644
# (avant — fichier suivant)
--- a/src/scrabble/moteur/ia.py
# (après — fichier suivant)
+++ b/src/scrabble/moteur/ia.py
# ── Zone modifiée : ligne 60 (8 ligne(s)) dans l'ancienne version → ligne 60 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -60,8 +60,7 @@ Lexique), CHAMPION_DU_MONDE sur le Trie complet ODS8. Le vocabulaire plus
 large de CHAMPION_DU_MONDE lui ouvre des coups inaccessibles à EXPERT, d'où
 l'inégalité stricte en moyenne. Contrairement aux cinq premiers niveaux, ce
 n'est donc PAS une propriété de ce module : à dictionnaire identique (par
-exemple si l'appelant transmettait le même Trie aux deux, ou avec le
-vocabulaire humain désactivé — voir ``ui.accueil``), les deux niveaux
+exemple si l'appelant transmettait le même Trie aux deux), les deux niveaux
 redeviennent mécaniquement égaux, comme le vérifie la fixture de test dédiée.
 
 Pourquoi « top 60 % » pour FACILE plutôt qu'une moitié/tranche centrale ? La
# (diff du fichier suivant)
diff --git a/src/scrabble/moteur/partie.py b/src/scrabble/moteur/partie.py
# (index — ignorable)
index 647a4ff..43014b2 100644
# (avant — fichier suivant)
--- a/src/scrabble/moteur/partie.py
# (après — fichier suivant)
+++ b/src/scrabble/moteur/partie.py
# ── Zone modifiée : ligne 315 (10 ligne(s)) dans l'ancienne version → ligne 315 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -315,10 +315,10 @@ class Partie:
     niveau, voir ``scrabble.moteur.ia.resoudre_palier``). Un niveau **absent**
     du mapping (dont ``dictionnaires_ia`` vide ou ``None``, tout comme
     :data:`~scrabble.moteur.ia.Niveau.CHAMPION_DU_MONDE` construit sans entrée)
-    retombe sur ``dictionnaire`` complet — comportement historique inchangé, y
-    compris quand le réglage « vocabulaire humain » (issue #206) est désactivé :
-    l'appelant UI transmet alors un mapping vide et toutes les IA jouent sur
-    l'ODS8 complet.
+    retombe sur ``dictionnaire`` complet — comportement historique inchangé et
+    défensif, conservé même si l'appelant UI construit désormais toujours le
+    mapping par palier sans condition (issue #370, lot E : suppression du
+    réglage global « vocabulaire humain », issue #206).
     """
 
     def __init__(
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/accueil.py b/src/scrabble/ui/accueil.py
# (index — ignorable)
index b93e51f..c8d03f7 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/accueil.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/accueil.py
# ── Zone modifiée : ligne 108 (22 ligne(s)) dans l'ancienne version → ligne 108 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -108,22 +108,16 @@ _LIBELLES_NIVEAUX: dict[Niveau, str] = {
 def _disponibilite_niveau(niveau: Niveau) -> tuple[bool, str | None]:
     """Disponibilité du vocabulaire IA d'un niveau (issue #369, lot C, point 5).
 
-    Réglage « vocabulaire humain » (issue #206) désactivé (défaut) → toujours
-    disponible : tous les niveaux jouent alors sur l'ODS8 complet (point 7 de
-    l'issue #369), le fichier de vocabulaire d'un palier n'entre donc jamais
-    en jeu et ne doit pas bloquer la sélection d'un niveau. Activé → un
-    niveau est indisponible quand son palier (:func:`resoudre_palier`) est
+    Un niveau est indisponible quand son palier (:func:`resoudre_palier`) est
     connu mais que le fichier de vocabulaire correspondant est absent du
     disque (:func:`~scrabble.dictionnaire.dictionnaire.paliers_disponibles`).
     :data:`~scrabble.moteur.ia.Niveau.CHAMPION_DU_MONDE` (palier ``None``) ne
-    dépend d'aucun fichier : toujours disponible, réglage ou pas.
+    dépend d'aucun fichier : toujours disponible.
 
     Renvoie ``(True, None)`` si disponible, ``(False, message)`` sinon, où
     ``message`` reprend le libellé retenu par l'issue : « <Niveau> en erreur,
     veuillez choisir un autre niveau. Prévenir Alain pour la réparation. ».
     """
-    if not bool(charger_config().get("vocabulaire_humain", False)):
-        return True, None
     palier = resoudre_palier(niveau)
     if palier is None or paliers_disponibles().get(palier, False):
         return True, None
# ── Zone modifiée : ligne 548 (15 ligne(s)) dans l'ancienne version → ligne 542 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -548,15 +542,14 @@ class ApiAccueil:
         variation (config courante vs niveaux **stockés**, voir
         :func:`~scrabble.persistance.stockage.niveaux_ia_stockes`).
 
-        Réglage global « vocabulaire humain » (issue #206), toujours
-        indépendant du niveau de difficulté : désactivé (défaut) → mapping
-        **vide** ; chaque IA retombe alors sur le dictionnaire complet dans
-        ``Partie`` (comportement historique inchangé, coût nul — voir le
-        docstring de ``Partie`` pour ce repli). Activé → un Trie par niveau
-        **présent uniquement** (chargement paresseux, point 3 de l'issue) :
-        au plus 3 IA à une table, donc au plus 3 paliers chargés, jamais les
-        six — le rapport #366 chiffre un Trie complet à plusieurs dizaines de
-        Mo, et les mesures du lot C (voir CHANGELOG) confirment l'écart.
+        Vocabulaire par palier appliqué inconditionnellement (issue #370, lot
+        E : suppression du réglage global « vocabulaire humain », issue #206,
+        devenu redondant depuis que chaque niveau a son propre palier) : un
+        Trie par niveau **présent uniquement** (chargement paresseux, point 3
+        de l'issue #369) — au plus 3 IA à une table, donc au plus 3 paliers
+        chargés, jamais les six — le rapport #366 chiffre un Trie complet à
+        plusieurs dizaines de Mo, et les mesures du lot C (voir CHANGELOG)
+        confirment l'écart.
 
         Chaque niveau se résout vers un palier via
         :func:`~scrabble.moteur.ia.resoudre_palier` :
# ── Zone modifiée : ligne 594 (8 ligne(s)) dans l'ancienne version → ligne 587 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -594,8 +587,6 @@ class ApiAccueil:
         relue ici via un second ``charger_config()`` qui pourrait en théorie
         diverger. ``mode_belgicisme`` (issue #274) suit la même logique.
         """
-        if not bool(charger_config().get("vocabulaire_humain", False)):
-            return {}
         resultat: dict[Niveau, Any] = {}
         for niveau in dict.fromkeys(niveaux):  # dédoublonne, ordre préservé
             palier = resoudre_palier(niveau)
# ── Zone modifiée : ligne 677 (9 ligne(s)) dans l'ancienne version → ligne 668 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -677,9 +668,9 @@ class ApiAccueil:
             # Réglage du bonus officiel au finisseur (issue #134), câblé dans le
             # moteur via creer_partie.
             bonus_fin_partie = bool(config.get("bonus_fin_partie", False))
-            # Réglage « vocabulaire humain » (issue #206) : un Trie par niveau
-            # d'IA présent (issue #369, lot C), construit sur la même source et
-            # le même mode que le Trie complet (issues #210, #274).
+            # Vocabulaire par palier (issue #369, lot C) : un Trie par niveau
+            # d'IA présent, construit sur la même source et le même mode que
+            # le Trie complet (issues #210, #274).
             tries_ia = self._construire_trie_ia(
                 source, niveaux_ia, mode_belgicisme, trie_complet=trie
             )
# ── Zone modifiée : ligne 806 (10 ligne(s)) dans l'ancienne version → ligne 797 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -806,10 +797,10 @@ class ApiAccueil:
             # l'IA sur la source active (Hunspell/ODS), pas sur l'ODS par défaut.
             source = charger_config().get("source_dictionnaire", "ods")
             trie = obtenir_trie(source)
-            # Réglage « vocabulaire humain » (issue #206) : une partie reprise doit
-            # continuer de restreindre son IA si le réglage est actif — sur la même
-            # source que le Trie complet (issue #210), et niveau par niveau
-            # (issue #369, lot C) selon les niveaux **stockés**.
+            # Vocabulaire par palier (issue #369, lot C) : une partie reprise
+            # continue de restreindre son IA niveau par niveau, sur la même
+            # source que le Trie complet (issue #210), selon les niveaux
+            # **stockés**.
             niveaux_stockes = niveaux_ia_stockes(id_partie)
             tries_ia = self._construire_trie_ia(
                 source, niveaux_stockes, trie_complet=trie
# ── Zone modifiée : ligne 871 (7 ligne(s)) dans l'ancienne version → ligne 862 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -871,7 +862,6 @@ class ApiAccueil:
             "theme_plateau": self._lire("theme_plateau"),
             "source_dictionnaire": self._lire("source_dictionnaire"),
             "bonus_fin_partie": self._lire_bool("bonus_fin_partie"),
-            "vocabulaire_humain": self._lire_bool("vocabulaire_humain"),
             "type_echange": self._lire("type_echange"),
             "avatar_principal": self._lire("avatar_principal"),
             # Grille d'avatars disponibles pour le sélecteur visuel (issue #143) :
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.html b/src/scrabble/ui/web/accueil.html
# (index — ignorable)
index a285ef3..0c0f06d 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.html
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.html
# ── Zone modifiée : ligne 226 (20 ligne(s)) dans l'ancienne version → ligne 226 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -226,20 +226,6 @@
                     </p>
                 </div>
 
-                <div class="champ champ-case">
-                    <label class="case-label" for="check-vocabulaire-humain">
-                        <input type="checkbox" id="check-vocabulaire-humain">
-                        <span>Vocabulaire humain de l'ordinateur</span>
-                    </label>
-                    <p class="aide">
-                        Limite l'ordinateur (tous niveaux) aux mots courants et aux
-                        classiques du jeu (WU, SIX…), plutôt qu'à tout le
-                        dictionnaire. Vous, vous pouvez toujours jouer et vérifier
-                        n'importe quel mot valide. Désactivé par défaut ; prend
-                        effet à la prochaine partie.
-                    </p>
-                </div>
-
                 <div class="champ champ-radios" id="champ-type-echange">
                     <span class="champ-titre">Type d'échange</span>
                     <div class="radios" id="radios-type-echange" role="radiogroup"
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.js b/src/scrabble/ui/web/accueil.js
# (index — ignorable)
index 49b79b1..8f16d5f 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.js
# ── Zone modifiée : ligne 525 (7 ligne(s)) dans l'ancienne version → ligne 525 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -525,7 +525,6 @@ document.addEventListener('DOMContentLoaded', async () => {
     const selectTheme = document.getElementById('select-theme');
     const selectSource = document.getElementById('select-source');
     const checkBonusFin = document.getElementById('check-bonus-fin');
-    const checkVocabulaireHumain = document.getElementById('check-vocabulaire-humain');
     const radiosTypeEchange = document.getElementById('radios-type-echange');
     const statutGeneral = document.getElementById('statut-general');
 
# ── Zone modifiée : ligne 648 (7 ligne(s)) dans l'ancienne version → ligne 647 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -648,7 +647,6 @@ document.addEventListener('DOMContentLoaded', async () => {
         remplirSelect(selectTheme, r.themes, r.theme_plateau);
         remplirSelect(selectSource, r.sources, r.source_dictionnaire);
         checkBonusFin.checked = Boolean(r.bonus_fin_partie);
-        checkVocabulaireHumain.checked = Boolean(r.vocabulaire_humain);
         remplirRadios(radiosTypeEchange, 'type_echange', r.types_echange, r.type_echange);
         labelsSources = {};
         (r.sources || []).forEach((s) => { labelsSources[s.valeur] = s.libelle; });
# ── Zone modifiée : ligne 688 (15 ligne(s)) dans l'ancienne version → ligne 686 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -688,15 +686,6 @@ document.addEventListener('DOMContentLoaded', async () => {
             checkBonusFin.checked = Boolean(retenue);
         }
     });
-    // Vocabulaire humain (issue #206) : même schéma booléen que le bonus.
-    checkVocabulaireHumain.addEventListener('change', async () => {
-        const retenue = await enregistrerReglage(
-            'vocabulaire_humain', checkVocabulaireHumain.checked);
-        if (retenue !== null) {
-            checkVocabulaireHumain.checked = Boolean(retenue);
-        }
-    });
-
     // ---- Onglet Dictionnaire ----
     const formRecherche = document.getElementById('form-recherche');
     const inputMot = document.getElementById('input-mot');
# (diff du fichier suivant)
diff --git a/tests/test_accueil.py b/tests/test_accueil.py
# (index — ignorable)
index 7e45b87..c9c4f55 100644
# (avant — fichier suivant)
--- a/tests/test_accueil.py
# (après — fichier suivant)
+++ b/tests/test_accueil.py
# ── Zone modifiée : ligne 304 (36 ligne(s)) dans l'ancienne version → ligne 304 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -304,36 +304,13 @@ class TestDisponibiliteNiveaux:
     refusée), pas seulement au lancement.
     """
 
-    def test_obtenir_disponibilite_niveaux_tous_disponibles_par_defaut(
-        self, monkeypatch
-    ):
-        """Réglage désactivé (défaut) : tous les niveaux sont disponibles.
-
-        Comportement retenu quand « vocabulaire humain » est désactivé (issue
-        #369, point 7) : tous les niveaux jouent sur l'ODS8 complet, aucun
-        fichier de palier n'entre en jeu, donc aucun niveau n'est bloqué.
-        """
-        from scrabble.ui.accueil import ApiAccueil
-
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": False}
-        )
-        api = ApiAccueil()
-        disponibilites = api.obtenir_disponibilite_niveaux()
-
-        assert len(disponibilites) == len(NIVEAUX_LABELS)
-        assert all(d["disponible"] for d in disponibilites)
-        assert all(d["message"] is None for d in disponibilites)
-
     def test_obtenir_disponibilite_niveaux_signale_le_palier_manquant(
         self, monkeypatch
     ):
-        """Réglage actif : un palier absent est signalé indisponible, avec message."""
+        """Un palier absent est signalé indisponible, avec message (issue #370, lot E :
+        le vocabulaire par palier s'applique désormais sans condition)."""
         from scrabble.ui.accueil import ApiAccueil
 
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
-        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.paliers_disponibles",
             lambda: {
# ── Zone modifiée : ligne 366 (9 ligne(s)) dans l'ancienne version → ligne 343 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -366,9 +343,6 @@ class TestDisponibiliteNiveaux:
         """
         from scrabble.ui.accueil import ApiAccueil
 
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
-        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.paliers_disponibles", lambda: {"debutant": False}
         )
# ── Zone modifiée : ligne 387 (9 ligne(s)) dans l'ancienne version → ligne 361 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -387,9 +361,6 @@ class TestDisponibiliteNiveaux:
         """Un niveau dont le palier est indisponible n'affecte pas les autres."""
         from scrabble.ui.accueil import ApiAccueil
 
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
-        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.paliers_disponibles",
             lambda: {"debutant": False, "expert": True},
# ── Zone modifiée : ligne 420 (9 ligne(s)) dans l'ancienne version → ligne 391 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -420,9 +391,7 @@ class TestDisponibiliteNiveaux:
         from scrabble.dictionnaire.dictionnaire import Trie
         from scrabble.ui.accueil import ApiAccueil
 
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config", lambda: {"vocabulaire_humain": True}
-        )
+        monkeypatch.setattr("scrabble.ui.accueil.charger_config", lambda: {})
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
             lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
# ── Zone modifiée : ligne 721 (10 ligne(s)) dans l'ancienne version → ligne 690 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -721,10 +690,6 @@ class TestSourceDictionnaireAppliquee:
         from scrabble.dictionnaire.dictionnaire import Trie
 
         appels: list[str] = []
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config",
-            lambda: {"vocabulaire_humain": True},
-        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.paliers_disponibles", lambda: {"expert": True}
         )
# ── Zone modifiée : ligne 738 (24 ligne(s)) dans l'ancienne version → ligne 703 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -738,24 +703,6 @@ class TestSourceDictionnaireAppliquee:
         assert Niveau.EXPERT in tries_ia
         assert appels == ["hunspell"]
 
-    def test_construire_trie_ia_vide_si_vocabulaire_inactif(self, monkeypatch):
-        """_construire_trie_ia renvoie {} (et n'appelle pas obtenir_trie_ia) si inactif."""
-        from scrabble.moteur.ia import Niveau
-        from scrabble.ui.accueil import ApiAccueil
-
-        appels: list[str] = []
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config",
-            lambda: {"vocabulaire_humain": False},
-        )
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.obtenir_trie_ia",
-            lambda source="ods", **_: appels.append(source),
-        )
-
-        assert ApiAccueil._construire_trie_ia("hunspell", [Niveau.EXPERT]) == {}
-        assert appels == []
-
     def test_construire_trie_ia_champion_du_monde_reutilise_trie_complet(
         self, monkeypatch
     ):
# ── Zone modifiée : ligne 769 (10 ligne(s)) dans l'ancienne version → ligne 716 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -769,10 +716,6 @@ class TestSourceDictionnaireAppliquee:
         from scrabble.dictionnaire.dictionnaire import Trie
 
         appels_ia: list[str] = []
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config",
-            lambda: {"vocabulaire_humain": True},
-        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie_ia",
             lambda source="ods", **_: appels_ia.append(source),
# ── Zone modifiée : ligne 801 (10 ligne(s)) dans l'ancienne version → ligne 744 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -801,10 +744,6 @@ class TestSourceDictionnaireAppliquee:
         from scrabble.dictionnaire.dictionnaire import Trie
 
         appels: list[str] = []
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config",
-            lambda: {"vocabulaire_humain": True},
-        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.paliers_disponibles",
             lambda: {p: True for p in ("debutant", "facile", "intermediaire", "avance", "expert")},
# ── Zone modifiée : ligne 833 (10 ligne(s)) dans l'ancienne version → ligne 772 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -833,10 +772,6 @@ class TestSourceDictionnaireAppliquee:
         from scrabble.moteur.ia import Niveau
         from scrabble.ui.accueil import ApiAccueil
 
-        monkeypatch.setattr(
-            "scrabble.ui.accueil.charger_config",
-            lambda: {"vocabulaire_humain": True},
-        )
         monkeypatch.setattr(
             "scrabble.ui.accueil.paliers_disponibles", lambda: {"expert": False}
         )
# (diff du fichier suivant)
diff --git a/tests/test_config.py b/tests/test_config.py
# (index — ignorable)
index e49a772..923931d 100644
# (avant — fichier suivant)
--- a/tests/test_config.py
# (après — fichier suivant)
+++ b/tests/test_config.py
# ── Zone modifiée : ligne 99 (7 ligne(s)) dans l'ancienne version → ligne 99 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -99,7 +99,6 @@ def test_fichier_valide_non_reecrit(tmp_path):
         "prenom_principal": "Marie",
         "theme_plateau": "vert",
         "bonus_fin_partie": True,
-        "vocabulaire_humain": True,
         "type_echange": "partiel",
         "avatar_principal": "avatar-04",
     }
# ── Zone modifiée : ligne 124 (7 ligne(s)) dans l'ancienne version → ligne 123 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -124,7 +123,6 @@ def test_sauvegarder_puis_recharger(tmp_path):
             "prenom_principal": "Alice",
             "theme_plateau": "abrege",
             "bonus_fin_partie": True,
-            "vocabulaire_humain": True,
             "type_echange": "partiel",
             "avatar_principal": "avatar-11",
         },
# ── Zone modifiée : ligne 139 (7 ligne(s)) dans l'ancienne version → ligne 137 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -139,7 +137,6 @@ def test_sauvegarder_puis_recharger(tmp_path):
         "prenom_principal": "Alice",
         "theme_plateau": "abrege",
         "bonus_fin_partie": True,
-        "vocabulaire_humain": True,
         "type_echange": "partiel",
         "avatar_principal": "avatar-11",
     }
# ── Zone modifiée : ligne 155 (7 ligne(s)) dans l'ancienne version → ligne 152 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -155,7 +152,6 @@ def test_prenom_principal_vide_par_defaut_non_reecrit(tmp_path):
         "prenom_principal": "",
         "theme_plateau": "classique",
         "bonus_fin_partie": False,
-        "vocabulaire_humain": False,
         "type_echange": "complet",
         "avatar_principal": "",
     }
# ── Zone modifiée : ligne 340 (45 ligne(s)) dans l'ancienne version → ligne 336 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -340,45 +336,27 @@ def test_bonus_fin_partie_valeur_non_booleenne_reparee(tmp_path, invalide):
 
 
 # --------------------------------------------------------------------------- #
-# Vocabulaire humain de l'IA (issue #206)
+# Clé orpheline « vocabulaire_humain » (issue #370, lot E)
 # --------------------------------------------------------------------------- #
 
-def test_vocabulaire_humain_active_par_defaut(tmp_path):
-    """Le réglage « vocabulaire humain » (issue #206) est activé par défaut (issue #342)."""
-    chemin = tmp_path / "config.json"
-
-    config = charger_config(chemin)
-
-    assert config["vocabulaire_humain"] is True
-    assert CONFIG_DEFAUT["vocabulaire_humain"] is True
-
-
-@pytest.mark.parametrize("valeur", [True, False])
-def test_vocabulaire_humain_booleen_conserve(tmp_path, valeur):
-    """Un vrai booléen est conservé tel quel, sans réparation."""
-    chemin = tmp_path / "config.json"
-    chemin.write_text(
-        json.dumps({"vocabulaire_humain": valeur}), encoding="utf-8"
-    )
-
-    config = charger_config(chemin)
-
-    assert config["vocabulaire_humain"] is valeur
-
-
-@pytest.mark.parametrize("invalide", ["true", 1, 0, None, "oui"])
-def test_vocabulaire_humain_valeur_non_booleenne_reparee(tmp_path, invalide):
-    """Toute valeur non booléenne (str, entier, None) retombe sur le défaut."""
+def test_vocabulaire_humain_orpheline_ignoree(tmp_path):
+    """Une config existante avec la clé supprimée (issue #206) se charge sans
+    planter ni la réintroduire : traitée comme toute clé inconnue, elle est
+    silencieusement nettoyée (risque signalé par le rapport de lecture #366 —
+    la clé est présente dans les config.json existantes d'Alain, sa mère et
+    Béatrice)."""
     chemin = tmp_path / "config.json"
     chemin.write_text(
-        json.dumps({"vocabulaire_humain": invalide}), encoding="utf-8"
+        json.dumps({"niveau_ia": "expert", "vocabulaire_humain": True}),
+        encoding="utf-8",
     )
 
     config = charger_config(chemin)
 
-    assert config["vocabulaire_humain"] is True
+    assert config == CONFIG_DEFAUT | {"niveau_ia": "expert"}
+    assert "vocabulaire_humain" not in config
     releu = json.loads(chemin.read_text(encoding="utf-8"))
-    assert releu["vocabulaire_humain"] is True
+    assert "vocabulaire_humain" not in releu
 
 
 # --------------------------------------------------------------------------- #
# (diff du fichier suivant)
diff --git a/tests/test_jeu_pose.py b/tests/test_jeu_pose.py
# (index — ignorable)
index 882bffd..d198756 100644
# (avant — fichier suivant)
--- a/tests/test_jeu_pose.py
# (après — fichier suivant)
+++ b/tests/test_jeu_pose.py
# ── Zone modifiée : ligne 608 (7 ligne(s)) dans l'ancienne version → ligne 608 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -608,7 +608,6 @@ class TestSourceDictionnaireValidationCoup:
             "scrabble.ui.accueil.charger_config",
             lambda: {
                 "source_dictionnaire": source,
-                "vocabulaire_humain": False,
                 "bonus_fin_partie": False,
             },
         )
# (diff du fichier suivant)
diff --git a/tests/test_reglages.py b/tests/test_reglages.py
# (index — ignorable)
index 7a63dd4..185b944 100644
# (avant — fichier suivant)
--- a/tests/test_reglages.py
# (après — fichier suivant)
+++ b/tests/test_reglages.py
# ── Zone modifiée : ligne 109 (25 ligne(s)) dans l'ancienne version → ligne 109 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -109,25 +109,6 @@ def test_modifier_bonus_fin_partie_non_booleen_rejete(tmp_path):
         modifier_reglage("bonus_fin_partie", "true", chemin)
 
 
-@pytest.mark.parametrize("valeur", [True, False])
-def test_modifier_vocabulaire_humain_booleen(tmp_path, valeur):
-    """Le réglage booléen vocabulaire_humain (issue #206) fait un round-trip."""
-    chemin = tmp_path / "config.json"
-
-    retenue = modifier_reglage("vocabulaire_humain", valeur, chemin)
-
-    assert retenue is valeur
-    assert lire_reglage("vocabulaire_humain", chemin) is valeur
-    assert json.loads(chemin.read_text(encoding="utf-8"))["vocabulaire_humain"] is valeur
-
-
-def test_modifier_vocabulaire_humain_non_booleen_rejete(tmp_path):
-    """Une valeur non booléenne pour vocabulaire_humain lève TypeError."""
-    chemin = tmp_path / "config.json"
-    with pytest.raises(TypeError):
-        modifier_reglage("vocabulaire_humain", "oui", chemin)
-
-
 def test_modifier_reglage_inconnu(tmp_path):
     chemin = tmp_path / "config.json"
     with pytest.raises(KeyError):
# (diff du fichier suivant)
diff --git a/tests/test_reglages_ui.py b/tests/test_reglages_ui.py
# (index — ignorable)
index bffb831..36fd770 100644
# (avant — fichier suivant)
--- a/tests/test_reglages_ui.py
# (après — fichier suivant)
+++ b/tests/test_reglages_ui.py
# ── Zone modifiée : ligne 111 (18 ligne(s)) dans l'ancienne version → ligne 111 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -111,18 +111,6 @@ def test_obtenir_reglages_generaux_expose_bonus_fin_partie(monkeypatch):
     assert data["bonus_fin_partie"] is True
 
 
-def test_obtenir_reglages_generaux_expose_vocabulaire_humain(monkeypatch):
-    """La structure expose vocabulaire_humain sous forme de booléen (issue #206)."""
-    monkeypatch.setattr(
-        r, "lire_reglage",
-        lambda cle: True if cle == "vocabulaire_humain" else "",
-    )
-
-    data = ApiAccueil().obtenir_reglages_generaux()
-
-    assert data["vocabulaire_humain"] is True
-
-
 def test_obtenir_reglages_generaux_expose_type_echange(monkeypatch):
     """La structure expose type_echange + les options complet/partiel (issue #138)."""
     monkeypatch.setattr(
