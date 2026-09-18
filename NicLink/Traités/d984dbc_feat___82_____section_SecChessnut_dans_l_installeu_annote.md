d984dbc

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit d984dbc
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Jul 28 01:27:29 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    feat: #82 — section SecChessnut dans l'installeur NSIS
    
    Ajoute la détection automatique du modèle Chessnut à l'installation
    Windows : appel de scripts/detect_chessnut.py (issue #81) avec le
    Python du venv, juste après SecVenv et avant SecStockfish. Message
    utilisateur adapté au code de sortie (0=connu/absent, 1=nouveau modèle
    enregistré, 2=erreur). makensis : 0 erreur, 0 warning.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/TACHES.md b/TACHES.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6f6ca71..a80718e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/TACHES.md
# ── Version APRÈS ce commit.
+++ b/TACHES.md
# ── Zone modifiée : ligne 47 (6 ligne(s)) dans l'ancienne version → ligne 47 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -47,6 +47,8 @@
 
 ### Session du 28 juillet
 
+Intégration de detect_chessnut.py dans l'installeur NSIS : section SecChessnut ajoutée après SecVenv, appel avec le Python du venv, message utilisateur selon le code de sortie. makensis : 0 erreur, 0 warning. (issue #82)
+
 - **Support Chessnut Go (idProduct `8501`) — non détecté par l'app** `[Linux]` (issue #78) — Alain utilise un Chessnut Go (modèle de voyage, ref CG100) : `lsusb` a révélé `2d80:8501`, même `idVendor` que tous les modèles Chessnut, `idProduct` inédit. Correctif identique à l'issue #77 (Air Plus) : `0x8501` ajouté à `PRODUCT_IDS` dans `hid_backend.py` (L.12), règle udev ajoutée dans `99-chessnutair.rules.example`, notes ajoutées dans `INSTALLATION_ALCHESS.md` aux côtés du Air (8003) et Air Plus (8202). `py_compile` OK sur `hid_backend.py`. **Test réel décisif à faire** avec l'échiquier branché. Backup pinné avant modif.
 
 Ajout de scripts/detect_chessnut.py — détection et enregistrement automatique des modèles Chessnut inconnus (idProduct), avec mise à jour de hid_backend.py et règle udev Linux. Appelé par l'installeur NSIS (Windows) et au premier démarrage. (issue #81)
# (diff du fichier suivant)
diff --git a/installer-exe/alchess_setup.nsi b/installer-exe/alchess_setup.nsi
# (index — ignorable)
index 99488ed..9606ddc 100644
# (avant — fichier suivant)
--- a/installer-exe/alchess_setup.nsi
# (après — fichier suivant)
+++ b/installer-exe/alchess_setup.nsi
# ── Zone modifiée : ligne 1349 (6 ligne(s)) dans l'ancienne version → ligne 1349 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1349,6 +1349,26 @@ SectionGroup "Configuration AlChess" SecGroupConfig
             DetailPrint "================================================"
     SectionEnd
 
+    ; -- Section 3b : Detection automatique du modele Chessnut (issue #82) ---
+    ; Suite de #81 (scripts/detect_chessnut.py). Code de sortie :
+    ;   0 = echiquier deja connu ou aucun echiquier branche
+    ;   1 = nouveau modele detecte et enregistre automatiquement
+    ;   2 = erreur (script absent, echiquier illisible, etc.)
+    Section "Detection Chessnut" SecChessnut
+        DetailPrint "Detection du modele Chessnut branche..."
+        nsExec::ExecToLog '"$EXEDIR\${VENV_SUBDIR}\Scripts\python.exe" "$EXEDIR\scripts\detect_chessnut.py"'
+        Pop $R0
+        ${If} $R0 == 0
+            DetailPrint "Echiquier detecte et deja reconnu, ou aucun echiquier branche."
+            DetailPrint "Si votre echiquier n'est pas branche, branchez-le avant de lancer AlChess."
+        ${ElseIf} $R0 == 1
+            DetailPrint "Nouveau modele Chessnut detecte et enregistre automatiquement."
+            MessageBox MB_OK "Un nouveau modele d'echiquier Chessnut a ete detecte et enregistre.$\r$\nAlChess le reconnaitra au prochain lancement."
+        ${Else}
+            DetailPrint "Avertissement : detection Chessnut non disponible (echiquier peut-etre absent)."
+        ${EndIf}
+    SectionEnd
+
     ; -- Phase 4 : portage de Install-Stockfish (cascade CPU) ----------------
     ; Equivalent de Install-Stockfish dans install_alchess.ps1 (issue #49).
     ;
