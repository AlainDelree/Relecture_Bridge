f238327

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit f238327
# ── Qui a fait ce commit.
Author: Alain Delree <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Fri Aug 7 21:53:17 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Corrige WinError 5 (bascule auto-MAJ en 2 temps) et PermissionError unlink (issue #33)

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/actualise.py b/actualise.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 9813aeb..d0873cb 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/actualise.py
# ── Version APRÈS ce commit.
+++ b/actualise.py
# ── Zone modifiée : ligne 115 (17 ligne(s)) dans l'ancienne version → ligne 115 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -115,17 +115,28 @@ def _relancer_en_enfant() -> None:
     subprocess.Popen(commande)
 
 
+_NOM_EXECUTABLE = "Actualise.exe"
+
+
 def _basculer_par_renommage(dossier_source: Path, destination: Path) -> None:
     """Bascule le contenu de ``dossier_source`` (dossier temporaire
     d'extraction) vers ``destination``, fichier par fichier, via
     renommage (``os.replace``) plutôt qu'une réécriture en place.
 
     Un ``.exe`` en cours d'exécution ne peut pas être réécrit en place
-    sous Windows (``PermissionError``), mais peut être renommé — voir
-    CONCEPTION.md, « Garde-fou anti-boucle infinie ». Toute ``OSError``
-    (ex. fichier encore verrouillé) remonte telle quelle à l'appelant,
-    qui décide de la marche à suivre (conservation du zip source pour
-    nouvelle tentative).
+    sous Windows (``PermissionError``/``WinError 5``, ``os.replace``
+    devant implicitement supprimer la destination avant d'y déplacer la
+    source) — voir CONCEPTION.md, « Garde-fou anti-boucle infinie ».
+    Cas particulier de ``_NOM_EXECUTABLE`` (``Actualise.exe``) : Windows
+    autorise en revanche de le *renommer* pendant qu'il tourne, d'où une
+    bascule en deux temps propre à ce fichier — renommage de l'exécutable
+    courant en ``Actualise.exe.old`` (nom alors libéré), puis déplacement
+    du nouvel exécutable vers ce nom libéré (simple déplacement, plus un
+    remplacement). Le reliquat ``.old`` est nettoyé au lancement suivant
+    par ``_nettoyer_ancien_executable``. Toute ``OSError`` (ex. fichier
+    encore verrouillé) remonte telle quelle à l'appelant, qui décide de
+    la marche à suivre (conservation du zip source pour nouvelle
+    tentative).
     """
     for chemin_source in dossier_source.rglob("*"):
         chemin_relatif = chemin_source.relative_to(dossier_source)
# ── Zone modifiée : ligne 134 (9 ligne(s)) dans l'ancienne version → ligne 145 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -134,9 +145,26 @@ def _basculer_par_renommage(dossier_source: Path, destination: Path) -> None:
             chemin_destination.mkdir(parents=True, exist_ok=True)
         else:
             chemin_destination.parent.mkdir(parents=True, exist_ok=True)
+            if chemin_destination.name == _NOM_EXECUTABLE and chemin_destination.exists():
+                chemin_destination.replace(chemin_destination.with_name(f"{_NOM_EXECUTABLE}.old"))
             os.replace(chemin_source, chemin_destination)
 
 
+def _nettoyer_ancien_executable() -> None:
+    """Supprime silencieusement le reliquat ``Actualise.exe.old`` laissé
+    par une bascule d'auto-mise-à-jour précédente, s'il existe.
+
+    Voir ``_basculer_par_renommage`` : le renommage préalable de
+    l'exécutable courant en ``.old`` (seule opération autorisée par
+    Windows sur un ``.exe`` en cours d'exécution) laisse ce fichier une
+    fois la bascule terminée. Il n'est plus verrouillé par personne dès
+    que ce nouveau lancement démarre : nettoyage au tout début du
+    lancement suivant.
+    """
+    chemin_ancien = config.chemin_config_portable() / f"{_NOM_EXECUTABLE}.old"
+    chemin_ancien.unlink(missing_ok=True)
+
+
 def appliquer_mises_a_jour_en_attente(est_enfant: bool) -> None:
     """Applique, au lancement, les mises à jour mises en attente au
     cycle précédent (étape 4 de la séquence de démarrage).
# ── Zone modifiée : ligne 377 (6 ligne(s)) dans l'ancienne version → ligne 405 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -377,6 +405,7 @@ def main(argv: list[str] | None = None) -> int:
     bloquante » pour le déroulé complet des étapes ci-dessous.
     """
     configurer_logging()
+    _nettoyer_ancien_executable()
 
     # Bloc englobant : sans lui, une exception non anticipée par les
     # except existants (ex. config.json absent dès le tout premier
# (diff du fichier suivant)
diff --git a/mise_a_jour.py b/mise_a_jour.py
# (index — ignorable)
index 6dafc27..ccbac2e 100644
# (avant — fichier suivant)
--- a/mise_a_jour.py
# (après — fichier suivant)
+++ b/mise_a_jour.py
# ── Zone modifiée : ligne 46 (6 ligne(s)) dans l'ancienne version → ligne 46 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -46,6 +46,7 @@ def telecharger_zip(url: str, sha256_attendu: str) -> Path | None:
                 fichier_temp.write(bloc)
     except requests.RequestException as erreur:
         _LOGGER.warning("Échec de téléchargement depuis %s : %s", url, erreur)
+        fichier_temp.close()
         chemin_temp.unlink(missing_ok=True)
         return None
 
