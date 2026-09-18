db48fbd

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit db48fbd
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 14:12:00 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #321 : champ de recherche par titre dans l'onglet Résultats
    
    Recherche par titre (state all, insensible casse+accents) ratissant les
    projets sélectionnés avec sa propre portée (défaut 15/projet, bornée à
    LIMITE_ISSUES_MAX), indépendante de la limite d'affichage de l'onglet.
    Fenêtre de résultats séparée réutilisant les badges Réponse/Diff/All et
    afficherIssue existants, zone de détail autonome permettant d'enchaîner
    plusieurs corps. Retrait de l'entrée backlog #317 dans TACHES.md,
    désormais implémentée.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3687802..0109ed8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (53 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,53 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #321
+
+Champ de recherche par TITRE dans l'onglet Résultats de `new_issue.py`,
+répondant au backlog ouvert par #317 suite au doublon #315/#316 — sous
+une forme différente de l'idée initiale (titre ET corps) : décision de
+#321 de rester sur le titre seul, plus rapide et suffisant pour
+retrouver un sujet déjà traité. Entrée backlog correspondante retirée
+de `TACHES.md`.
+
+- `app/issues.py` : nouvelle route `recherche_issues` (une par projet,
+  comme `issues_liste`) — `gh issue list --state all --limit <portée>`
+  (state `all` : on cherche justement une issue déjà fermée/done),
+  `--limit` réutilisant `_limite_issues_requete`/`LIMITE_ISSUES_MIN`/
+  `LIMITE_ISSUES_MAX` sans dupliquer de borne. Filtrage sur le titre
+  uniquement, insensible casse+accents via `_normaliser_recherche`
+  (NFKD + suppression des diacritiques + casefold). Même gestion
+  d'erreur (timeout/gh introuvable/returncode) qu'`issues_liste`.
+- `app/__init__.py` : route `/recherche-issues/<nom_projet>`.
+- `static/js/app.js` : champ texte + champ « portée » (défaut 15/projet,
+  borné à `LIMITE_ISSUES_MAX`, réglage DISTINCT de la limite d'affichage
+  de l'onglet) dans la barre de contrôles, déclenchement au clic (ou
+  Entrée) uniquement — jamais à la frappe, cohérent avec #270. La
+  recherche porte sur les projets actuellement sélectionnés dans les
+  filtres (un appel `gh` par projet, portée non cumulative), ratisse
+  toute la portée sans s'arrêter au premier match, respecte le filtre
+  « 👷 Ouvriers », et agrège les échecs par projet sans annuler les
+  autres. `construireLigneIssueDOM` extrait de `rendreListeIssues` pour
+  être partagée avec la nouvelle fenêtre de résultats, qui réutilise
+  telles quelles `copierReponseDepuisBadge`/`copierDiffDepuisBadge`/
+  `copierToutEtDiffDepuisBadge` (badges ✅/Diff/All) et une nouvelle
+  `afficherIssueRecherche` (double-clic) chargeant dans sa PROPRE zone
+  de détail (`#zone-issue-recherche`), autonome de celle de l'onglet —
+  plusieurs corps peuvent s'enchaîner sans se fermer mutuellement.
+  `demarrerRedimTitre`/`finRedimTitre` adaptés pour redimensionner la
+  colonne titre de la fenêtre indépendamment de celle de l'onglet, sans
+  persister ce redimensionnement en localStorage.
+- `templates/index.html` : barre de recherche statique dans l'onglet
+  Résultats + modal `#modal-recherche-titre` (liste + zone de détail
+  propres, bouton Fermer).
+- `static/css/style.css` : styles de la barre et du modal.
+- `TACHES.md` : retrait de l'entrée de backlog « Champ de recherche
+  texte dans l'onglet Résultats » (#317), désormais implémentée.
+
+La limite d'affichage par défaut de l'onglet (`LIMITE_ISSUES_DEFAUT`,
+30) reste inchangée — le 15 par défaut ne concerne que la portée de
+recherche, un réglage distinct.
+
 ## 2 août 2026 — issue #319
 
 `TACHES.md` : retrait de l'entrée de backlog « Garde-fou technique sur
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index 54996a2..e0da671 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 184 (27 ligne(s)) dans l'ancienne version → ligne 184 (3 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -184,27 +184,3 @@ soin, pas seulement en confiance sur la consigne donnée à CCL.
 
 **Statut** : idée en attente, pas de développement lancé. Reçue via rapport
 d'audit Scrabble le 24/07/2026.
-
----
-
-## Champ de recherche texte dans l'onglet Résultats de new_issue.py
-
-**Contexte** : le 02/08/2026, une issue a été envoyée deux fois par
-inadvertance (#315 et #316, doublon), faute de moyen rapide de
-vérifier si une issue similaire avait déjà été traitée. Une alerte
-automatique basée sur la similarité de titre a été envisagée mais
-écartée : les templates d'issues récurrentes (ex. « Rebuild
-exécutable/installeur Scrabble », revenu une dizaine de fois pour des
-raisons différentes) produiraient trop de faux positifs, menant à
-ignorer l'alerte.
-
-**Idée** : ajouter un champ de recherche texte dans l'onglet Résultats
-de `new_issue.py`, filtrant sur titre ET corps des issues déjà
-envoyées (pas seulement le titre, pour retrouver une issue même si son
-libellé a légèrement varié d'une version à l'autre). Objectif :
-vérifier rapidement, en cas de doute, si un sujet a déjà été traité
-avant d'envoyer une nouvelle issue — sans alerte intrusive ni faux
-positif automatique.
-
-**Statut** : idée en attente, pas de développement lancé. Reçue le
-02/08/2026 (issue #317), suite au doublon #315/#316.
# (diff du fichier suivant)
diff --git a/app/__init__.py b/app/__init__.py
# (index — ignorable)
index 3054fd7..9aebd05 100644
# (avant — fichier suivant)
--- a/app/__init__.py
# (après — fichier suivant)
+++ b/app/__init__.py
# ── Zone modifiée : ligne 65 (7 ligne(s)) dans l'ancienne version → ligne 65 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -65,7 +65,7 @@ def _enregistrer_routes(app: Flask) -> None:
                               arreter_watcher_route, statut)
     from app.issues import (apercu, envoyer, issues_liste, issue_detail,
                             diff_commit, issues_en_attente, annuler_issue,
-                            fermer_issue, joindre_image)
+                            fermer_issue, joindre_image, recherche_issues)
     from app.templates import (templates_liste, templates_sauvegarder,
                                templates_supprimer)
     from app.journal import journal
