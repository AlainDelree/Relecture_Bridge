0e689f3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0e689f3
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 22:51:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #276 : drapeau belge devant les définitions belges dans la loupe
    
    - dictionnaire.py : charger_definitions_belges() (toutes les lignes du CSV,
      aucun filtre existe_sens_standard, découpage sur " | ", cache mémoire) et
      definitions_annotees() (fusion standards + belges, dédup mot pour mot
      insensible casse/espaces/ponctuation finale, cas académique géré).
    - jeu.py : verifier_mot_dictionnaire branche definitions_annotees ; la source
      active ne filtre plus que les gloses standards (comportement ODS/Hunspell
      inchangé), les gloses belges restent permanentes, indépendantes du mode
      Belgicisme de la partie.
    - jeu.css : pastille .drapeau-mini (dégradé tricolore, même recette que
      .drapeau-belgique dans accueil.css).
    - jeu.js : afficherDefinitionBrouillon lit soit une chaîne brute soit un
      objet {texte, origine}, préfixe le drapeau uniquement pour origine=belge.
    - Tests : charger_definitions_belges, definitions_annotees (sketter sans
      équivalent standard, académique dédupliqué, mot sans définition belge
      inchangé), intégration dans verifier_mot_dictionnaire/ApiJeu.verifier_mot.
    
    771 tests passés.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/dictionnaire/dictionnaire.py b/src/scrabble/dictionnaire/dictionnaire.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 98e0e36..fcf779b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/dictionnaire/dictionnaire.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/dictionnaire/dictionnaire.py
# ── Zone modifiée : ligne 302 (6 ligne(s)) dans l'ancienne version → ligne 302 (87 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -302,6 +302,87 @@ def definition_mot(
     return gloses
 
 
