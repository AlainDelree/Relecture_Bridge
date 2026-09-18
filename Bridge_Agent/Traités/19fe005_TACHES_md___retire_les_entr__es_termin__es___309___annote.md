19fe005

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 19fe005
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 2 10:30:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    TACHES.md : retire les entrées terminées (#309, #310) — issue #312
    
    Suppression des trois entrées de backlog désormais implémentées :
    « Capture stderr CCL » + « Vérification pre-flight du token » (issue
    #309, commit bcd3a11) et « Archivage de historique_durees.json »
    (issue #310, commit 6df2f44). Reste du fichier inchangé. CHANGELOG.md
    mis à jour.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 60ed7fb..46c991d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,18 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 2 août 2026 — issue #312
+
+`TACHES.md` : retrait des trois entrées de backlog désormais
+implémentées — « Capture stderr CCL dans watcher.py » et « Vérification
+pre-flight de la validité du token CCL » (issue #309, commit bcd3a11)
+et « Archivage de logs/historique_durees.json » (issue #310, commit
+6df2f44). Suppression simple, sans section « Terminé » : c'est déjà la
+convention établie pour ce fichier (cf. commit dcecb85). Reste du
+fichier inchangé, notamment « Garde-fou technique sur la modification
+de PERIMETRE » (#298) et « Concurrence limitée aux issues mode_lecture »,
+toujours en attente sans implémentation.
+
 ## 2 août 2026 — issue #310
 
 Nouveau script `scripts/archiver_historique.py`, lancement manuel
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index b135f48..b761c8e 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 80 (32 ligne(s)) dans l'ancienne version → ligne 80 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -80,32 +80,6 @@ modélisation qu'on prendrait mal à la légère.
 
 ---
 
-## Archivage de logs/historique_durees.json
-
-**Contexte** : le fichier accumule depuis mai sans jamais être purgé —
-682 entrées, 112 Ko au 29/07/2026 — et il est relu puis réécrit à chaque
-clôture d'issue. Répartition : scrabble 284, bridge_agent 237, alchess 58,
-rummikub 24, actualise 22, bloc_score 21, ecole 18, ff_galerie 13,
-diagnostique_programme 5. Les entrées `ff_galerie` datent de mai et ne
-correspondent pas à un usage réel du bridge (projet piloté par EmailJS) ;
-elles ne polluent aucun calcul — la calibration filtre par combinaison —
-mais brouillent la lecture manuelle.
-
-**Idée** : archiver les vieilles entrées pour contenir la taille du
-fichier et rendre son contenu lisible.
-
-**Point à concevoir avant implémentation, impératif** : ne PAS archiver
-naïvement par mois. L'EWMA de la calibration a une demi-vie de 15 issues ;
-une bascule mensuelle ferait repartir le calcul de zéro à chaque nouveau
-mois, précisément pour les projets les plus actifs. Il faut soit archiver
-sans rendre les entrées invisibles au calcul, soit assumer explicitement
-la remise à zéro.
-
-**Statut** : aucune urgence à 112 Ko. À traiter avant que le fichier
-n'atteigne plusieurs Mo. Lié à l'entrée sur la calibration ci-dessus.
-
----
-
 ## Concurrence limitée aux issues mode_lecture
 
 **Contexte** : `watcher.py` est aujourd'hui strictement séquentiel (une issue à
# ── Zone modifiée : ligne 213 (42 ligne(s)) dans l'ancienne version → ligne 187 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -213,42 +187,6 @@ d'audit Scrabble le 24/07/2026.
 
 ---
 
-## Capture stderr CCL dans watcher.py
-
-**Contexte** : actuellement le stderr de CCL n'est pas capturé par
-`watcher.py`. Quand CCL échoue avant même de produire une réponse
-exploitable, le watcher journalise seulement "Erreur inconnue", ce qui
-masque la vraie cause (token expiré, coupure réseau, installation CCL
-cassée) et oblige à aller vérifier manuellement sur le terminal/la machine
-concernée.
-
-**Idée** : capturer (au moins) les premières lignes du stderr du process
-CCL et les afficher dans le log watcher (`logs/watcher-<nom>.log`) en cas
-d'échec, pour permettre un diagnostic immédiat sans accès terminal.
-
-**Statut** : idée en attente, pas de développement lancé. Identifiée lors
-de l'incident du 29/07/2026 (token CCL expiré → "Erreur inconnue" non
-diagnosticable, cf. issue #279).
-
----
-
-## Vérification pre-flight de la validité du token CCL
-
-**Contexte** : lors du même incident du 29/07/2026, le watcher a enchaîné
-les 3 tentatives d'exécution (avec leurs timeouts respectifs) avant
-d'échouer, alors que le token CCL était expiré dès le départ — un
-diagnostic évitable en amont.
-
-**Idée** : avant de lancer une issue, vérifier que CCL est bien authentifié
-(ex. `claude -p "" 2>&1 | grep -i "not logged"`) et journaliser un
-avertissement explicite si le token est absent ou expiré, plutôt que
-d'attendre l'échec des 3 tentatives pour le découvrir.
-
-**Statut** : idée en attente, pas de développement lancé. Identifiée lors
-de l'incident du 29/07/2026 (cf. issue #279).
-
----
-
 ## Garde-fou technique sur la modification de PERIMETRE
 
 **Contexte** : PERIMETRE (`configs/*.conf`, ex. `ccw.conf`) est un simple
