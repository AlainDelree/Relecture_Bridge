acf44f1

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit acf44f1
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 16:08:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #252 : test anti-collision de noms entre mixins (hors stubs de typage)
    
    Améliore le test #251 pour distinguer stubs de typage et vraies implémentations :
    
    - Utilise l'AST pour une détection fiable des stubs (corps = `...` seul ou
      après docstring), au lieu d'une simple heuristique textuelle.
    - Vérifie qu'aucune vraie implémentation n'apparaît dans plus d'un mixin.
    - Ajoute un second test vérifiant l'ordre MRO : si un nom existe à la fois
      comme stub et comme vraie implémentation, le mixin avec l'implémentation
      doit apparaître AVANT celui avec le stub dans le MRO (sinon le stub
      masquerait silencieusement la vraie méthode).
    
    749 tests passent (747 + 2 tests anti-collision).
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/test_api_jeu_mixins.py b/tests/test_api_jeu_mixins.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index cf931f9..1144714 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/tests/test_api_jeu_mixins.py
# ── Version APRÈS ce commit.
+++ b/tests/test_api_jeu_mixins.py
# ── Zone modifiée : ligne 1 (10 ligne(s)) dans l'ancienne version → ligne 1 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,10 +1,23 @@
-"""Test anti-collision de noms entre les mixins d'ApiJeu (issue #251).
+"""Test anti-collision de noms entre les mixins d'ApiJeu (issues #251, #252).
 
-Ce test vérifie mécaniquement qu'aucun nom de méthode n'est défini dans plus
-d'un mixin (ou dans ApiJeu de base), ce qui serait un bug silencieux où l'un
-écraserait l'autre selon l'ordre du MRO.
+Ce test vérifie mécaniquement :
+
+1. Qu'aucun nom de méthode **avec une vraie implémentation** (non-stub) n'apparaît
+   dans plus d'un des mixins ou dans ApiJeu de base — un doublon serait un bug
+   silencieux où l'un écraserait l'autre selon l'ordre du MRO.
+
+2. Que pour tout nom présent à la fois comme stub (corps ``...``) dans un mixin
+   ET comme vraie implémentation dans un autre, l'ordre d'héritage déclaré sur
+   ApiJeu place bien le mixin avec la vraie implémentation AVANT celui avec le
+   stub — sinon le MRO ferait passer le stub en premier, masquant silencieusement
+   la vraie méthode.
+
+**Point important** : plusieurs mixins déclarent des méthodes "stub" à but de
+typage uniquement (corps réduit à ``...``, ex. ``def _diffuser(self) -> None: ...``).
+Ce ne sont PAS de vraies collisions et le test les ignore.
 """
 
+import ast
 import inspect
 
 from scrabble.ui.api_diffusion import MixinDiffusion
# ── Zone modifiée : ligne 21 (8 ligne(s)) dans l'ancienne version → ligne 34 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -21,8 +34,12 @@ def _est_stub_protocole(valeur) -> bool:
     Les mixins déclarent des méthodes attendues d'autres mixins pour l'annotation
     de type, avec un corps réduit à ``...``. Ces stubs ne sont pas de vraies
     implémentations et ne constituent pas des collisions.
+
+    Utilise l'AST pour une détection fiable : le corps est un stub si et seulement
+    s'il ne contient que :
+    - ``...`` seul (``Expr(Constant(Ellipsis))``), ou
+    - une docstring suivie de ``...`` (``Expr(Constant(str))``, puis ``Expr(Constant(Ellipsis))``).
     """
-    # Déballer les staticmethod/classmethod pour accéder à la fonction sous-jacente
     if isinstance(valeur, staticmethod):
         valeur = valeur.__func__
     elif isinstance(valeur, classmethod):
# ── Zone modifiée : ligne 31 (60 ligne(s)) dans l'ancienne version → ligne 48 (166 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,60 +48,166 @@ def _est_stub_protocole(valeur) -> bool:
         return False
     try:
         source = inspect.getsource(valeur)
