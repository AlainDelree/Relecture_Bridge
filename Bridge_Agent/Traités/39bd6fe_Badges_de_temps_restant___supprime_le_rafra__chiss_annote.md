39bd6fe

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 39bd6fe
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 05:33:34 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Badges de temps restant : supprime le rafraîchissement périodique, ne charge qu'à la demande (issue #270)
    
    Reprise propre de #269 (fermée en échec : 3 tentatives timeout à 900s,
    travail resté non commité proprement). intervalFetchTiming supprimé,
    intervalTempsRestant conservé. chargerTimingIssues() appelée seulement
    au chargement initial et depuis rafraichirResultats(). Décompte figé à
    « 0s — budget épuisé » au lieu d'un compteur de dépassement croissant,
    jamais de valeur négative ni de message spéculatif. Retrait des deux
    résidus de debug laissés par la tentative précédente (console.error
    DEBUG-269-TRACE, harnais temporaire dans templates/index.html). Second
    appelant de /issues-en-attente (garde-fou avant envoi) intact.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6628813..a010a9d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,10 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 29 juillet 2026 — issue #270
+
+Badges de temps restant : suppression du rafraîchissement périodique (issue #270, remplace #269 fermée sans correctif — mesure infaisable dans le TIMEOUT, décisions non tranchées). `intervalFetchTiming` (re-fetch de `/issues-en-attente/<projet>` toutes les 15s pour tous les projets configurés, ~3840 pts/h mesurés par #263, premier poste de consommation du quota GraphQL) supprimé ; `intervalTempsRestant` conservé (décompte purement client, recalcul chaque seconde, sans coût réseau). `chargerTimingIssues()` n'est plus appelée qu'au chargement initial de l'onglet Résultats et depuis `rafraichirResultats()` (bouton rafraîchir), pour qu'un seul geste mette à jour liste ET badges. Décision sur le décompte (point 3 de #269, laissé en suspens) : une fois le budget total épuisé, le badge se fige à « ⌛ 0s — budget épuisé » au lieu d'un compteur de dépassement qui grossissait indéfiniment (`⌛ dépassement +Xs`) — jamais de valeur négative, jamais de message spéculatif du type « terminé ? » (l'état réel n'est pas connu sans re-fetch), badge visible jusqu'au prochain rafraîchissement manuel. Retrait de deux résidus d'une tentative précédente non commitée proprement : un `console.error('[DEBUG-269-TRACE]', …)` dans `chargerTimingIssues()` et un bloc `<script>` de harnais temporaire dans `templates/index.html` (auto-bascule vers l'onglet Résultats après 800ms) qui portait lui-même la mention « à retirer avant commit ». Second appelant de `/issues-en-attente` (~ligne 2735, garde-fou avant l'envoi d'une nouvelle issue) : hors périmètre de cette issue, laissé strictement tel quel. Aucune mesure de gain (hors périmètre, cf. #269 : nécessite un navigateur ouvert 5+ minutes, invérifiable depuis l'agent) — à faire par Alain avec `scripts/mesurer_api.py`.
+
 ## 29 juillet 2026 — issue #268
 
 Corrige la corruption du § 10 provoquée par #263 (issue #268) : l'entrée de #263, destinée au vrai pied de page (dernière ligne du fichier), avait été insérée à la place du `<date> — ...` du modèle explicatif du §10 — remplacement effectué sur la première occurrence de « Dernière mise à jour » dans le fichier, qui est cet exemple, pas le pied de page situé bien plus bas. Deux dégâts cumulés : le §10 affichait un modèle cassé (phrase du point 2 disloquée par le texte de #263 inséré en son milieu) et le vrai pied de page n'avait PAS reçu l'entrée de #263 — il avait seulement perdu #252, passant de trois entrées (#257, #253, #252) à deux (#257, #253), contredisant le rapport de clôture de #263 qui affirmait à tort « Footer glissé (#263 en tête, #257 et #253 conservées, #252 sorti) ». **Correctifs** : (1) §10 restauré au mot près dans son état d'origine (`*Dernière mise à jour : <date> — ...*`) ; (2) pied de page reconstruit avec l'entrée #263 en tête suivie de #257 et #253 (les trois entrées les plus récentes parmi les issues modifiant cette doc), puis complété dans la même opération par cette propre entrée #268, faisant sortir #253 ; (3) garde-fou ajouté au §10 (nouveau point 3) : le format n'apparaît qu'à la toute dernière ligne du fichier, une recherche sur « Dernière mise à jour » remontant d'abord l'exemple du §10 — toujours viser la fin du fichier, jamais la première occurrence. **Test (point 4)** : regex de `nouveau_projet.py` (`(\*Dernière mise à jour : )[^—]*( —)`) rejouée réellement (`re.sub`) contre la première ligne du pied de page corrigé — match confirmé, substitution de la date vérifiée avec succès. Aucun fichier `.py` modifié, aucune section renumérotée.
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 98ae8cd..83de482 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1240 (21 ligne(s)) dans l'ancienne version → ligne 1240 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1240,21 +1240,22 @@ function appliquerFiltresListe() {
 // (champ `debut`). Le compte à rebours est ensuite PUREMENT client : une fois
 // debut+timeout connus, un intervalle JS recalcule le restant chaque seconde
 // sans re-solliciter le serveur.
-// Mise à jour des données elles-mêmes (issue #269) : PLUS de re-fetch
-// périodique — l'interface web laissée ouverte avec plusieurs projets
-// configurés interrogeait GitHub en continu (~3840 pts/h mesurés, premier
-// poste de consommation du quota GraphQL, cf. issue #263) pour un gain
-// (voir apparaître un badge 15s plus tôt) jugé insuffisant par Alain.
+// Mise à jour des données elles-mêmes (issue #270, suite #269) : PLUS de
+// re-fetch périodique — l'interface web laissée ouverte avec plusieurs
+// projets configurés interrogeait GitHub en continu (~3840 pts/h mesurés,
+// premier poste de consommation du quota GraphQL, cf. issue #263) pour un
+// gain (voir apparaître un badge 15s plus tôt) jugé insuffisant par Alain.
 // chargerTimingIssues() n'est donc plus appelée qu'à la demande : au
 // chargement initial de l'onglet Résultats (demarrerTempsRestant) et par le
 // bouton rafraîchir (rafraichirResultats), qui met à jour liste ET badges
 // d'un même geste. Conséquence assumée : une issue qui se termine pendant
-// que l'onglet reste ouvert garde son décompte affiché (y compris en
-// dépassement, cf. formaterBadgeTempsRestant) jusqu'au prochain
-// rafraîchissement manuel — comportement jugé moins trompeur qu'un badge qui
-// disparaîtrait ou se figerait sans explication, et cohérent avec le fait
-// que la LISTE elle-même (chargerListeIssues) suit déjà ce même modèle
-// « à la demande » et ne se rafraîchit pas non plus toute seule.
+// que l'onglet reste ouvert garde son décompte affiché jusqu'au prochain
+// rafraîchissement manuel. Décompte figé à zéro une fois le budget épuisé
+// (cf. formaterBadgeTempsRestant) : jamais de valeur négative, jamais de
+// message spéculatif du type « terminé ? » — sans re-fetch, cette
+// information n'est pas connue côté client. Cohérent avec le fait que la
+// LISTE elle-même (chargerListeIssues) suit déjà ce même modèle « à la
+// demande » et ne se rafraîchit pas non plus toute seule.
 let timingIssues = {};              // clé "projet#numero" → {timeout, max_essais, backoff, debut, sans_limite}
 let intervalTempsRestant = null;    // recalcul 1 s du compte à rebours (client seul, aucun appel réseau)
 
# ── Zone modifiée : ligne 1271 (7 ligne(s)) dans l'ancienne version → ligne 1272 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1271,7 +1272,6 @@ function formaterDuree(s) {
 // Récupère, pour tous les projets, les débuts de traitement + timeouts des
 // issues ouvertes, puis rafraîchit immédiatement les badges.
 async function chargerTimingIssues() {
-  console.error('[DEBUG-269-TRACE]', new Error().stack);
   const noms = nomsProjetsDisponibles();
   // On repart de l'état COURANT, pas d'un map vide (issue #190). Avant, chaque
   // appel reconstruisait le map à partir de zéro : dès qu'un fetch
# ── Zone modifiée : ligne 1432 (12 ligne(s)) dans l'ancienne version → ligne 1432 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1432,12 +1432,22 @@ function formaterBadgeTempsRestant(badge, t) {
     badge.title = 'Le 1er cycle TIMEOUT (' + t.timeout + 's) a été dépassé, mais '
                 + 'le watcher dispose de ' + essais + ' tentatives. Reste ~'
                 + formaterDuree(restant) + ' sur le budget total ; pas encore un échec.';
-  } else {                               // budget total (toutes tentatives) épuisé
-    badge.textContent = '⌛ dépassement +' + formaterDuree(-restant);
+  } else {
+    // Budget total (toutes tentatives) épuisé : décompte figé à zéro (issue
+    // #270), jamais de valeur négative ni de compteur de dépassement qui
+    // grossirait indéfiniment. Sans re-fetch périodique, on ne sait pas si
+    // l'issue est toujours bloquée, retentée ou déjà fermée — un « dépassement
+    // +Xs » qui continue à monter suggérerait un suivi en temps réel qu'on
+    // n'a plus, et un message du type « terminé ? » serait une pure
+    // spéculation. Le badge reste donc affiché, figé, jusqu'au prochain
+    // rafraîchissement manuel (rafraichirResultats).
+    badge.textContent = '⌛ 0s — budget épuisé';
     badge.classList.add('tr-depasse');
     badge.title = 'Budget total épuisé (' + essais + ' tentatives × ' + t.timeout
                 + 's' + (backoff ? ' + backoffs' : '') + ') ; intervention '
-                + 'humaine probable (label needs-human).';
+                + 'humaine probable (label needs-human). Décompte figé à zéro : '
+                + "l'état réel (toujours bloquée, retentée, ou déjà fermée) "
+                + "n'est connu qu'au prochain rafraîchissement manuel.";
   }
 }
 
