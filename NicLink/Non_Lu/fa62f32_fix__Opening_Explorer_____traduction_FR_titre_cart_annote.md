fa62f32

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit fa62f32
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 14 20:12:56 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: Opening Explorer — traduction FR titre/carte (issue #152)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/web/static/i18n/fr.json b/nicsoft/web/static/i18n/fr.json
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index b729664..beea283 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/web/static/i18n/fr.json
# ── Version APRÈS ce commit.
+++ b/nicsoft/web/static/i18n/fr.json
# ── Zone modifiée : ligne 237 (7 ligne(s)) dans l'ancienne version → ligne 237 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -237,7 +237,7 @@
   "parametres.enregistrer": "💾 Enregistrer",
   "parametres.toast.enregistre": "Paramètres enregistrés",
   "parametres.toast.erreur": "Erreur lors de l'enregistrement des paramètres",
-  "opening_explorer.titre": "♟ Opening Explorer",
+  "opening_explorer.titre": "♟ Explorateur d'ouvertures",
   "opening_explorer.catalogue.titre": "📚 Catalogue",
   "opening_explorer.catalogue.vide": "Aucune ouverture dans le catalogue.",
   "opening_explorer.mes_ouvertures.titre": "★ Mes ouvertures",
# ── Zone modifiée : ligne 613 (6 ligne(s)) dans l'ancienne version → ligne 613 (6 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -613,6 +613,6 @@
   "ouvertures.titre": "📖 Ouvertures",
   "ouvertures.carte_exercices.titre": "📚 Exercices",
   "ouvertures.carte_exercices.desc": "Entraînez-vous aux ouvertures sur l'échiquier physique — le livre répond et corrige vos coups.",
-  "ouvertures.carte_explorer.titre": "♟ Opening Explorer",
+  "ouvertures.carte_explorer.titre": "♟ Explorateur d'ouvertures",
   "ouvertures.carte_explorer.desc": "Explorez une ouverture coup par coup avec des explications générées par IA."
 }