-        lignes = [l.strip() for l in source.splitlines() if l.strip()]
-        # Stub simple sur une ligne ou décorateur + stub sur deux lignes
-        if len(lignes) == 1 and lignes[0].endswith(": ..."):
-            return True
-        if len(lignes) == 2 and lignes[0].startswith("@") and lignes[1].endswith(": ..."):
-            return True
+        # Dé-indenter la source pour que l'AST la parse (elle peut être indentée
+        # dans la classe).
+        source = inspect.cleandoc(source)
+        tree = ast.parse(source)
+        # L'AST contient un Module avec une seule FunctionDef.
+        if not tree.body or not isinstance(tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef)):
+            return False
+        func_def = tree.body[0]
+        body = func_def.body
+        # Corps vide interdit en Python, mais bon.
+        if not body:
+            return False
+        # Ignorer une éventuelle docstring en tête.
+        debut = 0
+        if (
+            isinstance(body[0], ast.Expr)
+            and isinstance(body[0].value, ast.Constant)
+            and isinstance(body[0].value.value, str)
+        ):
+            debut = 1
+        reste = body[debut:]
+        # Le corps est un stub s'il ne contient qu'un ``...`` après la docstring.
+        if len(reste) == 1 and isinstance(reste[0], ast.Expr):
+            noeud = reste[0].value
+            # ``Ellipsis`` peut être représenté comme Constant(Ellipsis) ou Ellipsis.
+            if isinstance(noeud, ast.Constant) and noeud.value is ...:
+                return True
+            if isinstance(noeud, ast.Ellipsis):  # Python < 3.8 (compat)
+                return True
         return False
-    except (OSError, TypeError):
+    except (OSError, TypeError, SyntaxError):
         return False
 
 
-def _methodes_directes(cls: type) -> set[str]:
-    """Renvoie les noms de méthodes/fonctions définies directement sur ``cls``.
+def _methodes_directes(cls: type) -> dict[str, bool]:
+    """Renvoie les méthodes définies directement sur ``cls`` avec leur nature.
 
     On ne considère que les attributs appelables (``callable``) définis dans le
     ``__dict__`` de la classe — pas ceux hérités via le MRO. Les annotations de
-    type, les attributs de données (non-callable) et les stubs de protocole
-    (méthodes avec corps ``...``) sont exclus.
+    type et les attributs de données (non-callable) sont exclus.
+
+    Retourne un dictionnaire ``{nom: est_stub}``, où ``est_stub`` vaut ``True``
+    si la méthode est un stub de typage (corps ``...``), ``False`` sinon.
     """
-    noms = set()
+    resultat: dict[str, bool] = {}
     for nom, valeur in vars(cls).items():
-        if _est_stub_protocole(valeur):
-            continue
         if callable(valeur) or isinstance(valeur, (classmethod, staticmethod, property)):
-            noms.add(nom)
-    return noms
+            est_stub = _est_stub_protocole(valeur)
+            resultat[nom] = est_stub
+    return resultat
 
 
-def test_absence_collision_noms_mixins():
-    """Vérifie qu'aucun nom de méthode n'apparaît dans plus d'un mixin/classe."""
-    classes = {
-        "MixinDiffusion": MixinDiffusion,
-        "MixinTirageOrdre": MixinTirageOrdre,
-        "MixinPose": MixinPose,
-        "MixinEchange": MixinEchange,
-        "MixinTourEtFinPartie": MixinTourEtFinPartie,
-        "ApiJeu": ApiJeu,
-    }
+# Ordre d'héritage selon le MRO réel de Python : la classe elle-même est
+# en premier, puis les mixins dans l'ordre de déclaration (premier = priorité
+# MRO la plus haute).
+ORDRE_HERITAGE = [
+    "ApiJeu",
+    "MixinDiffusion",
+    "MixinTirageOrdre",
+    "MixinTourEtFinPartie",
+    "MixinPose",
+    "MixinEchange",
+]
+
+CLASSES = {
+    "ApiJeu": ApiJeu,
+    "MixinDiffusion": MixinDiffusion,
+    "MixinTirageOrdre": MixinTirageOrdre,
+    "MixinTourEtFinPartie": MixinTourEtFinPartie,
+    "MixinPose": MixinPose,
+    "MixinEchange": MixinEchange,
+}
+
 
+def test_absence_collision_noms_mixins():
+    """Vérifie qu'aucun nom de méthode réelle n'apparaît dans plus d'un mixin."""
     # Dictionnaire : nom de méthode -> liste des classes où il est défini
-    occurrences: dict[str, list[str]] = {}
+    # avec une vraie implémentation (non-stub).
+    occurrences_reelles: dict[str, list[str]] = {}
 
