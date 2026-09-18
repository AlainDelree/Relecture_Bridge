6c93631

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 6c93631
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Wed Aug 12 20:28:12 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Icône AlChess : roi noir (alchess.ico), correction raccourci NSIS

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5ff4cf6..7c9bd95 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 5 (7 ligne(s)) dans l'ancienne version → ligne 5 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -5,7 +5,7 @@
 ## ⚡ Prioritaire
 
 - **Release v1.3.1 à packager** `[Linux/Windows]` — regrouper les correctifs depuis v1.3.0 (dont issue #96) : `./make_release.sh 1.3.1` + tag + `gh release create`.
-- **ACTION ALAIN — Validation VM NSIS** `[Windows]` — relancer `AlChess_Setup.exe` sur VM Windows et confirmer l'installation/lancement de bout en bout (issues #64–#67, #58).
+- **ACTION ALAIN — Valider nouveau raccourci Windows** `[Windows]` — relancer `AlChess_Setup.exe` sur VM Windows et vérifier que le raccourci bureau affiche bien l'icône roi noir.
 - **Tester une partie réelle Rodent sur Windows** `[Windows]` — sur portable physique (jeu + changement d'Elo + redémarrage).
 - **Tester vc_redist sur un Windows sans le runtime VC++** `[Windows]` — la VM actuelle a déjà le runtime, il faut un Windows propre.
 
# (diff du fichier suivant)
diff --git a/alchess.ico b/alchess.ico
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..de934b8
Binary files /dev/null and b/alchess.ico differ
# (diff du fichier suivant)
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# (index — ignorable)
index a20a1aa..9fe0c3a 100644
# (avant — fichier suivant)
--- a/installer-exe/alchess_setup.nsi
# (après — fichier suivant)
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1914 (7 ligne(s)) dans l'ancienne version → ligne 1914 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1914,7 +1914,7 @@ Section "Raccourci bureau" SecShortcut
     ; ne remonte pas une erreur laissee par une instruction anterieure.
     ClearErrors
     CreateShortcut "$DESKTOP\AlChess.lnk" "$EXEDIR\2-Lancer_AlChess.bat" \
-        "" "$EXEDIR\niclink_icon.ico" 0 SW_SHOWNORMAL "" "Launch AlChess"
+        "" "$EXEDIR\alchess.ico" 0 SW_SHOWNORMAL "" "Launch AlChess"
     IfErrors shortcut_failed shortcut_ok
 
     shortcut_failed:
# (diff du fichier suivant)
diff --git a/make_release.sh b/make_release.sh
# (index — ignorable)
index 4bdd074..262dd30 100755
# (avant — fichier suivant)
--- a/make_release.sh
# (après — fichier suivant)
+++ b/make_release.sh
# ── Zone modifiée : ligne 60 (6 ligne(s)) dans l'ancienne version → ligne 60 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -60,6 +60,7 @@ INCLUDE=(
   start_alchess.ps1
   99-chessnutair.rules.example
   niclink_icon.ico
+  alchess.ico
 )
 
 for item in "${INCLUDE[@]}"; do
