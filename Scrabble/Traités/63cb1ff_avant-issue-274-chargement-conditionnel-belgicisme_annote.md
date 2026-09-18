63cb1ff

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 63cb1ff
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 22:00:01 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-issue-274-chargement-conditionnel-belgicismes-dictionnaire

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 008c5bd..c5a2a17 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 12 (6 ligne(s)) dans l'ancienne version → ligne 12 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -12,6 +12,10 @@ sessions.
 -Quand vérifier dictionnaire perd le focus il se referme, il faut que derniers coups fasse de meme.
 -Afficher tous les coups du jeu dans derniers coups(les coups les plus récent en haut)
 
+##Creer un fichier meilleurs score
+Creer un fichiers meilleur score répartis en 3 catégories(1vs1, 1vs2, 1vs3) et par niveaux(Débutant, facile, Intermédiaire, Avancé, Expert)
+Garder les 10 meilleurs score par combinaison catégorie/niveau
+
 ## Creer TextField constemment visible pourle dictionnaire
 
 Vu la fréquence d'utilisation du dictionnaire dans l'écran de jeu observée, il faut remplacer le bouton loupe, ouvrant un textfield pour chercher la définition d'un mot par le textefield accessible directement dans l'ecran
