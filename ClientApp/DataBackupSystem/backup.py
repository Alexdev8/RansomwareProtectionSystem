import os
import shutil
from hashlib import sha256
import datetime
import requests
import re
import uuid
from dotenv import load_dotenv
import ClientApp.load_vars as vars

source_dir = "source_dir"
backup_dir = "backup_dir"
directory_to_send = "backup_dir/backup28062023140357"

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def full_backup(source_dir, backup_dir):
    timestamp = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
    backup_dir = os.path.join(backup_dir, f"backup{timestamp}")
    shutil.copytree(source_dir, backup_dir)
    print(f"Sauvegarde complète effectuée : {backup_dir}")


def get_last_backup(backup_dir):
    last_backups = [f for f in os.listdir(backup_dir) if f.startswith("backup")]
    if last_backups:
        last_backups.sort(reverse=True)
        return os.path.join(backup_dir, last_backups[0])
    else:
        return None


def partial_backup(source_dir, backup_dir):
    last_backup = get_last_backup(backup_dir)

    if last_backup is None:
        print("Erreur: Aucune sauvegarde n'a été trouvé ! Veuillez démarrer une sauvegarde complète de la machine ou "
              "bien contactez votre administrateur.")
        return

    for root, _, files in os.walk(source_dir):
        for file in files:
            source_path = os.path.join(root, file)
            relative_path = os.path.relpath(source_path, source_dir)
            backup_path = os.path.join(last_backup, relative_path)

            if os.path.exists(backup_path):
                # Compare modification timestamps to check if the file has been modified
                if os.path.getmtime(source_path) > os.path.getmtime(backup_path):
                    # Copy the modified file to the new backup directory
                    new_backup_path = os.path.join(last_backup, relative_path)
                    os.makedirs(os.path.dirname(new_backup_path), exist_ok=True)
                    shutil.copy2(source_path, new_backup_path)
            else:
                # Copy new file to the new backup directory
                new_backup_path = os.path.join(last_backup, relative_path)
                os.makedirs(os.path.dirname(new_backup_path), exist_ok=True)
                shutil.copy2(source_path, new_backup_path)

    print(f"Sauvegarde partielle effectuée : {last_backup}")


def send_directory_files(directory, url):
    # Créer une archive du répertoire
    base_name = os.path.basename(directory)
    archive_name = f"{base_name}.zip"
    shutil.make_archive(base_name, 'zip', directory)

    # Envoyer l'archive via sendfile
    with open(archive_name, 'rb') as f:
        files = {'files': (archive_name, f, 'application/zip')}
        response = requests.post(url, params={"machineAddress":':'.join(re.findall('..', '%012x' % uuid.getnode())), "date": datetime.datetime.now()}, files=files, headers={"Authorization": f"Bearer {os.environ.get('ACCESS_TOKEN')}"})

        # Traiter la réponse du serveur si nécessaire
        if response.status_code==201:
            print("Répertoire envoyé avec succès !")
        else:
            print("Une erreur est survenue lors de l'envoi !")
            print("Raison : " + response.text)

    # Supprimer l'archive après l'envoi
    os.remove(archive_name)

# full_backup(source_dir, backup_dir)
# partial_backup(source_dir, backup_dir)
send_directory_files(directory_to_send, os.environ.get("SERVER_ADDRESS") + '/' + vars.get('VARS', 'CLIENT_ID') + '/backup/push')
