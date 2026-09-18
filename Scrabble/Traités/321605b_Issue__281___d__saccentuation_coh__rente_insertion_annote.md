321605b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 321605b
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 00:06:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #281 : désaccentuation cohérente insertion + recherche du Trie
    
    L'ODS8 est stocké sans accent (comme les lettres physiques du jeu), mais
    la comparaison d'appartenance au Trie conservait les accents : un mot
    valide tapé avec accent (« académique ») était signalé invalide. Chaque
    source (ODS, Hunspell, belgicismes, ajouts/retraits) est désormais
    désaccentuée juste avant insertion dans le Trie (construire_trie,
    construire_ensemble_ia), et symétriquement au moment du test
    d'appartenance (Dictionnaire.mot_valide, verifier_mot_dictionnaire).
    normaliser_mot reste inchangée (definitions.json/Hunspell/Wiktionnaire
    en dépendent ailleurs). VERSION_CACHE incrémentée pour invalider les
    caches disque existants.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/dictionnaire/dictionnaire.py b/src/scrabble/dictionnaire/dictionnaire.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5b217b8..883b4bc 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/dictionnaire/dictionnaire.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/dictionnaire/dictionnaire.py
# ── Zone modifiée : ligne 19 (8 ligne(s)) dans l'ancienne version → ligne 19 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -19,8 +19,27 @@ personnalisation faite en mode ODS ne s'applique pas au mode Hunspell et
 inversement. La sélection de la paire se fait via :func:`chemins_modifs`.
 
 Normalisation systématique de chaque mot au chargement : passage en MAJUSCULES
-(les accents sont conservés — le Scrabble francophone distingue ``ELEVE`` de
-``ÉLÈVE``) et suppression des espaces superflus.
+(les accents sont conservés par :func:`normaliser_mot` — inchangé, utilisé tel
+quel par ``definitions.json``/Hunspell/le Wiktionnaire ailleurs dans le module)
+et suppression des espaces superflus.
+
+Désaccentuation du Trie de validation (issue #281)
+---------------------------------------------------
+L'ODS8 est stocké **sans aucun accent** (cohérent avec les lettres physiques du
+jeu, elles-mêmes non accentuées), alors que Hunspell contient légitimement des
+entrées accentuées. Pour qu'un mot valide soit reconnu de façon identique qu'il
+soit tapé avec ou sans accent — quelle que soit la source — :func:`desaccentuer`
+est appliquée à **toutes** les entrées juste avant leur insertion dans le Trie
+(:func:`construire_trie`, :func:`construire_ensemble_ia`), et symétriquement au
+mot recherché juste avant le test d'appartenance (:meth:`Dictionnaire.mot_valide`,
+``verifier_mot_dictionnaire`` dans ``scrabble.ui.jeu``). Un Trie destiné à la
+validation doit donc toujours contenir des entrées désaccentuées ; l'éventuelle
+« collision » entre deux mots distincts qui se désaccentuent à l'identique (ex.
+« jeune »/« jeûne ») n'est pas un défaut à corriger : sur un plateau réel, les
+lettres ne portent elles-mêmes aucun accent, donc les deux mots sont déjà un
+seul et même mot jouable. Seul l'affichage des définitions (``definition_mot``/
+``definitions_annotees``, inchangé) doit continuer à lister les gloses des deux
+mots à la suite sous la même clé désaccentuée.
 
 Dépliage Hunspell
 -----------------
# ── Zone modifiée : ligne 114 (7 ligne(s)) dans l'ancienne version → ligne 133 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -114,7 +133,8 @@ CHEMIN_CACHE_IA = DOSSIER_DICO / "trie_ia_cache.pkl"
 CHEMIN_DEFINITIONS = DOSSIER_DICO / "definitions.json"
 
 # Version du format de cache : incrémenter invalide tous les caches existants.
-VERSION_CACHE = 1
+# 2 (issue #281) : le Trie contient désormais des entrées désaccentuées.
+VERSION_CACHE = 2
 
 
 # --------------------------------------------------------------------------- #
# ── Zone modifiée : ligne 880 (8 ligne(s)) dans l'ancienne version → ligne 900 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -880,8 +900,15 @@ class Dictionnaire:
         self.trie = trie
 
     def mot_valide(self, mot: str) -> bool:
-        """Indique si ``mot`` est valide (après normalisation)."""
-        return normaliser_mot(mot) in self.trie
+        """Indique si ``mot`` est valide (après normalisation et désaccentuation).
+
+        Le Trie de validation contient des entrées désaccentuées (issue #281,
+        cohérent avec toutes les sources — ODS8/Hunspell/belgicismes — voir le
+        docstring du module) : on désaccentue donc ``mot`` avant le test
+        d'appartenance, sinon un mot valide tapé avec accent (ex. « académique »)
+        serait à tort signalé invalide.
+        """
+        return desaccentuer(normaliser_mot(mot)) in self.trie
 
     def __len__(self) -> int:
         return len(self.trie)
