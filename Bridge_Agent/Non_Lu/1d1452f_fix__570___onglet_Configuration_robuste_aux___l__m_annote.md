1d1452f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1d1452f
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 19:34:18 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #570 : onglet Configuration robuste aux éléments DOM absents (getElementById null) + gabarit .conf mentionne MAX_WRITE_PARALLELE
    
    Vérification (pas supposition) : app/projets.py::get_config() délègue entièrement à watcher.py::charger_config(), qui a TOUJOURS eu un défaut explicite (entier("MAX_WRITE_PARALLELE", 2)) depuis son introduction en #337 — confirmé par git blame et par un test runtime sur un .conf sans cette clé (résultat : 2). L'hypothèse d'une lecture indépendante sans défaut côté serveur est donc infirmée : il n'existe qu'une seule lecture du .conf, partagée. Aucun autre champ de l'onglet Configuration n'a de divergence équivalente, pour la même raison structurelle.
    
    Cause réelle du plantage "document.getElementById(...) is null" : ce message ne peut provenir que d'un ÉLÉMENT DOM absent, pas d'une valeur cfg absente (cfg.max_write_parallele || 2 protégeait déjà cette valeur). Le scénario le plus probable est un déploiement où templates/index.html (mis en cache par Jinja2, TEMPLATES_AUTO_RELOAD=False avec debug=False sur le process Flask longue durée de new_issue.py) reste l'ancienne version sans les éléments ajoutés par #568, alors que static/js/app.js (relu à chaque requête) est déjà la nouvelle version qui les référence — un redémarrage du process résorbe ce cas précis, mais la même classe de bug peut resurgir à chaque ajout futur de champ.
    
    Fix appliqué : chargerConfig() passe par un helper majChampConfig() qui vérifie l'existence de l'élément avant d'écrire dedans, pour TOUS les champs de l'onglet (pas seulement MAX_WRITE_PARALLELE) — un champ manquant au chargement n'interrompt plus les suivants. Ajout de MAX_WRITE_PARALLELE (commenté, défaut 2) au gabarit GABARIT_CONF de nouveau_projet.py, absent jusqu'ici : sans cet ajout, tout nouveau projet créé après #568 aurait le même trou de documentation que les projets pré-existants (le comportement runtime reste correct grâce au défaut de charger_config(), mais la clé n'apparaissait nulle part dans le .conf généré).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nouveau_projet.py b/nouveau_projet.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9edf109..903672c 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nouveau_projet.py
# ── Version APRÈS ce commit.
+++ b/nouveau_projet.py
# ── Zone modifiée : ligne 1318 (6 ligne(s)) dans l'ancienne version → ligne 1318 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1318,6 +1318,11 @@ SCRIPT_BIP        = {script_bip}
 # 0 = tonalité normale ; réglable aussi depuis l'onglet Configuration.
 # TONALITE_BIP    = 0
 
+# Nombre de tâches mode_write concurrentes via git worktrees (issue #337),
+# 1-4, plafonné à 4 (issue #568). 2 = défaut ; réglable aussi depuis l'onglet
+# Configuration.
+# MAX_WRITE_PARALLELE = 2
+
 # ─── Journaux (rotation par taille, archives datées) ──────────────────────────
 LOG_TAILLE_MAX_MO = 1
 LOG_ARCHIVES      = 5
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index eab45a2..224fbd2 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 235 (36 ligne(s)) dans l'ancienne version → ligne 235 (48 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -235,36 +235,48 @@ async function mettreAJourInfoProjet(reinitialiserTimeout = true) {
   } catch(e) {}
 }
 
