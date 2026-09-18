60776b3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 60776b3
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 14:43:26 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #550 : cause racine confirmée empiriquement (écart cwd/dossier git réel, pas l'allowlist) ; champ SOUS_DOSSIER pour aligner cwd_effectif sur le sous-projet ciblé côté canal unifié for-windows
    
    Reproduction locale Linux (claude --print, allowedTools identique à watcher.py,
    structure cwd-parent + sous-dossier-cible) : `git -C <sous-dossier> pull --ff-only`
    et `cd <sous-dossier> && git pull --ff-only` sont bloqués par Claude Code avec les
    mêmes messages exacts qu'observés sur CCW/gestionmail (#546/#548), alors que le
    même `git pull --ff-only` bare avec cwd déjà positionné sur le bon dossier réussit.
    Confirme que #546/#549 (allowlist, version CLI) enquêtaient sur le mauvais
    mécanisme.
    
    Ajoute extraire_sous_dossier()/valider_sous_dossier() (calqués sur
    extraire_repo_cible/valider_repo_cible, #125) et le branchement dans
    _traiter_issue_synchrone : quand l'en-tête d'une issue fournit
    `| SOUS_DOSSIER | <chemin relatif> |`, cwd_effectif = REP_TRAVAIL/SOUS_DOSSIER
    (rejeté si absolu, hors REP_TRAVAIL, ou inexistant). Sans objet si worktree isolé
    ou PERIMETRE_DYNAMIQUE déjà actifs ; absent de l'issue = comportement inchangé.
    
    Documente le nouveau champ et le protocole de retest CCW dans BRIDGE_AGENT_DOC.md §16.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1ae7ae2..106aae3 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1715 (6 ligne(s)) dans l'ancienne version → ligne 1715 (50 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1715,6 +1715,50 @@ strict des builds par construction (un seul process `watcher.py` sur ce
 canal, une issue à la fois) et supprime tout risque de contention CPU/RAM
 entre deux builds parallèles.
 
