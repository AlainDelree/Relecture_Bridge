e69fb74

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e69fb74
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Sep 2 22:10:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #516 : champ RELANCE dans issues_inbox pour corriger/relancer une issue needs-human
    
    - scripts/watcher_issues_inbox.py : | RELANCE | #N | détourne un bloc vers
      la correction de l'issue #N déjà ouverte (TIMEOUT/MODELE fusionnés dans
      le corps existant, needs-human retiré, commentaire de trace) au lieu
      d'une création — anti-doublon court-circuité (n'a de sens que pour une
      création). Validation dépôt/état via `gh issue view --repo` avant toute
      modification.
    - app/interruption.py : extrait relancer_issue() du cœur de route_relancer()
      (bouton "Relancer", #460) pour la réutiliser depuis issues_inbox/, sans
      dupliquer le retrait de label + la pose de commentaire.
    - BRIDGE_AGENT_DOC.md (§3.14, §6) + tests/test_champ_relance_516.py.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4a4805b..0faf082 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 454 (6 ligne(s)) dans l'ancienne version → ligne 454 (78 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -454,6 +454,78 @@ fichier n'est supprimé qu'une fois **tous** les blocs traités :
   ce déplacement : chaque motif d'échec a déjà été journalisé individuellement
   ci-dessus.
 
+### 3.14 Champ `RELANCE` : corriger/relancer une issue `needs-human` existante (issue #516)
+
+**Problème résolu.** Corriger une issue en échec (`needs-human`) —
+typiquement pour ajuster un `TIMEOUT` trop court après un échec par
+dépassement — obligeait jusqu'ici à sortir du flux `issues_inbox` : éditer le
+corps à la main sur GitHub, puis retirer `needs-human` (bouton
+« 🔄 Relancer », §13 « Relancer une issue bloquée en needs-human », issue
+#460). Redéposer un `.txt` avec le même
+titre échouait systématiquement : l'anti-doublon (§3.4) rejette tout titre
+déjà porté par une issue OUVERTE — ce qui inclut justement `needs-human`,
+puisqu'elle reste ouverte. Ce comportement de l'anti-doublon reste correct et
+inchangé ; `RELANCE` ajoute un chemin **volontaire** et **distinct** pour
+cibler une issue déjà ouverte, en cohérence avec le champ `SUITE_DE`
+existant (§6) qui référence lui aussi une issue par `#N`.
+
+**Format.** `| RELANCE | #N |` dans l'en-tête (même zone bornée que les
+autres champs, §3.3) — la présence de ce champ détourne **tout le bloc** vers
+le chemin de relance, avant toute validation/anti-doublon de création :
+`#Titre:` n'est plus requis (ignoré s'il est présent) et aucune issue n'est
+jamais créée pour ce bloc.
+
+```markdown
+| PROJET  | bridge_agent |
+| RELANCE | #612 |
+| TIMEOUT | 1800s |
+
+Le TIMEOUT de 900s était trop court : la tâche a échoué par dépassement.
+```
+
+**Validation avant modification (`valider_relance`, `_recuperer_issue`,
+`scripts/watcher_issues_inbox.py`) :**
+- `PROJET` doit désigner un `configs/<PROJET>.conf` valide (résout le dépôt
+  GitHub cible, `cfg_projet.depot`) ;
+- `RELANCE` doit être un numéro exploitable (`#N` ou `N`) ;
+- `gh issue view <N> --repo <depot>` doit réussir — échoue déjà si l'issue
+  n'existe pas ou n'appartient pas à ce dépôt, ce qui couvre la vérification
+  « bon dépôt/projet » sans logique supplémentaire ;
+- l'issue doit être **OUVERTE** (`state == "OPEN"`).
+Tout échec → rejet vers `rejected/` avec motif clair, même mécanique que
+§3.4 (`_rejeter`).
+
+**Champs corrigibles dans le corps : `TIMEOUT` et `MODELE` uniquement**
+(`_fusionner_entete`/`_maj_ligne_entete`). Ces deux champs sont purement
+textuels dans le corps GitHub existant de l'issue ciblée, sans effet de bord
+— la fonction **corrige une ligne déjà présente**, elle n'en insère jamais
+une nouvelle. `MODE` est volontairement exclu : le mode réellement appliqué
+est armé par le label GitHub `mode_write`/`mode_scratch` (§5), pas par le
+texte du corps ; le changer sans resynchroniser ce label serait trompeur, et
+resynchroniser un label qui arme l'écriture pour CCL depuis ce chemin est
+jugé hors-scope pour cette première itération. `LABELS` est exclu aussi : ce
+champ n'apparaît jamais dans le corps (`construire_body` ne l'y écrit pas,
+§3.3) — « corriger le corps » n'a pas de sens pour lui ici.
+
+**Retrait de `needs-human` + commentaire de trace : réutilisation de
+`app.interruption.relancer_issue()`**, extraite du cœur de `route_relancer()`
+(bouton « 🔄 Relancer », issue #460) précisément pour ce réemploi — aucune
+logique de retrait de label / pose de commentaire dupliquée entre les deux
+flux. Le commentaire posté diffère de celui du bouton (mention explicite
+d'issues_inbox/RELANCE) et résume les champs effectivement corrigés, plus le
+texte libre éventuel du fichier (au-delà de l'en-tête et de `#Titre:`) —
+utile pour tracer *pourquoi* la correction a été faite.
+
+**Non traité par ce chemin** (hors-scope, cf. ci-dessus) : changement de
+`MODE`/labels via `RELANCE`, insertion d'un champ absent du corps cible,
+renommage du titre GitHub. Une correction plus large reste possible à la
+main sur GitHub, comme avant #516.
+
+**Formulaire web.** Pas de reprise dans `new_issue.py`/`static/js/app.js` :
+le formulaire sert à **créer** des issues, et dispose déjà d'un chemin dédié
+pour cibler une issue existante (bouton « 🔄 Relancer », §13) — dupliquer
+`RELANCE` là n'apporterait rien.
+
 ---
 
 ## 4. Labels disponibles
# ── Zone modifiée : ligne 556 (6 ligne(s)) dans l'ancienne version → ligne 628 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -556,6 +628,7 @@ Le watcher lit ces champs dans le tableau markdown de l'en-tête :
 | `TYPE` | `chef` ou `ouvrier` | Identifie le rôle de l'issue dans le pattern multi-agent. `chef` = orchestre les ouvriers. `ouvrier` = sous-tâche créée par le chef, masquée par défaut dans l'onglet Résultats. Absent = issue normale. |
 | `FICHIER_CONTEXTE` | ex. chemin relatif | Fichier additionnel fourni en contexte à CCL pour cette issue (modifiable via l'onglet Configuration, voir §12) |
 | `SUITE_DE` | ex. `#5` | Indique que cette issue fait suite à l'issue #N (discussion ou tâche complémentaire). Absent = issue inédite. |
+| `RELANCE` | ex. `#612` | **Spécifique à `issues_inbox/`** (issue #516, voir §3.14) — présent, détourne le fichier déposé vers la correction/relance de l'issue #N déjà ouverte (`TIMEOUT`/`MODELE` du fichier fusionnés dans son corps, `needs-human` retiré) plutôt que de créer une nouvelle issue. N'a aucun effet une fois l'issue créée — lu uniquement au dépôt du fichier, jamais par `watcher.py`. |
 | `COMPLEXITE` | `rapide` / `court` / `normal` / `lourd` | 4e dimension de la clé EWMA de calibration TIMEOUT (issue #434, voir §19), estimée par Claude Chat au moment de rédiger l'issue. Absent ou valeur non reconnue = `normal` (défaut, ~300s). CCL/CCW doit l'inclure dans les issues chef/ouvrier qu'il crée (voir `consignes/globales.md`) ; pour les issues de Claude Chat, c'est géré côté doc/prompt. |
 | `RESEAU` | `oui` ou `non` | Tag réseau pour la calibration TIMEOUT (issue #220/#435, voir §19) : `oui` = issue impliquant de lourdes opérations réseau (téléchargements, builds avec fetch, etc.), `non` = issue purement locale. Lu par `_detecter_tag_reseau(body)`. Absent ou valeur non reconnue = `None` (F ignoré, facteur d'ambiance neutre). Optionnel (voir `consignes/globales.md`). |
 
# (diff du fichier suivant)
diff --git a/CHANGELOG-516.md b/CHANGELOG-516.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..769dc4c
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/CHANGELOG-516.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (40 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,40 @@
+## 2 septembre 2026 — issue #516
+
+Champ `RELANCE` dans `issues_inbox/` : corriger/relancer une issue
+`needs-human` sans repasser par une édition manuelle sur GitHub. Jusqu'ici,
+ajuster un `TIMEOUT` trop court après un échec par dépassement obligeait à
+sortir du flux `issues_inbox` — redéposer un `.txt` avec le même titre
+échouait systématiquement (anti-doublon §3.4, qui rejette tout titre déjà
+porté par une issue OUVERTE, `needs-human` incluse).
+- `scripts/watcher_issues_inbox.py` : nouveau champ d'en-tête optionnel
+  `| RELANCE | #N |` (en cohérence avec `SUITE_DE`, §6). Présent, il
+  détourne tout le bloc vers la correction de l'issue #N déjà ouverte —
+  aucune création, anti-doublon court-circuité (n'a de sens que pour une
+  création). Validation avant modification (`valider_relance`,
+  `_recuperer_issue`) : `PROJET` résout le dépôt cible, `RELANCE` doit être
+  un numéro exploitable, `gh issue view --repo` confirme l'existence et
+  l'appartenance au bon dépôt, l'issue doit être OUVERTE — sinon rejet vers
+  `rejected/`, même mécanique que les rejets existants. Champs corrigibles
+  dans le corps : `TIMEOUT` et `MODELE` uniquement (`_fusionner_entete`/
+  `_maj_ligne_entete` — corrige une ligne déjà présente, n'en insère jamais
+  une nouvelle). `MODE` est exclu (le mode réel est armé par le label GitHub
+  `mode_write`/`mode_scratch`, pas par le texte du corps — le
+  resynchroniser depuis ce chemin est jugé hors-scope pour cette première
+  itération) ; `LABELS` aussi (n'apparaît jamais dans le corps).
+- `app/interruption.py` : logique de `route_relancer()` (bouton
+  « 🔄 Relancer », issue #460) extraite dans `relancer_issue(depot, numero,
+  commentaire=...)`, réutilisée telle quelle par le champ `RELANCE` — aucun
+  retrait de label / pose de commentaire dupliqué entre les deux flux. Le
+  commentaire posté depuis `issues_inbox/` mentionne explicitement RELANCE,
+  résume les champs corrigés et reprend le texte libre éventuel du fichier
+  déposé.
+- `BRIDGE_AGENT_DOC.md` : nouveau §3.14, ligne `RELANCE` ajoutée au tableau
+  §6.
+- `tests/test_champ_relance_516.py` (nouveau) : extraction du champ,
+  parsing du numéro, fusion des champs corrigibles (jamais d'insertion d'un
+  champ absent), chemin complet `_traiter_relance` (succès, issue fermée,
+  numéro invalide) — tous les appels `gh` substitués, aucun accès réseau.
+- Formulaire web (`new_issue.py`) volontairement non modifié : il sert à
+  **créer** des issues et dispose déjà d'un chemin dédié pour cibler une
+  issue existante (bouton « 🔄 Relancer ») — dupliquer `RELANCE` là
+  n'apporterait rien.
# (diff du fichier suivant)
diff --git a/app/interruption.py b/app/interruption.py
# (index — ignorable)
index 66a499a..507a5e0 100644
# (avant — fichier suivant)
--- a/app/interruption.py
# (après — fichier suivant)
+++ b/app/interruption.py
# ── Zone modifiée : ligne 442 (17 ligne(s)) dans l'ancienne version → ligne 442 (34 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -442,17 +442,34 @@ def route_interrompre():
     return jsonify(**reponse)
 
 
-def route_relancer():
-    """POST /relancer-issue — remet en file d'attente une issue bloquée en
-    needs-human (issue #460), sans recréer une nouvelle issue.
+def relancer_issue(depot: str, numero: int, commentaire: str = COMMENTAIRE_RELANCE) -> tuple[str, list]:
+    """Cœur de la relance (issue #460) : retrait du label needs-human + trace
+    en commentaire GitHub — remet une issue en file d'attente sans recréer de
+    nouvelle issue. Factorisée hors de route_relancer() pour être réutilisable
+    hors contexte HTTP (champ RELANCE d'issues_inbox/, issue #516), qui poste
+    un commentaire de trace différent (mentionnant les champs corrigés).
 
     Il n'existe PAS de label « pending » dans ce projet : le watcher
     (watcher.py) traite déjà toute issue OUVERTE for-linux/for-windows tant
     qu'elle ne porte ni `done` ni `needs-human` (voir LABEL_ECHEC/LABEL_FAIT
     dans watcher.py) — retirer needs-human suffit donc à la rendre de nouveau
     éligible au prochain cycle. Ne relance PAS le watcher lui-même (même
-    esprit que route_interrompre ci-dessus : action manuelle séparée si le
-    watcher est éteint)."""
+    esprit que interrompre_linux/interrompre_windows ci-dessus : action
+    manuelle séparée si le watcher est éteint)."""
+    statut_label, msg_label = _retirer_label_gh(depot, numero, LABEL_NEEDS_HUMAN)
+    etapes = [{"etape": "retrait_label_needs_human", "statut": statut_label, "message": msg_label}]
+
+    statut_comment, msg_comment = _commenter_gh(depot, numero, commentaire)
+    etapes.append({"etape": "commentaire", "statut": statut_comment, "message": msg_comment})
+
+    statut_global = "echec" if any(e["statut"] == "echec" for e in etapes) else "ok"
+    return statut_global, etapes
+
+
+def route_relancer():
+    """POST /relancer-issue — remet en file d'attente une issue bloquée en
+    needs-human (issue #460), sans recréer une nouvelle issue. Mince wrapper
+    Flask autour de relancer_issue() ci-dessus, qui porte la logique réelle."""
     data   = request.json or {}
     depot  = (data.get("depot") or "").strip()
     numero = data.get("numero")
# ── Zone modifiée : ligne 463 (11 ligne(s)) dans l'ancienne version → ligne 480 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -463,11 +480,5 @@ def route_relancer():
         return jsonify(succes=False, erreur="Numéro d'issue invalide."), 400
     numero = int(numero)
 
-    statut_label, msg_label = _retirer_label_gh(depot, numero, LABEL_NEEDS_HUMAN)
-    etapes = [{"etape": "retrait_label_needs_human", "statut": statut_label, "message": msg_label}]
-
-    statut_comment, msg_comment = _commenter_gh(depot, numero, COMMENTAIRE_RELANCE)
-    etapes.append({"etape": "commentaire", "statut": statut_comment, "message": msg_comment})
-
-    statut_global = "echec" if any(e["statut"] == "echec" for e in etapes) else "ok"
+    statut_global, etapes = relancer_issue(depot, numero)
     return jsonify(succes=True, statut_global=statut_global, etapes=etapes)
# (diff du fichier suivant)
diff --git a/scripts/watcher_issues_inbox.py b/scripts/watcher_issues_inbox.py
# (index — ignorable)
index f531c8c..cba2205 100644
# (avant — fichier suivant)
--- a/scripts/watcher_issues_inbox.py
# (après — fichier suivant)
+++ b/scripts/watcher_issues_inbox.py
# ── Zone modifiée : ligne 16 (6 ligne(s)) dans l'ancienne version → ligne 16 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -16,6 +16,11 @@ avant création, réutilise app/issues.py::_issue_ouverte_meme_titre() (garde
 du formulaire web, issue #189) pour rejeter un titre déjà porté par une
 issue ouverte du même dépôt.
 
+Champ RELANCE (issue #516) : `| RELANCE | #N |` dans l'en-tête détourne tout
+le bloc vers la correction/relance de l'issue #N déjà ouverte (needs-human
+typiquement) plutôt qu'une création — aucune issue créée, anti-doublon
+court-circuité (il n'a de sens que pour une création). Voir _traiter_relance.
+
 Après création réussie de l'issue, le watcher CCL du projet concerné
 (`watcher.py --config configs/<projet>.conf`) est démarré automatiquement
 s'il n'est pas déjà actif (issue #486, mode « dépose et oublie ») — via
# ── Zone modifiée : ligne 36 (6 ligne(s)) dans l'ancienne version → ligne 41 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -36,6 +41,7 @@ Alain de le créer à la main s'il veut surcharger les défauts.
 """
 
 import argparse
+import json
 import logging
 import os
 import re
# ── Zone modifiée : ligne 55 (6 ligne(s)) dans l'ancienne version → ligne 61 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -55,6 +61,7 @@ from watcher import (charger_config, lire_conf, est_titre_chef,  # noqa: E402
                      LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS)
 from app.watchers import demarrer_watcher  # noqa: E402 (issue #486)
 from app.issues import _issue_ouverte_meme_titre  # noqa: E402 (issue #491)
+from app.interruption import relancer_issue  # noqa: E402 (issue #516)
 
 log = logging.getLogger("watcher_issues_inbox")
 
# ── Zone modifiée : ligne 172 (7 ligne(s)) dans l'ancienne version → ligne 179 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -172,7 +179,10 @@ def retirer_ligne_entete(corps: str, champ: str) -> str:
 
 TITRE_RE = re.compile(r"^#Titre:\s*(.*)$", re.IGNORECASE | re.MULTILINE)
 
-CHAMPS_ENTETE = ("PROJET", "TIMEOUT", "MODELE", "MODE", "LABELS")
+# RELANCE (issue #516) : champ optionnel en cohérence avec SUITE_DE (§6 du
+# DOC) — présent, il détourne tout le bloc du chemin de création habituel
+# vers le chemin de relance d'une issue EXISTANTE (voir _traiter_relance).
+CHAMPS_ENTETE = ("PROJET", "TIMEOUT", "MODELE", "MODE", "LABELS", "RELANCE")
 
 
 def extraire_champs(contenu: str) -> dict:
# ── Zone modifiée : ligne 200 (6 ligne(s)) dans l'ancienne version → ligne 210 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -200,6 +210,7 @@ def extraire_champs(contenu: str) -> dict:
         "modele":       (valeurs["MODELE"] or "").strip(),
         "mode_brut":    valeurs["MODE"],
         "labels_brut":  valeurs["LABELS"],
+        "relance_brut": valeurs["RELANCE"],
         "titre":        titre,
         "corps":        reste.strip("\n"),
     }
# ── Zone modifiée : ligne 295 (6 ligne(s)) dans l'ancienne version → ligne 306 (194 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -295,6 +306,194 @@ def valider(champs: dict):
     return True, "", cfg_projet
 
 
+# ─── RELANCE — corriger/relancer une issue needs-human existante sans repasser
+# par GitHub (issue #516) : le champ `| RELANCE | #N |` détourne un bloc du
+# chemin de création habituel (§3.4, anti-doublon compris — il n'a de sens
+# que pour une CRÉATION) vers un chemin qui cible l'issue #N déjà ouverte,
+# met à jour son corps avec les champs d'en-tête corrigés, retire le label
+# needs-human et poste un commentaire de trace — en réutilisant
+# app.interruption.relancer_issue() (cœur du bouton « 🔄 Relancer », issue
+# #460) plutôt que de dupliquer le retrait de label + la pose du commentaire.
+#
+# Champs corrigibles volontairement limités à TIMEOUT et MODELE : purement
+# textuels dans le corps, sans effet de bord. MODE est exclu (le mode réel
+# est arme par le label GitHub `mode_write`, pas par le texte du corps — le
+# changer sans re-synchroniser ce label serait trompeur, et synchroniser un
+# label qui ARME l'écriture pour CCL depuis ce chemin est jugé hors-scope
+# pour cette première itération) ; LABELS est exclu aussi (il n'apparaît
+# jamais dans le corps — voir construire_body — donc « corriger le corps »
+# n'a pas de sens pour ce champ). RELANCE ne fait que CORRIGER un champ déjà
+# présent dans le corps existant : un champ absent du corps cible reste
+# absent (pas d'insertion de ligne d'en-tête).
+
+RELANCE_RE = re.compile(r"^#?\s*(\d+)\s*$")
+
+COMMENTAIRE_RELANCE_INBOX = "🔄 Relancée via issues_inbox/ (champ RELANCE, issue #516)."
+
+
+def _numero_relance(brut: str | None) -> int | None:
+    if not brut:
+        return None
+    m = RELANCE_RE.match(brut.strip())
+    return int(m.group(1)) if m else None
+
+
+def valider_relance(champs: dict):
+    """Retourne (True, "", cfg_projet, numero) si le bloc RELANCE est
+    exploitable, sinon (False, détail_erreur, None, None). Ne vérifie PAS
+    l'existence/l'ouverture/le dépôt de l'issue ciblée — cf. _recuperer_issue,
+    qui s'en charge via `gh issue view --repo` (échoue déjà si l'issue #N
+    n'appartient pas à ce dépôt)."""
+    if not champs["projet"]:
+        return False, "en-tête malformé : champ PROJET manquant ou vide.", None, None
+
+    chemin_conf = DOSSIER_SCRIPT / "configs" / f"{champs['projet']}.conf"
+    if not chemin_conf.exists():
+        return False, f"projet inconnu : « {champs['projet']} » (configs/{champs['projet']}.conf introuvable).", None, None
+    try:
+        cfg_projet = charger_config(chemin_conf)
+    except SystemExit as e:
+        return False, f"config du projet « {champs['projet']} » invalide : {e}", None, None
+
+    numero = _numero_relance(champs["relance_brut"])
+    if numero is None:
+        return False, f"RELANCE invalide : « {champs['relance_brut']} » (attendu #<numéro>).", None, None
+
+    if champs["modele"] and champs["modele"] not in MODELES_VALIDES:
+        return False, (f"MODELE inconnu : « {champs['modele']} » "
+                        f"(valeurs acceptées : {', '.join(sorted(MODELES_VALIDES))})."), None, None
+
+    if champs["timeout_brut"]:
+        valeur = champs["timeout_brut"].strip().lower().rstrip("s")
+        if not valeur.isdigit():
+            return False, f"TIMEOUT invalide : « {champs['timeout_brut']} » (doit être un nombre).", None, None
+
+    return True, "", cfg_projet, numero
+
+
+def _recuperer_issue(depot: str, numero: int):
+    """(True, "", issue_dict) ou (False, détail_erreur, None). `gh issue view
+    --repo <depot>` échoue déjà si l'issue n'existe pas dans CE dépôt — c'est
+    ce qui couvre la vérification « appartient au bon dépôt/projet » exigée
+    avant toute modification."""
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "view", str(numero), "--repo", depot,
+             "--json", "number,state,body,title"],
+            capture_output=True, text=True, timeout=30,
+        )
+        if res.returncode != 0:
+            detail = (res.stderr or res.stdout or "").strip()
+            return False, detail or f"issue #{numero} introuvable dans {depot}.", None
+        return True, "", json.loads(res.stdout)
+    except subprocess.TimeoutExpired:
+        return False, "timeout (gh n'a pas répondu en 30s).", None
+    except FileNotFoundError:
+        return False, "gh introuvable dans le PATH.", None
+    except (json.JSONDecodeError, OSError) as e:
+        return False, str(e), None
+
+
+def _maj_ligne_entete(corps: str, champ: str, valeur: str) -> str:
+    """Remplace la valeur de `champ` si sa ligne existe déjà dans l'en-tête de
+    `corps` (le corps GitHub EXISTANT de l'issue ciblée, pas le fichier
+    déposé) ; sinon `corps` inchangé — RELANCE corrige un champ déjà présent,
+    jamais n'en insère un nouveau."""
+    m = _regex_champ(champ).search(_zone_entete(corps))
+    if not m:
+        return corps
+    debut_valeur, fin_valeur = m.start(1), m.end(1)
+    return corps[:debut_valeur] + f" {valeur} " + corps[fin_valeur:]
+
+
+def _fusionner_entete(corps_existant: str, champs: dict) -> tuple[str, list]:
+    """Applique au corps existant de l'issue ciblée les champs TIMEOUT/MODELE
+    fournis par le fichier RELANCE. Retourne (nouveau_corps, champs_modifies)
+    — la liste sert à la fois au commentaire de trace et au log."""
+    nouveau = corps_existant
+    modifies = []
+
+    if champs["timeout_brut"]:
+        valeur = f"{int(champs['timeout_brut'].strip().lower().rstrip('s'))}s"
+        avant = nouveau
+        nouveau = _maj_ligne_entete(nouveau, "TIMEOUT", valeur)
+        if nouveau != avant:
+            modifies.append(f"TIMEOUT → {valeur}")
+
+    if champs["modele"]:
+        avant = nouveau
+        nouveau = _maj_ligne_entete(nouveau, "MODELE", champs["modele"])
+        if nouveau != avant:
+            modifies.append(f"MODELE → {champs['modele']}")
+
+    return nouveau, modifies
+
+
+def _modifier_corps_gh(depot: str, numero: int, corps: str) -> tuple[bool, str]:
+    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
+        f.write(corps)
+        chemin_body = f.name
+    try:
+        res = subprocess.run(
+            ["gh", "issue", "edit", str(numero), "--repo", depot, "--body-file", chemin_body],
+            capture_output=True, text=True, timeout=30,
+        )
+        if res.returncode == 0:
+            return True, ""
+        return False, (res.stderr or res.stdout or "erreur gh inconnue").strip()
+    except subprocess.TimeoutExpired:
+        return False, "timeout (gh n'a pas répondu en 30s)."
+    except FileNotFoundError:
+        return False, "gh introuvable dans le PATH."
+    except Exception as e:
+        return False, str(e)
+    finally:
+        Path(chemin_body).unlink(missing_ok=True)
+
+
+def _traiter_relance(cfg: ConfigInbox, champs: dict):
+    """Bloc RELANCE (issue #516) : cible l'issue GitHub #N déjà ouverte au
+    lieu d'en créer une nouvelle. Retourne le même tuple que _traiter_bloc
+    pour une création (succes, titre, projet, texte, resultat_gh) —
+    `resultat_gh` toujours vide ici, RELANCE ne créant jamais d'issue."""
+    ok, detail, cfg_projet, numero = valider_relance(champs)
+    if not ok:
+        return False, champs["titre"] or f"RELANCE {champs['relance_brut']}", champs["projet"], detail, ""
+
+    depot = cfg_projet.depot
+    ok_view, detail_view, issue = _recuperer_issue(depot, numero)
+    if not ok_view:
+        return False, f"#{numero}", champs["projet"], f"issue #{numero} introuvable dans {depot} : {detail_view}", ""
+
+    if (issue.get("state") or "").upper() != "OPEN":
+        return (False, issue.get("title") or f"#{numero}", champs["projet"],
+                f"issue #{numero} n'est pas ouverte (état : {issue.get('state')}).", "")
+
+    corps_existant = issue.get("body") or ""
+    nouveau_corps, modifies = _fusionner_entete(corps_existant, champs)
+
+    if nouveau_corps != corps_existant:
+        ok_edit, detail_edit = _modifier_corps_gh(depot, numero, nouveau_corps)
+        if not ok_edit:
+            return (False, issue.get("title") or f"#{numero}", champs["projet"],
+                    f"mise à jour du corps de #{numero} échouée : {detail_edit}", "")
+
+    commentaire = COMMENTAIRE_RELANCE_INBOX
+    if modifies:
+        commentaire += "\n\nChamps corrigés : " + ", ".join(modifies) + "."
+    if champs["corps"]:
+        commentaire += "\n\n" + champs["corps"]
+
+    statut_global, etapes = relancer_issue(depot, numero, commentaire=commentaire)
+    if statut_global != "ok":
+        detail_erreurs = "; ".join(e["message"] for e in etapes if e["statut"] == "echec")
+        return (False, issue.get("title") or f"#{numero}", champs["projet"],
+                f"relance de #{numero} incomplète : {detail_erreurs}", "")
+
+    suffixe = f" — relance de #{numero}" + (f" ({', '.join(modifies)})" if modifies else "")
+    return True, issue.get("title") or f"#{numero}", champs["projet"], suffixe, ""
+
+
 # ─── Construction body/labels (miroir de app/issues.py::construire_body /
 # construire_labels, pour produire des issues indiscernables de celles créées
 # via le formulaire web) ────────────────────────────────────────────────────
# ── Zone modifiée : ligne 470 (6 ligne(s)) dans l'ancienne version → ligne 669 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -470,6 +669,13 @@ def _traiter_bloc(cfg: ConfigInbox, contenu_bloc: str):
       la sortie de `gh issue create` (URL), pour le seul log console.
     """
     champs = extraire_champs(contenu_bloc)
+
+    # RELANCE (issue #516) : détourne ce bloc vers une issue EXISTANTE avant
+    # toute validation/anti-doublon de création — les deux chemins n'ont rien
+    # en commun (cf. _traiter_relance).
+    if champs["relance_brut"]:
+        return _traiter_relance(cfg, champs)
+
     ok, detail, cfg_projet = valider(champs)
     if not ok:
         return False, champs["titre"], champs["projet"], detail, ""
# (diff du fichier suivant)
diff --git a/tests/test_champ_relance_516.py b/tests/test_champ_relance_516.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..e007036
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_champ_relance_516.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (221 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,221 @@
+#!/usr/bin/env python3
+"""Test de non-régression — issue #516 : champ d'en-tête `| RELANCE | #N |`
+dans `issues_inbox/`, pour corriger/relancer une issue `needs-human` sans
+repasser par une édition manuelle sur GitHub.
+
+Couvre : extraction du champ (`extraire_champs`), parsing du numéro
+(`_numero_relance`), fusion des champs corrigibles dans le corps GitHub
+existant (`_fusionner_entete`/`_maj_ligne_entete` — jamais d'insertion d'une
+ligne absente), et le chemin complet `_traiter_relance` (anti-doublon
+court-circuité, validation dépôt/état, réutilisation de
+`app.interruption.relancer_issue`, coeur du bouton « 🔄 Relancer » #460).
+Tous les appels `gh` sont substitués (aucun accès réseau).
+
+Exécution :  python3 tests/test_champ_relance_516.py
+Sortie      :  code 0 si tous les scénarios passent, 1 sinon.
+"""
+
+import sys
+import tempfile
+from pathlib import Path
+from types import SimpleNamespace
+
+RACINE = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(RACINE))
+sys.path.insert(0, str(RACINE / "scripts"))
+
+import watcher_issues_inbox as w  # noqa: E402
+
+
+def _cfg_projet(depot="AlainDelree/Bridge_Agent", nom="bridge_agent"):
+    return SimpleNamespace(depot=depot, nom=nom, timeout_claude=300, timeout_chef=1200)
+
+
+def _preparer_config_bidon(tmp_dir: Path, projet="bridge_agent"):
+    """Fait pointer DOSSIER_SCRIPT/charger_config vers un projet bidon —
+    évite toute dépendance à un vrai configs/<projet>.conf (gitignoré,
+    absent de ce worktree)."""
+    (tmp_dir / "configs").mkdir(parents=True, exist_ok=True)
+    (tmp_dir / "configs" / f"{projet}.conf").write_text("DEPOT=AlainDelree/Bridge_Agent\n")
+    w.DOSSIER_SCRIPT = tmp_dir
+    w.charger_config = lambda chemin: _cfg_projet()
+
+
+def scenario_1_extraction_champ_relance():
+    """Le champ RELANCE est reconnu comme les autres champs d'en-tête et
+    retiré du corps restant."""
+    contenu = (
+        "| PROJET  | bridge_agent |\n"
+        "| RELANCE | #77 |\n"
+        "| TIMEOUT | 1800s |\n"
+        "\n"
+        "Le TIMEOUT était trop court, la tâche a échoué par dépassement.\n"
+    )
+    champs = w.extraire_champs(contenu)
+    assert champs["relance_brut"] == "#77", champs["relance_brut"]
+    assert champs["timeout_brut"] == "1800s", champs["timeout_brut"]
+    assert "RELANCE" not in champs["corps"], champs["corps"]
+    return {"relance_brut": champs["relance_brut"]}
+
+
+def scenario_2_numero_relance_formats():
+    """_numero_relance tolère « #N », « N », les espaces ; rejette le reste."""
+    assert w._numero_relance("#42") == 42
+    assert w._numero_relance("42") == 42
+    assert w._numero_relance("  # 7 ") == 7  # espaces autour du # et du nombre tolérés
+    assert w._numero_relance("#7") == 7
+    assert w._numero_relance("abc") is None
+    assert w._numero_relance(None) is None
+    assert w._numero_relance("") is None
+    return {}
+
+
+def scenario_3_fusion_entete_corrige_champ_existant():
+    """TIMEOUT/MODELE déjà présents dans le corps GitHub existant sont
+    corrigés ; un champ absent (MODELE ici) n'est jamais inséré."""
+    corps_existant = (
+        "## En-tête\n\n"
+        "| Champ    | Valeur |\n"
+        "|----------|--------|\n"
+        "| SOURCE   | CC |\n"
+        "| TIMEOUT  | 300s |\n"
+        "| PROJET   | bridge_agent |\n\n"
+        "## Contexte\nTexte.\n"
+    )
+    champs = {"timeout_brut": "1800s", "modele": "claude-opus-4-8", "corps": ""}
+    nouveau, modifies = w._fusionner_entete(corps_existant, champs)
+    assert "| TIMEOUT  | 1800s |" in nouveau, nouveau
+    assert "300s" not in nouveau, nouveau
+    assert "MODELE" not in nouveau, "MODELE absent du corps cible ne doit jamais être inséré"
+    assert modifies == ["TIMEOUT → 1800s"], modifies
+    return {"modifies": modifies}
+
+
+def scenario_4_fusion_entete_rien_a_corriger():
+    """Aucun champ TIMEOUT/MODELE fourni → corps inchangé, liste vide."""
+    corps_existant = "| TIMEOUT | 300s |\n"
+    nouveau, modifies = w._fusionner_entete(corps_existant, {"timeout_brut": None, "modele": "", "corps": ""})
+    assert nouveau == corps_existant
+    assert modifies == []
+    return {}
+
+
+def scenario_5_traiter_relance_chemin_complet_succes(tmp_path_factory):
+    """Chemin complet : issue ouverte du bon dépôt, corps mis à jour, puis
+    relancer_issue() (réutilisée telle quelle, pas dupliquée) retire
+    needs-human + poste le commentaire de trace."""
+    tmp_dir = tmp_path_factory()
+    _preparer_config_bidon(tmp_dir)
+
+    appels = {}
+
+    def _fausse_recuperation(depot, numero):
+        appels["depot_view"] = depot
+        appels["numero_view"] = numero
+        return True, "", {
+            "number": numero, "state": "OPEN", "title": "TIMEOUT trop court",
+            "body": "| TIMEOUT | 300s |\n| PROJET | bridge_agent |\n",
+        }
+
+    def _faux_edit_corps(depot, numero, corps):
+        appels["corps_envoye"] = corps
+        return True, ""
+
+    def _faux_relancer(depot, numero, commentaire=""):
+        appels["commentaire"] = commentaire
+        appels["depot_relance"] = depot
+        appels["numero_relance"] = numero
+        return "ok", [{"etape": "retrait_label_needs_human", "statut": "succes", "message": ""},
+                        {"etape": "commentaire", "statut": "succes", "message": ""}]
+
+    w._recuperer_issue = _fausse_recuperation
+    w._modifier_corps_gh = _faux_edit_corps
+    w.relancer_issue = _faux_relancer
+
+    contenu = (
+        "| PROJET  | bridge_agent |\n"
+        "| RELANCE | #77 |\n"
+        "| TIMEOUT | 1800s |\n"
+        "\n"
+        "Le précédent essai a échoué par dépassement de délai.\n"
+    )
+    champs = w.extraire_champs(contenu)
+    succes, titre, projet, texte, resultat_gh = w._traiter_relance(w.ConfigInbox(), champs)
+
+    assert succes, texte
+    assert titre == "TIMEOUT trop court", titre
+    assert projet == "bridge_agent", projet
+    assert resultat_gh == ""
+    assert "#77" in texte, texte
+    assert appels["depot_view"] == "AlainDelree/Bridge_Agent"
+    assert appels["numero_view"] == 77
+    assert "| TIMEOUT | 1800s |" in appels["corps_envoye"], appels["corps_envoye"]
+    assert "TIMEOUT → 1800s" in appels["commentaire"], appels["commentaire"]
+    assert "échoué par dépassement" in appels["commentaire"], appels["commentaire"]
+    assert appels["numero_relance"] == 77
+    return {"texte": texte}
+
+
+def scenario_6_traiter_relance_issue_fermee_rejetee():
+    """Une issue fermée est rejetée avec un motif clair — pas de modification
+    tentée."""
+    def _fausse_recuperation(depot, numero):
+        return True, "", {"number": numero, "state": "CLOSED", "title": "Ancienne tâche", "body": ""}
+
+    w._recuperer_issue = _fausse_recuperation
+
+    contenu = "| PROJET | bridge_agent |\n| RELANCE | #99 |\n"
+    champs = w.extraire_champs(contenu)
+    succes, titre, projet, texte, _ = w._traiter_relance(w.ConfigInbox(), champs)
+    assert not succes
+    assert "n'est pas ouverte" in texte, texte
+    return {"texte": texte}
+
+
+def scenario_7_traiter_relance_numero_invalide_rejete():
+    """RELANCE avec une valeur non numérique est rejeté avant tout appel gh."""
+    contenu = "| PROJET | bridge_agent |\n| RELANCE | pas-un-numero |\n"
+    champs = w.extraire_champs(contenu)
+    succes, titre, projet, texte, _ = w._traiter_relance(w.ConfigInbox(), champs)
+    assert not succes
+    assert "RELANCE invalide" in texte, texte
+    return {"texte": texte}
+
+
+def main():
+    tmp = tempfile.TemporaryDirectory()
+
+    def _tmp_path_factory():
+        return Path(tmp.name)
+
+    tests = [
+        ("champ RELANCE extrait et retiré du corps", scenario_1_extraction_champ_relance),
+        ("_numero_relance tolère #N/N, rejette le reste", scenario_2_numero_relance_formats),
+        ("_fusionner_entete corrige un champ existant, n'en insère jamais", scenario_3_fusion_entete_corrige_champ_existant),
+        ("_fusionner_entete : rien à corriger → corps inchangé", scenario_4_fusion_entete_rien_a_corriger),
+        ("_traiter_relance : chemin complet, succès", lambda: scenario_5_traiter_relance_chemin_complet_succes(_tmp_path_factory)),
+        ("_traiter_relance : issue fermée → rejet", scenario_6_traiter_relance_issue_fermee_rejetee),
+        ("_traiter_relance : RELANCE non numérique → rejet", scenario_7_traiter_relance_numero_invalide_rejete),
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
+    tmp.cleanup()
+    if echecs:
+        print(f"\n❌ {echecs} scénario(s) en échec.")
+        return 1
+    print("\n✅ Tous les scénarios passent.")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
