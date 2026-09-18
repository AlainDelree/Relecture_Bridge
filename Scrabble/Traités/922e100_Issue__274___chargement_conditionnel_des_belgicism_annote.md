922e100

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 922e100
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 22:15:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #274 : chargement conditionnel des belgicismes dans le dictionnaire de validation
    
    Quand ConfigPartie.mode_belgicisme est actif, les mots de
    belgicismes_a_revoir.csv sans équivalent standard (existe_sens_standard
    != "oui") rejoignent le dictionnaire de validation (joueur + IA) :
    (source ∪ ajoutés ∪ belges) − retirés. Le cache pickle (Trie complet et
    Trie IA) est étendu d'une clé "belge" qui invalide le cache sur
    changement de mode ; le CSV est surveillé par mtime en mode actif.
    ApiAccueil.lancer_partie() transmet mode_belgicisme à obtenir_trie() et
    obtenir_trie_ia(). Mode par défaut (France) : comportement inchangé.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/dictionnaire/dictionnaire.py b/src/scrabble/dictionnaire/dictionnaire.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 225a615..98e0e36 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/dictionnaire/dictionnaire.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/dictionnaire/dictionnaire.py
# ── Zone modifiée : ligne 39 (6 ligne(s)) dans l'ancienne version → ligne 39 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -39,6 +39,7 @@ configurée change.
 
 from __future__ import annotations
 
+import csv
 import json
 import pickle
 import re
# ── Zone modifiée : ligne 96 (6 ligne(s)) dans l'ancienne version → ligne 97 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -96,6 +97,12 @@ CHEMINS_CLASSIQUES: tuple[Path, Path] = (
 # avertissement journalisé — voir :func:`construire_ensemble_ia`.
 CHEMIN_MOTS_COURANTS = DOSSIER_DICO / "mots_courants.txt"
 
+# Belgicismes à revoir (issue #274) : CSV colonnes ``mot`` /
+# ``définition(s) belge(s)`` / ``origine_wallonne`` / ``existe_sens_standard``,
+# maintenu manuellement. Chargé uniquement quand le mode Belgicisme est actif
+# (``ConfigPartie.mode_belgicisme``) — voir :func:`charger_belgicismes`.
+CHEMIN_BELGICISMES = DOSSIER_DICO / "belgicismes_a_revoir.csv"
+
 CHEMIN_CACHE = DOSSIER_DICO / "trie_cache.pkl"
 # Cache disque du Trie restreint de l'IA (issue #206), distinct du cache du Trie
 # complet. Invalidé par mtime des mêmes sources que le Trie complet, plus
# ── Zone modifiée : ligne 195 (6 ligne(s)) dans l'ancienne version → ligne 202 (36 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -195,6 +202,36 @@ def charger_ods(chemin: Path = CHEMIN_ODS) -> set[str]:
     return lire_liste_mots(chemin)
 
 
+def charger_belgicismes(chemin: Path = CHEMIN_BELGICISMES) -> set[str]:
+    """Charge les belgicismes sans équivalent standard (mode Belgicisme, issue #274).
+
+    Lit ``belgicismes_a_revoir.csv`` (colonnes ``mot``, ``définition(s) belge(s)``,
+    ``origine_wallonne``, ``existe_sens_standard``) et ne retient que les lignes
+    où ``existe_sens_standard`` (normalisé, insensible à la casse/espaces) est
+    différent de ``"oui"`` : les mots déjà notés ``oui`` existent déjà en
+    français standard, donc déjà dans le dictionnaire via sa source normale — ne
+    pas les réajouter ici évite tout doublon. Leurs définitions belges
+    additionnelles relèvent d'un futur chantier (la loupe), hors périmètre.
+
+    Fichier absent toléré (``set()``, aucune exception), comme
+    :func:`lire_liste_mots`.
+    """
+    mots: set[str] = set()
+    try:
+        with open(chemin, "r", encoding="utf-8", newline="") as fichier:
+            lecteur = csv.DictReader(fichier)
+            for ligne in lecteur:
+                existe = (ligne.get("existe_sens_standard") or "").strip().lower()
+                if existe == "oui":
+                    continue
+                mot = normaliser_mot(ligne.get("mot") or "")
+                if mot:
+                    mots.add(mot)
+    except (FileNotFoundError, IsADirectoryError, OSError):
+        return set()
+    return mots
+
+
 # --------------------------------------------------------------------------- #
 # Définitions (index mot → liste de définitions), restreint à l'ODS8
 # --------------------------------------------------------------------------- #
# ── Zone modifiée : ligne 773 (6 ligne(s)) dans l'ancienne version → ligne 810 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -773,6 +810,8 @@ def _sources_pertinentes(
     base_hunspell: Path,
     chemin_ajoutes: Path,
     chemin_retires: Path,
+    mode_belgicisme: bool = False,
+    chemin_belgicismes: Path = CHEMIN_BELGICISMES,
 ) -> list[Path]:
     """Liste des fichiers dont la modification doit invalider le cache."""
     if source == "hunspell":
# ── Zone modifiée : ligne 783 (11 ligne(s)) dans l'ancienne version → ligne 822 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -783,11 +822,18 @@ def _sources_pertinentes(
     else:
         fichiers = [chemin_ods]
     fichiers += [chemin_ajoutes, chemin_retires]
