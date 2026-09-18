867a3f4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 867a3f4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 21:57:59 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Documente la procédure d'interruption d'une issue CCW coincée (§16.4, issue #287)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9b7a435..22b2928 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1398 (6 ligne(s)) dans l'ancienne version → ligne 1398 (40 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1398,6 +1398,40 @@ le propriétaire diffère de l'utilisateur courant. L'exception est à ajouter
 en étape 0 de chaque première issue sur un nouveau sous-dossier. Les issues
 suivantes la trouvent déjà en place.
 
+### 16.4 Interrompre une issue CCW coincée (issue #287)
+
+**Symptôme :** le watcher `CCW-Watcher` détecte bien l'issue à chaque cycle
+mais log en boucle, sans jamais progresser :
+
+```
+Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\
+```
+
+**Cause :** un fichier verrou laissé dans
+`C:\CCW\Bridge_Agent\logs\verrous\` n'a pas été nettoyé — process tué
+brutalement, ou redémarrage NSSM du service sans libération propre du
+verrou en cours. Le watcher refuse alors de retraiter l'issue tant que ce
+fichier existe, même après redémarrage.
+
+**Procédure manuelle :**
+
+1. Redémarrer le service (ne suffit pas seul, mais nécessaire) :
+
+   ```powershell
+   nssm restart CCW-Watcher
+   ```
+
+2. Lister puis supprimer le(s) fichier(s) verrou restant(s) :
+
+   ```powershell
+   Get-ChildItem C:\CCW\Bridge_Agent\logs\verrous\ -Filter "*.lock"
+   Remove-Item C:\CCW\Bridge_Agent\logs\verrous\<fichier>.lock
+   ```
+
+**Note :** un bouton **« Interrompre »** dans l'onglet CCW de `new_issue.py`
+est prévu pour automatiser cette procédure à distance depuis Linux (voir
+`TACHES.md`).
+
 ---
 
 ## 17. Notifications centralisées — détection serveur des transitions (issue #187)
# ── Zone modifiée : ligne 1858 (6 ligne(s)) dans l'ancienne version → ligne 1892 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1858,6 +1892,6 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 30 juillet 2026 — Documente au §3 « Créer une issue — la méthode normale » le comportement exact du bouton **« Aperçu de la commande »** de l'onglet Nouvelle issue (issue #285) : il appelle la route `/apercu` (fonction `apercu()` de `app/issues.py`), qui construit à partir des champs actuellement remplis dans le formulaire la commande `gh issue create` exacte qui serait exécutée (dépôt, titre, labels, `--body-file`), suivie en commentaire du corps complet qui serait envoyé, renvoyée en JSON ; `afficherApercu()` (`static/js/app.js`) affiche ce texte tel quel dans la zone `zone-apercu` sous le formulaire. C'est un aperçu pur : aucune issue n'est créée, aucune commande n'est réellement exécutée. Précédemment — Ajoute au §11 « Conventions de code » le paragraphe « Niveau de détail des issues » (issue #281) : Claude Chat décrit le problème, la cause et l'intention du fix, sans rédiger le code complet (blocs Avant/Après, implémentations entières) — CCL lit les fichiers source et fait l'implémentation lui-même ; exception tolérée pour un snippet de 1-2 lignes si la syntaxe est non-triviale ou l'intention ambiguë sans exemple. Précédemment — Documente dans §13 le diagnostic du symptôme « Erreur inconnue » observé la nuit du 29/07/2026 (issue #279) : plusieurs issues échouaient en ~1,2 s, 3 tentatives et passe diagnostique comprises, un message générique masquant totalement la cause réelle. Nouveau bloc « Diagnostic — CCL ne démarre pas » en fin de §13 : symptôme (échec quasi immédiat sur toutes les issues → cause systémique, pas liée à une tâche précise) ; première vérification (`claude -p "test" 2>&1` — une réponse « Not logged in » signe un token de session CCL expiré) ; résolution (`claude` en interactif puis `/login`) ; autres causes possibles (réseau/DNS indisponible, installation `claude` corrompue) ; et le critère qui les distingue — un token expiré échoue en moins de 2 s, un problème réseau échoue proche du TIMEOUT configuré.*
+*Dernière mise à jour : 30 juillet 2026 — Ajoute au §16 « Agent Windows CCW » la sous-section 16.4 « Interrompre une issue CCW coincée » (issue #287) : symptôme (le watcher `CCW-Watcher` log en boucle « Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\ » sans jamais progresser), cause (fichier verrou orphelin dans `C:\CCW\Bridge_Agent\logs\verrous\`, non nettoyé après un process tué brutalement ou un redémarrage NSSM sans libération propre), procédure manuelle (`nssm restart CCW-Watcher` puis lister/supprimer le(s) fichier(s) `.lock` restant(s) via `Get-ChildItem`/`Remove-Item`), et note sur le bouton **« Interrompre »** prévu dans l'onglet CCW de `new_issue.py` pour automatiser cette procédure (voir `TACHES.md`). Précédemment — Documente au §3 « Créer une issue — la méthode normale » le comportement exact du bouton « Aperçu de la commande » de l'onglet Nouvelle issue (issue #285) : il appelle la route `/apercu` (fonction `apercu()` de `app/issues.py`), qui construit à partir des champs actuellement remplis dans le formulaire la commande `gh issue create` exacte qui serait exécutée, suivie en commentaire du corps complet qui serait envoyé, renvoyée en JSON ; `afficherApercu()` (`static/js/app.js`) affiche ce texte tel quel dans la zone `zone-apercu` sous le formulaire — un aperçu pur, aucune issue n'est créée. Précédemment — Ajoute au §11 « Conventions de code » le paragraphe « Niveau de détail des issues » (issue #281) : Claude Chat décrit le problème, la cause et l'intention du fix, sans rédiger le code complet (blocs Avant/Après, implémentations entières) — CCL lit les fichiers source et fait l'implémentation lui-même ; exception tolérée pour un snippet de 1-2 lignes si la syntaxe est non-triviale ou l'intention ambiguë sans exemple.*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index acc3cee..fa38e82 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,10 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 30 juillet 2026 — issue #287
+
+Documente au §16 « Agent Windows CCW » de `BRIDGE_AGENT_DOC.md` la procédure d'interruption d'une issue CCW coincée (issue #287), jusqu'ici purement manuelle et non écrite nulle part. Nouvelle sous-section **16.4 « Interrompre une issue CCW coincée »** insérée après la note sur `safe.directory` (fin du §16), avant le §17 : **symptôme** — le watcher `CCW-Watcher` détecte bien l'issue à chaque cycle mais log en boucle, sans jamais progresser, « Issue différée : un autre traitement détient déjà le verrou sur `\\VBOXSVR\CCW_Share\` » ; **cause** — un fichier verrou laissé dans `C:\CCW\Bridge_Agent\logs\verrous\` n'a pas été nettoyé (process tué brutalement, ou redémarrage NSSM du service sans libération propre du verrou en cours), le watcher refusant alors de retraiter l'issue tant que ce fichier existe, même après redémarrage ; **procédure manuelle** en deux étapes — `nssm restart CCW-Watcher` (nécessaire mais pas suffisant seul), puis lister et supprimer le(s) fichier(s) `.lock` restant(s) dans `C:\CCW\Bridge_Agent\logs\verrous\` via `Get-ChildItem ... -Filter "*.lock"` et `Remove-Item` ; **note** — un bouton « Interrompre » dans l'onglet CCW de `new_issue.py` est prévu pour automatiser cette procédure à distance depuis Linux (voir `TACHES.md`, backlog ajouté par l'issue précédente be4cae0). Pied de page de `BRIDGE_AGENT_DOC.md` glissé (issue #287 en tête, #285 et #281 conservées comme les deux entrées les plus récentes parmi les issues modifiant cette doc, #279 sorti). Aucun fichier `.py`/`.js` modifié (documentation seule), aucune section renumérotée.
+
 ## 30 juillet 2026 — issue #285
 
 Documente au §3 « Créer une issue — la méthode normale » de `BRIDGE_AGENT_DOC.md` le comportement exact du bouton **« Aperçu de la commande »** de l'onglet Nouvelle issue (issue #285), jusqu'ici non décrit malgré sa présence de longue date dans le formulaire. Nouveau paragraphe inséré juste après la description du lancement (`new_issue.py`/`lancer_new_issue.sh`) et avant le « Format du corps pour copier-coller » : le bouton appelle la route `/apercu` (fonction `apercu()` de `app/issues.py`), qui construit à partir des champs actuellement remplis dans le formulaire la commande `gh issue create` exacte qui serait exécutée (dépôt, titre, labels, `--body-file`), suivie en commentaire du corps complet qui serait envoyé, renvoyée en JSON. `afficherApercu()` (`static/js/app.js`) affiche ce texte tel quel dans la zone `zone-apercu` sous le formulaire. Point clé : c'est un aperçu pur — aucune issue n'est créée, aucune commande n'est réellement exécutée, rien n'est modifié tant que le bouton d'envoi n'est pas cliqué séparément. Pied de page de `BRIDGE_AGENT_DOC.md` glissé (issue #285 en tête, #281 et #279 conservées comme les deux entrées les plus récentes parmi les issues modifiant cette doc, #268 sorti). Aucun fichier `.py`/`.js` modifié (documentation seule), aucune section renumérotée.
