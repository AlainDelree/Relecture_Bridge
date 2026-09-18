095f2d9

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 095f2d9
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Jul 28 01:13:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    docs: #79 — section 4bis « échiquier non détecté » (Linux + Windows) dans INSTALLATION_ALCHESS.md

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/INSTALLATION_ALCHESS.md b/INSTALLATION_ALCHESS.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 1fa0074..2a2ce16 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/INSTALLATION_ALCHESS.md
# ── Version APRÈS ce commit.
+++ b/INSTALLATION_ALCHESS.md
# ── Zone modifiée : ligne 123 (6 ligne(s)) dans l'ancienne version → ligne 123 (86 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -123,6 +123,86 @@ ls -la /dev/hidraw*                    # doit montrer un hidraw avec crw-rw-rw-
 
 ---
 
+## 4bis. Mon échiquier Chessnut n'est pas détecté
+
+### Principe
+
+Si AlChess affiche « Board not detected » au démarrage, l'idProduct USB de
+votre modèle n'est peut-être pas encore connu. Tous les modèles Chessnut
+partagent `idVendor=2d80` et le même protocole HID — seul l'idProduct
+change. Le correctif est une ligne dans `nicsoft/niclink/hid_backend.py`.
+
+### Étape 1 — Identifier l'idProduct
+
+**Linux :**
+
+```bash
+lsusb | grep 2d80
+# Exemple : Bus 001 Device 008: ID 2d80:8501 Chessnut Chessnut Go
+#                                       ^^^^ = idProduct
+```
+
+**Windows :**
+
+Ouvrir PowerShell et lancer :
+
+```powershell
+Get-PnpDevice -Class HIDClass | Where-Object { $_.InstanceId -like "*2D80*" } | Select-Object FriendlyName, InstanceId
+```
+
+L'InstanceId contient `VID_2D80&PID_XXXX` — les 4 chiffres après `PID_`
+sont l'idProduct.
+
+Alternative : Gestionnaire de périphériques → clic droit sur le Chessnut →
+Propriétés → Détails → ID matériel.
+
+### Étape 2 — Ajouter l'idProduct dans le code
+
+Ouvrir `nicsoft/niclink/hid_backend.py` (ligne ~12) :
+
+- Linux : `~/NicLink/nicsoft/niclink/hid_backend.py`
+- Windows : `<dossier AlChess>\nicsoft\niclink\hid_backend.py` (avec
+  Notepad ou VS Code)
+
+Ligne à modifier :
+
+```python
+PRODUCT_IDS = [0x8001, 0x8002, 0x8003, 0x8202, 0x8501]  # 8003=Air, 8202=Air Plus, 8501=Chessnut Go
+```
+
+Ajouter votre idProduct (en hexadécimal, préfixe `0x`) à la liste. Exemple
+pour un idProduct `85AB` :
+
+```python
+PRODUCT_IDS = [0x8001, 0x8002, 0x8003, 0x8202, 0x8501, 0x85AB]
+```
+
+### Étape 3 (Linux uniquement) — Règle udev
+
+```bash
+sudo tee -a /etc/udev/rules.d/99-chessnutair.rules <<EOF
+SUBSYSTEM=="usb", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="XXXX", GROUP="plugdev", TAG+="uaccess"
+KERNEL=="hidraw*", SUBSYSTEM=="hidraw", ATTRS{idVendor}=="2d80", ATTRS{idProduct}=="XXXX", GROUP="plugdev", TAG+="uaccess"
+EOF
+sudo udevadm control --reload-rules && sudo udevadm trigger
+```
+
+(Remplacer `XXXX` par votre idProduct en minuscules, ex. `85ab`)
+
+### Étape 4 — Relancer AlChess
+
+- Linux : `python3 -m nicsoft.web`
+- Windows : double-cliquer `2-Lancer_AlChess.bat`
+
+### Signaler votre modèle
+
+Si ça fonctionne, ouvrir une issue sur
+https://github.com/AlainDelree/AlChess en indiquant le nom exact du modèle
+et l'idProduct — il sera ajouté à la liste officielle pour les prochaines
+versions.
+
+---
+
 ## 4c. Recompilation du driver — si `_niclink.so` ne fonctionne pas
 
 Le fichier `nicsoft/niclink/_niclink.cpython-312-x86_64-linux-gnu.so` est un
