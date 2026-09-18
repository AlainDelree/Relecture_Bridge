e61e0b5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e61e0b5
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 18:57:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    TACHES : post-v1.3.1 — nettoyer items résolus, ajouter SmartScreen README

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 01f5f86..e68a636 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 4 (8 ligne(s)) dans l'ancienne version → ligne 4 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,8 +4,7 @@
 
 ## ⚡ Prioritaire
 
-- **ACTION ALAIN — Publier v1.3.1** `[Linux]` — `git push origin v1.3.1` puis `gh release create v1.3.1 dist/AlChess-v1.3.1-*.zip --title "AlChess v1.3.1" --notes "..."`.
-- **ACTION ALAIN — Valider installeur standalone** `[Windows]` — lancer `AlChess_Setup.exe` seul (sans ZIP), vérifier clone GitHub dans `%LOCALAPPDATA%\AlChess` et raccourci bureau fonctionnel.
+- **README — documenter SmartScreen** `[Windows]` — ajouter section "Premier lancement Windows" : cliquer "More info" puis "Run anyway" sur l'alerte SmartScreen au premier lancement de `AlChess_Setup.exe`.
 - **Tester une partie réelle Rodent sur Windows** `[Windows]` — sur portable physique (jeu + changement d'Elo + redémarrage).
 - **Tester vc_redist sur un Windows sans le runtime VC++** `[Windows]` — la VM actuelle a déjà le runtime, il faut un Windows propre.
 