# ── Zone modifiée : ligne 90 (6 ligne(s)) dans l'ancienne version → ligne 90 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,6 +90,7 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/templates/<nom_projet>/<template_id>", "templates_supprimer", login_requis(templates_supprimer), methods=["DELETE"])
     app.add_url_rule("/journal/<nom_projet>", "journal", login_requis(journal))
     app.add_url_rule("/issues-liste/<nom_projet>", "issues_liste", login_requis(issues_liste))
+    app.add_url_rule("/recherche-issues/<nom_projet>", "recherche_issues", login_requis(recherche_issues))
     app.add_url_rule("/issue/<nom_projet>/<numero>", "issue_detail", login_requis(issue_detail))
     app.add_url_rule("/diff/<nom_projet>/<hash_commit>", "diff_commit", login_requis(diff_commit))
     app.add_url_rule("/issues-en-attente/<nom_projet>", "issues_en_attente", login_requis(issues_en_attente))
# (diff du fichier suivant)
diff --git a/app/issues.py b/app/issues.py
# (index — ignorable)
index bfeee51..6bd2c1f 100644
# (avant — fichier suivant)
--- a/app/issues.py
# (après — fichier suivant)
+++ b/app/issues.py
# ── Zone modifiée : ligne 11 (6 ligne(s)) dans l'ancienne version → ligne 11 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -11,6 +11,7 @@ import re
 import subprocess
 import sys  # noqa: F401 (conservé pour parité avec les autres modules extraits)
 import tempfile
+import unicodedata
 from datetime import datetime
 from pathlib import Path
 
# ── Zone modifiée : ligne 627 (6 ligne(s)) dans l'ancienne version → ligne 628 (55 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -627,6 +628,55 @@ def issues_liste(nom_projet):
         return jsonify(erreur=str(e)), 500
 
 
+def _normaliser_recherche(texte: str) -> str:
+    """Normalise un texte pour une comparaison de titre insensible à la casse
+    ET aux accents (issue #321, ex. « ecran » doit trouver « Écran ») :
+    décomposition Unicode (NFKD) qui sépare les diacritiques des lettres de
+    base, suppression de ces diacritiques, puis casefold (plus robuste que
+    .lower() pour une comparaison insensible à la casse)."""
+    decompose = unicodedata.normalize('NFKD', texte or '')
+    sans_accents = ''.join(c for c in decompose if not unicodedata.combining(c))
+    return sans_accents.casefold()
+
+
+def recherche_issues(nom_projet):
+    """Recherche par TITRE (jamais le corps) dans les issues d'un projet,
+    insensible à la casse et aux accents (issue #321). Réutilise la même
+    logique gh que issues_liste : --state all (une issue déjà fermée/done est
+    justement ce qu'on cherche à retrouver, cf. doublon #315/#316), --limit
+    borné par _limite_issues_requete (portée de recherche PAR PROJET,
+    INDÉPENDANTE de la limite d'affichage de l'onglet). Le filtrage se fait
+    ici côté serveur, sur le titre uniquement."""
+    cfg = projet_par_nom(nom_projet)
+    if not cfg:
+        return jsonify(erreur="Projet introuvable."), 404
+    limite = _limite_issues_requete()
+    titre_cherche = _normaliser_recherche(request.args.get("titre", ""))
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "list",
+             "--repo",  cfg.depot,
+             "--state", "all",
+             "--limit", str(limite),
+             "--json",  "number,title,state,labels,createdAt"],
+            capture_output=True, text=True, timeout=30
+        )
+        if res.returncode != 0:
+            return jsonify(erreur=res.stderr.strip() or "Erreur de gh."), 502
+        toutes = json.loads(res.stdout or "[]")
+    except subprocess.TimeoutExpired:
+        return jsonify(erreur="Timeout (gh n'a pas répondu en 30s)."), 504
+    except FileNotFoundError:
+        return jsonify(erreur="gh introuvable dans le PATH."), 500
+    except Exception as e:
+        return jsonify(erreur=str(e)), 500
+    if not titre_cherche:
+        return jsonify(toutes)
+    filtrees = [it for it in toutes
+                if titre_cherche in _normaliser_recherche(it.get("title", ""))]
+    return jsonify(filtrees)
+
+
 def issue_detail(nom_projet, numero):
     """Retourne le détail d'une issue (corps + commentaires) via gh."""
     cfg = projet_par_nom(nom_projet)
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index c71a9d6..5591c23 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 354 (3 ligne(s)) dans l'ancienne version → ligne 354 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -354,3 +354,12 @@ button.danger-plein:hover{background:#8f2626}
 .overlay-arret .msg{color:#fff;font-size:18px;font-weight:600;line-height:1.5;
   max-width:520px}
 .overlay-arret button{font-size:15px;padding:11px 24px}
