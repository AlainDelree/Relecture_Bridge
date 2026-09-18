5720fb6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5720fb6
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 18:07:48 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: numpy>=1.26.4 dans requirements.txt (issue #180)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/requirements.txt b/requirements.txt
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 28424e6..b9edbf2 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/requirements.txt
# ── Version APRÈS ce commit.
+++ b/requirements.txt
# ── Zone modifiée : ligne 2 (7 ligne(s)) dans l'ancienne version → ligne 2 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2,7 +2,7 @@ berserk==0.13.2
 pyproject-toml==0.0.10
 setuptools==69.1.1
 pybind11==2.11.1
-numpy==1.26.4
+numpy>=1.26.4
 chess==1.10.0
 readchar==4.0.5
 pyserial==3.5
