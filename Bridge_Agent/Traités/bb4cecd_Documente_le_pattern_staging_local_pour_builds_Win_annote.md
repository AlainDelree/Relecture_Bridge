bb4cecd

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bb4cecd
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 31 20:11:50 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Documente le pattern staging local pour builds Windows CCW (#297)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 22b2928..9d6de20 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1398 (6 ligne(s)) dans l'ancienne version → ligne 1398 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1398,6 +1398,18 @@ le propriétaire diffère de l'utilisateur courant. L'exception est à ajouter
 en étape 0 de chaque première issue sur un nouveau sous-dossier. Les issues
 suivantes la trouvent déjà en place.
 
+**Note staging local (issue #297) :** un build PyInstaller/Inno Setup lancé
+directement sur `\\VBOXSVR\CCW_Share` peut produire des fichiers
+tronqués/corrompus (diagnostiqué sur Scrabble, fix #338). Contournement
+standard : le script de build copie d'abord les sources vers un répertoire
+local à la VM (`C:\Temp\<Projet>Build` ou équivalent), construit
+entièrement là, puis ne recopie vers le partage que l'artefact final.
+Conséquence obligatoire : ajouter ce chemin local au `PERIMETRE` de
+`configs\ccw.conf` (liste séparée par virgules), sans quoi CCW refuse à
+juste titre d'en sortir et bloque le build. Avant de builder un nouveau
+projet, vérifier si son script suit déjà ce schéma de staging local et,
+si oui, étendre le `PERIMETRE` en conséquence.
+
 ### 16.4 Interrompre une issue CCW coincée (issue #287)
 
 **Symptôme :** le watcher `CCW-Watcher` détecte bien l'issue à chaque cycle
# ── Zone modifiée : ligne 1892 (6 ligne(s)) dans l'ancienne version → ligne 1904 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1892,6 +1904,6 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 30 juillet 2026 — Ajoute au §16 « Agent Windows CCW » la sous-section 16.4 « Interrompre une issue CCW coincée » (issue #287) : symptôme (le watcher `CCW-Watcher` log en boucle « Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\ » sans jamais progresser), cause (fichier verrou orphelin dans `C:\CCW\Bridge_Agent\logs\verrous\`, non nettoyé après un process tué brutalement ou un redémarrage NSSM sans libération propre), procédure manuelle (`nssm restart CCW-Watcher` puis lister/supprimer le(s) fichier(s) `.lock` restant(s) via `Get-ChildItem`/`Remove-Item`), et note sur le bouton **« Interrompre »** prévu dans l'onglet CCW de `new_issue.py` pour automatiser cette procédure (voir `TACHES.md`). Précédemment — Documente au §3 « Créer une issue — la méthode normale » le comportement exact du bouton « Aperçu de la commande » de l'onglet Nouvelle issue (issue #285) : il appelle la route `/apercu` (fonction `apercu()` de `app/issues.py`), qui construit à partir des champs actuellement remplis dans le formulaire la commande `gh issue create` exacte qui serait exécutée, suivie en commentaire du corps complet qui serait envoyé, renvoyée en JSON ; `afficherApercu()` (`static/js/app.js`) affiche ce texte tel quel dans la zone `zone-apercu` sous le formulaire — un aperçu pur, aucune issue n'est créée. Précédemment — Ajoute au §11 « Conventions de code » le paragraphe « Niveau de détail des issues » (issue #281) : Claude Chat décrit le problème, la cause et l'intention du fix, sans rédiger le code complet (blocs Avant/Après, implémentations entières) — CCL lit les fichiers source et fait l'implémentation lui-même ; exception tolérée pour un snippet de 1-2 lignes si la syntaxe est non-triviale ou l'intention ambiguë sans exemple.*
+*Dernière mise à jour : 31 juillet 2026 — Ajoute au §16.3 « Procédure — builder un projet Windows » une note « staging local » (issue #297) : un build PyInstaller/Inno Setup lancé directement sur `\\VBOXSVR\CCW_Share` peut produire des fichiers tronqués/corrompus (diagnostiqué sur Scrabble, fix #338) ; contournement standard — le script de build copie les sources vers un répertoire local à la VM (`C:\Temp\<Projet>Build`), construit entièrement là, puis ne recopie que l'artefact final vers le partage ; conséquence obligatoire — ajouter ce chemin local au `PERIMETRE` de `configs\ccw.conf`, sans quoi CCW bloque légitimement le build ; et rappel de vérifier ce schéma avant tout nouveau projet à builder. Précédemment — Ajoute au §16 « Agent Windows CCW » la sous-section 16.4 « Interrompre une issue CCW coincée » (issue #287) : symptôme (le watcher `CCW-Watcher` log en boucle « Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\ » sans jamais progresser), cause (fichier verrou orphelin dans `C:\CCW\Bridge_Agent\logs\verrous\`, non nettoyé après un process tué brutalement ou un redémarrage NSSM sans libération propre), procédure manuelle (`nssm restart CCW-Watcher` puis lister/supprimer le(s) fichier(s) `.lock` restant(s) via `Get-ChildItem`/`Remove-Item`), et note sur le bouton **« Interrompre »** prévu dans l'onglet CCW de `new_issue.py` pour automatiser cette procédure (voir `TACHES.md`). Précédemment — Documente au §3 « Créer une issue — la méthode normale » le comportement exact du bouton « Aperçu de la commande » de l'onglet Nouvelle issue (issue #285) : il appelle la route `/apercu` (fonction `apercu()` de `app/issues.py`), qui construit à partir des champs actuellement remplis dans le formulaire la commande `gh issue create` exacte qui serait exécutée, suivie en commentaire du corps complet qui serait envoyé, renvoyée en JSON ; `afficherApercu()` (`static/js/app.js`) affiche ce texte tel quel dans la zone `zone-apercu` sous le formulaire — un aperçu pur, aucune issue n'est créée.*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index fa38e82..63b165b 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,10 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 31 juillet 2026 — issue #297
+
+Documente au §16.3 « Procédure — builder un projet Windows » de `BRIDGE_AGENT_DOC.md` le pattern de staging local pour les builds Windows CCW (issue #297), jusqu'ici décrit uniquement dans le `CONTEXTE.md` propre au projet Scrabble et donc invisible pour toute autre instance CCL/CCW ayant le même besoin (ex. Rummikub, même stack PyInstaller + Inno Setup, prévoit ce pattern dès son premier script de build). Contexte : diagnostic du 31/07/2026 sur Scrabble — les builds PyInstaller + Inno Setup produisaient des fichiers tronqués/corrompus lorsqu'ils tournaient directement sur le partage VirtualBox `\\VBOXSVR\CCW_Share` (fix #338). Nouvelle note ajoutée juste après le paragraphe « Note safe.directory », avant la sous-section 16.4 : **contournement standard** — le script de build copie les sources vers un répertoire local à la VM (`C:\Temp\<Projet>Build` ou équivalent), construit entièrement là, puis ne recopie vers le partage que l'artefact final ; **conséquence obligatoire** — ajouter ce chemin local au `PERIMETRE` de `configs\ccw.conf` (liste séparée par virgules), sans quoi CCW refuse à juste titre d'en sortir et bloque légitimement le build ; **rappel** — avant d'ajouter un nouveau projet à builder sous Windows, vérifier si son script de build suit déjà ce schéma et, si oui, étendre le `PERIMETRE` en conséquence. Pied de page de `BRIDGE_AGENT_DOC.md` glissé (issue #297 en tête, #287 et #285 conservées comme les deux entrées les plus récentes parmi les issues modifiant cette doc, #281 sorti). Aucun fichier `.py`/`.js` modifié (documentation seule), aucune section renumérotée.
+
 ## 30 juillet 2026 — issue #287
 
 Documente au §16 « Agent Windows CCW » de `BRIDGE_AGENT_DOC.md` la procédure d'interruption d'une issue CCW coincée (issue #287), jusqu'ici purement manuelle et non écrite nulle part. Nouvelle sous-section **16.4 « Interrompre une issue CCW coincée »** insérée après la note sur `safe.directory` (fin du §16), avant le §17 : **symptôme** — le watcher `CCW-Watcher` détecte bien l'issue à chaque cycle mais log en boucle, sans jamais progresser, « Issue différée : un autre traitement détient déjà le verrou sur `\\VBOXSVR\CCW_Share\` » ; **cause** — un fichier verrou laissé dans `C:\CCW\Bridge_Agent\logs\verrous\` n'a pas été nettoyé (process tué brutalement, ou redémarrage NSSM du service sans libération propre du verrou en cours), le watcher refusant alors de retraiter l'issue tant que ce fichier existe, même après redémarrage ; **procédure manuelle** en deux étapes — `nssm restart CCW-Watcher` (nécessaire mais pas suffisant seul), puis lister et supprimer le(s) fichier(s) `.lock` restant(s) dans `C:\CCW\Bridge_Agent\logs\verrous\` via `Get-ChildItem ... -Filter "*.lock"` et `Remove-Item` ; **note** — un bouton « Interrompre » dans l'onglet CCW de `new_issue.py` est prévu pour automatiser cette procédure à distance depuis Linux (voir `TACHES.md`, backlog ajouté par l'issue précédente be4cae0). Pied de page de `BRIDGE_AGENT_DOC.md` glissé (issue #287 en tête, #285 et #281 conservées comme les deux entrées les plus récentes parmi les issues modifiant cette doc, #279 sorti). Aucun fichier `.py`/`.js` modifié (documentation seule), aucune section renumérotée.