+/* Recherche par titre (issue #321) : barre statique + modal de résultats. */
+.barre-recherche-titre{display:flex;align-items:center;gap:8px;flex-wrap:wrap;
+  margin:8px 0}
+.barre-recherche-titre input[type="text"]{flex:1;min-width:180px;
+  padding:5px 9px;font-size:13px;border:1px solid #ccc;border-radius:4px}
+.modal-recherche-titre{max-width:900px;max-height:85vh;overflow-y:auto;
+  text-align:left}
+.modal-recherche-titre .liste-issues{max-height:280px;margin-bottom:14px}
+.modal-recherche-titre .zone-issue{max-height:360px;overflow-y:auto}
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index bb1fc8a..6e4482a 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1035 (6 ligne(s)) dans l'ancienne version → ligne 1035 (128 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1035,6 +1035,128 @@ function basculerCocheResultat(event, projet, numero) {
   if (ligne) ligne.classList.toggle('resultat-traite', coche);
 }
 
+// Construit l'élément DOM d'UNE ligne d'issue (case à cocher, pastille,
+// badges ✅/Diff/All, titre) — markup PARTAGÉ entre la liste principale de
+// l'onglet Résultats (rendreListeIssues) et la fenêtre de recherche par titre
+// (issue #321), pour que chaque résultat de recherche soit une réplique EXACTE
+// d'une ligne de l'onglet. Les badges ✅/Diff/All sont câblés ICI (leur action
+// copierReponseDepuisBadge & consorts ne dépend d'aucun contexte, juste de
+// projet+numéro) ; en revanche onclick/ondblclick de la ligne elle-même ne
+// sont PAS posés ici — chaque appelant les branche selon son propre contexte
+// (sélection + zone de détail cible).
+function construireLigneIssueDOM(it) {
+  const etat = (it.state || '').toUpperCase() === 'CLOSED' ? 'fermé' : 'ouvert';
+  const couleur = couleurProjetResultats(it.projet);
+  const numero = String(it.number);
+  // Horodatage en heure locale du navigateur (issue #58). Depuis l'issue #95,
+  // la ligne n'affiche QUE l'heure "HH:MM:SS" (colonne plus étroite) ; la date
+  // complète "DD/MM/YYYY HH:MM:SS" reste disponible au survol (attribut title).
+  const dObj = it.createdAt ? new Date(it.createdAt) : null;
+  const heureCreation = dObj
+    ? dObj.toLocaleTimeString('fr-FR', {
+        hour: '2-digit', minute: '2-digit', second: '2-digit'
+      })
+    : '';
+  const dateCreation = dObj
+    ? dObj.toLocaleString('fr-FR', {
+        day: '2-digit', month: '2-digit', year: 'numeric',
+        hour: '2-digit', minute: '2-digit', second: '2-digit'
+      })
+    : '';
+  const ligne = document.createElement('div');
+  ligne.className = 'ligne-issue';
+  ligne.dataset.projet = it.projet;
+  ligne.dataset.numero = numero;
+  // Case à cocher libre (issue #154) : repère visuel personnel d'Alain, SANS
+  // aucune signification métier. État persisté côté navigateur uniquement
+  // (localStorage), jamais envoyé au serveur. On lit l'état mémorisé pour
+  // pré-cocher la case et marquer la ligne « traitée » dès le rendu (texte
+  // grisé + fond pâle, badges colorés préservés — voir .resultat-traite, #155).
+  const dejaCoche = estResultatCoche(it.projet, numero);
+  if (dejaCoche) ligne.classList.add('resultat-traite');
+  // TYPE de l'issue (pattern chef/ouvriers, issue #86) porté en dataset :
+  // exploité par appliquerFiltresListe() pour masquer les ouvriers au besoin.
+  ligne.dataset.type = typeIssue(it);
+  // Couleur du texte = couleur du projet ; fonds translucides propres au projet
+  // portés par des variables CSS, exploitées par .ligne-issue:hover/.selectionnee.
+  ligne.style.color = couleur;
+  ligne.style.setProperty('--bg-hover', avecOpacite(couleur, 0.10));
+  ligne.style.setProperty('--bg-sel',   avecOpacite(couleur, 0.20));
+  ligne.title = 'Double-cliquez pour afficher le détail de cette issue';
+  // Gauche : badges emoji (✅ ✏️ ⚠️ ○) + pastille ● colorée du projet.
+  // Centre : #N — titre [état].
+  // Le badge ✅ des issues FERMÉES portant le label « done » (les seules qui
+  // ont une réponse CCL) devient cliquable : un clic copie directement la
+  // réponse CCL sans ouvrir le détail (issue #62).
+  // Préfixe visuel du TYPE (🎯 chef / 👷 ouvrier / rien) et de l'OS CIBLE
+  // (🪟 for-windows / rien) devant les badges. Deux dimensions distinctes et
+  // cumulables : un ouvrier for-windows affiche « 👷🪟 » (issue #165).
+  const prefType = prefixeTypeIssue(it) + prefixeOSCible(it);
+  let badgesHtml = (prefType ? prefType + ' ' : '') + prefixeIssue(it.labels);
+  const nomsLabelsLigne = (it.labels || [])
+    .map(l => ((l && l.name) || l || '').toLowerCase());
+  if (etat === 'fermé' && nomsLabelsLigne.includes('done')
+      && badgesHtml.includes('✅')) {
+    // Trois badges aux rôles distincts et non redondants (issue #116) :
+    //   ✅ (vert) → réponse CCL COMPLÈTE seule (plus jamais le résumé),
+    //   « Diff »  → diff seul du/des commit(s) associé(s),
+    //   « All »   → réponse complète + diff ensemble.
+    // Le badge ✅ (vert) copie la réponse CCL COMPLÈTE (résumé + détails), sans
+    // le diff. Le résumé seul n'est plus copié par aucun badge (issue #116).
+    badgesHtml = badgesHtml.replace('✅',
+      '<span class="badge-copie-ccl" title="Copier la réponse CCL complète"'
+      + ' onclick="copierReponseDepuisBadge(event, \''
+      + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">✅</span>');
+    // Badge « Diff » (issue #116) : copie UNIQUEMENT le diff du/des commit(s)
+    // associé(s) (résultat de git show), sans la réponse. Sans commit (issue en
+    // lecture seule), comportement neutre — rien n'est copié, pas d'erreur.
+    badgesHtml +=
+      '<span class="badge-copie-diff" title="Copier le diff seul du/des commit(s)"'
+      + ' onclick="copierDiffDepuisBadge(event, \''
+      + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">Diff</span>';
+    // Badge « All » (issue #116) : copie, en un seul geste, la réponse CCL
+    // COMPLÈTE suivie du diff du/des commit(s) associé(s). Sans commit (lecture
+    // seule), copie la réponse seule — sans section diff vide ni erreur.
+    badgesHtml +=
+      '<span class="badge-copie-all" title="Copier la réponse complète + le diff"'
+      + ' onclick="copierToutEtDiffDepuisBadge(event, \''
+      + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">All</span>';
+  }
+  ligne.innerHTML =
+    // Case à cocher libre (issue #154), tout à gauche de la ligne. Le clic ne
+    // doit PAS sélectionner/ouvrir l'issue (stopPropagation) ; onchange délègue
+    // à basculerCocheResultat() qui persiste l'état dans localStorage.
+    '<input type="checkbox" class="coche-resultat"'
+    + (dejaCoche ? ' checked' : '')
+    + ' title="Repère personnel : marquer ce résultat comme traité/lu"'
+    + ' onclick="event.stopPropagation()"'
+    + ' onchange="basculerCocheResultat(event, \''
+    + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">'
+    + '<span class="ligne-date" title="' + escapeHtml(dateCreation) + '"'
+    + ' style="font-size:11px;color:#999;'
+    + 'min-width:66px;font-family:monospace">' + escapeHtml(heureCreation) + '</span>'
+    + '<span class="ligne-gauche">'
+    + '<span class="ligne-badges">' + badgesHtml + '</span>'
+    + '<span class="pastille-ligne" style="background:' + couleur + '"></span>'
+    + '</span>'
+    // Poignée de redimensionnement de la SEULE colonne titre (issue #95) :
+    // sur la bordure gauche de .ligne-texte. onclick stoppe la propagation
+    // pour qu'un clic de fin de glisser ne sélectionne pas l'issue.
+    + '<span class="poignee-titre" title="Glisser pour redimensionner la colonne titre"'
+    + ' onmousedown="demarrerRedimTitre(event)" onclick="event.stopPropagation()"></span>'
+    + '<span class="ligne-texte">#' + escapeHtml(numero) + ' — '
+    + escapeHtml(it.title) + ' [' + etat + ']</span>'
+    // Badge d'estimation prédictive (issue #108) PUIS badge de temps restant
+    // (issues #91/#106) : l'estimation (durée médiane historique du même
+    // projet+type+mode) s'affiche JUSTE AVANT le décompte, qui reste inchangé.
+    // Les deux sont remplis/actualisés par majBadgesTempsRestant().
+    + (etat === 'ouvert'
+        ? '<span class="ligne-estimation" style="display:none"></span>'
+          + '<span class="ligne-tempsrestant" style="display:none"></span>'
+        : '');
+  return ligne;
+}
+
 // (Re)construit la liste HTML cliquable à partir de listeIssuesResultats. TOUTES
 // les issues sont rendues comme lignes ; le filtre projet ne fait que masquer
 // (display:none) les lignes des projets inactifs. Chaque ligne est coloriée à la
# ── Zone modifiée : ligne 1051 (43 ligne(s)) dans l'ancienne version → ligne 1173 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1051,43 +1173,8 @@ function rendreListeIssues(reset) {
     return;
   }
   for (const it of listeIssuesResultats) {
-    const etat = (it.state || '').toUpperCase() === 'CLOSED' ? 'fermé' : 'ouvert';
-    const couleur = couleurProjetResultats(it.projet);
     const numero = String(it.number);
-    // Horodatage en heure locale du navigateur (issue #58). Depuis l'issue #95,
-    // la ligne n'affiche QUE l'heure "HH:MM:SS" (colonne plus étroite) ; la date
-    // complète "DD/MM/YYYY HH:MM:SS" reste disponible au survol (attribut title).
-    const dObj = it.createdAt ? new Date(it.createdAt) : null;
-    const heureCreation = dObj
-      ? dObj.toLocaleTimeString('fr-FR', {
-          hour: '2-digit', minute: '2-digit', second: '2-digit'
-        })
-      : '';
-    const dateCreation = dObj
-      ? dObj.toLocaleString('fr-FR', {
-          day: '2-digit', month: '2-digit', year: 'numeric',
-          hour: '2-digit', minute: '2-digit', second: '2-digit'
-        })
-      : '';
-    const ligne = document.createElement('div');
-    ligne.className = 'ligne-issue';
-    ligne.dataset.projet = it.projet;
-    ligne.dataset.numero = numero;
-    // Case à cocher libre (issue #154) : repère visuel personnel d'Alain, SANS
-    // aucune signification métier. État persisté côté navigateur uniquement
-    // (localStorage), jamais envoyé au serveur. On lit l'état mémorisé pour
-    // pré-cocher la case et marquer la ligne « traitée » dès le rendu (texte
-    // grisé + fond pâle, badges colorés préservés — voir .resultat-traite, #155).
-    const dejaCoche = estResultatCoche(it.projet, numero);
-    if (dejaCoche) ligne.classList.add('resultat-traite');
-    // TYPE de l'issue (pattern chef/ouvriers, issue #86) porté en dataset :
-    // exploité par appliquerFiltresListe() pour masquer les ouvriers au besoin.
-    ligne.dataset.type = typeIssue(it);
-    // Couleur du texte = couleur du projet ; fonds translucides propres au projet
-    // portés par des variables CSS, exploitées par .ligne-issue:hover/.selectionnee.
-    ligne.style.color = couleur;
-    ligne.style.setProperty('--bg-hover', avecOpacite(couleur, 0.10));
-    ligne.style.setProperty('--bg-sel',   avecOpacite(couleur, 0.20));
+    const ligne = construireLigneIssueDOM(it);
     // Clic simple : sélectionne SEULEMENT la ligne, sans charger son détail —
     // geste réflexe qui ne doit pas coûter un aller-retour réseau (issue #261).
     // Ctrl+clic : demande explicite de détail (comme le double-clic), puis
# ── Zone modifiée : ligne 1113 (78 ligne(s)) dans l'ancienne version → ligne 1200 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1113,78 +1200,6 @@ function rendreListeIssues(reset) {
       event.preventDefault();
       await afficherIssue(it.projet, numero);
     };
