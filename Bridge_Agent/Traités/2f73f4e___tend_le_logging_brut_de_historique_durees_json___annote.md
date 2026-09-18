2f73f4e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2f73f4e
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Jul 25 02:39:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Étend le logging brut de historique_durees.json (issue #220)
    
    Ajoute des champs bruts par entrée (longueur_corps_issue, nb_etapes_checklist,
    nb_projets_actifs_au_lancement, expiree, tag_reseau si détectable) pour
    préparer une future calibration automatique du TIMEOUT — sans changer aucun
    calcul existant. Corrige aussi l'absence de trace des timeouts : chaque
    tentative expirée (subprocess.TimeoutExpired) est désormais enregistrée avec
    expiree=true, alors qu'elle ne laissait auparavant aucune trace dans le
    fichier. mode reste binaire read/write (mode_tmp_write n'existe pas encore en
    code, cf. TACHES.md) ; nb_fichiers_cibles reste toujours null (pas de
    convention fiable pour extraire des chemins de fichiers d'un corps libre).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/watcher.py b/watcher.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5195e81..df59247 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/watcher.py
# ── Version APRÈS ce commit.
+++ b/watcher.py
# ── Zone modifiée : ligne 658 (12 ligne(s)) dans l'ancienne version → ligne 658 (44 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -658,12 +658,44 @@ def _consignes_injectees(nom_projet: str, titre: str, corps: str) -> str:
     return "\n\n".join(blocs)
 
 
+def _compter_etapes_checklist(body: str) -> int | None:
+    """Nombre d'items de checklist Markdown (`- [ ]` / `- [x]`) dans le corps de
+    l'issue (issue #220, champ nb_etapes_checklist), ou None si aucune checklist
+    n'est présente — valeur brute, aucune interprétation de ce que représentent
+    ces items."""
+    n = sum(1 for ligne in (body or "").splitlines()
+            if re.match(r"\s*[-*]\s*\[[ xX]\]", ligne))
+    return n or None
+
+
+def _detecter_tag_reseau(body: str) -> bool | None:
+    """Déduit tag_reseau depuis un marqueur explicite de l'en-tête (issue #220).
+
+    Aucun champ de ce type n'existe aujourd'hui dans le format d'en-tête bridge
+    (§6 du DOC : SOURCE/DEST/RETOUR/MODE/PRIORITE/TIMEOUT/PROJET/TYPE/MODELE/
+    FICHIER_CONTEXTE/SUITE_DE — pas de champ réseau). On ne fabrique donc PAS de
+    détection ici (pas de mot-clé deviné dans le corps) : ceci renvoie toujours
+    None pour l'instant, en attendant qu'un futur champ d'en-tête dédié soit
+    ajouté par Claude Chat à la rédaction des issues. enregistrer_duree omet la
+    clé tag_reseau de l'entrée tant que cette fonction renvoie None."""
+    return None
+
+
 def enregistrer_duree(projet: str, type_issue: str, mode: str,
-                      duree_s: float, date_iso: str):
-    """Ajoute une mesure de durée réelle (ACK → fermeture) à l'historique commun
-    (issue #108). Best-effort : toute erreur est journalisée sans jamais
-    interrompre le traitement de l'issue. Le fichier est une simple liste JSON
-    d'objets {projet, type, mode, duree, date}."""
+                      duree_s: float | None, date_iso: str, *,
+                      body: str = "", nb_projets_actifs: int = 0,
+                      expiree: bool = False):
+    """Ajoute une mesure de durée réelle (ACK → fermeture, ou ACK → timeout si
+    expiree=True) à l'historique commun (issue #108, étendu #220). Best-effort :
+    toute erreur est journalisée sans jamais interrompre le traitement de
+    l'issue. Le fichier est une liste JSON d'objets ; issue #220 étend chaque
+    entrée avec des champs BRUTS (aucune tranche/catégorisation) en préparation
+    d'une future calibration automatique du TIMEOUT : longueur_corps_issue,
+    nb_etapes_checklist, nb_fichiers_cibles (toujours None ici — pas de
+    convention fiable pour lister les fichiers cibles dans un corps libre,
+    mieux vaut None qu'une extraction fragile par regex), nb_projets_actifs_au_
+    lancement, expiree, et tag_reseau (omis tant qu'aucun marqueur explicite
+    n'existe, cf. _detecter_tag_reseau)."""
     try:
         DOSSIER_LOGS.mkdir(parents=True, exist_ok=True)
         historique = []
# ── Zone modifiée : ligne 672 (13 ligne(s)) dans l'ancienne version → ligne 704 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -672,13 +704,22 @@ def enregistrer_duree(projet: str, type_issue: str, mode: str,
                 historique = json.loads(FICHIER_HISTORIQUE.read_text(encoding="utf-8")) or []
             except (json.JSONDecodeError, OSError):
                 historique = []   # fichier corrompu : on repart d'une liste vide
-        historique.append({
+        entree = {
             "projet": projet,
             "type":   type_issue,
             "mode":   mode,
-            "duree":  round(duree_s),   # secondes
+            "duree":  round(duree_s) if duree_s is not None else None,   # secondes
             "date":   date_iso,
-        })
+            "longueur_corps_issue": len(body or ""),
+            "nb_etapes_checklist": _compter_etapes_checklist(body),
+            "nb_fichiers_cibles": None,
+            "nb_projets_actifs_au_lancement": nb_projets_actifs,
+            "expiree": expiree,
+        }
+        tag_reseau = _detecter_tag_reseau(body)
+        if tag_reseau is not None:
+            entree["tag_reseau"] = tag_reseau
+        historique.append(entree)
         FICHIER_HISTORIQUE.write_text(
             json.dumps(historique, ensure_ascii=False, indent=2), encoding="utf-8")
     except Exception as e:
# ── Zone modifiée : ligne 809 (6 ligne(s)) dans l'ancienne version → ligne 850 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -809,6 +850,15 @@ def _watcher_actif(cfg: Config) -> bool:
     except (OSError, ProcessLookupError, ValueError):
         return False
 
+
+def _compter_watchers_actifs() -> int:
+    """Nombre de watchers actuellement en cours d'exécution, tous projets
+    confondus (issue #220, champ nb_projets_actifs_au_lancement de l'historique
+    des durées). Réutilise les mêmes fichiers PID (logs/watcher-<nom>.pid, §13 du
+    DOC) que detecter_conflit_watcher, plutôt qu'un scan brut du dossier logs/."""
+    return sum(1 for cfg in _lister_projets_connus() if _watcher_actif(cfg))
+
+
 def detecter_conflit_watcher(repo_cible_resolu: Path, projet_courant: str) -> str | None:
     """Cherche un projet connu, watcher actif, dont le rep_travail ou le
     périmètre chevauche repo_cible_resolu (chemins résolus, égalité ou relation
# ── Zone modifiée : ligne 1404 (6 ligne(s)) dans l'ancienne version → ligne 1454 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1404,6 +1454,10 @@ def traiter_issue(issue: dict, dry_run: bool):
         # durées (issue #108). monotonic() pour la mesure d'écoulement (insensible aux
         # changements d'heure système).
         debut_traitement = time.monotonic()
+        # Nombre de watchers actifs au lancement DE CETTE ISSUE (issue #220, champ
+        # nb_projets_actifs_au_lancement) — figé une fois pour toute la durée du
+        # traitement (succès ou timeouts successifs), pas recalculé à chaque tentative.
+        nb_projets_actifs_debut = _compter_watchers_actifs()
 
         tentative = 0
         while True:
# ── Zone modifiée : ligne 1450 (6 ligne(s)) dans l'ancienne version → ligne 1504 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1450,6 +1504,8 @@ def traiter_issue(issue: dict, dry_run: bool):
                     "write" if autoriser_ecriture else "read",
                     time.monotonic() - debut_traitement,
                     datetime.now().isoformat(timespec="seconds"),
+                    body=body,
+                    nb_projets_actifs=nb_projets_actifs_debut,
                 )
                 notifier(
                     labels,
# ── Zone modifiée : ligne 1463 (6 ligne(s)) dans l'ancienne version → ligne 1519 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1463,6 +1519,27 @@ def traiter_issue(issue: dict, dry_run: bool):
             # Échec
             log.warning(f"  ✗ Tentative {tentative} échouée : {sortie}")
 
+            # Trace du timeout dans l'historique des durées (issue #220) : avant ce
+            # correctif, une tentative expirée (subprocess.TimeoutExpired dans
+            # lancer_claude, message "Timeout après <N>s") ne laissait AUCUNE trace
+            # dans historique_durees.json — seulement dans le log texte du watcher.
+            # Un enregistrement minimal (expiree=True) est ajouté ICI, PAR TENTATIVE
+            # expirée (pas seulement à l'abandon définitif), pour permettre de
+            # compter la fréquence réelle des timeouts dans une future issue — y
+            # compris pour les issues critiques en retry infini, qui n'atteignent
+            # jamais la branche d'abandon ci-dessous.
+            if sortie.startswith("Timeout après"):
+                enregistrer_duree(
+                    CFG.nom,
+                    deduire_type_issue(titre, body),
+                    "write" if autoriser_ecriture else "read",
+                    time.monotonic() - debut_traitement,
+                    datetime.now().isoformat(timespec="seconds"),
+                    body=body,
+                    nb_projets_actifs=nb_projets_actifs_debut,
+                    expiree=True,
+                )
+
             if tentative >= CFG.max_essais:
                 if critique:
                     alerte_critique(numero, titre, tentative, labels)
