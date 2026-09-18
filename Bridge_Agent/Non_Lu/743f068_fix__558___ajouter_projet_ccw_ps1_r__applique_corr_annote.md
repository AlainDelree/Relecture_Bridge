743f068

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 743f068
# ── Qui a fait ce commit.
Author: Athanatos123 <79310036+AlainDelree@users.noreply.github.com>
# ── Quand ce commit a été fait.
Date:   Tue Sep 15 17:31:27 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #558 : ajouter_projet_ccw.ps1 réapplique correctement les tokens existants via nssm
    
    Cause confirmée : la réapplication d'AppEnvironmentExtra après recréation du
    service passait $envExtra splatté (@envExtra) à nssm set, ce qui envoie
    chaque paire KEY=VALUE comme argument SÉPARÉ au lieu d'une unique chaîne
    multi-lignes — nssm échoue alors avec « Environment should comprise strings
    of the form KEY=VALUE. ». Les deux autres endroits du dépôt qui posent
    AppEnvironmentExtra (mettre_a_jour_tokens_ccw.ps1, creer_projet_ccw_complet.ps1)
    joignent déjà les paires en UNE chaîne séparée par `n — c'est ce pattern
    qui fonctionne, maintenant appliqué ici aussi.
    
    Ajoute un test de non-régression (analyse statique du script, PowerShell/nssm
    indisponibles sous Linux) qui aurait détecté ce bug avant le test réel #556.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/provisioning/windows/ajouter_projet_ccw.ps1 b/provisioning/windows/ajouter_projet_ccw.ps1
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6d0d7e0..7d0c64e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/provisioning/windows/ajouter_projet_ccw.ps1
# ── Version APRÈS ce commit.
+++ b/provisioning/windows/ajouter_projet_ccw.ps1
# ── Zone modifiée : ligne 253 (10 ligne(s)) dans l'ancienne version → ligne 253 (16 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -253,10 +253,16 @@ nssm set $NomService AppStdout        $LogService
 nssm set $NomService AppStderr        $LogService
 
 # Réappliquer les tokens préservés (AppEnvironmentExtra) lus avant le remove, pour
-# que la relance n'efface pas les tokens déjà posés (issue #181). Chaque élément
-# de $envExtra est une entrée KEY=valeur, passée comme argument distinct à nssm set.
+# que la relance n'efface pas les tokens déjà posés (issue #181). BUG #558 : passer
+# $envExtra splatté (@envExtra) fait recevoir à nssm.exe chaque entrée KEY=valeur
+# comme un argument SÉPARÉ, au lieu d'une unique valeur multi-lignes — nssm échoue
+# alors avec « Environment should comprise strings of the form KEY=VALUE ». Comme
+# mettre_a_jour_tokens_ccw.ps1 et creer_projet_ccw_complet.ps1 (seul pattern qui
+# fonctionne avec nssm), les entrées doivent être jointes en UNE SEULE chaîne, avec
+# un saut de ligne `n comme séparateur, avant d'être passées à nssm set.
 if ($tokensPreserve) {
-    nssm set $NomService AppEnvironmentExtra @envExtra | Out-Null
+    $envExtraChaine = [string]::Join("`n", $envExtra)
+    nssm set $NomService AppEnvironmentExtra $envExtraChaine | Out-Null
     Info "Tokens existants réappliqués (AppEnvironmentExtra préservé) — relance sans perte."
 }
 
