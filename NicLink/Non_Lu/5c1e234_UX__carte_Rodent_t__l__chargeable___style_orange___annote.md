5c1e234

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5c1e234
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 14:33:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    UX: carte Rodent téléchargeable = style orange + pulsation + tagline Installer (issue #191)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ea802d8..f72d5c9 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 541 (6 ligne(s)) dans l'ancienne version → ligne 541 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -541,6 +541,7 @@ function _applyRodentAvailability() {
   const msg = t("engine.rodent.unavailable");
   const downloadHint = t("engine.rodent.download");
   const downloadState = _rodentDownloadable && !_rodentAvailable;
+  const tagline = downloadState ? t("engine.rodent.install") : t("config.tagline.rodent");
   [["cfg-engine-rodent", "cfg-rodent-unavailable", "cfg-rodent-icon"],
    ["labo-eng-rodent",   "labo-rodent-unavailable", "labo-rodent-icon"]].forEach(([btnId, msgId, iconId]) => {
     const btn = document.getElementById(btnId);
# ── Zone modifiée : ligne 552 (6 ligne(s)) dans l'ancienne version → ligne 553 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -552,6 +553,8 @@ function _applyRodentAvailability() {
       if (_rodentAvailable)   btn.removeAttribute("title");
       else if (downloadState) btn.setAttribute("title", downloadHint);
       else                    btn.setAttribute("title", msg);
+      const taglineEl = btn.querySelector(".engine-tagline");
+      if (taglineEl) taglineEl.textContent = tagline;
     }
     if (icon) icon.textContent = downloadState ? "⬇" : "🐭";
     if (box) box.style.display = (!_rodentAvailable && !downloadState) ? "" : "none";
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# (index — ignorable)
index 965ffe8..d04156c 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/css/main.css
# (après — fichier suivant)
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 412 (11 ligne(s)) dans l'ancienne version → ligne 412 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -412,11 +412,16 @@
     }
     /* Rodent absent mais téléchargeable (Windows) : carte cliquable = bouton de téléchargement */
     .color-btn.engine-downloadable {
-      border-color: #3a5a7a;
-      background: #dce8f5;
-      color: #1a2a3a;
+      border-color: #e67e22;
+      background: #fff3e0;
+      color: #7d3c00;
+      animation: rodent-downloadable-pulse 2s ease-in-out infinite;
+    }
+    .color-btn.engine-downloadable:hover { background: #ffe0b2; }
+    @keyframes rodent-downloadable-pulse {
+      0%, 100% { box-shadow: 0 0 0 0 rgba(230, 126, 34, 0.35); }
+      50%      { box-shadow: 0 0 6px 3px rgba(230, 126, 34, 0.35); }
     }
-    .color-btn.engine-downloadable:hover { background: #c2d9ee; }
     .color-btn.engine-downloading {
       opacity: 0.6;
       cursor: wait;
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/de.json b/nicsoft/web/static/i18n/de.json
# (index — ignorable)
index 07de1ac..33fa3f5 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/de.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/de.json
# ── Zone modifiée : ligne 90 (6 ligne(s)) dans l'ancienne version → ligne 90 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,6 +90,7 @@
   "engine.maia.unavailable": "Maia (lc0 + Gewichte) ist auf diesem System nicht installiert",
   "engine.rodent.unavailable": "Rodent-Engine auf diesem System nicht verfügbar",
   "engine.rodent.download": "Rodent IV herunterladen",
+  "engine.rodent.install": "Installieren",
   "engine.rodent.downloading": "Wird heruntergeladen…",
   "engine.rodent.download_ok": "Rodent IV heruntergeladen — einsatzbereit",
   "engine.rodent.download_error": "Download fehlgeschlagen — Internetverbindung prüfen",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/en.json b/nicsoft/web/static/i18n/en.json
# (index — ignorable)
index 1dfbe45..7f3de64 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/en.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/en.json
# ── Zone modifiée : ligne 90 (6 ligne(s)) dans l'ancienne version → ligne 90 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,6 +90,7 @@
   "engine.maia.unavailable": "Maia (lc0 + weights) not installed on this system",
   "engine.rodent.unavailable": "Rodent engine unavailable on this system",
   "engine.rodent.download": "Download Rodent IV",
+  "engine.rodent.install": "Install",
   "engine.rodent.downloading": "Downloading…",
   "engine.rodent.download_ok": "Rodent IV downloaded — ready to use",
   "engine.rodent.download_error": "Download failed — check your internet connection",
# (diff du fichier suivant)
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# (index — ignorable)
index f50c848..6ae4b26 100644
# (avant — fichier suivant)
--- a/nicsoft/web/static/i18n/fr.json
# (après — fichier suivant)
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 90 (6 ligne(s)) dans l'ancienne version → ligne 90 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -90,6 +90,7 @@
   "engine.maia.unavailable": "Maia (lc0 + poids) non installé sur ce système",
   "engine.rodent.unavailable": "Moteur Rodent indisponible sur ce système",
   "engine.rodent.download": "Télécharger Rodent IV",
+  "engine.rodent.install": "Installer",
   "engine.rodent.downloading": "Téléchargement…",
   "engine.rodent.download_ok": "Rodent IV téléchargé — prêt à l'emploi",
   "engine.rodent.download_error": "Échec du téléchargement — vérifiez votre connexion internet",