-    ligne.title = 'Double-cliquez pour afficher le détail de cette issue';
-    // Gauche : badges emoji (✅ ✏️ ⚠️ ○) + pastille ● colorée du projet.
-    // Centre : #N — titre [état].
-    // Le badge ✅ des issues FERMÉES portant le label « done » (les seules qui
-    // ont une réponse CCL) devient cliquable : un clic copie directement la
-    // réponse CCL sans ouvrir le détail (issue #62).
-    // Préfixe visuel du TYPE (🎯 chef / 👷 ouvrier / rien) et de l'OS CIBLE
-    // (🪟 for-windows / rien) devant les badges. Deux dimensions distinctes et
-    // cumulables : un ouvrier for-windows affiche « 👷🪟 » (issue #165).
-    const prefType = prefixeTypeIssue(it) + prefixeOSCible(it);
-    let badgesHtml = (prefType ? prefType + ' ' : '') + prefixeIssue(it.labels);
-    const nomsLabelsLigne = (it.labels || [])
-      .map(l => ((l && l.name) || l || '').toLowerCase());
-    if (etat === 'fermé' && nomsLabelsLigne.includes('done')
-        && badgesHtml.includes('✅')) {
-      // Trois badges aux rôles distincts et non redondants (issue #116) :
-      //   ✅ (vert) → réponse CCL COMPLÈTE seule (plus jamais le résumé),
-      //   « Diff »  → diff seul du/des commit(s) associé(s),
-      //   « All »   → réponse complète + diff ensemble.
-      // Le badge ✅ (vert) copie la réponse CCL COMPLÈTE (résumé + détails), sans
-      // le diff. Le résumé seul n'est plus copié par aucun badge (issue #116).
-      badgesHtml = badgesHtml.replace('✅',
-        '<span class="badge-copie-ccl" title="Copier la réponse CCL complète"'
-        + ' onclick="copierReponseDepuisBadge(event, \''
-        + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">✅</span>');
-      // Badge « Diff » (issue #116) : copie UNIQUEMENT le diff du/des commit(s)
-      // associé(s) (résultat de git show), sans la réponse. Sans commit (issue en
-      // lecture seule), comportement neutre — rien n'est copié, pas d'erreur.
-      badgesHtml +=
-        '<span class="badge-copie-diff" title="Copier le diff seul du/des commit(s)"'
-        + ' onclick="copierDiffDepuisBadge(event, \''
-        + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">Diff</span>';
-      // Badge « All » (issue #116) : copie, en un seul geste, la réponse CCL
-      // COMPLÈTE suivie du diff du/des commit(s) associé(s). Sans commit (lecture
-      // seule), copie la réponse seule — sans section diff vide ni erreur.
-      badgesHtml +=
-        '<span class="badge-copie-all" title="Copier la réponse complète + le diff"'
-        + ' onclick="copierToutEtDiffDepuisBadge(event, \''
-        + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">All</span>';
-    }
-    ligne.innerHTML =
-      // Case à cocher libre (issue #154), tout à gauche de la ligne. Le clic ne
-      // doit PAS sélectionner/ouvrir l'issue (stopPropagation) ; onchange délègue
-      // à basculerCocheResultat() qui persiste l'état dans localStorage.
-      '<input type="checkbox" class="coche-resultat"'
-      + (dejaCoche ? ' checked' : '')
-      + ' title="Repère personnel : marquer ce résultat comme traité/lu"'
-      + ' onclick="event.stopPropagation()"'
-      + ' onchange="basculerCocheResultat(event, \''
-      + escapeHtml(it.projet) + '\', ' + Number(numero) + ')">'
-      + '<span class="ligne-date" title="' + escapeHtml(dateCreation) + '"'
-      + ' style="font-size:11px;color:#999;'
-      + 'min-width:66px;font-family:monospace">' + escapeHtml(heureCreation) + '</span>'
-      + '<span class="ligne-gauche">'
-      + '<span class="ligne-badges">' + badgesHtml + '</span>'
-      + '<span class="pastille-ligne" style="background:' + couleur + '"></span>'
-      + '</span>'
-      // Poignée de redimensionnement de la SEULE colonne titre (issue #95) :
-      // sur la bordure gauche de .ligne-texte. onclick stoppe la propagation
-      // pour qu'un clic de fin de glisser ne sélectionne pas l'issue.
-      + '<span class="poignee-titre" title="Glisser pour redimensionner la colonne titre"'
-      + ' onmousedown="demarrerRedimTitre(event)" onclick="event.stopPropagation()"></span>'
-      + '<span class="ligne-texte">#' + escapeHtml(numero) + ' — '
-      + escapeHtml(it.title) + ' [' + etat + ']</span>'
-      // Badge d'estimation prédictive (issue #108) PUIS badge de temps restant
-      // (issues #91/#106) : l'estimation (durée médiane historique du même
-      // projet+type+mode) s'affiche JUSTE AVANT le décompte, qui reste inchangé.
-      // Les deux sont remplis/actualisés par majBadgesTempsRestant().
-      + (etat === 'ouvert'
-          ? '<span class="ligne-estimation" style="display:none"></span>'
-            + '<span class="ligne-tempsrestant" style="display:none"></span>'
-          : '');
     zone.appendChild(ligne);
   }
   appliquerFiltresListe();
