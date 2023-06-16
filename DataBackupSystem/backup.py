import os
import shutil
import hashlib
import datetime


def sauvegarde_complete(source_dir, backup_dir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(backup_dir, f"backup_{timestamp}")
    shutil.copytree(source_dir, backup_dir)
    print(f"Sauvegarde complète effectuée : {backup_dir}")


def sauvegarde_incrementielle(source_dir, backup_dir):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_dir = os.path.join(backup_dir, f"backup_{timestamp}")
    os.makedirs(backup_dir)

    with open(os.path.join(backup_dir, "checksums.txt"), "w") as f:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                checksum = get_checksum(file_path)
                f.write(f"{file_path}:{checksum}\n")

    print(f"Sauvegarde incrémentielle effectuée : {backup_dir}")


def get_checksum(file_path):
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


# Exemple d'utilisation

source_dir = "/chemin/vers/le/dossier/source"
backup_dir = "/chemin/vers/le/dossier/de/sauvegarde"

# Sauvegarde complète
sauvegarde_complete(source_dir, backup_dir)

# Sauvegarde incrémentielle
sauvegarde_incrementielle(source_dir, backup_dir)
