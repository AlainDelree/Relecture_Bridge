84254a6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 84254a6
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 12:42:32 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #451 : création REINSTALLATION_CCW.md + référence en §16 de BRIDGE_AGENT_DOC.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4e6b2c9..a2d1ecc 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1217 (6 ligne(s)) dans l'ancienne version → ligne 1217 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1217,6 +1217,10 @@ finale.
 principalement les builds `.exe` (PyInstaller) qui exigent un environnement
 Windows natif.
 
+**Réinstallation du PC fixe :** procédure complète (Windows →
+`configurer_ssh_ccw.ps1` → `provisionner.ps1` → tokens → vérification) dans
+`provisioning/windows/REINSTALLATION_CCW.md` (issue #451).
+
 > **⚠️ Changement de plateforme (depuis août 2026, issue #446).** CCW ne
 > tourne plus dans une VM VirtualBox mais **sur un PC fixe physique**
 > (Pentium G2020). De nombreux paragraphes ci-dessous décrivent encore
# (diff du fichier suivant)
diff --git a/CHANGELOG-451.md b/CHANGELOG-451.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..8a27134
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/CHANGELOG-451.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,25 @@
+## 18 août 2026 — issue #451
+
+DOC — nouveau fichier `provisioning/windows/REINSTALLATION_CCW.md` :
+procédure complète de réinstallation du PC fixe CCW, aux côtés des scripts
+qu'elle utilise (`autounattend.xml`, `provisionner.ps1`,
+`mettre_a_jour_tokens_ccw.ps1`), plutôt que dans `BRIDGE_AGENT_DOC.md` qui
+est destiné aux agents CCL/CCW et non à la procédure d'installation
+Windows. Couvre dans l'ordre : réinstallation Windows via
+`autounattend.xml`, configuration SSH (`configurer_ssh_ccw.ps1`),
+vérification de la connexion SSH depuis CCL, provisioning logiciel
+(`provisionner.ps1`), topic ntfy + tokens
+(`mettre_a_jour_tokens_ccw.ps1`), vérification du service `CCW-Watcher`.
+Précise que la clé privée CCL (`~/.ssh/ccl_ccw`) reste sur le ThinkPad
+entre les réinstallations — seule la clé publique est à réinstaller sur le
+nouveau Windows.
+- `BRIDGE_AGENT_DOC.md` : §16 complété d'une ligne de référence vers ce
+  nouveau fichier.
+
+**Point d'attention signalé (pas corrigé, hors périmètre de cette
+issue) :** `configurer_ssh_ccw.ps1`, référencé à l'étape 2 de la
+procédure, n'existe pas dans `provisioning/windows/` au moment de la
+rédaction — il devra être créé (script PowerShell côté Windows qui active
+OpenSSH Server et installe la clé publique fournie dans
+`authorized_keys`) avant que l'étape 2 soit exécutable telle quelle. Une
+note l'indique en bas du nouveau fichier.
# (diff du fichier suivant)
diff --git a/provisioning/windows/REINSTALLATION_CCW.md b/provisioning/windows/REINSTALLATION_CCW.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..298a54e
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/provisioning/windows/REINSTALLATION_CCW.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (94 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,94 @@
+# REINSTALLATION_CCW — réinstallation du PC fixe CCW
+
+Procédure complète pour réinstaller de A à Z le PC fixe Windows dédié à
+l'agent **CCW** (Windows 11 IoT Enterprise LTSC, évaluation 90 jours), sans
+avoir à reconstruire la démarche de mémoire. Les scripts référencés vivent
+tous dans ce même dossier (`provisioning/windows/`). Pour le contexte
+général de l'agent CCW (rôle, architecture, onglet de pilotage), voir
+`BRIDGE_AGENT_DOC.md` §16.
+
+**Rappel important — clé SSH CCL→CCW.** La clé **privée** (`~/.ssh/ccl_ccw`
+sur le ThinkPad, côté CCL) **reste en place** d'une réinstallation à
+l'autre : elle n'a jamais besoin d'être régénérée ni retouchée. Seule sa
+**clé publique** (`~/.ssh/ccl_ccw.pub`) doit être réinstallée sur le
+Windows fraîchement réinstallé (étape 2 ci-dessous), puisque c'est
+`authorized_keys` côté Windows qui est reconstruit à zéro par la
+réinstallation, pas la paire de clés côté CCL.
+
+## Procédure
+
+### 1. Réinstallation Windows
+
+Réinstaller Windows sur le PC fixe en utilisant la réponse d'installation
+automatisée `autounattend.xml` de ce dossier (voir les commentaires en tête
+du fichier pour les valeurs à adapter avant usage, notamment le mot de
+passe administrateur).
+
+### 2. Configurer l'accès SSH depuis CCL
+
+Une fois Windows installé et une session ouverte, lancer **en admin** (PowerShell) :
+
+```powershell
+.\configurer_ssh_ccw.ps1 -ClePub "<contenu de ~/.ssh/ccl_ccw.pub>"
+```
+
+Ce script active/configure OpenSSH Server côté Windows et installe la clé
+publique fournie dans `authorized_keys` de l'utilisateur SSH (`AlainW`),
+pour permettre à CCL de piloter le PC fixe à distance par clé (sans mot de
+passe) — voir `BRIDGE_AGENT_DOC.md` §16.2.
+
+Le contenu à passer en `-ClePub` est celui de `~/.ssh/ccl_ccw.pub` **sur
+le ThinkPad** (CCL) — la clé publique correspondant à la clé privée
+`~/.ssh/ccl_ccw` mentionnée plus haut, qui elle ne bouge pas.
+
+### 3. Vérifier la connexion SSH depuis CCL
+
+Depuis le ThinkPad :
+
+```bash
+ssh -i ~/.ssh/ccl_ccw AlainW@<ip>
+```
+
+(`<ip>` = adresse IP locale du PC fixe.) La connexion doit s'établir sans
+demande de mot de passe. En cas d'échec, revérifier l'étape 2 (OpenSSH
+Server actif, clé bien copiée dans `authorized_keys`) avant de poursuivre.
+
+### 4. Provisionner le logiciel
+
+Toujours en admin sur le PC fixe (ou via la session SSH ouverte à l'étape
+précédente) :
+
+```powershell
+.\provisionner.ps1
+```
+
+Installe Git, GitHub CLI, Python 3, PyInstaller (winget) et Claude Code
+(installeur natif), clone `Bridge_Agent` en lecture seule dans
+`C:\CCW\Bridge_Agent`, écrit `configs\ccw.conf` (avec un placeholder
+`TOPIC_NTFY`) et enregistre le service Windows `CCW-Watcher` via NSSM.
+
+### 5. Renseigner le topic ntfy et poser les tokens
+
+Éditer `TOPIC_NTFY` dans `configs\ccw.conf` (remplacer le placeholder par
+le topic réel), puis lancer :
+
+```powershell
+.\mettre_a_jour_tokens_ccw.ps1
+```
+
+Le script demande `GH_TOKEN` puis `CLAUDE_CODE_OAUTH_TOKEN` en saisie
+masquée, les applique au service via `nssm set … AppEnvironmentExtra`, et
+redémarre `CCW-Watcher`.
+
+### 6. Vérifier que le service tourne
+
+Confirmer que `CCW-Watcher` est bien à l'état `running`, soit localement
+(`nssm status CCW-Watcher` ou services.msc sur le PC fixe), soit depuis
+CCL via l'onglet **CCW** de l'interface web (`new_issue.py`) — voir
+`BRIDGE_AGENT_DOC.md` §16.2.
+
+---
+
+> **Note.** `configurer_ssh_ccw.ps1` est référencé par cette procédure mais
+> n'existe pas encore dans ce dossier au moment de la rédaction — à créer
+> séparément avant de pouvoir dérouler l'étape 2 telle quelle.
