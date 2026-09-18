aea4287

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit aea4287
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 8 11:32:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #401 : onglet Résultats — largeur fixe (min-width:130px) de la zone d'icônes (.ligne-gauche) pour aligner les titres
    
    Le nombre d'icônes (préfixe type/OS, badges ✏️/✅/⚠️/○/Diff/All, pastille)
    variait d'une ligne à l'autre, décalant horizontalement le début du titre.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3832647..599d1e3 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,17 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 8 août 2026 — issue #401
+
+Onglet Résultats : les titres des issues ne s'alignaient pas horizontalement,
+la zone d'icônes à gauche (case à cocher, pastille, badges Diff/All, etc.)
+ayant une largeur variable selon le nombre d'icônes présents sur chaque ligne.
+- `static/css/style.css` : `.ligne-issue .ligne-gauche` (préfixe type/OS +
+  badges ✏️/✅/⚠️/○/Diff/All + pastille projet) reçoit un `min-width:130px`
+  — largeur fixe couvrant le cas le plus chargé (chef/ouvrier + for-windows +
+  mode_write+done+Diff+All), tous les titres démarrent désormais à la même
+  position, les icônes restant alignées à gauche (flex-start).
+
 ## 7 août 2026 — issue #389
 
 Fix `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x82` lors de la
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index 3437c55..15828c5 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 203 (7 ligne(s)) dans l'ancienne version → ligne 203 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -203,7 +203,14 @@ button.danger:hover{background:#f8d7da}
 .ligne-issue.resultat-traite.selectionnee .ligne-texte{color:#2a2a28;text-decoration:none}
 .ligne-issue.selectionnee{background:var(--bg-sel);font-weight:600}
 .ligne-issue.selectionnee:hover{background:var(--bg-sel)}
-.ligne-issue .ligne-gauche{display:inline-flex;align-items:center;gap:6px;flex-shrink:0}
+/* Largeur fixe (issue #401) : le nombre d'icônes (préfixe type/OS, badges
+   ✏️/✅/⚠️/○, Diff/All) varie d'une ligne à l'autre, ce qui décalait le début
+   du titre. min-width (et non width, pour ne jamais tronquer les badges dans
+   le cas rare — chef/ouvrier + for-windows + mode_write+done+Diff+All — le
+   plus large) fige cette zone : tous les titres démarrent à la même position
+   horizontale, les icônes restant alignées à gauche (flex-start par défaut). */
+.ligne-issue .ligne-gauche{display:inline-flex;align-items:center;gap:6px;flex-shrink:0;
+  min-width:130px}
 .ligne-issue .ligne-badges{font-size:13px;white-space:nowrap}
 .ligne-issue .badge-copie-ccl{cursor:pointer}
 /* Badge « All » (issue #95, rôle #116) : copie la réponse CCL complète + le diff.
