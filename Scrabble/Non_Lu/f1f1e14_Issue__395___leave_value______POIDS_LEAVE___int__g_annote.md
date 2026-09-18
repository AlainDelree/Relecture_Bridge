f1f1e14

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f1f1e14
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 11:38:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #395 : leave_value() + _POIDS_LEAVE + intégration _score_strategique

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/moteur/ia.py b/src/scrabble/moteur/ia.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9f35cb0..8e3db81 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/moteur/ia.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/moteur/ia.py
# ── Zone modifiée : ligne 86 (11 ligne(s)) dans l'ancienne version → ligne 86 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -86,11 +86,13 @@ un générateur aléatoire à graine fixée pour des tests reproductibles.
 from __future__ import annotations
 
 import random
+from collections.abc import Sequence
 from enum import Enum, auto
 from typing import TYPE_CHECKING
 
 from scrabble.moteur.generateur import CoupNote, generer_coups
 from scrabble.moteur.plateau_partie import Coup, PlateauPartie
+from scrabble.regles.lettres import JOKER
 from scrabble.regles.plateau import TypeCase
 
 if TYPE_CHECKING:
# ── Zone modifiée : ligne 188 (8 ligne(s)) dans l'ancienne version → ligne 190 (87 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -188,8 +190,87 @@ _CASES_BONUS_MOT = frozenset({TypeCase.MOT_DOUBLE, TypeCase.MOT_TRIPLE, TypeCase
 #: pénalité longueur s'applique.
 _SEUIL_PENALITE_LONGUEUR = 2
 
+#: Valeur heuristique de chaque lettre pour le calcul du reliquat (leave
+#: value, issue #395). Reflète la difficulté de placement future : le
+#: joker et le S (formation de pluriels/hooks) valent le plus cher, les
+#: lettres rares (Q/K/W/X/Z) le moins. Une lettre absente vaut 0.0
+#: (utilisé via ``.get()``, jamais levé en KeyError).
+_VALEURS_LEAVE: dict[str, float] = {
+    JOKER: 24.0,
+    # Voyelles
+    "E": 5.0,
+    "A": 4.0,
+    "I": 3.5,
+    "O": 3.0,
+    "U": 2.0,
+    # Consonnes fortes
+    "S": 9.0,
+    "R": 5.5,
+    "N": 4.5,
+    "T": 4.0,
+    "L": 3.5,
+    # Consonnes moyennes
+    "D": 3.0,
+    "M": 3.0,
+    "P": 2.5,
+    "C": 2.5,
+    "B": 2.0,
+    "F": 2.0,
+    "G": 2.0,
+    "H": 2.0,
+    "V": 2.0,
+    # Consonnes faibles
+    "J": 1.0,
+    "Y": 1.5,
+    "Q": 0.5,
+    "K": 0.5,
+    "W": 0.5,
+    "X": 0.5,
+    "Z": 0.5,
+}
+
+#: Voyelles comptées pour l'ajustement d'équilibre de :func:`leave_value`.
+_VOYELLES_LEAVE = frozenset("AEIOU")
+
+#: Poids d'intégration de la leave value dans :func:`_score_strategique`,
+#: par niveau (issue #395). Nul pour DEBUTANT/FACILE : ces niveaux
+#: n'anticipent pas la qualité du reliquat, cohérent avec leur tirage très
+#: large. Croissant avec le niveau, plafonné à 1.0 (poids plein) à partir
+#: d'EXPERT.
+_POIDS_LEAVE: dict[Niveau, float] = {
+    Niveau.DEBUTANT: 0.0,
+    Niveau.FACILE: 0.0,
+    Niveau.INTERMEDIAIRE: 0.3,
+    Niveau.AVANCE: 0.6,
+    Niveau.EXPERT: 1.0,
+    Niveau.CHAMPION_DU_MONDE: 1.0,
+}
+
+
+def leave_value(lettres: Sequence[str]) -> float:
+    """Valeur heuristique du reliquat (lettres restant au chevalet après un coup).
+
+    Combine la somme des valeurs individuelles (:data:`_VALEURS_LEAVE`) avec
+    un ajustement d'équilibre voyelles/consonnes : bonus (+4.0) si le
+    reliquat compte 2 à 4 voyelles (mélange jouable), malus (-4.0) s'il en
+    compte 0-1 (pas de quoi combiner) ou 5 et plus (engorgement). Renvoie
+    0.0 pour un reliquat vide (aucun ajustement d'équilibre appliqué).
+    """
+    if not lettres:
+        return 0.0
 
