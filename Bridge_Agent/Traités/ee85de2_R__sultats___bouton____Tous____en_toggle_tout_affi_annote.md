ee85de2

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ee85de2
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Jul 28 03:53:00 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Résultats : bouton « Tous » en toggle tout afficher / tout masquer (issue #262)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index edb0cd5..8434bca 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,24 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 28 juillet 2026 — issue #262
+
+Transforme le bouton « Tous » de l'onglet Résultats en véritable interrupteur à deux états, après que #259 a établi que le comportement inconditionnel qu'il évoluait n'était pas un bug : le besoin réel est un basculement rapide entre « tout afficher » et « tout masquer », le bouton « Tous » et la case de marquage étant les deux gestes les plus fréquents de cet onglet (le détail d'une issue y est presque jamais consulté, cf. #261).
+
+**Nouvelle fonction** : `reactiverTousLesFiltres()` renommée `basculerTousLesFiltres()` (`static/js/app.js`), commentaire d'en-tête réécrit pour décrire le toggle plutôt que la remise à zéro inconditionnelle. Règle : `noms.every(nom => projetsFiltresActifs.has(nom))` vrai (tout affiché) → passe à l'ensemble vide (tout masqué) ; faux (état partiel OU tout masqué) → passe à l'ensemble complet (tout affiché). Un seul état bascule vers « tout masqué », tout le reste revient à « tout affiché », conformément à l'énoncé.
+
+**Garde-fou de #259** : supprimé purement et simplement (`if (!noms.length) return;`), sans réécriture ni remplacement — l'ensemble vide qu'il interdisait est désormais l'état « tout masqué », volontaire et légitime, exactement ce que la fonction doit pouvoir produire. Le garder aurait bloqué le nouveau comportement dans le cas `noms` vide (aucun projet configuré), un cas de toute façon sans conséquence réelle (aucun bouton projet à masquer).
+
+**Persistance `localStorage`** (`CLE_FILTRES_RESULTATS`) : asymétrique, à dessein. Vers « tout affiché » → `localStorage.removeItem(...)`, comme avant #262 (retour au défaut — tout actif — au prochain chargement). Vers « tout masqué » → `sauvegarderFiltresProjets(noms)`, la même fonction qu'utilise déjà `basculerFiltreProjet()`, qui écrit `{nom: false, ...}` pour chaque projet : sans cette persistance explicite, un rechargement de page aurait silencieusement annulé le masquage volontaire (retour à tout affiché par défaut, cf. `restaurerFiltresProjets()`).
+
+**État visible sur le bouton** : `majClassesBoutonsFiltre()` (qui ne traitait jusqu'ici que les boutons `[data-projet]`) traite désormais aussi `.filtre-projet.tous` — classe `inactif` (grisée, CSS déjà existante) et `title` reflétant l'action du **prochain** clic (« Tout masquer » quand tout est affiché, « Tout afficher » sinon), pas l'état courant. Effet de bord nécessaire : dans `construireBoutonsFiltre()`, l'appel à `majClassesBoutonsFiltre()` se faisait juste après la boucle des boutons projet, donc **avant** la création du bouton « Tous » — déplacé après sa création (juste avant le bouton rafraîchir), sinon la mise à jour de son état visuel n'aurait rien trouvé dans le DOM à la construction initiale ni après reconstruction de la ligne de filtres.
+
+**Point 5 (cas limite tout masqué)** : `appliquerFiltresListe()` masque bien toutes les lignes (`projetVisible` faux pour tout projet quand l'ensemble est vide), `selectionnerPremiereVisible()` ne trouve aucune ligne visible et affiche proprement « Aucune issue à afficher », sans erreur. Défaut trouvé en vérifiant ce chemin : la ligne précédemment sélectionnée gardait sa classe `.selectionnee` (invisible mais toujours marquée) même masquée — au retour à « tout afficher », cette ligne redevenait visible et le code de resynchronisation (`if (!sel || sel.style.display === 'none')`), la trouvant déjà « sélectionnée » et visible, sautait la resélection : la zone de détail restait bloquée sur le message « Aucune issue à afficher » malgré une ligne visiblement en surbrillance. Ce chemin était déjà latent via `basculerFiltreProjet()` (désactiver le dernier projet actif un par un y menait aussi) mais quasi inatteignable en pratique ; le nouveau toggle le rend trivial (un clic). Corrigé dans `selectionnerPremiereVisible()` : la branche « aucune ligne visible » retire désormais aussi la classe `.selectionnee` de toute ligne qui la porterait encore et réinitialise `projetCourant`/`numeroCourant` (miroir du comportement déjà présent dans `selectionnerLigne()` pour son propre cas « aucune issue »). Effet : au retour à « tout afficher », plus aucune ligne ne porte `.selectionnee`, la resynchronisation se déclenche normalement et sélectionne proprement la première ligne visible.
+
+**Point 6 (rechargement / reconstruction)** : vérifié par lecture du chemin d'appel — `appliquerListeIssues()` recalcule toujours `projetsFiltresActifs = restaurerFiltresProjets(noms)` avant `construireBoutonsFiltre(noms)`, aussi bien au chargement initial qu'à toute reconstruction (ajout de projet). Après un masquage total persisté, un rechargement restaure bien un ensemble vide (chaque projet marqué `false` dans l'état sauvegardé) : le bouton affiche correctement l'état « inactif »/« Tout afficher » dès la construction, premier clic correct. Ajout d'un nouveau projet pendant un masquage total : ce projet, absent de l'état `localStorage` sauvegardé, est actif par défaut (`etat[nom] !== false` vrai pour une clé absente) — l'ensemble devient donc partiel plutôt que resté totalement vide ; le bouton reflète alors correctement « Tout afficher » (état partiel), et un premier clic affiche bien tout, conformément à la règle générale (tout état partiel bascule vers tout affiché).
+
+**Vérification** : `node --check static/js/app.js` → OK. Vérifications des points 5 et 6 faites par relecture attentive du chemin d'exécution réel du fichier (accès à un bac à sable DOM complet non disponible dans cette session — le fichier charge de nombreux `document.getElementById(...).addEventListener` en haut niveau, un stub minimal aurait été trompeur) ; le raisonnement s'appuie sur le code effectivement livré, ligne par ligne, pas sur une hypothèse.
+
 ## 28 juillet 2026 — issue #261
 
 Dans l'onglet Résultats, `afficherIssue()` (`static/js/app.js`) lançait un `fetch('/issue/<projet>/<numero>')` systématique — y compris pour un clic simple réflexe (sélectionner une ligne sans vouloir lire son détail) et pour la sélection automatique (`selectionnerPremiereVisible()`, déclenchée à l'ouverture de l'onglet, à chaque changement de filtre projet, après « Tous » et après chaque rafraîchissement de liste). Le TTL du cache `localStorage` (issue #52) ne dispensait que l'affichage immédiat : le fetch d'arrière-plan partait quand même. Dans l'usage réel, ce détail n'est presque jamais consulté ; chaque clic réflexe et chaque changement de filtre coûtaient donc un aller-retour GitHub inutile — autant d'occasions d'erreur/lenteur sur un réseau instable (issue #261).
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 4c3fdb7..afe5362 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 832 (7 ligne(s)) dans l'ancienne version → ligne 832 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -832,7 +832,6 @@ function construireBoutonsFiltre(noms) {
       + couleurProjetResultats(nom) + '"></span>' + escapeHtml(nom);
     zone.appendChild(btn);
   }
-  majClassesBoutonsFiltre();
   // Toggle « 👷 Ouvriers » (issue #86), après les boutons projet. Inactif par
   // défaut : les issues de type ouvrier restent masquées jusqu'à un clic.
   const ouv = document.createElement('span');
# ── Zone modifiée : ligne 846 (8 ligne(s)) dans l'ancienne version → ligne 845 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -846,8 +845,12 @@ function construireBoutonsFiltre(noms) {
   const tous = document.createElement('span');
   tous.className = 'filtre-projet tous';
   tous.textContent = 'Tous';
-  tous.onclick = reactiverTousLesFiltres;
+  tous.onclick = basculerTousLesFiltres;
   zone.appendChild(tous);
+  // Appelé ici, une fois TOUS les boutons créés (dont « Tous ») : sinon la
+  // mise à jour de son état visuel (issue #262) n'aurait rien à trouver dans
+  // le DOM, ce bouton étant créé après les boutons projet.
+  majClassesBoutonsFiltre();
   // Bouton rafraîchir déplacé ici, juste après « Tous » (issue #57). Recréé à
   // chaque reconstruction de la ligne car zone.innerHTML est vidé au début.
   const rafr = document.createElement('button');
# ── Zone modifiée : ligne 872 (20 ligne(s)) dans l'ancienne version → ligne 875 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -872,20 +875,28 @@ function basculerFiltreProjet(nom) {
   if (!sel || sel.style.display === 'none') selectionnerPremiereVisible();
 }
 
-// Remet tous les projets à l'état actif ET efface la mémoire localStorage
-// (retour au comportement par défaut : tous actifs au prochain chargement).
-function reactiverTousLesFiltres() {
+// Bascule « Tous » entre deux états (issue #262) : un vrai toggle, pas une
+// simple remise à zéro. Si au moins un projet est masqué → tout afficher ;
+// si tout est déjà affiché → tout masquer. Seul l'état « tout affiché »
+// bascule vers « tout masqué » ; tout état partiel revient à « tout affiché ».
+// L'ensemble vide (tout masqué) est un état légitime et volontaire — l'ancien
+// garde-fou de l'issue #259, qui l'interdisait, a été retiré : il contredisait
+// désormais l'intention même de la fonction.
+// Persistance localStorage asymétrique, à dessein : « tout affiché » efface
+// la mémoire (retour au défaut au prochain chargement, comme avant #262) ;
+// « tout masqué » est au contraire persisté via sauvegarderFiltresProjets
+// (comme basculerFiltreProjet), sans quoi un rechargement de page annulerait
+// silencieusement le masquage volontaire de l'utilisateur.
+function basculerTousLesFiltres() {
   const noms = nomsProjetsDisponibles();
-  // Garde-fou (issue #259) : nomsProjetsDisponibles() est déjà une source
-  // stable (le <select> global, indépendant de l'état d'affichage/filtre de
-  // l'onglet Résultats), donc ce cas ne devrait normalement jamais se
-  // produire ici. On le blinde quand même : un ensemble vide masquerait
-  // TOUTE la liste, un état sans usage dont on ne sort qu'en recliquant
-  // chaque projet un par un. En cas de liste vide, on laisse l'état inchangé
-  // plutôt que de tout masquer.
-  if (!noms.length) return;
-  projetsFiltresActifs = new Set(noms);
-  try { localStorage.removeItem(CLE_FILTRES_RESULTATS); } catch(e) {}
+  const tousAffiches = noms.every(nom => projetsFiltresActifs.has(nom));
+  if (tousAffiches) {
+    projetsFiltresActifs = new Set();
+    sauvegarderFiltresProjets(noms);
+  } else {
+    projetsFiltresActifs = new Set(noms);
+    try { localStorage.removeItem(CLE_FILTRES_RESULTATS); } catch(e) {}
+  }
   majClassesBoutonsFiltre();
   appliquerFiltresListe();
   const sel = document.querySelector('#liste-issues .ligne-issue.selectionnee');
# ── Zone modifiée : ligne 903 (6 ligne(s)) dans l'ancienne version → ligne 914 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -903,6 +914,15 @@ function majClassesBoutonsFiltre() {
       btn.style.color       = actif ? btn.dataset.couleur : '';
       btn.style.borderColor = actif ? btn.dataset.couleur : '';
     });
+  // Bouton « Tous » (issue #262) : reflète l'action du PROCHAIN clic, pas
+  // l'état courant — grisé (.inactif) tant qu'au moins un projet est masqué,
+  // ce qui correspond à « le prochain clic affichera tout ».
+  const boutonTous = document.querySelector('#filtres-projets .filtre-projet.tous');
+  if (boutonTous) {
+    const tousAffiches = nomsProjetsDisponibles().every(nom => projetsFiltresActifs.has(nom));
+    boutonTous.classList.toggle('inactif', !tousAffiches);
+    boutonTous.title = tousAffiches ? 'Tout masquer' : 'Tout afficher';
+  }
 }
 
 // Convertit une couleur hexadécimale #RRGGBB en rgba() avec l'alpha demandé.
# ── Zone modifiée : ligne 1447 (6 ligne(s)) dans l'ancienne version → ligne 1467 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1447,6 +1467,15 @@ function selectionnerPremiereVisible() {
   if (premiere) {
     selectionnerLigne(premiere.dataset.projet, premiere.dataset.numero);
   } else {
+    // Aucune ligne visible (ex. issue #262 : toggle « Tous » à l'état tout
+    // masqué) : on retire aussi la classe .selectionnee de la ligne masquée,
+    // sinon elle reste marquée sélectionnée en coulisse — un futur retour à
+    // l'affichage la retrouverait "déjà sélectionnée" et sauterait la
+    // resynchronisation (zone de détail restée sur ce message).
+    document.querySelectorAll('#liste-issues .ligne-issue.selectionnee')
+      .forEach(ligne => ligne.classList.remove('selectionnee'));
+    projetCourant = null;
+    numeroCourant = null;
     document.getElementById('zone-issue').innerHTML =
       '<div class="issue-vide">Aucune issue à afficher</div>';
   }
