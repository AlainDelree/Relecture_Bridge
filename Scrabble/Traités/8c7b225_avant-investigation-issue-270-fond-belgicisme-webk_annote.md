8c7b225

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8c7b225
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 20:52:33 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-investigation-issue-270-fond-belgicisme-webkitgtk

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d69f732..008c5bd 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 12 (18 ligne(s)) dans l'ancienne version → ligne 12 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -12,18 +12,9 @@ sessions.
 -Quand vérifier dictionnaire perd le focus il se referme, il faut que derniers coups fasse de meme.
 -Afficher tous les coups du jeu dans derniers coups(les coups les plus récent en haut)
 
-## Fenêtre de réglages avec onglets (dictionnaire)
+## Creer TextField constemment visible pourle dictionnaire
 
-Nouvelle fenêtre graphique de réglages (pywebview, séparée de l'écran de
-jeu), avec au moins 2 onglets :
-- **Général** : réglages existants (prénom, thème, mode de saisie...)
-- **Dictionnaire** : recherche d'un mot, affichage par source (ODS /
-  Hunspell) avec statut présent/absent + bouton Ajouter/Supprimer +
-  définition
-
-Prérequis : séparer `mots_ajoutes.txt`/`mots_retires.txt` par source (une
-paire par source : ODS et Hunspell) pour que les personnalisations
-restent indépendantes entre les deux sources.
+Vu la fréquence d'utilisation du dictionnaire dans l'écran de jeu observée, il faut remplacer le bouton loupe, ouvrant un textfield pour chercher la définition d'un mot par le textefield accessible directement dans l'ecran
 
 ## Point de vigilance : gestion d'erreurs dans accueil.py
 
# (diff du fichier suivant)
diff --git a/data/dictionnaire/belgicismes_a_revoir.csv b/data/dictionnaire/belgicismes_a_revoir.csv
# (index — ignorable)
index e72c3fa..84991c0 100644
# (avant — fichier suivant)
--- a/data/dictionnaire/belgicismes_a_revoir.csv
# (après — fichier suivant)
+++ b/data/dictionnaire/belgicismes_a_revoir.csv
# ── Zone modifiée : ligne 577 (8 ligne(s)) dans l'ancienne version → ligne 577 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -577,8 +577,8 @@ national-royalisme,"Idéologie politique de droite radicale mêlant nationalisme
 nenni,ou Expression négative qu’on emploie pour marquer un refus catégorique ou encore par plaisanterie dans les réponses.,non,oui
 nominette,Étiquette nominative.,non,non
 nonantaine,"Nombre d’environ nonante, quatre-vingt-dix. | Âge d’environ nonante ans.",non,non
-nonante,"Quatre-vingt-neuf/huitante-neuf plus un, soit neuf fois dix, adjectif numéral cardinal correspondant au nombre 90. | ou ou pour des raisons pratiques (Mathématiques, Bourse). Le nombre 90, entier naturel après quatre-vingt-neuf/huitante-neuf. | Chose portant le numéro 90. | Année qui se termine par 90, par exemple 1990.",non,oui
-nonante-cinq,"quatre-vingt-quinze. | 95, quatre-vingt-quinze.",non,non
+nonante,90.,non,oui
+nonante-cinq,95.,non,non
 nonante-deux,92.,non,non
 nonante-et-un,91.,non,non
 nonante-huit,98.,non,non
# ── Zone modifiée : ligne 755 (12 ligne(s)) dans l'ancienne version → ligne 755 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -755,12 +755,12 @@ scribain,"Coffre sur console, au milieu duquel est une espèce de tabernacle int
 section,Subdivision des communes correspondant aux anciennes communes avant la fusion des communes.,non,oui
 septantaine,"ou Nombre d’environ septante, soixante-dix. | ou Âge de septante ans, ou allant de septante à quatre-vingts ans.",non,non
 septantaines,Pluriel de septantaine.,non,non
-septante,"Soixante-neuf plus un, soit sept fois dix, adjectif numéral cardinal correspondant au nombre 70. | ou pour des raisons pratiques (Mathématiques, Bourse). Le nombre 70.",non,oui
+septante,70.,non,oui
 septante-cinq,75.,non,non
 septante-deux,72.,non,non
-septante-et-un,ou Le nombre 71.,non,oui
+septante-et-un,71.,non,oui
 septante-huit,78.,non,non
-septante-neuf,"79, soixante-dix-neuf.",non,non
+septante-neuf,79.,non,non
 septante-quatre,74.,non,non
 septante-sept,77.,non,non
 septante-six,76.,non,non
