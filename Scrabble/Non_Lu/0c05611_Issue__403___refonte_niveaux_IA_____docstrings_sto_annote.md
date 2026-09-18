0c05611

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0c05611
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 13:59:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #403 : refonte niveaux IA — docstrings stockage.py/partie.py (C/4)
    
    Met à jour le docstring de Partie (partie.py) : EXPERT rejoint désormais
    CHAMPION_DU_MONDE comme niveau absent du mapping de paliers (vocabulaire
    complet), suite à la refonte de l'échelle (issue #401) où EXPERT n'a plus
    de palier restreint contrairement à l'ancien mapping. Aucun changement de
    logique. stockage.py ne contenait aucun commentaire décrivant la sémantique
    par palier d'un niveau spécifique — laissé inchangé.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/moteur/partie.py b/src/scrabble/moteur/partie.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 43014b2..b8391b5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/moteur/partie.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/moteur/partie.py
# ── Zone modifiée : ligne 314 (11 ligne(s)) dans l'ancienne version → ligne 314 (13 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -314,11 +314,13 @@ class Partie:
     désormais jouer sur deux vocabulaires distincts (un palier de fréquence par
     niveau, voir ``scrabble.moteur.ia.resoudre_palier``). Un niveau **absent**
     du mapping (dont ``dictionnaires_ia`` vide ou ``None``, tout comme
-    :data:`~scrabble.moteur.ia.Niveau.CHAMPION_DU_MONDE` construit sans entrée)
-    retombe sur ``dictionnaire`` complet — comportement historique inchangé et
-    défensif, conservé même si l'appelant UI construit désormais toujours le
-    mapping par palier sans condition (issue #370, lot E : suppression du
-    réglage global « vocabulaire humain », issue #206).
+    :data:`~scrabble.moteur.ia.Niveau.EXPERT` et
+    :data:`~scrabble.moteur.ia.Niveau.CHAMPION_DU_MONDE` construits sans
+    entrée — refonte de l'échelle, issue #401) retombe sur ``dictionnaire``
+    complet — comportement historique inchangé et défensif, conservé même si
+    l'appelant UI construit désormais toujours le mapping par palier sans
+    condition (issue #370, lot E : suppression du réglage global « vocabulaire
+    humain », issue #206).
     """
 
     def __init__(
