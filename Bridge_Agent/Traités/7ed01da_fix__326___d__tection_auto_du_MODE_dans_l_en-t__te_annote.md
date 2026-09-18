7ed01da

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7ed01da
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 16:47:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #326 : détection auto du MODE dans l'en-tête + mode à valeurs extensibles
    
    - static/js/app.js : detecterModeDansCorps (calqué sur detecterTimeoutDansCorps)
      lit | MODE | ... | via lireChampEntete, reconnaissance tolérante (accents/
      casse, synonymes par mode), coche le bon radio, retire la ligne du corps,
      MODE absent/non reconnu -> LECTURE forcée (défaut sûr). Neutralisé en mode
      lot. mettreAJourBoutonEnvoi passe à 3 couleurs (COULEURS_MODE).
    - templates/index.html : 3e radio "lecture_active" (Lecture active) entre
      lecture et écriture, badge "scratch (mode_scratch, réservé)".
    - app/issues.py : table MODES {valeur radio -> (libellé fr, label github)}
      remplace les tests booléens en dur dans construire_body/construire_labels.
    - watcher.py : commentaire près de LABEL_ECRITURE documentant que mode_scratch
      est réservé et traité comme lecture seule tant que l'issue d'implémentation
      watcher n'est pas faite (aucune logique d'exécution touchée).
    - TACHES.md : backlog renommé mode_tmp_write -> mode_scratch (vocabulaire
      retenu), note de préparation faite par #326.
    - CHANGELOG.md : entrée.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 490fc76..f5a2fcd 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,51 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #326
+
+Détection automatique du MODE dans l'en-tête + mode à valeurs extensibles,
+préparation lecture active/mode_scratch (issue #326). Deux problèmes réglés
+ensemble : (1) contrairement à TIMEOUT/PROJET/titre, le champ `| MODE | … |`
+était GÉNÉRÉ à l'envoi mais jamais LU depuis le corps collé — Alain cochait
+« écriture » à la main par habitude même pour des tâches en réalité en
+lecture seule, ce qui rangeait des lectures dans la population « write » et
+faussait la calibration TIMEOUT (§19, clé projet|TYPE|mode) ; (2) le mode
+était un booléen en dur (`autoriser_ecriture` déduit du seul label
+`mode_write`), incapable de porter un futur 3e mode.
+
+Frontend (`static/js/app.js`) : nouveau `detecterModeDansCorps`, calqué sur
+`detecterTimeoutDansCorps`, branché sur l'input du corps — lit `| MODE | … |`
+via `lireChampEntete` (aucune regex dupliquée), reconnaît la valeur de façon
+tolérante (casse/accents, plusieurs libellés par mode : « écriture »/
+« write »/`mode_write` ; « lecture active »/« scratch »/`mode_scratch` ;
+« lecture »/« lecture seule »/« read »/`mode_read`), coche le bon radio,
+retire la ligne MODE du corps (comme TIMEOUT/PROJET) et met à jour la
+couleur du bouton d'envoi. **MODE absent ou non reconnu → LECTURE forcée**
+(défaut sûr, cohérent avec le reset après envoi). Neutralisé en mode lot
+(le MODE reste commun à tout le lot, DOC §3, inchangé).
+
+`templates/index.html` : 3e radio `lecture_active` entre lecture et
+écriture (ordre du moins au plus permissif), badge « scratch (mode_scratch,
+réservé) » + tooltip précisant que ce mode n'est pas encore fonctionnel côté
+watcher. Bouton d'envoi à 3 couleurs (`COULEURS_MODE`) : lecture → noir,
+lecture active → bleu, écriture → rouge (inchangé, réservé à l'écriture
+pleine, la plus risquée).
+
+`app/issues.py` : nouvelle table `MODES` ({valeur radio → (libellé
+français, label GitHub)}) lue à la fois par `construire_body` (champ
+`| MODE | … |`) et `construire_labels` (pose du label technique) — remplace
+les deux tests booléens en dur (`"ÉCRITURE" if mode == "ecriture" …` /
+`if mode == "ecriture": labels.append("mode_write")`). Un futur 4e mode ne
+demande qu'une ligne dans cette table.
+
+**`mode_scratch` reste RÉSERVÉ, watcher.py non touché** : cette issue ne
+porte pas l'implémentation de la lecture active côté watcher (issue séparée
+à venir) — juste documenté (commentaire près de `LABEL_ECRITURE`) qu'une
+issue portant `mode_scratch` sans `mode_write` est traitée comme lecture
+seule par le watcher actuel (`autoriser_ecriture` ne teste que
+`LABEL_ECRITURE`), comportement sûr. Backlog `TACHES.md` renommé en
+cohérence (`mode_tmp_write` → `mode_scratch`, vocabulaire retenu par #326).
+
 ## 2 août 2026 — issue #325
 
 Retrait de `TACHES.md` de l'entrée backlog « Bouton Interrompre dans
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index 951a85c..b70b63a 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 143 (7 ligne(s)) dans l'ancienne version → ligne 143 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -143,7 +143,7 @@ de code, pour valider le concept avant d'écrire le champ `WORKTREE` natif.
 
 ---
 
-## Mode mode_tmp_write — écriture scratch limitée pour outillage d'audit
+## Mode mode_scratch (lecture active) — écriture scratch limitée pour outillage d'audit
 
 **Contexte** : certains outils d'analyse (eslint flat config pour les
 versions ≥ 9, linters divers) exigent un vrai fichier de config sur disque,
