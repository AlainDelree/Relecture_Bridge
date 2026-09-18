c044068

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c044068
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 00:45:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #292 : mode Belgicisme, fond drapeau en image + panneau quasi opaque
    
    Remplace le voile CSS en linear-gradient (bandes forcément droites) par une
    vraie photo de drapeau belge ondulé (images/drapeau-belge.jpg, converti en
    JPEG q85 depuis la pièce jointe PNG 1,4 Mo -> 61 Ko) en background-image
    étiré 100%/100%. Panneau (.container::before) remonté à 95% d'opacité (le
    fond n'a plus besoin de transparaître à travers le contenu), hauteur
    toujours pilotée par le contenu réel (top/bottom -20px, pas de height fixe).
    Corrige le chevauchement du titre en tuiles avec le bouton réglages via un
    padding-right réservant sa place. Met à jour le harnais Playwright existant
    (assertions sur le fond et l'opacité du panneau, devenues obsolètes).
    
    Mode France strictement inchangé (captures à l'appui).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/_harness_jeu/i269_accueil_belgique.png b/scripts/_harness_jeu/i269_accueil_belgique.png
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c45c0b2..964ea87 100644
Binary files a/scripts/_harness_jeu/i269_accueil_belgique.png and b/scripts/_harness_jeu/i269_accueil_belgique.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_belgique_rempli_1280x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_belgique_rempli_1280x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..8d8b463
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_belgique_rempli_1280x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_belgique_rempli_1340x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_belgique_rempli_1340x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..8d8b463
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_belgique_rempli_1340x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_belgique_rempli_700x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_belgique_rempli_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..7172875
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_belgique_rempli_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_belgique_vide_1280x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_belgique_vide_1280x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..9e3f447
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_belgique_vide_1280x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_belgique_vide_1340x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_belgique_vide_1340x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..9e3f447
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_belgique_vide_1340x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_belgique_vide_700x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_belgique_vide_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..3601895
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_belgique_vide_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_france_rempli_700x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_france_rempli_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..587c236
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_france_rempli_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i292_accueil_france_vide_700x800_webkitgtk.png b/scripts/_harness_jeu/i292_accueil_france_vide_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..d0cc6e8
Binary files /dev/null and b/scripts/_harness_jeu/i292_accueil_france_vide_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/verif_belgicisme_269.mjs b/scripts/_harness_jeu/verif_belgicisme_269.mjs
# (index — ignorable)
index 7cfdcdd..aa31b4b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/scripts/_harness_jeu/verif_belgicisme_269.mjs
# ── Version APRÈS ce commit.
+++ b/scripts/_harness_jeu/verif_belgicisme_269.mjs
# ── Zone modifiée : ligne 1 (17 ligne(s)) dans l'ancienne version → ligne 1 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,17 +1,17 @@
-// Vérification issues #269 + #270 + #271 + #272 + #289 + #290 : cercles-
-// drapeaux France/Belgique de l'accueil, et fond du mode Belgicisme.
+// Vérification issues #269 + #270 + #271 + #272 + #289 + #290 + #291 + #292 :
+// cercles-drapeaux France/Belgique de l'accueil, et fond du mode Belgicisme.
 //
 // Contrôle en headless Playwright — le rendu réel WebKitGTK a été vérifié
-// manuellement par capture GTK+WebKit2 (issues #270/#271/#272/#289/#290, cf.
-// verif_belgicisme_290_webkitgtk.py et accueil.css) :
+// manuellement par capture GTK+WebKit2 (issues #270/#271/#272/#289/#290/#291/
+// #292, cf. verif_belgicisme_292_webkitgtk.py et accueil.css) :
 //   1. France actif par défaut, Belgique inactif.
 //   2. Clic sur le drapeau belge -> classe .actif bascule, aria-checked
 //      correct, body.mode-belgicisme posé, api.definir_mode_belgicisme(true)
 //      appelée.
-//   3. Fond blanc + voile tricolore noir/jaune/rouge quasi-opaque (alpha
-//      0.95, issue #272 — remplace l'alpha 0.22/0.32/0.26 trop pâle de #271,
-//      qui remplaçait le bandeau opaque 6px de #270, qui remplaçait lui-même
-//      le voile 12% invisible sur fond vert de #269) sur TOUTE la surface.
+//   3. Fond en image (`images/drapeau-belge.jpg`, issue #292 — remplace le
+//      voile CSS en `linear-gradient` des issues #271/#272 qui ne rendait
+//      jamais le tissu ondulé voulu par Alain), étiré sur toute la surface
+//      (`background-size: 100% 100%`).
 //   4. Sous-titre et légendes des drapeaux en texte noir uniforme
 //      (#1a1a1a), SANS plaque de fond (issue #272 — supprime le système de
 //      plaques blanches de #271) en mode Belgicisme — inchangés (texte
# ── Zone modifiée : ligne 19 (13 ligne(s)) dans l'ancienne version → ligne 19 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -19,13 +19,15 @@
 //      n'est PLUS concerné par cette règle depuis #290 : voir point 7.
 //   5. Plusieurs allers-retours France <-> Belgique : aucun résidu visuel
 //      (retour exact au fond normal, un seul cercle actif à la fois).
-//   6. Panneau translucide central (issue #289, opacité réduite à 60% par
-//      #290) : à plusieurs largeurs de fenêtre (700px repli, ~1280px
-//      résolution cible, 1920px pleine largeur), `.container` reste
-//      entièrement contenu dans le panneau de `.container::before` (aucun
-//      débordement sur le voile tricolore), et le panneau laisse toujours
-//      une marge visible avec le bord de la fenêtre (bandes tricolores
-//      toujours visibles, en bordure comme au centre à travers le panneau).
+//   6. Panneau quasi opaque central (issue #289, opacité réduite à 60% par
+//      #290 puis 50% par #291, remontée à 95% par #292 — l'image de fond
+//      n'a plus besoin de transparaître à travers le panneau) : à plusieurs
+//      largeurs de fenêtre (700px repli, ~1280px résolution cible, 1920px
+//      pleine largeur), `.container` reste entièrement contenu dans le
+//      panneau de `.container::before` (aucun débordement sur le fond), et
+//      le panneau laisse toujours une marge visible avec le bord de la
+//      fenêtre (drapeau visible en bordure comme au centre à travers le
+//      panneau, quasiment opaque).
 //   7. Titre en tuiles de Scrabble (issue #290) : en mode Belgicisme, chaque
 //      lettre de "Scrabble" (8 `<span class="lettre-scrabble">`) porte un
 //      fond opaque crème (#f5e6c8) et un contour doré — pas de couleur de
# ── Zone modifiée : ligne 102 (10 ligne(s)) dans l'ancienne version → ligne 104 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -102,10 +104,8 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
   }));
   await page.screenshot({ path: path.join(here, 'i269_accueil_belgique.png') });
 
