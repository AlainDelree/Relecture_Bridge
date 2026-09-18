1195aa7

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1195aa7
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 11:13:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Sécurité : ajout des en-têtes HTTP de protection dans _headers (#83)
    
    Bloc /* appliqué à tout le site (GitHub Pages prod, Cloudflare dev,
    relayé par le worker ff-app) :
    - X-Frame-Options: SAMEORIGIN (anti-clickjacking)
    - X-Content-Type-Options: nosniff (anti MIME sniffing)
    - Referrer-Policy: strict-origin-when-cross-origin
    - Permissions-Policy: geolocation=(), microphone=(), camera=()
    
    Pas de CSP dans ce commit (issue distincte, phase report-only).
    Blocs de cache existants préservés.
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/_headers b/_headers
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 118321e..9902b88 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/_headers
# ── Version APRÈS ce commit.
+++ b/_headers
# ── Zone modifiée : ligne 1 (3 ligne(s)) dans l'ancienne version → ligne 1 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,3 +1,9 @@
+/*
+  X-Frame-Options: SAMEORIGIN
+  X-Content-Type-Options: nosniff
+  Referrer-Policy: strict-origin-when-cross-origin
+  Permissions-Policy: geolocation=(), microphone=(), camera=()
+
 /sw.js
   Cache-Control: no-cache, no-store, must-revalidate
 
