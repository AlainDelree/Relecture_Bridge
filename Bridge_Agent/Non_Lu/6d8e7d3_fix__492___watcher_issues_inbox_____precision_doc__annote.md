6d8e7d3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6d8e7d3
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 27 18:00:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #492 : watcher_issues_inbox — precision doc notif_pc non synchronise avec localStorage

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index dea311b..af0bf85 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 2330 (6 ligne(s)) dans l'ancienne version → ligne 2330 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2330,6 +2330,15 @@ créée via `issues_inbox/` ne déclenchait aucun bip à sa clôture
 (`notifications.bip()`, cf. `watcher.py`), contrairement à celles créées via
 le formulaire.
 
+Ce défaut (issue #492) reproduit le comportement du tout premier usage du
+formulaire web, pas un état courant : côté formulaire, le label de
+notification coché reflète en réalité `localStorage` (clé
+`bridge_notif_pc`, issue #93), mémorisé côté navigateur d'Alain — un état
+que le watcher spool ne peut pas lire (pas de serveur web ni de session
+navigateur impliqués). `construire_labels()` ne cherche donc jamais à
+synchroniser dynamiquement ce choix avec le formulaire ; seul le champ
+`LABELS` explicite du fichier permet de s'écarter du défaut `notif_pc`.
+
 Le fichier est reparsé avec les mêmes regex que `static/js/app.js` (détection
 de champ d'en-tête à la frappe côté formulaire web), pour ne jamais diverger
 du format déjà produit par Claude Chat.
