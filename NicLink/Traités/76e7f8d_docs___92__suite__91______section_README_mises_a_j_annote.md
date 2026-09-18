76e7f8d

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 76e7f8d
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 30 03:15:00 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    docs: #92 (suite #91) — section README mises a jour automatiques
    
    Documente le mecanisme de mise a jour auto (git fetch + dernier tag
    de release), son caractere transparent, la desactivation via la
    checkbox du menu principal et le fichier no-update.txt genere.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/README.md b/README.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 45c58fb..51464f5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/README.md
# ── Version APRÈS ce commit.
+++ b/README.md
# ── Zone modifiée : ligne 113 (6 ligne(s)) dans l'ancienne version → ligne 113 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -113,6 +113,14 @@ python -m nicsoft.web
 
 Guide complet : [`INSTALLATION/`](INSTALLATION/).
 
+### Mises à jour automatiques
+
+Au démarrage, AlChess vérifie s'il existe une version plus récente sur GitHub (dernier tag de release publié) et se met à jour tout seul si c'est le cas. Ce mécanisme est **transparent** : il ne demande aucune action de votre part, mais nécessite une **connexion internet** au lancement.
+
+Vous pouvez désactiver cette vérification via la case à cocher prévue à cet effet dans le menu principal. Un avertissement s'affiche alors pour rappeler que vous ne recevrez plus les mises à jour automatiquement.
+
+Pour les utilisateurs avancés qui préfèrent gérer les mises à jour eux-mêmes (par exemple en environnement contrôlé), la désactivation crée simplement un fichier `no-update.txt` à la racine de l'installation. Sa présence suffit à couper la vérification automatique ; il peut aussi être créé ou supprimé manuellement.
+
 ### Contribuer
 
 Les contributions sont les bienvenues ! Ouvrez une **Issue** pour signaler un bug ou proposer une fonctionnalité, ou une **Pull Request** pour soumettre du code.
