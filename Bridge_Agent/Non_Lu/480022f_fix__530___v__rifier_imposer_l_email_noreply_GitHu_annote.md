480022f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 480022f
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Sat Sep 12 15:52:34 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #530 : vérifier/imposer l'email noreply GitHub avant le premier commit d'un nouveau projet

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nouveau_projet.py b/nouveau_projet.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1bdcad0..5a7f953 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nouveau_projet.py
# ── Version APRÈS ce commit.
+++ b/nouveau_projet.py
# ── Zone modifiée : ligne 350 (6 ligne(s)) dans l'ancienne version → ligne 350 (42 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -350,6 +350,42 @@ def _fichiers_suivis_preexistants(rep_path: Path, git_runner) -> list[str]:
     return sorted(f for f in fichiers if Path(f).name not in FICHIERS_CREES_PAR_SCRIPT)
 
 
+def _corriger_email_noreply(git_runner) -> str | None:
+    """Filet de sécurité avant le tout premier commit (issue #530) : sans
+    adresse noreply, `user.email` expose l'adresse email réelle dans les
+    métadonnées auteur/committer de chaque commit — visible publiquement une
+    fois le dépôt poussé. `git_runner` (le `_git()` de l'appelant, cwd déjà
+    fixé sur le dépôt) donne l'email EFFECTIF (local au dépôt tout juste
+    initialisé, ou à défaut la config globale — `git config user.email` sans
+    `--local` ni `--global` résout déjà cette priorité). S'il correspond déjà
+    au format noreply GitHub (`*@users.noreply.github.com` — cas normal sur
+    cette machine), ne fait rien et renvoie None : ce garde-fou doit rester
+    silencieux quand tout va bien. Sinon, récupère la vraie adresse noreply
+    du compte via `gh api user` (`id`+`login`, format documenté par GitHub :
+    `<id>+<login>@users.noreply.github.com` — c'est exactement celle déjà en
+    config globale sur cette machine) et la pose en config LOCALE au dépôt
+    (jamais globale, pour ne pas modifier silencieusement un réglage qui
+    dépasse ce projet). Renvoie l'adresse posée, ou None si déjà correcte OU
+    si `gh api user` échoue (pas de compte accessible — la création du
+    projet ne doit pas échouer pour autant, le commit part alors avec
+    l'email trouvé tel quel)."""
+    email_actuel = git_runner("config", "user.email").stdout.strip()
+    if email_actuel.endswith("@users.noreply.github.com"):
+        return None
+
+    identifiant = gh("api", "user", "-q", ".id")
+    login = gh("api", "user", "-q", ".login")
+    if identifiant.returncode != 0 or login.returncode != 0:
+        return None
+    identifiant, login = identifiant.stdout.strip(), login.stdout.strip()
+    if not identifiant or not login:
+        return None
+
+    email_noreply = f"{identifiant}+{login}@users.noreply.github.com"
+    git_runner("config", "user.email", email_noreply)
+    return email_noreply
+
+
 def initialiser_git(rep: str, depot: str) -> dict:
     """Initialise le dépôt git local du répertoire de travail (issue #257) :
     `git init` sur la branche `master`, `git remote add origin` en **HTTPS**
# ── Zone modifiée : ligne 387 (7 ligne(s)) dans l'ancienne version → ligne 423 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -387,7 +423,7 @@ def initialiser_git(rep: str, depot: str) -> dict:
     rep_path = Path(rep).expanduser()
     if (rep_path / ".git").exists():
         return {"ok": True, "deja_git": True, "push_ok": None,
-                "contenu_preexistant": [],
+                "contenu_preexistant": [], "email_corrige": None,
                 "detail": "déjà un dépôt git — inchangé.",
                 "commande_manuelle": None}
 
# ── Zone modifiée : ligne 403 (7 ligne(s)) dans l'ancienne version → ligne 439 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -403,7 +439,7 @@ def initialiser_git(rep: str, depot: str) -> dict:
     res_init = _git("init", "-b", "master")
     if res_init.returncode != 0:
         return {"ok": False, "deja_git": False, "push_ok": None,
-                "contenu_preexistant": [],
+                "contenu_preexistant": [], "email_corrige": None,
                 "detail": f"échec de git init : {res_init.stderr.strip()}",
                 "commande_manuelle": _commandes_git_manuelles(rep_path, depot,
                                                                complet=True)}
# ── Zone modifiée : ligne 423 (10 ligne(s)) dans l'ancienne version → ligne 459 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -423,10 +459,19 @@ def initialiser_git(rep: str, depot: str) -> dict:
     # n'a jamais atteint l'index et ne compte donc pas comme préexistant.
     preexistants = _fichiers_suivis_preexistants(rep_path, _git)
 
+    # Filet de sécurité issue #530 : avant le tout premier commit, s'assurer
+    # que l'email git effectif est bien l'adresse noreply GitHub du compte —
+    # sans quoi l'adresse réelle de l'utilisateur se retrouverait exposée
+    # dans les métadonnées auteur/committer, publiquement une fois poussé.
+    email_corrige = _corriger_email_noreply(_git)
+
     _git("commit", "-m", "Initialisation du projet", "--allow-empty")
 
     detail = (f"git init (branche master), remote origin {url} (HTTPS), "
               ".gitignore minimal, commit initial")
+    if email_corrige:
+        detail += (f" — ⚠ email git réel détecté, corrigé en local sur ce "
+                   f"dépôt : {email_corrige}")
 
     if preexistants:
         detail += (f" — ⚠ push automatique retenu : {len(preexistants)} "
# ── Zone modifiée : ligne 435 (7 ligne(s)) dans l'ancienne version → ligne 480 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -435,7 +480,8 @@ def initialiser_git(rep: str, depot: str) -> dict:
                    f"{', …' if len(preexistants) > 10 else ''}) ; ce contenu "
                    "n'a pas été relu.")
         return {"ok": True, "deja_git": False, "push_ok": None,
-                "contenu_preexistant": preexistants, "detail": detail,
+                "contenu_preexistant": preexistants, "email_corrige": email_corrige,
+                "detail": detail,
                 "commande_manuelle": _commandes_git_manuelles(rep_path, depot,
                                                                complet=False)}
 
# ── Zone modifiée : ligne 452 (8 ligne(s)) dans l'ancienne version → ligne 498 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -452,8 +498,8 @@ def initialiser_git(rep: str, depot: str) -> dict:
                                                        complet=False)
 
     return {"ok": True, "deja_git": False, "push_ok": push_ok,
-            "contenu_preexistant": [], "detail": detail,
-            "commande_manuelle": commande_manuelle}
+            "contenu_preexistant": [], "email_corrige": email_corrige,
+            "detail": detail, "commande_manuelle": commande_manuelle}
 
 
 def mettre_a_jour_doc(nom: str, depot: str, rep: str, perimetre: str) -> dict:
# ── Zone modifiée : ligne 794 (6 ligne(s)) dans l'ancienne version → ligne 840 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -794,6 +840,9 @@ def etape_git(depot: str, rep: str) -> dict:
                 "commande_manuelle": cmd}
 
     resultat = initialiser_git(rep, depot)
+    if resultat.get("email_corrige"):
+        print(f"   ⚠️  Email git réel détecté (pas l'adresse noreply GitHub) "
+              f"— corrigé en config LOCALE à ce dépôt : {resultat['email_corrige']}")
     if resultat["push_ok"]:
         print("   ✓ dépôt initialisé (branche master, remote HTTPS) et poussé "
               "sur origin/master.")
