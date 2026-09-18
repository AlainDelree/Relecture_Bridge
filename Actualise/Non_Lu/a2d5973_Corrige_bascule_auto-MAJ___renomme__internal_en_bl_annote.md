a2d5973

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit a2d5973
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 22:35:21 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige bascule auto-MAJ : renomme _internal en bloc plutôt que fichier par fichier (issue #34)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/actualise.py b/actualise.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index d0873cb..9ee147b 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/actualise.py
# ── Version APRÈS ce commit.
+++ b/actualise.py
# ── Zone modifiée : ligne 116 (6 ligne(s)) dans l'ancienne version → ligne 116 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -116,6 +116,7 @@ def _relancer_en_enfant() -> None:
 
 
 _NOM_EXECUTABLE = "Actualise.exe"
+_NOM_DOSSIER_INTERNAL = "_internal"
 
 
 def _basculer_par_renommage(dossier_source: Path, destination: Path) -> None:
# ── Zone modifiée : ligne 137 (9 ligne(s)) dans l'ancienne version → ligne 138 (32 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -137,9 +138,32 @@ def _basculer_par_renommage(dossier_source: Path, destination: Path) -> None:
     encore verrouillé) remonte telle quelle à l'appelant, qui décide de
     la marche à suivre (conservation du zip source pour nouvelle
     tentative).
+
+    Cas particulier de ``_NOM_DOSSIER_INTERNAL`` (``_internal``, dossier
+    PyInstaller contenant les ``.pyd``/``.dll`` chargés en mémoire par le
+    processus en cours) : contrairement à ``_NOM_EXECUTABLE``, ces
+    fichiers ne peuvent pas être renommés individuellement (verrou par
+    fichier). Windows autorise en revanche de renommer le *dossier*
+    entier même si des fichiers à l'intérieur sont verrouillés — même
+    bascule en deux temps que ``_NOM_EXECUTABLE``, mais appliquée au
+    dossier comme un bloc, avant la boucle fichier par fichier ci-dessous
+    (qui exclut alors ce dossier, déjà traité).
     """
+    dossier_internal_source = dossier_source / _NOM_DOSSIER_INTERNAL
+    dossier_internal_destination = destination / _NOM_DOSSIER_INTERNAL
+    bascule_internal_en_bloc = (
+        dossier_internal_source.is_dir() and dossier_internal_destination.is_dir()
+    )
+    if bascule_internal_en_bloc:
+        dossier_internal_destination.replace(
+            dossier_internal_destination.with_name(f"{_NOM_DOSSIER_INTERNAL}.old")
+        )
+        os.replace(dossier_internal_source, dossier_internal_destination)
+
     for chemin_source in dossier_source.rglob("*"):
         chemin_relatif = chemin_source.relative_to(dossier_source)
+        if bascule_internal_en_bloc and chemin_relatif.parts[0] == _NOM_DOSSIER_INTERNAL:
+            continue
         chemin_destination = destination / chemin_relatif
         if chemin_source.is_dir():
             chemin_destination.mkdir(parents=True, exist_ok=True)
# ── Zone modifiée : ligne 151 (19 ligne(s)) dans l'ancienne version → ligne 175 (30 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -151,19 +175,30 @@ def _basculer_par_renommage(dossier_source: Path, destination: Path) -> None:
 
 
 def _nettoyer_ancien_executable() -> None:
-    """Supprime silencieusement le reliquat ``Actualise.exe.old`` laissé
-    par une bascule d'auto-mise-à-jour précédente, s'il existe.
+    """Supprime silencieusement les reliquats ``Actualise.exe.old`` et
+    ``_internal.old`` laissés par une bascule d'auto-mise-à-jour
+    précédente, s'ils existent.
 
     Voir ``_basculer_par_renommage`` : le renommage préalable de
     l'exécutable courant en ``.old`` (seule opération autorisée par
     Windows sur un ``.exe`` en cours d'exécution) laisse ce fichier une
     fois la bascule terminée. Il n'est plus verrouillé par personne dès
     que ce nouveau lancement démarre : nettoyage au tout début du
-    lancement suivant.
+    lancement suivant. Même principe pour ``_internal.old`` (dossier),
+    à ceci près que ``shutil.rmtree`` peut échouer si le nettoyage
+    intervient trop tôt (fichiers encore verrouillés par l'ancien
+    processus en cours de terminaison) : l'erreur est alors ignorée
+    silencieusement, le nettoyage sera retenté au lancement suivant.
     """
-    chemin_ancien = config.chemin_config_portable() / f"{_NOM_EXECUTABLE}.old"
+    dossier_portable = config.chemin_config_portable()
+
+    chemin_ancien = dossier_portable / f"{_NOM_EXECUTABLE}.old"
     chemin_ancien.unlink(missing_ok=True)
 
+    dossier_internal_ancien = dossier_portable / f"{_NOM_DOSSIER_INTERNAL}.old"
+    if dossier_internal_ancien.is_dir():
+        shutil.rmtree(dossier_internal_ancien, ignore_errors=True)
+
 
 def appliquer_mises_a_jour_en_attente(est_enfant: bool) -> None:
     """Applique, au lancement, les mises à jour mises en attente au
