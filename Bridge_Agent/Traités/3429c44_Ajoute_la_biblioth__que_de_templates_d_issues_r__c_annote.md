3429c44

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3429c44
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 21:19:05 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute la bibliothèque de templates d'issues récurrentes (issue #284)
    
    Nouveau module app/templates.py (stockage JSON gitignoré par projet,
    configs/templates_<projet>.json) avec trois routes Flask (liste GET,
    création/mise à jour POST, suppression DELETE), enregistrées dans
    app/__init__.py. Côté formulaire « Nouvelle issue » : liste déroulante
    « Charger un template » filtrée par projet qui pré-remplit tout le
    formulaire, bouton « Créer le template », et icônes crayon/poubelle pour
    modifier/supprimer le template sélectionné (static/js/app.js,
    templates/index.html). .gitignore mis à jour pour configs/templates_*.json.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index e510302..cbf323a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 12 (3 ligne(s)) dans l'ancienne version → ligne 12 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -12,3 +12,6 @@ provisioning/windows/autounattend.local.xml
 # Mot de passe ccw-admin lu par l'onglet CCW (issue #174) si CCW_ADMIN_PASSWORD
 # n'est pas dans l'environnement — ne doit JAMAIS être committé.
 configs/ccw_admin.secret
+# Bibliothèque de templates d'issues récurrentes par projet (issue #284) :
+# état de formulaire local, pas du code — jamais committé.
+configs/templates_*.json
# (diff du fichier suivant)
diff --git a/app/__init__.py b/app/__init__.py
# (index — ignorable)
index 59f6ca3..3054fd7 100644
# (avant — fichier suivant)
--- a/app/__init__.py
# (après — fichier suivant)
+++ b/app/__init__.py
# ── Zone modifiée : ligne 66 (6 ligne(s)) dans l'ancienne version → ligne 66 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -66,6 +66,8 @@ def _enregistrer_routes(app: Flask) -> None:
     from app.issues import (apercu, envoyer, issues_liste, issue_detail,
                             diff_commit, issues_en_attente, annuler_issue,
                             fermer_issue, joindre_image)
