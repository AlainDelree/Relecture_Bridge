74c7c20

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 74c7c20
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 10:37:57 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #302 : essai visuel — fond tapis vert dans .zone-centrale en mode France (miroir bande tricolore Belgicisme)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/_harness_jeu/i296_belgique_rempli_1280x800.png b/scripts/_harness_jeu/i296_belgique_rempli_1280x800.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..bbd72e4
Binary files /dev/null and b/scripts/_harness_jeu/i296_belgique_rempli_1280x800.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_belgique_rempli_700x800.png b/scripts/_harness_jeu/i296_belgique_rempli_700x800.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..e253198
Binary files /dev/null and b/scripts/_harness_jeu/i296_belgique_rempli_700x800.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_belgique_vide_700x800.png b/scripts/_harness_jeu/i296_belgique_vide_700x800.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..bd7edbb
Binary files /dev/null and b/scripts/_harness_jeu/i296_belgique_vide_700x800.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_france_rempli_1280x800.png b/scripts/_harness_jeu/i296_france_rempli_1280x800.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..8ba2cfd
Binary files /dev/null and b/scripts/_harness_jeu/i296_france_rempli_1280x800.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_france_rempli_700x800.png b/scripts/_harness_jeu/i296_france_rempli_700x800.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..2502186
Binary files /dev/null and b/scripts/_harness_jeu/i296_france_rempli_700x800.png differ
# (diff du fichier suivant)
diff --git a/scripts/_harness_jeu/i296_france_vide_700x800.png b/scripts/_harness_jeu/i296_france_vide_700x800.png
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..de8d193
Binary files /dev/null and b/scripts/_harness_jeu/i296_france_vide_700x800.png differ
# (diff du fichier suivant)
diff --git a/src/scrabble/ui/web/accueil.css b/src/scrabble/ui/web/accueil.css
# (index — ignorable)
index 4314576..34588d3 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/web/accueil.css
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/web/accueil.css
# ── Zone modifiée : ligne 689 (6 ligne(s)) dans l'ancienne version → ligne 689 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -689,6 +689,20 @@ body:not(.mode-belgicisme) .titre-section-tuiles .lettre-scrabble {
     background: #ffffff;
 }
 
+/* Essai visuel (issue #302) : en mode France, surclasse le blanc uni
+   ci-dessus par le même tapis vert que le fond de `body` (dégradé radial
+   défini tout en haut de ce fichier), en miroir de la bande tricolore
+   ajoutée plus bas pour le mode Belgicisme — objectif de cohérence
+   visuelle symétrique entre les deux modes. Les cartes Joueurs/Parties en
+   cours gardent leur propre fond blanc opaque (`.liste-joueurs`,
+   `.parties-en-cours` ci-dessous) : seuls les espaces entre elles et les
+   titres en tuiles se retrouvent sur ce vert plutôt que sur du blanc. */
+body:not(.mode-belgicisme) .zone-centrale {
+    background: var(--tapis-vert);
+    background-image:
+        radial-gradient(120% 90% at 50% 30%, var(--tapis-vert-clair) 0%, var(--tapis-vert) 55%, var(--tapis-vert-fonce) 100%);
+}
+
 /* Les sections Joueurs/Continuer perdent leur marge de section générique
    (24px) une fois réunies dans `.zone-centrale` : sans ce nettoyage (issue
    #295, point 2g), la marge du bas de `.table-joueurs` créait un vide blanc
