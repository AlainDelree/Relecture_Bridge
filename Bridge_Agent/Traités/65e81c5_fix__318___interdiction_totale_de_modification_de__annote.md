65e81c5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 65e81c5
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 12:02:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #318 : interdiction totale de modification de configs/*.conf par CCL/CCW

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c786f63..dc4aa22 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 485 (10 ligne(s)) dans l'ancienne version → ligne 485 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -485,10 +485,21 @@ les petits changements (une ligne CSS, un label, une couleur).
 4. CCL exécute, committe, ne pousse pas
 5. Alain vérifie (`git show`) et pousse
 
-**Exception :** les modifications de `configs/*.conf` (`TOPIC_NTFY`,
-`FICHIER_CONTEXTE`, etc.) peuvent se faire directement via
-l'onglet Configuration de new_issue.py — elles ne touchent
-pas au code et sont gitignorées.
+**Exception :** les modifications de `configs/*.conf` (`PERIMETRE`,
+`TOPIC_NTFY`, `FICHIER_CONTEXTE`, etc.) peuvent se faire directement via
+l'onglet Configuration de new_issue.py, ou à la main par Alain — elles
+ne touchent pas au code et sont gitignorées. **Cette exception vaut
+uniquement pour Alain** : CCL/CCW ne modifie **jamais** `configs/*.conf`
+via une issue, même en mode_write et même si l'issue le demande
+explicitement en toutes lettres (issue #318, suite au diagnostic #298 —
+ce champ texte simple n'avait aucun garde-fou contre un élargissement ou
+un rétrécissement silencieux du PÉRIMÈTRE). La règle est injectée à
+CCL/CCW via `consignes/globales.md`, et doublée d'un garde-fou technique
+dans `watcher.py` (`_empreinte_configs` / `_restaurer_configs_modifies`) :
+toute modification de `configs/*.conf` survenue malgré tout au cours
+d'un traitement mode_write est détectée (comparaison du contenu avant/
+après chaque tentative) et annulée automatiquement, avec un WARNING
+journalisé, sans faire échouer le reste du traitement de l'issue.
 
 ### 12.1 Consignes injectées — architecture à trois couches (issues #209, #211)
 
