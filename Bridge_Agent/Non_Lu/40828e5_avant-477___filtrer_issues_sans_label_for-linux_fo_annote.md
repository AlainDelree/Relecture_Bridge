40828e5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 40828e5
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 20:52:45 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-477 : filtrer issues sans label for-linux/for-windows dans lister_issues

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1f1c3e6..4e858c6 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 24 (25 ligne(s)) dans l'ancienne version → ligne 24 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,25 +24,17 @@ sans polluer bridge_agent.
 bascule à partir d'une date, adaptation du provisioning CCW (clone du
 nouveau dépôt, config NSSM), labels à recréer sur le nouveau dépôt.
 
-**Statut** : idée en attente, setup physique (fixe Windows) pas encore
-en place. À reprendre quand le nouveau hardware sera opérationnel.
+**Statut** : évalué le 2026-08-21 — coût de migration élevé pour un
+bénéfice surtout esthétique. Le label `for-windows` sur bridge_agent fait
+le travail sans friction. À reconsidérer si des projets exclusivement
+Windows voient le jour et justifient un espace dédié.
 
 ## Calibration TIMEOUT — v2 (backtest des constantes)
 
-**Contexte** : la formule du §19 est
-`TIMEOUT_suggéré = max((duree_typique + k × variabilite) × F × backoff, plancher)`
-— EWMA par `projet|TYPE|mode|complexite`, demi-vie 15 issues, k=4,
-plancher 30 s, facteur d'ambiance `F` de demi-vie 4 h. Cette valeur reste
-purement INDICATIVE : le TIMEOUT réellement appliqué est celui de
-l'en-tête de l'issue (`extraire_timeout`).
-
-**Les trois défauts identifiés le 29/07/2026 sont corrigés** :
-- Défaut 1+2 : champ `RESEAU` implémenté, `F_reseau`/`F_local` alimentés,
-  fallback corrigé dans `lire_timeout_suggere` (#435).
-- Défaut 3 : champ `COMPLEXITE` ajouté comme 4e dimension de la clé EWMA
-  (#434).
-
-**Ce qui reste** : valider empiriquement les constantes
-(`K_VARIABILITE=4`, `DEMI_VIE_ISSUES=15`, `DEMI_VIE_AMBIANCE_HEURES=4`)
-par backtest sur `historique_durees.json` une fois ~20 observations
-accumulées par clé `projet|TYPE|mode|complexite`.
+**Statut** : ✅ Réalisé le 2026-08-21 — backtest effectué sur 1070
+observations (issues #475). Résultats : K=4 → 97% couverture (ratio
+médian 6.63x), K=3 → 96% couverture (ratio médian 5.36x). K passé à 3
+(issue #475), `k_utilise` enregistré dans `historique_durees.json` pour
+permettre la comparaison a posteriori. `DEMI_VIE_ISSUES=15` validée —
+toutes les demi-vies testées donnent 97% globalement. Pas de v2 nécessaire
+pour l'instant.
