bfb32e8

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit bfb32e8
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 24 17:14:13 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    backup: avant issue247 extraction screen-outils-exercices partie 3/4 (Ajouter ouverture au catalogue)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ed73293..db3b036 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/css/main.css
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 1518 (3 ligne(s)) dans l'ancienne version → ligne 1518 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1518,3 +1518,17 @@
 .outils-explore-moves-col { flex:1; min-width:200px; }
 .outils-explore-moves-title { font-size:0.82rem; font-weight:700; color:#3a5a7a; margin-bottom:6px; }
 .outils-explore-in-catalogue { margin-top:8px; font-size:0.83rem; color:#7b1fa2; font-weight:600; }
+
+/* ── Écran #screen-outils-exercices — Ajouter une ouverture au catalogue (issue #247 partie 3/4) ── */
+.outils-explore-add-section { display:none; margin-top:16px; border-top:1px solid #a0b8d0; padding-top:14px; }
+.outils-explore-add-title { font-weight:700; color:#1a2a3a; margin-bottom:10px; font-size:0.95rem; }
+.outils-add-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px 18px; }
+.add-required { color:#e94560; }
+.add-input-upper { text-transform:uppercase; }
+.add-input-mono { font-family:monospace; }
+.add-field-full { grid-column:1/-1; }
+.outils-explore-add-btn-row { display:flex; gap:10px; margin-top:10px; flex-wrap:wrap; }
+.outils-explore-add-preview { display:none; margin-top:10px; }
+.outils-explore-btn-add-wrap { margin-top:12px; display:none; }
+.outils-add-btn-row { display:flex; gap:10px; margin-top:12px; flex-wrap:wrap; }
+.outils-add-preview { display:none; margin-top:14px; }
