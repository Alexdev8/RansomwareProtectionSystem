import os
import shutil
import datetime


def full_backup(source_dir, backup_dir):
    timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
    backup_dir = os.path.join(backup_dir, f"full_backup{timestamp}")
    shutil.copytree(source_dir, backup_dir)
    print(f"Sauvegarde complète effectuée : {backup_dir}")


def get_last_full_backup(backup_dir):
    full_backups = [f for f in os.listdir(backup_dir) if f.startswith("full_backup")]
    if full_backups:
        full_backups.sort(reverse=True)
        return os.path.join(backup_dir, full_backups[0])
    else:
        return None


def get_last_partial_backup(backup_dir):
    partial_backups = [f for f in os.listdir(backup_dir) if f.startswith("partial_backup")]
    if partial_backups:
        partial_backups.sort(reverse=True)
        return os.path.join(backup_dir, partial_backups[0])
    else:
        return None


def partial_backup(source_dir, backup_dir):
    timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
    last_full_backup = get_last_full_backup(backup_dir)
    last_partial_backup = get_last_partial_backup(backup_dir)

    if last_full_backup is None:
        print("Aucune sauvegarde complète précédente trouvée.")
        return

    partial_backup_dir = os.path.join(backup_dir, f"partial_backup{timestamp}")
    os.makedirs(partial_backup_dir)

    copied_files = set()

    if last_partial_backup is not None:
        for root, _, files in os.walk(last_partial_backup):
            for file in files:
                copied_files.add(os.path.relpath(os.path.join(root, file), last_partial_backup))

    for root, _, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)
        destination_dir = os.path.join(partial_backup_dir, relative_path)
        os.makedirs(destination_dir, exist_ok=True)

        for file in files:
            source_path = os.path.join(root, file)
            destination_path = os.path.join(destination_dir, file)

            source_modified_time = os.path.getmtime(source_path)
            last_full_backup_file = os.path.join(last_full_backup, relative_path, file)

            if not os.path.exists(last_full_backup_file) or os.path.getmtime(last_full_backup_file) < source_modified_time:
                shutil.copy2(source_path, destination_path)
                copied_files.add(os.path.relpath(source_path, source_dir))

    for file in copied_files:
        source_path = os.path.join(source_dir, file)
        destination_path = os.path.join(partial_backup_dir, file)

        if not os.path.exists(destination_path):
            shutil.copy2(source_path, destination_path)

    print(f"Sauvegarde partielle effectuée : {partial_backup_dir}")


# Exemple d'utilisation
source_dir = "source_dir"
backup_dir = "backup_dir"

# Sauvegarde complète
# full_backup(source_dir, backup_dir)

# Sauvegarde partielle
partial_backup(source_dir, backup_dir)
