e11a05e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e11a05e
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 18 18:15:38 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    docs: entrée CHANGELOG-181 pour issue #181 (verif version Python NSIS)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-181.md b/CHANGELOG-181.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..71054a3
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-181.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,8 @@
+## Issue #181 — Vérification version Python dans l'installeur NSIS (essai2)
+
+- `installer-exe/alchess_setup.nsi` : nouvelle fonction `CheckPythonVersionWarning`, appelée juste après détection réussie de Python (SecPython, toutes stratégies : `py -0p`, PATH, scan des dossiers standards) et avant la création du venv. Avertit — sans bloquer — si le Python détecté est une pré-publication (suffixe `rc`/`a`/`b` dans la version complète, ex. `3.15.0rc1`) ou une version ancienne (< 3.10).
+- Cas non couvert par la comparaison existante (`CompareVersionToMinimum`) : elle ne compare que "X.Y" (ex. "3.15") au minimum requis (3.12), donc une RC comme `3.15.0rc1` passait la vérification sans que son suffixe soit examiné — cause du bug constaté (Python 3.15rc1 : `hidapi` ne compile pas faute de MSVC, aucun wheel précompilé n'existant pour une RC).
+- Ajout de `ExtractFullVersionFromPythonOutput` (garde le suffixe complet de la version, contrairement à `ExtractVersionFromPythonOutput` qui tronque à "X.Y") et de la macro `StrFunc` `StrStr` (recherche de sous-chaîne).
+- `MessageBox MB_OKCANCEL` non bloquante : affiche la version détectée, recommande Python 3.12/3.13 stable avec lien vers python.org, l'utilisateur peut continuer quand même (IDCANCEL → Abort propre).
+- Non appelée après `InstallPython312NSIS` (installation via winget) : cette voie installe toujours une 3.12 stable, jamais concernée.
+- Vérifié : `makensis -V4 alchess_setup.nsi` compile sans erreur (exit 0).