+    if mode_belgicisme:
+        fichiers.append(chemin_belgicismes)
     return fichiers
 
 
-def _cache_valide(chemin_cache: Path, source: str, sources: list[Path]) -> bool:
-    """Vrai si le cache existe, cible la bonne source et n'est pas périmé."""
+def _cache_valide(
+    chemin_cache: Path,
+    source: str,
+    sources: list[Path],
+    mode_belgicisme: bool = False,
+) -> bool:
+    """Vrai si le cache existe, cible la bonne source/mode et n'est pas périmé."""
     if not chemin_cache.exists():
         return False
     try:
# ── Zone modifiée : ligne 797 (7 ligne(s)) dans l'ancienne version → ligne 843 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -797,7 +843,11 @@ def _cache_valide(chemin_cache: Path, source: str, sources: list[Path]) -> bool:
         return False
     if not isinstance(entete, dict):
         return False
-    if entete.get("version") != VERSION_CACHE or entete.get("source") != source:
+    if (
+        entete.get("version") != VERSION_CACHE
+        or entete.get("source") != source
+        or entete.get("belge", False) != mode_belgicisme
+    ):
         return False
     mtime_cache = chemin_cache.stat().st_mtime
     for chemin in sources:
# ── Zone modifiée : ligne 819 (10 ligne(s)) dans l'ancienne version → ligne 869 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -819,10 +869,12 @@ def _lire_trie_cache(chemin_cache: Path) -> Trie | None:
     return None
 
 
-def _ecrire_trie_cache(chemin_cache: Path, source: str, trie: Trie) -> None:
-    """Sérialise le Trie et son en-tête (version + source) dans le cache."""
+def _ecrire_trie_cache(
+    chemin_cache: Path, source: str, trie: Trie, mode_belgicisme: bool = False
+) -> None:
+    """Sérialise le Trie et son en-tête (version + source + mode) dans le cache."""
     chemin_cache.parent.mkdir(parents=True, exist_ok=True)
-    entete = {"version": VERSION_CACHE, "source": source}
+    entete = {"version": VERSION_CACHE, "source": source, "belge": mode_belgicisme}
     with open(chemin_cache, "wb") as fichier:
         pickle.dump(entete, fichier, protocol=pickle.HIGHEST_PROTOCOL)
         pickle.dump(trie, fichier, protocol=pickle.HIGHEST_PROTOCOL)
# ── Zone modifiée : ligne 834 (12 ligne(s)) dans l'ancienne version → ligne 886 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -834,12 +886,19 @@ def construire_trie(
     base_hunspell: Path = BASE_HUNSPELL,
     chemin_ajoutes: Path | None = None,
     chemin_retires: Path | None = None,
+    mode_belgicisme: bool = False,
+    chemin_belgicismes: Path = CHEMIN_BELGICISMES,
 ) -> Trie:
     """Construit le Trie du dictionnaire final (sans passer par le cache).
 
     Les fichiers d'ajouts/retraits par défaut sont ceux **propres à la source**
     (voir :func:`chemins_modifs`) ; ``chemin_ajoutes``/``chemin_retires``
     explicites restent prioritaires (utile en test).
+
+    ``mode_belgicisme`` (issue #274) étend la formule à ``(source ∪ ajoutés ∪
+    belges) − retirés`` : les belgicismes sans équivalent standard
+    (:func:`charger_belgicismes`) rejoignent l'ensemble avant construction du
+    Trie. Défaut ``False`` : comportement strictement inchangé.
     """
     defaut_ajoutes, defaut_retires = chemins_modifs(source)
     if chemin_ajoutes is None:
# ── Zone modifiée : ligne 847 (9 ligne(s)) dans l'ancienne version → ligne 906 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -847,9 +906,12 @@ def construire_trie(
     if chemin_retires is None:
         chemin_retires = defaut_retires
     assurer_fichiers_modifs(chemin_ajoutes, chemin_retires)
+    mots_ajoutes = lire_liste_mots(chemin_ajoutes)
+    if mode_belgicisme:
+        mots_ajoutes = mots_ajoutes | charger_belgicismes(chemin_belgicismes)
     mots = construire_ensemble_mots(
         charger_source(source, chemin_ods, base_hunspell),
-        lire_liste_mots(chemin_ajoutes),
+        mots_ajoutes,
         lire_liste_mots(chemin_retires),
     )
     return Trie.depuis_iterable(mots)
# ── Zone modifiée : ligne 862 (14 ligne(s)) dans l'ancienne version → ligne 924 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -862,14 +924,21 @@ def obtenir_trie(
     chemin_ajoutes: Path | None = None,
     chemin_retires: Path | None = None,
     chemin_cache: Path = CHEMIN_CACHE,
