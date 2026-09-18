19f9eb5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 19f9eb5
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 09:43:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #296 (suite #295) : panneau France pleine hauteur, tuiles titre/sous-titre, étiquettes drapeaux retirées, "Parties en cours"
    
    Cinq ajustements sur l'accueil, tous vérifiés par capture WebKitGTK
    (scripts/_harness_jeu/verif_296_webkitgtk.py, i296_*.png) :
    
    1. `.container` passe en fond blanc + border-radius + overflow:hidden en
       mode France (body:not(.mode-belgicisme)), couvrant désormais toute la
       hauteur du contenu (titre inclus), symétrique au panneau translucide
       ::before du mode Belgicisme. Corrige au passage `.message-limite`, qui
       reposait implicitement sur le tapis vert (rose clair devenu illisible sur
       le nouveau fond blanc).
    
    2. Les tuiles du titre "Scrabble" (header h1 .lettre-scrabble) perdent leur
       scope `body.mode-belgicisme` et s'affichent désormais dans les deux
       modes, sur fond blanc. Retire aussi le margin-bottom dupliqué entre les
       deux règles `header h1` qui coexistaient (conflit de cascade à spécificité
       égale, silencieux avant que les deux règles ne s'appliquent aux mêmes
       modes).
    
    3. Sous-titre "Configuration de la partie" transformé en tuiles
       lettre par lettre (nouvelle classe `.sous-titre-tuiles`, plus petite que
       le titre principal), séparateurs de mots via `.fin-mot` (margin-right).
       Premier jet incomplet (ne posait que la taille, en s'appuyant à tort sur
       un style de base inexistant) détecté par capture WebKitGTK et corrigé
       avant ce commit — voir le style complet fond/bordure/relief ajouté à
       `.sous-titre-tuiles .lettre-scrabble`.
    
    4. Étiquettes texte "France"/"Belgique" retirées sous les cercles-drapeaux ;
       cercles et logique JS de sélection inchangés (aria-label/title portent
       déjà la même information).
    
    5. Titre de section "Continuer" (9 tuiles) remplacé par "Parties en cours"
       (14 tuiles + 2 séparateurs `.fin-mot`) : tient confortablement dans la
       zone centrale même à 700px de large, capture à l'appui.
    
    Nettoyage associé : suppression des règles CSS mortes `.subtitle` et
    `.drapeau-legende` (classes disparues du HTML).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/_harness_jeu/i296_belgique_rempli_1280x800_webkitgtk.png b/scripts/_harness_jeu/i296_belgique_rempli_1280x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..505eaef
