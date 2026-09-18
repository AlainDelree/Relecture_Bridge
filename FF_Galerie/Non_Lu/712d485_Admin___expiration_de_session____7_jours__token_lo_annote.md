712d485

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 712d485
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 11:16:53 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Admin : expiration de session à 7 jours (token localStorage) (#85)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-85.md b/CHANGELOG-85.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..8015fdf
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-85.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,26 @@
+# CHANGELOG — issue #85
+
+## Expiration de session dans l'admin (token localStorage)
+
+- `assets/js/admin.js` : ajout d'une expiration de session bornée à 7 jours.
+  - Nouvelle constante nommée `DUREE_SESSION_MAX_MS` (7 jours) en haut du
+    fichier, ajustable sans chercher dans le code.
+  - Nouvelle clé de stockage `K.loginTs` (`ff_gh_token_login`) : horodatage
+    du dernier login, stocké à côté du token.
+  - Nouvelle fonction `verifierExpirationSession()`, appelée au démarrage
+    synchrone d'admin.js AVANT `reprendreSessionExistante()`. Si le token
+    présent remonte à plus de 7 jours, elle purge du `localStorage` le token,
+    le secret ff-data et l'horodatage, efface le garde-fou de session
+    (`K.auth`) et réaffiche l'écran de connexion avec un message rassurant
+    (« Ta session a expiré (plus de 7 jours). Reconnecte-toi pour
+    continuer. »), pas une erreur alarmante.
+  - Un token présent sans horodatage (session ouverte avant ce déploiement)
+    n'est PAS déconnecté brutalement : l'horodatage est initialisé à
+    maintenant et la fenêtre de 7 jours démarre au premier chargement.
+  - L'horodatage est rafraîchi à chaque connexion réussie par les deux
+    chemins : `connexionParMotDePasse()` (mot de passe) et `validerToken()`
+    (saisie manuelle du token).
+- Aucun autre flux d'authentification affecté : `reprendreSessionExistante()`
+  n'appelle toujours ni `chargerTout()` ni `initTexturesUI()` ; la nouvelle
+  fonction respecte la même contrainte (aucune dépendance aux modules chargés
+  après). `node --check` passe.
# (diff du fichier suivant)
diff --git a/assets/js/admin.js b/assets/js/admin.js
# (index — ignorable)
index 01c9cbc..641634a 100644
# (avant — fichier suivant)
--- a/assets/js/admin.js
# (après — fichier suivant)
+++ b/assets/js/admin.js
# ── Zone modifiée : ligne 91 (10 ligne(s)) dans l'ancienne version → ligne 91 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -91,10 +91,20 @@ const K = {
   auth:     ADMIN_CFG.prefix + '_auth',
   token:    'ff_gh_token',          /* token partagé — même repo */
   ffSecret: 'ff_data_secret',       /* secret ff-data — partagé, Fred uniquement */
+  loginTs:  'ff_gh_token_login',    /* horodatage du dernier login (expiration de session, #85) */
   mur_hist: ADMIN_CFG.prefix + '_mur_hist',
   cad_hist: ADMIN_CFG.prefix + '_cad_hist'
 };
 
+/* Expiration de session (issue #85). Le token GitHub réside sans expiration
+   native dans localStorage : sans backend, impossible de poser un cookie
+   HttpOnly qui expirerait tout seul — compromis assumé. On borne donc la
+   durée de vie de la session par un horodatage de dernier login (K.loginTs)
+   stocké à côté du token. Passé ce délai, verifierExpirationSession() purge
+   le token ET le secret ff-data au démarrage et réaffiche l'écran de
+   connexion. Constante ajustable ici, sans chercher dans le code. */
+const DUREE_SESSION_MAX_MS = 7 * 24 * 60 * 60 * 1000; /* 7 jours */
+
 const MUR_DEFAULTS = ['#2e2e2e','#1c1c1c','#2a2420','#2c2535','#1e3a2a','#3a2a1e','#e8e4dc','#f5f5f5'];
 const CAD_DEFAULTS = ['#3a3a3a','#c8a050','#f0f0f0','#1c1c1c','#5c3d2e'];
 
# ── Zone modifiée : ligne 362 (6 ligne(s)) dans l'ancienne version → ligne 372 (45 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -362,6 +372,45 @@ function entrerDansAdmin() {
    autres modules (admin-emailjs.js, etc.) ne soient chargés — le hook
    dédié dans admin.html (après le chargement de tous les modules) s'en
    charge déjà pour ce cas précis, exactement pour éviter cette course. */