+    mode_belgicisme: bool = False,
+    chemin_belgicismes: Path = CHEMIN_BELGICISMES,
 ) -> Trie:
     """Retourne le Trie du dictionnaire, en s'appuyant sur le cache disque.
 
-    Le cache est rechargé s'il est présent, cible la même source et est plus
-    récent que tous les fichiers sources ; sinon il est reconstruit puis
-    réécrit. Les fichiers d'ajouts/retraits par défaut sont ceux **propres à la
-    source** (voir :func:`chemins_modifs`) ; des chemins explicites restent
-    prioritaires (utile en test).
+    Le cache est rechargé s'il est présent, cible la même source et le même
+    mode, et est plus récent que tous les fichiers sources ; sinon il est
+    reconstruit puis réécrit. Les fichiers d'ajouts/retraits par défaut sont
+    ceux **propres à la source** (voir :func:`chemins_modifs`) ; des chemins
+    explicites restent prioritaires (utile en test).
+
+    ``mode_belgicisme`` (issue #274, défaut ``False``) : voir
+    :func:`construire_trie`. Un changement de mode invalide le cache (en-tête
+    ``"belge"``) ; le CSV des belgicismes est surveillé par mtime quand le mode
+    est actif (:func:`_sources_pertinentes`).
     """
     defaut_ajoutes, defaut_retires = chemins_modifs(source)
     if chemin_ajoutes is None:
# ── Zone modifiée : ligne 878 (17 ligne(s)) dans l'ancienne version → ligne 947 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -878,17 +947,29 @@ def obtenir_trie(
         chemin_retires = defaut_retires
     assurer_fichiers_modifs(chemin_ajoutes, chemin_retires)
     sources = _sources_pertinentes(
-        source, chemin_ods, base_hunspell, chemin_ajoutes, chemin_retires
+        source,
+        chemin_ods,
+        base_hunspell,
+        chemin_ajoutes,
+        chemin_retires,
+        mode_belgicisme,
+        chemin_belgicismes,
     )
-    if _cache_valide(chemin_cache, source, sources):
+    if _cache_valide(chemin_cache, source, sources, mode_belgicisme):
         trie = _lire_trie_cache(chemin_cache)
         if trie is not None:
             return trie
     trie = construire_trie(
-        source, chemin_ods, base_hunspell, chemin_ajoutes, chemin_retires
+        source,
+        chemin_ods,
+        base_hunspell,
+        chemin_ajoutes,
+        chemin_retires,
+        mode_belgicisme,
+        chemin_belgicismes,
     )
     try:
-        _ecrire_trie_cache(chemin_cache, source, trie)
+        _ecrire_trie_cache(chemin_cache, source, trie, mode_belgicisme)
     except OSError:
         pass  # Un cache non écrit n'empêche pas de fonctionner.
     return trie
# ── Zone modifiée : ligne 917 (6 ligne(s)) dans l'ancienne version → ligne 998 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -917,6 +998,8 @@ def construire_ensemble_ia(
     chemin_ajoutes: Path | None = None,
     chemin_retires: Path | None = None,
     chemin_mots_courants: Path = CHEMIN_MOTS_COURANTS,
+    mode_belgicisme: bool = False,
+    chemin_belgicismes: Path = CHEMIN_BELGICISMES,
 ) -> set[str]:
     """Construit l'ensemble restreint de vocabulaire de l'IA (issue #206).
 
# ── Zone modifiée : ligne 939 (15 ligne(s)) dans l'ancienne version → ligne 1022 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -939,15 +1022,26 @@ def construire_ensemble_ia(
     script #205), on se rabat sur les seuls mots classiques avec un avertissement
     journalisé, plutôt que de planter. Un fichier présent mais vide est traité
     comme « aucun mot courant » sans avertissement (cas légitime).
+
+    ``mode_belgicisme`` (issue #274, défaut ``False``) : le dictionnaire complet
+    interne inclut aussi les belgicismes sans équivalent standard, pour rester
+    cohérent en sur-ensemble avec le Trie complet du jeu (voir
+    :func:`construire_trie`). Les mots belges restent toutefois hors du Trie IA
+    restreint, sauf s'ils figurent aussi dans ``mots_courants.txt`` ou
+    ``classiques_ajoutes.txt`` — comportement voulu, cohérent avec la philosophie
+    actuelle du filtre de vocabulaire de l'IA.
     """
     defaut_ajoutes, defaut_retires = chemins_modifs(source)
     if chemin_ajoutes is None:
         chemin_ajoutes = defaut_ajoutes
     if chemin_retires is None:
         chemin_retires = defaut_retires
+    mots_ajoutes = lire_liste_mots(chemin_ajoutes)
+    if mode_belgicisme:
+        mots_ajoutes = mots_ajoutes | charger_belgicismes(chemin_belgicismes)
     complet = construire_ensemble_mots(
         charger_source(source, chemin_ods, base_hunspell),
-        lire_liste_mots(chemin_ajoutes),
+        mots_ajoutes,
         lire_liste_mots(chemin_retires),
     )
     if not chemin_mots_courants.exists():
# ── Zone modifiée : ligne 969 (6 ligne(s)) dans l'ancienne version → ligne 1063 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -969,6 +1063,8 @@ def _sources_pertinentes_ia(
     chemin_ajoutes: Path,
     chemin_retires: Path,
     chemin_mots_courants: Path,
