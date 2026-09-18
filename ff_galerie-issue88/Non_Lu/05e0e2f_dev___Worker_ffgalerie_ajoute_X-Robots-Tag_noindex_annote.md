05e0e2f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 05e0e2f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 16:26:10 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    dev : Worker ffgalerie ajoute X-Robots-Tag noindex (anti-indexation) (#88)
    
    Empêche l'indexation de dev.frederiqueferette.be sans toucher au HTML ni à
    _headers (partagés avec la prod) et sans affecter la prod (servie par GitHub
    Pages, pas par ce Worker).
    
    - worker.js (nouveau) : sert les assets via env.ASSETS.fetch() (html_handling
      conservé, redirect /x.html->/x non cassé) puis ajoute X-Robots-Tag:
      noindex, nofollow sur toutes les réponses.
    - wrangler.toml : main + [assets] binding ASSETS + run_worker_first=true.
    - .assetsignore : exclut worker.js du service d'assets.
    
    Non déployé (Alain déploie après relecture). node --check : OK.
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.assetsignore b/.assetsignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 605a91a..0b395f3 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.assetsignore
# ── Version APRÈS ce commit.
+++ b/.assetsignore
# ── Zone modifiée : ligne 3 (6 ligne(s)) dans l'ancienne version → ligne 3 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3,6 +3,7 @@
 node_modules
 node_modules/**
 wrangler.toml
+worker.js
 _headers
 *.md
 .gitignore
# (diff du fichier suivant)
diff --git a/CHANGELOG-88.md b/CHANGELOG-88.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..a72dcab
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/CHANGELOG-88.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (44 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,44 @@
+# Changelog — Issue #88
+
+## Empêcher l'indexation de l'environnement dev (#88)
+
+Ajout d'un en-tête `X-Robots-Tag: noindex, nofollow` sur toutes les réponses
+de l'environnement dev (`dev.frederiqueferette.be`), sans toucher au HTML ni à
+`_headers` (partagés avec la prod) et sans affecter la prod.
+
+### Contexte
+- `index.html` / `galerie.html` portent en dur `<meta name="robots"
+  content="index, follow">`, identiques sur `dev` et `main`.
+- La prod (`frederiqueferette.be`) est servie par **GitHub Pages**
+  (`.github/workflows/deploy.yml`) et doit rester indexable.
+- Dev est servi par le **Worker Cloudflare `ffgalerie`**
+  (`.github/workflows/deploy-dev.yml` → `wrangler deploy` depuis la racine sur
+  push vers `dev`), dont la config se limitait à un bloc `[assets]` sans script.
+- Correction faite au niveau du Worker : elle ne cible donc que dev.
+
+### Modifications
+- **`worker.js`** (nouveau) : Worker racine minimal. Invoqué pour toutes les
+  requêtes, il délègue le service du fichier à `env.ASSETS.fetch()` puis ajoute
+  `X-Robots-Tag: noindex, nofollow` sur la réponse. `env.ASSETS.fetch()`
+  conserve `html_handling` / `not_found_handling` : le redirect connu
+  `/x.html` → `/x` sur dev n'est **pas** cassé.
+- **`wrangler.toml`** : ajout de `main = "worker.js"` et, dans `[assets]`,
+  de `binding = "ASSETS"` + `run_worker_first = true`. Le bloc `[assets]` et
+  `directory = "./"` sont conservés.
+- **`.assetsignore`** : ajout de `worker.js` pour que la source du Worker ne
+  soit pas servie comme asset public à `/worker.js`.
+
+### Vérification
+- `node --check worker.js` : OK (validé en module ES, format Cloudflare Worker,
+  identique aux Workers existants `app-worker/` et `data-worker/`).
+- Non déployé (Alain déploie après relecture).
+
+### À vérifier par Alain après `wrangler deploy` (sur dev)
+1. `curl -sI https://dev.frederiqueferette.be/` → `x-robots-tag: noindex, nofollow`.
+2. `curl -sI https://dev.frederiqueferette.be/galerie.html` → redirect 301/308
+   vers `/galerie` toujours présent (non cassé) + en-tête.
+3. `curl -sI https://dev.frederiqueferette.be/galerie` → 200 + en-tête.
+4. Un asset non-HTML (`/favicon.ico`, `/assets/...`) → 200 + en-tête.
+5. Une URL inexistante → 404 inchangé + en-tête.
+6. Contrôle croisé : `https://frederiqueferette.be/` (prod) NE porte PAS
+   l'en-tête (reste indexable).
# (diff du fichier suivant)
diff --git a/worker.js b/worker.js
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..69d3a07
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/worker.js
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (54 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,54 @@
+/* ===========================================================================
+   FF_Galerie — Worker RACINE « ffgalerie » (sert dev.frederiqueferette.be)
+   ---------------------------------------------------------------------------
+   RÔLE : servir l'environnement de développement EXACTEMENT comme avant, mais
+   en ajoutant sur CHAQUE réponse un en-tête `X-Robots-Tag: noindex, nofollow`
+   pour empêcher toute indexation / suivi de liens de dev par les moteurs.
+
+   POURQUOI ICI (et pas dans _headers ou dans le HTML) : les fichiers HTML et
+   `_headers` sont partagés entre les branches `dev` et `main`. La prod
+   (frederiqueferette.be) est servie par GitHub Pages (workflow deploy.yml) et
+   DOIT rester indexable. Seul dev est servi par ce Worker Cloudflare
+   « ffgalerie » (workflow deploy-dev.yml, `wrangler deploy` depuis la racine
+   sur push vers `dev`). Poser l'en-tête ici cible donc dev, et dev seulement.
+
+   CE QUI CHANGE DANS LA CHAÎNE DE SERVICE DE DEV :
+     • AVANT : wrangler.toml ne contenait qu'un bloc [assets] sans script. Les
+       assets statiques étaient servis directement par le runtime Cloudflare.
+     • APRÈS : `main = "worker.js"` + `[assets] binding = "ASSETS"` +
+       `run_worker_first = true`. Le Worker est désormais invoqué pour TOUTES
+       les requêtes ; il délègue le service du fichier à `env.ASSETS.fetch()`
+       (le pipeline natif des assets), puis ajoute l'en-tête sur la réponse.
+
+   COMPORTEMENT PRÉSERVÉ (important) : `env.ASSETS.fetch()` applique la même
+   configuration `html_handling` / `not_found_handling` que le service direct.
+   Le redirect connu `/x.html` → `/x` sur dev est donc conservé tel quel — on
+   ne fait que rattacher l'en-tête à la réponse (y compris aux redirects 3xx
+   et aux 404). Mêmes fichiers servis, même gestion des chemins.
+
+   À VÉRIFIER PAR ALAIN APRÈS DÉPLOIEMENT (`wrangler deploy` sur dev) :
+     1. `curl -sI https://dev.frederiqueferette.be/` → présence de
+        `x-robots-tag: noindex, nofollow`.
+     2. `curl -sI https://dev.frederiqueferette.be/galerie.html` → toujours un
+        redirect (301/308) vers `/galerie` (redirect NON cassé), avec l'en-tête.
+     3. `curl -sI https://dev.frederiqueferette.be/galerie` → 200, HTML servi,
+        avec l'en-tête.
+     4. Un asset non-HTML (ex. `/assets/...` ou `/favicon.ico`) → 200 + en-tête.
+     5. Une URL inexistante → comportement 404 inchangé, en-tête présent.
+     6. Contrôle croisé : la PROD (https://frederiqueferette.be/) NE porte PAS
+        cet en-tête (elle reste indexable).
+   =========================================================================== */
+
+export default {
+  async fetch(request, env) {
+    // Service natif de l'asset : conserve html_handling (redirect /x.html→/x)
+    // et not_found_handling, exactement comme le service direct d'aujourd'hui.
+    const reponse = await env.ASSETS.fetch(request);
+
+    // Recopie la réponse pour rendre les en-têtes mutables, puis interdit
+    // indexation et suivi des liens sur TOUTES les réponses de dev.
+    const sortie = new Response(reponse.body, reponse);
+    sortie.headers.set('X-Robots-Tag', 'noindex, nofollow');
+    return sortie;
+  }
+};
# (diff du fichier suivant)
diff --git a/wrangler.toml b/wrangler.toml
# (index — ignorable)
index 5a1f686..350e21f 100644
# (avant — fichier suivant)
--- a/wrangler.toml
# (après — fichier suivant)
+++ b/wrangler.toml
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 1 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +1,12 @@
 name = 'ffgalerie'
+main = "worker.js"
 compatibility_date = "2026-06-08"
 
+# Le Worker (worker.js) est invoqué pour TOUTES les requêtes (run_worker_first)
+# afin d'ajouter X-Robots-Tag: noindex sur dev. Il délègue le service des
+# fichiers à env.ASSETS.fetch() (binding "ASSETS"), qui conserve html_handling
+# (redirect /x.html → /x) et not_found_handling. Voir worker.js pour le détail.
 [assets]
 directory = "./"
+binding = "ASSETS"
+run_worker_first = true
