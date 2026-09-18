1a342bd

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 1a342bd
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 20:29:50 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: Opening Explorer TTS via edge-tts (voix neuronales) + fallback espeak-ng (issue #153)
    
    tts_engine.speak() essaie d'abord edge-tts (voix neuronales Microsoft,
    internet requis) puis bascule automatiquement sur espeak-ng si edge-tts
    echoue. Signature de speak() inchangee. Ajout edge-tts>=6.1.0 dans
    requirements.txt et verification alsa-utils (aplay) dans bootstrap_linux.sh.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bootstrap_linux.sh b/bootstrap_linux.sh
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 67da792..5e73661 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bootstrap_linux.sh
# ── Version APRÈS ce commit.
+++ b/bootstrap_linux.sh
# ── Zone modifiée : ligne 48 (7 ligne(s)) dans l'ancienne version → ligne 48 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -48,7 +48,7 @@ echo "Installation des dépendances..."
 "$INSTALL_DIR/venv/bin/pip" install --upgrade pip --quiet
 "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" --quiet
 
-# 4. espeak-ng (moteur TTS système requis par pyttsx3 pour la synthèse vocale)
+# 4. espeak-ng (fallback TTS hors ligne pour Opening Explorer)
 if ! command -v espeak-ng &>/dev/null; then
     echo "Installation d'espeak-ng (synthèse vocale)..."
     if sudo -n true 2>/dev/null; then
# ── Zone modifiée : ligne 59 (6 ligne(s)) dans l'ancienne version → ligne 59 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -59,6 +59,17 @@ if ! command -v espeak-ng &>/dev/null; then
     fi
 fi
 
+# 4b. aplay / alsa-utils (lecture audio des voix neuronales edge-tts)
+if ! command -v aplay &>/dev/null; then
+    echo "Installation d'alsa-utils (lecture audio)..."
+    if sudo -n true 2>/dev/null; then
+        sudo apt-get install -y alsa-utils
+    else
+        echo "AVERTISSEMENT : droits sudo requis pour installer alsa-utils."
+        echo "Exécutez manuellement : sudo apt-get install alsa-utils"
+    fi
+fi
+
 # 5. Règles udev Chessnut (optionnel — demande sudo)
 UDEV_RULE='SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", MODE="0666", GROUP="plugdev", TAG+="uaccess"'
 UDEV_FILE="/etc/udev/rules.d/99-chessnut-alchess.rules"
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# (index — ignorable)
index 8eee0d6..c54e4be 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 1 (33 ligne(s)) dans l'ancienne version → ligne 1 (80 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,33 +1,80 @@
 """
 nicsoft/modes/opening_explorer/tts_engine.py — NicLink
-Synthèse vocale des explications Opening Explorer via espeak-ng en
-subprocess direct. pyttsx3 abandonné : le GC détruisait l'engine pendant
-le callback espeak, provoquant des ReferenceError après un ou deux mots.
+Synthèse vocale des explications Opening Explorer via edge-tts (voix
+neuronales Microsoft, internet requis), avec fallback automatique sur
+espeak-ng en subprocess direct si edge-tts échoue (pas d'internet, etc.).
+pyttsx3 abandonné : le GC détruisait l'engine pendant le callback espeak,
+provoquant des ReferenceError après un ou deux mots.
 """
 
+import asyncio
 import logging
+import os
 import subprocess
+import tempfile
 
 logger = logging.getLogger("niclink.opening_explorer.tts")
 
 
-VOICE_MAP = {"fr": "fr", "en": "en", "de": "de"}
+VOICE_MAP_EDGE = {
+    "fr": "fr-FR-DeniseNeural",
+    "en": "en-GB-SoniaNeural",
+    "de": "de-DE-KatjaNeural",
+}
+VOICE_MAP_ESPEAK = {"fr": "fr", "en": "en", "de": "de"}
 
 
-def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr") -> None:
-    """Prononce `text` à voix haute si `enabled`, dans la langue `language`
-    (voix espeak-ng correspondante si disponible). Bloquant — à appeler
-    depuis un thread daemon, jamais depuis le thread principal.
-    Erreur silencieuse (espeak-ng manquant, etc.).
-    """
-    if not enabled or not text:
-        return
-    lang = VOICE_MAP.get(language, "fr")
+def _speak_edge(text: str, rate: int, language: str) -> bool:
+    """Essaie de parler via edge-tts. Retourne True si succès, False sinon."""
+    try:
+        import edge_tts
+
+        voice = VOICE_MAP_EDGE.get(language, "fr-FR-DeniseNeural")
+        # rate edge-tts : "+0%" = 150 mots/min ≈ normal
+        # on convertit le rate (mots/min) en pourcentage relatif
+        rate_pct = f"+{int((rate - 150) / 1.5)}%" if rate != 150 else "+0%"
+
+        async def _run():
+            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
+                tmp = f.name
+            try:
+                communicate = edge_tts.Communicate(text, voice, rate=rate_pct)
+                await communicate.save(tmp)
+                subprocess.run(["aplay", tmp], check=False, timeout=60)
+            finally:
+                try:
+                    os.unlink(tmp)
+                except Exception:
+                    pass
+
+        asyncio.run(_run())
+        return True
+    except Exception as e:
+        logger.warning(f"[TTS] edge-tts échoué : {e}")
+        return False
+
+
+def _speak_espeak(text: str, rate: int, language: str) -> None:
+    """Fallback espeak-ng."""
+    lang = VOICE_MAP_ESPEAK.get(language, "fr")
     try:
         subprocess.run(
             ["espeak-ng", "-v", lang, "-s", str(rate), text],
             timeout=60,
-            check=False
+            check=False,
         )
     except Exception as e:
-        logger.warning(f"[TTS] Échec espeak-ng : {e}")
+        logger.warning(f"[TTS] espeak-ng échoué : {e}")
+
+
+def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr") -> None:
+    """Prononce `text` à voix haute si `enabled`, dans la langue `language`.
+    Essaie d'abord edge-tts (voix neuronale, internet requis) puis bascule
+    automatiquement sur espeak-ng si edge-tts échoue. Bloquant — à appeler
+    depuis un thread daemon, jamais depuis le thread principal.
+    Erreur silencieuse (ni edge-tts ni espeak-ng disponibles, etc.).
+    """
+    if not enabled or not text:
+        return
+    if not _speak_edge(text, rate, language):
+        _speak_espeak(text, rate, language)
# (diff du fichier suivant)
diff --git a/requirements.txt b/requirements.txt
# (index — ignorable)
index fd7a00f..28424e6 100755
# (avant — fichier suivant)
--- a/requirements.txt
# (après — fichier suivant)
+++ b/requirements.txt
# ── Zone modifiée : ligne 15 (3 ligne(s)) dans l'ancienne version → ligne 15 (4 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -15,3 +15,4 @@ python-socketio==5.16.1
 Werkzeug==3.1.7
 # pyttsx3 nécessite un moteur TTS système : espeak-ng sur Linux (sudo apt install espeak-ng)
 pyttsx3==2.98
+edge-tts>=6.1.0
