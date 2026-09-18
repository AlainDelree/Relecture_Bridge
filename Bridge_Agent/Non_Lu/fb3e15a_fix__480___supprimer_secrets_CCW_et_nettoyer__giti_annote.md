fb3e15a

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit fb3e15a
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Tue Aug 25 10:13:19 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix #480 : supprimer secrets CCW et nettoyer .gitignore
    
    - Suppression de configs/ccw_admin.secret et configs/ccw_ssh.conf (jamais
      suivis par git, uniquement présents sur disque).
    - Notes_Perso.md déjà déplacé vers ~/Document_Projet/Bridge_Agent/ avant
      cette issue (jamais suivi par git non plus) : rien à faire côté dépôt,
      le script deplacer_docs_travail.sh demandé par l'issue n'existe pas dans
      ce dépôt et sa destination est hors périmètre CCL.
    - .gitignore : retrait de la ligne Notes_Perso.md et de la ligne+commentaire
      configs/ccw_admin.secret. Le motif générique configs/*.conf est conservé
      (il couvre aussi ccw_ssh.conf) car il ignore aussi les .conf des autres
      projets — le retirer les aurait exposés à tort.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/.gitignore b/.gitignore
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index cbf323a..b8749fe 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/.gitignore
# ── Version APRÈS ce commit.
+++ b/.gitignore
# ── Zone modifiée : ligne 4 (14 ligne(s)) dans l'ancienne version → ligne 4 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -4,14 +4,10 @@ configs/*.conf
 __pycache__/
 *.pyc
 venv/
-Notes_Perso.md
 ssl/
 # Copie locale d'autounattend.xml avec le vrai mot de passe (placeholder
 # remplacé) — ne doit JAMAIS être committée. Cf. en-tête d'autounattend.xml.
 provisioning/windows/autounattend.local.xml
-# Mot de passe ccw-admin lu par l'onglet CCW (issue #174) si CCW_ADMIN_PASSWORD
-# n'est pas dans l'environnement — ne doit JAMAIS être committé.
-configs/ccw_admin.secret
 # Bibliothèque de templates d'issues récurrentes par projet (issue #284) :
 # état de formulaire local, pas du code — jamais committé.
 configs/templates_*.json