Binary files /dev/null and b/scripts/_harness_jeu/i296_belgique_rempli_1280x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_belgique_rempli_700x800_webkitgtk.png b/scripts/_harness_jeu/i296_belgique_rempli_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..dcc21f1
Binary files /dev/null and b/scripts/_harness_jeu/i296_belgique_rempli_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_belgique_vide_700x800_webkitgtk.png b/scripts/_harness_jeu/i296_belgique_vide_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..8c0d9ca
Binary files /dev/null and b/scripts/_harness_jeu/i296_belgique_vide_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_france_rempli_1280x800_webkitgtk.png b/scripts/_harness_jeu/i296_france_rempli_1280x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..c443a8e
Binary files /dev/null and b/scripts/_harness_jeu/i296_france_rempli_1280x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_france_rempli_700x800_webkitgtk.png b/scripts/_harness_jeu/i296_france_rempli_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..37244d3
Binary files /dev/null and b/scripts/_harness_jeu/i296_france_rempli_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_france_vide_700x800_webkitgtk.png b/scripts/_harness_jeu/i296_france_vide_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..6da642d
Binary files /dev/null and b/scripts/_harness_jeu/i296_france_vide_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/verif_296_webkitgtk.py b/scripts/_harness_jeu/verif_296_webkitgtk.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..0807560
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/scripts/_harness_jeu/verif_296_webkitgtk.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (188 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,188 @@
+"""Vérification issue #296 (suite #295) sous WebKitGTK : panneau blanc
+France pleine hauteur, tuiles titre/sous-titre dans les deux modes,
+disparition des étiquettes "France"/"Belgique" sous les cercles-drapeaux,
+et nouveau titre de section "Parties en cours".
+
+Repris de verif_belgicisme_292_webkitgtk.py (même mock d'API, même mécanique
+de capture via webkit_web_view_get_snapshot). cf. bug #295 : toujours passer
+un chemin de sortie ABSOLU en argument, sinon les captures atterrissent dans
+le répertoire courant du process plutôt que dans SORTIE.
+
+Usage : /usr/bin/python3 verif_296_webkitgtk.py <dossier_sortie_absolu>
+"""
+import pathlib
+import sys
+
+import gi
+
+gi.require_version("Gtk", "3.0")
+gi.require_version("WebKit2", "4.1")
+from gi.repository import GLib, Gtk, WebKit2  # noqa: E402
+
+ICI = pathlib.Path(__file__).resolve().parent
+WEB = ICI.parent.parent / "src" / "scrabble" / "ui" / "web"
+SORTIE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ICI
+
+MOCK_JS_VIDE = """
+window.pywebview = { platform: 'test' };
+window.__appelsMode = [];
+setTimeout(() => {
+  window.pywebview.api = {
+    obtenir_etat: async () => ({
+      joueurs: [],
+      nb_humains: 0, nb_ordinateurs: 0, nb_total: 0,
+      peut_ajouter_humain: true, peut_ajouter_ordinateur: true, peut_lancer: false,
+      mode_belgicisme: false,
+    }),
+    obtenir_niveaux: async () => ['Débutant','Facile','Intermédiaire','Expert'],
+    lister_parties_en_cours: async () => [],
+    obtenir_prenom_principal: async () => 'Alain',
+    definir_mode_belgicisme: async (actif) => {
+      window.__appelsMode.push(actif);
+      return { succes: true, mode_belgicisme: actif };
+    },
+  };
+  window.dispatchEvent(new Event('pywebviewready'));
+}, 100);
+"""
+
+MOCK_JS_REMPLI = """
+window.pywebview = { platform: 'test' };
+window.__appelsMode = [];
+setTimeout(() => {
+  window.pywebview.api = {
+    obtenir_etat: async () => ({
+      joueurs: [
+        {nom:'Alain', humain:true, niveau:null},
+        {nom:'Béatrice', humain:true, niveau:null},
+        {nom:'Ordinateur 1', humain:false, niveau:'avance'},
+        {nom:'Ordinateur 2', humain:false, niveau:'expert'},
+      ],
+      nb_humains: 2, nb_ordinateurs: 2, nb_total: 4,
+      peut_ajouter_humain: false, peut_ajouter_ordinateur: false, peut_lancer: true,
+      mode_belgicisme: false,
+    }),
+    obtenir_niveaux: async () => ['Débutant','Facile','Intermédiaire','Expert'],
+    lister_parties_en_cours: async () => [
+      {
+        id: 1,
+        date_maj: '2026-07-20T14:32:00',
+        terminee: false,
+        joueurs: [{nom:'Alain', score: 84}, {nom:'Béatrice', score: 91}],
+      },
+      {
+        id: 2,
+        date_maj: '2026-07-18T09:05:00',
+        terminee: true,
+        joueurs: [{nom:'Alain', score: 312}, {nom:'Ordinateur 1', score: 289}],
+      },
+    ],
+    obtenir_prenom_principal: async () => 'Alain',
+    definir_mode_belgicisme: async (actif) => {
+      window.__appelsMode.push(actif);
+      return { succes: true, mode_belgicisme: actif };
+    },
+  };
+  window.dispatchEvent(new Event('pywebviewready'));
+}, 100);
+"""
+
+
+def construire_mock(mock_js, nom_tmp):
+    css = (WEB / "accueil.css").read_text()
+    css = css.replace("url(images/", f"url(file://{WEB / 'images'}/")
+    js = (WEB / "accueil.js").read_text()
+    html = (WEB / "accueil.html").read_text()
+    html = html.replace(
+        '<link rel="stylesheet" href="accueil.css">', f"<style>{css}</style>"
+    )
+    html = html.replace(
+        '<script src="accueil.js"></script>',
+        f"<script>{mock_js}</script><script>{js}</script>",
+    )
+    chemin = SORTIE / nom_tmp
+    chemin.write_text(html)
+    return chemin
+
+
+def capturer(url, largeur, hauteur, sortie_png, sequence_clics):
+    win = Gtk.Window()
+    win.set_default_size(largeur, hauteur)
+    webview = WebKit2.WebView()
+    win.add(webview)
+    win.show_all()
+
+    etape = {"i": 0}
+
+    def apres_chargement(view, event):
+        if event == WebKit2.LoadEvent.FINISHED and etape["i"] == 0:
+            etape["i"] = 1
+            GLib.timeout_add(400, lambda: jouer_sequence(0))
+
+    def jouer_sequence(i):
+        if i >= len(sequence_clics):
+            GLib.timeout_add(700, prendre_snapshot)
+            return False
+        webview.run_javascript(
+            f"document.querySelector('{sequence_clics[i]}').click();",
+            None, None, None,
+        )
+        GLib.timeout_add(250, lambda: jouer_sequence(i + 1))
+        return False
+
+    def prendre_snapshot():
+        webview.get_snapshot(
+            WebKit2.SnapshotRegion.FULL_DOCUMENT,
+            WebKit2.SnapshotOptions.NONE,
+            None, snapshot_pret, None,
+        )
+        return False
+
+    def snapshot_pret(view, result, data):
+        surface = webview.get_snapshot_finish(result)
+        surface.write_to_png(str(sortie_png))
+        win.destroy()
+        if minuterie["id"] is not None:
+            GLib.source_remove(minuterie["id"])
+            minuterie["id"] = None
+        Gtk.main_quit()
+
+    minuterie = {"id": None}
+    webview.connect("load-changed", apres_chargement)
+    webview.load_uri("file://" + url)
+    minuterie["id"] = GLib.timeout_add(15000, Gtk.main_quit)
+    Gtk.main()
+
+
+if __name__ == "__main__":
+    largeurs = [700, 1280]
+
+    mock_vide = construire_mock(MOCK_JS_VIDE, "_i296_mock_vide_tmp.html")
+    url_vide = str(mock_vide)
+
+    print("Capture France 700x800 (vide)...")
+    capturer(url_vide, 700, 800,
+             SORTIE / "i296_france_vide_700x800.png", [])
+
+    print("Capture Belgique 700x800 (vide)...")
+    capturer(url_vide, 700, 800,
+             SORTIE / "i296_belgique_vide_700x800.png", ["#drapeau-belgique"])
+
+    mock_vide.unlink()
+
+    mock_rempli = construire_mock(MOCK_JS_REMPLI, "_i296_mock_rempli_tmp.html")
+    url_rempli = str(mock_rempli)
+
+    for largeur in largeurs:
+        print(f"Capture France {largeur}x800 (rempli)...")
+        capturer(url_rempli, largeur, 800,
+                 SORTIE / f"i296_france_rempli_{largeur}x800.png", [])
+
+        print(f"Capture Belgique {largeur}x800 (rempli)...")
+        capturer(url_rempli, largeur, 800,
+                 SORTIE / f"i296_belgique_rempli_{largeur}x800.png",
+                 ["#drapeau-belgique"])
+
+    mock_rempli.unlink()
+
+    print("Captures écrites dans", SORTIE)
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# (index — ignorable)
index 75ad74d..84723d9 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.css
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 232 (9 ligne(s)) dans l'ancienne version → ligne 232 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -232,9 +232,10 @@ body.mode-belgicisme .container::before {
    au-dessus de `.container::before`), au-delà du seuil WCAG AA (4.5:1).
    `header h1` n'est PLUS dans cette liste depuis #290 : le titre est
    désormais composé de tuiles de Scrabble opaques par lettre (voir plus
-   bas), dont le contraste ne dépend pas de l'opacité du panneau. */
-body.mode-belgicisme .subtitle,
-body.mode-belgicisme .drapeau-legende,
+   bas), dont le contraste ne dépend pas de l'opacité du panneau.
+   `.subtitle` non plus depuis #296 (sous-titre passé en tuiles, même
+   raisonnement) ; `.drapeau-legende` a disparu du HTML au même moment
+   (étiquettes "France"/"Belgique" supprimées sous les cercles). */
 body.mode-belgicisme section h2,
 body.mode-belgicisme .compteur,
 body.mode-belgicisme .liste-joueurs .vide,