+/* Expiration de session (issue #85) : appelée au démarrage synchrone
+   d'admin.js, AVANT reprendreSessionExistante(). Si un token est présent et
+   que le dernier login (K.loginTs) remonte à plus de DUREE_SESSION_MAX_MS,
+   on purge token + secret ff-data + horodatage du localStorage, on efface le
+   garde-fou de session (K.auth) et on réaffiche l'écran de connexion avec un
+   message rassurant (session expirée, se reconnecter) — pas une erreur
+   alarmante. Retourne true si la session a été purgée (l'appelant NE doit
+   alors PAS enchaîner sur reprendreSessionExistante).
+
+   Cas d'un token présent sans horodatage (session ouverte AVANT le déploiement
+   de cette fonctionnalité) : on ne déconnecte pas brutalement, on initialise
+   simplement l'horodatage à maintenant — la borne des 7 jours démarre au
+   premier chargement post-déploiement.
+
+   Comme reprendreSessionExistante(), cette fonction n'appelle NI chargerTout()
+   NI initTexturesUI() : elle ne fait que lire/nettoyer le localStorage et
+   basculer d'écran, sans dépendre des autres modules pas encore chargés. */
+function verifierExpirationSession() {
+  const tok = localStorage.getItem(K.token);
+  if (!tok) return false;                       /* rien à expirer */
+  const ts = parseInt(localStorage.getItem(K.loginTs) || '', 10);
+  if (!Number.isFinite(ts)) {                   /* session antérieure à #85 : on horodate sans déconnecter */
+    localStorage.setItem(K.loginTs, String(Date.now()));
+    return false;
+  }
+  if (Date.now() - ts < DUREE_SESSION_MAX_MS) return false; /* encore dans la fenêtre */
+  /* Session expirée : purge et retour à l'écran de connexion. */
+  localStorage.removeItem(K.token);
+  localStorage.removeItem(K.ffSecret);
+  localStorage.removeItem(K.loginTs);
+  sessionStorage.removeItem(K.auth);
+  token = '';
+  ffSecret = '';
+  afficherEcran('ecran-token');
+  const err = document.getElementById('auth-err');
+  if (err) err.textContent = 'Ta session a expiré (plus de 7 jours). Reconnecte-toi pour continuer.';
+  return true;
+}
+
 async function reprendreSessionExistante() {
   token = localStorage.getItem(K.token) || '';
   if (!token) { afficherEcran('ecran-token'); return; }
# ── Zone modifiée : ligne 975 (6 ligne(s)) dans l'ancienne version → ligne 1024 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -975,6 +1024,7 @@ async function connexionParMotDePasse() {
     const data = await rep.json();
     token = data.token;
     localStorage.setItem(K.token, token);
+    localStorage.setItem(K.loginTs, String(Date.now())); /* horodatage login (#85) */
     if (data.ff_secret) {
       ffSecret = data.ff_secret;
       localStorage.setItem(K.ffSecret, ffSecret);
# ── Zone modifiée : ligne 1003 (6 ligne(s)) dans l'ancienne version → ligne 1053 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1003,6 +1053,7 @@ async function validerToken() {
     });
     if (rep.status === 401) throw new Error('token révoqué ou invalide');
     localStorage.setItem(K.token, t);
+    localStorage.setItem(K.loginTs, String(Date.now())); /* horodatage login (#85) */
     sessionStorage.setItem(K.auth, '1');
     entrerDansAdmin();
   } catch (e) { $('token-err').textContent = 'Token invalide : ' + e.message; token = ''; }
# ── Zone modifiée : ligne 1574 (7 ligne(s)) dans l'ancienne version → ligne 1625 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1574,7 +1625,11 @@ $('overlay-fiche').querySelector('.fiche-modal').addEventListener('touchend', e
 // ═══════════════════════════════════════════════
 // DÉMARRAGE
 // ═══════════════════════════════════════════════
-if (sessionStorage.getItem(K.auth) === '1') {
+/* Expiration de session (#85) : purge d'abord une session trop ancienne
+   (token vieux de plus de 7 jours). Si verifierExpirationSession() a purgé,
+   elle a déjà affiché l'écran de connexion avec son message → on n'enchaîne
+   PAS sur reprendreSessionExistante(). Sinon, comportement inchangé. */
+if (!verifierExpirationSession() && sessionStorage.getItem(K.auth) === '1') {
   reprendreSessionExistante();
 }
 // Sinon : ecran-token est déjà affiché par défaut (class="ecran actif")
