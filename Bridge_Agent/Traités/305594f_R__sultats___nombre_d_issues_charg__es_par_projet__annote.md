305594f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 305594f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 06:08:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Résultats : nombre d'issues chargées par projet rendu configurable (issue #271)
    
    Backend : issues_liste() accepte ?limite=N (entier borné 1-50, défaut 30
    inchangé si absent/invalide). Frontend : champ numérique persisté en
    localStorage (défaut 5), transmis à chargerListeIssues() sans déclencher
    de rechargement automatique (cohérent avec #270), cache liste invalidé au
    changement de valeur. Quota adaptatif d'appliquerFiltresListe() (#136)
    non touché.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a010a9d..eac7255 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,10 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 29 juillet 2026 — issue #271
+
+Résultats : nombre d'issues chargées par projet rendu configurable (issue #271), pour accélérer le bouton rafraîchir et réduire le volume rapatrié — jusqu'ici `issues_liste()` (`app/issues.py`) appelait `gh issue list --limit 30` en dur, **par projet** (jusqu'à 240 issues téléchargées avec 8 projets), alors que l'affichage était déjà plafonné par le quota adaptatif d'`appliquerFiltresListe()` (issue #136). **Backend** : `issues_liste()` accepte désormais un paramètre de requête optionnel `limite` (`_limite_issues_requete()`), entier borné entre 1 et 50 — toute valeur absente, non entière ou hors bornes retombe sur 30 (`LIMITE_ISSUES_DEFAUT`), comportement strictement inchangé pour tout appelant qui ne passe pas le paramètre (vérifié : `?limite=5`→5, `?limite=999`→50, `?limite=0`→1, `?limite=abc`→30, absent→30, via `test_client()` bout-en-bout contre `gh` réel). **Frontend** (`static/js/app.js`, `static/css/style.css`) : champ numérique `#limite-issues-projet` ajouté dans la ligne de filtres, juste avant le bouton rafraîchir, `title` explicite (« Nombre d'issues chargées par projet (pas un total). Ex. 5 → 5 issues par projet affiché. ») pour éviter la confusion nombre-par-projet / total — un total obligerait à diviser par le nombre de projets actifs, qui change à chaque clic sur un filtre. Persisté dans `localStorage` (`bridge_limite_issues_projet`), défaut **5** (besoin réel dans 70% des cas d'après l'issue, et non 30 : l'ancienne valeur reste atteignable en remontant le champ). `chargerListeIssues()` transmet la valeur courante (`limiteIssuesProjet()`) à chaque appel `/issues-liste/<projet>`. Changer la valeur du champ ne déclenche **aucun** rechargement automatique (cohérent avec la décision de #270) : seul le bouton rafraîchir applique la nouvelle limite ; en revanche `changerLimiteIssuesProjet()` invalide immédiatement `CLE_CACHE_ISSUES`, sans quoi un cache constitué à l'ancienne limite continuerait d'afficher une profondeur d'historique incohérente avec le réglage visible. Quota adaptatif de #136 (`appliquerFiltresListe()`) **non touché** : les deux mécanismes sont complémentaires (celui-ci plafonne ce qui est TÉLÉCHARGÉ, celui-là ce qui est MONTRÉ) ; commentaire ajouté pour expliciter que si la limite de téléchargement est plus basse que le quota d'affichage, ce dernier n'a simplement rien de plus à masquer — sans conséquence. **Mesure du coût GraphQL** (méthode #263 : deux `gh api rate_limit` encadrant un appel isolé de `gh issue list --json ...`, 3 répétitions, delta minimal retenu) sur `--limit 30/10/5` : les trois deltas minimaux mesurés valent **1 point** (identique au coût unitaire déjà mesuré par #263 pour cet appel) — résultat inattendu : le coût GraphQL par appel ne varie PAS avec `--limit` dans la plage testée, contrairement à l'intuition de l'issue ; le gain réel n'est donc pas une réduction du quota GraphQL (le nombre d'appels — un par projet — reste le facteur dominant, inchangé par cette issue) mais une réduction du volume de données transférées/parsées (23 113 → 3 445 octets entre `--limit 30` et `--limit 5` sur ce dépôt, soit -85%), donc du temps de traitement `gh`/JS et du risque de timeout sur un historique profond. Détail complet et tableau des mesures dans le rapport de clôture de l'issue #271 (non dupliqué ici). Route `/issues-liste/<projet>` non documentée dans `BRIDGE_AGENT_DOC.md` (aucune section ne la décrit) : aucune mise à jour de ce fichier, pied de page non glissé (condition de #10 non remplie — cette issue ne modifie pas `BRIDGE_AGENT_DOC.md`).
+
 ## 29 juillet 2026 — issue #270
 
 Badges de temps restant : suppression du rafraîchissement périodique (issue #270, remplace #269 fermée sans correctif — mesure infaisable dans le TIMEOUT, décisions non tranchées). `intervalFetchTiming` (re-fetch de `/issues-en-attente/<projet>` toutes les 15s pour tous les projets configurés, ~3840 pts/h mesurés par #263, premier poste de consommation du quota GraphQL) supprimé ; `intervalTempsRestant` conservé (décompte purement client, recalcul chaque seconde, sans coût réseau). `chargerTimingIssues()` n'est plus appelée qu'au chargement initial de l'onglet Résultats et depuis `rafraichirResultats()` (bouton rafraîchir), pour qu'un seul geste mette à jour liste ET badges. Décision sur le décompte (point 3 de #269, laissé en suspens) : une fois le budget total épuisé, le badge se fige à « ⌛ 0s — budget épuisé » au lieu d'un compteur de dépassement qui grossissait indéfiniment (`⌛ dépassement +Xs`) — jamais de valeur négative, jamais de message spéculatif du type « terminé ? » (l'état réel n'est pas connu sans re-fetch), badge visible jusqu'au prochain rafraîchissement manuel. Retrait de deux résidus d'une tentative précédente non commitée proprement : un `console.error('[DEBUG-269-TRACE]', …)` dans `chargerTimingIssues()` et un bloc `<script>` de harnais temporaire dans `templates/index.html` (auto-bascule vers l'onglet Résultats après 800ms) qui portait lui-même la mention « à retirer avant commit ». Second appelant de `/issues-en-attente` (~ligne 2735, garde-fou avant l'envoi d'une nouvelle issue) : hors périmètre de cette issue, laissé strictement tel quel. Aucune mesure de gain (hors périmètre, cf. #269 : nécessite un navigateur ouvert 5+ minutes, invérifiable depuis l'agent) — à faire par Alain avec `scripts/mesurer_api.py`.
# (diff du fichier suivant)
diff --git a/app/issues.py b/app/issues.py
# (index — ignorable)
index 9f88016..bfeee51 100644
# (avant — fichier suivant)
--- a/app/issues.py
# (après — fichier suivant)
+++ b/app/issues.py
# ── Zone modifiée : ligne 578 (17 ligne(s)) dans l'ancienne version → ligne 578 (41 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -578,17 +578,41 @@ def _nettoyer_fichier(chemin: Path) -> None:
         pass
 
 
+LIMITE_ISSUES_DEFAUT = 30
+LIMITE_ISSUES_MIN = 1
+LIMITE_ISSUES_MAX = 50
+
+
+def _limite_issues_requete():
+    """Lit le paramètre de requête `limite` (issue #271) : entier borné entre
+    LIMITE_ISSUES_MIN et LIMITE_ISSUES_MAX. Toute valeur absente ou invalide
+    (non fournie, non entière, hors bornes) retombe sur LIMITE_ISSUES_DEFAUT —
+    comportement strictement inchangé pour tout appelant qui ne passe pas ce
+    paramètre."""
+    brut = request.args.get("limite")
+    if brut is None:
+        return LIMITE_ISSUES_DEFAUT
+    try:
+        valeur = int(brut)
+    except (TypeError, ValueError):
+        return LIMITE_ISSUES_DEFAUT
+    return max(LIMITE_ISSUES_MIN, min(LIMITE_ISSUES_MAX, valeur))
+
+
 def issues_liste(nom_projet):
-    """Retourne les 30 dernières issues (tous états) du projet via gh."""
+    """Retourne les dernières issues (tous états) du projet via gh, jusqu'à
+    LIMITE_ISSUES_DEFAUT (30) sauf si le paramètre `limite` en fournit une
+    autre (issue #271)."""
     cfg = projet_par_nom(nom_projet)
     if not cfg:
         return jsonify(erreur="Projet introuvable."), 404
+    limite = _limite_issues_requete()
     try:
         res = subprocess.run(
             ["gh", "issue", "list",
              "--repo",  cfg.depot,
              "--state", "all",
-             "--limit", "30",
+             "--limit", str(limite),
              "--json",  "number,title,state,labels,createdAt"],
             capture_output=True, text=True, timeout=30
         )
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index 88184ac..c71a9d6 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 123 (6 ligne(s)) dans l'ancienne version → ligne 123 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -123,6 +123,11 @@ button.danger:hover{background:#f8d7da}
    au-dessus du seuil WCAG AA (4.5:1). */
 .filtre-projet.inactif{background:#f2f2f0;color:#5a5a5a}
 .filtre-projet.tous{border-style:dashed;color:#555}
+/* Champ « limite par projet » (issue #271), juste avant le bouton rafraîchir. */
+.limite-issues-label{display:inline-flex;align-items:center;gap:5px;
+  font-size:12px;color:#555;user-select:none}
+.limite-issues-projet{width:44px;font-size:12px;padding:3px 5px;
+  border:1px solid #ccc;border-radius:6px;background:#fff;color:#333}
 /* Liste HTML cliquable des issues (remplace l'ancienne combobox #select-issue).
    Une ligne par issue, coloriée à la couleur de son projet — contrôle total du
    rendu, contrairement à <option> que Firefox refuse de colorier. Les couleurs
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 83de482..7002386 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 685 (6 ligne(s)) dans l'ancienne version → ligne 685 (45 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -685,6 +685,45 @@ let projetsFiltresActifs = new Set();
 // instantané depuis le cache, rafraîchi ensuite par un fetch d'arrière-plan.
 const CLE_CACHE_ISSUES = 'bridge_cache_issues';
 
+// ── Limite d'issues chargées PAR PROJET (issue #271) ──────────────────────
+// Transmise en paramètre de requête à /issues-liste/<projet> : c'est ce qui
+// est TÉLÉCHARGÉ depuis GitHub, pas ce qui est affiché — le quota adaptatif
+// d'appliquerFiltresListe() (issue #136) reste seul responsable de ce qui est
+// MONTRÉ une fois la liste en mémoire. Un total serait ambigu (il faudrait le
+// diviser par le nombre de projets actifs, qui change à chaque clic sur un
+// filtre) ; exprimer un nombre par projet garde le même sens en toute
+// circonstance. Défaut 5 (besoin courant réel dans 70% des cas d'après
+// l'issue) et non 30 : l'ancienne valeur reste atteignable en remontant le
+// champ. Changer la valeur ne déclenche PAS de rechargement automatique
+// (cohérent avec #270) : seul le bouton rafraîchir applique la nouvelle
+// limite. Le cache liste est néanmoins invalidé tout de suite (point 6),
+// sinon un cache constitué à une profondeur différente resterait affiché
+// avec une profondeur d'historique qui ne correspond plus au réglage visible.
+const CLE_LIMITE_ISSUES = 'bridge_limite_issues_projet';
+const LIMITE_ISSUES_DEFAUT = 5;
+const LIMITE_ISSUES_MIN = 1;
+const LIMITE_ISSUES_MAX = 50;
+
+function limiteIssuesProjet() {
+  let brut = null;
+  try { brut = localStorage.getItem(CLE_LIMITE_ISSUES); } catch(e) {}
+  const n = parseInt(brut, 10);
+  return Number.isFinite(n) && n >= LIMITE_ISSUES_MIN && n <= LIMITE_ISSUES_MAX
+    ? n : LIMITE_ISSUES_DEFAUT;
+}
+
+// Applique une nouvelle valeur saisie : bornée, persistée, cache liste
+// invalidé — mais AUCUN rechargement déclenché ici (voir commentaire ci-dessus).
+function changerLimiteIssuesProjet(valeur) {
+  const n = parseInt(valeur, 10);
+  const bornee = Number.isFinite(n)
+    ? Math.min(LIMITE_ISSUES_MAX, Math.max(LIMITE_ISSUES_MIN, n))
+    : LIMITE_ISSUES_DEFAUT;
+  try { localStorage.setItem(CLE_LIMITE_ISSUES, String(bornee)); } catch(e) {}
+  try { localStorage.removeItem(CLE_CACHE_ISSUES); } catch(e) {}
+  return bornee;
+}
+
 // Affiche/masque l'indicateur discret « Mise à jour… » sous la liste.
 function majIndicateurListe(actif) {
   const el = document.getElementById('maj-indicateur');
# ── Zone modifiée : ligne 718 (19 ligne(s)) dans l'ancienne version → ligne 757 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -718,19 +757,23 @@ async function chargerListeIssues() {
     zone.innerHTML = '<div class="issue-vide">Chargement…</div>';
   }
 
-  // 2) Fetch d'arrière-plan des issues de chaque projet (jusqu'à 30 côté
-  //    backend). Le nombre réellement affiché par projet est ensuite plafonné
+  // 2) Fetch d'arrière-plan des issues de chaque projet (jusqu'à la limite
+  //    par projet réglée par l'utilisateur côté backend, issue #271 — 5 par
+  //    défaut). Le nombre réellement affiché par projet est ensuite plafonné
   //    par un quota adaptatif dans appliquerFiltresListe() (issue #136), selon
   //    le nombre de projets actifs dans le filtre — plus de troncature ici.
+  const limite = limiteIssuesProjet();
   majIndicateurListe(true);
   try {
     const listes = await Promise.all(noms.map(async nom => {
       try {
-        const rep = await fetch('/issues-liste/' + encodeURIComponent(nom));
+        const rep = await fetch('/issues-liste/' + encodeURIComponent(nom)
+          + '?limite=' + encodeURIComponent(limite));
         const liste = await rep.json();
         if (!Array.isArray(liste)) return [];
-        // Toute la liste reçue (déjà plafonnée à 30 côté backend), triée par
-        // date de création décroissante (plus récentes en premier).
+        // Toute la liste reçue (déjà plafonnée côté backend à la limite par
+        // projet), triée par date de création décroissante (plus récentes en
+        // premier).
         return liste
           .slice()
           .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
# ── Zone modifiée : ligne 851 (6 ligne(s)) dans l'ancienne version → ligne 894 (32 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -851,6 +894,32 @@ function construireBoutonsFiltre(noms) {
   // mise à jour de son état visuel (issue #262) n'aurait rien à trouver dans
   // le DOM, ce bouton étant créé après les boutons projet.
   majClassesBoutonsFiltre();
+  // Champ « limite par projet » (issue #271), juste avant le bouton
+  // rafraîchir. Recréé à chaque reconstruction de la ligne comme les autres
+  // contrôles ci-dessus ; sa valeur est restaurée depuis localStorage à
+  // chaque fois. Le libellé et le title précisent explicitement qu'il s'agit
+  // d'un nombre PAR PROJET (pas un total) et que la saisie seule ne recharge
+  // rien — cohérent avec la décision de #270 : seul le bouton ↻ recharge.
+  const limiteLabel = document.createElement('label');
+  limiteLabel.className = 'limite-issues-label';
+  limiteLabel.title = 'Nombre d\'issues chargées par projet (pas un total). '
+    + 'Ex. 5 → 5 issues par projet affiché. La saisie seule ne recharge '
+    + 'rien : cliquez sur ↻ pour appliquer.';
+  limiteLabel.textContent = 'par projet :';
+  const limiteInput = document.createElement('input');
+  limiteInput.type = 'number';
+  limiteInput.id = 'limite-issues-projet';
+  limiteInput.className = 'limite-issues-projet';
+  limiteInput.min = String(LIMITE_ISSUES_MIN);
+  limiteInput.max = String(LIMITE_ISSUES_MAX);
+  limiteInput.step = '1';
+  limiteInput.value = String(limiteIssuesProjet());
+  limiteInput.title = limiteLabel.title;
+  limiteInput.onchange = () => {
+    limiteInput.value = String(changerLimiteIssuesProjet(limiteInput.value));
+  };
+  limiteLabel.appendChild(limiteInput);
+  zone.appendChild(limiteLabel);
   // Bouton rafraîchir déplacé ici, juste après « Tous » (issue #57). Recréé à
   // chaque reconstruction de la ligne car zone.innerHTML est vidé au début.
   const rafr = document.createElement('button');
# ── Zone modifiée : ligne 1212 (7 ligne(s)) dans l'ancienne version → ligne 1281 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1212,7 +1281,12 @@ function finRedimTitre() {
 function appliquerFiltresListe() {
   // Quota adaptatif par projet (issue #136) : au lieu d'un plafond fixe, le
   // nombre d'issues affichées par projet dépend du nombre de projets actifs
-  // dans le filtre. 1 projet → 30 ; 2 → 15 ; 3 → 10 ; 4 → 7 ; etc.
+  // dans le filtre. 1 projet → 30 ; 2 → 15 ; 3 → 10 ; 4 → 7 ; etc. Ce calcul
+  // reste basé sur 30 (délibérément non touché par #271) : il plafonne ce qui
+  // est MONTRÉ, indépendamment de limiteIssuesProjet() qui plafonne ce qui est
+  // TÉLÉCHARGÉ. Si la limite de téléchargement est plus basse que ce quota
+  // d'affichage, ce dernier n'a simplement rien de plus à masquer — sans
+  // conséquence, les deux mécanismes ne se contredisent pas.
   const nActifs = projetsFiltresActifs.size;
   const quota   = nActifs > 0 ? Math.max(1, Math.floor(30 / nActifs)) : 0;
 
