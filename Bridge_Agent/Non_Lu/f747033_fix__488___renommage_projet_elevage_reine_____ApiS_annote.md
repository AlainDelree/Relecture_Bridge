f747033

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f747033
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 22:05:13 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #488 : renommage projet elevage_reine → ApiSelect (§2 + §7 du DOC)
    
    - BRIDGE_AGENT_DOC.md §2 (Projets actifs) et §7 (Périmètre par projet) :
      remplacement de la ligne elevage_reine par ApiSelect
      (AlainDelree/ApiSelect, ~/ApiSelect)
    - Suppression locale de configs/elevage_reine.conf (fichier gitignoré,
      pas de diff git associé)
    - configs/ApiSelect.conf non créé : à faire par Alain une fois le dossier
      de travail et le dépôt GitHub renommés (garde-fou §11)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d54dd04..2f47a5e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 74 (7 ligne(s)) dans l'ancienne version → ligne 74 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -74,7 +74,7 @@ Claude Chat → crée une issue → GitHub → watcher.py détecte → CCL exéc
 | `actualise` | AlainDelree/Actualise | ~/Actualise | (conf local) |
 | `bloc_score` | AlainDelree/Bloc_score | ~/Bloc_score | (conf local) |
 | `rummikub` | AlainDelree/Rummikub | ~/Rummikub | (conf local) |
-| `elevage_reine` | AlainDelree/Elevage_reine | ~/Elevage_reine | (conf local) |
+| `ApiSelect` | AlainDelree/ApiSelect | ~/ApiSelect | (conf local) |
 
 Chaque projet a son propre watcher (`watcher.py --config configs/<nom>.conf`)
 et son propre journal de log (`logs/watcher-<nom>.log`).
# ── Zone modifiée : ligne 357 (7 ligne(s)) dans l'ancienne version → ligne 357 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -357,7 +357,7 @@ hors périmètre même si l'issue le demande explicitement :
 | `actualise` | /home/alain/Actualise |
 | `bloc_score` | /home/alain/Bloc_score |
 | `rummikub` | /home/alain/Rummikub |
-| `elevage_reine` | /home/alain/Elevage_reine |
+| `ApiSelect` | /home/alain/ApiSelect |
 
 ---
 
