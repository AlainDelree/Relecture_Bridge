bc8c82d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bc8c82d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 3 00:56:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #346 : ajout entrée Actualise à BUILD_WINDOWS_CCW.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BUILD_WINDOWS_CCW.md b/BUILD_WINDOWS_CCW.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2e5dd9f..8747c68 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BUILD_WINDOWS_CCW.md
# ── Version APRÈS ce commit.
+++ b/BUILD_WINDOWS_CCW.md
# ── Zone modifiée : ligne 48 (6 ligne(s)) dans l'ancienne version → ligne 48 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -48,6 +48,26 @@ build suit déjà ce schéma de staging local et, si oui, étendre le
 
 ---
 
+## Actualise
+
+- **Chemin du clone CCW** : `Z:\CCW\actualise` (dépôt AlainDelree/Actualise,
+  public)
+- **Script de build** : `build\rebuild_actualise.bat` (staging local
+  `C:\Temp\ActualiseBuild`, PAS d'étape Inno Setup — Actualise se
+  distribue en `dist\Actualise\` nu via Release GitHub, pas d'installeur)
+- **`.spec`** : `actualise.spec` — `--onedir --noconsole` (invisible
+  pendant que l'application cible tourne, logging fichier compense, voir
+  `CONCEPTION.md` du projet Actualise) ; `datas=[]` explicite
+  (`config.json` est externe, jamais embarqué) ; `hiddenimports=[]`
+  (`requests` détecté seul par PyInstaller)
+- **TIMEOUT de référence observé** : build réel 90,47 s (marge très
+  confortable avec le TIMEOUT de 1800s utilisé)
+- **Taille de référence de l'artefact final** : `dist\Actualise\` non
+  compressé, 20 970 000 octets environ (20,97 Mo, 29 fichiers) —
+  `Actualise.exe` seul : 4 388 786 octets, SHA-256
+  `61A3373D6EE2D48A357E34BA9E967236B101F3F580BD98BC20DD667C86772F47`
+  (référence du 3 août 2026)
+
 ## Rummikub
 
 - **Chemin du clone CCW** : `Z:\CCW\rummikub`
