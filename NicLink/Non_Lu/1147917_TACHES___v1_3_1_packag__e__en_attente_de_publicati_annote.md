1147917

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1147917
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 18:11:34 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    TACHES : v1.3.1 packagée, en attente de publication

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 2857fa4..01f5f86 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 4 (7 ligne(s)) dans l'ancienne version → ligne 4 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,7 +4,7 @@
 
 ## ⚡ Prioritaire
 
-- **Release v1.3.1 à packager** `[Linux/Windows]` — regrouper les correctifs depuis v1.3.0 (dont issue #96) : `./make_release.sh 1.3.1` + tag + `gh release create`.
+- **ACTION ALAIN — Publier v1.3.1** `[Linux]` — `git push origin v1.3.1` puis `gh release create v1.3.1 dist/AlChess-v1.3.1-*.zip --title "AlChess v1.3.1" --notes "..."`.
 - **ACTION ALAIN — Valider installeur standalone** `[Windows]` — lancer `AlChess_Setup.exe` seul (sans ZIP), vérifier clone GitHub dans `%LOCALAPPDATA%\AlChess` et raccourci bureau fonctionnel.
 - **Tester une partie réelle Rodent sur Windows** `[Windows]` — sur portable physique (jeu + changement d'Elo + redémarrage).
 - **Tester vc_redist sur un Windows sans le runtime VC++** `[Windows]` — la VM actuelle a déjà le runtime, il faut un Windows propre.
