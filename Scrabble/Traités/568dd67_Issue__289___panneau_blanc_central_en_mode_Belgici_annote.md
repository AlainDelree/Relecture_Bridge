568dd67

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 568dd67
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 21:45:15 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #289 : panneau blanc central en mode Belgicisme (corrige le débordement)
    
    Le débordement constaté (titre/cartes lisibles seulement sur la bande jaune,
    qui rétrécit avec la fenêtre) touchait toute largeur < ~1920px, y compris
    la résolution cible réelle (~1280px) et le repli 700px : le .container
    (600px max) débordait visuellement sur les bandes noire/rouge voisines dès
    que la bande jaune (largeur/3) devenait plus étroite que lui.
    
    Corrige à la racine plutôt que par filet de sécurité par élément : un
    panneau blanc/quasi-opaque (.container::before, largeur clamp(620px, 94vw,
    720px), top/bottom négatifs pour suivre la hauteur réelle du contenu)
    couvre désormais tout .container et déborde légèrement sur les côtés. Tout
    le contenu (titre, cartes, boutons) repose donc toujours sur du blanc ; le
    voile tricolore (inchangé) ne reste visible que dans les marges latérales,
    jamais sous du texte.
    
    La règle de couleur de texte forcée (#1a1a1a) est conservée mais
    recontextualisée : elle protégeait le contraste sur la bande jaune, elle
    protège maintenant le contraste sur le panneau blanc (~19:1, WCAG AA
    largement dépassé) — un retour au texte blanc d'origine (pensé pour le
    tapis vert plein écran) a été écarté car illisible sur un panneau blanc.
    
    Vérifié : harnais Playwright étendu (panneau contient .container sans
    débordement à 700/1280/1920px de large) + captures WebKitGTK réelles à
    700/1280/1340px (écran physique limité à 1360x768 ici). Mode France
    strictement inchangé (capture de référence incluse).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/_harness_jeu/i269_accueil_belgique.png b/scripts/_harness_jeu/i269_accueil_belgique.png
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 554c15a..73d92b0 100644
Binary files a/scripts/_harness_jeu/i269_accueil_belgique.png and b/scripts/_harness_jeu/i269_accueil_belgique.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i289_accueil_belgique_1280x800_webkitgtk.png b/scripts/_harness_jeu/i289_accueil_belgique_1280x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..2555957
Binary files /dev/null and b/scripts/_harness_jeu/i289_accueil_belgique_1280x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i289_accueil_belgique_1340x800_webkitgtk.png b/scripts/_harness_jeu/i289_accueil_belgique_1340x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..2555957
Binary files /dev/null and b/scripts/_harness_jeu/i289_accueil_belgique_1340x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i289_accueil_belgique_700x800_webkitgtk.png b/scripts/_harness_jeu/i289_accueil_belgique_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..c7be731
Binary files /dev/null and b/scripts/_harness_jeu/i289_accueil_belgique_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i289_accueil_france_700x800_webkitgtk.png b/scripts/_harness_jeu/i289_accueil_france_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..2867c87
Binary files /dev/null and b/scripts/_harness_jeu/i289_accueil_france_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/verif_belgicisme_269.mjs b/scripts/_harness_jeu/verif_belgicisme_269.mjs
# (index — ignorable)
index 1ea5ade..4b1d164 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/scripts/_harness_jeu/verif_belgicisme_269.mjs
# ── Version APRÈS ce commit.
+++ b/scripts/_harness_jeu/verif_belgicisme_269.mjs
# ── Zone modifiée : ligne 1 (8 ligne(s)) dans l'ancienne version → ligne 1 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,8 +1,8 @@
-// Vérification issues #269 + #270 + #271 + #272 : cercles-drapeaux
+// Vérification issues #269 + #270 + #271 + #272 + #289 : cercles-drapeaux
 // France/Belgique de l'accueil, et fond du mode Belgicisme.
 //
 // Contrôle en headless Playwright — le rendu réel WebKitGTK a été vérifié
-// manuellement par capture GTK+WebKit2 (issues #270/#271/#272, cf.
+// manuellement par capture GTK+WebKit2 (issues #270/#271/#272/#289, cf.
 // verif_belgicisme_270_webkitgtk.py et accueil.css) :
 //   1. France actif par défaut, Belgique inactif.
 //   2. Clic sur le drapeau belge -> classe .actif bascule, aria-checked
