75fd406

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 75fd406
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 05:51:51 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #405 : lancement d'Actualise en arrière-plan au démarrage de Scrabble

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/main.py b/main.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 09f8b0d..d5467f4 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/main.py
# ── Version APRÈS ce commit.
+++ b/main.py
# ── Zone modifiée : ligne 66 (4 ligne(s)) dans l'ancienne version → ligne 66 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -66,4 +66,16 @@ if __name__ == "__main__":
         except Exception:
             pass  # ne jamais bloquer le démarrage de Scrabble
 
+    # Lancement d'Actualise au démarrage (issue #405) : si l'application est
+    # installée, on la démarre en arrière-plan (subprocess non-bloquant) pour
+    # qu'elle puisse gérer les mises à jour de Scrabble. Absente ou en échec
+    # de lancement : on continue normalement, sans jamais bloquer ni faire
+    # planter le démarrage de Scrabble.
+    _actualise_exe = Path(r"C:\Actualise\Actualise.exe")
+    if _actualise_exe.exists():
+        try:
+            subprocess.Popen([str(_actualise_exe), "--config", "scrabble"])
+        except Exception:
+            pass  # ne jamais bloquer le démarrage de Scrabble
+
     raise SystemExit(main())
