0a3eaaf

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0a3eaaf
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 19:45:31 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #389 : _executer_ps/_executer_commande_ps décodent stdout/stderr en cp1252 (errors=replace)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG.md b/CHANGELOG.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index f093999..3832647 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/CHANGELOG.md
# ── Version APRÈS ce commit.
+++ b/CHANGELOG.md
# ── Zone modifiée : ligne 9 (6 ligne(s)) dans l'ancienne version → ligne 9 (19 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,6 +9,19 @@ milliers de caractères sur une seule ligne logique, coûteux à relire et
 
 Convention d'ajout : voir §10 de `BRIDGE_AGENT_DOC.md`.
 
+## 7 août 2026 — issue #389
+
+Fix `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x82` lors de la
+finalisation d'un projet CCW : la sortie de `powershell.exe` exécuté dans
+la VM invitée est encodée en CP1252 (page de code Windows par défaut), pas
+en UTF-8.
+- `app/ccw.py` : `_executer_ps` et `_executer_commande_ps` (même schéma —
+  toutes deux lancent `powershell.exe` via `guestcontrol run`) décodent
+  désormais `stdout`/`stderr` en `encoding="cp1252"` avec `errors="replace"`
+  en filet de sécurité, au lieu de `text=True` (UTF-8 implicite côté hôte
+  Linux). `_copier` (guestcontrol `copyto`, ne lance aucun processus dans
+  la VM) n'était pas concernée, laissée inchangée.
+
 ## 6 août 2026 — issue #384
 
 Panneau flottant actions : toggles `notif_pc`/`notif_gsm`/`notif_tous` sur
# (diff du fichier suivant)
diff --git a/app/ccw.py b/app/ccw.py
# (index — ignorable)
index 5ad45c7..556c6c5 100644
# (avant — fichier suivant)
--- a/app/ccw.py
# (après — fichier suivant)
+++ b/app/ccw.py
# ── Zone modifiée : ligne 137 (7 ligne(s)) dans l'ancienne version → ligne 137 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -137,7 +137,11 @@ def _copier(base: list[str], source_local: Path, timeout: int):
 
 
 def _executer_ps(base: list[str], nom_script: str, args_ps: list[str], timeout: int):
-    """Exécute un script .ps1 (déjà poussé dans DEST_DIR_INVITE) via powershell.exe."""
+    """Exécute un script .ps1 (déjà poussé dans DEST_DIR_INVITE) via powershell.exe.
+
+    stdout/stderr proviennent de la console Windows de la VM, encodée en
+    CP1252 (page de code par défaut), pas en UTF-8 — d'où le décodage
+    explicite ci-dessous (errors="replace" en filet de sécurité)."""
     dest = DEST_DIR_INVITE + nom_script
     cmd = base + [
         "run",
# ── Zone modifiée : ligne 147 (7 ligne(s)) dans l'ancienne version → ligne 151 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -147,7 +151,8 @@ def _executer_ps(base: list[str], nom_script: str, args_ps: list[str], timeout:
         "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", dest,
     ] + args_ps
-    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
+    return subprocess.run(cmd, capture_output=True, encoding="cp1252",
+                           errors="replace", timeout=timeout)
 
 
 def _executer_commande_ps(base: list[str], commande: str, timeout: int):
# ── Zone modifiée : ligne 156 (7 ligne(s)) dans l'ancienne version → ligne 161 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -156,7 +161,10 @@ def _executer_commande_ps(base: list[str], commande: str, timeout: int):
     Utilisé pour lancer un exécutable déjà présent dans le PATH de la VM (ex.
     « nssm ») sans avoir à pousser un script .ps1 pour une commande triviale.
     Passe par powershell.exe -Command afin de bénéficier de la résolution du
-    PATH (guestcontrol run --exe exige sinon un chemin absolu vers l'exe)."""
+    PATH (guestcontrol run --exe exige sinon un chemin absolu vers l'exe).
+
+    Même remarque que _executer_ps : sortie de la console Windows en
+    CP1252, pas en UTF-8."""
     cmd = base + [
         "run",
         "--exe", POWERSHELL_INVITE,
# ── Zone modifiée : ligne 165 (7 ligne(s)) dans l'ancienne version → ligne 173 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -165,7 +173,8 @@ def _executer_commande_ps(base: list[str], commande: str, timeout: int):
         "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-Command", commande,
     ]
-    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
+    return subprocess.run(cmd, capture_output=True, encoding="cp1252",
+                           errors="replace", timeout=timeout)
 
 
 def _message_echec(action: str, res) -> str:
