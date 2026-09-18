## Nature du changement
Ajout d'une ligne pour le projet `relecture_bridge` (dépôt AlainDelree/Relecture_Bridge, chemin ~/Relecture_Bridge) dans deux tableaux de `BRIDGE_AGENT_DOC.md` : le tableau des projets actifs (§2) et celui du périmètre des projets (§7). Aucune modification de code, uniquement de la documentation générée.

## Intention probable
Régénérer les tableaux de documentation pour refléter un fichier `.conf` créé après le dernier passage du script de génération, comme l'indique le message de commit.

## Points d'attention
- Le changement est présenté comme une régénération automatique depuis les fichiers `configs/*.conf` : vérifier que les deux tableaux ont bien été régénérés par le script et non édités à la main, pour rester cohérent avec le commit précédent (#571) qui portait sur cette même génération.
- S'assurer que le dépôt `AlainDelree/Relecture_Bridge` et le fichier `.conf` correspondant existent réellement, l'entrée étant ajoutée manuellement à la doc.
