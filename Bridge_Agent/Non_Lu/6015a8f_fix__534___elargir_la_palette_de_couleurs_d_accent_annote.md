6015a8f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6015a8f
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Sat Sep 12 17:46:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #534 : elargir la palette de couleurs d'accent et corriger la collision ecole/apiselect + ff_galerie/actualise
    
    - nouveau_projet.py : PALETTE_COULEURS passe de 10 a 16 teintes reparties sur le cercle chromatique (ajout indigo/orchidee/rose fonce/taupe/sauge) ; nouvelle couleur pour ff_galerie (vert emeraude) et ecole (olive/moutarde) qui partageaient exactement la meme couleur qu'actualise et apiselect (le bug racine : couleurs_utilisees() ne lisait que les .conf, ignorant les projets legacy sans champ COULEUR persiste). Ajout de COULEURS_LEGACY_SANS_CONF pour que ces couleurs soient desormais correctement exclues de la proposition aux futurs projets.
    - static/js/app.js : COULEURS_PROJET mis a jour en synchro (ff_galerie, ecole).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nouveau_projet.py b/nouveau_projet.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5a7f953..f78b370 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nouveau_projet.py
# ── Version APRÈS ce commit.
+++ b/nouveau_projet.py
# ── Zone modifiée : ligne 48 (24 ligne(s)) dans l'ancienne version → ligne 48 (54 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -48,24 +48,54 @@ LABELS = [
 ]
 
 # Palette fixe de couleurs d'accent proposées à la création d'un projet (issue
-# #121). Une dizaine de teintes bien distinctes, incluant les 5 déjà en usage
-# (cohérence visuelle avec l'existant : voir COULEURS_PROJET dans app.js). Une
-# couleur est attribuée dès la création et écrite dans le .conf (champ COULEUR) ;
-# celles déjà prises par un projet existant sont exclues de la proposition. Hex
-# #RRGGBB, écrits en MAJUSCULES mais comparés sans tenir compte de la casse.
+# #121, élargie issue #534). Teintes réparties sur le cercle chromatique (et
+# pas seulement par variations d'une même famille), en jouant aussi sur la
+# saturation/luminosité pour rester distinguables au premier coup d'œil dans
+# l'onglet Résultats (cohérence visuelle avec l'existant : voir
+# COULEURS_PROJET dans app.js — les couleurs des projets sans champ COULEUR
+# persisté doivent rester en synchro avec COULEURS_LEGACY_SANS_CONF
+# ci-dessous). Une couleur est attribuée dès la création et écrite dans le
+# .conf (champ COULEUR) ; celles déjà prises par un projet existant sont
+# exclues de la proposition. Hex #RRGGBB, écrits en MAJUSCULES mais comparés
+# sans tenir compte de la casse.
 PALETTE_COULEURS = [
-    "#185FA5",  # bleu       (bridge_agent)
-    "#3B6D11",  # vert       (alchess)
-    "#BA7517",  # orange     (ff_galerie)
-    "#0E8A82",  # turquoise  (scrabble)
-    "#6B3FA0",  # violet     (ecole)
-    "#B0323A",  # rouge brique
-    "#A2348A",  # magenta
+    "#185FA5",  # bleu           (bridge_agent)
+    "#3B6D11",  # vert           (alchess)
+    "#BA7517",  # orange         (actualise)
+    "#0E8A82",  # turquoise      (scrabble)
+    "#6B3FA0",  # violet         (apiselect)
+    "#B0323A",  # rouge brique   (diagnostique_programme)
+    "#A2348A",  # magenta        (bloc_score)
     "#3B45A0",  # indigo
-    "#7A4E2D",  # brun
-    "#556070",  # gris ardoise
+    "#7A4E2D",  # brun           (chesscoach)
+    "#556070",  # gris ardoise   (rummikub)
+    "#1F7A3D",  # vert émeraude  (ff_galerie — nouvelle couleur issue #534,
+                #                 remplace #BA7517 devenu ambigu avec actualise)
+    "#656812",  # olive/moutarde (ecole — nouvelle couleur issue #534,
+                #                 remplace #6B3FA0 devenu ambigu avec apiselect)
+    "#883894",  # orchidée
+    "#9E2E5F",  # rose foncé / framboise
+    "#76614C",  # taupe (brun grisé, neutre)
+    "#516840",  # sauge (vert grisé, neutre)
 ]
 
