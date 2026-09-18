fae2011

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit fae2011
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 12:50:43 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #454 : bandeau d'avertissement échéance éval Windows CCW dans new_issue.py

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-454.md b/CHANGELOG-454.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..59d5b4d
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-454.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,24 @@
+## 18 août 2026 — issue #454
+
+FEATURE — Bandeau d'avertissement d'échéance de l'éval Windows CCW dans
+`new_issue.py`.
+- `app/eval_windows.py` (nouveau) : `etat_eval_windows()` lit
+  `provisioning/windows/eval-expiration.json`, recalcule la date
+  d'expiration (`date_installation` + `eval_jours`, même logique que
+  `provisioning/windows/verifier_expiration_ccw.py`) et retourne `None`
+  si le fichier est absent/invalide ou si l'échéance est encore lointaine
+  (> 14 jours), sinon un état `{jours_restants, date_expiration, niveau,
+  message}` avec `niveau` = `orange` (≤ 14 j) ou `rouge` (≤ 5 j ou
+  échéance dépassée).
+- `app/vues.py` : la route `index()` passe `eval_windows=etat_eval_windows()`
+  au gabarit.
+- `templates/index.html` : bandeau `{% if eval_windows %}` inséré juste
+  après l'en-tête, en dehors des panneaux d'onglets → visible sur tous
+  les onglets sans dupliquer le HTML.
+- `static/css/style.css` : styles `.bandeau-eval-windows.orange` (fond
+  `#fff3cd`) et `.rouge` (fond `#f8d7da`), cohérents avec les couleurs
+  d'alerte déjà utilisées ailleurs dans l'interface.
+- Vérifié par test manuel (`create_app()` + `test_client`) avec état
+  forcé orange/rouge/absent : bandeau présent avec le bon texte et la
+  bonne classe, absent quand l'échéance est lointaine (cas réel actuel :
+  89 jours restants au 18/08/2026) ou quand le fichier est absent/invalide.
# (diff du fichier suivant)
diff --git a/app/eval_windows.py b/app/eval_windows.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..4eda8c2
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/app/eval_windows.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (53 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,53 @@
+"""Bandeau d'avertissement d'échéance de l'éval Windows CCW (issue #454).
+
+Réutilise le même calcul que provisioning/windows/verifier_expiration_ccw.py
+(date_installation + eval_jours → date d'expiration), mais retourne un état
+structuré pour l'interface web plutôt que d'imprimer sur la sortie standard.
+"""
+
+import json
+from datetime import date, timedelta
+
+from app.etat import RACINE
+
+FICHIER_META = RACINE / "provisioning" / "windows" / "eval-expiration.json"
+
+SEUIL_ORANGE = 14  # jours restants à partir desquels le bandeau orange apparaît
+SEUIL_ROUGE = 5    # jours restants (ou dépassement) à partir desquels il passe au rouge
+
+
+def etat_eval_windows() -> dict | None:
+    """État du bandeau d'avertissement, ou None si rien à afficher (fichier
+    absent/invalide, ou échéance encore lointaine)."""
+    if not FICHIER_META.exists():
+        return None
+    try:
+        with FICHIER_META.open(encoding="utf-8") as f:
+            meta = json.load(f)
+        date_install = date.fromisoformat(str(meta["date_installation"]))
+        eval_jours = int(meta["eval_jours"])
+    except (json.JSONDecodeError, OSError, KeyError, ValueError, TypeError):
+        return None
+
+    date_expiration = date_install + timedelta(days=eval_jours)
+    jours_restants = (date_expiration - date.today()).days
+
+    if jours_restants <= SEUIL_ROUGE:
+        niveau = "rouge"
+    elif jours_restants <= SEUIL_ORANGE:
+        niveau = "orange"
+    else:
+        return None
+
+    if jours_restants < 0:
+        texte_jours = f"expirée depuis {-jours_restants} jour(s)"
+    else:
+        texte_jours = f"{jours_restants} jour(s) restant(s)"
+
+    return {
+        "jours_restants": jours_restants,
+        "date_expiration": date_expiration.strftime("%d/%m/%Y"),
+        "niveau": niveau,
+        "message": (f"⚠️ Éval Windows CCW : {texte_jours} — réinstaller avant le "
+                    f"{date_expiration.strftime('%d/%m/%Y')}"),
+    }
# (diff du fichier suivant)
diff --git a/app/vues.py b/app/vues.py
# (index — ignorable)
index ccb6d6f..9c19c9b 100644
# (avant — fichier suivant)
--- a/app/vues.py
# (après — fichier suivant)
+++ b/app/vues.py
# ── Zone modifiée : ligne 8 (10 ligne(s)) dans l'ancienne version → ligne 8 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -8,10 +8,12 @@ from flask import render_template
 
 from app.projets import lister_projets
 from app.issues import formats_image_acceptes
+from app.eval_windows import etat_eval_windows
 from app import etat
 
 
 def index():
     return render_template("index.html", projets=lister_projets(),
                            auth_active=bool(etat.get("MOT_DE_PASSE")),
-                           formats_image=formats_image_acceptes())
+                           formats_image=formats_image_acceptes(),
+                           eval_windows=etat_eval_windows())
# (diff du fichier suivant)
diff --git a/static/css/style.css b/static/css/style.css
# (index — ignorable)
index 15828c5..4c6b0f1 100644
# (avant — fichier suivant)
--- a/static/css/style.css
# (après — fichier suivant)
+++ b/static/css/style.css
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,9 @@ body{font-family:system-ui,sans-serif;font-size:14px;background:#f0efe9;color:#1
 .entete{padding:14px 20px;border-bottom:1px solid #dad9d2;display:flex;align-items:center;gap:9px;background:#e7e6e0}
 .entete h1{font-size:15px;font-weight:500}
 .entete .statut{margin-left:auto;font-size:12px;color:#888}
+.bandeau-eval-windows{padding:9px 20px;font-size:13px;font-weight:600;text-align:center}
+.bandeau-eval-windows.orange{background:#fff3cd;color:#856404;border-bottom:1px solid #ffe08a}
+.bandeau-eval-windows.rouge{background:#f8d7da;color:#721c24;border-bottom:1px solid #f5c6cb}
 .bandeau-projet{display:flex;flex-direction:column;gap:8px;
   padding:14px 20px;border-bottom:1px solid #dad9d2;background:#e7e6e0;
   border-left:4px solid #1a1a18}
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index d82fd38..1e270fc 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 25 (6 ligne(s)) dans l'ancienne version → ligne 25 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,6 +25,12 @@
             style="font-size:12px;padding:5px 12px">Quitter</button>
   </div>
 
+  <!-- ─── Bandeau d'avertissement échéance éval Windows CCW (issue #454) : visible
+       sur tous les onglets, hors des panneaux, tant que l'échéance approche. ─ -->
+  {% if eval_windows %}
+  <div class="bandeau-eval-windows {{ eval_windows.niveau }}">{{ eval_windows.message }}</div>
+  {% endif %}
+
   <!-- ─── Bandeau global : sélecteur de projet (pilote tous les onglets sauf Watchers) ─ -->
   <div class="bandeau-projet">
 
