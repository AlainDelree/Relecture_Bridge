7ddf9cc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7ddf9cc
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 11:44:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #317 : ajout entrée backlog champ de recherche onglet Résultats

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b761c8e..51acac2 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 216 (3 ligne(s)) dans l'ancienne version → ligne 216 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -216,3 +216,27 @@ silencieusement son propre périmètre d'exécution.
 
 **Statut** : idée en attente, pas de développement lancé. Diagnostic
 établi le 31/07/2026 (issue #298).
+
+---
+
+## Champ de recherche texte dans l'onglet Résultats de new_issue.py
+
+**Contexte** : le 02/08/2026, une issue a été envoyée deux fois par
+inadvertance (#315 et #316, doublon), faute de moyen rapide de
+vérifier si une issue similaire avait déjà été traitée. Une alerte
+automatique basée sur la similarité de titre a été envisagée mais
+écartée : les templates d'issues récurrentes (ex. « Rebuild
+exécutable/installeur Scrabble », revenu une dizaine de fois pour des
+raisons différentes) produiraient trop de faux positifs, menant à
+ignorer l'alerte.
+
+**Idée** : ajouter un champ de recherche texte dans l'onglet Résultats
+de `new_issue.py`, filtrant sur titre ET corps des issues déjà
+envoyées (pas seulement le titre, pour retrouver une issue même si son
+libellé a légèrement varié d'une version à l'autre). Objectif :
+vérifier rapidement, en cas de doute, si un sujet a déjà été traité
+avant d'envoyer une nouvelle issue — sans alerte intrusive ni faux
+positif automatique.
+
+**Statut** : idée en attente, pas de développement lancé. Reçue le
+02/08/2026 (issue #317), suite au doublon #315/#316.