+    from app.templates import (templates_liste, templates_sauvegarder,
+                               templates_supprimer)
     from app.journal import journal
     from app.ccw import (ccw_vm_statut, ccw_demarrer_vm, ccw_projets,
                          ccw_ajouter_projet, ccw_finaliser_projet,
# ── Zone modifiée : ligne 82 (6 ligne(s)) dans l'ancienne version → ligne 84 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -82,6 +84,10 @@ def _enregistrer_routes(app: Flask) -> None:
     app.add_url_rule("/apercu", "apercu", login_requis(apercu), methods=["POST"])
     app.add_url_rule("/envoyer", "envoyer", login_requis(envoyer), methods=["POST"])
     app.add_url_rule("/joindre-image", "joindre_image", login_requis(joindre_image), methods=["POST"])
+    # ─── Bibliothèque de templates d'issues récurrentes (issue #284) ──────────
+    app.add_url_rule("/templates/<nom_projet>", "templates_liste", login_requis(templates_liste), methods=["GET"])
+    app.add_url_rule("/templates", "templates_sauvegarder", login_requis(templates_sauvegarder), methods=["POST"])
+    app.add_url_rule("/templates/<nom_projet>/<template_id>", "templates_supprimer", login_requis(templates_supprimer), methods=["DELETE"])
     app.add_url_rule("/journal/<nom_projet>", "journal", login_requis(journal))
     app.add_url_rule("/issues-liste/<nom_projet>", "issues_liste", login_requis(issues_liste))
     app.add_url_rule("/issue/<nom_projet>/<numero>", "issue_detail", login_requis(issue_detail))
# (diff du fichier suivant)
diff --git a/app/templates.py b/app/templates.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..c5e6280
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/app/templates.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (111 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,111 @@
+"""Bibliothèque de templates d'issues récurrentes (issue #284).
+
+Certaines issues reviennent régulièrement à l'identique (ex. build Scrabble) :
+plutôt que de redemander à Claude Chat ou de fouiller les conversations
+passées, un template capture l'état complet du formulaire « Nouvelle issue »
+(titre, corps, priorité, timeout, mode, notifications, modèle) et se recharge
+en un clic. Stockage : un fichier JSON gitignoré par projet
+(configs/templates_<projet>.json) — état de formulaire local, pas du code.
+"""
+
+import json
+import uuid
+from pathlib import Path
+
+from flask import jsonify, request
+
+from app.projets import projet_par_nom
+
+# Racine du projet (dossier parent du package app/) : configs/ y vit.
+DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
+DOSSIER_TEMPLATES = DOSSIER_SCRIPT / "configs"
+
+# Champs stockés par template, avec leur défaut — mêmes clés que
+# collecterFormulaire() côté navigateur pour que sauvegarde et rechargement du
+# formulaire n'aient aucune conversion à faire.
+CHAMPS_TEMPLATE_DEFAUTS = {
+    "titre":           "",
+    "corps":           "",
+    "priorite":        "normale",
+    "timeout":         "300",
+    "mode":            "lecture",
+    "notifs":          [],
+    "modele_ponctuel": "",
+}
+
+
+def _chemin_templates(nom_projet: str) -> Path:
+    return DOSSIER_TEMPLATES / f"templates_{nom_projet}.json"
+
+
+def _charger_templates(nom_projet: str) -> list:
+    """Liste des templates du projet, ou liste vide si le fichier n'existe pas
+    encore ou est illisible/corrompu."""
+    chemin = _chemin_templates(nom_projet)
+    try:
+        if chemin.exists():
+            return json.loads(chemin.read_text(encoding="utf-8")) or []
+    except (json.JSONDecodeError, OSError):
+        pass
+    return []
+
+
+def _sauvegarder_templates(nom_projet: str, templates: list) -> None:
+    chemin = _chemin_templates(nom_projet)
+    chemin.write_text(
+        json.dumps(templates, ensure_ascii=False, indent=2), encoding="utf-8"
+    )
+
+
+# ─── Routes Flask ──────────────────────────────────────────────────────────────
+
+def templates_liste(nom_projet):
+    """Retourne la bibliothèque de templates du projet (GET)."""
+    if not projet_par_nom(nom_projet):
+        return jsonify(erreur="Projet introuvable."), 404
+    return jsonify(_charger_templates(nom_projet))
+
+
+def templates_sauvegarder():
+    """Crée ou met à jour un template (POST).
+
+    Un `id` présent dans le corps de la requête et correspondant à un template
+    existant du projet met à jour cette entrée ; sinon (absent ou inconnu) une
+    nouvelle entrée est créée avec un id généré."""
+    data = request.json or {}
+    nom_projet = (data.get("projet") or "").strip()
+    if not projet_par_nom(nom_projet):
+        return jsonify(succes=False, erreur="Projet introuvable."), 404
+    nom = (data.get("nom") or "").strip()
+    if not nom:
+        return jsonify(succes=False, erreur="Le nom du template est obligatoire."), 400
+
+    templates = _charger_templates(nom_projet)
+    id_existant = data.get("id")
+    id_final = id_existant if any(t.get("id") == id_existant for t in templates) else uuid.uuid4().hex[:8]
+
+    template = {"id": id_final, "nom": nom, "projet": nom_projet}
+    for champ, defaut in CHAMPS_TEMPLATE_DEFAUTS.items():
+        template[champ] = data.get(champ, defaut)
+
+    for i, t in enumerate(templates):
+        if t.get("id") == id_final:
+            templates[i] = template
+            break
+    else:
+        templates.append(template)
+
+    _sauvegarder_templates(nom_projet, templates)
+    return jsonify(succes=True, template=template)
+
+
+def templates_supprimer(nom_projet, template_id):
+    """Supprime un template du projet (DELETE)."""
+    if not projet_par_nom(nom_projet):
+        return jsonify(succes=False, erreur="Projet introuvable."), 404
+    templates = _charger_templates(nom_projet)
+    restants = [t for t in templates if t.get("id") != template_id]
+    if len(restants) == len(templates):
+        return jsonify(succes=False, erreur="Template introuvable."), 404
+    _sauvegarder_templates(nom_projet, restants)
+    return jsonify(succes=True)
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 7002386..bb1fc8a 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 86 (6 ligne(s)) dans l'ancienne version → ligne 86 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -86,6 +86,9 @@ function onProjetChange(reinitialiserTimeout = true) {
   appliquerAccentProjet(nom);
   verifierStatut();
   mettreAJourInfoProjet(reinitialiserTimeout);
+  // Bibliothèque de templates (issue #284) : filtrée par projet, rechargée à
+  // chaque changement de projet (manuel ou détection d'en-tête).
+  chargerTemplates();
   // L'onglet Résultats est indépendant du sélecteur global (il agrège tous
   // les projets) : on ne le recharge donc PAS ici.
   // Si l'onglet Configuration est actif, recharger sa config pour le
# ── Zone modifiée : ligne 2484 (6 ligne(s)) dans l'ancienne version → ligne 2487 (145 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2484,6 +2487,145 @@ function collecterFormulaire() {
   };
 }
 
