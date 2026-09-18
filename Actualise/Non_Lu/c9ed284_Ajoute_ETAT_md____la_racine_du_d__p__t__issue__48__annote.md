c9ed284

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit c9ed284
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 22:34:22 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute ETAT.md à la racine du dépôt (issue #48)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/ETAT.md b/ETAT.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..163e2b6
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/ETAT.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (29 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,29 @@
+# État du système — Actualise et ses clients
+
+## Versions publiées
+- Actualise v9 — publié sur GitHub, installé et fonctionnel
+- Scrabble v12 — publié sur GitHub (Release v12), build officiel avec commits leave_value (moteur IA amélioré) et nouveau setup sans Actualise
+- Rummikub v12 — publié sur GitHub (Release v12), nouveau setup sans Actualise
+- Actualise-Setup-v9.exe — nouvel installeur indépendant créé et buildé
+
+## Architecture en place (refonte complète effectuée)
+- Raccourcis → exe direct (Scrabble.exe / Rummikub.exe), plus via Actualise
+- Les jeux lancent Actualise au démarrage si présent (C:\Actualise\Actualise.exe), tournent sans lui si absent
+- Les setups jeux n'embarquent plus Actualise — ils déposent uniquement leur config_<jeu>.json dans C:\Actualise\
+- Actualise ne lance plus aucun jeu
+- Actualise-Setup.exe installe Actualise indépendamment
+
+## Procédure de déploiement sur les anciens PC (validée)
+1. Désinstaller Actualise (Paramètres Windows)
+2. Supprimer C:\Actualise\ manuellement
+3. Installer Actualise-Setup-v9.exe
+4. Installer Scrabble-Setup-v12.exe
+5. Installer Rummikub-Setup-v12.exe
+6. Lancer verifier_installation.py pour confirmer
+7. Lancer Scrabble
+
+## Points en suspens
+- Builds CCW pas encore testés sur le nouveau PC fixe Windows (Samba,
+  remplace la VM VirtualBox). Chemins VirtualBox (\\VBOXSVR\CCW_Share\,
+  Z:\CCW\) dans les scripts de build à adapter au nouveau partage Samba.
+- verifier_installation.py existe comme script standalone (pas dans un dépôt)
