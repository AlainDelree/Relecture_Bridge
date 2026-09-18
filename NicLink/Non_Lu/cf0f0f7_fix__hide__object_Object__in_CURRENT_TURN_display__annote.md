cf0f0f7

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit cf0f0f7
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 22:23:13 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: hide [object Object] in CURRENT TURN display

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3a919d7..a82e301 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 932 (7 ligne(s)) dans l'ancienne version → ligne 932 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -932,7 +932,11 @@ socket.on("undo_move", (data) => {
   hideFeedback();
   if (data.message || data.message_key) {
     const turnInfo = document.getElementById("turn-info");
-    if (turnInfo) { turnInfo.textContent = data.message_key ? t(data.message_key) : data.message; turnInfo.className = "warning"; }
+    if (turnInfo) {
+      const msg = data.message_key ? t(data.message_key) : data.message;
+      turnInfo.textContent = (typeof msg === "string" && msg && msg !== "[object Object]") ? msg : "";
+      turnInfo.className = "warning";
+    }
   }
   // Resynchroniser chess.js avec la position après undo (full_fen inclut le tour et le roque)
   if (_virtualMode) _virtSyncChess(data.full_fen || data.fen);
# ── Zone modifiée : ligne 1392 (7 ligne(s)) dans l'ancienne version → ligne 1396 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1392,7 +1396,8 @@ function _i18nMsg(data, field = "message", keyField = "message_key") {
     if (vars.piece_key) vars.piece = t(vars.piece_key);
     return t(data[keyField], vars);
   }
-  return data[field] || "";
+  const val = data[field];
+  return (typeof val === "string" && val && val !== "[object Object]") ? val : "";
 }
 
 function afficherToast(message, type) {
