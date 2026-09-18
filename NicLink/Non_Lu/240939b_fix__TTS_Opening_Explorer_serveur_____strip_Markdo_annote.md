240939b

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 240939b
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 21:49:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: TTS Opening Explorer serveur — strip Markdown avant edge-tts (issue #156, suite #155)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 3229660..3d9e78a 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 27 (6 ligne(s)) dans l'ancienne version → ligne 27 (18 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -27,6 +27,18 @@ VOICE_MAP_EDGE = {
 VOICE_MAP_ESPEAK = {"fr": "fr", "en": "en", "de": "de"}
 
 
+def strip_markdown(text: str) -> str:
+    """Retire les marqueurs Markdown (titres, gras, italique) avant lecture TTS."""
+    import re
+    text = re.sub(r'#{1,6}\s*', '', text)
+    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
+    text = re.sub(r'__(.+?)__', r'\1', text)
+    text = re.sub(r'\*(.+?)\*', r'\1', text)
+    text = re.sub(r'_(.+?)_', r'\1', text)
+    text = re.sub(r'\n+', ' ', text)
+    return text.strip()
+
+
 def check_internet() -> bool:
     """Test rapide (2s max) de connectivité, pour décider edge-tts vs Web Speech API."""
     try:
# ── Zone modifiée : ligne 96 (6 ligne(s)) dans l'ancienne version → ligne 108 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -96,6 +108,7 @@ def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr
     edge-tts) — dans ce cas l'appelant doit basculer sur le Web Speech API
     côté navigateur (pas d'espeak-ng comme fallback serveur).
     """
+    text = strip_markdown(text)
     if not enabled or not text:
         return False
     if not check_internet():