# ── Zone modifiée : ligne 986 (6 ligne(s)) dans l'ancienne version → ligne 1013 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -986,6 +1013,12 @@ def construire_trie(
     belges) − retirés`` : les belgicismes sans équivalent standard
     (:func:`charger_belgicismes`) rejoignent l'ensemble avant construction du
     Trie. Défaut ``False`` : comportement strictement inchangé.
+
+    Chaque entrée est **désaccentuée** (:func:`desaccentuer`) juste avant
+    l'insertion dans le Trie (issue #281), quelle que soit la source d'origine
+    (ODS8, dépliage Hunspell, belgicismes, ajouts/retraits manuels) : un mot
+    valide est ainsi reconnu de façon identique qu'il soit tapé avec ou sans
+    accent. Voir :meth:`Dictionnaire.mot_valide`, symétrique côté recherche.
     """
     defaut_ajoutes, defaut_retires = chemins_modifs(source)
     if chemin_ajoutes is None:
# ── Zone modifiée : ligne 1001 (7 ligne(s)) dans l'ancienne version → ligne 1034 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1001,7 +1034,7 @@ def construire_trie(
         mots_ajoutes,
         lire_liste_mots(chemin_retires),
     )
-    return Trie.depuis_iterable(mots)
+    return Trie.depuis_iterable(desaccentuer(mot) for mot in mots)
 
 
 def obtenir_trie(
# ── Zone modifiée : ligne 1117 (6 ligne(s)) dans l'ancienne version → ligne 1150 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1117,6 +1150,11 @@ def construire_ensemble_ia(
     restreint, sauf s'ils figurent aussi dans ``mots_courants.txt`` ou
     ``classiques_ajoutes.txt`` — comportement voulu, cohérent avec la philosophie
     actuelle du filtre de vocabulaire de l'IA.
+
+    Toutes les entrées (dictionnaire complet, mots courants, classiques) sont
+    **désaccentuées** (:func:`desaccentuer`) avant l'union/intersection (issue
+    #281), pour rester un sous-ensemble cohérent du Trie complet désaccentué
+    construit par :func:`construire_trie`.
     """
     defaut_ajoutes, defaut_retires = chemins_modifs(source)
     if chemin_ajoutes is None:
# ── Zone modifiée : ligne 1131 (6 ligne(s)) dans l'ancienne version → ligne 1169 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1131,6 +1169,7 @@ def construire_ensemble_ia(
         mots_ajoutes,
         lire_liste_mots(chemin_retires),
     )
+    complet = {desaccentuer(mot) for mot in complet}
     if not chemin_mots_courants.exists():
         journal.info(
             "Vocabulaire IA (issue #206) : fichier des mots courants absent "
# ── Zone modifiée : ligne 1138 (8 ligne(s)) dans l'ancienne version → ligne 1177 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1138,8 +1177,9 @@ def construire_ensemble_ia(
             "Déposez « Lexique383.tsv » puis lancez "
             "« scripts/generer_mots_courants.py » pour l'enrichir."
         )
-    mots_courants = lire_liste_mots(chemin_mots_courants)
-    restreint = (mots_courants | ensemble_classiques()) & complet
+    mots_courants = {desaccentuer(mot) for mot in lire_liste_mots(chemin_mots_courants)}
+    classiques = {desaccentuer(mot) for mot in ensemble_classiques()}
+    restreint = (mots_courants | classiques) & complet
     return restreint
 
 
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/jeu.py b/src/scrabble/ui/jeu.py
# (index — ignorable)
index bf80059..8aab253 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/jeu.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/jeu.py
# ── Zone modifiée : ligne 49 (6 ligne(s)) dans l'ancienne version → ligne 49 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -49,6 +49,7 @@ from scrabble.dictionnaire.dictionnaire import (
     CHEMIN_DEFINITIONS,
     Trie,
     definitions_annotees,
+    desaccentuer,
     normaliser_mot,
 )
 from scrabble.moteur.ia import Niveau
