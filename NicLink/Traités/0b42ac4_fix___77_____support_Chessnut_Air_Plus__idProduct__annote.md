0b42ac4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 0b42ac4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 16:35:43 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: #77 — support Chessnut Air Plus (idProduct 8202) en détection USB
    
    Ajoute 0x8202 à la liste PRODUCT_IDS de hid_backend.py (déjà une liste,
    pas de valeur unique en dur) pour reconnaître le Chessnut Air Plus en
    plus de l'Air classique (8003). Met à jour les fichiers de setup USB
    (99-chessnutair.rules.example, INSTALLATION_ALCHESS.md) pour documenter
    l'idProduct alternatif. Aucune anticipation de différence de protocole
    trouvée dans le code — hypothèse retenue : protocole HID identique
    (même vendor, même famille de produit), à confirmer par test réel.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/99-chessnutair.rules.example b/99-chessnutair.rules.example
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ab330fd..0bf46b1 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/99-chessnutair.rules.example
# ── Version APRÈS ce commit.
+++ b/99-chessnutair.rules.example
# ── Zone modifiée : ligne 1 (5 ligne(s)) dans l'ancienne version → ligne 1 (11 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,5 +1,11 @@
 SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", /
 ATTRS{idProduct}=="8002", GROUP="wheel", MODE="0660"
 
+# Chessnut Air
+SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8003", GROUP="wheel", MODE="0660"
+
+# Chessnut Air Plus
+SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8202", GROUP="wheel", MODE="0660"
+
 # set the permissions for device files
 KERNEL=="hidraw*", GROUP="wheel", MODE="0660"
# (diff du fichier suivant)
diff --git a/INSTALLATION_ALCHESS.md b/INSTALLATION_ALCHESS.md
# (index — ignorable)
index cfc2c42..4719615 100644
# (avant — fichier suivant)
--- a/INSTALLATION_ALCHESS.md
# (après — fichier suivant)
+++ b/INSTALLATION_ALCHESS.md
# ── Zone modifiée : ligne 68 (6 ligne(s)) dans l'ancienne version → ligne 68 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -68,6 +68,10 @@ sudo udevadm control --reload-rules
 > ⚠️ **Important** : débrancher et rebrancher le Chessnut **après** avoir appliqué
 > les règles pour qu'elles prennent effet.
 