# ── Zone modifiée : ligne 1457 (7 ligne(s)) dans l'ancienne version → ligne 1467 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1457,7 +1467,7 @@ function majBadgesTempsRestant() {
 
 // Démarre le suivi du temps restant (à l'ouverture de l'onglet Résultats) :
 // fetch initial des débuts/timeouts puis recalcul chaque seconde (client
-// seul). Plus de re-fetch périodique (issue #269) : les données ne sont
+// seul). Plus de re-fetch périodique (issue #270) : les données ne sont
 // ensuite rafraîchies qu'explicitement, via rafraichirResultats().
 function demarrerTempsRestant() {
   chargerTimingIssues();
# ── Zone modifiée : ligne 1798 (7 ligne(s)) dans l'ancienne version → ligne 1808 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1798,7 +1808,7 @@ async function rafraichirResultats() {
   } catch(e) {}
   // 3) Recharge la liste depuis GitHub.
   await chargerListeIssues();
-  // 3bis) Recharge aussi les badges de temps restant (issue #269) : depuis la
+  // 3bis) Recharge aussi les badges de temps restant (issue #270) : depuis la
   // suppression du re-fetch périodique, c'est le SEUL geste qui les remet à
   // jour — sans cet appel, le bouton actualiserait les états d'issues en
   // laissant les badges figés, une incohérence pire que l'ancien comportement.
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index c66b73c..b48ccc2 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 522 (8 ligne(s)) dans l'ancienne version → ligne 522 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -522,8 +522,5 @@
   window.MIMES_IMAGE_ACCEPTES = {{ formats_image.mimes | tojson }};
 </script>
 <script src="{{ url_for('static', filename='js/app.js') }}"></script>
-<script>/* HARNAIS TEMPORAIRE mesure issue #269 — à retirer avant commit */
-setTimeout(function(){ if (typeof basculerOnglet === 'function') basculerOnglet('resultats'); }, 800);
-</script>
 </body>
 </html>