+    mode_belgicisme: bool = False,
+    chemin_belgicismes: Path = CHEMIN_BELGICISMES,
 ) -> list[Path]:
     """Fichiers dont la modification doit invalider le cache du Trie IA.
 
# ── Zone modifiée : ligne 977 (7 ligne(s)) dans l'ancienne version → ligne 1073 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -977,7 +1073,13 @@ def _sources_pertinentes_ia(
     évolution de l'une de ces listes doit reconstruire le vocabulaire restreint.
     """
     fichiers = _sources_pertinentes(
-        source, chemin_ods, base_hunspell, chemin_ajoutes, chemin_retires
+        source,
+        chemin_ods,
+        base_hunspell,
+        chemin_ajoutes,
+        chemin_retires,
+        mode_belgicisme,
+        chemin_belgicismes,
     )
     chemin_classiques_ajoutes, chemin_classiques_retires = chemins_classiques()
     fichiers += [
# ── Zone modifiée : ligne 996 (16 ligne(s)) dans l'ancienne version → ligne 1098 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -996,16 +1098,21 @@ def obtenir_trie_ia(
     chemin_retires: Path | None = None,
     chemin_mots_courants: Path = CHEMIN_MOTS_COURANTS,
     chemin_cache: Path = CHEMIN_CACHE_IA,
+    mode_belgicisme: bool = False,
+    chemin_belgicismes: Path = CHEMIN_BELGICISMES,
 ) -> Trie:
     """Retourne le Trie restreint de l'IA (issue #206), via le cache disque.
 
     Construit :func:`construire_ensemble_ia` puis le met en cache sur le modèle
-    exact d':func:`obtenir_trie` (en-tête version + source, invalidation par
-    mtime), dans un fichier distinct (:data:`CHEMIN_CACHE_IA`). Les sources
+    exact d':func:`obtenir_trie` (en-tête version + source + mode, invalidation
+    par mtime), dans un fichier distinct (:data:`CHEMIN_CACHE_IA`). Les sources
     surveillées incluent en plus ``mots_courants.txt`` et la paire des classiques
     (:func:`_sources_pertinentes_ia`). Les chemins d'ajouts/retraits par défaut
     sont ceux propres à la source ; des chemins explicites restent prioritaires
     (utile en test).
+
+    ``mode_belgicisme`` (issue #274, défaut ``False``) : voir
+    :func:`construire_ensemble_ia`.
     """
     defaut_ajoutes, defaut_retires = chemins_modifs(source)
     if chemin_ajoutes is None:
# ── Zone modifiée : ligne 1020 (8 ligne(s)) dans l'ancienne version → ligne 1127 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1020,8 +1127,10 @@ def obtenir_trie_ia(
         chemin_ajoutes,
         chemin_retires,
         chemin_mots_courants,
+        mode_belgicisme,
+        chemin_belgicismes,
     )
-    if _cache_valide(chemin_cache, source, sources):
+    if _cache_valide(chemin_cache, source, sources, mode_belgicisme):
         trie = _lire_trie_cache(chemin_cache)
         if trie is not None:
             return trie
# ── Zone modifiée : ligne 1032 (10 ligne(s)) dans l'ancienne version → ligne 1141 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1032,10 +1141,12 @@ def obtenir_trie_ia(
         chemin_ajoutes,
         chemin_retires,
         chemin_mots_courants,
+        mode_belgicisme,
+        chemin_belgicismes,
     )
     trie = Trie.depuis_iterable(ensemble)
     try:
-        _ecrire_trie_cache(chemin_cache, source, trie)
+        _ecrire_trie_cache(chemin_cache, source, trie, mode_belgicisme)
     except OSError:
         pass  # Un cache non écrit n'empêche pas de fonctionner.
     return trie
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/accueil.py b/src/scrabble/ui/accueil.py
# (index — ignorable)
index 2969801..f36a7cf 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/accueil.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/accueil.py
# ── Zone modifiée : ligne 127 (11 ligne(s)) dans l'ancienne version → ligne 127 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -127,11 +127,11 @@ class ConfigPartie:
 
     joueurs: list[JoueurConfig] = field(default_factory=list)
     # Mode dictionnaire régional (issue #269) : bascule facultative entre le
-    # dictionnaire standard (France, choix par défaut) et un futur
-    # dictionnaire belge additionnel. Cette issue ne couvre QUE l'interface
-    # (cercles-drapeaux) et le stockage de ce choix — le chargement effectif
-    # du dictionnaire belge et l'affichage de ses définitions restent un
-    # chantier séparé, à venir.
+    # dictionnaire standard (France, choix par défaut) et le dictionnaire
+    # étendu aux belgicismes sans équivalent standard (issue #274, lu par
+    # ``ApiAccueil.lancer_partie``). L'affichage de définitions belges
+    # additionnelles pour les mots existant déjà en français standard reste un
+    # chantier séparé (la loupe), à venir.
     mode_belgicisme: bool = False
 
     @property