# ── Zone modifiée : ligne 1230 (17 ligne(s)) dans l'ancienne version → ligne 1245 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1230,17 +1245,23 @@ function appliquerLargeurTitre() {
 let redimTitreEtat = null;
 
 // Début du glisser sur la poignée gauche de la colonne titre. On mémorise la
-// largeur de départ de CETTE ligne comme référence ; le mouvement met à jour la
-// var CSS partagée par toutes les lignes (colonne cohérente).
+// largeur de départ de CETTE ligne comme référence, ainsi que la liste (.liste-
+// issues) qui la contient : depuis l'issue #321, ce n'est plus forcément
+// #liste-issues (l'onglet Résultats) — la fenêtre de recherche par titre
+// affiche ses propres lignes dans #liste-resultats-recherche, qui porte aussi
+// la classe .liste-issues et doit se redimensionner indépendamment, sans
+// affecter la colonne de l'onglet.
 function demarrerRedimTitre(event) {
   event.preventDefault();
   event.stopPropagation();
   const ligne = event.currentTarget.closest('.ligne-issue');
   const texte = ligne ? ligne.querySelector('.ligne-texte') : null;
-  if (!texte) return;
+  const liste = ligne ? ligne.closest('.liste-issues') : null;
+  if (!texte || !liste) return;
   redimTitreEtat = {
     xDepart: event.clientX,
     largeurDepart: texte.getBoundingClientRect().width,
+    liste: liste,
   };
   document.body.style.cursor = 'col-resize';
   document.body.style.userSelect = 'none';
# ── Zone modifiée : ligne 1256 (22 ligne(s)) dans l'ancienne version → ligne 1277 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1256,22 +1277,23 @@ function surRedimTitre(event) {
   const delta = redimTitreEtat.xDepart - event.clientX;
   let w = Math.round(redimTitreEtat.largeurDepart + delta);
   w = Math.max(80, Math.min(w, 1200));
-  const liste = document.getElementById('liste-issues');
-  if (!liste) return;
-  liste.style.setProperty('--largeur-titre', w + 'px');
-  liste.classList.add('titre-redimensionne');
+  redimTitreEtat.liste.style.setProperty('--largeur-titre', w + 'px');
+  redimTitreEtat.liste.classList.add('titre-redimensionne');
 }
 
