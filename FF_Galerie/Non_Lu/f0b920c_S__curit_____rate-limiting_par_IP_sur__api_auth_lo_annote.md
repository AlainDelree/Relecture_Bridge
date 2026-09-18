f0b920c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f0b920c
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 16:24:06 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Sécurité : rate-limiting par IP sur /api/auth/login + MDP 12 car. min (#87)
    
    - worker.js : second compteur d'échecs indexé sur CF-Connecting-IP
      (auth/tentatives-ip/<ip>, seuil 30 échecs / fenêtre 1 h via TTL KV),
      cumulé avec le compteur par nom existant (5 échecs / 15 min) qui reste
      inchangé. En-tête IP absent (curl local) → aucun comptage, login OK.
    - gerer-utilisateurs.sh : refuse un mot de passe < 12 caractères et
      redemande la saisie au lieu de sortir en erreur.
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/data-worker/gerer-utilisateurs.sh b/data-worker/gerer-utilisateurs.sh
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 550f22d..61a73d6 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/data-worker/gerer-utilisateurs.sh
# ── Version APRÈS ce commit.
+++ b/data-worker/gerer-utilisateurs.sh
# ── Zone modifiée : ligne 55 (8 ligne(s)) dans l'ancienne version → ligne 55 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -55,8 +55,18 @@ echo "Création/mise à jour du compte « $NOM »"
 echo "(le mot de passe et le token ne s'afficheront pas à l'écran)"
 echo
 
-read -r -s -p "Mot de passe pour $NOM : " MOT_DE_PASSE
-echo
+# Le mot de passe doit faire au moins 12 caractères : en deçà, le PBKDF2
+# du worker ne protège plus grand-chose. On redemande la saisie plutôt que
+# de sortir en erreur.
+while true; do
+  read -r -s -p "Mot de passe pour $NOM (12 caractères minimum) : " MOT_DE_PASSE
+  echo
+  if [[ "${#MOT_DE_PASSE}" -lt 12 ]]; then
+    echo "  → trop court (${#MOT_DE_PASSE} caractère(s)), il en faut au moins 12. Recommence."
+    continue
+  fi
+  break
+done
 read -r -s -p "Token GitHub pour $NOM (celui qu'il/elle utilisera) : " TOKEN
 echo
 
# (diff du fichier suivant)
diff --git a/data-worker/worker.js b/data-worker/worker.js
# (index — ignorable)
index 18a4dc7..b342575 100644
# (avant — fichier suivant)
--- a/data-worker/worker.js
# (après — fichier suivant)
+++ b/data-worker/worker.js
# ── Zone modifiée : ligne 171 (7 ligne(s)) dans l'ancienne version → ligne 171 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -171,7 +171,8 @@ async function archiverVersGitHub(cle, contenuTexte, branche, message, env) {
 
    Stockage KV :
      auth/utilisateurs/<nom>  → { hash, sel, iterations, token, ff_secret? }
-     auth/tentatives/<nom>    → { echecs }  (TTL 15 min, anti brute-force)
+     auth/tentatives/<nom>    → { echecs }  (TTL 15 min, anti brute-force par NOM : 5 échecs)
+     auth/tentatives-ip/<ip>  → { echecs }  (TTL 1 h, anti brute-force par IP : 30 échecs)
 
    - POST /api/auth/creer-utilisateur  (protégé par FF_DATA_SECRET, comme
      PUT/DELETE) : { nom, mot_de_passe, token, ff_secret? } → hache le mot
# ── Zone modifiée : ligne 213 (6 ligne(s)) dans l'ancienne version → ligne 214 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -213,6 +214,15 @@ function normaliserNomUtilisateur(nom) {
   return (nom || '').trim().toLowerCase().replace(/[^a-z0-9_-]/g, '');
 }
 
+/* Normalise une adresse IP (en-tête CF-Connecting-IP) en identifiant de clé
+   KV sûr : on garde chiffres/lettres (IPv6), point, deux-points, tiret,
+   underscore. Renvoie '' si l'en-tête est absent/vide — l'appelant
+   n'applique alors AUCUN comptage par IP (cas des tests locaux au curl, où
+   Cloudflare ne pose pas cet en-tête). */
+function normaliserIp(ip) {
+  return (ip || '').trim().toLowerCase().replace(/[^a-z0-9.:_-]/g, '');
+}
+
 async function gererCreationUtilisateur(request, env) {
   if (!estAutorise(request, env)) return reponseJSON({ erreur: 'Non autorisé' }, 401);
   let corps;
# ── Zone modifiée : ligne 238 (6 ligne(s)) dans l'ancienne version → ligne 248 (27 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -238,6 +248,27 @@ async function gererLogin(request, env) {
   const motDePasse = corps.mot_de_passe || '';
   if (!nom || !motDePasse) return reponseJSON({ erreur: 'Identifiants manquants' }, 400);
 
+  /* Anti brute-force PAR IP (durcissement en profondeur, CUMULÉ avec le
+     compteur par nom ci-dessous — les deux blocages sont indépendants). Il
+     couvre l'angle mort du compteur par nom : une attaque essayant un mot
+     de passe courant contre de nombreux noms différents ne déclenche jamais
+     le blocage par nom. Seuil volontairement PERMISSIF (30 échecs par
+     heure, toutes cibles confondues), pour ne pas gêner un utilisateur
+     légitime maladroit tout en cassant un balayage massif.
+     CF-Connecting-IP est posé par Cloudflare, non falsifiable côté worker.
+     S'il est absent (tests locaux au curl), normaliserIp renvoie '' et on
+     ne compte simplement pas — le login n'échoue jamais pour cette raison. */
+  const ip = normaliserIp(request.headers.get('CF-Connecting-IP'));
+  const cleTentativesIp = ip ? 'auth/tentatives-ip/' + ip : null;
+  let echecsIp = 0;
+  if (cleTentativesIp) {
+    const brutIp = await env.FF_DATA.get(cleTentativesIp);
+    echecsIp = brutIp ? (JSON.parse(brutIp).echecs || 0) : 0;
+    if (echecsIp >= 30) {
+      return reponseJSON({ erreur: 'Trop de tentatives échouées depuis cette adresse, réessayez plus tard' }, 429);
+    }
+  }
+
   const cleTentatives = 'auth/tentatives/' + nom;
   const brutTentatives = await env.FF_DATA.get(cleTentatives);
   const echecsActuels = brutTentatives ? (JSON.parse(brutTentatives).echecs || 0) : 0;
# ── Zone modifiée : ligne 260 (6 ligne(s)) dans l'ancienne version → ligne 291 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -260,6 +291,12 @@ async function gererLogin(request, env) {
 
   if (!valide) {
     await env.FF_DATA.put(cleTentatives, JSON.stringify({ echecs: echecsActuels + 1 }), { expirationTtl: 900 });
+    /* Incrémente aussi le compteur par IP (TTL 1 h) quand l'en-tête est
+       présent. On ne le remet PAS à zéro sur un login réussi : il agrège
+       plusieurs noms, le laisser expirer naturellement est plus prudent. */
+    if (cleTentativesIp) {
+      await env.FF_DATA.put(cleTentativesIp, JSON.stringify({ echecs: echecsIp + 1 }), { expirationTtl: 3600 });
+    }
     return reponseJSON({ erreur: 'Identifiants invalides' }, 401);
   }
 
