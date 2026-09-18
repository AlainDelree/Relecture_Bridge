e9b06be

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e9b06be
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 16:51:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #475 : K_VARIABILITE=3, enregistrement de k_utilise dans historique_durees.json

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/watcher.py b/watcher.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d063e89..ad01156 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/watcher.py
# ── Version APRÈS ce commit.
+++ b/watcher.py
# ── Zone modifiée : ligne 95 (7 ligne(s)) dans l'ancienne version → ligne 95 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -95,7 +95,7 @@ FICHIER_HISTORIQUE = DOSSIER_LOGS / "historique_durees.json"
 FICHIER_ETAT_TIMEOUT   = DOSSIER_LOGS / "etat_timeout.json"
 FICHIER_ETAT_AMBIANCE  = DOSSIER_LOGS / "etat_ambiance.json"
 
-K_VARIABILITE               = 4     # constante de départ de la formule (à backtester plus tard)
+K_VARIABILITE               = 3     # issue #475 : backtest sur 1070 observations (96% couverture, -20% de gaspillage vs K=4)
 DEMI_VIE_ISSUES             = 15    # demi-vie de l'EWMA duree_typique/variabilite, EN NOMBRE D'ISSUES
 ALPHA_EWMA_ISSUES           = 1 - 0.5 ** (1 / DEMI_VIE_ISSUES)
 DEMI_VIE_AMBIANCE_HEURES    = 4.0   # demi-vie de l'EWMA F_reseau/F_local, TEMPORELLE (pas en nb d'issues)
# ── Zone modifiée : ligne 920 (6 ligne(s)) dans l'ancienne version → ligne 920 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -920,6 +920,7 @@ def enregistrer_duree(projet: str, type_issue: str, mode: str,
             "nb_fichiers_cibles": None,
             "nb_projets_actifs_au_lancement": nb_projets_actifs,
             "expiree": expiree,
+            "k_utilise": K_VARIABILITE,
         }
         tag_reseau = _detecter_tag_reseau(body)
         if tag_reseau is not None:
