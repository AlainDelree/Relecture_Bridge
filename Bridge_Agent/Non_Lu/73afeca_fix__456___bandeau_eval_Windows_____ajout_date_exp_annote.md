73afeca

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 73afeca
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 13:09:44 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #456 : bandeau eval Windows — ajout date_expiration_oauth_token (état + affichage combiné)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/eval_windows.py b/app/eval_windows.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4eda8c2..f26ef03 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/eval_windows.py
# ── Version APRÈS ce commit.
+++ b/app/eval_windows.py
# ── Zone modifiée : ligne 1 (4 ligne(s)) dans l'ancienne version → ligne 1 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,4 +1,5 @@
-"""Bandeau d'avertissement d'échéance de l'éval Windows CCW (issue #454).
+"""Bandeau d'avertissement d'échéance de l'éval Windows CCW (issue #454) et
+du CLAUDE_CODE_OAUTH_TOKEN du service CCW-Watcher (issue #456).
 
 Réutilise le même calcul que provisioning/windows/verifier_expiration_ccw.py
 (date_installation + eval_jours → date d'expiration), mais retourne un état
# ── Zone modifiée : ligne 16 (38 ligne(s)) dans l'ancienne version → ligne 17 (72 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -16,38 +17,72 @@ SEUIL_ORANGE = 14  # jours restants à partir desquels le bandeau orange appara
 SEUIL_ROUGE = 5    # jours restants (ou dépassement) à partir desquels il passe au rouge
 
 
+def _niveau(jours_restants: int) -> str | None:
+    """Niveau d'alerte ("rouge"/"orange") pour un nombre de jours restants
+    donné, ou None si l'échéance est encore lointaine."""
+    if jours_restants <= SEUIL_ROUGE:
+        return "rouge"
+    if jours_restants <= SEUIL_ORANGE:
+        return "orange"
+    return None
+
+
 def etat_eval_windows() -> dict | None:
-    """État du bandeau d'avertissement, ou None si rien à afficher (fichier
-    absent/invalide, ou échéance encore lointaine)."""
+    """État du bandeau d'avertissement (éval Windows + token OAuth CCW), ou
+    None si rien à afficher (fichier absent/invalide, ou échéances encore
+    lointaines)."""
     if not FICHIER_META.exists():
         return None
     try:
         with FICHIER_META.open(encoding="utf-8") as f:
             meta = json.load(f)
+    except (json.JSONDecodeError, OSError):
+        return None
+
+    alertes = []
+
+    try:
         date_install = date.fromisoformat(str(meta["date_installation"]))
         eval_jours = int(meta["eval_jours"])
-    except (json.JSONDecodeError, OSError, KeyError, ValueError, TypeError):
-        return None
+        date_expiration = date_install + timedelta(days=eval_jours)
+        jours_restants = (date_expiration - date.today()).days
+        niveau = _niveau(jours_restants)
+        if niveau:
+            if jours_restants < 0:
+                texte_jours = f"expirée depuis {-jours_restants} jour(s)"
+            else:
+                texte_jours = f"{jours_restants} jour(s) restant(s)"
+            alertes.append({
+                "niveau": niveau,
+                "message": (f"⚠️ Éval Windows CCW : {texte_jours} — réinstaller avant le "
+                            f"{date_expiration.strftime('%d/%m/%Y')}"),
+            })
+    except (KeyError, ValueError, TypeError):
+        pass
 
-    date_expiration = date_install + timedelta(days=eval_jours)
-    jours_restants = (date_expiration - date.today()).days
+    try:
+        date_token = date.fromisoformat(str(meta["date_expiration_oauth_token"]))
+        jours_restants_token = (date_token - date.today()).days
+        niveau_token = _niveau(jours_restants_token)
+        if niveau_token:
+            if jours_restants_token < 0:
+                texte_jours = f"expiré depuis {-jours_restants_token} jour(s)"
+            else:
+                texte_jours = f"{jours_restants_token} jours restants"
+            alertes.append({
+                "niveau": niveau_token,
+                "message": (f"⚠️ OAuth Token CCW : {texte_jours} — renouveler avant le "
+                            f"{date_token.strftime('%d/%m/%Y')}"),
+            })
+    except (KeyError, ValueError, TypeError):
+        pass
 
-    if jours_restants <= SEUIL_ROUGE:
-        niveau = "rouge"
-    elif jours_restants <= SEUIL_ORANGE:
-        niveau = "orange"
-    else:
+    if not alertes:
         return None
 
-    if jours_restants < 0:
-        texte_jours = f"expirée depuis {-jours_restants} jour(s)"
-    else:
-        texte_jours = f"{jours_restants} jour(s) restant(s)"
+    niveau_global = "rouge" if any(a["niveau"] == "rouge" for a in alertes) else "orange"
 
     return {
-        "jours_restants": jours_restants,
-        "date_expiration": date_expiration.strftime("%d/%m/%Y"),
-        "niveau": niveau,
-        "message": (f"⚠️ Éval Windows CCW : {texte_jours} — réinstaller avant le "
-                    f"{date_expiration.strftime('%d/%m/%Y')}"),
+        "niveau": niveau_global,
+        "messages": [a["message"] for a in alertes],
     }
# (diff du fichier suivant)
diff --git a/provisioning/windows/eval-expiration.json b/provisioning/windows/eval-expiration.json
# (index — ignorable)
index f20218a..6b18167 100644
# (avant — fichier suivant)
--- a/provisioning/windows/eval-expiration.json
# (après — fichier suivant)
+++ b/provisioning/windows/eval-expiration.json
# ── Zone modifiée : ligne 5 (5 ligne(s)) dans l'ancienne version → ligne 5 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,5 +5,6 @@
   "eval_jours": 90,
   "date_installation": "2026-08-17",
   "date_expiration": "2026-11-15",
-  "note": "date_installation = date d'installation effective de Windows dans la VM. date_expiration = date_installation + eval_jours. Après expiration, Windows redémarre automatiquement toutes les heures, ce qui casse le service CCW-Watcher : recréer la VM avant (creer_vm_ccw.py --recreate). Si la date d'install réelle diffère, ajuster date_installation ci-dessus ; date_expiration est purement informative et recalculée par le script à partir de date_installation + eval_jours."
+  "date_expiration_oauth_token": "2026-10-17",
+  "note": "date_installation = date d'installation effective de Windows dans la VM. date_expiration = date_installation + eval_jours. Après expiration, Windows redémarre automatiquement toutes les heures, ce qui casse le service CCW-Watcher : recréer la VM avant (creer_vm_ccw.py --recreate). Si la date d'install réelle diffère, ajuster date_installation ci-dessus ; date_expiration est purement informative et recalculée par le script à partir de date_installation + eval_jours. date_expiration_oauth_token = date d'expiration du CLAUDE_CODE_OAUTH_TOKEN du service CCW-Watcher (indépendante de l'éval Windows) ; à mettre à jour manuellement après chaque renouvellement du token."
 }
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index 1e270fc..b86edf8 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 28 (7 ligne(s)) dans l'ancienne version → ligne 28 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -28,7 +28,11 @@
   <!-- ─── Bandeau d'avertissement échéance éval Windows CCW (issue #454) : visible
        sur tous les onglets, hors des panneaux, tant que l'échéance approche. ─ -->
   {% if eval_windows %}
-  <div class="bandeau-eval-windows {{ eval_windows.niveau }}">{{ eval_windows.message }}</div>
+  <div class="bandeau-eval-windows {{ eval_windows.niveau }}">
+    {% for message in eval_windows.messages %}
+    <div>{{ message }}</div>
+    {% endfor %}
+  </div>
   {% endif %}
 
   <!-- ─── Bandeau global : sélecteur de projet (pilote tous les onglets sauf Watchers) ─ -->
