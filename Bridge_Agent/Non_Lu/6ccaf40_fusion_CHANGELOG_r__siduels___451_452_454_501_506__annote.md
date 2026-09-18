6ccaf40

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6ccaf40
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Sep 7 20:22:42 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fusion CHANGELOG résiduels (#451/452/454/501/506/507/509/516) + #521 (fusionner_changelog.py)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-451.md b/CHANGELOG-451.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8a27134..0000000
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG-451.md
# ── Version APRÈS ce commit.
+++ /dev/null
# ── Zone modifiée : ligne 1 (25 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,25 +0,0 @@
-## 18 août 2026 — issue #451
-
-DOC — nouveau fichier `provisioning/windows/REINSTALLATION_CCW.md` :
-procédure complète de réinstallation du PC fixe CCW, aux côtés des scripts
-qu'elle utilise (`autounattend.xml`, `provisionner.ps1`,
-`mettre_a_jour_tokens_ccw.ps1`), plutôt que dans `BRIDGE_AGENT_DOC.md` qui
-est destiné aux agents CCL/CCW et non à la procédure d'installation
-Windows. Couvre dans l'ordre : réinstallation Windows via
-`autounattend.xml`, configuration SSH (`configurer_ssh_ccw.ps1`),
-vérification de la connexion SSH depuis CCL, provisioning logiciel
-(`provisionner.ps1`), topic ntfy + tokens
-(`mettre_a_jour_tokens_ccw.ps1`), vérification du service `CCW-Watcher`.
-Précise que la clé privée CCL (`~/.ssh/ccl_ccw`) reste sur le ThinkPad
-entre les réinstallations — seule la clé publique est à réinstaller sur le
-nouveau Windows.
-- `BRIDGE_AGENT_DOC.md` : §16 complété d'une ligne de référence vers ce
-  nouveau fichier.
-
-**Point d'attention signalé (pas corrigé, hors périmètre de cette
-issue) :** `configurer_ssh_ccw.ps1`, référencé à l'étape 2 de la
-procédure, n'existe pas dans `provisioning/windows/` au moment de la
-rédaction — il devra être créé (script PowerShell côté Windows qui active
-OpenSSH Server et installe la clé publique fournie dans
-`authorized_keys`) avant que l'étape 2 soit exécutable telle quelle. Une
-note l'indique en bas du nouveau fichier.
# (diff du fichier suivant)
diff --git a/CHANGELOG-452.md b/CHANGELOG-452.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index e52b4be..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-452.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (8 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,8 +0,0 @@
-## 18 août 2026 — issue #452
-
-CONFIG — `provisioning/windows/eval-expiration.json` mis à jour pour
-refléter l'échéance réelle du PC fixe physique (remplaçant l'ancienne VM
-VirtualBox, cf. #449/#450), installé le 17 août 2026.
-- `date_installation` : `2026-07-19` → `2026-08-17`.
-- `date_expiration` : `2026-10-17` → `2026-11-15` (date_installation +
-  eval_jours = 90 jours, conforme à la note du fichier).
# (diff du fichier suivant)
diff --git a/CHANGELOG-454.md b/CHANGELOG-454.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 59d5b4d..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-454.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (24 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,24 +0,0 @@
-## 18 août 2026 — issue #454
-
-FEATURE — Bandeau d'avertissement d'échéance de l'éval Windows CCW dans
-`new_issue.py`.
-- `app/eval_windows.py` (nouveau) : `etat_eval_windows()` lit
-  `provisioning/windows/eval-expiration.json`, recalcule la date
-  d'expiration (`date_installation` + `eval_jours`, même logique que
-  `provisioning/windows/verifier_expiration_ccw.py`) et retourne `None`
-  si le fichier est absent/invalide ou si l'échéance est encore lointaine
-  (> 14 jours), sinon un état `{jours_restants, date_expiration, niveau,
-  message}` avec `niveau` = `orange` (≤ 14 j) ou `rouge` (≤ 5 j ou
-  échéance dépassée).
-- `app/vues.py` : la route `index()` passe `eval_windows=etat_eval_windows()`
-  au gabarit.
-- `templates/index.html` : bandeau `{% if eval_windows %}` inséré juste
-  après l'en-tête, en dehors des panneaux d'onglets → visible sur tous
-  les onglets sans dupliquer le HTML.
-- `static/css/style.css` : styles `.bandeau-eval-windows.orange` (fond
-  `#fff3cd`) et `.rouge` (fond `#f8d7da`), cohérents avec les couleurs
-  d'alerte déjà utilisées ailleurs dans l'interface.
-- Vérifié par test manuel (`create_app()` + `test_client`) avec état
-  forcé orange/rouge/absent : bandeau présent avec le bon texte et la
-  bonne classe, absent quand l'échéance est lointaine (cas réel actuel :
-  89 jours restants au 18/08/2026) ou quand le fichier est absent/invalide.
# (diff du fichier suivant)
diff --git a/CHANGELOG-501.md b/CHANGELOG-501.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index ef92ba2..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-501.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (14 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,14 +0,0 @@
-## #501 — finaliser_projet_ccw.ps1 : clarification du prompt de confirmation du token
-
-Le message `Read-Host 'Appuie sur Entrée une fois le token créé et copié'` prêtait à
-confusion : il pouvait être lu comme une demande de coller le token à cet endroit,
-alors qu'il ne fait qu'attendre une touche Entrée pour continuer — le vrai collage
-du token a lieu juste après, dans `mettre_a_jour_tokens_ccw.ps1` (« Collez la valeur
-de GH_TOKEN »). Un utilisateur a déjà collé son token par erreur à cette invite.
-
-Reformulé en : `'Ne colle RIEN ici : une fois le token créé et copié, appuie juste
-sur Entrée pour continuer (le collage se fera à l'étape suivante)'`.
-
-Le script personnel `creer_projet_ccw_complet.ps1` (hors dépôt officiel) n'est pas
-accessible depuis ce worktree — la même formulation cohérente y est recommandée
-manuellement si un message similaire y existe.
# (diff du fichier suivant)
diff --git a/CHANGELOG-506.md b/CHANGELOG-506.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index de1fb28..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-506.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (24 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,24 +0,0 @@
-## #506 — eval-expiration.json : correction date d'installation Windows PC fixe (2026-08-30)
-
-`provisioning/windows/eval-expiration.json` contenait déjà `date_installation:
-2026-08-17` / `date_expiration: 2026-11-15` (mis à jour par le fix #452, le
-2026-08-18) — pas les valeurs `2026-07-19`/`2026-10-17` que l'issue supposait.
-La mesure fraîche du 30 août 2026 fournie dans l'issue (`GracePeriodRemaining`
-= 111244 min ≈ 77,25 j restants) recalcule une expiration au **2026-11-15**
-et une installation au **2026-08-17** — exactement les valeurs déjà en place.
-Aucune modification du JSON n'était donc nécessaire.
-
-En revanche, `BRIDGE_AGENT_DOC.md` §16.1 (tableau « Repères de dates »)
-n'avait pas été mis à jour lors du fix #452 et affichait encore les
-anciennes dates de la VM. Corrigé :
-- « Date d'installation Windows » : 2026-07-19 → **2026-08-17**
-- « Expiration éval Windows (90 j) » : 2026-10-17 → **2026-11-15**
-
-Non touché (hors périmètre de l'issue) :
-- §16, tableau `provisioning/windows/` (ligne `eval-expiration.json`) :
-  mentions 2026-07-19/2026-10-17 explicitement présentées comme historique
-  de l'ancienne VM VirtualBox (issue #167), conservées telles quelles.
-- §16.1, ligne « Expiration token GitHub » (≈ 2026-10-17) : concerne
-  l'expiration d'un token GitHub fine-grained réel, non recalculable depuis
-  la mesure Windows fournie — signalé pour vérification manuelle éventuelle,
-  non modifié.
# (diff du fichier suivant)
diff --git a/CHANGELOG-507.md b/CHANGELOG-507.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index d237a87..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-507.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (8 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,8 +0,0 @@
-## #507 — CONTEXTE.md : correction de deux mentions obsolètes de "VM Windows"
-
-`CONTEXTE.md` mentionnait encore « VM Windows » à deux endroits (description
-du module `app/ccw` et entrée changelog §16), alors que la migration vers un
-PC fixe physique est actée depuis longtemps (`BRIDGE_AGENT_DOC.md` §16,
-issue #446). Remplacé par « PC Windows physique », cohérent avec le
-vocabulaire de `BRIDGE_AGENT_DOC.md`. Vérifié qu'aucune autre mention de VM
-ne subsiste dans le fichier.
# (diff du fichier suivant)
diff --git a/CHANGELOG-509.md b/CHANGELOG-509.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index f4fd48e..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-509.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (19 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,19 +0,0 @@
-## 30 août 2026 — issue #509
-
-Panneau Infrastructure — bouton « Retirer needs-human » sur l'issue
-sélectionnée : demande déjà entièrement couverte par l'issue #460
-(commit `8dec213`, fusionné dans `master` avant #509). Vérification faite
-que le bouton « 🔄 Relancer » de `#pl-zone-actions`
-(`rendrePanneauLateralActions()`, `static/js/app.js`) remplit exactement
-le besoin décrit : visible uniquement quand l'issue sélectionnée porte le
-label `needs-human` et est ouverte, retire ce label via `gh issue edit
---remove-label` (route `POST /relancer-issue`,
-`app/interruption.py::route_relancer`, même mécanisme `--add-label`/
-`--remove-label` que `app/issues.py::modifier_label_notif`), ne ferme pas
-l'issue, poste un commentaire de trace, puis rafraîchit la liste et le
-détail sans rechargement manuel complet. Aucune modification de code
-nécessaire.
-- `BRIDGE_AGENT_DOC.md` : ajout de la sous-section « Relancer une issue
-  bloquée en `needs-human` (issue #460, cf. #509) » (juste après
-  « Interrompre une issue bloquée »), qui manquait — seul point réellement
-  manquant identifié pour cette issue.
# (diff du fichier suivant)
diff --git a/CHANGELOG-516.md b/CHANGELOG-516.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 769dc4c..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-516.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (40 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,40 +0,0 @@
-## 2 septembre 2026 — issue #516
-
-Champ `RELANCE` dans `issues_inbox/` : corriger/relancer une issue
-`needs-human` sans repasser par une édition manuelle sur GitHub. Jusqu'ici,
-ajuster un `TIMEOUT` trop court après un échec par dépassement obligeait à
-sortir du flux `issues_inbox` — redéposer un `.txt` avec le même titre
-échouait systématiquement (anti-doublon §3.4, qui rejette tout titre déjà
-porté par une issue OUVERTE, `needs-human` incluse).
-- `scripts/watcher_issues_inbox.py` : nouveau champ d'en-tête optionnel
-  `| RELANCE | #N |` (en cohérence avec `SUITE_DE`, §6). Présent, il
-  détourne tout le bloc vers la correction de l'issue #N déjà ouverte —
-  aucune création, anti-doublon court-circuité (n'a de sens que pour une
-  création). Validation avant modification (`valider_relance`,
-  `_recuperer_issue`) : `PROJET` résout le dépôt cible, `RELANCE` doit être
-  un numéro exploitable, `gh issue view --repo` confirme l'existence et
-  l'appartenance au bon dépôt, l'issue doit être OUVERTE — sinon rejet vers
-  `rejected/`, même mécanique que les rejets existants. Champs corrigibles
-  dans le corps : `TIMEOUT` et `MODELE` uniquement (`_fusionner_entete`/
-  `_maj_ligne_entete` — corrige une ligne déjà présente, n'en insère jamais
-  une nouvelle). `MODE` est exclu (le mode réel est armé par le label GitHub
-  `mode_write`/`mode_scratch`, pas par le texte du corps — le
-  resynchroniser depuis ce chemin est jugé hors-scope pour cette première
-  itération) ; `LABELS` aussi (n'apparaît jamais dans le corps).
-- `app/interruption.py` : logique de `route_relancer()` (bouton
-  « 🔄 Relancer », issue #460) extraite dans `relancer_issue(depot, numero,
-  commentaire=...)`, réutilisée telle quelle par le champ `RELANCE` — aucun
-  retrait de label / pose de commentaire dupliqué entre les deux flux. Le
-  commentaire posté depuis `issues_inbox/` mentionne explicitement RELANCE,
-  résume les champs corrigés et reprend le texte libre éventuel du fichier
-  déposé.
-- `BRIDGE_AGENT_DOC.md` : nouveau §3.14, ligne `RELANCE` ajoutée au tableau
-  §6.
-- `tests/test_champ_relance_516.py` (nouveau) : extraction du champ,
-  parsing du numéro, fusion des champs corrigibles (jamais d'insertion d'un
-  champ absent), chemin complet `_traiter_relance` (succès, issue fermée,
-  numéro invalide) — tous les appels `gh` substitués, aucun accès réseau.
-- Formulaire web (`new_issue.py`) volontairement non modifié : il sert à
-  **créer** des issues et dispose déjà d'un chemin dédié pour cibler une
-  issue existante (bouton « 🔄 Relancer ») — dupliquer `RELANCE` là
-  n'apporterait rien.
# (diff du fichier suivant)
diff --git a/CHANGELOG-521.md b/CHANGELOG-521.md
# ── Ce fichier est supprimé par ce commit.
deleted file mode 100644
# (index — ignorable)
index 2ab006d..0000000
# (avant — fichier suivant)
--- a/CHANGELOG-521.md
# (après — fichier suivant)
+++ /dev/null
# ── Zone modifiée : ligne 1 (38 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,38 +0,0 @@
-## 7 septembre 2026 — issue #521
-
-Traçabilité minimale sur `logs/historique_durees.json` et
-`logs/etat_timeout.json`, pour diagnostiquer une future perte de données
-comme celle du 7 septembre 2026 restée inexpliquée faute de preuve (fichiers
-gitignorés, aucun historique git natif).
-- Approche retenue (parmi les deux esquissées dans l'issue) : un journal
-  séparé append-only, plutôt qu'une exception ciblée au `.gitignore` de
-  `logs/` — `historique_durees.json` grossit à chaque issue close
-  (cf. `scripts/archiver_historique.py`), le suivre en git alourdirait
-  chaque commit de sauvegarde CCL sans rapport avec la tâche en cours.
-- `watcher.py` : nouveau `logs/journal_ecritures_historique.jsonl` (JSON
-  Lines, déjà couvert par le `.gitignore` existant de `logs/`) via
-  `_journaliser_ecriture` (nouvelle fonction). Une ligne par écriture
-  significative : `nb_avant`/`nb_apres` (nombre d'entrées), taille en octets
-  avant/après, `operation`, et `reinitialise_corruption=true` si l'écriture
-  repart d'un JSON illisible (la signature exacte d'une perte de données
-  silencieuse — jusqu'ici, `enregistrer_duree` réinitialisait déjà
-  discrètement l'historique à `[]` dans ce cas, sans laisser aucune trace).
-  Appelé depuis `enregistrer_duree` (`operation="cloture_issue"`,
-  `historique_durees.json`) et depuis `_maj_etat_json` pour
-  `etat_timeout.json` uniquement (`operation="calibration_timeout"`,
-  nombre de combinaisons avant/après) — `etat_ambiance.json` non instrumenté
-  (deux clés fixes `F_reseau`/`F_local`, jamais perdues de la même façon,
-  hors du périmètre demandé par l'issue).
-- `scripts/archiver_historique.py` : écrit aussi dans ce même journal
-  (`operation="archivage_manuel"`, nouvelle fonction locale
-  `_journaliser_archivage`, sans importer `watcher.py` — cohérent avec le
-  découplage volontaire du script) lors d'une exécution réelle (jamais en
-  `--dry-run`). But : qu'une réduction volontaire et attendue du fichier
-  (archivage manuel par Alain) ne soit jamais confondue, à la lecture du
-  journal, avec une chute inexpliquée.
-- `BRIDGE_AGENT_DOC.md` (§19.3, §19.7) : documentation du nouveau journal et
-  de son rôle diagnostique.
-- Aucun test dédié ajouté : vérification manuelle (écritures normales,
-  simulation d'une corruption suivie d'une réinitialisation, exécution de
-  `archiver_historique.py`) dans un dossier temporaire isolé, hors du
-  périmètre du projet — cf. rapport de clôture de l'issue.
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 35da678..0ecbea9 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (215 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,215 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 7 septembre 2026 — issue #521
+
+Traçabilité minimale sur `logs/historique_durees.json` et
+`logs/etat_timeout.json`, pour diagnostiquer une future perte de données
+comme celle du 7 septembre 2026 restée inexpliquée faute de preuve (fichiers
+gitignorés, aucun historique git natif).
+- Approche retenue (parmi les deux esquissées dans l'issue) : un journal
+  séparé append-only, plutôt qu'une exception ciblée au `.gitignore` de
+  `logs/` — `historique_durees.json` grossit à chaque issue close
+  (cf. `scripts/archiver_historique.py`), le suivre en git alourdirait
+  chaque commit de sauvegarde CCL sans rapport avec la tâche en cours.
+- `watcher.py` : nouveau `logs/journal_ecritures_historique.jsonl` (JSON
+  Lines, déjà couvert par le `.gitignore` existant de `logs/`) via
+  `_journaliser_ecriture` (nouvelle fonction). Une ligne par écriture
+  significative : `nb_avant`/`nb_apres` (nombre d'entrées), taille en octets
+  avant/après, `operation`, et `reinitialise_corruption=true` si l'écriture
+  repart d'un JSON illisible (la signature exacte d'une perte de données
+  silencieuse — jusqu'ici, `enregistrer_duree` réinitialisait déjà
+  discrètement l'historique à `[]` dans ce cas, sans laisser aucune trace).
+  Appelé depuis `enregistrer_duree` (`operation="cloture_issue"`,
+  `historique_durees.json`) et depuis `_maj_etat_json` pour
+  `etat_timeout.json` uniquement (`operation="calibration_timeout"`,
+  nombre de combinaisons avant/après) — `etat_ambiance.json` non instrumenté
+  (deux clés fixes `F_reseau`/`F_local`, jamais perdues de la même façon,
+  hors du périmètre demandé par l'issue).
+- `scripts/archiver_historique.py` : écrit aussi dans ce même journal
+  (`operation="archivage_manuel"`, nouvelle fonction locale
+  `_journaliser_archivage`, sans importer `watcher.py` — cohérent avec le
+  découplage volontaire du script) lors d'une exécution réelle (jamais en
+  `--dry-run`). But : qu'une réduction volontaire et attendue du fichier
+  (archivage manuel par Alain) ne soit jamais confondue, à la lecture du
+  journal, avec une chute inexpliquée.
+- `BRIDGE_AGENT_DOC.md` (§19.3, §19.7) : documentation du nouveau journal et
+  de son rôle diagnostique.
+- Aucun test dédié ajouté : vérification manuelle (écritures normales,
+  simulation d'une corruption suivie d'une réinitialisation, exécution de
+  `archiver_historique.py`) dans un dossier temporaire isolé, hors du
+  périmètre du projet — cf. rapport de clôture de l'issue.
+
+## 2 septembre 2026 — issue #516
+
+Champ `RELANCE` dans `issues_inbox/` : corriger/relancer une issue
+`needs-human` sans repasser par une édition manuelle sur GitHub. Jusqu'ici,
+ajuster un `TIMEOUT` trop court après un échec par dépassement obligeait à
+sortir du flux `issues_inbox` — redéposer un `.txt` avec le même titre
+échouait systématiquement (anti-doublon §3.4, qui rejette tout titre déjà
+porté par une issue OUVERTE, `needs-human` incluse).
+- `scripts/watcher_issues_inbox.py` : nouveau champ d'en-tête optionnel
+  `| RELANCE | #N |` (en cohérence avec `SUITE_DE`, §6). Présent, il
+  détourne tout le bloc vers la correction de l'issue #N déjà ouverte —
+  aucune création, anti-doublon court-circuité (n'a de sens que pour une
+  création). Validation avant modification (`valider_relance`,
+  `_recuperer_issue`) : `PROJET` résout le dépôt cible, `RELANCE` doit être
+  un numéro exploitable, `gh issue view --repo` confirme l'existence et
+  l'appartenance au bon dépôt, l'issue doit être OUVERTE — sinon rejet vers
+  `rejected/`, même mécanique que les rejets existants. Champs corrigibles
+  dans le corps : `TIMEOUT` et `MODELE` uniquement (`_fusionner_entete`/
+  `_maj_ligne_entete` — corrige une ligne déjà présente, n'en insère jamais
+  une nouvelle). `MODE` est exclu (le mode réel est armé par le label GitHub
+  `mode_write`/`mode_scratch`, pas par le texte du corps — le
+  resynchroniser depuis ce chemin est jugé hors-scope pour cette première
+  itération) ; `LABELS` aussi (n'apparaît jamais dans le corps).
+- `app/interruption.py` : logique de `route_relancer()` (bouton
+  « 🔄 Relancer », issue #460) extraite dans `relancer_issue(depot, numero,
+  commentaire=...)`, réutilisée telle quelle par le champ `RELANCE` — aucun
+  retrait de label / pose de commentaire dupliqué entre les deux flux. Le
+  commentaire posté depuis `issues_inbox/` mentionne explicitement RELANCE,
+  résume les champs corrigés et reprend le texte libre éventuel du fichier
+  déposé.
+- `BRIDGE_AGENT_DOC.md` : nouveau §3.14, ligne `RELANCE` ajoutée au tableau
+  §6.
+- `tests/test_champ_relance_516.py` (nouveau) : extraction du champ,
+  parsing du numéro, fusion des champs corrigibles (jamais d'insertion d'un
+  champ absent), chemin complet `_traiter_relance` (succès, issue fermée,
+  numéro invalide) — tous les appels `gh` substitués, aucun accès réseau.
+- Formulaire web (`new_issue.py`) volontairement non modifié : il sert à
+  **créer** des issues et dispose déjà d'un chemin dédié pour cibler une
+  issue existante (bouton « 🔄 Relancer ») — dupliquer `RELANCE` là
+  n'apporterait rien.
+
+## 30 août 2026 — issue #509
+
+Panneau Infrastructure — bouton « Retirer needs-human » sur l'issue
+sélectionnée : demande déjà entièrement couverte par l'issue #460
+(commit `8dec213`, fusionné dans `master` avant #509). Vérification faite
+que le bouton « 🔄 Relancer » de `#pl-zone-actions`
+(`rendrePanneauLateralActions()`, `static/js/app.js`) remplit exactement
+le besoin décrit : visible uniquement quand l'issue sélectionnée porte le
+label `needs-human` et est ouverte, retire ce label via `gh issue edit
+--remove-label` (route `POST /relancer-issue`,
+`app/interruption.py::route_relancer`, même mécanisme `--add-label`/
+`--remove-label` que `app/issues.py::modifier_label_notif`), ne ferme pas
+l'issue, poste un commentaire de trace, puis rafraîchit la liste et le
+détail sans rechargement manuel complet. Aucune modification de code
+nécessaire.
+- `BRIDGE_AGENT_DOC.md` : ajout de la sous-section « Relancer une issue
+  bloquée en `needs-human` (issue #460, cf. #509) » (juste après
+  « Interrompre une issue bloquée »), qui manquait — seul point réellement
+  manquant identifié pour cette issue.
+
+## #507 — CONTEXTE.md : correction de deux mentions obsolètes de "VM Windows"
+
+`CONTEXTE.md` mentionnait encore « VM Windows » à deux endroits (description
+du module `app/ccw` et entrée changelog §16), alors que la migration vers un
+PC fixe physique est actée depuis longtemps (`BRIDGE_AGENT_DOC.md` §16,
+issue #446). Remplacé par « PC Windows physique », cohérent avec le
+vocabulaire de `BRIDGE_AGENT_DOC.md`. Vérifié qu'aucune autre mention de VM
+ne subsiste dans le fichier.
+
+## #506 — eval-expiration.json : correction date d'installation Windows PC fixe (2026-08-30)
+
+`provisioning/windows/eval-expiration.json` contenait déjà `date_installation:
+2026-08-17` / `date_expiration: 2026-11-15` (mis à jour par le fix #452, le
+2026-08-18) — pas les valeurs `2026-07-19`/`2026-10-17` que l'issue supposait.
+La mesure fraîche du 30 août 2026 fournie dans l'issue (`GracePeriodRemaining`
+= 111244 min ≈ 77,25 j restants) recalcule une expiration au **2026-11-15**
+et une installation au **2026-08-17** — exactement les valeurs déjà en place.
+Aucune modification du JSON n'était donc nécessaire.
+
+En revanche, `BRIDGE_AGENT_DOC.md` §16.1 (tableau « Repères de dates »)
+n'avait pas été mis à jour lors du fix #452 et affichait encore les
+anciennes dates de la VM. Corrigé :
+- « Date d'installation Windows » : 2026-07-19 → **2026-08-17**
+- « Expiration éval Windows (90 j) » : 2026-10-17 → **2026-11-15**
+
+Non touché (hors périmètre de l'issue) :
+- §16, tableau `provisioning/windows/` (ligne `eval-expiration.json`) :
+  mentions 2026-07-19/2026-10-17 explicitement présentées comme historique
+  de l'ancienne VM VirtualBox (issue #167), conservées telles quelles.
+- §16.1, ligne « Expiration token GitHub » (≈ 2026-10-17) : concerne
+  l'expiration d'un token GitHub fine-grained réel, non recalculable depuis
+  la mesure Windows fournie — signalé pour vérification manuelle éventuelle,
+  non modifié.
+
+## #501 — finaliser_projet_ccw.ps1 : clarification du prompt de confirmation du token
+
+Le message `Read-Host 'Appuie sur Entrée une fois le token créé et copié'` prêtait à
+confusion : il pouvait être lu comme une demande de coller le token à cet endroit,
+alors qu'il ne fait qu'attendre une touche Entrée pour continuer — le vrai collage
+du token a lieu juste après, dans `mettre_a_jour_tokens_ccw.ps1` (« Collez la valeur
+de GH_TOKEN »). Un utilisateur a déjà collé son token par erreur à cette invite.
+
+Reformulé en : `'Ne colle RIEN ici : une fois le token créé et copié, appuie juste
+sur Entrée pour continuer (le collage se fera à l'étape suivante)'`.
+
+Le script personnel `creer_projet_ccw_complet.ps1` (hors dépôt officiel) n'est pas
+accessible depuis ce worktree — la même formulation cohérente y est recommandée
+manuellement si un message similaire y existe.
+
+## 18 août 2026 — issue #454
+
+FEATURE — Bandeau d'avertissement d'échéance de l'éval Windows CCW dans
+`new_issue.py`.
+- `app/eval_windows.py` (nouveau) : `etat_eval_windows()` lit
+  `provisioning/windows/eval-expiration.json`, recalcule la date
+  d'expiration (`date_installation` + `eval_jours`, même logique que
+  `provisioning/windows/verifier_expiration_ccw.py`) et retourne `None`
+  si le fichier est absent/invalide ou si l'échéance est encore lointaine
+  (> 14 jours), sinon un état `{jours_restants, date_expiration, niveau,
+  message}` avec `niveau` = `orange` (≤ 14 j) ou `rouge` (≤ 5 j ou
+  échéance dépassée).
+- `app/vues.py` : la route `index()` passe `eval_windows=etat_eval_windows()`
+  au gabarit.
+- `templates/index.html` : bandeau `{% if eval_windows %}` inséré juste
+  après l'en-tête, en dehors des panneaux d'onglets → visible sur tous
+  les onglets sans dupliquer le HTML.
+- `static/css/style.css` : styles `.bandeau-eval-windows.orange` (fond
+  `#fff3cd`) et `.rouge` (fond `#f8d7da`), cohérents avec les couleurs
+  d'alerte déjà utilisées ailleurs dans l'interface.
+- Vérifié par test manuel (`create_app()` + `test_client`) avec état
+  forcé orange/rouge/absent : bandeau présent avec le bon texte et la
+  bonne classe, absent quand l'échéance est lointaine (cas réel actuel :
+  89 jours restants au 18/08/2026) ou quand le fichier est absent/invalide.
+
+## 18 août 2026 — issue #452
+
+CONFIG — `provisioning/windows/eval-expiration.json` mis à jour pour
+refléter l'échéance réelle du PC fixe physique (remplaçant l'ancienne VM
+VirtualBox, cf. #449/#450), installé le 17 août 2026.
+- `date_installation` : `2026-07-19` → `2026-08-17`.
+- `date_expiration` : `2026-10-17` → `2026-11-15` (date_installation +
+  eval_jours = 90 jours, conforme à la note du fichier).
+
+## 18 août 2026 — issue #451
+
+DOC — nouveau fichier `provisioning/windows/REINSTALLATION_CCW.md` :
+procédure complète de réinstallation du PC fixe CCW, aux côtés des scripts
+qu'elle utilise (`autounattend.xml`, `provisionner.ps1`,
+`mettre_a_jour_tokens_ccw.ps1`), plutôt que dans `BRIDGE_AGENT_DOC.md` qui
+est destiné aux agents CCL/CCW et non à la procédure d'installation
+Windows. Couvre dans l'ordre : réinstallation Windows via
+`autounattend.xml`, configuration SSH (`configurer_ssh_ccw.ps1`),
+vérification de la connexion SSH depuis CCL, provisioning logiciel
+(`provisionner.ps1`), topic ntfy + tokens
+(`mettre_a_jour_tokens_ccw.ps1`), vérification du service `CCW-Watcher`.
+Précise que la clé privée CCL (`~/.ssh/ccl_ccw`) reste sur le ThinkPad
+entre les réinstallations — seule la clé publique est à réinstaller sur le
+nouveau Windows.
+- `BRIDGE_AGENT_DOC.md` : §16 complété d'une ligne de référence vers ce
+  nouveau fichier.
+
+**Point d'attention signalé (pas corrigé, hors périmètre de cette
+issue) :** `configurer_ssh_ccw.ps1`, référencé à l'étape 2 de la
+procédure, n'existe pas dans `provisioning/windows/` au moment de la
+rédaction — il devra être créé (script PowerShell côté Windows qui active
+OpenSSH Server et installe la clé publique fournie dans
+`authorized_keys`) avant que l'étape 2 soit exécutable telle quelle. Une
+note l'indique en bas du nouveau fichier.
+
 ## 7 septembre 2026 — issue #518
 
 DOC — retrait de toute mention du copier-coller comme méthode de création
