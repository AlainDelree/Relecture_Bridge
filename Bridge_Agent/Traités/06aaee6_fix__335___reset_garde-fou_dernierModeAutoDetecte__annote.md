06aaee6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 06aaee6
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 22:32:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #335 : reset garde-fou dernierModeAutoDetecte au vidage du formulaire

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d764995..1a8baa1 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,34 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #335
+
+Correction du radio Mode qui restait parfois figé sur « Lecture seule » après
+un collage, alors que le corps collé portait bien `| MODE | écriture |` —
+symptôme intermittent, corrigé par un simple F5 puis re-collage (observé à la
+suite des issues #157 et suivantes).
+
+- Cause racine : `viderFormulaire()` (appelée après chaque envoi réussi) remet
+  le radio Mode sur *lecture* mais ne réinitialisait pas `dernierModeAutoDetecte`,
+  la variable de garde de `detecterModeDansCorps()` (#326) qui évite de réécraser
+  un choix manuel quand « rien de neuf » n'est détecté dans le corps. Si le
+  corps collé ensuite portait le MÊME MODE que la détection précédente,
+  `detecterModeDansCorps` voyait `valeurDetectee === dernierModeAutoDetecte` et
+  ne touchait plus au radio — qui restait donc sur *lecture*, alors que ce
+  n'était pas un choix manuel d'Alain mais le défaut posé de force par
+  `viderFormulaire()` (qui vide aussi le corps par affectation directe de
+  `.value`, sans déclencher d'événement `input`, donc sans repasser par la
+  détection). Un rafraîchissement de page réinitialise cette variable JS à
+  `null`, ce qui « corrigeait » silencieusement le symptôme au collage suivant.
+- `static/js/app.js` (`viderFormulaire`) : ajout de `dernierModeAutoDetecte =
+  null;` juste après la remise à *lecture* du radio, pour que le prochain
+  collage soit toujours traité comme une détection neuve, quelle que soit la
+  valeur MODE précédemment vue dans la session.
+- Non modifié : `detecterProjetDansCorps`/`detecterTimeoutDansCorps`
+  partagent le même schéma de garde-fou (`dernierProjetAutoDetecte`,
+  `dernierTimeoutAutoDetecte`) et pourraient présenter la même faille — hors
+  périmètre de cette issue, à traiter séparément si observé en pratique.
+
 ## 2 août 2026 — issue #334
 
 Onglet Résultats : fetch unique de vérification 15s après le dépassement du
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 90b7970..ce8de7d 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 4294 (6 ligne(s)) dans l'ancienne version → ligne 4294 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4294,6 +4294,14 @@ function viderFormulaire(cacherMsg=true) {
   // Réinitialise le timeout sur la valeur TIMEOUT_CLAUDE du projet courant.
   mettreAJourInfoProjet();
   document.querySelector('input[name=mode][value=lecture]').checked = true;
+  // Réinitialise le garde-fou de detecterModeDansCorps (#335) : sans ça, coller
+  // ensuite un corps portant le MÊME MODE que la détection précédente est vu
+  // comme « rien de neuf » (ligne ~3812) et le radio — pourtant remis de force à
+  // lecture juste au-dessus, pas par un choix manuel d'Alain — ne rebasculait
+  // pas sur la valeur collée. D'où le symptôme intermittent (dépend de si le
+  // MODE collé diffère du précédent) qu'un F5 « corrigeait » en réinitialisant
+  // cette variable JS à null.
+  dernierModeAutoDetecte = null;
   mettreAJourBoutonEnvoi();
   document.querySelectorAll('input[name=notifs]').forEach(c => c.checked = false);
   // notif_pc revient à l'état mémorisé (coché par défaut), pas à décoché.
