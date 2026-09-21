## Issue #57 — fetch_projets() met 80s au lieu de 0,4s (résolution IPv6)

- `relecture_web/git_info.py` : `fetch_projets()` force désormais la
  résolution IPv4 le temps de l'appel `urlopen(DOC_URL)`, en remplaçant
  temporairement `socket.getaddrinfo` par une variante qui filtre sur
  `socket.AF_INET`, restaurée dans un `finally` juste après l'appel réseau.
  Corrige un ralentissement de 80s (4x `TIMEOUT_RESEAU`, retries IPv6 en
  série) à 0,2-0,4s, sans toucher aux commandes `git` (qui n'utilisent pas
  ce mécanisme) ni au reste de l'application.
