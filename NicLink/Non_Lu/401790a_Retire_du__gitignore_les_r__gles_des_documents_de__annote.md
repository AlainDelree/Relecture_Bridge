401790a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 401790a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 09:09:57 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Retire du .gitignore les règles des documents de travail déménagés hors dépôt (issue #251)
    
    TRAVAIL_EN_COURS/, TACHES.md, REARCHITECTURE_ALAIN.md, REARCHITECTURE_CLAUDE_CODE.md,
    HANDOFF_*.md, AUDIT_ALCHESS.md, Copier-coller, mockup_menu.html, test_perm.txt +
    commentaires devenus orphelins. logs/ conservé inchangé.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index bb7eef4..7f575cd 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 11 (13 ligne(s)) dans l'ancienne version → ligne 11 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -11,13 +11,6 @@ build/
 # Parties temporaires
 games/tmp/*.pgn
 
-TRAVAIL_EN_COURS/
-TACHES.md
-
-#Fichiers rearchitecture Linux Windows Android
-REARCHITECTURE_ALAIN.md
-REARCHITECTURE_CLAUDE_CODE.md
-
 # Exécutables moteurs Windows (trop lourds, téléchargés par install_alchess.ps1)
 engines/stockfish*.exe
 engines/stockfish-windows*/
# ── Zone modifiée : ligne 32 (12 ligne(s)) dans l'ancienne version → ligne 25 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -32,12 +25,6 @@ alchess_log.txt
 # --- Données personnelles (ne jamais publier) ---
 games/
 
-# --- Fichiers de travail / documents de handoff ---
-HANDOFF_*.md
-AUDIT_ALCHESS.md
-Copier-coller
-mockup_menu.html
-test_perm.txt
 logs/
 
 .assetsignore