# ── Zone modifiée : ligne 439 (12 ligne(s)) dans l'ancienne version → ligne 439 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -439,12 +439,10 @@ class ApiAccueil:
         """Enregistre le choix France/Belgique des cercles-drapeaux (issue #269).
 
         Se contente de stocker le booléen dans la configuration de la partie
-        en cours de création (``config_partie.mode_belgicisme``), pour qu'un
-        futur chantier (chargement du dictionnaire belge) puisse le lire
-        facilement au lancement de la partie via ``self.config_partie.
-        mode_belgicisme``. Aucune logique de dictionnaire n'est implémentée
-        ici — le choix France reste sans effet tant que ce chantier n'existe
-        pas.
+        en cours de création (``config_partie.mode_belgicisme``). C'est
+        :meth:`lancer_partie` qui le lit pour construire le dictionnaire de
+        validation (issue #274, :func:`~scrabble.dictionnaire.dictionnaire.
+        obtenir_trie`) — cette méthode-ci ne fait qu'enregistrer le choix.
         """
         self.config_partie.mode_belgicisme = bool(actif)
         journal.info(
# ── Zone modifiée : ligne 458 (7 ligne(s)) dans l'ancienne version → ligne 456 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -458,7 +456,7 @@ class ApiAccueil:
         }
 
     @staticmethod
-    def _construire_trie_ia(source: str) -> Any:
+    def _construire_trie_ia(source: str, mode_belgicisme: bool = False) -> Any:
         """Trie restreint de l'IA si « vocabulaire humain » est actif, sinon ``None``.
 
         Réglage global unique (issue #206), indépendant du niveau de difficulté :
# ── Zone modifiée : ligne 472 (10 ligne(s)) dans l'ancienne version → ligne 470 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -472,10 +470,14 @@ class ApiAccueil:
         ici via un second ``charger_config()`` qui pourrait en théorie diverger.
         On garantit ainsi que le vocabulaire de l'IA reste un sous-ensemble strict
         du dictionnaire de validation effectivement utilisé pour la partie.
+
+        ``mode_belgicisme`` (issue #274, défaut ``False``) est transmis de la
+        même façon, pour la même raison : il doit correspondre exactement au
+        mode utilisé pour le Trie complet de la partie.
         """
         if not bool(charger_config().get("vocabulaire_humain", False)):
             return None