-  // Fond blanc + voile tricolore quasi-opaque sur toute la surface
-  // (issue #272, alpha 0.95 — remplace l'alpha 0.22/0.32/0.26 trop pâle de
-  // #271) : fond blanc uni + les trois couleurs franches du drapeau belge
-  // présentes dans le background-image, étalées sur 100% de la surface.
+  // Fond en image de drapeau ondulé, étiré sur toute la surface (issue
+  // #292 — remplace le voile CSS en `linear-gradient` des issues #271/#272).
   const fond = await page.evaluate(() => {
     const style = getComputedStyle(document.body);
     return {
# ── Zone modifiée : ligne 115 (10 ligne(s)) dans l'ancienne version → ligne 115 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -115,10 +115,7 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
     };
   });
   const fondOk =
-    fond.backgroundColor === 'rgb(255, 255, 255)' &&
-    fond.backgroundImage.includes('rgba(0, 0, 0, 0.95)') &&
-    fond.backgroundImage.includes('rgba(250, 224, 66, 0.95)') &&
-    fond.backgroundImage.includes('rgba(237, 41, 57, 0.95)') &&
+    fond.backgroundImage.includes('drapeau-belge.jpg') &&
     /100%\s*100%/.test(fond.backgroundSize);
 
   // Sous-titre/légendes en texte noir uniforme, SANS plaque de fond (issue
# ── Zone modifiée : ligne 162 (13 ligne(s)) dans l'ancienne version → ligne 159 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -162,13 +159,13 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
     tuiles.map((t) => t.texte).join('') === 'Scrabble' &&
     tuiles.every((t) => t.backgroundColor === 'rgb(245, 230, 200)' && t.color === 'rgb(74, 52, 24)');
 
