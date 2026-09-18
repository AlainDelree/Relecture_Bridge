65890a4

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 65890a4
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 14:03:36 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    chore: réécrit AMELIORATIONS.md — todo vidée, lazy loading GSM confirmé efficace

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/AMELIORATIONS.md b/AMELIORATIONS.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index ba8d3f9..f9403c1 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/AMELIORATIONS.md
# ── Version APRÈS ce commit.
+++ b/AMELIORATIONS.md
# ── Zone modifiée : ligne 1 (146 ligne(s)) dans l'ancienne version → ligne 1 (33 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1,146 +1,33 @@
 # FF_Galerie — Liste d'améliorations
-> Audit du 2026-06-08 · Mis à jour 2026-06-11
+> Repris à zéro le 2026-08-25 — l'historique détaillé (gains immédiats, performance images, architecture, infra) est archivé dans `git log` et les commits de l'époque ; ce fichier ne garde que ce qui reste réellement à faire.
 
-**Légende effort :** 🟢 rapide (< 30 min) · 🟡 moyen (1–3 h) · 🔴 chantier (> 3 h)  
+**Légende effort :** 🟢 rapide (< 30 min) · 🟡 moyen (1–3 h) · 🔴 chantier (> 3 h)
 **Légende impact :** ⭐ cosmétique · ⭐⭐ utile · ⭐⭐⭐ critique
 
 ---
 
-## 0 · To-do active
+## To-do active
 
-- [x] 🟡 ⭐⭐⭐ **Rendu galerie desktop** ✅
-- [ ] 🟢 ⭐⭐ **Instagram Frédérique** → `contact.html` + `data/contact.json` quand elle crée le compte
-- [x] 🟡 ⭐⭐ **Admin : gestion musique** ✅
-- [ ] 🟢 ⭐⭐ **Photos vraies Daw** — remplacer placeholders `artistes/daw/`
-- [ ] 🟢 ⭐ **Tester envoi d'emails** depuis le GSM de Fred et de Daw
-- [x] 🟢 ⭐ **Vérifier HTTPS enforce** ✅
-- [ ] 🟢 ⭐⭐ **Révoquer token classic Fred** — à faire quand Alain est avec elle
-- [ ] 🟢 ⭐ **Lien guide photogrammétrie dans admin** — onglet Artistes Invités, visible si `type === "sculpture"`. PDF dans `docs/guide-photo-3D-sculpture.pdf`. URL : `https://raw.githubusercontent.com/AlainDelree/FF_Galerie/main/docs/guide-photo-3D-sculpture.pdf`
+_Rien pour l'instant._
 
 ---
 
-## 1 · Gains immédiats
+## Idées futures (non planifiées)
 
