051c819

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 051c819
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 18:09:57 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute le numéro de build au nom de l'asset Release GitHub (issue #32)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/actualise.py b/actualise.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9d50dce..9813aeb 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/actualise.py
# ── Version APRÈS ce commit.
+++ b/actualise.py
# ── Zone modifiée : ligne 289 (11 ligne(s)) dans l'ancienne version → ligne 289 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -289,11 +289,11 @@ def _url_asset_release(depot_github: str, build: int, prefixe: str) -> str:
     Voir CONCEPTION.md, « Distribution des binaires — GitHub Releases » :
     un seul asset zip par tag, le tag étant ``v<build>`` (ex. ``v48``).
     Convention retenue ici pour le nom de fichier de l'asset publié :
-    ``<prefixe>.zip`` (ex. ``actualise.zip``, ``scrabble.zip``) — à
-    documenter/adapter si un autre nommage d'asset est publié côté
-    Release.
+    ``<prefixe>-v<build>.zip`` (ex. ``actualise-v48.zip``,
+    ``scrabble-v4.zip``) — à documenter/adapter si un autre nommage
+    d'asset est publié côté Release.
     """
-    return _GABARIT_URL_RELEASE.format(depot=depot_github, build=build, fichier=f"{prefixe}.zip")
+    return _GABARIT_URL_RELEASE.format(depot=depot_github, build=build, fichier=f"{prefixe}-v{build}.zip")
 
 
 def tache_verification_arriere_plan() -> None:
