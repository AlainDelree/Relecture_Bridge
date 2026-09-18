97b209e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 97b209e
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 22:56:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: move rodent_download socket listeners after socket init

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4362c32..a05bc18 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 566 (26 ligne(s)) dans l'ancienne version → ligne 566 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -566,26 +566,6 @@ function downloadRodent() {
   socket.emit("download_rodent", {});
 }
 
-socket.on("rodent_download_progress", (data) => {
-  const msg = `${t("engine.rodent.downloading")} (${data.index}/${data.total} ${data.file})`;
-  ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
-    const status = document.getElementById(id);
-    if (status) status.textContent = msg;
-  });
-});
-
-socket.on("rodent_download_result", (data) => {
-  const msg = data && data.ok ? t("engine.rodent.download_ok") : t("engine.rodent.download_error");
-  ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
-    const status = document.getElementById(id);
-    if (status) status.textContent = msg;
-  });
-  ["cfg-rodent-download-btn", "labo-rodent-download-btn"].forEach(id => {
-    const btn = document.getElementById(id);
-    if (btn) btn.disabled = false;
-  });
-});
-
 // Vérifie si aucun moteur n'est disponible — grise le bouton Démarrer et affiche l'alerte.
 function _checkNoEngineAvailable() {
   const noEngine = !_stockfishAvailable && !_maiaAvailable && !_rodentAvailable;
# ── Zone modifiée : ligne 5984 (3 ligne(s)) dans l'ancienne version → ligne 5964 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5984,3 +5964,23 @@ socket.on("rodent_status", (data) => {
   }
   _applyRodentAvailability();
 });
+
+socket.on("rodent_download_progress", (data) => {
+  const msg = `${t("engine.rodent.downloading")} (${data.index}/${data.total} ${data.file})`;
+  ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
+    const status = document.getElementById(id);
+    if (status) status.textContent = msg;
+  });
+});
+
+socket.on("rodent_download_result", (data) => {
+  const msg = data && data.ok ? t("engine.rodent.download_ok") : t("engine.rodent.download_error");
+  ["cfg-rodent-download-status", "labo-rodent-download-status"].forEach(id => {
+    const status = document.getElementById(id);
+    if (status) status.textContent = msg;
+  });
+  ["cfg-rodent-download-btn", "labo-rodent-download-btn"].forEach(id => {
+    const btn = document.getElementById(id);
+    if (btn) btn.disabled = false;
+  });
+});