# ── Zone modifiée : ligne 873 (7 ligne(s)) dans l'ancienne version → ligne 874 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -873,7 +874,11 @@ def verifier_mot_dictionnaire(
 
     ``lettres`` est la suite de jetons arrangés dans la zone de brouillon (dans
     l'ordre affiché), soit sous forme de liste, soit déjà concaténée. Le mot est
-    normalisé (majuscules, NFC) comme le Trie ODS8 l'attend, puis testé via
+    normalisé (majuscules, NFC) puis **désaccentué** (:func:`desaccentuer`,
+    issue #281) juste avant le test d'appartenance, cohérent avec le Trie de
+    validation qui contient lui-même des entrées désaccentuées (voir le
+    docstring du module ``dictionnaire``) — un mot valide tapé avec accent (ex.
+    « académique ») doit être reconnu comme un mot tapé sans accent. Testé via
     :meth:`dictionnaire.contient`. **Lecture seule** : aucune mutation de la
     partie ni du dictionnaire.
 
# ── Zone modifiée : ligne 905 (7 ligne(s)) dans l'ancienne version → ligne 910 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -905,7 +910,7 @@ def verifier_mot_dictionnaire(
             "succes": False,
             "erreur": "La zone de brouillon ne contient aucune lettre à vérifier.",
         }
-    valide = bool(dictionnaire.contient(mot))
+    valide = bool(dictionnaire.contient(desaccentuer(mot)))
     definition = None
     if valide:
         annotees = definitions_annotees(mot, chemin_definitions, chemin_belgicismes)
# (diff du fichier suivant)
diff --git a/tests/test_dictionnaire.py b/tests/test_dictionnaire.py
# (index — ignorable)
index d5cfb29..673a30d 100644
# (avant — fichier suivant)
--- a/tests/test_dictionnaire.py
# (après — fichier suivant)
+++ b/tests/test_dictionnaire.py
# ── Zone modifiée : ligne 249 (13 ligne(s)) dans l'ancienne version → ligne 249 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -249,13 +249,16 @@ def test_trie_mot_vide_ignore():
 
 
 def test_dictionnaire_mot_valide_normalise_l_entree():
-    """``mot_valide`` normalise l'entrée avant de consulter le Trie."""
-    dico = Dictionnaire(Trie.depuis_iterable(["CHAT", "ÉLÈVE"]))
+    """``mot_valide`` normalise PUIS désaccentue l'entrée avant de consulter le
+    Trie (issue #281) : un Trie de validation contient toujours des entrées
+    déjà désaccentuées (voir :func:`construire_trie`), donc « ELEVE » ici,
+    reconnu qu'on tape « élève » ou « eleve » — accents ou non, même mot."""
+    dico = Dictionnaire(Trie.depuis_iterable(["CHAT", "ELEVE"]))
 
     assert dico.mot_valide("chat")
     assert dico.mot_valide("  Chat ")
     assert dico.mot_valide("élève")
-    assert not dico.mot_valide("eleve")   # accents distincts
+    assert dico.mot_valide("eleve")       # accents désormais indifférents
     assert not dico.mot_valide("zzz")
 
 
# ── Zone modifiée : ligne 378 (6 ligne(s)) dans l'ancienne version → ligne 381 (43 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -378,6 +381,43 @@ def test_charger_definitions_mot_ascii_sans_accent(tmp_path):
     ]
 
 
+def test_definition_mot_jeune_jeune_circonflexe_meme_cle_desaccentuee(tmp_path):
+    """« jeune » et « jeûne » partagent la clé désaccentuée JEUNE (issue #281).
+
+    C'est le scénario de « collision » évoqué par Alain : les lettres du
+    Scrabble n'ayant elles-mêmes aucun accent, les deux mots sont déjà un seul
+    et même mot jouable — pas un bug à corriger. Le point à vérifier est que
+    l'affichage combine bien les gloses des DEUX mots sous cette clé unique,
+    sans que l'une masque l'autre. ``definition_mot``/``definitions_annotees``
+    ne sont pas modifiées par cette issue : elles utilisaient déjà
+    ``desaccentuer(normaliser_mot(mot))`` pour retrouver la clé, et le
+    contenu de la clé (une simple liste) affiche déjà toutes les gloses
+    à la suite — comportement confirmé ici, aucun correctif requis.
+    """
+    fichier = tmp_path / "definitions.json"
+    fichier.write_text(
+        json.dumps(
+            {
+                "JEUNE": [
+                    "Qui est dans une phase au commencement de sa vie.",  # jeune
+                    "Abstention totale d'aliments.",                     # jeûne
+                ]
+            },
+            ensure_ascii=False,
+        ),
+        encoding="utf-8",
+    )
+
+    attendu = [
+        "Qui est dans une phase au commencement de sa vie.",
+        "Abstention totale d'aliments.",
+    ]
+    # Les deux graphies (avec et sans accent circonflexe) retrouvent la même
+    # liste combinée : aucune des deux définitions n'est masquée par l'autre.
+    assert definition_mot("jeûne", fichier) == attendu
+    assert definition_mot("jeune", fichier) == attendu
+
+
 def test_charger_definitions_json_invalide(tmp_path):
     """Un JSON illisible retombe sur un dict vide plutôt que de planter."""
     fichier = tmp_path / "definitions.json"
