b3472f8

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b3472f8
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 11:27:14 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #448 : BRIDGE_AGENT_DOC.md §16.2 mis à jour pour CCW sur SSH (post #447)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ba7b43c..4e6b2c9 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1565 (66 ligne(s)) dans l'ancienne version → ligne 1565 (71 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1565,66 +1565,71 @@ la VM (`creer_vm_ccw.py --recreate` + ré-attacher un ISO frais +
 `lancer_provisioning.py`) → renouveler les tokens
 (`mettre_a_jour_tokens_ccw.ps1`) → mettre à jour `eval-expiration.json`.
 
-### 16.2 Onglet « CCW » de l'interface web (issue #174)
-
-> **⚠️ Partiellement obsolète (PC physique, issue #446).** Tout ce qui repose
-> sur `VBoxManage guestcontrol` — démarrer la VM, pousser/exécuter des
-> scripts à distance (points 1, 2, 3, 4 ci-dessous) — est **inopérant** sur
-> un PC physique : il n'y a plus de VM à piloter. L'onglet reste décrit
-> ci-dessous tel qu'il a été conçu (utile pour comprendre le pattern de
-> pose sécurisée des tokens, §16.2 « Sécurité des tokens »), en attendant
-> une **refonte** adaptée au nouveau contexte (pilotage d'un service NSSM
-> sur un PC physique, sans VM à démarrer ni à interroger via
-> `guestcontrol`).
-
-**Rôle.** Piloter CCW (la VM et ses projets) **entièrement depuis Linux**, via
-l'onglet **CCW** de `new_issue.py` — même style que les autres onglets. Il
-**remplace l'usage manuel de PowerShell dans la VM** pour les opérations
-courantes : plus besoin d'ouvrir une console PowerShell dans la fenêtre de la VM
-ni de copier-coller hôte↔VM (source d'erreurs récurrentes). Les scripts
-PowerShell existants restent l'**implémentation sous-jacente** : l'onglet les
-pousse et les exécute à distance via `VBoxManage guestcontrol` (pattern
-`copyto` + `run` de `lancer_provisioning.py`). Côté serveur, toute la logique
-vit dans `app/ccw.py` (routes `/ccw/*`).
+### 16.2 Onglet « CCW » de l'interface web (issue #174, SSH depuis #447)
+
+**Rôle.** Piloter CCW (le PC fixe physique et ses projets) **entièrement
+depuis Linux**, via l'onglet **CCW** de `new_issue.py` — même style que les
+autres onglets. Il **remplace l'usage manuel de PowerShell sur le PC** pour
+les opérations courantes : plus besoin d'ouvrir une console PowerShell sur le
+PC fixe ni de copier-coller hôte↔PC (source d'erreurs récurrentes). Les
+scripts PowerShell existants restent l'**implémentation sous-jacente** :
+l'onglet les pousse et les exécute à distance via **SSH/SCP** (copie par
+`scp`, exécution par `ssh ... powershell.exe -File`). Côté serveur, toute la
+logique vit dans `app/ccw.py` (routes `/ccw/*`).
 
 **Ce que fait l'onglet :**
 
-1. **VM CCW-Build** — affiche son état (`running`/`poweroff`/`saved`, même
-   `VMState` que `demarrer_ccw.sh`) et, si arrêtée, un bouton **Démarrer
-   (headless)** (qui appelle `demarrer_ccw.sh`).
-2. **Projets CCW existants** — liste les services `CCW-Watcher*` de la VM
-   (via `lister_projets_ccw.ps1`, exécuté à distance) : nom du projet, service,
-   état (`running`/`stopped`) et indicateur si `TOPIC_NTFY` est encore un
-   placeholder. **Rafraîchi à la demande** (pas de polling : chaque appel
-   déclenche un `guestcontrol`).
-3. **Ajouter un projet** — champs *nom* + *dépôt owner/repo*, bouton **Créer**
-   qui exécute `ajouter_projet_ccw.ps1` à distance (clone + config + service) et
-   affiche sa sortie.
-4. **Finaliser un projet** — champs *projet* (ou sélection dans la liste du
-   point 2), `TOPIC_NTFY`, `GH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`. Bouton
+1. **Projets CCW existants** — liste les services `CCW-Watcher*` du PC fixe
+   (via `lister_projets_ccw.ps1`, poussé puis exécuté à distance par SSH) :
+   nom du projet, service, état (`running`/`stopped`) et indicateur si
+   `TOPIC_NTFY` est encore un placeholder. **Rafraîchi à la demande** (pas de
+   polling : chaque appel déclenche un aller-retour SSH complet).
+2. **Ajouter un projet** — champs *nom* + *dépôt owner/repo*, bouton **Créer**
+   qui pousse puis exécute `ajouter_projet_ccw.ps1` à distance (clone +
+   config + service) et affiche sa sortie.
+3. **Finaliser un projet** — champs *projet* (ou sélection dans la liste du
+   point 1), `TOPIC_NTFY`, `GH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`. Bouton
    **Finaliser** qui écrit le topic **et** pose les deux tokens en enchaînant,
    puis redémarre le service et affiche les dernières lignes de log
    (via `finaliser_projet_ccw_auto.ps1`).
+4. **Démarrer / arrêter / redémarrer un service** — actions indépendantes
+   pilotant le service NSSM d'un projet (`nssm start|stop|restart <service>`,
+   exécuté à distance), sans toucher au topic ni aux tokens (issues #180,
+   #203). Le nom exact du service est résolu via `lister_projets_ccw.ps1`
+   (source de vérité unique — gère notamment le cas spécial
+   `Bridge_Agent` → service `CCW-Watcher` sans suffixe).
+5. **Nettoyer verrous CCW** — bouton « 🔒 Nettoyer verrous CCW + redémarrer »
+   (issue #431) : arrête le service, supprime les `.lock` orphelins du
+   dossier de verrous du projet, puis relance le service, en un seul
+   aller-retour SSH (via `nettoyer_verrous_ccw.ps1`).
+
+**Configuration SSH.** Lue au moment de l'action (jamais codée en dur), par
+ordre de priorité pour chaque valeur — variable d'environnement d'abord,
+sinon fichier local `configs/ccw_ssh.conf` (gitignoré, comme les
+`configs/*.conf`, format « CLÉ = valeur ») :
+
+1. hôte du PC fixe (IP ou nom réseau local) : `CCW_SSH_HOTE` / `HOTE` ;
+2. utilisateur SSH : `CCW_SSH_UTILISATEUR` / `UTILISATEUR` (défaut `AlainW`) ;
+3. chemin de la clé privée SSH sur CCL : `CCW_SSH_CLE_PRIVEE` / `CLE_PRIVEE`.
+
+Prérequis manuels (hors périmètre de ce code) : OpenSSH Server activé sur le
+PC fixe, clé publique installée dans `authorized_keys` de l'utilisateur SSH.
+Authentification **par clé uniquement** (`BatchMode=yes` — jamais de prompt
+interactif, un serveur web ne peut pas répondre à un mot de passe),
+acceptation silencieuse d'une nouvelle clé d'hôte (`StrictHostKeyChecking=
+accept-new`, réseau local de confiance), délai de connexion court
+(`ConnectTimeout=10`) pour échouer vite si le PC est injoignable.
+Configuration absente/incomplète → l'onglet affiche un message clair, aucune
+erreur Flask brute. Toute erreur SSH/SCP (PC éteint ou injoignable, timeout,
+script distant en échec) remonte de la même façon un message lisible dans
+l'interface.
 
 **Sécurité des tokens (impératif).** Les tokens ne transitent **jamais** en
-argument de ligne de commande vers `guestcontrol` (invisibles dans les
-process/event logs Windows) et ne sont **jamais journalisés** côté Linux. Ils
-sont écrits dans un **fichier temporaire local à permissions `0600`**, poussé
-dans la VM via `copyto`, lu côté VM par PowerShell (`-FichierTokens`), puis
-supprimé des **deux côtés** dans un `finally` (Python côté hôte, PowerShell côté
-VM) — exactement le pattern du mot de passe `ccw-admin`.
-
-**Mot de passe `ccw-admin` (côté serveur).** Jamais demandé à chaque action ni
-codé en dur. `app/ccw.py` le lit, à l'action, par ordre de priorité :
-
-1. variable d'environnement **`CCW_ADMIN_PASSWORD`** (cohérent avec
-   `lancer_provisioning.py`) — l'exporter avant de lancer `new_issue.py` ;
-2. sinon fichier local **`configs/ccw_admin.secret`** (gitignoré, comme les
-   `configs/*.conf`), dont la première ligne est le mot de passe.
-
-Absent des deux → l'onglet affiche un message clair, aucune erreur Flask brute.
-Toute erreur `guestcontrol` (VM éteinte, timeout, script distant en échec)
-remonte de la même façon un message lisible dans l'interface.
+argument de ligne de commande (invisibles dans les process/event logs
+Windows) et ne sont **jamais journalisés** côté Linux. Ils sont écrits dans
+un **fichier temporaire local à permissions `0600`**, poussé sur le PC fixe
+via `scp`, lu côté PC par PowerShell (`-FichierValeurs`), puis supprimé des
+**deux côtés** dans un `finally` (Python côté hôte, PowerShell côté PC).
 
 ### 16.3 Procédure — builder un projet Windows
 