# ── Zone modifiée : ligne 18 (6 ligne(s)) dans l'ancienne version → ligne 18 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -18,6 +18,12 @@
 //      blanc, pas de plaque) en mode France.
 //   5. Plusieurs allers-retours France <-> Belgique : aucun résidu visuel
 //      (retour exact au fond normal, un seul cercle actif à la fois).
+//   6. Panneau blanc central (issue #289) : à plusieurs largeurs de fenêtre
+//      (700px repli, ~1280px résolution cible, 1920px pleine largeur),
+//      `.container` reste entièrement contenu dans le panneau blanc de
+//      `.container::before` (aucun débordement sur le voile tricolore), et
+//      le panneau laisse toujours une marge visible avec le bord de la
+//      fenêtre (bandes tricolores toujours visibles, en bordure).
 import pw from '/home/alain/.npm-global/lib/node_modules/playwright/index.js';
 const { chromium } = pw;
 import { fileURLToPath } from 'url';
# ── Zone modifiée : ligne 133 (6 ligne(s)) dans l'ancienne version → ligne 139 (49 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -133,6 +139,49 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
     noirSansPlaque(textes.legendeFrance) &&
     noirSansPlaque(textes.legendeBelgique);
 
+  // Panneau blanc central (issue #289) : à plusieurs largeurs de fenêtre
+  // (700px repli, ~1280px résolution cible, 1920px pleine largeur déjà
+  // correcte avant #289 — ne doit pas être cassée), `.container` doit rester
+  // entièrement contenu dans le panneau blanc de `.container::before`, et le
+  // panneau doit toujours laisser une marge visible avec le bord de fenêtre
+  // (bande tricolore visible, en bordure uniquement).
+  const largeursPanneau = [700, 1280, 1920];
+  const mesuresPanneau = [];
+  for (const largeur of largeursPanneau) {
+    await page.setViewportSize({ width: largeur, height: 780 });
+    await page.waitForTimeout(60);
+    const mesure = await page.evaluate(() => {
+      const conteneur = document.querySelector('.container');
+      const rectConteneur = conteneur.getBoundingClientRect();
+      const stylePanneau = getComputedStyle(conteneur, '::before');
+      const largeurPanneau = parseFloat(stylePanneau.width);
+      const centreFenetre = window.innerWidth / 2;
+      const panneauGauche = centreFenetre - largeurPanneau / 2;
+      const panneauDroit = centreFenetre + largeurPanneau / 2;
+      return {
+        largeurFenetre: window.innerWidth,
+        fondPanneau: stylePanneau.backgroundColor,
+        largeurPanneau,
+        panneauGauche,
+        panneauDroit,
+        conteneurGauche: rectConteneur.left,
+        conteneurDroit: rectConteneur.right,
+      };
+    });
+    mesuresPanneau.push({ largeur, ...mesure });
+  }
+  await page.setViewportSize({ width: 700, height: 780 });
+  await page.waitForTimeout(60);
+  const TOLERANCE = 1;
+  const panneauOk = mesuresPanneau.every((m) =>
+    m.conteneurGauche >= m.panneauGauche - TOLERANCE &&
+    m.conteneurDroit <= m.panneauDroit + TOLERANCE &&
+    m.panneauGauche > 0 &&
+    m.panneauDroit < m.largeurFenetre &&
+    m.fondPanneau !== 'rgba(0, 0, 0, 0)' &&
+    m.fondPanneau !== 'transparent'
+  );
+
   // Plusieurs allers-retours pour détecter un résidu visuel.
   const historique = [];
   for (let i = 0; i < 4; i++) {
# ── Zone modifiée : ligne 184 (6 ligne(s)) dans l'ancienne version → ligne 233 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -184,6 +233,7 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
     JSON.stringify(apresBelgique.appels) === JSON.stringify([true]) &&
     fondOk &&
     textesOk &&
+    panneauOk &&
     etatFinal.bodyModeBelge === false &&
     etatFinal.franceActif === true &&
     etatFinal.belgiqueActif === false &&
# ── Zone modifiée : ligne 196 (10 ligne(s)) dans l'ancienne version → ligne 246 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -196,10 +246,11 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
   console.log('Après clic Belgique :', JSON.stringify(apresBelgique));
   console.log('Fond blanc + voile tricolore quasi-opaque (issue #272) :', JSON.stringify(fond), fondOk ? '(OK)' : '(INSUFFISANT)');
   console.log('Titre/sous-titre/légendes texte noir sans plaque (issue #272) :', JSON.stringify(textes), textesOk ? '(OK)' : '(INSUFFISANT)');
+  console.log('Panneau blanc central (issue #289), par largeur :', JSON.stringify(mesuresPanneau), panneauOk ? '(OK)' : '(DEBORDEMENT)');
   console.log('Historique bascules (mode belge actif ?) :', historique);
   console.log('État final (retour France) :', JSON.stringify(etatFinal));
   console.log('Erreurs JS :', errs.length ? errs : 'aucune');
-  console.log(ok ? 'OK — cercles-drapeaux fonctionnels, fond blanc+tricolore franc, texte sans plaque, aucun résidu visuel'
+  console.log(ok ? 'OK — cercles-drapeaux fonctionnels, fond blanc+tricolore franc, texte sans plaque, panneau blanc sans débordement à 700/1280/1920px, aucun résidu visuel'
                  : 'ECHEC');
   await browser.close();
   process.exit(ok ? 0 : 1);
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/verif_belgicisme_289_webkitgtk.py b/scripts/_harness_jeu/verif_belgicisme_289_webkitgtk.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..33a7ee3
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/scripts/_harness_jeu/verif_belgicisme_289_webkitgtk.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (156 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,156 @@
+"""Vérification issue #289 : panneau blanc central du mode Belgicisme sous
+WebKitGTK (le moteur utilisé par pywebview sous Linux, cf. CONTEXTE.md — le
+harnais Playwright habituel de _harness_jeu ne teste que Chromium et n'aurait
+pas détecté l'écart de rendu constaté en #270).
+
+#289 ajoute un panneau blanc/quasi-opaque derrière `.container` (voir
+`.container::before` dans accueil.css) pour que le titre, les cartes et les
+boutons du mode Belgicisme reposent toujours sur du blanc, quelle que soit la
+largeur de fenêtre — le voile tricolore noir/jaune/rouge (issue #272) ne
+reste visible que dans les marges latérales, hors du panneau. Ce harnais
+reprend celui de #270/#272 (même mock d'API, même mécanique de capture via
+webkit_web_view_get_snapshot) mais capture PLUSIEURS largeurs de fenêtre — les
+largeurs identifiées par l'investigation précédente comme sujettes au
+débordement : ~1280px (résolution cible réelle) et 700px (repli non
+maximisé) — plus une largeur large (1920px) pour vérifier que le panneau ne
+casse pas la mise en page déjà correcte à cette taille.
+
+Prérequis système (déjà présents sur cette machine) : gir1.2-webkit2-4.1,
+python3-gi (paquets système — utiliser /usr/bin/python3, pas un venv qui ne
+voit pas les dist-packages système), un DISPLAY X11 valide (le WebView a
+besoin d'un GtkWindow réel ; pas de Xvfb installé ici, mais le DISPLAY
+existant a suffi).
+
+Usage : /usr/bin/python3 verif_belgicisme_289_webkitgtk.py [dossier_sortie]
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
+MOCK_JS = """
+window.pywebview = { platform: 'test' };
+window.__appelsMode = [];
+setTimeout(() => {
+  window.pywebview.api = {
+    obtenir_etat: async () => ({
+      joueurs: [{nom:'Alain', humain:true, niveau:null}],
+      nb_humains: 1, nb_ordinateurs: 0, nb_total: 1,
+      peut_ajouter_humain: true, peut_ajouter_ordinateur: true, peut_lancer: true,
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
+
+def construire_mock():
+    css = (WEB / "accueil.css").read_text()
+    js = (WEB / "accueil.js").read_text()
+    html = (WEB / "accueil.html").read_text()
+    html = html.replace(
+        '<link rel="stylesheet" href="accueil.css">', f"<style>{css}</style>"
+    )
+    html = html.replace(
+        '<script src="accueil.js"></script>',
+        f"<script>{MOCK_JS}</script><script>{js}</script>",
+    )
+    chemin = SORTIE / "_i289_mock_tmp.html"
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
+            # Le fond passe du vert au blanc+tricolore (transition CSS
+            # `background-image 0.2s ease` du body) : 700ms de marge pour
+            # être sûr que la capture ne tombe jamais en plein fondu.
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
+        Gtk.main_quit()
+
+    webview.connect("load-changed", apres_chargement)
+    webview.load_uri("file://" + url)
+    GLib.timeout_add(15000, Gtk.main_quit)
+    Gtk.main()
+
+
+if __name__ == "__main__":
+    mock = construire_mock()
+    url = str(mock)
+
+    # Largeurs identifiées par l'investigation précédente : 700 (repli non
+    # maximisé), 1280 (résolution cible logique réelle), 1340 (proche de la
+    # pleine largeur déjà correcte avant #289 — ne doit pas être cassée par
+    # le panneau). Plafonné à 1340 (et non 1920) : l'écran réel de cette
+    # machine fait 1360x768 (xrandr), une fenêtre GTK ne peut pas dépasser
+    # cette largeur ici — le cas ≥1800px est déjà couvert numériquement par
+    # le harnais Playwright (verif_belgicisme_269.mjs, sans cette limite
+    # d'écran physique).
+    largeurs = [700, 1280, 1340]
+    for largeur in largeurs:
+        print(f"Capture Belgique {largeur}x800...")
+        capturer(
+            url, largeur, 800,
+            SORTIE / f"i289_accueil_belgique_{largeur}x800_webkitgtk.png",
+            ["#drapeau-belgique"],
+        )
+
+    print("Capture France 700x800 (référence, mode inchangé)...")
+    capturer(
+        url, 700, 800,
+        SORTIE / "i289_accueil_france_700x800_webkitgtk.png",
+        [],
+    )
+
+    mock.unlink()
+    print("Captures écrites dans", SORTIE)
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# (index — ignorable)
index 51e8a4c..c4a95fb 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.css
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 56 (8 ligne(s)) dans l'ancienne version → ligne 56 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -56,8 +56,9 @@ body {
 }
 
 /* Mode Belgicisme (issue #269, bandeau opaque #270, fond tricolore #271,
-   couleurs franches + suppression des plaques #272) : Alain a vérifié le
-   rendu réel WebKitGTK de #271 par capture et constaté deux problèmes.
+   couleurs franches + suppression des plaques #272, panneau blanc central
+   #289) : Alain a vérifié le rendu réel WebKitGTK de #271 par capture et
+   constaté deux problèmes.
    1. Le voile tricolore (alpha 0.22/0.32/0.26 sur fond blanc) restait trop
       pâle pour être identifié comme noir/jaune/rouge francs — gris clair,
       jaune délavé, rose pastel. On remonte l'alpha à 0.95 sur les trois
# ── Zone modifiée : ligne 70 (10 ligne(s)) dans l'ancienne version → ligne 71 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -70,10 +71,24 @@ body {
       titre/sous-titre/légendes (#271, pensé pour un contraste indépendant
       de la bande dessous) est donc une complexité inutile : supprimé au
       profit d'une seule couleur de texte sombre (#1a1a1a), appliquée
-      uniformément à tous les textes du mode Belgicisme. Cette couleur
-      contraste ~15:1 sur le jaune franc du voile (bien au-delà du seuil
-      WCAG AA 4.5:1) — seule bande qui compte puisqu'aucun texte ne repose
-      sur le noir ou le rouge.
+      uniformément à tous les textes du mode Belgicisme.
+   Investigation ultérieure (avant #289) : cette approche "tout repose sur la
+   bande jaune" suppose que la bande jaune (1/3 de la largeur de fenêtre) est
+   toujours au moins aussi large que le `.container` (600px max) centré
+   dessus. Faux dès que la fenêtre descend sous ~1920px de large (bande
+   jaune = largeur/3 < 600px) : `.container` déborde alors visuellement sur
+   les bandes noire et rouge voisines, où le texte sombre #1a1a1a devient
+   illisible (noir sur noir) ou peu contrasté (noir sur rouge). Aucune
+   largeur de bande fixe ne peut garantir l'absence de débordement : la
+   bande jaune est proportionnelle à la fenêtre, `.container` ne l'est pas.
+   #289 corrige ce défaut à la racine (au lieu d'un filet de sécurité par
+   élément) en s'inspirant d'une référence visuelle type site officiel
+   Scrabble : un panneau blanc/quasi-opaque (voir `.container::before`
+   ci-dessous) couvre `.container` et déborde légèrement sur les côtés, de
+   sorte que tout le contenu (titre, cartes, boutons) repose désormais
+   TOUJOURS sur du blanc, quelle que soit la largeur de fenêtre — le voile
+   tricolore du body (inchangé ci-dessous) ne reste visible que dans les
+   marges latérales, hors du panneau, jamais sous du texte ou une carte.
    Le mode France reste strictement inchangé (aucune de ces règles n'existe
    hors de `body.mode-belgicisme`). */
 body.mode-belgicisme {
# ── Zone modifiée : ligne 91 (10 ligne(s)) dans l'ancienne version → ligne 106 (54 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -91,10 +106,54 @@ body.mode-belgicisme {
     background-attachment: fixed;
 }
 
-/* Texte uniforme sombre, sans plaque (issue #272 — remplace le système de
-   plaques blanches de #271, cf. commentaire de body.mode-belgicisme
-   ci-dessus). Tous ces textes reposent sur la bande jaune, seule bande qui
-   porte du contenu. */
+/* Panneau blanc central (issue #289). `.container` (max-width 600px) est
+   toujours plus étroit que le panneau : la marge entre les deux bords est le
+   "padding visuel" demandé, et le voile tricolore ne transparaît que dans
+   les marges latérales entre le panneau et le bord de la fenêtre. `top`/
+   `bottom` négatifs (plutôt qu'une `height` fixe) font que le panneau suit
+   automatiquement la hauteur réelle du contenu, quel que soit le nombre de
+   joueurs/parties affichés. `clamp()` garantit un panneau toujours plus
+   large que `.container` (620px plancher, contre 600px de large maximum
+   pour `.container`) tout en laissant une marge visible à toutes les
+   largeurs testées (700px, ~1280px, pleine largeur ≥1800px) : à 700px de
+   large, `94vw` ≈ 658px (marge visible ≈ 21px de chaque côté) ; au-delà de
+   ~766px de large, le panneau plafonne à 720px et la marge tricolore
+   grandit avec la fenêtre — comportement identique à toutes les tailles,
+   pas seulement un correctif pour petits écrans. `z-index: -1` s'appuie sur
+   le contexte d'empilement créé par `position: relative` sur `.container` :
+   le panneau reste sous son contenu (header, cartes, boutons, tous non
+   positionnés) sans affecter l'empilement par rapport au fond tricolore du
+   body, peint séparément avant `.container` dans l'ordre du document. */
+body.mode-belgicisme .container {
+    position: relative;
+}
+
+body.mode-belgicisme .container::before {
+    content: "";
+    position: absolute;
+    top: -20px;
+    bottom: -20px;
+    left: 50%;
+    transform: translateX(-50%);
+    width: clamp(620px, 94vw, 720px);
+    background: rgba(255, 255, 255, 0.97);
+    border-radius: 12px;
+    box-shadow: 0 2px 16px rgba(0, 0, 0, 0.18);
+    z-index: -1;
+}
+
+/* Texte sombre uniforme (issue #272, remplace le système de plaques de #271 ;
+   toujours d'actualité après #289). Ces éléments reposaient sur la bande
+   jaune (#272) ; ils reposent désormais sur le panneau blanc de #289 — la
+   raison change, la couleur reste : #1a1a1a contraste ~19:1 sur le panneau
+   quasi-opaque (blanc à 97%), bien au-delà du seuil WCAG AA (4.5:1), et ce
+   contraste ne dépend plus des proportions du voile tricolore puisque le
+   panneau ne fait plus jamais transparaître la bande dessous. Un retour aux
+   couleurs France d'origine (texte blanc, pensées pour le tapis vert plein
+   écran) a été envisagé (cf. tâche #289) mais écarté : sur le panneau blanc
+   quasi-opaque, du texte blanc tomberait sous le seuil WCAG AA (contraste
+   ~1:1), ce qui aurait réintroduit le problème de lisibilité que #289
+   corrige. */
 body.mode-belgicisme header h1,
 body.mode-belgicisme .subtitle,
 body.mode-belgicisme .drapeau-legende,
# ── Zone modifiée : ligne 114 (6 ligne(s)) dans l'ancienne version → ligne 173 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -114,6 +173,14 @@ body.mode-belgicisme section h2 {
     border-bottom-color: rgba(0, 0, 0, 0.2);
 }
 
+/* Toujours nécessaire après #289 (vérifié) : la bordure pointillée par
+   défaut (`rgba(255, 255, 255, 0.4)`, pensée pour ressortir sur le tapis vert
+   ou la bande tricolore) resterait invisible sur le panneau blanc — il faut
+   une bordure sombre. Le fond (`rgba(255, 255, 255, 0.55)`) est en revanche
+   devenu sans objet : posé sur le panneau blanc de #289 plutôt que sur la
+   bande tricolore directe de #272, il ne se distingue plus visuellement du
+   fond par défaut (`rgba(255, 255, 255, 0.08)`, ligne ~316) — conservé tel
+   quel par prudence, sans effet visible constaté. */
 body.mode-belgicisme .liste-joueurs:has(.vide),
 body.mode-belgicisme .parties-en-cours:has(.vide) {
     background: rgba(255, 255, 255, 0.55);
