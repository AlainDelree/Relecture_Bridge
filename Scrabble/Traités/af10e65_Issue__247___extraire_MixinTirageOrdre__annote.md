af10e65

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit af10e65
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 15:29:02 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #247 : extraire MixinTirageOrdre
    
    Crée src/scrabble/ui/api_tirage_ordre.py avec class MixinTirageOrdre contenant
    les méthodes déplacées depuis ApiJeu : obtenir_tirage_ordre, terminer_tirage,
    finaliser_entree_vue_jeu, _finaliser_entree_vue_jeu, supprimer_partie_annulee,
    annuler_tirage, obtenir_theme_plateau, journaliser_mesure_fenetre, obtenir_chevalet.
    
    En-tête de commentaire précisant la dépendance vers MixinDiffusion (self._diffuser).
    
    Modifie ApiJeu pour hériter de (MixinDiffusion, MixinTirageOrdre) et retire les
    méthodes déplacées de jeu.py.
    
    Ajuste les tests pour patcher au bon endroit (api_tirage_ordre au lieu de jeu).
    
    pytest : 747 passed. py_compile OK. Aucune duplication.
    
    Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/api_tirage_ordre.py b/src/scrabble/ui/api_tirage_ordre.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..c5e82c1
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/api_tirage_ordre.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (259 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,259 @@
+"""Mixin « tirage d'ordre » pour l'API Jeu (issue #247).
+
+Ce mixin regroupe les méthodes liées au **tirage de l'ordre de jeu** et à
+l'initialisation de l'écran de jeu : obtenir/terminer le tirage, finalisation
+d'entrée en vue jeu, annulation, thème plateau, mesures de fenêtre, chevalet
+public.
+
+Dépendances vers MixinDiffusion
+-------------------------------
+Ce mixin utilise les primitives suivantes de :class:`~.api_diffusion.MixinDiffusion` :
+
+- ``self._diffuser()`` — appelée par :meth:`_finaliser_entree_vue_jeu` pour
+  amorcer le panneau chevalet avec l'état frais après un ``load_url``.
+"""
+
+from __future__ import annotations
+
+import threading
+from typing import Any, TYPE_CHECKING
+
+from scrabble import journal
+from scrabble.config import THEMES_PLATEAU, charger_config
+from scrabble.persistance.stockage import supprimer_partie
+
+if TYPE_CHECKING:
+    import webview
+
+    from scrabble.moteur.partie import Partie
+
+
+class MixinTirageOrdre:
+    """Méthodes de tirage d'ordre et d'initialisation pour ApiJeu (issue #247)."""
+
+    # Attributs attendus sur la classe hôte (ApiJeu), déclarés pour les
+    # annotations — pas de valeur par défaut, ils vivent sur l'instance.
+    _partie: Partie | None
+    _id_partie: int | None
+    _infos_tirage: dict[str, Any] | None
+    _tirage_termine: bool
+    _retour_menu: bool
+    _window_plateau: "webview.Window | None"
+    _chemin_persistance: Any
+
+    # Méthodes attendues de MixinDiffusion (via l'héritage multiple d'ApiJeu).
+    def _diffuser(self) -> None: ...
+
+    # Méthode attendue d'ApiJeu.
+    @staticmethod
+    def _erreur_aucune_partie() -> dict[str, Any]: ...
+
+    # ------------------------------------------------------------------ #
+    # Tirage de l'ordre de jeu affiché dans la fenêtre Jeu (issue #170)
+    # ------------------------------------------------------------------ #
+
+    def obtenir_tirage_ordre(self) -> dict[str, Any] | None:
+        """Détail du tirage d'ordre à afficher au démarrage, ou ``None``.
+
+        Appelée par le JS de la fenêtre Jeu à l'initialisation : si une nouvelle
+        partie vient d'être lancée (« Lancer la partie » ou « Recommencer »), on
+        renvoie le détail reconstitué par :func:`detail_tirage_ordre`
+        (``{"tirages": [...], "ordre": [...]}``) pour que le JS affiche l'écran de
+        tirage à la place du plateau et des fiches ; le reste de l'interface (barre
+        globale comprise, issue #168) reste masqué tant que « Continuer » n'a pas
+        été cliqué. Renvoie ``None`` lors d'une reprise de partie (aucun tirage à
+        rejouer) : l'écran de jeu s'ouvre alors directement jouable.
+        """
+        from scrabble.ui.jeu import detail_tirage_ordre
+
+        if self._infos_tirage is None:
+            return None
+        return detail_tirage_ordre(
+            self._infos_tirage.get("noms_creation", []),
+            self._infos_tirage.get("graine"),
+            self._infos_tirage.get("noms_humains"),
+        )
+
+    def terminer_tirage(self) -> dict[str, Any]:
+        """Fin du tirage d'ordre : rend l'écran de jeu jouable (issue #170).
+
+        Appelée quand l'utilisateur clique « Continuer » sur l'écran de tirage.
+        Le JS, de son côté, réaffiche le plateau, les fiches joueurs, la barre
+        globale ET le panneau chevalet intégré (zone C). Depuis le nettoyage du
+        modèle de fenêtres (issue #193, plus de fenêtre chevalet compagnon à
+        révéler/positionner), Python n'a plus qu'à marquer le tirage terminé.
+
+        Idempotente (garde ``_tirage_termine``) : un second appel — reprise, ou
+        double-clic — est sans effet.
+        """
+        if self._tirage_termine:
+            return {"succes": True}
+        self._tirage_termine = True
+        journal.info(
+            f"Jeu : tirage d'ordre terminé (partie #{self._id_partie})."
+        )
+        return {"succes": True}
+
+    def finaliser_entree_vue_jeu(self) -> None:
+        """Rejoue la finalisation des fenêtres à chaque entrée en vue Jeu (issue #180).
+
+        Appelée par le routeur de la coquille mono-fenêtre unifiée
+        (:meth:`~scrabble.ui.application.ApiRouteur.demarrer_jeu`) juste après un
+        ``load_url('jeu.html')`` dans la fenêtre unique. Elle **rejoue à la
+        demande** ce que le chemin historique ne faisait qu'une fois, dans le
+        callback de ``webview.start`` (:func:`_finaliser_fenetres`) — car la
+        coquille unifiée n'a qu'**une seule** boucle ``webview.start`` pour toute
+        la session (rapport #178, risque 3) :
+
+        * **maximisation du plateau** (:func:`_maximiser_plateau`) — la fenêtre
+          unique, déjà affichée, est (ré)affirmée maximisée à chaque entrée ;
+        * **amorçage du panneau chevalet** (:meth:`_diffuser`) : la fenêtre ayant
+          été chargée une seule fois au démarrage — **avant** qu'une partie
+          n'existe — son ``obtenir_etat_chevalet`` initial n'a rien reçu. On lui
+          pousse donc l'état frais (l'``evaluate_js`` traverse le pont), pour que
+          les bonnes lettres soient prêtes, y compris pendant que le JS masque
+          encore la zone C le temps du tirage d'ordre.
+
+        Depuis le nettoyage du modèle de fenêtres (issue #193), il n'y a plus de
+        fenêtre chevalet compagnon à révéler, repositionner ou lier ici : le
+        chevalet est une zone de la fenêtre unique, montrée/masquée par le JS.
+
+        Exécutée dans un **fil dédié** (comme le callback de ``webview.start``) :
+        elle enchaîne des attentes ``shown`` et des déplacements de fenêtre qui ne
+        doivent pas bloquer le pont JS (l'appel ``api.demarrer_jeu()`` rend la main
+        immédiatement).
+        """
+        threading.Thread(
+            target=self._finaliser_entree_vue_jeu,
+            name="finaliser-entree-vue-jeu",
+            daemon=True,
+        ).start()
+
+    def _finaliser_entree_vue_jeu(self) -> None:
+        """Corps (hors fil) de :meth:`finaliser_entree_vue_jeu` — voir sa docstring."""
+        from scrabble.ui.jeu import _maximiser_plateau
+
+        plateau = self._window_plateau
+        if plateau is not None:
+            _maximiser_plateau(plateau)
+        # Amorce le panneau chevalet (zone C) pré-chargé — la fenêtre ayant été
+        # chargée une fois au démarrage, avant toute partie — avec l'état frais.
+        if self._partie is not None:
+            self._diffuser()
+
+    def supprimer_partie_annulee(self) -> None:
+        """Supprime de la persistance la partie créée puis annulée au tirage (issue #170).
+
+        Cœur « persistance » de l'annulation du tirage, isolé pour être partagé
+        entre le chemin de production (:meth:`annuler_tirage`, qui enchaîne ensuite
+        un ``destroy()`` des fenêtres) et la coquille unifiée
+        (:meth:`~scrabble.ui.application.ApiRouteur.annuler_tirage_accueil`, qui
+        enchaîne un retour à l'accueil par ``load_url``). À ce stade la partie a
+        été créée et suivie en base mais **aucun coup n'a été joué** : on la
+        supprime pour qu'elle n'apparaisse pas comme partie fantôme dans
+        « Reprendre une partie ».
+
+        Sans identifiant de persistance (``_id_partie`` à ``None``, mode
+        démonstration) il n'y a rien à supprimer. Une erreur de suppression est
+        seulement tracée : elle ne doit pas empêcher le retour à l'accueil.
+        """
+        if self._id_partie is None:
+            return
+        try:
+            supprimee = supprimer_partie(self._id_partie, self._chemin_persistance)
+            journal.info(
+                f"Jeu : tirage annulé — partie #{self._id_partie} supprimée "
+                f"(supprimee={supprimee})."
+            )
+        except Exception as e:  # noqa: BLE001 - on trace, sans planter la fermeture
+            journal.erreur(
+                f"Jeu : suppression de la partie #{self._id_partie} annulée "
+                "impossible.",
+                e,
+            )
+
+    def annuler_tirage(self) -> dict[str, Any]:
+        """Annule le tirage : supprime la partie créée et revient à l'accueil.
+
+        Point d'entrée du bouton « Annuler » de l'écran de tirage (issue #170,
+        reprise de l'annulation de la modale d'accueil, issue #67). À ce stade la
+        partie a été créée et suivie en base mais **aucun coup n'a été joué** : on
+        la supprime donc de la persistance (:func:`supprimer_partie`) pour qu'elle
+        n'apparaisse pas comme partie fantôme dans « Reprendre une partie », puis
+        on ferme la fenêtre de jeu et on rouvre l'accueil — en réutilisant le
+        mécanisme « Retour au menu » (drapeau ``_retour_menu`` lu par
+        :func:`lancer_jeu`, qui rappelle alors :func:`~scrabble.ui.accueil.
+        lancer_accueil`). L'écran de jeu ne s'étant pas encore ouvert visuellement
+        (le tirage est affiché à sa place), l'utilisateur perçoit un simple retour
+        à la configuration.
+
+        Retourne ``{"succes": True}`` si la fermeture a été demandée, sinon
+        ``{"succes": False, "erreur": ...}`` (le JS réactive alors le bouton).
+        """
+        if self._window_plateau is None:
+            return {"succes": False, "erreur": "Aucune fenêtre associée."}
+        self.supprimer_partie_annulee()
+        try:
+            # Retour à l'accueil via le même chemin que « Retour au menu ».
+            self._retour_menu = True
+            self._window_plateau.destroy()
+            return {"succes": True}
+        except Exception as e:  # noqa: BLE001 - on remonte l'erreur au JS
+            self._retour_menu = False
+            return {"succes": False, "erreur": f"Fermeture impossible : {e}"}
+
+    def obtenir_theme_plateau(self) -> str:
+        """Retourne le thème visuel du plateau choisi dans les réglages.
+
+        Lit ``theme_plateau`` de :func:`~scrabble.config.charger_config` (champ
+        auto-réparant : une valeur inconnue retombe sur ``"classique"``). Le JS
+        applique la classe CSS ``theme-<nom>`` correspondante au plateau et
+        choisit les libellés (complets ou abrégés). Par sécurité, si la valeur
+        lue n'est pas un thème connu, on renvoie ``"classique"``.
+        """
+        theme = charger_config().get("theme_plateau", "classique")
+        return theme if theme in THEMES_PLATEAU else "classique"
+
+    def journaliser_mesure_fenetre(self, mesures: dict[str, Any]) -> dict[str, Any]:
+        """Journalise la géométrie verticale réelle de l'écran de jeu (issue #152).
+
+        Sur le modèle de la trace de tirage (issue #116) et de la modale du joker
+        (issue #140), le JS mesure — au chargement de la fenêtre plateau, sous le
+        vrai moteur WebKitGTK — la hauteur totale de la fenêtre, le bas réel du
+        plateau et l'espace restant en dessous. Objectif : objectiver la
+        régression de l'issue #152 (moins d'espace sous le plateau qu'avant, le
+        chevalet — 175 px de haut minimum, cf. #140/#141 — empiétant sur le
+        plateau) et vérifier, après correctif, que l'espace disponible est bien
+        redevenu suffisant (``espace_sous_plateau`` >= ``chevalet_min``).
+
+        Purement informatif : n'altère aucun état, retourne toujours un succès.
+        """
+        try:
+            details = ", ".join(f"{cle}={valeur}" for cle, valeur in mesures.items())
+            journal.info(f"Jeu : géométrie réelle écran de jeu — {details}.")
+        except Exception as e:  # noqa: BLE001 - une trace ne doit jamais bloquer
+            journal.erreur("Jeu : échec de journalisation de la géométrie.", e)
+        return {"succes": True}
+
+    def obtenir_chevalet(self, index_joueur: int) -> dict[str, Any]:
+        """Retourne le chevalet du **seul** joueur d'index ``index_joueur``.
+
+        C'est le point d'entrée du bouton « voir mes lettres ». Il ne renvoie
+        jamais le chevalet d'un autre joueur ni la totalité des chevalets : le
+        joueur qui révèle ses lettres ne dévoile rien de celles des autres.
+        """
+        from scrabble.ui.jeu import serialiser_chevalet
+
+        if self._partie is None:
+            return self._erreur_aucune_partie()
+        if not isinstance(index_joueur, int) or not (
+            0 <= index_joueur < len(self._partie.joueurs)
+        ):
+            return {"succes": False, "erreur": "Index de joueur invalide."}
+        joueur = self._partie.joueurs[index_joueur]
+        return {
+            "succes": True,
+            "index": index_joueur,
+            "nom": joueur.nom,
+            "lettres": serialiser_chevalet(joueur),
+        }
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/jeu.py b/src/scrabble/ui/jeu.py
# (index — ignorable)
index 4d06ef6..de16fc9 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/jeu.py
# (après — fichier suivant)
+++ b/src/scrabble/ui/jeu.py
# ── Zone modifiée : ligne 79 (6 ligne(s)) dans l'ancienne version → ligne 79 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -79,6 +79,7 @@ from scrabble.regles.lettres import JOKER, valeur_lettre
 from scrabble.regles.plateau import TAILLE, type_case
 from scrabble.ui import TAPIS_VERT
 from scrabble.ui.api_diffusion import MixinDiffusion
+from scrabble.ui.api_tirage_ordre import MixinTirageOrdre
 
 DOSSIER_WEB = Path(__file__).parent / "web"
 
# ── Zone modifiée : ligne 1056 (7 ligne(s)) dans l'ancienne version → ligne 1057 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1056,7 +1057,7 @@ def detail_tirage_ordre(
 # --------------------------------------------------------------------------- #
 
 
-class ApiJeu(MixinDiffusion):
+class ApiJeu(MixinDiffusion, MixinTirageOrdre):
     """API Python exposée au JavaScript de l'écran de jeu (issue #90).
 
     Depuis l'issue #187 (migration du chevalet en zone C) puis l'issue #193
# ── Zone modifiée : ligne 1286 (210 ligne(s)) dans l'ancienne version → ligne 1287 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1286,210 +1287,6 @@ class ApiJeu(MixinDiffusion):
             return self._erreur_aucune_partie()
         return self._etat_chevalet()
 
-    # ------------------------------------------------------------------ #
-    # Tirage de l'ordre de jeu affiché dans la fenêtre Jeu (issue #170)
-    # ------------------------------------------------------------------ #
-
-    def obtenir_tirage_ordre(self) -> dict[str, Any] | None:
-        """Détail du tirage d'ordre à afficher au démarrage, ou ``None``.
-
-        Appelée par le JS de la fenêtre Jeu à l'initialisation : si une nouvelle
-        partie vient d'être lancée (« Lancer la partie » ou « Recommencer »), on
-        renvoie le détail reconstitué par :func:`detail_tirage_ordre`
-        (``{"tirages": [...], "ordre": [...]}``) pour que le JS affiche l'écran de
-        tirage à la place du plateau et des fiches ; le reste de l'interface (barre
-        globale comprise, issue #168) reste masqué tant que « Continuer » n'a pas
-        été cliqué. Renvoie ``None`` lors d'une reprise de partie (aucun tirage à
-        rejouer) : l'écran de jeu s'ouvre alors directement jouable.
-        """
-        if self._infos_tirage is None:
-            return None
-        return detail_tirage_ordre(
-            self._infos_tirage.get("noms_creation", []),
-            self._infos_tirage.get("graine"),
-            self._infos_tirage.get("noms_humains"),
-        )
-
-    def terminer_tirage(self) -> dict[str, Any]:
-        """Fin du tirage d'ordre : rend l'écran de jeu jouable (issue #170).
-
-        Appelée quand l'utilisateur clique « Continuer » sur l'écran de tirage.
-        Le JS, de son côté, réaffiche le plateau, les fiches joueurs, la barre
-        globale ET le panneau chevalet intégré (zone C). Depuis le nettoyage du
-        modèle de fenêtres (issue #193, plus de fenêtre chevalet compagnon à
-        révéler/positionner), Python n'a plus qu'à marquer le tirage terminé.
-
-        Idempotente (garde ``_tirage_termine``) : un second appel — reprise, ou
-        double-clic — est sans effet.
-        """
-        if self._tirage_termine:
-            return {"succes": True}
-        self._tirage_termine = True
-        journal.info(
-            f"Jeu : tirage d'ordre terminé (partie #{self._id_partie})."
-        )
-        return {"succes": True}
-
-    def finaliser_entree_vue_jeu(self) -> None:
-        """Rejoue la finalisation des fenêtres à chaque entrée en vue Jeu (issue #180).
-
-        Appelée par le routeur de la coquille mono-fenêtre unifiée
-        (:meth:`~scrabble.ui.application.ApiRouteur.demarrer_jeu`) juste après un
-        ``load_url('jeu.html')`` dans la fenêtre unique. Elle **rejoue à la
-        demande** ce que le chemin historique ne faisait qu'une fois, dans le
-        callback de ``webview.start`` (:func:`_finaliser_fenetres`) — car la
-        coquille unifiée n'a qu'**une seule** boucle ``webview.start`` pour toute
-        la session (rapport #178, risque 3) :
-
-        * **maximisation du plateau** (:func:`_maximiser_plateau`) — la fenêtre
-          unique, déjà affichée, est (ré)affirmée maximisée à chaque entrée ;
-        * **amorçage du panneau chevalet** (:meth:`_diffuser`) : la fenêtre ayant
-          été chargée une seule fois au démarrage — **avant** qu'une partie
-          n'existe — son ``obtenir_etat_chevalet`` initial n'a rien reçu. On lui
-          pousse donc l'état frais (l'``evaluate_js`` traverse le pont), pour que
-          les bonnes lettres soient prêtes, y compris pendant que le JS masque
-          encore la zone C le temps du tirage d'ordre.
-
-        Depuis le nettoyage du modèle de fenêtres (issue #193), il n'y a plus de
-        fenêtre chevalet compagnon à révéler, repositionner ou lier ici : le
-        chevalet est une zone de la fenêtre unique, montrée/masquée par le JS.
-
-        Exécutée dans un **fil dédié** (comme le callback de ``webview.start``) :
-        elle enchaîne des attentes ``shown`` et des déplacements de fenêtre qui ne
-        doivent pas bloquer le pont JS (l'appel ``api.demarrer_jeu()`` rend la main
-        immédiatement).
-        """
-        threading.Thread(
-            target=self._finaliser_entree_vue_jeu,
-            name="finaliser-entree-vue-jeu",
-            daemon=True,
-        ).start()
-
-    def _finaliser_entree_vue_jeu(self) -> None:
-        """Corps (hors fil) de :meth:`finaliser_entree_vue_jeu` — voir sa docstring."""
-        plateau = self._window_plateau
-        if plateau is not None:
-            _maximiser_plateau(plateau)
-        # Amorce le panneau chevalet (zone C) pré-chargé — la fenêtre ayant été
-        # chargée une fois au démarrage, avant toute partie — avec l'état frais.
-        if self._partie is not None:
-            self._diffuser()
-
-    def supprimer_partie_annulee(self) -> None:
-        """Supprime de la persistance la partie créée puis annulée au tirage (issue #170).
-
-        Cœur « persistance » de l'annulation du tirage, isolé pour être partagé
-        entre le chemin de production (:meth:`annuler_tirage`, qui enchaîne ensuite
-        un ``destroy()`` des fenêtres) et la coquille unifiée
-        (:meth:`~scrabble.ui.application.ApiRouteur.annuler_tirage_accueil`, qui
-        enchaîne un retour à l'accueil par ``load_url``). À ce stade la partie a
-        été créée et suivie en base mais **aucun coup n'a été joué** : on la
-        supprime pour qu'elle n'apparaisse pas comme partie fantôme dans
-        « Reprendre une partie ».
-
-        Sans identifiant de persistance (``_id_partie`` à ``None``, mode
-        démonstration) il n'y a rien à supprimer. Une erreur de suppression est
-        seulement tracée : elle ne doit pas empêcher le retour à l'accueil.
-        """
-        if self._id_partie is None:
-            return
-        try:
-            supprimee = supprimer_partie(self._id_partie, self._chemin_persistance)
-            journal.info(
-                f"Jeu : tirage annulé — partie #{self._id_partie} supprimée "
-                f"(supprimee={supprimee})."
-            )
-        except Exception as e:  # noqa: BLE001 - on trace, sans planter la fermeture
-            journal.erreur(
-                f"Jeu : suppression de la partie #{self._id_partie} annulée "
-                "impossible.",
-                e,
-            )
-
-    def annuler_tirage(self) -> dict[str, Any]:
-        """Annule le tirage : supprime la partie créée et revient à l'accueil.
-
-        Point d'entrée du bouton « Annuler » de l'écran de tirage (issue #170,
-        reprise de l'annulation de la modale d'accueil, issue #67). À ce stade la
-        partie a été créée et suivie en base mais **aucun coup n'a été joué** : on
-        la supprime donc de la persistance (:func:`supprimer_partie`) pour qu'elle
-        n'apparaisse pas comme partie fantôme dans « Reprendre une partie », puis
-        on ferme la fenêtre de jeu et on rouvre l'accueil — en réutilisant le
-        mécanisme « Retour au menu » (drapeau ``_retour_menu`` lu par
-        :func:`lancer_jeu`, qui rappelle alors :func:`~scrabble.ui.accueil.
-        lancer_accueil`). L'écran de jeu ne s'étant pas encore ouvert visuellement
-        (le tirage est affiché à sa place), l'utilisateur perçoit un simple retour
-        à la configuration.
-
-        Retourne ``{"succes": True}`` si la fermeture a été demandée, sinon
-        ``{"succes": False, "erreur": ...}`` (le JS réactive alors le bouton).
-        """
-        if self._window_plateau is None:
-            return {"succes": False, "erreur": "Aucune fenêtre associée."}
-        self.supprimer_partie_annulee()
-        try:
-            # Retour à l'accueil via le même chemin que « Retour au menu ».
-            self._retour_menu = True
-            self._window_plateau.destroy()
-            return {"succes": True}
-        except Exception as e:  # noqa: BLE001 - on remonte l'erreur au JS
-            self._retour_menu = False
-            return {"succes": False, "erreur": f"Fermeture impossible : {e}"}
-
-    def obtenir_theme_plateau(self) -> str:
-        """Retourne le thème visuel du plateau choisi dans les réglages.
-
-        Lit ``theme_plateau`` de :func:`~scrabble.config.charger_config` (champ
-        auto-réparant : une valeur inconnue retombe sur ``"classique"``). Le JS
-        applique la classe CSS ``theme-<nom>`` correspondante au plateau et
-        choisit les libellés (complets ou abrégés). Par sécurité, si la valeur
-        lue n'est pas un thème connu, on renvoie ``"classique"``.
-        """
-        theme = charger_config().get("theme_plateau", "classique")
-        return theme if theme in THEMES_PLATEAU else "classique"
-
-    def journaliser_mesure_fenetre(self, mesures: dict[str, Any]) -> dict[str, Any]:
-        """Journalise la géométrie verticale réelle de l'écran de jeu (issue #152).
-
-        Sur le modèle de la trace de tirage (issue #116) et de la modale du joker
-        (issue #140), le JS mesure — au chargement de la fenêtre plateau, sous le
-        vrai moteur WebKitGTK — la hauteur totale de la fenêtre, le bas réel du
-        plateau et l'espace restant en dessous. Objectif : objectiver la
-        régression de l'issue #152 (moins d'espace sous le plateau qu'avant, le
-        chevalet — 175 px de haut minimum, cf. #140/#141 — empiétant sur le
-        plateau) et vérifier, après correctif, que l'espace disponible est bien
-        redevenu suffisant (``espace_sous_plateau`` >= ``chevalet_min``).
-
-        Purement informatif : n'altère aucun état, retourne toujours un succès.
-        """
-        try:
-            details = ", ".join(f"{cle}={valeur}" for cle, valeur in mesures.items())
-            journal.info(f"Jeu : géométrie réelle écran de jeu — {details}.")
-        except Exception as e:  # noqa: BLE001 - une trace ne doit jamais bloquer
-            journal.erreur("Jeu : échec de journalisation de la géométrie.", e)
-        return {"succes": True}
-
-    def obtenir_chevalet(self, index_joueur: int) -> dict[str, Any]:
-        """Retourne le chevalet du **seul** joueur d'index ``index_joueur``.
-
-        C'est le point d'entrée du bouton « voir mes lettres ». Il ne renvoie
-        jamais le chevalet d'un autre joueur ni la totalité des chevalets : le
-        joueur qui révèle ses lettres ne dévoile rien de celles des autres.
-        """
-        if self._partie is None:
-            return self._erreur_aucune_partie()
-        if not isinstance(index_joueur, int) or not (
-            0 <= index_joueur < len(self._partie.joueurs)
-        ):
-            return {"succes": False, "erreur": "Index de joueur invalide."}
-        joueur = self._partie.joueurs[index_joueur]
-        return {
-            "succes": True,
-            "index": index_joueur,
-            "nom": joueur.nom,
-            "lettres": serialiser_chevalet(joueur),
-        }
-
     # ------------------------------------------------------------------ #
     # État de pose partagé et diffusion aux deux fenêtres (issue #90)
     # ------------------------------------------------------------------ #
# (diff du fichier suivant)
diff --git a/tests/test_application.py b/tests/test_application.py
# (index — ignorable)
index ff5aa9e..871936c 100644
# (avant — fichier suivant)
--- a/tests/test_application.py
# (après — fichier suivant)
+++ b/tests/test_application.py
# ── Zone modifiée : ligne 405 (7 ligne(s)) dans l'ancienne version → ligne 405 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -405,7 +405,7 @@ class TestTransitionsJeuAccueil:
         assert routeur._api_jeu._recommencer is False
 
     def test_annuler_tirage_accueil_supprime_puis_retourne(self, monkeypatch):
-        from scrabble.ui import jeu as mod
+        from scrabble.ui import api_tirage_ordre as mod
 
         supprimees: list = []
         monkeypatch.setattr(
# ── Zone modifiée : ligne 438 (7 ligne(s)) dans l'ancienne version → ligne 438 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -438,7 +438,7 @@ class TestTransitionsJeuAccueil:
             journal, "cloturer_session", lambda *a, **k: cloturees.append(1)
         )
         monkeypatch.setattr(
-            "scrabble.ui.jeu.supprimer_partie", lambda id_p, chemin: True
+            "scrabble.ui.api_tirage_ordre.supprimer_partie", lambda id_p, chemin: True
         )
 
         routeur, _fenetre, partie, _appels = self._routeur_en_jeu(
# (diff du fichier suivant)
diff --git a/tests/test_jeu.py b/tests/test_jeu.py
# (index — ignorable)
index 175a92e..50dc5dd 100644
# (avant — fichier suivant)
--- a/tests/test_jeu.py
# (après — fichier suivant)
+++ b/tests/test_jeu.py
# ── Zone modifiée : ligne 305 (7 ligne(s)) dans l'ancienne version → ligne 305 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -305,7 +305,7 @@ class TestThemePlateau:
     def test_theme_valide_transmis(self, monkeypatch):
         """Un thème reconnu dans la config est renvoyé tel quel."""
         monkeypatch.setattr(
-            "scrabble.ui.jeu.charger_config", lambda: {"theme_plateau": "vert"}
+            "scrabble.ui.api_tirage_ordre.charger_config", lambda: {"theme_plateau": "vert"}
         )
         api = ApiJeu(_partie_simple(), id_partie=1)
         assert api.obtenir_theme_plateau() == "vert"
# ── Zone modifiée : ligne 313 (14 ligne(s)) dans l'ancienne version → ligne 313 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -313,14 +313,14 @@ class TestThemePlateau:
     def test_theme_inconnu_retombe_sur_classique(self, monkeypatch):
         """Une valeur imprévue (config trafiquée) est ramenée à « classique »."""
         monkeypatch.setattr(
-            "scrabble.ui.jeu.charger_config", lambda: {"theme_plateau": "n_importe_quoi"}
+            "scrabble.ui.api_tirage_ordre.charger_config", lambda: {"theme_plateau": "n_importe_quoi"}
         )
         api = ApiJeu(_partie_simple(), id_partie=1)
         assert api.obtenir_theme_plateau() == "classique"
 
     def test_theme_absent_retombe_sur_classique(self, monkeypatch):
         """Clé absente de la config : défaut « classique »."""
-        monkeypatch.setattr("scrabble.ui.jeu.charger_config", lambda: {})
+        monkeypatch.setattr("scrabble.ui.api_tirage_ordre.charger_config", lambda: {})
         api = ApiJeu(_partie_simple(), id_partie=1)
         assert api.obtenir_theme_plateau() == "classique"
 
# ── Zone modifiée : ligne 2504 (7 ligne(s)) dans l'ancienne version → ligne 2504 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2504,7 +2504,7 @@ class TestApiJeuTirageOrdre:
         assert api._tirage_termine is True
 
     def test_annuler_tirage_supprime_la_partie_et_ferme(self, monkeypatch):
-        from scrabble.ui import jeu as mod
+        from scrabble.ui import api_tirage_ordre as mod
 
         supprimees: list = []
         monkeypatch.setattr(
# ── Zone modifiée : ligne 2587 (7 ligne(s)) dans l'ancienne version → ligne 2587 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2587,7 +2587,7 @@ class TestApiJeuHelpersCoquilleUnifiee:
         assert infos is not None
 
     def test_supprimer_partie_annulee_supprime_via_persistance(self, monkeypatch):
-        from scrabble.ui import jeu as mod
+        from scrabble.ui import api_tirage_ordre as mod
 
         supprimees: list = []
         monkeypatch.setattr(
# ── Zone modifiée : ligne 2601 (7 ligne(s)) dans l'ancienne version → ligne 2601 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2601,7 +2601,7 @@ class TestApiJeuHelpersCoquilleUnifiee:
         assert supprimees == [42]
 
     def test_supprimer_partie_annulee_mode_demo_ne_supprime_rien(self, monkeypatch):
-        from scrabble.ui import jeu as mod
+        from scrabble.ui import api_tirage_ordre as mod
 
         supprimees: list = []
         monkeypatch.setattr(