-        return obtenir_trie_ia(source)
+        return obtenir_trie_ia(source, mode_belgicisme=mode_belgicisme)
 
     def lancer_partie(self) -> dict[str, Any]:
         """Crée et démarre la partie avec la configuration actuelle.
# ── Zone modifiée : ligne 529 (13 ligne(s)) dans l'ancienne version → ligne 531 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -529,13 +531,17 @@ class ApiAccueil:
             # transmet la même source au Trie complet et au Trie restreint de l'IA.
             config = charger_config()
             source = config.get("source_dictionnaire", "ods")
-            trie = obtenir_trie(source)
+            # Mode Belgicisme (issue #269) choisi pour cette partie : ajoute au
+            # dictionnaire les belgicismes sans équivalent standard (issue #274).
+            mode_belgicisme = self.config_partie.mode_belgicisme
+            trie = obtenir_trie(source, mode_belgicisme=mode_belgicisme)
             # Réglage du bonus officiel au finisseur (issue #134), câblé dans le
             # moteur via creer_partie.
             bonus_fin_partie = bool(config.get("bonus_fin_partie", False))
             # Réglage « vocabulaire humain » (issue #206) : Trie restreint de l'IA,
-            # construit sur la même source que le Trie complet (issue #210).
-            trie_ia = self._construire_trie_ia(source)
+            # construit sur la même source et le même mode que le Trie complet
+            # (issues #210, #274).
+            trie_ia = self._construire_trie_ia(source, mode_belgicisme)
             self._partie = creer_partie(
                 noms_humains=noms_humains,
                 dictionnaire=trie,
# (diff du fichier suivant)
diff --git a/tests/test_accueil.py b/tests/test_accueil.py
# (index — ignorable)
index df21c64..5000e69 100644
# (avant — fichier suivant)
--- a/tests/test_accueil.py
# (après — fichier suivant)
+++ b/tests/test_accueil.py
# ── Zone modifiée : ligne 326 (7 ligne(s)) dans l'ancienne version → ligne 326 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -326,7 +326,7 @@ class TestApiAccueilLancement:
         # désormais la source lue dans la config (issue #210), d'où ``source``.
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": Trie.depuis_iterable(["MAISON", "TEST"]),
+            lambda source="ods", **_: Trie.depuis_iterable(["MAISON", "TEST"]),
         )
         # Stub de la persistance pour éviter d'écrire sur disque
         monkeypatch.setattr(
# ── Zone modifiée : ligne 359 (7 ligne(s)) dans l'ancienne version → ligne 359 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -359,7 +359,7 @@ class TestApiAccueilLancement:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": Trie.depuis_iterable(["TEST"]),
+            lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.reprendre_partie",
# ── Zone modifiée : ligne 394 (7 ligne(s)) dans l'ancienne version → ligne 394 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -394,7 +394,7 @@ class TestApiAccueilLancement:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": Trie.depuis_iterable(["TEST"]),
+            lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.reprendre_partie",
# ── Zone modifiée : ligne 478 (7 ligne(s)) dans l'ancienne version → ligne 478 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -478,7 +478,7 @@ class TestSourceDictionnaireAppliquee:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": appels.append(source)
+            lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
         monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 7)
# ── Zone modifiée : ligne 509 (7 ligne(s)) dans l'ancienne version → ligne 509 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -509,7 +509,7 @@ class TestSourceDictionnaireAppliquee:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": appels.append(source)
+            lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
         monkeypatch.setattr(
# ── Zone modifiée : ligne 532 (7 ligne(s)) dans l'ancienne version → ligne 532 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -532,7 +532,7 @@ class TestSourceDictionnaireAppliquee:
         monkeypatch.setattr("scrabble.ui.accueil.charger_config", lambda: {})
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": appels.append(source)
+            lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
         monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 1)
# ── Zone modifiée : ligne 556 (7 ligne(s)) dans l'ancienne version → ligne 556 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -556,7 +556,7 @@ class TestSourceDictionnaireAppliquee:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie_ia",
-            lambda source="ods": appels.append(source)
+            lambda source="ods", **_: appels.append(source)
             or Trie.depuis_iterable(["TEST"]),
         )
 
# ── Zone modifiée : ligne 575 (7 ligne(s)) dans l'ancienne version → ligne 575 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -575,7 +575,7 @@ class TestSourceDictionnaireAppliquee:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie_ia",
-            lambda source="ods": appels.append(source),
+            lambda source="ods", **_: appels.append(source),
         )
 
         assert ApiAccueil._construire_trie_ia("hunspell") is None
# ── Zone modifiée : ligne 604 (7 ligne(s)) dans l'ancienne version → ligne 604 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -604,7 +604,7 @@ class TestSourceDictionnaireAppliquee:
             lambda: {"source_dictionnaire": "hunspell"},
         )
         monkeypatch.setattr(
-            "scrabble.ui.accueil.obtenir_trie", lambda source="ods": tries[source]
+            "scrabble.ui.accueil.obtenir_trie", lambda source="ods", **_: tries[source]
         )
         monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 1)
 
# ── Zone modifiée : ligne 814 (7 ligne(s)) dans l'ancienne version → ligne 814 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -814,7 +814,7 @@ class TestApiAccueilInfosTirage:
 
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": Trie.depuis_iterable(["MAISON", "TEST"]),
+            lambda source="ods", **_: Trie.depuis_iterable(["MAISON", "TEST"]),
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.demarrer_suivi",
# (diff du fichier suivant)
diff --git a/tests/test_dictionnaire.py b/tests/test_dictionnaire.py
# (index — ignorable)
index 7ec7301..a4836be 100644
# (avant — fichier suivant)
--- a/tests/test_dictionnaire.py
# (après — fichier suivant)
+++ b/tests/test_dictionnaire.py
# ── Zone modifiée : ligne 9 (8 ligne(s)) dans l'ancienne version → ligne 9 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,8 +9,10 @@ et la normalisation sont testées de façon déterministe et rapide.
 
 from __future__ import annotations
 
+import csv
 import json
 import os
+import pickle
 import time
 
 import pytest
# ── Zone modifiée : ligne 21 (6 ligne(s)) dans l'ancienne version → ligne 23 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -21,6 +23,7 @@ from scrabble.dictionnaire.dictionnaire import (
     Dictionnaire,
     Trie,
     assurer_fichiers_modifs,
+    charger_belgicismes,
     charger_definitions,
     charger_ods,
     chemins_modifs,
# ── Zone modifiée : ligne 466 (6 ligne(s)) dans l'ancienne version → ligne 469 (203 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -466,6 +469,203 @@ def test_cache_invalide_si_source_configuree_change(tmp_path):
     assert _cache_valide(chemin_cache, "hunspell", sources_ods) is False
 
 
+# --------------------------------------------------------------------------- #
+# Belgicismes (mode Belgicisme), issue #274
+# --------------------------------------------------------------------------- #
+
+def _ecrire_csv_belgicismes(chemin, lignes):
+    """Écrit un CSV belgicismes factice. ``lignes`` : liste de (mot, existe)."""
+    with open(chemin, "w", encoding="utf-8", newline="") as fichier:
+        ecrivain = csv.writer(fichier)
+        ecrivain.writerow(
+            ["mot", "définition(s) belge(s)", "origine_wallonne", "existe_sens_standard"]
+        )
+        for mot, existe in lignes:
+            ecrivain.writerow([mot, "Une définition.", "non", existe])
+
+
+def test_charger_belgicismes_ne_retient_que_les_mots_sans_equivalent_standard(tmp_path):
+    """Seuls les mots ``existe_sens_standard`` != "oui" (normalisé) sont chargés."""
+    chemin = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(
+        chemin,
+        [
+            ("sketter", "non"),
+            ("abaisser", "oui"),
+            ("abiye", " Non "),
+            ("dringuelle", "NON"),
+        ],
+    )
+    mots = charger_belgicismes(chemin)
+    assert mots == {"SKETTER", "ABIYE", "DRINGUELLE"}
+    assert "ABAISSER" not in mots
+
+
+def test_charger_belgicismes_fichier_absent(tmp_path):
+    """Fichier absent : ensemble vide, sans erreur (comme lire_liste_mots)."""
+    assert charger_belgicismes(tmp_path / "absent.csv") == set()
+
+
+def test_construire_trie_mode_belgicisme_ajoute_mot_belge(tmp_path):
+    """Un mot belge (existe_sens_standard=non) est valide en mode Belgicisme et
+    invalide en mode France (issue #274) — ex. « sketter », absent de l'ODS."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["chat"]
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(chemin_belges, [("sketter", "non")])
+
+    trie_france = construire_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        mode_belgicisme=False,
+        chemin_belgicismes=chemin_belges,
+    )
+    trie_belgique = construire_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        mode_belgicisme=True,
+        chemin_belgicismes=chemin_belges,
+    )
+
+    assert "SKETTER" not in trie_france
+    assert "SKETTER" in trie_belgique
+    assert "CHAT" in trie_france and "CHAT" in trie_belgique
+
+
+def test_construire_trie_mode_belgicisme_pas_de_doublon_mot_standard(tmp_path):
+    """Un mot ``existe_sens_standard=oui`` n'est pas réinjecté par le chargement
+    belge : il est déjà présent via la source standard, comportement inchangé."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["academique"]
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(chemin_belges, [("academique", "oui")])
+
+    trie = construire_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        mode_belgicisme=True,
+        chemin_belgicismes=chemin_belges,
+    )
+
+    assert "ACADEMIQUE" in trie
+    assert len(trie) == 1  # un seul mot : pas de doublon via le CSV belge
+
+
+def test_construire_trie_mode_belgicisme_mot_oui_absent_de_la_source_reste_absent(
+    tmp_path,
+):
+    """Un mot ``oui`` absent de la source standard n'est pas ajouté via le CSV
+    belge (seuls les mots ``!= oui`` sont chargés, voir :func:`charger_belgicismes`)."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["chat"]
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(chemin_belges, [("zorglub", "oui")])
+
+    trie = construire_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        mode_belgicisme=True,
+        chemin_belgicismes=chemin_belges,
+    )
+    assert "ZORGLUB" not in trie
+
+
+def test_obtenir_trie_cache_mode_defaut_false_comportement_inchange(tmp_path):
+    """Non-régression (issue #274) : mode par défaut (``False``), le cache se
+    comporte strictement comme avant cette issue (écrit puis relu sans
+    reconstruction superflue)."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["chat"]
+    )
+    chemin_cache = tmp_path / "trie_cache.pkl"
+    kwargs = dict(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        chemin_cache=chemin_cache,
+    )
+
+    trie1 = obtenir_trie(**kwargs)
+    assert chemin_cache.exists()
+    mtime_cache = chemin_cache.stat().st_mtime_ns
+
+    trie2 = obtenir_trie(**kwargs)
+    assert chemin_cache.stat().st_mtime_ns == mtime_cache  # non réécrit
+    assert "CHAT" in trie1 and "CHAT" in trie2
+
+
+def test_obtenir_trie_cache_invalide_si_mode_belgicisme_change(tmp_path):
+    """Basculer le mode Belgicisme invalide le cache existant (en-tête ``belge``)."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["chat"]
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(chemin_belges, [("sketter", "non")])
+    chemin_cache = tmp_path / "trie_cache.pkl"
+    kwargs = dict(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        chemin_cache=chemin_cache,
+        chemin_belgicismes=chemin_belges,
+    )
+
+    trie_france = obtenir_trie(mode_belgicisme=False, **kwargs)
+    assert "SKETTER" not in trie_france
+
+    trie_belgique = obtenir_trie(mode_belgicisme=True, **kwargs)
+    assert "SKETTER" in trie_belgique
+
+    # Rebasculer en France reconstruit aussi (le cache belge ne doit pas fuiter).
+    trie_france_2 = obtenir_trie(mode_belgicisme=False, **kwargs)
+    assert "SKETTER" not in trie_france_2
+
+
+def test_obtenir_trie_cache_ancien_sans_champ_belge_reste_valide_en_mode_france(
+    tmp_path,
+):
+    """Un cache écrit avant l'issue #274 (en-tête sans clé ``belge``) reste
+    valide en mode France par défaut, sans reconstruction (repli
+    ``entete.get("belge", False)``)."""
+    chemin_ods, chemin_ajoutes, chemin_retires = _preparer_dico(
+        tmp_path, source_mots=["chat"]
+    )
+    chemin_cache = tmp_path / "trie_cache.pkl"
+    trie = construire_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+    )
+    with open(chemin_cache, "wb") as fichier:
+        pickle.dump({"version": d.VERSION_CACHE, "source": "ods"}, fichier)
+        pickle.dump(trie, fichier)
+    mtime_cache = chemin_cache.stat().st_mtime_ns
+
+    trie_relu = obtenir_trie(
+        source="ods",
+        chemin_ods=chemin_ods,
+        chemin_ajoutes=chemin_ajoutes,
+        chemin_retires=chemin_retires,
+        chemin_cache=chemin_cache,
+    )
+    assert chemin_cache.stat().st_mtime_ns == mtime_cache  # pas régénéré
+    assert "CHAT" in trie_relu
+
+
 # --------------------------------------------------------------------------- #
 # Désaccentuation + définitions (issue #111, onglet Dictionnaire)
 # --------------------------------------------------------------------------- #
