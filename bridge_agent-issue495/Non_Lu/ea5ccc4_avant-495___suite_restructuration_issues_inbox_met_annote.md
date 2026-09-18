ea5ccc4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ea5ccc4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 27 18:23:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-495 : suite restructuration issues_inbox methode principale (relance timeout)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index af0bf85..0efdd83 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 17 (6 ligne(s)) dans l'ancienne version → ligne 17 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -17,6 +17,17 @@ Claude Chat → crée une issue → GitHub → watcher.py détecte → CCL exéc
 → poste le résultat en commentaire → ferme l'issue → notification GSM/bureau
 ```
 
+> **Créer une issue : deux méthodes, une principale (§3) et une de backup
+> (§20).** La méthode à utiliser en priorité est le dépôt d'un fichier
+> `.txt` dans `~/Bridge_Agent/issues_inbox/` (§3) : Claude Chat dépose,
+> le watcher spool crée l'issue tout seul, sans repasser par le formulaire
+> web. Le copier-coller dans le formulaire web `new_issue.py` (§20) reste
+> intégralement fonctionnel et documenté, mais en tant que **backup** —
+> utile si le watcher spool est indisponible, pour une création manuelle
+> par Alain directement dans le navigateur, ou pour l'aperçu de la commande
+> avant envoi (fonctionnalité propre au formulaire, sans équivalent côté
+> spool).
+
 > **Rafraîchissement automatique du clone local en début de cycle (issue #185).**
 > Au début de **chaque cycle de polling** — juste avant de lister les issues
 > ouvertes — `watcher.py` lance un `git pull --ff-only` dans son répertoire de
# ── Zone modifiée : ligne 312 (7 ligne(s)) dans l'ancienne version → ligne 323 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -312,7 +323,7 @@ Le watcher lit ces champs dans le tableau markdown de l'en-tête :
 
 | Champ | Valeur | Effet |
 |-------|--------|-------|
-| `MODE` | `lecture` ou `écriture` | Auto-détecté par `new_issue.py` (§3, issue #326) pour pré-sélectionner le radio Mode du formulaire ; c'est ce radio, pas la valeur du champ, qui arme (ou non) le label `mode_write` posé sur l'issue — donc le mode écriture de CCL. Défaut lecture si absent/non reconnu. Voir §5 pour le comportement de chaque mode. |
+| `MODE` | `lecture` ou `écriture` | Auto-détecté par `new_issue.py` (§20, issue #326) pour pré-sélectionner le radio Mode du formulaire ; c'est ce radio, pas la valeur du champ, qui arme (ou non) le label `mode_write` posé sur l'issue — donc le mode écriture de CCL. Défaut lecture si absent/non reconnu. Voir §5 pour le comportement de chaque mode. |
 | `PRIORITE` | `haute` ou `critique` | Retry infini (au lieu de 3 max) |
 | `TIMEOUT` | ex. `600s` | Surcharge le timeout par défaut (300s) |
 | `MODELE` | ex. `claude-opus-4-5` | Force un modèle CCL spécifique pour cette issue |
# ── Zone modifiée : ligne 336 (8 ligne(s)) dans l'ancienne version → ligne 347 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -336,8 +347,10 @@ Format dans le corps :
 > (`bridge_agent`, `alchess`, `ff_galerie`).
 
 > ℹ️ Le champ `| LABELS | … |` (issue #161) n'est **pas** lu par le watcher :
-> il est consommé par `new_issue.py` au moment de la création pour ajouter des
-> labels supplémentaires (ex. `for-windows`) à ceux posés d'office. Voir §3.
+> il est consommé par `new_issue.py` (§20) ou par le watcher spool
+> `issues_inbox/` (§3) au moment de la création pour ajouter des labels
+> supplémentaires (ex. `for-windows`) à ceux posés d'office. Détail complet
+> au §20.
 
 ---
 
# ── Zone modifiée : ligne 445 (11 ligne(s)) dans l'ancienne version → ligne 458 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -445,11 +458,11 @@ méthode par défaut recommandée.
     tunnel.py         — tunnel Cloudflare (mode externe)
     vues.py           — routes Flask et rendu des pages
     etat.py           — état partagé de l'application
-    issues_inbox.py   — état de l'onglet « Résultats inbox » (§20, issue #483)
+    issues_inbox.py   — état de l'onglet « Résultats inbox » (§3, issue #483)
   templates/          — gabarits HTML (Jinja2)
   static/             — CSS, JS, assets statiques
-  issues_inbox/       — gitignoré : dépôt de fichiers .txt d'issues à créer (§20)
-    rejected/         — issues malformées, à corriger manuellement (§20)
+  issues_inbox/       — gitignoré : dépôt de fichiers .txt d'issues à créer (§3)
+    rejected/         — issues malformées, à corriger manuellement (§3)
   consignes/          — consignes injectées dans le prompt CCL par watcher.py (§12.1)
     globales.md       — NON-optionnel : rappels de sécurité, TOUTE issue
     type_chef.md      — optionnel : consignes du TYPE « chef »
# ── Zone modifiée : ligne 512 (10 ligne(s)) dans l'ancienne version → ligne 525 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -512,10 +525,12 @@ la même opération, en plus du point ci-dessus :
   (identifiants Python, commentaires, clés de config). Anglais conservé pour
   les contrats existants (noms de labels GitHub, drapeaux CLI, mots-clés Python).
 - **Issues** : produire titre + corps avec `#Titre:` en première ligne du corps.
