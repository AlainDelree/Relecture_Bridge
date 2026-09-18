fd78d1f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit fd78d1f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 1 13:20:34 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Cree BUILD_WINDOWS_CCW.md, allege §16.3 de BRIDGE_AGENT_DOC.md (#299)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9d6de20..fd99322 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1398 (17 ligne(s)) dans l'ancienne version → ligne 1398 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1398,17 +1398,9 @@ le propriétaire diffère de l'utilisateur courant. L'exception est à ajouter
 en étape 0 de chaque première issue sur un nouveau sous-dossier. Les issues
 suivantes la trouvent déjà en place.
 
-**Note staging local (issue #297) :** un build PyInstaller/Inno Setup lancé
-directement sur `\\VBOXSVR\CCW_Share` peut produire des fichiers
-tronqués/corrompus (diagnostiqué sur Scrabble, fix #338). Contournement
-standard : le script de build copie d'abord les sources vers un répertoire
-local à la VM (`C:\Temp\<Projet>Build` ou équivalent), construit
-entièrement là, puis ne recopie vers le partage que l'artefact final.
-Conséquence obligatoire : ajouter ce chemin local au `PERIMETRE` de
-`configs\ccw.conf` (liste séparée par virgules), sans quoi CCW refuse à
-juste titre d'en sortir et bloque le build. Avant de builder un nouveau
-projet, vérifier si son script suit déjà ce schéma de staging local et,
-si oui, étendre le `PERIMETRE` en conséquence.
+**Note staging local (issue #297) :** pattern général de contournement de
+la corruption de fichiers sur `\\VBOXSVR\CCW_Share`, et checklist par
+projet buildé (dont Scrabble) — voir `BUILD_WINDOWS_CCW.md`.
 
 ### 16.4 Interrompre une issue CCW coincée (issue #287)
 
# ── Zone modifiée : ligne 1904 (6 ligne(s)) dans l'ancienne version → ligne 1896 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1904,6 +1896,6 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 31 juillet 2026 — Ajoute au §16.3 « Procédure — builder un projet Windows » une note « staging local » (issue #297) : un build PyInstaller/Inno Setup lancé directement sur `\\VBOXSVR\CCW_Share` peut produire des fichiers tronqués/corrompus (diagnostiqué sur Scrabble, fix #338) ; contournement standard — le script de build copie les sources vers un répertoire local à la VM (`C:\Temp\<Projet>Build`), construit entièrement là, puis ne recopie que l'artefact final vers le partage ; conséquence obligatoire — ajouter ce chemin local au `PERIMETRE` de `configs\ccw.conf`, sans quoi CCW bloque légitimement le build ; et rappel de vérifier ce schéma avant tout nouveau projet à builder. Précédemment — Ajoute au §16 « Agent Windows CCW » la sous-section 16.4 « Interrompre une issue CCW coincée » (issue #287) : symptôme (le watcher `CCW-Watcher` log en boucle « Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\ » sans jamais progresser), cause (fichier verrou orphelin dans `C:\CCW\Bridge_Agent\logs\verrous\`, non nettoyé après un process tué brutalement ou un redémarrage NSSM sans libération propre), procédure manuelle (`nssm restart CCW-Watcher` puis lister/supprimer le(s) fichier(s) `.lock` restant(s) via `Get-ChildItem`/`Remove-Item`), et note sur le bouton **« Interrompre »** prévu dans l'onglet CCW de `new_issue.py` pour automatiser cette procédure (voir `TACHES.md`). Précédemment — Documente au §3 « Créer une issue — la méthode normale » le comportement exact du bouton « Aperçu de la commande » de l'onglet Nouvelle issue (issue #285) : il appelle la route `/apercu` (fonction `apercu()` de `app/issues.py`), qui construit à partir des champs actuellement remplis dans le formulaire la commande `gh issue create` exacte qui serait exécutée, suivie en commentaire du corps complet qui serait envoyé, renvoyée en JSON ; `afficherApercu()` (`static/js/app.js`) affiche ce texte tel quel dans la zone `zone-apercu` sous le formulaire — un aperçu pur, aucune issue n'est créée.*
+*Dernière mise à jour : 1er août 2026 — Crée `BUILD_WINDOWS_CCW.md` (issue #299) et allège d'autant le §16.3 « Procédure — builder un projet Windows » : la note « staging local » (issue #297) détaillée en toutes lettres — pattern de contournement de la corruption de fichiers sur `\\VBOXSVR\CCW_Share` et checklist par projet buildé — est remplacée par un renvoi de deux lignes vers ce nouveau fichier, qui porte désormais aussi la checklist Scrabble (clone, script de build, `.spec`, TIMEOUT, taille/hash de l'installeur de référence du 31/07/2026) ; objectif — éviter que chaque nouveau projet buildé sous Windows (Rummikub en préparation) n'ajoute encore du contenu spécifique-projet dans ce fichier central. Précédemment — Ajoute au §16 « Agent Windows CCW » la sous-section 16.4 « Interrompre une issue CCW coincée » (issue #287) : symptôme (le watcher `CCW-Watcher` log en boucle « Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\ » sans jamais progresser), cause (fichier verrou orphelin dans `C:\CCW\Bridge_Agent\logs\verrous\`, non nettoyé après un process tué brutalement ou un redémarrage NSSM sans libération propre), procédure manuelle (`nssm restart CCW-Watcher` puis lister/supprimer le(s) fichier(s) `.lock` restant(s) via `Get-ChildItem`/`Remove-Item`), et note sur le bouton **« Interrompre »** prévu dans l'onglet CCW de `new_issue.py` pour automatiser cette procédure (voir `TACHES.md`). Précédemment — Documente au §16.3 « Procédure — builder un projet Windows » le pattern de staging local pour les builds Windows CCW (issue #297) : diagnostic du 31/07/2026 sur Scrabble — les builds PyInstaller + Inno Setup produisaient des fichiers tronqués/corrompus lorsqu'ils tournaient directement sur le partage VirtualBox `\\VBOXSVR\CCW_Share` (fix #338) ; contournement standard — le script de build copie les sources vers un répertoire local à la VM (`C:\Temp\<Projet>Build`), construit entièrement là, puis ne recopie que l'artefact final vers le partage ; conséquence obligatoire — ajouter ce chemin local au `PERIMETRE` de `configs\ccw.conf`, sans quoi CCW bloque légitimement le build (contenu depuis remplacé par un renvoi, voir ci-dessus).*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/BUILD_WINDOWS_CCW.md b/BUILD_WINDOWS_CCW.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..9d2d1ba
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/BUILD_WINDOWS_CCW.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (62 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,62 @@
+# BUILD_WINDOWS_CCW — builds Windows par projet (CCW)
+
+Document de référence pour tout ce qui est **spécifique à un projet donné**
+dans les builds Windows délégués à CCW (PyInstaller/Inno Setup). Le pattern
+général et la procédure d'envoi d'une issue `for-windows` restent dans
+`BRIDGE_AGENT_DOC.md` (§16.3) ; ce fichier évite d'y accumuler, projet après
+projet, du contenu qui n'intéresse que le projet en question.
+
+Convention d'ajout : une nouvelle checklist par projet buildé, à la suite,
+la plus récente en premier. Ne pas renuméroter les entrées existantes.
+
+---
+
+## Pattern général — staging local (issue #297)
+
+Un build PyInstaller/Inno Setup lancé **directement** sur
+`\\VBOXSVR\CCW_Share` peut produire des fichiers tronqués/corrompus
+(diagnostiqué sur Scrabble, fix #338).
+
+**Contournement standard :** le script de build copie d'abord les sources
+vers un répertoire local à la VM (`C:\Temp\<Projet>Build` ou équivalent),
+construit **entièrement** là, puis ne recopie vers le partage que
+l'artefact final (installeur ou `dist\`).
+
+**Conséquence obligatoire :** ajouter ce chemin local au `PERIMETRE` de
+`configs\ccw.conf` (liste séparée par virgules), sans quoi CCW refuse à
+juste titre d'en sortir et bloque légitimement le build.
+
+**Rappel :** avant de builder un nouveau projet, vérifier si son script de
+build suit déjà ce schéma de staging local et, si oui, étendre le
+`PERIMETRE` en conséquence.
+
+---
+
+## Checklist par projet
+
+À remplir pour chaque projet buildé sous Windows :
+
+- **Chemin du clone CCW** : `Z:\CCW\<projet>`
+- **Script de build** : nom et emplacement (ex. `build\rebuild_<projet>.bat`)
+- **`.spec`** : liste explicite des `datas`, ou `collect_tree` en bloc —
+  ⚠️ mise en garde si en bloc : un `collect_tree` mal ciblé peut embarquer
+  des ressources volumineuses et non nécessaires dans l'artefact final
+  (cf. incident dump wiktionnaire 8,2 Go sur Scrabble, 31/07/2026)
+- **TIMEOUT de référence observé**
+- **Taille de référence de l'artefact final** (installeur ou `dist\`),
+  idéalement avec un hash pour détecter une régression silencieuse
+
+---
+
+## Scrabble
+
+- **Chemin du clone CCW** : `Z:\CCW\scrabble`
+- **Script de build** : `build\rebuild_scrabble.bat` (7 étapes, fix #338)
+- **`.spec`** : `scrabble.spec` corrigé en liste explicite des `datas`
+  (issue ouverte suite au diagnostic du dump wiktionnaire embarqué en bloc
+  par `collect_tree`)
+- **TIMEOUT de référence observé** : 1200s
+- **Taille de référence de l'artefact final** : installeur, 26 546 846
+  octets — SHA256
+  `d52e101f8758a1b107011adf0bc1a04102bce48d3283248650019ba101ef3254`
+  (référence du 31 juillet 2026)
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 63b165b..b273e55 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,30 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 1er août 2026 — issue #299
+
+Crée `BUILD_WINDOWS_CCW.md` à la racine du dépôt (issue #299), dédié au
+contenu spécifique-projet des builds Windows délégués à CCW — jusqu'ici en
+voie d'accumulation dans `BRIDGE_AGENT_DOC.md` (§16.3) à chaque nouveau
+projet buildé (Scrabble déjà, Rummikub en préparation). Le fichier reprend
+le pattern général de staging local documenté par l'issue #297 (corruption
+de fichiers sur `\\VBOXSVR\CCW_Share`, contournement via
+`C:\Temp\<Projet>Build`, extension obligatoire du `PERIMETRE` dans
+`configs\ccw.conf`), ajoute une checklist type à remplir par projet
+buildé (clone CCW, script de build, `.spec` — datas explicites ou
+`collect_tree` en bloc avec mise en garde suite à l'incident dump
+wiktionnaire 8,2 Go sur Scrabble du 31/07/2026 —, TIMEOUT de référence,
+taille/hash de l'artefact final), et une première entrée déjà remplie
+pour Scrabble (`Z:\CCW\scrabble`, `build\rebuild_scrabble.bat` en 7
+étapes fix #338, `scrabble.spec` corrigé en liste explicite, TIMEOUT
+1200s, installeur de référence 26 546 846 octets, SHA256
+`d52e101f8758a1b107011adf0bc1a04102bce48d3283248650019ba101ef3254`).
+En contrepartie, la note « staging local » ajoutée au §16.3 de
+`BRIDGE_AGENT_DOC.md` par l'issue #297 est remplacée par un renvoi de
+deux lignes vers ce nouveau fichier ; pied de page de `BRIDGE_AGENT_DOC.md`
+glissé (#299 en tête, #287 conservée, #297 conservée en dernière position
+avec note du remplacement, #285 sorti).
+
 ## 31 juillet 2026 — issue #297
 
 Documente au §16.3 « Procédure — builder un projet Windows » de `BRIDGE_AGENT_DOC.md` le pattern de staging local pour les builds Windows CCW (issue #297), jusqu'ici décrit uniquement dans le `CONTEXTE.md` propre au projet Scrabble et donc invisible pour toute autre instance CCL/CCW ayant le même besoin (ex. Rummikub, même stack PyInstaller + Inno Setup, prévoit ce pattern dès son premier script de build). Contexte : diagnostic du 31/07/2026 sur Scrabble — les builds PyInstaller + Inno Setup produisaient des fichiers tronqués/corrompus lorsqu'ils tournaient directement sur le partage VirtualBox `\\VBOXSVR\CCW_Share` (fix #338). Nouvelle note ajoutée juste après le paragraphe « Note safe.directory », avant la sous-section 16.4 : **contournement standard** — le script de build copie les sources vers un répertoire local à la VM (`C:\Temp\<Projet>Build` ou équivalent), construit entièrement là, puis ne recopie vers le partage que l'artefact final ; **conséquence obligatoire** — ajouter ce chemin local au `PERIMETRE` de `configs\ccw.conf` (liste séparée par virgules), sans quoi CCW refuse à juste titre d'en sortir et bloque légitimement le build ; **rappel** — avant d'ajouter un nouveau projet à builder sous Windows, vérifier si son script de build suit déjà ce schéma et, si oui, étendre le `PERIMETRE` en conséquence. Pied de page de `BRIDGE_AGENT_DOC.md` glissé (issue #297 en tête, #287 et #285 conservées comme les deux entrées les plus récentes parmi les issues modifiant cette doc, #281 sorti). Aucun fichier `.py`/`.js` modifié (documentation seule), aucune section renumérotée.
