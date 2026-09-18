a056862

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a056862
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 13 23:22:06 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: _apply_rodent_options() use PersonalityFile not Personality

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/engine/engine_manager.py b/nicsoft/engine/engine_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 7ad1b10..ca7cbac 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/engine/engine_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/engine/engine_manager.py
# ── Zone modifiée : ligne 549 (7 ligne(s)) dans l'ancienne version → ligne 549 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -549,7 +549,7 @@ def rodent_available() -> bool:
 
 
 # ── Rodent IV : personnalités et bornes ──────────────────────────────────────
-# Valeurs EXACTES de l'option UCI combo "Personality" du binaire Rodent IV 0.33
+# Valeurs EXACTES de l'option UCI combo "PersonalityFile" du binaire Rodent IV
 # (relevées via `uci`). Le sélecteur UI doit envoyer une de ces valeurs telles
 # quelles ; toute autre valeur est refusée par le moteur. "Bosboom.txt" porte
 # bien l'extension dans la déclaration UCI (quirk du binaire).
# ── Zone modifiée : ligne 706 (7 ligne(s)) dans l'ancienne version → ligne 706 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -706,7 +706,7 @@ class RodentEngine(EngineManager):
 
     Spécificités (cf. investigation issue #12) :
       - L'ordre d'envoi des `setoption` est IMPÉRATIF :
-          Personality → UCI_LimitStrength → UCI_Elo  (Elo TOUJOURS en dernier).
+          PersonalityFile → UCI_LimitStrength → UCI_Elo  (Elo TOUJOURS en dernier).
         Chaque option est envoyée dans son propre `configure()` pour garantir
         l'ordre indépendamment de l'implémentation de python-chess. Si l'Elo
         n'est pas envoyé en dernier, le moteur retombe à pleine puissance.
# ── Zone modifiée : ligne 738 (7 ligne(s)) dans l'ancienne version → ligne 738 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -738,7 +738,7 @@ class RodentEngine(EngineManager):
 
     def _apply_rodent_options(self, engine: chess.engine.SimpleEngine) -> None:
         """
-        Envoie les options dans l'ordre impératif Personality → LimitStrength → Elo.
+        Envoie les options dans l'ordre impératif PersonalityFile → LimitStrength → Elo.
         Un `configure()` distinct par option = un `setoption` distinct, ordre garanti.
 
         Note (vérifié via logs UCI, issue #13) : python-chess n'émet PAS un
# ── Zone modifiée : ligne 746 (11 ligne(s)) dans l'ancienne version → ligne 746 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -746,11 +746,11 @@ class RodentEngine(EngineManager):
         par le moteur. Rodent IV déclare `UCI_LimitStrength` avec le défaut
         `true` → la ligne LimitStrength n'apparaît pas dans les logs (no-op),
         l'option étant déjà active. L'ordre réellement envoyé reste donc
-        Personality → UCI_Elo (Elo en dernier), ce qui satisfait la contrainte
+        PersonalityFile → UCI_Elo (Elo en dernier), ce qui satisfait la contrainte
         de l'issue #12. Robuste : si un build avait le défaut `false`,
         python-chess enverrait la ligne (valeur ≠ défaut).
         """
-        engine.configure({"Personality": self._personality})
+        engine.configure({"PersonalityFile": self._personality})
         engine.configure({"UCI_LimitStrength": True})
         engine.configure({"UCI_Elo": self._engine_elo})
 
# ── Zone modifiée : ligne 777 (7 ligne(s)) dans l'ancienne version → ligne 777 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -777,7 +777,7 @@ class RodentEngine(EngineManager):
             raise
 
     def set_elo(self, elo: int) -> None:
-        """Change l'Elo à chaud en respectant l'ordre Personality → LimitStrength → Elo."""
+        """Change l'Elo à chaud en respectant l'ordre PersonalityFile → LimitStrength → Elo."""
         self._engine_elo  = max(RODENT_ELO_MIN, min(RODENT_ELO_MAX, elo))
         self._engine_name = f"Rodent {self._engine_elo}"
         with self._lock_play:
