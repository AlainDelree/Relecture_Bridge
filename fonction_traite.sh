# Fonctions pour marquer des diffs comme traités.
#
# Usage simple : traite <bout_du_hash_ou_du_nom>
#   → déplace UN diff (et son _annote.md) de Non_Lu/ vers Traités/
#
# Usage plage : traite <hash_debut> <hash_fin>
#   → déplace TOUS les diffs compris chronologiquement entre les deux (inclus),
#     dans le même projet. Peu importe l'ordre dans lequel tu donnes les hash.
#
# Dans les deux cas, rien n'est supprimé — juste rangé hors de vue dans
# <projet>/Traités/. Compatible aussi avec d'anciens fichiers restés à la
# racine du projet (avant l'introduction du sous-dossier Non_Lu/).

# Déduit le dossier racine d'un projet à partir d'un fichier trouvé, que ce
# fichier soit dans <projet>/Non_Lu/ (nouveau) ou directement dans <projet>/
# (ancien, avant l'introduction de Non_Lu/).
_racine_projet_pour() {
    local fichier="$1"
    local parent
    parent=$(dirname "$fichier")
    if [ "$(basename "$parent")" = "Non_Lu" ]; then
        dirname "$parent"
    else
        echo "$parent"
    fi
}

traite() {
    if [ "$#" -eq 2 ]; then
        _traite_plage "$1" "$2"
        return $?
    fi

    if [ "$#" -ne 1 ]; then
        echo "Usage : traite <bout_du_hash>  OU  traite <hash_debut> <hash_fin>"
        return 1
    fi

    local motif="$1"
    local trouves
    trouves=$(find ~/Relecture_Bridge -maxdepth 3 -type f \
        \( -iname "*${motif}*.diff" -o -iname "*${motif}*_annote.md" \) \
        ! -path "*/Traités/*" ! -path "*/Traites/*")

    if [ -z "$trouves" ]; then
        echo "Aucun fichier trouvé pour '$motif'"
        return 1
    fi

    echo "$trouves" | while IFS= read -r fichier; do
        local racine_projet
        racine_projet=$(_racine_projet_pour "$fichier")
        mkdir -p "$racine_projet/Traités"
        mv "$fichier" "$racine_projet/Traités/"
        echo "→ $(basename "$fichier") déplacé vers Traités/"
    done
}

_traite_plage() {
    local motif_debut="$1"
    local motif_fin="$2"

    local fichier_debut fichier_fin
    fichier_debut=$(find ~/Relecture_Bridge -maxdepth 3 -type f \
        \( -iname "*${motif_debut}*.diff" -o -iname "*${motif_debut}*_annote.md" \) \
        ! -path "*/Traités/*" ! -path "*/Traites/*" | head -n1)
    fichier_fin=$(find ~/Relecture_Bridge -maxdepth 3 -type f \
        \( -iname "*${motif_fin}*.diff" -o -iname "*${motif_fin}*_annote.md" \) \
        ! -path "*/Traités/*" ! -path "*/Traites/*" | head -n1)

    if [ -z "$fichier_debut" ]; then
        echo "Aucun fichier trouvé pour '$motif_debut'"
        return 1
    fi
    if [ -z "$fichier_fin" ]; then
        echo "Aucun fichier trouvé pour '$motif_fin'"
        return 1
    fi

    local racine_projet
    racine_projet=$(_racine_projet_pour "$fichier_debut")
    if [ "$racine_projet" != "$(_racine_projet_pour "$fichier_fin")" ]; then
        echo "Les deux hash ne sont pas dans le même dossier de projet — traitement par plage annulé."
        return 1
    fi

    # On utilise la date de modification réelle du fichier plutôt que le nom,
    # pour ne pas dépendre de l'ordre des éléments dans le nom de fichier.
    local ts_debut ts_fin ts_min ts_max
    ts_debut=$(stat -c %Y "$fichier_debut")
    ts_fin=$(stat -c %Y "$fichier_fin")

    if [ "$ts_debut" -lt "$ts_fin" ]; then
        ts_min="$ts_debut"; ts_max="$ts_fin"
    else
        ts_min="$ts_fin"; ts_max="$ts_debut"
    fi

    echo "Plage détectée dans $(basename "$racine_projet") : de $(date -d "@$ts_min" '+%Y-%m-%d %H:%M:%S') à $(date -d "@$ts_max" '+%Y-%m-%d %H:%M:%S')"

    # Candidats : fichiers dans <projet>/Non_Lu/ (nouveau) ET directement
    # dans <projet>/ (anciens, avant l'introduction de Non_Lu/), jamais dans Traités/.
    local compteur=0
    local fichier ts
    while IFS= read -r fichier; do
        ts=$(stat -c %Y "$fichier")
        [ "$ts" -lt "$ts_min" ] && continue
        [ "$ts" -gt "$ts_max" ] && continue
        mkdir -p "$racine_projet/Traités"
        mv "$fichier" "$racine_projet/Traités/"
        echo "→ $(basename "$fichier") déplacé vers Traités/"
        compteur=$((compteur + 1))
    done < <(find "$racine_projet" -maxdepth 2 -type f \
                 \( -name '*.diff' -o -name '*_annote.md' \) \
                 ! -path "*/Traités/*")

    echo "$compteur fichier(s) déplacé(s)."
}

