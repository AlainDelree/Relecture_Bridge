596e867

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 596e867
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 12:24:39 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    chore: longueur minimale du mot de passe ramenée à 6 caractères

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/data-worker/gerer-utilisateurs.sh b/data-worker/gerer-utilisateurs.sh
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0707dfa..2823eb6 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/data-worker/gerer-utilisateurs.sh
# ── Version APRÈS ce commit.
+++ b/data-worker/gerer-utilisateurs.sh
# ── Zone modifiée : ligne 70 (10 ligne(s)) dans l'ancienne version → ligne 70 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -70,10 +70,10 @@ echo
 # du worker ne protège plus grand-chose. On redemande la saisie plutôt que
 # de sortir en erreur.
 while true; do
-  read -r -s -p "Mot de passe pour $NOM (12 caractères minimum) : " MOT_DE_PASSE
+  read -r -s -p "Mot de passe pour $NOM (6 caractères minimum) : " MOT_DE_PASSE
   echo
-  if [[ "${#MOT_DE_PASSE}" -lt 12 ]]; then
-    echo "  → trop court (${#MOT_DE_PASSE} caractère(s)), il en faut au moins 12. Recommence."
+  if [[ "${#MOT_DE_PASSE}" -lt 6 ]]; then
+    echo "  → trop court (${#MOT_DE_PASSE} caractère(s)), il en faut au moins 6. Recommence."
     continue
   fi
   break
