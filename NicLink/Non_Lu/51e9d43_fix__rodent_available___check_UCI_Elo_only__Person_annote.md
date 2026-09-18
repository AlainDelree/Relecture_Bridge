51e9d43

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 51e9d43
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 23:10:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: rodent_available() check UCI_Elo only (PersonalityFile not Personality)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/engine/engine_manager.py b/nicsoft/engine/engine_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a08fa9e..7ad1b10 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/engine/engine_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/engine/engine_manager.py
# ── Zone modifiée : ligne 526 (9 ligne(s)) dans l'ancienne version → ligne 526 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -526,9 +526,9 @@ def rodent_available() -> bool:
 
     Ne se contente pas de vérifier la présence du binaire : le lance réellement
     et exige que le handshake UCI aboutisse (`uci` + `isready`, effectués par
-    `popen_uci`) ET que les options attendues soient exposées (`Personality`,
-    `UCI_Elo`) — garantie qu'il s'agit bien de Rodent IV et non d'un binaire
-    corrompu ou incompatible. À appeler côté UI/menu avant d'offrir le moteur.
+    `popen_uci`) ET que l'option attendue soit exposée (`UCI_Elo`) — garantie
+    qu'il s'agit bien de Rodent IV et non d'un binaire corrompu ou
+    incompatible. À appeler côté UI/menu avant d'offrir le moteur.
     """
     path = find_rodent()
     if not path:
# ── Zone modifiée : ligne 536 (7 ligne(s)) dans l'ancienne version → ligne 536 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -536,7 +536,7 @@ def rodent_available() -> bool:
     engine = None
     try:
         engine = chess.engine.SimpleEngine.popen_uci(path)
-        return "Personality" in engine.options and "UCI_Elo" in engine.options
+        return "UCI_Elo" in engine.options
     except Exception as e:
         logger.warning(f"Rodent IV présent mais ne répond pas au handshake UCI : {e}")
         return False
