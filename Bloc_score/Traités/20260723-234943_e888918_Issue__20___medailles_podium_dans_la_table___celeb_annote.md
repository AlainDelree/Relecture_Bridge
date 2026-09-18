# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit e888918fc3335e42068bdf61f98a3faee1ff156b
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Thu Jul 23 23:49:43 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    Issue #20 : medailles podium dans la table + celebration renforcee (medaille + texte + anim, reduced-motion respecte) sur l'ecran de fin

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/bloc-jeu.html b/bloc-jeu.html
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6cdc50d..c630b6e 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/bloc-jeu.html
# ── Version APRÈS ce commit.
+++ b/bloc-jeu.html
# ── Zone modifiée : ligne 538 (6 ligne(s)) dans l'ancienne version → ligne 538 (44 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -538,6 +538,44 @@
     line-height:1;
     margin-bottom:22px;
   }
+  /* Célébration podium (rangs 1-3) sur l'écran de fin : médaille en grand + texte dédié.
+     Masquée par défaut, .show ajoutée par le JS quand le score du jour atteint le podium. */
+  .podium-celebration{
+    display:none;
+    margin-bottom:16px;
+  }
+  .podium-celebration.show{display:block;}
+  .podium-medal{
+    display:block;
+    font-size:76px;
+    line-height:1;
+    /* Entrée en rebond/rotation (même esprit que flourishPop/scoreBump) rejouée à chaque
+       affichage grâce au reflow forcé côté JS avant l'ajout de .show. */
+    animation:podiumPop 0.9s ease both;
+  }
+  .podium-text{
+    display:block;
+    font-family:'Fraunces', serif;
+    font-weight:900;
+    font-size:22px;
+    letter-spacing:0.01em;
+    color:var(--mustard);
+    margin-top:6px;
+  }
+  @media (max-width:380px){
+    .podium-medal{font-size:60px;}
+    .podium-text{font-size:19px;}
+  }
+  @keyframes podiumPop{
+    0%{opacity:0; transform:scale(0.3) rotate(-22deg);}
+    55%{opacity:1; transform:scale(1.25) rotate(9deg);}
+    75%{transform:scale(0.94) rotate(-4deg);}
+    100%{opacity:1; transform:scale(1) rotate(0deg);}
+  }
+  /* Accessibilité : médaille affichée instantanément, sans rebond/rotation */
+  @media (prefers-reduced-motion: reduce){
+    .podium-medal{animation:none;}
+  }
   .overlay button{
     background:var(--teal);
     color:var(--ink);
# ── Zone modifiée : ligne 644 (6 ligne(s)) dans l'ancienne version → ligne 682 (10 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -644,6 +682,10 @@
   <div class="card">
     <h2>Partie finie</h2>
     <p>Plus aucune des trois pièces ne rentre sur la grille.</p>
+    <div class="podium-celebration" id="podiumCeleb" aria-live="polite">
+      <span class="podium-medal" id="podiumMedal"></span>
+      <span class="podium-text" id="podiumText"></span>
+    </div>
     <div class="final-score" id="finalScore">0</div>
     <div class="top-list" id="finalTopList"></div>
     <div class="name-fix" id="nameFix">
# ── Zone modifiée : ligne 759 (6 ligne(s)) dans l'ancienne version → ligne 801 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -759,6 +801,7 @@
   let fileName = null;
   let playerName = '';     // nom courant du joueur (mémoire seule, pas de localStorage)
   let lastRecorded = null; // dernière entrée créée par recordScore() → surbrillance du jour
+  const PODIUM_MEDALS = ['🥇','🥈','🥉']; // médailles des rangs 1, 2, 3 (table + célébration)
 
   // --- persistance par dépôt GitHub (marche sur tous les navigateurs) ---
   const GH_OWNER = 'AlainDelree';
# ── Zone modifiée : ligne 1066 (7 ligne(s)) dans l'ancienne version → ligne 1109 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1066,7 +1109,8 @@
       }
       const place = document.createElement('td');
       place.className = 'rank';
-      place.textContent = (i+1)+'.';
+      // Podium (rangs 1-3) : médaille à la place du numéro ; rangs 4-10 : "4.", "5."...
+      place.textContent = i < 3 ? PODIUM_MEDALS[i] : (i+1)+'.';
       const nm = document.createElement('td');
       nm.className = 'name';
       nm.textContent = name;
# ── Zone modifiée : ligne 1160 (6 ligne(s)) dans l'ancienne version → ligne 1204 (9 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1160,6 +1204,9 @@
   const restartBtn = document.getElementById('restartBtn');
   const overlay = document.getElementById('overlay');
   const finalScoreEl = document.getElementById('finalScore');
+  const podiumCeleb = document.getElementById('podiumCeleb');
+  const podiumMedal = document.getElementById('podiumMedal');
+  const podiumText = document.getElementById('podiumText');
   const finalTopList = document.getElementById('finalTopList');
   const nameFix = document.getElementById('nameFix');
   const nameFixInput = document.getElementById('nameFixInput');
# ── Zone modifiée : ligne 1321 (6 ligne(s)) dans l'ancienne version → ligne 1368 (26 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1321,6 +1368,26 @@
     return false;
   }
 
+  // Célébration renforcée du podium sur l'écran de fin. Retrouve le rang (0-2) de
+  // lastRecorded dans topScores par score+date+nom (même logique que la surbrillance
+  // .current de renderTopList). Rang 1-3 → médaille en grand + texte dédié + animation
+  // d'entrée (rejouée via reflow forcé). Hors podium ou hors top 10 → rien de plus.
+  const PODIUM_TEXTS = ['NOUVEAU RECORD !', '2ème meilleur score !', '3ème meilleur score !'];
+  function celebratePodium(){
+    podiumCeleb.classList.remove('show');
+    if(!lastRecorded) return;
+    const name = lastRecorded.name || 'Anonyme';
+    const idx = topScores.findIndex(e =>
+      e.score === lastRecorded.score &&
+      e.date === lastRecorded.date &&
+      (e.name || 'Anonyme') === name);
+    if(idx < 0 || idx > 2) return;   // hors top 10, ou top 10 mais hors podium (rangs 4-10)
+    podiumMedal.textContent = PODIUM_MEDALS[idx];
+    podiumText.textContent = PODIUM_TEXTS[idx];
+    void podiumCeleb.offsetWidth;    // reflow → l'animation d'entrée rejoue à chaque game over
+    podiumCeleb.classList.add('show');
+  }
+
   function checkGameOver(){
     const remaining = tray.filter(p=>!p.used);
     const usable = remaining.length ? remaining : tray;
# ── Zone modifiée : ligne 1330 (6 ligne(s)) dans l'ancienne version → ligne 1397 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1330,6 +1397,7 @@
       finalScoreEl.textContent = score;
       recordScore(score);
       renderTopList(finalTopList, lastRecorded);
+      celebratePodium();
       offerNameFix();
       updateScores();
       updateReviveBtn();
