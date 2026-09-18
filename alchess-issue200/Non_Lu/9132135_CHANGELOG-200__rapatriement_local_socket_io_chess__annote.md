9132135

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9132135
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 22 08:24:40 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    CHANGELOG-200: rapatriement local socket.io/chess.js

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-200.md b/CHANGELOG-200.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..bdb2529
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-200.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,10 @@
+# Changelog — Issue #200
+
+## Rapatrier socket.io et chess.js en local
+
+- Téléchargé `socket.io.min.js` (v4.7.2) et `chess.min.js` (v0.10.3) dans
+  `nicsoft/web/static/vendor/socket.io/` et `nicsoft/web/static/vendor/chess.js/`.
+- `index.html` référence désormais `/static/vendor/socket.io/socket.io.min.js`
+  et `/static/vendor/chess.js/chess.min.js` au lieu de cdnjs.cloudflare.com.
+- Testé : démarrage serveur Flask OK, page servie sans requête vers cdnjs,
+  handshake Socket.IO fonctionnel, fichiers vendor servis en HTTP 200.