# ── Zone modifiée : ligne 1904 (6 ligne(s)) dans l'ancienne version → ligne 1915 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1904,6 +1915,6 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 1er août 2026 — Crée `BUILD_WINDOWS_CCW.md` (issue #299) et allège d'autant le §16.3 « Procédure — builder un projet Windows » : la note « staging local » (issue #297) détaillée en toutes lettres — pattern de contournement de la corruption de fichiers sur `\\VBOXSVR\CCW_Share` et checklist par projet buildé — est remplacée par un renvoi de deux lignes vers ce nouveau fichier, qui porte désormais aussi la checklist Scrabble (clone, script de build, `.spec`, TIMEOUT, taille/hash de l'installeur de référence du 31/07/2026) ; objectif — éviter que chaque nouveau projet buildé sous Windows (Rummikub en préparation) n'ajoute encore du contenu spécifique-projet dans ce fichier central. Précédemment — Ajoute au §16 « Agent Windows CCW » la sous-section 16.4 « Interrompre une issue CCW coincée » (issue #287) : symptôme (le watcher `CCW-Watcher` log en boucle « Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\ » sans jamais progresser), cause (fichier verrou orphelin dans `C:\CCW\Bridge_Agent\logs\verrous\`, non nettoyé après un process tué brutalement ou un redémarrage NSSM sans libération propre), procédure manuelle (`nssm restart CCW-Watcher` puis lister/supprimer le(s) fichier(s) `.lock` restant(s) via `Get-ChildItem`/`Remove-Item`), et note sur le bouton **« Interrompre »** prévu dans l'onglet CCW de `new_issue.py` pour automatiser cette procédure (voir `TACHES.md`). Précédemment — Documente au §16.3 « Procédure — builder un projet Windows » le pattern de staging local pour les builds Windows CCW (issue #297) : diagnostic du 31/07/2026 sur Scrabble — les builds PyInstaller + Inno Setup produisaient des fichiers tronqués/corrompus lorsqu'ils tournaient directement sur le partage VirtualBox `\\VBOXSVR\CCW_Share` (fix #338) ; contournement standard — le script de build copie les sources vers un répertoire local à la VM (`C:\Temp\<Projet>Build`), construit entièrement là, puis ne recopie que l'artefact final vers le partage ; conséquence obligatoire — ajouter ce chemin local au `PERIMETRE` de `configs\ccw.conf`, sans quoi CCW bloque légitimement le build (contenu depuis remplacé par un renvoi, voir ci-dessus).*
+*Dernière mise à jour : 2 août 2026 — §12 « Règles d'usage » : le paragraphe « Exception » sur `configs/*.conf` précise désormais que cette exception (modification directe, hors passage par CC) vaut uniquement pour Alain (à la main ou via l'onglet Configuration de `new_issue.py`), jamais pour CCL/CCW — même en mode_write, même si l'issue le demande explicitement en toutes lettres (issue #318, suite au diagnostic #298 : PERIMETRE est un champ texte simple sans garde-fou contre un élargissement/rétrécissement silencieux). Renvoie vers le garde-fou technique ajouté à `watcher.py` (`_empreinte_configs`/`_restaurer_configs_modifies`) qui détecte et annule automatiquement toute modification de `configs/*.conf` survenue malgré tout en cours de traitement, sans faire échouer le reste de l'issue. Précédemment — Crée `BUILD_WINDOWS_CCW.md` (issue #299) et allège d'autant le §16.3 « Procédure — builder un projet Windows » : la note « staging local » (issue #297) détaillée en toutes lettres — pattern de contournement de la corruption de fichiers sur `\\VBOXSVR\CCW_Share` et checklist par projet buildé — est remplacée par un renvoi de deux lignes vers ce nouveau fichier, qui porte désormais aussi la checklist Scrabble (clone, script de build, `.spec`, TIMEOUT, taille/hash de l'installeur de référence du 31/07/2026) ; objectif — éviter que chaque nouveau projet buildé sous Windows (Rummikub en préparation) n'ajoute encore du contenu spécifique-projet dans ce fichier central. Précédemment — Ajoute au §16 « Agent Windows CCW » la sous-section 16.4 « Interrompre une issue CCW coincée » (issue #287) : symptôme (le watcher `CCW-Watcher` log en boucle « Issue différée : un autre traitement détient déjà le verrou sur \\VBOXSVR\CCW_Share\ » sans jamais progresser), cause (fichier verrou orphelin dans `C:\CCW\Bridge_Agent\logs\verrous\`, non nettoyé après un process tué brutalement ou un redémarrage NSSM sans libération propre), procédure manuelle (`nssm restart CCW-Watcher` puis lister/supprimer le(s) fichier(s) `.lock` restant(s) via `Get-ChildItem`/`Remove-Item`), et note sur le bouton **« Interrompre »** prévu dans l'onglet CCW de `new_issue.py` pour automatiser cette procédure (voir `TACHES.md`).*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 5d264c3..000023a 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (41 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,41 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #318
+
+Interdiction totale de modification de `configs/*.conf` par CCL/CCW, y
+compris en mode_write (diagnostic #298, décision du 02/08/2026 : pas de
+mécanisme de détection/confirmation, interdiction pure et simple —
+seul Alain modifie ces fichiers à la main ou via l'onglet Configuration
+de `new_issue.py`).
+
+- `consignes/globales.md` : nouvelle règle explicite — CCL/CCW ne
+  modifie JAMAIS `configs/*.conf`, même si une issue le demande en
+  toutes lettres ; en cas de demande de ce type, refuser cette partie
+  de la tâche, l'expliquer dans le rapport de clôture, ne rien
+  committer sur ce point.
+- `watcher.py` : garde-fou technique en deux temps.
+  - `_detecter_demande_modif_configs` : repérage best-effort (regex sur
+    un chemin `configs/*.conf` dans le corps) juste avant le lancement
+    de claude en mode_write — purement informatif (WARNING journalisé),
+    ne bloque rien.
+  - `_empreinte_configs` / `_restaurer_configs_modifies` : instantané
+    intégral (contenu brut) de `configs/*.conf` pris une seule fois
+    avant la première tentative de `traiter_issue`, comparé après
+    CHAQUE tentative (succès ou échec). Toute modification, création ou
+    suppression détectée est annulée automatiquement (restauration du
+    contenu d'origine, ou suppression d'un fichier apparu), avec un
+    WARNING explicite par fichier concerné — sans jamais faire échouer
+    le reste du traitement de l'issue (best-effort, aucune exception
+    propagée). `configs/` est commun à tous les projets (partagé par ce
+    `watcher.py`), donc l'ensemble du dossier est protégé, pas
+    seulement le `.conf` du projet en cours de traitement.
+- `BRIDGE_AGENT_DOC.md` (§12) : le paragraphe « Exception » sur
+  `configs/*.conf` précise désormais que cette exception vaut
+  uniquement pour Alain (à la main ou via l'onglet Configuration),
+  jamais pour CCL/CCW, même en mode_write, et renvoie vers le
+  garde-fou technique de `watcher.py`.
+
 ## 2 août 2026 — issue #315
 
 `BUILD_WINDOWS_CCW.md` : ajout de la checklist Rummikub (build validé),
# (diff du fichier suivant)
diff --git a/consignes/globales.md b/consignes/globales.md
# (index — ignorable)
index cd0482a..8de6c98 100644
# (avant — fichier suivant)
--- a/consignes/globales.md
# (après — fichier suivant)
+++ b/consignes/globales.md
# ── Zone modifiée : ligne 50 (3 ligne(s)) dans l'ancienne version → ligne 50 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -50,3 +50,14 @@
   ou de modification du pipeline — il documente le pattern de staging
   local, l'extension du PÉRIMÈTRE associée, et une checklist par projet
   déjà buildé.
+- **Interdiction absolue de modifier `configs/*.conf` :** CCL/CCW ne
+  modifie JAMAIS un fichier `configs/*.conf` (PERIMETRE, TOPIC_NTFY,
+  FICHIER_CONTEXTE, etc.), même si une issue le demande explicitement en
+  toutes lettres. Seul Alain modifie ces fichiers, à la main ou via
+  l'onglet Configuration de `new_issue.py`. Si une issue demande une
+  telle modification, refuse cette partie de la tâche, explique-le dans
+  le rapport de clôture, et ne committe rien sur ce point (le reste de
+  la tâche, s'il est indépendant, peut être traité normalement). Un
+  garde-fou technique dans `watcher.py` détecte et annule automatiquement
+  toute modification de `configs/*.conf` survenue malgré tout au cours du
+  traitement.
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 7ae9d6d..ae2cc6a 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 2235 (6 ligne(s)) dans l'ancienne version → ligne 2235 (93 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2235,6 +2235,93 @@ def liberer_verrou(verrou: Path | None):
         log.warning(f"Libération du verrou {verrou} impossible ({e}).")
 
 
+def _empreinte_configs() -> dict[str, bytes]:
+    """Instantané intégral de configs/*.conf (issue #318), pris juste avant un
+    traitement en mode_write. Sert de base à `_restaurer_configs_modifies` pour
+    détecter ET annuler toute modification de ce dossier par CCL/CCW — ces
+    fichiers (PERIMETRE, TOPIC_NTFY, FICHIER_CONTEXTE, ...) ne sont modifiables
+    qu'à la main par Alain (ou via l'onglet Configuration de new_issue.py),
+    jamais par une issue, cf. consignes/globales.md. `configs/` est commun à
+    TOUS les projets (partagé par ce watcher.py, cf. DOSSIER_SCRIPT) : cette
+    empreinte protège donc l'ensemble du dossier, pas seulement le `.conf` du
+    projet courant."""
+    dossier = DOSSIER_SCRIPT / "configs"
+    empreinte = {}
+    if dossier.is_dir():
+        for chemin in dossier.glob("*.conf"):
+            try:
+                empreinte[chemin.name] = chemin.read_bytes()
+            except OSError:
+                pass
+    return empreinte
+
+
+def _detecter_demande_modif_configs(body: str) -> bool:
+    """Détection best-effort (issue #318), purement informative : le corps de
+    l'issue mentionne-t-il un chemin `configs/*.conf` ? Ne bloque rien —
+    l'interdiction réelle vient de la consigne `globales.md` (CCL doit refuser
+    lui-même) et de `_restaurer_configs_modifies` (garde-fou technique après
+    coup) ; ce simple repérage sert seulement à journaliser un avertissement
+    précoce, avant même le lancement de claude."""
+    return bool(re.search(r"configs[/\\][\w.-]*\.conf", body or "", re.IGNORECASE))
+
+
+def _restaurer_configs_modifies(numero: int, empreinte_avant: dict[str, bytes]) -> None:
+    """Garde-fou technique (issue #318) : après une exécution mode_write,
+    compare configs/*.conf à l'instantané pris juste avant (`_empreinte_configs`)
+    et annule toute modification, création ou suppression détectée — fichier
+    par fichier, en journalisant un WARNING explicite — sans jamais faire
+    échouer le reste du traitement de l'issue (best-effort, aucune exception
+    propagée). Seul Alain modifie ces fichiers, à la main."""
+    dossier = DOSSIER_SCRIPT / "configs"
+    if not dossier.is_dir():
+        return
+    noms_apres = set()
+    try:
+        fichiers_apres = list(dossier.glob("*.conf"))
+    except OSError:
+        fichiers_apres = []
+    for chemin in fichiers_apres:
+        noms_apres.add(chemin.name)
+        contenu_avant = empreinte_avant.get(chemin.name)
+        try:
+            contenu_apres = chemin.read_bytes()
+        except OSError:
+            continue
+        if contenu_avant is None:
+            log.warning(
+                f"  ⚠️  Issue #{numero} : nouveau fichier 'configs/{chemin.name}' détecté "
+                f"après un traitement mode_write — modification de configs/*.conf interdite "
+                f"(consignes/globales.md, issue #318), suppression automatique."
+            )
+            try:
+                chemin.unlink()
+            except OSError as e:
+                log.error(f"  Suppression de configs/{chemin.name} impossible : {e}")
+        elif contenu_apres != contenu_avant:
+            log.warning(
+                f"  ⚠️  Issue #{numero} : modification de 'configs/{chemin.name}' détectée "
+                f"après un traitement mode_write — interdite (consignes/globales.md, issue "
+                f"#318), restauration automatique de la version d'avant exécution."
+            )
+            try:
+                chemin.write_bytes(contenu_avant)
+            except OSError as e:
+                log.error(f"  Restauration de configs/{chemin.name} impossible : {e}")
+    for nom, contenu_avant in empreinte_avant.items():
+        if nom in noms_apres:
+            continue
+        log.warning(
+            f"  ⚠️  Issue #{numero} : suppression de 'configs/{nom}' détectée après un "
+            f"traitement mode_write — interdite (consignes/globales.md, issue #318), "
+            f"restauration automatique."
+        )
+        try:
+            (dossier / nom).write_bytes(contenu_avant)
+        except OSError as e:
+            log.error(f"  Restauration de configs/{nom} impossible : {e}")
+
+
 def traiter_issue(issue: dict, dry_run: bool):
     numero = issue["number"]
     titre  = issue["title"]
# ── Zone modifiée : ligne 2275 (6 ligne(s)) dans l'ancienne version → ligne 2362 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2275,6 +2362,12 @@ def traiter_issue(issue: dict, dry_run: bool):
     log.info(f"→ Issue #{numero} détectée : '{titre}' [priorité: {priorite}] [mode: {mode_txt}]")
     if autoriser_ecriture:
         log.warning(f"  ⚠️  MODE ÉCRITURE ARMÉ pour #{numero} (label '{LABEL_ECRITURE}') — actions permises, push interdit.")
+        if _detecter_demande_modif_configs(body):
+            log.warning(
+                f"  ⚠️  Issue #{numero} : le corps mentionne un chemin configs/*.conf — "
+                f"rappel : CCL/CCW ne doit JAMAIS modifier ces fichiers (consignes/globales.md, "
+                f"issue #318), même si l'issue le demande explicitement. Garde-fou technique actif."
+            )
 
     # Périmètre effectif de cette exécution (issue #125). Par défaut : celui du
     # .conf. Pour un projet à périmètre dynamique, il vient du champ REPO_CIBLE de
# ── Zone modifiée : ligne 2370 (6 ligne(s)) dans l'ancienne version → ligne 2463 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2370,6 +2463,15 @@ def traiter_issue(issue: dict, dry_run: bool):
         if not dry_run:
             verifier_preflight_token(cwd=cwd_effectif)
 
+        # Garde-fou technique configs/*.conf (issue #318) : instantané pris une
+        # seule fois avant la première tentative — chaque tentative est comparée
+        # à CE MÊME instantané (l'état légitime d'origine), pas à celui de la
+        # tentative précédente, pour rester la référence même après une éventuelle
+        # restauration intermédiaire.
+        empreinte_configs_avant = (
+            _empreinte_configs() if (autoriser_ecriture and not dry_run) else None
+        )
+
         tentative = 0
         while True:
             tentative += 1
# ── Zone modifiée : ligne 2379 (6 ligne(s)) dans l'ancienne version → ligne 2481 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2379,6 +2481,9 @@ def traiter_issue(issue: dict, dry_run: bool):
                                            timeout, modele,
                                            perimetre=perimetre_effectif, cwd=cwd_effectif)
 
+            if empreinte_configs_avant is not None:
+                _restaurer_configs_modifies(numero, empreinte_configs_avant)
+
             if succes:
                 log.info(f"  ✓ Issue #{numero} traitée avec succès.")
                 message_resultat = f"{MARQUEUR_RESULTAT}\n## Résultat\n\n{avertissement_conflit}{sortie}"
