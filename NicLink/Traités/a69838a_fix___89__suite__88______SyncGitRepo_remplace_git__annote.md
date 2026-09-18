a69838a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a69838a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 02:25:19 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #89 (suite #88) — SyncGitRepo remplace git clone par init+fetch+reset
    
    git clone ne pouvait jamais aboutir dans repo_absent car $EXEDIR est
    deja rempli par le ZIP de release (git refuse un dossier non vide).
    Remplace par git init + remote add origin + fetch --depth=1 origin
    master + reset --hard origin/master, chaque etape testee (Pop $R0,
    IntCmp) avec Return non fatal en cas d'echec (pas d'Abort) : l'app
    deja presente reste utilisable meme si la conversion en depot echoue.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 4cd917f..86f20f7 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/installer-exe/alchess_setup.nsi
# ── Version APRÈS ce commit.
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1229 (12 ligne(s)) dans l'ancienne version → ligne 1229 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1229,12 +1229,15 @@ FunctionEnd
 ; ---------------------------------------------------------------------------
 ;  SyncGitRepo
 ;  Transforme $EXEDIR en depot git a jour : "git pull --ff-only" si $EXEDIR
-;  est deja un depot (dossier .git present), sinon tente un "git clone".
-;  Le clone n'aboutit que si $EXEDIR est vide (dossier "co-localise" actuel,
-;  deja rempli par le ZIP de release) : dans ce cas on logue et on continue
-;  SANS Abort (voir note d'adaptation en tete de section) — l'app deja
-;  presente reste utilisee telle quelle, seule la mise a jour auto est
-;  indisponible tant que $EXEDIR n'est pas un vrai clone git.
+;  est deja un depot (dossier .git present), sinon convertit le dossier
+;  existant en depot git via "git init" + "git remote add" + "git fetch
+;  --depth=1" + "git reset --hard" (issue #89, suite #88) — "git clone"
+;  ne peut jamais aboutir ici car $EXEDIR est deja rempli par le ZIP de
+;  release (git refuse de cloner dans un dossier non vide). Chaque etape
+;  est testee individuellement ; en cas d'echec sur l'une d'elles, on
+;  logue l'erreur et on Return SANS Abort (voir note d'adaptation en tete
+;  de section) — l'app deja presente reste utilisable, seule la mise a
+;  jour auto est indisponible tant que $EXEDIR n'est pas un vrai clone git.
 ; ---------------------------------------------------------------------------
 Function SyncGitRepo
     DetailPrint "================================================"
# ── Zone modifiée : ligne 1258 (22 ligne(s)) dans l'ancienne version → ligne 1261 (49 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1258,22 +1261,49 @@ Function SyncGitRepo
             Return
 
     repo_absent:
-        DetailPrint "  Aucun depot git dans $EXEDIR — tentative de clonage..."
-        nsExec::ExecToLog 'cmd /c git clone --branch master https://github.com/AlainDelree/AlChess.git "$EXEDIR"'
+        ; $EXEDIR est deja rempli par le ZIP de release : "git clone" ne peut
+        ; jamais y aboutir (git refuse un dossier non vide). On convertit donc
+        ; le dossier existant en depot git : init + remote add + fetch (shallow)
+        ; + reset --hard sur origin/master (issue #89, suite #88).
+        DetailPrint "  Aucun depot git dans $EXEDIR — conversion en depot (init+fetch+reset)..."
+
+        nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" init'
         Pop $R0
-        IntCmp $R0 0 clone_ok clone_fail clone_fail
-
-        clone_fail:
-            ; Cas normal actuel : $EXEDIR deja rempli par le ZIP de release
-            ; (git refuse de cloner dans un dossier non vide). Non bloquant :
-            ; l'app deja presente reste utilisee, simplement sans auto-update
-            ; tant qu'elle n'a pas ete (re)installee via un vrai clone.
-            DetailPrint "  Clonage impossible (code $R0) — dossier probablement deja rempli."
-            DetailPrint "  L'application deja presente est conservee (pas de mise a jour automatique)."
+        IntCmp $R0 0 sync_init_ok sync_init_fail sync_init_fail
+
+        sync_init_fail:
+            DetailPrint "  AVERTISSEMENT : git init a echoue (code $R0) — l'application deja presente est conservee."
+            Return
+
+        sync_init_ok:
+            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" remote add origin https://github.com/AlainDelree/AlChess.git'
+            Pop $R0
+            IntCmp $R0 0 sync_remote_ok sync_remote_fail sync_remote_fail
+
+        sync_remote_fail:
+            DetailPrint "  AVERTISSEMENT : git remote add a echoue (code $R0) — l'application deja presente est conservee."
+            Return
+
+        sync_remote_ok:
+            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" fetch --depth=1 origin master'
+            Pop $R0
+            IntCmp $R0 0 sync_fetch_ok sync_fetch_fail sync_fetch_fail
+
+        sync_fetch_fail:
+            DetailPrint "  AVERTISSEMENT : git fetch a echoue (code $R0) — l'application deja presente est conservee."
+            Return
+
+        sync_fetch_ok:
+            nsExec::ExecToLog 'cmd /c git -C "$EXEDIR" reset --hard origin/master'
+            Pop $R0
+            IntCmp $R0 0 sync_reset_ok sync_reset_fail sync_reset_fail
+
+        sync_reset_fail:
+            DetailPrint "  AVERTISSEMENT : git reset --hard a echoue (code $R0) — l'application deja presente est conservee."
             Return
 
-        clone_ok:
-            DetailPrint "  Code AlChess clone avec succes."
+        sync_reset_ok:
+            DetailPrint "  Depot git initialise avec succes : $EXEDIR est maintenant un vrai clone AlChess."
             Return
 FunctionEnd
 
