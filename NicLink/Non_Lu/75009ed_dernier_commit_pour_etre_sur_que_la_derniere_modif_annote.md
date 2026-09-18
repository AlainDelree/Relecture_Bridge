75009ed

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 75009ed
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 22:06:33 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    dernier commit pour etre sur que la derniere modification ne soit pas ecraser

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7d1e51c..aa00e7a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 42 (7 ligne(s)) dans l'ancienne version → ligne 42 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -42,7 +42,7 @@
 - **Réduire la taille des ZIP** (~210/215 Mo) — élagage `books/`/`exe/`/`docs/` de Rodent à valider avec Alain.
 - **i18n — corrections résiduelles au fil des tests DE** (edge cases, `eco_import.py`).
 - **Améliorer la visibilité moteurs de recherche** `[Les deux]` — image de prévisualisation sociale, communautés (r/chess, forums Chessnut).
-
+- **Permettre de choisir une couleur par défaut dans partie pédagogique**  Je sais que Jess préfère jouer les noirs mais actuellement les blancs sont sélectionnés par défaut.  On peut changer ca via une checkbox "Faire de ce choix ma couleur par défaut"
 ---
 
 ## 🧪 Tests automatisés
