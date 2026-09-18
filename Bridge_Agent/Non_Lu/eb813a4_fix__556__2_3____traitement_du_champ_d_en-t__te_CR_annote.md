eb813a4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit eb813a4
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 16:49:32 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #556 (2/3) : traitement du champ d'en-tête CREATION dans watcher.py —
    bootstrap automatique d'un service CCW dédié
    
    Ajoute à watcher.py la détection précoce de `| CREATION | oui |` (avant tout
    lancement de claude, décision #554 §2.5 : jamais d'invocation de claude pour
    cette opération), l'extraction des 6 champs CREATION_* (nom, dépôt, topic
    ntfy, 2 tokens chiffrés base64/RSA-OAEP-SHA256), le déchiffrement via
    openssl (résolution robuste du chemin, point d'attention #557), le retrait
    immédiat des tokens du corps GitHub (§2.4 de #554), et l'appel séquentiel de
    ajouter_projet_ccw.ps1 puis finaliser_projet_ccw_auto.ps1 -FichierValeurs
    (format vérifié par lecture du script, identique à celui déjà produit par
    app/ccw.py) — compte-rendu + fermeture si succès, needs-human + log complet
    si échec.
    
    Test sans vraie issue GitHub ni machine CCW réelle
    (tests/test_creation_bootstrap_ccw_556.py, 15 scénarios, déchiffrement RÉEL
    via openssl local), et convention documentée dans BRIDGE_AGENT_DOC.md §16.6
    pour le formulaire web à venir (3/3, non traité ici).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 106aae3..f94ca48 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 2368 (6 ligne(s)) dans l'ancienne version → ligne 2368 (145 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2368,6 +2368,145 @@ et avoir `claude setup-token` prêt à lancer pour générer le second token.
 Le script s'arrête (code de sortie 1) et invite à vérifier/recréer le
 token concerné si l'un des deux manque ou échoue au test à blanc.
 
+### 16.6 Bootstrap automatique via le champ `CREATION` (issues #554/#556, 2/3)
+
+**But.** Créer un service CCW dédié **de bout en bout à partir d'une seule
+issue GitHub**, sans aucune session `claude` (décision #554 §2.5) : les
+scripts PowerShell déjà testés en §16.5/tableau de provisioning
+(`ajouter_projet_ccw.ps1` puis `finaliser_projet_ccw_auto.ps1
+-FichierValeurs`) sont appelés directement par `watcher.py`, en Python
+déterministe. Le problème résolu est la transmission **asynchrone** de
+`GH_TOKEN`/`CLAUDE_CODE_OAUTH_TOKEN` : le PC CCW peut être éteint au moment
+où l'issue est créée, donc les tokens ne peuvent pas transiter en clair —
+d'où le chiffrement asymétrique avec la paire de clés de bootstrap générée
+par `provisionner.ps1` (issue #554, 1/3, `C:\CCW\cles_bootstrap\`).
+
+**Détection et traitement (`watcher.py`, issue #556).** `_traiter_issue_
+synchrone` détecte le champ `| CREATION | oui |` **tôt dans le dispatch**,
+juste après la garde d'idempotence habituelle et AVANT tout ce qui touche au
+pipeline `lancer_claude` (mode, périmètre, verrou) — `creation_demandee(body)`
+→ délégation complète à `_traiter_creation_projet_ccw`, qui gère seule tout
+le cycle de vie de l'issue (aucun retour au dispatch normal). Sans objet sur
+n'importe quel autre canal/projet : en pratique n'a de sens que posté sur le
+dépôt `AlainDelree/Bridge_Agent` avec le label `for-windows` (canal unifié,
+service `CCW-Watcher`, seul habilité à écrire les 4 services concernés —
+chicken-and-egg sinon : le nouveau projet n'a par définition pas encore de
+token pour recevoir sa propre issue de bootstrap).
+
+**Format attendu du corps de l'issue.** Six champs dans le tableau d'en-tête
+(en plus des champs standards SOURCE/DEST/…, §6) :
+
+```markdown
+| CREATION              | oui |
+| CREATION_NOM_PROJET   | <NomProjet> |
+| CREATION_DEPOT        | <owner/repo> |
+| CREATION_TOPIC_NTFY   | <topic ntfy dédié> |
+| CREATION_GH_TOKEN     | <token GH_TOKEN chiffré, base64> |
+| CREATION_OAUTH_TOKEN  | <token CLAUDE_CODE_OAUTH_TOKEN chiffré, base64> |
+```
+
+- `CREATION` : déclencheur. Valeurs actives reconnues : `oui`/`true`/`vrai`
+  (insensible à la casse) ; absent ou toute autre valeur → dispatch normal
+  inchangé (comportement historique, aucun risque de régression).
+- `CREATION_NOM_PROJET` / `CREATION_DEPOT` : passés **tels quels** à
+  `ajouter_projet_ccw.ps1 -NomProjet -Depot` (même validation qu'un appel
+  manuel — nom sans espace, dépôt au format `owner/repo`).
+- `CREATION_TOPIC_NTFY` : passé tel quel dans le fichier de valeurs
+  (`TOPIC_NTFY=`, voir plus bas).
+- `CREATION_GH_TOKEN` / `CREATION_OAUTH_TOKEN` : les deux tokens, **chiffrés
+  individuellement** avec la clé PUBLIQUE de bootstrap (`bootstrap_publique.
+  pem`, récupérée depuis CCW — cf. §554 1/3), puis encodés en base64 **sur
+  une seule ligne** (`base64 -w0` ou équivalent — indispensable pour tenir
+  dans une cellule de tableau markdown). Convention de chiffrement, à
+  respecter EXACTEMENT côté formulaire (issue à venir, 3/3) :
+
+  ```bash
+  # Une seule fois : récupérer bootstrap_publique.pem depuis CCW (§554 1/3).
+  echo -n "<token en clair>" | openssl pkeyutl -encrypt \
+      -pubin -inkey bootstrap_publique.pem \
+      -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 \
+      -out token.bin
+  base64 -w0 token.bin        # → valeur du champ CREATION_GH_TOKEN/CREATION_OAUTH_TOKEN
+  ```
+
+  **Padding OAEP/SHA-256 impératif des deux côtés** (chiffrement côté
+  formulaire, déchiffrement côté `watcher.py`/`dechiffrer_token_bootstrap`)
+  — propriété volontaire d'OAEP : un mauvais padding fait **échouer**
+  `openssl pkeyutl -decrypt` plutôt que de réussir silencieusement avec un
+  résultat corrompu, contrairement au padding PKCS#1 v1.5 historique
+  (`RSA genpkey`/`rsa_keygen_bits:3072`, issue #554 — la taille de clé
+  n'impose aucune contrainte de padding, choisi indépendamment ici).
+
+**Comportement précis de `watcher.py` (issue #556).**
+
+1. Extraction des 6 champs (`extraire_champs_creation`) ; un seul manquant
+   → échec **définitif** immédiat (`needs-human`, aucun retry, aucun script
+   PowerShell ni déchiffrement tenté) — erreur de configuration/issue, pas
+   un échec transitoire, même logique que `REPO_CIBLE`/`SOUS_DOSSIER`.
+2. **Retrait immédiat** des deux tokens chiffrés du corps GitHub
+   (`gh issue edit --body-file`, remplacés par `<retiré après application>`)
+   — AVANT même la tentative de déchiffrement, dès que les valeurs sont en
+   mémoire : limite le temps d'exposition résiduel (§2.4 de #554).
+   Best-effort (un échec ici ne bloque pas le bootstrap, juste journalisé).
+3. Résolution robuste du chemin `openssl` (`_resoudre_openssl`) : PATH →
+   installation manuelle Windows documentée en #557
+   (`C:\Program Files\OpenSSL-Win64\bin\openssl.exe`, **pas** sur le PATH par
+   défaut sur CCW) → repli `usr\bin` de Git pour Windows (même binaire que
+   celui utilisé par `provisionner.ps1` pour la GÉNÉRATION des clés,
+   `Resoudre-OpenSSL` côté PowerShell — dupliqué en Python plutôt que
+   dot-sourcé, cette fonction n'ayant besoin que d'un chemin).
+4. Déchiffrement des deux tokens avec `C:\CCW\cles_bootstrap\bootstrap_
+   privee.pem` (chemin dérivé de `DOSSIER_SCRIPT.parent` — jamais un
+   `C:\CCW` en dur — puisque `watcher.py` vit toujours dans
+   `<RepCCW>\Bridge_Agent`, cf. plus haut dans ce §16).
+5. Écriture d'un fichier temporaire « clé=valeur » **au format EXACT** déjà
+   lu par `finaliser_projet_ccw_auto.ps1 -FichierValeurs` (vérifié en lisant
+   le script avant d'écrire ce code — identique à celui déjà produit par
+   `app/ccw.py`, `ccw_finaliser_projet`) : trois lignes `TOPIC_NTFY=`/
+   `GH_TOKEN=`/`CLAUDE_CODE_OAUTH_TOKEN=`, UTF-8, **aucun espace autour du
+   `=`** (`Lire-ValeurFichier` côté PowerShell ne rogne que la clé, pas la
+   valeur).
+6. Appel séquentiel `ajouter_projet_ccw.ps1 -NomProjet -Depot` puis
+   `finaliser_projet_ccw_auto.ps1 -NomProjet -FichierValeurs` (PowerShell
+   **local** — `watcher.py` tourne déjà sur la machine CCW cible,
+   contrairement à l'onglet CCW de l'interface web qui pilote la même paire
+   de scripts à distance via SSH, `app/ccw.py`). Sortie complète des deux
+   scripts capturée pour le compte-rendu.
+7. Suppression du fichier de valeurs en deux lignes de défense : le
+   `finally` PowerShell de `finaliser_projet_ccw_auto.ps1` (déjà en place),
+   PUIS un nettoyage Python en repli (couvre le cas où le script n'a jamais
+   démarré ou a planté avant son propre `finally`) — même prudence que
+   `app/ccw.py`.
+8. Selon le résultat : commentaire de compte-rendu (log complet des deux
+   scripts en accordéon `<details>`) + fermeture de l'issue si succès (codes
+   0 et 2 — 2 = tokens appliqués mais vérification finale non concluante,
+   signalé en avertissement, pas un échec), ou `needs-human` + log complet
+   en commentaire si échec (code ≠ 0/2, timeout, script introuvable, erreur
+   de déchiffrement…).
+
+**Sans objet pour l'agent Linux (CCL).** `_traiter_creation_projet_ccw`
+vérifie `platform.system() == "Windows"` avant toute tentative réelle
+(scripts PowerShell inexistants sur CCL) — échec propre et explicite
+(`needs-human`) plutôt qu'une exception si le champ apparaissait par erreur
+sur un canal `for-linux`.
+
+**Test sans vraie issue GitHub ni machine CCW réelle** (sur le modèle du
+test unitaire `SOUS_DOSSIER` de #550) :
+`tests/test_creation_bootstrap_ccw_556.py` — extraction/détection des
+champs, non-collision `CREATION`/`CREATION_NOM_PROJET` (préfixe partagé),
+retrait des tokens du corps, résolution `openssl` (3 replis), chiffrement/
+déchiffrement RÉEL via un openssl local, chemin complet de
+`_traiter_creation_projet_ccw` (succès/champ manquant/dry-run, faux `gh` et
+faux `powershell` sur le `PATH`), et un scénario bout en bout via
+`traiter_issue` vérifiant qu'un faux `claude` marqueur n'est **jamais**
+touché.
+
+**Reste à faire (issue 3/3, #559 ou suivant, hors périmètre de #556) :** le
+formulaire web qui génère automatiquement ces 6 champs (récupération de
+`bootstrap_publique.pem`, chiffrement des deux tokens, remplissage du
+corps) — cette issue a été testée avec une issue `for-windows` créée à la
+main, sans attendre le formulaire.
+
 ---
 
 ## 17. Notifications centralisées — détection serveur des transitions (issue #187)
# (diff du fichier suivant)
diff --git a/CHANGELOG-556.md b/CHANGELOG-556.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..63769da
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/CHANGELOG-556.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (57 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,57 @@
+# CHANGELOG-556 — entrées à fusionner dans CHANGELOG.md
+
+## 15 septembre 2026 — issue #556 (2/3)
+
+Traitement du champ d'en-tête `CREATION` dans `watcher.py` — bootstrap
+automatique d'un service CCW dédié, suite de la conception validée en #554
+et de la génération de la paire de clés RSA 3072 (#554 1/3) : ENTIÈREMENT
+déterministe, n'invoque JAMAIS `claude` (décision #554 §2.5) — réutilise
+directement les scripts PowerShell déjà testés (`ajouter_projet_ccw.ps1`
+puis `finaliser_projet_ccw_auto.ps1 -FichierValeurs`, format vérifié par
+lecture du script avant écriture du code, identique à celui déjà produit
+par `app/ccw.py`).
+
+`_traiter_issue_synchrone` détecte `| CREATION | oui |` tôt dans le
+dispatch, AVANT tout ce qui touche au pipeline `lancer_claude`. Convention
+de 6 champs d'en-tête proposée et documentée (`CREATION`,
+`CREATION_NOM_PROJET`, `CREATION_DEPOT`, `CREATION_TOPIC_NTFY`,
+`CREATION_GH_TOKEN`, `CREATION_OAUTH_TOKEN`) : les deux tokens transitent
+chiffrés individuellement (RSA/OAEP-SHA256 via `openssl pkeyutl -encrypt`,
+clé publique de bootstrap) puis encodés en base64 sur une seule ligne.
+`_extraire_champ_entete` compare le nom de champ EXACTEMENT (pas une
+sous-chaîne comme les extracteurs existants SOUS_DOSSIER/REPO_CIBLE) : évite
+la collision entre `CREATION` et son propre préfixe partagé avec
+`CREATION_NOM_PROJET`/etc.
+
+Résolution robuste du chemin `openssl` (`_resoudre_openssl`, point
+d'attention hérité de #557 puisque #558 n'était pas encore mergé au moment
+de cette tâche) : PATH → installation manuelle Windows
+(`C:\Program Files\OpenSSL-Win64\bin\openssl.exe`, pas sur le PATH par
+défaut sur CCW) → repli `usr\bin` de Git pour Windows — dupliqué en Python
+plutôt que réutilisé depuis `Resoudre-OpenSSL` côté PowerShell
+(`provisionner.ps1`, #554) : pas de dot-sourcing PowerShell depuis Python,
+et un simple calcul de chemin ne justifie pas d'exécuter un script externe.
+
+Retrait immédiat des deux tokens chiffrés du corps GitHub (`gh issue edit
+--body-file`, remplacés par `<retiré après application>`) DÈS que les
+valeurs sont en mémoire — avant même la tentative de déchiffrement — pour
+limiter le temps d'exposition résiduel (§2.4 de #554). Fichier de valeurs
+temporaire supprimé en deux lignes de défense (le `finally` PowerShell déjà
+en place côté `finaliser_projet_ccw_auto.ps1`, PUIS un nettoyage Python en
+repli). Compte-rendu + fermeture si succès (codes 0/2), `needs-human` + log
+complet en commentaire si échec — un champ manquant est traité comme une
+erreur de configuration définitive (aucun script PowerShell ni
+déchiffrement tenté).
+
+Testé sans vraie issue GitHub ni machine CCW réelle (sur le modèle du test
+`SOUS_DOSSIER` de #550) : `tests/test_creation_bootstrap_ccw_556.py`, 15
+scénarios — extraction/détection, non-collision `CREATION`/
+`CREATION_NOM_PROJET`, retrait des tokens, résolution `openssl` (3 replis),
+chiffrement/déchiffrement RÉEL via un openssl local (RSA 3072 généré à la
+volée), chemin complet succès/champ manquant/dry-run (faux `gh` et faux
+`powershell` sur le `PATH`), et un scénario bout en bout via `traiter_issue`
+vérifiant qu'un faux `claude` marqueur n'est jamais touché.
+
+Documenté en détail dans `BRIDGE_AGENT_DOC.md` §16.6 (nouvelle
+sous-section), à l'intention du formulaire web à venir (3/3, #559 ou
+suivant — non traité ici, `new_issue.py` non touché).
# (diff du fichier suivant)
diff --git a/tests/test_creation_bootstrap_ccw_556.py b/tests/test_creation_bootstrap_ccw_556.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..16082ad
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_creation_bootstrap_ccw_556.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (660 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,660 @@
+#!/usr/bin/env python3
+"""Test de non-régression — issue #556 (2/3) : traitement du champ d'en-tête
+`CREATION` dans watcher.py — bootstrap automatique d'un service CCW dédié.
+
+Couvre, SANS vraie issue GitHub ni vraie machine CCW (sur le modèle du test
+unitaire SOUS_DOSSIER de #550) :
+- extraction/détection des champs CREATION/CREATION_* (`creation_demandee`,
+  `extraire_champs_creation`), y compris la non-collision entre `CREATION` et
+  `CREATION_NOM_PROJET`/... (préfixe partagé) ;
+- retrait des 2 tokens chiffrés du corps (`_corps_avec_tokens_retires`) ;
+- résolution robuste du chemin openssl (`_resoudre_openssl`) : PATH, repli
+  installation manuelle Windows (#557), repli usr\\bin de Git, échec propre ;
+- chiffrement/déchiffrement réel via openssl local (RSA 3072 + OAEP/SHA-256,
+  convention documentée en BRIDGE_AGENT_DOC.md §16) — `dechiffrer_token_bootstrap` ;
+- le chemin complet `_traiter_creation_projet_ccw` : succès (2 scripts
+  PowerShell appelés dans l'ordre, avec les bons arguments, fichier de
+  valeurs au format attendu par finaliser_projet_ccw_auto.ps1, tokens
+  redirigés du corps GitHub, commentaire + fermeture), échec (champ manquant
+  → needs-human, sans toucher à openssl/PowerShell), dry-run (simulé, aucun
+  script exécuté) ;
+- le dispatch dans `traiter_issue` : une issue CREATION ne lance JAMAIS
+  `claude` (décision #554 §2.5) — vérifié en observant qu'un faux `claude`
+  marqueur n'est jamais touché.
+
+`gh` et `powershell` sont remplacés par de faux exécutables (même technique
+que tests/test_lecture_active_327.py) : aucun accès réseau ni machine
+Windows réelle. `platform.system` est monkeypatché pour simuler CCW.
+
+Exécution :  python3 tests/test_creation_bootstrap_ccw_556.py
+Sortie      :  code 0 si tous les scénarios passent, 1 sinon.
+"""
+
+import base64
+import os
+import stat
+import subprocess
+import sys
+import tempfile
+from pathlib import Path
+
+RACINE = Path(__file__).resolve().parent.parent
+sys.path.insert(0, str(RACINE))
+
+import watcher  # noqa: E402
+
+
+# ─── Aides crypto (openssl réel, disponible sur CCL) ────────────────────────
+
+def _generer_paire_cles(tmp: Path) -> tuple[Path, Path]:
+    tmp.mkdir(parents=True, exist_ok=True)
+    priv = tmp / "bootstrap_privee.pem"
+    pub = tmp / "bootstrap_publique.pem"
+    subprocess.run(["openssl", "genpkey", "-algorithm", "RSA",
+                     "-pkeyopt", "rsa_keygen_bits:3072", "-out", str(priv)],
+                    check=True, capture_output=True)
+    subprocess.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)],
+                    check=True, capture_output=True)
+    return priv, pub
+
+
+def _chiffrer(pub: Path, texte_clair: str) -> str:
+    res = subprocess.run(
+        ["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", str(pub),
+         "-pkeyopt", "rsa_padding_mode:oaep", "-pkeyopt", "rsa_oaep_md:sha256"],
+        input=texte_clair.encode("utf-8"), capture_output=True, check=True,
+    )
+    return base64.b64encode(res.stdout).decode("ascii")
+
+
+# ─── Scénarios : extraction / détection ─────────────────────────────────────
+
+def scenario_creation_demandee_detection():
+    """`creation_demandee` reconnaît oui/true/vrai, rejette le reste, et ne
+    se laisse PAS piéger par le préfixe partagé avec CREATION_NOM_PROJET."""
+    assert watcher.creation_demandee("| CREATION | oui |\n")
+    assert watcher.creation_demandee("| CREATION | TRUE |\n")
+    assert watcher.creation_demandee("| CREATION | Vrai |\n")
+    assert not watcher.creation_demandee("| CREATION | non |\n")
+    assert not watcher.creation_demandee("Rien à voir ici.\n")
+    # Collision : une ligne CREATION_NOM_PROJET seule (sans ligne CREATION)
+    # ne doit JAMAIS activer le bootstrap — bug visé par la comparaison
+    # exacte de _extraire_champ_entete plutôt qu'une recherche de sous-chaîne.
+    assert not watcher.creation_demandee("| CREATION_NOM_PROJET | oui |\n")
+    return {}
+
+
+def scenario_extraction_champs_creation():
+    """extraire_champs_creation lit les 5 champs, sans confondre CREATION_NOM_PROJET
+    et CREATION_NOM_PROJET_QUELQUECHOSE (comparaison exacte)."""
+    corps = (
+        "| CREATION | oui |\n"
+        "| CREATION_NOM_PROJET | MonProjet |\n"
+        "| CREATION_DEPOT | AlainDelree/MonProjet |\n"
+        "| CREATION_TOPIC_NTFY | bridge-monprojet |\n"
+        "| CREATION_GH_TOKEN | QUFBQg== |\n"
+        "| CREATION_OAUTH_TOKEN | Q0NDRA== |\n"
+    )
+    champs = watcher.extraire_champs_creation(corps)
+    assert champs["CREATION_NOM_PROJET"] == "MonProjet", champs
+    assert champs["CREATION_DEPOT"] == "AlainDelree/MonProjet", champs
+    assert champs["CREATION_TOPIC_NTFY"] == "bridge-monprojet", champs
+    assert champs["CREATION_GH_TOKEN"] == "QUFBQg==", champs
+    assert champs["CREATION_OAUTH_TOKEN"] == "Q0NDRA==", champs
+    return {"champs": list(champs)}
+
+
+def scenario_extraction_champs_absents():
+    """Champs absents du corps → chaînes vides, pas d'exception."""
+    champs = watcher.extraire_champs_creation("| PROJET | bridge_agent |\n")
+    assert all(v == "" for v in champs.values()), champs
+    return {}
+
+
+def scenario_retrait_tokens_corps():
+    """_corps_avec_tokens_retires masque UNIQUEMENT les 2 champs de tokens,
+    laisse le reste du corps identique (y compris CREATION_NOM_PROJET, qui
+    partage le préfixe CREATION_ mais n'est pas un secret)."""
+    corps = (
+        "| CREATION | oui |\n"
+        "| CREATION_NOM_PROJET | MonProjet |\n"
+        "| CREATION_GH_TOKEN | SECRETGH== |\n"
+        "| CREATION_OAUTH_TOKEN | SECRETOAUTH== |\n"
+        "\nTexte libre après l'en-tête.\n"
+    )
+    nouveau = watcher._corps_avec_tokens_retires(corps)
+    assert "SECRETGH==" not in nouveau, nouveau
+    assert "SECRETOAUTH==" not in nouveau, nouveau
+    assert nouveau.count("<retiré après application>") == 2, nouveau
+    assert "| CREATION_NOM_PROJET | MonProjet |" in nouveau, nouveau
+    assert "Texte libre après l'en-tête." in nouveau, nouveau
+    return {}
+
+
+# ─── Scénarios : résolution openssl ─────────────────────────────────────────
+
+def scenario_resoudre_openssl_path():
+    """openssl déjà sur le PATH (cas CCL, et CCW si l'installeur l'y ajoute) :
+    résolu en premier, sans consulter les autres candidats."""
+    chemin = watcher._resoudre_openssl()
+    assert chemin, chemin
+    assert Path(chemin).is_file(), chemin
+    return {"chemin": chemin}
+
+
+def scenario_resoudre_openssl_repli_installation_manuelle(tmp_path_factory):
+    """PATH sans openssl → repli sur l'installation manuelle Windows (#557)."""
+    tmp = tmp_path_factory()
+    faux_openssl = tmp / "openssl.exe"
+    faux_openssl.write_text("faux binaire\n")
+    ancien_which = watcher.shutil.which
+    ancien_chemin = watcher.CHEMIN_OPENSSL_WIN64
+    try:
+        watcher.shutil.which = lambda nom: None
+        watcher.CHEMIN_OPENSSL_WIN64 = faux_openssl
+        chemin = watcher._resoudre_openssl()
+        assert chemin == str(faux_openssl), chemin
+    finally:
+        watcher.shutil.which = ancien_which
+        watcher.CHEMIN_OPENSSL_WIN64 = ancien_chemin
+    return {}
+
+
+def scenario_resoudre_openssl_repli_git_usr_bin(tmp_path_factory):
+    """PATH sans openssl, installation manuelle absente → repli usr\\bin de
+    Git (même binaire que celui utilisé par provisionner.ps1 à la
+    génération des clés)."""
+    tmp = tmp_path_factory()
+    racine_git = tmp / "Git"
+    git_exe = racine_git / "cmd" / "git.exe"
+    git_exe.parent.mkdir(parents=True)
+    git_exe.write_text("faux git\n")
+    openssl_usr_bin = racine_git / "usr" / "bin" / "openssl.exe"
+    openssl_usr_bin.parent.mkdir(parents=True)
+    openssl_usr_bin.write_text("faux openssl\n")
+
+    ancien_which = watcher.shutil.which
+    ancien_chemin = watcher.CHEMIN_OPENSSL_WIN64
+    try:
+        def _which(nom):
+            return str(git_exe) if nom == "git" else None
+        watcher.shutil.which = _which
+        watcher.CHEMIN_OPENSSL_WIN64 = tmp / "chemin_inexistant" / "openssl.exe"
+        chemin = watcher._resoudre_openssl()
+        assert chemin == str(openssl_usr_bin), chemin
+    finally:
+        watcher.shutil.which = ancien_which
+        watcher.CHEMIN_OPENSSL_WIN64 = ancien_chemin
+    return {}
+
+
+def scenario_resoudre_openssl_echec_propre(tmp_path_factory):
+    """Aucun candidat trouvable → RuntimeError explicite (pas d'exception
+    non gérée)."""
+    tmp = tmp_path_factory()
+    ancien_which = watcher.shutil.which
+    ancien_chemin = watcher.CHEMIN_OPENSSL_WIN64
+    try:
+        watcher.shutil.which = lambda nom: None
+        watcher.CHEMIN_OPENSSL_WIN64 = tmp / "chemin_inexistant" / "openssl.exe"
+        try:
+            watcher._resoudre_openssl()
+            assert False, "RuntimeError attendue"
+        except RuntimeError as e:
+            assert "introuvable" in str(e), e
+    finally:
+        watcher.shutil.which = ancien_which
+        watcher.CHEMIN_OPENSSL_WIN64 = ancien_chemin
+    return {}
+
+
+# ─── Scénarios : déchiffrement réel ──────────────────────────────────────────
+
+def scenario_dechiffrement_aller_retour(tmp_path_factory):
+    """Chiffré côté « formulaire » (clé publique, OAEP/SHA-256) → déchiffré
+    par dechiffrer_token_bootstrap (clé privée) : round-trip exact."""
+    tmp = tmp_path_factory()
+    priv, pub = _generer_paire_cles(tmp)
+    token_clair = "ghp_CeciEstUnFauxTokenDeTest1234567890"
+    b64 = _chiffrer(pub, token_clair)
+    dechiffre = watcher.dechiffrer_token_bootstrap(b64, priv)
+    assert dechiffre == token_clair, dechiffre
+    return {}
+
+
+def scenario_dechiffrement_base64_invalide(tmp_path_factory):
+    """Base64 corrompu → ValueError explicite, pas d'appel openssl inutile."""
+    tmp = tmp_path_factory()
+    priv, _pub = _generer_paire_cles(tmp)
+    try:
+        watcher.dechiffrer_token_bootstrap("ceci n'est pas du base64 valide!!", priv)
+        assert False, "ValueError attendue"
+    except ValueError:
+        pass
+    return {}
+
+
+def scenario_dechiffrement_mauvaise_cle(tmp_path_factory):
+    """Chiffré avec une clé, déchiffré avec une AUTRE (clé privée non
+    correspondante) → RuntimeError (openssl échoue), jamais un résultat
+    corrompu silencieux (propriété du padding OAEP)."""
+    tmp = tmp_path_factory()
+    _priv_a, pub_a = _generer_paire_cles(tmp / "a")
+    priv_b, _pub_b = _generer_paire_cles(tmp / "b")
+    b64 = _chiffrer(pub_a, "peu importe")
+    try:
+        watcher.dechiffrer_token_bootstrap(b64, priv_b)
+        assert False, "RuntimeError attendue"
+    except RuntimeError:
+        pass
+    return {}
+
+
+# ─── Scénario complet : _traiter_creation_projet_ccw ────────────────────────
+
+FAUX_GH = """#!/bin/bash
+# Faux `gh` — issue #556. Stateful sur `issue view --json comments` (marqueur
+# touché par `issue comment` quand le body contient MARQUEUR_RESULTAT) et
+# journalise les `issue edit --body-file` (retrait des tokens) et
+# `issue close`/`issue edit --add-label` dans des fichiers dédiés.
+if [ "$1" = "issue" ] && [ "$2" = "comment" ]; then
+    bodyfile=""
+    prev=""
+    for arg in "$@"; do
+        if [ "$prev" = "--body-file" ]; then bodyfile="$arg"; fi
+        prev="$arg"
+    done
+    if [ -n "$bodyfile" ] && grep -q -- '<!-- bridge:resultat -->' "$bodyfile" 2>/dev/null; then
+        touch "$TEST_556_MARQUEUR"
+    fi
+    exit 0
+fi
+if [ "$1" = "issue" ] && [ "$2" = "view" ]; then
+    if [ -n "$TEST_556_MARQUEUR" ] && [ -f "$TEST_556_MARQUEUR" ]; then
+        echo '{"comments":[{"body":"<!-- bridge:resultat -->\\nfake"}]}'
+    else
+        echo '{"comments":[]}'
+    fi
+    exit 0
+fi
+if [ "$1" = "issue" ] && [ "$2" = "edit" ]; then
+    bodyfile=""
+    label=""
+    prev=""
+    for arg in "$@"; do
+        if [ "$prev" = "--body-file" ]; then bodyfile="$arg"; fi
+        if [ "$prev" = "--add-label" ]; then label="$arg"; fi
+        prev="$arg"
+    done
+    if [ -n "$bodyfile" ]; then
+        cp "$bodyfile" "$TEST_556_CORPS_EDITE"
+    fi
+    if [ -n "$label" ]; then
+        echo "$label" >> "$TEST_556_LABELS"
+    fi
+    exit 0
+fi
+if [ "$1" = "issue" ] && [ "$2" = "close" ]; then
+    touch "$TEST_556_FERME"
+    exit 0
+fi
+exit 0
+"""
+
+FAUX_POWERSHELL = """#!/bin/bash
+# Faux `powershell` — issue #556. Journalise chaque invocation (script + args)
+# dans $TEST_556_LOG_PS, une ligne par appel. Code de sortie piloté par
+# $TEST_556_CODE_AJOUTER / $TEST_556_CODE_FINALISER selon le script ciblé.
+script=""
+prev=""
+for arg in "$@"; do
+    if [ "$prev" = "-File" ]; then script="$arg"; fi
+    prev="$arg"
+done
+nom_script=$(basename "$script")
+echo "$nom_script|$*" >> "$TEST_556_LOG_PS"
+if [ "$nom_script" = "ajouter_projet_ccw.ps1" ]; then
+    echo "[ajouter-projet] simulation OK"
+    exit "${TEST_556_CODE_AJOUTER:-0}"
+fi
+if [ "$nom_script" = "finaliser_projet_ccw_auto.ps1" ]; then
+    echo "[finaliser-auto] simulation OK"
+    # Vérifie que le fichier de valeurs contient bien les 3 clés attendues,
+    # au format EXACT lu par mettre_a_jour_tokens_ccw.ps1 (Lire-ValeurFichier).
+    fichier_valeurs=""
+    prev2=""
+    for arg in "$@"; do
+        if [ "$prev2" = "-FichierValeurs" ]; then fichier_valeurs="$arg"; fi
+        prev2="$arg"
+    done
+    if [ -n "$fichier_valeurs" ] && [ -f "$fichier_valeurs" ]; then
+        cp "$fichier_valeurs" "$TEST_556_FICHIER_VALEURS_VU"
+    fi
+    exit "${TEST_556_CODE_FINALISER:-0}"
+fi
+exit 0
+"""
+
+
+def _preparer_bin(tmp: Path) -> Path:
+    bin_dir = tmp / "bin"
+    bin_dir.mkdir(exist_ok=True)
+    for nom, contenu in (("gh", FAUX_GH), ("powershell", FAUX_POWERSHELL)):
+        chemin = bin_dir / nom
+        chemin.write_text(contenu, encoding="utf-8")
+        chemin.chmod(chemin.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
+    return bin_dir
+
+
+def _corps_creation(nom_projet, depot, topic, gh_b64, oauth_b64):
+    return (
+        "## En-tête\n\n"
+        "| CREATION | oui |\n"
+        f"| CREATION_NOM_PROJET | {nom_projet} |\n"
+        f"| CREATION_DEPOT | {depot} |\n"
+        f"| CREATION_TOPIC_NTFY | {topic} |\n"
+        f"| CREATION_GH_TOKEN | {gh_b64} |\n"
+        f"| CREATION_OAUTH_TOKEN | {oauth_b64} |\n"
+    )
+
+
+def scenario_traiter_creation_succes(tmp_path_factory):
+    """Chemin complet, succès : les 2 scripts PowerShell sont appelés dans
+    l'ordre avec les bons arguments, le fichier de valeurs respecte le
+    format -FichierValeurs, les tokens en clair (déchiffrés) y figurent (pas
+    les versions chiffrées), le corps GitHub est édité pour retirer les
+    tokens AVANT l'exécution des scripts, et l'issue est fermée avec le
+    commentaire de résultat marqué."""
+    tmp = tmp_path_factory()
+    bin_dir = _preparer_bin(tmp)
+    priv, pub = _generer_paire_cles(tmp)
+    gh_clair, oauth_clair = "ghp_secretGH1234", "oauth_secretCCC5678"
+    corps = _corps_creation("MonProjet", "AlainDelree/MonProjet", "bridge-monprojet",
+                             _chiffrer(pub, gh_clair), _chiffrer(pub, oauth_clair))
+
+    ancien_path = os.environ.get("PATH", "")
+    ancien_cfg = watcher.CFG
+    ancien_cle = watcher.CHEMIN_CLE_PRIVEE_BOOTSTRAP
+    ancien_dossier_ps = watcher.DOSSIER_PROVISIONING_WINDOWS
+    ancien_system = watcher.platform.system
+    marqueur = tmp / "marqueur_resultat"
+    corps_edite = tmp / "corps_edite.md"
+    labels_fichier = tmp / "labels.txt"
+    ferme_fichier = tmp / "ferme"
+    log_ps = tmp / "log_ps.txt"
+    fichier_valeurs_vu = tmp / "fichier_valeurs_vu.txt"
+    os.environ.update({
+        "TEST_556_MARQUEUR": str(marqueur),
+        "TEST_556_CORPS_EDITE": str(corps_edite),
+        "TEST_556_LABELS": str(labels_fichier),
+        "TEST_556_FERME": str(ferme_fichier),
+        "TEST_556_LOG_PS": str(log_ps),
+        "TEST_556_FICHIER_VALEURS_VU": str(fichier_valeurs_vu),
+    })
+    try:
+        os.environ["PATH"] = f"{bin_dir}:{ancien_path}"
+        watcher.CFG = watcher.Config(
+            nom="ccw", depot="AlainDelree/Bridge_Agent",
+            rep_travail=Path("/tmp/nexiste-pas-556"), topic_ntfy="ccw",
+            label="for-windows", notifier_local=False,
+        )
+        watcher.CHEMIN_CLE_PRIVEE_BOOTSTRAP = priv
+        # Scripts PowerShell attendus : seule leur PRÉSENCE (fichier) est
+        # vérifiée par le code avant exécution — le faux `powershell` sur le
+        # PATH ignore leur contenu réel.
+        dossier_ps = tmp / "provisioning" / "windows"
+        dossier_ps.mkdir(parents=True)
+        for nom_ps in ("ajouter_projet_ccw.ps1", "finaliser_projet_ccw_auto.ps1", "mettre_a_jour_tokens_ccw.ps1"):
+            (dossier_ps / nom_ps).write_text("# script factice\n")
+        watcher.DOSSIER_PROVISIONING_WINDOWS = dossier_ps
+        watcher.platform.system = lambda: "Windows"
+
+        watcher._traiter_creation_projet_ccw(9556, corps, ["for-windows"], dry_run=False)
+
+        assert marqueur.exists(), "commentaire de résultat jamais posté"
+        assert ferme_fichier.exists(), "issue jamais fermée"
+        assert not labels_fichier.exists() or "needs-human" not in labels_fichier.read_text(), \
+            "needs-human posé alors que le scénario doit réussir"
+
+        lignes_ps = log_ps.read_text().splitlines()
+        assert len(lignes_ps) == 2, lignes_ps
+        assert lignes_ps[0].startswith("ajouter_projet_ccw.ps1|"), lignes_ps
+        assert lignes_ps[1].startswith("finaliser_projet_ccw_auto.ps1|"), lignes_ps
+        assert "-NomProjet MonProjet" in lignes_ps[0], lignes_ps[0]
+        assert "-Depot AlainDelree/MonProjet" in lignes_ps[0], lignes_ps[0]
+        assert "-NomProjet MonProjet" in lignes_ps[1], lignes_ps[1]
+
+        contenu_valeurs = fichier_valeurs_vu.read_text()
+        assert "TOPIC_NTFY=bridge-monprojet" in contenu_valeurs, contenu_valeurs
+        assert f"GH_TOKEN={gh_clair}" in contenu_valeurs, contenu_valeurs
+        assert f"CLAUDE_CODE_OAUTH_TOKEN={oauth_clair}" in contenu_valeurs, contenu_valeurs
+
+        corps_final = corps_edite.read_text()
+        assert gh_clair not in corps_final and oauth_clair not in corps_final, corps_final
+        assert "<retiré après application>" in corps_final, corps_final
+        assert "MonProjet" in corps_final, "le reste du corps ne doit pas être altéré"
+    finally:
+        os.environ["PATH"] = ancien_path
+        for var in ("TEST_556_MARQUEUR", "TEST_556_CORPS_EDITE", "TEST_556_LABELS",
+                    "TEST_556_FERME", "TEST_556_LOG_PS", "TEST_556_FICHIER_VALEURS_VU"):
+            os.environ.pop(var, None)
+        watcher.CFG = ancien_cfg
+        watcher.CHEMIN_CLE_PRIVEE_BOOTSTRAP = ancien_cle
+        watcher.DOSSIER_PROVISIONING_WINDOWS = ancien_dossier_ps
+        watcher.platform.system = ancien_system
+    return {}
+
+
+def scenario_traiter_creation_champ_manquant_needs_human(tmp_path_factory):
+    """Champ CREATION_DEPOT absent → échec DÉFINITIF immédiat (needs-human),
+    SANS toucher openssl ni PowerShell (vérifié : aucune entrée dans le log
+    des invocations PowerShell)."""
+    tmp = tmp_path_factory()
+    bin_dir = _preparer_bin(tmp)
+    corps = (
+        "| CREATION | oui |\n"
+        "| CREATION_NOM_PROJET | MonProjet |\n"
+        "| CREATION_TOPIC_NTFY | bridge-monprojet |\n"
+        "| CREATION_GH_TOKEN | QUFBQg== |\n"
+        "| CREATION_OAUTH_TOKEN | Q0NDRA== |\n"
+    )
+    ancien_path = os.environ.get("PATH", "")
+    ancien_cfg = watcher.CFG
+    ancien_system = watcher.platform.system
+    labels_fichier = tmp / "labels.txt"
+    log_ps = tmp / "log_ps.txt"
+    os.environ.update({
+        "TEST_556_MARQUEUR": str(tmp / "marqueur"),
+        "TEST_556_CORPS_EDITE": str(tmp / "corps_edite.md"),
+        "TEST_556_LABELS": str(labels_fichier),
+        "TEST_556_FERME": str(tmp / "ferme"),
+        "TEST_556_LOG_PS": str(log_ps),
+        "TEST_556_FICHIER_VALEURS_VU": str(tmp / "fichier_valeurs_vu.txt"),
+    })
+    try:
+        os.environ["PATH"] = f"{bin_dir}:{ancien_path}"
+        watcher.CFG = watcher.Config(
+            nom="ccw", depot="AlainDelree/Bridge_Agent",
+            rep_travail=Path("/tmp/nexiste-pas-556b"), topic_ntfy="ccw",
+            label="for-windows", notifier_local=False,
+        )
+        watcher.platform.system = lambda: "Windows"
+
+        watcher._traiter_creation_projet_ccw(9557, corps, ["for-windows"], dry_run=False)
+
+        assert labels_fichier.exists() and "needs-human" in labels_fichier.read_text(), \
+            "label needs-human attendu"
+        assert not log_ps.exists(), "aucun script PowerShell ne doit être lancé pour un champ manquant"
+    finally:
+        os.environ["PATH"] = ancien_path
+        for var in ("TEST_556_MARQUEUR", "TEST_556_CORPS_EDITE", "TEST_556_LABELS",
+                    "TEST_556_FERME", "TEST_556_LOG_PS", "TEST_556_FICHIER_VALEURS_VU"):
+            os.environ.pop(var, None)
+        watcher.CFG = ancien_cfg
+        watcher.platform.system = ancien_system
+    return {}
+
+
+def scenario_traiter_creation_dry_run(tmp_path_factory):
+    """dry_run=True : simulé (commentaire + fermeture), AUCUN script
+    PowerShell exécuté, aucun déchiffrement tenté."""
+    tmp = tmp_path_factory()
+    bin_dir = _preparer_bin(tmp)
+    corps = _corps_creation("MonProjet", "AlainDelree/MonProjet", "bridge-monprojet",
+                             "chiffre-bidon-gh", "chiffre-bidon-oauth")
+    ancien_path = os.environ.get("PATH", "")
+    ancien_cfg = watcher.CFG
+    ancien_system = watcher.platform.system
+    marqueur = tmp / "marqueur"
+    ferme_fichier = tmp / "ferme"
+    log_ps = tmp / "log_ps.txt"
+    os.environ.update({
+        "TEST_556_MARQUEUR": str(marqueur),
+        "TEST_556_CORPS_EDITE": str(tmp / "corps_edite.md"),
+        "TEST_556_LABELS": str(tmp / "labels.txt"),
+        "TEST_556_FERME": str(ferme_fichier),
+        "TEST_556_LOG_PS": str(log_ps),
+        "TEST_556_FICHIER_VALEURS_VU": str(tmp / "fichier_valeurs_vu.txt"),
+    })
+    try:
+        os.environ["PATH"] = f"{bin_dir}:{ancien_path}"
+        watcher.CFG = watcher.Config(
+            nom="ccw", depot="AlainDelree/Bridge_Agent",
+            rep_travail=Path("/tmp/nexiste-pas-556c"), topic_ntfy="ccw",
+            label="for-windows", notifier_local=False,
+        )
+        watcher.platform.system = lambda: "Windows"
+
+        watcher._traiter_creation_projet_ccw(9558, corps, ["for-windows"], dry_run=True)
+
+        assert marqueur.exists(), "commentaire de résultat (simulé) jamais posté"
+        assert ferme_fichier.exists(), "issue jamais fermée (dry-run)"
+        assert not log_ps.exists(), "aucun script PowerShell ne doit être lancé en dry-run"
+    finally:
+        os.environ["PATH"] = ancien_path
+        for var in ("TEST_556_MARQUEUR", "TEST_556_CORPS_EDITE", "TEST_556_LABELS",
+                    "TEST_556_FERME", "TEST_556_LOG_PS", "TEST_556_FICHIER_VALEURS_VU"):
+            os.environ.pop(var, None)
+        watcher.CFG = ancien_cfg
+        watcher.platform.system = ancien_system
+    return {}
+
+
+def scenario_dispatch_jamais_claude(tmp_path_factory):
+    """Bout en bout via watcher.traiter_issue() : une issue portant CREATION
+    ne lance JAMAIS `claude`, même si un faux `claude` (qui échouerait le
+    test s'il était invoqué) est sur le PATH — décision #554 §2.5."""
+    tmp = tmp_path_factory()
+    bin_dir = _preparer_bin(tmp)
+    marqueur_claude = tmp / "claude_a_ete_lance"
+    claude_path = bin_dir / "claude"
+    claude_path.write_text(f"#!/bin/bash\ntouch {marqueur_claude}\nexit 1\n", encoding="utf-8")
+    claude_path.chmod(claude_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
+
+    priv, pub = _generer_paire_cles(tmp)
+    corps = _corps_creation("AutreProjet", "AlainDelree/AutreProjet", "bridge-autreprojet",
+                             _chiffrer(pub, "ghtok"), _chiffrer(pub, "oauthtok"))
+    issue = {
+        "number": 9559, "title": "Créer le projet AutreProjet",
+        "body": corps, "labels": [{"name": "for-windows"}],
+    }
+
+    ancien_path = os.environ.get("PATH", "")
+    ancien_cfg = watcher.CFG
+    ancien_cle = watcher.CHEMIN_CLE_PRIVEE_BOOTSTRAP
+    ancien_dossier_ps = watcher.DOSSIER_PROVISIONING_WINDOWS
+    ancien_system = watcher.platform.system
+    ancien_dossier_verrous = watcher.DOSSIER_VERROUS
+    marqueur_resultat = tmp / "marqueur_resultat"
+    os.environ.update({
+        "TEST_556_MARQUEUR": str(marqueur_resultat),
+        "TEST_556_CORPS_EDITE": str(tmp / "corps_edite.md"),
+        "TEST_556_LABELS": str(tmp / "labels.txt"),
+        "TEST_556_FERME": str(tmp / "ferme"),
+        "TEST_556_LOG_PS": str(tmp / "log_ps.txt"),
+        "TEST_556_FICHIER_VALEURS_VU": str(tmp / "fichier_valeurs_vu.txt"),
+    })
+    try:
+        os.environ["PATH"] = f"{bin_dir}:{ancien_path}"
+        watcher.DOSSIER_VERROUS = tmp / "verrous"
+        watcher.CFG = watcher.Config(
+            nom="ccw", depot="AlainDelree/Bridge_Agent",
+            rep_travail=Path("/tmp/nexiste-pas-556d"), topic_ntfy="ccw",
+            label="for-windows", notifier_local=False,
+        )
+        watcher.CHEMIN_CLE_PRIVEE_BOOTSTRAP = priv
+        dossier_ps = tmp / "provisioning" / "windows"
+        dossier_ps.mkdir(parents=True)
+        for nom_ps in ("ajouter_projet_ccw.ps1", "finaliser_projet_ccw_auto.ps1", "mettre_a_jour_tokens_ccw.ps1"):
+            (dossier_ps / nom_ps).write_text("# script factice\n")
+        watcher.DOSSIER_PROVISIONING_WINDOWS = dossier_ps
+        watcher.platform.system = lambda: "Windows"
+        watcher.issues_en_cours.discard(9559)
+
+        watcher.traiter_issue(issue, dry_run=False)
+
+        assert not marqueur_claude.exists(), "claude a été invoqué alors que CREATION doit s'en passer entièrement (#554 §2.5)"
+        assert marqueur_resultat.exists(), "le bootstrap déterministe n'a pourtant pas abouti"
+    finally:
+        os.environ["PATH"] = ancien_path
+        for var in ("TEST_556_MARQUEUR", "TEST_556_CORPS_EDITE", "TEST_556_LABELS",
+                    "TEST_556_FERME", "TEST_556_LOG_PS", "TEST_556_FICHIER_VALEURS_VU"):
+            os.environ.pop(var, None)
+        watcher.CFG = ancien_cfg
+        watcher.CHEMIN_CLE_PRIVEE_BOOTSTRAP = ancien_cle
+        watcher.DOSSIER_PROVISIONING_WINDOWS = ancien_dossier_ps
+        watcher.platform.system = ancien_system
+        watcher.DOSSIER_VERROUS = ancien_dossier_verrous
+        watcher.issues_en_cours.discard(9559)
+    return {}
+
+
+def main():
+    tmp = tempfile.TemporaryDirectory()
+    compteur = {"n": 0}
+
+    def _tmp_path_factory():
+        compteur["n"] += 1
+        p = Path(tmp.name) / f"scenario{compteur['n']}"
+        p.mkdir(parents=True, exist_ok=True)
+        return p
+
+    tests = [
+        ("creation_demandee : détection + non-collision avec CREATION_NOM_PROJET", scenario_creation_demandee_detection),
+        ("extraire_champs_creation : les 5 champs, valeurs exactes", scenario_extraction_champs_creation),
+        ("extraire_champs_creation : champs absents → chaînes vides", scenario_extraction_champs_absents),
+        ("_corps_avec_tokens_retires : masque uniquement les 2 tokens", scenario_retrait_tokens_corps),
+        ("_resoudre_openssl : trouvé sur le PATH", scenario_resoudre_openssl_path),
+        ("_resoudre_openssl : repli installation manuelle Windows (#557)", lambda: scenario_resoudre_openssl_repli_installation_manuelle(_tmp_path_factory)),
+        ("_resoudre_openssl : repli usr\\bin de Git", lambda: scenario_resoudre_openssl_repli_git_usr_bin(_tmp_path_factory)),
+        ("_resoudre_openssl : aucun candidat → RuntimeError propre", lambda: scenario_resoudre_openssl_echec_propre(_tmp_path_factory)),
+        ("dechiffrer_token_bootstrap : aller-retour chiffrement réel (openssl)", lambda: scenario_dechiffrement_aller_retour(_tmp_path_factory)),
+        ("dechiffrer_token_bootstrap : base64 invalide → ValueError", lambda: scenario_dechiffrement_base64_invalide(_tmp_path_factory)),
+        ("dechiffrer_token_bootstrap : mauvaise clé → RuntimeError (pas de résultat corrompu)", lambda: scenario_dechiffrement_mauvaise_cle(_tmp_path_factory)),
+        ("_traiter_creation_projet_ccw : chemin complet, succès", lambda: scenario_traiter_creation_succes(_tmp_path_factory)),
+        ("_traiter_creation_projet_ccw : champ manquant → needs-human, aucun script lancé", lambda: scenario_traiter_creation_champ_manquant_needs_human(_tmp_path_factory)),
+        ("_traiter_creation_projet_ccw : dry-run simulé, aucun script lancé", lambda: scenario_traiter_creation_dry_run(_tmp_path_factory)),
+        ("traiter_issue : dispatch CREATION → claude JAMAIS invoqué (#554 §2.5)", lambda: scenario_dispatch_jamais_claude(_tmp_path_factory)),
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
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 6a3601a..94d1f78 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 31 (6 ligne(s)) dans l'ancienne version → ligne 31 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,6 +31,8 @@ import shutil
 import threading
 import ctypes
 import ctypes.wintypes
+import base64
+import binascii
 from logging.handlers import RotatingFileHandler
 from dataclasses import dataclass, field
 from pathlib import Path
# ── Zone modifiée : ligne 49 (6 ligne(s)) dans l'ancienne version → ligne 51 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -49,6 +51,26 @@ import notifications
 DOSSIER_SCRIPT = Path(__file__).resolve().parent
 DOSSIER_LOGS   = DOSSIER_SCRIPT / "logs"
 
+# Bootstrap automatique d'un service CCW dédié (issue #556, 2/3, champ
+# d'en-tête CREATION — voir plus bas et BRIDGE_AGENT_DOC.md §16). Scripts
+# PowerShell déjà en place (issue #170/#173/#174) : watcher.py les APPELLE,
+# il ne réimplémente rien. DOSSIER_SCRIPT pointe TOUJOURS vers le clone
+# Bridge_Agent (un seul watcher.py partagé par tous les services CCW, cf.
+# §16 du DOC) : ce chemin résout correctement quel que soit le projet piloté
+# par CETTE instance.
+DOSSIER_PROVISIONING_WINDOWS = DOSSIER_SCRIPT / "provisioning" / "windows"
+# Clé privée de bootstrap (issue #554) : dossier FRÈRE de Bridge_Agent
+# (généré par provisionner.ps1 dans <RepCCW>\cles_bootstrap, jamais dans un
+# clone git). DOSSIER_SCRIPT.parent == RepCCW, quel que soit son nom réel.
+CHEMIN_CLE_PRIVEE_BOOTSTRAP = DOSSIER_SCRIPT.parent / "cles_bootstrap" / "bootstrap_privee.pem"
+# Installation manuelle d'OpenSSL sur CCW (point d'attention #557, repris ici
+# faute d'avoir #558 déjà mergé) : PAS sur le PATH par défaut, distincte de
+# l'openssl embarqué par Git pour Windows utilisé par provisionner.ps1 pour
+# la GÉNÉRATION de la paire de clés (Resoudre-OpenSSL côté PowerShell).
+CHEMIN_OPENSSL_WIN64 = Path(r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe")
+TIMEOUT_CREATION_CLONE    = 600  # ajouter_projet_ccw.ps1 : clone git, potentiellement long
+TIMEOUT_CREATION_FINALISE = 60   # finaliser_projet_ccw_auto.ps1 : pas de réseau (NSSM + tokens)
+
 # scripts/traitement_fin.py (issue #352) : notifier_fin_issue()/notifier_debut_
 # issue() (#515) y sont importées directement (pas via subprocess comme le bip)
 # pour pouvoir les déclencher à chaque fin/début d'issue indépendamment des
# ── Zone modifiée : ligne 1629 (6 ligne(s)) dans l'ancienne version → ligne 1651 (417 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1629,6 +1651,417 @@ def valider_sous_dossier(rep_travail: Path, sous_dossier: str) -> tuple[bool, st
         return False, f"'{resolu}' n'existe pas ou n'est pas un dossier", Path()
     return True, "", resolu
 
+# ─── Bootstrap automatique d'un service CCW dédié (issue #556, 2/3) ────────────
+# Champ d'en-tête optionnel CREATION : déclenche, en Python déterministe et
+# SANS jamais invoquer `claude` (décision #554 §2.5), la création complète
+# d'un service CCW dédié pour un nouveau projet. Convention détaillée dans
+# BRIDGE_AGENT_DOC.md §16 (pour le formulaire web à venir, 3/3, #559+) :
+#   | CREATION | oui |                — déclencheur (toute autre valeur/absence ignore ce champ)
+#   | CREATION_NOM_PROJET | <nom> |   — passé tel quel à ajouter_projet_ccw.ps1 -NomProjet
+#   | CREATION_DEPOT | owner/repo |   — passé tel quel à ajouter_projet_ccw.ps1 -Depot
+#   | CREATION_TOPIC_NTFY | <topic> | — passé tel quel dans le fichier de valeurs (TOPIC_NTFY=)
+#   | CREATION_GH_TOKEN | <base64> |        — token GH_TOKEN chiffré (voir dechiffrer_token_bootstrap)
+#   | CREATION_OAUTH_TOKEN | <base64> |     — token CLAUDE_CODE_OAUTH_TOKEN chiffré (idem)
+CHAMPS_CREATION = (
+    "CREATION_NOM_PROJET",
+    "CREATION_DEPOT",
+    "CREATION_TOPIC_NTFY",
+    "CREATION_GH_TOKEN",
+    "CREATION_OAUTH_TOKEN",
+)
+
+def _extraire_champ_entete(body: str, nom_champ: str) -> str:
+    """Extrait la valeur d'un champ `| NOM_CHAMP | valeur |` de l'en-tête
+    bridge (issue #556). Comparaison EXACTE (pas une sous-chaîne comme
+    extraire_sous_dossier/extraire_repo_cible) sur le premier segment trimé
+    et mis en majuscules : nécessaire ici parce que CREATION est le préfixe
+    littéral de CREATION_NOM_PROJET/CREATION_DEPOT/…, une simple recherche
+    de sous-chaîne `"| CREATION" in ligne.upper()` matcherait ces AUTRES
+    champs par erreur (ex. sur la ligne CREATION_NOM_PROJET). Retourne "" si
+    le champ est absent ou vide."""
+    for ligne in body.splitlines():
+        parts = ligne.split("|")
+        if len(parts) >= 3 and parts[1].strip().upper() == nom_champ:
+            valeur = parts[2].strip()
+            if valeur and valeur.lower() not in ("", "-"):
+                return valeur
+    return ""
+
+def creation_demandee(body: str) -> bool:
+    """Indique si l'issue porte `| CREATION | oui |` (issue #556) — déclencheur
+    du bootstrap automatique d'un service CCW dédié, détecté tôt dans le
+    dispatch, AVANT tout lancement de claude. Valeurs actives reconnues :
+    oui/true/vrai (insensible à la casse). Absent ou toute autre valeur :
+    dispatch normal inchangé (lancement de claude comme avant #556)."""
+    return _extraire_champ_entete(body, "CREATION").strip().lower() in ("oui", "true", "vrai")
+
+def extraire_champs_creation(body: str) -> dict[str, str]:
+    """Extrait les 5 champs CREATION_* du corps de l'issue (issue #556).
+    Chaque valeur manquante reste "" — la validation (champs requis tous
+    présents) est faite par l'appelant, pas ici."""
+    return {champ: _extraire_champ_entete(body, champ) for champ in CHAMPS_CREATION}
+
+def _corps_avec_tokens_retires(body: str) -> str:
+    """Retourne `body` avec les valeurs de CREATION_GH_TOKEN/CREATION_OAUTH_TOKEN
+    remplacées par un placeholder (issue #556, §2.4 de #554) — limite le temps
+    d'exposition résiduel des tokens chiffrés sur GitHub. Sans effet sur le
+    reste du corps. Appelée dès que les valeurs sont extraites en mémoire :
+    la suite du traitement ne relit plus jamais le corps de l'issue."""
+    placeholder = "<retiré après application>"
+    lignes = body.splitlines(keepends=True)
+    for i, ligne in enumerate(lignes):
+        parts = ligne.split("|")
+        if len(parts) >= 3 and parts[1].strip().upper() in ("CREATION_GH_TOKEN", "CREATION_OAUTH_TOKEN"):
+            parts[2] = f" {placeholder} "
+            lignes[i] = "|".join(parts)
+    return "".join(lignes)
+
+def _editer_corps_issue(numero: int, nouveau_corps: str) -> bool:
+    """Remplace le corps d'une issue (`gh issue edit --body-file`, même
+    protection --body-file que commenter_issue contre la limite argv Windows,
+    issue #237). Réservé au retrait des tokens chiffrés (issue #556, §2.4)."""
+    fichier_tmp = None
+    try:
+        with tempfile.NamedTemporaryFile(
+                mode="w", suffix=".md", delete=False,
+                encoding="utf-8") as f:
+            f.write(nouveau_corps)
+            fichier_tmp = f.name
+        res = subprocess.run(
+            ["gh", "issue", "edit", str(numero),
+             "--repo", CFG.depot,
+             "--body-file", fichier_tmp],
+            capture_output=True, text=True,
+            encoding="utf-8", errors="replace", timeout=30
+        )
+        if res.returncode != 0:
+            log.error(f"Erreur édition du corps de l'issue #{numero} (code {res.returncode}) : {res.stderr.strip()}")
+            return False
+        return True
+    except Exception as e:
+        log.error(f"Erreur édition du corps de l'issue #{numero} : {e}")
+        return False
+    finally:
+        if fichier_tmp:
+            try:
+                Path(fichier_tmp).unlink(missing_ok=True)
+            except OSError:
+                pass
+
+def _resoudre_openssl() -> str:
+    """Résout le chemin de l'exécutable openssl (issue #556), robuste au
+    point d'attention découvert en #557 : sur CCW, openssl n'est disponible
+    qu'après une installation manuelle séparée
+    (C:\\Program Files\\OpenSSL-Win64\\bin\\openssl.exe — CHEMIN_OPENSSL_WIN64),
+    PAS sur le PATH par défaut. Distinct de l'openssl embarqué par Git pour
+    Windows (usr\\bin) qu'utilise provisionner.ps1 pour la GÉNÉRATION de la
+    paire de clés (Resoudre-OpenSSL côté PowerShell, issue #554) — dupliqué
+    ici plutôt que réutilisé : pas de dot-sourcing PowerShell depuis Python,
+    et cette fonction n'a besoin que d'un CHEMIN, pas d'exécuter du PowerShell.
+
+    Ordre de résolution :
+      1. `openssl` sur le PATH (shutil.which — couvre Linux/CCL, où openssl
+         est quasi toujours présent, et un CCW où l'installeur l'aurait
+         ajouté au PATH) ;
+      2. l'installation manuelle documentée (#557) ;
+      3. le sous-dossier usr\\bin de Git pour Windows, en repli ultime (même
+         binaire que celui utilisé à la génération des clés).
+
+    Lève RuntimeError si aucune des trois ne mène à un fichier présent —
+    erreur de configuration machine, traitée par l'appelant comme définitive
+    (needs-human, aucun retry), jamais comme un échec transitoire."""
+    depuis_path = shutil.which("openssl")
+    if depuis_path:
+        return depuis_path
+
+    candidats = [CHEMIN_OPENSSL_WIN64]
+    git_exe = shutil.which("git")
+    if git_exe:
+        # <GitRoot>\{bin,cmd}\git.exe → deux parents → <GitRoot> → usr\bin
+        # (sibling de mingw64/bin/cmd dans une installation Git pour Windows
+        # standard), PAS un sous-dossier de mingw64.
+        racine_git = Path(git_exe).resolve().parent.parent
+        candidats.append(racine_git / "usr" / "bin" / "openssl.exe")
+
+    for candidat in candidats:
+        if candidat.is_file():
+            return str(candidat)
+
+    raise RuntimeError(
+        "openssl introuvable (ni sur le PATH, ni dans l'installation manuelle "
+        f"{CHEMIN_OPENSSL_WIN64}, ni dans le usr\\bin de Git) — impossible de "
+        "déchiffrer les tokens de bootstrap (issue #556)."
+    )
+
+def dechiffrer_token_bootstrap(valeur_base64: str, chemin_cle_privee: Path) -> str:
+    """Déchiffre un token de bootstrap encodé en base64 (issue #556).
+
+    Convention (documentée en détail dans BRIDGE_AGENT_DOC.md §16, à
+    l'intention du formulaire à venir en 3/3) : le token en clair (UTF-8) est
+    chiffré côté formulaire avec la clé PUBLIQUE de bootstrap via
+    `openssl pkeyutl -encrypt -pubin -inkey bootstrap_publique.pem
+     -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256`, puis le
+    résultat binaire est encodé en base64 SANS retour à la ligne (`base64
+    -w0` ou équivalent) pour tenir dans une cellule de tableau markdown.
+    Cette fonction inverse exactement cette chaîne : décodage base64 →
+    `openssl pkeyutl -decrypt` avec le MÊME padding OAEP/SHA-256 (impératif —
+    un mauvais padding fait ÉCHOUER le déchiffrement plutôt que de réussir
+    silencieusement avec un résultat corrompu, propriété du padding OAEP) et
+    la clé PRIVÉE locale.
+
+    Lève ValueError (base64 invalide) ou RuntimeError (openssl absent ou en
+    échec) — toutes deux traitées par l'appelant comme une erreur de
+    configuration/issue définitive (needs-human, aucun retry)."""
+    try:
+        chiffre = base64.b64decode(valeur_base64, validate=True)
+    except (binascii.Error, ValueError) as e:
+        raise ValueError(f"base64 invalide : {e}") from e
+
+    openssl = _resoudre_openssl()
+    fichier_tmp = None
+    try:
+        with tempfile.NamedTemporaryFile(
+                mode="wb", suffix=".bin", delete=False) as f:
+            f.write(chiffre)
+            fichier_tmp = f.name
+        res = subprocess.run(
+            [openssl, "pkeyutl", "-decrypt",
+             "-inkey", str(chemin_cle_privee),
+             "-pkeyopt", "rsa_padding_mode:oaep",
+             "-pkeyopt", "rsa_oaep_md:sha256",
+             "-in", fichier_tmp],
+            capture_output=True, timeout=30
+        )
+        if res.returncode != 0:
+            raise RuntimeError(
+                f"openssl pkeyutl -decrypt a échoué (code {res.returncode}) : "
+                f"{res.stderr.decode('utf-8', errors='replace').strip()}"
+            )
+        return res.stdout.decode("utf-8").strip()
+    finally:
+        if fichier_tmp:
+            try:
+                Path(fichier_tmp).unlink(missing_ok=True)
+            except OSError:
+                pass
+
+def _ecrire_fichier_valeurs_creation(topic: str, gh_token: str, oauth_token: str) -> Path:
+    """Écrit le fichier temporaire « clé=valeur » consommé par
+    `finaliser_projet_ccw_auto.ps1 -FichierValeurs` (issue #556) — MÊME
+    format, vérifié par lecture du script avant d'écrire ce code, que celui
+    déjà produit par `app/ccw.py` (`ccw_finaliser_projet`) : trois lignes
+    `TOPIC_NTFY=`/`GH_TOKEN=`/`CLAUDE_CODE_OAUTH_TOKEN=`, UTF-8, AUCUN espace
+    autour du `=` (`Lire-ValeurFichier` côté PowerShell ne rogne que la CLÉ,
+    pas la valeur — un espace après `=` finirait dans le token). Permissions
+    restreintes en best-effort (0600 ; sans effet réel sous NTFS/Windows,
+    seulement sous POSIX — CCW reste protégé par les ACL du dossier temp
+    utilisateur). Suppression laissée à l'appelant (finally, comme ccw.py)."""
+    fd, chemin = tempfile.mkstemp(prefix="ccw-creation-vals-", suffix=".txt")
+    try:
+        os.chmod(chemin, 0o600)
+    except OSError:
+        pass
+    with os.fdopen(fd, "w", encoding="utf-8") as f:
+        f.write(f"TOPIC_NTFY={topic}\n")
+        f.write(f"GH_TOKEN={gh_token}\n")
+        f.write(f"CLAUDE_CODE_OAUTH_TOKEN={oauth_token}\n")
+    return Path(chemin)
+
+def _traiter_creation_projet_ccw(numero: int, body: str, labels: list[str], dry_run: bool) -> None:
+    """Bootstrap automatique d'un service CCW dédié (issue #556, 2/3),
+    déclenché par `| CREATION | oui |`. ENTIÈREMENT déterministe — n'invoque
+    JAMAIS `claude` (décision #554 §2.5) : appelle directement les 2 scripts
+    PowerShell déjà testés, EXACTEMENT comme le fait déjà l'onglet CCW de
+    l'interface web (`app/ccw.py`, `ccw_ajouter_projet`/`ccw_finaliser_projet`)
+    — à la différence près que watcher.py tourne DÉJÀ sur la machine CCW
+    cible (appel PowerShell local, pas de couche SSH).
+
+    Prend en charge la TOTALITÉ du cycle de vie de cette issue — pas d'ACK
+    séparé (traitement synchrone, une seule tentative, contrairement au
+    pipeline lancer_claude) : extraction, retrait immédiat des tokens
+    chiffrés du corps GitHub (§2.4 de #554, avant même la tentative de
+    déchiffrement), déchiffrement, écriture du fichier de valeurs, appel
+    séquentiel des 2 scripts PowerShell, compte-rendu, puis fermeture ou
+    `needs-human` selon le résultat. Retire `numero` de `issues_en_cours`
+    dans tous les cas avant de retourner (appelée avec l'entrée déjà ajoutée
+    par l'appelant)."""
+    log.info(f"→ Issue #{numero} : champ CREATION détecté — bootstrap automatique d'un service CCW dédié (#556).")
+
+    def _echec(message: str) -> None:
+        log.error(f"  ✗ Issue #{numero} (CREATION) : {message}")
+        commenter_issue(
+            numero,
+            f"❌ Bootstrap automatique du service CCW échoué : {message}\n\n"
+            f"Label `{LABEL_ECHEC}` posé — corrigez puis retirez-le pour relancer."
+        )
+        ajouter_label(numero, LABEL_ECHEC)
+        notifier(
+            labels,
+            titre=f"❌ {CFG.nom} #{numero} — bootstrap CCW échoué",
+            message=message,
+            urgence_bureau="critical",
+            priorite_ntfy="high",
+            numero=numero,
+        )
+        notifier_fin_sse(numero)
+        _issues_en_cours_retirer(numero)
+
+    champs = extraire_champs_creation(body)
+    nom_projet    = champs["CREATION_NOM_PROJET"]
+    depot         = champs["CREATION_DEPOT"]
+    topic_ntfy    = champs["CREATION_TOPIC_NTFY"]
+    gh_chiffre    = champs["CREATION_GH_TOKEN"]
+    oauth_chiffre = champs["CREATION_OAUTH_TOKEN"]
+
+    manquants = [nom for nom, valeur in champs.items() if not valeur]
+    if manquants:
+        _echec(f"champ(s) manquant(s) dans le corps de l'issue : {', '.join(manquants)}.")
+        return
+
+    if dry_run:
+        log.info(f"[DRY-RUN] Issue #{numero} : bootstrap CCW simulé pour le projet '{nom_projet}' (dépôt {depot}) — aucun script exécuté, aucun token déchiffré.")
+        commenter_resultat_avec_retry(
+            numero,
+            f"{MARQUEUR_RESULTAT}\n## Résultat\n\n"
+            f"[DRY-RUN] Bootstrap CCW simulé pour le projet **{nom_projet}** — aucune "
+            f"action réelle (ni décryptage, ni script PowerShell exécuté)."
+        )
+        fermer_issue(numero)
+        _issues_en_cours_retirer(numero)
+        return
+
+    # §2.4 (#554) : retrait immédiat des tokens du corps GitHub — les valeurs
+    # nécessaires sont déjà en mémoire ci-dessus, la suite ne relit plus
+    # jamais le corps de l'issue. Best-effort : un échec ici est journalisé
+    # mais NE bloque PAS le bootstrap (l'exposition résiduelle est fâcheuse,
+    # pas bloquante en soi).
+    if not _editer_corps_issue(numero, _corps_avec_tokens_retires(body)):
+        log.warning(f"  Issue #{numero} : retrait des tokens du corps GitHub échoué (best-effort, traitement poursuivi).")
+
+    if platform.system() != "Windows":
+        _echec("cette opération nécessite les scripts PowerShell CCW — non exécutable sur cette plateforme (agent Linux, hors périmètre CCW).")
+        return
+
+    try:
+        _resoudre_openssl()
+    except RuntimeError as e:
+        _echec(str(e))
+        return
+
+    if not CHEMIN_CLE_PRIVEE_BOOTSTRAP.is_file():
+        _echec(f"clé privée de bootstrap introuvable ({CHEMIN_CLE_PRIVEE_BOOTSTRAP}) — provisionner.ps1 a-t-il été rejoué depuis la dernière réinstallation (issue #554) ?")
+        return
+
+    try:
+        gh_token    = dechiffrer_token_bootstrap(gh_chiffre, CHEMIN_CLE_PRIVEE_BOOTSTRAP)
+        oauth_token = dechiffrer_token_bootstrap(oauth_chiffre, CHEMIN_CLE_PRIVEE_BOOTSTRAP)
+    except (ValueError, RuntimeError) as e:
+        _echec(f"déchiffrement des tokens impossible ({e}).")
+        return
+    if not gh_token or not oauth_token:
+        _echec("un des deux tokens déchiffrés est vide — chiffrement source probablement invalide.")
+        return
+
+    script_ajouter   = DOSSIER_PROVISIONING_WINDOWS / "ajouter_projet_ccw.ps1"
+    script_finaliser = DOSSIER_PROVISIONING_WINDOWS / "finaliser_projet_ccw_auto.ps1"
+    script_tokens    = DOSSIER_PROVISIONING_WINDOWS / "mettre_a_jour_tokens_ccw.ps1"
+    for s in (script_ajouter, script_finaliser, script_tokens):
+        if not s.is_file():
+            _echec(f"script attendu introuvable : {s} — clone Bridge_Agent incomplet ou en retard ?")
+            return
+
+    log.info(f"  Issue #{numero} : ajouter_projet_ccw.ps1 -NomProjet {nom_projet} -Depot {depot}…")
+    try:
+        res_ajouter = subprocess.run(
+            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_ajouter),
+             "-NomProjet", nom_projet, "-Depot", depot],
+            capture_output=True, text=True,
+            encoding="utf-8", errors="replace", timeout=TIMEOUT_CREATION_CLONE,
+        )
+    except subprocess.TimeoutExpired:
+        _echec(f"ajouter_projet_ccw.ps1 a dépassé le délai ({TIMEOUT_CREATION_CLONE}s — clone trop long ?).")
+        return
+    except Exception as e:
+        _echec(f"erreur d'exécution de ajouter_projet_ccw.ps1 : {e}")
+        return
+    sortie_ajouter = (res_ajouter.stdout or "") + (res_ajouter.stderr or "")
+    if res_ajouter.returncode != 0:
+        _echec(
+            f"ajouter_projet_ccw.ps1 a échoué (code {res_ajouter.returncode}).\n\n"
+            f"<details><summary>Log complet</summary>\n\n```\n{sortie_ajouter}\n```\n</details>"
+        )
+        return
+
+    log.info(f"  Issue #{numero} : finaliser_projet_ccw_auto.ps1 -NomProjet {nom_projet}…")
+    chemin_valeurs = _ecrire_fichier_valeurs_creation(topic_ntfy, gh_token, oauth_token)
+    try:
+        res_finaliser = subprocess.run(
+            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_finaliser),
+             "-NomProjet", nom_projet, "-FichierValeurs", str(chemin_valeurs)],
+            capture_output=True, text=True,
+            encoding="utf-8", errors="replace", timeout=TIMEOUT_CREATION_FINALISE,
+        )
+    except subprocess.TimeoutExpired:
+        _echec(f"finaliser_projet_ccw_auto.ps1 a dépassé le délai ({TIMEOUT_CREATION_FINALISE}s).")
+        return
+    except Exception as e:
+        _echec(f"erreur d'exécution de finaliser_projet_ccw_auto.ps1 : {e}")
+        return
+    finally:
+        # finaliser_projet_ccw_auto.ps1 supprime déjà ce fichier dans son
+        # propre finally PowerShell — nettoyage Python en DEUXIÈME ligne de
+        # défense (même pattern que app/ccw.py, issue #174) : couvre le cas
+        # où le script n'a jamais démarré ou a planté avant son propre finally.
+        if chemin_valeurs.exists():
+            try:
+                chemin_valeurs.unlink()
+            except OSError:
+                pass
+
+    sortie_finaliser = (res_finaliser.stdout or "") + (res_finaliser.stderr or "")
+    # Codes de mettre_a_jour_tokens_ccw.ps1, relayés par finaliser_projet_ccw_auto.ps1 :
+    # 0 = OK, 2 = à vérifier (avertissement, pas un échec), 1/autre = échec.
+    if res_finaliser.returncode not in (0, 2):
+        _echec(
+            f"finaliser_projet_ccw_auto.ps1 a échoué (code {res_finaliser.returncode}).\n\n"
+            f"<details><summary>Log complet</summary>\n\n```\n{sortie_ajouter}\n\n{sortie_finaliser}\n```\n</details>"
+        )
+        return
+
+    avertissement = ("" if res_finaliser.returncode == 0 else
+                      "\n\n⚠️ Tokens appliqués mais vérification finale non concluante (code 2) — relisez le log ci-dessous.")
+    message_resultat = (
+        f"{MARQUEUR_RESULTAT}\n## Résultat\n\n"
+        f"✅ Service CCW dédié « CCW-Watcher-{nom_projet} » créé et finalisé pour le projet "
+        f"**{nom_projet}** (dépôt `{depot}`).{avertissement}\n\n"
+        f"<details><summary>Log complet</summary>\n\n```\n{sortie_ajouter}\n\n{sortie_finaliser}\n```\n</details>"
+    )
+    if not commenter_resultat_avec_retry(numero, message_resultat):
+        log.error(f"  ✗ Commentaire de résultat #{numero} (CREATION) impossible après retries — issue laissée OUVERTE pour reprise.")
+        notifier(
+            labels,
+            titre=f"⚠️ {CFG.nom} #{numero} — bootstrap CCW résultat non posté",
+            message=f"Service CCW « {nom_projet} » créé, mais le commentaire de résultat a échoué (réseau).",
+            urgence_bureau="critical",
+            priorite_ntfy="high",
+            numero=numero,
+        )
+        _issues_en_cours_retirer(numero)
+        return
+    if not fermer_issue(numero):
+        log.warning(f"  Fermeture de l'issue #{numero} (CREATION) incomplète — sera retentée au prochain cycle (garde d'idempotence).")
+    log.info(f"  ✓ Issue #{numero} (CREATION) : service CCW « {nom_projet} » bootstrappé avec succès.")
+    notifier(
+        labels,
+        titre=f"✅ {CFG.nom} #{numero} — service CCW « {nom_projet} » créé",
+        message=f"Bootstrap automatique terminé pour le projet {nom_projet}.",
+        urgence_bureau="normal",
+        priorite_ntfy="default",
+        numero=numero,
+    )
+    notifier_fin_sse(numero)
+    _issues_en_cours_retirer(numero)
+
 # ─── Détection de conflit avec un watcher actif (issue #125) ───────────────────
 # Variantes LOCALES de app.projets.lister_projets() et app.watchers.watcher_actif() :
 # app.projets importe watcher — réutiliser ces fonctions ici créerait un import
# ── Zone modifiée : ligne 3224 (6 ligne(s)) dans l'ancienne version → ligne 3657 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3224,6 +3657,15 @@ def _traiter_issue_synchrone(issue: dict, dry_run: bool, chemin_worktree: Path |
         return
 
     _issues_en_cours_ajouter(numero)
+
+    # Bootstrap automatique CCW (issue #556, 2/3) : entièrement déterministe,
+    # détecté et traité AVANT tout lancement de claude — sans rapport avec le
+    # pipeline habituel (mode, périmètre, verrou, lancer_claude). Sans objet
+    # si le champ CREATION est absent/désactivé : dispatch normal inchangé.
+    if creation_demandee(body):
+        _traiter_creation_projet_ccw(numero, body, labels, dry_run)
+        return
+
     priorite = extraire_priorite(body)
     critique = priorite in PRIORITES_CRITIQUES
     timeout  = extraire_timeout(body, titre)