+# Cache mémoire des définitions belges, chargé paresseusement (issue #276).
+_DEFINITIONS_BELGES_CACHE: dict[str, list[str]] | None = None
+
+
+def charger_definitions_belges(
+    chemin: Path = CHEMIN_BELGICISMES,
+) -> dict[str, list[str]]:
+    """Charge l'index mot → liste de gloses belges (loupe, issue #276).
+
+    Contrairement à :func:`charger_belgicismes`, lit **toutes** les lignes du
+    CSV sans filtrer sur ``existe_sens_standard`` : la loupe doit pouvoir
+    afficher une glose belge même pour un mot qui existe déjà en français
+    standard (ex. ``académique``), la déduplication avec les gloses standards
+    étant faite séparément par :func:`definitions_annotees`. La colonne
+    ``définition(s) belge(s)`` est découpée sur `` | `` pour obtenir la liste
+    des gloses de chaque mot. Clé désaccentuée, même convention que
+    ``definitions.json`` (:func:`desaccentuer`). Mise en cache mémoire à
+    l'image de :func:`charger_definitions`. Fichier absent toléré (``{}``).
+    """
+    global _DEFINITIONS_BELGES_CACHE
+    if chemin == CHEMIN_BELGICISMES and _DEFINITIONS_BELGES_CACHE is not None:
+        return _DEFINITIONS_BELGES_CACHE
+    definitions: dict[str, list[str]] = {}
+    try:
+        with open(chemin, "r", encoding="utf-8", newline="") as fichier:
+            lecteur = csv.DictReader(fichier)
+            for ligne in lecteur:
+                mot = desaccentuer(normaliser_mot(ligne.get("mot") or ""))
+                if not mot:
+                    continue
+                brut = (ligne.get("définition(s) belge(s)") or "").strip()
+                if not brut:
+                    continue
+                gloses = [glose.strip() for glose in brut.split(" | ") if glose.strip()]
+                if gloses:
+                    definitions[mot] = gloses
+    except (FileNotFoundError, IsADirectoryError, OSError):
+        definitions = {}
+    if chemin == CHEMIN_BELGICISMES:
+        _DEFINITIONS_BELGES_CACHE = definitions
+    return definitions
+
+
+def _cle_dedup_glose(glose: str) -> str:
+    """Normalise une glose pour comparaison de doublon (casse/espaces/ponctuation)."""
+    sans_ponctuation_finale = glose.strip().rstrip(".!?;: ")
+    return " ".join(sans_ponctuation_finale.split()).lower()
+
+
+def definitions_annotees(
+    mot: str,
+    chemin_definitions: Path = CHEMIN_DEFINITIONS,
+    chemin_belges: Path = CHEMIN_BELGICISMES,
+) -> list[dict[str, str]] | None:
+    """Fusionne gloses standards et gloses belges d'un mot (loupe, issue #276).
+
+    Retourne une liste de ``{"texte": ..., "origine": "standard"|"belge"}`` :
+    les gloses standards d'abord (via :func:`definition_mot`), puis les gloses
+    belges (via :func:`charger_definitions_belges`) qui ne dupliquent pas déjà
+    une glose standard présente (comparaison normalisée insensible à la
+    casse/aux espaces/à la ponctuation finale — voir :func:`_cle_dedup_glose`,
+    cas ``académique`` dont les deux gloses belges existent déjà mot pour mot
+    dans le Wiktionnaire filtré). Renvoie ``None`` si le mot n'a ni définition
+    standard ni définition belge (même contrat que :func:`definition_mot`).
+    """
+    norme = normaliser_mot(mot)
+    if not norme:
+        return None
+    standards = definition_mot(norme, chemin_definitions) or []
+    cles_standards = {_cle_dedup_glose(glose) for glose in standards}
+    belges = charger_definitions_belges(chemin_belges).get(desaccentuer(norme), [])
+    annotees = [{"texte": glose, "origine": "standard"} for glose in standards]
+    for glose in belges:
+        if _cle_dedup_glose(glose) in cles_standards:
+            continue
+        annotees.append({"texte": glose, "origine": "belge"})
+    if not annotees:
+        return None
+    return annotees
+
+
 def assurer_fichiers_modifs(
     chemin_ajoutes: Path,
     chemin_retires: Path,
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/api_pose.py b/src/scrabble/ui/api_pose.py
# (index — ignorable)
index 1386e74..fdc0d23 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/api_pose.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/api_pose.py
# ── Zone modifiée : ligne 438 (19 ligne(s)) dans l'ancienne version → ligne 438 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -438,19 +438,21 @@ class MixinPose:
         l'ordre affiché). Le test est en **lecture seule** : il ne pose aucun
         coup, ne consomme aucun tour et ne modifie en rien l'état de la partie.
         Renvoie ``{"succes": True, "mot": <MOT>, "valide": bool, "definition":
-        [gloses] | None}`` ou, si le brouillon est vide, ``{"succes": False,
-        "erreur": <message>}``. La ``definition`` (ODS8 uniquement, issue #124)
-        est ``None`` quand le mot est invalide ou absent de l'index — l'UI
-        affiche alors « définition indisponible ».
-
-        Restriction à la source active (issue #127) : la définition n'est
-        renvoyée que si la partie est jouée avec ``"ods"`` comme source de
-        dictionnaire (``config["source_dictionnaire"]``, seule source de vérité
-        de la source active — ni ``Partie`` ni ``Dictionnaire`` ne la
-        mémorisent). En source ``"hunspell"``, ``definition`` vaut toujours
-        ``None``, même pour un mot par ailleurs présent dans l'index ODS8, pour
-        rester strictement cohérent avec ce qui valide réellement les coups sur
-        le plateau.
+        [{"texte": ..., "origine": "standard"|"belge"}, ...] | None}`` ou, si
+        le brouillon est vide, ``{"succes": False, "erreur": <message>}``. La
+        ``definition`` est ``None`` quand le mot est invalide ou sans aucune
+        glose — l'UI affiche alors « définition indisponible ».
+
+        Restriction à la source active (issue #127) : les gloses **standards**
+        (ODS8, issue #124) ne sont renvoyées que si la partie est jouée avec
+        ``"ods"`` comme source de dictionnaire (``config["source_dictionnaire"]``,
+        seule source de vérité de la source active — ni ``Partie`` ni
+        ``Dictionnaire`` ne la mémorisent) ; en source ``"hunspell"``, elles
+        sont toujours absentes, pour rester strictement cohérent avec ce qui
+        valide réellement les coups sur le plateau. Les gloses **belges**
+        (issue #276) échappent à cette restriction : elles sont renvoyées dès
+        qu'elles existent, quelle que soit la source active ou le mode
+        Belgicisme de la partie en cours.
         """
         from scrabble.ui import jeu as mod_jeu
         from scrabble.ui.jeu import verifier_mot_dictionnaire
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/jeu.py b/src/scrabble/ui/jeu.py
# (index — ignorable)
index a7bc7b2..bf80059 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/jeu.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/jeu.py
# ── Zone modifiée : ligne 45 (9 ligne(s)) dans l'ancienne version → ligne 45 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -45,9 +45,10 @@ import webview
 from scrabble import journal
 from scrabble.config import AVATARS_DISPONIBLES, THEMES_PLATEAU, charger_config
 from scrabble.dictionnaire.dictionnaire import (
+    CHEMIN_BELGICISMES,
     CHEMIN_DEFINITIONS,
     Trie,
-    definition_mot,
+    definitions_annotees,
     normaliser_mot,
 )
 from scrabble.moteur.ia import Niveau
# ── Zone modifiée : ligne 866 (6 ligne(s)) dans l'ancienne version → ligne 867 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -866,6 +867,7 @@ def verifier_mot_dictionnaire(
     lettres: Any,
     chemin_definitions: Path = CHEMIN_DEFINITIONS,
     source: str = "ods",
+    chemin_belgicismes: Path = CHEMIN_BELGICISMES,
 ) -> dict[str, Any]:
     """Teste l'appartenance au dictionnaire du mot formé par ``lettres``.
 
# ── Zone modifiée : ligne 876 (25 ligne(s)) dans l'ancienne version → ligne 878 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -876,25 +878,26 @@ def verifier_mot_dictionnaire(
     partie ni du dictionnaire.
 
     Renvoie ``{"succes": True, "mot": <MOT>, "valide": bool, "definition":
-    [gloses] | None}`` ; si la suite est vide (après normalisation),
-    ``{"succes": False, "erreur": <message>}``. Un joker (``*``) laissé dans le
-    brouillon n'est pas une lettre fixe : il empêche tout mot d'être trouvé (le
-    test renverra ``valide`` faux), ce qui est le comportement attendu d'un
-    simple test d'appartenance.
-
-    La définition n'est calculée que si le mot est valide **et** que la source
-    active de la partie (``source``) est ``"ods"``, en réutilisant
-    :func:`~scrabble.dictionnaire.dictionnaire.definition_mot` (ODS8 uniquement,
-    même source que l'onglet Dictionnaire des réglages, issue #111). Quand la
-    partie est jouée avec ``"hunspell"`` comme source active (issue #127), la
-    définition est **systématiquement** ``None``, même si le mot valide se
-    trouve, par coïncidence, présent dans l'index ODS8 : « Vérification
-    dictionnaire » reste ainsi strictement cohérent avec ce qui valide les coups
-    sur le plateau et ne laisse pas croire que l'ODS8 joue un rôle dans cette
-    partie. En source ODS, un mot présent seulement dans Hunspell — ou absent de
-    l'index — renvoie aussi ``"definition": None`` : à l'UI d'afficher
-    « définition indisponible ». Un mot invalide renvoie toujours ``None``
-    (aucune définition n'a de sens).
+    [{"texte": ..., "origine": "standard"|"belge"}, ...] | None}`` ; si la
+    suite est vide (après normalisation), ``{"succes": False, "erreur":
+    <message>}``. Un joker (``*``) laissé dans le brouillon n'est pas une
+    lettre fixe : il empêche tout mot d'être trouvé (le test renverra
+    ``valide`` faux), ce qui est le comportement attendu d'un simple test
+    d'appartenance.
+
+    Les gloses sont calculées, pour un mot valide, via
+    :func:`~scrabble.dictionnaire.dictionnaire.definitions_annotees` (issue
+    #276), qui fusionne gloses standards et gloses belges (dédupliquées mot
+    pour mot, cas ``académique``). La source active de la partie (``source``)
+    continue de filtrer les gloses **standards** uniquement, comme avant
+    l'issue #276 : quand la partie est jouée avec ``"hunspell"`` (issue #127),
+    les gloses standards (ODS8) sont retirées du résultat, cohérent avec ce qui
+    valide les coups sur le plateau. Les gloses **belges**, elles, restent
+    toujours affichées quand elles existent, indépendamment de la source et du
+    mode Belgicisme de la partie (permanent, hors périmètre du filtre
+    ``source``). Un mot invalide, ou sans aucune glose (standard ou belge),
+    renvoie ``"definition": None`` : à l'UI d'afficher « définition
+    indisponible ».
     """
     mot = normaliser_mot(_concatener_lettres(lettres))
     if not mot:
# ── Zone modifiée : ligne 903 (11 ligne(s)) dans l'ancienne version → ligne 906 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -903,11 +906,12 @@ def verifier_mot_dictionnaire(
             "erreur": "La zone de brouillon ne contient aucune lettre à vérifier.",
         }
     valide = bool(dictionnaire.contient(mot))
-    definition = (
-        definition_mot(mot, chemin_definitions)
-        if valide and source == "ods"
-        else None
-    )
+    definition = None
+    if valide:
+        annotees = definitions_annotees(mot, chemin_definitions, chemin_belgicismes)
+        if annotees and source != "ods":
+            annotees = [glose for glose in annotees if glose["origine"] != "standard"]
+        definition = annotees or None
     return {
         "succes": True,
         "mot": mot,
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# (index — ignorable)
index eda11b6..c46d556 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.css
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 1885 (6 ligne(s)) dans l'ancienne version → ligne 1885 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1885,6 +1885,28 @@ body {
     font-style: italic;
 }
 
+/* Pastille-drapeau belge miniature (issue #276) : préfixe une glose belge
+   non dupliquée dans la liste, pour la distinguer des gloses standards sans
+   dépendre du mode Belgicisme de la partie en cours. Même dégradé tricolore
+   CSS que .drapeau-belgique (accueil.css) — pas d'asset image, juste un
+   cercle en aplat de couleurs ; dupliqué plutôt que factorisé, les deux
+   fichiers CSS restant scopés chacun à leur écran (convention du projet). */
+.definition-brouillon .drapeau-mini {
+    display: inline-block;
+    width: 12px;
+    height: 12px;
+    margin-right: 4px;
+    border-radius: 50%;
+    vertical-align: middle;
+    flex: 0 0 auto;
+    background: linear-gradient(
+        90deg,
+        #000000 0%, #000000 33.33%,
+        #fae042 33.33%, #fae042 66.66%,
+        #ed2939 66.66%, #ed2939 100%
+    );
+}
+
 /* Modale de détail du score « moins intrusive » (issue #128). Ouverte depuis
    « Derniers coups », elle recouvrait auparavant une grande partie du plateau
    (fond plein écran assombri + panneau large centré), masquant précisément la
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index d3a817f..77ec591 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 1592 (10 ligne(s)) dans l'ancienne version → ligne 1592 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1592,10 +1592,15 @@ document.addEventListener('DOMContentLoaded', async () => {
     }
 
     // Affiche la définition sous le verdict (issue #124). ``definition`` est la
-    // liste de gloses ODS8 (ou null/absente). On n'appelle cette fonction que
-    // pour un mot VALIDE : une liste vide/nulle signifie « pas de définition
-    // dans l'index » (mot Hunspell uniquement) et affiche un message clair,
-    // cohérent avec l'onglet Dictionnaire des réglages (issue #111).
+    // liste de gloses (ou null/absente). On n'appelle cette fonction que pour
+    // un mot VALIDE : une liste vide/nulle signifie « pas de définition dans
+    // l'index » (mot Hunspell uniquement) et affiche un message clair,
+    // cohérent avec l'onglet Dictionnaire des réglages (issue #111). Depuis
+    // l'issue #276, chaque glose est soit une chaîne brute (rétrocompatibilité
+    // si ``definition`` reste un tableau de chaînes dans un cas limite), soit
+    // un objet ``{texte, origine}`` — les gloses d'origine belge affichent une
+    // pastille-drapeau ``.drapeau-mini`` en préfixe, en permanence, quel que
+    // soit le mode Belgicisme de la partie en cours.
     function afficherDefinitionBrouillon(definition) {
         if (!definitionBrouillon) return;
         definitionBrouillon.innerHTML = '';
# ── Zone modifiée : ligne 1603 (8 ligne(s)) dans l'ancienne version → ligne 1608 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1603,8 +1608,17 @@ document.addEventListener('DOMContentLoaded', async () => {
             const ol = document.createElement('ol');
             ol.className = 'definition-gloses';
             definition.forEach((glose) => {
+                const estObjet = glose && typeof glose === 'object';
+                const texte = estObjet ? glose.texte : glose;
+                const origine = estObjet ? glose.origine : 'standard';
                 const li = document.createElement('li');
-                li.textContent = glose;
+                if (origine === 'belge') {
+                    const drapeau = document.createElement('span');
+                    drapeau.className = 'drapeau-mini';
+                    drapeau.title = 'Définition belge';
+                    li.appendChild(drapeau);
+                }
+                li.appendChild(document.createTextNode(texte));
                 ol.appendChild(li);
             });
             definitionBrouillon.appendChild(ol);
# (diff du fichier suivant)
diff --git a/tests/test_dictionnaire.py b/tests/test_dictionnaire.py
# (index — ignorable)
index a4836be..d7a7e52 100644
# (avant — fichier suivant)
--- a/tests/test_dictionnaire.py
# (après — fichier suivant)
+++ b/tests/test_dictionnaire.py
# ── Zone modifiée : ligne 25 (12 ligne(s)) dans l'ancienne version → ligne 25 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,12 +25,14 @@ from scrabble.dictionnaire.dictionnaire import (
     assurer_fichiers_modifs,
     charger_belgicismes,
     charger_definitions,
+    charger_definitions_belges,
     charger_ods,
     chemins_modifs,
     construire_ensemble_ia,
     construire_ensemble_mots,
     construire_trie,
     definition_mot,
+    definitions_annotees,
     desaccentuer,
     ensemble_classiques,
     est_mot_scrabble,
# ── Zone modifiée : ligne 666 (6 ligne(s)) dans l'ancienne version → ligne 668 (149 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -666,6 +668,149 @@ def test_obtenir_trie_cache_ancien_sans_champ_belge_reste_valide_en_mode_france(
     assert "CHAT" in trie_relu
 
 
+# --------------------------------------------------------------------------- #
+# Définitions belges + fusion annotée (loupe), issue #276
+# --------------------------------------------------------------------------- #
+
+def _ecrire_csv_definitions_belges(chemin, lignes):
+    """Écrit un CSV belgicismes factice avec définition personnalisée.
+
+    ``lignes`` : liste de ``(mot, definition_brute, existe_sens_standard)``.
+    """
+    with open(chemin, "w", encoding="utf-8", newline="") as fichier:
+        ecrivain = csv.writer(fichier)
+        ecrivain.writerow(
+            ["mot", "définition(s) belge(s)", "origine_wallonne", "existe_sens_standard"]
+        )
+        for mot, definition, existe in lignes:
+            ecrivain.writerow([mot, definition, "non", existe])
+
+
+def test_charger_definitions_belges_ne_filtre_pas_existe_sens_standard(tmp_path):
+    """Contrairement à charger_belgicismes, TOUTES les lignes sont chargées, y
+    compris ``existe_sens_standard=oui`` (cas ``académique``, issue #276)."""
+    chemin = tmp_path / "belgicismes.csv"
+    _ecrire_csv_definitions_belges(
+        chemin,
+        [
+            ("academique", "Universitaire. | Relatif à un retard toléré.", "oui"),
+            ("sketter", "Casser, fatiguer.", "non"),
+        ],
+    )
+
+    definitions = charger_definitions_belges(chemin)
+
+    assert definitions["ACADEMIQUE"] == [
+        "Universitaire.",
+        "Relatif à un retard toléré.",
+    ]
+    assert definitions["SKETTER"] == ["Casser, fatiguer."]
+
+
+def test_charger_definitions_belges_fichier_absent(tmp_path):
+    """Fichier absent : dict vide, sans erreur (comme charger_definitions)."""
+    assert charger_definitions_belges(tmp_path / "absent.csv") == {}
+
+
+def test_definitions_annotees_mot_belge_sans_equivalent_standard(tmp_path):
+    """« sketter » : aucune glose standard, toutes les gloses sont belges."""
+    chemin_defs = tmp_path / "definitions.json"
+    chemin_defs.write_text(json.dumps({}), encoding="utf-8")
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_definitions_belges(chemin_belges, [("sketter", "Casser, fatiguer.", "non")])
+
+    annotees = definitions_annotees("sketter", chemin_defs, chemin_belges)
+
+    assert annotees == [{"texte": "Casser, fatiguer.", "origine": "belge"}]
+
+
+def test_definitions_annotees_mot_avec_glose_belge_non_dupliquee(tmp_path):
+    """Une glose standard suivie d'une glose belge non dupliquée (drapeau)."""
+    chemin_defs = tmp_path / "definitions.json"
+    chemin_defs.write_text(
+        json.dumps({"CHAT": ["Petit félin domestique."]}), encoding="utf-8"
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_definitions_belges(chemin_belges, [("chat", "Loquet de porte.", "non")])
+
+    annotees = definitions_annotees("chat", chemin_defs, chemin_belges)
+
+    assert annotees == [
+        {"texte": "Petit félin domestique.", "origine": "standard"},
+        {"texte": "Loquet de porte.", "origine": "belge"},
+    ]
+
+
+def test_definitions_annotees_academique_deduplique_sans_doublon(tmp_path):
+    """Cas ``académique`` (issue #276) : les deux gloses belges existent déjà
+    mot pour mot dans le Wiktionnaire filtré — aucun doublon, aucune glose
+    belge ajoutée, pas de drapeau sur les gloses partagées."""
+    chemin_defs = tmp_path / "definitions.json"
+    chemin_defs.write_text(
+        json.dumps(
+            {
+                "ACADEMIQUE": [
+                    "Qui se rapporte aux académies.",
+                    "Universitaire.",
+                    "Relatif à un retard toléré.",
+                ]
+            }
+        ),
+        encoding="utf-8",
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_definitions_belges(
+        chemin_belges,
+        [("academique", "Universitaire. | Relatif à un retard toléré.", "oui")],
+    )
+
+    annotees = definitions_annotees("academique", chemin_defs, chemin_belges)
+
+    assert annotees == [
+        {"texte": "Qui se rapporte aux académies.", "origine": "standard"},
+        {"texte": "Universitaire.", "origine": "standard"},
+        {"texte": "Relatif à un retard toléré.", "origine": "standard"},
+    ]
+    assert all(glose["origine"] == "standard" for glose in annotees)
+
+
+def test_definitions_annotees_dedup_insensible_casse_espaces_ponctuation(tmp_path):
+    """La déduplication ignore casse, espaces superflus et ponctuation finale."""
+    chemin_defs = tmp_path / "definitions.json"
+    chemin_defs.write_text(json.dumps({"MOT": ["Une   glose.  "]}), encoding="utf-8")
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_definitions_belges(chemin_belges, [("mot", "une glose", "non")])
+
+    annotees = definitions_annotees("mot", chemin_defs, chemin_belges)
+
+    assert annotees == [{"texte": "Une   glose.  ", "origine": "standard"}]
+
+
+def test_definitions_annotees_mot_sans_definition_belge_comportement_inchange(tmp_path):
+    """Un mot sans entrée dans le CSV belge : uniquement les gloses standards,
+    comportement strictement inchangé (mêmes gloses, simplement annotées)."""
+    chemin_defs = tmp_path / "definitions.json"
+    chemin_defs.write_text(
+        json.dumps({"CHIEN": ["Mammifère domestique."]}), encoding="utf-8"
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_definitions_belges(chemin_belges, [("sketter", "Casser, fatiguer.", "non")])
+
+    annotees = definitions_annotees("chien", chemin_defs, chemin_belges)
+
+    assert annotees == [{"texte": "Mammifère domestique.", "origine": "standard"}]
+
+
+def test_definitions_annotees_mot_totalement_absent_renvoie_none(tmp_path):
+    """Ni définition standard ni définition belge : None (comme definition_mot)."""
+    chemin_defs = tmp_path / "definitions.json"
+    chemin_defs.write_text(json.dumps({}), encoding="utf-8")
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_definitions_belges(chemin_belges, [("sketter", "Casser, fatiguer.", "non")])
+
+    assert definitions_annotees("zorglub", chemin_defs, chemin_belges) is None
+
+
 # --------------------------------------------------------------------------- #
 # Désaccentuation + définitions (issue #111, onglet Dictionnaire)
 # --------------------------------------------------------------------------- #
# (diff du fichier suivant)
diff --git a/tests/test_jeu_brouillon.py b/tests/test_jeu_brouillon.py
# (index — ignorable)
index e6d1514..35ed93d 100644
# (avant — fichier suivant)
--- a/tests/test_jeu_brouillon.py
# (après — fichier suivant)
+++ b/tests/test_jeu_brouillon.py
# ── Zone modifiée : ligne 6 (6 ligne(s)) dans l'ancienne version → ligne 6 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -6,6 +6,7 @@ mutation de la partie ni du dictionnaire.
 Classe extraite de ``test_jeu.py`` (issue #257).
 """
 
+import csv
 import json
 
 import pytest
# ── Zone modifiée : ligne 53 (17 ligne(s)) dans l'ancienne version → ligne 54 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -53,17 +54,25 @@ class TestVerifierMotDictionnaire:
             encoding="utf-8",
         )
         res = verifier_mot_dictionnaire(
-            _DicoMots("CHAT"), ["C", "H", "A", "T"], fichier
+            _DicoMots("CHAT"),
+            ["C", "H", "A", "T"],
+            fichier,
+            chemin_belgicismes=tmp_path / "absent_belges.csv",
         )
         assert res["valide"] is True
-        assert res["definition"] == ["Petit félin domestique."]
+        assert res["definition"] == [
+            {"texte": "Petit félin domestique.", "origine": "standard"}
+        ]
 
     def test_definition_mot_hunspell_sans_definition(self, tmp_path):
         # Mot valide mais absent de l'index (cas Hunspell uniquement) : None.
         fichier = tmp_path / "definitions.json"
         fichier.write_text(json.dumps({"CHAT": ["Félin."]}), encoding="utf-8")
         res = verifier_mot_dictionnaire(
-            _DicoMots("KWYJIBO"), ["K", "W", "Y", "J", "I", "B", "O"], fichier
+            _DicoMots("KWYJIBO"),
+            ["K", "W", "Y", "J", "I", "B", "O"],
+            fichier,
+            chemin_belgicismes=tmp_path / "absent_belges.csv",
         )
         assert res["valide"] is True
         assert res["definition"] is None
# ── Zone modifiée : ligne 72 (7 ligne(s)) dans l'ancienne version → ligne 81 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -72,7 +81,12 @@ class TestVerifierMotDictionnaire:
         # Même si le mot figure dans l'index, un mot invalide reste sans déf.
         fichier = tmp_path / "definitions.json"
         fichier.write_text(json.dumps({"XYZ": ["Bruit."]}), encoding="utf-8")
-        res = verifier_mot_dictionnaire(_DicoMots("CHAT"), ["X", "Y", "Z"], fichier)
+        res = verifier_mot_dictionnaire(
+            _DicoMots("CHAT"),
+            ["X", "Y", "Z"],
+            fichier,
+            chemin_belgicismes=tmp_path / "absent_belges.csv",
+        )
         assert res["valide"] is False
         assert res["definition"] is None
 
# ── Zone modifiée : ligne 85 (10 ligne(s)) dans l'ancienne version → ligne 99 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -85,10 +99,16 @@ class TestVerifierMotDictionnaire:
             encoding="utf-8",
         )
         res = verifier_mot_dictionnaire(
-            _DicoMots("CHAT"), ["C", "H", "A", "T"], fichier, source="ods"
+            _DicoMots("CHAT"),
+            ["C", "H", "A", "T"],
+            fichier,
+            source="ods",
+            chemin_belgicismes=tmp_path / "absent_belges.csv",
         )
         assert res["valide"] is True
-        assert res["definition"] == ["Petit félin domestique."]
+        assert res["definition"] == [
+            {"texte": "Petit félin domestique.", "origine": "standard"}
+        ]
 
     def test_definition_jamais_en_source_hunspell(self, tmp_path):
         # Issue #127 : mot valide en Hunspell, présent PAR COÏNCIDENCE dans
# ── Zone modifiée : ligne 99 (11 ligne(s)) dans l'ancienne version → ligne 119 (96 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -99,11 +119,96 @@ class TestVerifierMotDictionnaire:
             encoding="utf-8",
         )
         res = verifier_mot_dictionnaire(
-            _DicoMots("CHAT"), ["C", "H", "A", "T"], fichier, source="hunspell"
+            _DicoMots("CHAT"),
+            ["C", "H", "A", "T"],
+            fichier,
+            source="hunspell",
+            chemin_belgicismes=tmp_path / "absent_belges.csv",
         )
         assert res["valide"] is True
         assert res["definition"] is None
 
+    def test_definition_belge_affichee_independamment_de_la_source(self, tmp_path):
+        # Issue #276 : une glose belge non dupliquée reste affichée même en
+        # source Hunspell — seules les gloses standards sont filtrées par la
+        # source active, jamais les gloses belges (permanent).
+        fichier_defs = tmp_path / "definitions.json"
+        fichier_defs.write_text(
+            json.dumps({"CHAT": ["Petit félin domestique."]}), encoding="utf-8"
+        )
+        fichier_belges = tmp_path / "belgicismes.csv"
+        fichier_belges.write_text(
+            "mot,définition(s) belge(s),origine_wallonne,existe_sens_standard\n"
+            "chat,Loquet de porte.,non,oui\n",
+            encoding="utf-8",
+        )
+        res = verifier_mot_dictionnaire(
+            _DicoMots("CHAT"),
+            ["C", "H", "A", "T"],
+            fichier_defs,
+            source="hunspell",
+            chemin_belgicismes=fichier_belges,
+        )
+        assert res["valide"] is True
+        # La glose standard est filtrée (source Hunspell), la glose belge reste.
+        assert res["definition"] == [{"texte": "Loquet de porte.", "origine": "belge"}]
+
+    def test_definition_academique_deduplique_sans_doublon(self, tmp_path):
+        # Cas académique (issue #276) : les deux gloses belges sont déjà mot
+        # pour mot dans le Wiktionnaire filtré — aucun doublon affiché.
+        fichier_defs = tmp_path / "definitions.json"
+        fichier_defs.write_text(
+            json.dumps(
+                {
+                    "ACADEMIQUE": [
+                        "Qui se rapporte aux académies.",
+                        "Universitaire.",
+                        "Relatif à un retard toléré.",
+                    ]
+                }
+            ),
+            encoding="utf-8",
+        )
+        fichier_belges = tmp_path / "belgicismes.csv"
+        fichier_belges.write_text(
+            "mot,définition(s) belge(s),origine_wallonne,existe_sens_standard\n"
+            "academique,Universitaire. | Relatif à un retard toléré.,non,oui\n",
+            encoding="utf-8",
+        )
+        res = verifier_mot_dictionnaire(
+            _DicoMots("ACADEMIQUE"),
+            list("ACADEMIQUE"),
+            fichier_defs,
+            chemin_belgicismes=fichier_belges,
+        )
+        assert res["valide"] is True
+        assert res["definition"] == [
+            {"texte": "Qui se rapporte aux académies.", "origine": "standard"},
+            {"texte": "Universitaire.", "origine": "standard"},
+            {"texte": "Relatif à un retard toléré.", "origine": "standard"},
+        ]
+        assert all(glose["origine"] == "standard" for glose in res["definition"])
+
+    def test_definition_mot_belge_sans_equivalent_standard(self, tmp_path):
+        # « sketter » : aucune glose standard, uniquement des gloses belges.
+        fichier_defs = tmp_path / "definitions.json"
+        fichier_defs.write_text(json.dumps({}), encoding="utf-8")
+        fichier_belges = tmp_path / "belgicismes.csv"
+        with open(fichier_belges, "w", encoding="utf-8", newline="") as fichier:
+            ecrivain = csv.writer(fichier)
+            ecrivain.writerow(
+                ["mot", "définition(s) belge(s)", "origine_wallonne", "existe_sens_standard"]
+            )
+            ecrivain.writerow(["sketter", "Casser, fatiguer.", "non", "non"])
+        res = verifier_mot_dictionnaire(
+            _DicoMots("SKETTER"),
+            list("SKETTER"),
+            fichier_defs,
+            chemin_belgicismes=fichier_belges,
+        )
+        assert res["valide"] is True
+        assert res["definition"] == [{"texte": "Casser, fatiguer.", "origine": "belge"}]
+
     def test_accepte_chaine_deja_assemblee(self):
         res = verifier_mot_dictionnaire(_DicoMots("CHAT"), "chat")
         assert res["mot"] == "CHAT"
# ── Zone modifiée : ligne 156 (24 ligne(s)) dans l'ancienne version → ligne 261 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -156,24 +261,30 @@ class TestVerifierMotDictionnaire:
             lambda: {"source_dictionnaire": "ods"},
         )
         monkeypatch.setattr(
-            "scrabble.ui.jeu.definition_mot",
-            lambda mot, chemin=None: ["Petit félin domestique."],
+            "scrabble.ui.jeu.definitions_annotees",
+            lambda mot, chemin_definitions=None, chemin_belgicismes=None: [
+                {"texte": "Petit félin domestique.", "origine": "standard"}
+            ],
         )
         api = ApiJeu(_partie_simple(), None)
         res = api.verifier_mot(["C", "H", "A", "T"])
         assert res["valide"] is True
-        assert res["definition"] == ["Petit félin domestique."]
+        assert res["definition"] == [
+            {"texte": "Petit félin domestique.", "origine": "standard"}
+        ]
 
     def test_api_pas_de_definition_en_source_hunspell(self, monkeypatch):
-        # Issue #127 : source active Hunspell → jamais de définition, même si le
-        # mot valide est par coïncidence présent dans l'index ODS8.
+        # Issue #127 : source active Hunspell → jamais de définition STANDARD,
+        # même si le mot valide est par coïncidence présent dans l'index ODS8.
         monkeypatch.setattr(
             "scrabble.ui.jeu.charger_config",
             lambda: {"source_dictionnaire": "hunspell"},
         )
         monkeypatch.setattr(
-            "scrabble.ui.jeu.definition_mot",
-            lambda mot, chemin=None: ["Petit félin domestique."],
+            "scrabble.ui.jeu.definitions_annotees",
+            lambda mot, chemin_definitions=None, chemin_belgicismes=None: [
+                {"texte": "Petit félin domestique.", "origine": "standard"}
+            ],
         )
         api = ApiJeu(_partie_simple(), None)
         res = api.verifier_mot(["C", "H", "A", "T"])