-- [x] 🟢 ⭐⭐⭐ **Restriction domaine EmailJS** ✅
-- [x] 🟢 ⭐⭐ **PAT fine-grained GitHub** ✅
-- [x] 🟢 ⭐⭐ **`loading="lazy"` + `decoding="async"`** ✅
-- [x] 🟢 ⭐⭐ **Unifier Google Fonts** ✅
-- [x] 🟢 ⭐ **SRI sur CDN** ✅
-
----
-
-## 2 · Performance images
-
-> **Résultat :** 8,3 Mo → ~756 Ko sur le mur (×11). Modale mobile : WebP via srcset (×2.5 vs JPG).
-
-- [x] 🟡 ⭐⭐⭐ **Miniatures WebP** (`toile-NNN-thumb.webp`, 400 px, q82) ✅
-- [x] 🟡 ⭐⭐ **Plein format WebP** (`toile-NNN.webp`, q88) — 32 toiles ✅
-- [x] 🟡 ⭐⭐⭐ **galerie.js** : mur → miniature, modale → plein format ✅
-- [x] 🟢 ⭐⭐ **Préchargement via thumbs WebP** ✅
-- [x] 🟢 ⭐⭐ **srcset galerie** — mur mobile + mur desktop + modale (thumb 400w + WebP 1200w, lazy-imageset) ✅
-- [x] 🟢 ⭐⭐ **Thumbs WebP nouvelles toiles** — toiles 34-36 générées ✅
-
----
-
-## 3 · Nettoyage repo
-
-- [x] **Retirer fichiers parasites** ✅
-- [x] **Mettre à jour `.gitignore`** ✅
-
----
-
-## 4 · Architecture
-
-### 4a · Templates HTML externalisés
-- [x] 🔴 ⭐⭐ **TPL_* → fichiers HTML** ✅
-
-### 4b · Modules extraits (admin.js 3984 → 852 lignes)
-
-| Module | Lignes | Contenu |
-|--------|--------|---------|
-| `admin-vue-artistes.js` | 378 | Vue artistes invités |
-| `admin-emailjs.js` | 295 | Config & test EmailJS |
-| `admin-media.js` | 198 | Musique + Photo resize |
-| `admin-pages.js` | 267 | Infos/Agenda + Collègues |
-| `admin-backup.js` | 67 | Backup/Rollback |
-| `admin-textures.js` | 735 | Presets/Couleurs/Textures + Crop |
-| `admin-galerie.js` | 1051 | Plan · Grille · Stock · Placement · Fiche · Modal salle |
-
-- [x] C1–C5 tous mergés ✅
-
-### 4c · Refacto galerie.js → core + renderer
-- [x] 🟡 ⭐⭐ **`galerie.js` splitté** ✅
-  - `galerie-core.js` (508 l.) : noyau partagé — nav, modal, silhouettes, plancher, utils
-  - `galerie-peinture.js` (348 l.) : renderer peinture — `creerTableau` + init `Promise.all`
-  - 5 HTML mis à jour (Fred, Daw, Alaindelree, Raoul, template)
-  - Prépare `galerie-sculpture.js` : même core, renderer différent
-
-### 4d · Propagation automatique du `<head>`
-- [x] 🔴 ⭐⭐⭐ **Script `build/propagate_head.py`** ✅  
-  Usage : modifier `build/head-template.html` ou `build/pages.json` → `python3 build/propagate_head.py` → commit.  
-  Prérequis galerie sculpture : ✅ fait.
-
----
-
-## 5 · Qualité & robustesse
-
-- [x] 🟢 ⭐⭐ **noindex artistes draft** ✅
-- [x] 🟢 ⭐ **Stubs vides supprimés** ✅
-- [x] 🟢 ⭐⭐ **Capturer 401 sur écriture** ✅
-- [x] 🟡 ⭐⭐ **UX Couleurs/Textures** — boutons Sauvegarder/Annuler + snapshot ✅
-- [x] 🟢 ⭐⭐ **UX Suppression toile** — bouton dans barre principale ✅
-- [x] 🟢 ⭐⭐ **Panneau Musique trop haut sur PC** ✅
-- [x] 🟡 ⭐⭐ **UX Autres pages** — bouton Enregistrer par section, sauve GitHub directement ✅
-- [x] 🟢 ⭐⭐ **Feedback boutons** — "En cours…" uniformisé ✅
-- [x] 🟢 ⭐⭐ **noscript + aria-label** — 5 pages publiques ✅
-- [ ] 🟢 ⭐⭐ **Lenteur chargement miniatures GSM** — envisager `raw.githubusercontent.com + cache:'reload'`
-
----
-
-## 6 · Infrastructure
-
-- [x] 🟢 ⭐⭐⭐ **Cloudflare Workers** ✅
-- [x] 🟢 ⭐⭐⭐ **`dev.frederiqueferette.be`** ✅
-- [x] 🟢 ⭐⭐⭐ **BRANCH dynamique** ✅
-- [x] 🟢 ⭐⭐ **package.json + .assetsignore** — build Cloudflare ~20s ✅
-- [x] 🟢 ⭐ **Supprimer compte Netlify** ✅
-
----
-
-## 7 · Idées futures
-
-- [x] 💡 **Galerie sculpture** — Phase 1 (fondations) + Phase 2 (renderer) ✅ · Phase 3 (admin) à faire
-  - `galerie-sculpture.js` + `galerie-sculpture.css` · socles sur parquet · model-viewer auto-rotate
-  - Gabarit auto depuis `dimensions.hauteur` (≤25→S, ≤50→M, ≤100→L, >100→SOL)
-  - Dimensions viewer proportionnelles (px/cm) · profondeur par scale
-  - Grille de repérage SVG perspective (A→J × 1→5) · bouton ⊞ toggle
-  - ⚠️ **Scale réel à remettre** quand GLBs photogrammétriques disponibles :
-    ```js
-    viewer.addEventListener('load', () => {
-      const dims = viewer.getDimensions();
-      const f = targetHm / dims.y;
-      if (f > 0.01 && f < 100) viewer.setAttribute('scale', f+' '+f+' '+f);
-    });
-    ```
-    Nécessite GLBs à l'échelle réelle (1 unité = 1 mètre). Chercher sur Sketchfab : filtre `photogrammetry`.
-- [ ] 💡 **PWA / Service Worker** — galerie installable sur mobile, consultable offline en vernissage.
-- [ ] 💡 **raw.githubusercontent.com + `cache:'reload'`** — plus rapide que API pour lireRaw, tout en évitant le cache CDN.
 - [ ] 💡 **Palette de couleurs par artiste invité**
+- [ ] 💡 **Choix du nombre de silhouettes par plan de profondeur** dans l'admin (actuellement aléatoire dans `genererSilhouettes()`)
 
 ---
 
-## Récapitulatif restant
+## Fait — pour mémoire (détail dans `git log`)
 
-| Priorité | Tâche | Effort |
-|----------|-------|--------|
-| ⚡ 1 | Révoquer token classic Fred | 🟢 |
-| ⚡ 2 | Instagram Fred (en attente) | 🟢 |
-| ⚡ 3 | Photos vraies Daw | 🟢 |
-| ⚡ 4 | Test emails GSM | 🟢 |
-| 🏗️ 5 | Lenteur miniatures GSM | 🟡 |
-| 💡 6 | Galerie sculpture | 🔴 |
-| 💡 7 | PWA / Service Worker | 🔴 |
+- Rendu galerie desktop, admin gestion musique, HTTPS enforce
+- Sécurité : restriction domaine EmailJS, PAT fine-grained, révocation token classic Fred
+- Performance images : miniatures + plein format WebP, srcset, préchargement (60 fichiers `.webp`), lazy loading natif confirmé efficace sur GSM (25/08/2026)
+- Architecture : templates HTML externalisés, `admin.js` splitté en modules, `galerie.js` → core + renderers, propagation automatique du `<head>`
+- Infra : Cloudflare Workers, `dev.frederiqueferette.be`, PWA (`sw.js`, `manifest.webmanifest`, `app-worker/`)
+- Galerie sculpture : renderer complet, admin complet (greffons, scénarios vitrine, gabarits/supports, anti-chevauchement) — pas juste les fondations, tout le système vitrine est en place
 
 ---
 
-*Mis à jour 2026-06-13 · Auto-deploy dev → Cloudflare Workers via GitHub Action (wrangler 4, Node 22) · plus de `wrangler deploy` manuel nécessaire*
+*Mis à jour 2026-08-25*
