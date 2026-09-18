631a301

# ── Identifiant unique de ce commit (hash SHA). Sert à le retrouver précisément (ex. `git show <hash>`).
commit 631a301
# ── Qui a fait ce commit.
Author: Athanatos123 <alain.delree@gmail.com>
# ── Quand ce commit a été fait.
Date:   Sat Aug 15 13:45:46 2026 +0200

# ── Message de commit : résumé de l'intention du changement, écrit par celui qui a committé.
    fix: Opening Explorer — prompt LLM pro, accès sans plateau, notation parlée FR (issue #157)
    
    - game_manager.py : explorer_load() bascule sur VirtualBoard si aucun
      échiquier physique n'est détecté, au lieu de bloquer l'accès (comme
      outils_exercices/parametres).
    - llm_explainer.py : prompts système FR/EN/DE réécrits (ton direct,
      factuel, sans flatterie ni titre ni émoji, sans accroche sur le nom
      de l'ouverture).
    - tts_engine.py : ajout san_to_spoken_fr() (Cc3 → "Cavalier en c3",
      exd5 → "pion prend en d5", roques, promotions, prises), appliquée
      dans speak() pour le français.
    - data/explorer_cache.json vidé pour régénérer les anciennes
      explications flatteuses avec le nouveau prompt.

# ── Début du diff pour CE fichier précis. a/ = version avant, b/ = version après (identiques si le fichier n'a pas été renommé).
diff --git a/nicsoft/core/game_manager.py b/nicsoft/core/game_manager.py
# ── Identifiants internes git (hash du contenu avant/après). Sans intérêt au quotidien, ignorable.
index 6c0266f..0c42d01 100644
# ── Version AVANT ce commit (/dev/null = le fichier n'existait pas).
--- a/nicsoft/core/game_manager.py
# ── Version APRÈS ce commit.
+++ b/nicsoft/core/game_manager.py
# ── Zone modifiée : ligne 1116 (14 ligne(s)) dans l'ancienne version → ligne 1116 (15 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -1116,14 +1116,15 @@ def explorer_load(source_type: str, opening_id: str, variant_index=None) -> dict
         book_path = str(book_candidate if book_candidate and book_candidate.exists() else BOOK_DEFAULT)
         source = PolyglotSource(ouverture, book_path)
 
+    used_virtual = _virtual_mode
     try:
         nl_inst = create_board(virtual=_virtual_mode, logger_name="NicLink_explorer")
     except Exception as e:
-        logger.error(f"[EXPLORER] Échiquier non détecté : {e}")
-        send_event("board_error", {"message": "Échiquier non détecté — vérifiez l'USB et allumez le plateau."})
-        return {"error": "Échiquier non détecté."}
+        logger.info(f"[EXPLORER] Échiquier physique indisponible, bascule en mode virtuel : {e}")
+        nl_inst = create_board(virtual=True, logger_name="NicLink_explorer")
+        used_virtual = True
 
-    if _virtual_mode:
+    if used_virtual:
         set_virtual_board(nl_inst)
     _explorer_nl_inst = nl_inst
 
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/llm_explainer.py b/nicsoft/modes/opening_explorer/llm_explainer.py
# (index — ignorable)
index 748cc94..3de82ea 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/opening_explorer/llm_explainer.py
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/llm_explainer.py
# ── Zone modifiée : ligne 42 (23 ligne(s)) dans l'ancienne version → ligne 42 (28 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -42,23 +42,28 @@ _ARROWS_INSTRUCTION = {
 
 _SYSTEM_PROMPTS = {
     "fr": (
-        "Tu es un entraîneur d'échecs pédagogue. Explique les coups d'une "
-        "ouverture à un joueur débutant. Sois concis (3-4 phrases maximum), "
-        "clair et encourageant. Réponds uniquement en français. "
-        "Utilise toujours les termes français : Blancs (jamais White), "
-        "Noirs (jamais Black), cavalier, fou, tour, dame, roi."
+        "Tu es un entraîneur d'échecs. Explique les coups d'une ouverture à "
+        "un joueur débutant en 2-3 phrases maximum. Sois direct et factuel, "
+        "sans flatterie, sans titre, sans émoji. Ne commence pas par le nom "
+        "de l'ouverture ni par une formule d'accroche. Utilise les termes "
+        "français : Blancs, Noirs, cavalier, fou, tour, dame, roi. Réponds "
+        "uniquement en français."
         + _ARROWS_INSTRUCTION["fr"]
     ),
     "en": (
-        "You are a friendly chess coach. Explain opening moves to a "
-        "beginner player. Be concise (3-4 sentences maximum), clear and "
-        "encouraging. Answer only in English."
+        "You are a chess coach. Explain the moves of an opening to a "
+        "beginner player in 2-3 sentences maximum. Be direct and factual, "
+        "without flattery, without a title, without emoji. Do not start "
+        "with the name of the opening or a catchy opening line. Answer "
+        "only in English."
         + _ARROWS_INSTRUCTION["en"]
     ),
     "de": (
-        "Du bist ein pädagogischer Schachtrainer. Erkläre die Züge einer "
-        "Eröffnung einem Anfänger. Sei prägnant (maximal 3-4 Sätze), klar "
-        "und ermutigend. Antworte ausschließlich auf Deutsch."
+        "Du bist ein Schachtrainer. Erkläre die Züge einer Eröffnung einem "
+        "Anfänger in maximal 2-3 Sätzen. Sei direkt und sachlich, ohne "
+        "Schmeicheleien, ohne Titel, ohne Emoji. Beginne nicht mit dem "
+        "Namen der Eröffnung oder einer einleitenden Floskel. Antworte "
+        "ausschließlich auf Deutsch."
         + _ARROWS_INSTRUCTION["de"]
     ),
 }
# (diff du fichier suivant)
diff --git a/nicsoft/modes/opening_explorer/tts_engine.py b/nicsoft/modes/opening_explorer/tts_engine.py
# (index — ignorable)
index 3d9e78a..ea94f7b 100644
# (avant — fichier suivant)
--- a/nicsoft/modes/opening_explorer/tts_engine.py
# (après — fichier suivant)
+++ b/nicsoft/modes/opening_explorer/tts_engine.py
# ── Zone modifiée : ligne 13 (6 ligne(s)) dans l'ancienne version → ligne 13 (7 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -13,6 +13,7 @@ provoquant des ReferenceError après un ou deux mots.
 import asyncio
 import logging
 import os
+import re
 import subprocess
 import tempfile
 
# ── Zone modifiée : ligne 26 (10 ligne(s)) dans l'ancienne version → ligne 27 (51 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -26,10 +27,51 @@ VOICE_MAP_EDGE = {
 }
 VOICE_MAP_ESPEAK = {"fr": "fr", "en": "en", "de": "de"}
 
+PIECES_FR = {
+    'N': 'Cavalier', 'C': 'Cavalier',
+    'B': 'Fou',      'F': 'Fou',
+    'R': 'Tour',     'T': 'Tour',
+    'Q': 'Dame',     'D': 'Dame',
+    'K': 'Roi',
+}
+
+_SAN_MOVE_RE = re.compile(r'\b([NBRKQCDFDT]?[a-h]?[1-8]?x?[a-h][1-8](?:=[NBRQKCDFDT])?[+#]?)\b')
+
+
+def san_to_spoken_fr(san: str) -> str:
+    """Convertit une notation SAN (ex. Cc3, Nc3, exd5, e8=Q) en texte parlé français."""
+    san = san.strip()
+    if san in ('O-O-O', '0-0-0'):
+        return 'grand roque'
+    if san in ('O-O', '0-0'):
+        return 'petit roque'
+    san_clean = re.sub(r'[+#!?]', '', san)
+    ep = ' en passant' if san_clean.endswith('e.p.') else ''
+    san_clean = san_clean.replace('e.p.', '').strip()
+    promo = ''
+    promo_match = re.search(r'=([NBRQKCDFDT])', san_clean)
+    if promo_match:
+        promo = ' promotion en ' + PIECES_FR.get(promo_match.group(1), '')
+        san_clean = san_clean[:promo_match.start()]
+    takes = 'x' in san_clean
+    san_clean = san_clean.replace('x', '')
+    piece = ''
+    if san_clean and san_clean[0].upper() in PIECES_FR:
+        piece = PIECES_FR[san_clean[0].upper()]
+        san_clean = san_clean[1:]
+    dest = san_clean[-2:] if len(san_clean) >= 2 else san_clean
+    if piece:
+        if takes:
+            return f'{piece} prend en {dest}{promo}{ep}'
+        return f'{piece} en {dest}{promo}{ep}'
+    else:
+        if takes:
+            return f'pion prend en {dest}{promo}{ep}'
+        return f'{dest}{promo}{ep}'
+
 
 def strip_markdown(text: str) -> str:
     """Retire les marqueurs Markdown (titres, gras, italique) avant lecture TTS."""
-    import re
     text = re.sub(r'#{1,6}\s*', '', text)
     text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
     text = re.sub(r'__(.+?)__', r'\1', text)
# ── Zone modifiée : ligne 109 (6 ligne(s)) dans l'ancienne version → ligne 151 (8 ligne(s)) dans la nouvelle. Une ligne '+' = ajoutée, '-' = supprimée, sans signe = contexte inchangé.
@@ -109,6 +151,8 @@ def speak(text: str, rate: int = 150, enabled: bool = False, language: str = "fr
     côté navigateur (pas d'espeak-ng comme fallback serveur).
     """
     text = strip_markdown(text)
+    if language == "fr" and text:
+        text = _SAN_MOVE_RE.sub(lambda m: san_to_spoken_fr(m.group(1)), text)
     if not enabled or not text:
         return False
     if not check_internet():
