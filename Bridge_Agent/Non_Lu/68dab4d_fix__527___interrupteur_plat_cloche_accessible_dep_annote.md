68dab4d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 68dab4d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Sep 10 20:21:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #527 : interrupteur plat/cloche accessible depuis new_issue.py
    
    - app/son.py (nouveau) : routes GET/POST /son-actif (lit/écrit
      scripts/son_actif.txt) et POST /tester-son (bip immédiat avec le
      timbre actuellement enregistré) — global, sans <nom_projet>,
      contrairement à /tester-bip/<projet> (tonalité, issue #526).
    - templates/index.html + static/css/style.css + static/js/app.js :
      nouvelle zone #pl-zone-son dans le panneau flottant Infrastructure
      (onglet Résultats), toujours visible — sélecteur segmenté Plat/Cloche
      (écrit son_actif.txt au clic, pas de rechargement requis) + bouton
      Tester le son. Initialisée une seule fois (initZoneSon, appelée par
      demarrerPanneauLateral), pas reconstruite à chaque cycle de
      rafraichirPanneauLateralResultats comme les autres zones.
    - scripts/traitement_fin.py + BRIDGE_AGENT_DOC.md : documentation de
      l'interrupteur et clarification de son interaction avec TONALITE_BIP
      (issue #526) — la tonalité (par projet) décale la fréquence des DEUX
      timbres plat/cloche, elle ne choisit pas entre eux ; le timbre
      (global, ce réglage) et la tonalité (par projet) sont orthogonaux.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 22f2904..65232a7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 2180 (6 ligne(s)) dans l'ancienne version → ligne 2180 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2180,6 +2180,22 @@ new_issue.py (ThinkPad) → polling gh → détecte la transition → bip/bulle/
   reconnue → défaut inchangé (`plat`), pour ne rien casser silencieusement.
   Ce fichier n'est **pas** un `configs/*.conf` : le garde-fou §11 ne s'y
   applique pas.
+- **Interrupteur plat/cloche accessible depuis l'interface (issue #527).**
+  Avant cette issue, changer de son imposait d'éditer `son_actif.txt` à la
+  main. `new_issue.py` expose désormais ce choix dans le panneau flottant
+  Infrastructure de l'onglet Résultats (`#pl-zone-son`, `templates/index.html`
+  + `static/js/app.js::initZoneSon`/`choisirSonActif`/`testerSonActif`) : un
+  sélecteur à deux positions « Plat »/« Cloche », toujours visible, et un
+  bouton **« Tester le son »**. Deux routes dédiées (`app/son.py`,
+  **GLOBALES, sans `<nom_projet>`** — contrairement à `/tester-bip/<projet>`
+  ci-dessous) :
+  - `GET`/`POST /son-actif` : lit/écrit `son_actif.txt` — le clic sur une
+    position écrit directement le fichier (pas de bouton « Enregistrer »
+    séparé), effectif au bip suivant sans redémarrage d'aucun processus
+    (`traitement_fin.py::son_actif()` relit le fichier à chaque bip) ;
+  - `POST /tester-son` : joue le bip avec le timbre actuellement enregistré
+    dans `son_actif.txt` (tonalité neutre, `0` — ce réglage n'est pas
+    rattaché à un projet).
 - **Tonalité du bip par projet (issue #526), clé `.conf` `TONALITE_BIP`.**
   `son_actif.txt` (ci-dessus) choisit le son pour **tous** les projets à la
   fois ; `TONALITE_BIP` (optionnelle, entier en **demi-tons**, défaut `0` =
# (diff du fichier suivant)
diff --git a/app/__init__.py b/app/__init__.py
# (index — ignorable)
index bef6de0..082be7b 100644
# (avant — fichier suivant)
--- a/app/__init__.py
# (après — fichier suivant)
+++ b/app/__init__.py
# ── Zone modifiée : ligne 81 (6 ligne(s)) dans l'ancienne version → ligne 81 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -81,6 +81,7 @@ def _enregistrer_routes(app: Flask) -> None:
     from app.issues_inbox import (etat_inbox, demarrer_watcher_inbox_route,
                                   arreter_watcher_inbox_route)
     from app.diag_heartbeat import visibilite as diag_visibilite   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
+    from app.son import get_son_actif, post_son_actif, tester_son
     from app.vues import index
 
     app.add_url_rule("/login", "login", login, methods=["GET"])
# ── Zone modifiée : ligne 142 (3 ligne(s)) dans l'ancienne version → ligne 143 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -142,3 +143,8 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/issues-inbox/demarrer-watcher", "demarrer_watcher_inbox_route", login_requis(demarrer_watcher_inbox_route), methods=["POST"])
     app.add_url_rule("/issues-inbox/arreter-watcher", "arreter_watcher_inbox_route", login_requis(arreter_watcher_inbox_route), methods=["POST"])
     app.add_url_rule("/diag-visibilite", "diag_visibilite", diag_visibilite, methods=["POST"])   # DIAGNOSTIC TEMPORAIRE — issue #157, à retirer
+    # ─── Interrupteur global plat/cloche du bip (issue #527), distinct de la
+    # tonalité par projet (issue #526, /tester-bip/<nom_projet> ci-dessus) ────
+    app.add_url_rule("/son-actif", "get_son_actif", login_requis(get_son_actif), methods=["GET"])
+    app.add_url_rule("/son-actif", "post_son_actif", login_requis(post_son_actif), methods=["POST"])
+    app.add_url_rule("/tester-son", "tester_son", login_requis(tester_son), methods=["POST"])
# (diff du fichier suivant)
diff --git a/app/son.py b/app/son.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..64f420d
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/app/son.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (68 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,68 @@
+"""Interrupteur global plat/cloche du bip (issue #527).
+
+`scripts/traitement_fin.py` lit `scripts/son_actif.txt` (une seule ligne,
+`plat` ou `cloche`) pour choisir entre `bip_plat()` et `bip()` — voir le
+docstring de ce module pour le détail des deux timbres et leur interaction
+avec `TONALITE_BIP` (réglage PAR PROJET, orthogonal à celui-ci qui est
+GLOBAL : la tonalité décale la fréquence des DEUX timbres, elle ne choisit
+pas entre eux). Avant cette issue, seule une édition manuelle du fichier
+permettait de changer de timbre ; ces routes l'exposent dans l'interface,
+à la façon de `/tester-bip/<nom_projet>` pour la tonalité (app/projets.py).
+
+Contrairement à `TONALITE_BIP`, ce réglage n'est pas dans un `.conf` de
+projet : `son_actif.txt` pilote TOUS les projets utilisant le script partagé,
+donc ces routes ne prennent pas de `<nom_projet>` en paramètre.
+"""
+
+import sys
+from pathlib import Path
+
+from flask import jsonify, request
+
+DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(DOSSIER_SCRIPT))
+
+import notifications  # noqa: E402
+
+CHEMIN_SON_ACTIF   = DOSSIER_SCRIPT / "scripts" / "son_actif.txt"
+SCRIPT_BIP_PARTAGE = DOSSIER_SCRIPT / "scripts" / "traitement_fin.py"
+
+SONS_VALIDES = ("plat", "cloche")
+
+
+def _lire_son_actif() -> str:
+    """Même logique que `son_actif()` dans scripts/traitement_fin.py : fichier
+    absent, illisible, ou valeur non reconnue → 'plat' (défaut inchangé)."""
+    try:
+        valeur = CHEMIN_SON_ACTIF.read_text(encoding="utf-8").strip().lower()
+        if valeur in SONS_VALIDES:
+            return valeur
+    except OSError:
+        pass
+    return "plat"
+
+
+def get_son_actif():
+    """GET /son-actif — état courant, pour peupler l'interrupteur au chargement."""
+    return jsonify(son=_lire_son_actif())
+
+
+def post_son_actif():
+    """POST /son-actif — écrit le timbre choisi ({"son": "plat"|"cloche"}) dans
+    `son_actif.txt`, effectif au bip suivant sans redémarrage d'aucun processus
+    (le fichier est relu à chaque bip par traitement_fin.py::son_actif())."""
+    data = request.json or {}
+    son = str(data.get("son", "")).strip().lower()
+    if son not in SONS_VALIDES:
+        return jsonify(erreur=f"Valeur invalide (attendu 'plat' ou 'cloche') : {son!r}"), 400
+    CHEMIN_SON_ACTIF.write_text(son + "\n", encoding="utf-8")
+    return jsonify(succes=True, son=son)
+
+
+def tester_son():
+    """POST /tester-son — joue le bip avec le timbre ACTUELLEMENT enregistré
+    dans son_actif.txt (le front écrit d'abord via POST /son-actif au clic sur
+    l'interrupteur, donc ce test entend toujours le dernier choix). Tonalité
+    neutre (0) : ce réglage est global, pas rattaché à un projet."""
+    notifications.bip(SCRIPT_BIP_PARTAGE, 1)
+    return jsonify(succes=True)
# (diff du fichier suivant)
diff --git a/scripts/traitement_fin.py b/scripts/traitement_fin.py
# (index — ignorable)
index fd5da38..a25ac76 100644
# (avant — fichier suivant)
--- a/scripts/traitement_fin.py
# (après — fichier suivant)
+++ b/scripts/traitement_fin.py
# ── Zone modifiée : ligne 22 (7 ligne(s)) dans l'ancienne version → ligne 22 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -22,7 +22,11 @@ exponentielle décroissante ; voir #437 et sa révocation). Ce seul fichier
 pilote le son pour TOUS les projets utilisant ce script partagé (via
 `SCRIPT_BIP`), sans avoir à toucher aux `configs/*.conf` individuels. Fichier
 absent, illisible, ou contenant une valeur non reconnue → défaut inchangé
-(`plat`), pour ne rien casser silencieusement.
+(`plat`), pour ne rien casser silencieusement. Depuis l'issue #527, ce fichier
+n'a plus besoin d'être édité à la main : un interrupteur GLOBAL dans le
+panneau flottant Infrastructure de `new_issue.py` (`#pl-zone-son`, routes
+GET/POST `/son-actif` dans `app/son.py`) l'écrit directement, effectif au bip
+suivant sans redémarrage d'aucun processus.
 
 Tonalité par projet (issue #526) : `--tonalite <demi-tons>` décale la
 fréquence de synthèse (`f_effective = f_base × 2^(demi-tons/12)`), appliqué
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index f16d104..68f9403 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 341 (6 ligne(s)) dans l'ancienne version → ligne 341 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -341,6 +341,15 @@ button.danger:hover{background:#f8d7da}
    laisser un espace blanc inutile dans le panneau. */
 .pl-zone-extras{margin:10px 0}
 .pl-zone-extras:empty{display:none;margin:0}
+/* Interrupteur global plat/cloche du bip (issue #527) : sélecteur segmenté à
+   deux positions, même esprit que .filtre-projet mais sans pastille. */
+.pl-zone-son{margin:10px 0;padding-bottom:10px;border-bottom:1px solid #e0dfda}
+.pl-son-segmente{display:inline-flex;border:1px solid #ccc;border-radius:6px;overflow:hidden}
+.pl-son-opt{padding:3px 9px;font-size:12px;border:none;border-right:1px solid #ccc;
+  background:#fff;color:#333;cursor:pointer}
+.pl-son-opt:last-child{border-right:none}
+.pl-son-opt:hover{background:#eee}
+.pl-son-opt.actif{background:#185FA5;color:#fff}
 .pl-sep{border:none;border-top:1px solid #e0dfda;margin:14px 0}
 .pl-actions{display:flex;flex-direction:column;gap:8px}
 .pl-actions button{width:100%}
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index ef2fda5..f74c835 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1924 (7 ligne(s)) dans l'ancienne version → ligne 1924 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1924,7 +1924,7 @@ function demarrerStreamFinIssue() {
 
 // ─── Panneau latéral droit de l'onglet Résultats (issue #375, #377, #380) ──
 // Panneau FLOTTANT (position:fixed, voir .panneau-lateral dans style.css),
-// basculé par #pl-toggle, trois zones EMPILÉES, non exclusives, pilotées par
+// basculé par #pl-toggle, zones EMPILÉES, non exclusives, pilotées par
 // projetCourant/numeroCourant (mêmes variables que la sélection de ligne,
 // voir selectionnerLigne) :
 //  - zone haute (#pl-zone-monitoring) : monitoring passif des watchers CCL+CCW
# ── Zone modifiée : ligne 1932 (6 ligne(s)) dans l'ancienne version → ligne 1932 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1932,6 +1932,11 @@ function demarrerStreamFinIssue() {
 //    rendue, sélection ou non — pour garder l'infra sous les yeux en
 //    travaillant sur une issue (issue #377), une ligne par watcher, noir et
 //    blanc, bouton individuel Lancer/Relancer (issue #380) ;
+//  - #pl-zone-son (issue #527) : interrupteur global plat/cloche du bip, voir
+//    initZoneSon()/choisirSonActif()/testerSonActif() ci-dessous — seule zone
+//    de ce panneau NON reconstruite à chaque cycle de
+//    rafraichirPanneauLateralResultats (initialisée une fois, se met à jour
+//    elle-même au clic) ;
 //  - zone médiane (#pl-zone-extras) : réservée aux futurs boutons (issue
 //    #380), occupée depuis l'issue #485 par le contrôle du watcher spool
 //    (issues_inbox) — rendrePanneauLateralExtras(), fetch /issues-inbox/etat ;
# ── Zone modifiée : ligne 1972 (6 ligne(s)) dans l'ancienne version → ligne 1977 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1972,6 +1977,7 @@ function mettreAJourToggleLateral() {
 function demarrerPanneauLateral() {
   ouvrirPanneauLateralParDefaut();
   rafraichirPanneauLateralResultats();
+  initZoneSon();
   arreterPanneauLateral();
   intervalPanneauLateral = setInterval(rafraichirPanneauLateralResultats, 30000);
 }
# ── Zone modifiée : ligne 2145 (6 ligne(s)) dans l'ancienne version → ligne 2151 (59 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2145,6 +2151,59 @@ async function rendrePanneauLateralMonitoring() {
   zone.innerHTML = html;
 }
 
+// ─── Interrupteur global plat/cloche du bip (#pl-zone-son, issue #527) ─────
+// GLOBAL (pas par projet — voir scripts/son_actif.txt, lu par TOUS les
+// projets via le script partagé), distinct de la tonalité par projet
+// (TONALITE_BIP, onglet Configuration, issue #526) : la tonalité décale la
+// fréquence des DEUX timbres plat/cloche, elle ne choisit pas entre eux.
+// Initialisé une seule fois par demarrerPanneauLateral() (pas à chaque cycle
+// de rafraichirPanneauLateralResultats) — cette zone est la seule source
+// d'écriture de son_actif.txt depuis l'interface, rien ne peut la faire
+// diverger de l'état serveur entre deux chargements de page.
+async function initZoneSon() {
+  const seg = document.getElementById('pl-son-segmente');
+  if (!seg) return;
+  let son = 'plat';
+  try {
+    const rep = await fetch('/son-actif');
+    const donnees = await rep.json();
+    if (donnees && (donnees.son === 'plat' || donnees.son === 'cloche')) son = donnees.son;
+  } catch(e) { /* défaut 'plat' conservé */ }
+  refleterSonActif(son);
+}
+
+function refleterSonActif(son) {
+  const optPlat   = document.getElementById('pl-son-opt-plat');
+  const optCloche = document.getElementById('pl-son-opt-cloche');
+  if (optPlat)   optPlat.classList.toggle('actif', son === 'plat');
+  if (optCloche) optCloche.classList.toggle('actif', son === 'cloche');
+}
+
+// Écrit le choix dans son_actif.txt au clic — effectif au bip suivant, sans
+// rechargement de page (traitement_fin.py relit le fichier à chaque bip).
+async function choisirSonActif(son) {
+  refleterSonActif(son);   // optimiste : réactivité immédiate au clic
+  try {
+    await fetch('/son-actif', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({son: son})
+    });
+  } catch(e) {
+    alert('Erreur réseau : ' + e.message);
+  }
+}
+
+// Joue le bip avec le timbre actuellement enregistré dans son_actif.txt
+// (même principe que testerBip() pour la tonalité par projet, issue #526).
+async function testerSonActif() {
+  try {
+    await fetch('/tester-son', {method: 'POST'});
+  } catch(e) {
+    alert('Erreur réseau : ' + e.message);
+  }
+}
+
 // Zone réservée #pl-zone-extras (issue #380), occupée depuis l'issue #485 par
 // le contrôle du watcher spool issues_inbox (scripts/watcher_issues_inbox.py)
 // — un seul watcher, pas de paramètre projet, contrairement aux watchers CCL
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 0337733..52950f5 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 269 (12 ligne(s)) dans l'ancienne version → ligne 269 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -269,12 +269,21 @@
     <!-- Panneau flottant de monitoring (issue #375, #376, #377, refonte
          overlay lisible #380) : position:fixed (voir .panneau-lateral,
          style.css), basculé par #pl-toggle, ouvert par défaut à l'entrée dans
-         l'onglet (ouvrirPanneauLateralParDefaut). Trois zones empilées,
-         peuplées par rafraichirPanneauLateralResultats() (static/js/app.js)
-         — jamais rempli côté serveur.
+         l'onglet (ouvrirPanneauLateralParDefaut). Zones empilées, peuplées
+         par rafraichirPanneauLateralResultats() (static/js/app.js) — jamais
+         remplies côté serveur, à l'exception de #pl-zone-son ci-dessous.
          - #pl-zone-monitoring : monitoring de l'infrastructure, TOUJOURS
            visible, une ligne par watcher CCL/service CCW (VM CCW, watchers
            CCL, services CCW).
+         - #pl-zone-son (issue #527) : interrupteur global plat/cloche du bip
+           + test immédiat. GLOBAL (pas par projet, contrairement à la
+           tonalité de l'onglet Configuration, issue #526) — TOUJOURS visible,
+           initialisé une seule fois au chargement (initZoneSon(),
+           static/js/app.js) et mis à jour par ses propres handlers au clic,
+           PAS reconstruit à chaque cycle de rafraichirPanneauLateralResultats
+           (contrairement aux autres zones ci-dessous) : rien ne le ferait
+           diverger de l'état réel puisque cette zone est la seule à écrire
+           dans son_actif.txt depuis l'interface.
          - #pl-zone-extras : zone réservée aux futurs boutons (issue #380),
            occupée depuis l'issue #485 par le contrôle du watcher spool
            (issues_inbox) — rendrePanneauLateralExtras() (static/js/app.js).
# ── Zone modifiée : ligne 282 (6 ligne(s)) dans l'ancienne version → ligne 291 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -282,6 +291,17 @@
            vide (donc invisible) tant qu'aucune ligne n'est sélectionnée. -->
     <div id="panneau-lateral-resultats" class="panneau-lateral">
       <div id="pl-zone-monitoring"></div>
+      <div id="pl-zone-son" class="pl-zone-son">
+        <div class="pl-resume-titre">Son du bip</div>
+        <div class="pl-ligne">
+          <span class="pl-ligne-libelle">Timbre</span>
+          <span class="pl-son-segmente" id="pl-son-segmente">
+            <button type="button" class="pl-son-opt" id="pl-son-opt-plat" onclick="choisirSonActif('plat')">Plat</button>
+            <button type="button" class="pl-son-opt" id="pl-son-opt-cloche" onclick="choisirSonActif('cloche')">Cloche</button>
+          </span>
+          <button type="button" class="pl-btn-mini" onclick="testerSonActif()">Tester le son</button>
+        </div>
+      </div>
       <!-- Zone réservée aux futurs boutons (issue #380) : vide intentionnellement. -->
       <div id="pl-zone-extras" class="pl-zone-extras"></div>
       <div id="pl-zone-actions"></div>