-def _score_strategique(cn: CoupNote, niveau: Niveau) -> int:
+    total = sum(_VALEURS_LEAVE.get(lettre, 0.0) for lettre in lettres)
+    nb_voyelles = sum(1 for lettre in lettres if lettre in _VOYELLES_LEAVE)
+    if nb_voyelles in (2, 3, 4):
+        total += 4.0
+    else:
+        total -= 4.0
+    return total
+
+
+def _score_strategique(
+    cn: CoupNote, niveau: Niveau, lettres_restantes: Sequence[str] = ()
+) -> int:
     """Score ajusté servant UNIQUEMENT au tri des coups par niveau IA.
 
     N'affecte pas :attr:`CoupNote.score` (score réel affiché/marqué) : c'est
# ── Zone modifiée : ligne 206 (6 ligne(s)) dans l'ancienne version → ligne 287 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -206,6 +287,13 @@ def _score_strategique(cn: CoupNote, niveau: Niveau) -> int:
     faible, cohérent avec l'idée qu'un débutant humain *essaie* de faire de
     vrais mots — c'est la qualité de sa recherche qui est faible, pas son
     style de jeu.
+
+    Un troisième ajustement, optionnel, prend en compte ``lettres_restantes``
+    (le reliquat au chevalet après ce coup) : sa valeur heuristique
+    (:func:`leave_value`) est ajoutée au score, pondérée par
+    :data:`_POIDS_LEAVE` selon le niveau (nulle pour DEBUTANT/FACILE — ces
+    niveaux restent inchangés) et arrondie à l'entier pour rester cohérente
+    avec le type de retour ``int`` (issue #395).
     """
     ajustement = 0
 
# ── Zone modifiée : ligne 226 (6 ligne(s)) dans l'ancienne version → ligne 314 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -226,6 +314,9 @@ def _score_strategique(cn: CoupNote, niveau: Niveau) -> int:
             bonus //= 2
         ajustement += bonus
 
+    if _POIDS_LEAVE[niveau] > 0.0:
+        ajustement += round(_POIDS_LEAVE[niveau] * leave_value(lettres_restantes))
+
     return cn.score + ajustement
 
 
# ── Zone modifiée : ligne 238 (6 ligne(s)) dans l'ancienne version → ligne 329 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -238,6 +329,15 @@ def choisir_coup(
 ) -> Coup | None:
     """Choisit un coup selon le niveau IA, ou None pour passer.
 
+    Le tri par score stratégique (:func:`_score_strategique`) est fait en
+    deux passes : une première passe sans reliquat, puis une seconde qui
+    calcule, pour chaque coup, les lettres restant au chevalet une fois ce
+    coup joué (chevalet moins :attr:`~scrabble.moteur.generateur.CoupNote.lettres_du_chevalet`)
+    et relance le tri avec ce score enrichi de la leave value (issue #395).
+    Le reliquat dépendant de chaque coup individuellement, il ne peut pas
+    être calculé une fois pour toute la liste — d'où la lambda qui le
+    recalcule à la volée pour chaque comparaison.
+
     Args:
         plateau: État courant du plateau de jeu.
         chevalet: Jetons disponibles pour le joueur IA.
# ── Zone modifiée : ligne 256 (6 ligne(s)) dans l'ancienne version → ligne 356 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -256,6 +356,18 @@ def choisir_coup(
 
     coups = sorted(coups, key=lambda cn: _score_strategique(cn, niveau), reverse=True)
 
+    def _lettres_restantes(cn: CoupNote) -> list[str]:
+        restantes = list(chevalet)
+        for lettre in cn.lettres_du_chevalet:
+            restantes.remove(lettre)
+        return restantes
+
+    coups = sorted(
+        coups,
+        key=lambda cn: _score_strategique(cn, niveau, _lettres_restantes(cn)),
+        reverse=True,
+    )
+
     if niveau in (Niveau.EXPERT, Niveau.CHAMPION_DU_MONDE):
         return _choisir_expert(coups, rng)
     if niveau == Niveau.AVANCE:
