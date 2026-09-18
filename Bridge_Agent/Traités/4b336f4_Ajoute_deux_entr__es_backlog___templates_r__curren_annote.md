4b336f4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4b336f4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 20:43:58 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute deux entrées backlog : templates récurrents + projet CCW dédié

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e4f6986..e9b4c6f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 4 (6 ligne(s)) dans l'ancienne version → ligne 4 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,6 +4,46 @@ Idées et pistes non prioritaires, à réaliser éventuellement plus tard.
 Alain peut modifier ce fichier directement, sans passer par une issue.
 
 ---
+## Issues récurrentes — bibliothèque de templates par projet
+
+**Contexte** : certaines issues reviennent régulièrement à l'identique ou
+quasi-identique (ex. build Scrabble, build Actualise). Aujourd'hui il faut
+soit redemander à Claude Chat de régénérer l'issue, soit fouiller dans les
+conversations passées pour retrouver la dernière version.
+
+**Idée** : un onglet « Templates » dans new_issue.py permettant de gérer
+une bibliothèque d'issues types par projet. Cliquer sur un template
+pré-remplit le formulaire (titre + corps complet), prêt à envoyer en un
+clic. Création/modification des templates depuis l'interface, stockés
+localement (ex. JSON dans configs/ ou dossier dédié templates/, gitignoré
+ou versionné selon le choix d'Alain).
+
+**Statut** : idée en attente, pas de développement lancé.
+
+---
+
+## Projet dédié à la communication CCL ↔ CCW
+
+**Contexte** : aujourd'hui les issues Windows passent par le projet
+`bridge_agent` avec le label `for-windows`, ce qui est contre-intuitif —
+bridge_agent est le projet de l'infrastructure elle-même, pas un relais
+CCL↔CCW. Avec le futur setup (ThinkPad Linux + fixe Windows en parallèle),
+la communication inter-agents va prendre de l'ampleur et mérite son propre
+espace.
+
+**Idée** : créer un projet dédié (ex. `ccw_relay` ou `bridge_ccw`) dont
+le seul rôle est de porter les issues `for-windows`. Le watcher CCW
+surveillerait ce dépôt au lieu de bridge_agent. Les issues CCW auraient
+leur propre historique, leur propre CHANGELOG, leur propre CONTEXTE.md —
+sans polluer bridge_agent.
+
+**Points à concevoir** : migration des issues CCW existantes ou simple
+bascule à partir d'une date, adaptation du provisioning CCW (clone du
+nouveau dépôt, config NSSM), labels à recréer sur le nouveau dépôt.
+
+**Statut** : idée en attente, setup physique (fixe Windows) pas encore
+en place. À reprendre quand le nouveau hardware sera opérationnel.
+
 ## Empecher Claude Chat de créer des issues trop détailler
 Parfois, Claude Chat ecrit de tres longue issue en détaillant beaucoup trop le code et ce faisant fait le travail de CCL.  Il faut trouver un moyen(consigne ou autre) pour le maintenir dans des issues de plus haut niveau.  Exemple d'issue détaillé ci-après:
 
