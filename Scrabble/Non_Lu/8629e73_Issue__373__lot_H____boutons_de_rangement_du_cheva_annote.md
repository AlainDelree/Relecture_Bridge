8629e73

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8629e73
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 6 08:08:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #373 (lot H) : boutons de rangement du chevalet (gauche/droite)
    
    Deux boutons « ⇤ »/« ⇥ » dans l'en-tête de « Mes lettres » regroupent les
    lettres restantes en comblant les trous laissés par des poses précédentes,
    ordre relatif préservé. Réutilisent le mécanisme JS local du réarrangement
    manuel existant (panneauLettres) : chevalet vide/lettres déjà posées en
    attente/mode échange partiel gérés. L'ordre du chevalet n'étant jamais
    persisté côté Python (constat documenté dans CHANGELOG et les tests), les
    boutons ont la même portée locale que le glisser au clic déjà en place.
    
    Tests statiques (markup + logique JS) dans test_chevalet_rangement.py, sur
    le modèle de test_accueil_niveaux_visuels.py (issue #371).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0a17222..a026867 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,26 @@ Historique des changements notables, par ordre antéchronologique. Voir aussi
 
 ### Ajouté
 
+- **Issue #373** (lot H) — Deux boutons de rangement du chevalet, « ⇤ » (tout
+  à gauche) et « ⇥ » (tout à droite), placés dans l'en-tête du bloc « 🎴 Mes
+  lettres » : regroupent d'un clic les lettres restantes en comblant les trous
+  laissés par des poses précédentes, ordre relatif préservé (compactage, pas
+  de tri). Boutons `.btn-icone-seule` (cible min 40px, déjà éprouvée pour
+  « ↻ Resynchroniser ») avec `title` au survol, pensés pour une joueuse de
+  plus de 80 ans manipulant à la souris. Cas limites : chevalet vide ou
+  aucune lettre libre → bouton sans effet ; lettres déjà posées en attente
+  sur le plateau → laissées à leur emplacement, seules les lettres restantes
+  du chevalet bougent ; mode échange partiel actif → rangement désactivé
+  (même restriction que le glisser au clic droit existant, issue #138).
+  Réutilise le même mécanisme JS local que le réarrangement manuel déjà en
+  place (« cliquez, réarrangez ») : **l'ordre du chevalet n'est jamais
+  persisté côté Python** (`obtenir_chevalet`/`serialiser_chevalet` ne
+  sérialisent qu'un ensemble de lettres) — un nouveau tirage ou un échange
+  reconstruit le panneau depuis zéro. Les boutons ne sont donc ni plus ni
+  moins durables que le réarrangement manuel existant : aucune régression,
+  mais aucune persistance non plus, comme documenté dans
+  `tests/test_chevalet_rangement.py`.
+
 - **Issue #372** (lot G, suite de #362) — `scripts/mesurer_force_niveaux.py`
   gagne des **paramètres variables**, pour mesurer l'effet d'un réglage sans
   éditer le code de production. Chaque camp (A/B) devient une *configuration*
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.css b/src/scrabble/ui/web/jeu.css
# (index — ignorable)
index 48036ee..adc912b 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.css
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.css
# ── Zone modifiée : ligne 269 (6 ligne(s)) dans l'ancienne version → ligne 269 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -269,6 +269,17 @@ body {
     min-width: 0;
 }
 
+/* Boutons de rangement du chevalet (issue #373) : regrouper d'un clic les
+   lettres restantes tout à gauche ou tout à droite, sans changer leur ordre
+   relatif — utile après quelques poses qui laissent des trous. Réutilisent
+   .btn-icone-seule (cible min 40px, public senior) déjà éprouvé pour
+   « ↻ Resynchroniser ». */
+.panneau-rangement {
+    display: flex;
+    gap: 6px;
+    flex: 0 0 auto;
+}
+
 /* Rangée unique (issue #189) : les 9 emplacements (7 lettres + 2 vides) alignés
    horizontalement sans repli (``nowrap``), centrés dans la largeur du panneau.
    Remplace la grille 3×3 de #187 : la marge élargie (voir .container) offre
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.html b/src/scrabble/ui/web/jeu.html
# (index — ignorable)
index 79922a5..2da1d9d 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.html
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.html
# ── Zone modifiée : ligne 205 (6 ligne(s)) dans l'ancienne version → ligne 205 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -205,6 +205,20 @@
                                 🎴 Mes lettres <span class="bloc-titre-note">— cliquez, réarrangez</span>
                             </span>
                         </span>
+                        <span class="panneau-rangement">
+                            <button type="button" id="btn-ranger-gauche"
+                                    class="btn btn-secondaire btn-icone-seule"
+                                    title="Regrouper mes lettres restantes tout à gauche"
+                                    aria-label="Regrouper mes lettres restantes tout à gauche">
+                                ⇤
+                            </button>
+                            <button type="button" id="btn-ranger-droite"
+                                    class="btn btn-secondaire btn-icone-seule"
+                                    title="Regrouper mes lettres restantes tout à droite"
+                                    aria-label="Regrouper mes lettres restantes tout à droite">
+                                ⇥
+                            </button>
+                        </span>
                     </div>
                     <div id="panneau" class="panneau" aria-label="Chevalet du joueur (réarrangeable)"></div>
                 </div>
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/jeu.js b/src/scrabble/ui/web/jeu.js
# (index — ignorable)
index 54eb1fc..18e29e0 100644
# (avant — fichier suivant)
--- a/src/scrabble/ui/web/jeu.js
# (après — fichier suivant)
+++ b/src/scrabble/ui/web/jeu.js
# ── Zone modifiée : ligne 917 (6 ligne(s)) dans l'ancienne version → ligne 917 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -917,6 +917,10 @@ document.addEventListener('DOMContentLoaded', async () => {
     // garantie de l'issue #99 est donc inchangée ; seule la localisation du DOM
     // change.
     const panneauEl = document.getElementById('panneau');
+    // Boutons de rangement du chevalet (issue #373) : regroupent d'un clic les
+    // lettres restantes à gauche/droite, ordre relatif préservé.
+    const btnRangerGauche = document.getElementById('btn-ranger-gauche');
+    const btnRangerDroite = document.getElementById('btn-ranger-droite');
 
     // Dernier payload chevalet reçu de Python (état privé du joueur de référence).
     // Distinct de ``etat`` (état public du plateau) : ne jamais les confondre.
# ── Zone modifiée : ligne 949 (6 ligne(s)) dans l'ancienne version → ligne 953 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -949,6 +953,7 @@ document.addEventListener('DOMContentLoaded', async () => {
         if (!panneauEl) {
             return;
         }
+        majBoutonsRangement();
         panneauEl.innerHTML = '';
         if (panneauLettres.length === 0) {
             panneauEl.innerHTML = '<span class="panneau-vide">Chevalet vide.</span>';
# ── Zone modifiée : ligne 1223 (6 ligne(s)) dans l'ancienne version → ligne 1228 (72 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1223,6 +1228,72 @@ document.addEventListener('DOMContentLoaded', async () => {
         });
     }
 
+    /** Active/désactive les boutons de rangement (issue #373) : rien à ranger
+     *  si le chevalet est vide, et pas de réarrangement en mode échange
+     *  partiel (issue #138, même restriction que le clic droit). */
+    function majBoutonsRangement() {
+        if (!btnRangerGauche || !btnRangerDroite) {
+            return;
+        }
+        const desactive = panneauLettres.length === 0 || enModeEchange();
+        btnRangerGauche.disabled = desactive;
+        btnRangerDroite.disabled = desactive;
+    }
+
+    /**
+     * Regroupe les lettres RESTANTES du chevalet tout à gauche ou tout à
+     * droite, en préservant leur ordre relatif — on compacte, on ne trie pas
+     * (issue #373). Une lettre déjà posée en attente sur le plateau (case
+     * « utilisee ») reste figée à son emplacement visuel : seules les
+     * lettres encore au chevalet et les cases vides se déplacent, si bien
+     * qu'une pose en cours n'est jamais perturbée par ce rangement. Purement
+     * local (même mécanisme que le glisser au clic ci-dessus) : voir la
+     * docstring de la section « Chevalet du joueur humain de référence »
+     * plus haut pour le constat sur la non-persistance côté Python.
+     */
+    function rangerChevalet(direction) {
+        if (enModeEchange() || panneauLettres.length === 0) {
+            return;
+        }
+        const utilises = indexUtilises();
+        // Positions libres de bouger (non « utilisee ») et lettres restantes
+        // trouvées à ces positions, dans leur ordre d'apparition.
+        const positions = [];
+        const lettresLibres = [];
+        panneauLettres.forEach((l, i) => {
+            if (l !== null && utilises.has(l.indexOrigine)) {
+                return;
+            }
+            positions.push(i);
+            if (l !== null) {
+                lettresLibres.push(l);
+            }
+        });
+        if (lettresLibres.length === 0 || lettresLibres.length === positions.length) {
+            return; // rien de libre à déplacer, ou déjà totalement tassé
+        }
+        const decalage = direction === 'droite' ? positions.length - lettresLibres.length : 0;
+        positions.forEach((pos, i) => {
+            const rang = i - decalage;
+            panneauLettres[pos] =
+                (rang >= 0 && rang < lettresLibres.length) ? lettresLibres[rang] : null;
+        });
+        // Une sélection de pose en cours porte sur un index de panneauLettres
+        // qui vient de bouger : on l'annule, comme au déplacement par clic.
+        if (panneauSelection !== null) {
+            panneauSelection = null;
+            api.selectionner_lettre(null);
+        }
+        rendrePanneau();
+    }
+
+    if (btnRangerGauche) {
+        btnRangerGauche.addEventListener('click', () => rangerChevalet('gauche'));
+    }
+    if (btnRangerDroite) {
+        btnRangerDroite.addEventListener('click', () => rangerChevalet('droite'));
+    }
+
     /**
      * Anime le dernier coup s'il vient d'apparaître (issue #62). Détecte
      * l'apparition d'un NOUVEAU coup (index qui change) plutôt que de ré-animer
# (diff du fichier suivant)
diff --git a/tests/test_chevalet_rangement.py b/tests/test_chevalet_rangement.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..5ba8f57
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_chevalet_rangement.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (164 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,164 @@
+"""Tests des boutons de rangement du chevalet « tout à gauche / tout à droite »
+(issue #373, lot H).
+
+Le réarrangement du chevalet — manuel (clic-clic, drag droit) comme celui de
+ces deux nouveaux boutons — est une pure mécanique JS locale : Python ne
+sérialise jamais d'ordre de chevalet (voir ``obtenir_chevalet``/
+``serialiser_chevalet``, ``api_tirage_ordre.py``/``jeu.py``), seulement
+l'ensemble des lettres. Il n'y a donc rien à tester côté Python pour cette
+fonctionnalité ; on vérifie ici, comme pour le lot F (issue #371,
+``test_accueil_niveaux_visuels.py``), le markup et la logique JS par lecture
+statique des fichiers de ``ui/web/``.
+"""
+
+import re
+
+from scrabble.ui.jeu import DOSSIER_WEB
+
+
+def _lire(nom: str) -> str:
+    return (DOSSIER_WEB / nom).read_text(encoding="utf-8")
+
+
+class TestBoutonsPresents:
+    """Les deux boutons existent dans le markup, avec un ``title`` explicite."""
+
+    def test_bouton_gauche_present(self):
+        html = _lire("jeu.html")
+        assert 'id="btn-ranger-gauche"' in html
+
+    def test_bouton_droite_present(self):
+        html = _lire("jeu.html")
+        assert 'id="btn-ranger-droite"' in html
+
+    def test_boutons_ont_un_title_comprehensible(self):
+        html = _lire("jeu.html")
+        for id_bouton in ("btn-ranger-gauche", "btn-ranger-droite"):
+            m = re.search(
+                r'<button\b[^>]*\bid="' + id_bouton + r'"[^>]*>', html
+            )
+            assert m, f"{id_bouton} introuvable"
+            balise = m.group(0)
+            assert 'title="' in balise and 'title=""' not in balise, (
+                f"{id_bouton} sans title exploitable au survol"
+            )
+
+    def test_boutons_reutilisent_la_classe_cible_accessible(self):
+        """Cible de clic suffisamment grande (public senior, issue #373) :
+        réutilise ``.btn-icone-seule`` (min 40px), déjà éprouvée pour
+        « ↻ Resynchroniser »."""
+        html = _lire("jeu.html")
+        for id_bouton in ("btn-ranger-gauche", "btn-ranger-droite"):
+            m = re.search(
+                r'<button\b[^>]*\bid="' + id_bouton + r'"[^>]*>', html
+            )
+            assert "btn-icone-seule" in m.group(0)
+
+    def test_css_min_width_40px_pour_cible_accessible(self):
+        css = _lire("jeu.css")
+        bloc = re.search(r"\.btn-icone-seule\s*\{([^}]+)\}", css)
+        assert bloc, ".btn-icone-seule introuvable dans jeu.css"
+        assert "min-width: 40px" in bloc.group(1)
+
+
+class TestCablageJS:
+    """Les boutons sont câblés à la fonction de rangement dans jeu.js."""
+
+    def test_ecouteurs_de_clic_presents(self):
+        js = _lire("jeu.js")
+        assert "btnRangerGauche.addEventListener('click'" in js
+        assert "btnRangerDroite.addEventListener('click'" in js
+
+    def test_appel_avec_la_bonne_direction(self):
+        js = _lire("jeu.js")
+        assert "rangerChevalet('gauche')" in js
+        assert "rangerChevalet('droite')" in js
+
+    def test_fonction_rangerChevalet_definie(self):
+        js = _lire("jeu.js")
+        assert "function rangerChevalet(direction)" in js
+
+
+class TestCompactageLogiqueJS:
+    """Comportement attendu de ``rangerChevalet`` (lecture statique du corps).
+
+    On ne peut pas exécuter le JS directement en pytest (pas de moteur JS
+    dans la suite) : on vérifie donc, comme le lot F pour les maps de
+    libellés, la PRÉSENCE des garde-fous attendus dans le corps de la
+    fonction — chevalet vide, mode échange partiel, lettres déjà posées en
+    attente (« utilisee ») laissées de côté, ordre relatif préservé.
+    """
+
+    @staticmethod
+    def _corps() -> str:
+        js = _lire("jeu.js")
+        m = re.search(
+            r"function rangerChevalet\(direction\) \{(.*?)\n    \}",
+            js,
+            re.DOTALL,
+        )
+        assert m, "corps de rangerChevalet introuvable"
+        return m.group(1)
+
+    def test_ignore_le_mode_echange_partiel(self):
+        """Cas limite : pas de rangement pendant le marquage d'échange partiel
+        (issue #138) — même restriction que le clic droit existant."""
+        corps = self._corps()
+        assert "enModeEchange()" in corps
+
+    def test_ignore_chevalet_vide(self):
+        corps = self._corps()
+        assert "panneauLettres.length === 0" in corps
+
+    def test_ne_deplace_pas_les_lettres_deja_posees(self):
+        """Cas limite : une pose en cours (lettre « utilisee ») n'est jamais
+        perturbée — seules les lettres RESTANTES du chevalet bougent (choix
+        documenté dans le commentaire de la fonction, issue #373)."""
+        corps = self._corps()
+        assert "indexUtilises" in corps or "utilises" in corps
+        assert "utilises.has(l.indexOrigine)" in corps
+
+    def test_preserve_l_ordre_relatif_sans_trier(self):
+        """Le compactage lit ``lettresLibres`` dans l'ordre d'apparition puis
+        les replace dans ce même ordre — aucun ``.sort()`` n'intervient."""
+        corps = self._corps()
+        assert ".sort(" not in corps
+
+    def test_decalage_nul_a_gauche_et_vers_la_fin_a_droite(self):
+        corps = self._corps()
+        assert "direction === 'droite'" in corps
+        assert "positions.length - lettresLibres.length" in corps
+
+
+class TestPersistanceChevaletCotePython:
+    """Constat de l'issue (point 3) : l'ordre du chevalet est-il persisté ?
+
+    Réponse : NON — ni pour le réarrangement manuel existant, ni pour ces
+    nouveaux boutons. ``serialiser_chevalet``/``obtenir_chevalet`` ne
+    sérialisent qu'un ENSEMBLE de lettres (dans l'ordre du modèle Python,
+    inchangé par la réflexion JS) ; le réarrangement visuel ne vit que dans
+    ``panneauLettres`` côté navigateur et est reconstruit dès que le contenu
+    du chevalet change (nouveau tirage, échange) — voir
+    ``reconstruirePanneau``/``appliquerEtatChevalet``. Les boutons de
+    rangement suivent exactement le même mécanisme que le glisser au clic
+    déjà en place : ni plus ni moins persistants que lui, donc aucune
+    régression introduite. Ce test documente ce constat pour éviter qu'une
+    future modification ne le suppose à tort persisté côté serveur.
+    """
+
+    def test_obtenir_chevalet_ne_renvoie_pas_de_champ_ordre(self):
+        import inspect
+
+        from scrabble.ui.api_tirage_ordre import MixinTirageOrdre
+
+        source = inspect.getsource(MixinTirageOrdre.obtenir_chevalet)
+        assert "ordre" not in source.lower()
+
+    def test_reconstruction_du_panneau_efface_le_rangement_local(self):
+        """``reconstruirePanneau`` reconstruit ``panneauLettres`` depuis
+        ``etatChevalet.lettres`` (l'ordre Python) : tout rangement local —
+        manuel ou via ces boutons — est perdu au tirage/échange suivant."""
+        js = _lire("jeu.js")
+        m = re.search(r"function reconstruirePanneau\(\) \{(.*?)\n    \}", js, re.DOTALL)
+        assert m, "reconstruirePanneau introuvable"
+        assert "etatChevalet.lettres" in m.group(1)
