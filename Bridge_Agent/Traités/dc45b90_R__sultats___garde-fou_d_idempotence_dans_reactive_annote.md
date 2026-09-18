dc45b90

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit dc45b90
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Jul 28 03:14:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Résultats : garde-fou d'idempotence dans reactiverTousLesFiltres() (issue #259)
    
    nomsProjetsDisponibles() ne retourne pas vide au second appel — elle lit
    le <select> global, jamais vidé côté client. Ce n'était donc pas la cause
    du symptôme signalé. Garde-fou ajouté quand même en second rideau : si
    la liste des projets connus est vide, reactiverTousLesFiltres() laisse
    l'état inchangé plutôt que de vider projetsFiltresActifs.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0e7fd68..7bea4b8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,16 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 28 juillet 2026 — issue #259
+
+Ajoute un garde-fou d'idempotence à `reactiverTousLesFiltres()` (bouton « Tous » de l'onglet Résultats, `static/js/app.js`), suite à un signalement de second clic masquant tous les projets (issue #259). **Diagnostic** : la piste envisagée (`nomsProjetsDisponibles()` retournant vide au second appel, faisant écrire un `Set` vide) ne s'est pas confirmée. `nomsProjetsDisponibles()` lit `[...document.getElementById('projet').options]` — le `<select>` global, peuplé une seule fois côté serveur par `lister_projets()` et jamais vidé/reconstruit côté client (seul `ajouterProjetAuSelecteur()` y ajoute une option, sans jamais en retirer) ; il est donc déjà indépendant de l'état d'affichage/filtre de l'onglet Résultats — `appliquerFiltresListe()` ne fait que masquer des LIGNES d'issues (`ligne.style.display`), jamais les options du select, et `localStorage.removeItem` ne touche pas non plus le DOM. Vérifié par exécution directe du fichier réel (`static/js/app.js` chargé tel quel dans un bac à sable `vm` Node, sans modification) : deux appels consécutifs à `reactiverTousLesFiltres()`, partant d'un état partiellement ou totalement désactivé, produisent chacun l'ensemble complet des projets — aucune régression vers un `Set` vide observée sur ce chemin. Seuls trois points du fichier réaffectent `projetsFiltresActifs` (déclaration initiale, `appliquerListeIssues()` via `restaurerFiltresProjets()`, et `reactiverTousLesFiltres()`) ; les deux derniers ont été rejoués sous test sans reproduire le symptôme. Le symptôme décrit (plus aucune issue affichée, récupérable seulement en recliquant chaque projet un par un) correspond en revanche exactement au comportement déjà connu et documenté de `basculerFiltreProjet()` lorsqu'on désactive le dernier projet actif restant (vérifié : le `Set` devient bien vide dans ce cas précis) — plausiblement la manipulation réellement en cause, plutôt qu'un second clic sur « Tous ».
+
+**Solution retenue** : aucune correction de source nécessaire pour `nomsProjetsDisponibles()`, déjà appuyée sur une source stable. Garde-fou ajouté en second rideau dans `reactiverTousLesFiltres()` : si `nomsProjetsDisponibles()` retourne une liste vide (cas normalement inatteignable dans l'onglet Résultats, `chargerListeIssues()` court-circuitant déjà l'absence de projet), la fonction retourne immédiatement sans toucher à `projetsFiltresActifs` — état laissé inchangé plutôt que vidé. Vérifié par test direct (select vidé artificiellement) : l'état actif reste intact après le clic.
+
+**Non modifié, signalé seulement (point 4)** : `basculerFiltreProjet()` désactivant le dernier projet actif produit bien un `Set` vide et un affichage sans aucune issue — confirmé par test. Comportement volontairement laissé tel quel : désactiver explicitement tous les projets un par un est une action délibérée de l'utilisateur, à la différence d'un second clic sur « Tous ».
+
+**Vérifications (point 5)**, par exécution directe du fichier réel dans un bac à sable Node (`vm`) : **rechargement de page** — filtres partiellement désactivés puis persistés en `localStorage`, `appliquerListeIssues()` (chemin de chargement) restaure correctement l'état partiel, puis deux clics consécutifs sur « Tous » réactivent et maintiennent l'ensemble complet ; **reconstruction de la ligne de filtres** — ajout d'un projet au `<select>` puis `appliquerListeIssues()`/`construireBoutonsFiltre()` reconstruits, `nomsProjetsDisponibles()` inclut bien le nouveau projet, deux clics consécutifs sur « Tous » restent corrects et incluent le projet ajouté. `node --check static/js/app.js` → OK.
+
 ## 28 juillet 2026 — issue #258
 
 Corrige deux défauts de `initialiser_git()` livrée par #257 : publication involontaire d'un répertoire préexistant, et absence de timeout sur les appels git (issue #258). **Défaut 1** : `creer_depot()` crée le dépôt GitHub en `--public`, et `initialiser_git()` fait `git add -A` puis pousse automatiquement — sans risque sur un répertoire neuf (cas nominal), mais si `REP_TRAVAIL` désigne un dossier **existant et non versionné** (cas explicitement couvert par le script, qui gère « création ET installation »), l'intégralité de son contenu était publiée sans confirmation ni aperçu ; le `.gitignore` minimal (`venv/`, `__pycache__/`, `*.pyc`, `*.log`, `.env`) ne protège que quelques cas. **Défaut 2** : `_git()` appelait `subprocess.run` sans `timeout=`, alors que le reste du code en pose un partout ailleurs (30s pour `commenter_issue`, 120s pour le push des pièces jointes) — un `git push` qui pend sur un réseau instable bloquait la requête Flask indéfiniment.
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 8274be0..b2f83dd 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 875 (7 ligne(s)) dans l'ancienne version → ligne 875 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -875,7 +875,16 @@ function basculerFiltreProjet(nom) {
 // Remet tous les projets à l'état actif ET efface la mémoire localStorage
 // (retour au comportement par défaut : tous actifs au prochain chargement).
 function reactiverTousLesFiltres() {
-  projetsFiltresActifs = new Set(nomsProjetsDisponibles());
+  const noms = nomsProjetsDisponibles();
+  // Garde-fou (issue #259) : nomsProjetsDisponibles() est déjà une source
+  // stable (le <select> global, indépendant de l'état d'affichage/filtre de
+  // l'onglet Résultats), donc ce cas ne devrait normalement jamais se
+  // produire ici. On le blinde quand même : un ensemble vide masquerait
+  // TOUTE la liste, un état sans usage dont on ne sort qu'en recliquant
+  // chaque projet un par un. En cas de liste vide, on laisse l'état inchangé
+  // plutôt que de tout masquer.
+  if (!noms.length) return;
+  projetsFiltresActifs = new Set(noms);
   try { localStorage.removeItem(CLE_FILTRES_RESULTATS); } catch(e) {}
   majClassesBoutonsFiltre();
   appliquerFiltresListe();
