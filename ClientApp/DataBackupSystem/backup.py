import os
import shutil
from hashlib import sha256
import datetime


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




while True:
    print("\n==============================================")
    print("Bienvenue dans votre système de sauvegarde :)")
    print("==============================================")
    print("1) Sauvegarde complète")
    print("2) Sauvegarde incrémentale")
    print("3) Quitter")
    choix = input('\nQue choisissez-vous de faire ?\n')
    source_dir = "source_dir"
    backup_dir = "backup_dir"
    if choix.strip() == "1":
        # Sauvegarde complète
        full_backup(source_dir, backup_dir)
        tempo = input('Appuyez sur une touche pour continuer...')
    elif choix.strip() == "2":
        # Sauvegarde incrémentale
        partial_backup(source_dir, backup_dir)

        tempo = input('Appuyez sur une touche pour continuer...')
    elif choix.strip() == "3":
        break
    else:
        print("Votre choix n'est pas valide. Tapez 1), 2) ou 3)\n")
        tempo = input('Appuyez sur une touche pour recommencer...')
        continue