# ── Zone modifiée : ligne 154 (8 ligne(s)) dans l'ancienne version → ligne 154 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -154,8 +154,16 @@ réglé par une consigne d'abandon immédiat au refus de permission) — c'est
 un besoin distinct et réel, pour les cas où l'outil a effectivement besoin
 d'un fichier de config.
 
+**Préparation faite (issue #326)** : vocabulaire retenu « lecture active »
+(label `mode_scratch`, renommé depuis la proposition initiale
+`mode_tmp_write` ci-dessous) ; formulaire (3e radio) et champ d'en-tête
+`| MODE | … |` préparés côté `new_issue.py` pour porter cette valeur. Label
+encore RÉSERVÉ : le watcher actuel ne le connaît pas et traite une issue
+`mode_scratch` comme lecture seule. Reste à faire ci-dessous : toute la
+logique d'exécution côté `watcher.py`.
+
 **Proposition** (reçue via rapport d'audit Scrabble) : un troisième mode,
-`mode_tmp_write`, avec :
+`mode_scratch`, avec :
 - Écriture autorisée uniquement dans un chemin scratch bien défini et
   validé strictement côté watcher (ex. `/tmp/bridge_scratch_<projet>/`),
   jamais dans `REP_TRAVAIL` du projet. Validation stricte du chemin pour
# (diff du fichier suivant)
diff --git a/app/issues.py b/app/issues.py
# (index — ignorable)
index 6bd2c1f..dd6f89d 100644
# (avant — fichier suivant)
--- a/app/issues.py
# (après — fichier suivant)
+++ b/app/issues.py
# ── Zone modifiée : ligne 142 (6 ligne(s)) dans l'ancienne version → ligne 142 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -142,6 +142,29 @@ def _parser_labels_entete(corps: str) -> list:
     return [lab.strip() for lab in m.group(1).split(",") if lab.strip()]
 
 
+# Table de correspondance MODE (issue #326) : {valeur du radio formulaire →
+# (libellé français écrit dans le champ d'en-tête | MODE | …, label GitHub
+# posé — None si aucun)}. Le mode n'est plus un booléen en dur (autrefois
+# `"ÉCRITURE" if mode == "ecriture" else "lecture seule"` + `if mode ==
+# "ecriture": labels.append("mode_write")`) : construire_body et
+# construire_labels lisent tous deux cette table, si bien qu'un futur 4e mode
+# ne demande qu'une ligne ici.
+#
+# lecture_active (label mode_scratch) est RÉSERVÉ : cette issue prépare le
+# terrain formulaire/en-tête pour la future « lecture active » du backlog
+# TACHES.md (écriture scratch limitée pour linters exigeant un fichier de
+# config sur disque), mais NE PORTE PAS l'implémentation côté watcher. Tant
+# que cette implémentation n'est pas faite, watcher.py ignore mode_scratch
+# (LABEL_ECRITURE == "mode_write" seul teste autoriser_ecriture) et traite
+# l'issue comme lecture seule — comportement sûr, mais pas encore la
+# « lecture active » annoncée par ce mode.
+MODES = {
+    "lecture":        ("lecture", None),
+    "lecture_active": ("lecture active", "mode_scratch"),
+    "ecriture":       ("écriture", "mode_write"),
+}
+
+
 def construire_body(data: dict) -> str:
     """Construit le body markdown depuis les champs du formulaire : tableau
     d'en-tête + corps rédigé par Claude Chat.
# ── Zone modifiée : ligne 153 (7 ligne(s)) dans l'ancienne version → ligne 176 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -153,7 +176,7 @@ def construire_body(data: dict) -> str:
     universelle quel que soit le chemin de création de l'issue (formulaire web,
     `gh issue create` d'un chef, création manuelle GitHub). Source unique de
     vérité côté watcher, plus de double injection. Voir §12.1 du DOC."""
-    mode            = "ÉCRITURE" if data.get("mode") == "ecriture" else "lecture seule"
+    mode, _         = MODES.get(data.get("mode"), MODES["lecture"])
     priorite        = data.get("priorite", "normale")
     timeout         = data.get("timeout", "300")
     modele_ponctuel = data.get("modele_ponctuel", "").strip()
# ── Zone modifiée : ligne 197 (8 ligne(s)) dans l'ancienne version → ligne 220 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -197,8 +220,9 @@ def construire_labels(data: dict) -> str:
     # autres labels standards (mode_write, notifs) restent posés normalement.
     if "for-windows" not in extras:
         labels.append("for-linux")
-    if data.get("mode") == "ecriture":
-        labels.append("mode_write")
+    _, label_mode = MODES.get(data.get("mode"), MODES["lecture"])
+    if label_mode:
+        labels.append(label_mode)
     notifs = data.get("notifs", [])
     if isinstance(notifs, str):
         notifs = [notifs]
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index a4f1fa2..6297c81 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 3471 (11 ligne(s)) dans l'ancienne version → ligne 3471 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3471,11 +3471,20 @@ async function actionWatchers(action) {
   await verifierStatut();
 }
 
+// Couleur du bouton d'envoi par mode — gradation cohérente avec l'ordre du
+// moins au plus permissif (issue #326) : lecture (noir) → lecture active
+// (bleu) → écriture (rouge, réservé à l'écriture pleine, la plus risquée).
+const COULEURS_MODE = {
+  lecture:        '#1a1a18',
+  lecture_active: '#1a4d8f',
+  ecriture:       '#a32d2d',
+};
 function mettreAJourBoutonEnvoi() {
-  const ecriture = document.querySelector('input[name=mode]:checked').value === 'ecriture';
+  const mode = document.querySelector('input[name=mode]:checked').value;
+  const couleur = COULEURS_MODE[mode] || COULEURS_MODE.lecture;
   const btn = document.getElementById('btn-envoyer');
-  btn.style.background    = ecriture ? '#a32d2d' : '#1a1a18';
-  btn.style.borderColor   = ecriture ? '#a32d2d' : '#1a1a18';
+  btn.style.background    = couleur;
+  btn.style.borderColor   = couleur;
 }
 
 // Détection de « #Titre: … » en première ligne du corps.
# ── Zone modifiée : ligne 3618 (6 ligne(s)) dans l'ancienne version → ligne 3627 (70 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3618,6 +3627,70 @@ function detecterTimeoutDansCorps() {
 }
 document.getElementById('corps').addEventListener('input', detecterTimeoutDansCorps);
 
