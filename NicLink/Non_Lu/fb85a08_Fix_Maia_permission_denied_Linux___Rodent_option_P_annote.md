fb85a08

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit fb85a08
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 21 17:26:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Fix Maia permission denied Linux + Rodent option Personality (issue #197)
    
    - find_lc0() devient sensible à la plateforme (comme find_stockfish/
      find_rodent) : sous Linux/Mac, ne considère plus lc0.exe (présent à
      côté du binaire natif dans engines/maia/), qui causait un
      [Errno 13] Permission denied (fichier non exécutable, PE Windows).
    - Ajout de _ensure_executable() : positionne le bit +x sur le binaire
      lc0 avant lancement si absent, sans réinstallation requise.
    - RodentEngine : l'option UCI PersonalityFile n'existe pas sur le
      binaire installé (« does not support option PersonalityFile ») ;
      remplacée par Personality dans _apply_rodent_options(), les
      commentaires et RODENT_PERSONALITIES.
    
    Vérifié : lancement réel de Maia et Rodent OK, Stockfish sans
    régression, py_compile OK, 36 tests unitaires passent.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/engine/engine_manager.py b/nicsoft/engine/engine_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ca7cbac..8a20a5a 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/engine/engine_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/engine/engine_manager.py
# ── Zone modifiée : ligne 549 (7 ligne(s)) dans l'ancienne version → ligne 549 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -549,7 +549,7 @@ def rodent_available() -> bool:
 
 
 # ── Rodent IV : personnalités et bornes ──────────────────────────────────────
-# Valeurs EXACTES de l'option UCI combo "PersonalityFile" du binaire Rodent IV
+# Valeurs EXACTES de l'option UCI combo "Personality" du binaire Rodent IV
 # (relevées via `uci`). Le sélecteur UI doit envoyer une de ces valeurs telles
 # quelles ; toute autre valeur est refusée par le moteur. "Bosboom.txt" porte
 # bien l'extension dans la déclaration UCI (quirk du binaire).
# ── Zone modifiée : ligne 568 (22 ligne(s)) dans l'ancienne version → ligne 568 (54 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -568,22 +568,54 @@ RODENT_PERSONALITY_DEFAUT = "Tal"
 
 
 def find_lc0() -> str | None:
-    """Cherche l'exécutable lc0 sur le système."""
+    """
+    Cherche l'exécutable lc0 sur le système, selon la plateforme.
+
+    Les deux binaires (lc0 et lc0.exe) coexistent souvent dans engines/maia/
+    (release multi-plateforme) : il est impératif de ne considérer le .exe
+    que sous Windows, sinon Linux tente d'exécuter un PE et échoue (issue #197).
+    """
+    import sys
     import shutil
-    candidates = [
-        shutil.which("lc0"),
-        str(ENGINES_DIR / "maia" / "lc0.exe"),  # Windows
-        str(ENGINES_DIR / "maia" / "lc0"),       # Linux/Mac
-        str(Path.home() / "lc0" / "build" / "release" / "lc0"),
-        "/usr/local/bin/lc0",
-        "/usr/bin/lc0",
-    ]
+    if sys.platform == "win32":
+        candidates = [
+            shutil.which("lc0"),
+            str(ENGINES_DIR / "maia" / "lc0.exe"),
+        ]
+    else:
+        candidates = [
+            shutil.which("lc0"),
+            str(ENGINES_DIR / "maia" / "lc0"),
+            str(Path.home() / "lc0" / "build" / "release" / "lc0"),
+            "/usr/local/bin/lc0",
+            "/usr/bin/lc0",
+        ]
     for path in candidates:
         if path and Path(path).exists():
             return path
     return None
 
 
+def _ensure_executable(path: str) -> None:
+    """
+    S'assure que le binaire à `path` a le bit exécutable (Linux/Mac).
+    No-op sous Windows et si le bit est déjà positionné. Couvre les
+    installations où l'extraction (zip, clone) n'a pas préservé les
+    permissions d'origine (issue #197).
+    """
+    import sys
+    if sys.platform == "win32":
+        return
+    import os
+    import stat
+    try:
+        mode = os.stat(path).st_mode
+        if not (mode & stat.S_IXUSR):
+            os.chmod(path, mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
+    except OSError as e:
+        logger.warning(f"Impossible de positionner le bit exécutable sur {path} : {e}")
+
+
 def find_maia_weights(elo: int) -> str | None:
     """
     Cherche le fichier de poids Maia pour un niveau Elo donné.
# ── Zone modifiée : ligne 640 (6 ligne(s)) dans l'ancienne version → ligne 672 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -640,6 +672,7 @@ class MaiaEngine(EngineManager):
     def _init_maia(self, lc0_path: str, weights_path: str,
                    stockfish_path: str | None) -> None:
         """Lance lc0 avec les poids Maia + Stockfish pour l'analyse."""
+        _ensure_executable(lc0_path)
         try:
             # Moteur de jeu : lc0 + poids Maia
             self._engine_play = chess.engine.SimpleEngine.popen_uci(
# ── Zone modifiée : ligne 704 (12 ligne(s)) dans l'ancienne version → ligne 737 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -704,12 +737,14 @@ class RodentEngine(EngineManager):
     """
     Moteur Rodent IV — adversaire faible pensé pour les débutants.
 
-    Spécificités (cf. investigation issue #12) :
+    Spécificités (cf. investigation issue #12, corrigé issue #197) :
       - L'ordre d'envoi des `setoption` est IMPÉRATIF :
-          PersonalityFile → UCI_LimitStrength → UCI_Elo  (Elo TOUJOURS en dernier).
+          Personality → UCI_LimitStrength → UCI_Elo  (Elo TOUJOURS en dernier).
         Chaque option est envoyée dans son propre `configure()` pour garantir
         l'ordre indépendamment de l'implémentation de python-chess. Si l'Elo
         n'est pas envoyé en dernier, le moteur retombe à pleine puissance.
+      - L'option UCI s'appelle `Personality` (et non `PersonalityFile` — ce
+        binaire Rodent IV rejette ce nom avec "does not support option").
       - L'analyse (barre d'évaluation, qualité des coups) est déléguée à
         Stockfish : Rodent n'est pas conçu pour évaluer objectivement.
     """
# ── Zone modifiée : ligne 738 (7 ligne(s)) dans l'ancienne version → ligne 773 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -738,7 +773,7 @@ class RodentEngine(EngineManager):
 
     def _apply_rodent_options(self, engine: chess.engine.SimpleEngine) -> None:
         """
-        Envoie les options dans l'ordre impératif PersonalityFile → LimitStrength → Elo.
+        Envoie les options dans l'ordre impératif Personality → LimitStrength → Elo.
         Un `configure()` distinct par option = un `setoption` distinct, ordre garanti.
 
         Note (vérifié via logs UCI, issue #13) : python-chess n'émet PAS un
# ── Zone modifiée : ligne 746 (11 ligne(s)) dans l'ancienne version → ligne 781 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -746,11 +781,11 @@ class RodentEngine(EngineManager):
         par le moteur. Rodent IV déclare `UCI_LimitStrength` avec le défaut
         `true` → la ligne LimitStrength n'apparaît pas dans les logs (no-op),
         l'option étant déjà active. L'ordre réellement envoyé reste donc
-        PersonalityFile → UCI_Elo (Elo en dernier), ce qui satisfait la contrainte
+        Personality → UCI_Elo (Elo en dernier), ce qui satisfait la contrainte
         de l'issue #12. Robuste : si un build avait le défaut `false`,
         python-chess enverrait la ligne (valeur ≠ défaut).
         """
-        engine.configure({"PersonalityFile": self._personality})
+        engine.configure({"Personality": self._personality})
         engine.configure({"UCI_LimitStrength": True})
         engine.configure({"UCI_Elo": self._engine_elo})
 
# ── Zone modifiée : ligne 777 (7 ligne(s)) dans l'ancienne version → ligne 812 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -777,7 +812,7 @@ class RodentEngine(EngineManager):
             raise
 
     def set_elo(self, elo: int) -> None:
-        """Change l'Elo à chaud en respectant l'ordre PersonalityFile → LimitStrength → Elo."""
+        """Change l'Elo à chaud en respectant l'ordre Personality → LimitStrength → Elo."""
         self._engine_elo  = max(RODENT_ELO_MIN, min(RODENT_ELO_MAX, elo))
         self._engine_name = f"Rodent {self._engine_elo}"
         with self._lock_play:
