## Issue #53 — 2026-09-20

- Doc : `RELECTURE_WEB_DOC.md` section 7 (`branches_cibles.conf`)
  corrigée — le passage affirmait encore que déclarer plusieurs
  branches cibles pour un projet « fait toujours planter la génération
  de la page `/projet/<nom>` », ce que l'issue #50 a corrigé
  (`est_branche_mergee` et `get_diagnostic_doublons_branche` gèrent
  désormais une liste de cibles). Le texte reflète maintenant l'état
  réel : la page s'affiche sans erreur, le badge « fusionnée » est
  correct (vrai si fusionnée dans au moins une cible) ; seul le bouton
  **Merger** reste à corriger, renvoi explicite vers l'issue #51 pour
  ce point précis.