-// Fin du glisser : on persiste la largeur courante dans localStorage.
+// Fin du glisser : on persiste la largeur courante dans localStorage — mais
+// UNIQUEMENT pour la liste de l'onglet Résultats (#liste-issues) ; un
+// redimensionnement dans la fenêtre de recherche reste local à cette session,
+// la fenêtre étant reconstruite à chaque nouvelle recherche.
 function finRedimTitre() {
   document.removeEventListener('mousemove', surRedimTitre);
   document.removeEventListener('mouseup', finRedimTitre);
   document.body.style.cursor = '';
   document.body.style.userSelect = '';
   if (!redimTitreEtat) return;
+  const liste = redimTitreEtat.liste;
   redimTitreEtat = null;
-  const liste = document.getElementById('liste-issues');
-  if (!liste) return;
+  if (liste.id !== 'liste-issues') return;
   const w = parseInt(liste.style.getPropertyValue('--largeur-titre'), 10);
   if (Number.isFinite(w) && w > 0) {
     try { localStorage.setItem(CLE_LARGEUR_TITRE, String(w)); } catch(e) {}
# ── Zone modifiée : ligne 1859 (6 ligne(s)) dans l'ancienne version → ligne 1881 (201 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1859,6 +1881,201 @@ async function afficherIssue(nom, numero) {
   }
 }
 