+// Détection de « | MODE | <valeur> | » dans le corps → pré-sélection du radio
+// mode (lecture / lecture active / écriture), calquée sur detecterTimeoutDansCorps
+// (issue #326). Contrairement à PROJET/TIMEOUT, qui ignorent silencieusement un
+// champ absent, MODE a un DÉFAUT explicite quand il est absent ou non reconnu :
+// LECTURE (défaut sûr — cohérent avec le reset après envoi, ligne ~4090, et le
+// principe qu'une issue déclare toujours explicitement son mode quand elle
+// écrit, sinon c'est lecture). Corrige la calibration TIMEOUT (§19, clé
+// projet|TYPE|mode) faussée par l'habitude de cocher « écriture » à la main
+// même pour des tâches en réalité en lecture seule.
+//
+// Reconnaissance TOLÉRANTE (insensible casse/accents, plusieurs libellés par
+// mode) — ordre du tableau significatif : « lecture active » doit être testé
+// avant « lecture » pour ne pas être absorbé par ce synonyme plus court.
+const MODE_SYNONYMES = [
+  { valeur: 'ecriture',       motifs: ['écriture', 'ecriture', 'write', 'mode_write'] },
+  { valeur: 'lecture_active', motifs: ['lecture active', 'scratch', 'mode_scratch'] },
+  { valeur: 'lecture',        motifs: ['lecture seule', 'lecture', 'read', 'mode_read'] },
+];
+
+function normaliserTexteMode(texte) {
+  return texte.trim().toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
+}
+
+// Traduit le texte brut de la cellule « | MODE | … | » en valeur de radio.
+// Absent (chaîne vide/null) ou non reconnu → 'lecture' (défaut sûr).
+function reconnaitreModeTexte(brut) {
+  if (!brut) return 'lecture';
+  const normalise = normaliserTexteMode(brut);
+  const trouve = MODE_SYNONYMES.find(({ motifs }) =>
+    motifs.some(m => normalise.includes(normaliserTexteMode(m))));
+  return trouve ? trouve.valeur : 'lecture';
+}
+
+// Même garde-fou « valeur détectée changée » que detecterProjetDansCorps/
+// detecterTimeoutDansCorps : en régime stable (rien de neuf dans le corps), un
+// choix manuel du radio n'est jamais réécrasé — seul un changement effectif du
+// signal détecté (apparition/disparition/modification du champ MODE)
+// déclenche une resynchronisation.
+let dernierModeAutoDetecte = null;
+function detecterModeDansCorps() {
+  // Mode LOT : le MODE reste COMMUN à tout le lot, choisi via le radio du
+  // formulaire — pas détecté par bloc (DOC §3, hors périmètre de #326).
+  if (enModeLot()) { dernierModeAutoDetecte = null; return; }
+  const corpsEl = document.getElementById('corps');
+  const brut = lireChampEntete(corpsEl.value, 'MODE');
+  const valeurDetectee = reconnaitreModeTexte(brut);
+
+  // Rien de neuf depuis la dernière détection : ne pas réécraser un éventuel
+  // choix manuel d'Alain.
+  if (valeurDetectee === dernierModeAutoDetecte) return;
+  dernierModeAutoDetecte = valeurDetectee;
+
+  const radio = document.querySelector(`input[name=mode][value="${valeurDetectee}"]`);
+  if (radio && !radio.checked) radio.checked = true;
+
+  // Retire la ligne MODE du corps (comme TIMEOUT/PROJET), pour éviter que
+  // construire_body empile un second tableau d'en-tête — uniquement si le
+  // champ était effectivement présent (rien à retirer sinon).
+  if (brut) corpsEl.value = retirerLigneEntete(corpsEl.value, 'MODE');
+
+  mettreAJourBoutonEnvoi();
+}
+document.getElementById('corps').addEventListener('input', detecterModeDansCorps);
+
 // Résumé lecture seule des champs d'en-tête détectés dans le corps (issue #117).
 // Sous le champ Titre, on affiche une petite série de badges listant, dans
 // l'ordre du §6, les champs d'en-tête effectivement présents dans le corps
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 8517de2..081217e 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 114 (9 ligne(s)) dans l'ancienne version → ligne 114 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -114,9 +114,18 @@
     </div>
 
     <div class="titre-section">Mode</div>
