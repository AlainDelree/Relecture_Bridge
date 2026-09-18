e08a188

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e08a188
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 20:35:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: TTS Opening Explorer — aplay incapable de lire le MP3 edge-tts, remplacé par mpg123 (issue #154)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bootstrap_linux.sh b/bootstrap_linux.sh
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5e73661..25126b5 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bootstrap_linux.sh
# ── Version APRÈS ce commit.
+++ b/bootstrap_linux.sh
# ── Zone modifiée : ligne 59 (14 ligne(s)) dans l'ancienne version → ligne 59 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -59,14 +59,14 @@ if ! command -v espeak-ng &>/dev/null; then
     fi
 fi
 
-# 4b. aplay / alsa-utils (lecture audio des voix neuronales edge-tts)
-if ! command -v aplay &>/dev/null; then
-    echo "Installation d'alsa-utils (lecture audio)..."
+# 4b. mpg123 (lecture MP3 des voix neuronales edge-tts)
+if ! command -v mpg123 &>/dev/null; then
+    echo "Installation de mpg123 (lecture audio)..."
     if sudo -n true 2>/dev/null; then
-        sudo apt-get install -y alsa-utils
+        sudo apt-get install -y mpg123
     else
-        echo "AVERTISSEMENT : droits sudo requis pour installer alsa-utils."
-        echo "Exécutez manuellement : sudo apt-get install alsa-utils"
+        echo "AVERTISSEMENT : droits sudo requis pour installer mpg123."
+        echo "Exécutez manuellement : sudo apt-get install mpg123"
     fi
 fi
 
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# (index — ignorable)
index c54e4be..cccba12 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 40 (7 ligne(s)) dans l'ancienne version → ligne 40 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -40,7 +40,7 @@ def _speak_edge(text: str, rate: int, language: str) -> bool:
             try:
                 communicate = edge_tts.Communicate(text, voice, rate=rate_pct)
                 await communicate.save(tmp)
-                subprocess.run(["aplay", tmp], check=False, timeout=60)
+                subprocess.run(["mpg123", "-q", tmp], check=False, timeout=60)
             finally:
                 try:
                     os.unlink(tmp)
