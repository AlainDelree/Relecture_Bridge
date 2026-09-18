12b5314

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 12b5314
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 23:03:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Met à jour ETAT.md : note chemins VirtualBox caduque supprimée (issue #50)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/ETAT.md b/ETAT.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 163e2b6..7791c58 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/ETAT.md
# ── Version APRÈS ce commit.
+++ b/ETAT.md
# ── Zone modifiée : ligne 24 (6 ligne(s)) dans l'ancienne version → ligne 24 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,6 +24,6 @@
 
 ## Points en suspens
 - Builds CCW pas encore testés sur le nouveau PC fixe Windows (Samba,
-  remplace la VM VirtualBox). Chemins VirtualBox (\\VBOXSVR\CCW_Share\,
-  Z:\CCW\) dans les scripts de build à adapter au nouveau partage Samba.
+  remplace la VM VirtualBox). Audit confirmé : aucun script de build actif
+  ne référence plus les anciens chemins VirtualBox.
 - verifier_installation.py existe comme script standalone (pas dans un dépôt)