# ── Zone modifiée : ligne 583 (6 ligne(s)) dans l'ancienne version → ligne 623 (82 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -583,6 +623,82 @@ def test_construire_trie_mode_belgicisme_mot_oui_absent_de_la_source_reste_absen
     assert "ZORGLUB" not in trie
 
 
+# --------------------------------------------------------------------------- #
+# Désaccentuation cohérente insertion + recherche (issue #281)
+# --------------------------------------------------------------------------- #
+
+def test_construire_trie_ods_reconnait_les_mots_tapes_avec_accent(tmp_path):
+    """L'ODS8 est stocké sans accent : un mot valide tapé AVEC accent (ex.
+    « académique », « école », « été ») doit être reconnu, la comparaison
+    d'appartenance étant elle aussi désaccentuée (:meth:`Dictionnaire.mot_valide`)."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["academique", "ecole", "ete"]
+    )
+    trie = construire_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+    )
+    dico = Dictionnaire(trie)
+
+    assert dico.mot_valide("académique")
+    assert dico.mot_valide("école")
+    assert dico.mot_valide("été")
+    # La forme sans accent reste bien sûr valide aussi (non-régression).
+    assert dico.mot_valide("ACADEMIQUE")
+
+
+def test_construire_trie_hunspell_mot_accentue_reste_valide(tmp_path, monkeypatch):
+    """Non-régression : Hunspell contient légitimement des entrées accentuées
+    (ex. « ACADÉMIQUE »). La désaccentuation à l'insertion et à la recherche
+    étant symétrique, ce mot reste reconnu — tapé avec ou sans accent."""
+    monkeypatch.setattr(
+        d,
+        "charger_source",
+        lambda source, chemin_ods, base_hunspell: {"ACADÉMIQUE", "ÉCOLE"},
+    )
+    chemin_ajoutes = tmp_path / "mots_ajoutes.txt"
+    chemin_ajoutes.touch()
+    chemin_retires = tmp_path / "mots_retires.txt"
+    chemin_retires.touch()
+
+    trie = construire_trie(
+        source="hunspell",
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+    )
+    dico = Dictionnaire(trie)
+
+    assert dico.mot_valide("académique")
+    assert dico.mot_valide("ACADEMIQUE")
+    assert dico.mot_valide("école")
+
+
+def test_construire_trie_belgicisme_accentue_sans_equivalent_standard(tmp_path):
+    """Un belgicisme accentué sans équivalent standard (ex. « agréation »,
+    ``existe_sens_standard=non``) est valide en mode Belgicisme, reconnu qu'on
+    le tape avec ou sans accent (issue #281)."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["chat"]
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(chemin_belges, [("agréation", "non")])
+
+    trie = construire_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        mode_belgicisme=True,
+        chemin_belgicismes=chemin_belges,
+    )
+    dico = Dictionnaire(trie)
+
+    assert dico.mot_valide("agréation")
+    assert dico.mot_valide("AGREATION")
+
+
 def test_obtenir_trie_cache_mode_defaut_false_comportement_inchange(tmp_path):
     """Non-régression (issue #274) : mode par défaut (``False``), le cache se
     comporte strictement comme avant cette issue (écrit puis relu sans
# (diff du fichier suivant)
diff --git a/tests/test_jeu_brouillon.py b/tests/test_jeu_brouillon.py
# (index — ignorable)
index 57b756f..e6307a3 100644
# (avant — fichier suivant)
--- a/tests/test_jeu_brouillon.py
# (après — fichier suivant)
+++ b/tests/test_jeu_brouillon.py
# ── Zone modifiée : ligne 219 (6 ligne(s)) dans l'ancienne version → ligne 219 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -219,6 +219,14 @@ class TestVerifierMotDictionnaire:
         assert res["valide"] is True
         assert res["definition"] == [{"texte": "Casser, fatiguer.", "origine": "belge"}]
 
+    def test_mot_tape_avec_accent_reconnu_valide(self):
+        # Issue #281 : le Trie de validation contient des entrées désaccentuées
+        # (ici « ACADEMIQUE », comme le stocke réellement l'ODS8) — un mot tapé
+        # avec accent dans la loupe doit être désaccentué avant le test
+        # d'appartenance, cohérent avec l'insertion.
+        res = verifier_mot_dictionnaire(_DicoMots("ACADEMIQUE"), "académique")
+        assert res["valide"] is True
+
     def test_accepte_chaine_deja_assemblee(self):
         res = verifier_mot_dictionnaire(_DicoMots("CHAT"), "chat")
         assert res["mot"] == "CHAT"
