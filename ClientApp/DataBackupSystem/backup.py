import os
import shutil
from hashlib import sha256
import datetime


def sauvegarde_complete(source_dir, backup_dir):
    timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M")
    backup_dir = os.path.join(backup_dir, f"full_backup{timestamp}")
    shutil.copytree(source_dir, backup_dir)
    print(f"Sauvegarde complète effectuée : {backup_dir}")

def sauvegarde_incrementielle(source_dir, backup_dir):
    timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M")
    backup_dir = os.path.join(backup_dir, f"partial_backup{timestamp}")
    os.makedirs(backup_dir)

    previous_backup_dir = get_latest_full_backup_dir(backup_dir)
    if previous_backup_dir:
        print("Vérification des fichiers modifiés...")
        compare_and_backup_modified_files(source_dir, previous_backup_dir, backup_dir)
    else:
        print("Aucune sauvegarde complète précédente trouvée. Effectuez d'abord une sauvegarde complète.")

    print(f"Sauvegarde incrémentielle effectuée : {backup_dir}")

def get_latest_full_backup_dir(backup_dir):
    backup_dirs = [os.path.join(backup_dir, d) for d in os.listdir(backup_dir) if os.path.isdir(os.path.join(backup_dir, d))]
    backup_dirs.sort(reverse=True)  # Tri décroissant des dossiers de sauvegarde
    for backup_dir in backup_dirs:
        if backup_dir.startswith("full_backup"):
            return backup_dir
    return None

def compare_and_backup_modified_files(source_dir, previous_backup_dir, current_backup_dir):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            source_file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(source_file_path, source_dir)
            previous_file_path = os.path.join(previous_backup_dir, relative_file_path)
            current_file_path = os.path.join(current_backup_dir, relative_file_path)
            if has_file_changed(source_file_path, previous_file_path):
                shutil.copy2(source_file_path, current_file_path)

def has_file_changed(file1, file2):
    hash1 = get_file_hash(file1)
    hash2 = get_file_hash(file2)
    return hash1 != hash2

def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
        file_hash = sha256(file_data).hexdigest()
        return file_hash


# Exemple d'utilisation

source_dir = "/Users/christophereybaud/PycharmProjects/RansomwareProtectionSystem/DataBackupSystem/source_dir"
backup_dir = "/Users/christophereybaud/PycharmProjects/RansomwareProtectionSystem/DataBackupSystem/backup_dir"

# Sauvegarde complète

# Sauvegarde incrémentielle

sauvegarde_incrementielle(source_dir, backup_dir)