# ── Zone modifiée : ligne 256 (11 ligne(s)) dans l'ancienne version → ligne 257 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -256,11 +257,28 @@ body.mode-belgicisme .message-limite {
     text-shadow: none;
 }
 
-/* Titre en tuiles de Scrabble (issue #290), mode Belgicisme uniquement.
+/* Même correction pour le mode France (issue #296) : `.message-limite` est
+   ajouté après `.zone-boutons` (accueil.js), donc à l'intérieur de
+   `.container` — désormais peint en blanc sur toute sa hauteur en mode
+   France (voir `body:not(.mode-belgicisme) .container` plus bas). Le rose
+   clair par défaut, pensé pour le tapis vert, devient quasi invisible sur ce
+   fond blanc, comme constaté pour le mode Belgicisme en #292. */
+body:not(.mode-belgicisme) .message-limite {
+    color: var(--couleur-danger);
+    text-shadow: none;
+}
+
+/* Titre en tuiles de Scrabble (issue #290, étendu aux deux modes en #296).
    Le HTML (accueil.html) découpe "Scrabble" en 8 `<span class="lettre-
-   scrabble">` ; en mode France, aucune règle ne cible cette classe, le texte
-   s'affiche comme un h1 normal (blanc, cf. règle générale `header h1` plus
-   bas). Ici, chaque lettre devient une tuile individuelle :
+   scrabble">`. Jusqu'à #296, ce style était scopé à `body.mode-belgicisme` :
+   en mode France, aucune règle ne ciblait cette classe, le texte s'affichait
+   comme un h1 normal (blanc, cf. règle générale `header h1` plus bas). Le
+   scope est retiré depuis #296 : le panneau `.container` étant désormais
+   blanc pleine hauteur dans les deux modes (voir `body:not(.mode-
+   belgicisme) .container` plus bas), les tuiles reposent sur fond blanc en
+   France comme en Belgicisme — leur fond crème/contour doré opaques
+   restent contrastés indépendamment de la couleur derrière. Ici, chaque
+   lettre devient une tuile individuelle :
    - fond crème `#f5e6c8` (teinte jaune/crème façon tuile réelle, cohérente
      avec le jaune du drapeau belge) ;
    - contour doré `#caa02c` + ombres internes (clair en haut-gauche, sombre
# ── Zone modifiée : ligne 291 (7 ligne(s)) dans l'ancienne version → ligne 309 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -291,7 +309,7 @@ body.mode-belgicisme .message-limite {
    dans laquelle `justify-content: center` centre les tuiles, les décalant
    d'autant vers la gauche : espace réservé au bouton à toutes les largeurs
    de fenêtre, sans dépendre d'un calcul de largeur de tuiles fragile. */
