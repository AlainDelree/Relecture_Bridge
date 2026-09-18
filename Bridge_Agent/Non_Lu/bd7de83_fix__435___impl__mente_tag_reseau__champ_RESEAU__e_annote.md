bd7de83

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bd7de83
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 14:30:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #435 : implémente tag_reseau (champ RESEAU) et corrige le fallback F_local de lire_timeout_suggere

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0ca8e36..78fc85f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 311 (6 ligne(s)) dans l'ancienne version → ligne 311 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -311,6 +311,7 @@ Le watcher lit ces champs dans le tableau markdown de l'en-tête :
 | `FICHIER_CONTEXTE` | ex. chemin relatif | Fichier additionnel fourni en contexte à CCL pour cette issue (modifiable via l'onglet Configuration, voir §12) |
 | `SUITE_DE` | ex. `#5` | Indique que cette issue fait suite à l'issue #N (discussion ou tâche complémentaire). Absent = issue inédite. |
 | `COMPLEXITE` | `rapide` / `court` / `normal` / `lourd` | 4e dimension de la clé EWMA de calibration TIMEOUT (issue #434, voir §19), estimée par Claude Chat au moment de rédiger l'issue. Absent ou valeur non reconnue = `normal` (défaut, ~300s). CCL/CCW doit l'inclure dans les issues chef/ouvrier qu'il crée (voir `consignes/globales.md`) ; pour les issues de Claude Chat, c'est géré côté doc/prompt. |
+| `RESEAU` | `oui` ou `non` | Tag réseau pour la calibration TIMEOUT (issue #220/#435, voir §19) : `oui` = issue impliquant de lourdes opérations réseau (téléchargements, builds avec fetch, etc.), `non` = issue purement locale. Lu par `_detecter_tag_reseau(body)`. Absent ou valeur non reconnue = `None` (F ignoré, facteur d'ambiance neutre). Optionnel (voir `consignes/globales.md`). |
 
 Format dans le corps :
 ```markdown
# ── Zone modifiée : ligne 2138 (20 ligne(s)) dans l'ancienne version → ligne 2139 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2138,20 +2139,6 @@ issues de la même combinaison s'il le juge utile.
 
 ### 19.6 Limitations connues, à traiter plus tard
 
-- **`tag_reseau` n'est peuplé nulle part actuellement** :
-  `_detecter_tag_reseau` retourne toujours `None` (aucun champ d'en-tête
-  bridge dédié n'existe aujourd'hui pour signaler qu'une issue s'est
-  déroulée dans des conditions réseau particulières). Conséquence : `F_reseau`
-  et `F_local` restent tous deux à leur valeur neutre (`F` planché à 1.0,
-  jamais mis à jour) tant qu'un futur champ d'en-tête dédié n'est pas créé et
-  que `_detecter_tag_reseau` n'est pas branché dessus.
-- **Incohérence inerte sur échec définitif** : `lire_timeout_suggere()`
-  retombe toujours sur `F_local` par défaut, sans lire le tag réel de
-  l'issue en échec — contrairement au cas succès (`maj_calibration_timeout`),
-  qui choisit `F_reseau`/`F_local` selon `_detecter_tag_reseau(body)`. Sans
-  effet tant que `tag_reseau` n'est jamais peuplé (point précédent), mais à
-  corriger le jour où il le sera (lire le tag de l'issue en échec plutôt que
-  de supposer `F_local`).
 - **Démarrage à froid trompeur** : la toute première observation réussie
   d'une combinaison (projet, `TYPE`, mode) donne `variabilite = 0` (pas
   d'écart mesurable sans historique préalable), donc un `TIMEOUT_suggéré`
# ── Zone modifiée : ligne 2184 (16 ligne(s)) dans l'ancienne version → ligne 2171 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2184,16 +2171,29 @@ issues de la même combinaison s'il le juge utile.
 - **#223** — exclusion des entrées `expiree=true` du calcul du badge
   d'estimation de durée de l'interface web (`estimer_duree`), pour ne pas
   fausser la médiane affichée à Alain avec des tentatives avortées.
+- **#435** — `_detecter_tag_reseau` implémenté : lecture du champ d'en-tête
+  `RESEAU` (`oui`/`non`, §6), calquée sur `extraire_complexite`. `F_reseau`/
+  `F_local` sont désormais réellement alimentés. `lire_timeout_suggere`
+  reçoit en plus un paramètre `body` pour choisir le bon `F` sur le chemin
+  échec définitif, au lieu de toujours retomber sur `F_local`.
 
 ---
 
 *Dernière mise à jour : 10 août 2026 — §6 « Champs spéciaux dans le corps
-de l'issue » : nouveau champ `COMPLEXITE` documenté (issue #434) — 4e
-dimension de la clé EWMA de calibration TIMEOUT (§19), quatre niveaux
-`rapide`/`court`/`normal`/`lourd`, défaut `normal` (~300s) si absent. §19.1
-et §19.3 mis à jour en conséquence : la clé `etat_timeout.json` passe de
-`projet|TYPE|mode` à `projet|TYPE|mode|complexite` — nouvelles clés
-distinctes, historique existant traité comme `normal`, aucune régression.
+de l'issue » : nouveau champ `RESEAU` documenté (issue #435, `oui`/`non`,
+lu par `_detecter_tag_reseau`, optionnel). §19.6 : les deux limitations
+« `tag_reseau` n'est peuplé nulle part » et « incohérence inerte sur échec
+définitif » sont levées — `_detecter_tag_reseau(body)` lit désormais le
+champ `RESEAU`, et `lire_timeout_suggere()` reçoit `body` pour choisir
+`F_reseau`/`F_local` selon le tag réel de l'issue en échec, au lieu de
+toujours retomber sur `F_local` (voir §19.7).
+Précédemment — §6 « Champs spéciaux dans le corps de l'issue » : nouveau
+champ `COMPLEXITE` documenté (issue #434) — 4e dimension de la clé EWMA de
+calibration TIMEOUT (§19), quatre niveaux `rapide`/`court`/`normal`/`lourd`,
+défaut `normal` (~300s) si absent. §19.1 et §19.3 mis à jour en conséquence :
+la clé `etat_timeout.json` passe de `projet|TYPE|mode` à
+`projet|TYPE|mode|complexite` — nouvelles clés distinctes, historique
+existant traité comme `normal`, aucune régression.
 Précédemment — §17 « Notifications centralisées » : nouvelle sous-section
 17.3 documentant le SSE de fin d'issue (issue #350) — `scripts/bip.py`
 renommé `scripts/traitement_fin.py` (clé de config `SCRIPT_BIP` inchangée,
# (diff du fichier suivant)
diff --git a/consignes/globales.md b/consignes/globales.md
# (index — ignorable)
index e596635..fab9e54 100644
# (avant — fichier suivant)
--- a/consignes/globales.md
# (après — fichier suivant)
+++ b/consignes/globales.md
# ── Zone modifiée : ligne 70 (3 ligne(s)) dans l'ancienne version → ligne 70 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -70,3 +70,11 @@
   projet/TYPE/mode/complexite) : sans lui, la valeur par défaut `normal` est
   utilisée. Cette consigne ne concerne QUE les issues que TU rédiges — les
   issues rédigées par Claude Chat suivent leurs propres instructions.
+- **Champ RESEAU (optionnel) dans les issues que tu crées toi-même
+  (chef/ouvrier) :** si la tâche confiée implique de lourdes opérations
+  réseau (téléchargements, builds avec fetch de dépendances, etc.), inclus
+  `| RESEAU | oui |` dans l'en-tête ; si elle est purement locale, `| RESEAU
+  | non |`. Ce champ alimente le facteur d'ambiance F de la calibration
+  automatique du TIMEOUT (`F_reseau`/`F_local`) — absent, il n'a aucun
+  effet. Comme pour COMPLEXITE, cette consigne ne concerne que les issues
+  que TU rédiges.
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 06130d1..d063e89 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 868 (15 ligne(s)) dans l'ancienne version → ligne 868 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -868,15 +868,21 @@ def _compter_etapes_checklist(body: str) -> int | None:
 
 
 def _detecter_tag_reseau(body: str) -> bool | None:
-    """Déduit tag_reseau depuis un marqueur explicite de l'en-tête (issue #220).
-
-    Aucun champ de ce type n'existe aujourd'hui dans le format d'en-tête bridge
-    (§6 du DOC : SOURCE/DEST/RETOUR/MODE/PRIORITE/TIMEOUT/PROJET/TYPE/MODELE/
-    FICHIER_CONTEXTE/SUITE_DE — pas de champ réseau). On ne fabrique donc PAS de
-    détection ici (pas de mot-clé deviné dans le corps) : ceci renvoie toujours
-    None pour l'instant, en attendant qu'un futur champ d'en-tête dédié soit
-    ajouté par Claude Chat à la rédaction des issues. enregistrer_duree omet la
-    clé tag_reseau de l'entrée tant que cette fonction renvoie None."""
+    """Extrait tag_reseau depuis le champ d'en-tête RESEAU (issue #220, implémenté
+    #435) — « | RESEAU | oui | » / « | RESEAU | non | », calqué sur
+    extraire_complexite. Insensible à la casse. 'oui' → True, 'non' → False,
+    champ absent ou valeur non reconnue → None (aucun mot-clé deviné dans le
+    corps). enregistrer_duree omet la clé tag_reseau de l'entrée tant que
+    cette fonction renvoie None."""
+    for ligne in (body or "").splitlines():
+        if "| RESEAU" in ligne.upper():
+            parts = ligne.split("|")
+            if len(parts) >= 3:
+                valeur = parts[2].strip().lower()
+                if valeur == "oui":
+                    return True
+                if valeur == "non":
+                    return False
     return None
 
 
# ── Zone modifiée : ligne 1190 (7 ligne(s)) dans l'ancienne version → ligne 1196 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1190,7 +1196,8 @@ def maj_calibration_timeout(*, projet: str, type_issue: str, mode: str,
     return suggere
 
 
-def lire_timeout_suggere(projet: str, type_issue: str, mode: str, complexite: str = "normal") -> float | None:
+def lire_timeout_suggere(projet: str, type_issue: str, mode: str, complexite: str = "normal",
+                         body: str = "") -> float | None:
     """Lit (sans écrire ni verrouiller) le TIMEOUT_suggéré actuellement en
     vigueur pour la combinaison (projet, TYPE, mode, complexite — issue
     #434), à partir de l'état déjà persisté par maj_calibration_timeout
# ── Zone modifiée : ligne 1203 (7 ligne(s)) dans l'ancienne version → ligne 1210 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1203,7 +1210,11 @@ def lire_timeout_suggere(projet: str, type_issue: str, mode: str, complexite: st
     fois la même observation. Une simple lecture de l'état déjà à jour suffit.
     Best-effort : retourne None si l'état est illisible ou si aucun succès n'a
     encore été enregistré pour cette combinaison (mêmes conditions que
-    maj_calibration_timeout)."""
+    maj_calibration_timeout).
+
+    body (issue #435) : corps de l'issue échouée, pour lire le tag_reseau via
+    _detecter_tag_reseau — même logique que maj_calibration_timeout. Absent
+    (chaîne vide) ou tag non trouvé → repli sur F_local, comme avant."""
     try:
         cle = _cle_combinaison(projet, type_issue, mode, complexite)
         combo = _lire_json_best_effort(FICHIER_ETAT_TIMEOUT).get(cle)
# ── Zone modifiée : ligne 1215 (10 ligne(s)) dans l'ancienne version → ligne 1226 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1215,10 +1226,12 @@ def lire_timeout_suggere(projet: str, type_issue: str, mode: str, complexite: st
         variabilite = combo.get("variabilite") or 0.0
         backoff = combo.get("multiplicateur_backoff", 1.0)
 
-        # F_local par défaut (hypothèse la moins généreuse) : cette lecture
-        # est hors contexte d'une issue précise, donc sans tag_reseau connu —
-        # même choix par défaut que maj_calibration_timeout en l'absence de tag.
-        f_brut = (_lire_json_best_effort(FICHIER_ETAT_AMBIANCE).get("F_local") or {}).get("valeur_ewma")
+        # F_reseau si le tag RESEAU de cette issue est explicitement connu et
+        # positif, F_local sinon (hypothèse la moins généreuse par défaut) —
+        # même choix que maj_calibration_timeout.
+        tag_reseau = _detecter_tag_reseau(body)
+        cle_f = "F_reseau" if tag_reseau else "F_local"
+        f_brut = (_lire_json_best_effort(FICHIER_ETAT_AMBIANCE).get(cle_f) or {}).get("valeur_ewma")
         f_pertinent = max(1.0, f_brut) if f_brut is not None else 1.0
 
         return max((duree_typique + K_VARIABILITE * variabilite) * f_pertinent * backoff,
# ── Zone modifiée : ligne 3333 (7 ligne(s)) dans l'ancienne version → ligne 3346 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3333,7 +3346,7 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                     mode_echec        = _etiquette_calibration(mode)
                     complexite_echec  = extraire_complexite(body)
                     duree_echec       = time.monotonic() - debut_traitement
-                    suggere_echec     = lire_timeout_suggere(CFG.nom, type_issue_echec, mode_echec, complexite_echec)
+                    suggere_echec     = lire_timeout_suggere(CFG.nom, type_issue_echec, mode_echec, complexite_echec, body)
                     message_echec += formater_bloc_calibration(duree_echec, timeout, suggere_echec)
                     commenter_issue(numero, message_echec)
                     ajouter_label(numero, LABEL_ECHEC)
