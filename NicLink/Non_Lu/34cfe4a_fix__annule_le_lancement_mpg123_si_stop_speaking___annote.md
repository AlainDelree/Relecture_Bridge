34cfe4a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 34cfe4a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 20:45:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: annule le lancement mpg123 si stop_speaking() pendant download edge-tts (issue #166, suite #165)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6052b6c..c8cb561 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 20 (6 ligne(s)) dans l'ancienne version → ligne 20 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -20,6 +20,7 @@ import tempfile
 logger = logging.getLogger("niclink.opening_explorer.tts")
 
 _current_tts_process: "subprocess.Popen | None" = None
+_tts_generation: int = 0
 
 
 VOICE_MAP_EDGE = {
# ── Zone modifiée : ligne 103 (6 ligne(s)) dans l'ancienne version → ligne 104 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -103,6 +104,7 @@ def check_internet() -> bool:
 
 def _speak_edge(text: str, rate: int, language: str) -> bool:
     """Essaie de parler via edge-tts. Retourne True si succès, False sinon."""
+    global _tts_generation
     try:
         import edge_tts
 
# ── Zone modifiée : ligne 110 (14 ligne(s)) dans l'ancienne version → ligne 112 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -110,14 +112,17 @@ def _speak_edge(text: str, rate: int, language: str) -> bool:
         # rate edge-tts : "+0%" = 150 mots/min ≈ normal
         # on convertit le rate (mots/min) en pourcentage relatif
         rate_pct = f"+{int((rate - 150) / 1.5)}%" if rate != 150 else "+0%"
+        my_gen = _tts_generation
 
         async def _run():
+            global _current_tts_process
             with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                 tmp = f.name
             try:
                 communicate = edge_tts.Communicate(text, voice, rate=rate_pct)
                 await communicate.save(tmp)
-                global _current_tts_process
+                if _tts_generation != my_gen:
+                    return  # stop_speaking() appelé pendant le download
                 proc = subprocess.Popen(["mpg123", "-q", tmp])
                 _current_tts_process = proc
                 proc.wait()
# ── Zone modifiée : ligne 150 (7 ligne(s)) dans l'ancienne version → ligne 155 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -150,7 +155,8 @@ def _speak_espeak(text: str, rate: int, language: str) -> None:
 
 def stop_speaking() -> None:
     """Interrompt immédiatement la lecture mpg123 en cours, si active."""
-    global _current_tts_process
+    global _current_tts_process, _tts_generation
+    _tts_generation += 1
     proc = _current_tts_process
     if proc is not None and proc.poll() is None:
         proc.terminate()