-  Alain colle le tout dans le champ Corps de new_issue.py — un seul copier-coller.
-  Le corps est toujours présenté dans **un seul bloc de code**, qu'il s'agisse
-  d'une issue unique ou d'un lot de plusieurs issues (issue #153, étendue par
-  #443), afin qu'Alain puisse utiliser le bouton copier du bloc.
+  Méthode principale : dépôt d'un fichier dans `issues_inbox/` (§3). En
+  backup, Alain colle le tout dans le champ Corps de new_issue.py (§20) — un
+  seul copier-coller. Le corps est toujours présenté dans **un seul bloc de
+  code**, qu'il s'agisse d'une issue unique ou d'un lot de plusieurs issues
+  (issue #153, étendue par #443), afin qu'Alain puisse utiliser le bouton
+  copier du bloc.
 - **Mode par défaut** : lecture seule. N'armer `mode_write` que si la tâche
   demande explicitement une modification de fichier.
 - **Scripts PowerShell (`.ps1`) : BOM UTF-8 obligatoire dès la création.**
# ── Zone modifiée : ligne 589 (7 ligne(s)) dans l'ancienne version → ligne 604 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -589,7 +604,8 @@ les petits changements (une ligne CSS, un label, une couleur).
 **Workflow :**
 1. Alain décrit l'idée à CC dans Claude Chat
 2. CC génère l'issue (titre + corps avec `| PROJET | <nom> |`)
-3. Alain colle dans new_issue.py et envoie
+3. CC dépose le fichier dans `issues_inbox/` (§3, méthode principale) — ou,
+   en backup, Alain colle dans new_issue.py (§20) et envoie
 4. CCL exécute, committe, ne pousse pas
 5. Alain vérifie (`git show`) et pousse
 
# ── Zone modifiée : ligne 637 (9 ligne(s)) dans l'ancienne version → ligne 653 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -637,9 +653,10 @@ curl -sL "https://raw.githubusercontent.com/AlainDelree/Bridge_Agent/master/cons
 ```
 
 **Couverture universelle (issue #211).** Une issue peut naître de trois chemins :
-(1) le formulaire web (`new_issue.py`), (2) un CCL « chef » via `gh issue create`
-en ligne de commande (§14, pattern Chef → Ouvrier), (3) une création manuelle
-directe sur GitHub (§3). En #209 les consignes étaient écrites dans le **corps**
+(1) le formulaire web (`new_issue.py`) ou le watcher spool `issues_inbox/`
+(§3/§20), (2) un CCL « chef » via `gh issue create` en ligne de commande
+(§14, pattern Chef → Ouvrier), (3) une création manuelle directe sur GitHub
+(§20, pour le format du corps). En #209 les consignes étaient écrites dans le **corps**
 de l'issue par `app/issues.py`, ce qui ne couvrait QUE le chemin 1 — les issues
 ouvrières créées par un chef (chemin 2), justement de vraies tâches `mode_write`,
 échappaient à l'injection. Depuis #211, l'injection se fait dans le **prompt CCL**
# ── Zone modifiée : ligne 1156 (7 ligne(s)) dans l'ancienne version → ligne 1173 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1156,7 +1173,7 @@ create`, puis surveille sa fermeture avant de livrer sa réponse.
 - **Critère de décision** : le chef se justifie quand la tâche comporte du
   travail réel côté Linux (avant et/ou après) dans la même unité de travail.
   Si la TOTALITÉ de la tâche s'exécute sous Windows, créer directement
-  l'issue avec `| LABELS | for-windows |` (§3) — pas de chef.
+  l'issue avec `| LABELS | for-windows |` (§20) — pas de chef.
 - **Contre-exemple explicite** : un chef qui se contente de créer un ouvrier
   puis d'attendre sa fermeture, sans orchestration réelle, est du surcoût
   pur (deux issues, deux invocations `claude`, TIMEOUT long, attente
