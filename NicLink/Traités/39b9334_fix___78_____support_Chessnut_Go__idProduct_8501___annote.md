39b9334

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 39b9334
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Jul 28 00:52:16 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #78 — support Chessnut Go (idProduct 8501) en détection USB

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/99-chessnutair.rules.example b/99-chessnutair.rules.example
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0bf46b1..f0dd737 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/99-chessnutair.rules.example
# ── Version APRÈS ce commit.
+++ b/99-chessnutair.rules.example
# ── Zone modifiée : ligne 7 (5 ligne(s)) dans l'ancienne version → ligne 7 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -7,5 +7,9 @@ SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8003", GROUP="whee
 # Chessnut Air Plus
 SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8202", GROUP="wheel", MODE="0660"
 
+# Chessnut Go (CG100, idProduct 8501)
+SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8501", GROUP="plugdev", TAG+="uaccess"
+KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8501", GROUP="plugdev", TAG+="uaccess"
+
 # set the permissions for device files
 KERNEL=="hidraw*", GROUP="wheel", MODE="0660"
# (diff du fichier suivant)
diff --git a/INSTALLATION_ALCHESS.md b/INSTALLATION_ALCHESS.md
# (index — ignorable)
index 4719615..1fa0074 100644
# (avant — fichier suivant)
--- a/INSTALLATION_ALCHESS.md
# (après — fichier suivant)
+++ b/INSTALLATION_ALCHESS.md
# ── Zone modifiée : ligne 72 (6 ligne(s)) dans l'ancienne version → ligne 72 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -72,6 +72,11 @@ sudo udevadm control --reload-rules
 > (`8202` au lieu de `8003`). Vérifier avec `lsusb` et adapter la valeur
 > `idProduct` dans la commande ci-dessus en conséquence.
 