+// ─── Bibliothèque de templates d'issues récurrentes (issue #284) ──────────────
+// Un template capture l'état complet du formulaire (mêmes clés que
+// collecterFormulaire()) sous un nom choisi par l'utilisateur, pour recréer en
+// un clic une issue qui revient régulièrement à l'identique (ex. build
+// Scrabble). Liste rechargée à chaque changement de projet (onProjetChange).
+let templatesProjetActuel = [];
+
+async function chargerTemplates() {
+  const select = document.getElementById('template-select');
+  if (!select) return;
+  const nomProjet = document.getElementById('projet').value;
+  try {
+    const rep = await fetch('/templates/' + encodeURIComponent(nomProjet));
+    const json = await rep.json();
+    templatesProjetActuel = Array.isArray(json) ? json : [];
+  } catch(e) {
+    templatesProjetActuel = [];
+  }
+  select.innerHTML = '<option value="">-- Aucun --</option>' +
+    templatesProjetActuel.map(t =>
+      '<option value="' + escapeHtml(t.id) + '">' + escapeHtml(t.nom) + '</option>'
+    ).join('');
+  onTemplateSelectChange();
+}
+
+function templateSelectionne() {
+  const select = document.getElementById('template-select');
+  if (!select || !select.value) return null;
+  return templatesProjetActuel.find(t => t.id === select.value) || null;
+}
+
+// Sélectionner un template dans la liste déroulante pré-remplit tout le
+// formulaire ci-dessous (titre, corps, priorité, timeout, mode, notifications,
+// modèle) et active/désactive les icônes modifier/supprimer.
+function onTemplateSelectChange() {
+  const t = templateSelectionne();
+  const btnMod = document.getElementById('btn-template-modifier');
+  const btnSup = document.getElementById('btn-template-supprimer');
+  if (btnMod) btnMod.disabled = !t;
+  if (btnSup) btnSup.disabled = !t;
+  if (t) chargerTemplateDansFormulaire(t);
+}
+
+function chargerTemplateDansFormulaire(t) {
+  document.getElementById('titre').value = t.titre || '';
+  document.getElementById('priorite').value = t.priorite || 'normale';
+  document.getElementById('timeout').value = t.timeout || 300;
+  const radio = document.querySelector('input[name=mode][value="' + (t.mode || 'lecture') + '"]');
+  if (radio) radio.checked = true;
+  document.querySelectorAll('input[name=notifs]').forEach(c => {
+    c.checked = Array.isArray(t.notifs) && t.notifs.includes(c.value);
+  });
+  document.getElementById('corps').value = t.corps || '';
+  document.getElementById('modele-ponctuel').value = t.modele_ponctuel || '';
+  mettreAJourBoutonEnvoi();
+  mettreAJourResumeEntete();
+}
+
+// Enregistre l'état actuel du formulaire comme NOUVEAU template du projet en
+// cours (bouton « Créer le template »). Demande le nom via un prompt simple.
+async function creerTemplate() {
+  const nom = prompt('Nom du template :');
+  if (!nom || !nom.trim()) return;
+  const data = collecterFormulaire();
+  data.nom = nom.trim();
+  try {
+    const rep  = await fetch('/templates', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify(data)
+    });
+    const json = await rep.json();
+    if (json.succes) {
+      await chargerTemplates();
+      document.getElementById('template-select').value = json.template.id;
+      onTemplateSelectChange();
+      afficherToast('Template « ' + nom.trim() + ' » créé.');
+    } else {
+      afficherMessage('Erreur : ' + (json.erreur || 'échec inconnu'), 'erreur');
+    }
+  } catch(e) {
+    afficherMessage('Erreur réseau : ' + e.message, 'erreur');
+  }
+}
+
+// Écrase le template actuellement sélectionné avec l'état courant du
+// formulaire (icône crayon) — le nom reste modifiable via le prompt.
+async function modifierTemplateSelectionne() {
+  const t = templateSelectionne();
+  if (!t) return;
+  const nom = prompt('Nom du template :', t.nom);
+  if (!nom || !nom.trim()) return;
+  const data = collecterFormulaire();
+  data.id  = t.id;
+  data.nom = nom.trim();
+  try {
+    const rep  = await fetch('/templates', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify(data)
+    });
+    const json = await rep.json();
+    if (json.succes) {
+      await chargerTemplates();
+      document.getElementById('template-select').value = json.template.id;
+      onTemplateSelectChange();
+      afficherToast('Template « ' + nom.trim() + ' » mis à jour.');
+    } else {
+      afficherMessage('Erreur : ' + (json.erreur || 'échec inconnu'), 'erreur');
+    }
+  } catch(e) {
+    afficherMessage('Erreur réseau : ' + e.message, 'erreur');
+  }
+}
+
+// Supprime le template actuellement sélectionné (icône poubelle), après
+// confirmation.
+async function supprimerTemplateSelectionne() {
+  const t = templateSelectionne();
+  if (!t) return;
+  if (!confirm('Supprimer le template « ' + t.nom + ' » ?')) return;
+  const nomProjet = document.getElementById('projet').value;
+  try {
+    const rep  = await fetch(
+      '/templates/' + encodeURIComponent(nomProjet) + '/' + encodeURIComponent(t.id),
+      {method: 'DELETE'}
+    );
+    const json = await rep.json();
+    if (json.succes) {
+      await chargerTemplates();
+      afficherToast('Template supprimé.');
+    } else {
+      afficherMessage('Erreur : ' + (json.erreur || 'échec inconnu'), 'erreur');
+    }
+  } catch(e) {
+    afficherMessage('Erreur réseau : ' + e.message, 'erreur');
+  }
+}
+
 function afficherMessage(texte, type) {
   const el = document.getElementById('message');
   el.textContent = texte;
# ── Zone modifiée : ligne 3615 (6 ligne(s)) dans l'ancienne version → ligne 3757 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3615,6 +3757,11 @@ function viderFormulaire(cacherMsg=true) {
   // Le corps est vidé par programme (pas d'event « input ») : on masque
   // explicitement le résumé d'en-tête (issue #117).
   mettreAJourResumeEntete();
+  // Désélectionne le template chargé (issue #284) : un formulaire vidé ne
+  // reflète plus aucun template en particulier.
+  const selectTemplate = document.getElementById('template-select');
+  if (selectTemplate) selectTemplate.value = '';
+  onTemplateSelectChange();
 }
 
 // ─── Nouveau projet (issue #99) ───────────────────────────────────────────