-  // Panneau translucide central (issue #289, opacité réduite à 60% par
-  // #290) : à plusieurs largeurs de fenêtre (700px repli, ~1280px résolution
-  // cible, 1920px pleine largeur déjà correcte avant #289 — ne doit pas être
-  // cassée), `.container` doit rester entièrement contenu dans le panneau de
-  // `.container::before`, et le panneau doit toujours laisser une marge
-  // visible avec le bord de fenêtre (bande tricolore visible, en bordure
-  // comme — désormais — en transparence à travers le panneau lui-même).
+  // Panneau quasi opaque central (issue #289, opacité 60% par #290, 50% par
+  // #291, 95% par #292) : à plusieurs largeurs de fenêtre (700px repli,
+  // ~1280px résolution cible, 1920px pleine largeur déjà correcte avant
+  // #289 — ne doit pas être cassée), `.container` doit rester entièrement
+  // contenu dans le panneau de `.container::before`, et le panneau doit
+  // toujours laisser une marge visible avec le bord de fenêtre (drapeau
+  // visible en bordure).
   const largeursPanneau = [700, 1280, 1920];
   const mesuresPanneau = [];
   for (const largeur of largeursPanneau) {
# ── Zone modifiée : ligne 202 (7 ligne(s)) dans l'ancienne version → ligne 199 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -202,7 +199,7 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
     m.conteneurDroit <= m.panneauDroit + TOLERANCE &&
     m.panneauGauche > 0 &&
     m.panneauDroit < m.largeurFenetre &&
-    m.fondPanneau === 'rgba(255, 255, 255, 0.6)'
+    m.fondPanneau === 'rgba(255, 255, 255, 0.95)'
   );
 
   // Plusieurs allers-retours pour détecter un résidu visuel.
# ── Zone modifiée : ligne 261 (8 ligne(s)) dans l'ancienne version → ligne 258 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -261,8 +258,8 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
     etatFinal.bodyModeBelge === false &&
     etatFinal.franceActif === true &&
     etatFinal.belgiqueActif === false &&
-    etatFinal.backgroundColor !== 'rgb(255, 255, 255)' &&
-    !etatFinal.backgroundImage.includes('rgba(250, 224, 66,') &&
+    etatFinal.backgroundColor !== 'rgb(13, 13, 13)' &&
+    !etatFinal.backgroundImage.includes('drapeau-belge.jpg') &&
     franceInchange(etatFinal) &&
     errs.length === 0;
 
# ── Zone modifiée : ligne 275 (7 ligne(s)) dans l'ancienne version → ligne 272 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -275,7 +272,7 @@ const html = fs.readFileSync(path.join(web, 'accueil.html'), 'utf8')
   console.log('Historique bascules (mode belge actif ?) :', historique);
   console.log('État final (retour France) :', JSON.stringify(etatFinal));
   console.log('Erreurs JS :', errs.length ? errs : 'aucune');
