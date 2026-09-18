8e909ce

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 8e909ce
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Jul 27 07:15:11 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige le contraste illisible des pastilles de filtre projet désélectionnées (issue #250)
    
    Trois atténuations cumulées (opacity:.4 + fond gris clair + texte #999 déjà
    pâle) faisaient tomber le contraste du texte très en dessous de tout seuil
    lisible. Supprime l'opacity globale (qui délavait aussi la pastille colorée
    et la bordure, cf. le même piège corrigé en #156) et ne garde que fond +
    texte, avec #5a5a5a sur #f2f2f0 (ratio 6.15:1, > seuil WCAG AA 4.5:1).

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/css/style.css b/static/css/style.css
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0856b46..6b1a1f0 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/css/style.css
# ── Version APRÈS ce commit.
+++ b/static/css/style.css
# ── Zone modifiée : ligne 105 (7 ligne(s)) dans l'ancienne version → ligne 105 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -105,7 +105,15 @@ button.danger:hover{background:#f8d7da}
   font-weight:500;padding:5px 11px;border:1px solid #ccc;border-radius:14px;
   background:#fff;color:#333;cursor:pointer;user-select:none;transition:opacity .12s}
 .filtre-projet .pastille{width:9px;height:9px;border-radius:50%;flex-shrink:0}
-.filtre-projet.inactif{opacity:.4;background:#f2f2f0;color:#999}
+/* Pastille désélectionnée lisible (issue #250) : l'ancienne opacity:.4 se
+   cumulait à un fond clair et un texte déjà pâle (#999), faisant tomber le
+   contraste du texte très en dessous de tout seuil lisible — précisément
+   l'info nécessaire pour re-sélectionner un filtre. Même piège que la ligne
+   « résultat traité » (#156) : on n'atténue plus via une opacity globale (qui
+   délavait aussi la pastille colorée et la bordure), seulement le fond et le
+   texte. #5a5a5a sur #f2f2f0 donne un ratio de contraste de 6.15:1, largement
+   au-dessus du seuil WCAG AA (4.5:1). */
+.filtre-projet.inactif{background:#f2f2f0;color:#5a5a5a}
 .filtre-projet.tous{border-style:dashed;color:#555}
 /* Liste HTML cliquable des issues (remplace l'ancienne combobox #select-issue).
    Une ligne par issue, coloriée à la couleur de son projet — contrôle total du
