d9ae2a3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d9ae2a3
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 08:04:37 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Fiabilise la publication du commentaire de résultat (issue #237)
    
    - commenter_issue / editer_dernier_commentaire : --body <message> remplacé
      par --body-file <tmp UTF-8> (supprime la limite argv Windows 32767 et les
      problèmes d'échappement, cause probable du commentaire silencieusement
      absent sur l'issue #236 malgré un exit code 0 de gh).
    - commenter_resultat_avec_retry : vérification post-publication — après
      chaque tentative rendant 0, relit l'issue et exige la présence effective
      du commentaire (marqueur MARQUEUR_RESULTAT) avant de retourner True ; sinon
      traite comme un échec et enchaîne sur la tentative suivante.
    - resultat_deja_poste : repère désormais le commentaire de résultat par
      MARQUEUR_RESULTAT (ligne HTML invisible en tête du message) au lieu de la
      sous-chaîne "## Résultat", qui matchait aussi "## Résultat attendu" (titre
      de section quasi omniprésent) — faux positif latent distinct de #236.
    - Ajoute tests/test_verification_commentaire_237.py : reproduit "gh rend 0
      mais aucun commentaire n'existe" en isolation et bout-en-bout via
      traiter_issue, vérifie que l'issue n'est pas fermée dans ce cas.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/test_verification_commentaire_237.py b/tests/test_verification_commentaire_237.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..31f5b76
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/tests/test_verification_commentaire_237.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (157 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,157 @@
+#!/usr/bin/env python3
+"""Test de non-régression — issue #237.
+
+Reproduit l'incident de l'issue #236 : `gh issue comment` rend le code de
+retour 0 alors qu'AUCUN commentaire n'a réellement été créé (troncature
+silencieuse côté `gh`, notamment via le plafond argv Windows). Avant #237,
+`commenter_resultat_avec_retry` faisait confiance au seul code de retour et
+`fermer_issue` était appelée juste après — effaçant silencieusement le
+travail. Ce test vérifie que la VÉRIFICATION post-publication (relecture de
+l'issue, présence du marqueur `MARQUEUR_RESULTAT`) empêche ce scénario : si
+`gh` rend 0 mais que la relecture ne trouve aucun commentaire correspondant,
+la tentative est traitée comme un échec, toutes les tentatives échouent (le
+mock ne pose jamais le commentaire) et l'issue N'EST PAS fermée.
+
+Exécution :  python3 tests/test_verification_commentaire_237.py
+Sortie      :  code 0 si tous les scénarios passent, 1 sinon.
+"""
+
+import sys
+from pathlib import Path
+from unittest import mock
+
+RACINE = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(RACINE))
+
+import watcher  # noqa: E402
+
+
+def scenario_1_gh_rend_0_sans_commentaire_reel():
+    """`gh issue comment` rend 0 à chaque tentative, mais la relecture de
+    l'issue ne trouve jamais le marqueur (comme si le commentaire n'avait
+    jamais été créé, cf. #236). commenter_resultat_avec_retry doit épuiser
+    toutes ses tentatives et retourner False — jamais True sur la seule foi
+    du code de retour."""
+    appels_comment = {"n": 0}
+
+    def fake_run(cmd, **kwargs):
+        res = mock.Mock()
+        if "comment" in cmd:
+            appels_comment["n"] += 1
+            res.returncode = 0  # gh ment : rend 0 sans rien poster
+            res.stdout = ""
+            res.stderr = ""
+        elif "view" in cmd:
+            res.returncode = 0
+            res.stdout = '{"comments": []}'  # jamais retrouvé à la relecture
+            res.stderr = ""
+        else:
+            raise AssertionError(f"commande inattendue : {cmd}")
+        return res
+
+    with mock.patch.object(watcher, "CFG", mock.Mock(depot="exemple/depot-test")), \
+         mock.patch.object(watcher.subprocess, "run", fake_run), \
+         mock.patch.object(watcher.time, "sleep", lambda _: None):
+        resultat = watcher.commenter_resultat_avec_retry(
+            999, f"{watcher.MARQUEUR_RESULTAT}\n## Résultat\n\nOK"
+        )
+
+    assert resultat is False, (
+        "commenter_resultat_avec_retry a retourné True alors qu'aucun "
+        "commentaire n'a jamais été confirmé présent — régression #236."
+    )
+    # 1 tentative initiale + 3 retries (DELAIS_RETRY_RESULTAT) = 4.
+    assert appels_comment["n"] == 1 + len(watcher.DELAIS_RETRY_RESULTAT), (
+        f"Nombre de tentatives inattendu : {appels_comment['n']}"
+    )
+    return {"appels_comment": appels_comment["n"]}
+
+
+def scenario_2_traiter_issue_ne_ferme_pas_si_verification_echoue():
+    """Bout-en-bout via traiter_issue (comme #236 l'a vécu) : lancer_claude
+    réussit, mais le commentaire de résultat n'est jamais confirmé présent à
+    la relecture. L'issue ne doit PAS être fermée (ni `gh issue close`, ni
+    label `done`) : elle reste ouverte pour reprise au prochain cycle."""
+    appels = {"close": 0, "edit_done": 0}
+
+    def fake_run(cmd, **kwargs):
+        res = mock.Mock()
+        if "comment" in cmd:
+            res.returncode = 0
+            res.stdout = ""
+            res.stderr = ""
+        elif "view" in cmd:
+            res.returncode = 0
+            res.stdout = '{"comments": []}'
+            res.stderr = ""
+        elif "close" in cmd:
+            appels["close"] += 1
+            res.returncode = 0
+            res.stdout = ""
+            res.stderr = ""
+        elif "edit" in cmd:
+            if watcher.LABEL_FAIT in cmd:
+                appels["edit_done"] += 1
+            res.returncode = 0
+            res.stdout = ""
+            res.stderr = ""
+        else:
+            raise AssertionError(f"commande inattendue : {cmd}")
+        return res
+
+    issue = {"number": 236, "title": "issue de test", "body": "", "labels": []}
+
+    with mock.patch.object(watcher, "CFG", mock.Mock(
+                depot="exemple/depot-test", nom="test_237",
+                max_essais=1, perimetre="/tmp", rep_travail=Path("/tmp"),
+                perimetre_dynamique=False)), \
+         mock.patch.object(watcher.subprocess, "run", fake_run), \
+         mock.patch.object(watcher.time, "sleep", lambda _: None), \
+         mock.patch.object(watcher, "lancer_claude",
+                            lambda *a, **k: (True, "sortie de build")), \
+         mock.patch.object(watcher, "acquerir_verrou", lambda *a, **k: Path("/tmp/verrou-test-237")), \
+         mock.patch.object(watcher, "liberer_verrou", lambda *a, **k: None), \
+         mock.patch.object(watcher, "notifier", lambda *a, **k: None), \
+         mock.patch.object(watcher, "enregistrer_duree", lambda *a, **k: None), \
+         mock.patch.object(watcher, "maj_calibration_timeout", lambda *a, **k: None):
+        watcher.traiter_issue(issue, dry_run=False)
+
+    assert appels["close"] == 0, (
+        "L'issue a été fermée (`gh issue close`) alors que le commentaire de "
+        "résultat n'a jamais été confirmé présent — régression #236."
+    )
+    assert appels["edit_done"] == 0, (
+        "Le label 'done' a été posé alors que le commentaire de résultat n'a "
+        "jamais été confirmé présent — régression #236."
+    )
+    return appels
+
+
+def main():
+    tests = [
+        ("gh rend 0 sans commentaire réel → échec après épuisement des tentatives",
+         scenario_1_gh_rend_0_sans_commentaire_reel),
+        ("traiter_issue ne ferme pas l'issue si la vérification échoue",
+         scenario_2_traiter_issue_ne_ferme_pas_si_verification_echoue),
+    ]
+    echecs = 0
+    for nom, fn in tests:
+        try:
+            rap = fn()
+            print(f"  ✓ {nom}  ({rap})")
+        except AssertionError as e:
+            echecs += 1
+            print(f"  ✗ {nom}\n      {e}")
+        except Exception as e:  # noqa: BLE001
+            echecs += 1
+            print(f"  ✗ {nom} — erreur inattendue : {type(e).__name__}: {e}")
+
+    if echecs:
+        print(f"\n❌ {echecs} scénario(s) en échec.")
+        return 1
+    print("\n✅ Tous les scénarios passent.")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 3d1d947..2de32a7 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 24 (6 ligne(s)) dans l'ancienne version → ligne 24 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -24,6 +24,7 @@ import os
 import glob
 import re
 import hashlib
+import tempfile
 from logging.handlers import RotatingFileHandler
 from dataclasses import dataclass, field
 from pathlib import Path
# ── Zone modifiée : ligne 147 (6 ligne(s)) dans l'ancienne version → ligne 148 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -147,6 +148,14 @@ PAUSE_ENTRE_TENTATIVES = 5
 # 1 tentative initiale + 3 tentatives espacées de 5, 10 puis 20 s.
 DELAIS_RETRY_RESULTAT = (5, 10, 20)
 
+# Marqueur non ambigu identifiant un commentaire de RÉSULTAT posté par le
+# watcher (issue #237). Ligne HTML invisible sur GitHub, placée en tête du
+# commentaire. Remplace le repérage par sous-chaîne "## Résultat", qui matchait
+# aussi "## Résultat attendu" (titre de section présent dans quasi toutes les
+# issues) — un faux positif aurait fermé une issue sans rien traiter si ce
+# texte apparaissait un jour dans un commentaire.
+MARQUEUR_RESULTAT = "<!-- bridge:resultat -->"
+
 # Abréviations du dictionnaire bridge
 SOURCES = {"CC": "Claude Chat", "CCL": "Claude Code Linux", "CCW": "Claude Code Windows"}
 
# ── Zone modifiée : ligne 1256 (12 ligne(s)) dans l'ancienne version → ligne 1265 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1256,12 +1265,25 @@ def commenter_issue(numero: int, message: str) -> bool:
     Retourne True si `gh` a réussi (returncode 0), False sinon. Avant issue #195
     le code de retour n'était jamais inspecté : `subprocess.run` retourne
     normalement même sur exit non-zéro, donc un échec réseau intermittent de
-    `gh issue comment` restait silencieux côté Python."""
+    `gh issue comment` restait silencieux côté Python.
+
+    Passe le message via `--body-file` (fichier temporaire UTF-8) plutôt que
+    `--body <message>` (issue #237) : sous Windows la ligne de commande est
+    plafonnée à 32767 caractères, dépassés par un rapport de build
+    multi-étapes — `gh` retournait alors un exit code 0 sans avoir rien posté
+    (troncature silencieuse en amont). `--body-file` supprime aussi tout
+    problème d'échappement de shell."""
+    fichier_tmp = None
     try:
+        with tempfile.NamedTemporaryFile(
+                mode="w", suffix=".md", delete=False,
+                encoding="utf-8") as f:
+            f.write(message)
+            fichier_tmp = f.name
         res = subprocess.run(
             ["gh", "issue", "comment", str(numero),
              "--repo", CFG.depot,
-             "--body", message],
+             "--body-file", fichier_tmp],
             capture_output=True, text=True,
             encoding="utf-8", errors="replace", timeout=30
         )
# ── Zone modifiée : ligne 1272 (6 ligne(s)) dans l'ancienne version → ligne 1294 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1272,6 +1294,12 @@ def commenter_issue(numero: int, message: str) -> bool:
     except Exception as e:
         log.error(f"Erreur commentaire issue #{numero} : {e}")
         return False
+    finally:
+        if fichier_tmp:
+            try:
+                Path(fichier_tmp).unlink(missing_ok=True)
+            except OSError:
+                pass
 
 def editer_dernier_commentaire(numero: int, message: str) -> bool:
     """Édite le dernier commentaire posté par le watcher sur l'issue
# ── Zone modifiée : ligne 1282 (13 ligne(s)) dans l'ancienne version → ligne 1310 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1282,13 +1310,22 @@ def editer_dernier_commentaire(numero: int, message: str) -> bool:
     ne sont connus qu'APRÈS la fermeture de l'issue (maj_calibration_timeout
     a besoin de duree_reelle), donc après le premier `commenter_resultat_avec_
     retry`. Best-effort : un échec ici n'affecte ni la clôture déjà effectuée
-    ni le commentaire déjà en place (juste privé de son bloc calibration)."""
+    ni le commentaire déjà en place (juste privé de son bloc calibration).
+
+    Passe le message via `--body-file` pour la même raison que
+    `commenter_issue` (issue #237)."""
+    fichier_tmp = None
     try:
+        with tempfile.NamedTemporaryFile(
+                mode="w", suffix=".md", delete=False,
+                encoding="utf-8") as f:
+            f.write(message)
+            fichier_tmp = f.name
         res = subprocess.run(
             ["gh", "issue", "comment", str(numero),
              "--repo", CFG.depot,
              "--edit-last",
-             "--body", message],
+             "--body-file", fichier_tmp],
             capture_output=True, text=True,
             encoding="utf-8", errors="replace", timeout=30
         )
# ── Zone modifiée : ligne 1299 (6 ligne(s)) dans l'ancienne version → ligne 1336 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1299,6 +1336,38 @@ def editer_dernier_commentaire(numero: int, message: str) -> bool:
     except Exception as e:
         log.error(f"Erreur édition dernier commentaire issue #{numero} : {e}")
         return False
+    finally:
+        if fichier_tmp:
+            try:
+                Path(fichier_tmp).unlink(missing_ok=True)
+            except OSError:
+                pass
+
+def _commentaire_marque_present(numero: int, marqueur: str = MARQUEUR_RESULTAT) -> bool:
+    """Relit l'issue et indique si un commentaire portant `marqueur` est bien
+    présent (issue #237). Sert à VÉRIFIER qu'un commentaire a réellement été
+    créé plutôt que de faire confiance au seul code de retour de `gh` (celui-ci
+    peut rendre 0 sans qu'aucun commentaire n'existe, cf. issue #236).
+
+    En cas d'erreur de lecture, retourne False (on ne peut pas confirmer la
+    présence => la tentative est traitée comme un échec, quitte à reposter)."""
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "view", str(numero),
+             "--repo", CFG.depot,
+             "--json", "comments"],
+            capture_output=True, text=True,
+            encoding="utf-8", errors="replace", timeout=30
+        )
+        if res.returncode != 0:
+            log.error(f"Erreur lecture commentaires issue #{numero} (code {res.returncode}) : {res.stderr.strip()}")
+            return False
+        data = json.loads(res.stdout or "{}")
+        return any(marqueur in (c.get("body") or "")
+                   for c in data.get("comments", []))
+    except Exception as e:
+        log.error(f"Erreur vérification présence commentaire issue #{numero} : {e}")
+        return False
 
 def commenter_resultat_avec_retry(numero: int, message: str) -> bool:
     """Poste le commentaire de RÉSULTAT avec retry/backoff (issue #195).
# ── Zone modifiée : ligne 1306 (43 ligne(s)) dans l'ancienne version → ligne 1375 (55 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1306,43 +1375,55 @@ def commenter_resultat_avec_retry(numero: int, message: str) -> bool:
     1 tentative initiale, puis jusqu'à 3 tentatives espacées de 5, 10 puis 20 s
     (DELAIS_RETRY_RESULTAT). Retourne True dès qu'une tentative réussit, False si
     toutes échouent. Réservé au commentaire de résultat : l'ACK et le message
-    d'échec restent best-effort sans retry."""
-    if commenter_issue(numero, message):
+    d'échec restent best-effort sans retry.
+
+    VÉRIFICATION post-publication (issue #236/#237) : un exit code 0 de `gh`
+    ne suffit plus à conclure au succès — l'incident #236 a montré un
+    commentaire jamais créé malgré un code de retour 0 (dépassement de la
+    limite argv Windows, cf. `commenter_issue`). Après chaque tentative
+    rendant 0, on relit l'issue et on exige la présence effective du
+    commentaire (marqueur `MARQUEUR_RESULTAT`, ajouté par l'appelant en tête
+    de `message`) avant de retourner True. Si la relecture ne le trouve pas,
+    la tentative est traitée comme un échec et on enchaîne sur la suivante."""
+    def _tentative() -> bool:
+        if not commenter_issue(numero, message):
+            return False
+        if not _commentaire_marque_present(numero):
+            log.error(
+                f"  Commentaire de résultat #{numero} : `gh` a rendu 0 mais aucun "
+                f"commentaire correspondant n'a été retrouvé à la relecture — "
+                f"traité comme un échec (issue #236)."
+            )
+            return False
+        return True
+
+    if _tentative():
         return True
     for delai in DELAIS_RETRY_RESULTAT:
         log.warning(f"  Commentaire de résultat #{numero} échoué — nouvelle tentative dans {delai}s.")
         time.sleep(delai)
-        if commenter_issue(numero, message):
+        if _tentative():
             return True
     log.error(f"  Commentaire de résultat #{numero} échoué après {1 + len(DELAIS_RETRY_RESULTAT)} tentatives.")
     return False
 
 def resultat_deja_poste(numero: int) -> bool:
     """Garde d'idempotence (issue #195) : indique si l'issue porte déjà un
-    commentaire de résultat (`## Résultat`) posté par le watcher.
+    commentaire de résultat posté par le watcher.
+
+    Repère le commentaire par `MARQUEUR_RESULTAT` (issue #237), une ligne HTML
+    invisible ajoutée en tête du message de résultat — et non plus par la
+    sous-chaîne "## Résultat", qui matchait aussi "## Résultat attendu" (titre
+    de section présent dans quasi toutes nos issues) : si ce texte atterrissait
+    un jour dans un commentaire, l'ancienne garde fermait l'issue sans rien
+    traiter.
 
     Sert à éviter un retraitement complet à tort si l'issue est reprise alors
     qu'un cycle précédent avait réussi le commentaire mais échoué la fermeture
     (coupure réseau entre `comment` et `close`). En cas d'erreur de lecture, on
     retourne False (comportement historique : on retraite) plutôt que de risquer
     de sauter à tort une issue réellement non traitée."""
-    try:
-        res = subprocess.run(
-            ["gh", "issue", "view", str(numero),
-             "--repo", CFG.depot,
-             "--json", "comments"],
-            capture_output=True, text=True,
-            encoding="utf-8", errors="replace", timeout=30
-        )
-        if res.returncode != 0:
-            log.error(f"Erreur lecture commentaires issue #{numero} (code {res.returncode}) : {res.stderr.strip()}")
-            return False
-        data = json.loads(res.stdout or "{}")
-        return any("## Résultat" in (c.get("body") or "")
-                   for c in data.get("comments", []))
-    except Exception as e:
-        log.error(f"Erreur vérification idempotence issue #{numero} : {e}")
-        return False
+    return _commentaire_marque_present(numero)
 
 def fermer_issue(numero: int):
     """Ferme une issue et ajoute le label 'done'."""
# ── Zone modifiée : ligne 1847 (7 ligne(s)) dans l'ancienne version → ligne 1928 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1847,7 +1928,7 @@ def traiter_issue(issue: dict, dry_run: bool):
 
             if succes:
                 log.info(f"  ✓ Issue #{numero} traitée avec succès.")
-                message_resultat = f"## Résultat\n\n{avertissement_conflit}{sortie}"
+                message_resultat = f"{MARQUEUR_RESULTAT}\n## Résultat\n\n{avertissement_conflit}{sortie}"
                 # Le commentaire de résultat est critique (issue #195) : on le
                 # poste avec retry/backoff et on ne ferme l'issue QUE s'il a réussi.
                 if not commenter_resultat_avec_retry(numero, message_resultat):
