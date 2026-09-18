#!/bin/bash
# Installe le hook post-commit sur tous les projets actifs Bridge_Agent
# (liste récupérée dynamiquement depuis le tableau §2 de BRIDGE_AGENT_DOC.md
# — colonne « Répertoire de travail CCL » — plutôt que codée en dur ici)
#
# Usage : ./installer.sh
# (le hook post-commit doit être dans le même dossier que ce script)

set -e

DOSSIER_SCRIPT=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
HOOK_SOURCE="$DOSSIER_SCRIPT/post-commit"
RESUME_SOURCE="$DOSSIER_SCRIPT/resumer_diff.py"
DOC_URL="https://raw.githubusercontent.com/AlainDelree/Bridge_Agent/master/BRIDGE_AGENT_DOC.md"

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "Erreur : post-commit introuvable dans $DOSSIER_SCRIPT"
    exit 1
fi

# Déploiement du script de résumé (partagé, une seule copie pour tous les projets)
if [ -f "$RESUME_SOURCE" ]; then
    mkdir -p "$HOME/.config/relecture-bridge"
    cp "$RESUME_SOURCE" "$HOME/.config/relecture-bridge/resumer_diff.py"
    echo "✓ Script de résumé installé dans ~/.config/relecture-bridge/"
    echo "  (pour le désactiver plus tard : touch ~/.config/relecture-bridge/desactiver-resume)"
    echo ""
else
    echo "⚠ resumer_diff.py introuvable — les diffs seront exportés sans résumé."
    echo ""
fi

# Récupération de la liste des projets actifs depuis BRIDGE_AGENT_DOC.md
# (tableau §2, colonne « Répertoire de travail CCL »), au lieu d'une liste
# codée en dur — un nouveau projet ajouté à la doc est ainsi couvert sans
# modifier ce script.
echo "→ Récupération de la liste des projets depuis $DOC_URL ..."
DOC_CONTENU=$(curl -sf --max-time 20 "$DOC_URL") || {
    echo "❌ Erreur : impossible de récupérer BRIDGE_AGENT_DOC.md (réseau indisponible" >&2
    echo "   ou URL inaccessible). Installation annulée — aucune liste de projets" >&2
    echo "   fiable disponible, pas d'installation sur une liste vide." >&2
    exit 1
}

REPERTOIRES=$(printf '%s\n' "$DOC_CONTENU" | awk '
    /<!-- DEBUT:TABLEAU_PROJETS_ACTIFS/ { dans_tableau=1; next }
    /<!-- FIN:TABLEAU_PROJETS_ACTIFS/   { dans_tableau=0 }
    dans_tableau && /^\|/ && $0 !~ /^\|[-| ]+\|$/ && $0 !~ /Répertoire de travail CCL/ {
        split($0, champs, "|")
        rep = champs[4]
        gsub(/^[ \t]+|[ \t]+$/, "", rep)
        print rep
    }
')

if [ -z "$REPERTOIRES" ]; then
    echo "❌ Erreur : aucun répertoire de projet trouvé dans le tableau de" >&2
    echo "   BRIDGE_AGENT_DOC.md (format de tableau inattendu — la structure" >&2
    echo "   attendue est balisée par <!-- DEBUT/FIN:TABLEAU_PROJETS_ACTIFS -->)." >&2
    echo "   Installation annulée — aucune installation sur une liste vide." >&2
    exit 1
fi

PROJETS=()
while IFS= read -r rep; do
    [ -z "$rep" ] && continue
    PROJETS+=("${rep/#\~/$HOME}")
done <<< "$REPERTOIRES"

echo "  ${#PROJETS[@]} projet(s) trouvé(s) dans la doc."
echo ""

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
