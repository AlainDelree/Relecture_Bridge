9fa5b91

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 9fa5b91
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Thu Sep 17 18:16:48 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Ajoute un encart Démarrage rapide en tête du §16 (ajouter CCW à un projet)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b3f6fca..38f931d 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1693 (6 ligne(s)) dans l'ancienne version → ligne 1693 (21 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1693,6 +1693,21 @@ Windows natif.
 `configurer_ssh_ccw.ps1` → `provisionner.ps1` → tokens → vérification) dans
 `provisioning/windows/REINSTALLATION_CCW.md` (issue #451).
 
+> **🚀 Démarrage rapide — ajouter CCW à un projet (issue #559/#560).**
+> Dans le modal « + Nouveau projet », coche la case **« Projet CCW »**,
+> remplis le topic ntfy, puis clique **« Créer le projet »**. Une fois le
+> projet créé, un bloc **« Finaliser le bootstrap CCW »** apparaît avec le
+> nom du dépôt réel : crée à ce moment-là un token GitHub fine-grained
+> dédié (accès **uniquement** au nouveau dépôt, `Issues: Read and write` /
+> `Metadata: Read-only`) et un `CLAUDE_CODE_OAUTH_TOKEN` (`claude
+> setup-token`), colle les deux, clique **« Finaliser le bootstrap CCW »**.
+> C'est tout — un service Windows dédié se crée automatiquement, même si
+> CCW est éteint au moment du clic (l'issue attend simplement en file).
+> Si le bouton « Rafraîchir la clé publique » indique une clé absente ou
+> périmée, CCW doit être allumé le temps de cliquer dessus une fois — voir
+> §16.7 pour le détail. Le reste de ce §16 documente le fonctionnement
+> interne, pas la marche à suivre au quotidien.
+
 > **⚠️ Changement de plateforme (depuis août 2026, issue #446).** CCW ne
 > tourne plus dans une VM VirtualBox mais **sur un PC fixe physique**
 > (Pentium G2020). De nombreux paragraphes ci-dessous décrivent encore
