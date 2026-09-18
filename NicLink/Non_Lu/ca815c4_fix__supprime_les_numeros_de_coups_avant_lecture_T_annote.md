ca815c4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit ca815c4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 16 10:38:35 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: supprime les numeros de coups avant lecture TTS (issue #169, suite #168)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c8cb561..2a1f64d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 80 (6 ligne(s)) dans l'ancienne version → ligne 80 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -80,6 +80,7 @@ def strip_markdown(text: str) -> str:
     text = re.sub(r'__(.+?)__', r'\1', text)
     text = re.sub(r'\*(.+?)\*', r'\1', text)
     text = re.sub(r'_(.+?)_', r'\1', text)
+    text = re.sub(r'\b\d+\.{1,3}\s*', '', text)
     text = re.sub(r'\n+', ' ', text)
     return text.strip()
 
