92db1a5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 92db1a5
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 23:58:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Met à jour ETAT.md : builds CCW sur PC fixe validés (issue #51)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/ETAT.md b/ETAT.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7791c58..6a86ab2 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/ETAT.md
# ── Version APRÈS ce commit.
+++ b/ETAT.md
# ── Zone modifiée : ligne 23 (7 ligne(s)) dans l'ancienne version → ligne 23 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -23,7 +23,7 @@
 7. Lancer Scrabble
 
 ## Points en suspens
-- Builds CCW pas encore testés sur le nouveau PC fixe Windows (Samba,
-  remplace la VM VirtualBox). Audit confirmé : aucun script de build actif
-  ne référence plus les anciens chemins VirtualBox.
+- Builds CCW sur le nouveau PC fixe Windows (Samba, remplace la VM
+  VirtualBox) validés le 20 août 2026 : chaîne PyInstaller + ISCC
+  fonctionnelle, Actualise-Setup-v9.exe produit sans erreur.
 - verifier_installation.py existe comme script standalone (pas dans un dépôt)
