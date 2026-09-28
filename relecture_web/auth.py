#!/usr/bin/env python3
"""
Authentification de relecture_web (issue #92) : mot de passe haché (sha256,
jamais stocké en clair), clé de session Flask persistée, et génération d'un
certificat auto-signé pour le mode --externe.

Propre à relecture_bridge, sans code partagé avec bridge_agent (new_issue.py
/ app/auth.py) — même principe, implémentation indépendante.
"""

import getpass
import hashlib
import hmac
import os
import subprocess

DOSSIER = os.path.dirname(os.path.abspath(__file__))

CHEMIN_MOT_DE_PASSE = os.path.join(DOSSIER, "mot_de_passe.conf")
CHEMIN_CLE_SECRETE = os.path.join(DOSSIER, "secret_key.conf")
DOSSIER_SSL = os.path.join(DOSSIER, "ssl")
CHEMIN_CERTIFICAT = os.path.join(DOSSIER_SSL, "cert.pem")
CHEMIN_CLE_PRIVEE = os.path.join(DOSSIER_SSL, "key.pem")


def hacher_mot_de_passe(mot_de_passe_clair):
    return hashlib.sha256(mot_de_passe_clair.encode("utf-8")).hexdigest()


def mot_de_passe_configure():
    return os.path.exists(CHEMIN_MOT_DE_PASSE) and bool(_lire_hash_stocke())


def _lire_hash_stocke():
    try:
        with open(CHEMIN_MOT_DE_PASSE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None


def definir_mot_de_passe(mot_de_passe_clair):
    """Écrit le hash sha256 du mot de passe, jamais le mot de passe en clair.
    Permissions restreintes (0600) : seul le compte local peut le lire."""
    hash_calcule = hacher_mot_de_passe(mot_de_passe_clair)
    with open(CHEMIN_MOT_DE_PASSE, "w", encoding="utf-8") as f:
        f.write(hash_calcule + "\n")
    os.chmod(CHEMIN_MOT_DE_PASSE, 0o600)


def verifier_mot_de_passe(mot_de_passe_saisi):
    """Comparaison en temps constant (hmac.compare_digest) pour ne pas
    exposer d'information via le temps de réponse."""
    hash_stocke = _lire_hash_stocke()
    if not hash_stocke:
        return False
    return hmac.compare_digest(hacher_mot_de_passe(mot_de_passe_saisi), hash_stocke)


def definir_mot_de_passe_interactif():
    """Demande le mot de passe deux fois (confirmation), jamais affiché ni
    stocké en clair (`getpass`) — utilisé par `--set-password`."""
    mot_de_passe = getpass.getpass("Nouveau mot de passe relecture_web : ")
    if not mot_de_passe:
        print("❌ Mot de passe vide refusé — rien n'a été enregistré.")
        return False
    confirmation = getpass.getpass("Confirmez le mot de passe : ")
    if mot_de_passe != confirmation:
        print("❌ Les deux saisies ne correspondent pas — rien n'a été enregistré.")
        return False
    definir_mot_de_passe(mot_de_passe)
    print(f"✅ Mot de passe enregistré ({CHEMIN_MOT_DE_PASSE}).")
    return True


def charger_ou_creer_cle_secrete():
    """`SECRET_KEY` Flask générée une seule fois puis persistée (hex dans un
    fichier gitignoré, permissions 0600) — jamais régénérée aléatoirement à
    chaque démarrage, sinon toute session survivante serait invalidée à
    chaque redémarrage de relecture_web."""
    try:
        with open(CHEMIN_CLE_SECRETE, "r", encoding="ascii") as f:
            contenu = f.read().strip()
        if contenu:
            return bytes.fromhex(contenu)
    except (OSError, ValueError):
        pass

    cle = os.urandom(32)
    with open(CHEMIN_CLE_SECRETE, "w", encoding="ascii") as f:
        f.write(cle.hex())
    os.chmod(CHEMIN_CLE_SECRETE, 0o600)
    return cle


def assurer_certificat_ssl():
    """Génère un certificat auto-signé (RSA 4096, 10 ans) via `openssl` si
    `ssl/cert.pem`/`ssl/key.pem` n'existent pas encore pour ce dépôt, sinon
    réutilise les fichiers déjà présents — jamais régénéré à chaque
    lancement. Retourne le tuple (cert, clé) attendu par `ssl_context` de
    Flask/Werkzeug."""
    if os.path.exists(CHEMIN_CERTIFICAT) and os.path.exists(CHEMIN_CLE_PRIVEE):
        return CHEMIN_CERTIFICAT, CHEMIN_CLE_PRIVEE

    os.makedirs(DOSSIER_SSL, exist_ok=True)
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:4096",
            "-keyout", CHEMIN_CLE_PRIVEE, "-out", CHEMIN_CERTIFICAT,
            "-days", "3650", "-nodes",
            "-subj", "/CN=relecture_bridge",
        ],
        check=True, capture_output=True,
    )
    os.chmod(CHEMIN_CLE_PRIVEE, 0o600)
    return CHEMIN_CERTIFICAT, CHEMIN_CLE_PRIVEE