# ── Zone modifiée : ligne 941 (3 ligne(s)) dans l'ancienne version → ligne 1141 (48 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -941,3 +1141,48 @@ def test_obtenir_trie_ia_cache_invalide_si_classiques_change(tmp_path, monkeypat
 
     trie2 = obtenir_trie_ia(**kwargs)
     assert "WU" in trie2                          # cache invalidé
+
+
+def test_construire_ensemble_ia_mode_belgicisme_hors_courants_reste_exclu(
+    tmp_path, monkeypatch
+):
+    """Le ``complet`` interne inclut les belges actifs (sur-ensemble cohérent
+    avec le Trie complet, issue #274), mais le Trie IA restreint ne les retient
+    que s'ils sont aussi mots courants/classiques — sinon ils restent exclus."""
+    ods, aj, re_, co, *_ = _preparer_ia(
+        tmp_path, monkeypatch, source_mots=["chat"], courants=["chat"]
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(chemin_belges, [("sketter", "non")])
+
+    ensemble = construire_ensemble_ia(
+        chemin_ods=ods,
+        chemin_ajoutes=aj,
+        chemin_retires=re_,
+        chemin_mots_courants=co,
+        mode_belgicisme=True,
+        chemin_belgicismes=chemin_belges,
+    )
+    assert ensemble == {"CHAT"}
+    assert "SKETTER" not in ensemble
+
+
+def test_construire_ensemble_ia_mode_belgicisme_mot_courant_est_inclus(
+    tmp_path, monkeypatch
+):
+    """Un mot belge aussi présent dans ``mots_courants.txt`` rejoint le Trie IA."""
+    ods, aj, re_, co, *_ = _preparer_ia(
+        tmp_path, monkeypatch, source_mots=["chat"], courants=["chat", "sketter"]
+    )
+    chemin_belges = tmp_path / "belgicismes.csv"
+    _ecrire_csv_belgicismes(chemin_belges, [("sketter", "non")])
+
+    ensemble = construire_ensemble_ia(
+        chemin_ods=ods,
+        chemin_ajoutes=aj,
+        chemin_retires=re_,
+        chemin_mots_courants=co,
+        mode_belgicisme=True,
+        chemin_belgicismes=chemin_belges,
+    )
+    assert ensemble == {"CHAT", "SKETTER"}
# (diff du fichier suivant)
diff --git a/tests/test_jeu_pose.py b/tests/test_jeu_pose.py
# (index — ignorable)
index 16640eb..1251730 100644
# (avant — fichier suivant)
--- a/tests/test_jeu_pose.py
# (après — fichier suivant)
+++ b/tests/test_jeu_pose.py
# ── Zone modifiée : ligne 614 (7 ligne(s)) dans l'ancienne version → ligne 614 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -614,7 +614,7 @@ class TestSourceDictionnaireValidationCoup:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda s="ods": self._TRIES[s],
+            lambda s="ods", **_: self._TRIES[s],
         )
         # Pas de persistance en base pendant le test : id_partie reste None,
         # ce qui neutralise aussi ``_persister_entrees`` côté ApiJeu.
