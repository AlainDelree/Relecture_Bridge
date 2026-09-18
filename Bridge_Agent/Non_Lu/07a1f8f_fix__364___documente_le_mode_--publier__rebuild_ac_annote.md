07a1f8f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 07a1f8f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 18:37:43 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #364 : documente le mode --publier (rebuild_actualise.bat) et relais for-windows #365

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BUILD_WINDOWS_CCW.md b/BUILD_WINDOWS_CCW.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 8747c68..a9d6744 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BUILD_WINDOWS_CCW.md
# ── Version APRÈS ce commit.
+++ b/BUILD_WINDOWS_CCW.md
# ── Zone modifiée : ligne 67 (6 ligne(s)) dans l'ancienne version → ligne 67 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -67,6 +67,15 @@ build suit déjà ce schéma de staging local et, si oui, étendre le
   `Actualise.exe` seul : 4 388 786 octets, SHA-256
   `61A3373D6EE2D48A357E34BA9E967236B101F3F580BD98BC20DD667C86772F47`
   (référence du 3 août 2026)
+- **Mode `--publier`** (suite #328/#329, demandé par #364, implémenté côté
+  CCW via l'issue for-windows #365 — `rebuild_actualise.bat` vit dans le
+  dépôt Actualise, hors périmètre CCL) : après un build réussi, construit
+  `actualise.zip` (manifeste `{"build": N, "supprimer": []}`), détermine le
+  numéro de build (auto = `version.json` existant + 1, ou forcé via
+  `--publier --build N`), calcule le SHA-256 du zip, écrit `version.json`
+  (`{"build": N, "sha256": "..."}`) et fait un commit local sur le dépôt
+  Actualise — jamais de `git push` ni de Release GitHub (restent manuels,
+  à la charge d'Alain). Comportement par défaut (sans paramètre) inchangé.
 
 ## Rummikub
 
