419126e

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 419126e
# ── Qui a fait ce commit.
Author: CCL agent <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sun Aug 9 13:53:29 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    avant-issue-401-refonte-niveaux-ia

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/resultats_avance_vs_cdm0_ods8.csv b/resultats_avance_vs_cdm0_ods8.csv
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 0000000..ff953ea
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- /dev/null
# ── Version APRÈS ce commit.
+++ b/resultats_avance_vs_cdm0_ods8.csv
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,51 @@
+graine,score_AVANCE,score_CHAMPION_DU_MONDE,vainqueur,a_commence,tours
+0,185,446,CHAMPION_DU_MONDE,AVANCE,36
+1,240,379,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,47
+2,167,405,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,33
+3,113,207,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,25
+4,150,188,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,22
+5,183,195,CHAMPION_DU_MONDE,AVANCE,41
+6,214,376,CHAMPION_DU_MONDE,AVANCE,44
+7,94,177,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,21
+8,136,312,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,33
+9,216,235,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,40
+10,165,348,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,41
+11,124,427,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,33
+12,200,212,CHAMPION_DU_MONDE,AVANCE,37
+13,207,371,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,37
+14,194,308,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,35
+15,184,295,CHAMPION_DU_MONDE,AVANCE,41
+16,125,178,CHAMPION_DU_MONDE,AVANCE,30
+17,105,195,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,19
+18,184,280,CHAMPION_DU_MONDE,AVANCE,36
+19,176,314,CHAMPION_DU_MONDE,AVANCE,36
+20,185,357,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,39
+21,168,266,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,43
+22,139,174,CHAMPION_DU_MONDE,AVANCE,27
+23,109,311,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,23
+24,239,337,CHAMPION_DU_MONDE,AVANCE,46
+25,318,405,CHAMPION_DU_MONDE,AVANCE,39
+26,133,251,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,35
+27,181,362,CHAMPION_DU_MONDE,AVANCE,36
+28,92,315,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,33
+29,156,295,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,43
+30,172,219,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,39
+31,186,328,CHAMPION_DU_MONDE,AVANCE,40
+32,219,339,CHAMPION_DU_MONDE,AVANCE,51
+33,138,292,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,29
+34,218,433,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,46
+35,187,315,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,38
+36,156,360,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,34
+37,136,209,CHAMPION_DU_MONDE,AVANCE,22
+38,297,405,CHAMPION_DU_MONDE,AVANCE,44
+39,113,198,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,24
+40,184,231,CHAMPION_DU_MONDE,AVANCE,42
+41,189,241,CHAMPION_DU_MONDE,AVANCE,35
+42,183,320,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,42
+43,144,340,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,35
+44,182,413,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,50
+45,147,340,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,38
+46,149,306,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,37
+47,231,248,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,40
+48,231,391,CHAMPION_DU_MONDE,AVANCE,44
+49,187,345,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,43
# (diff du fichier suivant)
diff --git a/resultats_avance_vs_cdm_ancien.csv b/resultats_avance_vs_cdm_ancien.csv
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..987aa74
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/resultats_avance_vs_cdm_ancien.csv
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,51 @@
+graine,score_AVANCE,score_CHAMPION_DU_MONDE[vocab=intermediaire],vainqueur,a_commence,tours
+0,206,207,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,41
+1,225,299,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],42
+2,103,227,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],28
+3,117,176,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],28
+4,174,227,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],30
+5,340,278,AVANCE,AVANCE,48
+6,235,179,AVANCE,AVANCE,32
+7,212,295,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],48
+8,289,222,AVANCE,CHAMPION_DU_MONDE[vocab=intermediaire],47
+9,182,126,AVANCE,CHAMPION_DU_MONDE[vocab=intermediaire],29
+10,168,176,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],22
+11,121,249,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],22
+12,192,206,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,35
+13,68,145,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],19
+14,170,285,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],31
+15,211,188,AVANCE,AVANCE,37
+16,229,327,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,42
+17,200,271,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],39
+18,161,209,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,37
+19,92,146,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,21
+20,290,269,AVANCE,CHAMPION_DU_MONDE[vocab=intermediaire],44
+21,220,229,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],43
+22,114,191,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,26
+23,173,164,AVANCE,CHAMPION_DU_MONDE[vocab=intermediaire],26
+24,201,199,AVANCE,AVANCE,37
+25,164,336,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,42
+26,309,227,AVANCE,CHAMPION_DU_MONDE[vocab=intermediaire],40
+27,164,176,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,35
+28,211,233,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],43
+29,215,293,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],42
+30,118,157,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],30
+31,173,218,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,35
+32,182,175,AVANCE,AVANCE,38
+33,244,302,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],47
+34,142,216,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],36
+35,239,293,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],43
+36,122,227,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],36
+37,175,107,AVANCE,AVANCE,26
+38,278,339,CHAMPION_DU_MONDE[vocab=intermediaire],AVANCE,46
+39,249,243,AVANCE,CHAMPION_DU_MONDE[vocab=intermediaire],45
+40,286,188,AVANCE,AVANCE,43
+41,182,139,AVANCE,AVANCE,25
+42,183,233,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],38
+43,257,244,AVANCE,CHAMPION_DU_MONDE[vocab=intermediaire],42
+44,79,92,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],17
+45,161,247,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],41
+46,207,235,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],44
+47,116,227,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],31
+48,277,265,AVANCE,AVANCE,48
+49,206,327,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],42
# (diff du fichier suivant)
diff --git a/resultats_expert_vs_cdm_ancien.csv b/resultats_expert_vs_cdm_ancien.csv
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..700f6cc
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/resultats_expert_vs_cdm_ancien.csv
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,51 @@
+graine,score_EXPERT,score_CHAMPION_DU_MONDE[vocab=intermediaire],vainqueur,a_commence,tours
+0,283,211,EXPERT,EXPERT,36
+1,281,280,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],38
+2,238,248,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],25
+3,160,107,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],21
+4,169,172,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],26
+5,336,202,EXPERT,EXPERT,47
+6,321,306,EXPERT,EXPERT,46
+7,181,292,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],39
+8,222,153,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],24
+9,246,233,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],36
+10,272,373,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],43
+11,223,206,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],30
+12,284,176,EXPERT,EXPERT,36
+13,241,299,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],46
+14,152,171,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],29
+15,199,150,EXPERT,EXPERT,26
+16,166,166,nul,EXPERT,30
+17,294,240,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],53
+18,278,189,EXPERT,EXPERT,41
+19,205,152,EXPERT,EXPERT,29
+20,332,235,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],39
+21,159,163,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],28
+22,234,214,EXPERT,EXPERT,39
+23,172,174,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],25
+24,113,139,CHAMPION_DU_MONDE[vocab=intermediaire],EXPERT,22
+25,113,152,CHAMPION_DU_MONDE[vocab=intermediaire],EXPERT,21
+26,252,234,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],35
+27,210,216,CHAMPION_DU_MONDE[vocab=intermediaire],EXPERT,37
+28,362,179,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],38
+29,195,265,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],32
+30,185,233,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],29
+31,220,202,EXPERT,EXPERT,36
+32,114,162,CHAMPION_DU_MONDE[vocab=intermediaire],EXPERT,20
+33,225,359,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],45
+34,437,271,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],36
+35,245,341,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],45
+36,275,212,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],35
+37,145,92,EXPERT,EXPERT,23
+38,231,240,CHAMPION_DU_MONDE[vocab=intermediaire],EXPERT,30
+39,327,280,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],40
+40,308,174,EXPERT,EXPERT,35
+41,228,107,EXPERT,EXPERT,25
+42,252,170,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],40
+43,376,174,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],32
+44,240,310,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],51
+45,359,216,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],44
+46,282,185,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],32
+47,243,169,EXPERT,CHAMPION_DU_MONDE[vocab=intermediaire],33
+48,272,227,EXPERT,EXPERT,39
+49,170,201,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],27
# (diff du fichier suivant)
diff --git a/resultats_intermediaire_vs_cdm0_ods8.csv b/resultats_intermediaire_vs_cdm0_ods8.csv
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..d162ba7
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/resultats_intermediaire_vs_cdm0_ods8.csv
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,51 @@
+graine,score_INTERMEDIAIRE,score_CHAMPION_DU_MONDE,vainqueur,a_commence,tours
+0,87,204,CHAMPION_DU_MONDE,INTERMEDIAIRE,28
+1,190,254,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,43
+2,152,356,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,35
+3,127,435,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,51
+4,163,401,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,44
+5,177,364,CHAMPION_DU_MONDE,INTERMEDIAIRE,41
+6,132,298,CHAMPION_DU_MONDE,INTERMEDIAIRE,34
+7,204,383,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,50
+8,153,358,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,43
+9,47,158,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,18
+10,155,473,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,45
+11,188,491,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,49
+12,149,444,CHAMPION_DU_MONDE,INTERMEDIAIRE,46
+13,105,278,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,35
+14,198,299,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,47
+15,95,198,CHAMPION_DU_MONDE,INTERMEDIAIRE,26
+16,189,316,CHAMPION_DU_MONDE,INTERMEDIAIRE,42
+17,217,353,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,45
+18,99,252,CHAMPION_DU_MONDE,INTERMEDIAIRE,33
+19,210,298,CHAMPION_DU_MONDE,INTERMEDIAIRE,40
+20,127,382,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,47
+21,196,291,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,49
+22,133,308,CHAMPION_DU_MONDE,INTERMEDIAIRE,34
+23,169,368,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,42
+24,270,352,CHAMPION_DU_MONDE,INTERMEDIAIRE,41
+25,64,182,CHAMPION_DU_MONDE,INTERMEDIAIRE,21
+26,137,357,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,42
+27,167,403,CHAMPION_DU_MONDE,INTERMEDIAIRE,40
+28,187,344,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,43
+29,193,390,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,47
+30,114,187,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,26
+31,171,311,CHAMPION_DU_MONDE,INTERMEDIAIRE,35
+32,169,351,CHAMPION_DU_MONDE,INTERMEDIAIRE,44
+33,105,262,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,29
+34,177,475,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,41
+35,238,357,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,44
+36,178,430,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,47
+37,86,204,CHAMPION_DU_MONDE,INTERMEDIAIRE,20
+38,224,456,CHAMPION_DU_MONDE,INTERMEDIAIRE,52
+39,158,306,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,46
+40,121,293,CHAMPION_DU_MONDE,INTERMEDIAIRE,47
+41,142,261,CHAMPION_DU_MONDE,INTERMEDIAIRE,36
+42,213,366,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,46
+43,205,471,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,41
+44,81,211,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,25
+45,54,293,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,31
+46,122,300,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,41
+47,244,359,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,48
+48,173,297,CHAMPION_DU_MONDE,INTERMEDIAIRE,41
+49,138,261,CHAMPION_DU_MONDE,CHAMPION_DU_MONDE,41
# (diff du fichier suivant)
diff --git a/resultats_intermediaire_vs_cdm_ancien.csv b/resultats_intermediaire_vs_cdm_ancien.csv
# ── Ce fichier n'existait pas avant ce commit : il vient d'être créé.
new file mode 100644
# (index — ignorable)
index 0000000..fd24a7b
# (avant — fichier suivant)
--- /dev/null
# (après — fichier suivant)
+++ b/resultats_intermediaire_vs_cdm_ancien.csv
# ── Zone modifiée : ligne 0 (0 ligne(s)) dans l'ancienne version → ligne 1 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -0,0 +1,51 @@
+graine,score_INTERMEDIAIRE,score_CHAMPION_DU_MONDE[vocab=intermediaire],vainqueur,a_commence,tours
+0,170,305,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,45
+1,204,228,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],42
+2,180,263,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],36
+3,94,193,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],27
+4,116,215,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],21
+5,156,239,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,36
+6,129,253,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,29
+7,151,206,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],30
+8,206,294,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],49
+9,153,199,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],30
+10,159,228,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],37
+11,139,169,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],27
+12,209,293,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,45
+13,97,156,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],29
+14,193,177,INTERMEDIAIRE,CHAMPION_DU_MONDE[vocab=intermediaire],44
+15,208,263,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,42
+16,163,216,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,38
+17,124,307,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],53
+18,139,186,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,36
+19,195,241,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,44
+20,108,221,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],35
+21,213,269,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],52
+22,105,185,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,32
+23,124,221,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],31
+24,264,309,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,47
+25,154,184,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,41
+26,102,223,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],31
+27,136,263,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,35
+28,90,146,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],25
+29,128,351,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],32
+30,146,221,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],34
+31,175,256,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,55
+32,105,255,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,28
+33,147,150,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],37
+34,109,177,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],26
+35,133,173,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],32
+36,227,411,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],45
+37,66,118,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,20
+38,166,292,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,31
+39,71,185,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],25
+40,178,201,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,53
+41,144,127,INTERMEDIAIRE,INTERMEDIAIRE,23
+42,218,213,INTERMEDIAIRE,CHAMPION_DU_MONDE[vocab=intermediaire],54
+43,111,219,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],37
+44,75,110,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],20
+45,183,288,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],45
+46,129,201,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],40
+47,112,218,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],36
+48,174,201,CHAMPION_DU_MONDE[vocab=intermediaire],INTERMEDIAIRE,35
+49,79,178,CHAMPION_DU_MONDE[vocab=intermediaire],CHAMPION_DU_MONDE[vocab=intermediaire],32