# (diff du fichier suivant)
diff --git a/tests/test_journal_integration.py b/tests/test_journal_integration.py
# (index — ignorable)
index 0757dd9..7bd4ca2 100644
# (avant — fichier suivant)
--- a/tests/test_journal_integration.py
# (après — fichier suivant)
+++ b/tests/test_journal_integration.py
# ── Zone modifiée : ligne 115 (7 ligne(s)) dans l'ancienne version → ligne 115 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -115,7 +115,7 @@ class TestJournalAccueil:
     def test_lancer_partie_journalise_avec_nb_joueurs(self, espion, monkeypatch):
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": Trie.depuis_iterable(["MAISON", "TEST"]),
+            lambda source="ods", **_: Trie.depuis_iterable(["MAISON", "TEST"]),
         )
         monkeypatch.setattr("scrabble.ui.accueil.demarrer_suivi", lambda partie: 42)
 
# ── Zone modifiée : ligne 133 (7 ligne(s)) dans l'ancienne version → ligne 133 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -133,7 +133,7 @@ class TestJournalAccueil:
         boum = RuntimeError("dictionnaire cassé")
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": (_ for _ in ()).throw(boum),
+            lambda source="ods", **_: (_ for _ in ()).throw(boum),
         )
         api = ApiAccueil()
         api.ajouter_humain("Alice")
# ── Zone modifiée : ligne 154 (7 ligne(s)) dans l'ancienne version → ligne 154 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -154,7 +154,7 @@ class TestJournalAccueil:
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": Trie.depuis_iterable(["TEST"]),
+            lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
         monkeypatch.setattr(
             "scrabble.ui.accueil.reprendre_partie",
# ── Zone modifiée : ligne 169 (7 ligne(s)) dans l'ancienne version → ligne 169 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -169,7 +169,7 @@ class TestJournalAccueil:
     def test_reprendre_introuvable_journalise_erreur(self, espion, monkeypatch):
         monkeypatch.setattr(
             "scrabble.ui.accueil.obtenir_trie",
-            lambda source="ods": Trie.depuis_iterable(["TEST"]),
+            lambda source="ods", **_: Trie.depuis_iterable(["TEST"]),
         )
 
         def _absente(id_partie, trie, dictionnaire_ia=None):
