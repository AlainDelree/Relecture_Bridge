d027078

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d027078
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 22:22:14 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #291 : titre en tuiles agrandi + relief renforcé, panneau à 50%
    
    Suite à #290, dont le résultat ne correspondait pas à l'image de référence
    (jointe à #290, ouverte et examinée pour cette tâche à
    issue-attachments/20260726-221403-...340168.png) : les tuiles du titre
    "Scrabble" passent de 1.6rem/2px de bordure à 3.2rem/3px, avec un relief
    (ombres internes + portée) nettement renforcé pour rester perceptible à
    cette taille. Le panneau translucide (.container::before) passe de 60% à
    50% d'opacité blanche pour laisser les bandes tricolores plus saturées
    (rouge et jaune nettement moins délavés), en restant au-dessus du seuil
    WCAG AA sur la bande noire (4.75:1, calcul détaillé en commentaire). Mode
    France strictement inchangé. Nouveau harnais WebKitGTK #291 (dérivé de
    celui de #290) avec captures réelles à l'appui.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/_harness_jeu/i291_accueil_belgique_1280x800_webkitgtk.png b/scripts/_harness_jeu/i291_accueil_belgique_1280x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..a0f90e3
Binary files /dev/null and b/scripts/_harness_jeu/i291_accueil_belgique_1280x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i291_accueil_belgique_1340x800_webkitgtk.png b/scripts/_harness_jeu/i291_accueil_belgique_1340x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..a0f90e3
Binary files /dev/null and b/scripts/_harness_jeu/i291_accueil_belgique_1340x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i291_accueil_belgique_700x800_webkitgtk.png b/scripts/_harness_jeu/i291_accueil_belgique_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..d7b49aa
Binary files /dev/null and b/scripts/_harness_jeu/i291_accueil_belgique_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i291_accueil_france_700x800_webkitgtk.png b/scripts/_harness_jeu/i291_accueil_france_700x800_webkitgtk.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..5d25440
Binary files /dev/null and b/scripts/_harness_jeu/i291_accueil_france_700x800_webkitgtk.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/verif_belgicisme_291_webkitgtk.py b/scripts/_harness_jeu/verif_belgicisme_291_webkitgtk.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..7afc54e
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/scripts/_harness_jeu/verif_belgicisme_291_webkitgtk.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (149 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,149 @@
+"""Vérification issue #291 : refonte du titre en tuiles + panneau du mode
+Belgicisme sous WebKitGTK (le moteur utilisé par pywebview sous Linux, cf.
+CONTEXTE.md — le harnais Playwright habituel de _harness_jeu ne teste que
+Chromium et n'aurait pas détecté l'écart de rendu constaté en #270).
+
+#291 corrige le rendu de #290 (titre en tuiles jugé trop petit, bandes
+tricolores délavées) après comparaison réelle avec l'image de référence
+jointe à #290 : tuiles du titre agrandies (1.6rem -> 3.2rem, relief renforcé)
+et panneau translucide recalibré de 60% à 50% d'opacité blanche (cf.
+`.container::before` dans accueil.css) pour laisser les bandes tricolores
+plus saturées. Ce harnais reprend celui de #290 (même mock d'API, même
+mécanique de capture via webkit_web_view_get_snapshot) aux mêmes largeurs,
+pour comparaison directe avant/après.
+
+Prérequis système (déjà présents sur cette machine) : gir1.2-webkit2-4.1,
+python3-gi (paquets système — utiliser /usr/bin/python3, pas un venv qui ne
+voit pas les dist-packages système), un DISPLAY X11 valide (le WebView a
+besoin d'un GtkWindow réel ; pas de Xvfb installé ici, mais le DISPLAY
+existant a suffi).
+
+Usage : /usr/bin/python3 verif_belgicisme_291_webkitgtk.py [dossier_sortie]
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
+    chemin = SORTIE / "_i291_mock_tmp.html"
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
+    # Mêmes largeurs que #289 (700 repli, 1280 résolution cible, 1340 proche
+    # pleine largeur — écran physique de cette machine limité à 1360x768,
+    # cf. commentaire équivalent dans verif_belgicisme_289_webkitgtk.py) pour
+    # comparaison directe avant/après #290.
+    largeurs = [700, 1280, 1340]
+    for largeur in largeurs:
+        print(f"Capture Belgique {largeur}x800...")
+        capturer(
+            url, largeur, 800,
+            SORTIE / f"i291_accueil_belgique_{largeur}x800_webkitgtk.png",
+            ["#drapeau-belgique"],
+        )
+
+    print("Capture France 700x800 (référence, mode inchangé)...")
+    capturer(
+        url, 700, 800,
+        SORTIE / "i291_accueil_france_700x800_webkitgtk.png",
+        [],
+    )
+
+    mock.unlink()
+    print("Captures écrites dans", SORTIE)
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# (index — ignorable)
index 87cd063..1e461d4 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/accueil.css
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 147 (18 ligne(s)) dans l'ancienne version → ligne 147 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -147,18 +147,24 @@ body.mode-belgicisme {
    fourchette 55-70% demandée) laisse les trois bandes clairement
    reconnaissables à travers tout le panneau tout en gardant un contraste
    confortable pour le texte sombre posé dessus (voir liste "texte sombre
-   uniforme" plus bas). Calcul de contraste WCAG (fond body déjà mélangé à
-   95% sur blanc, cf. plus haut ; panneau blanc à 60% par-dessus ; texte
-   #1a1a1a, luminance relative ~0.0104) sur les trois bandes, cas le plus
-   défavorable en premier :
-     - bande noire  (~#0d0d0d dessous) -> effectif ~rgb(158,158,158) -> ratio ≈ 6.5:1
-     - bande rouge  (~#ef3443 dessous) -> effectif ~rgb(249,178,184) -> ratio ≈ 10.0:1
-     - bande jaune  (~#fae24b dessous) -> effectif ~rgb(253,244,187) -> ratio ≈ 15.6:1
-   Les trois dépassent le seuil WCAG AA (4.5:1), la bande noire restant la
-   plus contraignante avec une marge confortable (~1.4x le minimum). Une
-   opacité plus basse (vers 55%) resterait conforme mais avec moins de marge
-   sur la bande noire ; 60% a été retenu comme compromis entre translucidité
-   marquée et marge de sécurité du contraste. */
+   uniforme" plus bas).
+
+   Ré-ajustement (issue #291) : après comparaison avec l'image de référence
+   jointe à #290 (bandes nettement vives à travers le panneau, pas
+   délavées), 60% restait encore trop proche de l'opaque — le rouge
+   ressortait rosé et le jaune pâle plutôt que saturés. Passage à 0.5 (50%),
+   qui laisse nettement plus de saturation traverser tout en restant
+   au-dessus du seuil WCAG AA sur la bande noire (le cas le plus
+   défavorable, cf. calcul ci-dessous) :
+     - bande noire  (~#0d0d0d dessous) -> effectif ~rgb(134,134,134) -> ratio ≈ 4.75:1
+     - bande rouge  (~#ef3443 dessous) -> effectif ~rgb(246,154,162) -> ratio ≈ 8.3:1
+     - bande jaune  (~#fae24b dessous) -> effectif ~rgb(252,240,165) -> ratio ≈ 15.1:1
+   Les trois dépassent toujours le seuil WCAG AA (4.5:1), la bande noire
+   restant la plus contraignante mais avec une marge réelle (~1.06x le
+   minimum, valeur fixe et déterministe — un mélange alpha CSS, pas un
+   rendu variable). Descendre davantage (45%) ferait passer cette bande
+   sous 4.5:1 (voir calcul dans l'historique de l'issue) : 50% est le
+   plancher compatible avec l'AA sur ce panneau. */
 body.mode-belgicisme .container {
     position: relative;
 }
# ── Zone modifiée : ligne 171 (7 ligne(s)) dans l'ancienne version → ligne 177 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -171,7 +177,7 @@ body.mode-belgicisme .container::before {
     left: 50%;
     transform: translateX(-50%);
     width: clamp(620px, 94vw, 720px);
-    background: rgba(255, 255, 255, 0.6);
+    background: rgba(255, 255, 255, 0.5);
     border-radius: 12px;
     box-shadow: 0 2px 16px rgba(0, 0, 0, 0.18);
     z-index: -1;
# ── Zone modifiée : ligne 208 (34 ligne(s)) dans l'ancienne version → ligne 214 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -208,34 +214,46 @@ body.mode-belgicisme .parties-en-cours .vide {
      qui détache chaque tuile du panneau ;
    - coins légèrement arrondis.
    Fond opaque : le contraste du texte `#4a3418` sur `#f5e6c8` (~9.5:1) ne
-   dépend pas de l'opacité du panneau dessous. */
+   dépend pas de l'opacité du panneau dessous.
+
+   Agrandissement + relief renforcé (issue #291) : comparaison avec l'image
+   de référence jointe à #290 (ouverte pour cette tâche, cf. rapport) — les
+   tuiles du titre y occupent une large portion de la largeur du panneau
+   avec un relief 3D marqué, très loin des tuiles ~1.6rem/2px de bordure
+   d'origine (qui donnaient un petit ruban de texte dans un coin). Tuiles
+   portées à 3.2rem (× ~2 en linéaire, × ~4 en surface), bordure doublée à
+   3px, ombres internes et portée renforcées (offsets et opacités accrus)
+   pour un embossage net à cette taille — à 2px/1px d'ombre, le relief
+   devenait imperceptible sur une tuile deux fois plus grande. 8 tuiles à
+   3.2rem + 7 espaces de 8px ≈ 427px, confortable dans les 560px de contenu
+   du panneau (600px - 2×20px de padding, cf. `.container`). */
 body.mode-belgicisme header h1 {
     display: flex;
     justify-content: center;
     align-items: center;
-    gap: 4px;
-    margin-bottom: 8px;
+    gap: 8px;
+    margin-bottom: 14px;
 }
 
 body.mode-belgicisme header h1 .lettre-scrabble {
     display: inline-flex;
     align-items: center;
     justify-content: center;
-    min-width: 1.6rem;
-    height: 1.6rem;
-    padding: 0 2px;
+    min-width: 3.2rem;
+    height: 3.2rem;
+    padding: 0 4px;
     background: #f5e6c8;
     color: #4a3418;
-    font-size: 1.15rem;
+    font-size: 2.2rem;
     font-weight: 700;
     line-height: 1;
     text-shadow: none;
-    border-radius: 4px;
-    border: 2px solid #caa02c;
+    border-radius: 8px;
+    border: 3px solid #caa02c;
     box-shadow:
-        inset 1px 1px 0 rgba(255, 250, 230, 0.7),
-        inset -1px -1px 0 rgba(120, 80, 10, 0.5),
-        0 2px 3px rgba(0, 0, 0, 0.3);
+        inset 2px 2px 0 rgba(255, 250, 230, 0.8),
+        inset -2px -2px 0 rgba(120, 80, 10, 0.65),
+        0 4px 6px rgba(0, 0, 0, 0.4);
 }
 
 body.mode-belgicisme .btn-reglages {
# ── Zone modifiée : ligne 251 (12 ligne(s)) dans l'ancienne version → ligne 269 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -251,12 +269,13 @@ body.mode-belgicisme section h2 {
    ou la bande tricolore) resterait invisible sur le panneau blanc — il faut
    une bordure sombre. Le fond (`rgba(255, 255, 255, 0.55)`) était devenu sans
    objet sur le panneau quasi-opaque de #289 (indiscernable du fond par
-   défaut) mais redevient utile depuis que le panneau est translucide à 60%
-   (#290) : cette couche blanche supplémentaire éclaircit encore le fond sous
-   ce texte, sans jamais faire baisser le contraste (empilement de couches
-   blanches translucides = seulement plus clair, jamais plus sombre — vérifié
-   au pire cas sur la bande noire : ~211,211,211 effectif, contraste #1a1a1a
-   ≈ 11.6:1, au-delà du 6.5:1 déjà obtenu sur le panneau seul). */
+   défaut) mais redevient utile depuis que le panneau est translucide (#290,
+   opacité recalibrée à 50% en #291) : cette couche blanche supplémentaire
+   éclaircit encore le fond sous ce texte, sans jamais faire baisser le
+   contraste (empilement de couches blanches translucides = seulement plus
+   clair, jamais plus sombre — vérifié au pire cas sur la bande noire :
+   ~201,201,201 effectif, contraste #1a1a1a ≈ 10.5:1, au-delà du 4.75:1 déjà
+   obtenu sur le panneau seul à 50%). */
 body.mode-belgicisme .liste-joueurs:has(.vide),
 body.mode-belgicisme .parties-en-cours:has(.vide) {
     background: rgba(255, 255, 255, 0.55);
