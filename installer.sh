#!/bin/bash
# Installe le hook post-commit sur tous les projets actifs Bridge_Agent
# (liste tirée du §2 de BRIDGE_AGENT_DOC.md — à ajuster si la liste évolue)
#
# Usage : ./installer.sh
# (le hook post-commit doit être dans le même dossier que ce script)

set -e

DOSSIER_SCRIPT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK_SOURCE="$DOSSIER_SCRIPT/post-commit"
ANNOTATION_SOURCE="$DOSSIER_SCRIPT/annoter_diff.py"

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "Erreur : post-commit introuvable dans $DOSSIER_SCRIPT"
    exit 1
fi

# Déploiement du script d'annotation (partagé, une seule copie pour tous les projets)
if [ -f "$ANNOTATION_SOURCE" ]; then
    mkdir -p "$HOME/.config/relecture-bridge"
    cp "$ANNOTATION_SOURCE" "$HOME/.config/relecture-bridge/annoter_diff.py"
    echo "✓ Script d'annotation installé dans ~/.config/relecture-bridge/"
    echo "  (pour le désactiver plus tard : touch ~/.config/relecture-bridge/desactiver-annotation)"
    echo ""
else
    echo "⚠ annoter_diff.py introuvable — les diffs seront exportés sans annotation."
    echo ""
fi

PROJETS=(
    "$HOME/Bridge_Agent"
    "$HOME/NicLink"
    "$HOME/FF_Galerie"
    "$HOME/Ecole"
    "$HOME/Scrabble"
    "$HOME/Diagnostique_Programme"
    "$HOME/Actualise"
    "$HOME/Bloc_score"
)

for projet in "${PROJETS[@]}"; do
    if [ -d "$projet/.git" ]; then
        cp "$HOOK_SOURCE" "$projet/.git/hooks/post-commit"
        chmod +x "$projet/.git/hooks/post-commit"
        echo "✓ Hook installé sur $projet"
    else
        echo "⚠ Ignoré (pas un dépôt git) : $projet"
    fi
done

echo ""
echo "Terminé. Les diffs de chaque futur commit apparaîtront dans ~/Relecture_Bridge/<projet>/"
