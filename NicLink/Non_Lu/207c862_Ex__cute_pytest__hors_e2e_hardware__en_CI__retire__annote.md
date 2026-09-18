207c862

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 207c862
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 10:35:11 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Exécute pytest (hors e2e/hardware) en CI, retire le commentaire pybind11 obsolète (issue #209)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.github/workflows/python-app.yml b/.github/workflows/python-app.yml
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ac1c21f..f92e78c 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.github/workflows/python-app.yml
# ── Version APRÈS ce commit.
+++ b/.github/workflows/python-app.yml
# ── Zone modifiée : ligne 1 (7 ligne(s)) dans l'ancienne version → ligne 1 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,7 +1,7 @@
-# This workflow will install Python dependencies, it can not run test's bc pybind11 jank
+# This workflow installs Python dependencies and runs the pytest suite (hors e2e et hardware).
 # For more information see: https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python
 
-name: insall NicLink python deps
+name: NicLink python deps + tests
 
 on:
   push:
# ── Zone modifiée : ligne 28 (4 ligne(s)) dans l'ancienne version → ligne 28 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,4 +28,7 @@ jobs:
         python -m pip install --upgrade pip
         pip install flake8 pytest
         if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
+    - name: Run tests (hors e2e et hardware)
+      run: |
+        pytest --ignore=nicsoft/tests/e2e -m "not hardware"
 