+    <!-- Ordre du moins au plus permissif (issue #326) : lecture → lecture
+         active → écriture. Lecture active (label mode_scratch) est RÉSERVÉE :
+         préparée ici côté formulaire/en-tête, pas encore fonctionnelle côté
+         watcher (traitée comme lecture seule en attendant l'issue dédiée). -->
     <div class="radio-groupe">
       <label><input type="radio" name="mode" value="lecture" checked
                     onchange="mettreAJourBoutonEnvoi()"> Lecture seule</label>
+      <label><input type="radio" name="mode" value="lecture_active"
+                    onchange="mettreAJourBoutonEnvoi()"
+                    title="Réservé : préparé côté formulaire, pas encore fonctionnel côté watcher.">
+        Lecture active <span class="badge-alerte">scratch (mode_scratch, réservé)</span>
+      </label>
       <label><input type="radio" name="mode" value="ecriture"
                     onchange="mettreAJourBoutonEnvoi()">
         Écriture <span class="badge-alerte">⚠ mode_write</span>
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 0755c1b..f79e44f 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 132 (6 ligne(s)) dans l'ancienne version → ligne 132 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -132,6 +132,14 @@ LABEL_ECRITURE  = "mode_write"    # ARME le mode écriture (--dangerously-skip-p
 LABEL_ECHEC     = "needs-human"   # posé après échec définitif : stoppe le retraitement auto
 LABEL_FAIT      = "done"          # posé au succès
 
+# "mode_scratch" (issue #326) : label RÉSERVÉ pour la future « lecture active »
+# (TACHES.md) — écriture scratch limitée pour les linters qui exigent un
+# fichier de config sur disque. #326 ne prépare que le formulaire/en-tête ;
+# cette constante n'existe PAS encore ici volontairement : autoriser_ecriture
+# ne teste que LABEL_ECRITURE, donc une issue portant mode_scratch (sans
+# mode_write) est traitée comme lecture seule par ce watcher — comportement
+# sûr, en attendant l'issue d'implémentation dédiée qui l'activera.
+
 # Labels de notification (opt-in, cumulatifs avec le bip). Depuis l'issue #187,
 # le dispatch concret selon ces labels vit dans notifications.py (module partagé
 # avec new_issue.py) ; ces constantes restent ici comme contrat documentaire du
