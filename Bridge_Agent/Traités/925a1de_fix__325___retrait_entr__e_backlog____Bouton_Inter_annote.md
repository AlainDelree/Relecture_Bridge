925a1de

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 925a1de
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 15:39:20 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #325 : retrait entrée backlog « Bouton Interrompre dans l'onglet CCW » (implémentée par #323)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ad47de8..490fc76 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,16 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #325
+
+Retrait de `TACHES.md` de l'entrée backlog « Bouton Interrompre dans
+l'onglet CCW » (procédure manuelle nssm restart + suppression des
+`.lock`), désormais implémentée — et dépassée — par #323 (suite #320) :
+le bouton « ⛔ Interrompre cette issue » a été ajouté dans l'onglet
+Résultats, pas l'onglet CCW, et couvre CCL comme CCW. Même convention de
+retrait que #317 (retiré par #321) et les entrées PERIMETRE (#319) :
+suppression pure de la section obsolète, rien d'autre touché.
+
 ## 2 août 2026 — issue #324
 
 Ajout au backlog `TACHES.md` d'une entrée (pas d'implémentation) :
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index b570232..951a85c 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 5 (15 ligne(s)) dans l'ancienne version → ligne 5 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,15 +5,6 @@ Alain peut modifier ce fichier directement, sans passer par une issue.
 
 ---
 
-##Bouton Interrompre dans l'onglet CCW
-
-Procédure : nssm restart CCW-Watcher, puis supprimer le(s) fichier(s)
-  dans C:\CCW\Bridge_Agent\logs\verrous\ :
-  Get-ChildItem C:\CCW\Bridge_Agent\logs\verrous\ -Filter "*.lock"
-  Remove-Item C:\CCW\Bridge_Agent\logs\verrous\<fichier>.lock
-
----
-
 ## Projet dédié à la communication CCL ↔ CCW
 
 **Contexte** : aujourd'hui les issues Windows passent par le projet