+// Écrit une valeur dans un champ de l'onglet Configuration sans planter si
+// l'élément est absent du DOM (page pas encore rafraîchie après un déploiement
+// ayant ajouté ce champ, ou valeur absente/null/undefined renvoyée par le
+// serveur — issue #570) : ignore ce champ plutôt que d'interrompre le
+// chargement des champs suivants.
+function majChampConfig(id, valeur, proprite = 'value') {
+  const el = document.getElementById(id);
+  if (el) el[proprite] = valeur;
+}
+
 async function chargerConfig() {
   const nom = document.getElementById('projet').value;
   try {
     const rep = await fetch('/config/' + encodeURIComponent(nom));
     const cfg = await rep.json();
 
-    document.getElementById('config-readonly').innerHTML =
+    majChampConfig('config-readonly',
       `NOM = ${cfg.nom}<br>DEPOT = ${cfg.depot}<br>` +
       `REP_TRAVAIL = ${cfg.rep_travail}<br>` +
       (cfg.perimetre  ? `PERIMETRE = ${cfg.perimetre}<br>` : '') +
-      (cfg.cmd_backup ? `CMD_BACKUP = ${cfg.cmd_backup}` : '');
-
-    document.getElementById('conf-TOPIC_NTFY').value        = cfg.topic_ntfy        || '';
-    document.getElementById('conf-LABEL').value             = cfg.label             || 'for-linux';
-    document.getElementById('conf-INTERVALLE').value        = cfg.intervalle        || 10;
-    document.getElementById('conf-MAX_ESSAIS').value        = cfg.max_essais        || 3;
-    document.getElementById('conf-TIMEOUT_CLAUDE').value    = cfg.timeout_claude    || 300;
-    document.getElementById('conf-SCRIPT_BIP').value        = cfg.script_bip        || '';
+      (cfg.cmd_backup ? `CMD_BACKUP = ${cfg.cmd_backup}` : ''),
+      'innerHTML');
+
+    majChampConfig('conf-TOPIC_NTFY', cfg.topic_ntfy || '');
+    majChampConfig('conf-LABEL', cfg.label || 'for-linux');
+    majChampConfig('conf-INTERVALLE', cfg.intervalle || 10);
+    majChampConfig('conf-MAX_ESSAIS', cfg.max_essais || 3);
+    majChampConfig('conf-TIMEOUT_CLAUDE', cfg.timeout_claude || 300);
+    majChampConfig('conf-SCRIPT_BIP', cfg.script_bip || '');
     // ?? et non || : 0 est une valeur valide (tonalité normale).
-    document.getElementById('conf-TONALITE_BIP').value      = cfg.tonalite_bip      ?? 0;
-    document.getElementById('tonalite-bip-valeur').textContent = cfg.tonalite_bip   ?? 0;
-    document.getElementById('conf-FICHIER_CONTEXTE').value  = cfg.fichier_contexte  || '';
-    document.getElementById('conf-MODELE_CCL').value        = cfg.modele_ccl        || '';
-    document.getElementById('conf-LOG_TAILLE_MAX_MO').value = cfg.log_taille_max_mo || 1;
-    document.getElementById('conf-LOG_ARCHIVES').value      = cfg.log_archives      || 5;
+    majChampConfig('conf-TONALITE_BIP', cfg.tonalite_bip ?? 0);
+    majChampConfig('tonalite-bip-valeur', cfg.tonalite_bip ?? 0, 'textContent');
+    majChampConfig('conf-FICHIER_CONTEXTE', cfg.fichier_contexte || '');
+    majChampConfig('conf-MODELE_CCL', cfg.modele_ccl || '');
+    majChampConfig('conf-LOG_TAILLE_MAX_MO', cfg.log_taille_max_mo || 1);
+    majChampConfig('conf-LOG_ARCHIVES', cfg.log_archives || 5);
     // ?? et non || : 0 est une valeur valide (auto-extinction désactivée).
-    document.getElementById('conf-DELAI_INACTIVITE_MIN').value = cfg.delai_inactivite_min ?? 20;
-    document.getElementById('conf-MAX_WRITE_PARALLELE').value      = cfg.max_write_parallele      || 2;
-    document.getElementById('max-write-parallele-valeur').textContent = cfg.max_write_parallele || 2;
-    document.getElementById('msg-config').style.display = 'none';
+    majChampConfig('conf-DELAI_INACTIVITE_MIN', cfg.delai_inactivite_min ?? 20);
+    majChampConfig('conf-MAX_WRITE_PARALLELE', cfg.max_write_parallele || 2);
+    majChampConfig('max-write-parallele-valeur', cfg.max_write_parallele || 2, 'textContent');
+    const msgConfig = document.getElementById('msg-config');
+    if (msgConfig) msgConfig.style.display = 'none';
   } catch(e) {
     const msg = document.getElementById('msg-config');
     msg.textContent = 'Erreur de chargement : ' + e.message;
