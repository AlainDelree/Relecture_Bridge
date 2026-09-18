100d768

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 100d768
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 20:03:25 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute deux entrées backlog watcher : capture stderr CCL et pre-flight token (issue #280)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3a8428b..e4f6986 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 295 (3 ligne(s)) dans l'ancienne version → ligne 295 (39 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -295,3 +295,39 @@ soin, pas seulement en confiance sur la consigne donnée à CCL.
 
 **Statut** : idée en attente, pas de développement lancé. Reçue via rapport
 d'audit Scrabble le 24/07/2026.
+
+---
+
+## Capture stderr CCL dans watcher.py
+
+**Contexte** : actuellement le stderr de CCL n'est pas capturé par
+`watcher.py`. Quand CCL échoue avant même de produire une réponse
+exploitable, le watcher journalise seulement "Erreur inconnue", ce qui
+masque la vraie cause (token expiré, coupure réseau, installation CCL
+cassée) et oblige à aller vérifier manuellement sur le terminal/la machine
+concernée.
+
+**Idée** : capturer (au moins) les premières lignes du stderr du process
+CCL et les afficher dans le log watcher (`logs/watcher-<nom>.log`) en cas
+d'échec, pour permettre un diagnostic immédiat sans accès terminal.
+
+**Statut** : idée en attente, pas de développement lancé. Identifiée lors
+de l'incident du 29/07/2026 (token CCL expiré → "Erreur inconnue" non
+diagnosticable, cf. issue #279).
+
+---
+
+## Vérification pre-flight de la validité du token CCL
+
+**Contexte** : lors du même incident du 29/07/2026, le watcher a enchaîné
+les 3 tentatives d'exécution (avec leurs timeouts respectifs) avant
+d'échouer, alors que le token CCL était expiré dès le départ — un
+diagnostic évitable en amont.
+
+**Idée** : avant de lancer une issue, vérifier que CCL est bien authentifié
+(ex. `claude -p "" 2>&1 | grep -i "not logged"`) et journaliser un
+avertissement explicite si le token est absent ou expiré, plutôt que
+d'attendre l'échec des 3 tentatives pour le découvrir.
+
+**Statut** : idée en attente, pas de développement lancé. Identifiée lors
+de l'incident du 29/07/2026 (cf. issue #279).