-body.mode-belgicisme header h1 {
+header h1 {
     display: flex;
     justify-content: center;
     align-items: center;
# ── Zone modifiée : ligne 300 (7 ligne(s)) dans l'ancienne version → ligne 318 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -300,7 +318,7 @@ body.mode-belgicisme header h1 {
     padding-right: 56px;
 }
 
-body.mode-belgicisme header h1 .lettre-scrabble {
+header h1 .lettre-scrabble {
     display: inline-flex;
     align-items: center;
     justify-content: center;
# ── Zone modifiée : ligne 357 (6 ligne(s)) dans l'ancienne version → ligne 375 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -357,6 +375,26 @@ body.mode-belgicisme .parties-en-cours:has(.vide) {
     padding: 20px;
 }
 
+/* Panneau blanc pleine hauteur en mode France (issue #296, suite de #295) :
+   `.zone-centrale` ne couvrait que les sections Joueurs/Continuer, laissant
+   le titre et les cercles-drapeaux directement sur le tapis vert — asymétrie
+   avec le mode Belgicisme, où `.container::before` couvre déjà tout le
+   contenu (titre inclus, cf. #289). Ici on peint directement `.container`
+   plutôt que d'ajouter un pseudo-élément superposé : le mode France n'a pas
+   besoin de déborder sur les côtés comme le panneau translucide belge (pas
+   de voile tricolore à laisser transparaître dans les marges), donc pas
+   besoin du `position: relative` + `::before` + `z-index: -1` utilisés en
+   Belgicisme. `overflow: hidden` évite que les coins arrondis des enfants
+   (zone-centrale, etc.) débordent du rayon du panneau. `:not(.mode-
+   belgicisme)` exclut explicitement le mode Belgicisme : celui-ci reste géré
+   par son propre panneau translucide (`.container::before`), sans peindre
+   `.container` lui-même en blanc opaque par-dessus. */
+body:not(.mode-belgicisme) .container {
+    background: white;
+    border-radius: 16px;
+    overflow: hidden;
+}
+
 /* En-tête */
 header {
     text-align: center;
# ── Zone modifiée : ligne 392 (26 ligne(s)) dans l'ancienne version → ligne 430 (73 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -392,26 +430,73 @@ header {
     cursor: default;
 }
 
-/* Textes sur le tapis vert (issue #77, suite de #75). Le titre était en vert
-   primaire (var(--couleur-primaire)) : vert sur vert, quasi illisible depuis
-   l'ajout du fond en feutre (issue #75). On le passe en blanc franc avec une
-   ombre portée légère, reprenant EXACTEMENT le traitement du décor « SCRABBLE »
-   de l'écran de jeu (issue #70) : contraste large et confortable, pensé pour une
-   lecture aisée par un public âgé (> 80 ans). Blanc pur (#fff) sur le vert
-   #35654d ≈ 6:1, au-delà du seuil WCAG AA (4.5:1). */
+/* Texte de secours pour `header h1` (issue #77, suite de #75) : conservé au
+   cas où le h1 contiendrait un jour du texte brut plutôt que des tuiles
+   (blanc franc + ombre portée, pensé à l'origine pour le tapis vert). Depuis
+   #290/#296, le h1 ne contient plus que des `.lettre-scrabble` (tuiles
+   opaques, dans les deux modes désormais) : ni la couleur ni l'ombre ne sont
+   donc visibles en pratique. `margin-bottom` retiré d'ici (issue #296) : il
+   ferait doublon avec celui, plus généreux (14px), de la règle `header h1`
+   ci-dessous qui gère l'espacement réel du conteneur de tuiles — même
+   sélecteur, même spécificité, deux valeurs différentes auraient créé un
+   conflit d'ordre de cascade fragile. */
 header h1 {
     font-size: 2rem;
     color: #ffffff;
-    margin-bottom: 4px;
     text-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
 }
 
-/* Sous-titre : gris #666 (prévu pour un fond clair) illisible sur le vert. Blanc
-   très légèrement adouci + ombre portée pour rester net sans dureté. */
-.subtitle {
-    color: rgba(255, 255, 255, 0.92);
-    font-size: 0.95rem;
-    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
+/* Sous-titre "Configuration de la partie" en tuiles (issue #296), même
+   principe que le titre principal (`header h1`) et les titres de section
+   (`.titre-section-tuiles`) : chaque lettre est une tuile de Scrabble
+   opaque, dans les deux modes. Tuiles nettement plus petites que celles du
+   titre (clamp 0.65-0.85rem de police contre 2.2rem) — un sous-titre reste
+   un sous-titre, pas un second titre principal.
+
+   Contrairement au titre et aux titres de section, ce groupe de tuiles n'a
+   PAS de base commune à hériter (chacun des deux autres définit sa propre
+   copie complète fond/bordure/relief, aucune n'est factorisée dans une
+   règle `.lettre-scrabble` non préfixée) : la première version de cette
+   règle ne posait que la taille, en s'appuyant à tort sur un style de base
+   supposé — capture WebKitGTK à l'appui (texte plat sans tuile visible),
+   corrigé en ajoutant ici la même recette complète que les deux autres
+   groupes, à l'échelle réduite de ce sous-titre. */
+.sous-titre-tuiles {
+    display: flex;
+    flex-wrap: wrap;
+    gap: 2px;
+    justify-content: center;
+    margin: 0.3rem 0 0.6rem;
+}
+
+.sous-titre-tuiles .lettre-scrabble {
+    display: inline-flex;
+    align-items: center;
+    justify-content: center;
+    font-size: clamp(0.65rem, 1.5vw, 0.85rem);
+    width: clamp(1.1rem, 2.2vw, 1.4rem);
+    height: clamp(1.1rem, 2.2vw, 1.4rem);
+    background: #f5e6c8;
+    color: #4a3418;
+    font-weight: 700;
+    line-height: 1;
+    border-radius: 3px;
+    border: 1px solid #caa02c;
+    box-shadow:
+        inset 1px 1px 0 rgba(255, 250, 230, 0.8),
+        inset -1px -1px 0 rgba(120, 80, 10, 0.65),
+        0 1px 2px rgba(0, 0, 0, 0.3);
+}
+
+/* `.fin-mot` (issue #296) : sur la dernière lettre de chaque mot sauf le
+   dernier, dans un groupe de tuiles lettre par lettre (`.sous-titre-tuiles`
+   ou `.titre-section-tuiles`, ex. "Configuration de la partie" ou "Parties
+   en cours"). Simule l'espace inter-mots par un margin-right, faute
+   d'espace typographique visible entre des tuiles individuelles. Règle
+   générique (non préfixée) : le même balisage/la même classe sert dans les
+   deux contextes. */
+.fin-mot {
+    margin-right: 0.4rem;
 }
 
 /* Cercles-drapeaux du mode dictionnaire (issue #269), sous le sous-titre. */
# ── Zone modifiée : ligne 493 (12 ligne(s)) dans l'ancienne version → ligne 578 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -493,12 +578,6 @@ header h1 {
     text-shadow: 0 1px 3px rgba(0, 0, 0, 0.7);
 }
 
-.drapeau-legende {
-    color: rgba(255, 255, 255, 0.9);
-    font-size: 0.8rem;
-    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
-}
-
 /* Sections */
 section {
     margin-bottom: 24px;
# ── Zone modifiée : ligne 518 (13 ligne(s)) dans l'ancienne version → ligne 597 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -518,13 +597,15 @@ section h2 {
     text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
 }
 
-/* Titres de section en tuiles Scrabble (issue #295) : « Joueurs » et
-   « Continuer » reprennent le principe des tuiles du titre principal (fond
-   crème, contour doré, relief), en plus petit et alignées à gauche plutôt que
-   centrées. Contrairement aux tuiles du `header h1` (réservées au mode
-   Belgicisme, cf. commentaire plus haut), celles-ci sont volontairement NON
-   scopées à `body.mode-belgicisme` : le texte de l'issue demande qu'elles
-   s'affichent aussi en mode France, posées directement sur le tapis vert. */
+/* Titres de section en tuiles Scrabble (issue #295, « Continuer » renommé
+   « Parties en cours » en #296) : « Joueurs » et « Parties en cours »
+   reprennent le principe des tuiles du titre principal (fond crème, contour
+   doré, relief), en plus petit et alignées à gauche plutôt que centrées.
+   Non scopées à `body.mode-belgicisme` depuis l'origine (#295) : le texte de
+   l'issue demandait qu'elles s'affichent aussi en mode France, posées
+   directement sur le tapis vert — ce que fait désormais aussi `header h1`
+   depuis #296 (cf. commentaire plus haut), la distinction entre les deux
+   n'existe donc plus. */
 .titre-section-tuiles {
     display: flex;
     flex-wrap: wrap;
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.html b/src/scrabble/ui/web/accueil.html
# (index — ignorable)
index 11cb72e..367ba9d 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.html
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.html
# ── Zone modifiée : ligne 15 (16 ligne(s)) dans l'ancienne version → ligne 15 (45 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -15,16 +15,45 @@
         <header>
             <button id="btn-reglages" class="btn-reglages" title="Réglages"
                     aria-label="Réglages">⚙</button>
-            <!-- Lettres découpées en <span> individuels (issue #290) : en mode
-                 France, ce balisage est invisible (aucune règle CSS hors
-                 `body.mode-belgicisme` ne cible `.lettre-scrabble`, le texte
-                 s'affiche comme un h1 normal). En mode Belgicisme uniquement,
-                 accueil.css transforme chaque span en tuile de Scrabble
-                 individuelle (fond crème, contour doré, relief). Généré
-                 statiquement ici plutôt qu'en JS : le texte "Scrabble" est
-                 fixe, pas besoin de complexité dynamique pour 8 lettres. -->
+            <!-- Lettres découpées en <span> individuels (issue #290, tuiles
+                 étendues au mode France en #296) : accueil.css transforme
+                 chaque span en tuile de Scrabble individuelle (fond crème,
+                 contour doré, relief), dans les deux modes désormais — le
+                 panneau `.container` étant blanc pleine hauteur dans les
+                 deux modes depuis #296. Généré statiquement ici plutôt qu'en
+                 JS : le texte "Scrabble" est fixe, pas besoin de complexité
+                 dynamique pour 8 lettres. -->
             <h1><span class="lettre-scrabble">S</span><span class="lettre-scrabble">c</span><span class="lettre-scrabble">r</span><span class="lettre-scrabble">a</span><span class="lettre-scrabble">b</span><span class="lettre-scrabble">b</span><span class="lettre-scrabble">l</span><span class="lettre-scrabble">e</span></h1>
-            <p class="subtitle">Configuration de la partie</p>
+            <!-- Sous-titre en tuiles (issue #296), même principe que le titre
+                 et les titres de section : chaque lettre est une tuile
+                 individuelle ; les 4 mots sont séparés par un margin-right de
+                 0.4rem posé sur la dernière lettre de chaque mot (sauf le
+                 dernier mot), via la classe `.fin-mot` (voir accueil.css). -->
+            <p class="sous-titre-tuiles">
+              <span class="lettre-scrabble">C</span><span
+              class="lettre-scrabble">o</span><span
+              class="lettre-scrabble">n</span><span
+              class="lettre-scrabble">f</span><span
+              class="lettre-scrabble">i</span><span
+              class="lettre-scrabble">g</span><span
+              class="lettre-scrabble">u</span><span
+              class="lettre-scrabble">r</span><span
+              class="lettre-scrabble">a</span><span
+              class="lettre-scrabble">t</span><span
+              class="lettre-scrabble">i</span><span
+              class="lettre-scrabble">o</span><span
+              class="lettre-scrabble fin-mot">n</span><span
+              class="lettre-scrabble">d</span><span
+              class="lettre-scrabble fin-mot">e</span><span
+              class="lettre-scrabble">l</span><span
+              class="lettre-scrabble fin-mot">a</span><span
+              class="lettre-scrabble">p</span><span
+              class="lettre-scrabble">a</span><span
+              class="lettre-scrabble">r</span><span
+              class="lettre-scrabble">t</span><span
+              class="lettre-scrabble">i</span><span
+              class="lettre-scrabble">e</span>
+            </p>
         </header>
 
         <!-- Mode dictionnaire régional (issue #269) : choix exclusif entre le
# ── Zone modifiée : ligne 36 (19 ligne(s)) dans l'ancienne version → ligne 65 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -36,19 +65,21 @@
              couvert ici. -->
         <div class="mode-dictionnaire" role="radiogroup"
              aria-label="Mode de dictionnaire, France ou Belgique">
+            <!-- Étiquettes texte "France"/"Belgique" retirées sous les cercles
+                 (issue #296) : les cercles-drapeaux restent seuls, avec leur
+                 `aria-label`/`title` déjà porteurs du même texte pour
+                 l'accessibilité. -->
             <div class="drapeau-choix">
                 <button type="button" class="drapeau-cercle drapeau-france actif"
                         id="drapeau-france" role="radio" aria-checked="true"
                         aria-label="Dictionnaire France (choix par défaut)"
                         title="Dictionnaire France"></button>
-                <span class="drapeau-legende">France</span>
             </div>
             <div class="drapeau-choix">
                 <button type="button" class="drapeau-cercle drapeau-belgique"
                         id="drapeau-belgique" role="radio" aria-checked="false"
                         aria-label="Mode Belgicisme (Belgique)"
                         title="Mode Belgicisme"></button>
-                <span class="drapeau-legende">Belgique</span>
             </div>
         </div>
 
# ── Zone modifiée : ligne 81 (16 ligne(s)) dans l'ancienne version → ligne 112 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -81,16 +112,26 @@
                 </section>
 
                 <section class="reprise" id="section-reprise">
+                    <!-- "Continuer" (9 tuiles) remplacé par "Parties en cours"
+                         (issue #296) : 14 lettres tiennent confortablement
+                         dans la zone centrale même à 700px de large (cf.
+                         rapport). `.fin-mot` sépare les 3 mots (voir
+                         accueil.css). -->
                     <h2 class="titre-section-tuiles">
-                      <span class="lettre-scrabble">C</span><span
-                      class="lettre-scrabble">o</span><span
-                      class="lettre-scrabble">n</span><span
+                      <span class="lettre-scrabble">P</span><span
+                      class="lettre-scrabble">a</span><span
+                      class="lettre-scrabble">r</span><span
                       class="lettre-scrabble">t</span><span
                       class="lettre-scrabble">i</span><span
-                      class="lettre-scrabble">n</span><span
-                      class="lettre-scrabble">u</span><span
                       class="lettre-scrabble">e</span><span
-                      class="lettre-scrabble">r</span>
+                      class="lettre-scrabble fin-mot">s</span><span
+                      class="lettre-scrabble">e</span><span
+                      class="lettre-scrabble fin-mot">n</span><span
+                      class="lettre-scrabble">c</span><span
+                      class="lettre-scrabble">o</span><span
+                      class="lettre-scrabble">u</span><span
+                      class="lettre-scrabble">r</span><span
+                      class="lettre-scrabble">s</span>
                     </h2>
                     <div id="parties-en-cours" class="parties-en-cours">
                         <p class="vide">Aucune partie enregistrée.</p>