+// ─── Fenêtre de recherche par titre (issue #321) ──────────────────────────
+// Contexte : le 02/08/2026 une issue a été envoyée en double (#315/#316)
+// faute de moyen rapide de vérifier si un sujet avait déjà été traité. La
+// PORTÉE de recherche (nombre d'issues ratissées PAR PROJET sélectionné dans
+// les filtres) est INDÉPENDANTE de la limite d'affichage de l'onglet
+// (limiteIssuesProjet) : la recherche re-interroge toujours GitHub avec sa
+// propre portée — elle ne filtre jamais listeIssuesResultats déjà en mémoire,
+// sans quoi une issue au-delà de la limite d'affichage resterait introuvable.
+
+// Jeton anti-course dédié à la zone de détail de la fenêtre de recherche —
+// INDÉPENDANT de afficherIssueSeq (zone-issue de l'onglet Résultats) : les
+// deux zones chargent des détails en parallèle sans interférer, et un
+// double-clic dans la fenêtre n'affecte jamais projetCourant/numeroCourant ni
+// la sélection de l'onglet (contrairement à afficherIssue, qui reste dédiée à
+// #zone-issue et inchangée).
+let seqDetailRecherche = 0;
+
+// Charge et affiche le détail d'un résultat de recherche dans la zone de
+// détail PROPRE à la fenêtre (#zone-issue-recherche, autonome — jamais
+// #zone-issue de l'onglet). Reprend la même mécanique cache TTL + fetch +
+// rendu que afficherIssue, en réutilisant construireHtmlIssue (même badges,
+// mêmes onglets Réponse/Diff) sans la dupliquer.
+async function afficherIssueRecherche(nom, numero) {
+  numero = numero == null ? '' : String(numero);
+  const zone = document.getElementById('zone-issue-recherche');
+  if (!zone || !nom || !numero) return;
+  const seq = ++seqDetailRecherche;
+
+  const cleCache = CLE_CACHE_DETAIL + nom + '_' + numero;
+  let htmlAffiche = null;
+  try {
+    const obj = JSON.parse(localStorage.getItem(cleCache) || 'null');
+    if (obj && obj.it && (Date.now() - obj.ts) < TTL_DETAIL_MS) {
+      htmlAffiche = construireHtmlIssue(obj.it, nom);
+      zone.innerHTML = htmlAffiche;
+    }
+  } catch(e) {}
+  if (htmlAffiche === null) {
+    zone.innerHTML = '<div class="issue-vide">Chargement de l\'issue #' + escapeHtml(numero) + '…</div>';
+  }
+
+  try {
+    const rep = await fetch('/issue/' + encodeURIComponent(nom) + '/' + encodeURIComponent(numero));
+    const it = await rep.json();
+    if (seq !== seqDetailRecherche) return;
+    if (it.erreur) {
+      if (htmlAffiche === null) {
+        zone.innerHTML = '<div class="issue-vide">Erreur : ' + escapeHtml(it.erreur) + '</div>';
+      }
+      return;
+    }
+    try { localStorage.setItem(cleCache, JSON.stringify({ts: Date.now(), it: it})); } catch(e) {}
+    const htmlFrais = construireHtmlIssue(it, nom);
+    if (htmlFrais !== htmlAffiche) {
+      zone.innerHTML = htmlFrais;
+    }
+  } catch(e) {
+    if (seq === seqDetailRecherche && htmlAffiche === null) {
+      zone.innerHTML = '<div class="issue-vide">Erreur réseau : ' + escapeHtml(e.message) + '</div>';
+    }
+  }
+}
+
+// Lit le champ « portée » de la recherche, bornée par les mêmes constantes
+// que la limite d'affichage (LIMITE_ISSUES_MIN..MAX) — deux réglages distincts
+// partageant les mêmes bornes serveur (_limite_issues_requete).
+function porteeRechercheTitre() {
+  const input = document.getElementById('recherche-titre-portee');
+  const n = parseInt(input ? input.value : '', 10);
+  const bornee = Number.isFinite(n)
+    ? Math.min(LIMITE_ISSUES_MAX, Math.max(LIMITE_ISSUES_MIN, n))
+    : 15;
+  if (input) input.value = String(bornee);
+  return bornee;
+}
+
+// (Re)construit la liste des résultats de recherche : réplique EXACTE d'une
+// ligne de l'onglet Résultats (construireLigneIssueDOM, mêmes badges), dont le
+// double-clic cible la zone de détail PROPRE à la fenêtre (afficherIssueRecherche),
+// jamais celle de l'onglet.
+function rendreResultatsRecherche(resultats) {
+  const zone = document.getElementById('liste-resultats-recherche');
+  zone.innerHTML = '';
+  if (!resultats.length) {
+    zone.innerHTML = '<div class="issue-vide">Aucun résultat</div>';
+    return;
+  }
+  for (const it of resultats) {
+    const numero = String(it.number);
+    const ligne = construireLigneIssueDOM(it);
+    ligne.ondblclick = async (event) => {
+      event.preventDefault();
+      await afficherIssueRecherche(it.projet, numero);
+    };
+    zone.appendChild(ligne);
+  }
+}
+
+function ouvrirModalRechercheTitre() {
+  const modal = document.getElementById('modal-recherche-titre');
+  if (modal) modal.classList.add('actif');
+}
+
+function fermerModalRechercheTitre() {
+  const modal = document.getElementById('modal-recherche-titre');
+  if (modal) modal.classList.remove('actif');
+}
+
+// Lance la recherche par titre : un appel gh --state all --limit <portée> PAR
+// PROJET sélectionné dans les filtres (issue #321), state=all car on cherche
+// justement à retrouver un sujet DÉJÀ traité (doublon #315/#316). Déclenchée
+// UNIQUEMENT au clic sur le bouton (ou Entrée dans le champ texte) — jamais à
+// la frappe, cohérent avec la décision de #270 pour le bouton ↻. L'échec d'un
+// projet n'annule pas la recherche sur les autres : ce qui a réussi est
+// agrégé, les projets en échec sont listés dans un message discret.
+async function lancerRechercheTitre() {
+  const champTexte = document.getElementById('recherche-titre-texte');
+  const titre = (champTexte ? champTexte.value : '').trim();
+  const zoneErreurs = document.getElementById('recherche-titre-erreurs');
+  if (zoneErreurs) { zoneErreurs.style.display = 'none'; zoneErreurs.innerHTML = ''; }
+
+  if (!titre) {
+    if (zoneErreurs) {
+      zoneErreurs.textContent = 'Saisissez un titre à rechercher.';
+      zoneErreurs.style.display = '';
+    }
+    return;
+  }
+  // Portée = projets ACTUELLEMENT sélectionnés dans les filtres de l'onglet
+  // (projetsFiltresActifs) — pas tous les projets configurés.
+  const projets = nomsProjetsDisponibles().filter(nom => projetsFiltresActifs.has(nom));
+  if (!projets.length) {
+    if (zoneErreurs) {
+      zoneErreurs.textContent = 'Aucun projet sélectionné — activez au moins un filtre projet ci-dessus.';
+      zoneErreurs.style.display = '';
+    }
+    return;
+  }
+
+  const portee = porteeRechercheTitre();
+  const btn = document.getElementById('btn-recherche-titre');
+  const indicateur = document.getElementById('recherche-titre-indicateur');
+  if (btn) btn.disabled = true;
+  if (indicateur) indicateur.style.display = '';
+
+  const echecs = [];
+  let resultats = [];
+  try {
+    // Un appel gh PAR PROJET sélectionné, chacun avec sa propre portée — la
+    // recherche ne s'arrête pas au premier match, elle ratisse toute la
+    // portée de tous les projets sélectionnés (issue #321).
+    const listes = await Promise.all(projets.map(async nom => {
+      try {
+        const rep = await fetch('/recherche-issues/' + encodeURIComponent(nom)
+          + '?titre=' + encodeURIComponent(titre)
+          + '&limite=' + encodeURIComponent(portee));
+        const json = await rep.json();
+        if (!Array.isArray(json)) {
+          echecs.push(nom + ' : ' + (json && json.erreur ? json.erreur : 'erreur inconnue'));
+          return [];
+        }
+        return json.map(it => Object.assign({}, it, {projet: nom}));
+      } catch(e) {
+        echecs.push(nom + ' : erreur réseau (' + e.message + ')');
+        return [];
+      }
+    }));
+    resultats = listes.flat();
+  } finally {
+    if (btn) btn.disabled = false;
+    if (indicateur) indicateur.style.display = 'none';
+  }
+
+  // Filtre « 👷 Ouvriers » (issue #86), même détection que l'onglet — appliqué
+  // uniquement sur les projets ratissés (les autres n'ont de toute façon pas
+  // été interrogés).
+  if (!filtreOuvriersActif) {
+    resultats = resultats.filter(it => typeIssue(it) !== 'ouvrier');
+  }
+  resultats.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
+
+  if (zoneErreurs && echecs.length) {
+    zoneErreurs.innerHTML = '⚠️ Échec sur ' + echecs.length + ' projet(s) : '
+      + echecs.map(escapeHtml).join(' — ');
+    zoneErreurs.style.display = '';
+  }
+
+  rendreResultatsRecherche(resultats);
+  const zoneDetail = document.getElementById('zone-issue-recherche');
+  if (zoneDetail) {
+    zoneDetail.innerHTML = '<div class="issue-vide">Double-cliquez un résultat pour afficher son détail.</div>';
+  }
+  ouvrirModalRechercheTitre();
+}
+
 // Bouton rafraîchir (issue #56) : vide le cache localStorage (liste + tous les
 // détails) puis recharge tout depuis GitHub. Contourne le TTL du cache détail,
 // qui peut montrer une issue « ouverte » alors que le watcher l'a fermée.
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 0799c80..59dcef9 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 184 (6 ligne(s)) dans l'ancienne version → ligne 184 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -184,6 +184,29 @@
     <!-- Boutons toggle : un par projet + « Tous ». Générés dynamiquement. -->
     <div id="filtres-projets" class="filtres-projets"></div>
 
