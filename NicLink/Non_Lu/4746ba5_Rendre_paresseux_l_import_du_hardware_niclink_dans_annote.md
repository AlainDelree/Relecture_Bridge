4746ba5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4746ba5
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 08:55:05 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Rendre paresseux l'import du hardware niclink dans nicsoft/__init__.py (issue #204)
    
    Retire l'import eager 'from . import niclink' qui déclenchait le chargement
    complet du driver Chessnut (et hidapi) au premier import de n'importe quel
    sous-module du package nicsoft. Aucun usage implicite trouvé ailleurs dans
    le code (tous les accès à nicsoft.niclink passent déjà par un import direct
    explicite) — aucune adaptation nécessaire en dehors de ce fichier.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/__init__.py b/nicsoft/__init__.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7b4a8e2..e69de29 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/__init__.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/__init__.py
# ── Zone modifiée : ligne 1 (1 ligne(s)) dans l'ancienne version → ligne 0 (0 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1 +0,0 @@
-from . import niclink
