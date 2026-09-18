b202e79

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit b202e79
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Jul 26 08:09:24 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Dérive le libellé d'agent de l'ACK de la configuration (issue #239)
    
    L'ACK affichait « agent Linux » en dur, ce qui trompe le diagnostic
    quand c'est le watcher CCW (Windows) qui traite l'issue (constaté sur
    #236). watcher.py tournant tel quel sur les deux plateformes, le
    libellé est désormais déduit de platform.system() (agent Linux /
    agent Windows), avec repli inchangé pour les .conf existants. Nouveau
    champ optionnel LIBELLE_AGENT pour forcer une valeur explicite si la
    détection ne convient pas.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/BRIDGE_AGENT_DOC.md b/BRIDGE_AGENT_DOC.md
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index eab1813..f282dc5 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/BRIDGE_AGENT_DOC.md
# ── Version APRÈS ce commit.
+++ b/BRIDGE_AGENT_DOC.md
# ── Zone modifiée : ligne 715 (8 ligne(s)) dans l'ancienne version → ligne 715 (23 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -715,8 +715,23 @@ de l'expiration — à activer par Alain s'il le souhaite (cf. proposition issue
 Windows installé (pas encore exécuté contre une VM réelle). À noter :
 `watcher.py` n'a nécessité **aucune modification** — il est déjà portable et
 son `LABEL` est paramétrable par config, donc `LABEL=for-windows` dans
-`ccw.conf` suffit à ce qu'il ne prenne que les issues Windows. Le watcher
-tourne comme **vrai service Windows** enregistré via NSSM (issue #148) —
+`ccw.conf` suffit à ce qu'il ne prenne que les issues Windows.
+
+**Libellé d'agent dans l'ACK (issue #239).** Le message d'ACK posté à la
+réception d'une issue (`✅ ACK — Issue #N reçue par watcher.py (…, projet
+<nom>)`) affiche un libellé d'agent déduit automatiquement de la plateforme
+(`platform.system()`) : « agent Linux » côté CCL, « agent Windows » côté CCW.
+Aucune action requise sur les `.conf` existants (repli inchangé). Champ
+optionnel `LIBELLE_AGENT` disponible dans n'importe quel `.conf` pour forcer
+un libellé explicite si la détection automatique ne convient pas (ex.
+exécution dans un conteneur ou un environnement où `platform.system()` ne
+reflète pas l'agent réel) :
+
+```
+LIBELLE_AGENT = agent Windows
+```
+
+Le watcher tourne comme **vrai service Windows** enregistré via NSSM (issue #148) —
 équivalent direct des services systemd du §13 : démarrage au boot **sans
 session ouverte** (`SERVICE_AUTO_START`) et redémarrage automatique sur
 échec (`AppExit Default Restart` + `AppRestartDelay 5000`), sous LocalSystem
# (diff du fichier suivant)
diff --git a/watcher.py b/watcher.py
# (index — ignorable)
index 9420220..c092d17 100644
# (avant — fichier suivant)
--- a/watcher.py
# (après — fichier suivant)
+++ b/watcher.py
# ── Zone modifiée : ligne 25 (6 ligne(s)) dans l'ancienne version → ligne 25 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -25,6 +25,7 @@ import glob
 import re
 import hashlib
 import tempfile
+import platform
 from logging.handlers import RotatingFileHandler
 from dataclasses import dataclass, field
 from pathlib import Path
# ── Zone modifiée : ligne 190 (6 ligne(s)) dans l'ancienne version → ligne 191 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -190,6 +191,7 @@ class Config:
     perimetre_dynamique: bool = False  # périmètre fourni par l'issue (REPO_CIBLE) plutôt que figé dans le .conf — outil d'audit multi-dépôts (issue #125)
     notifier_local: bool   = True  # ce watcher émet-il lui-même bip/notify-send/ntfy à la fin d'une issue (issue #187) ? True = comportement historique. Mettre à False sur la VM CCW (et éventuellement CCL) pour laisser new_issue.py notifier de façon centralisée sur le ThinkPad, sans doublon.
     delai_inactivite_min: int = 20  # auto-extinction : minutes sans aucune issue traitable avant que le watcher ne s'arrête proprement (issue #200). 0 = désactivé (le watcher tourne indéfiniment, comportement historique).
+    libelle_agent: str     = ""    # libellé de l'agent affiché dans l'ACK (ex. "agent Linux", "agent Windows") — vide = déduit automatiquement de la plateforme (issue #239)
 
     @property
     def url_ntfy(self) -> str:
# ── Zone modifiée : ligne 199 (6 ligne(s)) dans l'ancienne version → ligne 201 (17 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -199,6 +201,17 @@ class Config:
     def fichier_log(self) -> Path:
         return DOSSIER_LOGS / f"watcher-{self.nom}.log"
 
+    @property
+    def libelle_agent_effectif(self) -> str:
+        """Libellé d'agent à afficher dans l'ACK. Priorité : LIBELLE_AGENT du
+        .conf s'il est déclaré, sinon détection de plateforme (issue #239) —
+        un même watcher.py tourne sur CCL (Linux) et CCW (Windows), et le
+        libellé doit refléter la machine qui a réellement traité l'issue plutôt
+        qu'un texte figé "agent Linux" trompeur côté Windows."""
+        if self.libelle_agent:
+            return self.libelle_agent
+        return "agent Windows" if platform.system() == "Windows" else "agent Linux"
+
 
 CHAMPS_REQUIS = ("NOM", "DEPOT", "REP_TRAVAIL", "TOPIC_NTFY")
 
# ── Zone modifiée : ligne 270 (6 ligne(s)) dans l'ancienne version → ligne 283 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -270,6 +283,7 @@ def charger_config(chemin: Path) -> Config:
         perimetre_dynamique = booleen("PERIMETRE_DYNAMIQUE", False),
         notifier_local      = booleen("NOTIFIER_LOCAL", True),
         delai_inactivite_min = entier("DELAI_INACTIVITE_MIN", 20),
+        libelle_agent       = brut.get("LIBELLE_AGENT", ""),
     )
 
 
# ── Zone modifiée : ligne 1935 (7 ligne(s)) dans l'ancienne version → ligne 1949 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1935,7 +1949,7 @@ def traiter_issue(issue: dict, dry_run: bool):
     try:
         commenter_issue(
             numero,
-            f"✅ ACK — Issue #{numero} reçue par watcher.py (agent Linux, projet {CFG.nom}). "
+            f"✅ ACK — Issue #{numero} reçue par watcher.py ({CFG.libelle_agent_effectif}, projet {CFG.nom}). "
             f"Mode : **{mode_txt}**. Traitement en cours..."
         )
         # Départ du chrono de durée réelle (ACK → fermeture), pour l'historique des
