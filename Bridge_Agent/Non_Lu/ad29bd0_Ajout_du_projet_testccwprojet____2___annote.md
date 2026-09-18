ad29bd0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ad29bd0
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Thu Sep 17 17:52:53 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajout du projet testccwprojet (§2)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 73f7e8d..b3f6fca 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 77 (6 ligne(s)) dans l'ancienne version → ligne 77 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -77,6 +77,7 @@ Claude Chat → crée une issue → GitHub → watcher.py détecte → CCL exéc
 | `ApiSelect` | AlainDelree/ApiSelect | ~/ApiSelect | (conf local) |
 | `chesscoach` | AlainDelree/Chesscoach | ~/ChessCoach | (conf local) |
 | `gestionmail` | AlainDelree/GestionMail | ~/GestionMail | (conf local) |
+| `testccwprojet` | AlainDelree/Testccwprojet | ~/Testccwprojet | (conf local) |
 
 Chaque projet a son propre watcher (`watcher.py --config configs/<nom>.conf`)
 et son propre journal de log (`logs/watcher-<nom>.log`).
# ── Zone modifiée : ligne 689 (6 ligne(s)) dans l'ancienne version → ligne 690 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -689,6 +690,7 @@ hors périmètre même si l'issue le demande explicitement :
 | `ApiSelect` | /home/alain/ApiSelect |
 | `chesscoach` | /home/alain/ChessCoach |
 | `gestionmail` | /home/alain/GestionMail |
+| `testccwprojet` | /home/alain/Testccwprojet |
 
 ---
 
# ── Zone modifiée : ligne 3404 (7 ligne(s)) dans l'ancienne version → ligne 3406 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3404,7 +3406,7 @@ de création d'issue, seul valable pour du contenu qu'il produit.
 
 ---
 
-*Dernière mise à jour : 13 septembre 2026 — Sous-section « Couleur d'accent
+*Dernière mise à jour : 17 septembre 2026 — Sous-section « Couleur d'accent
 des projets » (§12) complétée (issue #540) : procédure de recyclage de la
 couleur d'un projet mis à l'arrêt, appliquée à `ecole`/`ff_galerie`. Nouvelle
 constante partagée `COULEUR_PROJET_INACTIF` (`#767676`, contraste texte noir
