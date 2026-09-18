25c1c3c

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 25c1c3c
Merge: cd3840a 1000464
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Fri Sep 18 19:59:30 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Merge worktree-issue-539

diff --cc CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1bc44c6,3ad9ea9..4b018b0
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
@@@ -9,83 -9,83 +9,160 @@@ milliers de caractères sur une seule l
  
  Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
  
 +## 14 septembre 2026 — issue #542
 +
 +Mode lecture bloqué sur des commandes nécessitant une approbation
 +interactive impossible en session non-interactive (issue #542, constaté
 +sur CCW via l'issue de diagnostic #541 : `git fetch`/`git pull` et
 +`Add-Type -AssemblyName ...` refusés par Claude Code avec « This command
 +requires approval »). Confirmé dans le code (`lancer_claude`) :
 +`MODE_LECTURE` n'a jamais `--dangerously-skip-permissions` (réservé à
 +`mode_write`/`mode_scratch`) — reproduit à l'identique sur CCL avec le CLI
 +`claude` nu (`git -C ... fetch` bloqué avec le même message), donc bien un
 +bug partagé par les deux plateformes (`watcher.py` commun), pas spécifique
 +à CCW/Windows.
 +
 +Plutôt que d'ajouter `--dangerously-skip-permissions` en lecture seule (ce
 +qui désarmerait toutes les protections de Claude Code sans le filet de
 +sécurité technique dont bénéficie la lecture active, empreinte
 +avant/après), ajout d'une allowlist fine via `--allowedTools` — mécanisme
 +natif de Claude Code qui débloque des commandes précises sans toucher au
 +reste : `git fetch` (jamais d'écriture dans l'arbre de travail),
 +`git pull --ff-only` (échoue plutôt que de merger — même opération que le
 +`git pull --ff-only` déjà fait automatiquement par le watcher en début de
 +cycle sur `REP_TRAVAIL`) et `Add-Type -AssemblyName` côté CCW (charge un
 +assembly .NET nommé, sans exécuter de code arbitraire —
 +`Add-Type -TypeDefinition`, qui compile du C#, reste volontairement hors
 +liste). Nouvelle constante `OUTILS_LECTURE_AUTORISES` dans `watcher.py`,
 +ajoutée à `cmd` uniquement en `MODE_LECTURE`. `git status`/`log`/`diff`/
 +`show` n'ont pas eu besoin d'y être ajoutés : déjà autorisés sans
 +approbation par l'heuristique interne de Claude Code (vérifié).
 +
 +Vérification de bout en bout via `lancer_claude` en conditions réelles
 +(pas seulement `claude --help`) : `git fetch --dry-run` + `git pull
 +--ff-only` s'exécutent sans blocage en mode lecture (résultat renvoyé
 +normalement) ; une tentative d'écriture hors allowlist (redirection shell
 +vers un fichier du projet) reste bloquée par le sandbox, confirmant que le
 +périmètre d'écriture de la lecture seule n'a pas été élargi. Le cas
 +`Add-Type -AssemblyName` (spécifique PowerShell/CCW) n'a pas pu être
 +vérifié en conditions réelles faute d'environnement Windows disponible ici
 +— à confirmer côté CCW à l'occasion d'une prochaine tâche PowerShell en
 +lecture seule.
 +
 +## 13 septembre 2026 — issue #540
 +
 +Recyclage de la couleur des projets à l'arrêt (`ecole`, `ff_galerie`) vers
 +un gris neutre partagé, pour libérer leur ancienne couleur dédiée dans une
 +palette déjà contrainte (#539 : combinaison distance CIE76 + écart de
 +teinte Lab, seulement 5 couleurs libres avant cette issue).
 +
 +Nouvelle constante `COULEUR_PROJET_INACTIF = "#767676"` définie à deux
 +endroits (`nouveau_projet.py` et `static/js/app.js`, pas de mécanisme de
 +partage de constantes entre les deux) : contraste texte noir 4,62:1
 +(`_contraste_avec_noir(0, 0, 46)`), au-dessus du seuil `SEUIL_CONTRASTE_NOIR`
 +(4,5:1) commun aux couleurs actives — sans contrainte de saturation 100% ni
 +de distance/teinte Lab, le but étant justement de signaler visuellement
 +l'absence d'identité propre.
 +
 +Traitement volontairement ASYMÉTRIQUE entre les deux fichiers, vérifié
 +concrètement plutôt que supposé :
 +- `nouveau_projet.py` : `ecole` et `ff_galerie` **retirées** de
 +  `COULEURS_PROJETS_EXISTANTS` (pas remplacées par le gris). Ce dictionnaire
 +  est passé en `couleurs_a_eviter` à `generer_palette()`, qui compare les
 +  couleurs par angle de teinte Lab (`_teinte_lab`) ; un gris (saturation 0)
 +  a un a\*/b\* quasi nul, donc un angle `atan2(0,0)` dégénéré à 0°, qui
 +  entre en collision avec l'exclusion de teinte prévue pour les rouges et
 +  fait échouer l'assertion de fin de `generer_palette()` — reproduit
 +  concrètement en testant les deux variantes (retrait vs. remplacement par
 +  le gris) avant de choisir. Les retirer suffit et n'a pas cet effet de
 +  bord : `couleurs_disponibles()` passe de 5 à 6 couleurs proposées à un
 +  futur projet, confirmant que l'ancienne couleur dédiée est bien recyclée.
 +- `static/js/app.js` : `ecole` et `ff_galerie` restent des clés de
 +  `COULEURS_PROJET` (seule source de vérité pour l'affichage, y compris des
 +  projets à l'arrêt), simplement avec la valeur `COULEUR_PROJET_INACTIF` à
 +  la place de leur ancienne teinte dédiée.
 +
 +Documentation : sous-section « Couleur d'accent des projets » de
 +`BRIDGE_AGENT_DOC.md` complétée d'une procédure de recyclage réutilisable
 +pour un futur projet mis à l'arrêt (retrait côté Python, remplacement de la
 +valeur côté JS, pourquoi ce n'est pas symétrique).
+ ## 13 septembre 2026 — issue #539
+ 
+ Suite retour d'usage sur #535 : 3 paires de couleurs de projet restaient
+ visuellement trop proches malgré une distance CIE76 au-dessus du seuil de
+ garde de 15 posé en #535 — `alchess`/`rummikub`, `ecole`/`chesscoach`,
+ `actualise`/`gestionmail`.
+ 
+ **Diagnostic (point 1 de l'issue)** : les couleurs réellement en usage pour
+ `alchess`/`rummikub` et `ecole`/`chesscoach` ont une distance CIE76 de 56 et
+ 52 — largement AU-DESSUS du seuil de 15, pas « de justesse » comme supposé.
+ La vraie cause : leur écart d'angle de teinte dans le plan Lab a\*/b\* n'est
+ que de 1,6° et 0,4° — ces couleurs ne diffèrent quasiment qu'en clarté/chroma,
+ pas en teinte. CIE76 (distance euclidienne L/a\*/b\*) traite cet écart comme
+ n'importe quel autre, alors que l'œil, sur une petite pastille, identifie
+ d'abord la teinte : deux nuances d'une même teinte se lisent comme UNE seule
+ couleur, pas deux. `actualise`/`gestionmail` n'a pas pu être mesurée sur la
+ couleur réelle (gestionmail est un projet créé après #535, sa couleur ne vit
+ que dans `configs/gestionmail.conf`, hors périmètre de ce worktree et de
+ toute façon jamais modifiable par CCL/CCW) — mais le même mécanisme est en
+ cause : `actualise` (ancienne valeur, teinte Lab ≈292°) se trouvait dans la
+ même zone bleu-violet que `ff_galerie` (285,5°), `gestionmail` (candidat le
+ plus proche de la palette de l'époque : `#9191FF`, ≈296°) et `chesscoach`
+ (318,3°).
+ 
+ **Correction (points 2 et 3)** : `nouveau_projet.py` — ajout d'un second seuil
+ de garde `SEUIL_ECART_TEINTE_MIN` (15°, écart minimal d'angle de teinte Lab
+ entre deux couleurs de la palette), complémentaire de `SEUIL_DISTANCE_MIN`
+ (remonté 15→20, défense en profondeur mais insuffisant seul ici : 56 et 52
+ sont déjà loin au-dessus). `generer_palette()` vérifie désormais les deux
+ seuils, par construction (filtrage des candidats) ET par assertion finale.
+ Correction ciblée de 4 couleurs seulement dans `COULEURS_PROJETS_EXISTANTS`
+ (les 7 autres restent inchangées, même esprit que la correction #534
+ ecole/ff_galerie) :
+ - `alchess` `#00FF00`→`#00D68F` (pas de champ COULEUR persisté en `.conf`,
+   contrairement à `rummikub` → conservée)
+ - `ecole` `#DE85FF`→`#CC7400` (pas de champ COULEUR persisté, contrairement à
+   `chesscoach` → conservée ; nouvelle teinte ambre/moutarde, clin d'œil à la
+   couleur qu'ecole portait déjà entre #534 et #535)
+ - `actualise` `#086BFF`→`#009DD6` (seul levier disponible côté code puisque
+   gestionmail — l'autre membre de la paire — n'est pas modifiable ; nouvelle
+   teinte délibérément écartée de toute la zone bleu-violet 197°-320°)
+ - `bloc_score` `#FFB0AB`→`#FF8595` : 4e paire découverte en appliquant le
+   nouveau seuil (non signalée dans l'issue) avec `bridge_agent` (écart de
+   teinte 13,2°, sous le nouveau plancher de 15°) — `bridge_agent` non
+   retouché, nouvelle teinte toujours rose/saumon pâle.
+ 
+ Toutes les paires (11 couleurs figées + palette régénérée) validées sans
+ violation par script (120 paires testées, contraste texte noir >= 4,5:1
+ conservé partout). `static/js/app.js` (`COULEURS_PROJET`) mis à jour en
+ synchro.
+ 
+ **Mécanisme de sélection pour les futurs projets (point 4)** :
+ `generer_palette()` accepte désormais un paramètre `couleurs_a_eviter`
+ (passé avec `COULEURS_PROJETS_EXISTANTS`) et l'utilise comme réservation
+ initiale de l'algorithme glouton — pas seulement en post-filtrage comme le
+ faisait déjà `couleurs_utilisees()`. Sans ce paramètre, la garantie de
+ distance/teinte ne portait que sur les couleurs générées ENTRE ELLES, jamais
+ sur les 11 couleurs gelées en dur : c'est exactement ce trou qui avait laissé
+ passer la collision `actualise`/`gestionmail` (gestionmail avait pris une
+ couleur de la palette, valide par rapport aux autres couleurs générées, mais
+ jamais vérifiée par rapport à `actualise`). Avec ce paramètre, toute couleur
+ encore proposée à un futur projet est garantie distincte de TOUS les projets
+ existants. Conséquence attendue : `NB_COULEURS_PALETTE` (30 demandées) ne
+ produit plus que 5 couleurs effectivement disponibles au-delà des 11
+ historiques (contre 40 avant #539) — la combinaison seuil de distance +
+ seuil de teinte limite mécaniquement le nombre de couleurs vraiment
+ distinctes sur le cercle chromatique ; à surveiller si de nombreux nouveaux
+ projets sont créés.
+ 
+ **Point d'attention laissé à Alain** : la couleur réelle de
+ `configs/gestionmail.conf` n'a pas pu être lue (hors périmètre du worktree
+ `/home/alain/bridge_agent-issue539`, et modification de `configs/*.conf`
+ interdite à CCL/CCW dans tous les cas) ni donc revérifiée contre la nouvelle
+ valeur d'`actualise`. À vérifier manuellement ; si elle s'avère encore trop
+ proche d'une des 11 couleurs figées (ou d'une future couleur de
+ `PALETTE_COULEURS`), seule une modification manuelle du `.conf` par Alain
+ peut la corriger.
  
  ## 11 septembre 2026 — issue #528
  
