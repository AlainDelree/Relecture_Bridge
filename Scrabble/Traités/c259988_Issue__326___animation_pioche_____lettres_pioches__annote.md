c259988

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c259988
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 09:23:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #326 : animation pioche — lettres_pioches correctes pour echanger_tout et echanger_selection (suite #325)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/src/scrabble/ui/api_echange.py b/src/scrabble/ui/api_echange.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 206147b..23020fd 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/src/scrabble/ui/api_echange.py
# ── Version APRÈS ce commit.
+++ b/src/scrabble/ui/api_echange.py
# ── Zone modifiée : ligne 57 (21 ligne(s)) dans l'ancienne version → ligne 57 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -57,21 +57,19 @@ class MixinEchange:
         ``{"succes": False, "erreur": <message clair>}`` — l'état n'est pas
         modifié.
         """
-        from collections import Counter
-
         from scrabble.ui import jeu as mod_jeu
         from scrabble.ui.jeu import echanger_chevalet_complet, index_humain_reference
 
         nom = self._partie.joueur_courant().nom
         nb_avant = len(self._partie.historique)
-        # Capture du chevalet du joueur de référence avant l'échange, pour en
-        # déduire par diff les lettres tout juste piochées (issue #325).
         index_ref = index_humain_reference(self._partie.joueurs)
-        avant = list(self._partie.joueurs[index_ref].chevalet)
         resultat = echanger_chevalet_complet(self._partie, self._id_partie)
         if resultat.get("succes"):
             apres = self._partie.joueurs[index_ref].chevalet
-            self._lettres_pioches = list((Counter(apres) - Counter(avant)).elements())
+            # Échange complet : tout le chevalet est rendu et remplacé, donc
+            # les lettres piochées sont exactement le nouveau chevalet
+            # (issue #326).
+            self._lettres_pioches = list(apres)
             mod_jeu.journal.info(f"Jeu : échange complet du chevalet par {nom}.")
             self._persister_entrees(self._partie.historique[nb_avant:])
             self._finaliser_si_terminee()
# ── Zone modifiée : ligne 213 (7 ligne(s)) dans l'ancienne version → ligne 211 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -213,7 +211,16 @@ class MixinEchange:
         resultat = echanger_jetons(self._partie, self._id_partie, jetons)
         if resultat.get("succes"):
             apres = self._partie.joueurs[index_ref].chevalet
-            self._lettres_pioches = list((Counter(apres) - Counter(avant)).elements())
+            # Échange partiel : les lettres gardées = avant moins les jetons
+            # échangés (connus précisément) ; les lettres piochées = apres
+            # moins les gardées (issue #326).
+            gardes = list(avant)
+            for j in jetons:
+                if j in gardes:
+                    gardes.remove(j)
+            self._lettres_pioches = list(
+                (Counter(apres) - Counter(gardes)).elements()
+            )
             mod_jeu.journal.info(
                 f"Jeu : échange partiel de {len(jetons)} lettre(s) par {nom}."
             )
