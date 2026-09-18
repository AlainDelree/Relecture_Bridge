5b255fc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5b255fc
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 12:49:08 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #453 : suppression note obsolete configurer_ssh_ccw.ps1 dans REINSTALLATION_CCW.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/provisioning/windows/REINSTALLATION_CCW.md b/provisioning/windows/REINSTALLATION_CCW.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 298a54e..03f78cc 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/provisioning/windows/REINSTALLATION_CCW.md
# ── Version APRÈS ce commit.
+++ b/provisioning/windows/REINSTALLATION_CCW.md
# ── Zone modifiée : ligne 86 (9 ligne(s)) dans l'ancienne version → ligne 86 (3 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -86,9 +86,3 @@ Confirmer que `CCW-Watcher` est bien à l'état `running`, soit localement
 (`nssm status CCW-Watcher` ou services.msc sur le PC fixe), soit depuis
 CCL via l'onglet **CCW** de l'interface web (`new_issue.py`) — voir
 `BRIDGE_AGENT_DOC.md` §16.2.
-
----
-
-> **Note.** `configurer_ssh_ccw.ps1` est référencé par cette procédure mais
-> n'existe pas encore dans ce dossier au moment de la rédaction — à créer
-> séparément avant de pouvoir dérouler l'étape 2 telle quelle.
