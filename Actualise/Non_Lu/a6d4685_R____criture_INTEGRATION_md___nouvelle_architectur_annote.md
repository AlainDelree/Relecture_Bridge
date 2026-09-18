a6d4685

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a6d4685
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 21:17:05 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Réécriture INTEGRATION.md : nouvelle architecture multi-app (issue #38)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/INTEGRATION.md b/INTEGRATION.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 19af184..cba1d8a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/INTEGRATION.md
# ── Version APRÈS ce commit.
+++ b/INTEGRATION.md
# ── Zone modifiée : ligne 10 (6 ligne(s)) dans l'ancienne version → ligne 10 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -10,6 +10,7 @@ Actualise est une instance unique partagée entre toutes les applications cibles
 
 ## 3. Checklist d'intégration pour un nouveau projet cible
 
+- **Droits d'installation** : le setup doit utiliser `PrivilegesRequired=admin` (jamais `lowest`) pour pouvoir créer et écrire dans `C:\Actualise\` (racine du disque système, inaccessible en écriture aux utilisateurs standards). Avec `admin`, les constantes InnoSetup `{autopf}`, `{autodesktop}` et `{autoprograms}` résolvent vers les emplacements "tous les utilisateurs" (C:\Program Files\, Bureau commun, menu Démarrer commun). Incident réel : avec `lowest`, Actualise n'est pas déployé, le raccourci pointe vers l'ancienne installation et l'application ne démarre pas.
 - **Dossier Actualise partagé** : `C:\Actualise\` — jamais un dossier par app.
 - **Deux fichiers de config** à créer par le setup InnoSetup :
   - `C:\Actualise\config_actualise.json` — uniquement s'il n'existe pas déjà (ne pas écraser si une autre app l'a déjà créé).
# ── Zone modifiée : ligne 55 (7 ligne(s)) dans l'ancienne version → ligne 56 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -55,7 +56,7 @@ Actualise est une instance unique partagée entre toutes les applications cibles
 - Asset zip nommé `<prefixe>-v<build>.zip` (ex. `scrabble-v8.zip`) — Actualise construit l'URL dynamiquement à partir du numéro de build.
 - Tag GitHub : `v<build>` (ex. `v8`).
 - Le zip doit être à plat : exécutable et `_internal\` directement à la racine, sans sous-dossier intermédiaire.
-- Inclure un `manifest.json` à la racine : `{"supprimer": []}` (liste des fichiers à nettoyer lors de l'installation, vide par défaut).
+- Inclure un `manifest.json` à la racine : `{"supprimer": []}`.
 - L'app cible doit publier son propre `version.json` à la racine du dépôt : `{"build": N, "sha256": "..."}`.
 
 ## 6. Intégration dans le code de l'application cible
