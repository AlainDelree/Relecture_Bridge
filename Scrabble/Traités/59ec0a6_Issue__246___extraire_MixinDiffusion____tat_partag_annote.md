59ec0a6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 59ec0a6
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 15:23:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #246 : extraire MixinDiffusion (état partagé et diffusion)
    
    Création de src/scrabble/ui/api_diffusion.py contenant la classe
    MixinDiffusion avec les 6 méthodes extraites de ApiJeu :
    - _placements_publics
    - _etat_plateau
    - _etat_chevalet
    - _diffuser
    - _pousser
    - _refuser_hors_tour
    
    ApiJeu hérite désormais de MixinDiffusion. Les imports circulaires
    sont évités par des imports locaux (lazy imports) dans les méthodes
    qui en ont besoin.
    
    pytest : 747 passed, py_compile OK, aucune duplication.
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/api_diffusion.py b/src/scrabble/ui/api_diffusion.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..701925b
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/api_diffusion.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (195 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,195 @@
+"""Mixin socle de diffusion d'état pour l'API Jeu (issue #246).
+
+Ce mixin est le **socle dont dépendent les autres mixins ApiJeu** : il expose
+la mécanique de diffusion d'état vers la fenêtre Jeu (placements publics,
+états plateau/chevalet, diffusion, poussage, garde de tour). Les autres mixins
+qui mutualisent des parties de l'ApiJeu s'appuient sur ces primitives —
+aucune dépendance sortante n'est attendue pour celui-ci.
+"""
+
+from __future__ import annotations
+
+import json
+from typing import Any, TYPE_CHECKING
+
+from scrabble import journal
+
+if TYPE_CHECKING:
+    import webview
+
+    from scrabble.moteur.partie import Partie
+
+
+class MixinDiffusion:
+    """Primitives de diffusion d'état partagées par ApiJeu et ses mixins."""
+
+    # Attributs attendus sur la classe hôte (ApiJeu), déclarés pour les
+    # annotations — pas de valeur par défaut, ils vivent sur l'instance.
+    _partie: Partie | None
+    _id_partie: int | None
+    _selection: int | None
+    _en_attente: list[dict[str, Any]]
+    _joker_demande: dict[str, Any] | None
+    _type_echange: str
+    _mode_echange: bool
+    _selection_echange: list[int]
+    _window_plateau: "webview.Window | None"
+
+    def _placements_publics(self) -> list[dict[str, Any]]:
+        """Placements en attente **sans** l'index de chevalet (part côté plateau).
+
+        La fenêtre plateau n'a aucun besoin de connaître de quel emplacement du
+        chevalet provient une lettre posée (``index``) : elle n'affiche que la
+        tuile sur le plateau. On ne lui transmet donc que la position, la lettre
+        (déjà destinée à être visible sur le plateau), le drapeau joker et la
+        valeur en points. Les lettres *non posées* du chevalet, elles, ne partent
+        jamais vers la fenêtre plateau (issues #33/#35).
+        """
+        return [
+            {
+                "ligne": p["ligne"],
+                "colonne": p["colonne"],
+                "lettre": p["lettre"],
+                "joker": p["joker"],
+                "valeur": p["valeur"],
+            }
+            for p in self._en_attente
+        ]
+
+    def _etat_plateau(self) -> dict[str, Any]:
+        """État **public** destiné à la fenêtre plateau (issue #90).
+
+        C'est :func:`etat_public` (aucune identité de lettre de chevalet), enrichi
+        des seuls placements en attente déjà posés sur le plateau
+        (:meth:`_placements_publics`) et de l'index de la lettre sélectionnée
+        (``selection`` : une information neutre — un simple index — qui ne dévoile
+        aucune lettre).
+        """
+        from scrabble.ui.jeu import etat_public
+
+        etat = etat_public(self._partie, self._id_partie)
+        etat["en_attente"] = self._placements_publics()
+        etat["selection"] = self._selection
+        # Échange partiel (issue #138) : le mode réglé et l'éventuelle sélection
+        # d'échange en cours (index neutres) pilotent l'affichage des boutons de
+        # la zone de jeu (« Échanger des lettres… » / « Échanger la sélection »).
+        etat["type_echange"] = self._type_echange
+        etat["mode_echange"] = self._mode_echange
+        etat["selection_echange"] = list(self._selection_echange)
+        return etat
+
+    def _etat_chevalet(self) -> dict[str, Any]:
+        """État **complet** (lettres privées incluses) destiné au panneau chevalet.
+
+        Depuis l'issue #99, le payload porte sur le **joueur humain de référence**
+        (:func:`index_humain_reference`), et non plus sur le joueur courant : ses
+        lettres sont **toujours** sérialisées (panneau toujours visible et
+        réarrangeable), y compris hors de son tour. ``mon_tour`` dit si c'est
+        actuellement son tour — seule condition pour poser réellement (garde de
+        tour, :meth:`_refuser_hors_tour`). L'état de pose complet est joint
+        (sélection, placements avec leur ``index`` de chevalet, éventuelle demande
+        de choix de lettre pour un joker), ainsi que quelques champs publics (nom
+        du joueur de référence, fin de partie) pour éviter un aller-retour.
+
+        La garantie de confidentialité demeure : jamais le chevalet d'un
+        ordinateur ni d'un autre joueur humain que le joueur de référence.
+        """
+        from scrabble.ui.jeu import index_humain_reference, serialiser_chevalet
+
+        partie = self._partie
+        index_reference = index_humain_reference(partie.joueurs)
+        reference = partie.joueurs[index_reference]
+        return {
+            "index_reference": index_reference,
+            "nom": reference.nom,
+            "mon_tour": partie.index_courant == index_reference
+            and not partie.terminee,
+            "terminee": partie.terminee,
+            "nb_lettres": len(reference.chevalet),
+            # Lettres privées : toujours celles du joueur de référence (issue #99),
+            # jamais un ordinateur ni un autre humain.
+            "lettres": serialiser_chevalet(reference),
+            "selection": self._selection,
+            "en_attente": [dict(p) for p in self._en_attente],
+            "joker_demande": self._joker_demande,
+            # Échange partiel (issue #138) : le panneau marque distinctement les
+            # lettres à échanger quand ``mode_echange`` est actif.
+            "type_echange": self._type_echange,
+            "mode_echange": self._mode_echange,
+            "selection_echange": list(self._selection_echange),
+        }
+
+    def _diffuser(self) -> None:
+        """Pousse l'état pertinent à la fenêtre Jeu après toute mutation (issue #90).
+
+        Depuis l'issue #187 (Issue B), le chevalet a migré de sa fenêtre flottante
+        séparée vers la zone C de ``jeu.html`` : les DEUX charges sont donc poussées
+        à la **même** fenêtre (``self._window_plateau``, l'unique fenêtre Jeu), qui
+        expose désormais les deux points d'entrée JS :
+
+        * ``window.appliquerEtatPlateau`` reçoit l'état **public**
+          (:meth:`_etat_plateau`), jamais de lettre du chevalet ;
+        * ``window.appliquerEtatChevalet`` reçoit l'état **complet**
+          (:meth:`_etat_chevalet`), lettres privées du seul joueur humain de
+          référence comprises.
+
+        Confidentialité (issues #33/#35, #99) — À NOTER : les lettres privées et
+        l'état public co-résident maintenant dans le même document, mais aucune
+        fuite n'est introduite : :meth:`_etat_chevalet` ne sérialise toujours que
+        le chevalet du joueur humain de référence (jamais un ordinateur ni un autre
+        humain), exactement comme lorsqu'il alimentait une fenêtre séparée. La
+        garantie de l'issue #99 est inchangée ; seule la fenêtre cible a changé.
+
+        Chaque appel est encadré d'un ``try/except`` (:meth:`_pousser`) : une
+        fenêtre fermée ou un JS pas encore prêt ne doit jamais faire planter une
+        action de jeu.
+
+        Depuis le nettoyage du modèle de fenêtres (issue #193), il n'existe plus
+        qu'une seule fenêtre : les deux charges y sont poussées, il n'y a plus de
+        fenêtre chevalet flottante à alimenter.
+        """
+        self._pousser(
+            self._window_plateau, "appliquerEtatPlateau", self._etat_plateau()
+        )
+        self._pousser(
+            self._window_plateau, "appliquerEtatChevalet", self._etat_chevalet()
+        )
+
+    @staticmethod
+    def _pousser(
+        window: "webview.Window | None", fonction: str, charge: dict[str, Any]
+    ) -> None:
+        """Appelle ``window.<fonction>(<charge JSON>)`` si la fenêtre existe."""
+        if window is None:
+            return
+        script = (
+            f"window.{fonction} && window.{fonction}("
+            f"{json.dumps(charge, ensure_ascii=False)})"
+        )
+        try:
+            window.evaluate_js(script)
+        except Exception as e:  # noqa: BLE001 - une vue absente ne bloque pas le jeu
+            journal.erreur("Jeu : échec de la diffusion d'un état à une fenêtre.", e)
+
+    def _refuser_hors_tour(self) -> dict[str, Any] | None:
+        """Refus normalisé si une mutation de pose est tentée hors du tour.
+
+        Garde de tour de l'issue #99. Le panneau du joueur de référence est
+        désormais toujours visible et sélectionnable, y compris hors de son tour
+        (réflexion libre) ; mais **muter** l'état de pose (sélection, placement en
+        attente, retrait, annulation) reste réservé à son tour réel — jusqu'ici
+        c'était garanti seulement par le masquage du chevalet hors tour, ce qui
+        n'est plus le cas (signalé par le rapport #98).
+
+        Renvoie ``{"succes": False, "erreur": ...}`` si la partie est terminée ou
+        si ce n'est pas le tour du joueur humain de référence
+        (:func:`index_humain_reference`), sinon ``None`` (action autorisée).
+        """
+        from scrabble.ui.jeu import index_humain_reference
+
+        partie = self._partie
+        if partie.terminee or partie.index_courant != index_humain_reference(
+            partie.joueurs
+        ):
+            return {"succes": False, "erreur": "Ce n'est pas votre tour."}
+        return None
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/jeu.py b/src/scrabble/ui/jeu.py
# (index — ignorable)
index cd83657..4d06ef6 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/jeu.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/jeu.py
# ── Zone modifiée : ligne 78 (6 ligne(s)) dans l'ancienne version → ligne 78 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -78,6 +78,7 @@ from scrabble.moteur.validation import CoupInvalide, DictionnaireMots, valider_c
 from scrabble.regles.lettres import JOKER, valeur_lettre
 from scrabble.regles.plateau import TAILLE, type_case
 from scrabble.ui import TAPIS_VERT
+from scrabble.ui.api_diffusion import MixinDiffusion
 
 DOSSIER_WEB = Path(__file__).parent / "web"
 
# ── Zone modifiée : ligne 1055 (7 ligne(s)) dans l'ancienne version → ligne 1056 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1055,7 +1056,7 @@ def detail_tirage_ordre(
 # --------------------------------------------------------------------------- #
 
 
-class ApiJeu:
+class ApiJeu(MixinDiffusion):
     """API Python exposée au JavaScript de l'écran de jeu (issue #90).
 
     Depuis l'issue #187 (migration du chevalet en zone C) puis l'issue #193
# ── Zone modifiée : ligne 1493 (159 ligne(s)) dans l'ancienne version → ligne 1494 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1493,159 +1494,6 @@ class ApiJeu:
     # État de pose partagé et diffusion aux deux fenêtres (issue #90)
     # ------------------------------------------------------------------ #
 
-    def _placements_publics(self) -> list[dict[str, Any]]:
-        """Placements en attente **sans** l'index de chevalet (part côté plateau).
-
-        La fenêtre plateau n'a aucun besoin de connaître de quel emplacement du
-        chevalet provient une lettre posée (``index``) : elle n'affiche que la
-        tuile sur le plateau. On ne lui transmet donc que la position, la lettre
-        (déjà destinée à être visible sur le plateau), le drapeau joker et la
-        valeur en points. Les lettres *non posées* du chevalet, elles, ne partent
-        jamais vers la fenêtre plateau (issues #33/#35).
-        """
-        return [
-            {
-                "ligne": p["ligne"],
-                "colonne": p["colonne"],
-                "lettre": p["lettre"],
-                "joker": p["joker"],
-                "valeur": p["valeur"],
-            }
-            for p in self._en_attente
-        ]
-
-    def _etat_plateau(self) -> dict[str, Any]:
-        """État **public** destiné à la fenêtre plateau (issue #90).
-
-        C'est :func:`etat_public` (aucune identité de lettre de chevalet), enrichi
-        des seuls placements en attente déjà posés sur le plateau
-        (:meth:`_placements_publics`) et de l'index de la lettre sélectionnée
-        (``selection`` : une information neutre — un simple index — qui ne dévoile
-        aucune lettre).
-        """
-        etat = etat_public(self._partie, self._id_partie)
-        etat["en_attente"] = self._placements_publics()
-        etat["selection"] = self._selection
-        # Échange partiel (issue #138) : le mode réglé et l'éventuelle sélection
-        # d'échange en cours (index neutres) pilotent l'affichage des boutons de
-        # la zone de jeu (« Échanger des lettres… » / « Échanger la sélection »).
-        etat["type_echange"] = self._type_echange
-        etat["mode_echange"] = self._mode_echange
-        etat["selection_echange"] = list(self._selection_echange)
-        return etat
-
-    def _etat_chevalet(self) -> dict[str, Any]:
-        """État **complet** (lettres privées incluses) destiné au panneau chevalet.
-
-        Depuis l'issue #99, le payload porte sur le **joueur humain de référence**
-        (:func:`index_humain_reference`), et non plus sur le joueur courant : ses
-        lettres sont **toujours** sérialisées (panneau toujours visible et
-        réarrangeable), y compris hors de son tour. ``mon_tour`` dit si c'est
-        actuellement son tour — seule condition pour poser réellement (garde de
-        tour, :meth:`_refuser_hors_tour`). L'état de pose complet est joint
-        (sélection, placements avec leur ``index`` de chevalet, éventuelle demande
-        de choix de lettre pour un joker), ainsi que quelques champs publics (nom
-        du joueur de référence, fin de partie) pour éviter un aller-retour.
-
-        La garantie de confidentialité demeure : jamais le chevalet d'un
-        ordinateur ni d'un autre joueur humain que le joueur de référence.
-        """
-        partie = self._partie
-        index_reference = index_humain_reference(partie.joueurs)
-        reference = partie.joueurs[index_reference]
-        return {
-            "index_reference": index_reference,
-            "nom": reference.nom,
-            "mon_tour": partie.index_courant == index_reference
-            and not partie.terminee,
-            "terminee": partie.terminee,
-            "nb_lettres": len(reference.chevalet),
-            # Lettres privées : toujours celles du joueur de référence (issue #99),
-            # jamais un ordinateur ni un autre humain.
-            "lettres": serialiser_chevalet(reference),
-            "selection": self._selection,
-            "en_attente": [dict(p) for p in self._en_attente],
-            "joker_demande": self._joker_demande,
-            # Échange partiel (issue #138) : le panneau marque distinctement les
-            # lettres à échanger quand ``mode_echange`` est actif.
-            "type_echange": self._type_echange,
-            "mode_echange": self._mode_echange,
-            "selection_echange": list(self._selection_echange),
-        }
-
-    def _diffuser(self) -> None:
-        """Pousse l'état pertinent à la fenêtre Jeu après toute mutation (issue #90).
-
-        Depuis l'issue #187 (Issue B), le chevalet a migré de sa fenêtre flottante
-        séparée vers la zone C de ``jeu.html`` : les DEUX charges sont donc poussées
-        à la **même** fenêtre (``self._window_plateau``, l'unique fenêtre Jeu), qui
-        expose désormais les deux points d'entrée JS :
-
-        * ``window.appliquerEtatPlateau`` reçoit l'état **public**
-          (:meth:`_etat_plateau`), jamais de lettre du chevalet ;
-        * ``window.appliquerEtatChevalet`` reçoit l'état **complet**
-          (:meth:`_etat_chevalet`), lettres privées du seul joueur humain de
-          référence comprises.
-
-        Confidentialité (issues #33/#35, #99) — À NOTER : les lettres privées et
-        l'état public co-résident maintenant dans le même document, mais aucune
-        fuite n'est introduite : :meth:`_etat_chevalet` ne sérialise toujours que
-        le chevalet du joueur humain de référence (jamais un ordinateur ni un autre
-        humain), exactement comme lorsqu'il alimentait une fenêtre séparée. La
-        garantie de l'issue #99 est inchangée ; seule la fenêtre cible a changé.
-
-        Chaque appel est encadré d'un ``try/except`` (:meth:`_pousser`) : une
-        fenêtre fermée ou un JS pas encore prêt ne doit jamais faire planter une
-        action de jeu.
-
-        Depuis le nettoyage du modèle de fenêtres (issue #193), il n'existe plus
-        qu'une seule fenêtre : les deux charges y sont poussées, il n'y a plus de
-        fenêtre chevalet flottante à alimenter.
-        """
-        self._pousser(
-            self._window_plateau, "appliquerEtatPlateau", self._etat_plateau()
-        )
-        self._pousser(
-            self._window_plateau, "appliquerEtatChevalet", self._etat_chevalet()
-        )
-
-    @staticmethod
-    def _pousser(
-        window: webview.Window | None, fonction: str, charge: dict[str, Any]
-    ) -> None:
-        """Appelle ``window.<fonction>(<charge JSON>)`` si la fenêtre existe."""
-        if window is None:
-            return
-        script = (
-            f"window.{fonction} && window.{fonction}("
-            f"{json.dumps(charge, ensure_ascii=False)})"
-        )
-        try:
-            window.evaluate_js(script)
-        except Exception as e:  # noqa: BLE001 - une vue absente ne bloque pas le jeu
-            journal.erreur("Jeu : échec de la diffusion d'un état à une fenêtre.", e)
-
-    def _refuser_hors_tour(self) -> dict[str, Any] | None:
-        """Refus normalisé si une mutation de pose est tentée hors du tour.
-
-        Garde de tour de l'issue #99. Le panneau du joueur de référence est
-        désormais toujours visible et sélectionnable, y compris hors de son tour
-        (réflexion libre) ; mais **muter** l'état de pose (sélection, placement en
-        attente, retrait, annulation) reste réservé à son tour réel — jusqu'ici
-        c'était garanti seulement par le masquage du chevalet hors tour, ce qui
-        n'est plus le cas (signalé par le rapport #98).
-
-        Renvoie ``{"succes": False, "erreur": ...}`` si la partie est terminée ou
-        si ce n'est pas le tour du joueur humain de référence
-        (:func:`index_humain_reference`), sinon ``None`` (action autorisée).
-        """
-        partie = self._partie
-        if partie.terminee or partie.index_courant != index_humain_reference(
-            partie.joueurs
-        ):
-            return {"succes": False, "erreur": "Ce n'est pas votre tour."}
-        return None
-
     def selectionner_lettre(self, index: Any) -> dict[str, Any]:
         """Sélectionne (ou désélectionne) la lettre du chevalet d'index ``index``.
 
