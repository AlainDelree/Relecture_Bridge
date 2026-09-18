fe46486

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit fe46486
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 03:18:00 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    docs: #93 (suite #92) — section README Automatic updates cote anglais

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/README.md b/README.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 51464f5..4535529 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/README.md
# ── Version APRÈS ce commit.
+++ b/README.md
# ── Zone modifiée : ligne 233 (6 ligne(s)) dans l'ancienne version → ligne 233 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -233,6 +233,14 @@ python -m nicsoft.web
 
 Full guide: [`INSTALLATION/`](INSTALLATION/).
 
+### Automatic updates
+
+On startup, AlChess checks whether a newer version is available on GitHub (latest published release tag) and updates itself automatically if so. This mechanism is **transparent**: it requires no action on your part, but does need an **internet connection** at launch.
+
+You can disable this check via the dedicated checkbox in the main menu. A warning is then displayed to remind you that you will no longer receive automatic updates.
+
+For advanced users who prefer to manage updates themselves (for example in a controlled environment), disabling the check simply creates a `no-update.txt` file at the root of the installation. Its presence is enough to turn off the automatic check; it can also be created or deleted manually.
+
 ### Contributing
 
 Contributions are welcome! Open an **Issue** to report a bug or suggest a feature, or a **Pull Request** to submit code.
