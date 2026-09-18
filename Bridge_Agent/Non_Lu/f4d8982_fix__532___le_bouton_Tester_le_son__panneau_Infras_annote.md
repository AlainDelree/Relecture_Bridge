f4d8982

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f4d8982
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Sat Sep 12 16:05:24 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #532 : le bouton Tester le son (panneau Infrastructure) joue la tonalité du projet actif
    
    /tester-son jouait systématiquement à tonalité neutre (0), qui ne
    correspond à aucun son réellement entendu en pratique dès qu'un projet
    règle TONALITE_BIP (ex. bridge_agent : -12). Le front transmet
    désormais le projet sélectionné dans la liste des issues (projetCourant)
    et le backend (app/son.py::tester_son) lit TONALITE_BIP dans son .conf
    via projet_par_nom(), comme le fait déjà /tester-bip/<nom_projet> pour
    le bouton de l'onglet Configuration. Repli neutre inchangé si aucun
    projet n'est sélectionné ou introuvable.
    
    Diagnostic vérifié au passage : les deux boutons "Tester le son"
    n'appelaient PAS la même route (hypothèse non confirmée du diagnostic
    précédent) — Infrastructure -> /tester-son (ce fix), Configuration ->
    /tester-bip/<nom_projet> (déjà correct depuis #526, testait la valeur du
    curseur avant enregistrement).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/app/son.py b/app/son.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 64f420d..0e1f38c 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/app/son.py
# ── Version APRÈS ce commit.
+++ b/app/son.py
# ── Zone modifiée : ligne 23 (6 ligne(s)) dans l'ancienne version → ligne 23 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -23,6 +23,7 @@ DOSSIER_SCRIPT = Path(__file__).resolve().parent.parent
 sys.path.insert(0, str(DOSSIER_SCRIPT))
 
 import notifications  # noqa: E402
+from app.projets import projet_par_nom  # noqa: E402
 
 CHEMIN_SON_ACTIF   = DOSSIER_SCRIPT / "scripts" / "son_actif.txt"
 SCRIPT_BIP_PARTAGE = DOSSIER_SCRIPT / "scripts" / "traitement_fin.py"
# ── Zone modifiée : ligne 63 (6 ligne(s)) dans l'ancienne version → ligne 64 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -63,6 +64,14 @@ def tester_son():
     """POST /tester-son — joue le bip avec le timbre ACTUELLEMENT enregistré
     dans son_actif.txt (le front écrit d'abord via POST /son-actif au clic sur
     l'interrupteur, donc ce test entend toujours le dernier choix). Tonalité
-    neutre (0) : ce réglage est global, pas rattaché à un projet."""
-    notifications.bip(SCRIPT_BIP_PARTAGE, 1)
+    (issue #532) : celle du projet actif transmis par le front ({"projet":
+    <nom>}), lue dans son .conf comme le fait /tester-bip/<nom_projet> — pour
+    que ce bouton reproduise fidèlement ce qu'on entend réellement à la
+    clôture d'une issue de ce projet. Neutre (0) si aucun projet n'est
+    transmis ou introuvable (comportement inchangé)."""
+    data   = request.json or {}
+    projet = str(data.get("projet", "")).strip()
+    cfg    = projet_par_nom(projet) if projet else None
+    tonalite = cfg.tonalite_bip if cfg is not None else 0
+    notifications.bip(SCRIPT_BIP_PARTAGE, 1, tonalite=tonalite)
     return jsonify(succes=True)
# (diff du fichier suivant)
diff --git a/static/js/app.js b/static/js/app.js
# (index — ignorable)
index 1a902e7..9a74abd 100644
# (avant — fichier suivant)
--- a/static/js/app.js
# (après — fichier suivant)
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2194 (11 ligne(s)) dans l'ancienne version → ligne 2194 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2194,11 +2194,20 @@ async function choisirSonActif(son) {
   }
 }
 
-// Joue le bip avec le timbre actuellement enregistré dans son_actif.txt
-// (même principe que testerBip() pour la tonalité par projet, issue #526).
+// Joue le bip avec le timbre actuellement enregistré dans son_actif.txt, à la
+// tonalité du projet actif (projetCourant, celui de la ligne sélectionnée
+// dans la liste des issues — voir sa déclaration plus haut), pour que ce test
+// reflète fidèlement le son entendu à la clôture d'une issue de ce projet
+// (issue #532). Neutre si aucune ligne n'est sélectionnée (projetCourant
+// null) : le backend applique alors le même repli (même principe que
+// testerBip() pour la tonalité par projet, issue #526).
 async function testerSonActif() {
   try {
-    await fetch('/tester-son', {method: 'POST'});
+    await fetch('/tester-son', {
+      method: 'POST',
+      headers: {'Content-Type': 'application/json'},
+      body: JSON.stringify({projet: projetCourant})
+    });
   } catch(e) {
     alert('Erreur réseau : ' + e.message);
   }
