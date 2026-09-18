7dbde90

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7dbde90
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Mon Sep 14 20:14:37 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #542 : allowlist --allowedTools en mode lecture (git fetch/pull --ff-only, Add-Type -AssemblyName)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 120a8aa..80fd646 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 559 (6 ligne(s)) dans l'ancienne version → ligne 559 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -559,6 +559,24 @@ l'issue par ordre de priorité : `mode_write` (écriture) > `mode_scratch`
 **Lecture seule (défaut)** — CCL peut lire, analyser, grep, rapporter.
 Ne peut PAS écrire de fichier ni exécuter de commande modifiant le système.
 Idéal pour : diagnostics, audits, lectures de fichiers, comptages.
+- Ce mode n'a **jamais** `--dangerously-skip-permissions` (contrairement aux
+  deux autres modes ci-dessous) : toute commande hors allowlist Claude Code
+  reste bloquée derrière une demande d'approbation — inatteignable en session
+  non-interactive, donc un échec sûr (fail-safe), pas un blocage à débloquer
+  à l'aveugle.
+- **Allowlist ciblée (`--allowedTools`, issue #542)** : `git fetch` (ne touche
+  jamais l'arbre de travail), `git pull --ff-only` (échoue plutôt que de
+  merger — même opération que le `git pull --ff-only` automatique du watcher
+  en début de cycle sur `REP_TRAVAIL`, §1) et `Add-Type -AssemblyName` côté
+  CCW (charge un assembly .NET nommé depuis le GAC, sans exécuter de code
+  arbitraire — `Add-Type -TypeDefinition`, qui compile du C#, reste bloqué).
+  Ces trois commandes étaient auparavant bloquées par la demande d'approbation
+  interactive de Claude Code, jamais satisfiable en session non-interactive
+  (`claude --print`) — constaté sur CCW lors du diagnostic #541. `git
+  status`/`log`/`diff`/`show` n'ont pas besoin d'être dans cette liste : déjà
+  autorisés sans approbation par l'heuristique interne de Claude Code. Voir
+  `OUTILS_LECTURE_AUTORISES` dans `watcher.py` pour le détail et le
+  raisonnement de chaque entrée.
 
 **Lecture active (`mode_scratch`, issue #327)** — CCL peut écrire, mais
 **UNIQUEMENT** dans un dossier scratch dédié, jamais dans le projet. Utile
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 25290dd..1bc44c6 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (46 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,46 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 14 septembre 2026 — issue #542
+
+Mode lecture bloqué sur des commandes nécessitant une approbation
+interactive impossible en session non-interactive (issue #542, constaté
+sur CCW via l'issue de diagnostic #541 : `git fetch`/`git pull` et
+`Add-Type -AssemblyName ...` refusés par Claude Code avec « This command
+requires approval »). Confirmé dans le code (`lancer_claude`) :
+`MODE_LECTURE` n'a jamais `--dangerously-skip-permissions` (réservé à
+`mode_write`/`mode_scratch`) — reproduit à l'identique sur CCL avec le CLI
+`claude` nu (`git -C ... fetch` bloqué avec le même message), donc bien un
+bug partagé par les deux plateformes (`watcher.py` commun), pas spécifique
+à CCW/Windows.
+
+Plutôt que d'ajouter `--dangerously-skip-permissions` en lecture seule (ce
+qui désarmerait toutes les protections de Claude Code sans le filet de
+sécurité technique dont bénéficie la lecture active, empreinte
+avant/après), ajout d'une allowlist fine via `--allowedTools` — mécanisme
+natif de Claude Code qui débloque des commandes précises sans toucher au
+reste : `git fetch` (jamais d'écriture dans l'arbre de travail),
+`git pull --ff-only` (échoue plutôt que de merger — même opération que le
+`git pull --ff-only` déjà fait automatiquement par le watcher en début de
+cycle sur `REP_TRAVAIL`) et `Add-Type -AssemblyName` côté CCW (charge un
+assembly .NET nommé, sans exécuter de code arbitraire —
+`Add-Type -TypeDefinition`, qui compile du C#, reste volontairement hors
+liste). Nouvelle constante `OUTILS_LECTURE_AUTORISES` dans `watcher.py`,
+ajoutée à `cmd` uniquement en `MODE_LECTURE`. `git status`/`log`/`diff`/
+`show` n'ont pas eu besoin d'y être ajoutés : déjà autorisés sans
+approbation par l'heuristique interne de Claude Code (vérifié).
+
+Vérification de bout en bout via `lancer_claude` en conditions réelles
+(pas seulement `claude --help`) : `git fetch --dry-run` + `git pull
+--ff-only` s'exécutent sans blocage en mode lecture (résultat renvoyé
+normalement) ; une tentative d'écriture hors allowlist (redirection shell
+vers un fichier du projet) reste bloquée par le sandbox, confirmant que le
+périmètre d'écriture de la lecture seule n'a pas été élargi. Le cas
+`Add-Type -AssemblyName` (spécifique PowerShell/CCW) n'a pas pu être
+vérifié en conditions réelles faute d'environnement Windows disponible ici
+— à confirmer côté CCW à l'occasion d'une prochaine tâche PowerShell en
+lecture seule.
+
 ## 13 septembre 2026 — issue #540
 
 Recyclage de la couleur des projets à l'arrêt (`ecole`, `ff_galerie`) vers
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index d21f6be..740fc34 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 175 (6 ligne(s)) dans l'ancienne version → ligne 175 (49 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -175,6 +175,49 @@ MODE_LECTURE        = "lecture"         # défaut : diagnostic, aucune écriture
 MODE_LECTURE_ACTIVE = "lecture_active"  # écriture confinée au scratch (label mode_scratch)
 MODE_ECRITURE       = "ecriture"        # écriture libre dans REP_TRAVAIL (label mode_write)
 
+# ─── Allowlist fine pour MODE_LECTURE (issue #542) ─────────────────────────────
+# Confirmé par test direct du CLI `claude` (sans flag) : `git fetch`/`git pull`
+# (et, sur CCW, `Add-Type -AssemblyName ...` pour charger un assembly .NET) sont
+# bloqués par le système de permissions interactif de Claude Code, qui demande
+# une approbation — impossible à satisfaire en session non-interactive (`--print`,
+# lancée par watcher.py). MODE_LECTURE n'a jamais eu --dangerously-skip-permissions
+# (ce flag est réservé à MODE_ECRITURE/MODE_LECTURE_ACTIVE, cf. lancer_claude) : le
+# désarmer entièrement pour débloquer ces deux commandes désarmerait TOUTES les
+# protections en lecture seule, sans le filet de sécurité technique (empreinte
+# avant/après) dont bénéficie la lecture active — inacceptable.
+#
+# Solution retenue : --allowedTools, mécanisme de Claude Code qui autorise des
+# commandes précises SANS désarmer le reste (toute commande hors de cette liste
+# continue de demander une approbation, donc reste bloquée en session
+# non-interactive — comportement inchangé, fail-safe). Chaque entrée est un
+# préfixe exact de ligne de commande (pas un motif large type "git *") :
+#   - `git fetch`           : ne touche jamais l'arbre de travail (met seulement
+#                              à jour les refs distantes) — read-only par nature.
+#   - `git pull --ff-only`  : échoue si un fast-forward est impossible (jamais de
+#                              merge, jamais de perte de travail local) — même
+#                              opération que le `git pull --ff-only` que
+#                              watcher.py effectue déjà lui-même en début de
+#                              cycle sur REP_TRAVAIL (cf. CONTEXTE.md). `git pull`
+#                              SANS --ff-only reste bloqué (merge/rebase = écriture
+#                              non garantie sans risque).
+#   - `Add-Type -AssemblyName` : charge un assembly .NET nommé depuis le GAC
+#                              (PresentationFramework, System.Windows.Forms, ...) —
+#                              pas d'exécution de code arbitraire. Le préfixe exclut
+#                              volontairement `Add-Type -TypeDefinition`, qui
+#                              compile et exécute du C# arbitraire et doit rester
+#                              soumis à approbation. Spécifique à CCW (PowerShell) ;
+#                              inoffensif à garder aussi côté CCL (jamais invoqué
+#                              sous bash) — non vérifié en conditions réelles sur
+#                              Windows faute d'environnement CCW disponible ici.
+# git status/log/diff/show ne sont volontairement PAS dans cette liste : déjà
+# testés non bloqués par défaut (heuristique interne de Claude Code), donc rien
+# à y ajouter.
+OUTILS_LECTURE_AUTORISES = [
+    "Bash(git fetch:*)",
+    "Bash(git pull --ff-only:*)",
+    "Bash(Add-Type -AssemblyName:*)",
+]
+
 
 def _deduire_mode(labels: list[str]) -> str:
     """Déduit le MODE de traitement (issue #327) des labels GitHub d'une issue.
# ── Zone modifiée : ligne 2378 (6 ligne(s)) dans l'ancienne version → ligne 2421 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2378,6 +2421,12 @@ Si la tâche échoue, remplace ✅ par ❌ et explique la cause en une ligne.
     if mode != MODE_LECTURE:
         cmd.append("--dangerously-skip-permissions")
     cmd.append(prompt)
+    if mode == MODE_LECTURE:
+        # Issue #542 : allowlist fine plutôt que --dangerously-skip-permissions
+        # (voir commentaire sur OUTILS_LECTURE_AUTORISES) — débloque git
+        # fetch/pull --ff-only et le chargement d'assembly .NET sans désarmer le
+        # reste des protections de Claude Code en lecture seule.
+        cmd += ["--allowedTools"] + OUTILS_LECTURE_AUTORISES
 
     # Popen (plutôt que subprocess.run) pour garder la main sur le PID : le
     # nettoyage de l'arbre de process (issue #247, révisé #249) doit
