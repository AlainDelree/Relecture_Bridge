d92ee7f

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d92ee7f
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 8 13:07:02 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #523 : needs-human traité comme état terminal (décompte, timingIssues, issues-en-attente)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/issues.py b/app/issues.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 66ca7e0..6e10a3f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/issues.py
# ── Version APRÈS ce commit.
+++ b/app/issues.py
# ── Zone modifiée : ligne 26 (7 ligne(s)) dans l'ancienne version → ligne 26 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -26,7 +26,7 @@ from app.auth import login_requis  # noqa: F401 (exporté pour l'enregistrement
 from watcher import (est_titre_chef, deduire_type_issue, PAUSE_ENTRE_TENTATIVES,
                      _est_depot_git, LABEL_ECRITURE, LABEL_SCRATCH,
                      LABEL_NOTIF_PC, LABEL_NOTIF_GSM, LABEL_NOTIF_TOUS,
-                     extraire_complexite)
+                     LABEL_ECHEC, extraire_complexite)
 
 # Racine du projet (dossier parent du package app/).
 DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
# ── Zone modifiée : ligne 1055 (6 ligne(s)) dans l'ancienne version → ligne 1055 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1055,6 +1055,15 @@ def issues_en_attente(nom_projet):
                 # (cas rare, non nominal) ne doit apparaître qu'une fois.
                 if it.get("number") in vus:
                     continue
+                # needs-human est un état terminal côté décompte (issue #523) :
+                # le label ne ferme jamais l'issue (relance possible sans
+                # recréer), donc `--state open` la retourne encore ici — sans
+                # cette exclusion, chargerTimingIssues() réinjecterait une
+                # entrée stale à chaque rafraîchissement, avec le même `debut`
+                # figé, ce qui relance indéfiniment le décompte côté front.
+                noms_labels = [(l.get("name") or "").lower() for l in it.get("labels", [])]
+                if LABEL_ECHEC in noms_labels:
+                    continue
                 vus.add(it.get("number"))
                 issues.append(it)
     except subprocess.TimeoutExpired:
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 0fff423..c8e54a6 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 1816 (7 ligne(s)) dans l'ancienne version → ligne 1816 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1816,7 +1816,12 @@ async function verifierIssueApresDepassement(projet, numero) {
     return;   // échec réseau : pas de nouvelle tentative auto (cohérent avec #270)
   }
   if (!it || it.erreur) return;
-  if ((it.state || '').toUpperCase() === 'CLOSED') {
+  // needs-human est un état terminal côté décompte au même titre que la
+  // fermeture GitHub (state === 'CLOSED') : le label ne ferme jamais l'issue
+  // (relance possible sans recréer, cf. #460), mais plus aucun retraitement
+  // auto n'aura lieu — le badge doit donc s'arrêter immédiatement (issue #523).
+  const nomsLabels = (it.labels || []).map(l => ((l && l.name) || l || '').toLowerCase());
+  if ((it.state || '').toUpperCase() === 'CLOSED' || nomsLabels.includes('needs-human')) {
     const itListe = {
       number: it.number, title: it.title, state: it.state,
       labels: it.labels, createdAt: it.createdAt, projet: projet,
