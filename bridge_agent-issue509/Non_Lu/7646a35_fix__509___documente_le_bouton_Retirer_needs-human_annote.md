7646a35

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 7646a35
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 30 16:48:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #509 : documente le bouton Retirer needs-human (déjà implémenté par #460)
    
    Vérification : la fonctionnalité demandée (bouton dans #pl-zone-actions,
    visible si needs-human, retrait via gh --remove-label, issue non fermée,
    rafraîchissement auto) existe déjà intégralement depuis l'issue #460
    (commit 8dec213, static/js/app.js::rendrePanneauLateralActions/
    relancerIssue + app/interruption.py::route_relancer, déjà sur master).
    Seul manquait la documentation dans BRIDGE_AGENT_DOC.md, ajoutée ici.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c790521..eca2583 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1047 (6 ligne(s)) dans l'ancienne version → ligne 1047 (37 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1047,6 +1047,37 @@ moins une étape non critique en échec) ou `echec_critique` (l'arbre de
 process n'a pas pu être confirmé mort — le verrou est alors volontairement
 laissé en place, intervention manuelle requise).
 
+### Relancer une issue bloquée en `needs-human` (issue #460, cf. #509)
+
+**Symptôme visé.** Après 3 tentatives infructueuses, le watcher pose le
+label `needs-human` sur l'issue et cesse de la reprendre — jusqu'ici, la
+seule façon de débloquer le circuit était de retirer ce label à la main sur
+GitHub, un aller-retour répété en pratique à chaque échec.
+
+**Ce que fait le bouton.** Dans le panneau flottant Infrastructure, la zone
+d'actions contextuelles `#pl-zone-actions` (`rendrePanneauLateralActions()`,
+issue #375) affiche un bouton « 🔄 Relancer » dès que l'issue actuellement
+sélectionnée (`projetCourant`/`numeroCourant`) porte le label `needs-human`
+et est encore ouverte — sans fetch réseau, à partir des données déjà en
+mémoire (`listeIssuesResultats`). Un clic (après confirmation) appelle
+`relancerIssue()` → `POST /relancer-issue` (`app/interruption.py::
+route_relancer`), qui :
+
+- retire le label `needs-human` côté GitHub (`gh issue edit --remove-label`,
+  même mécanisme que `--add-label`/`--remove-label` utilisé par
+  `app/issues.py::modifier_label_notif`) ;
+- poste un commentaire de trace `🔄 Relancée via new_issue.py (retrait de
+  needs-human).` ;
+- **ne ferme pas l'issue** — il n'existe pas de label « pending » dans ce
+  projet : une issue ouverte sans `needs-human` ni `done` est déjà éligible
+  au prochain cycle de polling du watcher (`watcher.py`), à condition que
+  celui-ci tourne (aucune relance automatique du watcher lui-même).
+
+**Rafraîchissement.** Après succès, `relancerIssue()` recharge la liste
+(`chargerListeIssues()`) puis, si la ligne de l'issue reste visible sous les
+filtres courants, son détail (`afficherIssue()`) — le badge ⚠️ disparaît
+donc de la ligne concernée sans rechargement manuel complet de la page.
+
 ### Nettoyage de l'arbre de process après une tâche (issue #247)
 
 **Problème constaté.** Après un build Scrabble réussi côté CCW, un `cmd.exe`
# (diff du fichier suivant)
diff --git a/CHANGELOG-509.md b/CHANGELOG-509.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..f4fd48e
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/CHANGELOG-509.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,19 @@
+## 30 août 2026 — issue #509
+
+Panneau Infrastructure — bouton « Retirer needs-human » sur l'issue
+sélectionnée : demande déjà entièrement couverte par l'issue #460
+(commit `8dec213`, fusionné dans `master` avant #509). Vérification faite
+que le bouton « 🔄 Relancer » de `#pl-zone-actions`
+(`rendrePanneauLateralActions()`, `static/js/app.js`) remplit exactement
+le besoin décrit : visible uniquement quand l'issue sélectionnée porte le
+label `needs-human` et est ouverte, retire ce label via `gh issue edit
+--remove-label` (route `POST /relancer-issue`,
+`app/interruption.py::route_relancer`, même mécanisme `--add-label`/
+`--remove-label` que `app/issues.py::modifier_label_notif`), ne ferme pas
+l'issue, poste un commentaire de trace, puis rafraîchit la liste et le
+détail sans rechargement manuel complet. Aucune modification de code
+nécessaire.
+- `BRIDGE_AGENT_DOC.md` : ajout de la sous-section « Relancer une issue
+  bloquée en `needs-human` (issue #460, cf. #509) » (juste après
+  « Interrompre une issue bloquée »), qui manquait — seul point réellement
+  manquant identifié pour cette issue.
