0508fbb

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0508fbb
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 17:32:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix(#91): percent-encode X-FF-Message pour éviter le crash fetch() sur caractères non-Latin1
    
    Les en-têtes HTTP sont du ByteString (Latin-1 strict) : un caractère > 0xFF
    (tiret cadratin U+2014, guillemets courbes, accents, emoji) faisait planter
    fetch() côté admin avant même l'envoi (« character has value 8212 »).
    
    - admin.js _sauvegarderSallesKV() : encodeURIComponent() sur X-FF-Message
      (seul en-tête porteur de texte libre ; X-FF-Branch est une constante).
    - data-worker/worker.js : decodeURIComponent() défensif (try/catch) avant
      usage comme message de commit, pour rester lisible en clair côté Git.
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/assets/js/admin.js b/assets/js/admin.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 01c9cbc..ec83c03 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/assets/js/admin.js
# ── Version APRÈS ce commit.
+++ b/assets/js/admin.js
# ── Zone modifiée : ligne 481 (7 ligne(s)) dans l'ancienne version → ligne 481 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -481,7 +481,14 @@ async function _sauvegarderSallesKV(payloadTexte, message) {
       'Authorization': 'Bearer ' + ffSecret,
       'Content-Type': 'application/json',
       'X-FF-Branch': BRANCH,
-      'X-FF-Message': message || 'Admin : sauvegarde salles'
+      /* Les en-têtes HTTP sont des ByteString (Latin-1 strict) : tout caractère
+         > 0xFF (tiret cadratin —, guillemets courbes, accents composés, emoji…)
+         fait planter fetch() AVANT l'envoi (« character has value 8212 »).
+         On percent-encode donc le message libre — encodeURIComponent() ne
+         produit que de l'ASCII, quel que soit le texte fourni par l'appelant.
+         Le worker ff-data le decodeURIComponent() avant de l'utiliser comme
+         message de commit, pour qu'il reste lisible en clair côté Git. */
+      'X-FF-Message': encodeURIComponent(message || 'Admin : sauvegarde salles')
     },
     body: payloadTexte
   });
# (diff du fichier suivant)
diff --git a/data-worker/worker.js b/data-worker/worker.js
# (index — ignorable)
index b342575..b4cdd66 100644
# (avant — fichier suivant)
--- a/data-worker/worker.js
# (après — fichier suivant)
+++ b/data-worker/worker.js
# ── Zone modifiée : ligne 367 (7 ligne(s)) dans l'ancienne version → ligne 367 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -367,7 +367,18 @@ export default {
       }
       await env.FF_DATA.put(cle, corpsTexte);
       const branche = request.headers.get('X-FF-Branch') || 'dev';
-      const messageCommit = request.headers.get('X-FF-Message') || null;
+      /* X-FF-Message est percent-encodé côté admin (encodeURIComponent) car les
+         en-têtes HTTP sont du Latin-1 strict et refusent les caractères > 0xFF
+         (tiret cadratin, guillemets courbes, emoji…). On le décode ici pour que
+         le message de commit reste lisible en clair dans l'historique Git.
+         try/catch : un client non à jour (ou un « % » littéral non échappé)
+         enverrait une valeur non/malencodée → on garde alors le brut plutôt que
+         de perdre le message sur une URIError. */
+      let messageCommit = request.headers.get('X-FF-Message') || null;
+      if (messageCommit) {
+        try { messageCommit = decodeURIComponent(messageCommit); }
+        catch { /* valeur non percent-encodée : on la conserve telle quelle */ }
+      }
       ctx.waitUntil(archiverVersGitHub(cle, corpsTexte, branche, messageCommit, env));
       return reponseJSON({ ok: true, cle });
     }
