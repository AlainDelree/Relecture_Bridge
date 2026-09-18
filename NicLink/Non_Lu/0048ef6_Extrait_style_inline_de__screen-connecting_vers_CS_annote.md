0048ef6

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0048ef6
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 23 19:58:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Extrait style inline de #screen-connecting vers CSS (issue #233)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/css/main.css b/nicsoft/web/static/css/main.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d6ea26a..ad94df7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/css/main.css
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/css/main.css
# ── Zone modifiée : ligne 1106 (6 ligne(s)) dans l'ancienne version → ligne 1106 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1106,6 +1106,13 @@
 .expl-play-actions-card { padding:14px 16px; display:flex; flex-direction:column; gap:8px; }
 .expl-play-btn-back { background:#c2d4e8; color:#1a2a3a; border:1px solid #a0b8d0; margin-bottom:0; }
 
+/* ── Écran connexion échiquier (issue #233) ── */
+.screen-connecting { display:none; flex:1; flex-direction:column; align-items:center; justify-content:center; gap:20px; }
+.connecting-icon { font-size:2rem; }
+.connecting-msg { font-size:1.2rem; color:#e0e0e0; }
+.connecting-sub { color:#888; font-size:0.9rem; }
+.connecting-spinner { width:40px; height:40px; border:3px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite; }
+
 /* ── Outil 1 — formulaire ajout ouverture ── */
 .add-field { display:flex; flex-direction:column; gap:3px; }
 .add-label { font-size:0.82rem; font-weight:600; color:#3a5a7a; }
# (diff du fichier suivant)
diff --git a/nicsoft/web/templates/index.html b/nicsoft/web/templates/index.html
# (index — ignorable)
index 2764bc6..06000bd 100644
# (avant — fichier suivant)
--- a/nicsoft/web/templates/index.html
# (après — fichier suivant)
+++ b/nicsoft/web/templates/index.html
# ── Zone modifiée : ligne 1721 (11 ligne(s)) dans l'ancienne version → ligne 1721 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1721,11 +1721,11 @@
 
 
 <!-- ── Écran connexion échiquier ── -->
-<div id="screen-connecting" style="display:none; flex:1; flex-direction:column; align-items:center; justify-content:center; gap:20px;">
-  <div style="font-size:2rem;">♜</div>
-  <div id="connecting-msg" style="font-size:1.2rem; color:#e0e0e0;" data-i18n="connecting.msg">Connexion à l'échiquier…</div>
-  <div id="connecting-sub" style="color:#888; font-size:0.9rem;" data-i18n="connecting.sub">Vérifiez que le plateau est allumé et en position initiale.</div>
-  <div style="width:40px; height:40px; border:3px solid #e94560; border-top-color:transparent; border-radius:50%; animation:spin 0.8s linear infinite;"></div>
+<div id="screen-connecting" class="screen-connecting">
+  <div class="connecting-icon">♜</div>
+  <div id="connecting-msg" class="connecting-msg" data-i18n="connecting.msg">Connexion à l'échiquier…</div>
+  <div id="connecting-sub" class="connecting-sub" data-i18n="connecting.sub">Vérifiez que le plateau est allumé et en position initiale.</div>
+  <div class="connecting-spinner"></div>
 </div>
 
 