+> **Champ d'en-tête `SOUS_DOSSIER` (issue #550) — cibler un sous-projet du
+> canal unifié sans blocage `git`.** Sur ce canal, `claude` démarrait
+> jusqu'ici TOUJOURS avec pour cwd `REP_TRAVAIL` tout entier
+> (`C:\CCW_Share`), même quand l'issue ne visait qu'un sous-projet précis
+> (ex. `C:\CCW_Share\CCW\gestionmail\`). **Confirmé empiriquement** (issue
+> #550, reproduction locale Linux avec la même structure cwd-parent +
+> sous-dossier-cible) : quand le cwd réel du process diverge du dossier où
+> une commande `git` opère effectivement — atteint via `git -C <chemin>` ou
+> `cd <chemin> &&` —, Claude Code bloque la commande par une demande
+> d'approbation interactive (`This command requires approval`, ou pour la
+> forme `cd && git` : `This command changes directory before running git,
+> which can execute untrusted hooks from the target directory`), **même si
+> son préfixe correspond exactement à une entrée de
+> `OUTILS_LECTURE_AUTORISES`** — `--allowedTools` ne pilote pas ce
+> garde-fou-là. `git pull --ff-only` **bare** (sans `-C` ni `cd`), lancé
+> avec un cwd déjà positionné sur le bon dossier, n'est en revanche PAS
+> bloqué. C'était la cause racine réelle du blocage persistant constaté sur
+> `gestionmail` dans #546/#548/#549 — les correctifs successifs sur
+> l'allowlist (#546) et l'hypothèse de version CLI (#549) portaient sur le
+> mauvais mécanisme.
+>
+> Pour une issue `for-windows` ciblant un sous-projet du canal unifié,
+> ajouter dans l'en-tête un champ optionnel `| SOUS_DOSSIER | CCW\<projet> |`
+> (chemin **relatif** à `REP_TRAVAIL`, jamais absolu — un chemin absolu
+> reste l'usage de `REPO_CIBLE`, §périmètre dynamique). `watcher.py`
+> (`extraire_sous_dossier`/`valider_sous_dossier`) construit alors
+> `cwd_effectif = REP_TRAVAIL / SOUS_DOSSIER` (rejeté si absolu, si la
+> résolution sort de `REP_TRAVAIL` — traversée `..`/lien symbolique —, ou si
+> le dossier n'existe pas ; erreur définitive, `needs-human`, aucun retry) et
+> l'utilise aussi bien comme cwd réel du process que comme périmètre
+> effectif du prompt. Sans objet si le projet est déjà en
+> `PERIMETRE_DYNAMIQUE`/`REPO_CIBLE` (#125) ou si la tâche tourne dans un
+> worktree isolé (#337) — ces deux mécanismes restent seuls décisifs si
+> combinés par erreur. **Absent de l'issue (usage historique, sans
+> sous-projet ciblé) : comportement strictement inchangé**, `cwd_effectif`
+> reste `REP_TRAVAIL`.
+>
+> **Protocole de retest** (à rejouer sur CCW, hors du périmètre Linux de la
+> tâche #550 qui a implémenté ce champ) : ouvrir une issue `for-windows` en
+> mode lecture, en-tête `| SOUS_DOSSIER | CCW\gestionmail |`, corps demandant
+> `git pull --ff-only` dans `C:\CCW_Share\CCW\gestionmail\` — succès attendu
+> sans demande d'approbation, désormais que le cwd du process coïncide avec
+> ce dossier.
+
 > **Ce canal de build coexiste avec le modèle multi-projets (issue #170,
 > actif — voir plus bas dans ce §16).** Des services NSSM **additionnels**
 > `CCW-Watcher-<Projet>` surveillent chacun les issues **directement dans
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 607f4f2..6a3601a 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 1555 (6 ligne(s)) dans l'ancienne version → ligne 1555 (80 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1555,6 +1555,80 @@ def valider_repo_cible(chemin: str) -> tuple[bool, str]:
                        f"(uid propriétaire {proprietaire} ≠ uid watcher {os.getuid()})")
     return True, ""
 
+def extraire_sous_dossier(body: str) -> str:
+    """Extrait le SOUS_DOSSIER depuis le body de l'issue (en-tête bridge, issue
+    #550). Calqué sur extraire_repo_cible/extraire_timeout : cherche une ligne
+    « | SOUS_DOSSIER | <chemin relatif> | » et retourne le chemin tel quel
+    (str), ou "" si le champ est absent ou vide.
+
+    Distinct de REPO_CIBLE (#125, chemin ABSOLU, réservé aux projets
+    PERIMETRE_DYNAMIQUE) : SOUS_DOSSIER est un chemin RELATIF, résolu sous
+    CFG.rep_travail par valider_sous_dossier(), utilisable sur N'IMPORTE QUEL
+    projet sans réglage préalable dans le .conf. Pensé pour le canal unifié
+    for-windows (REP_TRAVAIL = dossier PARENT partagé, ex. C:\\CCW_Share,
+    contenant plusieurs sous-projets dans CCW\\<projet>\\) — voir le
+    commentaire de valider_sous_dossier pour la cause racine que ce champ
+    corrige."""
+    for ligne in body.splitlines():
+        if "| SOUS_DOSSIER" in ligne.upper():
+            parts = ligne.split("|")
+            if len(parts) >= 3:
+                valeur = parts[2].strip()
+                if valeur and valeur.lower() not in ("", "-"):
+                    return valeur
+    return ""
+
+def valider_sous_dossier(rep_travail: Path, sous_dossier: str) -> tuple[bool, str, Path]:
+    """Valide un SOUS_DOSSIER avant tout lancement de Claude Code (issue #550).
+
+    Contexte : sur le canal unifié for-windows (service NSSM `CCW-Watcher` de
+    base, REP_TRAVAIL = C:\\CCW_Share), le process `claude` démarrait
+    jusqu'ici TOUJOURS avec pour cwd REP_TRAVAIL tout entier, même quand
+    l'issue ne visait qu'un sous-projet précis (ex. `C:\\CCW_Share\\CCW\\
+    gestionmail\\`) — confirmé empiriquement (reproduction locale Linux,
+    issue #550) : quand le cwd réel du process diverge du dossier où une
+    commande git opère effectivement (atteint via `git -C <chemin>` ou
+    `cd <chemin> &&`), Claude Code bloque la commande par une demande
+    d'approbation interactive, MÊME si son préfixe correspond exactement à
+    une entrée de OUTILS_LECTURE_AUTORISES — `--allowedTools` ne pilote pas
+    ce garde-fou-là. `git pull --ff-only` bare (sans -C ni cd), lancé avec un
+    cwd déjà positionné sur le bon dossier, n'est en revanche PAS bloqué.
+    SOUS_DOSSIER permet de démarrer directement claude avec le bon cwd,
+    plutôt que de compter sur l'agent pour naviguer lui-même en cours de
+    tâche (ce que la commande git elle-même ne peut pas faire de façon fiable
+    sans -C/cd, précisément ce qui déclenche le blocage).
+
+    Vérifie, dans cet ordre :
+      1. `sous_dossier` n'est pas un chemin absolu (ni racine POSIX '/...' ni
+         lecteur Windows 'C:\\...') — un chemin absolu n'a pas sa place ici,
+         c'est REPO_CIBLE (#125) qu'il faut utiliser dans ce cas ;
+      2. une fois joint à `rep_travail` et résolu, le résultat reste bien
+         SOUS `rep_travail` (Path.relative_to — une séquence '..' ou un lien
+         symbolique qui en sortirait est refusé) ;
+      3. le chemin résolu existe et est un dossier.
+
+    Retourne (True, "", chemin_résolu) si tout passe, sinon (False, raison
+    explicite, Path()) — même logique de refus définitif (pas de retry) que
+    valider_repo_cible. Pas de vérification st_uid ici (indisponible sous
+    Windows, contrairement à valider_repo_cible) : le chemin reste confiné
+    sous rep_travail, qui appartient déjà à l'utilisateur du watcher."""
+    if not sous_dossier:
+        return False, "chemin vide", Path()
+    p = Path(sous_dossier)
+    if p.is_absolute():
+        return False, ("le chemin doit être RELATIF à REP_TRAVAIL — utiliser REPO_CIBLE "
+                       "(projet à PERIMETRE_DYNAMIQUE) pour un chemin absolu"), Path()
+    rep_travail_resolu = rep_travail.resolve()
+    resolu = (rep_travail_resolu / p).resolve()
+    try:
+        resolu.relative_to(rep_travail_resolu)
+    except ValueError:
+        return False, ("le chemin sort de REP_TRAVAIL une fois résolu (séquence '..' ou "
+                       "lien symbolique) — fournir un sous-dossier direct"), Path()
+    if not resolu.is_dir():
+        return False, f"'{resolu}' n'existe pas ou n'est pas un dossier", Path()
+    return True, "", resolu
+
 # ─── Détection de conflit avec un watcher actif (issue #125) ───────────────────
 # Variantes LOCALES de app.projets.lister_projets() et app.watchers.watcher_actif() :
 # app.projets importe watcher — réutiliser ces fonctions ici créerait un import
# ── Zone modifiée : ligne 3248 (6 ligne(s)) dans l'ancienne version → ligne 3322 (38 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3248,6 +3322,38 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
                 f"peuvent être obsolètes.\n\n"
             )
 
+    # SOUS_DOSSIER (issue #550) : cwd du subprocess dérivé d'un sous-dossier
+    # RELATIF sous REP_TRAVAIL — pour le canal unifié for-windows, où
+    # REP_TRAVAIL désigne un dossier PARENT partagé (ex. C:\CCW_Share) et non
+    # le sous-projet réellement visé par l'issue (ex. CCW\gestionmail). Voir
+    # le commentaire de valider_sous_dossier pour la cause racine (écart
+    # cwd/dossier git réel) que ce champ corrige. Sans objet si un worktree
+    # isolé ou un périmètre dynamique (REPO_CIBLE) sont déjà actifs pour
+    # cette tâche : ces deux mécanismes fixent déjà cwd_effectif eux-mêmes et
+    # restent seuls décisifs si combinés par erreur avec SOUS_DOSSIER — même
+    # esprit que la priorité worktree/REPO_CIBLE déjà en place ci-dessus.
+    # Absent de l'issue (usage historique, sans sous-projet ciblé) :
+    # cwd_effectif reste CFG.rep_travail, comportement strictement inchangé.
+    if chemin_worktree is None and not CFG.perimetre_dynamique:
+        sous_dossier = extraire_sous_dossier(body)
+        if sous_dossier:
+            valide, raison, chemin_resolu = valider_sous_dossier(CFG.rep_travail, sous_dossier)
+            if not valide:
+                log.error(f"  Issue #{numero} : SOUS_DOSSIER refusé ({raison}) — abandon, aucun lancement de Claude Code.")
+                commenter_issue(
+                    numero,
+                    f"❌ `SOUS_DOSSIER` refusé — `{sous_dossier}` : {raison}.\n\n"
+                    f"Aucun lancement de Claude Code (erreur de configuration/issue, pas un "
+                    f"échec transitoire). Corrigez le champ `SOUS_DOSSIER` puis retirez le "
+                    f"label `{LABEL_ECHEC}` pour relancer."
+                )
+                ajouter_label(numero, LABEL_ECHEC)
+                _issues_en_cours_retirer(numero)
+                return
+            cwd_effectif       = chemin_resolu
+            perimetre_effectif = str(chemin_resolu)
+            log.info(f"  SOUS_DOSSIER : cwd de cette exécution = {chemin_resolu} (issue #550).")
+
     # Garde-fou anti-collision inter-process (issue #189) : AVANT l'ACK et tout
     # lancement de claude, on pose un verrou exclusif sur le répertoire de travail
     # effectif. Si un AUTRE process (autre instance/relance de watcher, ou un
