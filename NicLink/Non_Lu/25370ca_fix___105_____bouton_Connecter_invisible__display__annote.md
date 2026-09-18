25370ca

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 25370ca
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 22:24:10 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #105 — bouton Connecter invisible (display:'' → 'block')

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/app.js b/nicsoft/web/static/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b226828..3a919d7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/app.js
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/app.js
# ── Zone modifiée : ligne 273 (7 ligne(s)) dans l'ancienne version → ligne 273 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -273,7 +273,7 @@ function _applyBoardBadge() {
   const btnConnecter       = document.getElementById("btn-connecter");
   if (schemaConnected)    schemaConnected.style.display    = _boardOk ? "block" : "none";
   if (schemaDisconnected) schemaDisconnected.style.display = _boardOk ? "none"  : "block";
-  if (btnConnecter)       btnConnecter.style.display       = _boardOk ? "none"  : "";
+  if (btnConnecter)       btnConnecter.style.display       = _boardOk ? "none"  : "block";
 
   // Déplace le wrapper HH selon l'état de l'échiquier : en bas de la colonne
   // Jouer (après Exercices) si non connecté, à sa place d'origine (avant Labo) sinon.