# (diff du fichier suivant)
diff --git a/tests/test_ajouter_projet_ccw_env_558.py b/tests/test_ajouter_projet_ccw_env_558.py
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..6815569
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/tests/test_ajouter_projet_ccw_env_558.py
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (154 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,154 @@
+#!/usr/bin/env python3
+"""Test de non-régression — issue #558 : `ajouter_projet_ccw.ps1` échouait à
+réappliquer les tokens existants (`AppEnvironmentExtra`) lors d'une relance
+sur un projet déjà finalisé.
+
+Cause réelle (confirmée par lecture du code, pas supposée) : la ligne de
+réapplication faisait `nssm set $NomService AppEnvironmentExtra @envExtra`
+— le splat PowerShell (`@`) d'un tableau de lignes `KEY=VALUE` fait recevoir
+à `nssm.exe` chaque entrée comme un argument SÉPARÉ au lieu d'une unique
+valeur multi-lignes, d'où l'erreur nssm « Environment should comprise
+strings of the form KEY=VALUE. ». Les DEUX autres endroits du dépôt qui
+posent `AppEnvironmentExtra` (`mettre_a_jour_tokens_ccw.ps1`,
+`creer_projet_ccw_complet.ps1`) construisent au contraire UNE SEULE chaîne,
+les paires étant séparées par un saut de ligne `` `n`` — c'est ce pattern qui
+fonctionne avec nssm (cf. BRIDGE_AGENT_DOC.md, « piège connu »).
+
+Ce test est une analyse STATIQUE du texte des scripts (pas d'exécution
+PowerShell ni nssm réels — indisponibles sous Linux) : il aurait détecté la
+régression avant le test réel sur `rummikub` en repérant le splat `@envExtra`
+passé directement à `nssm set … AppEnvironmentExtra`, et il garde la
+cohérence entre les 3 scripts qui manipulent ce paramètre.
+
+Exécution :  python3 tests/test_ajouter_projet_ccw_env_558.py
+Sortie      :  code 0 si tous les scénarios passent, 1 sinon.
+"""
+
+import re
+import sys
+from pathlib import Path
+
+RACINE = Path(__file__).resolve().parent.parent
+DOSSIER_PS = RACINE / "provisioning" / "windows"
+
+# Motif du bug #558 : un identifiant splatté (@nomVariable) passé comme valeur
+# à `nssm set … AppEnvironmentExtra`. Volontairement large (n'importe quel nom
+# de variable) pour attraper toute régression future, pas seulement $envExtra.
+MOTIF_SPLAT_BUG = re.compile(
+    r"nssm\s+set\s+\S+\s+AppEnvironmentExtra\s+@\w+", re.IGNORECASE
+)
+
+# Motif du pattern correct : une SEULE variable scalaire (pas de `@` en tête)
+# passée en valeur à `nssm set … AppEnvironmentExtra`.
+MOTIF_SCALAIRE_OK = re.compile(
+    r"nssm\s+set\s+\S+\s+AppEnvironmentExtra\s+\$\w+\s*(\||$)", re.MULTILINE
+)
+
+
+def _lire(nom_fichier: str) -> str:
+    chemin = DOSSIER_PS / nom_fichier
+    assert chemin.is_file(), f"script introuvable : {chemin}"
+    return chemin.read_text(encoding="utf-8-sig")
+
+
+def scenario_ajouter_projet_pas_de_splat():
+    """`ajouter_projet_ccw.ps1` ne doit JAMAIS passer un tableau splatté
+    (`@variable`) comme valeur de AppEnvironmentExtra à nssm — c'est
+    exactement le bug #558."""
+    texte = _lire("ajouter_projet_ccw.ps1")
+    trouve = MOTIF_SPLAT_BUG.findall(texte)
+    assert not trouve, f"splat @variable détecté sur AppEnvironmentExtra : {trouve}"
+    return {}
+
+
+def scenario_ajouter_projet_reapplique_une_chaine_unique():
+    """La réapplication des tokens préservés doit passer une SEULE chaîne
+    scalaire à `nssm set … AppEnvironmentExtra` (le fix #558)."""
+    texte = _lire("ajouter_projet_ccw.ps1")
+    assert MOTIF_SCALAIRE_OK.search(texte), (
+        "aucune réapplication de AppEnvironmentExtra via une variable "
+        "scalaire trouvée — le fix #558 a-t-il régressé ?"
+    )
+    return {}
+
+
+def scenario_ajouter_projet_construit_avec_saut_de_ligne():
+    """La chaîne reconstruite avant réapplication doit joindre les entrées
+    avec un saut de ligne `` `n`` (comme les 2 autres scripts qui posent
+    AppEnvironmentExtra) — un simple espace ou une virgule corromprait les
+    tokens (cf. piège documenté pour mettre_a_jour_tokens_ccw.ps1)."""
+    texte = _lire("ajouter_projet_ccw.ps1")
+    assert re.search(r'\[string\]::Join\(\s*"`n"\s*,\s*\$envExtra\s*\)', texte), (
+        "construction de la chaîne AppEnvironmentExtra introuvable ou "
+        "n'utilise plus le séparateur `n attendu"
+    )
+    return {}
+
+
+def scenario_coherence_mettre_a_jour_tokens():
+    """`mettre_a_jour_tokens_ccw.ps1` (référence qui a toujours fonctionné)
+    n'utilise pas non plus de splat — garde-fou de cohérence."""
+    texte = _lire("mettre_a_jour_tokens_ccw.ps1")
+    assert not MOTIF_SPLAT_BUG.findall(texte)
+    assert re.search(r"nssm\s+set\s+\$NomService\s+AppEnvironmentExtra\s+\$envExtra\s*\|", texte)
+    return {}
+
+
+def scenario_coherence_creer_projet_complet():
+    """`creer_projet_ccw_complet.ps1` (autre poseur de AppEnvironmentExtra,
+    hors provisioning/windows) n'utilise pas non plus de splat."""
+    chemin = RACINE / "creer_projet_ccw_complet.ps1"
+    assert chemin.is_file(), f"script introuvable : {chemin}"
+    texte = chemin.read_text(encoding="utf-8-sig")
+    assert not MOTIF_SPLAT_BUG.findall(texte)
+    assert re.search(r"nssm\s+set\s+\$NomService\s+AppEnvironmentExtra\s+\$nouvelExtra\s*\|", texte)
+    return {}
+
+
+def scenario_le_bug_aurait_ete_detecte_sur_l_ancien_code():
+    """Contrôle négatif : le motif de détection du bug matche bien sur le
+    texte de l'ANCIENNE ligne fautive (issue #558), pour prouver que ce test
+    n'est pas vide de sens — il aurait échoué AVANT le fix."""
+    ancienne_ligne = 'nssm set $NomService AppEnvironmentExtra @envExtra | Out-Null'
+    assert MOTIF_SPLAT_BUG.search(ancienne_ligne), (
+        "le motif de détection ne repère pas l'ancien bug — test inutile"
+    )
+    return {}
+
+
+def main():
+    tests = [
+        ("ajouter_projet_ccw.ps1 : pas de splat @variable sur AppEnvironmentExtra (bug #558)",
+         scenario_ajouter_projet_pas_de_splat),
+        ("ajouter_projet_ccw.ps1 : réapplication via une chaîne scalaire unique",
+         scenario_ajouter_projet_reapplique_une_chaine_unique),
+        ("ajouter_projet_ccw.ps1 : chaîne construite avec [string]::Join(\"`n\", ...)",
+         scenario_ajouter_projet_construit_avec_saut_de_ligne),
+        ("mettre_a_jour_tokens_ccw.ps1 : cohérence, pas de splat",
+         scenario_coherence_mettre_a_jour_tokens),
+        ("creer_projet_ccw_complet.ps1 : cohérence, pas de splat",
+         scenario_coherence_creer_projet_complet),
+        ("contrôle négatif : le motif détecte bien l'ancien code fautif",
+         scenario_le_bug_aurait_ete_detecte_sur_l_ancien_code),
+    ]
+    echecs = 0
+    for nom, fn in tests:
+        try:
+            rap = fn()
+            print(f"  ✓ {nom}  ({rap})")
+        except AssertionError as e:
+            echecs += 1
+            print(f"  ✗ {nom}\n      {e}")
+        except Exception as e:  # noqa: BLE001
+            echecs += 1
+            print(f"  ✗ {nom} — erreur inattendue : {type(e).__name__}: {e}")
+
+    if echecs:
+        print(f"\n❌ {echecs} scénario(s) en échec.")
+        return 1
+    print("\n✅ Tous les scénarios passent.")
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main())