# (diff du fichier suivant)
diff --git a/templates/index.html b/templates/index.html
# (index — ignorable)
index b48ccc2..0799c80 100644
# (avant — fichier suivant)
--- a/templates/index.html
# (après — fichier suivant)
+++ b/templates/index.html
# ── Zone modifiée : ligne 72 (6 ligne(s)) dans l'ancienne version → ligne 72 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -72,6 +72,23 @@
   <!-- ─── Onglet 1 : création d'issue ──────────────────────────────────── -->
   <div id="panneau-creation" class="panneau actif">
 
+    <!-- Bibliothèque de templates d'issues récurrentes (issue #284) : liste
+         filtrée dynamiquement selon le projet sélectionné dans le bandeau.
+         Charger un template pré-remplit tout le formulaire ci-dessous ; les
+         icônes crayon/poubelle modifient/suppriment le template sélectionné. -->
+    <div class="rangee" style="align-items:flex-end;gap:8px;margin-bottom:14px">
+      <div class="champ" style="flex:1">
+        <label>Charger un template</label>
+        <select id="template-select" onchange="onTemplateSelectChange()">
+          <option value="">-- Aucun --</option>
+        </select>
+      </div>
+      <button type="button" id="btn-template-modifier" onclick="modifierTemplateSelectionne()"
+              disabled title="Modifier le template sélectionné" style="padding:8px 12px">✏️</button>
+      <button type="button" id="btn-template-supprimer" onclick="supprimerTemplateSelectionne()"
+              disabled title="Supprimer le template sélectionné" style="padding:8px 12px">🗑️</button>
+    </div>
+
     <div class="rangee">
       <div class="champ" style="max-width:150px">
         <label>Priorité</label>
# ── Zone modifiée : ligne 126 (6 ligne(s)) dans l'ancienne version → ligne 143 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -126,6 +143,7 @@
       <div style="flex:1"></div>
       <button class="danger" onclick="viderFormulaire()">Vider</button>
       <button onclick="afficherApercu()">Aperçu de la commande</button>
+      <button onclick="creerTemplate()" title="Enregistre l'état actuel du formulaire comme nouveau template">Créer le template</button>
       <button class="primaire" id="btn-envoyer" onclick="envoyerIssue()">Envoyer l'issue</button>
     </div>
 
