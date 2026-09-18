9e71bba

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9e71bba
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 14:46:09 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #437 : bip() devient un son de cloche (880 Hz, enveloppe exponentielle), bip_plat() conservée en référence

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/scripts/traitement_fin.py b/scripts/traitement_fin.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 53cfeea..c1eb8e1 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/scripts/traitement_fin.py
# ── Version APRÈS ce commit.
+++ b/scripts/traitement_fin.py
# ── Zone modifiée : ligne 25 (17 ligne(s)) dans l'ancienne version → ligne 25 (40 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,17 +25,40 @@ import tempfile
 import urllib.request
 import wave
 
-F   = 440       # fréquence Hz
-DUR = 0.4       # durée secondes
-SR  = 44100     # sample rate
+F     = 880     # fréquence Hz
+DUR   = 1.5     # durée secondes
+SR    = 44100   # sample rate
+DECAY = 5       # facteur de décroissance de l'enveloppe exponentielle
 
 URL_NOTIFIER_FIN_ISSUE     = "http://localhost:5100/notifier-fin-issue"
 TIMEOUT_NOTIFIER_FIN_ISSUE = 1   # s — new_issue.py non lancé ne doit jamais retarder le bip
 
 
+def bip_plat():
+    """Bip sonore court (440 Hz, 0.4 s), sinusoïde plate — ancienne implémentation
+    conservée comme référence, non appelée (voir issue #437)."""
+    f_plat, dur_plat = 440, 0.4
+    samples = [int(32767 * math.sin(2 * math.pi * f_plat * t / SR)) for t in range(int(SR * dur_plat))]
+    data = struct.pack('<' + 'h' * len(samples), *samples)
+
+    tmp = tempfile.mktemp(suffix='.wav')
+    w = wave.open(tmp, 'w')
+    w.setnchannels(1)
+    w.setsampwidth(2)
+    w.setframerate(SR)
+    w.writeframes(data)
+    w.close()
+
+    os.system(f'aplay {tmp} 2>/dev/null')
+    os.remove(tmp)
+
+
 def bip():
-    """Bip sonore court (440 Hz, 0.4 s) via aplay."""
-    samples = [int(32767 * math.sin(2 * math.pi * F * t / SR)) for t in range(int(SR * DUR))]
+    """Son de cloche douce (880 Hz, enveloppe exponentielle décroissante) via aplay."""
+    samples = [
+        int(32767 * math.sin(2 * math.pi * F * t / SR) * math.exp(-t * DECAY / SR))
+        for t in range(int(SR * DUR))
+    ]
     data = struct.pack('<' + 'h' * len(samples), *samples)
 
     tmp = tempfile.mktemp(suffix='.wav')