-    for nom_classe, cls in classes.items():
-        for methode in _methodes_directes(cls):
-            if methode not in occurrences:
-                occurrences[methode] = []
-            occurrences[methode].append(nom_classe)
+    for nom_classe, cls in CLASSES.items():
+        methodes = _methodes_directes(cls)
+        for methode, est_stub in methodes.items():
+            if not est_stub:
+                if methode not in occurrences_reelles:
+                    occurrences_reelles[methode] = []
+                occurrences_reelles[methode].append(nom_classe)
 
-    # Filtrer les doublons (noms définis dans plus d'une source)
-    doublons = {nom: sources for nom, sources in occurrences.items() if len(sources) > 1}
+    # Filtrer les doublons (noms définis dans plus d'une source AVEC une vraie
+    # implémentation).
+    doublons = {
+        nom: sources
+        for nom, sources in occurrences_reelles.items()
+        if len(sources) > 1
+    }
 
     if doublons:
-        # Construire un message d'erreur clair listant les doublons
-        lignes = ["Collision(s) de noms entre mixins ApiJeu :"]
+        lignes = ["Collision(s) de noms entre mixins ApiJeu (vraies implémentations) :"]
         for nom, sources in sorted(doublons.items()):
             lignes.append(f"  - {nom!r} défini dans : {', '.join(sources)}")
         raise AssertionError("\n".join(lignes))
+
+
+def test_ordre_mro_stub_vs_implementation():
+    """Vérifie que les stubs ne masquent pas les vraies implémentations via le MRO.
+
+    Pour chaque nom de méthode qui apparaît à la fois comme stub dans un mixin
+    et comme vraie implémentation dans un autre, vérifie que le mixin avec
+    l'implémentation réelle apparaît AVANT le mixin avec le stub dans l'ordre
+    d'héritage déclaré sur ApiJeu. Sinon, le MRO Python ferait passer le stub
+    en premier, masquant silencieusement la vraie méthode.
+    """
+    # Collecte de toutes les méthodes avec leur nature par classe.
+    methodes_par_classe: dict[str, dict[str, bool]] = {}
+    for nom_classe, cls in CLASSES.items():
+        methodes_par_classe[nom_classe] = _methodes_directes(cls)
+
+    # Pour chaque nom de méthode, trouver où il apparaît comme stub et où comme
+    # vraie implémentation.
+    tous_noms: set[str] = set()
+    for methodes in methodes_par_classe.values():
+        tous_noms.update(methodes.keys())
+
+    erreurs: list[str] = []
+
+    for nom in sorted(tous_noms):
+        classes_stub: list[str] = []
+        classes_impl: list[str] = []
+
+        for nom_classe in ORDRE_HERITAGE:
+            methodes = methodes_par_classe[nom_classe]
+            if nom in methodes:
+                if methodes[nom]:  # est_stub
+                    classes_stub.append(nom_classe)
+                else:
+                    classes_impl.append(nom_classe)
+
+        # S'il y a à la fois des stubs ET des implémentations, vérifier l'ordre.
+        if classes_stub and classes_impl:
+            # Trouver le rang du premier stub et de la première implémentation
+            # dans l'ordre d'héritage (MRO).
+            rang_premier_stub = min(ORDRE_HERITAGE.index(c) for c in classes_stub)
+            rang_premiere_impl = min(ORDRE_HERITAGE.index(c) for c in classes_impl)
+
+            # Si un stub apparaît AVANT la première implémentation, c'est un
+            # problème : le MRO fera passer le stub en premier, masquant
+            # silencieusement la vraie méthode.
+            if rang_premier_stub < rang_premiere_impl:
+                premier_stub = ORDRE_HERITAGE[rang_premier_stub]
+                premiere_impl = ORDRE_HERITAGE[rang_premiere_impl]
+                erreurs.append(
+                    f"  - {nom!r} : stub dans {premier_stub} (rang {rang_premier_stub}) "
+                    f"AVANT implémentation dans {premiere_impl} (rang {rang_premiere_impl})"
+                )
+
+    if erreurs:
+        msg = (
+            "Ordre MRO dangereux : stub(s) masquant silencieusement la vraie implémentation :\n"
+            + "\n".join(erreurs)
+            + "\n\nSolution : réordonner les mixins dans la déclaration de ApiJeu "
+            "pour que le mixin avec l'implémentation apparaisse AVANT celui avec le stub."
+        )
+        raise AssertionError(msg)
