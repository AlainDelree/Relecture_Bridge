4717a8a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 4717a8a
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Thu Sep 17 19:13:37 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #567 : étend RELANCE à SOUS_DOSSIER et REPO_CIBLE
    
    valider_relance/_fusionner_entete corrigent désormais aussi SOUS_DOSSIER
    et REPO_CIBLE dans le corps d'une issue needs-human (même mécanique que
    TIMEOUT/MODELE, #516) : correction d'une ligne déjà présente uniquement,
    jamais d'insertion. Réutilise valider_sous_dossier/valider_repo_cible
    (watcher.py) pour rejeter toute valeur invalide comme à la création, et
    vérifie explicitement PERIMETRE_DYNAMIQUE=true avant d'accepter une
    correction REPO_CIBLE (garde-fou #125 déjà appliqué à chaque traitement
    par watcher.py, donc non contournable via ce chemin). MODE/labels
    restent exclus (#563), doc §3.14 mise à jour.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d27dfbf..84d9d00 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 457 (7 ligne(s)) dans l'ancienne version → ligne 457 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -457,7 +457,7 @@ fichier n'est supprimé qu'une fois **tous** les blocs traités :
   ce déplacement : chaque motif d'échec a déjà été journalisé individuellement
   ci-dessus.
 
-### 3.14 Champ `RELANCE` : corriger/relancer une issue `needs-human` existante (issue #516)
+### 3.14 Champ `RELANCE` : corriger/relancer une issue `needs-human` existante (issues #516, #567)
 
 **Problème résolu.** Corriger une issue en échec (`needs-human`) —
 typiquement pour ajuster un `TIMEOUT` trop court après un échec par
# ── Zone modifiée : ligne 498 (17 ligne(s)) dans l'ancienne version → ligne 498 (36 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -498,17 +498,36 @@ Le TIMEOUT de 900s était trop court : la tâche a échoué par dépassement.
 Tout échec → rejet vers `rejected/` avec motif clair, même mécanique que
 §3.4 (`_rejeter`).
 
-**Champs corrigibles dans le corps : `TIMEOUT` et `MODELE` uniquement**
-(`_fusionner_entete`/`_maj_ligne_entete`). Ces deux champs sont purement
-textuels dans le corps GitHub existant de l'issue ciblée, sans effet de bord
-— la fonction **corrige une ligne déjà présente**, elle n'en insère jamais
-une nouvelle. `MODE` est volontairement exclu : le mode réellement appliqué
-est armé par le label GitHub `mode_write`/`mode_scratch` (§5), pas par le
-texte du corps ; le changer sans resynchroniser ce label serait trompeur, et
-resynchroniser un label qui arme l'écriture pour CCL depuis ce chemin est
-jugé hors-scope pour cette première itération. `LABELS` est exclu aussi : ce
-champ n'apparaît jamais dans le corps (`construire_body` ne l'y écrit pas,
-§3.3) — « corriger le corps » n'a pas de sens pour lui ici.
+**Champs corrigibles dans le corps : `TIMEOUT`, `MODELE`, `SOUS_DOSSIER` et
+`REPO_CIBLE`** (`_fusionner_entete`/`_maj_ligne_entete`). Ces quatre champs
+sont des paramètres de chemin/configuration purement opérationnels dans le
+corps GitHub existant de l'issue ciblée, sans implication de sécurité — la
+fonction **corrige une ligne déjà présente**, elle n'en insère jamais une
+nouvelle. `MODE` est volontairement exclu : le mode réellement appliqué est
+armé par le label GitHub `mode_write`/`mode_scratch` (§5), pas par le texte
+du corps ; le changer sans resynchroniser ce label serait trompeur, et
+resynchroniser un label qui arme l'écriture pour CCL depuis ce chemin
+ouvrirait une voie de contournement du garde-fou d'auteur d'issue (issue
+#563) — jugé hors-scope, y compris après l'élargissement de #567. `LABELS`
+est exclu aussi : ce champ n'apparaît jamais dans le corps (`construire_body`
+ne l'y écrit pas, §3.3) — « corriger le corps » n'a pas de sens pour lui ici.
+
+`SOUS_DOSSIER` (#550) et `REPO_CIBLE` (#125) ont été ajoutés aux champs
+corrigibles par l'issue #567, retour d'expérience après un premier usage réel
+de `RELANCE` (#566) : ce sont deux champs de la même famille que `TIMEOUT`
+(un paramètre mal réglé peut provoquer un `needs-human`, sans impliquer le
+contournement d'un contrôle de sécurité). Leur correction réutilise **les
+mêmes validateurs qu'à la première exécution de l'issue**
+(`valider_sous_dossier`/`valider_repo_cible`, `watcher.py`) : une valeur
+invalide est rejetée par `valider_relance` exactement comme elle l'aurait été
+à la création, jamais acceptée silencieusement. `REPO_CIBLE` vérifie en plus
+que le projet a `PERIMETRE_DYNAMIQUE = true` dans son `.conf` — ce garde-fou
+n'est pas propre à `RELANCE` : `watcher.py` l'applique de toute façon à
+**chaque** traitement de l'issue, quel que soit le chemin par lequel son
+corps a été corrigé (RELANCE ou édition manuelle sur GitHub), donc `RELANCE`
+ne peut pas s'en affranchir. Le vérifier aussi dans `valider_relance` ne fait
+qu'échouer tôt avec un message clair, plutôt que de laisser passer une
+correction qui resterait de toute façon sans effet.
 
 **Retrait de `needs-human` + commentaire de trace : réutilisation de
 `app.interruption.relancer_issue()`**, extraite du cœur de `route_relancer()`
# (diff du fichier suivant)
diff --git a/scripts/watcher_issues_inbox.py b/scripts/watcher_issues_inbox.py
# (index — ignorable)
index cba2205..da0b61a 100644
# (avant — fichier suivant)
--- a/scripts/watcher_issues_inbox.py
# (après — fichier suivant)
+++ b/scripts/watcher_issues_inbox.py
# ── Zone modifiée : ligne 58 (7 ligne(s)) dans l'ancienne version → ligne 58 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -58,7 +58,8 @@ DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
 sys.path.insert(0, str(DOSSIER_SCRIPT))
 
 from watcher import (charger_config, lire_conf, est_titre_chef,  # noqa: E402
-                     LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS)
+                     LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS,
+                     valider_sous_dossier, valider_repo_cible)  # noqa: E402 (issue #567)
 from app.watchers import demarrer_watcher  # noqa: E402 (issue #486)
 from app.issues import _issue_ouverte_meme_titre  # noqa: E402 (issue #491)
 from app.interruption import relancer_issue  # noqa: E402 (issue #516)
# ── Zone modifiée : ligne 182 (7 ligne(s)) dans l'ancienne version → ligne 183 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -182,7 +183,11 @@ TITRE_RE = re.compile(r"^#Titre:\s*(.*)$", re.IGNORECASE | re.MULTILINE)
 # RELANCE (issue #516) : champ optionnel en cohérence avec SUITE_DE (§6 du
 # DOC) — présent, il détourne tout le bloc du chemin de création habituel
 # vers le chemin de relance d'une issue EXISTANTE (voir _traiter_relance).
-CHAMPS_ENTETE = ("PROJET", "TIMEOUT", "MODELE", "MODE", "LABELS", "RELANCE")
+# SOUS_DOSSIER/REPO_CIBLE (issue #567) : extraits ici comme TIMEOUT/MODELE
+# pour rester disponibles au chemin RELANCE (_fusionner_entete) — inutilisés
+# côté création (construire_body ne les réinsère pas, ce champ n'étant pas un
+# format supporté par issues_inbox pour créer une issue, §3.3 du DOC).
+CHAMPS_ENTETE = ("PROJET", "TIMEOUT", "MODELE", "MODE", "LABELS", "RELANCE", "SOUS_DOSSIER", "REPO_CIBLE")
 
 
 def extraire_champs(contenu: str) -> dict:
# ── Zone modifiée : ligne 211 (6 ligne(s)) dans l'ancienne version → ligne 216 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -211,6 +216,8 @@ def extraire_champs(contenu: str) -> dict:
         "mode_brut":    valeurs["MODE"],
         "labels_brut":  valeurs["LABELS"],
         "relance_brut": valeurs["RELANCE"],
+        "sous_dossier_brut": valeurs["SOUS_DOSSIER"],
+        "repo_cible_brut":   valeurs["REPO_CIBLE"],
         "titre":        titre,
         "corps":        reste.strip("\n"),
     }
# ── Zone modifiée : ligne 315 (16 ligne(s)) dans l'ancienne version → ligne 322 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -315,16 +322,27 @@ def valider(champs: dict):
 # app.interruption.relancer_issue() (cœur du bouton « 🔄 Relancer », issue
 # #460) plutôt que de dupliquer le retrait de label + la pose du commentaire.
 #
-# Champs corrigibles volontairement limités à TIMEOUT et MODELE : purement
-# textuels dans le corps, sans effet de bord. MODE est exclu (le mode réel
+# Champs corrigibles : TIMEOUT, MODELE, SOUS_DOSSIER et REPO_CIBLE (issue
+# #567 pour ces deux derniers) — quatre champs de chemin/paramètre purement
+# opérationnels, sans implication de sécurité. MODE reste exclu (le mode réel
 # est arme par le label GitHub `mode_write`, pas par le texte du corps — le
 # changer sans re-synchroniser ce label serait trompeur, et synchroniser un
-# label qui ARME l'écriture pour CCL depuis ce chemin est jugé hors-scope
-# pour cette première itération) ; LABELS est exclu aussi (il n'apparaît
-# jamais dans le corps — voir construire_body — donc « corriger le corps »
-# n'a pas de sens pour ce champ). RELANCE ne fait que CORRIGER un champ déjà
-# présent dans le corps existant : un champ absent du corps cible reste
-# absent (pas d'insertion de ligne d'en-tête).
+# label qui ARME l'écriture pour CCL depuis ce chemin ouvrirait une voie de
+# contournement du garde-fou d'auteur d'issue, issue #563) ; LABELS est exclu
+# aussi (il n'apparaît jamais dans le corps — voir construire_body — donc
+# « corriger le corps » n'a pas de sens pour ce champ). RELANCE ne fait que
+# CORRIGER un champ déjà présent dans le corps existant : un champ absent du
+# corps cible reste absent (pas d'insertion de ligne d'en-tête).
+#
+# SOUS_DOSSIER/REPO_CIBLE (#567) réutilisent leurs validateurs respectifs
+# (valider_sous_dossier/valider_repo_cible, watcher.py) au moment de la
+# relance, exactement comme à la première exécution — une correction
+# invalide est rejetée, jamais acceptée silencieusement. REPO_CIBLE vérifie
+# en plus que le projet a `PERIMETRE_DYNAMIQUE = true` dans son .conf : ce
+# garde-fou existant (watcher.py, traitement de l'issue) s'applique de toute
+# façon À CHAQUE traitement, RELANCE ou non — cette vérification côté
+# `valider_relance` ne fait qu'échouer tôt et clairement plutôt que de
+# laisser passer une correction qui serait silencieusement sans effet.
 
 RELANCE_RE = re.compile(r"^#?\s*(\d+)\s*$")
 
# ── Zone modifiée : ligne 343 (7 ligne(s)) dans l'ancienne version → ligne 361 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -343,7 +361,16 @@ def valider_relance(champs: dict):
     exploitable, sinon (False, détail_erreur, None, None). Ne vérifie PAS
     l'existence/l'ouverture/le dépôt de l'issue ciblée — cf. _recuperer_issue,
     qui s'en charge via `gh issue view --repo` (échoue déjà si l'issue #N
-    n'appartient pas à ce dépôt)."""
+    n'appartient pas à ce dépôt).
+
+    SOUS_DOSSIER/REPO_CIBLE (issue #567) sont validés ici avec les MÊMES
+    fonctions qu'à la première exécution de l'issue (valider_sous_dossier/
+    valider_repo_cible, watcher.py) — une correction invalide est rejetée,
+    pas silencieusement acceptée. REPO_CIBLE vérifie en plus que le projet a
+    `PERIMETRE_DYNAMIQUE = true` : sans ce réglage, watcher.py ignorerait de
+    toute façon le champ à chaque traitement (garde-fou déjà appliqué, pas
+    seulement à la création) — le rejeter ici évite juste une correction qui
+    n'aurait aucun effet."""
     if not champs["projet"]:
         return False, "en-tête malformé : champ PROJET manquant ou vide.", None, None
 
# ── Zone modifiée : ligne 368 (6 ligne(s)) dans l'ancienne version → ligne 395 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -368,6 +395,20 @@ def valider_relance(champs: dict):
         if not valeur.isdigit():
             return False, f"TIMEOUT invalide : « {champs['timeout_brut']} » (doit être un nombre).", None, None
 
+    if champs.get("sous_dossier_brut"):
+        ok_sd, raison_sd, _ = valider_sous_dossier(cfg_projet.rep_travail, champs["sous_dossier_brut"])
+        if not ok_sd:
+            return False, f"SOUS_DOSSIER invalide : « {champs['sous_dossier_brut']} » ({raison_sd}).", None, None
+
+    if champs.get("repo_cible_brut"):
+        if not getattr(cfg_projet, "perimetre_dynamique", False):
+            return False, (f"REPO_CIBLE fourni mais le projet « {champs['projet']} » n'a pas "
+                            f"PERIMETRE_DYNAMIQUE=true dans son .conf — ce champ n'a d'effet que "
+                            f"pour un projet à périmètre dynamique (issue #125)."), None, None
+        ok_rc, raison_rc = valider_repo_cible(champs["repo_cible_brut"])
+        if not ok_rc:
+            return False, f"REPO_CIBLE invalide : « {champs['repo_cible_brut']} » ({raison_rc}).", None, None
+
     return True, "", cfg_projet, numero
 
 
# ── Zone modifiée : ligne 407 (9 ligne(s)) dans l'ancienne version → ligne 448 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -407,9 +448,10 @@ def _maj_ligne_entete(corps: str, champ: str, valeur: str) -> str:
 
 
 def _fusionner_entete(corps_existant: str, champs: dict) -> tuple[str, list]:
-    """Applique au corps existant de l'issue ciblée les champs TIMEOUT/MODELE
-    fournis par le fichier RELANCE. Retourne (nouveau_corps, champs_modifies)
-    — la liste sert à la fois au commentaire de trace et au log."""
+    """Applique au corps existant de l'issue ciblée les champs TIMEOUT/MODELE/
+    SOUS_DOSSIER/REPO_CIBLE (issue #567 pour ces deux derniers) fournis par le
+    fichier RELANCE. Retourne (nouveau_corps, champs_modifies) — la liste sert
+    à la fois au commentaire de trace et au log."""
     nouveau = corps_existant
     modifies = []
 
# ── Zone modifiée : ligne 426 (6 ligne(s)) dans l'ancienne version → ligne 468 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -426,6 +468,18 @@ def _fusionner_entete(corps_existant: str, champs: dict) -> tuple[str, list]:
         if nouveau != avant:
             modifies.append(f"MODELE → {champs['modele']}")
 
+    if champs.get("sous_dossier_brut"):
+        avant = nouveau
+        nouveau = _maj_ligne_entete(nouveau, "SOUS_DOSSIER", champs["sous_dossier_brut"])
+        if nouveau != avant:
+            modifies.append(f"SOUS_DOSSIER → {champs['sous_dossier_brut']}")
+
+    if champs.get("repo_cible_brut"):
+        avant = nouveau
+        nouveau = _maj_ligne_entete(nouveau, "REPO_CIBLE", champs["repo_cible_brut"])
+        if nouveau != avant:
+            modifies.append(f"REPO_CIBLE → {champs['repo_cible_brut']}")
+
     return nouveau, modifies
 
 
# (diff du fichier suivant)
diff --git a/tests/test_champ_relance_516.py b/tests/test_champ_relance_516.py
# (index — ignorable)
index e007036..cab61f3 100644
# (avant — fichier suivant)
--- a/tests/test_champ_relance_516.py
# (après — fichier suivant)
+++ b/tests/test_champ_relance_516.py
# ── Zone modifiée : ligne 27 (18 ligne(s)) dans l'ancienne version → ligne 27 (22 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -27,18 +27,22 @@ sys.path.insert(0, str(RACINE / "scripts"))
 import watcher_issues_inbox as w  # noqa: E402
 
 
-def _cfg_projet(depot="AlainDelree/Bridge_Agent", nom="bridge_agent"):
-    return SimpleNamespace(depot=depot, nom=nom, timeout_claude=300, timeout_chef=1200)
+def _cfg_projet(depot="AlainDelree/Bridge_Agent", nom="bridge_agent", rep_travail=None, perimetre_dynamique=False):
+    return SimpleNamespace(depot=depot, nom=nom, timeout_claude=300, timeout_chef=1200,
+                            rep_travail=rep_travail or Path(tempfile.gettempdir()),
+                            perimetre_dynamique=perimetre_dynamique)
 
 
-def _preparer_config_bidon(tmp_dir: Path, projet="bridge_agent"):
+def _preparer_config_bidon(tmp_dir: Path, projet="bridge_agent", perimetre_dynamique=False):
     """Fait pointer DOSSIER_SCRIPT/charger_config vers un projet bidon —
     évite toute dépendance à un vrai configs/<projet>.conf (gitignoré,
-    absent de ce worktree)."""
+    absent de ce worktree). `rep_travail` du projet bidon pointe sur
+    `tmp_dir` (issue #567) : nécessaire à `valider_sous_dossier`, appelée par
+    `valider_relance` pour la correction SOUS_DOSSIER."""
     (tmp_dir / "configs").mkdir(parents=True, exist_ok=True)
     (tmp_dir / "configs" / f"{projet}.conf").write_text("DEPOT=AlainDelree/Bridge_Agent\n")
     w.DOSSIER_SCRIPT = tmp_dir
-    w.charger_config = lambda chemin: _cfg_projet()
+    w.charger_config = lambda chemin: _cfg_projet(rep_travail=tmp_dir, perimetre_dynamique=perimetre_dynamique)
 
 
 def scenario_1_extraction_champ_relance():
# ── Zone modifiée : ligne 182 (6 ligne(s)) dans l'ancienne version → ligne 186 (181 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -182,6 +186,181 @@ def scenario_7_traiter_relance_numero_invalide_rejete():
     return {"texte": texte}
 
 
+# ─── Issue #567 : extension de RELANCE à SOUS_DOSSIER et REPO_CIBLE ─────────
+
+def scenario_8_extraction_champs_sous_dossier_repo_cible():
+    """SOUS_DOSSIER et REPO_CIBLE sont reconnus comme TIMEOUT/MODELE et
+    retirés du corps restant."""
+    contenu = (
+        "| PROJET       | bridge_agent |\n"
+        "| RELANCE      | #77 |\n"
+        "| SOUS_DOSSIER | CCW/gestionmail |\n"
+        "| REPO_CIBLE   | /home/alain/Autre_Projet |\n"
+        "\n"
+        "Le chemin visé était incorrect, d'où la correction.\n"
+    )
+    champs = w.extraire_champs(contenu)
+    assert champs["sous_dossier_brut"] == "CCW/gestionmail", champs["sous_dossier_brut"]
+    assert champs["repo_cible_brut"] == "/home/alain/Autre_Projet", champs["repo_cible_brut"]
+    assert "SOUS_DOSSIER" not in champs["corps"], champs["corps"]
+    assert "REPO_CIBLE" not in champs["corps"], champs["corps"]
+    return {"sous_dossier_brut": champs["sous_dossier_brut"], "repo_cible_brut": champs["repo_cible_brut"]}
+
+
+def scenario_9_fusion_entete_corrige_sous_dossier_et_repo_cible():
+    """SOUS_DOSSIER/REPO_CIBLE déjà présents dans le corps GitHub existant
+    sont corrigés ; un champ absent n'est jamais inséré."""
+    corps_existant = (
+        "## En-tête\n\n"
+        "| Champ        | Valeur |\n"
+        "|--------------|--------|\n"
+        "| SOURCE       | CC |\n"
+        "| SOUS_DOSSIER | ancien/chemin |\n"
+        "| PROJET       | bridge_agent |\n\n"
+        "## Contexte\nTexte.\n"
+    )
+    champs = {"timeout_brut": None, "modele": "", "corps": "",
+              "sous_dossier_brut": "nouveau/chemin", "repo_cible_brut": "/repo/absent/du/corps"}
+    nouveau, modifies = w._fusionner_entete(corps_existant, champs)
+    assert "| SOUS_DOSSIER | nouveau/chemin |" in nouveau, nouveau
+    assert "ancien/chemin" not in nouveau, nouveau
+    assert "REPO_CIBLE" not in nouveau, "REPO_CIBLE absent du corps cible ne doit jamais être inséré"
+    assert modifies == ["SOUS_DOSSIER → nouveau/chemin"], modifies
+    return {"modifies": modifies}
+
+
+def scenario_10_valider_relance_sous_dossier_valide(tmp_path_factory):
+    """SOUS_DOSSIER valide (relatif, existe sous REP_TRAVAIL du projet) est
+    accepté par valider_relance — réutilise valider_sous_dossier telle
+    quelle."""
+    tmp_dir = tmp_path_factory()
+    _preparer_config_bidon(tmp_dir)
+    (tmp_dir / "souscode").mkdir(exist_ok=True)
+
+    champs = w.extraire_champs(
+        "| PROJET       | bridge_agent |\n"
+        "| RELANCE      | #77 |\n"
+        "| SOUS_DOSSIER | souscode |\n"
+    )
+    ok, detail, cfg_projet, numero = w.valider_relance(champs)
+    assert ok, detail
+    assert numero == 77
+    return {"detail": detail}
+
+
+def scenario_11_valider_relance_sous_dossier_invalide_rejete(tmp_path_factory):
+    """SOUS_DOSSIER pointant vers un dossier inexistant est rejeté — même
+    validateur, même exigence qu'à la création."""
+    tmp_dir = tmp_path_factory()
+    _preparer_config_bidon(tmp_dir)
+
+    champs = w.extraire_champs(
+        "| PROJET       | bridge_agent |\n"
+        "| RELANCE      | #77 |\n"
+        "| SOUS_DOSSIER | dossier/qui/nexiste/pas |\n"
+    )
+    ok, detail, cfg_projet, numero = w.valider_relance(champs)
+    assert not ok
+    assert "SOUS_DOSSIER invalide" in detail, detail
+    return {"detail": detail}
+
+
+def scenario_12_valider_relance_repo_cible_necessite_perimetre_dynamique(tmp_path_factory):
+    """REPO_CIBLE fourni via RELANCE mais projet SANS PERIMETRE_DYNAMIQUE=true
+    est rejeté — le garde-fou de #125 reste vérifié à la relance, pas
+    seulement à la création (issue #567)."""
+    tmp_dir = tmp_path_factory()
+    _preparer_config_bidon(tmp_dir, perimetre_dynamique=False)
+
+    champs = w.extraire_champs(
+        "| PROJET     | bridge_agent |\n"
+        "| RELANCE    | #77 |\n"
+        f"| REPO_CIBLE | {tmp_dir} |\n"
+    )
+    ok, detail, cfg_projet, numero = w.valider_relance(champs)
+    assert not ok
+    assert "PERIMETRE_DYNAMIQUE" in detail, detail
+    return {"detail": detail}
+
+
+def scenario_13_valider_relance_repo_cible_valide_avec_perimetre_dynamique(tmp_path_factory):
+    """REPO_CIBLE valide (absolu, existant, PERIMETRE_DYNAMIQUE=true) est
+    accepté par valider_relance — réutilise valider_repo_cible telle
+    quelle."""
+    tmp_dir = tmp_path_factory()
+    _preparer_config_bidon(tmp_dir, perimetre_dynamique=True)
+
+    champs = w.extraire_champs(
+        "| PROJET     | bridge_agent |\n"
+        "| RELANCE    | #77 |\n"
+        f"| REPO_CIBLE | {tmp_dir} |\n"
+    )
+    ok, detail, cfg_projet, numero = w.valider_relance(champs)
+    assert ok, detail
+    return {"detail": detail}
+
+
+def scenario_14_valider_relance_repo_cible_invalide_rejete(tmp_path_factory):
+    """REPO_CIBLE relatif (invalide selon valider_repo_cible) reste rejeté
+    même avec PERIMETRE_DYNAMIQUE=true — le garde-fou n'accepte pas
+    n'importe quel chemin pour autant."""
+    tmp_dir = tmp_path_factory()
+    _preparer_config_bidon(tmp_dir, perimetre_dynamique=True)
+
+    champs = w.extraire_champs(
+        "| PROJET     | bridge_agent |\n"
+        "| RELANCE    | #77 |\n"
+        "| REPO_CIBLE | chemin/relatif |\n"
+    )
+    ok, detail, cfg_projet, numero = w.valider_relance(champs)
+    assert not ok
+    assert "REPO_CIBLE invalide" in detail, detail
+    return {"detail": detail}
+
+
+def scenario_15_traiter_relance_sous_dossier_chemin_complet_succes(tmp_path_factory):
+    """Chemin complet _traiter_relance avec correction SOUS_DOSSIER : corps
+    mis à jour, retrait needs-human + commentaire de trace inchangés."""
+    tmp_dir = tmp_path_factory()
+    _preparer_config_bidon(tmp_dir)
+    (tmp_dir / "bonchemin").mkdir(exist_ok=True)
+
+    appels = {}
+
+    def _fausse_recuperation(depot, numero):
+        return True, "", {
+            "number": numero, "state": "OPEN", "title": "SOUS_DOSSIER incorrect",
+            "body": "| SOUS_DOSSIER | mauvais/chemin |\n| PROJET | bridge_agent |\n",
+        }
+
+    def _faux_edit_corps(depot, numero, corps):
+        appels["corps_envoye"] = corps
+        return True, ""
+
+    def _faux_relancer(depot, numero, commentaire=""):
+        appels["commentaire"] = commentaire
+        return "ok", [{"etape": "retrait_label_needs_human", "statut": "succes", "message": ""},
+                        {"etape": "commentaire", "statut": "succes", "message": ""}]
+
+    w._recuperer_issue = _fausse_recuperation
+    w._modifier_corps_gh = _faux_edit_corps
+    w.relancer_issue = _faux_relancer
+
+    champs = w.extraire_champs(
+        "| PROJET       | bridge_agent |\n"
+        "| RELANCE      | #77 |\n"
+        "| SOUS_DOSSIER | bonchemin |\n"
+        "\n"
+        "Le SOUS_DOSSIER pointait au mauvais endroit.\n"
+    )
+    succes, titre, projet, texte, resultat_gh = w._traiter_relance(w.ConfigInbox(), champs)
+
+    assert succes, texte
+    assert "| SOUS_DOSSIER | bonchemin |" in appels["corps_envoye"], appels["corps_envoye"]
+    assert "SOUS_DOSSIER → bonchemin" in appels["commentaire"], appels["commentaire"]
+    return {"texte": texte}
+
+
 def main():
     tmp = tempfile.TemporaryDirectory()
 
# ── Zone modifiée : ligne 196 (6 ligne(s)) dans l'ancienne version → ligne 375 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -196,6 +375,14 @@ def main():
         ("_traiter_relance : chemin complet, succès", lambda: scenario_5_traiter_relance_chemin_complet_succes(_tmp_path_factory)),
         ("_traiter_relance : issue fermée → rejet", scenario_6_traiter_relance_issue_fermee_rejetee),
         ("_traiter_relance : RELANCE non numérique → rejet", scenario_7_traiter_relance_numero_invalide_rejete),
+        ("champs SOUS_DOSSIER/REPO_CIBLE extraits et retirés du corps (#567)", scenario_8_extraction_champs_sous_dossier_repo_cible),
+        ("_fusionner_entete corrige SOUS_DOSSIER/REPO_CIBLE, n'en insère jamais (#567)", scenario_9_fusion_entete_corrige_sous_dossier_et_repo_cible),
+        ("valider_relance : SOUS_DOSSIER valide accepté (#567)", lambda: scenario_10_valider_relance_sous_dossier_valide(_tmp_path_factory)),
+        ("valider_relance : SOUS_DOSSIER invalide rejeté (#567)", lambda: scenario_11_valider_relance_sous_dossier_invalide_rejete(_tmp_path_factory)),
+        ("valider_relance : REPO_CIBLE sans PERIMETRE_DYNAMIQUE rejeté (#567)", lambda: scenario_12_valider_relance_repo_cible_necessite_perimetre_dynamique(_tmp_path_factory)),
+        ("valider_relance : REPO_CIBLE valide accepté avec PERIMETRE_DYNAMIQUE (#567)", lambda: scenario_13_valider_relance_repo_cible_valide_avec_perimetre_dynamique(_tmp_path_factory)),
+        ("valider_relance : REPO_CIBLE invalide rejeté même avec PERIMETRE_DYNAMIQUE (#567)", lambda: scenario_14_valider_relance_repo_cible_invalide_rejete(_tmp_path_factory)),
+        ("_traiter_relance : chemin complet SOUS_DOSSIER, succès (#567)", lambda: scenario_15_traiter_relance_sous_dossier_chemin_complet_succes(_tmp_path_factory)),
     ]
     echecs = 0
     for nom, fn in tests:
