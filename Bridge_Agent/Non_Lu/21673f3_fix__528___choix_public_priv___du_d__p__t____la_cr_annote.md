21673f3

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 21673f3
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 11 23:29:34 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #528 : choix public/privé du dépôt à la création d'un nouveau projet
    
    creer_depot() n'imposait plus --public en dur : nouveau paramètre
    `public: bool = True` (défaut cohérent avec le comportement historique)
    déterminant --public/--private côté `gh repo create`. Exposé dans les deux
    points d'entrée : CLI (etape_depot(), question « Dépôt public (non = privé) »
    après confirmation de création) et formulaire web (case à cocher « Dépôt
    public » dans templates/index.html, visible seulement quand le dépôt cible
    n'existe pas encore — même logique que la case « Créer le dépôt »),
    transmis via app/nouveau_projet.py::creer_nouveau_projet() → creer_projet()
    → creer_depot(). Docstrings/messages qui présupposaient un dépôt public
    (nouveau_projet.py, static/js/app.js) mis à jour. Aucune étape ultérieure
    (initialiser_git, remote, push) ne suppose un accès public : tout passe par
    gh/git en HTTPS authentifié via GH_TOKEN, donc un dépôt privé fonctionne à
    l'identique côté interface, seule condition que ce token ait les
    permissions nécessaires sur ce dépôt. §13 de BRIDGE_AGENT_DOC.md et
    CHANGELOG.md complétés.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 65232a7..4270de8 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1055 (8 ligne(s)) dans l'ancienne version → ligne 1055 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1055,8 +1055,21 @@ reproductible :
 deux, mêmes étapes, mêmes messages, comportement idempotent identique :
 
 1. **Dépôt GitHub** : `gh repo view` ; s'il n'existe pas encore, `gh repo create
-   <owner>/<Nom> --public` (sauf décoché côté web). S'il existe déjà →
-   installation dessus, rien recréé.
+   <owner>/<Nom> --public` ou `--private` selon le choix fait à la création
+   (issue #528 ; défaut **public**, cohérent avec le comportement historique —
+   CLI : question « Dépôt public (non = privé) » juste après la confirmation
+   de création ; web : case à cocher « Dépôt public », visible seulement
+   quand le dépôt n'existe pas encore). Sans effet si le dépôt existe déjà —
+   sa visibilité n'est pas modifiée. Un dépôt privé fonctionne à l'identique
+   côté Bridge_Agent : l'interface (affichage des résultats, création
+   d'issues, `app/issues.py`) passe systématiquement par `gh` authentifié via
+   `GH_TOKEN`, jamais par un accès public anonyme — seule condition, que ce
+   token ait les permissions nécessaires sur ce dépôt (sinon `gh repo create
+   --private` échoue immédiatement à l'étape 1, ou tout appel `gh`/`git`
+   ultérieur échoue avec une erreur d'authentification explicite). Si
+   décoché côté web (`creer_depot_si_absent`), la création est sautée
+   entièrement — auquel cas le choix public/privé est sans objet. S'il
+   existe déjà → installation dessus, rien recréé.
 2. **`configs/<nom>.conf`** généré depuis le gabarit interne (dépôt, répertoire
    de travail, périmètre, topic ntfy, couleur d'accent §121, etc.).
 3. **Labels GitHub** requis (§4) créés sur le dépôt cible, idempotent (les
# (diff du fichier suivant)
diff --git a/CHANGELOG.md b/CHANGELOG.md
# (index — ignorable)
index 0ecbea9..2f509a8 100644
# (avant — fichier suivant)
--- a/CHANGELOG.md
# (après — fichier suivant)
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (25 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,25 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 11 septembre 2026 — issue #528
+
+`creer_depot()` (`nouveau_projet.py`) n'était plus systématiquement `--public`
+codé en dur : nouveau paramètre `public: bool = True` déterminant le flag
+`gh repo create` (`--public`/`--private`), défaut cohérent avec le
+comportement historique. Exposé dans les deux points d'entrée existants :
+CLI (`etape_depot()`, question « Dépôt public (non = privé) » juste après la
+confirmation de création) et formulaire web (case à cocher « Dépôt public »
+dans `templates/index.html`, visible seulement quand le dépôt cible n'existe
+pas encore, comme la case « Créer le dépôt » dont elle dépend) → transmis à
+`app/nouveau_projet.py`/`creer_projet()` puis à `creer_depot()`. Aucune étape
+ultérieure (`initialiser_git()`, clonage, remote, push) ne suppose un accès
+public : tout passe par `gh`/`git` en HTTPS authentifié via `GH_TOKEN`
+(`_url_https()`, §9), donc un dépôt privé fonctionne à l'identique côté
+interface — seule condition, que ce token ait les permissions nécessaires
+sur ce dépôt. Commentaires/messages qui présupposaient un dépôt public
+(docstrings, messages CLI, encarts web) mis à jour en conséquence. §13 de la
+doc complété.
+
 ## 7 septembre 2026 — issue #521
 
 Traçabilité minimale sur `logs/historique_durees.json` et
# (diff du fichier suivant)
diff --git a/app/nouveau_projet.py b/app/nouveau_projet.py
# (index — ignorable)
index b29dffa..fb7f40e 100644
# (avant — fichier suivant)
--- a/app/nouveau_projet.py
# (après — fichier suivant)
+++ b/app/nouveau_projet.py
# ── Zone modifiée : ligne 80 (5 ligne(s)) dans l'ancienne version → ligne 80 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -80,5 +80,9 @@ def creer_nouveau_projet():
         # revalide contre les couleurs encore libres (issue #121) : une valeur
         # vide ou déjà prise retombe sur la première disponible.
         couleur               = data.get("couleur", ""),
+        # Visibilité du dépôt s'il doit être créé (issue #528) ; défaut public,
+        # cohérent avec le comportement historique. Sans effet si le dépôt
+        # existe déjà.
+        public                = bool(data.get("public", True)),
     )
     return jsonify(resultat), (200 if resultat.get("succes") else 400)
# (diff du fichier suivant)
diff --git a/nouveau_projet.py b/nouveau_projet.py
# (index — ignorable)
index 257234f..a0ae19f 100755
# (avant — fichier suivant)
--- a/nouveau_projet.py
# (après — fichier suivant)
+++ b/nouveau_projet.py
# ── Zone modifiée : ligne 221 (9 ligne(s)) dans l'ancienne version → ligne 221 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -221,9 +221,11 @@ def depot_existe(depot: str) -> bool:
     return gh("repo", "view", depot).returncode == 0
 
 
-def creer_depot(depot: str, nom: str) -> tuple[bool, str]:
-    """Crée le dépôt public. Renvoie (succès, message d'erreur éventuel)."""
-    res = gh("repo", "create", depot, "--public",
+def creer_depot(depot: str, nom: str, public: bool = True) -> tuple[bool, str]:
+    """Crée le dépôt, public ou privé selon `public` (issue #528 ; défaut
+    public, cohérent avec le comportement historique). Renvoie (succès,
+    message d'erreur éventuel)."""
+    res = gh("repo", "create", depot, "--public" if public else "--private",
              "--description", f"Projet {nom} — piloté via Bridge_Agent")
     return res.returncode == 0, res.stderr.strip()
 
# ── Zone modifiée : ligne 334 (7 ligne(s)) dans l'ancienne version → ligne 336 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -334,7 +336,8 @@ def _fichiers_suivis_preexistants(rep_path: Path, git_runner) -> list[str]:
     `*.pyc`, `*.log`, `.env`) n'a jamais atteint l'index et n'apparaît donc
     plus ici — c'est ce que git commit/push emporterait réellement. Une
     liste non vide signale un répertoire qui contenait déjà du contenu
-    SUIVI avant l'initialisation git : le dépôt étant créé **public**, ce
+    SUIVI avant l'initialisation git : le dépôt étant nouvellement créé
+    (public ou privé selon le choix fait à sa création — issue #528), ce
     contenu ne doit pas être publié sans relecture. `git_runner` est le
     point d'entrée `_git()` de l'appelant, déjà borné par TIMEOUT_GIT_LOCAL
     et tolérant au dépassement — réutilisé tel quel, pas de second timeout à
# ── Zone modifiée : ligne 429 (8 ligne(s)) dans l'ancienne version → ligne 432 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -429,8 +432,8 @@ def initialiser_git(rep: str, depot: str) -> dict:
         detail += (f" — ⚠ push automatique retenu : {len(preexistants)} "
                    "fichier(s) préexistant(s) détecté(s) dans le répertoire "
                    f"({', '.join(preexistants[:10])}"
-                   f"{', …' if len(preexistants) > 10 else ''}) ; le dépôt "
-                   "est public et ce contenu n'a pas été relu.")
+                   f"{', …' if len(preexistants) > 10 else ''}) ; ce contenu "
+                   "n'a pas été relu.")
         return {"ok": True, "deja_git": False, "push_ok": None,
                 "contenu_preexistant": preexistants, "detail": detail,
                 "commande_manuelle": _commandes_git_manuelles(rep_path, depot,
# ── Zone modifiée : ligne 486 (11 ligne(s)) dans l'ancienne version → ligne 489 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -486,11 +489,14 @@ def mettre_a_jour_doc(nom: str, depot: str, rep: str, perimetre: str) -> dict:
 
 def creer_projet(nom: str, depot: str = "", rep: str = "", perimetre: str = "",
                  topic: str = "", script_bip: str = "", avec_specs: bool = False,
-                 creer_depot_si_absent: bool = True, couleur: str = "") -> dict:
+                 creer_depot_si_absent: bool = True, couleur: str = "",
+                 public: bool = True) -> dict:
     """Orchestrateur non interactif appelé par la route Flask. Enchaîne les
     mêmes étapes que le script CLI (dépôt, .conf, labels, contexte, doc) et
     renvoie un compte-rendu structuré : {succes, nom, depot, rep, perimetre,
-    depot_existait, etapes:[{etape, ok, detail}], erreur}."""
+    depot_existait, etapes:[{etape, ok, detail}], erreur}. `public` (issue
+    #528) détermine la visibilité du dépôt s'il doit être créé ; sans effet
+    si le dépôt existe déjà (sa visibilité n'est alors pas modifiée)."""
     nom = (nom or "").strip().lower()
     if not nom:
         return {"succes": False, "erreur": "Un nom de projet est requis.", "etapes": []}
# ── Zone modifiée : ligne 526 (7 ligne(s)) dans l'ancienne version → ligne 532 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -526,7 +532,7 @@ def creer_projet(nom: str, depot: str = "", rep: str = "", perimetre: str = "",
             return {"succes": False, "etapes": etapes, "depot": depot,
                     "erreur": f"Le dépôt {depot} n'existe pas. Cochez la création "
                               "du dépôt pour continuer."}
-        ok, err = creer_depot(depot, nom)
+        ok, err = creer_depot(depot, nom, public=public)
         depot_existait = False
         if not ok:
             etapes.append({"etape": "Dépôt GitHub", "ok": False,
# ── Zone modifiée : ligne 534 (7 ligne(s)) dans l'ancienne version → ligne 540 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -534,7 +540,7 @@ def creer_projet(nom: str, depot: str = "", rep: str = "", perimetre: str = "",
             return {"succes": False, "etapes": etapes, "depot": depot,
                     "erreur": f"Impossible de créer {depot} : {err}"}
         etapes.append({"etape": "Dépôt GitHub", "ok": True,
-                       "detail": f"{depot} créé (public)."})
+                       "detail": f"{depot} créé ({'public' if public else 'privé'})."})
 
     # 2. Fichier configs/<nom>.conf.
     ecrire_conf(nom, depot, rep, perimetre, topic, script_bip, couleur)
# ── Zone modifiée : ligne 614 (7 ligne(s)) dans l'ancienne version → ligne 620 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -614,7 +620,8 @@ def etape_nom() -> str:
 
 def etape_depot(nom: str) -> tuple[str, bool]:
     """Renvoie (depot, existait_deja). Crée le dépôt s'il n'existe pas et que
-    l'utilisateur confirme."""
+    l'utilisateur confirme — public ou privé selon son choix (issue #528),
+    défaut public pour rester cohérent avec le comportement historique."""
     titre("2. Dépôt GitHub cible")
     # Proposition par défaut : owner du dépôt courant + nom capitalisé.
     depot = demander("Dépôt GitHub (owner/nom)", depot_defaut(nom))
# ── Zone modifiée : ligne 625 (12 ligne(s)) dans l'ancienne version → ligne 632 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -625,12 +632,14 @@ def etape_depot(nom: str) -> tuple[str, bool]:
         return depot, True
 
     print(f"   Le dépôt {depot} n'existe pas encore.")
-    if not demander_oui_non(f"Créer {depot} (public)", defaut=True):
+    if not demander_oui_non(f"Créer {depot}", defaut=True):
         print("   Abandon : impossible de continuer sans dépôt cible.")
         sys.exit(1)
 
-    print(f"   Création de {depot}…")
-    ok, err = creer_depot(depot, nom)
+    public = demander_oui_non("Dépôt public (non = privé)", defaut=True)
+
+    print(f"   Création de {depot} ({'public' if public else 'privé'})…")
+    ok, err = creer_depot(depot, nom, public=public)
     if not ok:
         print(f"   ❌ Échec de la création : {err}")
         sys.exit(1)
# ── Zone modifiée : ligne 785 (9 ligne(s)) dans l'ancienne version → ligne 794 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -785,9 +794,8 @@ def etape_git(depot: str, rep: str) -> dict:
               "sur origin/master.")
     elif resultat["contenu_preexistant"]:
         print("   ✓ dépôt initialisé, commit local créé.")
-        print("   ⚠️  push NON déclenché : le dépôt est public et le "
-              "répertoire contenait déjà du contenu non relu. Fichiers "
-              "préexistants détectés :")
+        print("   ⚠️  push NON déclenché : le répertoire contenait déjà du "
+              "contenu non relu. Fichiers préexistants détectés :")
         for f in resultat["contenu_preexistant"][:10]:
             print(f"      - {f}")
         if len(resultat["contenu_preexistant"]) > 10:
# ── Zone modifiée : ligne 978 (7 ligne(s)) dans l'ancienne version → ligne 986 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -978,7 +986,7 @@ def main() -> None:
     elif git_res["contenu_preexistant"]:
         print(f"   Dépôt git local : initialisé, commit local — push NON "
               f"automatique ({len(git_res['contenu_preexistant'])} fichier(s) "
-              "préexistant(s), dépôt public non relu)")
+              "préexistant(s) non relu(s))")
     elif git_res["ok"]:
         print("   Dépôt git local : initialisé, commit local — push manuel requis")
     else:
# ── Zone modifiée : ligne 992 (8 ligne(s)) dans l'ancienne version → ligne 1000 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -992,8 +1000,8 @@ def main() -> None:
           "prompt CCL (plafonné à 4000 caractères).")
     if git_res.get("commande_manuelle"):
         if git_res.get("contenu_preexistant"):
-            print("   • Push initial volontairement NON déclenché — dépôt "
-                  "public, contenu suivant non relu :")
+            print("   • Push initial volontairement NON déclenché — contenu "
+                  "préexistant non relu :")
             for f in git_res["contenu_preexistant"][:10]:
                 print(f"       - {f}")
             if len(git_res["contenu_preexistant"]) > 10:
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index f74c835..4e3d826 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 5458 (6 ligne(s)) dans l'ancienne version → ligne 5458 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5458,6 +5458,8 @@ function ouvrirNouveauProjet() {
   document.getElementById('np-specs').checked = false;
   document.getElementById('np-creer-depot').checked = true;
   document.getElementById('np-creer-depot-ligne').style.display = 'none';
+  document.getElementById('np-public').checked = true;
+  document.getElementById('np-public-ligne').style.display = 'none';
   document.getElementById('np-nom-msg').textContent = '';
   document.getElementById('np-depot-msg').textContent = '';
   document.getElementById('np-compte-rendu').style.display = 'none';
# ── Zone modifiée : ligne 5585 (19 ligne(s)) dans l'ancienne version → ligne 5587 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5585,19 +5587,23 @@ async function npVerifier() {
 function npAfficherEtatDepot(r) {
   const depotMsg   = document.getElementById('np-depot-msg');
   const ligneCreer = document.getElementById('np-creer-depot-ligne');
+  const lignePublic = document.getElementById('np-public-ligne');
   if (!r.nom_valide || !r.depot) {
     depotMsg.textContent = '';
     ligneCreer.style.display = 'none';
+    lignePublic.style.display = 'none';
     return;
   }
   if (r.depot_existe) {
     depotMsg.textContent = '✓ ' + r.depot + ' existe déjà → installation dessus (pas de recréation).';
     depotMsg.style.color = '#2e7d32';
     ligneCreer.style.display = 'none';
+    lignePublic.style.display = 'none';
   } else {
     depotMsg.textContent = 'ℹ ' + r.depot + " n'existe pas encore.";
     depotMsg.style.color = '#8a6d00';
     ligneCreer.style.display = 'block';
+    lignePublic.style.display = 'block';
   }
 }
 
# ── Zone modifiée : ligne 5630 (6 ligne(s)) dans l'ancienne version → ligne 5636 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5630,6 +5636,7 @@ async function soumettreNouveauProjet() {
     couleur:   npCouleurChoisie,
     avec_specs: document.getElementById('np-specs').checked,
     creer_depot_si_absent: document.getElementById('np-creer-depot').checked,
+    public: document.getElementById('np-public').checked,
   };
 
   let res;
# ── Zone modifiée : ligne 5712 (11 ligne(s)) dans l'ancienne version → ligne 5719 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5712,11 +5719,10 @@ function afficherRappelGit(nom) {
 //  2. Si l'initialisation git du répertoire de travail n'a pas pu se
 //     terminer (push initial échoué), OU si le push a été VOLONTAIREMENT
 //     retenu parce que le répertoire contenait déjà du contenu non relu
-//     (issue #258 — le dépôt est public), les commandes manuelles
-//     nécessaires. Les deux cas partagent commande_manuelle mais doivent
-//     rester des messages distincts : le premier est un échec, le second une
-//     retenue délibérée — les confondre laisserait croire à une erreur là où
-//     rien n'a raté.
+//     (issue #258), les commandes manuelles nécessaires. Les deux cas
+//     partagent commande_manuelle mais doivent rester des messages distincts :
+//     le premier est un échec, le second une retenue délibérée — les
+//     confondre laisserait croire à une erreur là où rien n'a raté.
 // Encart visuellement distinct (bordure bleue) de celui de afficherRappelGit
 // (bordure orange) : c'est précisément la confusion entre « dépôt
 // Bridge_Agent » et « dépôt du projet créé » qui a fait passer inaperçu le
# ── Zone modifiée : ligne 5735 (8 ligne(s)) dans l'ancienne version → ligne 5741 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5735,8 +5741,8 @@ function afficherRappelProjet(res) {
   } else if (res.git_contenu_preexistant && res.git_contenu_preexistant.length) {
     const noms = res.git_contenu_preexistant.slice(0, 10);
     const reste = res.git_contenu_preexistant.length - noms.length;
-    html += '<div>⚠ Push <b>volontairement non déclenché</b> : le dépôt est '
-          + '<b>public</b> et le répertoire contenait déjà '
+    html += '<div>⚠ Push <b>volontairement non déclenché</b> : le répertoire '
+          + 'contenait déjà '
           + res.git_contenu_preexistant.length + ' fichier(s) non relu(s) — '
           + "ce n'est pas un échec, rien n'a été publié :</div>"
           + '<pre>' + escapeHtml(noms.join('\n'))
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 52950f5..6097b19 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 606 (7 ligne(s)) dans l'ancienne version → ligne 606 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -606,7 +606,13 @@
     <label id="np-creer-depot-ligne"
            style="display:none;font-size:13px;color:#333;margin-bottom:12px">
       <input type="checkbox" id="np-creer-depot" checked>
-      Créer le dépôt (public) s'il n'existe pas encore
+      Créer le dépôt s'il n'existe pas encore
+    </label>
+
+    <label id="np-public-ligne"
+           style="display:none;font-size:13px;color:#333;margin-bottom:12px">
+      <input type="checkbox" id="np-public" checked>
+      Dépôt public (décocher pour un dépôt privé)
     </label>
 
     <div class="champ" style="margin-bottom:12px">
