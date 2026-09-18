a962f8a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a962f8a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 27 19:59:07 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #498 : interrupteur global de son (plat/cloche) via scripts/son_actif.txt
    
    traitement_fin.py lit désormais scripts/son_actif.txt (une ligne : plat ou
    cloche) au démarrage pour choisir entre bip_plat() et bip() -- un seul
    fichier pilote le son pour tous les projets utilisant le script partagé,
    sans plus avoir à passer par un SCRIPT_BIP dédié par variante. Fichier
    absent/illisible/valeur inconnue -> défaut plat inchangé. Fichier créé avec
    la valeur par défaut plat. Docstring de traitement_fin.py et
    BRIDGE_AGENT_DOC.md (§ bip/notifications) mis à jour. configs/*.conf non
    touchés (garde-fou §11).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 507e684..c790521 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1968 (6 ligne(s)) dans l'ancienne version → ligne 1968 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1968,6 +1968,20 @@ new_issue.py (ThinkPad) → polling gh → détecte la transition → bip/bulle/
   vers lui. **La clé de config reste `SCRIPT_BIP`** (renommer impliquerait de
   modifier les `configs/*.conf` gitignorés, hors périmètre agent — voir §17.3
   pour la marche à suivre manuelle).
+- **Choix du son : `scripts/son_actif.txt` (#498).** Le script contient deux
+  implémentations de bip — `bip_plat()` (440 Hz, sinusoïde plate) et `bip()`
+  (880 Hz, cloche à enveloppe exponentielle décroissante ; voir #437 et sa
+  révocation). Historiquement un projet isolé (ex. ff_galerie) pouvait obtenir
+  la cloche en pointant `SCRIPT_BIP` vers un script dédié
+  (`scripts/bip_Cloche.py`) — lourd, et il aurait fallu éditer `SCRIPT_BIP`
+  dans chaque `.conf` pour changer le son de tous les projets à la fois.
+  `main()` lit désormais un fichier unique `scripts/son_actif.txt` (une seule
+  ligne : `plat` ou `cloche`) au démarrage, **avant** d'appeler `bip_plat()`
+  ou `bip()` — un seul endroit pilote donc le son pour **tous** les projets
+  utilisant le script partagé. Fichier absent, illisible, ou valeur non
+  reconnue → défaut inchangé (`plat`), pour ne rien casser silencieusement.
+  Ce fichier n'est **pas** un `configs/*.conf` : le garde-fou §11 ne s'y
+  applique pas.
 
 **Éviter le spam de vieilles issues au démarrage.** Deux garde-fous combinés :
 - **filtre de récence** : seules les transitions horodatées dans les
# (diff du fichier suivant)
diff --git a/scripts/son_actif.txt b/scripts/son_actif.txt
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..c1f271b
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/scripts/son_actif.txt
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (1 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1 @@
+plat
# (diff du fichier suivant)
diff --git a/scripts/traitement_fin.py b/scripts/traitement_fin.py
# (index — ignorable)
index dc8377a..3254d1b 100644
# (avant — fichier suivant)
--- a/scripts/traitement_fin.py
# (après — fichier suivant)
+++ b/scripts/traitement_fin.py
# ── Zone modifiée : ligne 11 (6 ligne(s)) dans l'ancienne version → ligne 11 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -11,6 +11,15 @@ d'attendre un ↻ manuel ou le fetch post-TIMEOUT de #334. Le POST est silencieu
 en cas d'échec (new_issue.py non lancé, port fermé, etc.) : le bip reste
 fonctionnel indépendamment de ce canal.
 
+Choix du son (issue #498) : `main()` lit `scripts/son_actif.txt` (une seule
+ligne, `plat` ou `cloche`) pour décider quelle implémentation appeler —
+`bip_plat()` (440 Hz, sinusoïde plate) ou `bip()` (880 Hz, cloche à enveloppe
+exponentielle décroissante ; voir #437 et sa révocation). Ce seul fichier
+pilote le son pour TOUS les projets utilisant ce script partagé (via
+`SCRIPT_BIP`), sans avoir à toucher aux `configs/*.conf` individuels. Fichier
+absent, illisible, ou contenant une valeur non reconnue → défaut inchangé
+(`plat`), pour ne rien casser silencieusement.
+
 Usage :
     python3 traitement_fin.py                                   # un bip seul
     python3 traitement_fin.py --projet bridge_agent --numero 350 # bip + POST
# ── Zone modifiée : ligne 33 (10 ligne(s)) dans l'ancienne version → ligne 42 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -33,10 +42,12 @@ DECAY = 5       # facteur de décroissance de l'enveloppe exponentielle
 URL_NOTIFIER_FIN_ISSUE     = "http://localhost:5100/notifier-fin-issue"
 TIMEOUT_NOTIFIER_FIN_ISSUE = 1   # s — new_issue.py non lancé ne doit jamais retarder le bip
 
+FICHIER_SON_ACTIF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "son_actif.txt")
+
 
 def bip_plat():
-    """Bip sonore court (440 Hz, 0.4 s), sinusoïde plate — ancienne implémentation
-    conservée comme référence, non appelée (voir issue #437)."""
+    """Bip sonore court (440 Hz, 0.4 s), sinusoïde plate — son par défaut
+    (voir issue #437 et #498, `son_actif()` ci-dessous pour le choix du son)."""
     f_plat, dur_plat = 440, 0.4
     samples = [int(32767 * math.sin(2 * math.pi * f_plat * t / SR)) for t in range(int(SR * dur_plat))]
     data = struct.pack('<' + 'h' * len(samples), *samples)
# ── Zone modifiée : ligne 73 (6 ligne(s)) dans l'ancienne version → ligne 84 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -73,6 +84,19 @@ def bip():
     os.remove(tmp)
 
 
+def son_actif() -> str:
+    """Lit `FICHIER_SON_ACTIF` ('plat' ou 'cloche'). Absent, illisible, ou valeur
+    non reconnue → 'plat' (défaut inchangé, ne casse rien silencieusement)."""
+    try:
+        with open(FICHIER_SON_ACTIF, "r", encoding="utf-8") as f:
+            valeur = f.read().strip().lower()
+        if valeur in ("plat", "cloche"):
+            return valeur
+    except OSError:
+        pass
+    return "plat"
+
+
 def notifier_fin_issue(projet: str, numero: str):
     """POST best-effort vers new_issue.py (issue #350) : pousse un événement SSE
     `fin_issue` à l'onglet Résultats déjà ouvert. Timeout court et échec
# ── Zone modifiée : ligne 97 (7 ligne(s)) dans l'ancienne version → ligne 121 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -97,7 +121,10 @@ def main():
                         help="Numéro de l'issue (déclenche le POST /notifier-fin-issue avec --projet)")
     args = parser.parse_args()
 
-    bip_plat()
+    if son_actif() == "cloche":
+        bip()
+    else:
+        bip_plat()
 
     if args.projet and args.numero:
         notifier_fin_issue(args.projet, args.numero)
