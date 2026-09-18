9e5b4d6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9e5b4d6
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 12:44:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #452 : maj eval-expiration.json pour le PC fixe physique (17 aout - 15 nov 2026)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-452.md b/CHANGELOG-452.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..e52b4be
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-452.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,8 @@
+## 18 août 2026 — issue #452
+
+CONFIG — `provisioning/windows/eval-expiration.json` mis à jour pour
+refléter l'échéance réelle du PC fixe physique (remplaçant l'ancienne VM
+VirtualBox, cf. #449/#450), installé le 17 août 2026.
+- `date_installation` : `2026-07-19` → `2026-08-17`.
+- `date_expiration` : `2026-10-17` → `2026-11-15` (date_installation +
+  eval_jours = 90 jours, conforme à la note du fichier).
# (diff du fichier suivant)
diff --git a/provisioning/windows/eval-expiration.json b/provisioning/windows/eval-expiration.json
# (index — ignorable)
index 69ed8b0..ccbb944 100644
# (avant — fichier suivant)
--- a/provisioning/windows/eval-expiration.json
# (après — fichier suivant)
+++ b/provisioning/windows/eval-expiration.json
# ── Zone modifiée : ligne 3 (7 ligne(s)) dans l'ancienne version → ligne 3 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3,7 +3,7 @@
   "vm": "CCW-Build",
   "windows": "Windows 11 IoT Enterprise LTSC 2024",
   "eval_jours": 90,
-  "date_installation": "2026-07-19",
-  "date_expiration": "2026-10-17",
+  "date_installation": "2026-08-17",
+  "date_expiration": "2026-11-15",
   "note": "date_installation = date d'installation effective de Windows dans la VM. date_expiration = date_installation + eval_jours. Après expiration, Windows redémarre automatiquement toutes les heures, ce qui casse le service CCW-Watcher : recréer la VM avant (creer_vm_ccw.py --recreate). Si la date d'install réelle diffère, ajuster date_installation ci-dessus ; date_expiration est purement informative et recalculée par le script à partir de date_installation + eval_jours."
 }
