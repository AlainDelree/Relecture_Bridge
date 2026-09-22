## Nature du changement
Modification du fichier `fichier_test_defilement.txt` : trois blocs de 6 lignes (lignes 10-15, 70-75 et 140-145) passent de « contenu original » à « contenu version B ». Aucune logique applicative touchée, il s'agit uniquement de contenu texte de test.

## Intention probable
Le message « Version B : trois zones modifiées » indique qu'il s'agit de préparer un scénario de test, probablement pour exercer un cas de conflit ou de fusion sur plusieurs zones distinctes du même fichier.

## Points d'attention
- Ce commit modifie trois zones distinctes du même fichier : sur la branche `branche_test_conflit`, une fusion avec une « Version A » ou une autre variante concurrente générera très probablement des conflits sur ces trois emplacements, à résoudre dans le bon ordre.
- Aucun secret, identifiant ou code de sécurité n'est concerné.
