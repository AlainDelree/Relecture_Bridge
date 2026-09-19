## Nature du changement
Le bouton « Déconnexion » de `templates/index.html` (affiché uniquement si `auth_active`) voit son `onclick` passer de `location.href='/logout'` à `if(confirm('Se déconnecter ?')) location.href='/logout'`. Un fichier `CHANGELOG-575.md` documente l'incident et la correction. Aucune modification de style ni de logique serveur.

## Intention probable
Éviter les déconnexions accidentelles en mode `--externe` sur mobile, où le bouton se trouve sous le doigt lors de la fermeture du panneau Infrastructure, en ajoutant une confirmation annulable avant la navigation vers `/logout`.

## Points d'attention
- La confirmation est purement côté client : la route `/logout` reste accessible directement (URL, lien, script). Ce n'est pas une mesure de sécurité mais un simple garde-fou UX — à ne pas confondre avec une protection contre une déconnexion non désirée (ex. CSRF). Vérifier que `/logout` est bien protégée côté serveur si nécessaire.
- Le changelog mentionne un pattern identique pour le bouton « Quitter » (`quitter()` dans `static/js/*.js`) : s'assurer que la cohérence annoncée est réelle et que rien d'autre ne déclenche `/logout` sans confirmation.
