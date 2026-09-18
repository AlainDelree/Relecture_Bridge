2417780

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 2417780
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 19:13:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: retire détection USB redondante is_board_connected() dans explorer_load (issue #160, suite #159)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6e352d5..3542629 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 1117 (16 ligne(s)) dans l'ancienne version → ligne 1117 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1117,16 +1117,6 @@ def explorer_load(source_type: str, opening_id: str, variant_index=None) -> dict
         source = PolyglotSource(ouverture, book_path)
 
     used_virtual = _virtual_mode
-    if not used_virtual:
-        try:
-            from nicsoft.niclink import hid_backend
-            board_present = hid_backend.is_board_connected()
-        except Exception:
-            board_present = True  # détection indisponible : on tente la connexion normale
-        if not board_present:
-            logger.info("[EXPLORER] Aucun échiquier USB détecté, accès direct en mode virtuel.")
-            used_virtual = True
-
     try:
         nl_inst = create_board(virtual=used_virtual, logger_name="NicLink_explorer")
     except (Exception, SystemExit) as e:
# (diff du fichier suivant)
diff --git a/nicsoft/niclink/hid_backend.py b/nicsoft/niclink/hid_backend.py
# (index — ignorable)
index 8f5bd67..7efcd82 100644
# (avant — fichier suivant)
--- a/nicsoft/niclink/hid_backend.py
# (après — fichier suivant)
+++ b/nicsoft/niclink/hid_backend.py
# ── Zone modifiée : ligne 51 (18 ligne(s)) dans l'ancienne version → ligne 51 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -51,18 +51,6 @@ def _list_paths() -> list[tuple[bytes, int]]:
     return paths
 
 
-def is_board_connected() -> bool:
-    """Détection rapide (sans ouvrir le périphérique) d'un Chessnut Air branché en USB.
-
-    S'appuie sur hid.enumerate(), qui répond quasi instantanément — contrairement
-    à connect() qui ouvre le device et attend 2s d'initialisation hardware.
-    """
-    try:
-        return bool(_list_paths())
-    except Exception:
-        return False
-
-
 def _write(data: bytes) -> None:
     """Écriture HID avec délai minimum entre deux écritures (idem C++ WRITE_INTERVAL)."""
     global _last_write