-  console.log(ok ? 'OK — cercles-drapeaux fonctionnels, fond blanc+tricolore franc, texte sans plaque, titre en tuiles, panneau translucide (60%) sans débordement à 700/1280/1920px, aucun résidu visuel'
+  console.log(ok ? 'OK — cercles-drapeaux fonctionnels, fond image drapeau, texte sans plaque, titre en tuiles, panneau quasi opaque (95%) sans débordement à 700/1280/1920px, aucun résidu visuel'
                  : 'ECHEC');
   await browser.close();
   process.exit(ok ? 0 : 1);
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/verif_belgicisme_292_webkitgtk.py b/scripts/_harness_jeu/verif_belgicisme_292_webkitgtk.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..8491302
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/scripts/_harness_jeu/verif_belgicisme_292_webkitgtk.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (237 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,237 @@
+"""Vérification issue #292 : fond drapeau en image + panneau blanc flottant
+du mode Belgicisme sous WebKitGTK (le moteur utilisé par pywebview sous
+Linux, cf. CONTEXTE.md — le harnais Playwright habituel de _harness_jeu ne
+teste que Chromium et n'aurait pas détecté l'écart de rendu constaté en
+#270).
+
+#292 remplace le voile CSS en `linear-gradient` (#289-#291, bandes forcément
+droites et figées) par une vraie photo de drapeau belge ondulé
+(`images/drapeau-belge.jpg`) en `background-image`, repasse le panneau
+(`.container::before`) à une opacité quasi opaque (0.95, l'image n'a plus
+besoin de transparaître à travers le contenu) et corrige le chevauchement du
+titre en tuiles avec le bouton réglages. Ce harnais reprend celui de #291
+(même mock d'API, même mécanique de capture via
+webkit_web_view_get_snapshot) aux mêmes largeurs, mais ajoute une variante
+"contenu rempli" (plusieurs joueurs + plusieurs parties enregistrées) en
+plus de la variante "contenu vide" (aucun joueur, aucune partie), pour
+vérifier que le panneau s'arrête bien à la fin du contenu réel dans les deux
+cas.
+
+Prérequis système (déjà présents sur cette machine) : gir1.2-webkit2-4.1,
+python3-gi (paquets système — utiliser /usr/bin/python3, pas un venv qui ne
+voit pas les dist-packages système), un DISPLAY X11 valide (le WebView a
+besoin d'un GtkWindow réel ; pas de Xvfb installé ici, mais le DISPLAY
+existant a suffi).
+
+Usage : /usr/bin/python3 verif_belgicisme_292_webkitgtk.py [dossier_sortie]
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
+# Variante "vide" : aucun joueur, aucune partie enregistrée.
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
+# Variante "rempli" : plusieurs joueurs autour de la table + plusieurs
+# parties enregistrées (une en cours, une terminée), pour vérifier que le
+# panneau grandit avec le contenu plutôt que de rester figé à une hauteur.
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
+    # Le CSS est inliné dans un <style> d'un HTML temporaire écrit hors de
+    # web/ (dans SORTIE) : le chemin relatif `url(images/...)` doit être
+    # réécrit en chemin absolu file:// pour continuer à résoudre vers
+    # web/images/, sinon l'image de fond ne se charge pas dans ce harnais
+    # (bug spécifique au mock, sans rapport avec l'app réelle où accueil.css
+    # et images/ restent voisins sous web/).
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
+            # Le fond passe du vert à l'image drapeau (transition CSS
+            # `background-image 0.2s ease` du body) : 700ms de marge pour
+            # être sûr que la capture ne tombe jamais en plein fondu, et que
+            # l'image (chargée en parallèle) a le temps de s'afficher.
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
+    # Repli anti-blocage : sans lui, un chargement qui ne finit jamais (échec
+    # WebKit, ex.) bloquerait indéfiniment. Sans l'annuler via
+    # `GLib.source_remove` une fois la capture réussie (ci-dessus), ce
+    # timeout restait planté dans le contexte GLib par défaut au-delà de la
+    # fin du `Gtk.main()` courant et finissait par déclencher un
+    # `Gtk.main_quit()` prématuré pendant l'appel `capturer()` SUIVANT
+    # (partagent le même contexte GLib par défaut) — constaté : les deux
+    # dernières captures de la série (700/1280/1340 x vide/rempli) restaient
+    # silencieusement absentes, le script se terminant sans erreur.
+    minuterie = {"id": None}
+    webview.connect("load-changed", apres_chargement)
+    webview.load_uri("file://" + url)
+    minuterie["id"] = GLib.timeout_add(15000, Gtk.main_quit)
+    Gtk.main()
+
+
+if __name__ == "__main__":
+    # Mêmes largeurs que #289/#290/#291 (700 repli, 1280 résolution cible,
+    # 1340 proche pleine largeur — écran physique de cette machine limité à
+    # 1360x768) pour comparaison directe avant/après #292.
+    largeurs = [700, 1280, 1340]
+
+    mock_vide = construire_mock(MOCK_JS_VIDE, "_i292_mock_vide_tmp.html")
+    url_vide = str(mock_vide)
+    for largeur in largeurs:
+        print(f"Capture Belgique {largeur}x800 (contenu vide)...")
+        capturer(
+            url_vide, largeur, 800,
+            SORTIE / f"i292_accueil_belgique_vide_{largeur}x800_webkitgtk.png",
+            ["#drapeau-belgique"],
+        )
+
+    print("Capture France 700x800 (contenu vide, référence, mode inchangé)...")
+    capturer(
+        url_vide, 700, 800,
+        SORTIE / "i292_accueil_france_vide_700x800_webkitgtk.png",
+        [],
+    )
+    mock_vide.unlink()
+
+    mock_rempli = construire_mock(MOCK_JS_REMPLI, "_i292_mock_rempli_tmp.html")
+    url_rempli = str(mock_rempli)
+    for largeur in largeurs:
+        print(f"Capture Belgique {largeur}x800 (contenu rempli)...")
+        capturer(
+            url_rempli, largeur, 800,
+            SORTIE / f"i292_accueil_belgique_rempli_{largeur}x800_webkitgtk.png",
+            ["#drapeau-belgique"],
+        )
+
+    print("Capture France 700x800 (contenu rempli, référence, mode inchangé)...")
+    capturer(
+        url_rempli, 700, 800,
+        SORTIE / "i292_accueil_france_rempli_700x800_webkitgtk.png",
+        [],
+    )
+    mock_rempli.unlink()
+
+    print("Captures écrites dans", SORTIE)
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# (index — ignorable)
index 1e461d4..07c3d20 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.css
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 106 (16 ligne(s)) dans l'ancienne version → ligne 106 (32 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -106,16 +106,32 @@ body {
       crème, contour doré, relief), donc retiré de la liste "texte sombre
       uniforme" ci-dessous — son style est désormais défini séparément, plus
       bas dans ce fichier, avec son propre calcul de contraste (les tuiles
-      étant opaques, leur contraste ne dépend pas de l'opacité du panneau). */
+      étant opaques, leur contraste ne dépend pas de l'opacité du panneau).
+
+   Fond image + panneau quasi-opaque (issue #292) : le voile CSS en
+   `linear-gradient` (bandes forcément droites et figées) ne rendait jamais
+   le tissu ondulé voulu par Alain. Remplacé par une vraie photo de drapeau
+   belge ondulé (`images/drapeau-belge.jpg`) en `background-image`.
+   `background-size: 100% 100%` (étirement) plutôt que `cover` : `cover`
+   rognerait fortement les bandes noire/rouge sur les côtés dans une
+   fenêtre étroite, alors que l'étirement garde les trois bandes toujours
+   proportionnées sur toute la largeur — déformation imperceptible sur une
+   texture organique floue. Le panneau redevenant quasi opaque (voir
+   `.container::before`), le voile de fond n'a plus besoin de transparaître
+   à travers le contenu : il reste visible sur les côtés et en dessous du
+   panneau uniquement.
+
+   Asset (issue #292) : la pièce jointe de l'issue
+   (`issue-attachments/20260726-230812-drapeau_seul.png`, 1376x768) pèse
+   1,4 Mo en PNG — largement au-dessus du seuil d'1 Mo à partir duquel une
+   conversion s'impose pour un fichier embarqué dans l'installeur. Convertie
+   en JPEG qualité 85 (`images/drapeau-belge.jpg`, 61 Ko) : la texture est
+   une photo (bruit organique du tissu), pas un aplat ou un dessin au trait,
+   donc sans les artefacts de bloc que le JPEG produirait sur des à-plats
+   nets ou du texte — perte visuelle négligeable, gain de poids ~23x. */
 body.mode-belgicisme {
-    background-color: #ffffff;
-    background-image:
-        linear-gradient(
-            90deg,
-            rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.95) 33.33%,
-            rgba(250, 224, 66, 0.95) 33.33%, rgba(250, 224, 66, 0.95) 66.66%,
-            rgba(237, 41, 57, 0.95) 66.66%, rgba(237, 41, 57, 0.95) 100%
-        );
+    background-color: #0d0d0d;
+    background-image: url(images/drapeau-belge.jpg);
     background-repeat: no-repeat;
     background-size: 100% 100%;
     background-position: center;
# ── Zone modifiée : ligne 164 (7 ligne(s)) dans l'ancienne version → ligne 180 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -164,7 +180,20 @@ body.mode-belgicisme {
    minimum, valeur fixe et déterministe — un mélange alpha CSS, pas un
    rendu variable). Descendre davantage (45%) ferait passer cette bande
    sous 4.5:1 (voir calcul dans l'historique de l'issue) : 50% est le
-   plancher compatible avec l'AA sur ce panneau. */
+   plancher compatible avec l'AA sur ce panneau.
+
+   Retour au quasi-opaque (issue #292) : le fond tricolore n'est plus un
+   voile CSS pâle mais une vraie photo de drapeau (voir plus haut) — il
+   n'a plus besoin de transparaître à travers le panneau pour être identifié,
+   il reste pleinement visible sur les côtés et en dessous. Le panneau
+   remonte donc à 0.95 (95%, milieu de la fourchette 92-97% demandée) :
+   quasi opaque, texte très confortable dessus (le calcul WCAG AA du 50%
+   ci-dessus, déjà largement au-dessus du seuil, ne fait que s'améliorer
+   avec moins de mélange). `top`/`bottom` à -20px (pas de `height` fixe)
+   restent inchangés : le panneau suit la hauteur réelle de `.container`
+   (déterminée par son contenu), jamais celle de la fenêtre — vérifié à la
+   fois avec 0 joueur/0 partie et avec plusieurs joueurs/parties (le
+   drapeau redevient visible en dessous dès la fin du contenu). */
 body.mode-belgicisme .container {
     position: relative;
 }
# ── Zone modifiée : ligne 177 (7 ligne(s)) dans l'ancienne version → ligne 206 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -177,7 +206,7 @@ body.mode-belgicisme .container::before {
     left: 50%;
     transform: translateX(-50%);
     width: clamp(620px, 94vw, 720px);
-    background: rgba(255, 255, 255, 0.5);
+    background: rgba(255, 255, 255, 0.95);
     border-radius: 12px;
     box-shadow: 0 2px 16px rgba(0, 0, 0, 0.18);
     z-index: -1;
# ── Zone modifiée : ligne 202 (6 ligne(s)) dans l'ancienne version → ligne 231 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -202,6 +231,19 @@ body.mode-belgicisme .parties-en-cours .vide {
     text-shadow: none;
 }
 
+/* `.message-limite` ("Table complète (4 joueurs maximum)", etc.) gardait son
+   style pensé pour le tapis vert (rose clair #ffd0d0 + ombre portée) : quasi
+   invisible sur le panneau blanc/quasi-opaque du mode Belgicisme (constaté
+   en vérifiant le contraste WCAG AA de l'issue #292). Rouge alerte
+   (var(--couleur-danger), déjà utilisé ailleurs dans l'app pour ce
+   sémantisme) plutôt que le #1a1a1a uniforme ci-dessus : conserve le sens
+   "avertissement" du message tout en assurant un contraste confortable
+   (~7.5:1 sur le panneau à 95% d'opacité, bien au-delà du seuil AA 4.5:1). */
+body.mode-belgicisme .message-limite {
+    color: var(--couleur-danger);
+    text-shadow: none;
+}
+
 /* Titre en tuiles de Scrabble (issue #290), mode Belgicisme uniquement.
    Le HTML (accueil.html) découpe "Scrabble" en 8 `<span class="lettre-
    scrabble">` ; en mode France, aucune règle ne cible cette classe, le texte
# ── Zone modifiée : ligne 226 (13 ligne(s)) dans l'ancienne version → ligne 268 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -226,13 +268,24 @@ body.mode-belgicisme .parties-en-cours .vide {
    pour un embossage net à cette taille — à 2px/1px d'ombre, le relief
    devenait imperceptible sur une tuile deux fois plus grande. 8 tuiles à
    3.2rem + 7 espaces de 8px ≈ 427px, confortable dans les 560px de contenu
-   du panneau (600px - 2×20px de padding, cf. `.container`). */
+   du panneau (600px - 2×20px de padding, cf. `.container`).
+
+   Chevauchement avec le bouton réglages (issue #292) : à cette taille, les
+   tuiles centrées dans les 560px de `header` (via `justify-content: center`
+   sur toute sa largeur) ne laissent plus qu'une poignée de pixels avant le
+   bouton `.btn-reglages` (44px de large, ancré `top:0; right:0` sur ce
+   même `header`) — l'ombre portée des tuiles empiète visuellement dessus.
+   `padding-right: 56px` (44px de bouton + 12px de marge) réduit la boîte
+   dans laquelle `justify-content: center` centre les tuiles, les décalant
+   d'autant vers la gauche : espace réservé au bouton à toutes les largeurs
+   de fenêtre, sans dépendre d'un calcul de largeur de tuiles fragile. */
 body.mode-belgicisme header h1 {
     display: flex;
     justify-content: center;
     align-items: center;
     gap: 8px;
     margin-bottom: 14px;
+    padding-right: 56px;
 }
 
 body.mode-belgicisme header h1 .lettre-scrabble {
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/images/drapeau-belge.jpg b/src/scrabble/ui/web/images/drapeau-belge.jpg
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..be16e3e
Binary files /dev/null and b/src/scrabble/ui/web/images/drapeau-belge.jpg differ
