5714504

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 5714504
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Jul 29 08:24:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #318 : WM_CLASS (Linux/GTK) et AppUserModelID (Windows) pour afficher "Scrabble" dans la barre des tâches

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/main.py b/main.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 15cb776..7a58f6e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/main.py
# ── Version APRÈS ce commit.
+++ b/main.py
# ── Zone modifiée : ligne 31 (4 ligne(s)) dans l'ancienne version → ligne 31 (20 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -31,4 +31,20 @@ if not getattr(sys, "frozen", False):
 from scrabble.ui.application import main  # noqa: E402
 
 if __name__ == "__main__":
+    # Identification de l'application dans la barre des tâches (issue #318),
+    # à faire avant le premier (et unique) ``webview.start()`` (déclenché par
+    # ``main()`` ci-dessous).
+    if sys.platform == "win32":
+        import ctypes
+
+        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Scrabble")
+    elif sys.platform.startswith("linux"):
+        import gi
+
+        gi.require_version("Gtk", "3.0")
+        from gi.repository import GLib
+
+        GLib.set_prgname("Scrabble")
+        GLib.set_application_name("Scrabble")
+
     raise SystemExit(main())
