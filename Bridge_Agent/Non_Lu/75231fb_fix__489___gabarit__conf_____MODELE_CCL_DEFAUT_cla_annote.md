75231fb

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 75231fb
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 22:27:59 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #489 : gabarit .conf — MODELE_CCL_DEFAUT=claude-sonnet-5, SCRIPT_BIP_DEFAUT vers bip_Cloche.py

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nouveau_projet.py b/nouveau_projet.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9282592..e3bc97e 100755
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nouveau_projet.py
# ── Version APRÈS ce commit.
+++ b/nouveau_projet.py
# ── Zone modifiée : ligne 69 (7 ligne(s)) dans l'ancienne version → ligne 69 (12 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -69,7 +69,12 @@ PALETTE_COULEURS = [
 # Topic ntfy partagé par tous les projets existants (voir configs/*.conf).
 # Proposé par défaut ; l'utilisateur peut le changer pour un topic dédié.
 TOPIC_NTFY_DEFAUT = "hippocampe-ff-galerie-xyz123"
-SCRIPT_BIP_DEFAUT = "/home/alain/NicLink/bip.py"
+SCRIPT_BIP_DEFAUT = "/home/alain/Bridge_Agent/scripts/bip_Cloche.py"
+
+# Modèle CCL forcé par défaut sur tout nouveau projet (voir configs/*.conf) :
+# évite tout repli silencieux vers Opus sur le plan Max. Reste modifiable
+# à la main dans le .conf après génération (issue #489).
+MODELE_CCL_DEFAUT = "claude-sonnet-5"
 
 # Propriétaire GitHub par défaut pour le dépôt proposé (owner/Nom).
 OWNER_DEFAUT = "AlainDelree"
# ── Zone modifiée : ligne 237 (6 ligne(s)) dans l'ancienne version → ligne 242 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -237,6 +242,7 @@ def ecrire_conf(nom: str, depot: str, rep: str, perimetre: str,
         topic_ntfy=topic,
         script_bip=script_bip,
         couleur=couleur,
+        modele_ccl=MODELE_CCL_DEFAUT,
     )
     chemin.write_text(contenu, encoding="utf-8")
     return chemin
# ── Zone modifiée : ligne 655 (6 ligne(s)) dans l'ancienne version → ligne 661 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -655,6 +661,7 @@ def etape_conf(nom: str, depot: str, rep: str, perimetre: str) -> Path:
         topic_ntfy=topic,
         script_bip=SCRIPT_BIP_DEFAUT,
         couleur=couleur,
+        modele_ccl=MODELE_CCL_DEFAUT,
     )
     chemin.write_text(contenu, encoding="utf-8")
     print(f"   ✓ {chemin.relative_to(RACINE)} créé (à partir du gabarit).")
# ── Zone modifiée : ligne 913 (7 ligne(s)) dans l'ancienne version → ligne 920 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -913,7 +920,7 @@ LOG_ARCHIVES      = 5
 DELAI_INACTIVITE_MIN = 20
 
 # ─── Modèle CCL forcé (vide = défaut) ─────────────────────────────────────────
-MODELE_CCL        =
+MODELE_CCL        = {modele_ccl}
 
 # ─── Mot de passe interface (sha256 ; vide = pas d'authentification) ──────────
 # MOT_DE_PASSE    =
