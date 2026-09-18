eaf9204

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit eaf9204
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 24 20:45:57 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Nettoie .gitignore : ligne malformée (\n littéral), doublon games/, logs/*.log redondant, règles debug obsolètes (issue #250)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b47a4fd..bb7eef4 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 8 (18 ligne(s)) dans l'ancienne version → ligne 8 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -8,18 +8,11 @@ data/
 dist/
 build/
 
-# Logs
-logs/*.log
-
 # Parties temporaires
 games/tmp/*.pgn
 
-# Fichiers de test lenteur
-Lenteur*
-
 TRAVAIL_EN_COURS/
 TACHES.md
-\n# Fichiers de travail temporaires\nmockup_menu.html
 
 #Fichiers rearchitecture Linux Windows Android
 REARCHITECTURE_ALAIN.md
# ── Zone modifiée : ligne 33 (10 ligne(s)) dans l'ancienne version → ligne 26 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -33,10 +26,7 @@ engines/lc0*.exe
 # Installeur NSIS compilé (binaire Windows généré par makensis — voir issue #50)
 installer-exe/*.exe
 
-# Fichiers de debug et test
-debug_*.txt
-test_windows_result.txt
-alchess_err.txt
+# Log applicatif généré par les scripts de lancement Windows (2-Lancer_AlChess.bat, start_alchess.ps1, install_alchess.ps1)
 alchess_log.txt
 
 # --- Données personnelles (ne jamais publier) ---
# ── Zone modifiée : ligne 50 (7 ligne(s)) dans l'ancienne version → ligne 40 (5 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -50,7 +40,5 @@ mockup_menu.html
 test_perm.txt
 logs/
 
-# Parties (données perso / noms de tiers)
-games/
 .assetsignore
 .wrangler/
