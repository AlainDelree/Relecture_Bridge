5c2dfd1

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5c2dfd1
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 17:57:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #330 : documentation du champ d'en-tête MODE (auto-détecté depuis #326)
    
    §3 : MODE ajouté à la liste des champs d'en-tête reconnus, avec un
    paragraphe décrivant la détection (detecterModeDansCorps), la reconnaissance
    tolérante et le défaut lecture. §6 : ligne MODE dans le tableau des champs
    spéciaux. Ligne ~172 : précision mono-issue (auto-détecté) vs lot (commun).
    Pied de page + CHANGELOG.md mis à jour selon §10. mode_scratch/lecture
    active volontairement non documentés à ces deux endroits (hors périmètre).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 085ceba..ead755f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 137 (9 ligne(s)) dans l'ancienne version → ligne 137 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -137,9 +137,25 @@ Description précise. Indiquer explicitement si LECTURE SEULE.
 Ce que CCL doit produire ou confirmer.
 ```
 
-**Champs d'en-tête optionnels reconnus (`PROJET`, `TIMEOUT`, `MODELE`, `LABELS`) :**
-au même titre que `PROJET`/`TIMEOUT`/`MODELE`, `new_issue.py` reconnaît un champ
-`| LABELS | … |` dans l'en-tête du corps collé. Sa valeur est une liste de
+**Champs d'en-tête optionnels reconnus (`PROJET`, `TIMEOUT`, `MODELE`, `MODE`,
+`LABELS`) :**
+
+`| MODE | … |` (issue #326) est détecté par `new_issue.py`
+(`detecterModeDansCorps`) exactement comme `TIMEOUT`/`PROJET`/`MODELE` :
+la valeur reconnue pré-sélectionne le radio Mode du formulaire, puis la
+ligne est retirée du corps collé (le tableau d'en-tête final est reconstruit
+depuis le formulaire, pas depuis ce que Claude Chat a tapé). Seules deux
+valeurs sont fonctionnelles à ce jour : `| MODE | lecture |` et
+`| MODE | écriture |` (voir §5 pour le détail des modes). La reconnaissance
+est **tolérante** — insensible à la casse et aux accents, plusieurs libellés
+acceptés par valeur (ex. « écriture »/« ecriture »/« write » ;
+« lecture »/« lecture seule »/« read ») — et le **défaut est LECTURE** si le
+champ `MODE` est absent du corps ou si sa valeur n'est reconnue par aucun
+synonyme : une issue doit toujours déclarer explicitement l'écriture pour
+l'obtenir, jamais par omission.
+
+Au même titre que `PROJET`/`TIMEOUT`/`MODELE`, `new_issue.py` reconnaît aussi
+un champ `| LABELS | … |` dans l'en-tête du corps collé. Sa valeur est une liste de
 labels séparés par des virgules (les espaces superflus autour de chacun sont
 ignorés) qui **s'ajoutent** aux labels standards posés automatiquement (`bridge`,
 `for-linux`, `mode_write` selon le MODE, notifications) — ils ne les remplacent
# ── Zone modifiée : ligne 169 (8 ligne(s)) dans l'ancienne version → ligne 185 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -169,8 +185,12 @@ automatiquement le **mode lot** : le bouton d'envoi devient
 `#Titre:` suivant et est traité comme une issue indépendante, avec ses propres
 champs d'en-tête optionnels (`PROJET`, `TIMEOUT`, `MODELE`, `LABELS`) — à défaut,
 les valeurs du formulaire (projet sélectionné, timeout, modèle) s'appliquent en
