6e58ee0

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6e58ee0
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 20:22:29 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Documente la règle 'niveau de détail des issues' au §11 (issue #281)
    
    Claude Chat décrit le problème/la cause/l'intention du fix sans rédiger
    le code complet (blocs Avant/Après) ; CCL lit les sources et implémente.
    Exception tolérée : snippet de 1-2 lignes si non-trivial. Footer de
    BRIDGE_AGENT_DOC.md glissé (#281, #279, #268), CHANGELOG.md complété.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6dbddbb..d7e7407 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 437 (6 ligne(s)) dans l'ancienne version → ligne 437 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -437,6 +437,17 @@ la même opération, en plus du point ci-dessus :
   généralisée ici. `autounattend.xml` n'est **pas** concerné (lu par le parseur
   XML de l'installateur Windows, pas par PowerShell).
 - **Dogfooding** : Bridge_Agent se développe lui-même via ses propres issues.
+- **Niveau de détail des issues (issue #281)** : Claude Chat décrit le
+  problème, la cause et l'intention du fix. Il ne rédige pas le code complet
+  (blocs Avant/Après, implémentations entières) : CCL lit les fichiers
+  source et fait l'implémentation lui-même. **Exception tolérée** : un
+  snippet de 1-2 lignes si la syntaxe est non-triviale ou si l'intention
+  serait ambiguë sans exemple.
+  - *Mauvais exemple* : fournir les trois méthodes complètes Avant/Après
+    pour un fix pywebview de navigation différée.
+  - *Bon exemple* : « Dans `api.py`, pour les trois méthodes de navigation,
+    différer l'appel dans un thread daemon avec `time.sleep(0.05)` avant
+    de naviguer. »
 
 ---
 
# ── Zone modifiée : ligne 1836 (6 ligne(s)) dans l'ancienne version → ligne 1847 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1836,6 +1847,6 @@ issues de la même combinaison s'il le juge utile.
 
 ---
 
-*Dernière mise à jour : 30 juillet 2026 — Documente dans §13 le diagnostic du symptôme « Erreur inconnue » observé la nuit du 29/07/2026 (issue #279) : plusieurs issues échouaient en ~1,2 s, 3 tentatives et passe diagnostique comprises, un message générique masquant totalement la cause réelle. Nouveau bloc **« Diagnostic — CCL ne démarre pas »** en fin de §13 : symptôme (échec quasi immédiat sur toutes les issues → cause systémique, pas liée à une tâche précise) ; première vérification (`claude -p "test" 2>&1` — une réponse « Not logged in » signe un **token de session CCL expiré**) ; résolution (`claude` en interactif puis `/login`) ; autres causes possibles (réseau/DNS indisponible, installation `claude` corrompue) ; et le critère qui les distingue — un token expiré échoue en **moins de 2 s**, un problème réseau échoue **proche du TIMEOUT** configuré (l'appel reste bloqué en attente d'une réponse qui ne vient jamais). Aucun fichier `.py` modifié, aucune section renumérotée. Précédemment — Corrige la corruption du §10 provoquée par #263 (issue #268) : le remplacement automatique de la date du pied de page s'appliquait par erreur sur le modèle d'exemple du §10 (première occurrence du texte recherché dans le fichier) au lieu du vrai pied de page en fin de fichier. §10 restauré au mot près, pied de page reconstruit (#263, #257 puis #268), garde-fou ajouté au §10 pointant vers ce risque (toujours viser la fin du fichier, jamais la première occurrence). Précédemment — Mesure et attribution de la consommation du quota GraphQL GitHub (issue #263, suite à l'épuisement complet du 28/07 vers 3h — 5000/5000, `remaining: 0`) — aucun correctif, mesure seule. Ajout de `scripts/mesurer_api.py` (échantillonnage `gh api rate_limit`, gratuit) ; coûts unitaires mesurés par appel `gh` ; cause principale identifiée : **l'interface web laissée ouverte dans un navigateur** (`/issues-en-attente/<projet>` interrogé toutes les ~15s pour chaque projet, ≈3840 points/heure), avant même les watchers ou le poller de notifications. Détail complet : commentaire de clôture de l'issue #263.*
+*Dernière mise à jour : 30 juillet 2026 — Ajoute au §11 « Conventions de code » le paragraphe **« Niveau de détail des issues »** (issue #281) : Claude Chat décrit le problème, la cause et l'intention du fix, sans rédiger le code complet (blocs Avant/Après, implémentations entières) — CCL lit les fichiers source et fait l'implémentation lui-même ; exception tolérée pour un snippet de 1-2 lignes si la syntaxe est non-triviale ou l'intention ambiguë sans exemple. Mauvais exemple donné : les trois méthodes complètes Avant/Après d'un fix pywebview de navigation différée ; bon exemple : décrire l'intention (« différer l'appel dans un thread daemon avec `time.sleep(0.05)` avant de naviguer »). Aucun fichier `.py` modifié, aucune section renumérotée. Précédemment — Documente dans §13 le diagnostic du symptôme « Erreur inconnue » observé la nuit du 29/07/2026 (issue #279) : plusieurs issues échouaient en ~1,2 s, 3 tentatives et passe diagnostique comprises, un message générique masquant totalement la cause réelle. Nouveau bloc « Diagnostic — CCL ne démarre pas » en fin de §13 : symptôme (échec quasi immédiat sur toutes les issues → cause systémique, pas liée à une tâche précise) ; première vérification (`claude -p "test" 2>&1` — une réponse « Not logged in » signe un token de session CCL expiré) ; résolution (`claude` en interactif puis `/login`) ; autres causes possibles (réseau/DNS indisponible, installation `claude` corrompue) ; et le critère qui les distingue — un token expiré échoue en moins de 2 s, un problème réseau échoue proche du TIMEOUT configuré. Précédemment — Corrige la corruption du §10 provoquée par #263 (issue #268) : le remplacement automatique de la date du pied de page s'appliquait par erreur sur le modèle d'exemple du §10 (première occurrence du texte recherché dans le fichier) au lieu du vrai pied de page en fin de fichier. §10 restauré au mot près, pied de page reconstruit (#263, #257 puis #268), garde-fou ajouté au §10 pointant vers ce risque (toujours viser la fin du fichier, jamais la première occurrence).*
 
 Historique complet : voir [`CHANGELOG.md`](CHANGELOG.md).
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index f45d18e..d0d3ce8 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,10 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 30 juillet 2026 — issue #281
+
+Ajoute au §11 « Conventions de code » de `BRIDGE_AGENT_DOC.md` le paragraphe **« Niveau de détail des issues »** (issue #281), en réponse à une tendance observée chez Claude Chat à rédiger du code complet dans le corps des issues (blocs Avant/Après, implémentations entières) alors que CCL est capable de lire les fichiers source et d'implémenter lui-même à partir d'une description claire. La règle posée : Claude Chat décrit le problème, la cause et l'intention du fix, sans rédiger le code complet — CCL fait l'implémentation. **Exception tolérée** : un snippet de 1-2 lignes si la syntaxe est non-triviale ou si l'intention serait ambiguë sans exemple. **Mauvais exemple** donné : fournir les trois méthodes complètes Avant/Après pour un fix pywebview de navigation différée. **Bon exemple** : « Dans `api.py`, pour les trois méthodes de navigation, différer l'appel dans un thread daemon avec `time.sleep(0.05)` avant de naviguer. » Pied de page de `BRIDGE_AGENT_DOC.md` glissé (issue #281 en tête, #279 et #268 conservées comme les deux entrées les plus récentes parmi les issues modifiant cette doc, #263 sorti). Aucun fichier `.py` modifié, aucune section renumérotée.
+
 ## 30 juillet 2026 — issue #279
 
 Documente dans §13 de `BRIDGE_AGENT_DOC.md` le diagnostic du symptôme « Erreur inconnue » observé la nuit du 29/07/2026 (issue #279) : plusieurs issues avaient échoué en ~1,2 s, 3 tentatives et passe diagnostique comprises, le message générique masquant totalement la cause réelle — une session CCL expirée. Nouveau bloc **« Diagnostic — CCL ne démarre pas »** ajouté en fin de §13 (après le paragraphe sur les services systemd abandonnés) : **symptôme** (échec quasi immédiat sur toutes les issues → cause systémique, pas liée au contenu d'une tâche précise) ; **première vérification** (`claude -p "test" 2>&1` — une réponse « Not logged in » signe un token de session CCL expiré) ; **résolution** (lancer `claude` en session interactive, puis taper `/login`) ; **autres causes possibles** (réseau indisponible/DNS, installation `claude` corrompue) ; et le **critère de distinction** entre ces causes par le temps d'échec — un token expiré échoue en moins de 2 secondes (observé le 29/07/2026), un problème réseau échoue en général bien plus tard, proche du `TIMEOUT` configuré dans l'en-tête de l'issue (l'appel reste bloqué à attendre une réponse qui ne vient jamais). Pied de page de `BRIDGE_AGENT_DOC.md` glissé (issue #279 en tête, #268 et #263 conservées comme les deux entrées les plus récentes parmi les issues modifiant cette doc, #257 sorti). Aucun fichier `.py` modifié, aucune section renumérotée.
