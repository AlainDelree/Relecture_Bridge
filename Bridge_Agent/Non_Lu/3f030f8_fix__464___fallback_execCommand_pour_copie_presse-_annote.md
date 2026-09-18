3f030f8

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 3f030f8
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Aug 20 15:42:52 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #464 : fallback execCommand pour copie presse-papier en HTTP LAN

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/static/js/app.js b/static/js/app.js
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 5e75ba6..e878c3f 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/static/js/app.js
# ── Version APRÈS ce commit.
+++ b/static/js/app.js
# ── Zone modifiée : ligne 2945 (6 ligne(s)) dans l'ancienne version → ligne 2945 (40 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2945,6 +2945,40 @@ function feedbackBoutonVide(btn, libelle) {
   }, 2000);
 }
 
+// Copie texte dans le presse-papier : navigator.clipboard.writeText() si
+// disponible et la promesse aboutit ; sinon fallback document.execCommand
+// ('copy') via un <textarea> temporaire hors écran (issue #464). Nécessaire en
+// HTTP non-localhost (mode --lan) : navigator.clipboard est restreint aux
+// contextes sécurisés (HTTPS/localhost) et y est silencieusement indisponible.
+// Retourne true si la copie a réussi (par l'une ou l'autre voie).
+async function copierPressePapier(texte) {
+  if (navigator.clipboard && navigator.clipboard.writeText) {
+    try {
+      await navigator.clipboard.writeText(texte);
+      return true;
+    } catch(e) {
+      console.warn('copierPressePapier : échec navigator.clipboard, fallback execCommand.', e);
+    }
+  }
+  try {
+    const ta = document.createElement('textarea');
+    ta.value = texte;
+    ta.style.position = 'fixed';
+    ta.style.left = '-9999px';
+    ta.style.top = '0';
+    document.body.appendChild(ta);
+    ta.focus();
+    ta.select();
+    const ok = document.execCommand('copy');
+    document.body.removeChild(ta);
+    if (!ok) console.warn('copierPressePapier : échec document.execCommand(copy).');
+    return ok;
+  } catch(e) {
+    console.warn('copierPressePapier : échec fallback execCommand.', e);
+    return false;
+  }
+}
+
 async function copierReponse(btn) {
   // Le bouton vit dans le bloc résumé : on copie le texte de CE bloc
   // uniquement (résumé court), jamais le bloc détails verbeux (issue #59).
# ── Zone modifiée : ligne 2957 (23 ligne(s)) dans l'ancienne version → ligne 2991 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -2957,23 +2991,17 @@ async function copierReponse(btn) {
   const texte = corps.textContent || '';
   // Garde « copie vide » (issue #122) : rien à copier → feedback ⚠, pas de ✓.
   if (texteCopieVide(texte)) { feedbackBoutonVide(btn, libelle); return; }
-  if (navigator.clipboard && navigator.clipboard.writeText) {
-    try {
-      await navigator.clipboard.writeText(texte);
-      btn.disabled = true;
-      btn.textContent = '✓ Copié !';
-      setTimeout(function() {
-        btn.textContent = libelle;
-        btn.disabled = false;
-      }, 2000);
-      return;
-    } catch(e) {
-      console.warn('copierReponse : échec navigator.clipboard, fallback sélection.', e);
-    }
-  } else {
-    console.warn('copierReponse : navigator.clipboard indisponible (contexte non-HTTPS), fallback sélection.');
+  if (await copierPressePapier(texte)) {
+    btn.disabled = true;
+    btn.textContent = '✓ Copié !';
+    setTimeout(function() {
+      btn.textContent = libelle;
+      btn.disabled = false;
+    }, 2000);
+    return;
   }
-  // Fallback : on sélectionne le texte du bloc pour permettre un Ctrl+C manuel.
+  // Fallback ultime (échec clipboard ET execCommand) : on sélectionne le texte
+  // du bloc pour permettre un Ctrl+C manuel.
   const sel = window.getSelection();
   if (sel) {
     const range = document.createRange();
# ── Zone modifiée : ligne 3027 (23 ligne(s)) dans l'ancienne version → ligne 3055 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3027,23 +3055,17 @@ async function copierTout(btn) {
   const libelle = btn.textContent;
   // Garde « copie vide » (issue #122) : rien à copier → feedback ⚠, pas de ✓.
   if (texteCopieVide(texte)) { feedbackBoutonVide(btn, libelle); return; }
-  if (navigator.clipboard && navigator.clipboard.writeText) {
-    try {
-      await navigator.clipboard.writeText(texte);
-      btn.disabled = true;
-      btn.textContent = '✓ Copié !';
-      setTimeout(function() {
-        btn.textContent = libelle;
-        btn.disabled = false;
-      }, 1500);
-      return;
-    } catch(e) {
-      console.warn('copierTout : échec navigator.clipboard, fallback sélection.', e);
-    }
-  } else {
-    console.warn('copierTout : navigator.clipboard indisponible (contexte non-HTTPS), fallback sélection.');
+  if (await copierPressePapier(texte)) {
+    btn.disabled = true;
+    btn.textContent = '✓ Copié !';
+    setTimeout(function() {
+      btn.textContent = libelle;
+      btn.disabled = false;
+    }, 1500);
+    return;
   }
-  // Fallback : à défaut de presse-papier, on sélectionne au moins le résumé
+  // Fallback ultime (échec clipboard ET execCommand) : à défaut de
+  // presse-papier, on sélectionne au moins le résumé
   // affiché (le texte complet reconstruit ne peut pas être injecté dans le DOM).
   const sel = window.getSelection();
   if (sel && corps) {
# ── Zone modifiée : ligne 3098 (16 ligne(s)) dans l'ancienne version → ligne 3120 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3098,16 +3120,9 @@ async function copierReponseDepuisBadge(event, nom, numero) {
   // échec ou dernier commentaire vide) → feedback ⚠, aucune copie, pas de ✓.
   if (texteCopieVide(texte)) { feedbackBadgeVide(badge, original, titreOriginal); return; }
 
-  // Copie dans le presse-papier (fallback silencieux si indisponible / non-HTTPS).
-  if (navigator.clipboard && navigator.clipboard.writeText) {
-    try {
-      await navigator.clipboard.writeText(texte);
-    } catch(e) {
-      console.warn('copierReponseDepuisBadge : échec navigator.clipboard.', e);
-    }
-  } else {
-    console.warn('copierReponseDepuisBadge : navigator.clipboard indisponible (non-HTTPS).');
-  }
+  // Copie dans le presse-papier (fallback execCommand si l'API clipboard est
+  // indisponible ou échoue — issue #464).
+  await copierPressePapier(texte);
 
   // Feedback visuel : ✅ → ✓ pendant 1,5 s, puis retour au libellé (ligne inchangée).
   if (badge) {
# ── Zone modifiée : ligne 3281 (16 ligne(s)) dans l'ancienne version → ligne 3296 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3281,16 +3296,9 @@ async function copierToutEtDiffDepuisBadge(event, nom, numero) {
     afficherToast('⚠ Diff volumineux (' + nbLignes + ' lignes) — Claude.ai pourrait ne pas le lire');
   }
 
-  // Copie dans le presse-papier (fallback silencieux si indisponible / non-HTTPS).
-  if (navigator.clipboard && navigator.clipboard.writeText) {
-    try {
-      await navigator.clipboard.writeText(texte);
-    } catch(e) {
-      console.warn('copierToutEtDiffDepuisBadge : échec navigator.clipboard.', e);
-    }
-  } else {
-    console.warn('copierToutEtDiffDepuisBadge : navigator.clipboard indisponible (non-HTTPS).');
-  }
+  // Copie dans le presse-papier (fallback execCommand si l'API clipboard est
+  // indisponible ou échoue — issue #464).
+  await copierPressePapier(texte);
 
   // Feedback visuel : « All » → ✓ pendant 1,5 s, puis retour au libellé.
   if (badge) {
# ── Zone modifiée : ligne 3366 (16 ligne(s)) dans l'ancienne version → ligne 3374 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -3366,16 +3374,9 @@ async function copierDiffDepuisBadge(event, nom, numero) {
   // plus haut, feedback neutre déjà distinct du ✓.)
   if (texteCopieVide(texte)) { feedbackBadgeVide(badge, original, titreOriginal); return; }
 
-  // Copie dans le presse-papier (fallback silencieux si indisponible / non-HTTPS).
-  if (navigator.clipboard && navigator.clipboard.writeText) {
-    try {
-      await navigator.clipboard.writeText(texte);
-    } catch(e) {
-      console.warn('copierDiffDepuisBadge : échec navigator.clipboard.', e);
-    }
-  } else {
-    console.warn('copierDiffDepuisBadge : navigator.clipboard indisponible (non-HTTPS).');
-  }
+  // Copie dans le presse-papier (fallback execCommand si l'API clipboard est
+  // indisponible ou échoue — issue #464).
+  await copierPressePapier(texte);
 
   // Feedback visuel : « Diff » → ✓ pendant 1,5 s, puis retour au libellé.
   if (badge) {
