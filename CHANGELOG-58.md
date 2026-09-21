## Issue #58 — fetch_projets() doit se replier sur la résolution normale si le forçage IPv4 échoue

- `relecture_web/git_info.py` : extraction du téléchargement de
  `DOC_URL` dans `_telecharger_doc_projets(forcer_ipv4)`, réutilisable
  avec ou sans le monkeypatch IPv4 introduit par l'issue #57.
  `fetch_projets()` tente d'abord l'appel avec IPv4 forcé (rapide dans
  le cas normal) ; s'il échoue pour n'importe quelle raison (coupure
  réseau ponctuelle, IPv4 momentanément indisponible...), une seconde
  tentative est faite en résolution normale (IPv4 ou IPv6, au choix
  d'`urllib`) avant d'abandonner avec `ErreurRecuperationProjets`. Une
  perturbation réseau passagère ne provoque donc plus d'échec total du
  chargement de la liste des projets — au pire un chargement plus lent
  cette fois-là.
