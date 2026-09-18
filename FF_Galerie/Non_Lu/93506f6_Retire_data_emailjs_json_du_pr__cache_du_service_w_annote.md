93506f6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 93506f6
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 16:26:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Retire data/emailjs.json du précache du service worker (#89)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-89.md b/CHANGELOG-89.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..9cccb86
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-89.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,23 @@
+# CHANGELOG — Issue #89
+
+## Retirer `data/emailjs.json` du précache du service worker
+
+- **Fichier modifié :** `sw.js` — retrait de l'entrée `'/data/emailjs.json'`
+  de la liste `SHELL` (liste de précache du cache `ff-shell`). 1 ligne
+  supprimée.
+- **Vérification de dépendance :** confirmé qu'aucune page publique ni la PWA
+  ne dépend de ce fichier. La seule référence à `data/emailjs.json` est dans
+  `assets/js/admin-emailjs.js` (fetch), lui-même chargé uniquement depuis
+  `admin.html`. L'admin est de toute façon exclue du SW (chemin + referrer),
+  donc ce fichier n'était jamais servi depuis le cache à qui en a besoin.
+- **Cohérence du précache :** `precacheShell()` itère via
+  `Promise.allSettled(SHELL.map(...))` — aucun compteur figé sur l'ancienne
+  longueur, tableau bien formé. `node --check sw.js` passe.
+- **Purge des installs existants :** le cache `ff-shell` a un nom STABLE.
+  Retirer l'entrée empêche seulement les NOUVELLES installations de la mettre
+  en cache. `REFRESH`/`precacheShell` ne font que `cache.put` (ajout/mise à
+  jour), jamais de suppression des entrées obsolètes ; `activate` ne purge que
+  les caches nommés `ff-shell-*`. L'ancienne entrée persiste donc dans les
+  installs déjà déployés. Elle est inoffensive (site public = réseau d'abord ;
+  app = exclue par chemin/referrer). Purge réelle → vider les données de site /
+  réinstaller la PWA.
# (diff du fichier suivant)
diff --git a/sw.js b/sw.js
# (index — ignorable)
index b7360f0..e70183e 100644
# (avant — fichier suivant)
--- a/sw.js
# (après — fichier suivant)
+++ b/sw.js
# ── Zone modifiée : ligne 64 (7 ligne(s)) dans l'ancienne version → ligne 64 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -64,7 +64,6 @@ const SHELL = [
   '/data/artistes.json',
   '/data/infos.json',
   '/data/contact.json',
-  '/data/emailjs.json',
 
   '/favicon.ico',
   '/assets/images/icons/icon-192.png',
