cd3840a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit cd3840a
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 19:47:38 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajout du projet relecture_bridge (§2)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 325bea0..51c3fed 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 78 (6 ligne(s)) dans l'ancienne version → ligne 78 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -78,6 +78,7 @@ Claude Chat → crée une issue → GitHub → watcher.py détecte → CCL exéc
 | `chesscoach` | AlainDelree/Chesscoach | ~/ChessCoach | (conf local) |
 | `gestionmail` | AlainDelree/GestionMail | ~/GestionMail | (conf local) |
 | `testccwprojet` | AlainDelree/Testccwprojet | ~/Testccwprojet | (conf local) |
+| `relecture_bridge` | AlainDelree/Relecture_Bridge | ~/Relecture_Bridge | (conf local) |
 
 Chaque projet a son propre watcher (`watcher.py --config configs/<nom>.conf`)
 et son propre journal de log (`logs/watcher-<nom>.log`).
# ── Zone modifiée : ligne 710 (6 ligne(s)) dans l'ancienne version → ligne 711 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -710,6 +711,7 @@ hors périmètre même si l'issue le demande explicitement :
 | `chesscoach` | /home/alain/ChessCoach |
 | `gestionmail` | /home/alain/GestionMail |
 | `testccwprojet` | /home/alain/Testccwprojet |
+| `relecture_bridge` | /home/alain/Relecture_Bridge |
 
 ---
 
# ── Zone modifiée : ligne 3487 (7 ligne(s)) dans l'ancienne version → ligne 3489 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3487,7 +3489,7 @@ de création d'issue, seul valable pour du contenu qu'il produit.
 
 ---
 
-*Dernière mise à jour : 17 septembre 2026 — Sous-section « Couleur d'accent
+*Dernière mise à jour : 18 septembre 2026 — Sous-section « Couleur d'accent
 des projets » (§12) complétée (issue #540) : procédure de recyclage de la
 couleur d'un projet mis à l'arrêt, appliquée à `ecole`/`ff_galerie`. Nouvelle
 constante partagée `COULEUR_PROJET_INACTIF` (`#767676`, contraste texte noir
