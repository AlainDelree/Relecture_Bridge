61fca95

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 61fca95
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Jul 24 07:31:16 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #230 : isoler test_avatar_expose_dans_etat_public du config.json réel
    
    Le test comparait etat_public() — qui lit avatar_principal depuis le
    config.json de la machine (issue #143) — au calcul direct calculer_avatars()
    avec le défaut vide. Sur un poste de dév où config.json contient
    avatar_principal='avatar-01', l'humaine se voyait réserver avatar-01 côté
    etat_public vs avatar-03 (tirage par graine) côté calcul direct, d'où l'echec
    préexistant 'avatar-01' != 'avatar-03'.
    
    Le code d'attribution est correct ; le test manquait d'isolation. On mocke
    charger_config -> {} via monkeypatch, comme le fait déjà le voisin
    test_avatar_principal_applique_dans_etat_public, rendant le test déterministe
    et indépendant de la config persistante.
    
    Suite : 747 passed, 0 failed.
    
    Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/tests/test_jeu.py b/tests/test_jeu.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index a91a62c..175a92e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/tests/test_jeu.py
# ── Version APRÈS ce commit.
+++ b/tests/test_jeu.py
# ── Zone modifiée : ligne 1139 (7 ligne(s)) dans l'ancienne version → ligne 1139 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1139,7 +1139,14 @@ class TestCalculerAvatars:
         # Les avatars distincts saturent la bibliothèque avant les doublons.
         assert len(set(avatars)) == len(AVATARS)
 
-    def test_avatar_expose_dans_etat_public(self):
+    def test_avatar_expose_dans_etat_public(self, monkeypatch):
+        # On isole le test du config.json réel de la machine : etat_public lit
+        # avatar_principal de la config (issue #143) et un poste de dév peut y
+        # avoir un avatar choisi, ce qui ferait diverger l'attribution du calcul
+        # direct par défaut ci-dessous (avatar_principal absent = "").
+        import scrabble.ui.jeu as jeu
+
+        monkeypatch.setattr(jeu, "charger_config", lambda: {})
         joueurs = [
             Joueur(nom="Alice", humain=True),
             Joueur(nom="Robot", humain=False, niveau=Niveau.FACILE),