-repli (le champ `LABELS`, lui, est propre à chaque bloc : sans fallback). Le `MODE` (lecture/écriture) et les notifications sont communs à tout le
-lot. Les issues partent **en séquence** (une à la fois, jamais en parallèle),
+repli (le champ `LABELS`, lui, est propre à chaque bloc : sans fallback). Le
+`MODE` (lecture/écriture) et les notifications sont communs à tout le lot :
+contrairement au mono-issue (ci-dessus), où `MODE` est auto-détecté par bloc
+depuis l'en-tête, en mode lot un éventuel `| MODE | … |` dans un bloc est
+ignoré — seul le radio du formulaire, choisi une fois pour tout le lot,
+décide. Les issues partent **en séquence** (une à la fois, jamais en parallèle),
 **sans validation intermédiaire** (aucune modale « issues en attente » ni
 d'incohérence projet) : un bloc dont le `PROJET` diffère du projet sélectionné
 part quand même sur *son* `PROJET` et c'est simplement signalé ; un bloc en
# ── Zone modifiée : ligne 282 (6 ligne(s)) dans l'ancienne version → ligne 302 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -282,6 +302,7 @@ Le watcher lit ces champs dans le tableau markdown de l'en-tête :
 
 | Champ | Valeur | Effet |
 |-------|--------|-------|
+| `MODE` | `lecture` ou `écriture` | Auto-détecté par `new_issue.py` (§3, issue #326) pour pré-sélectionner le radio Mode du formulaire ; c'est ce radio, pas la valeur du champ, qui arme (ou non) le label `mode_write` posé sur l'issue — donc le mode écriture de CCL. Défaut lecture si absent/non reconnu. Voir §5 pour le comportement de chaque mode. |
 | `PRIORITE` | `haute` ou `critique` | Retry infini (au lieu de 3 max) |
 | `TIMEOUT` | ex. `600s` | Surcharge le timeout par défaut (300s) |
 | `MODELE` | ex. `claude-opus-4-5` | Force un modèle CCL spécifique pour cette issue |
# ── Zone modifiée : ligne 1955 (6 ligne(s)) dans l'ancienne version → ligne 1976 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1955,6 +1976,6 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 2 août 2026 — §4 « Labels disponibles » et §5, renommé « Modes lecture seule / lecture active / écriture » : implémente la « lecture active » (label `mode_scratch`) préparée côté formulaire/en-tête par #326 mais jusqu'ici ignorée par le watcher (issue #327). Le booléen `autoriser_ecriture` est remplacé par un MODE à trois valeurs (`lecture`/`lecture_active`/`ecriture`), déduit des labels par `watcher.py::_deduire_mode` et lu par les cinq points de décision (flag `--dangerously-skip-permissions`, bloc de garde-fou du prompt, backup, garde-fou `configs/*.conf`, étiquette de calibration TIMEOUT). La lecture active écrit UNIQUEMENT dans `/tmp/bridge_scratch_<projet>/` (créé avant CCL, nettoyé après, quel que soit le résultat) — défense en profondeur niveau 1 (bloc de prompt dédié) + niveau 2 (empreinte de l'état git du répertoire de travail avant/après, restauration + échec `needs-human` si une écriture est détectée hors scratch, même schéma que le garde-fou `configs/*.conf` #318). Le livrable reste un rapport, comme en lecture seule. §12 « Règles d'usage » précise que l'interdiction d'écriture sur `configs/*.conf` (#318) vaut aussi en lecture active. Précédemment — §12 « Règles d'usage » : le paragraphe « Exception » sur `configs/*.conf` précise désormais que cette exception (modification directe, hors passage par CC) vaut uniquement pour Alain (à la main ou via l'onglet Configuration de `new_issue.py`), jamais pour CCL/CCW — même en mode_write, même si l'issue le demande explicitement en toutes lettres (issue #318, suite au diagnostic #298 : PERIMETRE est un champ texte simple sans garde-fou contre un élargissement/rétrécissement silencieux). Renvoie vers le garde-fou technique ajouté à `watcher.py` (`_empreinte_configs`/`_restaurer_configs_modifies`) qui détecte et annule automatiquement toute modification de `configs/*.conf` survenue malgré tout en cours de traitement, sans faire échouer le reste de l'issue. Précédemment — Crée `BUILD_WINDOWS_CCW.md` (issue #299) et allège d'autant le §16.3 « Procédure — builder un projet Windows » : la note « staging local » (issue #297) détaillée en toutes lettres — pattern de contournement de la corruption de fichiers sur `\\VBOXSVR\CCW_Share` et checklist par projet buildé — est remplacée par un renvoi de deux lignes vers ce nouveau fichier, qui porte désormais aussi la checklist Scrabble (clone, script de build, `.spec`, TIMEOUT, taille/hash de l'installeur de référence du 31/07/2026) ; objectif — éviter que chaque nouveau projet buildé sous Windows (Rummikub en préparation) n'ajoute encore du contenu spécifique-projet dans ce fichier central.*
+*Dernière mise à jour : 2 août 2026 — §3 « Créer une issue — la méthode normale » et §6 « Champs spéciaux dans le corps de l'issue » : documente le champ d'en-tête `MODE` (issue #330), auto-détecté par `new_issue.py` (`detecterModeDansCorps`) au même titre que `TIMEOUT`/`PROJET`/`MODELE` (issue #326) — pré-sélectionne le radio Mode du formulaire puis la ligne est retirée du corps, reconnaissance tolérante (casse/accents, plusieurs libellés par valeur), défaut LECTURE si le champ est absent ou non reconnu. Seules les deux valeurs fonctionnelles `lecture`/`écriture` sont documentées à ces deux endroits ; la troisième valeur (lecture active/`mode_scratch`) reste décrite uniquement au §5 (issue #327), hors périmètre de #330. Précise aussi qu'en mono-issue `MODE` est auto-détecté depuis l'en-tête du bloc, alors qu'en mode lot il reste commun à tout le lot — choisi une fois au radio du formulaire, jamais lu bloc par bloc. Précédemment — §4 « Labels disponibles » et §5, renommé « Modes lecture seule / lecture active / écriture » : implémente la « lecture active » (label `mode_scratch`) préparée côté formulaire/en-tête par #326 mais jusqu'ici ignorée par le watcher (issue #327). Le booléen `autoriser_ecriture` est remplacé par un MODE à trois valeurs (`lecture`/`lecture_active`/`ecriture`), déduit des labels par `watcher.py::_deduire_mode` et lu par les cinq points de décision (flag `--dangerously-skip-permissions`, bloc de garde-fou du prompt, backup, garde-fou `configs/*.conf`, étiquette de calibration TIMEOUT). La lecture active écrit UNIQUEMENT dans `/tmp/bridge_scratch_<projet>/` (créé avant CCL, nettoyé après, quel que soit le résultat) — défense en profondeur niveau 1 (bloc de prompt dédié) + niveau 2 (empreinte de l'état git du répertoire de travail avant/après, restauration + échec `needs-human` si une écriture est détectée hors scratch, même schéma que le garde-fou `configs/*.conf` #318). Le livrable reste un rapport, comme en lecture seule. §12 « Règles d'usage » précise que l'interdiction d'écriture sur `configs/*.conf` (#318) vaut aussi en lecture active. Précédemment — §12 « Règles d'usage » : le paragraphe « Exception » sur `configs/*.conf` précise désormais que cette exception (modification directe, hors passage par CC) vaut uniquement pour Alain (à la main ou via l'onglet Configuration de `new_issue.py`), jamais pour CCL/CCW — même en mode_write, même si l'issue le demande explicitement en toutes lettres (issue #318, suite au diagnostic #298 : PERIMETRE est un champ texte simple sans garde-fou contre un élargissement/rétrécissement silencieux). Renvoie vers le garde-fou technique ajouté à `watcher.py` (`_empreinte_configs`/`_restaurer_configs_modifies`) qui détecte et annule automatiquement toute modification de `configs/*.conf` survenue malgré tout en cours de traitement, sans faire échouer le reste de l'issue.*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 741a0e3..b2f5594 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (35 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,35 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #330
+
+Documentation du champ d'en-tête `MODE`, jusqu'ici absent de
+`BRIDGE_AGENT_DOC.md` alors qu'il est auto-détecté depuis #326.
+
+- **§3** — ajout de `MODE` à la liste des champs d'en-tête optionnels
+  reconnus, avec un paragraphe dédié : `| MODE | … |` est détecté par
+  `new_issue.py` (`detecterModeDansCorps`) exactement comme
+  `TIMEOUT`/`PROJET`/`MODELE` — pré-sélectionne le radio Mode du
+  formulaire puis la ligne est retirée du corps collé. Reconnaissance
+  tolérante (insensible casse/accents, plusieurs libellés par valeur) et
+  défaut LECTURE si le champ est absent ou non reconnu.
+- **§6** — ajout d'une ligne `MODE` au tableau des champs spéciaux :
+  valeurs `lecture`/`écriture`, effet (arme ou non le label `mode_write`
+  via le radio du formulaire), renvoi au §5 pour le comportement des
+  modes.
+- **Ligne ~172 (§3, envoi en lot)** — précision : en mono-issue `MODE`
+  est auto-détecté depuis l'en-tête du bloc, alors qu'en mode lot il
+  reste commun à tout le lot (choisi une fois au radio du formulaire,
+  jamais lu bloc par bloc).
+- Volontairement **hors périmètre** : la troisième valeur (« lecture
+  active » / `mode_scratch`) n'est PAS ajoutée à ces deux endroits — elle
+  reste documentée uniquement au §5 (issue #327), car cette issue ne
+  documente que les deux valeurs fonctionnelles au sens de la détection
+  `new_issue.py`/formulaire.
+- Pied de page de `BRIDGE_AGENT_DOC.md` mis à jour selon la convention
+  §10 (nouvelle entrée en tête, glissement des deux précédentes ; l'entrée
+  #299 sort du pied de page — déjà disponible dans `CHANGELOG.md`).
+
 ## 2 août 2026 — issue #327
 
 Implémentation du mode « lecture active » (`mode_scratch`) côté