+> ℹ️ **Chessnut Go** (modèle de voyage, ref CG100) : même `idVendor` (`2d80`)
+> mais `idProduct` différent (`8501` au lieu de `8003`). Vérifier avec
+> `lsusb` et adapter la valeur `idProduct` dans la commande ci-dessus en
+> conséquence.
+
 > ⚠️ **Note sur hidraw** : sur certaines machines, le device `hidraw` du Chessnut
 > peut ne pas être couvert par la règle au premier branchement. Vérifier avec :
 > ```bash
# ── Zone modifiée : ligne 112 (6 ligne(s)) dans l'ancienne version → ligne 117 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -112,6 +117,10 @@ ls -la /dev/hidraw*                    # doit montrer un hidraw avec crw-rw-rw-
 > `0x2d80:0x8202:0x40` dans la commande ci-dessus (idProduct `8202` au lieu
 > de `8003`).
 
+> ℹ️ **Chessnut Go** (CG100) : remplacer `0x2d80:0x8003:0x40` par
+> `0x2d80:0x8501:0x40` dans la commande ci-dessus (idProduct `8501` au lieu
+> de `8003`).
+
 ---
 
 ## 4c. Recompilation du driver — si `_niclink.so` ne fonctionne pas
# ── Zone modifiée : ligne 398 (14 ligne(s)) dans l'ancienne version → ligne 407 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -398,14 +407,14 @@ cp _niclink.cpython-312-x86_64-linux-gnu.so ~/NicLink/nicsoft/niclink/
 cd ~/NicLink
 
 # 5. Règle udev Chessnut Air
-# (idProduct 8003 = Chessnut Air ; 8202 = Chessnut Air Plus — adapter selon lsusb)
+# (idProduct 8003 = Chessnut Air ; 8202 = Chessnut Air Plus ; 8501 = Chessnut Go — adapter selon lsusb)
 echo 'ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="2d80", ATTR{idProduct}=="8003", MODE="0666", ATTR{power/control}="on", ATTR{power/autosuspend}="-1"
 KERNEL=="hidraw*", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8003", MODE="0666"' | sudo tee /etc/udev/rules.d/99-chessnut.rules
 sudo udevadm control --reload-rules
 # → débrancher/rebrancher le Chessnut
 
 # 6. Quirk usbhid (si Chessnut absent de /sys/bus/hid/devices/)
-# (remplacer 0x8003 par 0x8202 pour un Chessnut Air Plus)
+# (remplacer 0x8003 par 0x8202 pour un Chessnut Air Plus, ou 0x8501 pour un Chessnut Go)
 echo 'options usbhid quirks=0x2d80:0x8003:0x40' | sudo tee /etc/modprobe.d/chessnut.conf
 sudo update-initramfs -u
 # → redémarrer le PC
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index 7ad3a9e..bc008c4 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 45 (6 ligne(s)) dans l'ancienne version → ligne 45 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -45,6 +45,10 @@
 
 ## ✅ Bugs résolus récemment
 
+### Session du 28 juillet
+
+- **Support Chessnut Go (idProduct `8501`) — non détecté par l'app** `[Linux]` (issue #78) — Alain utilise un Chessnut Go (modèle de voyage, ref CG100) : `lsusb` a révélé `2d80:8501`, même `idVendor` que tous les modèles Chessnut, `idProduct` inédit. Correctif identique à l'issue #77 (Air Plus) : `0x8501` ajouté à `PRODUCT_IDS` dans `hid_backend.py` (L.12), règle udev ajoutée dans `99-chessnutair.rules.example`, notes ajoutées dans `INSTALLATION_ALCHESS.md` aux côtés du Air (8003) et Air Plus (8202). `py_compile` OK sur `hid_backend.py`. **Test réel décisif à faire** avec l'échiquier branché. Backup pinné avant modif.
+
 ### Session du 27 juillet
 
 - **Support Chessnut Air Plus (idProduct `8202`) — non détecté par l'app** `[Linux]` (issue #77) — Un utilisateur (Jess) possédant un **Chessnut Air Plus** (`lsusb` : `2d80:8202`, même `idVendor` que l'Air classique mais `idProduct` différent) ne voyait jamais son échiquier détecté — l'app ne connaissait que `8003` (Air classique). **Grep exhaustif** `8003`/`2d80` dans tout `nicsoft/` : une seule occurrence de code, `nicsoft/niclink/hid_backend.py` (backend hidapi Python, **chemin réellement utilisé** — `_niclink.so` C++ n'est qu'un fallback si `hid_backend` échoue à s'importer). Bonne nouvelle : `PRODUCT_IDS` était **déjà une liste** (`[0x8001, 0x8002, 0x8003]`), pas une valeur unique — correctif minimal : ajout de `0x8202` à la liste (`hid_backend.py` L.12), avec commentaire indiquant quel idProduct correspond à quel modèle. **Aucune trace** dans le code d'une anticipation de différence de protocole entre Air et Air Plus (pas de gestion de version firmware) → hypothèse retenue (même famille de produit, même vendor) : protocole HID identique, seul l'idProduct change. À confirmer par le test réel de Jess. Fichiers annexes également mis à jour par cohérence : `99-chessnutair.rules.example` (règle udev supplémentaire pour `8003` et `8202`, sans supprimer l'ancienne règle `8002`) et `INSTALLATION_ALCHESS.md` (notes ajoutées aux sections 4/4b + au script récapitulatif, rappelant d'adapter `idProduct` `8003`→`8202` pour un Air Plus). `py_compile` OK sur `hid_backend.py`. **Test réel décisif à faire par Jess** : relancer l'app avec l'Air Plus branché et confirmer la détection (plus de « Board not detected »). Backup pinné avant modif.
# (diff du fichier suivant)
diff --git a/nicsoft/niclink/hid_backend.py b/nicsoft/niclink/hid_backend.py
# (index — ignorable)
index ede78c0..d1c51fe 100644
# (avant — fichier suivant)
--- a/nicsoft/niclink/hid_backend.py
# (après — fichier suivant)
+++ b/nicsoft/niclink/hid_backend.py
# ── Zone modifiée : ligne 9 (7 ligne(s)) dans l'ancienne version → ligne 9 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,7 +9,7 @@ import threading
 import time
 
 VENDOR_ID   = 0x2d80
-PRODUCT_IDS = [0x8001, 0x8002, 0x8003, 0x8202]  # 8003=Chessnut Air, 8202=Chessnut Air Plus
+PRODUCT_IDS = [0x8001, 0x8002, 0x8003, 0x8202, 0x8501]  # 8003=Air, 8202=Air Plus, 8501=Chessnut Go
 USAGE_PAGE  = 0xFF00
 WRITE_INTERVAL = 0.2  # secondes — identique au C++ (200ms)
 