+    <!-- Recherche par titre (issue #321) : bloc STATIQUE (pas régénéré à
+         chaque bascule de filtre, contrairement à #filtres-projets), pour ne
+         jamais perdre la saisie en cours. La PORTÉE (nombre d'issues ratissées
+         PAR PROJET sélectionné ci-dessus) est un réglage DISTINCT de la limite
+         d'affichage de l'onglet (« par projet : ») — la recherche re-interroge
+         toujours GitHub, elle ne filtre jamais ce qui est déjà en mémoire.
+         Déclenchée uniquement au clic sur « Rechercher » (ou Entrée dans le
+         champ texte), jamais à la frappe (cohérent avec #270). -->
+    <div class="barre-recherche-titre">
+      <input type="text" id="recherche-titre-texte"
+             placeholder="Rechercher un titre déjà traité…" autocomplete="off"
+             onkeydown="if(event.key==='Enter'){event.preventDefault();lancerRechercheTitre();}">
+      <label class="limite-issues-label"
+             title="Nombre d'issues ratissées PAR PROJET sélectionné ci-dessus (pas un total). Réglage distinct de la limite d'affichage de l'onglet.">
+        portée :
+        <input type="number" id="recherche-titre-portee" class="limite-issues-projet"
+               min="1" max="50" step="1" value="15">
+      </label>
+      <button id="btn-recherche-titre" onclick="lancerRechercheTitre()">🔍 Rechercher</button>
+      <span id="recherche-titre-indicateur" class="maj-indicateur" style="display:none">Recherche…</span>
+    </div>
+    <div id="recherche-titre-erreurs" class="message" style="display:none"></div>
+
     <!-- Liste HTML cliquable des issues récentes (tous projets). Remplace la
          combobox : chaque ligne est coloriée à la couleur de son projet, ce que
          Firefox refuse de faire sur les <option>. Navigation par clic direct. -->
# ── Zone modifiée : ligne 519 (6 ligne(s)) dans l'ancienne version → ligne 542 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -519,6 +542,24 @@
   </div>
 </div>
 
+<!-- ─── Modal « Résultats de recherche par titre » (issue #321) ──────────────
+     Fenêtre séparée et AUTONOME : sa propre liste (réplique exacte des lignes
+     de l'onglet Résultats, mêmes badges ✅/Diff/All) et sa PROPRE zone de
+     détail (#zone-issue-recherche) — un double-clic ici n'affecte jamais la
+     zone de détail de l'onglet Résultats. -->
+<div id="modal-recherche-titre" class="modal-overlay">
+  <div class="modal-carte modal-recherche-titre">
+    <div class="modal-titre">🔍 Résultats de recherche</div>
+    <div id="liste-resultats-recherche" class="liste-issues"></div>
+    <div id="zone-issue-recherche" class="zone-issue">
+      <div class="issue-vide">Double-cliquez un résultat pour afficher son détail.</div>
+    </div>
+    <div class="modal-boutons">
+      <button id="btn-fermer-recherche-titre" onclick="fermerModalRechercheTitre()">Fermer</button>
+    </div>
+  </div>
+</div>
+
 <!-- ─── Overlay « serveur arrêté » ────────────────────────────────────────── -->
 <div id="overlay-arret" class="overlay-arret">
   <div class="msg">🔴 Serveur arrêté — relancez new_issue.py puis rechargez</div>
