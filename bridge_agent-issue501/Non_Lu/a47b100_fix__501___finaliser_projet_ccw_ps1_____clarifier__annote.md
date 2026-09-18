a47b100

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a47b100
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 30 16:15:03 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #501 : finaliser_projet_ccw.ps1 — clarifier le prompt de confirmation du token

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/CHANGELOG-501.md b/CHANGELOG-501.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..ef92ba2
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/CHANGELOG-501.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (14 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,14 @@
+## #501 — finaliser_projet_ccw.ps1 : clarification du prompt de confirmation du token
+
+Le message `Read-Host 'Appuie sur Entrée une fois le token créé et copié'` prêtait à
+confusion : il pouvait être lu comme une demande de coller le token à cet endroit,
+alors qu'il ne fait qu'attendre une touche Entrée pour continuer — le vrai collage
+du token a lieu juste après, dans `mettre_a_jour_tokens_ccw.ps1` (« Collez la valeur
+de GH_TOKEN »). Un utilisateur a déjà collé son token par erreur à cette invite.
+
+Reformulé en : `'Ne colle RIEN ici : une fois le token créé et copié, appuie juste
+sur Entrée pour continuer (le collage se fera à l'étape suivante)'`.
+
+Le script personnel `creer_projet_ccw_complet.ps1` (hors dépôt officiel) n'est pas
+accessible depuis ce worktree — la même formulation cohérente y est recommandée
+manuellement si un message similaire y existe.
# (diff du fichier suivant)
diff --git a/provisioning/windows/finaliser_projet_ccw.ps1 b/provisioning/windows/finaliser_projet_ccw.ps1
# (index — ignorable)
index 3f93fdb..78c6c0a 100644
# (avant — fichier suivant)
--- a/provisioning/windows/finaliser_projet_ccw.ps1
# (après — fichier suivant)
+++ b/provisioning/windows/finaliser_projet_ccw.ps1
# ── Zone modifiée : ligne 151 (7 ligne(s)) dans l'ancienne version → ligne 151 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -151,7 +151,7 @@ Info '  • Permissions : Issues = Read and write, Metadata = Read-only'
 Info '  • Expiration : LA MÊME DATE que le token Bridge_Agent (≈ 2026-10-17,'
 Info "    aligné sur l'éval Windows) — ne pas laisser dériver (cf. §16)."
 Write-Host ''
-Read-Host 'Appuie sur Entrée une fois le token créé et copié' | Out-Null
+Read-Host 'Ne colle RIEN ici : une fois le token créé et copié, appuie juste sur Entrée pour continuer (le collage se fera à l''étape suivante)' | Out-Null
 Write-Host ''
 
 # ---------------------------------------------------------------------------
