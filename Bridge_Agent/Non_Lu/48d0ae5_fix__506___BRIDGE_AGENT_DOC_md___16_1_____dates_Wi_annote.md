48d0ae5

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 48d0ae5
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 30 16:30:47 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #506 : BRIDGE_AGENT_DOC.md §16.1 — dates Windows PC fixe alignées sur eval-expiration.json (déjà correct)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index c790521..bb79f80 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 1655 (8 ligne(s)) dans l'ancienne version → ligne 1655 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1655,8 +1655,8 @@ Fine-grained tokens) :
 
 | Repère | Valeur | Source |
 |--------|--------|--------|
-| Date d'installation Windows | **2026-07-19** | `provisioning/windows/eval-expiration.json` (`date_installation`) |
-| Expiration éval Windows (90 j) | **2026-10-17** | idem (`date_expiration`, recalculée : install + 90 j) |
+| Date d'installation Windows | **2026-08-17** | `provisioning/windows/eval-expiration.json` (`date_installation`) |
+| Expiration éval Windows (90 j) | **2026-11-15** | idem (`date_expiration`, recalculée : install + 90 j) |
 | Expiration token GitHub | **≈ 2026-10-17** (aligné volontairement, non stocké) | *pas de métadonnée dédiée — voir note ci-dessous* |
 
 > Le token GitHub fine-grained a été créé avec une durée alignée sur l'éval
# (diff du fichier suivant)
diff --git a/CHANGELOG-506.md b/CHANGELOG-506.md
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..de1fb28
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/CHANGELOG-506.md
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (24 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,24 @@
+## #506 — eval-expiration.json : correction date d'installation Windows PC fixe (2026-08-30)
+
+`provisioning/windows/eval-expiration.json` contenait déjà `date_installation:
+2026-08-17` / `date_expiration: 2026-11-15` (mis à jour par le fix #452, le
+2026-08-18) — pas les valeurs `2026-07-19`/`2026-10-17` que l'issue supposait.
+La mesure fraîche du 30 août 2026 fournie dans l'issue (`GracePeriodRemaining`
+= 111244 min ≈ 77,25 j restants) recalcule une expiration au **2026-11-15**
+et une installation au **2026-08-17** — exactement les valeurs déjà en place.
+Aucune modification du JSON n'était donc nécessaire.
+
+En revanche, `BRIDGE_AGENT_DOC.md` §16.1 (tableau « Repères de dates »)
+n'avait pas été mis à jour lors du fix #452 et affichait encore les
+anciennes dates de la VM. Corrigé :
+- « Date d'installation Windows » : 2026-07-19 → **2026-08-17**
+- « Expiration éval Windows (90 j) » : 2026-10-17 → **2026-11-15**
+
+Non touché (hors périmètre de l'issue) :
+- §16, tableau `provisioning/windows/` (ligne `eval-expiration.json`) :
+  mentions 2026-07-19/2026-10-17 explicitement présentées comme historique
+  de l'ancienne VM VirtualBox (issue #167), conservées telles quelles.
+- §16.1, ligne « Expiration token GitHub » (≈ 2026-10-17) : concerne
+  l'expiration d'un token GitHub fine-grained réel, non recalculable depuis
+  la mesure Windows fournie — signalé pour vérification manuelle éventuelle,
+  non modifié.
