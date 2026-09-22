## 2026-09-22 — issue #62 (relecture_web)

- Journalisation persistante des tentatives de fusion automatique du
  CHANGELOG (déclenchée après un merge, issue #51) : jusqu'ici, le
  résultat (succès/échec) n'était visible que via un message flash
  éphémère, affiché une seule fois juste après l'action — vécu
  concrètement quand Alain a mergé deux branches sur `bridge_agent`
  depuis `relecture_web` sans repérer le détail du message, sans moyen
  après coup de confirmer si la fusion automatique avait réellement
  réussi.
  - `git_info.py` : nouveau fichier de log `relecture_web/changelog_fusion.log`
    (non commité, voir `.gitignore`), une ligne par tentative réellement
    lancée (script trouvé ou non) — date/heure ISO, projet, commande
    exécutée, résultat (`SUCCES`/`ECHEC`), message d'erreur le cas
    échéant. Écrite par la nouvelle fonction `_journaliser_fusion_changelog`,
    appelée depuis `fusionner_changelog_worktree` (qui accepte maintenant
    un paramètre optionnel `nom_projet`). Une erreur d'écriture du journal
    reste silencieuse pour l'utilisateur — elle ne doit jamais faire
    échouer la fusion elle-même.
  - `fusionner_worktree` propage `nom_projet` jusqu'à
    `fusionner_changelog_worktree` ; `app.py` passe `projet["nom"]` lors de
    l'appel dans `merger_branches_route`.
  - `RELECTURE_WEB_DOC.md` (section 9, ligne **Merger** du tableau des
    actions) mise à jour en conséquence.