+# Couleurs des projets historiques n'ayant pas (encore) de champ COULEUR
+# persisté dans leur .conf : ils tirent leur couleur de la carte fixe
+# COULEURS_PROJET de app.js plutôt que d'une valeur écrite dans le .conf.
+# couleurs_utilisees() ci-dessous ne lit QUE les .conf : sans cette liste, ces
+# couleurs paraîtraient à tort "libres" et pourraient être réattribuées à un
+# nouveau projet — c'est exactement ce qui s'est produit avant l'issue #534
+# (apiselect avait hérité du violet d'ecole, actualise de l'orange de
+# ff_galerie, deux paires alors visuellement indiscernables). Tenue à jour
+# manuellement en synchro avec COULEURS_PROJET dans app.js.
+COULEURS_LEGACY_SANS_CONF = {
+    "#185FA5",  # bridge_agent
+    "#3B6D11",  # alchess
+    "#0E8A82",  # scrabble
+    "#1F7A3D",  # ff_galerie
+    "#656812",  # ecole
+}
+
 # Topic ntfy partagé par tous les projets existants (voir configs/*.conf).
 # Proposé par défaut ; l'utilisateur peut le changer pour un topic dédié.
 TOPIC_NTFY_DEFAUT = "hippocampe-ff-galerie-xyz123"
# ── Zone modifiée : ligne 164 (10 ligne(s)) dans l'ancienne version → ligne 194 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -164,10 +194,12 @@ def conf_existe(nom: str) -> bool:
 
 def couleurs_utilisees() -> set[str]:
     """Ensemble des couleurs (hex minuscules) déjà attribuées à un projet
-    existant, lues depuis le champ COULEUR de chaque configs/*.conf. Lecture
-    minimale et tolérante (même esprit zéro-dépendance que le reste du script) :
-    un .conf illisible est simplement ignoré."""
-    prises: set[str] = set()
+    existant : celles des projets legacy sans champ COULEUR (voir
+    COULEURS_LEGACY_SANS_CONF) plus celles lues depuis le champ COULEUR de
+    chaque configs/*.conf. Lecture minimale et tolérante (même esprit
+    zéro-dépendance que le reste du script) : un .conf illisible est
+    simplement ignoré."""
+    prises: set[str] = {c.lower() for c in COULEURS_LEGACY_SANS_CONF}
     for chemin in DOSSIER_CONFIGS.glob("*.conf"):
         try:
             for brut in chemin.read_text(encoding="utf-8").splitlines():
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 7c23d05..11a8ff2 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 22 (13 ligne(s)) dans l'ancienne version → ligne 22 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -22,13 +22,19 @@ let sourceFinIssue = null;
 // SOURCE UNIQUE DE VÉRITÉ pour la couleur de chaque projet (issue #120).
 // Utilisée à la fois pour l'accent du formulaire (couleurProjet) et pour les
 // pastilles/badges/boutons de l'onglet Résultats (couleurProjetResultats).
-// Les 5 couleurs sont volontairement distinctes visuellement.
+// Sert uniquement aux projets legacy sans champ COULEUR persisté dans leur
+// .conf (les autres projets ont leur couleur écrite dans configs/*.conf, voir
+// couleurProjet ci-dessous). Couleurs volontairement distinctes visuellement
+// (issue #534 : ff_galerie et ecole ont été recolorées ici — leurs anciennes
+// teintes #BA7517/#6B3FA0 étaient devenues identiques à celles, persistées,
+// de actualise/apiselect ; cette carte doit rester en synchro avec
+// COULEURS_LEGACY_SANS_CONF dans nouveau_projet.py).
 const COULEURS_PROJET = {
   'bridge_agent': '#185FA5',  // bleu
   'alchess':      '#3B6D11',  // vert
-  'ff_galerie':   '#BA7517',  // orange
+  'ff_galerie':   '#1F7A3D',  // vert émeraude
   'scrabble':     '#0E8A82',  // turquoise
-  'ecole':        '#6B3FA0',  // violet
+  'ecole':        '#656812',  // olive/moutarde
 };
 
 // Couleur de secours STABLE dérivée du nom du projet (hash simple sur les