+> ℹ️ **Chessnut Air Plus** : même `idVendor` (`2d80`) mais `idProduct` différent
+> (`8202` au lieu de `8003`). Vérifier avec `lsusb` et adapter la valeur
+> `idProduct` dans la commande ci-dessus en conséquence.
+
 > ⚠️ **Note sur hidraw** : sur certaines machines, le device `hidraw` du Chessnut
 > peut ne pas être couvert par la règle au premier branchement. Vérifier avec :
 > ```bash
# ── Zone modifiée : ligne 104 (6 ligne(s)) dans l'ancienne version → ligne 108 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -104,6 +108,10 @@ ls -la /dev/hidraw*                    # doit montrer un hidraw avec crw-rw-rw-
 > ℹ️ Le quirk `0x40` force le kernel à traiter le Chessnut comme un device HID
 > complet, contournant le problème de binding automatique.
 
+> ℹ️ **Chessnut Air Plus** : remplacer `0x2d80:0x8003:0x40` par
+> `0x2d80:0x8202:0x40` dans la commande ci-dessus (idProduct `8202` au lieu
+> de `8003`).
+
 ---
 
 ## 4c. Recompilation du driver — si `_niclink.so` ne fonctionne pas
# ── Zone modifiée : ligne 390 (12 ligne(s)) dans l'ancienne version → ligne 398 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -390,12 +398,14 @@ cp _niclink.cpython-312-x86_64-linux-gnu.so ~/NicLink/nicsoft/niclink/
 cd ~/NicLink
 
 # 5. Règle udev Chessnut Air
+# (idProduct 8003 = Chessnut Air ; 8202 = Chessnut Air Plus — adapter selon lsusb)
 echo 'ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="2d80", ATTR{idProduct}=="8003", MODE="0666", ATTR{power/control}="on", ATTR{power/autosuspend}="-1"
 KERNEL=="hidraw*", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="8003", MODE="0666"' | sudo tee /etc/udev/rules.d/99-chessnut.rules
 sudo udevadm control --reload-rules
 # → débrancher/rebrancher le Chessnut
 
 # 6. Quirk usbhid (si Chessnut absent de /sys/bus/hid/devices/)
+# (remplacer 0x8003 par 0x8202 pour un Chessnut Air Plus)
 echo 'options usbhid quirks=0x2d80:0x8003:0x40' | sudo tee /etc/modprobe.d/chessnut.conf
 sudo update-initramfs -u
 # → redémarrer le PC
# (diff du fichier suivant)
diff --git a/TACHES.md b/TACHES.md
# (index — ignorable)
index aa08816..7ad3a9e 100644
# (avant — fichier suivant)
--- a/TACHES.md
# (après — fichier suivant)
+++ b/TACHES.md
# ── Zone modifiée : ligne 45 (6 ligne(s)) dans l'ancienne version → ligne 45 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -45,6 +45,10 @@
 
 ## ✅ Bugs résolus récemment
 
+### Session du 27 juillet
+
+- **Support Chessnut Air Plus (idProduct `8202`) — non détecté par l'app** `[Linux]` (issue #77) — Un utilisateur (Jess) possédant un **Chessnut Air Plus** (`lsusb` : `2d80:8202`, même `idVendor` que l'Air classique mais `idProduct` différent) ne voyait jamais son échiquier détecté — l'app ne connaissait que `8003` (Air classique). **Grep exhaustif** `8003`/`2d80` dans tout `nicsoft/` : une seule occurrence de code, `nicsoft/niclink/hid_backend.py` (backend hidapi Python, **chemin réellement utilisé** — `_niclink.so` C++ n'est qu'un fallback si `hid_backend` échoue à s'importer). Bonne nouvelle : `PRODUCT_IDS` était **déjà une liste** (`[0x8001, 0x8002, 0x8003]`), pas une valeur unique — correctif minimal : ajout de `0x8202` à la liste (`hid_backend.py` L.12), avec commentaire indiquant quel idProduct correspond à quel modèle. **Aucune trace** dans le code d'une anticipation de différence de protocole entre Air et Air Plus (pas de gestion de version firmware) → hypothèse retenue (même famille de produit, même vendor) : protocole HID identique, seul l'idProduct change. À confirmer par le test réel de Jess. Fichiers annexes également mis à jour par cohérence : `99-chessnutair.rules.example` (règle udev supplémentaire pour `8003` et `8202`, sans supprimer l'ancienne règle `8002`) et `INSTALLATION_ALCHESS.md` (notes ajoutées aux sections 4/4b + au script récapitulatif, rappelant d'adapter `idProduct` `8003`→`8202` pour un Air Plus). `py_compile` OK sur `hid_backend.py`. **Test réel décisif à faire par Jess** : relancer l'app avec l'Air Plus branché et confirmer la détection (plus de « Board not detected »). Backup pinné avant modif.
+
 ### Session du 26 juillet
 
 - **📄 `make_release.sh` — texte `--notes` par défaut corrigé (bilingue FR/EN, plus jamais figé sur "Première version")** `[Linux/Windows]` (issue #76) — La commande `gh release create` suggérée en fin de script contenait un texte `--notes` fixe : « Première version téléchargeable. Voir le README pour l'installation. » Vrai seulement pour v1.0.0, ce texte avait été copié-collé tel quel sur v1.1.0 et v1.2.0, rendant leur description trompeuse (une 3e release affichant encore « Première version téléchargeable »). Le texte n'était de plus pas bilingue, contrairement au README (FR/EN). **Correctif** : texte `--notes` remplacé par un défaut générique toujours vrai quelle que soit la version, bilingue FR/EN, renvoyant vers le README (`Voir le README pour les instructions d'installation (FR/EN). / See the README for installation instructions (FR/EN). / https://github.com/AlainDelree/AlChess#readme`). **Commentaire ajouté juste avant la commande suggérée**, rappelant explicitement à Alain de personnaliser ce texte avec les changements notables de la version avant de publier, plutôt que de le copier-coller tel quel — pour éviter que l'erreur ne se reproduise. Vérifié : `bash -n make_release.sh` (syntaxe OK) + rendu de la commande testé isolément (guillemets bien équilibrés, texte multi-lignes s'affiche correctement). Backup pinné + commit checkpoint avant modif.
# (diff du fichier suivant)
diff --git a/nicsoft/niclink/hid_backend.py b/nicsoft/niclink/hid_backend.py
# (index — ignorable)
index 0b5b6b3..ede78c0 100644
# (avant — fichier suivant)
--- a/nicsoft/niclink/hid_backend.py
# (après — fichier suivant)
+++ b/nicsoft/niclink/hid_backend.py
# ── Zone modifiée : ligne 9 (7 ligne(s)) dans l'ancienne version → ligne 9 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -9,7 +9,7 @@ import threading
 import time
 
 VENDOR_ID   = 0x2d80
-PRODUCT_IDS = [0x8001, 0x8002, 0x8003]
+PRODUCT_IDS = [0x8001, 0x8002, 0x8003, 0x8202]  # 8003=Chessnut Air, 8202=Chessnut Air Plus
 USAGE_PAGE  = 0xFF00
 WRITE_INTERVAL = 0.2  # secondes — identique au C++ (200ms)
 
