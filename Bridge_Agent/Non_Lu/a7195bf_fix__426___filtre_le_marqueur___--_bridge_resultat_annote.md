a7195bf

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a7195bf
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Mon Aug 10 13:17:28 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #426 : filtre le marqueur <!-- bridge:resultat --> du texte copié dans le presse-papier

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b8d5554..0bd39ef 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2453 (7 ligne(s)) dans l'ancienne version → ligne 2453 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2453,7 +2453,7 @@ function construireHtmlIssue(it, nom) {
         // Réponse de CCL : on sépare le résumé court (texte AVANT <details>)
         // du bloc détails verbeux. Le bouton « Copier » est ancré au bloc
         // résumé et ne copie que ce résumé — pas les détails (issue #59).
-        const corpsBrut = c.body || '';
+        const corpsBrut = retirerMarqueurResultat(c.body || '');
         const idxDetails = corpsBrut.indexOf('<details>');
         const resume = (idxDetails >= 0 ? corpsBrut.slice(0, idxDetails) : corpsBrut)
                        .replace(/\s+$/, '');
# ── Zone modifiée : ligne 2919 (6 ligne(s)) dans l'ancienne version → ligne 2919 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2919,6 +2919,16 @@ async function copierReponse(btn) {
   }
 }
 
+// Retire la ligne marqueur `<!-- bridge:resultat -->` (posée en tête du
+// commentaire CCL par watcher.py, MARQUEUR_RESULTAT) du texte brut avant
+// affichage/copie (issue #426) : ce marqueur HTML est avalé par le parseur
+// de Claude.ai au collage, rendant le contenu illisible. Il reste dans le
+// corps GitHub brut (utile à watcher.py pour repérer le commentaire) — on ne
+// le filtre qu'à la lecture côté interface, jamais côté GitHub.
+function retirerMarqueurResultat(texte) {
+  return (texte || '').replace(/^<!--\s*bridge:resultat\s*-->\n?/, '');
+}
+
 // Reconstruit la réponse CCL COMPLÈTE en markdown brut (issue #77) : le résumé,
 // une ligne vide, puis le contenu du bloc <details> débarrassé de ses seules
 // balises structurantes (<details>, <summary>, </summary>, </details>). Le texte
# ── Zone modifiée : ligne 3050 (7 ligne(s)) dans l'ancienne version → ligne 3060 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3050,7 +3060,7 @@ async function copierReponseDepuisBadge(event, nom, numero) {
 function reponseCompleteCcl(it) {
   const comms = (it && it.comments) || [];
   if (!comms.length) return '';
-  const corpsBrut = comms[comms.length - 1].body || '';
+  const corpsBrut = retirerMarqueurResultat(comms[comms.length - 1].body || '');
   const idxDetails = corpsBrut.indexOf('<details>');
   const resume  = (idxDetails >= 0 ? corpsBrut.slice(0, idxDetails) : corpsBrut)
                   .replace(/\s+$/, '');
